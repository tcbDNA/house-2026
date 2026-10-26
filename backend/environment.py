"""National environment and default scenario from poll race crosstabs.

National level (S, "the current method"). Each group's generic-ballot margin
is averaged across the latest poll from each pollster that publishes a race
breakdown (data/generic_ballot_crosstabs.csv), weighted by √(subgroup n); its
shift from the group's 2024 margin (Catalist, or Pew validated voters — see
config.group_baseline) is weighted by the group's share of the electorate:

  S           = Σ_g share_g × (avg_2026_margin_g − margin_2024_g)
  environment = PRES_2024_POPVOTE + S

Pattern across groups (config.pollster_matched_shifts). Within each pollster,
compare its 2026 crosstab with its own final 2024 pre-election poll
(data/pollster_2024_crosstabs.csv), net of the change in its topline, so
persistent crosstab bias and 2024's overall polling miss both cancel:

  r_pg   = (m26_pg − m24_pg) − (m26_p,top − m24_p,top)          (two-way margins)
  r_avg_g = Σ_p √n_eff_pg r_pg / Σ_p √n_eff_pg,   n_eff = 1 / (1/n26 + 1/n24)
  shift_g = S + (r_avg_g − c)

c is the share-weighted mean of r_avg over the slider groups (shares
renormalized), so Σ share × shift = S and the national level is unchanged;
"other" keeps S. Groups without enough matched pollsters keep their
current-method shift, and c absorbs it so the level still holds (Asian: only
matched if every pollster with a 2026 Asian crosstab has a 2024 one). The
race × education frame matches the white college / non-college cells the
same way; the non-white cells keep the current rule (2024 + the non-white
race groups' average shift).

Electorate shares are the model's national shares for the active settings
(model.national_shares), so the composition target (config.white_share)
feeds both this estimate and the district-level demographic shift.

Default scenario: each slider sits at its group's 2024 margin (Catalist —
the model's reference) plus its shift, so each district swings with its own
demographics; the uniform wave holds what every district shares — the 2024
level plus the "other" race group's shift, which has no slider:

  wave  = PRES_2024_POPVOTE + share_other × shift_other
  total = wave + Σ_{slider groups} share_g × shift_g = environment
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from config import DEFAULT_SETTINGS, DEFAULT_TREND_WEIGHT, DESIGN_EFFECT, Settings
from model import CATALIST_BASELINES, national_shares

DATA = Path(__file__).resolve().parent / "data"
CSV_PATH = DATA / "generic_ballot_crosstabs.csv"
CSV_2024_PATH = DATA / "pollster_2024_crosstabs.csv"
PEW_VALIDATED_PATH = DATA / "pew_validated_2024.csv"
GROUPS = ("white_nh", "black", "hispanic", "asian")
EDU_GROUPS = ("white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college")
WHITE_EDU = ("white_college", "white_non_college")
NONWHITE = ("black", "hispanic", "asian", "other")
# Asian crosstabs are thin: match only if every 2026 Asian crosstab has a 2024 pair.
MATCH_ALL_REQUIRED = ("asian",)
OTHER_BASELINE = 7.06   # Catalist 2024 "other" race margin (frontend OTHER_RACE_BASELINE)
PRES_2024_POPVOTE = -1.5   # Trump R+1.5 (matches senate_model / county_model)
N_CAP = 2000
MIN_POLLS = 2
LOO_THRESHOLD = 1.5   # pts; leave-one-out move that triggers the weighted median


def two_way(dem: float, rep: float) -> float:
    return 100.0 * (dem - rep) / (dem + rep)


def _estimated_group_n(n: int, group: str) -> float:
    """Where a poll publishes only percentages: total n × the group's share of
    the electorate (the model's national shares at default settings)."""
    return n * national_shares(DEFAULT_SETTINGS)[group]


def margin_se(margin: float, n: float) -> float:
    """Sampling error of a two-way margin (pts): 200 × sqrt(p(1 − p) × deff / n)."""
    p = min(max((1.0 + margin / 100.0) / 2.0, 0.01), 0.99)
    return 200.0 * math.sqrt(p * (1.0 - p) * DESIGN_EFFECT / n)


def load_polls(path: Path = CSV_PATH) -> dict[str, dict]:
    """pollster -> {"n", "end", "population", "margins": {group: two-way margin},
    "group_n": {group: subgroup n}, "group_n_source": {group: source}}.

    Subgroup n, in order of preference: as published ("published"); from the
    published margins of error, n × (MOE_total / MOE_group)², which carries
    any oversampling and weighting the pollster's MOEs reflect ("moe"); else
    total n × the group's electorate share ("share")."""
    rows: dict[str, list[dict]] = defaultdict(list)
    with path.open() as f:
        for r in csv.DictReader(f):
            rows[r["pollster"]].append(r)
    polls: dict[str, dict] = {}
    for name, rs in rows.items():
        n = int(rs[0]["n"])
        top_moe = next((float(r["moe"]) for r in rs if r["group"] == "topline" and r.get("moe")), None)
        p = polls[name] = {"n": n, "end": rs[0]["end"], "population": rs[0]["population"],
                           "margins": {}, "group_n": {}, "group_n_source": {}}
        for r in rs:
            g = r["group"]
            p["margins"][g] = two_way(float(r["dem"]), float(r["rep"]))
            if r.get("group_n") or g == "topline":
                p["group_n"][g], src = float(r["group_n"] or n), "published"
            elif r.get("moe") and top_moe:
                p["group_n"][g], src = n * (top_moe / float(r["moe"])) ** 2, "moe"
            else:
                p["group_n"][g], src = _estimated_group_n(n, g), "share"
            p["group_n_source"][g] = src
    return polls


def load_baselines(source: str) -> dict[str, float]:
    """2024 group margins (two-way) the current method measures from. Pew's
    validated-voter study has no "other" or non-white × education cells;
    those keep Catalist's."""
    base = {**CATALIST_BASELINES, "other": OTHER_BASELINE}
    if source == "pew_validated":
        with PEW_VALIDATED_PATH.open() as f:
            base.update({r["group"]: two_way(float(r["harris"]), float(r["trump"]))
                         for r in csv.DictReader(f)})
    return base


def weighted_mean(pairs: list[tuple[float, float]]) -> float:
    return sum(w * x for w, x in pairs) / sum(w for w, _ in pairs)


def _weight(p: dict, g: str, settings: Settings, equal_weights: bool) -> float:
    if equal_weights:
        return 1.0
    n = p["group_n"][g] if settings.subgroup_n_weights else p["n"]
    return math.sqrt(min(n, N_CAP))


def weighted_median(pairs: list[tuple[float, float]]) -> float:
    """Median of x under weights w (pairs of (w, x)); averages the two middle
    values when the cumulative weight lands exactly on half."""
    pairs = sorted(pairs, key=lambda wx: wx[1])
    half, cum = sum(w for w, _ in pairs) / 2.0, 0.0
    for i, (w, x) in enumerate(pairs):
        cum += w
        if abs(cum - half) < 1e-9 * half and i + 1 < len(pairs):
            return (x + pairs[i + 1][1]) / 2.0
        if cum > half:
            return x
    return pairs[-1][1]


def matched_changes(polls: dict[str, dict], polls_2024: dict[str, dict], groups: tuple[str, ...],
                    settings: Settings = DEFAULT_SETTINGS, equal_weights: bool = False) -> dict[str, dict]:
    """group -> {"r_avg", "se", "pollsters": [(name, r, n_eff, se_r, pop26, pop24)],
    "pooled_n", "missing", "r_mean", "r_median", "loo": {name: r_avg without it},
    "max_loo", "method"}. "missing" lists pollsters with a 2026 crosstab for the
    group but no 2024 pair. se_r combines both years' sampling error of the
    group margin; se is the inverse-variance SE of the combined r."""
    out = {}
    for g in groups:
        rows, missing = [], []
        for name, p in polls.items():
            if g not in p["margins"]:
                continue
            q = polls_2024.get(name)
            if q is None or g not in q["margins"]:
                missing.append(name)
                continue
            r = ((p["margins"][g] - q["margins"][g])
                 - (p["margins"]["topline"] - q["margins"]["topline"]))
            n26, n24 = p["group_n"][g], q["group_n"][g]
            se_r = math.hypot(margin_se(p["margins"][g], n26), margin_se(q["margins"][g], n24))
            rows.append((name, r, 1.0 / (1.0 / n26 + 1.0 / n24), se_r, p["population"], q["population"]))
        m = {"pollsters": rows, "missing": missing, "pooled_n": sum(row[2] for row in rows),
             "r_avg": None, "se": None, "r_mean": None, "r_median": None, "loo": {}, "max_loo": 0.0,
             "method": None}
        if rows:
            def w(row):
                if equal_weights:
                    return 1.0
                return 1.0 / row[3] ** 2 if settings.matched_inverse_variance else math.sqrt(row[2])
            pairs = [(w(row), row[1]) for row in rows]
            m["r_mean"] = weighted_mean(pairs)
            m["r_median"] = weighted_median(pairs)
            m["se"] = 1.0 / math.sqrt(sum(1.0 / row[3] ** 2 for row in rows))
            if len(rows) > 1:
                m["loo"] = {row[0]: weighted_mean(pairs[:i] + pairs[i + 1:]) for i, row in enumerate(rows)}
                m["max_loo"] = max(abs(v - m["r_mean"]) for v in m["loo"].values())
            robust = settings.matched_median_fallback and m["max_loo"] > LOO_THRESHOLD
            m["method"] = "weighted median" if robust else "weighted mean"
            m["r_avg"] = m["r_median"] if robust else m["r_mean"]
        out[g] = m
    return out


def _centered(S: float, r: dict[str, float], fixed: dict[str, float],
              shares: dict[str, float]) -> tuple[dict[str, float], float]:
    """shift_g = S + r_g − c for matched groups; `fixed` groups keep their
    shift and c absorbs their deviation from S, so the share-weighted shift
    over matched + fixed (+ any remainder at S) stays S."""
    s_m = sum(shares[g] for g in r)
    c = (sum(shares[g] * r[g] for g in r) + sum(shares[g] * (f - S) for g, f in fixed.items())) / s_m
    return {**{g: S + r[g] - c for g in r}, **fixed}, c


def _matchable(g: str, m: dict) -> bool:
    if m["r_avg"] is None or len(m["pollsters"]) < MIN_POLLS:
        return False
    return not (g in MATCH_ALL_REQUIRED and m["missing"])


def estimate(polls: dict[str, dict], settings: Settings = DEFAULT_SETTINGS,
             equal_weights: bool = False, polls_2024: dict[str, dict] | None = None) -> dict:
    by_group: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for p in polls.values():
        for g, m in p["margins"].items():
            by_group[g].append((_weight(p, g, settings, equal_weights), m))

    ns = national_shares(settings)
    shares = {g: ns[g] for g in GROUPS + ("other",)}
    base = load_baselines(settings.group_baseline)

    # Current method: poll-average margin minus the 2024 margin. Groups with
    # too few polls, and "other", take the share-weighted average shift.
    margins = {g: weighted_mean(by_group[g]) for g in GROUPS if len(by_group[g]) >= MIN_POLLS}
    observed_share = sum(shares[g] for g in margins)
    avg_shift = sum(shares[g] * (margins[g] - base[g]) for g in margins) / observed_share
    current = {g: (margins[g] - base[g] if g in margins else avg_shift) for g in GROUPS}
    current["other"] = avg_shift
    imputed = {g: True for g in GROUPS + ("other",) if g not in margins}
    S = sum(shares[g] * current[g] for g in GROUPS + ("other",))

    # Non-white × education cells (current rule): 2024 + the non-white race
    # groups' average shift.
    def nonwhite_avg(sh: dict[str, float]) -> float:
        return sum(shares[g] * sh[g] for g in NONWHITE) / sum(shares[g] for g in NONWHITE)

    edu_current, edu_imputed = {}, {}
    for g in EDU_GROUPS:
        if g in WHITE_EDU and len(by_group[g]) >= MIN_POLLS:
            edu_current[g] = weighted_mean(by_group[g]) - base[g]
        else:
            edu_current[g] = nonwhite_avg(current)
            edu_imputed[g] = True

    matched, c, c_edu = {}, None, None
    shifts, edu_shifts = dict(current), dict(edu_current)
    if settings.pollster_matched_shifts:
        polls_2024 = load_polls(CSV_2024_PATH) if polls_2024 is None else polls_2024
        matched = matched_changes(polls, polls_2024, GROUPS + WHITE_EDU, settings, equal_weights)
        r = {g: matched[g]["r_avg"] for g in GROUPS if _matchable(g, matched[g])}
        race, c = _centered(S, r, {g: current[g] for g in GROUPS if g not in r}, shares)
        shifts = {**race, "other": S}
        nw = nonwhite_avg(shifts)
        r_edu = {g: matched[g]["r_avg"] for g in WHITE_EDU if _matchable(g, matched[g])}
        if r_edu:
            fixed = {g: (edu_current[g] if g in WHITE_EDU else nw) for g in EDU_GROUPS if g not in r_edu}
            edu_shifts, c_edu = _centered(S, r_edu, fixed, {g: ns[g] for g in EDU_GROUPS})
        else:
            edu_shifts = {g: (edu_current[g] if g in WHITE_EDU and g not in edu_imputed else nw)
                          for g in EDU_GROUPS}

    contributions = {g: shares[g] * shifts[g] for g in GROUPS + ("other",)}
    shift = sum(contributions.values())
    baseline_composition = sum(shares[g] * base[g] for g in GROUPS + ("other",))
    return {
        "margins": margins,                 # 2026 poll-average margins (current method)
        "imputed": imputed,
        "baselines": base,
        "current_shifts": current,
        "shifts": shifts,
        "sliders": {g: CATALIST_BASELINES[g] + shifts[g] for g in GROUPS},
        "edu_current_shifts": edu_current,
        "edu_shifts": edu_shifts,
        "edu_sliders": {g: CATALIST_BASELINES[g] + edu_shifts[g] for g in EDU_GROUPS},
        "edu_imputed": edu_imputed,
        "matched": matched,
        "c": c,
        "c_edu": c_edu,
        "S": S,
        "n_polls": {g: len(by_group[g]) for g in GROUPS + EDU_GROUPS + ("topline",)},
        "contributions": contributions,
        "shift": shift,
        "environment": PRES_2024_POPVOTE + shift,
        "environment_on_composition": baseline_composition + shift,
        "baseline_on_composition": baseline_composition,
        "topline": weighted_mean(by_group["topline"]),
        "shares": shares,
    }


@lru_cache(maxsize=32)
def default_scenario(settings: Settings = DEFAULT_SETTINGS) -> dict:
    """Default wave, slider positions and national shares for `settings`."""
    est = estimate(load_polls(), settings)
    sliders = {**CATALIST_BASELINES, **est["sliders"]}
    wave = PRES_2024_POPVOTE + est["contributions"]["other"]
    ns = national_shares(settings)
    slider_shift = sum(ns[g] * (sliders[g] - CATALIST_BASELINES[g]) for g in GROUPS)
    return {
        "wave": wave,
        "sliders": sliders,
        "edu_frame_sliders": dict(est["edu_sliders"]),
        "national_shares": ns,
        "environment": est["environment"],
        "slider_shift": slider_shift,
        "total": wave + slider_shift,
        "trend_discount": DEFAULT_TREND_WEIGHT,
    }
