"""Parse Georgia Votes county pages (georgiavotes.com/county?c=N) for GA-01's counties into ga01_counties.csv.
usage: python3 -I ga01_parse.py <dir with ids.txt and <County>.html>"""
import re, html, sys, json, csv
d = sys.argv[1]
num = lambda s: float(s.replace(",", ""))
rows = []
for ln in open(f"{d}/ids.txt"):
    n, c = ln.split()
    t = open(f"{d}/{n}.html", errors="ignore").read()
    x = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S); x = re.sub(r"<[^>]+>", " ", x); x = re.sub(r"\s+", " ", html.unescape(x))
    r = {"county": n, "gv_id": c}
    m = re.search(r"([\d,]+) people in [A-Za-z .]+ County have voted early in the 2026 general election , ([\d.]+)% of the county.s registered voters\. ([\d,]+) voted by mail and ([\d,]+) early in person\.", x)
    r.update(votes=num(m.group(1)), pct_reg=num(m.group(2)), mail=num(m.group(3)), early=num(m.group(4)))
    m = re.search(r"at this point in 2022 , when ([\d,]+) had voted", x); r["v22"] = num(m.group(1))
    m = re.search(r"It has ([\d,]+) registered voters", x); r["reg"] = num(m.group(1))
    seg = x[x.find("Show the numbers Race 2026 2024 2022"):][:300]
    for g in ("White", "Black", "Hispanic", "Asian"):
        mm = re.search(rf"{g} ([\d.]+)% ([\d.]+)% ([\d.]+)%", seg); r[f"{g.lower()}_26"], r[f"{g.lower()}_24"], r[f"{g.lower()}_22"] = map(float, mm.groups())
    for lab, key in (("2024 President", "pres24"), ("2022 Governor", "gov22"), ("2022 U.S. Senate", "sen22")):
        mm = re.search(rf"{re.escape(lab)} ([RD])\+([\d.]+) ([RD])\+([\d.]+)", x)
        r[key] = (1 if mm.group(1) == "D" else -1) * float(mm.group(2))
    m = re.search(r"Early Voters ([\d,]+) \( ([\d.]+)% \).*?Day Of Voters ([\d,]+) \( ([\d.]+)% \).*?Non-Voters ([\d,]+) \( ([\d.]+)% \)", x)
    r.update(h_early=num(m.group(1)), h_dayof=num(m.group(3)), h_none=num(m.group(5)))
    rows.append(r)
w = csv.DictWriter(open(f"{d}/ga01_counties.csv", "w", newline=""), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in sorted(rows, key=lambda r: -r["votes"]):
    print(f"{r['county']:10s} votes {r['votes']:>7,.0f} vs22 {r['votes']/r['v22']-1:+6.1%} reg {r['pct_reg']:4.1f}% black {r['black_22']:4.1f}->{r['black_24']:4.1f}->{r['black_26']:4.1f} white {r['white_22']:4.1f}->{r['white_26']:4.1f} pres24 {r['pres24']:+6.1f} gov22 {r['gov22']:+6.1f} sen22 {r['sen22']:+6.1f} new {r['h_none']/r['votes']:.1%}")
