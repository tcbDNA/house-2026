"""County overlay (model-v4 item 7): slice-level projections.

Each (district, county) slice — or each county in a Senate state — is
projected from its own pieces instead of shifting every slice by the same
amount:

  slice = slice 2024 margin
        + demographic shift      (the parent county's electorate shares)
        + trend_weight × residual (county-level residual trend, item 2
                                   coefficients with the intercept, county
                                   shares and battleground status; shrunk
                                   toward the district's / state's residual
                                   with weight = votes / (votes + k), 2024
                                   county votes, k = settings.overlay_shrink_k)
        + uniform swing          (the district's, or the Senate's)
        + candidate effects      (WAR, incumbency, challenger)
        + reconciling shift      (one per district / state, so the
                                   2024-vote-weighted slices add up exactly
                                   to its projection)

Slices take their parent county's shares (no slice-level demographics) and
the county's residual trend. Where the 2024 slice results are estimated
(slices tagged pres_year_source 2020: AK AR CT ID ME MI ND NJ OK OR PA SD),
slice-level trends aren't used anywhere: those slices take the district's
residual. In the Senate view the counties are real counties, so they use
their own residuals — except Alaska, whose borough-level 2024 results are
estimated and so take the state's.

This changes only the overlay; no district, state or seat projection.
The reconciling shift should be small: a large one means the slice inputs
and the district / state inputs disagree upstream (analysis/overlay_check.py).
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

import model
import trend as trend_mod
from config import Settings

ESTIMATED_COUNTY_STATES = frozenset({"AK"})   # county-level 2024 results estimated


def shrink_weight(votes: np.ndarray, k: float) -> np.ndarray:
    return votes / (votes + k)


class CountyTerms:
    """Per-county demographic shift and carried (residual) trend for one
    scenario, indexed by FIPS."""

    def __init__(self, counties: list[dict], pop: dict[str, np.ndarray], sliders: dict,
                 settings: Settings, frame: str, center: float = 0.0):
        shares = model.electorate_shares(pop, settings)
        shifts, _ = model.demographic_shift(shares, sliders, settings)
        self.demo = sum(shifts.values())
        self.shifts = shifts
        y = np.array([c.get("rel_trend") or 0.0 for c in counties], dtype=float)
        bg = trend_mod.battleground([c["state"] for c in counties])
        self.resid = model.carried_trend(y, shares, bg, settings, frame) - center
        self.votes = np.array([c.get("total_2024") or 0.0 for c in counties], dtype=float)
        self.index = {c["fips"]: i for i, c in enumerate(counties)}


@lru_cache(maxsize=32)
def district_residuals(settings: Settings, frame: str) -> dict[str, float]:
    """district -> carried (residual) trend, as the House model computes it."""
    import main
    b = main.BUNDLE
    carried = model.carried_trend(b.rel_trend, model.electorate_shares(b.pop, settings),
                                  b.battleground, settings, frame)
    return {r["district"]: float(v) for r, v in zip(b.districts, carried)}


def _reconcile(projs: list[float], weights: list[float], target: float) -> float:
    w = np.array(weights, dtype=float)
    return target - float(np.array(projs) @ w / w.sum()) if w.sum() > 0 else 0.0


def district_slices(did: str, drow: dict, slices: list[dict], uniform_swing: float, terms: CountyTerms,
                    trend_discount: float, settings: Settings, frame: str) -> dict:
    district_resid = district_residuals(settings, frame)[did]
    candidate_adj = ((drow.get("war_adj_discounted") or 0.0) + (drow.get("incumbency_adj") or 0.0)
                     + (drow.get("challenger_adj") or 0.0))
    # Locked seats (CA same-party top-two) show ±100; reconcile the overlay to
    # the projection before the lock.
    target = drow["projection"]
    if drow.get("lockout"):
        target = (drow["margin_2024"] + uniform_swing + (drow.get("rel_trend_applied") or 0.0)
                  + candidate_adj + (drow.get("demo_shift") or 0.0))
    first = []
    for s in slices:
        i = terms.index.get(s["fips"])
        estimated = s.get("pres_year_source") == 2020
        if i is None or estimated:
            w, resid = 0.0, district_resid
            demo = (drow.get("demo_shift") or 0.0) if i is None else float(terms.demo[i])
        else:
            w = float(shrink_weight(terms.votes[i], settings.overlay_shrink_k))
            resid = w * float(terms.resid[i]) + (1 - w) * district_resid
            demo = float(terms.demo[i])
        proj = s["margin_2024"] + demo + trend_discount * resid + uniform_swing + candidate_adj
        first.append((s, i, w, resid, demo, proj, estimated))
    rec = _reconcile([f[5] for f in first], [f[0]["total_2024"] for f in first], target)
    # District 2024 margin minus the slices' vote-weighted 2024 margin: an
    # upstream mismatch between the slice results and the district's.
    w = np.array([f[0]["total_2024"] for f in first], dtype=float)
    margin_gap = (drow["margin_2024"] - float(np.array([f[0]["margin_2024"] for f in first]) @ w / w.sum())
                  if w.sum() > 0 else 0.0)
    out = []
    for s, i, w, resid, demo, proj, estimated in first:
        out.append({
            "fips": s["fips"], "name": s["name"], "margin_2024": round(s["margin_2024"], 1),
            "margin_2020": round(s["margin_2020"], 1) if s.get("margin_2020") is not None else None,
            "total_2024": s["total_2024"], "residual_trend": round(resid, 2), "residual_weight": round(w, 3),
            "rel_trend": round(resid, 2), "rel_trend_applied": round(trend_discount * resid, 2),
            "demo_shift": round(demo, 2),
            "race_shift": round(float(terms.shifts["race"][i]), 2) if i is not None else drow.get("race_shift"),
            "edu_shift": round(float(terms.shifts["edu"][i]), 2) if i is not None else drow.get("edu_shift"),
            "age_shift": round(float(terms.shifts["age"][i]), 2) if i is not None else drow.get("age_shift"),
            "projection": round(proj + rec, 2),
            "slice_results_estimated": estimated,
            "overlap_fraction": s["share_of_county_2024"], "fully_contained": s["fully_contained"],
        })
    return {"counties": out, "reconcile": round(rec, 2), "candidate_adj": round(candidate_adj, 2),
            "district_residual": round(district_resid, 2), "target": round(target, 2),
            "slice_margin_gap": round(margin_gap, 2)}


def state_counties(state: str, counties: list[dict], terms: CountyTerms, state_resid: float,
                   senate_swing: float, candidate_adj: float, target: float, trend_discount: float,
                   settings: Settings) -> dict:
    first = []
    for c in counties:
        i = terms.index[c["fips"]]
        if state in ESTIMATED_COUNTY_STATES:
            w, resid = 0.0, state_resid
        else:
            w = float(shrink_weight(terms.votes[i], settings.overlay_shrink_k))
            resid = w * float(terms.resid[i]) + (1 - w) * state_resid
        demo = float(terms.demo[i])
        proj = (c.get("margin_2024") or 0.0) + demo + trend_discount * resid + senate_swing + candidate_adj
        first.append((c, i, w, resid, demo, proj))
    rec = _reconcile([f[5] for f in first], [f[0].get("total_2024") or 0.0 for f in first], target)
    return {"rows": [(c, i, w, resid, demo, proj + rec) for c, i, w, resid, demo, proj in first],
            "reconcile": round(rec, 2)}
