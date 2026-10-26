import re, sys, html as H
def strip(s):
    return H.unescape(re.sub(r'<[^>]+>', '', s)).replace('\xa0', ' ').strip()
def parse(h):
    title = strip(re.search(r'<title>(.*?)</title>', h, re.S).group(1))
    tables = []
    for m in re.finditer(r'<table class="data[^"]*"[^>]*>(.*?)</table>', h, re.S):
        tables.append(m.group(1))
    if not tables:
        return title, None, [], []
    t = max(tables, key=lambda s: s.count('<tr'))
    rows = re.findall(r'<tr([^>]*)>(.*?)</tr>', t, re.S)
    hdr = None; out = []
    for attrs, body in rows:
        cls = re.search(r'class="([^"]*)"', attrs)
        cls = cls.group(1) if cls else ''
        if 'header' in cls:
            hdr = [strip(x) for x in re.findall(r'<th[^>]*>(.*?)</th>', body, re.S)]
            continue
        tds = re.findall(r'<td[^>]*>(.*?)</td>', body, re.S)
        if not tds: continue
        a = re.search(r'class="normal_pollster_name"[^>]*>(.*?)</a>', tds[0], re.S)
        name = strip(a.group(1)) if a else strip(tds[0])
        link = re.search(r'href="([^"]*)"', tds[0])
        did = re.search(r'data-id="(\d+)"', attrs)
        out.append(dict(cls=cls, data_id=did.group(1) if did else '', pollster=name,
                        link=link.group(1) if link else '', cells=[strip(x) for x in tds]))
    smalls = [s for s in tables if s is not t]
    return title, hdr, out, smalls
if __name__ == '__main__':
    h = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    title, hdr, rows, smalls = parse(h)
    print(title); print(hdr)
    for r in rows[:8]: print(r['cls'], r['data_id'], r['pollster'], r['cells'][1:])
    print(len(rows), sum('isInRcpAvg' in r['cls'] for r in rows))
