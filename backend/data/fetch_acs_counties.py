"""Fetch ACS demographics at county level — same variables as fetch_acs.py
but with `for=county:*&in=state:*`. Two-batch split to fit Census 50-var limit.

Output: data/demographics_acs_counties.csv (~3,143 county rows).
"""
import csv, json, os, sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from fetch_acs import (
    VARS_A, VARS_B, load_env, fnum, ACS_BASE, ACS_YEAR, STATE_FIPS,
)

OUT = Path(__file__).resolve().parent / "demographics_acs_counties.csv"


def _fetch_chunk(key, vars_list):
    params = {
        "get": ",".join(["NAME"] + vars_list),
        "for": "county:*",
        "in": "state:*",
        "key": key,
    }
    url = f"{ACS_BASE}?{urlencode(params)}"
    with urlopen(url, timeout=120) as r:
        data = json.loads(r.read())
    header = data[0]
    return [dict(zip(header, row)) for row in data[1:]]


def fetch_county_data(key):
    a = _fetch_chunk(key, VARS_A)
    b = _fetch_chunk(key, VARS_B)
    b_idx = {(r["state"], r["county"]): r for r in b}
    out = []
    for ra in a:
        rb = b_idx.get((ra["state"], ra["county"]))
        if rb is None: continue
        out.append({**ra, **{k: v for k, v in rb.items() if k in VARS_B}})
    return out


def normalize(raw_rows):
    rows = []
    for r in raw_rows:
        state_fips = r["state"]
        county_fips = r["county"]
        state = STATE_FIPS.get(state_fips)
        if state is None: continue   # skip DC / PR / territories without USPS code
        fips = state_fips + county_fips   # 5-digit county FIPS

        total_pop = fnum(r["B01003_001E"])
        race_total = fnum(r["B03002_001E"])
        if race_total == 0: continue
        white_nh = fnum(r["B03002_003E"])
        black    = fnum(r["B03002_004E"])
        asian    = fnum(r["B03002_006E"])
        hispanic = fnum(r["B03002_012E"])
        other = max(race_total - white_nh - black - asian - hispanic, 0)

        edu_total = fnum(r["B15003_001E"])
        college_count = sum(fnum(r[v]) for v in
                            ("B15003_022E","B15003_023E","B15003_024E","B15003_025E"))
        wnh_25p = fnum(r["C15002H_001E"])
        wnh_col = fnum(r["C15002H_006E"]) + fnum(r["C15002H_011E"])
        nwh_25p = max(edu_total - wnh_25p, 0)
        nwh_col = max(college_count - wnh_col, 0)

        under18 = sum(fnum(r[v]) for v in (
            "B01001_003E","B01001_004E","B01001_005E","B01001_006E",
            "B01001_027E","B01001_028E","B01001_029E","B01001_030E"))
        vap = max(total_pop - under18, 0)
        age_18_29 = sum(fnum(r[v]) for v in (
            "B01001_007E","B01001_008E","B01001_009E","B01001_010E","B01001_011E",
            "B01001_031E","B01001_032E","B01001_033E","B01001_034E","B01001_035E"))
        age_30_44 = sum(fnum(r[v]) for v in (
            "B01001_012E","B01001_013E","B01001_014E",
            "B01001_036E","B01001_037E","B01001_038E"))
        age_45_64 = sum(fnum(r[v]) for v in (
            "B01001_015E","B01001_016E","B01001_017E","B01001_018E","B01001_019E",
            "B01001_039E","B01001_040E","B01001_041E","B01001_042E","B01001_043E"))
        age_65p = sum(fnum(r[v]) for v in (
            "B01001_020E","B01001_021E","B01001_022E","B01001_023E","B01001_024E","B01001_025E",
            "B01001_044E","B01001_045E","B01001_046E","B01001_047E","B01001_048E","B01001_049E"))

        rows.append({
            "fips": fips, "state": state,
            "name": r["NAME"].split(",")[0].strip(),
            "pct_white_nh": round(100 * white_nh / race_total, 2),
            "pct_black":    round(100 * black    / race_total, 2),
            "pct_hispanic": round(100 * hispanic / race_total, 2),
            "pct_asian":    round(100 * asian    / race_total, 2),
            "pct_other":    round(100 * other    / race_total, 2),
            "pct_college":  round(100 * college_count / edu_total, 2) if edu_total else 0,
            "pct_white_nh_college":     round(100 * wnh_col / edu_total, 2) if edu_total else 0,
            "pct_white_nh_non_college": round(100 * max(wnh_25p - wnh_col, 0) / edu_total, 2) if edu_total else 0,
            "pct_nonwhite_college":     round(100 * nwh_col / edu_total, 2) if edu_total else 0,
            "pct_nonwhite_non_college": round(100 * max(nwh_25p - nwh_col, 0) / edu_total, 2) if edu_total else 0,
            "pct_under_30": round(100 * age_18_29 / vap, 2) if vap else 0,
            "pct_30_44":    round(100 * age_30_44 / vap, 2) if vap else 0,
            "pct_45_64":    round(100 * age_45_64 / vap, 2) if vap else 0,
            "pct_65_plus":  round(100 * age_65p  / vap, 2) if vap else 0,
            "median_age":   fnum(r["B01002_001E"]),
            "median_income": int(fnum(r["B19013_001E"])),
            "total_population": int(total_pop),
            "source": f"ACS_{ACS_YEAR}_5yr",
        })
    return sorted(rows, key=lambda r: r["fips"])


def main():
    load_env()
    key = os.environ.get("CENSUS_API_KEY")
    if not key:
        sys.exit("CENSUS_API_KEY not set")
    print(f"Fetching ACS {ACS_YEAR} 5-year demographics at county level...", file=sys.stderr)
    raw = fetch_county_data(key)
    print(f"  got {len(raw)} raw county rows", file=sys.stderr)
    rows = normalize(raw)
    print(f"  kept {len(rows)} counties after filtering", file=sys.stderr)

    cols = list(rows[0].keys())
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
