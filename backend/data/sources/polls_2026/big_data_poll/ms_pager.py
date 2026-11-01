"""Step through a public MarketSight crosstab view page by page (the view's own pager, as a browser does) and
save each page's HTML. usage: python3 ms_pager.py <url> <outdir> <pages>"""
import re, sys, html, urllib.request, urllib.parse, http.cookiejar
url, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "Mozilla/5.0 (Macintosh) Chrome/124")]
t = op.open(url, timeout=90).read().decode("utf-8", "replace")
open(f"{out}/page_01.html", "w").write(t)
def fields(t):
    f = {}
    for m in re.finditer(r'<input([^>]+)>', t):
        a = m.group(1)
        nm = re.search(r'name="([^"]+)"', a); v = re.search(r'value="([^"]*)"', a)
        tp = re.search(r'type="([^"]+)"', a)
        if nm and (not tp or tp.group(1) in ("hidden", "text")):
            f[html.unescape(nm.group(1))] = html.unescape(v.group(1)) if v else ""
    return f
P = "ctl00$PageContent$m_itemView$CrosstabView$TopPager$"
for p in range(2, n + 1):
    f = fields(t)
    f["__EVENTTARGET"] = P + "PagerManualEnter"; f["__EVENTARGUMENT"] = ""
    f[P + "PagerManualEnter"] = str(p)
    act = re.search(r'<form[^>]+action="([^"]+)"', t).group(1)
    post = urllib.parse.urljoin(url, html.unescape(act))
    t = op.open(post, data=urllib.parse.urlencode(f).encode(), timeout=90).read().decode("utf-8", "replace")
    open(f"{out}/page_{p:02d}.html", "w").write(t)
    cur = re.search(r'm_currentPageHiddenField"[^>]*value="(\d+)"', t)
    print(p, "current", cur.group(1) if cur else "?", len(t))
