"""Item 2 backtest: does the 2020→2024 trend carry into 2025?

County level, New Jersey (21 counties) and Virginia (133 counties and
independent cities), 2025 governor's races:

  y = 2025 governor margin − 2024 presidential margin        (D − R, % of total)
  x = county 2020→2024 presidential trend (vs. the nation; the state fixed
      effect makes the reference irrelevant)

controlling for the same electorate shares as the district trend regression
(race frame: Black, Hispanic, Asian, other vs. white; age: under 30, 30–44,
65+ vs. 45–64), with a state fixed effect, weighted by 2025 votes. Neither
state was a 2024 battleground, so this speaks to the demographic and
residual parts of the trend only. This result set the default residual-trend
weight to 0 (config.DEFAULT_TREND_WEIGHT); 0.5 and the others stay scenarios.

Sources (data/sources/gov_2025/, see SOURCES.md):
  nj_2025-official-general-results-governor.pdf (+ .txt extract)
  va_2025_governor_elstats_search.csv (+ .url)

Usage (from backend/): python3 analysis/trend_weight_nj_va_2025.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
import model  # noqa: E402
import trend  # noqa: E402
from config import DEFAULT_SETTINGS  # noqa: E402

SRC = BACKEND / "data" / "sources" / "gov_2025"
CONTROLS = ("black", "hispanic", "asian", "other", "under_30", "age_30_44", "age_65_plus")


def nj_results() -> dict[str, tuple[int, int, int]]:
    """county name (upper) -> (Dem, Rep, total) from the official list's text."""
    counties = {"ATLANTIC", "BERGEN", "BURLINGTON", "CAMDEN", "CAPE MAY", "CUMBERLAND", "ESSEX",
                "GLOUCESTER", "HUDSON", "HUNTERDON", "MERCER", "MIDDLESEX", "MONMOUTH", "MORRIS",
                "OCEAN", "PASSAIC", "SALEM", "SOMERSET", "SUSSEX", "UNION", "WARREN"}
    tally = defaultdict(lambda: [0, 0, 0])
    for line in (SRC / "nj_2025-official-general-results-governor.txt").read_text().splitlines():
        m = re.match(r"^([A-Z ]+?) ([A-Z][A-Z ]*?) ([\d,]+)$", line.strip())
        if not m:
            continue
        county = next((c for c in counties if line.startswith(c + " ")), None)
        if county is None:
            continue
        party = line[len(county) + 1:].rsplit(" ", 1)[0]
        votes = int(line.rsplit(" ", 1)[1].replace(",", ""))
        tally[county][2] += votes
        if party == "DEMOCRATIC":
            tally[county][0] += votes
        elif party == "REPUBLICAN":
            tally[county][1] += votes
    assert len(tally) == 21, sorted(tally)
    return {c: tuple(v) for c, v in tally.items()}


def va_results() -> dict[str, tuple[int, int, int]]:
    """locality name (upper) -> (Dem, Rep, total votes cast)."""
    out = defaultdict(lambda: [0, 0, 0])
    with (SRC / "va_2025_governor_elstats_search.csv").open() as f:
        for r in csv.DictReader(f):
            if r["division_type"] != "Locality" or not r["election_date"].startswith("2025-11-04"):
                continue
            name, v = r["division_name"].upper(), int(r["votes"])
            if r["candidate_party_name"] == "Democratic":
                out[name][0] += v
            elif r["candidate_party_name"] == "Republican":
                out[name][1] += v
            elif r["candidate_name"] == "Total Votes Cast":
                out[name][2] += v
    assert len(out) == 133, len(out)
    return {c: tuple(v) for c, v in out.items()}


def main():
    counties = [c for c in json.loads((BACKEND / "data" / "counties.json").read_text())["counties"]
                if c["state"] in ("NJ", "VA")]
    results = {"NJ": nj_results(), "VA": va_results()}
    rows, missing = [], []
    for c in counties:
        key = c["name"].upper()
        if c["state"] == "NJ":
            key = key.replace(" COUNTY", "")
        r = results[c["state"]].get(key)
        if r is None:
            missing.append((c["state"], c["name"]))
            continue
        d, rep, tot = r
        rows.append((c, 100.0 * (d - rep) / tot, tot))
    if missing:
        sys.exit(f"unmatched counties: {missing}")

    shares = model.electorate_shares(model.population_shares([c for c, _, _ in rows]), DEFAULT_SETTINGS)
    y = np.array([m25 - c["margin_2024"] for c, m25, _ in rows])
    x = np.array([c["rel_trend"] for c, _, _ in rows])
    va = np.array([1.0 if c["state"] == "VA" else 0.0 for c, _, _ in rows])
    w = np.array([tot for _, _, tot in rows], dtype=float)

    def report(label, X, names, mask=None):
        m = np.ones(len(y), bool) if mask is None else mask
        beta, se, hc1, r2 = trend.wls(y[m], X[m], w[m])
        i = names.index("trend")
        print(f"  {label:52} trend coef {beta[i]:+.3f}  SE {se[i]:.3f} (HC1 {hc1[i]:.3f})  "
              f"R² {r2:.3f}  n={m.sum()}")
        return beta, names

    ctrl = np.column_stack([shares[g] for g in CONTROLS])
    print(f"NJ + VA 2025 governor: weighted mean of (2025 gov − 2024 pres) = {y @ w / w.sum():+.2f} pts "
          f"(NJ {y[va == 0] @ w[va == 0] / w[va == 0].sum():+.2f}, VA {y[va == 1] @ w[va == 1] / w[va == 1].sum():+.2f})")
    print("\nRegression of (2025 governor margin − 2024 presidential margin) on county 2020→2024 trend:")
    full_names = ["const", "trend", "VA"] + list(CONTROLS)
    beta, _ = report("main: + race/age shares + state FE (weights = 2025 votes)",
                     np.column_stack([np.ones_like(y), x, va, ctrl]), full_names)
    report("no demographic controls, state FE",
           np.column_stack([np.ones_like(y), x, va]), ["const", "trend", "VA"])
    report("NJ only, + controls", np.column_stack([np.ones_like(y), x, ctrl]),
           ["const", "trend"] + list(CONTROLS), va == 0)
    report("VA only, + controls", np.column_stack([np.ones_like(y), x, ctrl]),
           ["const", "trend"] + list(CONTROLS), va == 1)
    print("\nMain-model coefficients: " + "  ".join(f"{n}={b:+.2f}" for n, b in zip(full_names, beta)))
    print("\nReading: a positive trend coefficient means places that moved toward Trump in 2020→2024\n"
          "moved further that way in 2025 (trend persists); negative means they moved back.\n"
          "Model default: 0 × the residual trend (config.DEFAULT_TREND_WEIGHT; 0.5 etc. are scenarios).")


if __name__ == "__main__":
    main()
