"""Item 7 check: reconciling shifts of the county overlay.

For every House district (its county slices) and every state (its counties,
reconciled to the Senate seat or, with no race, to the state's fundamentals),
the reconciling shift is what's left after projecting each slice from its own
pieces. It decomposes exactly into

  reconcile = (target 2024 margin − vote-weighted slice 2024 margins)
            + (target demographic shift − slices' average)
            + trend weight × (target residual − slices' average residual)
            + override (poll-based Senate races: poll target − model projection)

and anything above 0.5 points is flagged, since it means the slice inputs and
the district / state inputs disagree upstream.

Usage (from backend/): python3 analysis/overlay_check.py > analysis/overlay_check.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main  # noqa: E402
import overlay  # noqa: E402
import senate_model  # noqa: E402
from config import DEFAULT_SETTINGS, DEFAULT_TREND_WEIGHT  # noqa: E402
from environment import default_scenario  # noqa: E402
from model import demographic_shift, electorate_shares, population_shares, project  # noqa: E402

FLAG = 0.5
S, TD, FRAME = DEFAULT_SETTINGS, DEFAULT_TREND_WEIGHT, "race"


def wavg(x, w):
    w = np.asarray(w, dtype=float)
    return float(np.asarray(x, dtype=float) @ w / w.sum())


def districts():
    d = default_scenario(S)
    house = project(main.BUNDLE, d["wave"], d["sliders"], TD, S, FRAME)
    rows = {r["district"]: r for r in house["districts"]}
    by_state = {}
    for c in main.COUNTY_BUNDLE.counties:
        by_state.setdefault(c["state"], []).append(c)
    terms = {st: overlay.CountyTerms(cs, population_shares(cs), d["sliders"], S, FRAME)
             for st, cs in by_state.items()}
    out = []
    for did, slices in main._DISTRICT_COUNTY_SLICES.items():
        drow, st = rows[did], did[:2]
        if st not in terms:   # no county rows (CT: planning regions) — slices use district values
            terms[st] = overlay.CountyTerms([], population_shares([]), d["sliders"], S, FRAME)
        r = overlay.district_slices(did, drow, slices, house["uniform_swing"], terms[st], TD, S, FRAME)
        w = [s["total_2024"] for s in r["counties"]]
        parts = {
            "margin": drow["margin_2024"] - wavg([s["margin_2024"] for s in slices], w),
            "demo": (drow.get("demo_shift") or 0.0) - wavg([s["demo_shift"] for s in r["counties"]], w),
            "trend": TD * (r["district_residual"] - wavg([s["residual_trend"] for s in r["counties"]], w)),
        }
        est = all(s.get("pres_year_source") == 2020 for s in slices)
        out.append((did, r["reconcile"], parts, est, drow.get("lockout")))
    return out


def states():
    d = default_scenario(S)
    sb = main.SENATE_BUNDLE
    sen = senate_model.project(sb, d["wave"], d["sliders"], TD, S, FRAME)
    seats = {s["state"]: s for s in sen["seats"]}
    resid, center = senate_model.all_state_residuals(sb, S, FRAME)
    swing = d["wave"] - senate_model.PRES_2024_POPVOTE
    out = []
    for j, s in enumerate(sb.states):
        st = s["state"]
        counties = [c for c in main.COUNTY_BUNDLE.counties if c["state"] == st]
        if not counties:
            continue
        pop_j = {g: v[j:j + 1] for g, v in sb.all_pop.items()}
        demo_state = float(sum(demographic_shift(electorate_shares(pop_j, S), d["sliders"], S)[0].values())[0])
        model_target = (s.get("presidential_margin_2024") or 0.0) + TD * resid[st] + swing + demo_state
        seat = seats.get(st)
        cand = 0.0
        target = model_target
        override = 0.0
        if seat is not None:
            cand = ((seat.get("war_adj_discounted") or 0.0) + (seat.get("incumbency_adj") or 0.0)
                    + (seat.get("challenger_adj") or 0.0))
            target = seat["projection"]
            override = target - seat["model_projection"] if seat.get("poll_weight") else 0.0
        terms = overlay.CountyTerms(counties, population_shares(counties), d["sliders"], S, FRAME, center)
        r = overlay.state_counties(st, counties, terms, resid[st], swing, cand, target, TD, S)
        w = [c.get("total_2024") or 0.0 for c in counties]
        res = [x[3] for x in r["rows"]]
        parts = {
            "margin": (s.get("presidential_margin_2024") or 0.0) - wavg([c.get("margin_2024") or 0.0 for c in counties], w),
            "demo": demo_state - wavg([x[4] for x in r["rows"]], w),
            "trend": TD * (resid[st] - wavg(res, w)),
            "override": override,
        }
        out.append((st, r["reconcile"], parts, seat is not None, bool(seat and seat.get("poll_weight"))))
    return out


def main_cli():
    print(f"settings: shrink k = {S.overlay_shrink_k:,.0f} votes; trend weight {TD}; frame {FRAME}")
    dist = districts()
    print(f"\n== House districts ({len(dist)}): reconciling shift = margin + demographic + trend parts")
    print(f"  {'district':8} {'shift':>6} {'margin':>7} {'demo':>6} {'trend':>6}  notes")
    for did, rec, p, est, lock in sorted(dist, key=lambda x: -abs(x[1]))[:25]:
        notes = []
        if abs(rec) > FLAG:
            notes.append("FLAG")
        if est:
            notes.append("estimated slices")
        if lock:
            notes.append(f"locked {lock} (reconciled to pre-lock projection)")
        print(f"  {did:8} {rec:+6.2f} {p['margin']:+7.2f} {p['demo']:+6.2f} {p['trend']:+6.2f}  {' · '.join(notes)}")
    recs = np.array([abs(r) for _, r, *_ in dist])
    print(f"  |shift| median {np.median(recs):.2f}, 90th pct {np.quantile(recs, 0.9):.2f}; "
          f"{int((recs > FLAG).sum())} of {len(dist)} above {FLAG}")
    parts = {k: np.array([p[k] for _, _, p, *_ in dist]) for k in ("margin", "demo", "trend")}
    upstream = [did for did, _, p, *_ in dist if abs(p["margin"]) > FLAG]
    est = {did for did, _, _, e, _ in dist if e}
    single = [did for did, *_ in dist if len(main._DISTRICT_COUNTY_SLICES[did]) == 1]
    print(f"  mean |part|: margin {np.abs(parts['margin']).mean():.2f}, demographic "
          f"{np.abs(parts['demo']).mean():.2f}, trend {np.abs(parts['trend']).mean():.2f}")
    print(f"  Upstream data mismatch (slices' 2024 margins vs the district's, |margin part| > {FLAG}): "
          f"{len(upstream)} districts, {sum(d in est for d in upstream)} of them in the estimated-slice states:\n"
          f"    {', '.join(upstream)}")
    print(f"  The demographic and trend parts come from slices taking their parent county's shares and\n"
          f"  residual (option (a)): in counties split among several districts every slice gets the county\n"
          f"  average. Of the {len(single)} districts inside a single county, "
          f"{sum(abs(r) > FLAG for d, r, *_ in dist if d in single)} have shifts above {FLAG} for that reason alone.")

    sts = states()
    print(f"\n== States ({len(sts)}): reconciled to the Senate seat, or the state's fundamentals with no race")
    print(f"  {'state':5} {'shift':>6} {'margin':>7} {'demo':>6} {'trend':>6} {'override':>8}  notes")
    for st, rec, p, has_seat, ov in sorted(sts, key=lambda x: -abs(x[1])):
        notes = []
        if abs(rec - p["override"]) > FLAG:
            notes.append("FLAG")
        if ov:
            notes.append("poll blend (expected)")
        if not has_seat:
            notes.append("no 2026 race")
        print(f"  {st:5} {rec:+6.2f} {p['margin']:+7.2f} {p['demo']:+6.2f} {p['trend']:+6.2f} {p['override']:+8.2f}  "
              f"{' · '.join(notes)}")
    flagged = [st for st, rec, p, *_ in sts if abs(rec - p["override"]) > FLAG]
    print(f"  states flagged (|shift excluding override| > {FLAG}): {', '.join(flagged) or 'none'}")
    print("  The state shifts are mostly the trend part: counties' 2020→2024 shifts, averaged with 2024\n"
          "  turnout weights, don't add up to the state's own shift (the turnout-composition offset also\n"
          "  seen in the item 8 cross-level check). The margin part is ~0 now that county margins are\n"
          "  total-vote margins.")


if __name__ == "__main__":
    main_cli()
