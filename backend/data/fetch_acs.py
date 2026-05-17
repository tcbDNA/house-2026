"""Pull ACS 5-year demographics at congressional-district level for the 370
districts in states that did NOT redistrict mid-decade.

Outputs demographics_acs.csv in this directory.

Why CD-level instead of tract + spatial join: for non-redrawn states the
Census-published CD aggregations are exactly on the lines we want (118th =
119th = v18 "2024" lines), so the spatial join would just reproduce the
Census's own work. Redrawn states (CA/TX/FL/OH/NC/MO/UT/TN) are excluded
here and come from DRA via Path B.
"""

import csv
import os
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ACS_YEAR = "2023"
ACS_BASE = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5"

REDRAWN_STATES = {"CA", "TX", "OH", "NC", "MO", "UT", "TN", "FL", "LA", "AL"}  # tagged as old-lines estimates; DRA aggregation overrides

STATE_FIPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}

AT_LARGE = {"AK", "DE", "ND", "SD", "VT", "WY"}

# Two variable batches because the Census API caps each request at 50 vars.
# Batch A: race, education, headline scalars, under-18 + 18-29 + 65+ brackets.
# Batch B: 30-44 + 45-64 age brackets (the "middle band" added for finer age
# resolution).
VARS_A = [
    # B03002 — Hispanic-origin-aware race
    "B03002_001E",  # total
    "B03002_003E",  # white alone, non-Hispanic
    "B03002_004E",  # Black alone, non-Hispanic
    "B03002_006E",  # Asian alone, non-Hispanic
    "B03002_012E",  # Hispanic or Latino (any race)
    # B15003 — education attainment, 25+ (all-race)
    "B15003_001E",
    "B15003_022E", "B15003_023E", "B15003_024E", "B15003_025E",
    # C15002H — white-alone-not-Hispanic × education for 25+
    "C15002H_001E", "C15002H_006E", "C15002H_011E",
    # Headline scalars
    "B01002_001E",  # median age
    "B19013_001E",  # median household income
    "B01003_001E",  # total population
    # B01001 brackets: under 18, 18-29, 65+
    "B01001_003E", "B01001_004E", "B01001_005E", "B01001_006E",
    "B01001_027E", "B01001_028E", "B01001_029E", "B01001_030E",
    "B01001_007E", "B01001_008E", "B01001_009E", "B01001_010E", "B01001_011E",
    "B01001_031E", "B01001_032E", "B01001_033E", "B01001_034E", "B01001_035E",
    "B01001_020E", "B01001_021E", "B01001_022E", "B01001_023E", "B01001_024E", "B01001_025E",
    "B01001_044E", "B01001_045E", "B01001_046E", "B01001_047E", "B01001_048E", "B01001_049E",
]

VARS_B = [
    # B01001 brackets: 30-44 (male 012-014, female 036-038)
    "B01001_012E", "B01001_013E", "B01001_014E",
    "B01001_036E", "B01001_037E", "B01001_038E",
    # B01001 brackets: 45-64 (male 015-019, female 039-043)
    "B01001_015E", "B01001_016E", "B01001_017E", "B01001_018E", "B01001_019E",
    "B01001_039E", "B01001_040E", "B01001_041E", "B01001_042E", "B01001_043E",
]

VARS = VARS_A + VARS_B  # full superset, used elsewhere for column lookups


def load_env():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def _fetch_chunk(key: str, vars_list: list[str]) -> list[dict]:
    params = {
        "get": ",".join(["NAME"] + vars_list),
        "for": "congressional district:*",
        "in": "state:*",
        "key": key,
    }
    url = f"{ACS_BASE}?{urlencode(params)}"
    import json
    with urlopen(url, timeout=60) as resp:
        data = json.loads(resp.read())
    headers = data[0]
    return [dict(zip(headers, row)) for row in data[1:]]


def fetch_cd_data(key: str) -> list[dict]:
    """Two API calls (Census 50-var limit), merged by (state, congressional district)."""
    a = _fetch_chunk(key, VARS_A)
    b = _fetch_chunk(key, VARS_B)
    b_by_key = {(r["state"], r["congressional district"]): r for r in b}
    merged = []
    for ra in a:
        rb = b_by_key.get((ra["state"], ra["congressional district"]))
        if rb is None:
            continue
        merged.append({**ra, **{k: v for k, v in rb.items() if k in VARS_B}})
    return merged


def fnum(s):
    if s is None or s in ("", "null"):
        return 0.0
    try:
        v = float(s)
        if v < 0:
            return 0.0  # ACS uses negatives as sentinels for "no data"
        return v
    except ValueError:
        return 0.0


