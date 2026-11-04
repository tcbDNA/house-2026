"""Aggregate tables for the Alaska ranked-choice dashboard, from the CVR, the precinct results file, the summary report
stamp and the combined-count output (ak_combine.py). Every table is a count over ballots; nothing is ballot-level.
usage: python3 -I ak_dash_data.py <cvr dir> <precinct csv> <combined.json> <summary stamp text> <cvr last-modified> <out dir>
  summary stamp: the summary PDF's header time as printed ("11/4/2026 2:19:06 AM", Alaska time)
  cvr last-modified: the CVR zip's Last-Modified header ("Wed, 04 Nov 2026 11:42:46 GMT")"""
import collections, csv, datetime as dt, email.utils, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ak_rcv import STATEWIDE, load, read_cvr, state, tabulate

D, PCSV, COMB, STAMP, LASTMOD, OUT = sys.argv[1:7]
os.makedirs(OUT, exist_ok=True)
contests, cands, groups = load(D)
parties = {p["Id"]: p["Description"] for p in json.load(open(f"{D}/PartyManifest.json"))["List"]}
portion = {p["Id"]: p for p in json.load(open(f"{D}/PrecinctPortionManifest.json"))["List"]}
dist = {d["Id"]: d for d in json.load(open(f"{D}/DistrictManifest.json"))["List"]}
dtype = {t["Id"]: t["Description"] for t in json.load(open(f"{D}/DistrictTypeManifest.json"))["List"]}
hd_of = {}
for x in json.load(open(f"{D}/DistrictPrecinctPortionManifest.json"))["List"]:
    d = dist[x["DistrictId"]]
    if dtype[d["DistrictTypeId"]] == "State House": hd_of[x["PrecinctPortionId"]] = int(d["Description"].split()[-1])
pct_hd = {}  # precinct name (as the CVR and the precinct file both print it) -> house district
for pid, p in portion.items():
    h = hd_of[pid]
    assert pct_hd.setdefault(p["Description"], h) == h, p


def hd_of_name(n):
    """a precinct file row's district: the CVR's, else the name's own ("District 30 - Absentee", "01-600 Ketchikan")"""
    if n in pct_hd: return pct_hd[n]
    return int(n.split()[1]) if n.startswith("District ") else int(n.split("-")[0])
SID = {"U.S. Senator": "senate", "U.S. Representative": "house", "Governor / Lieutenant Governor": "governor"}
LABEL = {"senate": "U.S. Senate", "house": "U.S. House", "governor": "Governor"}
by_name = {c["Description"]: k for k, c in contests.items()}

# one pass: patterns statewide and by house district
pat_hd = collections.defaultdict(collections.Counter)
cvr_pct = collections.Counter()  # Senate ballots per precinct


def each(s, v, cid, key):
    if contests[cid]["Description"] in STATEWIDE: pat_hd[(cid, hd_of[v["PrecinctPortionId"]])][key] += 1
    if contests[cid]["Description"] == "U.S. Senator": cvr_pct[portion[v["PrecinctPortionId"]]["Description"]] += 1


pat, by_group, not_counted, n_sessions, _ = read_cvr(D, contests, groups, each)
reg = lambda cid: [k for k, c in cands.items() if c["ContestId"] == cid and c["Type"] != "WriteIn"]
nm = lambda k: cands[k]["Description"] if isinstance(k, int) else k

# precinct results file: ballots per precinct and contest, and per counting group for the Senate
csv_ballots = collections.Counter(); csv_seen = set(); csv_grp = collections.Counter()
GRP = ("Election Day", "Absentee", "Early Voting", "Question", "Remote")
for row in csv.DictReader(open(PCSV, encoding="utf-8-sig")):
    k = (row["Precinct_name"], int(row["Contest_Id"]))
    if k in csv_seen: continue
    csv_seen.add(k)
    csv_ballots[k] += int(row["total_ballots"])
    if k[1] == by_name["U.S. Senator"]:
        for g in GRP: csv_grp[g] += int(row[f"{g}_ballots"] or 0)


