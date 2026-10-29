"""Governor projection report: each race's model projection, polling average
(effective poll count), blend weight, final projection, P(D win) and flags,
and the governorships after the election. Optional KEY=VALUE settings overrides.

Usage (from backend/): python3 analysis/governor_projection.py [key=value ...] > analysis/governor_projection.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from fastapi.testclient import TestClient  # noqa: E402
import main  # noqa: E402


def parse(v: str):
    return (v == "true") if v in ("true", "false") else float(v)


def main_cli():
    over = {k: parse(v) for k, v in (a.split("=") for a in sys.argv[1:])}
    r = TestClient(main.app).post("/api/governors/project", json={"settings": over} if over else {}).json()
    s, g = r["summary"], r["summary"]["governorships"]
    print(f"Governors, settings overrides: {over or 'none (defaults)'}")
    print(f"Projected winners: D {s['d_up']} + {s['not_up_d']} not up = {s['d_up'] + s['not_up_d']}, "
          f"R {s['r_up']} + {s['not_up_r']} = {s['r_up'] + s['not_up_r']}, I {s['i_up'] + s['not_up_i']}; "
          f"D pickups {s['d_pickups']}, R pickups {s['r_pickups']}, I pickups {s['i_pickups']}")
    print(f"Simulated D governorships: median {g['d_median']}, 80% range {g['d_p10']}-{g['d_p90']}; "
          f"P(D majority, 26+) {g['p_d_majority']:.3f}, P(R majority) {g['p_r_majority']:.3f}\n")
    print(f"{'st':3} {'model':>7} {'polls (n_eff)':>15} {'w':>5} {'proj':>7} {'P(D)':>6}  flags / opponent")
    for x in sorted(r["races"], key=lambda x: x["projection"]):
        pa, mp = x["poll_average"], x["model_projection"]
        flags = [f["code"] + ("!" if f.get("risk") else "") for f in x["flags"]]
        if x["flip"]:
            flags.append(f"flip {x['flip']}")
        if x["opponent_party"] != "(R)":
            flags.append(f"vs {x['opponent']} {x['opponent_party']}")
        if x.get("three_way"):
            flags.append("three-way P(win): " + ", ".join(f"{c['name'].split()[-1]} {c['p']:.3f}"
                                                         for c in x["three_way"]["candidates"]))
        print(f"{x['state']:3} {('%+7.1f' % mp) if mp is not None else '    n/a'} "
              f"{('%+7.1f (%g)' % (pa['margin'], pa['n_eff'])) if pa else '-':>15} {x['poll_weight']:5.2f} "
              f"{x['projection']:+7.1f} {x['p_d']:6.3f}  {', '.join(flags)}")


if __name__ == "__main__":
    main_cli()
