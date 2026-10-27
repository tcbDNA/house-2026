"""Item 4 diagnostics: what the group errors and the two national terms do.

For each error configuration (same seed, same draws otherwise):
  - SD of the simulated national margin (2024-turnout-weighted mean of the
    simulated district margins);
  - the average pairwise correlation of simulated margins among the five
    competitive districts (projected margin within 10 points) with the
    highest Hispanic electorate shares;
  - headline House / Senate metrics.

Usage (from backend/): python3 analysis/error_diagnostics.py > analysis/error_diagnostics.txt
"""
from __future__ import annotations

import sys
from dataclasses import replace
from itertools import combinations
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main  # noqa: E402
import model  # noqa: E402
from analysis.compare import metrics, run  # noqa: E402
from config import DEFAULT_SETTINGS  # noqa: E402
from probability import house_sims  # noqa: E402

S = DEFAULT_SETTINGS
CONFIGS = [
    ("before (no group or extra national terms)", replace(S, group_errors=False, national_extra_errors=False)),
    ("group errors only", replace(S, national_extra_errors=False)),
    ("composition + level only", replace(S, group_errors=False)),
    ("item 4 default (both)", S),
]


def main_cli():
    base = run(S)
    rows = base["house"]["districts"]
    hisp = model.electorate_shares(main.BUNDLE.pop, S)["hispanic"]
    w = main.BUNDLE.turnout_weights(S)
    comp = [i for i, r in enumerate(rows) if abs(r["projection"]) < 10]
    five = sorted(comp, key=lambda i: -hisp[i])[:5]

    terms = main._terms("house", S, "race")
    print("== Group error σ_g = sqrt(SE_g² + τ_g²) (race frame; τ are judgment calls)")
    for g, se, tau, sig in zip(terms.groups, terms.se, terms.tau, terms.sigma):
        print(f"  {g:10} SE {se:5.2f}  τ {tau:4.1f}  σ {sig:5.2f}")
    edu = main._terms("house", S, "race_edu")
    print("  race × edu frame: " + ", ".join(f"{g} σ {s:.2f} (SE {e:.2f}, τ {t:.1f})"
                                             for g, s, e, t in zip(edu.groups, edu.sigma, edu.se, edu.tau)))
    print(f"  national: polling 2.5, composition {terms.sigma_composition}, level {terms.sigma_level}")

    print("\nFive competitive districts (|projection| < 10) with the highest Hispanic electorate share:")
    for i in five:
        print(f"  {rows[i]['district']:6} projection {rows[i]['projection']:+6.1f}  Hispanic {hisp[i] * 100:5.1f}%")

    print("\n== Before / after")
    for label, s in CONFIGS:
        r = rows if s == S else run(s)["house"]["districts"]
        sims = house_sims(r, main._terms("house", s, "race"))
        nat_sd = float((sims @ w).std())
        c = np.corrcoef(sims[:, five].T)
        avg_corr = float(np.mean([c[a, b] for a, b in combinations(range(5), 2)]))
        print(f"  {label:42} national SD {nat_sd:4.2f}   avg pairwise corr (5 Hispanic seats) {avg_corr:.3f}")
        print(f"  {'':42} {metrics(run(s))}")


if __name__ == "__main__":
    main_cli()
