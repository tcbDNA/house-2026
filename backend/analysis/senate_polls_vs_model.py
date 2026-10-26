"""Compare each competitive Senate race's projection with its polling
average, on raw and two-party margins (data/senate_poll_averages.csv: RealClearPolling where it publishes
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


def two_party(d: float, r: float) -> float:
    """Margin with undecideds (and minor candidates) allocated proportionally."""
    return 100.0 * (d - r) / (d + r)


def main_cli():
    seats = {s["state"]: s for s in run()["senate"]["seats"]}
    rows = list(csv.DictReader(AVERAGES.open()))
    print("The model's own projection (before the poll blend) vs the polling average, raw (undecideds")
    print("left in) and two-party (undecideds allocated proportionally). Montana (three-way) is raw only.\n")
    print(f"{'race':4} {'model':>7} {'raw':>7} {'2-party':>8} {'diff raw':>9} {'diff 2p':>8} {'n':>3}  source; sponsors")
    flagged, flagged2, pairs = [], [], []
    for r in sorted(rows, key=lambda r: -abs(seats[r["state"]]["projection"] - float(r["margin"]))):
        s = seats[r["state"]]
        # The model's own projection, before the poll blend.
        m, raw = s["model_projection"], float(r["margin"])
        tp = raw if r["state"] == "MT" else two_party(float(r["d"]), float(r["r"]))
        override = bool(s.get("independent_candidate"))
        if abs(m - raw) > THRESHOLD:
            flagged.append(r["state"])
        if abs(m - tp) > THRESHOLD:
            flagged2.append(r["state"])
        if not override:
            pairs.append((m, raw, tp))
        print(f"{r['state']:4} {m:+7.1f} {raw:+7.1f} {tp:+8.1f} {m - raw:+9.1f} {m - tp:+8.1f} {r['n_polls']:>3}  "
              f"{'[independent: polls only] ' if override else ''}{r['source']}; {r['sponsors']}")
    m, raw, tp = np.array(pairs).T
    s_raw = float(np.polyfit(m, raw, 1)[0])
    s_tp = float(np.polyfit(m, tp, 1)[0])
    print(f"\nRaces differing by more than {THRESHOLD:.0f} pts: raw {', '.join(flagged)}; two-party {', '.join(flagged2)}")
    print(f"Across the {len(pairs)} two-party races, the slope of the polling average on the")
    print(f"model projection is {s_raw:.2f} on raw margins and {s_tp:.2f} on two-party margins")
    print(f"(mean |model| {np.abs(m).mean():.1f}; mean |poll| raw {np.abs(raw).mean():.1f}, two-party {np.abs(tp).mean():.1f}).")
    print(f"Mean model − poll (two-party): {np.mean(m - tp):+.2f}; RMS difference {np.sqrt(np.mean((m - tp) ** 2)):.2f}.")


if __name__ == "__main__":
    main_cli()
