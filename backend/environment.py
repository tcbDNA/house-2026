"""National environment and default scenario from poll race crosstabs.

Each group's generic-ballot margin is averaged across the latest poll from
each pollster that publishes a race breakdown (data/generic_ballot_crosstabs.csv),
its shift from the Catalist 2024 margin is weighted by the group's share of
the electorate, and the summed shift is added to the 2024 result:

  shift_g     = avg_two_way_margin_g − catalist_2024_margin_g
  environment = PRES_2024_POPVOTE + Σ_g share_g × shift_g

Electorate shares are the model's national shares for the active settings
(model.national_shares), so the composition target (config.white_share)
feeds both this estimate and the district-level demographic shift.

Default scenario: the race sliders sit at the poll-average margins, so each
district swings with its own demographics; the uniform wave holds what every
district shares — the 2024 level plus the "other" race group's shift, which
has no slider:

  wave  = PRES_2024_POPVOTE + share_other × shift_other
  total = wave + Σ_{slider groups} share_g × shift_g = environment
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from config import DEFAULT_SETTINGS, Settings
from model import CATALIST_BASELINES, national_shares

CSV_PATH = Path(__file__).resolve().parent / "data" / "generic_ballot_crosstabs.csv"
GROUPS = ("white_nh", "black", "hispanic", "asian")
EDU_GROUPS = ("white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college")
NONWHITE = ("black", "hispanic", "asian", "other")
OTHER_BASELINE = 7.06   # Catalist 2024 "other" race margin (frontend OTHER_RACE_BASELINE)
PRES_2024_POPVOTE = -1.5   # Trump R+1.5 (matches senate_model / county_model)
N_CAP = 2000
MIN_POLLS = 2


def two_way(dem: float, rep: float) -> float:
    return 100.0 * (dem - rep) / (dem + rep)


def load_polls(path: Path = CSV_PATH) -> dict[str, dict]:
    """pollster -> {"n": int, "end": str, "population": str, "margins": {group: two-way margin}}"""
    polls: dict[str, dict] = {}
    with path.open() as f:
        for r in csv.DictReader(f):
            p = polls.setdefault(r["pollster"], {"n": int(r["n"]), "end": r["end"],
                                                 "population": r["population"], "margins": {}})
            p["margins"][r["group"]] = two_way(float(r["dem"]), float(r["rep"]))
    return polls


def weighted_mean(pairs: list[tuple[float, float]]) -> float:
    return sum(w * x for w, x in pairs) / sum(w for w, _ in pairs)


def estimate(polls: dict[str, dict], settings: Settings = DEFAULT_SETTINGS,
             equal_weights: bool = False) -> dict:
    by_group: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for p in polls.values():
        w = 1.0 if equal_weights else math.sqrt(min(p["n"], N_CAP))
        for g, m in p["margins"].items():
            by_group[g].append((w, m))

    ns = national_shares(settings)
    shares = {g: ns[g] for g in GROUPS + ("other",)}

    margins = {g: weighted_mean(by_group[g]) for g in GROUPS if len(by_group[g]) >= MIN_POLLS}
    observed_share = sum(shares[g] for g in margins)
    avg_shift = sum(shares[g] * (margins[g] - CATALIST_BASELINES[g]) for g in margins) / observed_share
    imputed = {}
    for g in GROUPS:
        if g not in margins:
            margins[g] = CATALIST_BASELINES[g] + avg_shift
            imputed[g] = True
    margins["other"] = OTHER_BASELINE + avg_shift
    imputed["other"] = True

    baselines = {**CATALIST_BASELINES, "other": OTHER_BASELINE}
    contributions = {g: shares[g] * (margins[g] - baselines[g]) for g in GROUPS + ("other",)}
    shift = sum(contributions.values())
    baseline_composition = sum(shares[g] * baselines[g] for g in margins)
    # Race × education cells, for the alternative slider frame. Cells with
    # fewer than MIN_POLLS polls take their 2024 margin plus the non-white
    # shift from the race groups above (white cells are well covered).
    nonwhite_shift = (sum(contributions[g] for g in NONWHITE)
                      / sum(shares[g] for g in NONWHITE))
    edu_margins, edu_imputed = {}, {}
    for g in EDU_GROUPS:
        if len(by_group[g]) >= MIN_POLLS:
            edu_margins[g] = weighted_mean(by_group[g])
        else:
            edu_margins[g] = CATALIST_BASELINES[g] + nonwhite_shift
            edu_imputed[g] = True

    return {
        "margins": margins,
        "imputed": imputed,
        "edu_margins": edu_margins,
        "edu_imputed": edu_imputed,
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
    sliders = {**CATALIST_BASELINES, **{g: est["margins"][g] for g in GROUPS}}
    wave = PRES_2024_POPVOTE + est["contributions"]["other"]
    ns = national_shares(settings)
    slider_shift = sum(ns[g] * (sliders[g] - CATALIST_BASELINES[g]) for g in GROUPS)
    return {
        "wave": wave,
        "sliders": sliders,
        "edu_frame_sliders": dict(est["edu_margins"]),
        "national_shares": ns,
        "environment": est["environment"],
        "slider_shift": slider_shift,
        "total": wave + slider_shift,
    }
