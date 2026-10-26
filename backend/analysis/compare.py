"""Run the default scenario and record headline metrics for the change log.

Usage (from backend/):
  python3 analysis/compare.py --label baseline [--note "diagnostics text"]

Appends one row to analysis/comparison.csv and writes the full House/Senate
output to analysis/runs/<label>.json. Every run uses the model's default
scenario (DEFAULT_ENVIRONMENT, DEFAULT_SLIDERS, trend 0.5) and the fixed
Monte Carlo seed, so rows are directly comparable.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

import main  # noqa: E402  (loads bundles + defaults exactly as the API does)
import model  # noqa: E402
import senate_model  # noqa: E402
from probability import add_senate_win_probabilities, add_win_probabilities  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent
TABLE = OUT_DIR / "comparison.csv"
FIELDS = ["label", "national_margin", "house_d_seats", "house_median", "house_p10", "house_p90",
          "house_p_d_majority", "senate_d_seats", "senate_median", "senate_p_d_control", "diagnostics"]


def run(env: float | None = None, sliders: dict | None = None, trend_discount: float = 0.5) -> dict:
    env = main.DEFAULT_ENVIRONMENT if env is None else env
    sliders = main.DEFAULT_SLIDERS if sliders is None else sliders
    B = main.BUNDLE
    house = add_win_probabilities(model.project(B, env, sliders, trend_discount))
    s = senate_model.project(main.SENATE_BUNDLE, env, sliders, trend_discount)
    senate = add_senate_win_probabilities(s, s["summary"]["not_up_d"], s["summary"]["not_up_r"])
    # National margin: 2024-turnout-weighted mean of every district's projection
    # before the CA lockout override.
    pre_lockout = (B.base_margin + B.rel_trend * trend_discount + house["uniform_swing"]
                   + np.array([d["demo_shift"] for d in house["districts"]]))
    return {"house": house, "senate": senate, "national_margin": float(pre_lockout @ B.turnout_w)}


def metrics(r: dict) -> dict:
    hs, ss = r["house"]["summary"], r["senate"]["summary"]
    hd, sd = hs["seat_distribution"], ss["seat_distribution"]
    return {
        "national_margin": round(r["national_margin"], 2),
        "house_d_seats": hs["d_seats"], "house_median": hd["d_median"],
        "house_p10": hd["d_p10"], "house_p90": hd["d_p90"],
        "house_p_d_majority": hd["p_d_majority"],
        "senate_d_seats": ss["final_d"], "senate_median": sd["d_median"],
        "senate_p_d_control": sd.get("p_d_control", sd["p_d_majority"]),
    }


def main_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    r = run()
    row = {"label": args.label, **metrics(r), "diagnostics": args.note}
    (OUT_DIR / "runs").mkdir(exist_ok=True)
    (OUT_DIR / "runs" / f"{args.label}.json").write_text(json.dumps(
        {"metrics": row, "house": r["house"], "senate": r["senate"]}))
    new = not TABLE.exists()
    with TABLE.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)
    print(json.dumps(row, indent=1))


if __name__ == "__main__":
    main_cli()
