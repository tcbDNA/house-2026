"""Compare the tabulator's rounds with the Division's official RCV Detailed Reports (PDF text via pypdf).
usage: <venv python> -I validate.py <rcv.json> [--csv out.csv] <report.pdf> <contest name> [...pairs]"""
import csv, json, re, sys
from pypdf import PdfReader
res = {c["contest"]: c for c in json.load(open(sys.argv[1]))["contests"]}
args = sys.argv[2:]
out_csv = None
if args[:1] == ["--csv"]: out_csv, args = args[1], args[2:]
allok = True
table = []
for pdf, name in zip(args[::2], args[1::2]):
    t = " ".join((p.extract_text() or "") for p in PdfReader(pdf).pages)
    t = re.sub(r"\s+", " ", t)
    mine = res[name]
    print(f"== {name} ({pdf.split('/')[-1]})")
    n_ok = 0
    for r in mine["rounds"]:
        m = re.search(rf"Round {r['round']} Candidate Votes Percentage (.*?) Continuing Ballots Total ([\d,]+) Blanks ([\d,]+) Exhausted ([\d,]+) Overvotes ([\d,]+)", t)
        off = dict(re.findall(r"([A-Z][^\d%]*?) ([\d,]+) [\d.]+%", m.group(1)))
        off = {k.strip(): int(v.replace(",", "")) for k, v in off.items() if int(v.replace(",", ""))}
        o_tot = [int(x.replace(",", "")) for x in m.groups()[1:]]
        mine_tot = [r["continuing"], r["blanks"], r["exhausted"], r["overvotes"]]
        diffs = {k: r["votes"].get(k, 0) - v for k, v in off.items() if r["votes"].get(k, 0) != v}
        diffs.update({k: v for k, v in r["votes"].items() if k not in off and v})
        tot_d = [a - b for a, b in zip(mine_tot, o_tot)]
        ok = not diffs and not any(tot_d)
        allok &= ok
        n_ok += ok
        print(f" round {r['round']}: {'MATCH' if ok else 'DIFF'}  official {off} cont/blank/exh/over {o_tot}" + ("" if ok else f"  mine-minus-official {diffs} {tot_d}"))
    table.append({"contest": name, "report": pdf.split("/")[-1], "rounds": len(mine["rounds"]), "rounds_matching": n_ok,
                  "candidates": len(mine["rounds"][0]["votes"])})
print("ALL MATCH" if allok else "SOME DIFFER")
if out_csv:
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0])); w.writeheader(); w.writerows(table)
