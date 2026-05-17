"""Build state-level data for the Senate model.

Produces senate_states.json with one entry per state:
  - presidential margin 2020, 2024
  - state trend (state shift vs. national)
  - aggregated demographics (population-weighted from district data)
  - 2026 Class II seat roster (incumbent, party, retiring, etc.)
  - Senate WAR (most recent cycle per senator)

Reads:
  national_sensitivity_v20.csv
  demographics.csv
  raw_war.csv
"""

import csv
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).resolve().parent
V20 = DATA_DIR.parent.parent / "national_sensitivity_v20.csv"
DEMOS = DATA_DIR / "demographics.csv"
RAW_WAR = DATA_DIR / "raw_war.csv"
OUT = DATA_DIR / "senate_states.json"

# Presidential national popular vote margins (D-R).
# 2020 = Biden D+4.5, 2024 = Trump R+1.5.
PRES_2020 = 4.5
PRES_2024 = -1.5
NATIONAL_PRES_SHIFT = PRES_2024 - PRES_2020   # -6.0 (national moved 6 pts R)

# State USPS -> full name (Senate WAR rows use full state names).
STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}
NAME_TO_USPS = {v: k for k, v in STATE_NAMES.items()}

# 2026 Senate seat roster (Class II + specials).
# Each entry: state -> dict with seat info. Multiple seats per state become
# {state: [seat1, seat2]} only for special elections.
SEATS_2026 = {
    # === Class II (regular term ends Jan 2027) ===
    "AL": {"incumbent": "(open, Tuberville→gov)", "party": "(R)", "retiring": True, "type": "regular"},
    "AK": {"incumbent": "Dan Sullivan", "party": "(R)", "retiring": False, "type": "regular"},
    "AR": {"incumbent": "Tom Cotton", "party": "(R)", "retiring": False, "type": "regular"},
    "CO": {"incumbent": "John Hickenlooper", "party": "(D)", "retiring": False, "type": "regular"},
    "DE": {"incumbent": "Chris Coons", "party": "(D)", "retiring": False, "type": "regular"},
    "GA": {"incumbent": "Jon Ossoff", "party": "(D)", "retiring": False, "type": "regular"},
    "ID": {"incumbent": "Jim Risch", "party": "(R)", "retiring": False, "type": "regular"},
    "IL": {"incumbent": "(open, Durbin retiring)", "party": "(D)", "retiring": True, "type": "regular"},
    "IA": {"incumbent": "(open, Ernst retiring)", "party": "(R)", "retiring": True, "type": "regular"},
    "KS": {"incumbent": "Roger Marshall", "party": "(R)", "retiring": False, "type": "regular"},
    "KY": {"incumbent": "(open, McConnell retiring)", "party": "(R)", "retiring": True, "type": "regular"},
    "LA": {"incumbent": "(open, Cassidy lost primary)", "party": "(R)", "retiring": True, "type": "regular",
           "primary_unresolved": True},  # Cassidy lost; both R and D primaries head to runoff
    "ME": {"incumbent": "Susan Collins", "party": "(R)", "retiring": False, "type": "regular"},
    "MA": {"incumbent": "Ed Markey", "party": "(D)", "retiring": False, "type": "regular"},
    "MI": {"incumbent": "(open, Peters retiring)", "party": "(D)", "retiring": True, "type": "regular"},
    "MN": {"incumbent": "(open, Smith retiring)", "party": "(D)", "retiring": True, "type": "regular"},
    "MS": {"incumbent": "Cindy Hyde-Smith", "party": "(R)", "retiring": False, "type": "regular"},
    "MT": {"incumbent": "(open, Daines retiring)", "party": "(R)", "retiring": True, "type": "regular"},
    "NE": {"incumbent": "Pete Ricketts", "party": "(R)", "retiring": False, "type": "regular"},
    "NH": {"incumbent": "(open, Shaheen retiring)", "party": "(D)", "retiring": True, "type": "regular"},
    "NJ": {"incumbent": "Cory Booker", "party": "(D)", "retiring": False, "type": "regular"},
    "NM": {"incumbent": "Ben Ray Luján", "party": "(D)", "retiring": False, "type": "regular"},
    "NC": {"incumbent": "(open, Tillis retiring)", "party": "(R)", "retiring": True, "type": "regular"},
    "OK": {"incumbent": "(open, Mullin→DHS)", "party": "(R)", "retiring": True, "type": "regular",
           "note": "Mullin resigned to become DHS Director; Gov. Stitt to appoint successor"},
    "OR": {"incumbent": "Jeff Merkley", "party": "(D)", "retiring": False, "type": "regular"},
    "RI": {"incumbent": "Jack Reed", "party": "(D)", "retiring": False, "type": "regular"},
    "SC": {"incumbent": "Lindsey Graham", "party": "(R)", "retiring": False, "type": "regular"},
    "SD": {"incumbent": "Mike Rounds", "party": "(R)", "retiring": False, "type": "regular"},
    "TN": {"incumbent": "Bill Hagerty", "party": "(R)", "retiring": False, "type": "regular"},
    "TX": {"incumbent": "John Cornyn", "party": "(R)", "retiring": False, "type": "regular",
           "primary_unresolved": True,
           "note": "Cornyn vs Paxton R primary headed to runoff; nominee uncertain. "
                   "WAR + incumbency suppressed until runoff resolves."},
    "VA": {"incumbent": "Mark Warner", "party": "(D)", "retiring": False, "type": "regular"},
    "WV": {"incumbent": "Shelley Moore Capito", "party": "(R)", "retiring": False, "type": "regular"},
    "WY": {"incumbent": "(open, Lummis retiring)", "party": "(R)", "retiring": True, "type": "regular"},
    # === Specials (Class I remainders) ===
    # `appointed: True` zeroes out incumbency_adj — appointees haven't won an
    # election yet so they don't carry the typical ~3pt structural advantage
    # that comes from established campaign infrastructure, name ID, etc.
    "OH": {"incumbent": "Jon Husted", "party": "(R)", "retiring": False, "type": "special",
           "appointed": True,
           "note": "appointed 2025; special for remainder of Vance's term to 2028"},
    "FL": {"incumbent": "Ashley Moody", "party": "(R)", "retiring": False, "type": "special",
           "appointed": True,
           "note": "appointed 2025; special for remainder of Rubio's term to 2028"},
}


