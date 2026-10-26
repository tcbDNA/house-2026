"""Market-implied 2026 turnout per race, from Kalshi's "Midterm Voter Turnout"
markets (series KXMIDTERMVOTETURN: "Will the total vote count for all
participants in <race> be above X?"), saved under
sources/turnout_2026/kalshi_markets_KXMIDTERMVOTETURN_p*.json.

For each race: the mid of the yes bid / ask of every threshold with a
two-sided quote, made non-increasing in the threshold (pool-adjacent-
violators), then the threshold where P(total > X) crosses 0.5 by linear
interpolation = the market's median total vote. Ratio = that / the race's
2024 presidential vote (state results for Senate and governor races; the
precinct-based district totals for House races).

Writes turnout_2026.csv (one row per race) and prints the national ratio
(2024-vote-weighted across House races with a usable median), which is the
default for any geography without its own market.

Usage (from backend/data/): python3 build_turnout_2026.py
"""
from __future__ import annotations

import csv
import glob
import json
import re
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parent
SRC = DATA / "sources" / "turnout_2026"
OUT = DATA / "turnout_2026.csv"


def pava_decreasing(ys: list[float]) -> list[float]:
    """Least-squares non-increasing fit (pool adjacent violators)."""
    blocks = []   # [sum, count]
    for y in ys:
        blocks.append([y, 1])
        while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] < blocks[-1][0] / blocks[-1][1]:
            s, c = blocks.pop()
            blocks[-1][0] += s; blocks[-1][1] += c
    out = []
    for s, c in blocks:
        out += [s / c] * c
    return out


def implied_median(points: list[tuple[float, float]]) -> tuple[float | None, str]:
    """points: (threshold, P(total > threshold)). Returns (median, note)."""
    if len(points) < 2:
        return None, "fewer than 2 quoted thresholds"
    points.sort()
    xs = [x for x, _ in points]
    ps = pava_decreasing([p for _, p in points])
    if ps[0] < 0.5:
        return None, f"median below the lowest quoted threshold ({xs[0]:,.0f})"
    if ps[-1] > 0.5:
        return None, f"median above the highest quoted threshold ({xs[-1]:,.0f})"
    for (x0, p0), (x1, p1) in zip(zip(xs, ps), zip(xs[1:], ps[1:])):
        if p0 >= 0.5 >= p1:
            if p0 == p1:
                return (x0 + x1) / 2, ""
            return x0 + (p0 - 0.5) / (p0 - p1) * (x1 - x0), ""
    return None, "no crossing"


def race_geography(code: str) -> tuple[str, str, str]:
    """Kalshi race code -> (kind, state, district id or '')."""
    st, rest = code[:2], code[2:]
    if rest == "SEN":
        return "senate", st, ""
    if rest == "GOV":
        return "governor", st, ""
    if rest == "AL":
        return "house", st, f"{st}-AL"
    if rest.isdigit():
        return "house", st, f"{st}-{rest}"
    return "other", st, ""


def main():
    markets = [m for f in sorted(glob.glob(str(SRC / "kalshi_markets_KXMIDTERMVOTETURN_p*.json")))
               for m in json.load(open(f))["markets"]]
    by_race: dict[str, list] = defaultdict(list)
    updated = ""
    for m in markets:
        code = m["ticker"].split("-")[1]
        try:
            x = float(m["floor_strike"])
            bid, ask = float(m["yes_bid_dollars"]), float(m["yes_ask_dollars"])
        except (TypeError, ValueError, KeyError):
            continue
        updated = max(updated, m.get("updated_time") or "")
        if 0.0 < bid <= ask < 1.0:   # two-sided quote
            by_race[code].append((x, (bid + ask) / 2))

    state_votes = {r["state"]: float(r["total_2024"]) for r in csv.DictReader((DATA / "state_pres_results.csv").open())}
    slices = json.loads((DATA / "district_county_slices.json").read_text())
    district_votes = {d: float(sum(s["total_2024"] for s in rows)) for d, rows in slices.items()}

    codes = sorted({m["ticker"].split("-")[1] for m in markets})
    rows = []
    for code in codes:
        kind, st, did = race_geography(code)
        median, note = implied_median(by_race.get(code, []))
        base = district_votes.get(did) if kind == "house" else state_votes.get(st)
        ratio = median / base if median and base else None
        rows.append({"race": code, "kind": kind, "state": st, "district": did,
                     "implied_total_votes": round(median) if median else "",
                     "quoted_thresholds": len(by_race.get(code, [])),
                     "total_2024": round(base) if base else "",
                     "ratio_to_2024": round(ratio, 4) if ratio else "", "note": note})
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    house = [r for r in rows if r["kind"] == "house" and r["ratio_to_2024"] != ""]
    nat = sum(r["implied_total_votes"] for r in house) / sum(r["total_2024"] for r in house)
    ok = {k: sum(1 for r in rows if r["kind"] == k and r["ratio_to_2024"] != "") for k in ("senate", "governor", "house")}
    tot = {k: sum(1 for r in rows if r["kind"] == k) for k in ("senate", "governor", "house")}
    print(f"markets last updated {updated}; races with a usable median: " +
          ", ".join(f"{k} {ok[k]}/{tot[k]}" for k in ok))
    print(f"national ratio (House races, 2024-vote-weighted): {nat:.3f}")
    for k in ("senate",):
        for r in rows:
            if r["kind"] == k:
                print(f"  {r['race']:6} implied {r['implied_total_votes'] or '-':>11} vs 2024 {r['total_2024']:>11}  "
                      f"ratio {r['ratio_to_2024'] or '-':>6}  {r['note']}")


if __name__ == "__main__":
    main()
