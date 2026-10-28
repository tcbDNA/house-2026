"""Governor polling averages for the governors model's poll blend ->
governor_poll_averages.csv.

Same rules as the Senate (build_senate_poll_averages.py, whose helpers this
reuses):
  * Excluded pollsters: Rasmussen Reports, ActiVote, Wedgewood Polls, and
    Median Strategies (user decisions); polls with a partisan sponsor are not
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
  * Alaska (ranked-choice): polls' final-round D / R numbers where a pollster
    reports them (rcv_final_d / rcv_final_r) are used in place of first
    choices; the RCP average is used only if none of its polls reports a final
    round (noted).
  * third_party_share: mean share of every candidate other than the two in the
    averaged polls (for Georgia's runoff and Vermont's legislature flags).

Inputs: sources/gov_polls_2026/ (README.md there): rcp_gov_<st>_<id>.json,
gov_polls_compiled.json.

Usage (from backend/data/): python3 build_governor_poll_averages.py
Writes governor_poll_averages.csv and prints the per-race report
(saved as ../analysis/governor_poll_averages.txt).
"""
from __future__ import annotations

import csv
import json
from email.utils import parsedate_to_datetime
from pathlib import Path

from build_senate_poll_averages import (
    WINDOW_START, d, label, partisan_sponsor, pollster_key, rcp_end, same_poll,
)

DATA = Path(__file__).resolve().parent
SRC = DATA / "sources" / "gov_polls_2026"
OUT = DATA / "governor_poll_averages.csv"
RETRIEVED = None   # set from the compiled file's retrieval date
EXCLUDED_POLLSTERS = ("rasmussen", "activote", "wedgewood", "median strategies")


def excluded(name: str) -> bool:
    return any(x in name.lower() for x in EXCLUDED_POLLSTERS)


def rcp_feeds() -> dict[str, Path]:
    """state -> its two-way RCP governor feed (rcp_gov_<st>_<id>.json)."""
    out = {}
    for f in sorted(SRC.glob("rcp_gov_*_*.json")):
        st = f.name.split("_")[2].upper()
        out.setdefault(st, f)
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
            "averaged": averaged, "local_file": f"sources/gov_polls_2026/{path.name}",
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
        out.append({"pollster": p["pollster"], "sponsor": p.get("sponsor"), "partisan": p.get("partisan"),
                    "end": d(p["end"]), "released": d(p.get("released")), "anti_r": anti, "r": rep,
                    "others": others,
                    "question": "ranked-choice final round" if rcv else "head-to-head" if h2h else "full ballot",
                    "rcv": rcv, "source": p.get("source", "")})
    return out


def build() -> str:
    comp = compiled()
    feeds = rcp_feeds()
    rows, report = [], []
    report.append(f"Governor polling averages; recompute window: polls ending on or after {WINDOW_START}.\n")
    for st in sorted(comp):
        race = comp[st]
        polls = poll_rows(race, st)
        sponsored = [p for p in polls if partisan_sponsor(p)]
        usable = [p for p in polls if not excluded(p["pollster"]) and not partisan_sponsor(p)
                  and p["anti_r"] is not None and p["r"] is not None]
        dropped = [f"{label(p)}, ending {p['end']} (partisan sponsor)" for p in sponsored if p["end"] >= WINDOW_START]
        rcp = (load_rcp(st, feeds[st], race.get("d_candidate"), race.get("r_candidate"))
               if st in feeds else None)
        rcv_polls = [p for p in usable if p["rcv"]]
        newer = []
        if rcp:
            latest = max(a["end"] for a in rcp["averaged"])
            newer = [p for p in usable if p["end"] > latest
                     and (p["released"] is None or p["released"] >= rcp["built"])]
        use_rcp = rcp and not newer and not (st == "AK" and rcv_polls)
        if use_rcp:
            ps = [a for a in rcp["averaged"] if any(same_poll(q, a) for q in sponsored)]
            kept = [a for a in rcp["averaged"] if not excluded(a["pollster"]) and a not in ps
                    and a["anti_r"] is not None and a["r"] is not None]
            removed = [a for a in rcp["averaged"] if a not in kept]
            anti = sum(a["anti_r"] for a in kept) / len(kept)
            rep = sum(a["r"] for a in kept) / len(kept)
            third = sum(a["others"] for a in kept) / len(kept)
            used = [f"{a['pollster']} {a['dates']}" for a in kept]
            method = "RCP average" + ("; removed: " + ", ".join(f"{a['pollster']} {a['dates']}" for a in removed)
                                      if removed else "")
            as_of, url, local = rcp["built"].isoformat(), rcp["url"], rcp["local_file"]
            published = round(rcp["published"][0] - rcp["published"][1], 1) \
                if None not in rcp["published"] else ""
        else:
            window = [p for p in usable if p["end"] >= WINDOW_START]
            if st == "AK" and rcv_polls:
                window = [p for p in window if p["rcv"]]
            latest_by = {}
            for p in sorted(window, key=lambda p: p["end"]):
                latest_by[pollster_key(p["pollster"])] = p
            kept = sorted(latest_by.values(), key=lambda p: p["end"], reverse=True)
            if not kept:
                report.append(f"{st}: no RCP average and no poll ending on/after {WINDOW_START} -> model only")
                continue
            anti = sum(p["anti_r"] for p in kept) / len(kept)
            rep = sum(p["r"] for p in kept) / len(kept)
            third = sum(p["others"] for p in kept) / len(kept)
            used = [f"{label(p)}, ending {p['end']} ({p['question']}, {p['anti_r']:g}/{p['r']:g})" for p in kept]
            method = ("recomputed: newer polls than RCP's average" if newer else
                      "recomputed: final-round polls (ranked choice)" if rcp else
                      "recomputed: RCP publishes no average")
            as_of = max(p["end"] for p in kept).isoformat()
            url, local = "", "sources/gov_polls_2026/gov_polls_compiled.json"
            published = round(rcp["published"][0] - rcp["published"][1], 1) \
                if rcp and None not in rcp["published"] else ""
        margin = anti - rep
        blend = 100 * margin / (anti + rep)
        rows.append({"state": st, "d": round(anti, 2), "r": round(rep, 2), "margin": round(margin, 2),
                     "blend_margin": round(blend, 2), "n_polls": len(kept),
                     "third_party_share": round(third, 2), "rcv_final_polls": sum(1 for p in kept if p.get("rcv")),
                     "margin_published": published, "method": method, "as_of": as_of,
                     "polls": "; ".join(used), "url": url, "local_file": local,
                     "newer_polls": "; ".join(f"{label(p)} ending {p['end']}, released {p['released'] or 'n/a'}"
                                              for p in newer)})
        report.append(f"{st}: {method}; {len(kept)} poll(s); anti-R {anti:.2f} / R {rep:.2f} -> margin {margin:+.2f}, "
                      f"blend margin {blend:+.2f}, third parties {third:.1f}"
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