# Known, well-established 2026 Senate challengers. For each, the model
# auto-looks-up the candidate's most recent House/Senate WAR from raw_war.csv
# using state as disambiguator. The "war" value below is a manual fallback
# used only when no raw-data match is found (e.g., Roy Cooper, who ran for
# Governor but never House/Senate).
CHALLENGERS = {
    # Manual `war` values are no longer permitted. All entries fall back to
    # auto-match from raw_war.csv (House + Senate records). Candidates without
    # any federal-race record (e.g. former governors like Cooper / LePage)
    # contribute 0 from this slot. State-aware disambiguation handles same-name
    # candidates (e.g. Mike Rogers MI Senate vs AL-03 House).
    #
    # Optional `co_nominee` / `co_nominee_party`: for OPEN seats where both
    # major-party nominees are known, the second nominee is shown in the UI.
    # Their WAR is auto-looked-up too and contributes to challenger_adj.
    "NC": {"name": "Roy Cooper", "party": "(D)", "war": 0.0,
           "co_nominee": "Michael Whatley", "co_nominee_party": "(R)",
           "note": "Cooper: former 2-term NC governor. Whatley: former RNC chair. "
                   "Both nominees lack federal-race WAR; no auto-match available."},
    "AK": {"name": "Mary Peltola", "party": "(D)", "war": 0.0,
           "note": "auto-WAR from 2024 House AK-AL"},
    "NE": {"name": "Dan Osborn", "party": "(I)", "war": 0.0,
           "note": "auto-WAR from 2024 Senate NE"},
    "OH": {"name": "Sherrod Brown", "party": "(D)", "war": 0.0,
           "note": "auto-WAR from 2024 Senate OH"},
    "MI": {"name": "Mike Rogers", "party": "(R)", "war": 0.0,
           "note": "auto-WAR from 2024 Senate MI (state-disambiguated from AL-03 House Mike Rogers)"},
    "OK": {"name": "Kevin Hern", "party": "(R)", "war": 0.0,
           "note": "auto-WAR from 2024 House OK-01"},
    # === From Wikipedia sweep (post-primary nominees, May 2026) ===
    # Whatley (R) is the same-party nominee for NC (R seat, Tillis retiring);
    # not tracked separately since data model is single-challenger-per-seat.
    "AR": {"name": "Hallie Shoffner", "party": "(D)", "war": 0.0,
           "note": "2026 D nominee per Wikipedia"},
    "CO": {"name": "Mark Baisley", "party": "(R)", "war": 0.0,
           "note": "2026 R nominee per Wikipedia"},
    "IL": {"name": "Don Tracy", "party": "(R)", "war": 0.0,
           "co_nominee": "Juliana Stratton", "co_nominee_party": "(D)",
           "note": "Open Durbin seat. Tracy: R nominee. Stratton: D nominee (IL Lt. Gov)."},
    "MA": {"name": "John Deaton", "party": "(R)", "war": 0.0,
           "note": "2026 R nominee per Wikipedia"},
    "MS": {"name": "Scott Colom", "party": "(D)", "war": 0.0,
           "note": "2026 D nominee per Wikipedia"},
    "SD": {"name": "Julian Beaudion", "party": "(D)", "war": 0.0,
           "note": "2026 D nominee per Wikipedia"},
    "TX": {"name": "James Talarico", "party": "(D)", "war": 0.0,
           "note": "2026 D nominee per Wikipedia"},
    "WV": {"name": "Rachel Fetty Anderson", "party": "(D)", "war": 0.0,
           "note": "2026 D nominee per Wikipedia"},
    "NH": {"name": "Chris Pappas", "party": "(D)", "war": 0.0,
           "note": "Open Shaheen seat. Sitting NH-01 rep; auto-WAR from 2024 House."},
    "ME": {"name": "Graham Platner", "party": "(D)", "war": 0.0,
           "note": "2026 presumptive D nominee; no federal-race record."},
    "IA": {"name": "Ashley Hinson", "party": "(R)", "war": 0.0,
           "note": "Open Ernst seat. Sitting IA-02 rep; auto-WAR from 2024 House."},
    "WY": {"name": "Harriet Hageman", "party": "(R)", "war": 0.0,
           "note": "Open Lummis seat. Sitting WY-AL rep; auto-WAR from 2024 House."},
    "SC": {"name": "Annie Andrews", "party": "(D)", "war": 0.0,
           "note": "2026 D Senate nominee (challenger to Graham)."},
}


