"""For the 7 redrawn states, aggregate tract-level ACS edu / age / income
onto the NEW district lines via the user's BAFs.

Method (standard population-weighted reaggregation):

  1. For each block in the state, read its population from DRA's block CSV
     and its district from the BAF. Tract GEOID = first 11 chars of block GEOID.
  2. For each (tract, district) pair, accumulate block population. That gives
     the share of each tract that falls in each district.
  3. Fetch ACS tract data (B15003 education, B01001 age brackets, B19013
     income, B01002 median age, B01003 total pop).
  4. For each district, build numerator/denominator sums:
        pct_college = sum(tract_share * tract_BA+_count)
                       / sum(tract_share * tract_25plus_count)
     Same idea for under-30 and 65+ shares of 18+ population.
  5. Median age / income use population-weighted mean of tract medians
     (approximation; medians don't compose exactly, but close enough for
     display).

Within-tract uniformity is the standard assumption; tracts are small (~4K
people) so the error is small.

Output: demographics_acs_new_lines.csv (~140 rows, redrawn states only).
"""

import csv
import io
import json
import os
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DATA_DIR = Path(__file__).resolve().parent
CACHE = DATA_DIR / "cache"
OUT = DATA_DIR / "demographics_acs_new_lines.csv"

REDRAWN_STATES = ["CA", "TX", "OH", "NC", "TN", "MO", "UT", "FL", "LA", "AL"]

STATE_USPS_TO_FIPS = {
    "CA": "06", "TX": "48", "OH": "39", "NC": "37",
    "TN": "47", "MO": "29", "UT": "49", "FL": "12", "LA": "22", "AL": "01",
}

ACS_YEAR = "2023"
ACS_BASE = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5"

# Variables — same set as fetch_acs.py minus race (already from DRA)
B15003_TOTAL = "B15003_001E"
B15003_COLLEGE = ("B15003_022E", "B15003_023E", "B15003_024E", "B15003_025E")
B01001_UNDER18 = (
    "B01001_003E", "B01001_004E", "B01001_005E", "B01001_006E",
    "B01001_027E", "B01001_028E", "B01001_029E", "B01001_030E",
)
B01001_18_29 = (
    "B01001_007E", "B01001_008E", "B01001_009E", "B01001_010E", "B01001_011E",
    "B01001_031E", "B01001_032E", "B01001_033E", "B01001_034E", "B01001_035E",
)
B01001_30_44 = (
    "B01001_012E", "B01001_013E", "B01001_014E",
    "B01001_036E", "B01001_037E", "B01001_038E",
)
B01001_45_64 = (
    "B01001_015E", "B01001_016E", "B01001_017E", "B01001_018E", "B01001_019E",
    "B01001_039E", "B01001_040E", "B01001_041E", "B01001_042E", "B01001_043E",
)
B01001_65P = (
    "B01001_020E", "B01001_021E", "B01001_022E", "B01001_023E", "B01001_024E", "B01001_025E",
    "B01001_044E", "B01001_045E", "B01001_046E", "B01001_047E", "B01001_048E", "B01001_049E",
)
B01001_TOTAL = "B01001_001E"
B01002_MEDIAN_AGE = "B01002_001E"
B19013_MEDIAN_INC = "B19013_001E"
B01003_TOTAL_POP = "B01003_001E"
# C15002H = white-alone-not-Hispanic × education, 25+. Used for the four-cell
# race-x-edu sliders. Nonwhite counts come from B15003 totals minus H.
C15002H_TOTAL = "C15002H_001E"
C15002H_COLLEGE = ("C15002H_006E", "C15002H_011E")  # male BA+, female BA+

# Two batches because Census API caps at 50 vars per request. Batch A holds
# the core demographic + edu + under-18/18-29/65+ brackets; batch B holds the
# middle-band age brackets (30-44, 45-64).
VARS_A = (
    [B15003_TOTAL] + list(B15003_COLLEGE)
    + [C15002H_TOTAL] + list(C15002H_COLLEGE)
    + [B01001_TOTAL] + list(B01001_UNDER18) + list(B01001_18_29) + list(B01001_65P)
    + [B01002_MEDIAN_AGE, B19013_MEDIAN_INC, B01003_TOTAL_POP]
)
VARS_B = list(B01001_30_44) + list(B01001_45_64)
ALL_VARS = VARS_A + VARS_B


def load_env():
    env_path = DATA_DIR.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def fnum(s):
    if s is None or s in ("", "null"):
        return 0.0
    try:
        v = float(s)
        return v if v >= 0 else 0.0
    except ValueError:
        return 0.0


