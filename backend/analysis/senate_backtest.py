"""Senate backtest, 2022 and 2024: the model's Senate structure rerun on that
year's inputs vs the final polling averages, both scored against the
official results.

Model (as in senate_model, on the inputs available before the election):

  projection = 2020 presidential margin (state, FEC)
             + 0.5 × residual trend   (state 2016→2020 shift vs the nation,
                                       demographic part removed by a vote-
                                       weighted state regression on race and
                                       age shares + battleground indicator,
                                       battleground part kept, centered)
             + uniform swing          (final generic-ballot average − 2020
                                       national presidential margin)
             + incumbency (±3.0)      (2022: FEC incumbent flag; 2024: the
                                       seat's 2018 winner running again)
             + WAR                    (Split Ticket records before that year,
                                       same blend, windows and exclusions)

Simplifications vs the 2026 model: no demographic group shifts (no crosstab
inputs for those years), today's ACS shares for the trend regression, and
the generic ballot (not the presidential race) as the 2024 environment.

Polls: RealClearPolling's final average for each race and for the generic
ballot, recomputed without Rasmussen and ActiVote (simple means of the
remaining polls in the average); compared raw and two-party (undecideds
allocated proportionally). Errors are projection − actual; the model and the
raw polls are scored against the actual total-vote margin, the two-party
polls against the actual two-party margin.

Usage (from backend/): python3 analysis/senate_backtest.py > analysis/senate_backtest.txt
"""
from __future__ import annotations

import csv
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "data"))
import senate_data as sd  # noqa: E402
import trend as trend_mod  # noqa: E402
from config import DEFAULT_SETTINGS  # noqa: E402
from model import electorate_shares, population_shares  # noqa: E402
from xlsx_table import read_sheet  # noqa: E402

SRC = BACKEND / "data" / "sources"
FEC = SRC / "fec_backtest"
POLLS = SRC / "polls_backtest"
TREND_WEIGHT = 0.5
INCUMBENCY = 3.0
EXCLUDED_POLLSTERS = ("rasmussen", "activote")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


SUFFIXES = ("jr", "sr", "ii", "iii", "iv")


def last_name(name: str) -> str:
    """Surname from 'Last, First' (FEC) or 'First Last[, Jr.]' (Clerk, Split Ticket)."""
    name = re.sub(r"\s*\(.*?\)", "", name or "").strip()
    if "," in name:
        head, tail = name.split(",", 1)
        if tail.strip().lower().strip(".") not in SUFFIXES:
            return norm(head)
        name = head
    parts = [p for p in name.split() if p.lower().strip(".") not in SUFFIXES]
    return norm(parts[-1]) if parts else ""


# ── inputs ──────────────────────────────────────────────────────────────────

def same_person(surname: str, other: str) -> bool:
    """Surname match tolerant of compound names ("Masto" vs "Cortez Masto")."""
    o = last_name(other) if (" " in other or "," in other) else norm(other)
    return bool(surname) and bool(o) and (surname == o or surname in o or o in surname)


def pres_margins() -> tuple[dict, dict, float, float]:
    m16, m20, w20 = {}, {}, {}
    d16 = r16 = t16 = 0.0
    with (FEC / "pres_2016_by_state.csv").open() as f:
        for r in csv.DictReader(f):
            d, rr, t = float(r["dem"]), float(r["rep"]), float(r["total"])
            m16[r["state"]] = 100 * (d - rr) / t
            d16, r16, t16 = d16 + d, r16 + rr, t16 + t
    d20 = r20 = t20 = 0.0
    with (BACKEND / "data" / "state_pres_results.csv").open() as f:
        for r in csv.DictReader(f):
            d, rr, t = float(r["dem_2020"]), float(r["rep_2020"]), float(r["total_2020"])
            m20[r["state"]] = 100 * (d - rr) / t
            w20[r["state"]] = t
            d20, r20, t20 = d20 + d, r20 + rr, t20 + t
    return m16, m20, 100 * (d20 - r20) / t20 - 100 * (d16 - r16) / t16, 100 * (d20 - r20) / t20, w20


