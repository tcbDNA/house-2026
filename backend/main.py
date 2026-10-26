from __future__ import annotations

from typing import Optional

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import DEFAULT_SETTINGS, Settings, settings_dict, settings_from
from environment import default_scenario
from model import (
    ALL_SLIDERS, CATALIST_BASELINES, NATIONAL_PRES_SHIFT, district_detail, load_bundle, project,
)
import senate_model as senate
import county_model as county
from probability import add_win_probabilities, add_senate_win_probabilities

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

# Default scenario for the default settings, computed from recent polls' race
# crosstabs (environment.default_scenario; data in
# data/generic_ballot_crosstabs.csv). The race sliders start at each group's
# poll-average margin so districts swing with their own demographics; the
# uniform wave holds the 2024 level plus the "other" race group's shift. The
# frontend fetches the same numbers from /api/defaults.
DEFAULT_SCENARIO = default_scenario(DEFAULT_SETTINGS)
DEFAULT_ENVIRONMENT = DEFAULT_SCENARIO["wave"]
DEFAULT_SLIDERS = DEFAULT_SCENARIO["sliders"]


class SliderValues(BaseModel):
    white_nh: float = DEFAULT_SLIDERS["white_nh"]
    black: float = DEFAULT_SLIDERS["black"]
    hispanic: float = DEFAULT_SLIDERS["hispanic"]
    asian: float = DEFAULT_SLIDERS["asian"]
    white_college: float = CATALIST_BASELINES["white_college"]
    white_non_college: float = CATALIST_BASELINES["white_non_college"]
    nonwhite_college: float = CATALIST_BASELINES["nonwhite_college"]
    nonwhite_non_college: float = CATALIST_BASELINES["nonwhite_non_college"]
    under_30: float = CATALIST_BASELINES["under_30"]
    age_30_44: float = CATALIST_BASELINES["age_30_44"]
    age_45_64: float = CATALIST_BASELINES["age_45_64"]
    age_65_plus: float = CATALIST_BASELINES["age_65_plus"]


class ProjectRequest(BaseModel):
    environment: float = Field(DEFAULT_ENVIRONMENT, ge=-20, le=20)
    sliders: SliderValues = SliderValues()
    # Multiplier on rel_trend (House) / state_trend (Senate). 1.0 = full trend
    # persistence, 0.5 = partial mean-reversion (default), 0.0 = ignore trend,
    # negative = the 2020→2024 shift partially reverses.
    trend_discount: float = Field(0.5, ge=-1.0, le=1.0)
    # Overrides for config.Settings fields (model-v4 flags and parameters).
    settings: dict = Field(default_factory=dict)
    # Active demographic slider frame; picks the trend regression's basis.
    frame: str = Field("race", pattern="^(race|race_edu)$")


class DefaultsRequest(BaseModel):
    settings: dict = Field(default_factory=dict)


def _settings(overrides: dict) -> Settings:
    try:
        return settings_from(overrides)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


def _defaults_payload(s: Settings) -> dict:
    d = default_scenario(s)
    return {**d, "settings": settings_dict(s)}


@app.get("/api/defaults")
def defaults_get():
    """Default scenario (uniform wave, slider positions, national electorate
    shares) for the default settings."""
    return _defaults_payload(DEFAULT_SETTINGS)


@app.post("/api/defaults")
def defaults_post(req: DefaultsRequest):
    """Default scenario for the given settings overrides."""
    return _defaults_payload(_settings(req.settings))


@app.get("/api/health")
def health():
    return {"status": "ok", "n_districts": BUNDLE.n}


@app.get("/api/baselines")
def baselines():
    """Catalist 2024 baselines per slider (zero demographic shift), plus the
    default scenario (poll-average race sliders + uniform wave)."""
    return {"baselines": CATALIST_BASELINES, "house_2024_popvote": -2.6,
            "default_environment": DEFAULT_ENVIRONMENT, "default_sliders": DEFAULT_SLIDERS}


@app.get("/api/districts")
def districts_baseline():
    """Projection for the default scenario."""
    return add_win_probabilities(project(BUNDLE, environment=DEFAULT_ENVIRONMENT,
                                         sliders=DEFAULT_SLIDERS))


