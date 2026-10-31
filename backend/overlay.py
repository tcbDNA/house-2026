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
the county's residual trend. That holds too where the 2024 slice results
are estimated (slices tagged pres_year_source 2020: AK AR CT ID ME MI ND NJ
OK OR PA SD), since only the split within a county is estimated, not the
county's results (settings.overlay_estimated_slice_trends; off: those
slices take the district's residual). Alaska's borough-level 2024 results
are estimated, so its slices take the district's residual and, in the
Senate view, its boroughs the state's.

This changes only the overlay; no district, state or seat projection.
The reconciling shift should be small: a large one means the slice inputs
and the district / state inputs disagree upstream (analysis/overlay_check.py).
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

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
    carried = model.carried_trend(b.rel_trend, model.electorate_shares(b.demographics(settings), settings),
                                  b.battleground, settings, frame)
    return {r["district"]: float(v) for r, v in zip(b.districts, carried)}


@lru_cache(maxsize=1)
def gov_county_results() -> dict[str, dict]:
    """state -> {"year", "incumbent", "margins": fips -> margin, "state_margin"}
    for each running incumbent's last governor race (data/gov_county_results.csv,
    built by data/build_gov_county_results.py)."""
    import csv
    path = Path(__file__).resolve().parent / "data" / "gov_county_results.csv"
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    tot = {}
    for r in csv.DictReader(path.open()):
        s = out.setdefault(r["state"], {"year": int(r["year"]), "incumbent": r["incumbent"], "margins": {},
                                        "third_candidate": r["third_candidate"],
                                        "third_candidate_pct": float(r["third_candidate_pct"] or 0)})
        s["margins"][r["fips"]] = float(r["margin"])
        s.setdefault("shares", {})[r["fips"]] = float(r["dem"]) / max(1.0, float(r["dem"]) + float(r["rep"]))
        t = tot.setdefault(r["state"], [0.0, 0.0, 0.0])
        t[0] += float(r["dem"]); t[1] += float(r["rep"]); t[2] += float(r["total"])
    for st, (d, r, t) in tot.items():
        out[st]["state_margin"] = 100.0 * (d - r) / t
    return out


def incumbent_shares(st: str, counties: list[dict], skip_third: bool = True) -> list[float] | None:
    """Each county's two-party D share in the incumbent's last governor race
    (the full log-odds governor maps start from these); None as incumbent_base."""
    if incumbent_base(st, counties, skip_third) is None:
        return None
    return [gov_county_results()[st]["shares"][c["fips"]] for c in counties]


def incumbent_base(st: str, counties: list[dict], skip_third: bool = True) -> list[float] | None:
    """Each county's starting margin from the incumbent's last governor race:
    the state's 2024 presidential margin (its counties, 2024-vote weighted)
    plus the county's margin in that race minus the race's statewide margin.
    None where the race's county results don't cover every county, or (skip_third)
    where a third candidate won over 5% in it."""
    g = gov_county_results().get(st)
    if g is None or any(c["fips"] not in g["margins"] for c in counties):
        return None
    if skip_third and g["third_candidate_pct"] > 5.0:
        return None
    w = sum(c.get("total_2024") or 0 for c in counties)
    pres = sum((c.get("margin_2024") or 0.0) * (c.get("total_2024") or 0) for c in counties) / w
    return [pres + g["margins"][c["fips"]] - g["state_margin"] for c in counties]


def third_party_share(c: dict) -> float:
    """A county's 2024 third-party share of the presidential vote (0 to 1);
    0 where the source's D + R exceeds its total (Fulton County, IL)."""
    tot = c.get("total_2024") or 0
    if not tot or c.get("dem_2024") is None or c.get("rep_2024") is None:
        return 0.0
    return max(0.0, 1.0 - (c["dem_2024"] + c["rep_2024"]) / tot)


def _reconcile(projs: list[float], weights: list[float], target: float) -> float:
    w = np.array(weights, dtype=float)
    return target - float(np.array(projs) @ w / w.sum()) if w.sum() > 0 else 0.0


def _margin_from_logit(logit: np.ndarray, o: np.ndarray) -> np.ndarray:
    """Total-vote margin (points) from the log-odds of the two-party D share,
    with third-party share o."""
    return 100.0 * (2 / (1 + np.exp(-logit)) - 1) * (1 - o)


def _logit(p) -> np.ndarray:
    p = np.clip(np.array(p, dtype=float), 1e-9, 1 - 1e-9)
    return np.log(p / (1 - p))


def _solve_logit_constant(logit: np.ndarray, o: np.ndarray, w: np.ndarray, target: float) -> float:
    """δ such that the w-weighted margins of logit + δ equal target (bisection;
    the weighted margin rises with δ)."""
    if w.sum() <= 0:
        return 0.0
    lo, hi = -30.0, 30.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if float(_margin_from_logit(logit + mid, o) @ w / w.sum()) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _reconcile_logodds(projs: list[float], weights: list[float], others: list[float],
                       target: float) -> tuple[float, np.ndarray]:
    """(δ, margins): one constant δ added to every county's log-odds of the
    two-party D share, with each county's third-party share held fixed, so
    the weighted margins match the target. Margins are total-vote points."""
    w = np.array(weights, dtype=float)
    o = np.clip(np.array(others, dtype=float), 0.0, 0.95)
    m = np.array(projs, dtype=float) / 100.0
    p = np.clip((1 - o + m) / (2 * (1 - o)), 1e-9, 1 - 1e-9)
    logit = np.log(p / (1 - p))
    margins = lambda delta: _margin_from_logit(logit + delta, o)
    if w.sum() <= 0:
        return 0.0, margins(0.0)
    lo, hi = -30.0, 30.0
    for _ in range(200):                     # weighted margin rises with δ: bisect
        mid = (lo + hi) / 2
        if float(margins(mid) @ w / w.sum()) < target:
            lo = mid
        else:
            hi = mid
    delta = (lo + hi) / 2
    return delta, margins(delta)


