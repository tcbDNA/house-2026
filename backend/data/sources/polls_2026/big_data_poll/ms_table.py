"""Lay a saved MarketSight crosstab page's results table out on a grid (rowSpan/colSpan honored), then print the
rows of one question for the named columns. Header row 0 = column groups, row 1 = column labels.
usage: python3 ms_table.py <page.html> <question substring> <group>:<label> ..."""
import re, sys, html
t = open(sys.argv[1], errors="replace").read()
ts = t.find('id="PageContent_m_itemView_CrosstabView_ResultsTable"'); ts = t.rfind("<table", 0, ts)
tab = t[ts:t.find("</table>", ts)]
clean = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()
grid, taken = [], {}
for r, tr in enumerate(re.findall(r"<tr[^>]*>(.*?)</tr>", tab, flags=re.S)):
    row, c = {}, 0
    for m in re.finditer(r"<t[dh]([^>]*?)(?:/>|>(.*?)</t[dh]>)", tr, flags=re.S):
        while (r, c) in taken: c += 1
        cs = int((re.search(r'colSpan="(\d+)"', m.group(1), re.I) or [0, 1])[1])
        rs = int((re.search(r'rowSpan="(\d+)"', m.group(1), re.I) or [0, 1])[1])
        for dr in range(rs):
            for dc in range(cs): taken[(r + dr, c + dc)] = clean(m.group(2)) if (dr, dc) == (0, 0) or dr == 0 else None
        c += cs
    grid.append(r)
ncol = max(c for _, c in taken) + 1
cell = lambda r, c: taken.get((r, c))
group = {}
g = None
for c in range(ncol):
    v = cell(0, c)
    if v is not None and v != "": g = v
    group[c] = g
cols = {(group[c], cell(1, c)): c for c in range(ncol) if cell(1, c)}
want = [tuple(w.split(":", 1)) for w in sys.argv[3:]]
for w in want:
    assert w in cols, (w, [k for k in cols if k[0] == w[0]])
on = seen = False
for r in range(2, len(grid)):
    lab = cell(r, 0) or ""
    if sys.argv[2] in lab: on = True; continue
    if on and lab and cell(r, 1) == lab:                # a title row spanning the table
        if seen: break
        continue
    if on: seen = True; print(f"{lab[:40]:40s}", " | ".join(f"{w[1][:14]}={cell(r, cols[w])}" for w in want))
