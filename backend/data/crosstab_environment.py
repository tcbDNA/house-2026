"""Generic-ballot estimate built from poll race crosstabs.

Instead of averaging poll toplines, measure how far each racial group has
moved since 2024 and add the share-weighted shift to the 2024 result:

  shift_g     = avg_two_way_margin_g (polls) − catalist_2024_margin_g
  environment = PRES_2024_POPVOTE + Σ_g electorate_share_g × shift_g

This uses the crosstabs for what they measure (each group's movement) without
also assuming a change in who turns out. For comparison the script also prints
the "2022 composition" variant, Σ_g share_g × avg_margin_g, which applies the
group margins to the Catalist 2022 midterm electorate (75.8% white) — that
builds in a ~1.6-pt R composition shift relative to 2024 that the polls' own
likely-voter models (~70–73% white) don't show.

Reads generic_ballot_crosstabs.csv (one row per poll × group, including a
"topline" row per poll). Each poll's numbers are converted to two-way margins
(100 × (D − R) / (D + R)) so pollsters' differing undecided rates don't distort
the average, and to match the two-way Catalist slider baselines.

  - One poll per pollster (the CSV should hold only each pollster's latest).
  - Polls are weighted by √n, with n capped at 2000 so very large online
    samples don't dominate.
  - A group needs crosstabs from at least MIN_POLLS (2) pollsters; otherwise (and
    for "other" race, which polls don't report consistently) it's set to its
    Catalist 2024 margin plus the share-weighted average shift of the groups
    that do have data.

Run:  python3 crosstab_environment.py [path/to/crosstabs.csv]
"""

from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DATA_DIR.parent))
from model import CATALIST_BASELINES, CATALIST_ELECTORATE_SHARES  # noqa: E402

CSV_PATH = DATA_DIR / "generic_ballot_crosstabs.csv"
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
    """pollster -> {"n": int, "end": str, "margins": {group: two-way margin}}"""
    polls: dict[str, dict] = {}
    with path.open() as f:
        for r in csv.DictReader(f):
            p = polls.setdefault(r["pollster"], {"n": int(r["n"]), "end": r["end"],
                                                 "population": r["population"], "margins": {}})
            p["margins"][r["group"]] = two_way(float(r["dem"]), float(r["rep"]))
    return polls


def weighted_mean(pairs: list[tuple[float, float]]) -> float:
    return sum(w * x for w, x in pairs) / sum(w for w, _ in pairs)


def estimate(polls: dict[str, dict], equal_weights: bool = False) -> dict:
    by_group: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for p in polls.values():
        w = 1.0 if equal_weights else math.sqrt(min(p["n"], N_CAP))
        for g, m in p["margins"].items():
            by_group[g].append((w, m))

    shares = {g: CATALIST_ELECTORATE_SHARES[g]
              for g in GROUPS + ("other",)}
    total_share = sum(shares.values())
    shares = {g: s / total_share for g, s in shares.items()}

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
    baseline_2022_comp = sum(shares[g] * baselines[g] for g in margins)
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
        "environment_2022_composition": baseline_2022_comp + shift,
        "baseline_2022_composition": baseline_2022_comp,
        "topline": weighted_mean(by_group["topline"]),
        "shares": shares,
    }


def fmt(m: float) -> str:
    return f"{'D' if m >= 0 else 'R'}+{abs(m):.1f}"


def main():
    polls = load_polls(Path(sys.argv[1]) if len(sys.argv) > 1 else CSV_PATH)
    est = estimate(polls)
    eq = estimate(polls, equal_weights=True)

    print(f"{len(polls)} polls: " + ", ".join(
        f"{k} ({v['end']}, {v['population'].upper()}, n={v['n']})"
        for k, v in sorted(polls.items(), key=lambda kv: kv[1]['end'], reverse=True)))
    print()
    print(f"{'group':10} {'polls':>5} {'share':>6} {'avg margin':>11} {'2024':>7} {'shift':>7} {'contrib':>8}")
    for g in GROUPS + ("other",):
        m = est["margins"][g]
        base = CATALIST_BASELINES.get(g, OTHER_BASELINE)
        tag = " (imputed)" if est["imputed"].get(g) else ""
        print(f"{g:10} {est['n_polls'].get(g, 0):>5} {est['shares'][g]:>6.3f} {fmt(m):>11} "
              f"{fmt(base):>7} {m - base:>+7.1f} {est['contributions'][g]:>+8.2f}{tag}")
    print()
    print(f"Share-weighted shift since 2024:                     {est['shift']:+.1f}")
    print(f"Generic ballot = 2024 result {fmt(PRES_2024_POPVOTE)} + shift:          {fmt(est['environment'])}"
          f"  (unrounded {est['environment']:+.2f})")
    print(f"  equal-weight-per-pollster version:                 {fmt(eq['environment'])}")
    print(f"Same polls' topline average (two-way):               {fmt(est['topline'])}")
    print(f"Alt: margins on the 2022 midterm electorate:         {fmt(est['environment_2022_composition'])}"
          f"  (2024 margins on that electorate: {fmt(est['baseline_2022_composition'])})")

    print()
    print(f"{'race x edu':22} {'polls':>5} {'avg margin':>11} {'2024':>7} {'shift':>7}")
    for g in EDU_GROUPS:
        m, base = est["edu_margins"][g], CATALIST_BASELINES[g]
        tag = " (imputed: 2024 + non-white shift)" if est["edu_imputed"].get(g) else ""
        print(f"{g:22} {est['n_polls'][g]:>5} {fmt(m):>11} {fmt(base):>7} {m - base:>+7.1f}{tag}")

    # Slider defaults. The sliders carry each group's shift into the districts
    # (shift × that group's electorate share there); the uniform wave covers
    # the rest so the national total equals the estimate. Computed the way the
    # slider panel computes its total (unnormalized Catalist shares, rounded
    # slider values).
    race = {g: round(est["margins"][g], 1) for g in GROUPS}
    edu = {g: round(est["edu_margins"][g], 1) for g in EDU_GROUPS}
    implied = lambda d: sum(CATALIST_ELECTORATE_SHARES[g] * (v - CATALIST_BASELINES[g])  # noqa: E731
                            for g, v in d.items())
    wave_race = round(est["environment"] - implied(race), 2)
    wave_edu = round(est["environment"] - implied(edu), 2)
    print()
    print("Slider defaults (race frame):", race)
    print("Slider defaults (race x edu frame):", edu)
    print(f"Uniform wave: race frame {wave_race:+.2f} (sliders carry {implied(race):+.2f}); "
          f"race x edu frame {wave_edu:+.2f} (sliders carry {implied(edu):+.2f})")
    print(f"-> backend/main.py DEFAULT_ENVIRONMENT = {wave_race}, DEFAULT_SLIDERS race keys as above;")
    print(f"   frontend App.tsx DEFAULT_ENV = {wave_race}; types.ts DEFAULT_SLIDERS / EDU_FRAME_DEFAULTS as above.")


if __name__ == "__main__":
    main()
