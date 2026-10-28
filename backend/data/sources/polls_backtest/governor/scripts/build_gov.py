"""Build tidy CSVs of RCP's final governor averages (2018, 2022) and the 2018 generic-ballot average,
with every poll RCP listed, from archived RCP pages (Wayback, raw `id_` copies) and RCP's feeds.
Adapted from ../../scripts/build.py (the Senate/generic-ballot backtest); same columns, plus
`third_candidate` / `third` for races whose RCP table has a third candidate column.
usage: python3 -I build_gov.py <polls_backtest/governor dir> <races.json>  > build_log.tsv"""
import csv, json, os, re, sys
from datetime import timezone
from email.utils import parsedate_to_datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_epolls import parse as parse_epolls

BASE = sys.argv[1]
FEEDS = os.path.join(BASE, 'rcp_feeds')
FEED_DATE = '2026-10-28'
FEED_URL = 'https://orig.realclearpolitics.com/poll/race/{}/polling_data.json'
COLS = ['year', 'state', 'pollster', 'start', 'end', 'population', 'n', 'dem', 'rep', 'in_average',
        'excluded_pollster', 'source_url', 'archive_url',
        'race', 'race_id', 'dem_candidate', 'rep_candidate', 'spread', 'date_raw', 'sample_raw',
        'data_source', 'notes', 'third_candidate', 'third']
# capture must be before 08:00 UTC the day after the election; "election-eve window" starts 2 days before
WINDOW_END = {2018: '20181107080000', 2022: '20221109080000'}
WINDOW_START = {2018: '20181104000000', 2022: '20221106000000'}
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
    p = os.path.join(FEEDS, f'race_{rid}_polling_data_{FEED_DATE}.json')
    return json.load(open(p)) if os.path.exists(p) else None


def feed_dates(feed):
    out = {}
    if feed:
        for p in feed.get('poll') or []:
            out[str(p['id'])] = (p.get('data_start_date'), p.get('data_end_date'))
    return out


def iso_dates(date_raw, yr_end_hint, elec_year):
    """date_raw like '11/5 - 11/7'. Year from the feed's data_end_date when available, else election year."""
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
    m = re.search(r'\((D|R|I|L|G|DFL|C|WF|Ind|NPA)\)', label)
    return m.group(1) if m else ''


def pick(cands):
    """cands: list of (name, partycode, value) in RCP column order.
    Returns dem, rep, third, extra_note. dem = first D column (else first non-R column, noted);
    rep = first R column; third = first remaining column; any further columns are listed in the note."""
    D = [c for c in cands if c[1] in ('D', 'DFL')]
    R = [c for c in cands if c[1] == 'R']
    note = ''
    rep = R[0] if R else None
    if D:
        dem = D[0]
    else:
        nonR = [c for c in cands if c is not rep]
        dem = nonR[0] if nonR else None
        if dem:
            note = f'no Democrat in RCP table; dem column = {dem[0]} ({dem[1]})'
    rest = [c for c in cands if c is not dem and c is not rep]
    third = rest[0] if rest else None
    if len(rest) > 1:
        note = (note + '; ' if note else '') + 'further RCP columns: ' + ', '.join(f'{c[0]} ({c[1]}) {c[2]}' for c in rest[1:])
    return dem, rep, third, note


def row_common(year, state, race, rid, src_url, arch_url, data_source):
    return dict(year=year, state=state.upper(), race=race, race_id=rid, source_url=src_url,
                archive_url=arch_url, data_source=data_source)


def from_wayback(year, state, rid, ts, url, path, feed):
    title, hdr, rows, _ = parse_epolls(open(path, encoding='utf-8', errors='replace').read())
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
    if not any('rcpAvg' in r['cls'] for r in rows):
        return None, race, 'page shows no RCP Average row'
    for r in rows:
        c = r['cells']
        if len(c) != len(hdr):
            continue
        is_avg = 'rcpAvg' in r['cls']
        if not is_avg and not r['data_id']:
            continue
        cands = [(re.sub(r'\s*\(.*$', '', hdr[i]).strip(), party(hdr[i]), c[i]) for i in ci]
        dem, rep, third, pnote = pick(cands)
        start, end, dnote = iso_dates(c[iD], fd.get(r['data_id'], (None, None))[1], year)
        pop, n = sample(c[iS])
        x = row_common(year, state, race, rid, url, arch, 'wayback_page')
        x.update(pollster='RCP Average' if is_avg else r['pollster'], start=start, end=end,
                 population='' if is_avg else pop, n='' if is_avg else n,
                 dem=dem[2] if dem else '', rep=rep[2] if rep else '',
                 third=third[2] if third else '',
                 dem_candidate=f'{dem[0]} ({dem[1]})' if dem else '',
                 rep_candidate=f'{rep[0]} ({rep[1]})' if rep else '',
                 third_candidate=f'{third[0]} ({third[1]})' if third else '',
                 in_average='no' if is_avg else ('yes' if 'isInRcpAvg' in r['cls'] else 'no'),
                 excluded_pollster='yes' if EXCL.search(r['pollster']) else 'no',
                 spread=c[iSp], date_raw=c[iD], sample_raw=c[iS],
                 notes='; '.join(z for z in [pnote, dnote] if z))
        out.append(x)
    return out, race, ''


