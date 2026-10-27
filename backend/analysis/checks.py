"""Item 8 checks.

1. Calibration: with the sliders at their 2024 values, the 2024-turnout-
   weighted average of the 435 district margins equals the uniform wave.
2. Cross-level (House vs Senate, every state): fundamentals = 2024 margin +
   uniform swing + trend term + demographic shift, before WAR, incumbency,
   challenger effects, the California lockouts and polling overrides. Compare
   the 2024-turnout-weighted average of a state's House district fundamentals
   with its Senate (statewide) fundamentals. The House calibration creates a
   constant national offset, so each state's gap is reported net of the
   national (2024-vote-weighted) average gap; |net gap| > 0.5 is flagged.
   Single-district states should show essentially no gap.
3. National margin vs the included polls' topline average and the public
   averages (environment.comparison_lines).

Usage (from backend/): python3 analysis/checks.py > analysis/checks.txt
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main  # noqa: E402
import model  # noqa: E402
import senate_model  # noqa: E402
from config import DEFAULT_SETTINGS, DEFAULT_TREND_WEIGHT  # noqa: E402
from environment import comparison_lines, default_scenario  # noqa: E402

FLAG = 0.5


def calibration(settings=DEFAULT_SETTINGS) -> None:
    d = default_scenario(settings)
    r = model.project(main.BUNDLE, d["wave"], dict(model.CATALIST_BASELINES), DEFAULT_TREND_WEIGHT, settings)
    gap = r["national_margin"] - d["wave"]
    print("== 1. Calibration (sliders at 2024 values)")
    # national_margin is reported to 3 decimals, so allow half a unit there.
    print(f"  turnout-weighted mean of 435 district margins {r['national_margin']:+.3f} vs wave "
          f"{d['wave']:+.4f}: difference {gap:+.4f} {'OK' if abs(gap) <= 5e-4 else 'FAIL'}")


def senate_all_states_bundle() -> senate_model.SenateBundle:
    """The Senate bundle's statewide fundamentals for every state (no WAR,
    incumbency, challenger or polling override)."""
    b = main.SENATE_BUNDLE
    pres = np.array([s.get("presidential_margin_2024") or 0.0 for s in b.states], dtype=float)
    return senate_model.SenateBundle(
        states=b.states, seats=b.states, base_margin=pres, state_trend=b.all_trend,
        battleground=b.all_battleground, pop=b.all_pop, all_trend=b.all_trend,
        all_battleground=b.all_battleground, all_pop=b.all_pop, all_votes_w=b.all_votes_w,
        poll_margin=np.full(len(b.states), np.nan), poll_n=np.zeros(len(b.states)),
        independent=np.zeros(len(b.states), dtype=bool))


def cross_level(settings=DEFAULT_SETTINGS, frame: str = "race") -> None:
    d = default_scenario(settings)
    env, sliders = d["wave"], d["sliders"]
    house = model.project(main.BUNDLE, env, sliders, DEFAULT_TREND_WEIGHT, settings, frame)
    swing = house["uniform_swing"]
    w = main.BUNDLE.turnout_weights(settings)
    by_state: dict[str, list[tuple[float, dict]]] = defaultdict(list)
    for i, row in enumerate(house["districts"]):
        by_state[row["state"]].append((w[i], row))

    sb = senate_all_states_bundle()
    sen, _, _, sen_demo, sen_trend, _ = senate_model._projections(sb, env, sliders, DEFAULT_TREND_WEIGHT,
                                                                    settings, frame)
    idx = {s["state"]: i for i, s in enumerate(sb.states)}
    votes = dict(zip([s["state"] for s in sb.states], sb.all_votes_w))

    rows = []
    for st, pts in by_state.items():
        ws = np.array([p[0] for p in pts]); ws = ws / ws.sum()
        avg = lambda k: float(sum(wi * r[k] for wi, (_, r) in zip(ws, pts)))  # noqa: E731
        house_f = avg("margin_2024") + swing + avg("rel_trend_applied") + avg("demo_shift")
        j = idx[st]
        rows.append((st, len(pts), house_f, float(sen[j]), house_f - float(sen[j]),
                     avg("margin_2024") - float(sb.base_margin[j]), avg("rel_trend_applied") - float(sen_trend[j])))
    national = sum(votes[r[0]] * r[4] for r in rows) / sum(votes[r[0]] for r in rows)
    print(f"\n== 2. Cross-level check, House vs Senate fundamentals (frame {frame})")
    print(f"  national average gap (House − Senate, 2024-vote-weighted): {national:+.2f}; net gap = gap − that")
    print(f"  {'state':5} {'districts':>9} {'House':>8} {'Senate':>8} {'gap':>7} {'net gap':>8} "
          f"{'2024 margin part':>16} {'trend part':>10}")
    flagged = []
    for st, n, h, s, g, mg, tr in sorted(rows, key=lambda r: -abs(r[4] - national)):
        net = g - national
        flag = abs(net) > FLAG
        if flag:
            flagged.append(st)
        print(f"  {st:5} {n:9d} {h:+8.2f} {s:+8.2f} {g:+7.2f} {net:+8.2f} {mg:+16.2f} {tr:+10.2f}"
              f"{'  FLAG' if flag else ''}")
    single = [(r[0], r[4] - national) for r in rows if r[1] == 1]
    print(f"  single-district states, net gap: " + ", ".join(f"{st} {v:+.2f}" for st, v in sorted(single)))
    print(f"  flagged (|net gap| > {FLAG}): {flagged or 'none'}")
    print("  Note: single-district states all sit at the same net gap because the national average\n"
          "  includes the House trend's turnout-composition offset: each district's 2020→2024 shift,\n"
          "  averaged over a state with 2024 turnout weights, differs from the state's own shift by\n"
          "  Σ(w2024 − w2020)·m2020. At-large states have none; the flagged states have the least.")


def averages(settings=DEFAULT_SETTINGS) -> None:
    d = default_scenario(settings)
    house = model.project(main.BUNDLE, d["wave"], d["sliders"], DEFAULT_TREND_WEIGHT, settings)
    print("\n== 3. National margin vs averages")
    for line in comparison_lines(house["national_margin"], d["poll_topline_average"], d["public_averages"]):
        print("  " + line)


if __name__ == "__main__":
    calibration()
    cross_level()
    averages()
