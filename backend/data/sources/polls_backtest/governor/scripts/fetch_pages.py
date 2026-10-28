"""Fetch the last good Wayback capture before the cutoff for each race page.
usage: python3 -I fetch_pages.py <cutoff YYYYMMDDhhmmss> <outdir> <pages.tsv: tag<TAB>url> <cdx listing files...>
Candidates are captures with status 200 or '-' (revisit), newest first. A capture is "good" when it is
served with HTTP 200 and contains an RCP poll table header. Results are appended
to <outdir>/_captures.tsv (tag, capture_utc, url, file); NONE when no good capture precedes the cutoff.
Downloaded files are only parsed as text (parse_epolls.py); nothing in them is executed."""
import os, re, subprocess, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_epolls import parse
from select_captures import norm

HERE = os.path.dirname(os.path.abspath(__file__))
cut, outdir, pages_fn = sys.argv[1], sys.argv[2], sys.argv[3]
caps = defaultdict(set)
for fn in sys.argv[4:]:
    for line in open(fn, encoding='utf-8', errors='replace'):
        f = line.split()
        if len(f) >= 3 and f[0].isdigit() and f[2] in ('200', '-'):
            caps[norm(f[1])].add(f[0])
capfile = os.path.join(outdir, '_captures.tsv')
if not os.path.exists(capfile):
    open(capfile, 'w').write('tag\tcapture_utc\turl\tfile\n')
done = {l.split('\t')[0] for l in open(capfile)}
log = os.path.join(outdir, '_fetch_log.tsv')
if not os.path.exists(log):
    open(log, 'w').write('fetched_utc\tcapture_ts\tmemento_datetime\torig_last_modified\torig_date\tbytes\tfile\turl\n')
for line in open(pages_fn):
    if not line.strip() or line.startswith('#'):
        continue
    tag, url = line.rstrip('\n').split('\t')[:2]
    if tag in done:
        continue
    cands = sorted((t for t in caps.get(norm(url), ()) if t < cut), reverse=True)
    got = None
    for ts in cands[:8]:
        fn = f'{tag}_wayback_{ts}.html'
        path = os.path.join(outdir, fn)
        r = subprocess.run([os.path.join(HERE, 'wb_fetch.sh'), ts, url, path, log], capture_output=True, text=True)
        print(r.stdout.strip(), r.stderr.strip(), file=sys.stderr)
        if r.returncode != 0 or not os.path.exists(path):
            continue
        try:
            title, hdr, rows, _ = parse(open(path, encoding='utf-8', errors='replace').read())
        except Exception as e:
            hdr, rows = None, []
        if hdr:  # a page with a poll-table header (possibly no polls yet)
            got = (ts, fn)
            break
        print(f'  not a usable page ({tag} {ts}); trying an older capture', file=sys.stderr)
        bad = os.path.join(os.path.dirname(HERE), 'bad_captures')
        os.makedirs(bad, exist_ok=True)
        os.rename(path, os.path.join(bad, fn))
    with open(capfile, 'a') as f:
        f.write(f'{tag}\t{got[0] if got else "NONE"}\t{url}\t{got[1] if got else ""}\n')
    print(tag, got[0] if got else 'NONE', f'({len(cands)} candidates before cutoff)')
