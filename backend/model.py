"""Projection model. Vectorized with numpy so a full 435-district projection
runs in <1ms.

Formula per district:
  proj = margin_2024 + uniform_swing + trend × trend_discount
       + war_adj_discounted + incumbency_adj + challenger_adj
       + demographic_shift

  trend         = district's 2020→2024 presidential shift relative to the nation
  uniform_swing = environment − turnout-weighted mean of everything above
                  except demographic_shift, so that with sliders at baseline the
                  national (2024-turnout-weighted) margin equals the environment.
  demographic_shift = Σ_axis w_axis × Σ_g electorate_share_g × (slider_g − baseline_g)

Electorate shares are ACS population shares rescaled so their national
turnout-weighted averages match Catalist's electorate composition. When more
than one demographic axis (race / race×edu / age) is moved, the axes are
averaged, weighted by how far each was moved (see `axis_weights`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

import trend
from config import DEFAULT_SETTINGS, Settings

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_PATH = DATA_DIR / "districts.json"
SLICES_PATH = DATA_DIR / "district_county_slices.json"

HOUSE_2024_POPVOTE = -2.6  # D-R; R won the 2024 House popular vote by 2.6
# 2020 Biden D+4.5 → 2024 Trump R+1.5 (matches senate_data.NATIONAL_PRES_SHIFT).
NATIONAL_PRES_SHIFT = -6.0
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
# adults-25+ (rescaled to the electorate — see `electorate_factors`) is its
# weight in the demographic_shift formula. The four cells sum to 100%.
#
# Vintage: these are 2024-cycle values. Update when Catalist publishes a new
# "What Happened" report (typically ~6 months post-election).
# Catalist 2024 "What Happened" published values, exact two-way D-R margins
# from the national crosstabs Excel:
# https://catalist.us/whathappened2024/  (Catalist_What_Happened_2024_Public_National_Crosstabs_2025_05_19.xlsx)
# margin = 2 * D_two_way_share - 100.  Nonwhite_college / nonwhite_non_college
# are share-weighted aggregates of Black / Latino / AAPI / Other cells.
# Catalist 2024 "What Happened" national-crosstabs D-R margins. Used as the
# slider zero-point to match the 2024 presidential baseline the rest of the
# model is built on. Parking sliders here = "group voted same as 2024";
# moving a slider models that group voting differently than 2024.
CATALIST_BASELINES = {
    "white_nh":               -15.24,   # Harris 42.38% two-way
    "black":                   70.80,   # 85.40%
    "hispanic":                 8.46,   # 54.23%
    "asian":                   21.38,   # 60.69%
    "white_college":            1.90,   # 50.95%
    "white_non_college":      -27.28,   # 36.36%
    "nonwhite_college":        36.82,   # share-weighted B/L/A/O college cells
    "nonwhite_non_college":    31.85,   # share-weighted B/L/A/O non-college cells
    "under_30":                10.52,   # 18-29: 55.26%
    "age_30_44":                4.70,   # 52.35%
    "age_45_64":               -8.64,   # 45.68%
    "age_65_plus":             -4.02,   # 47.99%
}
EPSILON = 1e-6   # for "is this slider parked at the baseline" checks

# Catalist electorate composition (2022 midterm shares — who shows up in a
# midterm), from the same "What Happened 2024" crosstabs. Mirrors the
# CATALIST_ELECTORATE_SHARES_* constants in frontend/src/types.ts, which the
# slider panel uses to display each axis's national shift.
CATALIST_ELECTORATE_SHARES = {
    "white_nh": 0.7581, "black": 0.0959, "hispanic": 0.0804, "asian": 0.0365, "other": 0.0292,
    "white_college": 0.3351, "white_non_college": 0.4230,
    "nonwhite_college": 0.1010, "nonwhite_non_college": 0.1409,
    "under_30": 0.1000, "age_30_44": 0.2001, "age_45_64": 0.3652, "age_65_plus": 0.3347,
}

RACE_SLIDERS = ("white_nh", "black", "hispanic", "asian")
EDU_SLIDERS = ("white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college")
AGE_SLIDERS = ("under_30", "age_30_44", "age_45_64", "age_65_plus")
ALL_SLIDERS = RACE_SLIDERS + EDU_SLIDERS + AGE_SLIDERS
AXIS_SLIDERS = {"race": RACE_SLIDERS, "edu": EDU_SLIDERS, "age": AGE_SLIDERS}
# Groups that partition each axis ("other" race has no slider but takes up
# part of the race electorate).
AXIS_GROUPS = {"race": RACE_SLIDERS + ("other",), "edu": EDU_SLIDERS, "age": AGE_SLIDERS}

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
GROUP_TO_PCT = {**SLIDER_TO_PCT, "other": "pct_other"}


def district_turnout(rows: list[dict]) -> np.ndarray:
    """2024 presidential votes cast per district, summed from the precinct-
    aggregated (district, county) slices."""
    slices = json.loads(SLICES_PATH.read_text())
    return np.array([sum(s["total_2024"] for s in slices.get(r["district"], []))
                     for r in rows], dtype=float)


def _population_shares(rows: list[dict]) -> dict[str, np.ndarray]:
    return {g: np.array([(r.get(f) or 0.0) for r in rows], dtype=float) / 100.0
            for g, f in GROUP_TO_PCT.items()}


def _rescale(pop: dict[str, np.ndarray], factors: dict[str, float]) -> dict[str, np.ndarray]:
    """Multiply each group's population share by its turnout factor, then
    renormalize within each axis so the unit's shares sum to 1."""
    out = {}
    for groups in AXIS_GROUPS.values():
        scaled = {g: pop[g] * factors[g] for g in groups}
        total = sum(scaled.values())
        total = np.where(total > 0, total, 1.0)
        for g in groups:
            out[g] = scaled[g] / total
    return out


