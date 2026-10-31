"""Senate polling averages for the poll blend -> senate_poll_averages.csv.

Rules (user decisions, Oct 2026):
  * Excluded pollsters: Rasmussen Reports and ActiVote (user decision),
    Wedgewood Polls, which admitted on Oct 20, 2026 that its polls were
    fabricated (sources/excluded_pollsters/), McLaughlin & Associates
    (user decision, Oct 30) and Quantus Insights (user decision, Oct 30:
    "R biased pollster").
  * Heritage Action's Cor Strategies poll in Texas is not counted (user
    decision Oct 28; NOT_COUNTED, LEAVE_OUT_NOT_COUNTED = False counts it).
  * Polls with a partisan sponsor are not counted, including any RCP has
    averaged (user decision Oct 28; LEAVE_OUT_PARTISAN_SPONSORS). Sponsors
    that name no party but lean partisan count too (user decision Oct 30;
    PARTISAN_LEANING_SPONSORS, LEAVE_OUT_PARTISAN_LEANING_SPONSORS).
  * Recomputed averages take one poll per pollster; polls sponsored by others
    are the pollster's, but YouGov Blue counts separately from YouGov (user
    decision Oct 28; YOUGOV_BLUE_OWN_POLLSTER).
  * Start from RealClearPolling's average, with Rasmussen Reports removed:
    the remaining polls RCP averaged, re-averaged (ActiVote and Wedgewood are
    never in an RCP average). A poll RCP lists but has not yet averaged can
    be counted ahead of RCP (RCP_PENDING; user decision Oct 27 for Echelon
    Insights' Maine poll; COUNT_RCP_PENDING = False turns it off), and so can
    a poll RCP doesn't list at all (ADDED_TO_RCP; user decision Oct 29 for
    MSU's Michigan survey; COUNT_ADDED_TO_RCP = False turns it off).
  * Optionally (COUNT_RCP_LEFT_OUT; user decision Oct 30 to add the setting),
    every poll RCP leaves out of an average it publishes: the latest poll by
    each pollster not in RCP's averaged set, or a newer poll by one that is,
    if it started on or after the start of RCP's averaging window and passes
    the rules above. Pollsters are matched through FIRM_ALIASES.
  * If a newer poll has come out since RCP last updated the average, or RCP
    publishes no average, recompute it from the most recent poll by each
    pollster whose fieldwork ended in the last three weeks (on or after
    WINDOW_START), excluded pollsters removed: a simple mean, using a
    poll's head-to-head question where it released one (as RCP's two-way
    averages do), else its full ballot.
    "Newer" = fieldwork ended after the latest poll in RCP's average and
    released on or after RCP's last update (lastBuildDate); with no known
    release date, the fieldwork test alone. A poll RCP's feed already lists
    is not newer: RCP has seen it (RCP_LISTED_NOT_NEWER; it counts, if at
    all, as a poll RCP left out).
  * No RCP average and no poll in the window -> no row (the race uses the
    model only).
  * blend_margin = two-party margin, 100 x (anti-R - R) / (anti-R + R); for the
    three-way Montana race the raw margin (Bodnar - Alme).

Inputs, all saved under sources/senate_polls_2026/ (see the READMEs there):
  recent/rcp_*.json, <st>/rcp_polling_data_*.json   RCP feeds
  recent/recent_polls_compiled.json                 polls ending >= Oct 1, 17 races
  votehub_polls_api_C.json, <st>/poliwave_<st>_sen.html   the other races

Usage (from backend/data/): python3 build_senate_poll_averages.py
Writes senate_poll_averages.csv and prints the per-race report
(saved as ../analysis/senate_poll_averages.txt).
"""
from __future__ import annotations

import csv
import html
import json
import re
from datetime import date
from email.utils import parsedate_to_datetime
from pathlib import Path

DATA = Path(__file__).resolve().parent
SRC = DATA / "sources" / "senate_polls_2026"
OUT = DATA / "senate_poll_averages.csv"

# RETRIEVED: date the poll sources were last refreshed (the as-of date of
# recomputed averages). WINDOW_START is fixed at three weeks before the first
# build (Oct 26): user decision, keep the polls already in the averages and add
# new ones as they come out rather than rolling the window forward.
RETRIEVED = date(2026, 10, 31)
WINDOW_START = date(2026, 10, 5)
EXCLUDED_POLLSTERS = ("rasmussen", "activote", "wedgewood", "mclaughlin", "quantus")
# Polls that can't be traced to any release (no source recorded anywhere).
UNVERIFIED = {("SC", "onpointpolitics (unidentified)"):
              "Poliwave only, 'Source: Not recorded'; no release found"}