@app.post("/api/project")
def project_endpoint(req: ProjectRequest):
    sliders = req.sliders.model_dump()
    # Clamp every slider to ±100
    for k in ("hispanic", "black", "asian", "white_nh",
              "white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college",
              "under_30", "age_30_44", "age_45_64", "age_65_plus"):
        sliders[k] = max(-100, min(100, sliders[k]))
    return add_win_probabilities(
        project(BUNDLE, environment=req.environment, sliders=sliders,
                trend_discount=req.trend_discount, settings=_settings(req.settings),
                frame=req.frame)
    )


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


def _wrap_senate(result):
    s = result.get("summary", {})
    return add_senate_win_probabilities(
        result,
        holdover_d=s.get("not_up_d", 0),
        holdover_r=s.get("not_up_r", 0),
    )


@app.get("/api/senate/seats")
def senate_baseline():
    return _wrap_senate(senate.project(SENATE_BUNDLE, environment=DEFAULT_ENVIRONMENT,
                                       sliders=DEFAULT_SLIDERS))


@app.post("/api/senate/project")
def senate_project(req: ProjectRequest):
    sliders = req.sliders.model_dump()
    for k in ("hispanic", "black", "asian", "white_nh",
              "white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college",
              "under_30", "age_30_44", "age_45_64", "age_65_plus"):
        sliders[k] = max(-100, min(100, sliders[k]))
    return _wrap_senate(senate.project(SENATE_BUNDLE, environment=req.environment,
                                       sliders=sliders, trend_discount=req.trend_discount,
                                       settings=_settings(req.settings), frame=req.frame))


@app.get("/api/senate/state/{state}")
def senate_state_detail(state: str):
    s = senate.state_detail(SENATE_BUNDLE, state.upper())
    if s is None:
        raise HTTPException(status_code=404, detail=f"state {state} not found")
    return s


# ──────────────── County endpoints ────────────────


COUNTY_GEOJSON_DIR = Path(__file__).resolve().parent / "data" / "county_geojson"
DISTRICT_COUNTIES_PATH = Path(__file__).resolve().parent / "data" / "district_counties.json"
DISTRICT_COUNTY_SLICES_PATH = Path(__file__).resolve().parent / "data" / "district_county_slices.json"
import json as _json
_DISTRICT_COUNTIES = _json.loads(DISTRICT_COUNTIES_PATH.read_text())
# Phase 3 precinct-aggregated slices (per (district, county) from DRA precinct
# data). Used in preference to area-overlap for any district whose state has
# been processed; falls back to area-overlap otherwise.
_DISTRICT_COUNTY_SLICES = (
    _json.loads(DISTRICT_COUNTY_SLICES_PATH.read_text())
    if DISTRICT_COUNTY_SLICES_PATH.exists() else {}
)


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
        settings=_settings(req.settings),
        frame=req.frame,
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
            # The Senate projection's own (residualized, discounted) trend term.
            state_trend_applied = seat.get("state_trend_applied") or 0
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
        settings=_settings(req.settings),
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


