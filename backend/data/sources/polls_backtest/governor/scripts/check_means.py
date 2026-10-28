"""Check that the simple mean of the in_average == yes polls reproduces RCP's printed average.
For each race: mean of dem / rep / third over the averaged polls (polls with a blank or '--' value for a
candidate are skipped for that candidate), compared with the RCP Average row. A value matches when
|mean - printed| <= 0.05 (so either round-half convention is accepted). The spread is checked the same way
(leader's mean minus runner-up's mean vs. RCP's printed spread).
usage: python3 -I check_means.py <csv> [<csv> ...]"""
import csv, re, sys
from collections import OrderedDict
from fractions import Fraction


def num(v):
    v = (v or '').strip()
    return Fraction(v) if re.match(r'^-?\d+(\.\d+)?$', v) else None


def fmt(f):
    return f'{float(f):.3f}' if f is not None else '-'


bad = 0
for fn in sys.argv[1:]:
    races = OrderedDict()
    for r in csv.DictReader(open(fn)):
        races.setdefault((r['year'], r['state'], r['race_id']), []).append(r)
    for (y, st, rid), rows in races.items():
        avg = [r for r in rows if r['pollster'] == 'RCP Average'][0]
        inav = [r for r in rows if r['in_average'] == 'yes']
        cols = ['dem', 'rep'] + (['third'] if avg.get('third') else [])
        res, ok = [], True
        means = {}
        for c in cols:
            vals = [num(r.get(c)) for r in inav]
            vals = [v for v in vals if v is not None]
            m = sum(vals) / len(vals) if vals else None
            means[c] = m
            p = num(avg.get(c))
            good = m is not None and p is not None and abs(m - p) <= Fraction(1, 20)
            ok &= good
            res.append(f'{c}: mean {fmt(m)} (n={len(vals)}) vs RCP {avg.get(c)} {"ok" if good else "MISMATCH"}')
        # spread
        sp = avg['spread'].strip()
        spm = re.match(r'^(.*?)\s*\+\s*(\d+(\.\d+)?)$', sp)
        if spm or sp.lower() == 'tie':
            names = {c: re.sub(r'\s*\(.*$', '', avg.get(c + '_candidate') or ('Democrats' if c == 'dem' else 'Republicans' if c == 'rep' else '')) for c in cols}
            ordered = sorted([c for c in cols if means[c] is not None], key=lambda c: -means[c])
            if len(ordered) >= 2:
                lead = means[ordered[0]] - means[ordered[1]]
                # RCP's spread is the difference of its rounded averages; also accept the unrounded lead +/-0.05
                plead = abs(num(avg.get(ordered[0])) - num(avg.get(ordered[1])))
                if sp.lower() == 'tie':
                    sgood = abs(lead) <= Fraction(1, 20) or plead == 0
                else:
                    who = spm.group(1).strip()
                    v = Fraction(spm.group(2))
                    sgood = (v == plead or abs(lead - v) <= Fraction(1, 20)) and (who == names[ordered[0]] or abs(lead) <= Fraction(1, 20))
                ok &= sgood
                res.append(f'spread: printed-average lead {names[ordered[0]]} +{fmt(plead)} (unrounded {fmt(lead)}) vs RCP "{sp}" {"ok" if sgood else "MISMATCH"}')
        else:
            res.append(f'spread: unparsed "{sp}"')
        bad += not ok
        print(y, st, rid, 'OK' if ok else 'MISMATCH', f'polls_in_avg={len(inav)}', '| ' + ' | '.join(res), sep='\t')
print(f'# {bad} race(s) did not reproduce', file=sys.stderr)