def write(name, rows, cols):
    with open(f"{OUT}/{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f"{name}.csv: {len(rows)} rows")


def party(k):
    a = cands[k]["Affiliations"]
    p = parties.get(a[0], "") if a else ""
    return {"Registered Republican": "R", "Registered Democrat": "D", "Nonpartisan": "N", "Undeclared": "U",
            "Registered Libertarian": "L", "Registered Democrat/Nonpartisan": "D/N"}.get(p, p)


def surname(k):
    n = cands[k]["Description"]
    return n.split("/")[0] if "," not in n else n.split(",")[0].strip()


def display(k):
    n = cands[k]["Description"]
    if "," not in n: return n                       # a governor ticket, "Last/Last"
    last, first = (x.strip() for x in n.split(",", 1))
    suf = ""
    for s in (" Jr.", " Sr."):
        if first.endswith(s): first, suf = first[: -len(s)], s
    return f"{first} {last}{suf}"


comb = json.load(open(COMB))
cand_rows, round_rows, tr_rows, depth_rows, next_rows, hd_rows, con_rows = [], [], [], [], [], [], []
for full in STATEWIDE:
    cid, sid = by_name[full], SID[full]
    t = tabulate(cid, pat[cid], contests, cands, by_group, not_counted, all_rounds=True)
    rounds = t["rounds"]; fin = list(rounds[-1]["votes"]); a, b = fin
    # colors: a Democrat blue (slot 0), the leading Republican red (slot 7), the rest in round-1 order
    r1 = list(rounds[0]["votes"]); ids = {nm(k): k for k in reg(cid)}
    slot, free = {}, [1, 2, 4, 6, 3, 5]
    for n in r1:
        p = party(ids[n])
        if p.startswith("D") and 0 not in slot.values(): slot[n] = 0
        elif p == "R" and 7 not in slot.values(): slot[n] = 7
    for n in r1:
        if n not in slot: slot[n] = free.pop(0)
    sn = collections.Counter(surname(ids[n]) for n in r1)
    for i, n in enumerate(r1):
        k = ids[n]; short = surname(k)
        if sn[short] > 1:  # two candidates share a surname (the Senate's two Sullivans)
            short += " Jr." if cands[k]["Description"].endswith(" Jr.") else (f" ({party(k)})" if party(k) else "")
        cand_rows.append({"contest_id": sid, "candidate": n, "display": display(k), "short": short, "party": party(k),
                          "round1_order": i + 1, "color_slot": slot[n]})
    elim = {r["round"]: r.get("eliminated") for r in rounds}
    for r in rounds:
        for n, v in r["votes"].items():
            round_rows.append({"contest_id": sid, "round": r["round"], "item": n, "item_type": "candidate", "votes": v,
                               "share_of_continuing": v / r["continuing"], "eliminated": int(elim[r["round"]] == n)})
        for it, key in (("Exhausted", "exhausted"), ("Overvote", "overvotes")):
            round_rows.append({"contest_id": sid, "round": r["round"], "item": it, "item_type": key, "votes": r[key],
                               "share_of_continuing": "", "eliminated": 0})
        if "eliminated" in r:
            n_e = r["votes"][r["eliminated"]]
            for dest, v in r["transfers"].items():
                to = {"exhausted": "Exhausted", "overvote": "Overvote"}.get(dest, dest)
                tr_rows.append({"contest_id": sid, "round": r["round"], "from": r["eliminated"], "to": to,
                                "to_type": "candidate" if to == dest else dest, "votes": v, "share_of_from": v / n_e})
    # ranking depth and next choice, for ballots counted for a candidate in round 1
    R = set(reg(cid))
    depth = collections.Counter(); nxt = collections.Counter()
    for key, v in pat[cid].items():
        f = state(key, R)
        if not isinstance(f, int): continue
        depth[(nm(f), len({r[0] for r in key if len(r) == 1}))] += v
        n2 = state(key, R - {f})
        nxt[(nm(f), {"exhausted": "No further choice", "overvote": "Overvote"}.get(n2, nm(n2)))] += v
    for (f, k), v in sorted(depth.items()):
        depth_rows.append({"contest_id": sid, "first_choice": f, "ranked": k, "ballots": v})
    for (f, n2), v in sorted(nxt.items()):
        next_rows.append({"contest_id": sid, "first_choice": f, "next_choice": n2,
                          "next_type": "candidate" if n2 in ids else ("overvote" if n2 == "Overvote" else "exhausted"), "ballots": v})
    # house districts: the statewide eliminations applied to each district's ballots
    order = [r["eliminated"] for r in rounds if "eliminated" in r]
    csv_hd = collections.Counter()
    for (pid, c2), v in csv_ballots.items():
        if c2 == cid: csv_hd[hd_of_name(pid)] += v
    for h in sorted(set(csv_hd) | {h for (c2, h) in pat_hd if c2 == cid}):
        P = pat_hd.get((cid, h), collections.Counter())
        n_cvr = sum(P.values())
        row = {"contest_id": sid, "hd": h, "ballots_cvr": n_cvr, "ballots_precinct_file": csv_hd[h], "not_in_cvr": csv_hd[h] - n_cvr,
               "finalist_a": a, "finalist_b": b, "votes_a": "", "votes_b": "", "share_a": "", "round1_leader": "", "round1_leader_share": "",
               "exhausted": "", "overvotes": "", "blanks": "", "inactive_share": ""}
        if n_cvr:
            th = tabulate(cid, P, contests, cands, order=order)
            fr = th["rounds"][-1]; r1h = th["rounds"][0]
            top = max(r1h["votes"], key=r1h["votes"].get)
            row.update(votes_a=fr["votes"][a], votes_b=fr["votes"][b], share_a=fr["votes"][a] / fr["continuing"],
                       round1_leader=top, round1_leader_share=r1h["votes"][top] / r1h["continuing"],
                       exhausted=fr["exhausted"], overvotes=fr["overvotes"], blanks=fr["blanks"],
                       inactive_share=(fr["exhausted"] + fr["overvotes"]) / (n_cvr - fr["blanks"]))
        hd_rows.append(row)
    # the contest's headline figures
    cb = comb[full]; sf = cb["scenario_final"]; lo, hi = cb["bounds"][f"{a}_minus_{b}_range"]
    c1 = cb["combined_rounds_scenario"][0]["votes"]; top1 = max(c1, key=c1.get)
    fr, r1x = rounds[-1], rounds[0]
    top = max(r1x["votes"], key=r1x["votes"].get)
    csv_tot = sum(v for (p, c2), v in csv_ballots.items() if c2 == cid)
    con_rows.append({"contest_id": sid, "contest": full, "label": LABEL[sid], "ballots_cvr": t["ballots"], "ballots_precinct_file": csv_tot,
                     "not_in_cvr": csv_tot - t["ballots"], "blanks": fr["blanks"], "rounds": len(rounds),
                     "round1_leader": top, "round1_leader_share": r1x["votes"][top] / r1x["continuing"],
                     "round1_majority": int(2 * r1x["votes"][top] > r1x["continuing"]),
                     "finalist_a": a, "finalist_b": b, "final_a": fr["votes"][a], "final_b": fr["votes"][b],
                     "final_margin": fr["votes"][a] - fr["votes"][b], "final_share_a": fr["votes"][a] / fr["continuing"],
                     "final_share_b": fr["votes"][b] / fr["continuing"],
                     "exhausted_final": fr["exhausted"], "overvotes_final": fr["overvotes"],
                     "inactive_share_final": (fr["exhausted"] + fr["overvotes"]) / (t["ballots"] - fr["blanks"]),
                     "combined_round1_leader": top1, "combined_round1_leader_share": c1[top1] / sum(c1.values()),
                     "combined_round1_majority": int(2 * c1[top1] > sum(c1.values())),
                     "combined_final_a": sf[a], "combined_final_b": sf[b], "combined_margin": sf[a] - sf[b],
                     "combined_share_a": sf[a] / (sf[a] + sf[b]), "combined_share_b": sf[b] / (sf[a] + sf[b]),
                     "bound_low": lo, "bound_high": hi, "hand_movable": cb["bounds"]["hand_votes_that_could_move"]})

# legislative contests (the law's stopping rule: a round-1 majority ends the count)
leg_rows = []
for cid, c in sorted(contests.items(), key=lambda x: x[0]):
    if c["Description"] in STATEWIDE: continue
    t = tabulate(cid, pat[cid], contests, cands, by_group, not_counted)
    rr = t["rounds"]; r1x, fr = rr[0], rr[-1]
    top1 = max(r1x["votes"], key=r1x["votes"].get); order_f = list(fr["votes"])
    fl = order_f[0]; ru = order_f[1] if len(order_f) > 1 else ""
    csv_tot = sum(v for (p, c2), v in csv_ballots.items() if c2 == cid)
    leg_rows.append({"contest": c["Description"], "chamber": "Senate" if c["Description"].startswith("Senate") else "House",
                     "candidates": len(reg(cid)), "rounds": len(rr), "round1_leader": top1,
                     "round1_leader_share": r1x["votes"][top1] / r1x["continuing"] if r1x["continuing"] else "",
                     "final_leader": fl, "final_runner_up": ru, "final_leader_share": fr["votes"][fl] / fr["continuing"] if fr["continuing"] else "",
                     "final_margin": fr["votes"][fl] - (fr["votes"][ru] if ru else 0),
                     "exhausted": fr["exhausted"], "inactive_share": (fr["exhausted"] + fr["overvotes"]) / (t["ballots"] - fr["blanks"]) if t["ballots"] > fr["blanks"] else "",
                     "leader_changed": int(fl != top1), "ballots_cvr": t["ballots"], "ballots_precinct_file": csv_tot,
                     "not_in_cvr": csv_tot - t["ballots"], "tie_note": t["note"] or ""})

# coverage
gp = {g: 0 for g in GRP}
for g, v in by_group[by_name["U.S. Senator"]].items(): gp[g] += v
stamp = dt.datetime.strptime(STAMP, "%m/%d/%Y %I:%M:%S %p").replace(tzinfo=dt.timezone(dt.timedelta(hours=-9)))
lm = email.utils.parsedate_to_datetime(LASTMOD)
sen = by_name["U.S. Senator"]
# real precincts only: the precinct file's "District N - Absentee / Early Voting" rows go by other names in the CVR
real = lambda n: not n.startswith("District ")
no_cvr = [p for (p, c2), v in csv_ballots.items() if c2 == sen and v and real(p) and not cvr_pct[p]]
partial = [p for (p, c2), v in csv_ballots.items() if c2 == sen and real(p) and cvr_pct[p] and v != cvr_pct[p]]
cov = [{"group": g, "ballots_cvr": gp[g], "ballots_precinct_file": csv_grp[g], "not_in_cvr": csv_grp[g] - gp[g]} for g in GRP]
write("candidates", cand_rows, list(cand_rows[0]))
write("rounds", round_rows, list(round_rows[0]))
write("transfers", tr_rows, list(tr_rows[0]))
write("ranking_depth", depth_rows, list(depth_rows[0]))
write("next_choice", next_rows, list(next_rows[0]))
write("house_districts", hd_rows, list(hd_rows[0]))
write("contests", con_rows, list(con_rows[0]))
write("legislative", leg_rows, list(leg_rows[0]))
write("coverage", cov, list(cov[0]))
write("status", [{"summary_report_time": stamp.astimezone(dt.timezone.utc).isoformat(), "cvr_file_time": lm.astimezone(dt.timezone.utc).isoformat(),
                    "cvr_ballots": n_sessions, "precinct_file_ballots": sum(csv_grp.values()), "not_in_cvr": sum(csv_grp.values()) - sum(gp.values()),
                    "precincts_not_in_cvr": len(no_cvr), "precincts_partly_in_cvr": len(partial),
                    "precincts_with_ballots": sum(1 for (p, c2), v in csv_ballots.items() if c2 == sen and v and real(p))}],
      ["summary_report_time", "cvr_file_time", "cvr_ballots", "precinct_file_ballots", "not_in_cvr", "precincts_not_in_cvr",
       "precincts_partly_in_cvr", "precincts_with_ballots"])
