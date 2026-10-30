"""Governor polling averages for the governors model's poll blend ->
governor_poll_averages.csv.

Same rules as the Senate (build_senate_poll_averages.py, whose helpers this
reuses):
  * Excluded pollsters: Rasmussen Reports, ActiVote, Wedgewood Polls,
    Median Strategies and McLaughlin & Associates (user decisions); polls with a partisan sponsor are not
    counted, including any RCP has averaged.
  * Start from RealClearPolling's average with those removed (the remaining
    polls RCP averaged, re-averaged).
  * If a newer poll came out after RCP last updated the average, or RCP
    publishes none, recompute from the most recent poll by each pollster whose
    fieldwork ended on or after WINDOW_START (the Senate's), head-to-head
    question where released. "Newer" = fieldwork ended after the latest poll
    in RCP's average and released on or after RCP's lastBuildDate.
  * blend_margin = two-party margin (anti-R − R), as in the Senate.
Governor-specific:
  * Alaska (ranked-choice): the model's margin is the final-round
    two-candidate margin. RCP's Alaska average is a final-round average; when
    it has to be recomputed, only polls reporting a final round
    (rcv_final_d / rcv_final_r) are used.
  * third_party_share: mean share of every candidate other than the two in the
    averaged polls (for Georgia's runoff and Vermont's legislature flags).
  * Sparse polling (user decision Oct 28; EXTEND_SPARSE_WINDOW): a recomputed
    average with fewer than three polls since WINDOW_START reaches back to
    Sep 1, each older poll counting half for the blend weight (n_eff).
  * Rhode Island (user decision Oct 28; INDEPENDENT_OPPONENT): the Democrat's
    main opponent is the independent, Ken Block; the margin is Foulkes − Block
    (raw, three-way), and Block's campaign poll is out as partisan-sponsored.
    republican_share is the Republican's mean share in the same polls (for the
    three-way win probabilities, probability.add_governor_win_probabilities).

Inputs: sources/gov_polls_2026/ (README.md there): rcp_gov_<st>_<id>.json,
gov_polls_compiled.json.

Usage (from backend/data/): python3 build_governor_poll_averages.py
Writes governor_poll_averages.csv and prints the per-race report
(saved as ../analysis/governor_poll_averages.txt).
"""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from email.utils import parsedate_to_datetime
from pathlib import Path

from build_senate_poll_averages import (
    LEAVE_OUT_VOTEHUB_INTERNAL, WINDOW_START, d, is_internal, label, partisan_sponsor, pollster_key, rcp_end,
    rcp_left_out, rcp_start, same_poll, votehub_internal,
)

# Sparse polling (user decision, Oct 28): a race with fewer than
# SPARSE_MIN_POLLS polls in the standard window (on or after WINDOW_START)
# reaches back to SPARSE_WINDOW_START, and each poll older than the standard
# window counts as OLD_POLL_WEIGHT of a poll for the blend weight (n_eff).
# EXTEND_SPARSE_WINDOW = False: the standard window only.
EXTEND_SPARSE_WINDOW = True
SPARSE_MIN_POLLS = 3
SPARSE_WINDOW_START = date(2026, 9, 1)
OLD_POLL_WEIGHT = 0.5
# Races whose Democrat's main opponent is an independent, not the Republican
# (user decision, Oct 28): state -> the independent's surname in the polls.
# The margin is the raw D − independent margin (three-way, like the Senate's
# Montana), on polls only.
INDEPENDENT_OPPONENT = {"RI": "Block"}
# Polls RCP doesn't list at all, counted in its average anyway (user decisions:
# Oct 29, MSU's Michigan Election Survey, Oct 8-23; Oct 30, the Washington
# Post-Schar School Kansas poll, Oct 22-26, which RCP averages for the Senate
# but not yet for governor). Keyed by (state, pollster as compiled, fieldwork
# end). False: RCP's averaged set as published.
COUNT_ADDED_TO_RCP = True
ADDED_TO_RCP = {("MI", "Michigan State University (Political Science)/Verasight", date(2026, 10, 23))}
# (The Washington Post-Schar School Kansas poll was here until RCP added it to
# its Kansas governor average on Oct 30.)

# Count the polls RCP leaves out of the averages it publishes (same rule as the
# Senate's COUNT_RCP_LEFT_OUT; setting added on the user's request, Oct 30).
# Alaska's RCP average is final-round, so only polls with a final round count
# there. False: RCP's averaged set as published, plus ADDED_TO_RCP.
COUNT_RCP_LEFT_OUT = True

