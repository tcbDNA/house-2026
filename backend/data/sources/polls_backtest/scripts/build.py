"""Build tidy CSVs of final RCP averages + poll lists from archived RCP pages / RCP feeds.
usage: python3 -I build.py <polls_backtest_dir>"""
import csv, json, os, re, sys, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse22 import parse as parse22
from parse24 import poll_lists

BASE = sys.argv[1]
FEEDS = os.path.join(BASE, 'rcp_feeds')
FEED_URL = 'https://orig.realclearpolitics.com/poll/race/{}/polling_data.json'
COLS = ['year', 'state', 'pollster', 'start', 'end', 'population', 'n', 'dem', 'rep', 'in_average',
        'excluded_pollster', 'source_url', 'archive_url',
        'race', 'race_id', 'dem_candidate', 'rep_candidate', 'spread', 'date_raw', 'sample_raw',
        'data_source', 'notes']
WINDOW_END = {2022: '20221109080000', 2024: '20241106080000'}
WINDOW_START = {2022: '20221106000000', 2024: '20241103000000'}
EXCL = re.compile(r'rasmussen|activote', re.I)

def captures(sub):
    d = {}
    p = os.path.join(BASE, sub, '_captures.tsv')
    if os.path.exists(p):
        for line in open(p):
            f = line.rstrip('\n').split('\t')
            if len(f) >= 4 and f[1].isdigit() and f[3]:
                d[f[0]] = (f[1], f[2], os.path.join(BASE, sub, f[3]))
            elif f[0] not in d:
                d[f[0]] = None
    return d

def load_feed(rid):
    p = os.path.join(FEEDS, f'race_{rid}_polling_data_2026-10-26.json')
    return json.load(open(p)) if os.path.exists(p) else None

def feed_dates(feed):
    out = {}
    if feed:
        for p in feed.get('poll') or []:
            out[str(p['id'])] = (p.get('data_start_date'), p.get('data_end_date'))
    return out

def iso_dates(date_raw, yr_end_hint, elec_year):
    """date_raw like '11/5 - 11/7'. Year from the feed's data_end_date when its month/day match, else election year."""
    m = re.match(r'\s*(\d{1,2})/(\d{1,2})\s*-\s*(\d{1,2})/(\d{1,2})\s*$', date_raw or '')
    if not m:
        return '', '', f'unparsed date "{date_raw}"'
    sm, sd, em, ed = map(int, m.groups())
    note = ''
    ey = elec_year
    if yr_end_hint:
        hm = re.match(r'(\d{4})/(\d{2})/(\d{2})', yr_end_hint)
        if hm and int(hm.group(2)) == em and int(hm.group(3)) == ed:
            ey = int(hm.group(1))
        elif hm:
            ey = int(hm.group(1))
            note = f'feed end date {yr_end_hint} differs from page date'
    sy = ey if (sm, sd) <= (em, ed) else ey - 1
    if (sm, sd) > (em, ed) and sm - em < 6:
        # e.g. '10/30 - 10/2': end before start within the same season -> RCP typo; keep raw, flag
        sy = ey
        note = (note + '; ' if note else '') + f'RCP date "{date_raw}" has end before start (as published)'
    return f'{sy:04d}-{sm:02d}-{sd:02d}', f'{ey:04d}-{em:02d}-{ed:02d}', note

def sample(s):
    s = (s or '').strip()
    m = re.match(r'^(\d[\d,]*)\s*([A-Za-z]+)?$', s)
    if m:
        return (m.group(2) or ''), m.group(1).replace(',', '')
    if re.match(r'^[A-Za-z]+$', s):
        return s, ''
    return '', ''

def party(label):
    m = re.search(r'\((D|R|I|L|G|DFL)\)', label)
    return m.group(1) if m else ''

AFF = {'Democrat': 'D', 'Republican': 'R', 'Independent': 'I', 'Libertarian': 'L', 'Green': 'G'}

def pick(cands):
    """cands: list of (name, partycode, value). returns dem, rep, ind, dem_name, rep_name, note"""
    D = [c for c in cands if c[1] == 'D']
    R = [c for c in cands if c[1] == 'R']
    I = [c for c in cands if c[1] == 'I']
    note = ''
    rep = R[0] if R else None
    ind = None
    if D:
        dem = D[0]
        if I:
            ind = I[0]
    elif I:
        dem = I[0]; note = f'no Democrat in RCP table; dem column = {I[0][0]} (I)'
    else:
        dem = None
    return dem, rep, ind, note

def row_common(year, state, race, rid, src_url, arch_url, data_source):
    return dict(year=year, state=state.upper(), race=race, race_id=rid, source_url=src_url,
                archive_url=arch_url, data_source=data_source)

