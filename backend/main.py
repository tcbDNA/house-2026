from __future__ import annotations

from typing import Optional

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from model import ALL_SLIDERS, CATALIST_BASELINES, district_detail, load_bundle, project
import senate_model as senate
import county_model as county

app = FastAPI(title="House 2026 Scenario API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BUNDLE = load_bundle()
SENATE_BUNDLE = senate.load_bundle()
COUNTY_BUNDLE = county.load_bundle()


class SliderValues(BaseModel):
    white_nh: float = CATALIST_BASELINES["white_nh"]
    black: float = CATALIST_BASELINES["black"]
    hispanic: float = CATALIST_BASELINES["hispanic"]
    asian: float = CATALIST_BASELINES["asian"]
    white_college: float = CATALIST_BASELINES["white_college"]
    white_non_college: float = CATALIST_BASELINES["white_non_college"]
    nonwhite_college: float = CATALIST_BASELINES["nonwhite_college"]
    nonwhite_non_college: float = CATALIST_BASELINES["nonwhite_non_college"]
    under_30: float = CATALIST_BASELINES["under_30"]
    age_30_44: float = CATALIST_BASELINES["age_30_44"]
    age_45_64: float = CATALIST_BASELINES["age_45_64"]
    age_65_plus: float = CATALIST_BASELINES["age_65_plus"]


class ProjectRequest(BaseModel):
    environment: float = Field(6.3, ge=-20, le=20)
    sliders: SliderValues = SliderValues()
    # Multiplier on rel_trend (House) / state_trend (Senate). 1.0 = full trend
    # persistence, 0.5 = partial mean-reversion (default), 0.0 = ignore trend.
    trend_discount: float = Field(0.5, ge=0.0, le=1.0)


@app.get("/api/health")
def health():
    return {"status": "ok", "n_districts": BUNDLE.n}


@app.get("/api/baselines")
def baselines():
    """Catalist 2024 baselines per slider (the default 'all groups match 2024'
    positions)."""
    return {"baselines": CATALIST_BASELINES, "house_2024_popvote": -2.6}


@app.get("/api/districts")
def districts_baseline():
    """Baseline projection at D+5, all sliders at 0."""
    return project(BUNDLE, environment=6.3)


@app.post("/api/project")
def project_endpoint(req: ProjectRequest):
    sliders = req.sliders.model_dump()
    # Clamp every slider to ±100
    for k in ("hispanic", "black", "asian", "white_nh",
              "white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college",
              "under_30", "age_30_44", "age_45_64", "age_65_plus"):
        sliders[k] = max(-100, min(100, sliders[k]))
    return project(BUNDLE, environment=req.environment, sliders=sliders,
                   trend_discount=req.trend_discount)


@app.get("/api/district/{district_id}")
def district_detail_endpoint(district_id: str):
    detail = district_detail(BUNDLE, district_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"district {district_id} not found")
    return detail


# ──────────────── Senate endpoints ────────────────


@app.get("/api/senate/health")
def senate_health():
    return {"status": "ok", "n_seats_up": SENATE_BUNDLE.n}


@app.get("/api/senate/seats")
def senate_baseline():
    return senate.project(SENATE_BUNDLE, environment=6.3)


@app.post("/api/senate/project")
def senate_project(req: ProjectRequest):
    sliders = req.sliders.model_dump()
    for k in ("hispanic", "black", "asian", "white_nh",
              "white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college",
              "under_30", "age_30_44", "age_45_64", "age_65_plus"):
        sliders[k] = max(-100, min(100, sliders[k]))
    return senate.project(SENATE_BUNDLE, environment=req.environment, sliders=sliders,
                          trend_discount=req.trend_discount)


@app.get("/api/senate/state/{state}")
def senate_state_detail(state: str):
    s = senate.state_detail(SENATE_BUNDLE, state.upper())
    if s is None:
        raise HTTPException(status_code=404, detail=f"state {state} not found")
    return s


# ──────────────── County endpoints ────────────────


COUNTY_GEOJSON_DIR = Path(__file__).resolve().parent / "data" / "county_geojson"


@app.get("/api/state/{state}/county_geojson")
def state_county_geojson(state: str):
    """Static GeoJSON boundaries for all counties in a state. Browser-cacheable
    since boundaries don't change with scenario."""
    path = COUNTY_GEOJSON_DIR / f"{state.upper()}.geojson"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"no GeoJSON for state {state}")
    return FileResponse(path, media_type="application/json",
                        headers={"Cache-Control": "public, max-age=86400"})


