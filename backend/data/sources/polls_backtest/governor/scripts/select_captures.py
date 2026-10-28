"""List Wayback captures per race page from windowed CDX listings, newest first.
usage: python3 -I select_captures.py <cutoff YYYYMMDDhhmmss> <cdx listing files...>
CDX lines: timestamp original statuscode length.  Status 200 and '-' (revisit: same payload as an
earlier capture, served in full by Wayback) count as captures; 3xx/4xx/5xx are ignored.
Prints one line per page: page_url  n_before_cutoff  ts_list_before_cutoff(desc)  ts_list_after_cutoff(asc)"""
import re, sys
from collections import defaultdict

def norm(u):
    u = re.sub(r'^https?://', '', u)
    u = re.sub(r'^www\.', '', u)
    u = u.replace(':80/', '/')
    u = re.split(r'[?#]', u)[0]
    m = re.match(r'(.*?\.html)', u)
    return m.group(1) if m else u

if __name__ == '__main__':
    cut = sys.argv[1]
    caps = defaultdict(set)
    for fn in sys.argv[2:]:
        for line in open(fn, encoding='utf-8', errors='replace'):
            f = line.split()
            if len(f) < 3 or not f[0].isdigit():
                continue
            ts, orig, st = f[0], f[1], f[2]
            if st not in ('200', '-'):
                continue
            u = norm(orig)
            if not re.search(r'-\d+\.html$', u):
                continue
            caps[u].add((ts, st))
    for u in sorted(caps):
        before = sorted([c for c in caps[u] if c[0] < cut], reverse=True)
        after = sorted([c for c in caps[u] if c[0] >= cut])
        print(u, len(before), ','.join(f'{t}:{s}' for t, s in before[:8]) or '-', ','.join(f'{t}:{s}' for t, s in after[:3]) or '-', sep='\t')