# Polls left out by user decision, keyed by (state, pollster as compiled).
# LEAVE_OUT_NOT_COUNTED = False counts them like any other poll.
LEAVE_OUT_NOT_COUNTED = True
NOT_COUNTED = {("TX", "Cor Strategies"): "Heritage Action; not counted, user decision Oct 28"}
# Polls with a partisan sponsor (a named sponsor plus a partisan flag: a
# candidate, campaign, party, PAC or partisan group) are not counted, including
# any RCP has averaged (user decision, Oct 28). False: counted like any other poll.
LEAVE_OUT_PARTISAN_SPONSORS = True
# Sponsors with no partisan flag in the compiled records that lean partisan, so
# their polls count as partisan-sponsored too, including any RCP has averaged
# (user decision Oct 30: "if your inclination is that it is sponsored by a
# partisan leaning group, don't add it"). Keyed by sponsor as compiled. False:
# only flagged sponsors.
LEAVE_OUT_PARTISAN_LEANING_SPONSORS = True
PARTISAN_LEANING_SPONSORS = {
    "Texas Public Opinion Research": "directed by Democratic strategist Luke Warford, former chief strategy "
                                     "officer of the Texas Democratic Party (Texas Tribune, Jul 28; TPR, Oct 2024); "
                                     "fielded by Slingshot Strategies, a Democratic firm",
    "A More Affordable Nevada": "\"a group backed by the Democratic Governors Association\" (DGA release, Sep 10, 2026; "
                                "sources/gov_polls_2026/dga_a_more_affordable_nevada_2026-09-10.html); its Hart Research "
                                "poll is in the governor averages only",
}
# Polls VoteHub marks as campaign or party internals (or with a partisan-flagged
# sponsor) count as partisan-sponsored too, even where the compiled record
# names no sponsor (Oct 30: the Idaho VoteNexus poll, commissioned by Knock
# Every Door PAC and the Achilles campaign). False: the compiled sponsor only.
LEAVE_OUT_VOTEHUB_INTERNAL = True
# YouGov Blue counts as its own pollster rather than as YouGov (user decision,
# Oct 28). False: one key for every YouGov poll.
YOUGOV_BLUE_OWN_POLLSTER = True
# Polls RCP lists but has not yet put in its average, counted in the RCP
# average ahead of RCP (user decision, Oct 27: RCP will add it). Keyed by
# (state, pollster and dates as RCP's feed lists them). False: RCP's
# averaged set as published.
COUNT_RCP_PENDING = True
RCP_PENDING = {("ME", "Echelon Insights", "10/16 - 10/23")}
# Polls RCP doesn't list at all, counted in its average anyway (user decisions,
# Oct 29: MSU's Michigan Election Survey, Oct 8-23; A2 Insights' Texas poll,
# Oct 23-27). Keyed by (state, pollster as compiled, fieldwork end). False:
# RCP's averaged set as published.
COUNT_ADDED_TO_RCP = True
ADDED_TO_RCP = {("MI", "Michigan State Univ. (Political Science)/Verasight", date(2026, 10, 23)),
                ("TX", "A2 Insights", date(2026, 10, 27))}
# A poll RCP's feed already lists (same firm, end within 2 days) is not
# "newer than RCP's average", even when its own release gives a later end
# date than RCP's row: RCP has seen it and left it out, so it counts, if at
# all, under COUNT_RCP_LEFT_OUT (Oct 31: Data for Progress's Maine poll, Oct
# 23-27, which RCP lists as 10/23-10/26). False: the date test alone.
RCP_LISTED_NOT_NEWER = True

