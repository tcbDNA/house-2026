"""Merge county pres + ACS demographics into counties.json.

Output schema mirrors districts.json's row format so county_model.py can reuse
the same projection formula (margin_2024 + uniform_swing + rel_trend × discount
+ demographic_shift). county_trend = (margin_2024 - margin_2020) - national
presidential shift, analogous to state_trend.
"""
import csv, json, sys
from pathlib import Path

DATA = Path(__file__).resolve().parent

# 2020 -> 2024 national presidential shift (D-R margin change at the popvote
# level). Biden +4.5 → Harris -1.5 → shift of -6.0. Matches senate_data.py.
NATIONAL_PRES_SHIFT = -6.0

NUMERIC_DEMOS = [
    "pct_white_nh","pct_black","pct_hispanic","pct_asian","pct_other",
    "pct_college",
    "pct_white_nh_college","pct_white_nh_non_college",
    "pct_nonwhite_college","pct_nonwhite_non_college",
    "pct_under_30","pct_30_44","pct_45_64","pct_65_plus",
    "median_age","median_income","total_population",
]


def to_num(s):
    if s is None or s == "": return None
    try: return float(s)
    except: return None


def main():
    pres = {r["fips"]: r for r in csv.DictReader((DATA / "county_pres.csv").open())}
    demos = {r["fips"]: r for r in csv.DictReader((DATA / "demographics_acs_counties.csv").open())}

    counties = []
    missing_pres = missing_demo = 0
    for fips, d in demos.items():
        p = pres.get(fips)
        if p is None:
            missing_pres += 1
            continue
        margin_2024 = to_num(p["margin_2024"])
        margin_2020 = to_num(p["margin_2020"])
        county_trend = round((margin_2024 - margin_2020) - NATIONAL_PRES_SHIFT, 2)
        row = {
            "fips": fips,
            "state": d["state"],
            "name": d["name"],
            "margin_2024": margin_2024,
            "margin_2020": margin_2020,
            "rel_trend": county_trend,   # named to match model.py expectations
            "total_2024": int(p["total_2024"]),
            "total_2020": int(p["total_2020"]),
        }
        for k in NUMERIC_DEMOS:
            row[k] = to_num(d.get(k))
        row["demo_source"] = d.get("source", "")
        counties.append(row)

    # Any pres rows without ACS demos
    have_demos = set(demos)
    for fips in pres:
        if fips not in have_demos:
            missing_demo += 1

    out = DATA / "counties.json"
    out.write_text(json.dumps({"counties": counties}, indent=None))
    print(f"Wrote {out} ({out.stat().st_size//1024} KB)", file=sys.stderr)
    print(f"  counties: {len(counties)}", file=sys.stderr)
    print(f"  missing pres results (skipped): {missing_pres}", file=sys.stderr)
    print(f"  pres rows without ACS demos: {missing_demo}", file=sys.stderr)


if __name__ == "__main__":
    main()