AFF = {'Democrat': 'D', 'Republican': 'R', 'Independent': 'I', 'Libertarian': 'L', 'Green': 'G'}


def rows_from_json(year, state, rid, polls, src_url, arch, data_source, race):
    """Feed entries with data_show != 1 are skipped: RCP does not display them (checked against every archived
    page here: none of the data_show 0/2 entries appears on a page) and they include '*PLACEHOLDER*' rows."""
    out, hidden = [], []
    for p in polls:
        t = p.get('type')
        if t not in ('rcp_average', 'poll', 'poll_rcp_avg'):
            continue
        if t != 'rcp_average' and str(p.get('data_show', '1')) != '1':
            hidden.append(f"{p['pollster']} {p['date']} (data_show={p.get('data_show')}{', flagged in average' if t == 'poll_rcp_avg' else ''})")
            continue
        is_avg = t == 'rcp_average'
        cands = [(c['name'], AFF.get(c.get('affiliation'), '?'), c['value']) for c in p['candidate']]
        dem, rep, third, pnote = pick(cands)
        start, end, dnote = iso_dates(p['date'], None if is_avg else p.get('data_end_date'), year)
        pop, n = sample(p.get('sampleSize'))
        sp = p.get('spread') or {}
        spv = sp.get('value', '')
        spread = 'Tie' if spv in ('', '0', '+0', '+0.0') else f"{sp.get('name', '')} {spv}"
        x = row_common(year, state, race, rid, src_url, arch, data_source)
        x.update(pollster='RCP Average' if is_avg else p['pollster'], start=start, end=end,
                 population='' if is_avg else pop, n='' if is_avg else n,
                 dem=dem[2] if dem else '', rep=rep[2] if rep else '', third=third[2] if third else '',
                 dem_candidate=f'{dem[0]} ({dem[1]})' if dem else '',
                 rep_candidate=f'{rep[0]} ({rep[1]})' if rep else '',
                 third_candidate=f'{third[0]} ({third[1]})' if third else '',
                 in_average='no' if is_avg else ('yes' if t == 'poll_rcp_avg' else 'no'),
                 excluded_pollster='yes' if (EXCL.search(p['pollster']) or EXCL.search(p.get('pollster_group_name') or '')) else 'no',
                 spread=spread, date_raw=p['date'], sample_raw=p.get('sampleSize', ''),
                 notes='; '.join(z for z in [pnote, dnote] if z))
        out.append(x)
    if hidden:
        for x in out:
            if x['pollster'] == 'RCP Average':
                x['notes'] = (x['notes'] + '; ' if x['notes'] else '') + 'feed entries not displayed by RCP were left out: ' + '; '.join(hidden)
    return out


def from_feed(year, state, rid, feed, why='no archive copy inside the election-eve window'):
    m = feed['moduleInfo']
    P = feed.get('poll') or []
    avg = [p for p in P if p['type'] == 'rcp_average']
    if str(m.get('show_rcp_avg')) != '1':
        return None, m['title'], 'feed: show_rcp_avg=0 (no average displayed)'
    if not avg or avg[0]['date'].startswith('12/31'):
        return None, m['title'], 'feed: no dated RCP average'
    out = rows_from_json(year, state, rid, P, FEED_URL.format(rid), '', f'rcp_feed_current_{FEED_DATE}', m['title'])
    for x in out:
        x['notes'] = (x['notes'] + '; ' if x['notes'] else '') + f'from current RCP feed ({why})'
    return out, m['title'], ''


def write(path, rows, cols):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in cols})


def edited_after(feed, ts, cutoff):
    """Poll entries in the feed whose RCP `updated` stamp falls after the capture and before the cutoff
    (both UTC, YYYYMMDDhhmmss). Evidence that RCP changed the race after the archived copy was taken."""
    out = []
    for p in (feed or {}).get('poll') or []:
        u = p.get('updated')
        if not u:
            continue
        try:
            t = parsedate_to_datetime(u).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')
        except Exception:
            continue
        if ts < t < cutoff:
            out.append(f"{p['pollster']} {p['date']} ({'in average' if p['type'] == 'poll_rcp_avg' else 'not in average'}) updated {u}")
    return out


def addnote(rows, s):
    for x in rows or []:
        x['notes'] = (x['notes'] + '; ' if x['notes'] else '') + s