# Left-out polls not counted under COUNT_RCP_LEFT_OUT because the sponsor (or
# the pollster itself) leans partisan or the client is likely partisan (user
# decision Oct 30: "if your inclination is that it is sponsored by a partisan
# leaning group, don't add it"). Keyed by (state, pollster as compiled, end).
LEFT_OUT_PARTISAN_LEANING = {
    ("SC", "Targoz Market Research", date(2026, 10, 25)): "South Carolina Policy Council, a conservative think tank",
    ("FL", "MDW Communications", date(2026, 10, 10)): "MDW and EDGE Communications, political consultancies",
    ("FL", "Fabrizio, Lee & Associates", date(2026, 10, 11)): "no client named; Fabrizio polls for Republican campaigns",
    ("CA", "Manhattan Institute", date(2026, 10, 1)): "a conservative think tank (its own poll)",
    ("WI", "YouGov", date(2026, 10, 9)): "City Forward Collective / CFC Action Fund, a school-choice group's electoral arm",
    ("TX", "Pollfinity", date(2026, 10, 18)): "owned and self-funded by Lars Mapstead, a 2024 Libertarian presidential "
                                              "candidate (user decision Oct 30)",
}
DATA = Path(__file__).resolve().parent
SRC = DATA / "sources" / "gov_polls_2026"
OUT = DATA / "governor_poll_averages.csv"
RETRIEVED = None   # set from the compiled file's retrieval date
EXCLUDED_POLLSTERS = ("rasmussen", "activote", "wedgewood", "median strategies", "mclaughlin")


def excluded(name: str) -> bool:
    return any(x in name.lower() for x in EXCLUDED_POLLSTERS)


def rcp_feeds() -> dict[str, Path]:
    """state -> its two-way RCP governor feed, rcp_gov_<st>_<id>.json (the
    folder also keeps three-way, multi-candidate, first-round and placeholder
    feeds, named rcp_gov_<st>_<kind>_<id>.json; those aren't averaged here)."""
    out = {}
    for f in sorted(SRC.glob("rcp_gov_*.json")):
        m = re.fullmatch(r"rcp_gov_([a-z]{2})_(\d+)\.json", f.name)
        if m:
            out[m.group(1).upper()] = f
    return out


def load_rcp(st: str, path: Path, d_name: str | None, r_name: str | None) -> dict | None:
    feed = json.loads(path.read_text())
    mi, rows = feed["moduleInfo"], feed.get("poll") or []
    avg = [p for p in rows if p["type"] == "rcp_average"]
    if not avg:
        return None

    def shares(p):
        cands = p["candidate"]
        r = [float(c["value"]) for c in cands if c.get("affiliation") == "Republican" and c.get("value")]
        a = [float(c["value"]) for c in cands if c.get("affiliation") != "Republican" and c.get("value")
             and (not d_name or d_name.split()[-1].lower() in c["name"].lower())]
        others = sum(float(c["value"]) for c in cands if c.get("value")) - (a[0] if a else 0) - (r[0] if r else 0)
        return (a[0] if a else None), (r[0] if r else None), others

    averaged = [{"pollster": p["pollster"].replace("*", "").strip(), "dates": p["date"],
                 "end": rcp_end(p["date"]), "anti_r": shares(p)[0], "r": shares(p)[1], "others": shares(p)[2]}
                for p in rows if p["type"] == "poll_rcp_avg"]
    return {"built": parsedate_to_datetime(mi["lastBuildDate"]).date(), "published": shares(avg[0])[:2],
            "window_start": rcp_start(avg[0]["date"]), "averaged": averaged, "local_file": f"sources/gov_polls_2026/{path.name}",
            "url": f"https://www.realclearpolling.com/polls/{mi['poll_contentful_fullpath']}/{mi['poll_contentful_slug']}"}


def compiled() -> dict:
    return json.loads((SRC / "gov_polls_compiled.json").read_text())