def _fetch_tract_chunk(state_fips: str, key: str, vars_list: list[str]) -> dict[str, dict]:
    params = {
        "get": ",".join(["NAME"] + vars_list),
        "for": "tract:*",
        "in": f"state:{state_fips}",
        "key": key,
    }
    url = f"{ACS_BASE}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "house-2026 acs-tract-fetch"})
    with urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    header = data[0]
    out = {}
    for row in data[1:]:
        rec = dict(zip(header, row))
        geoid = rec["state"] + rec["county"] + rec["tract"]
        out[geoid] = {v: fnum(rec[v]) for v in vars_list}
    return out


def fetch_tracts(state_fips: str, key: str) -> dict[str, dict]:
    """Return {11-digit tract GEOID -> {var: float}}, merged across the two
    API requests we need to fit under Census's 50-var limit."""
    a = _fetch_tract_chunk(state_fips, key, VARS_A)
    b = _fetch_tract_chunk(state_fips, key, VARS_B)
    out = {}
    for geoid, va in a.items():
        vb = b.get(geoid, {})
        out[geoid] = {**va, **vb}
    return out


def load_block_pops(state: str) -> dict[str, float]:
    """Return {15-digit block GEOID -> T_20_CENS_Total}."""
    zip_path = CACHE / f"block_{state}.zip"
    if not zip_path.exists():
        sys.exit(f"missing {zip_path}. Run aggregate_dra.py first to populate cache.")
    with zipfile.ZipFile(zip_path) as z:
        csv_name = next(n for n in z.namelist() if n.endswith(".csv"))
        with z.open(csv_name) as fbin:
            reader = csv.DictReader(io.TextIOWrapper(fbin, encoding="utf-8"))
            return {r["GEOID"]: fnum(r["T_20_CENS_Total"]) for r in reader}


