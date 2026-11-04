"""Combine the CVR's ranked-choice rounds with the ballots counted so far that are not in the CVR (precincts whose
ballots were counted by hand: first choices only, from the precinct results file).
  - scenario: the hand-counted ballots of each eliminated candidate move as that candidate's CVR ballots did in the
    same round (shares of its votes to each candidate, exhausted, overvote); their write-ins are left out
  - bounds: the finalists' margin if every hand-counted vote for a non-finalist, and every hand-counted write-in, went
    to one finalist or the other
Write-ins counted by hand = the summary report's write-ins minus the CVR's rank-1 write-ins.
usage: <python with pypdf> -I ak_combine.py <rcv all-rounds.json> <cvr_vs_precinct.json> <ElectionSummaryReportRPT.pdf> <out.json>"""
import json, re, sys
from pypdf import PdfReader

rcv = {c["contest"]: c for c in json.load(open(sys.argv[1]))["contests"]}
gap = json.load(open(sys.argv[2]))["missing_first_choices"]
summ = re.sub(r"\s+", " ", " ".join(p.extract_text() or "" for p in PdfReader(sys.argv[3]).pages))
out = {}
for name in ("U.S. Senator", "U.S. Representative", "Governor / Lieutenant Governor"):
    # the summary prints each contest's rows, then "Total Times Cast ... Precincts Reported ...", then the contest title
    m = re.search(r"Write-in ([\d,]+) [\d.]+% Total Votes [\d,]+ Total Times Cast [\d,]+ / [\d,]+ [\d.]+% Precincts Reported: [\d]+ of [\d]+ \([\d.]+%\) " + re.escape(name), summ)
    wi_hand = int(m.group(1).replace(",", "")) - gap[name]["Write-in"]["cvr"]
    H = {k: v["csv_in_precincts_without_cvr"] for k, v in gap[name].items() if k != "Write-in"}
    rounds = rcv[name]["rounds"]
    hold = dict(H); exh = ov = 0.0
    comb, order_ok = [], True
    for r in rounds:
        tot = {c: r["votes"][c] + hold.get(c, 0) for c in r["votes"]}
        comb.append({"round": r["round"], "votes": {c: round(v) for c, v in sorted(tot.items(), key=lambda x: -x[1])}})
        if "eliminated" in r:
            e = r["eliminated"]
            if min(tot, key=tot.get) != e: order_ok = False
            n_e = r["votes"][e]
            moved = hold.pop(e, 0)
            for dest, k in r["transfers"].items():
                share = moved * k / n_e
                if dest == "exhausted": exh += share
                elif dest == "overvote": ov += share
                else: hold[dest] = hold.get(dest, 0) + share
    fin = list(rounds[-1]["votes"])
    a, b = fin
    final = comb[-1]["votes"]
    base = {c: rounds[-1]["votes"][c] + H.get(c, 0) for c in fin}
    movable = sum(v for c, v in H.items() if c not in fin) + wi_hand
    out[name] = {"hand_counted_first_choices": H, "hand_counted_writeins": wi_hand,
                 "combined_rounds_scenario": comb, "elimination_order_unchanged": order_ok,
                 "scenario_final": final, "scenario_margin": {"leader": max(final, key=final.get), "votes": abs(final[a] - final[b]),
                                                              "pts": 100 * abs(final[a] - final[b]) / (final[a] + final[b])},
                 "bounds": {"finalists_before_hand_transfers": base, "hand_votes_that_could_move": movable,
                            f"{a}_minus_{b}_range": [base[a] - base[b] - movable, base[a] - base[b] + movable]}}
    print(f"\n== {name}: hand-counted first choices {H}, write-ins {wi_hand}")
    for r in comb: print(f"  round {r['round']}: " + "; ".join(f"{c} {v:,}" for c, v in r["votes"].items()))
    s = out[name]["scenario_margin"]
    print(f"  scenario: {s['leader']} by {s['votes']:,} ({s['pts']:.2f} pts); elimination order unchanged: {order_ok}")
    lo, hi = out[name]["bounds"][f"{a}_minus_{b}_range"]
    print(f"  bounds: {a} minus {b} from {lo:+,} to {hi:+,} ({movable:,} hand-counted votes for others or write-ins)")
json.dump(out, open(sys.argv[4], "w"), indent=1)
