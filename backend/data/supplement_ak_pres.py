"""Append Alaska borough/CA pres results to county_pres.csv.

The source CSV used by parse_county_pres.py doesn't have Alaska (the state
doesn't officially report pres by borough). This script supplements with:
  - 2024: actual harris/trump vote counts from Wikipedia
  - 2020: D-margins from Dave's Redistricting (per-borough), with vote totals
    proxied by 2024 totals (we don't have 2020 turnout per borough)

Run this AFTER parse_county_pres.py whenever county_pres.csv is regenerated.
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "county_pres.csv"

# (fips, name, harris24, trump24, others24, margin_2020_DRA)
AK_DATA = [
    ("02013", "Aleutians East Borough",       125,   288, 19,  -26.10),
    ("02016", "Aleutians West Census Area",   474,   469, 28,   +9.30),
    ("02020", "Anchorage Municipality",     64781, 62925, 5193, +2.20),
    ("02050", "Bethel Census Area",          2181,  1622, 466, +28.20),
    ("02060", "Bristol Bay Borough",          139,   254, 19,  -21.70),
    ("02063", "Chugach Census Area",         1246,  1807, 134,  -8.40),
    ("02066", "Copper River Census Area",     359,   995, 75,  -36.10),
    ("02068", "Denali Borough",               484,   754, 53,   -4.50),
    ("02070", "Dillingham Census Area",       670,   763, 72,   +6.40),
    ("02090", "Fairbanks North Star Borough",17037, 24857, 1791, -14.60),
    ("02100", "Haines Borough",               908,   791, 95,  +15.60),
    ("02105", "Hoonah-Angoon Census Area",    876,   548, 91,  +37.00),
    ("02110", "Juneau City and Borough",    10305,  5942, 730, +25.80),
    ("02122", "Kenai Peninsula Borough",    10347, 21861, 1168, -31.60),
    ("02130", "Ketchikan Gateway Borough",   2496,  3738, 267, -16.50),
    ("02150", "Kodiak Island Borough",       2469,  3547, 250, -21.70),
    ("02158", "Kusilvak Census Area",         820,   579, 171, +33.60),
    ("02164", "Lake and Peninsula Borough",   175,   230, 0,  +19.25),
    ("02170", "Matanuska-Susitna Borough",  13343, 40140, 1882, -48.30),
    ("02180", "Nome Census Area",            1424,  1167, 202, +22.60),
    ("02185", "North Slope Borough",          690,   939, 101,  -3.70),
    ("02188", "Northwest Arctic Borough",     648,   713, 140, +16.60),
    ("02195", "Petersburg Borough",           640,   970, 88,  -20.90),
    ("02198", "Prince of Wales-Hyder Census Area", 1588, 1735, 168, -7.30),
    ("02220", "Sitka City and Borough",      2057,  1659, 149, +17.60),
    ("02230", "Skagway Municipality",         717,   265, 52,  +48.50),
    ("02240", "Southeast Fairbanks Census Area", 528, 2846, 101, -57.20),
    ("02275", "Wrangell City and Borough",    359,   745, 32,  -29.60),
    ("02282", "Yakutat City and Borough",     271,   179, 21,  +14.10),
    ("02290", "Yukon-Koyukuk Census Area",   1386,   851, 140, +21.80),
]


def main():
    with OUT.open() as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [r for r in reader if not r[0].startswith("02")]

    for fips, name, harris, trump, others, m2020 in AK_DATA:
        total_2024 = harris + trump + others
        margin_2024 = round((harris - trump) / total_2024 * 100, 2)
        # Reverse-derive 2020 vote counts from DRA margin × proxied total
        total_2020 = total_2024  # AK doesn't publish 2020 by borough; use 2024 as proxy
        biden_2020 = round(total_2020 * (100 + m2020) / 200)
        trump_2020 = total_2020 - biden_2020
        rows.append([
            fips, "AK", name,
            str(harris), str(trump), str(total_2024),
            str(biden_2020), str(trump_2020), str(total_2020),
            f"{margin_2024}", f"{m2020}",
            "", "", "", "",
        ])

    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"appended {len(AK_DATA)} AK borough rows to {OUT}")


if __name__ == "__main__":
    main()