# Count the polls RCP leaves out of the averages it publishes (setting added on
# the user's request, Oct 30: "don't just rely on RCP -- they sometimes exclude
# pollsters for no reason"). In a race on RCP's average, add the latest poll
# by each pollster that isn't in RCP's averaged set, and replace a pollster's
# averaged poll with its newer one, when the poll started on or after the
# start of RCP's averaging window and passes the rules above (excluded
# pollsters, partisan sponsors, NOT_COUNTED). False: RCP's averaged set as
# published, plus RCP_PENDING and ADDED_TO_RCP.
COUNT_RCP_LEFT_OUT = True
# Left-out polls not counted under COUNT_RCP_LEFT_OUT because the sponsor (or
# the pollster itself) leans partisan or the client is likely partisan (user
# decision Oct 30: "if your inclination is that it is sponsored by a partisan
# leaning group, don't add it"). Keyed by (state, pollster as compiled, end).
LEFT_OUT_PARTISAN_LEANING = {
    ("SC", "Impact Research", date(2026, 10, 21)): "no client named; the memo was posted by Fresh Start PAC",
    ("SC", "Targoz Market Research", date(2026, 10, 25)): "South Carolina Policy Council, a conservative think tank",
    ("FL", "MDW Communications", date(2026, 10, 10)): "MDW and EDGE Communications, political consultancies",
    ("TX", "Pollfinity", date(2026, 10, 18)): "owned and self-funded by Lars Mapstead, a 2024 Libertarian presidential "
                                              "candidate (user decision Oct 30)",
}
# Pollster identity across RCP's and the compiled polls' names (first match
# wins; a sponsor's name counts too). Anything else: the first word.
FIRM_ALIASES = [
    (r"siena|ny ?times|new york times|\bnyt\b", "siena"), (r"\bcnn\b|ssrs", "cnn"),
    (r"\bfox\b|beacon research/shaw|shaw & co", "fox"), (r"cook political|new river", "cook"),
    (r"tpor|slingshot|texas public opinion", "tpor"), (r"texas southern|\btsu\b", "tsu"),
    (r"univision", "univision"), (r"bowling green|bgsu", "bgsu"),
    (r"michigan st(?:ate|\.)?.*(?:dps|political science)", "msu-polisci"), (r"michigan st(?:ate|\.)?|ippsr", "msu-ippsr"),
    (r"houston|hobby school", "uh"), (r"glengariff|detroit news", "glengariff"), (r"mitchell", "mitchell"),
    (r"\bunh\b|university of new hampshire", "unh"), (r"st\.? anselm|saint anselm", "stanselm"),
    (r"\bppic\b|public policy institute of california", "ppic"),
    (r"berkeley igs|governmental studies|la times|los angeles times", "igs"), (r"citrin|politico", "citrin"),
    (r"surveyusa", "surveyusa"), (r"suffolk", "suffolk"), (r"umass lowell|massachusetts lowell", "umasslowell"),
    (r"amherst|university of massachusetts department", "umassamherst"),
    (r"massinc|\bcwb\b|commonwealth beacon", "massinc"), (r"bravo|pennlive", "bravo"), (r"franklin|f&m", "fandm"),
    (r"great ?blue|ct insider|wfsb|sacred heart", "greatblue"), (r"wesleyan", "wesleyan"),
    (r"highground", "highground"), (r"arizona state|\basu\b|bsp research", "asu"), (r"fabrizio", "fabrizio"),
    (r"embold|pell center", "embold"), (r"emerson", "emerson"), (r"mason-dixon|mason dixon", "masondixon"),
    (r"insider ?advantage", "insideradvantage"), (r"co/efficient|coefficient", "coefficient"),
    (r"public policy polling|\bppp\b", "ppp"), (r"data for progress", "dfp"), (r"alaska survey research", "asr"),
    (r"national public affairs", "npa"), (r"global strategy group", "gsg"), (r"washington post", "wapo"),
    (r"high point|\bhpu\b", "hpu"), (r"east carolina|\becu\b", "ecu"), (r"citadel", "citadel"),
    (r"harper|carolina journal", "harper"), (r"north florida|\bunf\b", "unf"), (r"st\.? pete", "stpete"),
    (r"marquette", "marquette"), (r"league of american workers|\blaw\b|wick", "wick"), (r"votehub", "votehub"),
    (r"quinnipiac", "quinnipiac"), (r"marist", "marist"), (r"echelon", "echelon"), (r"trafalgar", "trafalgar"),
    (r"quantus", "quantus"), (r"cygnal", "cygnal"), (r"\bcbs\b", "cbs"), (r"\belon\b", "elon"),
    (r"morning consult", "morningconsult"), (r"albuquerque journal|research & polling", "rpi"),
    (r"kob-tv|kob\b", "surveyusa"),
]

INDEPENDENT = {"NE", "MT", "ID", "SD"}
THREE_WAY = {"MT"}

