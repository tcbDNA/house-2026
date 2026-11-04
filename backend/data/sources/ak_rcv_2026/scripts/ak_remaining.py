"""Ballots the Division had received but not counted: its "Election Statistics" table (issued and received, by type) against
the counting groups in the precinct results file (outputs/dashboard/coverage.csv); plus the 2024 final CVR's counting groups.
usage: python3 -I ak_remaining.py <results page html> <coverage.csv> <rcv_2024_final_cvr.json>"""
import csv, html, json, re, sys
t = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", t); t = html.unescape(re.sub(r"<[^>]+>", " ", t)); t = re.sub(r"\s+", " ", t)
m = re.search(r"Table last updated (.*?)\. Ballot Type Number Issued Number Received (.*?) Cast Vote Record", t)
print("Division table last updated", m.group(1))
types = {k.strip(): (int(a.replace(",", "")), int(b.replace(",", ""))) for k, a, b in re.findall(r"([A-Za-z][A-Za-z\- ()]+?) ([\d,]+) ([\d,]+)", m.group(2))}
for k, (a, b) in types.items(): print(f"  {k:30s} issued {a:>7,} received {b:>7,}")
cov = {r["group"]: int(r["ballots_precinct_file"]) for r in csv.DictReader(open(sys.argv[2]))}
early_rec = types["Early Vote"][1]
abs_rec = sum(b for k, (a, b) in types.items() if k != "Early Vote")
print(f"early vote: received {early_rec:,}, counted {cov['Early Voting']:,}, not yet counted {early_rec - cov['Early Voting']:,}")
print(f"absentee (mail, fax, online, in-person absentee, special needs): received {abs_rec:,}, counted {cov['Absentee']:,}, not yet counted {abs_rec - cov['Absentee']:,}")
print(f"together {early_rec - cov['Early Voting'] + abs_rec - cov['Absentee']:,}; questioned ballots counted so far {cov['Question']:,}")
for k in ("By Mail", "Online Delivery"):
    a, b = types[k]; print(f"{k}: issued but not yet received {a - b:,}")
g = next(c for c in json.load(open(sys.argv[3]))["contests"] if c["contest"] == "U.S. Representative")["by_counting_group"]
print("2024 final CVR, U.S. House ballots by counting group:", {k: f"{v:,}" for k, v in g.items()})
