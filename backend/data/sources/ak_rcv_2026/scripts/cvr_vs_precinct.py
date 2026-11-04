"""Which ballots in the election-night precinct results (GA_ENR_Precinct_State_of_Alaska.csv) are not in the CVR:
per precinct and counting group, ballots and rank-1 votes in the CSV vs the CVR, for the statewide contests.
usage: python3 -I cvr_vs_precinct.py <cvr dir> <precinct csv> <out.json>"""
import collections, csv, json, sys
D, CSV, OUT_JSON = sys.argv[1:4]
sys.argv = [sys.argv[0], D, "/dev/null"]
src = open(__file__.replace("cvr_vs_precinct.py", "ak_rcv.py")).read()
exec(src[:src.index("# ballot patterns per contest")])  # manifests and the streaming reader
pp = {p["Id"]: p["ExternalId"] for p in man("PrecinctPortion")}
STATE = {6: "U.S. Senator", 7: "U.S. Representative", 5: "Governor / Lieutenant Governor"}
GRP = {"Election Day": "Election Day", "Absentee": "Absentee", "Early Voting": "Early Voting", "Question": "Question", "Remote": "Remote"}
cvr_b = collections.Counter()      # (precinct, group) -> ballots with the Senate contest
cvr_v = collections.Counter()      # (precinct, contest, candidate name) -> rank-1 votes (single mark)
for f in sorted(glob.glob(f"{D}/CvrExport*.json")):
    for s in sessions(f):
        v = current(s); pid = pp[v["PrecinctPortionId"]]; g = groups[s["CountingGroupId"]]
        for card in v["Cards"]:
            for c in card["Contests"]:
                if c["Id"] not in STATE: continue
                if c["Id"] == 6: cvr_b[(pid, g)] += 1
                r1 = [m["CandidateId"] for m in c["Marks"] if m["IsVote"] and m["Rank"] == 1]
                if len(r1) == 1: cvr_v[(pid, c["Id"], cands[r1[0]]["Description"])] += 1
csv_b = collections.Counter(); csv_v = collections.Counter(); name = {}; flag = {}
for row in csv.DictReader(open(CSV, encoding="utf-8-sig")):
    cid = int(row["Contest_Id"])
    if cid not in STATE: continue
    pid = row["Pct_Id"]; name[pid] = row["Precinct_name"]; flag[pid] = row["Reporting_flag"]
    csv_v[(pid, cid, row["candidate_name"])] += int(row["total_votes"])
    if cid == 6 and row["cand_seq_nbr"] == "1":
        for g in GRP: csv_b[(pid, g)] += int(row[f"{g}_ballots"] or 0)
pcts = sorted(name)
rows = []
for pid in pcts:
    a = sum(csv_b[(pid, g)] for g in GRP); b = sum(cvr_b[(pid, g)] for g in GRP)
    rows.append({"pct": pid, "name": name[pid], "reporting_flag": flag[pid], "csv_ballots": a, "cvr_ballots": b,
                 "by_group": {g: [csv_b[(pid, g)], cvr_b[(pid, g)]] for g in GRP if csv_b[(pid, g)] or cvr_b[(pid, g)]}})
none = [r for r in rows if r["csv_ballots"] and not r["cvr_ballots"]]
part = [r for r in rows if r["cvr_ballots"] and r["csv_ballots"] != r["cvr_ballots"]]
print(f"precincts {len(rows)}; CSV ballots {sum(r['csv_ballots'] for r in rows):,}, CVR ballots {sum(r['cvr_ballots'] for r in rows):,}")
print(f"precincts with CSV ballots and none in the CVR: {len(none)} ({sum(r['csv_ballots'] for r in none):,} ballots)")
print(f"precincts in both with different counts: {len(part)} (CSV-CVR {sum(r['csv_ballots'] - r['cvr_ballots'] for r in part):+,})")
for r in sorted(part, key=lambda r: -abs(r['csv_ballots'] - r['cvr_ballots']))[:8]: print("  ", r["name"], r["csv_ballots"], r["cvr_ballots"], r["by_group"])
gap = collections.Counter()
for g in GRP:
    gap[g] = sum(csv_b[(p, g)] for p in pcts) - sum(cvr_b[(p, g)] for p in pcts)
print("CSV-CVR ballots by counting group:", dict(gap))
miss = {}
for cid, cn in STATE.items():
    cn_names = sorted({k[2] for k in csv_v if k[1] == cid})
    miss[cn] = {n: {"csv": sum(csv_v[(p, cid, n)] for p in pcts), "cvr": sum(cvr_v[(p, cid, n)] for p in pcts),
                    "csv_in_precincts_without_cvr": sum(csv_v[(r["pct"], cid, n)] for r in none)} for n in cn_names}
    miss[cn]["Write-in"] = {"cvr": sum(v for k, v in cvr_v.items() if k[1] == cid and k[2] == "Write-in")}  # the CSV has no write-in rows
    print(f"\n{cn}: rank-1 votes  CSV | CVR | CSV-CVR | in precincts with no CVR ballots")
    for n, d in miss[cn].items():
        if n == "Write-in": continue
        print(f"  {n:32s} {d['csv']:>8,} {d['cvr']:>8,} {d['csv'] - d['cvr']:>+8,} {d['csv_in_precincts_without_cvr']:>8,}")
json.dump({"precincts": rows, "missing_first_choices": miss, "gap_by_group": gap}, open(OUT_JSON, "w"), indent=1)
