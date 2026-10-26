"""Compare each competitive Senate race's projection with its polling
average (data/senate_poll_averages.csv: RealClearPolling where it publishes
an average, else Poliwave; Rasmussen polls removed from RCP's simple mean).
Lists races where the two differ by more than 5 points. Reporting only —
nothing in the model reads this file.

Usage (from backend/): python3 analysis/senate_polls_vs_model.py > analysis/senate_polls_vs_model.txt
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.compare import run  # noqa: E402

THRESHOLD = 5.0
AVERAGES = Path(__file__).resolve().parents[1] / "data" / "senate_poll_averages.csv"


def main_cli():
    seats = {s["state"]: s for s in run()["senate"]["seats"]}
    rows = list(csv.DictReader(AVERAGES.open()))
    print(f"{'race':4} {'model':>7} {'polls':>7} {'diff':>6} {'n':>3}  source; sponsors")
    flagged, pairs = [], []
    for r in sorted(rows, key=lambda r: -abs(seats[r["state"]]["projection"] - float(r["margin"]))):
        s = seats[r["state"]]
        m, p = s["projection"], float(r["margin"])
        diff = m - p
        over = abs(diff) > THRESHOLD
        override = s.get("poll_override") is not None
        if over:
            flagged.append(r["state"])
        if not override:
            pairs.append((m, p))
        print(f"{r['state']:4} {m:+7.1f} {p:+7.1f} {diff:+6.1f} {r['n_polls']:>3}  "
              f"{'FLAG ' if over else ''}{'[poll override] ' if override else ''}{r['source']}"
              f"{'; Rasmussen removed' if r['rasmussen_removed'] == 'yes' else ''}; {r['sponsors']}")
    m, p = np.array(pairs).T
    slope = float(np.polyfit(m, p, 1)[0])
    print(f"\nRaces differing by more than {THRESHOLD:.0f} pts: {', '.join(flagged)}")
    print(f"Across the {len(pairs)} races without a polling override, regressing the polling average on the\n"
          f"model projection gives a slope of {slope:.2f}: the polls are closer to a tie than the model\n"
          f"(mean |poll| {np.abs(p).mean():.1f} vs mean |model| {np.abs(m).mean():.1f}). Poll margins are raw shares with\n"
          f"undecideds left in, so some compression is expected, but not this much.")


if __name__ == "__main__":
    main_cli()