if __name__ == '__main__':
    races = json.load(open(sys.argv[2]))  # list of dicts: year,state,tag,rid,sub,out[,exclude][,note]
    caps, results, log = {}, {}, []
    for r in races:
        sub = r['sub']
        caps.setdefault(sub, captures(sub))
        cap = caps[sub].get(r['tag'])
        feed = load_feed(r['rid']) if r.get('rid') else None
        rows, race, why, src = None, '', '', 'none'
        if cap:
            ts, url, path = cap
            rows, race, why = from_wayback(r['year'], r['state'], r.get('rid', ''), ts, url, path, feed)
            src = f'wayback {ts}'
            win = WINDOW_START[r['year']]
            fa = [p for p in (feed or {}).get('poll') or [] if p['type'] == 'rcp_average' and not p['date'].startswith('12/31')]
            fshow = feed and str(feed['moduleInfo'].get('show_rcp_avg')) == '1'
            if feed and fa and fshow:
                fav = {c['affiliation'][0]: c['value'] for c in fa[0]['candidate']}
                wa = [x for x in rows if x['pollster'] == 'RCP Average'] if rows else []
                same = bool(wa) and wa[0]['date_raw'] == fa[0]['date'] and wa[0]['rep'] == fav.get('R')
                if not same:
                    wdesc = (f"{wa[0]['date_raw']} D {wa[0]['dem']} / R {wa[0]['rep']} ({wa[0]['spread']})" if wa else 'no RCP Average row')
                    ev = edited_after(feed, ts, WINDOW_END[r['year']])
                    if ts < win or ev:
                        frows, race2, why2 = from_feed(r['year'], r['state'], r['rid'], feed,
                                                       'no archive copy inside the election-eve window' if ts < win else
                                                       'the last archive copy before the cutoff predates RCP\'s final pre-election update')
                        if frows:
                            for x in frows:
                                x['archive_url'] = ''
                            if ts < win:
                                addnote(frows, f'latest archive capture is pre-window ({ts}) and shows {wdesc}')
                                rows, race, why, src = frows, race2, '', f'feed (archive {ts} pre-window)'
                            else:
                                addnote(frows, f'last archive capture before the cutoff ({ts} UTC) shows an earlier average, {wdesc}; '
                                                f'RCP edited poll entries after that capture and before the cutoff: {"; ".join(ev)}')
                                rows, race, why, src = frows, race2, 'archive superseded by later pre-election RCP edits', f'feed (archive {ts} superseded)'
                    else:
                        addnote(rows, f"current RCP feed shows a different average ({fa[0]['date']} {fav}); no RCP poll entry is stamped between the capture and the cutoff, so the archived page is kept")
                        why = (why + '; ' if why else '') + f"feed differs from archive (feed {fa[0]['date']} {fav})"
            elif feed and fa and rows:
                fav = {c['affiliation'][0]: c['value'] for c in fa[0]['candidate']}
                wa = [x for x in rows if x['pollster'] == 'RCP Average']
                if wa and wa[0]['dem'] == fav.get('D') and wa[0]['rep'] == fav.get('R'):
                    addnote(rows, f"current RCP feed hides this average (show_rcp_avg=0, date {fa[0]['date']}) but keeps the same values")
                elif wa:
                    addnote(rows, f"current RCP feed hides its average (show_rcp_avg=0, date {fa[0]['date']}) and has different values {fav}")
            if rows and rows[0]['data_source'] == 'wayback_page' and ts > WINDOW_END[r['year']]:
                addnote(rows, f'only capture near election is from the morning after ({ts} UTC, no results row yet)')
                why = (why + '; ' if why else '') + 'morning-after capture'
            if rows and rows[0]['data_source'] == 'wayback_page' and ts < win:
                addnote(rows, f'latest archive capture ({ts}) predates the election-eve window')
                why = (why + '; ' if why else '') + 'capture predates window'
        elif feed:
            rows, race, why = from_feed(r['year'], r['state'], r['rid'], feed)
            src = 'feed'
        else:
            why = 'no archive capture and no feed'
        if rows and r.get('note'):
            addnote(rows, r['note'])
        if rows and r.get('exclude'):
            why = (why + '; ' if why else '') + 'EXCLUDED from CSV: ' + r['exclude']
        elif rows:
            results.setdefault(r['out'], []).extend(rows)
        na = sum(1 for x in rows if x['in_average'] == 'yes') if rows else 0
        avg = [x for x in rows if x['pollster'] == 'RCP Average'] if rows else []
        a = avg[0] if avg else {}
        log.append('\t'.join(map(str, [r['year'], r['state'], r['tag'], src, race, len(rows) - 1 if rows else 0, na,
                                       a.get('start', ''), a.get('end', ''), a.get('dem', ''), a.get('rep', ''),
                                       a.get('third_candidate', ''), a.get('third', ''), a.get('spread', ''), why])))
    for out, rows in results.items():
        cols = COLS if 'governor' in out else COLS[:-2]
        write(os.path.join(BASE, out), rows, cols)
    print('\t'.join(['year', 'state', 'tag', 'source', 'race', 'polls_listed', 'polls_in_avg', 'avg_start', 'avg_end',
                     'dem', 'rep', 'third_candidate', 'third', 'spread', 'status']))
    print('\n'.join(log))
