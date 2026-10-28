"""Print the Markdown tables used in README.md, straight from the CSVs, captures, fetch logs and feeds.
usage: python3 -I readme_tables.py <polls_backtest/governor dir>"""
import csv, glob, json, os, re, sys
from collections import OrderedDict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_epolls import parse

B = sys.argv[1]


def md(d):  # 2018-10-24 -> 10/24
    return f'{int(d[5:7])}/{int(d[8:10])}' if d else ''


def ts_h(ts):
    return f'{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}'


def final_tables():
    for fn, title in [('governor_2018_rcp_final.csv', '2018 governor'), ('governor_2022_rcp_final.csv', '2022 governor'),
                      ('generic_ballot_2018_rcp_final.csv', '2018 generic ballot')]:
        races = OrderedDict()
        for r in csv.DictReader(open(os.path.join(B, fn))):
            races.setdefault((r['state'], r['race_id']), []).append(r)
        print(f'\n#### {title} ({len(races)} averages)\n')
        third = 'governor' in fn
        print('| State | Race | Window | D | R |' + (' Third |' if third else '') + ' RCP spread | Polls in avg (of which Rasmussen) | Polls listed | Source |')
        print('|---|---|---|---|---|' + ('---|' if third else '') + '---|---|---|---|')
        for (st, rid), rows in races.items():
            a = [r for r in rows if r['pollster'] == 'RCP Average'][0]
            polls = [r for r in rows if r['pollster'] != 'RCP Average']
            ina = [r for r in polls if r['in_average'] == 'yes']
            ras = sum(1 for r in ina if r['excluded_pollster'] == 'yes')
            race = re.sub(r'^\d{4} ', '', a['race'])
            race = re.sub(r'^.*? (Governor|Congressional Vote) - ', '', race) if 'Governor' in race else race
            if a['data_source'] == 'wayback_page':
                ts = re.search(r'/web/(\d{14})/', a['archive_url']).group(1)
                src = f'Wayback {ts_h(ts)}'
            else:
                src = '**RCP feed** (see caveats)'
            t = f" {a['third_candidate'].split(' (')[0]} {a['third']} |" if third and a['third'] else (' |' if third else '')
            print(f"| {st} | {race} ({rid}) | {md(a['start'])}–{md(a['end'])} | {a['dem']} | {a['rep']} |{t} {a['spread']} | {len(ina)} ({ras}) | {len(polls)} | {src} |")


def page_summary(path):
    t, h, rows, _ = parse(open(path, encoding='utf-8', errors='replace').read())
    if not h:
        return 'no poll table'
    cand = [x for x in h if re.search(r'\([A-Z]+\)', x)]
    n = sum(1 for r in rows if r['data_id'])
    if any('final results' in r['pollster'].lower() for r in rows):
        fr = [r for r in rows if 'final results' in r['pollster'].lower()][0]
        return f'Final Results row ({fr["cells"][-1]}); no RCP Average row; {n} polls listed'
    a = [r for r in rows if 'rcpAvg' in r['cls']]
    if not a:
        return f'No RCP Average row; {n} polls listed' if n else 'No polls listed (header only: ' + ', '.join(cand) + ')'
    c = a[0]['cells']
    vals = ' / '.join(f'{re.sub(r" ?[(].*", "", cand[i])} {c[len(c) - 1 - len(cand) + i]}' for i in range(len(cand)))
    k = sum('isInRcpAvg' in r['cls'] for r in rows)
    return f'RCP Average {c[1]}: {vals} ({c[-1]}); {k} of {n} listed polls in average'


def files_table():
    logs = {}
    for lp in glob.glob(os.path.join(B, '*', '_fetch_log.tsv')):
        for r in csv.DictReader(open(lp), delimiter='\t'):
            if 'file' in r and r.get('orig_last_modified') is not None:
                logs[r['file']] = r
    print('\n| File | Live URL | Archive URL | Capture (UTC) | Page last modified (orig. header) | What the page shows |')
    print('|---|---|---|---|---|---|')
    for sub in ['rcp_2018_governor', 'rcp_2022_governor', 'rcp_generic_ballot', 'other_captures', 'rcp_index']:
        for fn in sorted(os.listdir(os.path.join(B, sub))):
            if not fn.endswith('.html'):
                continue
            lg = logs.get(fn, {})
            url = lg.get('url', '')
            ts = re.search(r'_(\d{14})\.html$', fn).group(1)
            what = page_summary(os.path.join(B, sub, fn)) if sub != 'rcp_index' else 'RCP governor map (index of race pages)'
            print(f"| `{sub}/{fn}` | {url} | https://web.archive.org/web/{ts}/{url} | {ts_h(ts)} | {lg.get('orig_last_modified', '')} | {what} |")


def feeds_table():
    print('\n| File | URL | Title | RCP average in feed |')
    print('|---|---|---|---|')
    for p in sorted(glob.glob(os.path.join(B, 'rcp_feeds', 'race_*.json'))):
        d = json.load(open(p))
        m = d['moduleInfo']
        P = d.get('poll') or []
        a = [x for x in P if x['type'] == 'rcp_average']
        if not a:
            s = 'none'
        else:
            v = ', '.join(f"{c['name']} {c['value']}" for c in a[0]['candidate'])
            k = sum(1 for x in P if x['type'] == 'poll_rcp_avg')
            s = (f"shown: {a[0]['date']}, {v} ({k} polls flagged)" if str(m.get('show_rcp_avg')) == '1'
                 else f"hidden (`show_rcp_avg: 0`, date {a[0]['date']}): {v}")
        print(f"| `rcp_feeds/{os.path.basename(p)}` | https://orig.realclearpolitics.com/poll/race/{m['id']}/polling_data.json | {m['title']} | {s} |")


if __name__ == '__main__':
    final_tables()
    files_table()
    feeds_table()