def poll_rows(race: dict, st: str) -> list[dict]:
    out = []
    for p in race["polls"]:
        rcv = st == "AK" and p.get("rcv_final_d") is not None and p.get("rcv_final_r") is not None
        h2h = p.get("h2h_anti_r") is not None and p.get("h2h_r") is not None
        anti, rep = ((p["rcv_final_d"], p["rcv_final_r"]) if rcv else
                     (p["h2h_anti_r"], p["h2h_r"]) if h2h else (p["anti_r"], p["r"]))
        others = sum(o.get("pct") or 0 for o in (p.get("others") or [])) if not (rcv or h2h) else 0.0
        republican = None
        if st in INDEPENDENT_OPPONENT:   # D vs the independent; the Republican counts as a third party
            ind = [o.get("pct") for o in (p.get("others") or []) if INDEPENDENT_OPPONENT[st] in (o.get("name") or "")]
            others = others - (ind[0] or 0) + (rep or 0) if ind else others
            republican, rep = rep, (ind[0] if ind else None)
        out.append({"pollster": p["pollster"], "sponsor": p.get("sponsor"), "partisan": p.get("partisan"),
                    "start": d(p.get("start")), "end": d(p["end"]), "released": d(p.get("released")), "anti_r": anti, "r": rep,
                    "others": others, "republican": republican,
                    "question": "ranked-choice final round" if rcv else "head-to-head" if h2h else "full ballot",
                    "rcv": rcv, "source": p.get("source", "")})
    return out


