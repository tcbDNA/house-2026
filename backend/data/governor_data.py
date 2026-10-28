"""Build the governors model's data: gov_war_computed.csv and governor_states.json.

Governor WAR (Split Ticket publishes none — sources/split_ticket_war/README.md)
is computed the way Roy Cooper's rows in raw_war.csv were: the governor margin
minus the same year's presidential margin in the state; in a midterm year the
previous presidential margin plus that year's national swing (the national
House popular-vote margin minus the previous presidential popular-vote
margin; user decision Oct 28). Every record is labelled "computed".

Incumbency (user decision Oct 28): a computed margin still contains the
incumbent's edge, so each record carries k = +1 if the Democrat ran as the
incumbent, −1 if the Republican did, 0 otherwise, and the model nets it out
with the governor_incumbency setting: record = (margin − baseline) −
k × governor_incumbency, D-positive — subtracted for the incumbent, added back
for the opponent. A candidate's WAR is therefore war_a + governor_incumbency ×
war_b (governor_model). Split Ticket's House / Senate records already control
for incumbency (k = 0). Cooper's two Governor rows in raw_war.csv belong to
the Senate model and aren't used here.

The WAR blend is senate_data's, with Governor as the office: governor records
at full weight, House and Senate records at the 0.5× cross-office discount;
the last three cycles per office (Governor 2014+, House 2020+, Senate 2008+),
0.50 / 0.30 / 0.20 by recency, missing cycles zero-filled.

Reads (all under sources/ unless noted; see each folder's README.md):
  governors_2026/roster_2026.csv, governors_2026/not_up_2026.csv
  gov_results/gov_results.csv (+ gov_results/official_overrides.csv: official
      state canvass figures where they differ from Wikipedia)
  gov_results/pres_state_2008_2012.csv, gov_results/national_margins.csv
  fec_backtest/pres_2016_by_state.csv, fec_backtest/house_national_popular_vote.csv
  ../state_pres_results.csv (2020, 2024), ../raw_war.csv, ../governor_poll_averages.csv

Usage (from backend/data/): python3 governor_data.py
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import senate_data as sd

DATA = Path(__file__).resolve().parent
SRC = DATA / "sources"
ROSTER = SRC / "governors_2026" / "roster_2026.csv"
NOT_UP = SRC / "governors_2026" / "not_up_2026.csv"
RESULTS = SRC / "gov_results" / "gov_results.csv"
OVERRIDES = SRC / "gov_results" / "official_overrides.csv"
POLLS = DATA / "governor_poll_averages.csv"
WAR_OUT = DATA / "gov_war_computed.csv"
OUT = DATA / "governor_states.json"
PRES_YEARS = (2008, 2012, 2016, 2020, 2024)


def _f(x):
    return float(x) if x not in (None, "") else None


def pres_state_margins() -> dict[int, dict[str, float]]:
    """year -> state -> D − R presidential margin (points of the total vote)."""
    out = {y: {} for y in PRES_YEARS}
    with (SRC / "gov_results" / "pres_state_2008_2012.csv").open() as f:
        for r in csv.DictReader(f):
            out[int(r["year"])][r["state"]] = float(r["d_pct"]) - float(r["r_pct"])
    with (SRC / "fec_backtest" / "pres_2016_by_state.csv").open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            out[2016][r["state"]] = float(r["margin"])
    with (DATA / "state_pres_results.csv").open() as f:
        for r in csv.DictReader(f):
            out[2020][r["state"]] = float(r["margin_2020"])
            out[2024][r["state"]] = float(r["margin_2024"])
    return out


def national_margins() -> dict[tuple[int, str], float]:
    """(year, "house" / "president") -> national D − R margin."""
    out = {}
    with (SRC / "gov_results" / "national_margins.csv").open() as f:
        for r in csv.DictReader(f):
            out[(int(r["year"]), r["office"])] = float(r["margin"])
    return out


def baseline(year: int, state: str, pres: dict, nat: dict) -> tuple[float, str]:
    """The presidential baseline a governor margin is measured against."""
    if year in pres:
        return pres[year][state], f"{year} presidential margin"
    prev = year - 2
    swing = nat[(year, "house")] - nat[(prev, "president")]
    return pres[prev][state] + swing, (f"{prev} presidential margin + national swing {swing:+.2f} "
                                       f"({year} House vote − {prev} presidential vote)")


def results() -> list[dict]:
    rows = list(csv.DictReader(RESULTS.open()))
    if OVERRIDES.exists():
        over = {(r["year"], r["state"]): r for r in csv.DictReader(OVERRIDES.open())}
        for r in rows:
            o = over.get((r["year"], r["state"]))
            if o:
                for k in ("d_pct", "r_pct", "d_votes", "r_votes", "total_votes"):
                    if o.get(k):
                        r[k] = o[k]
                r["official_source"] = o["source_file"]
    return rows


def computed_records() -> list[dict]:
    """One computed WAR record per governor race with a D and an R nominee
    (gov_war_computed.csv)."""
    pres, nat = pres_state_margins(), national_margins()
    out = []
    for r in results():
        if not (r["d_candidate"] and r["r_candidate"] and r["d_pct"] and r["r_pct"]):
            continue
        if int(r["year"]) % 2:   # California's 2021 recall: a yes/no question, no baseline year
            continue
        year, st = int(r["year"]), r["state"]
        margin = float(r["d_pct"]) - float(r["r_pct"])
        base, how = baseline(year, st, pres, nat)
        k = 0
        if r.get("incumbent_ran") == "yes":
            k = 1 if r.get("incumbent_party", "").startswith("D") else -1 if r.get("incumbent_party", "").startswith("R") else 0
        out.append({"year": year, "state": st, "d_candidate": r["d_candidate"], "r_candidate": r["r_candidate"],
                    "d_pct": float(r["d_pct"]), "r_pct": float(r["r_pct"]), "margin": round(margin, 2),
                    "baseline": round(base, 2), "baseline_note": how, "war": round(margin - base, 2),
                    "incumbent_side": {1: "D", -1: "R", 0: ""}[k], "k": k, "label": "computed",
                    "source": r.get("official_source") or r["source_file"]})
    return out


def governor_wars(records: list[dict]) -> dict:
    """senate_data.load_all_wars' structure for the House / Senate records
    (Split Ticket, k = 0) plus the computed Governor records."""
    allw = {k: [x for x in v if x["chamber"] != "Governor"] for k, v in sd.load_all_wars().items()}
    for rec in records:
        if rec["year"] < sd.WAR_FIRST_YEAR["Governor"]:
            continue
        for letter, name in (("D", rec["d_candidate"]), ("R", rec["r_candidate"])):
            key = (rec["state"], sd._strip_accents(sd._clean_name(name)), letter)
            allw.setdefault(key, []).append({
                "year": rec["year"], "geo": sd.STATE_NAMES[rec["state"]], "chamber": "Governor",
                "sortable": -rec["war"], "k": rec["k"], "war_text": f"computed {rec['war']:+.2f}"})
    for v in allw.values():
        v.sort(key=lambda x: x["year"], reverse=True)
    return {k: v for k, v in allw.items() if v}


def candidate_war(state: str, name: str | None, letter: str, allw: dict) -> dict:
    """D-positive WAR effect of one candidate: a + governor_incumbency × b."""
    recs = sd.find_war(state, name, letter, allw) if name else None
    if not recs:
        return {"name": name, "a": 0.0, "b": 0.0, "records": []}
    a = -sd._time_weighted_sortable(recs, candidate_name=name, office="Governor")
    b = -sd._time_weighted_sortable([{**x, "sortable": x.get("k", 0)} for x in recs],
                                    candidate_name=name, office="Governor")
    return {"name": name, "a": round(a, 3), "b": round(b, 3),
            "records": [{"year": x["year"], "office": x["chamber"], "geo": x["geo"], "war": x["war_text"],
                         "k": x.get("k", 0)} for x in recs]}


TITLES = ("Governor ", "State Senator ", "Senator ", "Lt. Governor ", "Lieutenant Governor ")


def clean_name(ballot: str | None) -> str | None:
    """The roster's official ballot string -> the candidate's name for display
    and WAR matching: drops bracketed notes, quoted nicknames, office titles
    and middle initials. Alaska's top-four R entry lists three Republicans
    ("A / B / C ..."); the first is the polls' final-round Republican."""
    if not ballot:
        return None
    s = re.sub(r"\[.*?\]|\(.*?\)", "", ballot.split(" / ")[0])
    s = re.sub(r'"[^"]*"', "", s)
    for title in TITLES:
        if s.startswith(title):
            s = s[len(title):]
    s = re.sub(r"\b[A-Z]\.?(?=\s)", "", s)
    return re.sub(r"\s+", " ", s).strip()