def from_wayback22(year, state, rid, ts, url, path, feed):
    title, hdr, rows, _ = parse22(open(path, encoding='utf-8', errors='replace').read())
    race = re.sub(r'^RealClearPolitics - Election (\d{4}|Other) - ', '', title)
    if not hdr:
        return None, race, 'no poll table'
    iD, iS, iSp = hdr.index('Date'), hdr.index('Sample'), hdr.index('Spread')
    ci = [i for i, h in enumerate(hdr) if party(h)]
    fd = feed_dates(feed)
    arch = f'https://web.archive.org/web/{ts}/{url}'
    out = []
    if any('final results' in r['pollster'].lower() for r in rows):
        return None, race, 'page already shows Final Results row'
    has_avg = any('rcpAvg' in r['cls'] for r in rows)
    if not has_avg:
        return None, race, 'page shows no RCP Average row'
    for r in rows:
        c = r['cells']
        if len(c) != len(hdr):
            continue
        is_avg = 'rcpAvg' in r['cls']
        if not is_avg and not r['data_id']:
            continue  # e.g. final results rows (none expected before polls close)
        cands = [(re.sub(r'\s*\(.*$', '', hdr[i]).strip(), party(hdr[i]), c[i]) for i in ci]
        dem, rep, ind, pnote = pick(cands)
        start, end, dnote = iso_dates(c[iD], fd.get(r['data_id'], (None, None))[1], year)
        pop, n = sample(c[iS])
        x = row_common(year, state, race, rid, url, arch, 'wayback_page')
        x.update(pollster='RCP Average' if is_avg else r['pollster'], start=start, end=end,
                 population='' if is_avg else pop, n='' if is_avg else n,
                 dem=dem[2] if dem else '', rep=rep[2] if rep else '', ind=ind[2] if ind else '',
                 dem_candidate=f'{dem[0]} ({dem[1]})' if dem else '', rep_candidate=f'{rep[0]} ({rep[1]})' if rep else '',
                 in_average='no' if is_avg else ('yes' if 'isInRcpAvg' in r['cls'] else 'no'),
                 excluded_pollster='yes' if EXCL.search(r['pollster']) else 'no',
                 spread=c[iSp], date_raw=c[iD], sample_raw=c[iS],
                 notes='; '.join(z for z in [pnote, dnote] if z))
        out.append(x)
    return out, race, ''

def rows_from_json(year, state, rid, polls, src_url, arch, data_source, race):
    out = []
    for p in polls:
        t = p.get('type')
        if t not in ('rcp_average', 'poll', 'poll_rcp_avg'):
            continue
        is_avg = t == 'rcp_average'
        cands = [(c['name'], AFF.get(c.get('affiliation'), '?'), c['value']) for c in p['candidate']]
        dem, rep, ind, pnote = pick(cands)
        start, end, dnote = iso_dates(p['date'], None if is_avg else p.get('data_end_date'), year)
        pop, n = sample(p.get('sampleSize'))
        sp = p.get('spread') or {}
        spv = sp.get('value', '')
        spread = 'Tie' if spv in ('', '0', '+0', '+0.0') else f"{sp.get('name','')} {spv}"
        x = row_common(year, state, race, rid, src_url, arch, data_source)
        x.update(pollster='RCP Average' if is_avg else p['pollster'], start=start, end=end,
                 population='' if is_avg else pop, n='' if is_avg else n,
                 dem=dem[2] if dem else '', rep=rep[2] if rep else '', ind=ind[2] if ind else '',
                 dem_candidate=f'{dem[0]} ({dem[1]})' if dem else '', rep_candidate=f'{rep[0]} ({rep[1]})' if rep else '',
                 in_average='no' if is_avg else ('yes' if t == 'poll_rcp_avg' else 'no'),
                 excluded_pollster='yes' if (EXCL.search(p['pollster']) or EXCL.search(p.get('pollster_group_name') or '')) else 'no',
                 spread=spread, date_raw=p['date'], sample_raw=p.get('sampleSize', ''),
                 notes='; '.join(z for z in [pnote, dnote] if z))
        out.append(x)
    return out

def from_wayback24(year, state, rid, ts, url, path, feed):
    h = open(path, encoding='utf-8', errors='replace').read()
    L = poll_lists(h)
    if not L:
        return None, '', 'no poll list in page'
    big = max(L, key=len)
    t = re.search(r'<title>(.*?)</title>', h, re.S)
    race = re.sub(r'\s*\|\s*RealClearPolling$', '', H.unescape(t.group(1)).strip()) if t else ''
    if not any(p.get('type') == 'rcp_average' for p in big):
        return None, race, 'page shows no RCP Average row'
    from parse24 import next_payload
    hide = set(re.findall(r'"hideRcpAverageRow":(true|false)', next_payload(h)))
    if 'true' in hide:
        return None, race, 'page sets hideRcpAverageRow=true (no RCP Average displayed)'
    # sanity: all lists agree on the average
    avgs = {json.dumps(p['candidate'], sort_keys=True) for l in L for p in l if p.get('type') == 'rcp_average'}
    note = '' if len(avgs) == 1 else 'WARNING: page poll lists disagree on RCP average'
    arch = f'https://web.archive.org/web/{ts}/{url}'
    out = rows_from_json(year, state, rid, big, url, arch, 'wayback_page', race)
    if note:
        for x in out: x['notes'] = (x['notes'] + '; ' if x['notes'] else '') + note
    return out, race, ''

