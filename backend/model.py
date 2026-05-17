"""Projection model. Vectorized with numpy so a full 435-district projection
runs in <1ms.

Formula per district:
  proj = margin_2024 + uniform_swing + rel_trend + war_adj_discounted
       + incumbency_adj + challenger_adj
       + demographic_shift

  uniform_swing = environment_d_minus_r - (-2.6)   # 2024 House popvote was R+2.6
  demographic_shift = sum_g (pct_g_in_district / 100) * shift_g

Race-vs-education double-counting is handled by halving the contribution
of each axis when sliders on both axes are simultaneously nonzero.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

DATA_PATH = Path(__file__).resolve().parent / "data" / "districts.json"

HOUSE_2024_POPVOTE = -2.6  # D-R; R won the 2024 House popular vote by 2.6
TOSSUP_THRESHOLD = 3.0

# Catalist 2024 demographic baselines — D-R margin among each group in the
# 2024 election (Catalist "What Happened" cycle analysis, plus exit-poll
# aggregates where Catalist hasn't reported a number).
#
# Sliders are absolute group margins; the model subtracts this baseline so a
# slider parked at the Catalist value produces zero demographic shift (i.e.
# "this group voted the same as 2024"). Move a slider away from its baseline
# to model a real-world shift.
#
# Race × education: the education axis is now a four-cell decomposition
# (white_college, white_non_college, nonwhite_college, nonwhite_non_college)
# matching how Catalist actually reports. Each cell's share of the district's
# adults-25+ is its weight in the demographic_shift formula. The four cells
# together sum to 100% of the 25+ population.
#
# Vintage: these are 2024-cycle values. Update when Catalist publishes a new
# "What Happened" report (typically ~6 months post-election).
# Catalist 2024 "What Happened" published values, exact two-way D-R margins
# from the national crosstabs Excel:
# https://catalist.us/whathappened2024/  (Catalist_What_Happened_2024_Public_National_Crosstabs_2025_05_19.xlsx)
# margin = 2 * D_two_way_share - 100.  Nonwhite_college / nonwhite_non_college
# are share-weighted aggregates of Black / Latino / AAPI / Other cells.
# Catalist 2022 House popular-vote margins. Using the prior-midterm cycle as
# the "zero point" since 2026 is also a midterm; parking a slider here means
# "this group voted the same way they did in 2022."
CATALIST_BASELINES = {
    "white_nh":               -15.76,
    "black":                   76.22,
    "hispanic":                21.64,
    "asian":                   24.80,
    "white_college":           -2.20,
    "white_non_college":      -26.50,
    "nonwhite_college":        43.70,
    "nonwhite_non_college":    41.78,
    "under_30":                29.62,
    "age_30_44":               14.26,
    "age_45_64":               -9.24,
    "age_65_plus":            -12.16,
}
EPSILON = 1e-6   # for "is this slider parked at the baseline" checks

RACE_SLIDERS = ("white_nh", "black", "hispanic", "asian")
EDU_SLIDERS = ("white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college")
AGE_SLIDERS = ("under_30", "age_30_44", "age_45_64", "age_65_plus")
ALL_SLIDERS = RACE_SLIDERS + EDU_SLIDERS + AGE_SLIDERS

# Slider name -> demographic field in district record
SLIDER_TO_PCT = {
    "white_nh":              "pct_white_nh",
    "black":                 "pct_black",
    "hispanic":              "pct_hispanic",
    "asian":                 "pct_asian",
    "white_college":         "pct_white_nh_college",
    "white_non_college":     "pct_white_nh_non_college",
    "nonwhite_college":      "pct_nonwhite_college",
    "nonwhite_non_college":  "pct_nonwhite_non_college",
    "under_30":              "pct_under_30",
    "age_30_44":             "pct_30_44",
    "age_45_64":             "pct_45_64",
    "age_65_plus":           "pct_65_plus",
}


@dataclass
class DataBundle:
    districts: list[dict]
    # Arrays indexed parallel to `districts`:
    # `base_margin` excludes rel_trend so it can be discounted at project time.
    base_margin: np.ndarray         # margin_2024 + war_adj_discounted + incumbency_adj + challenger_adj
    rel_trend: np.ndarray           # district-relative trend; full-weight at trend_discount=1.0
    pct: dict[str, np.ndarray]      # slider key -> per-district share (0..1)

    @property
    def n(self) -> int:
        return len(self.districts)


def load_bundle(path: Path = DATA_PATH) -> DataBundle:
    raw = json.loads(path.read_text())
    rows = raw["districts"]
    n = len(rows)

    margin_2024 = np.array([r.get("margin_2024") or 0.0 for r in rows], dtype=float)
    rel_trend = np.array([r.get("rel_trend") or 0.0 for r in rows], dtype=float)
    war_adj = np.array([r.get("war_adj_discounted") or 0.0 for r in rows], dtype=float)
    incumbency_adj = np.array([r.get("incumbency_adj") or 0.0 for r in rows], dtype=float)
    challenger_adj = np.array([r.get("challenger_adj") or 0.0 for r in rows], dtype=float)
    base_margin = margin_2024 + war_adj + incumbency_adj + challenger_adj

    pct = {
        slider: np.array(
            [(r.get(field) or 0.0) for r in rows], dtype=float) / 100.0
        for slider, field in SLIDER_TO_PCT.items()
    }
    return DataBundle(districts=rows, base_margin=base_margin, rel_trend=rel_trend, pct=pct)


def project(
    bundle: DataBundle,
    environment: float = 5.0,
    sliders: dict[str, float] | None = None,
    trend_discount: float = 1.0,
) -> dict:
    """Run a scenario.

    Parameters
    ----------
    environment : float
        D popular-vote target (D+N).
    sliders : dict[str, float] | None
        Per-group absolute D-R margins. Per-district shifts are computed as
        deltas from CATALIST_BASELINES.
    trend_discount : float, default 1.0
        Multiplier applied to ``rel_trend`` before combining into the projection.
        1.0 = full trend persistence (the default; preserves prior behavior).
        0.5 = partial mean-reversion. 0.0 = trends fully ignored.
    """
    sliders = dict(sliders or {})
    for k in ALL_SLIDERS:
        sliders.setdefault(k, CATALIST_BASELINES[k])

    uniform_swing = environment - HOUSE_2024_POPVOTE

    # Deltas: how much each group's margin has moved vs. 2024 (Catalist baseline)
    deltas = {k: sliders[k] - CATALIST_BASELINES[k] for k in ALL_SLIDERS}

    race_shift = sum(bundle.pct[k] * deltas[k] for k in RACE_SLIDERS)
    edu_shift = sum(bundle.pct[k] * deltas[k] for k in EDU_SLIDERS)
    age_shift = sum(bundle.pct[k] * deltas[k] for k in AGE_SLIDERS)

    # Anti-double-count: if multiple axes have been moved from baseline,
    # half-weight each
    active_axes = sum(1 for keys in (RACE_SLIDERS, EDU_SLIDERS, AGE_SLIDERS)
                       if any(abs(deltas[k]) > EPSILON for k in keys))
    weight = 0.5 if active_axes >= 2 else 1.0

    demo_shift = weight * (race_shift + edu_shift + age_shift)
    rel_trend_applied = bundle.rel_trend * trend_discount
    projections = bundle.base_margin + rel_trend_applied + uniform_swing + demo_shift

    return _summarize(bundle, projections, demo_shift, environment, sliders, weight,
                      race_shift, edu_shift, age_shift, uniform_swing,
                      rel_trend_applied, trend_discount)


def _summarize(
    bundle, projections, demo_shift, environment, sliders, weight,
    race_shift, edu_shift, age_shift, uniform_swing,
    rel_trend_applied, trend_discount,
) -> dict:
    d_seats = int(np.sum(projections > 0))
    r_seats = int(np.sum(projections < 0))
    tossups = int(np.sum(np.abs(projections) <= TOSSUP_THRESHOLD))
    # Race-tier buckets: tossup ≤3 | lean 3-7 | likely 7-13 | safe >13
    buckets = {
        "d_safe":   int(np.sum(projections > 13)),
        "d_likely": int(np.sum((projections > 7) & (projections <= 13))),
        "d_lean":   int(np.sum((projections > 3) & (projections <= 7))),
        "d_tossup": int(np.sum((projections > 0) & (projections <= 3))),
        "r_tossup": int(np.sum((projections <= 0) & (projections > -3))),
        "r_lean":   int(np.sum((projections <= -3) & (projections > -7))),
        "r_likely": int(np.sum((projections <= -7) & (projections > -13))),
        "r_safe":   int(np.sum(projections <= -13)),
    }

    pickups_d, pickups_r = [], []
    out_districts = []
    for i, row in enumerate(bundle.districts):
        proj = float(projections[i])
        party = row.get("party", "")
        was_d = party == "(D)"
        is_d = proj > 0
        flipped_to_d = is_d and not was_d
        flipped_to_r = (not is_d) and was_d
        if flipped_to_d:
            pickups_d.append(row["district"])
        if flipped_to_r:
            pickups_r.append(row["district"])
        out_districts.append({
            "district": row["district"],
            "incumbent": row.get("incumbent", ""),
            "party": party,
            "state": row.get("state"),
            "lines": row.get("lines"),
            "margin_2024": row.get("margin_2024"),
            "rel_trend": row.get("rel_trend"),
            "rel_trend_applied": round(float(rel_trend_applied[i]), 2),
            "war_adj_discounted": row.get("war_adj_discounted"),
            "incumbency_adj": row.get("incumbency_adj"),
            "war_year": row.get("war_year"),
            "war_match_type": row.get("war_match_type"),
            "challenger": row.get("challenger"),
            "challenger_party": row.get("challenger_party"),
            "challenger_adj": row.get("challenger_adj"),
            "challenger_war": row.get("challenger_war"),
            "challenger_war_year": row.get("challenger_war_year"),
            "challenger_war_source": row.get("challenger_war_source"),
            "projection": round(proj, 2),
            "demo_shift": round(float(demo_shift[i]), 2),
            "race_shift": round(float(race_shift[i] * weight), 2),
            "edu_shift": round(float(edu_shift[i] * weight), 2),
            "age_shift": round(float(age_shift[i] * weight), 2),
            "is_tossup": abs(proj) <= TOSSUP_THRESHOLD,
            "flip": "to_D" if flipped_to_d else ("to_R" if flipped_to_r else None),
            "demo_source": row.get("demo_source"),
        })

    return {
        "environment": environment,
        "sliders": sliders,
        "axis_weight": weight,
        "uniform_swing": uniform_swing,
        "trend_discount": trend_discount,
        "summary": {
            "d_seats": d_seats,
            "r_seats": r_seats,
            "tossups": tossups,
            "d_pickups": pickups_d,
            "r_pickups": pickups_r,
            "majority": "D" if d_seats >= 218 else ("R" if r_seats >= 218 else "none"),
            "buckets": buckets,
        },
        "districts": out_districts,
    }


def district_detail(bundle: DataBundle, district_id: str) -> dict | None:
    for i, row in enumerate(bundle.districts):
        if row["district"] == district_id:
            return {
                **row,
                # base_margin here = full pre-environment baseline at trend_discount=1.0
                "base_margin": round(float(bundle.base_margin[i] + bundle.rel_trend[i]), 2),
            }
    return None