@lru_cache(maxsize=1)
def _district_rows() -> tuple[dict, ...]:
    return tuple(json.loads(DATA_PATH.read_text())["districts"])


@lru_cache(maxsize=1)
def _district_pop_and_weights() -> tuple[dict[str, np.ndarray], np.ndarray]:
    rows = list(_district_rows())
    w = district_turnout(rows)
    return _population_shares(rows), w / w.sum()


def trend_vs_nation(rows) -> np.ndarray:
    """District's own 2020→2024 presidential shift (pres_shift, from a single
    source — see load_data.py) relative to the nation, comparable to the
    Senate model's state_trend."""
    return np.array([(r.get("pres_shift") or 0.0) - NATIONAL_PRES_SHIFT for r in rows], dtype=float)


@lru_cache(maxsize=32)
def trend_fit(frame: str, white_share: float | None, include_age: bool = True,
              include_bg: bool = True) -> trend.TrendFit:
    """Vote-weighted regression of district trend on the frame's electorate
    shares (+ age) and the battleground indicator (trend.py)."""
    rows = list(_district_rows())
    pop, w = _district_pop_and_weights()
    shares = _rescale(pop, electorate_factors(white_share))
    bg = trend.battleground([r.get("state") or r["district"][:2] for r in rows])
    return trend.fit_trend(trend_vs_nation(rows), shares, w, bg, frame, include_age, include_bg)


def carried_trend(y: np.ndarray, shares: dict[str, np.ndarray], bg: np.ndarray,
                  settings: Settings, frame: str) -> np.ndarray:
    """Trend that trend_discount multiplies, for districts, states or counties."""
    if not (settings.trend_remove_demographic or settings.trend_remove_battleground):
        return y
    fit = trend_fit(frame, white_target(settings), settings.trend_include_age)
    return trend.carried_trend(y, fit, shares, bg, settings.trend_remove_demographic,
                               settings.trend_remove_battleground)