def from_feed(year, state, rid, feed):
    m = feed['moduleInfo']
    P = feed.get('poll') or []
    avg = [p for p in P if p['type'] == 'rcp_average']
    if m.get('show_rcp_avg') != 1 and str(m.get('show_rcp_avg')) != '1':
        return None, m['title'], 'feed: show_rcp_avg=0 (no average displayed)'
    if not avg or avg[0]['date'].startswith('12/31'):
        return None, m['title'], 'feed: no dated RCP average'
    out = rows_from_json(year, state, rid, P, FEED_URL.format(rid), '', 'rcp_feed_current_2026-10-26', m['title'])
    for x in out:
        x['notes'] = (x['notes'] + '; ' if x['notes'] else '') + 'from current RCP feed (no archive copy inside the election-eve window)'
    return out, m['title'], ''

def write(path, rows):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in COLS})

if __name__ == '__main__':
    races = json.load(open(sys.argv[2]))  # list of dicts: year,state,tag,rid,kind(22|24),sub,out
    caps = {}
    results = {}
    log = []
    for r in races:
        sub = r['sub']
        caps.setdefault(sub, captures(sub))
        cap = caps[sub].get(r['tag'])
        feed = load_feed(r['rid']) if r.get('rid') else None
        rows, race, why = None, '', ''
        if cap:
            ts, url, path = cap
            fn = from_wayback22 if r['kind'] == '22' else from_wayback24
            rows, race, why = fn(r['year'], r['state'], r.get('rid', ''), ts, url, path, feed)
            src = f'wayback {ts}'
            win = WINDOW_START[r['year']]
            fa = [p for p in (feed or {}).get('poll') or [] if p['type'] == 'rcp_average' and not p['date'].startswith('12/31')]
            fshow = feed and str(feed['moduleInfo'].get('show_rcp_avg')) == '1'
            if feed and fa and fshow:
                fav = {c['affiliation'][0]: c['value'] for c in fa[0]['candidate']}
                wa = [x for x in rows if x['pollster'] == 'RCP Average'] if rows else []
                same = bool(wa) and wa[0]['date_raw'] == fa[0]['date'] and wa[0]['rep'] == fav.get('R')
                if not same:
                    wdesc = (f"{wa[0]['date_raw']} {wa[0]['spread']}" if wa else 'no RCP Average row')
                    if ts < win:
                        frows, race2, why2 = from_feed(r['year'], r['state'], r['rid'], feed)
                        if frows:
                            for x in frows:
                                x['archive_url'] = ''
                                x['notes'] = x['notes'] + f'; latest archive capture is pre-window ({ts}) and shows {wdesc}'
                            rows, race, why, src = frows, race2, '', f'feed (archive {ts} pre-window)'
                    else:
                        for x in rows or []:
                            x['notes'] = (x['notes'] + '; ' if x['notes'] else '') + f"current RCP feed shows a different average ({fa[0]['date']} {fav})"
                        why = (why + '; ' if why else '') + 'feed differs from archive'
            if rows and rows[0]['data_source'] == 'wayback_page' and ts > WINDOW_END[r['year']]:
                for x in rows:
                    x['notes'] = (x['notes'] + '; ' if x['notes'] else '') + f'only capture near election is from the morning after ({ts} UTC, no results row yet)'
                why = (why + '; ' if why else '') + 'morning-after capture'
            if rows and rows[0]['data_source'] == 'wayback_page' and ts < win:
                for x in rows:
                    x['notes'] = (x['notes'] + '; ' if x['notes'] else '') + f'latest archive capture ({ts}) predates the election-eve window'
                why = (why + '; ' if why else '') + 'capture predates window'
        elif feed:
            rows, race, why = from_feed(r['year'], r['state'], r['rid'], feed)
            src = 'feed'
        else:
            src = 'none'; why = 'no archive capture and no feed'
        if rows and r.get('exclude'):
            why = (why + '; ' if why else '') + 'EXCLUDED from CSV: ' + r['exclude']
        elif rows:
            results.setdefault(r['out'], []).extend(rows)
        na = sum(1 for x in rows if x['in_average'] == 'yes') if rows else 0
        avg = [x for x in rows if x['pollster'] == 'RCP Average'] if rows else []
        a = avg[0] if avg else {}
        log.append('\t'.join(map(str, [r['year'], r['state'], r['tag'], src, race, len(rows) - 1 if rows else 0, na,
                                         a.get('start', ''), a.get('end', ''), a.get('dem', ''), a.get('rep', ''), a.get('ind', ''), a.get('spread', ''), why])))
    for out, rows in results.items():
        write(os.path.join(BASE, out), rows)
    print('\t'.join(['year','state','tag','source','race','polls_listed','polls_in_avg','avg_start','avg_end','dem','rep','ind','spread','status']))
    print('\n'.join(log))
