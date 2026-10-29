"""County-level projection. Same formula shape as the House model but applied
per county. There are no candidates / incumbency at county level — output is
a scenario-aware 2024-presidential-margin projection per county.

  proj = margin_2024 + uniform_swing + (county_trend × trend_discount) + demo_shift

`uniform_swing = environment - PRES_2024_POPVOTE` (Catalist 2024 R-1.5 baseline).
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from config import DEFAULT_SETTINGS, DEFAULT_TREND_WEIGHT, Settings
from model import (
    ALL_SLIDERS, CATALIST_BASELINES, TOSSUP_THRESHOLD, demo_key, demographic_shift, electorate_shares,
    population_shares, population_variants,
)

DATA_PATH = Path(__file__).resolve().parent / "data" / "counties.json"
PRES_2024_POPVOTE = -1.5   # Catalist 2024 R-1.5

# 2026 turnout as a share of 2024 presidential votes, per race, from Kalshi's
# turnout markets (data/turnout_2026.csv, built by data/build_turnout_2026.py
# from the saved KXMIDTERMVOTETURN markets: each race's market-implied median
# total vote ÷ its 2024 presidential vote). Used only to estimate the county
# overlay's 2026 vote counts — no projection, margin or probability uses it.
#   state view:    the state's Senate market, else its governor market, else
#                  its House markets combined
#   district view: the district's House market, else the state's ratio
# TURNOUT_2026_RATIO (the 2024-vote-weighted average over the 70 Senate and
# governor markets) is the last-resort fallback; 0.79 if the file is missing.
TURNOUT_PATH = Path(__file__).resolve().parent / "data" / "turnout_2026.csv"


@lru_cache(maxsize=1)
def _turnout_rows() -> tuple[dict, ...]:
    import csv
    if not TURNOUT_PATH.exists():
        return ()
    with TURNOUT_PATH.open() as f:
        return tuple(r for r in csv.DictReader(f) if r["ratio_to_2024"])


def _weighted(rows) -> float | None:
    rows = list(rows)
    if not rows:
        return None
    return sum(float(r["implied_total_votes"]) for r in rows) / sum(float(r["total_2024"]) for r in rows)


TURNOUT_2026_RATIO = round(_weighted(r for r in _turnout_rows() if r["kind"] in ("senate", "governor")) or 0.79, 3)


def turnout_ratio(state: str | None = None, district: str | None = None) -> tuple[float, str]:
    """(2026 turnout as a share of 2024, which Kalshi market it comes from)."""
    rows = _turnout_rows()
    if district:
        r = next((r for r in rows if r["kind"] == "house" and r["district"] == district), None)
        if r:
            return float(r["ratio_to_2024"]), f"Kalshi {district} House turnout market"
        state = state or district[:2]
    if state:
        for kind in ("senate", "governor"):
            r = next((r for r in rows if r["kind"] == kind and r["state"] == state), None)
            if r:
                return float(r["ratio_to_2024"]), f"Kalshi {state} {kind.capitalize()} turnout market"
        h = _weighted(r for r in rows if r["kind"] == "house" and r["state"] == state)
        if h:
            return h, f"Kalshi {state} House turnout markets combined"
    return TURNOUT_2026_RATIO, "average of Kalshi's 70 Senate and governor turnout markets"


@dataclass
class CountyBundle:
    counties: list[dict]
    base_margin: np.ndarray
    rel_trend: np.ndarray
    pop: dict[str, np.ndarray]
    pops: dict  # pop per model.demo_key (Louisiana / ACS vintage settings)

    @property
    def n(self) -> int:
        return len(self.counties)


def load_bundle(path: Path = DATA_PATH) -> CountyBundle:
    raw = json.loads(path.read_text())
    rows = raw["counties"]
    margin_2024 = np.array([r.get("margin_2024") or 0.0 for r in rows], dtype=float)
    rel_trend   = np.array([r.get("rel_trend") or 0.0 for r in rows], dtype=float)
    # No WAR / incumbency / challenger at county level.
    base_margin = margin_2024
    return CountyBundle(counties=rows, base_margin=base_margin, rel_trend=rel_trend,
                        pop=population_shares(rows), pops=population_variants(rows))


def project(
    bundle: CountyBundle,
    environment: float = 5.0,
    sliders: dict[str, float] | None = None,
    trend_discount: float = DEFAULT_TREND_WEIGHT,
    state_filter: str | None = None,
    senate_adjustment: float = 0.0,
    settings: Settings = DEFAULT_SETTINGS,
) -> dict:
    """`senate_adjustment` is a uniform D-R shift applied to every county in
    the state, capturing the Senate-race-specific terms (challenger WAR,
    incumbency adj, co-nominee WAR, war_adj_discounted) that don't otherwise
    exist at the county level. Set this to the seat's combined candidate
    effect so the county aggregate reconciles to the Senate projection."""
    sliders = dict(sliders or {})
    for k in ALL_SLIDERS:
        sliders.setdefault(k, CATALIST_BASELINES[k])

    uniform_swing = environment - PRES_2024_POPVOTE
    turnout, turnout_source = turnout_ratio(state=state_filter)
    shifts, weights = demographic_shift(electorate_shares(bundle.pops[demo_key(settings)], settings), sliders, settings)
    demo_shift = sum(shifts.values())

    rel_trend_applied = bundle.rel_trend * trend_discount
    projections = bundle.base_margin + rel_trend_applied + uniform_swing + demo_shift + senate_adjustment

    out_counties = []
    for i, c in enumerate(bundle.counties):
        if state_filter is not None and c["state"] != state_filter:
            continue
        proj = float(projections[i])
        total_24 = c.get("total_2024") or 0
        # Estimated 2026 turnout (midpoint of 2022 and 2024 levels) and D/R
        # vote counts derived from the projected margin. Two-way split.
        est_turnout = round(total_24 * turnout)
        # margin = D% - R%, two-way; clamp so extreme scenarios can't push
        # projected margins past ±100 into negative vote counts.
        d_share = max(0.0, min(1.0, (100 + proj) / 200.0))
        est_d_votes = round(est_turnout * d_share)
        est_r_votes = est_turnout - est_d_votes
        out_counties.append({
            "fips": c["fips"],
            "state": c["state"],
            "name": c["name"],
            "margin_2024": c.get("margin_2024"),
            "margin_2020": c.get("margin_2020"),
            "rel_trend": c.get("rel_trend"),
            "rel_trend_applied": round(float(rel_trend_applied[i]), 2),
            "total_2024": total_24,
            "estimated_turnout_2026": est_turnout,
            "estimated_d_votes": est_d_votes,
            "estimated_r_votes": est_r_votes,
            "projection": round(proj, 2),
            "demo_shift": round(float(demo_shift[i]), 2),
            "race_shift": round(float(shifts["race"][i]), 2),
            "edu_shift":  round(float(shifts["edu"][i]), 2),
            "age_shift":  round(float(shifts["age"][i]), 2),
            "is_tossup": abs(proj) <= TOSSUP_THRESHOLD,
        })

    return {
        "environment": environment,
        "sliders": sliders,
        "axis_weights": weights,
        "uniform_swing": uniform_swing,
        "trend_discount": trend_discount,
        "turnout_ratio_2026": turnout,
        "turnout_source": turnout_source,
        "senate_adjustment": senate_adjustment,
        "state": state_filter,
        "counties": out_counties,
    }