@lru_cache(maxsize=1)
def _catalist_factors() -> dict[str, float]:
    """Per-group turnout factors (iterative proportional fitting over House
    districts) such that the 2024-turnout-weighted national average of each
    rescaled share equals Catalist's 2022 electorate share. ACS shares are of
    total population (race, incl. children / non-citizens) or adults (age,
    edu), so without this e.g. Hispanic voters would be weighted at ~18%
    instead of ~8%."""
    pop, w = _district_pop_and_weights()
    target = {}
    for groups in AXIS_GROUPS.values():
        axis_total = sum(CATALIST_ELECTORATE_SHARES[g] for g in groups)
        target.update({g: CATALIST_ELECTORATE_SHARES[g] / axis_total for g in groups})
    factors = {g: 1.0 for g in GROUP_TO_PCT}
    for _ in range(200):
        shares = _rescale(pop, factors)
        for g in factors:
            factors[g] *= target[g] / float(shares[g] @ w)
    return factors


WHITE_GROUPS = {"race": ("white_nh",), "edu": ("white_college", "white_non_college")}


def _solve_nonwhite_scalar(pop, w, factors, axis: str, white_share: float) -> float:
    """Common multiplier λ on every non-white factor of `axis` such that the
    turnout-weighted national white share equals `white_share`. Within a
    district the non-white groups keep their ratios to each other; the white
    share falls monotonically as λ rises, so bisect on log λ."""
    white = WHITE_GROUPS[axis]
    groups = AXIS_GROUPS[axis]

    def national_white(lam: float) -> float:
        f = {g: factors[g] * (1.0 if g in white else lam) for g in groups}
        scaled = {g: pop[g] * f[g] for g in groups}
        total = sum(scaled.values())
        total = np.where(total > 0, total, 1.0)
        return float(sum(scaled[g] for g in white) / total @ w)

    lo, hi = -7.0, 7.0   # log λ
    for _ in range(100):
        mid = (lo + hi) / 2
        if national_white(np.exp(mid)) > white_share:
            lo = mid
        else:
            hi = mid
    return float(np.exp((lo + hi) / 2))


@lru_cache(maxsize=16)
def electorate_factors(white_share: float | None = None) -> dict[str, float]:
    """Turnout factors per group. `white_share=None` gives the Catalist-2022
    fit; otherwise every non-white factor in the race and race×education axes
    is multiplied by a common scalar (one per axis) so the national white
    share hits `white_share`. Age factors are never changed."""
    factors = dict(_catalist_factors())
    if white_share is None:
        return factors
    pop, w = _district_pop_and_weights()
    for axis in ("race", "edu"):
        lam = _solve_nonwhite_scalar(pop, w, factors, axis, white_share)
        for g in AXIS_GROUPS[axis]:
            if g not in WHITE_GROUPS[axis]:
                factors[g] *= lam
    return factors


def white_target(settings: Settings) -> float | None:
    return settings.white_share if settings.white_share_enabled else None


def electorate_shares(pop: dict[str, np.ndarray], settings: Settings = DEFAULT_SETTINGS,
                      ) -> dict[str, np.ndarray]:
    """Group -> per-row share of the electorate (0..1), including "other".
    `pop` comes from population_shares() for any geography (districts,
    states, counties) carrying the ACS pct_* fields."""
    return _rescale(pop, electorate_factors(white_target(settings)))


def population_shares(rows: list[dict]) -> dict[str, np.ndarray]:
    return _population_shares(rows)


@lru_cache(maxsize=16)
def _national_shares(white_share: float | None) -> tuple[tuple[str, float], ...]:
    pop, w = _district_pop_and_weights()
    shares = _rescale(pop, electorate_factors(white_share))
    return tuple((g, float(shares[g] @ w)) for g in GROUP_TO_PCT)


def national_shares(settings: Settings = DEFAULT_SETTINGS) -> dict[str, float]:
    """2024-turnout-weighted national electorate share of every group. The
    model's national demographic shift is exactly Σ_g share_g × Δ_g with
    these, so the slider panel and the crosstab estimate use them too."""
    return dict(_national_shares(white_target(settings)))


def axis_weights(deltas: dict[str, float], shares: dict[str, float]) -> dict[str, float]:
    """Weight on each demographic axis. Race, race×education and age are
    alternative descriptions of the same voters, so when more than one is
    moved their shifts are averaged rather than stacked — weighted by how far
    each axis was moved (electorate-share-weighted |Δ|). A lone moved axis
    gets full weight, two equally-moved axes get 0.5 each, and nudging a
    second axis slightly only takes a sliver of weight (no step change)."""
    mag = {axis: sum(shares[k] * abs(deltas[k]) for k in keys)
           for axis, keys in AXIS_SLIDERS.items()}
    total = sum(mag.values())
    if total <= EPSILON:
        return {axis: 1.0 for axis in mag}
    return {axis: m / total for axis, m in mag.items()}