def residual_trends(m16, m20, nat_shift, w20) -> dict[str, float]:
    """State 2016→2020 trend vs the nation, demographic part removed (the
    2026 model's default), battleground part kept, centered nationally."""
    import main
    sb = main.SENATE_BUNDLE
    states = [s["state"] for s in sb.states if s["state"] in m16 and s["state"] in m20]
    idx = [i for i, s in enumerate(sb.states) if s["state"] in states]
    pop = {g: v[idx] for g, v in sb.all_pop.items()}
    shares = electorate_shares(pop, DEFAULT_SETTINGS)
    y = np.array([(m20[s] - m16[s]) - nat_shift for s in states])
    bg = trend_mod.battleground(states)
    w = np.array([w20[s] for s in states])
    fit = trend_mod.fit_trend(y, shares, w, bg, "race", include_age=True, include_bg=True)
    carried = trend_mod.carried_trend(y, fit, shares, bg, remove_demographic=True, remove_battleground=False)
    carried = carried - float(carried @ w / w.sum())
    return dict(zip(states, carried.tolist()))


def results(year: int) -> dict[tuple[str, bool], dict]:
    out = {}
    with (FEC / f"senate_{year}_results.csv").open() as f:
        for r in csv.DictReader(f):
            out[(r["state"], r["special"] == "yes")] = r
    return out


def incumbents_2022() -> dict[str, set[str]]:
    rows = read_sheet(FEC / "federalelections2022.xlsx", "7. US Senate Results by State")
    out = defaultdict(set)
    for x in rows:
        if len(x) > 8 and x[5].strip() == "(I)" and x[3] == "S":
            out[x[1]].add(norm(x[7]))
    return out


def winners_2018() -> dict[str, str]:
    """state -> last name of the 2018 Senate general-election winner."""
    rows = read_sheet(FEC / "federalelections2018.xlsx", "2018 US Senate Results by State")
    best: dict[str, tuple[float, str]] = {}
    for x in rows:
        # "S", or "S-FULL TERM" where a special was also held (MN, MS 2018);
        # only full-term winners are up again six years later.
        if len(x) > 15 and x[3].startswith("S") and "UNEXPIRED" not in x[3] and x[7] and x[15]:
            try:
                v = float(x[15])
            except ValueError:
                continue
            if v > best.get(x[1], (0, ""))[0]:
                best[x[1]] = (v, norm(x[7]))
    return {st: name for st, (_, name) in best.items()}


def wars_for(year: int) -> dict:
    """Split Ticket records before `year`, windows shifted like the 2026 model's."""
    saved = dict(sd.WAR_FIRST_YEAR)
    shift = 2026 - year
    sd.WAR_FIRST_YEAR.update({k: v - shift for k, v in saved.items()})
    try:
        allw = sd.load_all_wars()
    finally:
        sd.WAR_FIRST_YEAR.clear(); sd.WAR_FIRST_YEAR.update(saved)
    return {k: [r for r in recs if r["year"] < year] for k, recs in allw.items()}


def war_effect(state: str, name: str, party: str, allw: dict) -> float:
    """D-positive margin effect of a candidate's WAR blend."""
    recs = sd.find_war(state, sd._strip_accents(sd._clean_name(name)), party, allw)
    recs = [r for r in recs or [] if r]
    if not recs:
        return 0.0
    return -sd._time_weighted_sortable(recs, candidate_name=sd._strip_accents(sd._clean_name(name)))


def races(year: int) -> list[dict]:
    """D-vs-R Senate races of `year` (Split Ticket's candidate names)."""
    out = []
    with (BACKEND / "data" / "raw_war.csv").open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["Chamber"] != "Senate" or int(r["Year"]) != year:
                continue
            geo = r["Geography"].strip()
            special = bool(re.search(r"spec", geo, re.I))
            name = re.sub(r"\s+(special election|special|spec)$", "", geo, flags=re.I).strip()
            st = sd.NAME_TO_USPS.get(name)
            if st:
                out.append({"state": st, "special": special, "dem": r["Democrat"], "rep": r["Republican"]})
    return out


def _excluded(row: dict) -> bool:
    return (row.get("excluded_pollster", "").lower() == "yes"
            or any(x in row["pollster"].lower() for x in EXCLUDED_POLLSTERS))


