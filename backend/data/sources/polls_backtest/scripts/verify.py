"""Compare each CSV race's average and in-average poll set (from archive) to the current RCP feed."""
import csv, json, os, sys
from collections import defaultdict
B = sys.argv[1]
for fn in ['senate_2022_rcp_final.csv', 'senate_2024_rcp_final.csv', 'generic_ballot_rcp_final.csv']:
    p = os.path.join(B, fn)
    if not os.path.exists(p): continue
    by = defaultdict(list)
    for r in csv.DictReader(open(p)):
        by[(r['year'], r['state'], r['race_id'])].append(r)
    for (y, st, rid), rows in by.items():
        fp = os.path.join(B, 'rcp_feeds', f'race_{rid}_polling_data_2026-10-26.json')
        if not rid or not os.path.exists(fp) or rows[0]['data_source'] != 'wayback_page':
            print(y, st, rid, rows[0]['data_source'], 'no feed comparison'); continue
        f = json.load(open(fp))
        fa = [x for x in f['poll'] if x['type'] == 'rcp_average']
        a = [r for r in rows if r['pollster'] == 'RCP Average'][0]
        def vals(x):
            d = {c['affiliation'][0]: c['value'] for c in x['candidate']}
            return d
        fav = vals(fa[0]) if fa else {}
        wb_in = sorted((r['date_raw'], r['dem'] or r['ind'], r['rep']) for r in rows if r['in_average'] == 'yes')
        fd_in = []
        for x in f['poll']:
            if x['type'] == 'poll_rcp_avg':
                v = vals(x)
                fd_in.append((x['date'], v.get('D') or v.get('I', ''), v.get('R', '')))
        fd_in.sort()
        avg_same = fa and fa[0]['date'] == a['date_raw'] and fav.get('R') == a['rep']
        print(y, st, rid, 'AVG', 'same' if avg_same else f"DIFF wb={a['date_raw']} D{a['dem']} R{a['rep']} feed={fa[0]['date'] if fa else None} {fav}",
              '| in-avg', 'same' if wb_in == fd_in else f'DIFF wb-only={sorted(set(wb_in)-set(fd_in))} feed-only={sorted(set(fd_in)-set(wb_in))}')