def _district_counties_from_slices(did: str, req: ProjectRequest, slices: list[dict]) -> dict:
    """Phase 3 backend: precinct-aggregated (district, county) slices.

    Each slice already has the actual 2024 D/R vote totals for the in-district
    portion of the county. The slice's projected 2026 margin is computed as
    `margin_2024 + uniform_swing + district_rel_trend_applied + candidate_adj`
    (district-level trend is used since precinct CSVs only carry 2024 results;
    this matches the model's own district-level math and keeps slices internally
    consistent with the district projection).
    """
    sliders = req.sliders.model_dump()
    for k in ("hispanic", "black", "asian", "white_nh",
              "white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college",
              "under_30", "age_30_44", "age_45_64", "age_65_plus"):
        sliders[k] = max(-100, min(100, sliders[k]))

    state = did.split("-")[0].upper()

    # Get the district's current scenario projection — used for the candidate
    # adjustment that gets added uniformly to every slice. (Demo shift and
    # uniform swing flow in via the per-slice math below.)
    district_proj = project(BUNDLE, environment=req.environment, sliders=sliders,
                            trend_discount=req.trend_discount, settings=_settings(req.settings),
                            frame=req.frame)
    drow = next((d for d in district_proj["districts"] if d["district"] == did), None)
    if drow is None:
        raise HTTPException(status_code=404, detail=f"district {did} not found in projection")

    candidate_adj = ((drow.get("war_adj_discounted") or 0.0)
                     + (drow.get("incumbency_adj") or 0.0)
                     + (drow.get("challenger_adj") or 0.0))
    rel_trend_applied = drow.get("rel_trend_applied") or 0.0
    uniform_swing = district_proj["uniform_swing"]
    demo_shift = drow.get("demo_shift") or 0.0

    # Per-slice projection first pass. Turnout-weighted aggregate may drift from
    # the district projection because (a) slice_m24 sums come from precinct data
    # while district margin_2024 comes from the sensitivity CSV, and (b) per-slice
    # rel_trend weighted avg ≠ district-level rel_trend. Compute a uniform shift
    # that reconciles the two so the header aggregate matches the district projection.
    TURNOUT_2026_RATIO = 0.79  # match county_model.py

    first_pass = []
    for s in slices:
        slice_m24 = s["margin_2024"]
        slice_m20 = s.get("margin_2020")
        if slice_m20 is not None:
            # Trend vs. the nation, matching the district-level rel_trend.
            slice_rel_trend = (slice_m24 - slice_m20) - NATIONAL_PRES_SHIFT
            slice_rel_trend_applied = slice_rel_trend * req.trend_discount
        else:
            slice_rel_trend = drow.get("rel_trend") or 0.0
            slice_rel_trend_applied = rel_trend_applied
        proj_pre = slice_m24 + uniform_swing + slice_rel_trend_applied + candidate_adj + demo_shift
        first_pass.append((s, slice_m24, slice_m20, slice_rel_trend, slice_rel_trend_applied, proj_pre))

    # Turnout-weighted aggregate of first-pass projections.
    tot_w = sum(s["total_2024"] for s, *_ in first_pass) or 1.0
    weighted_avg = sum(pp * s["total_2024"] for s, *_, pp in first_pass) / tot_w
    reconcile = drow["projection"] - weighted_avg

    enriched: list[dict] = []
    for s, slice_m24, slice_m20, slice_rel_trend, slice_rel_trend_applied, proj_pre in first_pass:
        proj = proj_pre + reconcile
        est_turnout = int(round(s["total_2024"] * TURNOUT_2026_RATIO))
        d_share = max(0.0, min(1.0, (100 + proj) / 200.0))
        est_d = int(round(est_turnout * d_share))
        est_r = est_turnout - est_d
        enriched.append({
            "fips": s["fips"],
            "state": state,
            "name": s["name"],
            "margin_2024": round(slice_m24, 1),
            "margin_2020": round(slice_m20, 1) if slice_m20 is not None else None,
            "rel_trend": round(slice_rel_trend, 2),
            "rel_trend_applied": round(slice_rel_trend_applied, 2),
            "total_2024": s["total_2024"],
            "estimated_turnout_2026": est_turnout,
            "estimated_d_votes": est_d,
            "estimated_r_votes": est_r,
            "projection": round(proj, 2),
            "demo_shift": demo_shift,
            "race_shift": drow.get("race_shift") or 0.0,
            "edu_shift": drow.get("edu_shift") or 0.0,
            "age_shift": drow.get("age_shift") or 0.0,
            "is_tossup": abs(proj) < 3.0,
            "overlap_fraction": s["share_of_county_2024"],
            "fully_contained": s["fully_contained"],
        })

    return {
        "district": did,
        "state": state,
        "district_projection": drow["projection"],
        "candidate_adj": round(candidate_adj, 2),
        "reconcile": round(reconcile, 2),
        "data_source": "precinct_aggregated",
        "counties": enriched,
    }