def poll_averages(year: int) -> tuple[dict, dict]:
    """(race key -> {d, r, n, n_excluded, published}, generic ballot)."""
    path = POLLS / f"senate_{year}_rcp_final.csv"
    by = defaultdict(lambda: {"polls": [], "avg": None})
    with path.open() as f:
        for r in csv.DictReader(f):
            key = r["state"]
            if r["pollster"].strip().lower() == "rcp average":
                by[key]["avg"] = (float(r["dem"]), float(r["rep"]))
            elif r.get("in_average", "").lower() == "yes":
                by[key]["polls"].append(r)
    out = {}
    for key, v in by.items():
        keep = [p for p in v["polls"] if not _excluded(p)]
        if not keep:
            continue
        d = sum(float(p["dem"]) for p in keep) / len(keep)
        rr = sum(float(p["rep"]) for p in keep) / len(keep)
        out[key] = {"d": d, "r": rr, "n": len(keep), "n_excluded": len(v["polls"]) - len(keep),
                    "published": v["avg"]}
    gb = {}
    with (POLLS / "generic_ballot_rcp_final.csv").open() as f:
        rows = [r for r in csv.DictReader(f) if int(r["year"]) == year]
    keep = [r for r in rows if r["pollster"].strip().lower() != "rcp average" and r.get("in_average", "").lower() == "yes"
            and not _excluded(r)]
    pub = next((r for r in rows if r["pollster"].strip().lower() == "rcp average"), None)
    gb = {"margin": sum(float(r["dem"]) - float(r["rep"]) for r in keep) / len(keep), "n": len(keep),
          "published": float(pub["dem"]) - float(pub["rep"]) if pub else None}
    return out, gb


# ── backtest ────────────────────────────────────────────────────────────────

def backtest(year: int, m16, m20, nat20, resid) -> list[dict]:
    res = results(year)
    polls, gb = poll_averages(year)
    allw = wars_for(year)
    inc22 = incumbents_2022() if year == 2022 else {}
    win18 = winners_2018() if year == 2024 else {}
    swing = gb["margin"] - nat20
    print(f"\n== {year}: generic ballot (RCP final, Rasmussen/ActiVote removed) "
          f"{gb['margin']:+.2f} from {gb['n']} polls (published {gb['published']:+.2f}); "
          f"2020 national presidential {nat20:+.2f}; uniform swing {swing:+.2f}")
    rows = []
    for race in races(year):
        st, special = race["state"], race["special"]
        r = res.get((st, special))
        if r is None:
            continue
        pkey = next((k for k in (f"{st}-special" if special else st, f"{st} special" if special else st, st)
                     if k in polls), None)
        if special and pkey == st:
            pkey = None   # don't attach the regular race's polls to a special
        d_l, r_l = last_name(race["dem"]), last_name(race["rep"])
        notes = (r.get("notes") or "").lower()
        if "not meaningful" in notes or "all-party" in notes or "jungle" in notes:
            continue   # not a D-vs-R contest (AK 2022 R vs R, LA 2022 all-party ballot)
        # The anti-R candidate may be an independent (ME 2024 King): use that
        # candidate's votes; skip if the names don't line up.
        if same_person(d_l, r.get("dem_name", "")):
            dv = float(r["dem_votes"])
        elif r.get("ind_name") and same_person(d_l, r["ind_name"]):
            dv = float(r["ind_votes"])
        else:
            continue
        if not same_person(r_l, r.get("rep_name", "")):
            continue
        if year == 2022:
            incs = inc22.get(st, ())
            inc = (INCUMBENCY if any(same_person(d_l, i) for i in incs)
                   else -INCUMBENCY if any(same_person(r_l, i) for i in incs) else 0.0)
        else:
            w = win18.get(st) if not special else None
            inc = INCUMBENCY if w and same_person(d_l, w) else -INCUMBENCY if w and same_person(r_l, w) else 0.0
        war = war_effect(st, race["dem"], "D", allw) + war_effect(st, race["rep"], "R", allw)
        proj = m20[st] + TREND_WEIGHT * resid.get(st, 0.0) + swing + inc + war
        rv, tv = float(r["rep_votes"]), float(r["total_votes"])
        actual = 100 * (dv - rv) / tv
        actual2 = 100 * (dv - rv) / (dv + rv)
        p = polls.get(pkey) if pkey else None
        rows.append({"state": st + (" (special)" if special else ""), "proj": proj, "actual": actual,
                     "actual2": actual2, "inc": inc, "war": war,
                     "poll": (p["d"] - p["r"]) if p else None,
                     "poll2": 100 * (p["d"] - p["r"]) / (p["d"] + p["r"]) if p else None,
                     "n_polls": p["n"] if p else 0, "n_excl": p["n_excluded"] if p else 0})
    return rows