@app.post("/api/state/{state}/counties")
def state_counties(state: str, req: ProjectRequest):
    sliders = req.sliders.model_dump()
    for k in ("hispanic", "black", "asian", "white_nh",
              "white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college",
              "under_30", "age_30_44", "age_45_64", "age_65_plus"):
        sliders[k] = max(-100, min(100, sliders[k]))

    # If this state has a Senate race in the model, compute the candidate-specific
    # adjustment (challenger WAR + incumbency + co-nominee + incumbent WAR) and
    # apply it uniformly to every county. This makes the county aggregate
    # reconcile to the Senate projection. For states without a 2026 Senate race,
    # the adjustment is 0 and the counties show a pure presidential projection.
    senate_adjustment = 0.0
    senate_result = senate.project(
        SENATE_BUNDLE,
        environment=req.environment,
        sliders=sliders,
        trend_discount=req.trend_discount,
    )
    seat = next((s for s in senate_result["seats"] if s["state"] == state.upper()), None)
    if seat is not None:
        senate_adjustment = (
            (seat.get("war_adj_discounted") or 0.0)
            + (seat.get("incumbency_adj") or 0.0)
            + (seat.get("challenger_adj") or 0.0)
        )
        # Add a reconciliation term so the county aggregate matches the Senate
        # projection exactly. The Senate model uses state-level pres margin
        # and state_trend; the county-level data sums to slightly different
        # totals because the underlying datasets come from different sources.
        # Pre-compute the turnout-weighted county pres margin / county trend
        # for this state and shift to reconcile.
        state_upper = state.upper()
        state_counties = [c for c in COUNTY_BUNDLE.counties if c["state"] == state_upper]
        total_24 = sum(c.get("total_2024") or 0 for c in state_counties)
        if total_24 > 0:
            wtd_county_pres = sum((c.get("margin_2024") or 0) * (c.get("total_2024") or 0) for c in state_counties) / total_24
            wtd_county_trend = sum((c.get("rel_trend") or 0) * (c.get("total_2024") or 0) for c in state_counties) / total_24
            state_pres = seat.get("presidential_margin_2024") or 0
            state_trend = seat.get("state_trend") or 0
            state_trend_applied = state_trend * req.trend_discount
            wtd_county_trend_applied = wtd_county_trend * req.trend_discount
            reconcile = (state_pres - wtd_county_pres) + (state_trend_applied - wtd_county_trend_applied)
            senate_adjustment += reconcile

    result = county.project(
        COUNTY_BUNDLE,
        environment=req.environment,
        sliders=sliders,
        trend_discount=req.trend_discount,
        state_filter=state.upper(),
        senate_adjustment=senate_adjustment,
    )
    if not result["counties"]:
        # Some states aren't covered by the underlying county pres dataset
        # (Alaska reports pres results by state-house district, not borough).
        # Return 200 with an empty list + reason so the UI can show a friendly
        # message instead of erroring.
        result["unavailable_reason"] = (
            f"No county-level 2024 presidential data available for {state.upper()}. "
            f"(AK reports results by state-house district; some other states "
            f"have data gaps in the source dataset.)"
        )
    # Attach the Senate context for the UI to display.
    result["senate_seat"] = seat
    return result