def normalize(raw_rows: list[dict]) -> list[dict]:
    out = []
    skipped_nondistrict = 0
    redrawn_count = 0
    for r in raw_rows:
        state_fips = r["state"]
        cd_code = r["congressional district"]
        state = STATE_FIPS.get(state_fips)
        if state is None:
            continue  # DC, PR, etc.
        if cd_code in ("ZZ", "98", "99"):
            skipped_nondistrict += 1
            continue
        is_redrawn = state in REDRAWN_STATES
        if state in AT_LARGE:
            district = f"{state}-AL"
        else:
            district = f"{state}-{int(cd_code):02d}"

        total_pop = fnum(r["B01003_001E"])
        race_total = fnum(r["B03002_001E"])
        if race_total == 0:
            continue
        white_nh = fnum(r["B03002_003E"])
        black = fnum(r["B03002_004E"])
        asian = fnum(r["B03002_006E"])
        hispanic = fnum(r["B03002_012E"])
        other = max(race_total - white_nh - black - asian - hispanic, 0)

        edu_total = fnum(r["B15003_001E"])
        college_count = sum(fnum(r[v]) for v in
                            ("B15003_022E", "B15003_023E", "B15003_024E", "B15003_025E"))

        # Race × education breakdown (BA+ within each race iterator).
        white_nh_25p = fnum(r["C15002H_001E"])
        white_nh_college = fnum(r["C15002H_006E"]) + fnum(r["C15002H_011E"])
        # Nonwhite (Black + Hispanic + Asian + Other) is the complement.
        nonwhite_25p = max(edu_total - white_nh_25p, 0)
        nonwhite_college = max(college_count - white_nh_college, 0)
        white_nh_non_college = max(white_nh_25p - white_nh_college, 0)
        nonwhite_non_college = max(nonwhite_25p - nonwhite_college, 0)

        # VAP = total - under-18
        under18 = sum(fnum(r[v]) for v in (
            "B01001_003E", "B01001_004E", "B01001_005E", "B01001_006E",
            "B01001_027E", "B01001_028E", "B01001_029E", "B01001_030E",
        ))
        vap = max(total_pop - under18, 0)

        age_18_29 = sum(fnum(r[v]) for v in (
            "B01001_007E", "B01001_008E", "B01001_009E", "B01001_010E", "B01001_011E",
            "B01001_031E", "B01001_032E", "B01001_033E", "B01001_034E", "B01001_035E",
        ))
        age_30_44 = sum(fnum(r[v]) for v in (
            "B01001_012E", "B01001_013E", "B01001_014E",
            "B01001_036E", "B01001_037E", "B01001_038E",
        ))
        age_45_64 = sum(fnum(r[v]) for v in (
            "B01001_015E", "B01001_016E", "B01001_017E", "B01001_018E", "B01001_019E",
            "B01001_039E", "B01001_040E", "B01001_041E", "B01001_042E", "B01001_043E",
        ))
        age_65p = sum(fnum(r[v]) for v in (
            "B01001_020E", "B01001_021E", "B01001_022E", "B01001_023E", "B01001_024E", "B01001_025E",
            "B01001_044E", "B01001_045E", "B01001_046E", "B01001_047E", "B01001_048E", "B01001_049E",
        ))

        out.append({
            "district": district,
            "pct_white_nh": round(100 * white_nh / race_total, 2),
            "pct_black": round(100 * black / race_total, 2),
            "pct_hispanic": round(100 * hispanic / race_total, 2),
            "pct_asian": round(100 * asian / race_total, 2),
            "pct_other": round(100 * other / race_total, 2),
            "pct_college": round(100 * college_count / edu_total, 2) if edu_total else 0,
            # Four-cell race-x-edu shares of total adults 25+ (sum to ~100%):
            "pct_white_nh_college":      round(100 * white_nh_college / edu_total, 2) if edu_total else 0,
            "pct_white_nh_non_college":  round(100 * white_nh_non_college / edu_total, 2) if edu_total else 0,
            "pct_nonwhite_college":      round(100 * nonwhite_college / edu_total, 2) if edu_total else 0,
            "pct_nonwhite_non_college":  round(100 * nonwhite_non_college / edu_total, 2) if edu_total else 0,
            "pct_under_30": round(100 * age_18_29 / vap, 2) if vap else 0,
            "pct_30_44":    round(100 * age_30_44 / vap, 2) if vap else 0,
            "pct_45_64":    round(100 * age_45_64 / vap, 2) if vap else 0,
            "pct_65_plus":  round(100 * age_65p / vap, 2) if vap else 0,
            "median_age": fnum(r["B01002_001E"]),
            "median_income": int(fnum(r["B19013_001E"])),
            "total_population": int(total_pop),
            "source": (f"ACS_{ACS_YEAR}_5yr_old_lines" if is_redrawn
                       else f"ACS_{ACS_YEAR}_5yr"),
        })
        if is_redrawn:
            redrawn_count += 1
    print(f"  redrawn-state rows (old-lines estimate): {redrawn_count}", file=sys.stderr)
    print(f"  skipped non-district codes: {skipped_nondistrict}", file=sys.stderr)
    return sorted(out, key=lambda r: r["district"])


def main():
    load_env()
    key = os.environ.get("CENSUS_API_KEY")
    if not key:
        sys.exit("CENSUS_API_KEY not set. Add it to backend/.env or export it.")
    print(f"Fetching ACS {ACS_YEAR} 5-year demographics at CD level...", file=sys.stderr)
    raw = fetch_cd_data(key)
    print(f"  got {len(raw)} raw CD rows", file=sys.stderr)
    rows = normalize(raw)
    print(f"  kept {len(rows)} districts after filtering", file=sys.stderr)

    out_path = Path(__file__).resolve().parent / "demographics_acs.csv"
    cols = ["district", "pct_white_nh", "pct_black", "pct_hispanic", "pct_asian",
            "pct_other", "pct_college",
            "pct_white_nh_college", "pct_white_nh_non_college",
            "pct_nonwhite_college", "pct_nonwhite_non_college",
            "pct_under_30", "pct_30_44", "pct_45_64", "pct_65_plus",
            "median_age", "median_income", "total_population", "source"]
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
