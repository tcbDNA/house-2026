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
from environment import (  # noqa: E402
    CSV_PATH, EDU_GROUPS, GROUPS, OTHER_BASELINE, PRES_2024_POPVOTE, default_scenario, estimate,
    load_polls,
)
from model import CATALIST_BASELINES  # noqa: E402


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
            overrides[k] = ast.literal_eval(v)
    return csv_path, settings_from(overrides)


def main():
    csv_path, settings = parse_args(sys.argv[1:])
    polls = load_polls(csv_path)
    est = estimate(polls, settings)
    eq = estimate(polls, settings, equal_weights=True)

    print(f"settings: white share {settings.effective_white_share:.4f}"
          f"{'' if settings.white_share_enabled else ' (target off: Catalist 2022 fit)'}")
    print(f"{len(polls)} polls: " + ", ".join(
        f"{k} ({v['end']}, {v['population'].upper()}, n={v['n']})"
        for k, v in sorted(polls.items(), key=lambda kv: kv[1]['end'], reverse=True)))
    print()
    print(f"{'group':10} {'polls':>5} {'share':>6} {'avg margin':>11} {'2024':>7} {'shift':>7} {'contrib':>8}")
    for g in GROUPS + ("other",):
        m = est["margins"][g]
        base = CATALIST_BASELINES.get(g, OTHER_BASELINE)
        tag = " (imputed)" if est["imputed"].get(g) else ""
        print(f"{g:10} {est['n_polls'].get(g, 0):>5} {est['shares'][g]:>6.3f} {fmt(m):>11} "
              f"{fmt(base):>7} {m - base:>+7.1f} {est['contributions'][g]:>+8.2f}{tag}")
    print()
    print(f"Share-weighted shift since 2024:                     {est['shift']:+.2f}")
    print(f"Generic ballot = 2024 result {fmt(PRES_2024_POPVOTE)} + shift:          {fmt(est['environment'])}"
          f"  (unrounded {est['environment']:+.2f})")
    print(f"  equal-weight-per-pollster version:                 {fmt(eq['environment'])}")
    print(f"Same polls' topline average (two-way):               {fmt(est['topline'])}")
    print(f"Alt: margins applied to these electorate shares:     {fmt(est['environment_on_composition'])}"
          f"  (2024 margins on them: {fmt(est['baseline_on_composition'])})")

    print()
    print(f"{'race x edu':22} {'polls':>5} {'avg margin':>11} {'2024':>7} {'shift':>7}")
    for g in EDU_GROUPS:
        m, base = est["edu_margins"][g], CATALIST_BASELINES[g]
        tag = " (imputed: 2024 + non-white shift)" if est["edu_imputed"].get(g) else ""
        print(f"{g:22} {est['n_polls'][g]:>5} {fmt(m):>11} {fmt(base):>7} {m - base:>+7.1f}{tag}")

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