@app.post("/api/district/{district_id}/counties")
def district_counties(district_id: str, req: ProjectRequest):
    """County-level overlay for a House district.

    Two data backends:
      - Phase 3 (precinct-aggregated): for any district whose state has been
        processed via build_district_county_slices.py from DRA precinct CSVs.
        Each (county, district) slice has actual D/R votes summed from precincts,
        so no reconciliation shift is needed.
      - Phase 1 (area-overlap): fallback for all other states. Returns the full
        county's presidential projection scaled by area-overlap; a reconciliation
        term ensures the aggregate matches the district projection.
    """
    did = district_id.upper()
    slices = _DISTRICT_COUNTY_SLICES.get(did)
    if slices is not None:
        return _district_counties_from_slices(did, req, slices)

    overlaps = _DISTRICT_COUNTIES.get(did)
    if overlaps is None:
        raise HTTPException(status_code=404, detail=f"no county overlap data for district {district_id}")

    sliders = req.sliders.model_dump()
    for k in ("hispanic", "black", "asian", "white_nh",
              "white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college",
              "under_30", "age_30_44", "age_45_64", "age_65_plus"):
        sliders[k] = max(-100, min(100, sliders[k]))

    state = district_id.split("-")[0].upper()

    # Get the district's current scenario projection so we can reconcile.
    district_proj = project(BUNDLE, environment=req.environment, sliders=sliders,
                            trend_discount=req.trend_discount, settings=_settings(req.settings),
                            frame=req.frame)
    drow = next((d for d in district_proj["districts"] if d["district"] == district_id.upper()), None)
    if drow is None:
        raise HTTPException(status_code=404, detail=f"district {district_id} not found in projection")

    candidate_adj = ((drow.get("war_adj_discounted") or 0.0)
                     + (drow.get("incumbency_adj") or 0.0)
                     + (drow.get("challenger_adj") or 0.0))

    # Compute county projections at this scenario (state-filtered).
    county_proj = county.project(
        COUNTY_BUNDLE,
        environment=req.environment,
        sliders=sliders,
        trend_discount=req.trend_discount,
        state_filter=state,
        senate_adjustment=0.0,
        settings=_settings(req.settings),
    )
    by_fips = {c["fips"]: c for c in county_proj["counties"]}

    # Filter & enrich. Compute overlap-weighted aggregate so we can reconcile
    # to the district projection. Weight by county_area * overlap (proxied by
    # 2024 turnout × overlap_fraction since we don't have an area number here).
    enriched: list[dict] = []
    weight_sum = 0.0
    pres_x_weight = 0.0
    for o in overlaps:
        c = by_fips.get(o["fips"])
        if c is None:
            continue
        w = (c.get("total_2024") or 0) * o["overlap_fraction"]
        weight_sum += w
        pres_x_weight += (c.get("projection") or 0) * w
        enriched.append({
            **c,
            "overlap_fraction": o["overlap_fraction"],
            "fully_contained": o["fully_contained"],
        })

    # Reconcile: shift every county projection by (district_proj − county_weighted_avg − candidate_adj)
    # so that overlap-weighted county avg + candidate_adj = district projection.
    reconcile = 0.0
    if weight_sum > 0:
        county_avg_pres = pres_x_weight / weight_sum
        reconcile = drow["projection"] - county_avg_pres - candidate_adj
    total_shift = candidate_adj + reconcile
    for c in enriched:
        c["projection"] = round((c.get("projection") or 0) + total_shift, 2)
        # Scale vote-count fields by overlap_fraction so partial counties show
        # the district's area-proportional slice rather than the full county.
        # Phase-1 approximation: assumes uniform population/voter density across
        # the county (which is wrong for big urban counties — Phase 2 BAFs fix this).
        frac = c.get("overlap_fraction", 1.0) or 1.0
        for k in ("total_2024", "estimated_turnout_2026",
                  "estimated_d_votes", "estimated_r_votes"):
            v = c.get(k)
            if v is not None:
                c[k] = int(round(v * frac))

    return {
        "district": district_id.upper(),
        "state": state,
        "district_projection": drow["projection"],
        "candidate_adj": round(candidate_adj, 2),
        "reconcile": round(reconcile, 2),
        "data_source": "area_overlap",
        "counties": enriched,
    }