def demographic_shift(pct: dict[str, np.ndarray], sliders: dict[str, float],
                      settings: Settings = DEFAULT_SETTINGS):
    """Returns ({axis: weighted per-row shift}, {axis: weight})."""
    deltas = {k: sliders[k] - CATALIST_BASELINES[k] for k in ALL_SLIDERS}
    weights = axis_weights(deltas, national_shares(settings))
    shifts = {axis: weights[axis] * sum(pct[k] * deltas[k] for k in keys)
              for axis, keys in AXIS_SLIDERS.items()}
    return shifts, weights


@dataclass
class DataBundle:
    districts: list[dict]
    # Arrays indexed parallel to `districts`. Trend and WAR are kept apart so
    # the settings can choose how they enter at project time.
    base_no_war: np.ndarray         # margin_2024 + incumbency_adj + challenger_adj
    war_binary: np.ndarray          # incumbent WAR, ×0.5 on any district not on 2024 lines
    war_scaled: np.ndarray          # incumbent WAR × (1 − 0.5 × share new to the incumbent)
    new_lines_binary: np.ndarray    # 1 if the district's lines label isn't "2024", else 0
    new_share: np.ndarray           # share of the district new vs. its largest 2024 predecessor
    rel_trend: np.ndarray           # district trend vs. the nation; full-weight at trend_discount=1.0
    battleground: np.ndarray        # 1 if in a 2024 presidential battleground state
    pop: dict[str, np.ndarray]      # group -> per-district ACS population share (0..1)
    turnout_w: np.ndarray           # 2024 votes, normalized to sum to 1

    def war(self, settings: Settings) -> np.ndarray:
        return self.war_scaled if settings.core_retention_scaling else self.war_binary

    def new_lines_weight(self, settings: Settings) -> np.ndarray:
        """0..1 weight on the simulation's new-lines error."""
        return self.new_share if settings.core_retention_scaling else self.new_lines_binary

    def base_margin(self, settings: Settings = DEFAULT_SETTINGS) -> np.ndarray:
        """margin_2024 + WAR + incumbency + challenger (no trend, no swing)."""
        return self.base_no_war + self.war(settings)

    @property
    def n(self) -> int:
        return len(self.districts)


def load_bundle(path: Path = DATA_PATH) -> DataBundle:
    raw = json.loads(path.read_text())
    rows = raw["districts"]

    margin_2024 = np.array([r.get("margin_2024") or 0.0 for r in rows], dtype=float)
    rel_trend = trend_vs_nation(rows)
    war_binary = np.array([r.get("war_adj_discounted") or 0.0 for r in rows], dtype=float)
    # Sitting incumbents carry a core-retention-scaled factor; everyone else
    # (nominees, open seats) has no new-lines discount either way.
    war_scaled = np.array([(r.get("war_adj") or 0.0) * r["war_lines_factor_scaled"]
                           if r.get("war_lines_factor_scaled") is not None
                           else (r.get("war_adj_discounted") or 0.0) for r in rows], dtype=float)
    incumbency_adj = np.array([r.get("incumbency_adj") or 0.0 for r in rows], dtype=float)
    challenger_adj = np.array([r.get("challenger_adj") or 0.0 for r in rows], dtype=float)
    new_lines_binary = np.array([1.0 if (r.get("lines") or "2024") != "2024" else 0.0
                                 for r in rows], dtype=float)
    new_share = np.array([r.get("new_share") or 0.0 for r in rows], dtype=float)

    turnout = district_turnout(rows)
    return DataBundle(districts=rows, base_no_war=margin_2024 + incumbency_adj + challenger_adj,
                      war_binary=war_binary, war_scaled=war_scaled,
                      new_lines_binary=new_lines_binary, new_share=new_share,
                      rel_trend=rel_trend,
                      battleground=trend.battleground([r.get("state") or r["district"][:2] for r in rows]),
                      pop=population_shares(rows), turnout_w=turnout / turnout.sum())


