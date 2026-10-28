"""Compare each race's average and in-average poll set in the CSVs with RCP's current feed
(adapted from ../../scripts/verify.py). For archive-based races, prints whether the feed's average and
averaged polls are the same; for differing polls, prints the feed's `updated` stamp (when RCP last saved
the poll entry). For feed-based races, compares the feed with the archived page instead.
usage: python3 -I verify_gov.py <polls_backtest/governor dir> <races.json>"""
import csv, json, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_gov import captures, from_wayback  # noqa: E402  (build_gov reads sys.argv[1] as BASE)

B = sys.argv[1]
FEED = 'race_{}_polling_data_2026-10-28.json'


def vals(x):
    d = {}
    for c in x['candidate']:
        k = c['affiliation'][0] if c.get('affiliation') in ('Democrat', 'Republican') else 'T'
        d.setdefault(k, c['value'])
    return d


races = json.load(open(sys.argv[2]))
tags = {(str(r['year']), r['state'].upper(), str(r.get('rid', ''))): r for r in races if not r.get('exclude')}
for fn in ['governor_2018_rcp_final.csv', 'governor_2022_rcp_final.csv', 'generic_ballot_2018_rcp_final.csv']:
    p = os.path.join(B, fn)
    if not os.path.exists(p):
        continue
    by = defaultdict(list)
    for r in csv.DictReader(open(p)):
        by[(r['year'], r['state'], r['race_id'])].append(r)
    for (y, st, rid), rows in by.items():
        fp = os.path.join(B, 'rcp_feeds', FEED.format(rid))
        if not os.path.exists(fp):
            print(y, st, rid, 'no feed file'); continue
        f = json.load(open(fp))
        P = f.get('poll') or []
        fa = [x for x in P if x['type'] == 'rcp_average']
        show = str(f['moduleInfo'].get('show_rcp_avg'))
        a = [r for r in rows if r['pollster'] == 'RCP Average'][0]
        fav = vals(fa[0]) if fa else {}
        if rows[0]['data_source'] == 'wayback_page':
            other = sorted((r['date_raw'], r['dem'], r['rep']) for r in rows if r['in_average'] == 'yes')
            other_avg = (a['date_raw'], a['dem'], a['rep'])
            label = 'wb'
        else:  # feed-based: compare feed with the archived page
            rr = tags.get((y, st, rid))
            cap = captures(rr['sub']).get(rr['tag']) if rr else None
            if not cap:
                print(y, st, rid, 'feed-based; no archive copy to compare'); continue
            wrows, _, why = from_wayback(int(y), st, rid, cap[0], cap[1], cap[2], f)
            if not wrows:
                print(y, st, rid, f'feed-based; archive {cap[0]}: {why}'); continue
            wa = [r for r in wrows if r['pollster'] == 'RCP Average'][0]
            other = sorted((r['date_raw'], r['dem'], r['rep']) for r in wrows if r['in_average'] == 'yes')
            other_avg = (wa['date_raw'], wa['dem'], wa['rep'])
            label = f'archive {cap[0]}'
        fd_in, upd = [], {}
        for x in P:
            if x['type'] == 'poll_rcp_avg':
                v = vals(x)
                k = (x['date'], v.get('D', ''), v.get('R', ''))
                fd_in.append(k)
                upd[k] = f"{x['pollster']} updated {x.get('updated')}"
        fd_in.sort()
        fdesc = f"feed(show_rcp_avg={show})={fa[0]['date'] if fa else None} D{fav.get('D')} R{fav.get('R')}" + (f" T{fav['T']}" if 'T' in fav else '')
        avg_same = bool(fa) and fa[0]['date'] == other_avg[0] and fav.get('R') == other_avg[2] and fav.get('D') == other_avg[1]
        vals_same = bool(fa) and fav.get('R') == other_avg[2] and fav.get('D') == other_avg[1]
        s_avg = 'same' if avg_same else ('same values, feed date placeholder' if vals_same and fa and fa[0]['date'].startswith('12/31') else f'DIFF {label}={other_avg[0]} D{other_avg[1]} R{other_avg[2]} {fdesc}')
        if fd_in == other:
            s_in = 'same'
        else:
            only_o = sorted(set(other) - set(fd_in))
            only_f = sorted(set(fd_in) - set(other))
            s_in = f'DIFF {label}-only={only_o} feed-only={[(k, upd[k]) for k in only_f]}'
        print(y, st, rid, rows[0]['data_source'], 'AVG', s_avg, '| in-avg', s_in, sep=' ')
