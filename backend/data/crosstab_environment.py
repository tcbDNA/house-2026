"""Print the crosstab-based generic-ballot estimate and the default scenario.

The estimation itself lives in backend/environment.py (the API computes the
default scenario from it at runtime). This script prints the per-group table
for a given settings value, e.g.

  python3 crosstab_environment.py                      # default settings
  python3 crosstab_environment.py white_share=0.76     # override settings
  python3 crosstab_environment.py --csv other.csv white_share_enabled=False

Reads generic_ballot_crosstabs.csv (one row per poll × group, including a
"topline" row per poll). Each poll's numbers are converted to two-way margins
(100 × (D − R) / (D + R)) so pollsters' differing undecided rates don't distort
the average, and to match the two-way Catalist slider baselines.

  - One poll per pollster (the CSV should hold only each pollster's latest
    poll with a race breakdown).
  - Polls are weighted by √n, with n capped at 2000.
  - A group needs crosstabs from at least MIN_POLLS (2) pollsters; otherwise
    (and for "other" race, which polls don't report consistently) it's set to
    its Catalist 2024 margin plus the share-weighted average shift of the
    groups that do have data.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import settings_from  # noqa: E402
from model import demo_key  # noqa: E402
from environment import (  # noqa: E402
    CSV_2024_PATH, CSV_PATH, EDU_GROUPS, GROUPS, LOO_THRESHOLD, PRES_2024_POPVOTE, WHITE_EDU,
    default_scenario, estimate, included_polls, load_polls,
)


def fmt(m: float) -> str:
    return f"{'D' if m >= 0 else 'R'}+{abs(m):.1f}"


def parse_args(argv: list[str]):
    csv_path, overrides = CSV_PATH, {}
    it = iter(argv)
    for a in it:
        if a == "--csv":
            csv_path = Path(next(it))
        else:
            k, v = a.split("=", 1)
            try:
                overrides[k] = ast.literal_eval(v)
            except (ValueError, SyntaxError):
                overrides[k] = v
    return csv_path, settings_from(overrides)


def main():
    csv_path, settings = parse_args(sys.argv[1:])
    polls = included_polls(load_polls(csv_path, demo_key(settings)), settings)
    est = estimate(polls, settings)
    eq = estimate(polls, settings, equal_weights=True)
    base = est["baselines"]

    print(f"settings: white share {settings.effective_white_share:.4f}"
          f"{'' if settings.white_share_enabled else ' (target off: Catalist 2022 fit)'}; "
          f"2024 baseline {settings.group_baseline}; "
          f"{'subgroup' if settings.subgroup_n_weights else 'total'}-n weights; "
          f"pollster-matched shifts {'on' if settings.pollster_matched_shifts else 'off'}")
    print(f"{len(polls)} polls: " + ", ".join(
        f"{k} ({v['end']}, {v['population'].upper()}, n={v['n']})"
        for k, v in sorted(polls.items(), key=lambda kv: kv[1]['end'], reverse=True)))
    polls_2024 = load_polls(CSV_2024_PATH, demo_key(settings))
    for label, ps in (("2026", polls), ("2024", polls_2024)):
        for src, how in (("moe", "derived from published MOEs, n × (MOE_total/MOE_group)²"),
                         ("share", "estimated as total n × electorate share")):
            got = {k: sorted(g for g, s in v["group_n_source"].items() if s == src) for k, v in ps.items()}
            got = {k: g for k, g in got.items() if g}
            if got:
                print(f"{label} subgroup n {how}: " + "; ".join(
                    f"{k} " + ", ".join(f"{g} {ps[k]['group_n'][g]:.0f}" for g in gs) for k, gs in got.items()))
    print()
    print("Current method (S): 2026 poll average − 2024 baseline")
    print(f"{'group':10} {'polls':>5} {'share':>6} {'avg margin':>11} {'2024':>7} {'shift':>7}")
    for g in GROUPS + ("other",):
        tag = " (imputed: average shift)" if est["imputed"].get(g) else ""
        avg = fmt(est["margins"][g]) if g in est["margins"] else "-"
        print(f"{g:10} {est['n_polls'].get(g, 0):>5} {est['shares'][g]:>6.3f} {avg:>11} "
              f"{fmt(base[g]):>7} {est['current_shifts'][g]:>+7.2f}{tag}")
    print(f"S = share-weighted shift since 2024: {est['S']:+.2f}")

    if est["matched"]:
        print()
        wts = ("inverse-variance weights (1/SE_r², SE_r from both years at deff 1.5)"
               if settings.matched_inverse_variance else "√n_eff weights")
        print("Pollster-matched pattern: r = (2026 group − 2024 group) − (2026 topline − 2024 topline),")
        print(f"combined with {wts}; shift = S + (r_avg − c).")
        print(f"If leaving out one pollster moves r_avg by more than {LOO_THRESHOLD} pts, the weighted median is used"
              f"{'' if settings.matched_median_fallback else ' (fallback OFF)'}.")
        print(f"{'group':18} {'old shift':>9} {'new shift':>9} {'r_avg':>7} {'SE':>5} {'mean':>7} {'median':>7} "
              f"{'max LOO':>7} {'pooled n_eff':>12}  method")
        rows = [(g, est["current_shifts"][g], est["shifts"][g]) for g in GROUPS] + \
               [(g, est["edu_current_shifts"][g], est["edu_shifts"][g]) for g in WHITE_EDU]
        for g, old, new in rows:
            m = est["matched"][g]
            if m["r_avg"] is None:
                print(f"{g:18} {old:>+9.2f} {new:>+9.2f}  (no matched pollsters)")
                continue
            note = m["method"] + (" [FLAGGED]" if m["method"] == "weighted median" else "")
            if abs(new - old) < 1e-9:
                note += "  [kept current method]"
            if m["missing"]:
                note += f"  [no 2024 pair: {', '.join(m['missing'])}]"
            print(f"{g:18} {old:>+9.2f} {new:>+9.2f} {m['r_avg']:>+7.2f} {m['se']:>5.2f} {m['r_mean']:>+7.2f} "
                  f"{m['r_median']:>+7.2f} {m['max_loo']:>7.2f} {m['pooled_n']:>12.0f}  {note}")
        print()
        print("Per pollster: r (SE_r, n_eff) | r_avg with that pollster left out")
        for g, _, _ in rows:
            m = est["matched"][g]
            if not m["pollsters"]:
                continue
            print(f"  {g}:")
            for name, r, n, se, p26, p24 in m["pollsters"]:
                pop = "" if p26 == p24 else f" {p26.upper()}/{p24.upper()}"
                loo = f"{m['loo'][name]:+.2f} ({m['loo'][name] - m['r_mean']:+.2f})" if name in m["loo"] else "-"
                print(f"    {name:20} {r:+6.1f} ({se:4.1f}, {n:5.0f}){pop}  | {loo}")
        print(f"{'other':18} {est['current_shifts']['other']:>+9.2f} {est['shifts']['other']:>+9.2f}"
              f"       -            -  (keeps S)")
        print(f"c (race frame) = {est['c']:+.2f}" + (f"; c (race × edu, white cells) = {est['c_edu']:+.2f}"
                                                   if est["c_edu"] is not None else ""))
        print("race × edu non-white cells (current rule: 2024 + non-white race groups' average shift): "
              + ", ".join(f"{g} {est['edu_shifts'][g]:+.2f}" for g in EDU_GROUPS if g not in WHITE_EDU))

    print()
    print(f"Generic ballot = 2024 result {fmt(PRES_2024_POPVOTE)} + shift: {fmt(est['environment'])}"
          f"  (unrounded {est['environment']:+.2f})")
    print(f"  equal-weight-per-pollster version:   {fmt(eq['environment'])}")
    print(f"  same polls' topline average (two-way): {fmt(est['topline'])}")
    if csv_path == CSV_PATH:
        d = default_scenario(settings)
        print()
        print("Default scenario (served by /api/defaults):")
        print(f"  uniform wave {d['wave']:+.2f} (2024 {PRES_2024_POPVOTE:+.1f} + other "
              f"{est['contributions']['other']:+.2f}); race sliders carry {d['slider_shift']:+.2f}; "
              f"total {fmt(d['total'])} ({d['total']:+.2f})")
        print("  race sliders:", {g: round(d["sliders"][g], 2) for g in GROUPS})
        print("  race x edu sliders:", {g: round(v, 2) for g, v in d["edu_frame_sliders"].items()})


if __name__ == "__main__":
    main()
