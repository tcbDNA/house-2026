"""County-level projection. Same formula shape as the House model but applied
per county. There are no candidates / incumbency at county level — output is
a scenario-aware 2024-presidential-margin projection per county.

  proj = margin_2024 + uniform_swing + (county_trend × trend_discount) + demo_shift

`uniform_swing = environment - PRES_2024_POPVOTE` (Catalist 2024 R-1.5 baseline).
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from model import (
    AGE_SLIDERS, ALL_SLIDERS, CATALIST_BASELINES, EDU_SLIDERS, EPSILON,
    RACE_SLIDERS, SLIDER_TO_PCT, TOSSUP_THRESHOLD,
)

DATA_PATH = Path(__file__).resolve().parent / "data" / "counties.json"
PRES_2024_POPVOTE = -1.5   # Catalist 2024 R-1.5

# 2026 turnout assumption: midpoint between 2022 midterm (~69% of 2024 pres
# turnout, the typical midterm-to-presidential ratio) and 2024 itself. Applied
# uniformly to each county's 2024 total to estimate 2026 total votes; D/R
# vote estimates then derive from the county's projected margin.
TURNOUT_2026_RATIO = 0.79    # avg of 2018/2016 (0.87) and 2022/2020 (0.71) midterm:pres ratios


@dataclass
class CountyBundle:
    counties: list[dict]
    base_margin: np.ndarray
    rel_trend: np.ndarray
    pct: dict[str, np.ndarray]

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
    pct = {
        slider: np.array([(r.get(field) or 0.0) for r in rows], dtype=float) / 100.0
        for slider, field in SLIDER_TO_PCT.items()
    }
    return CountyBundle(counties=rows, base_margin=base_margin, rel_trend=rel_trend, pct=pct)


def project(
    bundle: CountyBundle,
    environment: float = 5.0,
    sliders: dict[str, float] | None = None,
    trend_discount: float = 1.0,
    state_filter: str | None = None,
    senate_adjustment: float = 0.0,
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
    deltas = {k: sliders[k] - CATALIST_BASELINES[k] for k in ALL_SLIDERS}

    race_shift = sum(bundle.pct[k] * deltas[k] for k in RACE_SLIDERS)
    edu_shift  = sum(bundle.pct[k] * deltas[k] for k in EDU_SLIDERS)
    age_shift  = sum(bundle.pct[k] * deltas[k] for k in AGE_SLIDERS)
    active_axes = sum(1 for ks in (RACE_SLIDERS, EDU_SLIDERS, AGE_SLIDERS)
                      if any(abs(deltas[k]) > EPSILON for k in ks))
    weight = 0.5 if active_axes >= 2 else 1.0
    demo_shift = weight * (race_shift + edu_shift + age_shift)

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
        est_turnout = round(total_24 * TURNOUT_2026_RATIO)
        d_share = (100 + proj) / 200.0   # margin = D% - R%, two-way
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
            "race_shift": round(float(race_shift[i] * weight), 2),
            "edu_shift":  round(float(edu_shift[i] * weight), 2),
            "age_shift":  round(float(age_shift[i] * weight), 2),
            "is_tossup": abs(proj) <= TOSSUP_THRESHOLD,
        })

    return {
        "environment": environment,
        "sliders": sliders,
        "axis_weight": weight,
        "uniform_swing": uniform_swing,
        "trend_discount": trend_discount,
        "turnout_ratio_2026": TURNOUT_2026_RATIO,
        "senate_adjustment": senate_adjustment,
        "state": state_filter,
        "counties": out_counties,
    }