# RCP race feeds (two-way, except Montana's four-candidate race). None: RCP
# publishes no average for the race.
RCP_FEEDS = {
    "OH": "recent/rcp_oh_8689.json", "TX": "recent/rcp_tx_8867.json", "AK": "recent/rcp_ak_8754.json",
    "FL": "recent/rcp_fl_8948.json", "IA": "recent/rcp_ia_8930.json", "KS": "recent/rcp_ks_9106.json",
    "ME": "recent/rcp_me_9100.json", "SC": "recent/rcp_sc_9115.json", "MI": "recent/rcp_mi_8802.json",
    "NC": "recent/rcp_nc_8753.json", "NH": "recent/rcp_nh_8845.json", "MN": "recent/rcp_mn_8922.json",
    "GA": "recent/rcp_ga_8718.json", "MT": "recent/rcp_mt_9034.json",
    "AL": "al/rcp_polling_data_9229.json", "MA": "ma/rcp_polling_data_8899.json",
    "NM": "nm/rcp_polling_data_9122.json", "RI": "ri/rcp_polling_data_8954.json",
    "SD": "sd/rcp_polling_data_9232.json",
    "MS": None, "LA": None, "NE": None, "AR": None, "ID": None, "IL": None, "KY": None, "OK": None,
    "TN": None, "CO": None, "DE": None, "NJ": None, "OR": None, "VA": None, "WV": None, "WY": None,
}
# Races not in recent_polls_compiled.json: polls come from VoteHub's dump and
# Poliwave's race page. (anti-R surname, R surname) picks the two candidates.
OTHER_RACES = {
    "AL": ("Alabama", "Wess", "Moore"), "AR": ("Arkansas", "Shoffner", "Cotton"),
    "ID": ("Idaho", "Achilles", "Risch"), "MA": ("Massachusetts", "Markey", "Deaton"),
    "NM": ("New Mexico", "Luj", "Marker"), "RI": ("Rhode Island", "Reed", "McKay"),
    "SD": ("South Dakota", "Bengs", "Rounds"), "IL": ("Illinois", "Stratton", "Tracy"),
    "KY": ("Kentucky", "Booker", "Barr"), "OK": ("Oklahoma", "Thomas", "Mullin"),
    "TN": ("Tennessee", "Bradshaw", "Hagerty"), "CO": ("Colorado", "Hickenlooper", "Baisley"),
    "DE": ("Delaware", "Coons", "Republican"), "NJ": ("New Jersey", "Booker", "Murphy"),
    "OR": ("Oregon", "Merkley", "Republican"), "VA": ("Virginia", "Warner", "Republican"),
    "WV": ("West Virginia", "Democrat", "Capito"), "WY": ("Wyoming", "Democrat", "Lummis"),
}
RACE_NOTES = {
    "NE": "Independent Dan Osborn (no Democratic nominee) vs Pete Ricketts (R). Unlike the other "
          "independent races, it blends the polling average with the model like a two-party race.",
    "MT": "Three-way race: Alme (R) vs Bodnar (I), with Bankhead (D) polling a distant third, plus a "
          "Libertarian. The margin is Bodnar minus Alme from the three-way polls; as an independent "
          "race it rests on polls, the model filling in only with fewer than three.",
}


def d(s: str | None) -> date | None:
    return date.fromisoformat(s[:10]) if s else None


def pollster_key(name: str) -> str:
    """One key per polling firm (sponsored YouGov polls are YouGov's; YouGov
    Blue is its own if YOUGOV_BLUE_OWN_POLLSTER)."""
    n = re.sub(r"\(.*?\)", "", html.unescape(name)).lower().replace("*", "").strip()
    if YOUGOV_BLUE_OWN_POLLSTER and n.startswith("yougov blue"):
        return n
    return "yougov" if "yougov" in n else n


def excluded(name: str) -> bool:
    return any(x in name.lower() for x in EXCLUDED_POLLSTERS)


def partisan_sponsor(p: dict) -> bool:
    leaning = LEAVE_OUT_PARTISAN_LEANING_SPONSORS and p.get("sponsor") in PARTISAN_LEANING_SPONSORS
    return LEAVE_OUT_PARTISAN_SPONSORS and bool(p.get("sponsor") and (p.get("partisan") or leaning))


def same_poll(q: dict, a: dict) -> bool:
    """Compiled poll `q` is RCP row `a`: same end date, and the pollster's or
    sponsor's first word is in RCP's name, or both map to the same firm
    (FIRM_ALIASES: RCP lists Slingshot's TPOR polls as "TPOR")."""
    words = set(re.findall(r"[a-z]+", a["pollster"].lower()))
    first = lambda s: next((w for w in re.findall(r"[a-z]+", (s or "").lower()) if w not in ("a", "an", "the")), None)
    return q["end"] == a["end"] and (first(q["pollster"]) in words or first(q.get("sponsor")) in words
                                     or firm_key(q["pollster"], q.get("sponsor")) == firm_key(a["pollster"]))


def rcp_end(dates: str, year: int = 2026) -> date:
    """RCP's 'm/d - m/d' -> end date."""
    m, dd = dates.split("-")[-1].strip().split("/")
    return date(year, int(m), int(dd))


def rcp_start(dates: str, year: int = 2026) -> date:
    """RCP's 'm/d - m/d' -> start date."""
    m, dd = dates.split("-")[0].strip().split("/")
    return date(year, int(m), int(dd))