def district_slices(did: str, drow: dict, slices: list[dict], uniform_swing: float, terms: CountyTerms,
                    trend_discount: float, settings: Settings, frame: str) -> dict:
    district_resid = district_residuals(settings, frame)[did]
    candidate_adj = ((drow.get("war_adj_discounted") or 0.0) + (drow.get("incumbency_adj") or 0.0)
                     + (drow.get("challenger_adj") or 0.0))
    # Locked seats (CA same-party top-two) show ±100; reconcile the overlay to
    # the projection before the lock.
    county_trends = settings.overlay_estimated_slice_trends and did[:2] not in ESTIMATED_COUNTY_STATES
    target = drow["projection"]
    if drow.get("lockout"):
        target = (drow["margin_2024"] + uniform_swing + (drow.get("rel_trend_applied") or 0.0)
                  + candidate_adj + (drow.get("demo_shift") or 0.0))
    first = []
    for s in slices:
        i = terms.index.get(s["fips"])
        estimated = s.get("pres_year_source") == 2020
        if i is None or (estimated and not county_trends):
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
                   settings: Settings, others: list[float] | None = None,
                   base: list[float] | None = None, full_logodds: bool = False,
                   start_shares: list[float] | None = None) -> dict:
    """others (each county's 2024 third-party share): reconcile on the log-odds
    scale (the governor maps' governor_county_logodds_reconcile): the uniform
    swing and candidate terms are flat shifts too, so they become part of the
    one log-odds constant, which takes each county's own terms (starting
    margin, demographic shift, trend) to the target. Otherwise one flat shift
    in points. base: each county's starting margin in place of its 2024
    presidential margin (governor_county_incumbent_map).
    full_logodds (with others; governor_county_full_logodds): the whole county
    calculation is in log-odds. Each county starts from its log-odds of the
    two-party D share (start_shares, else its 2024 presidential share); the
    demographic and trend shifts, computed in points, become log-odds shifts
    the size they would be in an evenly split county (points / (50 × (1 −
    third-party share))), so a lopsided county moves fewer points than a close
    one; one log-odds constant then matches the target. Returns each step's
    effect in points as "effective": (start, demographic, trend) per county."""
    first = []
    for k, c in enumerate(counties):
        i = terms.index[c["fips"]]
        if state in ESTIMATED_COUNTY_STATES:
            w, resid = 0.0, state_resid
        else:
            w = float(shrink_weight(terms.votes[i], settings.overlay_shrink_k))
            resid = w * float(terms.resid[i]) + (1 - w) * state_resid
        demo = float(terms.demo[i])
        start = base[k] if base is not None else (c.get("margin_2024") or 0.0)
        proj = start + demo + trend_discount * resid + senate_swing + candidate_adj
        first.append((c, i, w, resid, demo, proj))
    projs, weights = [f[5] for f in first], [f[0].get("total_2024") or 0.0 for f in first]
    rec = _reconcile(projs, weights, target)
    if others is not None and full_logodds:
        o = np.clip(np.array(others, dtype=float), 0.0, 0.95)
        if start_shares is None:
            start_shares = [(c.get("dem_2024") or 0) / max(1, (c.get("dem_2024") or 0) + (c.get("rep_2024") or 0))
                            for c in counties]
        l0 = _logit(start_shares)
        l_demo = l0 + np.array([f[4] for f in first]) / (50.0 * (1 - o))
        l_own = l_demo + np.array([trend_discount * f[3] for f in first]) / (50.0 * (1 - o))
        delta = _solve_logit_constant(l_own, o, np.array(weights, dtype=float), target)
        m0, m1, m2 = _margin_from_logit(l0, o), _margin_from_logit(l_demo, o), _margin_from_logit(l_own, o)
        final = _margin_from_logit(l_own + delta, o)
        return {"rows": [(c, i, w, resid, demo, float(p)) for (c, i, w, resid, demo, _), p in zip(first, final)],
                "effective": [(float(a), float(b - a), float(d - b)) for a, b, d in zip(m0, m1, m2)],
                "reconcile": round(rec, 2), "reconcile_logodds": round(delta, 4)}
    if others is not None:
        own = [p - senate_swing - candidate_adj for p in projs]   # the county-specific terms only
        delta, final = _reconcile_logodds(own, weights, others, target)
        return {"rows": [(c, i, w, resid, demo, float(p)) for (c, i, w, resid, demo, _), p in zip(first, final)],
                "reconcile": round(rec, 2), "reconcile_logodds": round(delta, 4)}
    return {"rows": [(c, i, w, resid, demo, proj + rec) for c, i, w, resid, demo, proj in first],
            "reconcile": round(rec, 2)}
