"""Ranked-choice (instant runoff) tabulation of an Alaska Division of Elections Cast Vote Record export (Dominion JSON),
following the rules on the Division's results page (https://www.elections.alaska.gov/election-results/, "Sample RCV
Report & Definitions"):
  - one candidate eliminated per round (the fewest votes); tabulation continues until two candidates remain, unless a
    candidate has a majority in round 1; ties for last are reported, not broken (Alaska resolves them by lot)
  - unresolved write-ins are excluded: a ranking of a write-in is passed over, but is not a skipped ranking
  - an overvote (two candidates at one rank) makes the ballot inactive when it is reached
  - two or more skipped rankings in a row make the ballot inactive
  - a candidate ranked more than once counts at the highest ranking and the others are disregarded (6 AAC 25.072,
    https://www.akleg.gov/basis/aac.asp#6.25.072); a disregarded ranking is blank, but a rank naming two candidates
    stays an overvote
  - Blanks: ballots inactive in round 1 other than overvotes (no rankings, the first two skipped, or write-ins only)
Uses each ballot's current version (adjudicated if modified) and only marks the scanner counted as votes (IsVote); a
contest with no votes and an undervote count of 0 is not counted in that contest. These rules reproduce the Division's
official 2024 RCV reports from its 2024 CVR (see validate_2024.txt).
usage: python3 -I ak_rcv.py <cvr dir> <out.json> [--all-rounds] [contest name ...]   (default: every candidacy contest)
--all-rounds keeps eliminating after a round-1 majority, for information (the law stops there)"""
import collections, glob, json, os, sys

D, OUT = sys.argv[1], sys.argv[2]
ALL = "--all-rounds" in sys.argv
WANT = [a for a in sys.argv[3:] if a != "--all-rounds"]
man = lambda n: json.load(open(f"{D}/{n}Manifest.json"))["List"]
contests = {c["Id"]: c for c in man("Contest") if c["Type"] == "Candidacy" and (not WANT or c["Description"] in WANT)}
cands = {c["Id"]: c for c in man("Candidate")}
groups = {g["Id"]: g["Description"] for g in man("CountingGroup")}


def sessions(path):
    """yield each ballot session of a CvrExport file without loading the whole array as objects"""
    dec = json.JSONDecoder()
    with open(path, encoding="utf-8") as f:
        t = f.read()
    i = t.index('"Sessions":[') + len('"Sessions":[')
    while True:
        while t[i] in " \r\n\t,": i += 1
        if t[i] == "]": return
        obj, i = dec.raw_decode(t, i)
        yield obj


def current(s):
    m = s.get("Modified")
    return m if m and m.get("IsCurrent") else s["Original"]


# ballot patterns per contest: tuple over ranks 1..N of the sorted candidate ids voted at that rank
pat = {cid: collections.Counter() for cid in contests}
by_group = {cid: collections.Counter() for cid in contests}
not_counted = collections.Counter()
n_sessions = 0
files = sorted(glob.glob(f"{D}/CvrExport*.json"))
for f in files:
    for s in sessions(f):
        n_sessions += 1
        for card in current(s)["Cards"]:
            for c in card["Contests"]:
                if c["Id"] not in pat: continue
                ranks = [[] for _ in range(contests[c["Id"]]["NumOfRanks"])]
                for m in c["Marks"]:
                    if m["IsVote"]: ranks[m["Rank"] - 1].append(m["CandidateId"])
                if not any(ranks) and c["Undervotes"] == 0:
                    not_counted[c["Id"]] += 1
                    continue
                seen, key = set(), []
                for r in ranks:
                    key.append(() if len(r) == 1 and r[0] in seen else tuple(sorted(r)))
                    seen |= set(r)
                key = tuple(key)
                pat[c["Id"]][key] += 1
                by_group[c["Id"]][groups.get(s.get("CountingGroupId"), "?")] += 1