def party_tag(p: str | None) -> str:
    """'D' / 'Democratic' / '(D)' -> '(D)', etc."""
    s = (p or "").strip().strip("()").lower()
    if s.startswith("d"):
        return "(D)"
    if s.startswith("r"):
        return "(R)"
    return f"({s[:1].upper()})" if s else ""


def load_poll_averages() -> dict[str, dict]:
    if not POLLS.exists():
        return {}
    out = {}
    for r in csv.DictReader(POLLS.open()):
        out[r["state"]] = {"margin": float(r["blend_margin"]), "raw_margin": float(r["margin"]),
                           "n_polls": int(r["n_polls"]), "third_party_share": _f(r["third_party_share"]),
                           "rcv_final_polls": int(r["rcv_final_polls"] or 0), "method": r["method"],
                           "as_of": r["as_of"], "polls": r["polls"], "url": r["url"], "local_file": r["local_file"]}
    return out


def other_candidates(field: str) -> list[dict]:
    out = []
    for item in filter(None, (x.strip() for x in (field or "").split(";"))):
        parts = [p.strip() for p in item.split("|")]
        out.append({"name": parts[0], "party": party_tag(parts[1]) if len(parts) > 1 else "",
                    "max_poll_share": _f(parts[2]) if len(parts) > 2 else None,
                    "poll": parts[3] if len(parts) > 3 else None})
    return out


