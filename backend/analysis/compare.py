"""Run the default scenario and record headline metrics for the change log.

Usage (from backend/):
  python3 analysis/compare.py --label baseline [--note "diagnostics text"]
      [--set key=value ...]   # config.Settings overrides
      [--dry-run]             # print only; don't append to the table

Appends one row to analysis/comparison.csv and writes the full House/Senate
output to analysis/runs/<label>.json. Every run uses the default scenario for
its settings (environment.default_scenario: wave + poll-average sliders,
config.DEFAULT_TREND_WEIGHT unless --trend) and the fixed Monte Carlo seed,
so rows are directly comparable.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

import main  # noqa: E402  (loads bundles exactly as the API does)
import model  # noqa: E402
from config import DEFAULT_SETTINGS, DEFAULT_TREND_WEIGHT, Settings, settings_from  # noqa: E402
from environment import comparison_lines, default_scenario  # noqa: E402
import senate_model  # noqa: E402
from probability import add_senate_win_probabilities, add_win_probabilities  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent
TABLE = OUT_DIR / "comparison.csv"
FIELDS = ["label", "national_margin", "house_d_seats", "house_median", "house_p10", "house_p90",
          "house_p_d_majority", "senate_d_seats", "senate_median", "senate_p_d_control", "diagnostics"]


def run(settings: Settings = DEFAULT_SETTINGS, env: float | None = None,
        sliders: dict | None = None, trend_discount: float = DEFAULT_TREND_WEIGHT,
        frame: str = "race") -> dict:
    defaults = default_scenario(settings)
    env = defaults["wave"] if env is None else env
    sliders = defaults["sliders"] if sliders is None else sliders
    B = main.BUNDLE
    house = add_win_probabilities(model.project(B, env, sliders, trend_discount, settings, frame),
                                  terms=main._terms("house", settings, frame))
    s = senate_model.project(main.SENATE_BUNDLE, env, sliders, trend_discount, settings, frame)
    senate = add_senate_win_probabilities(s, s["summary"]["not_up_d"], s["summary"]["not_up_r"],
                                          terms=main._terms("senate", settings, frame))
    # National margin: 2024-turnout-weighted mean of every district's projection
    # before the CA lockout override (computed by the model).
    return {"house": house, "senate": senate, "national_margin": house["national_margin"]}


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
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--trend", type=float, default=DEFAULT_TREND_WEIGHT, help="trend weight")
    args = ap.parse_args()

    overrides = {}
    for kv in args.set:
        k, v = kv.split("=", 1)
        try:
            overrides[k] = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            overrides[k] = v   # bare string, e.g. group_baseline=pew_validated
    settings = settings_from(overrides)
    r = run(settings, trend_discount=args.trend)
    d = default_scenario(settings)
    for line in comparison_lines(r["national_margin"], d["poll_topline_average"], d["public_averages"]):
        print(line, file=sys.stderr)
    row = {"label": args.label, **metrics(r), "diagnostics": args.note}
    if args.dry_run:
        print(json.dumps(row, indent=1))
        return
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
