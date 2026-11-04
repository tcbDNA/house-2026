"""Exhausted ballots in Alaska's statewide ranked-choice counts, from the Division's official RCV Detailed Reports
(PDF text via pypdf), beside the 2026 count of the Nov 4 CVR (the dashboard's contests.csv and rounds.csv).
  exhaustion rate = exhausted ballots in the final round / continuing ballots in round 1
  inactive rate   = (exhausted + overvoted) in the final round / (round-1 continuing + round-1 overvotes)
  eliminated share = exhausted ballots / round-1 votes of the candidates eliminated (every exhausted ballot began with one)
usage: <python with pypdf> -I ak_exhaustion_history.py <out.csv> <dashboard dir> <label> <report.pdf> [<label> <report.pdf> ...]"""
import csv, re, sys
from pypdf import PdfReader

OUT, DASH, args = sys.argv[1], sys.argv[2], sys.argv[3:]
rows = []


def add(election, contest, source, r1, final, eliminated):
    cont1 = sum(r1["votes"].values())
    elim = sum(r1["votes"][c] for c in eliminated)
    rows.append({"election": election, "contest": contest, "source": source, "rounds": final["round"],
                 "round1_continuing": cont1, "blanks": r1["blanks"], "round1_overvotes": r1["overvotes"],
                 "exhausted_final": final["exhausted"], "overvotes_final": final["overvotes"],
                 "exhaustion_rate": final["exhausted"] / cont1,
                 "inactive_rate": (final["exhausted"] + final["overvotes"]) / (cont1 + r1["overvotes"]),
                 "eliminated_first_choices": elim, "exhausted_share_of_eliminated": final["exhausted"] / elim if elim else ""})


for label, pdf in zip(args[::2], args[1::2]):
    t = re.sub(r"\s+", " ", " ".join(p.extract_text() or "" for p in PdfReader(pdf).pages))
    contest = re.search(r"General Election (.*?) Official results", t) or re.search(r"OFFICIAL RESULTS (.*?) Official results", t)
    rounds = []
    for m in re.finditer(r"Round (\d+) Candidate Votes Percentage (.*?) Continuing Ballots Total ([\d,]+) Blanks ([\d,]+) Exhausted ([\d,]+) Overvotes ([\d,]+)", t):
        votes = {k.strip(): int(v.replace(",", "")) for k, v in re.findall(r"([A-Z][^\d%]*?) ([\d,]+) [\d.]+%", m.group(2))}
        rounds.append({"round": int(m.group(1)), "votes": {k: v for k, v in votes.items() if v}, "continuing": int(m.group(3).replace(",", "")),
                       "blanks": int(m.group(4).replace(",", "")), "exhausted": int(m.group(5).replace(",", "")), "overvotes": int(m.group(6).replace(",", ""))})
    r1, fin = rounds[0], rounds[-1]
    assert sum(r1["votes"].values()) == r1["continuing"], (pdf, r1)
    add(label, contest.group(1).strip() if contest else "", pdf.split("/")[-1], r1, fin, [c for c in r1["votes"] if c not in fin["votes"]])

# 2026, scanned ballots on the Nov 4 CVR
con = list(csv.DictReader(open(f"{DASH}/contests.csv")))
rnd = list(csv.DictReader(open(f"{DASH}/rounds.csv")))
for c in con:
    rr = [r for r in rnd if r["contest_id"] == c["contest_id"]]
    def at(k):
        x = [r for r in rr if int(r["round"]) == k]
        return {"round": k, "votes": {r["item"]: int(r["votes"]) for r in x if r["item_type"] == "candidate" and int(r["votes"])},
                "blanks": int(c["blanks"]), "exhausted": next(int(r["votes"]) for r in x if r["item_type"] == "exhausted"),
                "overvotes": next(int(r["votes"]) for r in x if r["item_type"] == "overvotes")}
    n = max(int(r["round"]) for r in rr)
    r1, fin = at(1), at(n)
    add("2026 general (Nov 4 CVR, scanned ballots only)", c["contest"], "contests.csv, rounds.csv", r1, fin, [k for k in r1["votes"] if k not in fin["votes"]])

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows:
    print(f"{r['election']:48s} {r['contest']:32s} rounds {r['rounds']}  exhausted {r['exhausted_final']:>7,} / {r['round1_continuing']:>7,} = {100 * r['exhaustion_rate']:.2f}%"
          f"  inactive {100 * r['inactive_rate']:.2f}%  of eliminated candidates' {r['eliminated_first_choices']:,}: {100 * r['exhausted_share_of_eliminated']:.1f}%")
