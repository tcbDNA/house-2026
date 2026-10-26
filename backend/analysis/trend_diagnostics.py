"""Item 2 diagnostics: trend regression fits and what residualizing changes.

Usage (from backend/): python3 analysis/trend_diagnostics.py > analysis/trend_diagnostics.txt
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main  # noqa: E402
import model  # noqa: E402
import trend  # noqa: E402
from analysis.compare import metrics, run  # noqa: E402
from config import DEFAULT_SETTINGS  # noqa: E402

S = DEFAULT_SETTINGS
OFF = replace(S, trend_remove_demographic=False, trend_remove_battleground=False)


def fmt_fit(f: trend.TrendFit) -> str:
    return "  ".join(f"{n}={b:+.2f}({s:.2f})" for n, b, s in zip(f.names, f.beta, f.se))


def main_cli():
    wt = model.white_target(S)
    print("== Trend regressions (WLS, weights = 2024 votes; coef(SE); y = 2020→2024 trend vs nation)")
    for frame in trend.FRAMES:
        with_bg = model.trend_fit(frame, wt, True, True)
        no_bg = model.trend_fit(frame, wt, True, False)
        se, hc1 = with_bg.coef_se("battleground")
        print(f"\n[{frame}] n={with_bg.n}  R² with battleground {with_bg.r2:.3f}, without {no_bg.r2:.3f}")
        print(f"  battleground coefficient {with_bg.coef('battleground'):+.3f}  SE {se:.3f}  (HC1 {hc1:.3f})")
        print(f"  {fmt_fit(with_bg)}")
        no_age = model.trend_fit(frame, wt, False, True)
        print(f"  without age shares: R² {no_age.r2:.3f}; battleground {no_age.coef('battleground'):+.3f}")

    base = run(OFF)
    full = run(S)
    print("\n== Headline metrics")
    for label, s in [("raw trend (both parts kept)", OFF), ("residualized (default)", S),
                     ("remove demographic part only", replace(S, trend_remove_battleground=False)),
                     ("remove battleground part only", replace(S, trend_remove_demographic=False)),
                     ("residualized, basis without age", replace(S, trend_include_age=False))]:
        print(f"  {label:34} {metrics(run(s))}")

    rows = main.BUNDLE.districts
    hisp_pop = {r["district"]: r.get("pct_hispanic") or 0.0 for r in rows}
    hisp_el = dict(zip([r["district"] for r in rows],
                       model.electorate_shares(main.BUNDLE.pop, S)["hispanic"] * 100))
    b = {d["district"]: d for d in base["house"]["districts"]}
    ch = sorted(((d["projection"] - b[d["district"]]["projection"], d) for d in full["house"]["districts"]
                 if abs(d["projection"]) < 99.5), key=lambda x: -abs(x[0]))
    print("\n== 15 districts whose projections change most (residualized − raw trend)")
    print(f"  {'district':8} {'change':>7} {'raw':>7} {'resid':>7} {'Hisp % pop':>10} {'Hisp % electorate':>17} {'BG':>3}")
    for delta, d in ch[:15]:
        print(f"  {d['district']:8} {delta:+7.2f} {b[d['district']]['projection']:+7.1f} {d['projection']:+7.1f} "
              f"{hisp_pop[d['district']]:10.1f} {hisp_el[d['district']]:17.1f} "
              f"{'Y' if d['state'] in trend.BATTLEGROUND_STATES else '':>3}")
    flips = [(d["district"], b[d["district"]]["projection"], d["projection"])
             for _, d in ch if (d["projection"] > 0) != (b[d["district"]]["projection"] > 0)]
    print(f"  seats changing side: {[(k, round(x, 1), round(y, 1)) for k, x, y in flips]}")

    sb = {s["state"]: s for s in base["senate"]["seats"]}
    sh = {s["state"]: s for s in main.SENATE_BUNDLE.seats}
    sch = sorted(((s["projection"] - sb[s["state"]]["projection"], s) for s in full["senate"]["seats"]),
                 key=lambda x: -abs(x[0]))
    print("\n== 10 Senate races whose projections change most")
    print(f"  {'state':5} {'change':>7} {'raw':>7} {'resid':>7} {'Hisp % pop':>10} {'BG':>3}")
    for delta, s in sch[:10]:
        print(f"  {s['state']:5} {delta:+7.2f} {sb[s['state']]['projection']:+7.1f} {s['projection']:+7.1f} "
              f"{sh[s['state']].get('pct_hispanic') or 0:10.1f} "
              f"{'Y' if s['state'] in trend.BATTLEGROUND_STATES else '':>3}")

    na = run(replace(S, trend_include_age=False))
    nb = {d["district"]: d["projection"] for d in na["house"]["districts"]}
    diffs = np.array([d["projection"] - nb[d["district"]] for d in full["house"]["districts"]
                      if abs(d["projection"]) < 99.5])
    print("\n== Including age in the basis (default) vs not")
    print(f"  district projections: mean |change| {np.abs(diffs).mean():.2f}, max {np.abs(diffs).max():.2f}; "
          f"House D seats {full['house']['summary']['d_seats']} vs {na['house']['summary']['d_seats']}")


if __name__ == "__main__":
    main_cli()