def build() -> str:
    comp = compiled()
    feeds = rcp_feeds()
    internal = (votehub_internal(SRC / "votehub_governor_all.json")
                if COUNT_RCP_LEFT_OUT or LEAVE_OUT_VOTEHUB_INTERNAL else {})
    rows, report = [], []
    report.append(f"Governor polling averages; recompute window: polls ending on or after {WINDOW_START}.\n")
    for st in sorted(comp):
        race = comp[st]
        polls = poll_rows(race, st)
        vh_internal = [p for p in polls if LEAVE_OUT_VOTEHUB_INTERNAL and is_internal(p, internal.get(st, ()))
                       and not partisan_sponsor(p)]
        sponsored = [p for p in polls if partisan_sponsor(p)] + vh_internal
        usable = [p for p in polls if not excluded(p["pollster"]) and p not in sponsored
                  and p["anti_r"] is not None and p["r"] is not None]
        dropped = [f"{label(p)}, ending {p['end']} (" + ("campaign/party internal per VoteHub" if p in vh_internal
                                                         else "partisan sponsor") + ")"
                   for p in sponsored if p["end"] >= WINDOW_START]
        rcp = (load_rcp(st, feeds[st], race.get("d_candidate"), race.get("r_candidate"))
               if st in feeds else None)
        rcv_polls = [p for p in usable if p["rcv"]]
        newer = []
        if rcp:
            latest = max(a["end"] for a in rcp["averaged"])
            newer = [p for p in usable if p["end"] > latest
                     and (p["released"] is None or p["released"] >= rcp["built"])]
        use_rcp = rcp and not newer
        if use_rcp:
            ps = [a for a in rcp["averaged"] if any(same_poll(q, a) for q in sponsored)]
            kept = [a for a in rcp["averaged"] if not excluded(a["pollster"]) and a not in ps
                    and a["anti_r"] is not None and a["r"] is not None]
            removed = [a for a in rcp["averaged"] if a not in kept]
            extra = [{"pollster": p["pollster"], "dates": f"ending {p['end']:%b %-d}", "end": p["end"],
                      "anti_r": p["anti_r"], "r": p["r"], "others": p["others"]}
                     for p in usable if COUNT_ADDED_TO_RCP and (st, p["pollster"], p["end"]) in ADDED_TO_RCP]
            kept = kept + extra
            replaced, left_out = (rcp_left_out(st, rcp, kept, usable, ADDED_TO_RCP if COUNT_ADDED_TO_RCP else set(),
                                               eligible=lambda p: (st, p["pollster"], p["end"]) not in LEFT_OUT_PARTISAN_LEANING
                                               and (p["rcv"] or st != "AK"),
                                               internal=internal.get(st, ()))
                                  if COUNT_RCP_LEFT_OUT else ([], []))
            kept = [a for a in kept if a not in replaced] + left_out
            anti = sum(a["anti_r"] for a in kept) / len(kept)
            rep = sum(a["r"] for a in kept) / len(kept)
            third = sum(a["others"] for a in kept) / len(kept)
            reps = []   # RCP's two-way feeds carry no Republican share for a race against an independent
            used = [f"{a.get('label', a['pollster'])} {a['dates']}" +
                    (f" (left out by RCP, counted; {a['question']}, {a['anti_r']:g}/{a['r']:g})" if a in left_out else "")
                    for a in kept]
            method = "RCP average" + ("; removed: " + ", ".join(f"{a['pollster']} {a['dates']}" for a in removed)
                                      if removed else "") + \
                ("; plus " + ", ".join(f"{a['pollster']} {a['dates']}" for a in extra) +
                 " (not listed by RCP, counted by user decision)" if extra else "") + \
                ("; plus polls RCP left out: " + ", ".join(f"{a['label']} {a['dates']}" for a in left_out) +
                 ("; replacing " + ", ".join(f"{a['pollster']} {a['dates']}" for a in replaced) if replaced else "")
                 if left_out else "")
            as_of, url, local = rcp["built"].isoformat(), rcp["url"], rcp["local_file"]
            published = round(rcp["published"][0] - rcp["published"][1], 1) \
                if None not in rcp["published"] else ""
        else:
            def latest(start):
                window = [p for p in usable if p["end"] >= start]
                if st == "AK" and rcv_polls:
                    window = [p for p in window if p["rcv"]]
                latest_by = {}
                for p in sorted(window, key=lambda p: p["end"]):
                    latest_by[pollster_key(p["pollster"])] = p
                return sorted(latest_by.values(), key=lambda p: p["end"], reverse=True)
            kept = latest(WINDOW_START)
            extended = EXTEND_SPARSE_WINDOW and len(kept) < SPARSE_MIN_POLLS
            if extended:
                kept = latest(SPARSE_WINDOW_START)
            if not kept:
                report.append(f"{st}: no RCP average and no poll ending on/after {WINDOW_START} -> model only")
                continue
            anti = sum(p["anti_r"] for p in kept) / len(kept)
            rep = sum(p["r"] for p in kept) / len(kept)
            third = sum(p["others"] for p in kept) / len(kept)
            reps = [p["republican"] for p in kept if p.get("republican") is not None]
            used = [f"{label(p)}, ending {p['end']} ({p['question']}, {p['anti_r']:g}/{p['r']:g})" for p in kept]
            method = ("recomputed: newer polls than RCP's average" if newer else
                      "recomputed: RCP publishes no average")
            if extended:
                method += f" (fewer than {SPARSE_MIN_POLLS} polls since {WINDOW_START}: window from {SPARSE_WINDOW_START}, older polls count half)"
            if st == "AK" and rcv_polls:
                method += " (final-round polls only)"
            as_of = max(p["end"] for p in kept).isoformat()
            url, local = "", "sources/gov_polls_2026/gov_polls_compiled.json"
            published = round(rcp["published"][0] - rcp["published"][1], 1) \
                if rcp and None not in rcp["published"] else ""
        margin = anti - rep
        three_way = st in INDEPENDENT_OPPONENT
        republican = sum(reps) / len(reps) if three_way and reps and len(reps) == len(kept) else None
        blend = margin if three_way else 100 * margin / (anti + rep)
        n_eff = (len(kept) if use_rcp else
                 sum(1.0 if p["end"] >= WINDOW_START else OLD_POLL_WEIGHT for p in kept))
        rows.append({"state": st, "d": round(anti, 2), "r": round(rep, 2), "margin": round(margin, 2),
                     "blend_margin": round(blend, 2), "n_polls": len(kept), "n_eff": n_eff,
                     "three_way": "yes" if three_way else "no",
                     "opponent": INDEPENDENT_OPPONENT.get(st, ""),
                     "third_party_share": round(third, 2),
                     "republican_share": round(republican, 2) if republican is not None else "",
                     "rcv_final_polls": sum(1 for p in kept if p.get("rcv")),
                     "margin_published": published, "method": method, "as_of": as_of,
                     "polls": "; ".join(used), "url": url, "local_file": local,
                     "newer_polls": "; ".join(f"{label(p)} ending {p['end']}, released {p['released'] or 'n/a'}"
                                              for p in newer)})
        report.append(f"{st}: {method}; {len(kept)} poll(s) (n_eff {n_eff:g}); anti-R {anti:.2f} / "
                      f"{'R' if not three_way else INDEPENDENT_OPPONENT[st]} {rep:.2f} -> margin {margin:+.2f}, "
                      f"blend margin {blend:+.2f}, third parties {third:.1f}"
                      + (f" (Republican {republican:.1f})" if republican is not None else "")
                      + (f" (RCP published {published:+.1f})" if published != "" else ""))
        for u in used:
            report.append(f"    - {u}")
        if dropped:
            report.append(f"    left out: {'; '.join(dropped)}")
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return "\n".join(report)


if __name__ == "__main__":
    print(build())
