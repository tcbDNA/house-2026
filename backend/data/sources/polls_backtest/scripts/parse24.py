import re, sys, json
def next_payload(html):
    out = []
    for m in re.finditer(r'self\.__next_f\.push\(\[1,(".*?")\]\)</script>', html, re.S):
        try:
            out.append(json.loads(m.group(1)))
        except Exception as e:
            pass
    return ''.join(out)
def poll_lists(html):
    p = next_payload(html)
    dec = json.JSONDecoder()
    res = []
    for m in re.finditer(r'"polls":\[', p):
        arr, _ = dec.raw_decode(p, m.end() - 1)
        res.append(arr)
    return res
if __name__ == '__main__':
    h = open(sys.argv[1], encoding='utf-8').read()
    L = poll_lists(h)
    for arr in L:
        print(len(arr), [x.get('type') for x in arr][:3], sum(1 for x in arr if x.get('type') == 'poll_rcp_avg'))
    big = max(L, key=len)
    for x in big[:12]:
        print(x['type'], x['pollster'], x['date'], x.get('sampleSize'), [(c['name'], c['affiliation'], c['value']) for c in x['candidate']], x['spread']['value'], x.get('data_start_date'), x.get('data_end_date'))