def project(
    bundle: DataBundle,
    environment: float = 5.0,
    sliders: dict[str, float] | None = None,
    trend_discount: float = 0.5,
    settings: Settings = DEFAULT_SETTINGS,
    frame: str = "race",
) -> dict:
    """Run a scenario.

    Parameters
    ----------
    environment : float
        National House popular-vote margin (D+N) with sliders at baseline.
    sliders : dict[str, float] | None
        Per-group absolute D-R margins. Per-district shifts are computed as
        deltas from CATALIST_BASELINES and add on top of the environment.
    trend_discount : float, default 0.5
        Multiplier applied to the trend term. 1.0 = full trend persistence,
        0.5 = partial mean-reversion, 0.0 = trends ignored, negative = the
        2020→2024 shift partially reverses. Applied to the carried
        (residualized) trend — see trend.py.
    frame : "race" | "race_edu"
        Active slider frame; picks the trend regression's demographic basis.
    """
    sliders = dict(sliders or {})
    for k in ALL_SLIDERS:
        sliders.setdefault(k, CATALIST_BASELINES[k])

    shares = electorate_shares(bundle.pop, settings)
    shifts, weights = demographic_shift(shares, sliders, settings)
    demo_shift = sum(shifts.values())
    rel_trend_carried = carried_trend(bundle.rel_trend, shares, bundle.battleground, settings, frame)
    rel_trend_applied = rel_trend_carried * trend_discount
    war = bundle.war(settings)
    structural = bundle.base_no_war + war + rel_trend_applied
    # Calibrate so the turnout-weighted national margin equals the environment.
    # (Lockouts are included at their pre-override margin.)
    uniform_swing = environment - float(structural @ bundle.turnout_w)
    projections = structural + uniform_swing + demo_shift
    national_margin = float(projections @ bundle.turnout_w)

    # Lockout override: in CA top-two primaries, some districts advanced two
    # same-party candidates to the general — the seat is guaranteed to stay
    # with that party regardless of environment. Force projection to ±100.
    for i, row in enumerate(bundle.districts):
        lockout = row.get("lockout")
        if lockout == "D":
            projections[i] = 100.0
        elif lockout == "R":
            projections[i] = -100.0

    result = _summarize(bundle, projections, demo_shift, environment, sliders, weights,
                        shifts, uniform_swing, rel_trend_applied, trend_discount,
                        war, bundle.new_lines_weight(settings), frame)
    result["national_margin"] = round(national_margin, 3)
    return result


def _summarize(
    bundle, projections, demo_shift, environment, sliders, weights,
    shifts, uniform_swing, rel_trend_applied, trend_discount, war, new_lines_weight, frame,
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
            "open_seat": not row.get("incumbent_is_sitting", False),
            "margin_2024": row.get("margin_2024"),
            "rel_trend": round(float(bundle.rel_trend[i]), 2),
            "rel_trend_applied": round(float(rel_trend_applied[i]), 2),
            "war_adj_discounted": round(float(war[i]), 3),
            "new_lines_weight": round(float(new_lines_weight[i]), 4),
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
            "race_shift": round(float(shifts["race"][i]), 2),
            "edu_shift": round(float(shifts["edu"][i]), 2),
            "age_shift": round(float(shifts["age"][i]), 2),
            "is_tossup": abs(proj) <= TOSSUP_THRESHOLD,
            "flip": "to_D" if flipped_to_d else ("to_R" if flipped_to_r else None),
            "demo_source": row.get("demo_source"),
        })

    return {
        "environment": environment,
        "sliders": sliders,
        "axis_weights": weights,
        "uniform_swing": round(uniform_swing, 2),
        "trend_discount": trend_discount,
        "frame": frame,
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
                "rel_trend": round(float(bundle.rel_trend[i]), 2),
                # base_margin here = full pre-environment baseline at trend_discount=1.0
                "base_margin": round(float(bundle.base_margin()[i] + bundle.rel_trend[i]), 2),
            }
    return None