def firm_key(name: str, sponsor: str | None = None) -> str:
    """One key per polling operation, matched across RCP's and the compiled names."""
    s = html.unescape(f"{name} {sponsor or ''}").lower().replace("*", "")
    for pat, key in FIRM_ALIASES:
        if re.search(pat, s):
            return key
    # "<partner>/YouGov" is the partner's poll; plain "YouGov" is YouGov's own
    return next((w for w in re.findall(r"[a-z0-9]+", s) if w not in ("a", "an", "the", "yougov")), "yougov")


STATE_NAMES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
               "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
               "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
               "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
               "MN": "Minnesota", "MS": "Mississippi", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
               "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
               "NC": "North Carolina", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
               "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
               "VT": "Vermont", "VA": "Virginia", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}


def votehub_internal(path: Path) -> dict[str, list[tuple[str, date, str]]]:
    """state -> (firm, end, why) for VoteHub rows that are campaign or party
    internals, or carry a sponsor with a partisan flag. COUNT_RCP_LEFT_OUT
    leaves these out even where the compiled poll records no sponsor."""
    names = {v: k for k, v in STATE_NAMES.items()}
    out = {}
    for x in json.loads(path.read_text())["items"]:
        st = names.get((x.get("subject") or "").replace("2026 ", "", 1))
        sponsors = ", ".join((s.get("name") if isinstance(s, dict) else str(s)) for s in (x.get("sponsors") or []))
        why = ("internal" if x.get("internal") else "") or (f"sponsor {sponsors}" if sponsors and x.get("partisan") else "")
        if st and why and x.get("end_date"):
            out.setdefault(st, []).append((firm_key(x["pollster"], sponsors), d(x["end_date"]),
                                           f"VoteHub: {why}, {x.get('partisan') or 'no'} partisan flag"))
    return out


def is_internal(p: dict, internal) -> bool:
    k = firm_key(p["pollster"], p.get("sponsor"))
    return any(k == f and abs((p["end"] - e).days) <= 2 for f, e, _ in internal)


def rcp_left_out(st: str, rcp: dict, kept: list[dict], usable: list[dict], added: set,
                 eligible=lambda p: True, internal=()) -> tuple[list[dict], list[dict]]:
    """COUNT_RCP_LEFT_OUT: (averaged polls to replace, left-out polls to add).
    A compiled poll is RCP's own averaged poll when the firm matches and the end
    dates are within 2 days; it is left out when its firm has no averaged poll,
    or only older ones."""
    by_firm = {}
    for a in kept:
        by_firm.setdefault(firm_key(a["pollster"]), []).append(a)
    best = {}
    for p in usable:
        if p.get("start") is None or p["start"] < rcp["window_start"] or not eligible(p):
            continue
        if (st, p["pollster"], p["end"]) in added:
            continue
        k = firm_key(p["pollster"], p.get("sponsor"))
        if any(k == f and abs((p["end"] - e).days) <= 2 for f, e, _ in internal):
            continue                      # a campaign / party internal per VoteHub
        same = by_firm.get(k, [])
        if any(abs((p["end"] - a["end"]).days) <= 2 for a in same):
            continue                      # RCP averages this poll
        if same and p["end"] <= max(a["end"] for a in same):
            continue                      # older than the firm's averaged poll
        if k not in best or p["end"] > best[k]["end"]:
            best[k] = p
    replace = [a for k in best for a in by_firm.get(k, [])]
    add = [{**p, "dates": f"{p['start']:%-m/%-d} - {p['end']:%-m/%-d}", "pending": False, "label": label(p)}
           for p in sorted(best.values(), key=lambda p: p["end"], reverse=True)]
    return replace, add


def rcp_listed(p: dict, rcp: dict) -> bool:
    """RCP_LISTED_NOT_NEWER: the poll is one of RCP's feed rows (averaged or not)."""
    k = firm_key(p["pollster"], p.get("sponsor"))
    return RCP_LISTED_NOT_NEWER and any(k == f and abs((p["end"] - e).days) <= 2 for f, e in rcp["listed"])