def load_baf(state: str) -> dict[str, int]:
    path = DATA_DIR / f"baf_{state.lower()}.csv"
    out = {}
    with path.open(newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    header = [h.strip().lower() for h in rows[0]]
    block_i = next(i for i, h in enumerate(header) if h in ("geoid", "geoid20", "blockid", "block_id", "block"))
    dist_i = next(i for i, h in enumerate(header) if h in ("district", "districtid", "district_id", "cd"))
    for r in rows[1:]:
        if len(r) <= max(block_i, dist_i):
            continue
        try:
            d = int(r[dist_i].strip())
        except ValueError:
            continue
        if d <= 0:
            continue
        out[r[block_i].strip().lstrip("'")] = d
    return out


def process_state(state: str, key: str) -> list[dict]:
    print(f"\n== {state} ==", file=sys.stderr)
    fips = STATE_USPS_TO_FIPS[state]
    baf = load_baf(state)
    block_pop = load_block_pops(state)
    tracts = fetch_tracts(fips, key)
    print(f"  baf={len(baf):,} blocks  block_pop={len(block_pop):,}  tracts={len(tracts):,}",
          file=sys.stderr)

    # tract -> district -> block_pop_sum
    tract_district_pop: dict[str, dict[int, float]] = {}
    unmatched_blocks = 0
    for block_id, district in baf.items():
        pop = block_pop.get(block_id, 0.0)
        if pop == 0:
            continue
        tract = block_id[:11]
        td = tract_district_pop.setdefault(tract, {})
        td[district] = td.get(district, 0.0) + pop

    # Compute district aggregations
    # acc[district] = {col_num, col_den, under30_num, vap_num (denom for both age sliders),
    #                  age65_num, med_age_wsum, med_inc_wsum, weight_sum, total_pop_sum}
    acc: dict[int, dict[str, float]] = {}

    for tract_geoid, dist_pops in tract_district_pop.items():
        t = tracts.get(tract_geoid)
        if t is None:
            continue  # tract not in ACS response (unusual; ACS covers populated tracts)
        tract_total_pop = sum(dist_pops.values())
        if tract_total_pop == 0:
            continue
        # Tract-level aggregates
        t_25plus = t[B15003_TOTAL]
        t_college = sum(t[v] for v in B15003_COLLEGE)
        t_wnh_25plus = t[C15002H_TOTAL]
        t_wnh_college = sum(t[v] for v in C15002H_COLLEGE)
        t_total_b01001 = t[B01001_TOTAL]
        t_under18 = sum(t[v] for v in B01001_UNDER18)
        t_18_29 = sum(t[v] for v in B01001_18_29)
        t_30_44 = sum(t[v] for v in B01001_30_44)
        t_45_64 = sum(t[v] for v in B01001_45_64)
        t_65p = sum(t[v] for v in B01001_65P)
        t_vap = max(t_total_b01001 - t_under18, 0)
        t_med_age = t[B01002_MEDIAN_AGE]
        t_med_inc = t[B19013_MEDIAN_INC]

        for district, dpop in dist_pops.items():
            share = dpop / tract_total_pop
            a = acc.setdefault(district, {
                "col_num": 0.0, "col_den": 0.0,
                "wnh_col_num": 0.0, "wnh_total_num": 0.0,
                "under30_num": 0.0, "age3044_num": 0.0, "age4564_num": 0.0, "age65_num": 0.0,
                "vap_den": 0.0,
                "med_age_wsum": 0.0, "med_inc_wsum": 0.0, "med_inc_weight": 0.0,
                "weight_sum": 0.0,
                "total_pop_sum": 0.0,
            })
            # counts × share
            a["col_num"] += share * t_college
            a["col_den"] += share * t_25plus
            a["wnh_col_num"] += share * t_wnh_college
            a["wnh_total_num"] += share * t_wnh_25plus
            a["under30_num"] += share * t_18_29
            a["age3044_num"] += share * t_30_44
            a["age4564_num"] += share * t_45_64
            a["age65_num"] += share * t_65p
            a["vap_den"] += share * t_vap
            # population-weighted median (approximation): weight by block pop assigned
            a["med_age_wsum"] += dpop * t_med_age
            # Median income at tract level is 0 for tracts with no households (some institutional)
            if t_med_inc > 0:
                a["med_inc_wsum"] += dpop * t_med_inc
                a["med_inc_weight"] += dpop
            a["weight_sum"] += dpop
            a["total_pop_sum"] += dpop

    # Materialize rows
    out = []
    for district in sorted(acc):
        a = acc[district]
        label = f"{state}-{district:02d}"
        pct_college = (a["col_num"] / a["col_den"] * 100) if a["col_den"] > 0 else None
        # Four-cell race-x-education shares of all adults 25+
        if a["col_den"] > 0:
            pct_white_nh_college = a["wnh_col_num"] / a["col_den"] * 100
            pct_white_nh_non_college = (a["wnh_total_num"] - a["wnh_col_num"]) / a["col_den"] * 100
            pct_nonwhite_college = (a["col_num"] - a["wnh_col_num"]) / a["col_den"] * 100
            pct_nonwhite_non_college = max(
                ((a["col_den"] - a["wnh_total_num"]) - (a["col_num"] - a["wnh_col_num"]))
                / a["col_den"] * 100,
                0.0,
            )
        else:
            pct_white_nh_college = pct_white_nh_non_college = None
            pct_nonwhite_college = pct_nonwhite_non_college = None
        pct_under_30 = (a["under30_num"] / a["vap_den"] * 100) if a["vap_den"] > 0 else None
        pct_30_44   = (a["age3044_num"] / a["vap_den"] * 100) if a["vap_den"] > 0 else None
        pct_45_64   = (a["age4564_num"] / a["vap_den"] * 100) if a["vap_den"] > 0 else None
        pct_65_plus = (a["age65_num"] / a["vap_den"] * 100) if a["vap_den"] > 0 else None
        med_age = (a["med_age_wsum"] / a["weight_sum"]) if a["weight_sum"] > 0 else None
        med_inc = (a["med_inc_wsum"] / a["med_inc_weight"]) if a["med_inc_weight"] > 0 else None
        out.append({
            "district": label,
            "pct_college": round(pct_college, 2) if pct_college is not None else "",
            "pct_white_nh_college":     round(pct_white_nh_college, 2)     if pct_white_nh_college     is not None else "",
            "pct_white_nh_non_college": round(pct_white_nh_non_college, 2) if pct_white_nh_non_college is not None else "",
            "pct_nonwhite_college":     round(pct_nonwhite_college, 2)     if pct_nonwhite_college     is not None else "",
            "pct_nonwhite_non_college": round(pct_nonwhite_non_college, 2) if pct_nonwhite_non_college is not None else "",
            "pct_under_30": round(pct_under_30, 2) if pct_under_30 is not None else "",
            "pct_30_44":    round(pct_30_44, 2)   if pct_30_44   is not None else "",
            "pct_45_64":    round(pct_45_64, 2)   if pct_45_64   is not None else "",
            "pct_65_plus":  round(pct_65_plus, 2) if pct_65_plus is not None else "",
            "median_age": round(med_age, 1) if med_age is not None else "",
            "median_income": int(med_inc) if med_inc is not None else "",
            "total_population_acs": int(a["total_pop_sum"]),
            "source": f"ACS_{ACS_YEAR}_tract_to_new_lines",
        })
    return out


def main():
    load_env()
    key = os.environ.get("CENSUS_API_KEY")
    if not key:
        sys.exit("CENSUS_API_KEY not set")

    targets = REDRAWN_STATES
    if len(sys.argv) > 1:
        targets = [s.upper() for s in sys.argv[1:]]

    all_rows = []
    for state in targets:
        all_rows.extend(process_state(state, key))

    cols = ["district", "pct_college",
            "pct_white_nh_college", "pct_white_nh_non_college",
            "pct_nonwhite_college", "pct_nonwhite_non_college",
            "pct_under_30", "pct_30_44", "pct_45_64", "pct_65_plus",
            "median_age", "median_income", "total_population_acs", "source"]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nWrote {OUT} ({len(all_rows)} rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