def _strip_accents(s: str) -> str:
    """Fold accented characters to ASCII so 'Luján' matches 'Lujan' in raw_war."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _strip_suffix(s: str) -> str:
    return re.sub(r"\b(jr|sr|ii|iii|iv)\.?\b", "", s, flags=re.IGNORECASE).strip()


def _fnum(s):
    if s is None or s == "":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_incumbent(field):
    s = (field or "").strip()
    if s.startswith("(") or s.lower().startswith("open"):
        return None
    return re.sub(r"\s*\(.*?\)\s*$", "", s).strip() or None


def load_state_presidential_margins():
    """Pick one row per state from v20 (state_margin fields are identical across districts)."""
    out = {}
    with V20.open() as f:
        for r in csv.DictReader(f):
            state = r["state"]
            if state not in out:
                out[state] = {
                    "state_margin_2024": _fnum(r["state_margin_2024"]),
                    "state_margin_2020": _fnum(r["state_margin_2020"]),
                }
    return out


def aggregate_state_demographics():
    """Population-weighted average of district demographics, per state."""
    pcts = ("pct_white_nh", "pct_black", "pct_hispanic", "pct_asian", "pct_other",
            "pct_college",
            "pct_white_nh_college", "pct_white_nh_non_college",
            "pct_nonwhite_college", "pct_nonwhite_non_college",
            "pct_under_30", "pct_30_44", "pct_45_64", "pct_65_plus",
            "median_age", "median_income")
    accum = defaultdict(lambda: {"pop": 0.0, **{k: 0.0 for k in pcts}})
    with DEMOS.open() as f:
        for r in csv.DictReader(f):
            district = r["district"]
            state = district.split("-")[0]
            pop = _fnum(r.get("total_population"))
            if pop == 0:
                continue
            accum[state]["pop"] += pop
            for k in pcts:
                accum[state][k] += pop * _fnum(r.get(k))
    out = {}
    for state, agg in accum.items():
        if agg["pop"] == 0:
            continue
        out[state] = {k: round(agg[k] / agg["pop"], 2) for k in pcts}
        out[state]["total_population"] = int(agg["pop"])
    return out


def _clean_name(raw: str) -> str:
    """Strip parenthetical annotations like '(Ind)' and trailing suffixes."""
    s = re.sub(r"\s*\(.*?\)\s*", " ", raw or "").strip()
    return s


# Time-weighting for multi-cycle WAR blend; matches load_data.WAR_WEIGHTS.
WAR_WEIGHTS = (0.50, 0.30, 0.20)

# Drop all cycles from this set of years from the WAR blend. 2014 races are
# too old + the partisan environment was idiosyncratic enough that treating
# them as 20-30% of a current candidate's personal vote signal misleads.
WAR_DROP_YEARS: set[int] = {2014}


# Cross-chamber discount applied to non-federal cycles (Governor) when they
# contribute to a Senate WAR blend. Captures that statewide-but-not-federal
# personal vote partially transfers (name rec, brand) but doesn't fully
# nationalize.
GOV_CROSS_CHAMBER_DISCOUNT = 0.5


def _time_weighted_sortable(records: list[dict]) -> float:
    """Blend up to 3 most-recent cycles using WAR_WEIGHTS on the universal
    `sortable` column (R-positive). `records` must be year-desc sorted.
    Missing slots = 0 (mean regression toward the average candidate).
    Governor cycles are discounted by GOV_CROSS_CHAMBER_DISCOUNT."""
    s = 0.0
    for i, w in enumerate(WAR_WEIGHTS):
        if i < len(records):
            r = records[i]
            d = GOV_CROSS_CHAMBER_DISCOUNT if r.get("chamber") == "Governor" else 1.0
            s += w * r["sortable"] * d
    return s


def load_all_wars():
    """For each (state, name, party_letter), collect ALL Senate OR House cycle
    WAR records (year-desc). State context disambiguates same-name candidates
    (e.g., Mike Rogers MI Senate vs AL-03 House)."""
    by_key: dict[tuple[str, str, str], list[dict]] = {}
    with RAW_WAR.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            chamber = r.get("Chamber")
            if chamber not in ("Senate", "House", "Governor"):
                continue
            try:
                year = int(r["Year"])
                sortable = float(r["Sortable"])
            except (ValueError, KeyError, TypeError):
                continue
            if year in WAR_DROP_YEARS:
                continue
            geo = (r.get("Geography") or "").strip()
            geo_clean = re.sub(r"\s*\(.*?\)\s*$", "", geo).strip()
            # Strip trailing "Special" / "Spec" / "Special Election" markers
            geo_clean = re.sub(
                r"\s+(special election|special|spec|s\.?e\.?)$",
                "", geo_clean, flags=re.IGNORECASE,
            ).strip()
            if chamber in ("Senate", "Governor"):
                state = NAME_TO_USPS.get(geo_clean)
            else:
                # House geography is "XX-NN" (or "XX-AL")
                state = geo_clean.split("-")[0] if "-" in geo_clean else None
                if state not in STATE_NAMES:
                    state = None
            if state is None:
                continue
            for party_letter, name_field in (("D", "Democrat"), ("R", "Republican")):
                name = _strip_accents(_clean_name(r.get(name_field) or ""))
                if not name:
                    continue
                key = (state, name, party_letter)
                by_key.setdefault(key, []).append({
                    "year": year, "geo": geo, "chamber": chamber,
                    "sortable": sortable, "war_text": r.get("WAR", ""),
                })
    for lst in by_key.values():
        lst.sort(key=lambda r: r["year"], reverse=True)
    return by_key


def load_senate_wars():
    """Senate-only WAR lookup (incumbents are definitionally in a Senate race
    that matches their seat). Returns (state, name, party) -> list of records
    year-desc with only Senate chamber rows."""
    all_wars = load_all_wars()
    out = {}
    for k, recs in all_wars.items():
        senate_recs = [r for r in recs if r["chamber"] == "Senate"]
        if senate_recs:
            out[k] = senate_recs
    return out


def find_war(state, name, party_letter, all_wars):
    """Return the year-desc record list for (state, name, party), or None.
    `all_wars` values are lists (multi-cycle history). Names are accent-folded
    for matching (raw_war.csv uses ASCII; some current data uses accented spellings)."""
    if not name:
        return None
    name = _strip_accents(name)
    recs = all_wars.get((state, name, party_letter))
    if recs:
        return recs
    # Fallback: same last-name and party in the same state (handles middle-init / suffix variation)
    last = _strip_suffix(name).split()[-1].lower() if name else ""
    first_initial = (_strip_suffix(name).split() or [""])[0][:1].lower()
    for (s, n, p), v in all_wars.items():
        if s == state and p == party_letter:
            if _strip_suffix(n).split()[-1].lower() == last:
                if (_strip_suffix(n).split() or [""])[0][:1].lower() == first_initial:
                    return v
    return None


INCUMBENCY_ADV_SENATE = 3.0  # Senate incumbency typically ~3 pts (~higher than House)


def lookup_war_for_candidate(state, name, party_letter, all_wars):
    """Return (war_signed, most_recent_record) for the candidate. `war_signed`
    is the time-weighted blend over up to 3 cycles, in the candidate's own
    party-perspective (D-positive for D, R-positive for R). Missing cycles
    zero-fill (mean regression)."""
    if not name:
        return 0.0, None
    recs = find_war(state, name, party_letter, all_wars)
    if not recs:
        return 0.0, None
    sortable_blend = _time_weighted_sortable(recs)
    war_signed = -sortable_blend if party_letter == "D" else +sortable_blend
    return war_signed, recs[0]


def main():
    margins = load_state_presidential_margins()
    demos = aggregate_state_demographics()
    all_wars = load_all_wars()
    # Senate-only history per (state, name, party). Drop entries with no Senate cycles.
    wars = {}
    for k, recs in all_wars.items():
        senate_recs = [r for r in recs if r["chamber"] == "Senate"]
        if senate_recs:
            wars[k] = senate_recs

    states = {}
    for state, name in STATE_NAMES.items():
        m = margins.get(state) or {}
        d = demos.get(state) or {}
        seat = SEATS_2026.get(state)

        # State trend = state_shift - national_shift (D-positive)
        state_shift = m.get("state_margin_2024", 0) - m.get("state_margin_2020", 0)
        state_trend = state_shift - NATIONAL_PRES_SHIFT  # how much state moved vs national

        # Senate WAR + incumbency
        war_signed = 0.0
        war_year = None
        war_match = None
        if seat:
            inc_name = parse_incumbent(seat["incumbent"])
            party = seat["party"]
            party_letter = "D" if party == "(D)" else "R" if party == "(R)" else None
            # `primary_unresolved` means we know the seat-party incumbent but
            # they haven't yet secured renomination (e.g. Cornyn TX with a
            # Paxton runoff). Treat the seat as having no current nominee on
            # that side: skip WAR + incumbency until the runoff resolves.
            primary_open = bool(seat.get("primary_unresolved"))
            if inc_name and party_letter and not primary_open:
                recs = find_war(state, inc_name, party_letter, wars)
                if recs:
                    war_year = recs[0]["year"]
                    sortable_blend = _time_weighted_sortable(recs)
                    war_signed = -sortable_blend if party_letter == "D" else +sortable_blend
                    war_match = "exact"
            # war_adj is D-positive: +war for D, -war for R
            war_adj = war_signed if party_letter == "D" else -war_signed if party_letter == "R" else 0.0
            # No 'redrawn' concept at state level — no half-discount
            war_adj_discounted = war_adj
            # Incumbency advantage: skip for appointees (haven't won an election
            # yet) and for unresolved primaries (we don't yet know if the
            # incumbent will be the nominee).
            incumbency_adj = 0.0
            if inc_name and party_letter and not seat.get("appointed") and not primary_open:
                incumbency_adj = (INCUMBENCY_ADV_SENATE if party_letter == "D"
                                  else -INCUMBENCY_ADV_SENATE)
        else:
            war_adj = war_adj_discounted = incumbency_adj = 0.0
            party = None
            inc_name = None

        # Challenger overlay — prefer raw-data WAR over manual estimate.
        # Independents matched against the Democrat column (per raw_war.csv).
        ch = CHALLENGERS.get(state)
        challenger_adj = 0.0
        challenger_war_used = None
        challenger_war_source = None
        challenger_war_year = None
        if ch is not None:
            ch_party_letter = "D" if ch["party"] in ("(D)", "(I)") else "R"
            # 1. Try raw-data lookup
            ch_war_signed, ch_rec = lookup_war_for_candidate(
                state, ch["name"], ch_party_letter, all_wars)
            if ch_rec is not None:
                challenger_war_used = abs(ch_war_signed)  # "magnitude of personal vote"
                challenger_war_source = f"{ch_rec['year']} {ch_rec['chamber']} {ch_rec['geo']}"
                challenger_war_year = ch_rec["year"]
                # ch_war_signed is in the candidate's own party-perspective
                # D candidate (incl. I caucusing D): positive = D-favorable margin adj
                # R candidate: positive (R-overperform) = R-favorable, so flip
                if ch["party"] == "(R)":
                    challenger_adj = -ch_war_signed
                else:
                    challenger_adj = +ch_war_signed
            else:
                # 2. Fall back to manual estimate
                challenger_war_used = float(ch["war"])
                challenger_war_source = "manual"
                if ch["party"] == "(R)":
                    challenger_adj = -challenger_war_used
                else:
                    challenger_adj = +challenger_war_used

        # Co-nominee: optional second named candidate (typically same-party as
        # retiring incumbent on an open seat). Auto-WAR looked up, contribution
        # added to challenger_adj alongside the primary challenger.
        co_nominee_name = None
        co_nominee_party_val = None
        co_nominee_war = None
        co_nominee_war_source = None
        co_nominee_war_year = None
        co_nominee_adj = 0.0
        if ch is not None and ch.get("co_nominee"):
            co_nominee_name = ch["co_nominee"]
            co_nominee_party_val = ch.get("co_nominee_party")
            co_party_letter = "D" if co_nominee_party_val in ("(D)", "(I)") else "R"
            co_war_signed, co_rec = lookup_war_for_candidate(
                state, co_nominee_name, co_party_letter, all_wars)
            if co_rec is not None:
                co_nominee_war = abs(co_war_signed)
                co_nominee_war_source = f"{co_rec['year']} {co_rec['chamber']} {co_rec['geo']}"
                co_nominee_war_year = co_rec["year"]
                co_nominee_adj = -co_war_signed if co_nominee_party_val == "(R)" else +co_war_signed
            else:
                co_nominee_war = 0.0
                co_nominee_war_source = "manual"

        states[state] = {
            "state": state,
            "name": name,
            "presidential_margin_2024": m.get("state_margin_2024"),
            "presidential_margin_2020": m.get("state_margin_2020"),
            "state_trend": round(state_trend, 2),
            **d,
            "seat_up_2026": seat is not None,
            "seat_type": seat["type"] if seat else None,
            "incumbent": seat["incumbent"] if seat else None,
            "party": seat["party"] if seat else None,
            "retiring": seat["retiring"] if seat else False,
            "appointed": seat.get("appointed", False) if seat else False,
            "primary_unresolved": seat.get("primary_unresolved", False) if seat else False,
            "note": seat.get("note") if seat else None,
            "war": round(war_signed, 2),
            "war_year": war_year,
            "war_match": war_match,
            "war_adj_discounted": round(war_adj_discounted, 2),
            "incumbency_adj": round(incumbency_adj, 2),
            "challenger": ch["name"] if ch else None,
            "challenger_party": ch["party"] if ch else None,
            "challenger_war": round(challenger_war_used, 2) if challenger_war_used is not None else None,
            "challenger_war_year": challenger_war_year,
            "challenger_war_source": challenger_war_source,
            "challenger_adj": round(challenger_adj + co_nominee_adj, 2),
            "challenger_note": ch.get("note") if ch else None,
            "co_nominee": co_nominee_name,
            "co_nominee_party": co_nominee_party_val,
            "co_nominee_war": round(co_nominee_war, 2) if co_nominee_war is not None else None,
            "co_nominee_war_year": co_nominee_war_year,
            "co_nominee_war_source": co_nominee_war_source,
            "co_nominee_adj": round(co_nominee_adj, 2),
        }

    OUT.write_text(json.dumps({"states": states, "national": {
        "presidential_2020": PRES_2020,
        "presidential_2024": PRES_2024,
        "national_shift": NATIONAL_PRES_SHIFT,
        "incumbency_adv": INCUMBENCY_ADV_SENATE,
    }}, indent=None))
    print(f"Wrote {OUT}", file=sys.stderr)
    n_up = sum(1 for s in states.values() if s["seat_up_2026"])
    n_regular = sum(1 for s in states.values() if s.get("seat_type") == "regular")
    n_special = sum(1 for s in states.values() if s.get("seat_type") == "special")
    n_retiring = sum(1 for s in states.values() if s.get("retiring"))
    print(f"  states with 2026 seats: {n_up}  (regular={n_regular}, special={n_special})", file=sys.stderr)
    print(f"  retirements: {n_retiring}", file=sys.stderr)

    # Show WAR match counts
    matched = sum(1 for s in states.values()
                  if s["seat_up_2026"] and s["war_match"] and not s["retiring"])
    unmatched = sum(1 for s in states.values()
                    if s["seat_up_2026"] and not s["war_match"] and not s["retiring"]
                    and parse_incumbent(s["incumbent"] or ""))
    print(f"  WAR matched: {matched}, unmatched named: {unmatched}", file=sys.stderr)


if __name__ == "__main__":
    main()