def load_rcp(st: str) -> dict | None:
    rel = RCP_FEEDS.get(st)
    if not rel:
        return None
    feed = json.loads((SRC / rel).read_text())
    mi, rows = feed["moduleInfo"], feed.get("poll") or []
    avg = [p for p in rows if p["type"] == "rcp_average"]
    if not avg:
        return None
    def shares(p):
        r = [float(c["value"]) for c in p["candidate"] if c.get("affiliation") == "Republican"]
        if st == "MT":   # four-way: Bodnar (I) vs Alme (R)
            a = [float(c["value"]) for c in p["candidate"] if c["name"] == "Bodnar"]
        else:
            a = [float(c["value"]) for c in p["candidate"] if c.get("affiliation") != "Republican"]
        return a[0], r[0]
    def pending(p):
        return COUNT_RCP_PENDING and (st, p["pollster"].replace("*", "").strip(), p["date"]) in RCP_PENDING
    averaged = [{"pollster": p["pollster"].replace("*", "").strip(), "dates": p["date"],
                 "end": rcp_end(p["date"]), "anti_r": shares(p)[0], "r": shares(p)[1],
                 "pending": p["type"] != "poll_rcp_avg"}
                for p in rows if p["type"] == "poll_rcp_avg" or (p["type"] == "poll" and pending(p))]
    if not averaged:   # an average row with no polls left in it (e.g. Nevada governor, Oct 30): no RCP average
        return None
    return {"built": parsedate_to_datetime(mi["lastBuildDate"]).date(), "published": shares(avg[0]),
            "window_start": rcp_start(avg[0]["date"]),
            "averaged": averaged, "local_file": f"sources/senate_polls_2026/{rel}",
            "listed": [(firm_key(p["pollster"]), rcp_end(p["date"])) for p in rows if p["type"] in ("poll", "poll_rcp_avg")],
            "url": f"https://www.realclearpolling.com/polls/{mi['poll_contentful_fullpath']}/{mi['poll_contentful_slug']}"}


def compiled_polls() -> dict[str, list[dict]]:
    raw = json.loads((SRC / "recent" / "recent_polls_compiled.json").read_text())
    out = {}
    for st, race in raw.items():
        out[st] = []
        for p in race["polls"]:
            h2h = p.get("h2h_anti_r") is not None and p.get("h2h_r") is not None
            out[st].append({
                "pollster": html.unescape(p["pollster"]), "sponsor": p.get("sponsor"), "partisan": p.get("partisan"),
                "start": d(p.get("start")), "end": d(p["end"]), "released": d(p.get("released")),
                "anti_r": p["h2h_anti_r"] if h2h else p["anti_r"], "r": p["h2h_r"] if h2h else p["r"],
                "question": "head-to-head" if h2h else "full ballot", "source": p.get("source", "")})
    return out


POLIWAVE_ROW = re.compile(
    r'\{date:"[\d-]+",pollster:"(?P<pollster>[^"]+)",pollsterID:\d+,question:"[^"]*",demoFilter:"All",'
    r'regionFilter:"All",options:\{(?P<opts>[^}]*)\},sampleSize:(?:[\d.]+|null),serialID:(?P<sid>\d+),'
    r'pollUrl:(?:"[^"]*"|null),startDate:"(?P<start>[\d-]+)",endDate:"(?P<end>[\d-]+)"')


def other_polls(st: str) -> list[dict]:
    """VoteHub rows, plus Poliwave rows VoteHub lacks (same end date +-1 day
    and same firm or the same numbers within 2 points = the same poll)."""
    name, anti, rep = OTHER_RACES[st]
    out = []
    for p in json.loads((SRC / "votehub_polls_api_C.json").read_text()):
        if p.get("poll_type") != "us-senator" or p.get("subject") != f"2026 {name}":
            continue
        a = [x["pct"] for x in p["answers"] if anti.lower() in x["choice"].lower()]
        r = [x["pct"] for x in p["answers"] if rep.lower() in x["choice"].lower()]
        if a and r:
            out.append({"pollster": p["pollster"], "sponsor": ", ".join(p.get("sponsors") or []) or None,
                        "partisan": p.get("partisan"), "start": d(p.get("start_date")), "end": d(p["end_date"]),
                        "released": d(p["created_at"]),
                        "anti_r": a[0], "r": r[0], "question": "full ballot", "source": "VoteHub"})
    pw = SRC / st.lower() / f"poliwave_{st.lower()}_sen.html"
    seen = set()
    for m in POLIWAVE_ROW.finditer(pw.read_text(encoding="utf-8", errors="replace")) if pw.exists() else []:
        if m["sid"] in seen:
            continue
        seen.add(m["sid"])
        opts = dict(kv.split(":") for kv in m["opts"].split(","))
        a = [float(v) for k, v in opts.items() if anti.upper() in k]
        r = [float(v) for k, v in opts.items() if rep.upper() in k]
        if not (a and r):
            continue
        end = d(m["end"])
        first = re.findall(r"[a-z]+", m["pollster"].lower())[0]
        dup = any(abs((q["end"] - end).days) <= 1 and
                  (re.findall(r"[a-z]+", q["pollster"].lower())[0] == first
                   or (abs(q["anti_r"] - a[0]) <= 2 and abs(q["r"] - r[0]) <= 2)) for q in out)
        if not dup:
            out.append({"pollster": m["pollster"], "sponsor": None, "partisan": None, "start": d(m["start"]),
                        "end": end, "released": None,
                        "anti_r": a[0], "r": r[0], "question": "full ballot", "source": "Poliwave"})
    return out