def score(rows: list[dict], label: str):
    both = [r for r in rows if r["poll"] is not None]
    m = np.array([r["proj"] - r["actual"] for r in both])
    p = np.array([r["poll"] - r["actual"] for r in both])
    p2 = np.array([r["poll2"] - r["actual2"] for r in both])
    def stats(e):
        return f"MAE {np.abs(e).mean():5.2f}  RMSE {np.sqrt((e ** 2).mean()):5.2f}  bias {e.mean():+5.2f}"
    print(f"  {label}: {len(both)} races with a polling average")
    print(f"    model            {stats(m)}")
    print(f"    polls (raw)      {stats(p)}")
    print(f"    polls (2-party)  {stats(p2)}")
    closer = sum(abs(a) < abs(b) for a, b in zip(m, p2))
    print(f"    model closer than the two-party polls in {closer} of {len(both)} races")
    # Best fixed blend of model and two-party polls (least squares on actual).
    proj = np.array([r["proj"] for r in both]); poll = np.array([r["poll2"] for r in both])
    act = np.array([r["actual"] for r in both])
    lam = np.linspace(0, 1, 101)
    rmse = [np.sqrt((((1 - l) * proj + l * poll - act) ** 2).mean()) for l in lam]
    best = lam[int(np.argmin(rmse))]
    print(f"    best fixed blend: {best:.2f} × polls + {1 - best:.2f} × model (RMSE {min(rmse):.2f}); "
          f"50/50 RMSE {rmse[50]:.2f}")
    sm = float(np.polyfit(proj, act, 1)[0]); sp = float(np.polyfit(poll, act, 1)[0])
    print(f"    slope of actual on model {sm:.2f}, on two-party polls {sp:.2f}")
    return both


def main_cli():
    m16, m20, nat_shift, nat20, w20 = pres_margins()
    resid = residual_trends(m16, m20, nat_shift, w20)
    print(f"national 2016→2020 presidential shift {nat_shift:+.2f}; trend weight {TREND_WEIGHT}; "
          f"Senate incumbency ±{INCUMBENCY}")
    allrows = []
    for year in (2022, 2024):
        rows = backtest(year, m16, m20, nat20, resid)
        print(f"  {'race':16} {'model':>7} {'polls 2p':>8} {'actual':>7} {'model err':>9} {'poll err':>8}  n (Ras/AV removed)")
        for r in sorted(rows, key=lambda r: abs(r["actual"])):
            if r["poll"] is None and abs(r["actual"]) > 20:
                continue
            pe = f"{r['poll2'] - r['actual2']:+8.1f}" if r["poll2"] is not None else "       -"
            pp = f"{r['poll2']:+8.1f}" if r["poll2"] is not None else "       -"
            removed = f" ({r['n_excl']} removed)" if r["n_excl"] else ""
            print(f"  {r['state']:16} {r['proj']:+7.1f} {pp} {r['actual']:+7.1f} {r['proj'] - r['actual']:+9.1f} {pe}  "
                  f"{r['n_polls']}{removed}")
        allrows += score(rows, str(year))
    m = np.array([r["proj"] - r["actual"] for r in allrows]); p2 = np.array([r["poll2"] - r["actual2"] for r in allrows])
    print(f"\n== Both years ({len(allrows)} races): model RMSE {np.sqrt((m ** 2).mean()):.2f}, MAE {np.abs(m).mean():.2f}; "
          f"two-party polls RMSE {np.sqrt((p2 ** 2).mean()):.2f}, MAE {np.abs(p2).mean():.2f}")
    proj = np.array([r["proj"] for r in allrows]); poll = np.array([r["poll2"] for r in allrows])
    act = np.array([r["actual"] for r in allrows])
    lam = np.linspace(0, 1, 101)
    rmse = [np.sqrt((((1 - l) * proj + l * poll - act) ** 2).mean()) for l in lam]
    print(f"   best fixed blend across both years: {lam[int(np.argmin(rmse))]:.2f} × polls (RMSE {min(rmse):.2f}); "
          f"50/50 RMSE {rmse[50]:.2f}")
    print("\nRaces without a polling average where an independent was the anti-R candidate (model only):\n"
          "  UT 2022 McMullin and NE 2024 Osborn - see the tables: the partisan baseline misses both by 17+ points.")


if __name__ == "__main__":
    main_cli()