def main():
    records = computed_records()
    with WAR_OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(records)
    allw = governor_wars(records)
    polls = load_poll_averages()
    races = {}
    for r in csv.DictReader(ROSTER.open()):
        st = r["state"]
        inc_party = party_tag(r["incumbent_party"])
        running = (r["incumbent_status"] or "").strip().lower() == "running"
        won = (r["incumbent_has_won_gov_election"] or "").strip().lower() == "yes"
        d_name, r_name = clean_name(r["d_nominee"]), clean_name(r["r_nominee"])
        d = candidate_war(st, d_name, "D", allw)
        rr = candidate_war(st, r_name, "R", allw)
        inc_sign = (1 if inc_party == "(D)" else -1 if inc_party == "(R)" else 0) if running and won else 0
        races[st] = {
            "state": st, "name": sd.STATE_NAMES[st], "party": inc_party,
            "incumbent": r["incumbent"], "incumbent_party": inc_party,
            "incumbent_status": r["incumbent_status"], "incumbent_running": running,
            "incumbent_elected_or_succeeded": r["incumbent_elected_or_succeeded"],
            "incumbent_won_gov_election": won,
            "d_nominee": d_name, "r_nominee": r_name,
            "d_ballot_name": r["d_nominee"], "r_ballot_name": r["r_nominee"],
            "anti_r_candidate": d_name, "anti_r_party": "(D)",
            "other_candidates": other_candidates(r["other_candidates"]),
            "war_a": round(d["a"] + rr["a"], 3), "war_b": round(d["b"] + rr["b"], 3),
            "war_detail": {"d": d, "r": rr}, "inc_sign": inc_sign,
            "poll_average": polls.get(st), "note": r.get("notes") or None,
            "source_files": r["source_files"],
        }
    not_up = {r["state"]: {"governor": r["governor"], "party": party_tag(r["party"]),
                           "source_files": r["source_files"]}
              for r in csv.DictReader(NOT_UP.open())}
    OUT.write_text(json.dumps({"races": races, "not_up": not_up}, indent=1))
    print(f"{len(races)} races, {len(not_up)} governorships not up, {len(records)} computed WAR records")


if __name__ == "__main__":
    main()