def label(p: dict) -> str:
    s = p["pollster"]
    if p.get("sponsor"):
        s += f" for {p['sponsor']}"
    if p.get("partisan") and f"({p['partisan']})" not in s:
        s += f" ({p['partisan']}-flagged)"
    return s


def build():
    global INTERNAL
    INTERNAL = (votehub_internal(SRC / "recent" / "votehub_senate_all.json")
                if COUNT_RCP_LEFT_OUT or LEAVE_OUT_VOTEHUB_INTERNAL else {})
    comp = compiled_polls()
    rows, report = [], []
    report.append(f"Senate polling averages, built from sources retrieved {RETRIEVED}; "
                  f"recompute window: polls ending on or after {WINDOW_START}.\n")
    for st in RCP_FEEDS:
        polls = comp[st] if st in comp else other_polls(st)
        left_out = {**UNVERIFIED, **(NOT_COUNTED if LEAVE_OUT_NOT_COUNTED else {})}
        internal = [p for p in polls if LEAVE_OUT_VOTEHUB_INTERNAL and is_internal(p, INTERNAL.get(st, ()))
                    and not partisan_sponsor(p)]
        usable = [p for p in polls if not excluded(p["pollster"]) and (st, p["pollster"]) not in left_out
                  and not partisan_sponsor(p) and p not in internal]
        dropped = [f"{p['pollster']} ({left_out[(st, p['pollster'])]})" for p in polls
                   if (st, p["pollster"]) in left_out]
        sponsored = [p for p in polls if partisan_sponsor(p)] + internal
        dropped += [f"{label(p)}, ending {p['end']} (" + ("campaign/party internal per VoteHub" if p in internal
                                                          else "partisan sponsor") + ")" for p in sponsored
                    if p["end"] >= WINDOW_START and (st, p["pollster"]) not in left_out]
        rcp = load_rcp(st)
        newer = []
        if rcp:
            latest = max(a["end"] for a in rcp["averaged"])
            newer = [p for p in usable if p["end"] > latest
                     and (p["released"] is None or p["released"] >= rcp["built"]) and not rcp_listed(p, rcp)]
        if rcp and not newer:
            ps = [a for a in rcp["averaged"] if any(same_poll(q, a) for q in sponsored)]
            kept = [a for a in rcp["averaged"] if not excluded(a["pollster"]) and a not in ps]
            exc = [a for a in rcp["averaged"] if excluded(a["pollster"])]
            ras = bool(exc)
            exc_note = ("Rasmussen removed" if all("rasmussen" in a["pollster"].lower() for a in exc) else
                        "excluded pollsters removed: " + ", ".join(f"{a['pollster']} {a['dates']}" for a in exc))
            added = [a for a in kept if a["pending"]]
            extra = [{"pollster": p["pollster"], "dates": f"ending {p['end']:%b %-d}", "end": p["end"],
                      "anti_r": p["anti_r"], "r": p["r"], "pending": False}
                     for p in usable if COUNT_ADDED_TO_RCP and (st, p["pollster"], p["end"]) in ADDED_TO_RCP]
            kept = kept + extra
            replaced, left_out = (rcp_left_out(st, rcp, kept, usable, ADDED_TO_RCP if COUNT_ADDED_TO_RCP else set(),
                                               eligible=lambda p: (st, p["pollster"], p["end"]) not in LEFT_OUT_PARTISAN_LEANING,
                                               internal=INTERNAL.get(st, ()))
                                  if COUNT_RCP_LEFT_OUT else ([], []))
            kept = [a for a in kept if a not in replaced] + left_out
            anti = sum(a["anti_r"] for a in kept) / len(kept)
            rep = sum(a["r"] for a in kept) / len(kept)
            if not ras and not added and not ps and not extra and not left_out:   # nothing changed: must reproduce RCP's published average
                assert abs(round(anti, 1) - rcp["published"][0]) < 0.051 and \
                       abs(round(rep, 1) - rcp["published"][1]) < 0.051, (st, anti, rep, rcp["published"])
            used = [f"{a.get('label', a['pollster'])} {a['dates']}" + (" (listed by RCP, counted ahead of RCP)" if a["pending"] else
                                                       " (not listed by RCP, counted by user decision)" if a in extra else
                                                       f" (left out by RCP, counted; {a['question']}, {a['anti_r']:g}/{a['r']:g})" if a in left_out else "")
                    for a in kept]
            plus = "; plus " + ", ".join(f"{a['pollster']} {a['dates']}" for a in added) + \
                " (listed by RCP, not yet averaged)" if added else ""
            minus = ("; partisan-sponsored poll removed: " + ", ".join(f"{a['pollster']} {a['dates']}" for a in ps)
                     if ps else "")
            plus += ("; plus " + ", ".join(f"{a['pollster']} {a['dates']}" for a in extra) +
                     " (not listed by RCP, counted by user decision)" if extra else "")
            if left_out:
                plus += ("; plus polls RCP left out: " + ", ".join(f"{a['label']} {a['dates']}" for a in left_out) +
                         ("; replacing " + ", ".join(f"{a['pollster']} {a['dates']}" for a in replaced) if replaced else ""))
            method = (f"RCP average, {exc_note}" if ras else "RCP average") + minus + plus
            src = "RealClearPolling" + (f", {exc_note}" if ras else "") + minus + plus
            as_of, url, local = rcp["built"].isoformat(), rcp["url"], rcp["local_file"]
            published = round(rcp["published"][0] - rcp["published"][1], 1)
            n = len(kept)
        else:
            window = [p for p in usable if p["end"] >= WINDOW_START]
            latest_by = {}
            for p in sorted(window, key=lambda p: p["end"]):
                latest_by[pollster_key(p["pollster"])] = p
            kept = sorted(latest_by.values(), key=lambda p: p["end"], reverse=True)
            if not kept:
                report.append(f"{st}: no RCP average and no poll ending on/after {WINDOW_START} -> model only")
                continue
            anti = sum(p["anti_r"] for p in kept) / len(kept)
            rep = sum(p["r"] for p in kept) / len(kept)
            used = [f"{label(p)}, ending {p['end']} ({p['question']}, {p['anti_r']:g}/{p['r']:g})" for p in kept]
            method = ("recomputed: newer polls than RCP's average" if rcp
                      else "recomputed: RCP publishes no average")
            src = (f"Recomputed (RCP average predates newer polls): latest poll by each pollster ending "
                   f"{WINDOW_START} or later, excluded pollsters removed" if rcp else
                   f"RCP-style average (RCP publishes none): latest poll by each pollster ending "
                   f"{WINDOW_START} or later, excluded pollsters removed")
            if any(p["end"] >= WINDOW_START for p in sponsored):
                src += ", partisan-sponsored polls left out"
            as_of = RETRIEVED.isoformat()
            url = f"https://www.poliwave.com/us/{st.lower()}/sen-fed"
            local = ("sources/senate_polls_2026/recent/recent_polls_compiled.json" if st in comp
                     else "sources/senate_polls_2026/votehub_polls_api_C.json")
            published = round(rcp["published"][0] - rcp["published"][1], 1) if rcp else ""
            n = len(kept)
            ras = any("rasmussen" in p["pollster"].lower() for p in polls if p["end"] >= WINDOW_START)
        margin = anti - rep
        blend = margin if st in THREE_WAY else 100 * margin / (anti + rep)
        rows.append({
            "state": st, "d": round(anti, 2), "r": round(rep, 2), "margin": round(margin, 2),
            "blend_margin": round(blend, 2), "n_polls": n,
            "independent": "yes" if st in INDEPENDENT else "no", "three_way": "yes" if st in THREE_WAY else "no",
            "margin_published": published, "source": src, "rasmussen_removed": "yes" if ras else "no",
            "as_of": as_of, "sponsors": "; ".join(used), "url": url, "local_file": local,
            "race_note": RACE_NOTES.get(st, ""), "method": method,
            "newer_polls": "; ".join(f"{label(p)} ending {p['end']}, released {p['released'] or 'n/a'}"
                                     for p in newer)})
        report.append(f"{st}: {method}; {n} poll(s); anti-R {anti:.2f} / R {rep:.2f} -> margin {margin:+.2f}, "
                      f"blend margin {blend:+.2f}" + (f" (RCP published {published:+.1f})" if published != "" else ""))
        if newer:
            report.append(f"    newer than RCP's average (built {rcp['built']}): " +
                          "; ".join(f"{label(p)} ending {p['end']} released {p['released'] or 'n/a'}" for p in newer))
        for u in used:
            report.append(f"    - {u}")
        if dropped:
            report.append(f"    left out: {'; '.join(dropped)}")
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return "\n".join(report)


if __name__ == "__main__":
    print(build())