def state(key, active):
    """where a ballot sits given the continuing candidates: a candidate id, or 'overvote' / 'exhausted'"""
    skips = 0
    for r in key:
        if not r:
            skips += 1
            if skips >= 2: return "exhausted"
            continue
        if len(r) > 1: return "overvote"
        if r[0] in active: return r[0]
        skips = 0  # a ranking of an eliminated candidate or an unresolved write-in is not a skip
    return "exhausted"


def tabulate(cid):
    P = pat[cid]
    regular = [k for k, c in cands.items() if c["ContestId"] == cid and c["Type"] != "WriteIn"]
    writein = {k for k, c in cands.items() if c["ContestId"] == cid and c["Type"] == "WriteIn"}
    name = lambda k: cands[k]["Description"] if isinstance(k, int) else k
    total = sum(P.values())
    # first choices with write-ins included, overvotes apart
    first = collections.Counter()
    for k, v in P.items(): first[name(state(k, set(regular) | writein))] += v
    active = set(regular)
    where = {k: state(k, active) for k in P}
    blanks = {k for k, s in where.items() if s == "exhausted"}
    nb = sum(P[k] for k in blanks)
    for k in blanks: where[k] = None
    rounds, out_note = [], None
    while True:
        tally = collections.Counter({c: 0 for c in active})
        inactive = collections.Counter()
        for k, s in where.items():
            if s is None: continue
            if isinstance(s, int): tally[s] += P[k]
            else: inactive[s] += P[k]
        cont = sum(tally.values())
        r = {"round": len(rounds) + 1, "votes": {name(c): tally[c] for c in sorted(tally, key=lambda c: -tally[c])},
             "continuing": cont, "blanks": nb, "exhausted": inactive["exhausted"], "overvotes": inactive["overvote"]}
        rounds.append(r)
        top = max(tally.values()) if tally else 0
        if len(active) <= 2 or (not ALL and len(rounds) == 1 and 2 * top > cont): break
        low = min(tally.values())
        last = [c for c in active if tally[c] == low]
        if len(last) > 1:
            out_note = f"tie for last in round {r['round']}: {', '.join(name(c) for c in last)} (Alaska breaks ties by lot); stopped"
            break
        e = last[0]
        active.discard(e)
        moved = collections.Counter()
        for k, s in where.items():
            if s == e:
                ns = state(k, active)
                where[k] = ns
                moved[name(ns)] += P[k]
        r["eliminated"] = name(e)
        r["transfers"] = dict(moved.most_common())
    win = max(rounds[-1]["votes"], key=rounds[-1]["votes"].get)
    return {"contest": contests[cid]["Description"], "ballots": total, "not_counted_no_votes_no_undervote": not_counted[cid], "by_counting_group": dict(by_group[cid]),
            "first_choices_incl_writeins": dict(first.most_common()), "rounds": rounds, "leader_final_round": win, "note": out_note}


res = {"cvr_dir": os.path.abspath(D), "all_rounds": ALL, "files": len(files), "sessions": n_sessions,
       "contests": [tabulate(cid) for cid in sorted(contests, key=lambda c: (contests[c]["DistrictId"] != 67 and c != 5, c))]}
json.dump(res, open(OUT, "w"), indent=1)
print(f"{n_sessions:,} ballot sessions in {len(files)} file(s)")
for c in res["contests"]:
    if WANT or c["contest"] in ("U.S. Senator", "U.S. Representative", "Governor / Lieutenant Governor"):
        print(f"\n== {c['contest']}: {c['ballots']:,} ballots with the contest")
        for r in c["rounds"]:
            tot = r["continuing"]
            print(f" Round {r['round']}: " + "; ".join(f"{k} {v:,} ({100 * v / tot:.2f}%)" for k, v in r["votes"].items())
                  + f" | continuing {tot:,}, blanks {r['blanks']:,}, exhausted {r['exhausted']:,}, overvotes {r['overvotes']:,}")
            if "eliminated" in r:
                print(f"   {r['eliminated']} eliminated -> " + ", ".join(f"{k} {v:,}" for k, v in r["transfers"].items()))
        if c["note"]: print(" NOTE:", c["note"])
