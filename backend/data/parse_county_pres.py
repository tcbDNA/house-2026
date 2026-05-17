"""Parse Dropbox county CSV into county_pres.csv. State code comes from the
X.4 column when present; falls back to deriving from the FIPS prefix so
counties created after 1980 (Broomfield CO, etc.) aren't dropped."""
import csv

SRC = "/Users/tcb_dna/Downloads/data-lzWxy.csv"
OUT = "/Users/tcb_dna/projects/house_2026/backend/data/county_pres.csv"

# Source-CSV bug: 2020 vote counts for these three Louisiana parishes are
# rotated among themselves (Lafayette's row has LaSalle's 2020 numbers, etc.).
# Override with the correct per-county 2020 totals (LA SOS / Wikipedia).
LA_2020_FIX = {
    "22055": {"biden": 39685, "trump": 72519, "total": 113398},  # Lafayette Parish
    "22057": {"biden": 8672,  "trump": 36024, "total": 45098},   # Lafourche Parish
    "22059": {"biden": 638,   "trump": 6378,  "total": 7077},    # LaSalle Parish
}

# State FIPS -> USPS
STATE_FIPS = {
    "01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE",
    "11":"DC","12":"FL","13":"GA","15":"HI","16":"ID","17":"IL","18":"IN","19":"IA",
    "20":"KS","21":"KY","22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN",
    "28":"MS","29":"MO","30":"MT","31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM",
    "36":"NY","37":"NC","38":"ND","39":"OH","40":"OK","41":"OR","42":"PA","44":"RI",
    "45":"SC","46":"SD","47":"TN","48":"TX","49":"UT","50":"VT","51":"VA","53":"WA",
    "54":"WV","55":"WI","56":"WY",
}


def num(s):
    if s is None or s == "": return None
    s = s.replace(",", "").rstrip("%").strip()
    try: return float(s)
    except: return None


def main():
    rows = []
    skipped_missing_pres = 0
    skipped_bad_state = 0
    with open(SRC, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            fips_raw = (r.get("X.2") or "").strip()
            if not fips_raw or not fips_raw.isdigit():
                continue
            fips = fips_raw.zfill(5)
            # Prefer X.4 (state USPS); fall back to FIPS prefix lookup.
            state = (r.get("X.4") or "").strip()
            if len(state) != 2:
                state = STATE_FIPS.get(fips[:2], "")
            if len(state) != 2:
                skipped_bad_state += 1
                continue

            harris = num(r.get("Harris"));   trump   = num(r.get("Trump"))
            biden  = num(r.get("Biden"));    trump20 = num(r.get("Trump1"))
            total20 = num(r.get("Total1"))
            if harris is None or trump is None or biden is None or trump20 is None:
                skipped_missing_pres += 1
                continue
            if (harris + trump) == 0 or (biden + trump20) == 0:
                continue

            # Apply per-FIPS overrides for known source-CSV bugs.
            fix = LA_2020_FIX.get(fips)
            if fix:
                biden, trump20, total20 = fix["biden"], fix["trump"], fix["total"]

            m24 = round(100 * (harris - trump) / (harris + trump), 2)
            m20 = round(100 * (biden - trump20) / (biden + trump20), 2)
            rows.append({
                "fips": fips, "state": state, "name": (r.get("NAME") or "").strip(),
                "harris_2024": int(harris), "trump_2024": int(trump),
                "total_2024": int(num(r.get("Total")) or 0),
                "biden_2020": int(biden), "trump_2020": int(trump20),
                "total_2020": int(total20 or 0),
                "margin_2024": m24, "margin_2020": m20,
                "pct_white_2020":    num(r.get("WHITE2020%")),
                "pct_black_2020":    num(r.get("BLACK2020%")),
                "pct_hispanic_2020": num(r.get("HISPANIC2020%")),
                "pct_asian_2020":    num(r.get("ASIAN2020%")),
            })

    print(f"parsed {len(rows)} counties across {len(set(r['state'] for r in rows))} states")
    if skipped_missing_pres:
        print(f"  skipped {skipped_missing_pres} rows missing presidential data")
    if skipped_bad_state:
        print(f"  skipped {skipped_bad_state} rows with no usable state code")
    # Spot-check Broomfield
    bf = next((r for r in rows if r["fips"] == "08014"), None)
    if bf:
        print(f"  Broomfield CO: margin_2024={bf['margin_2024']}, total={bf['total_2024']}")

    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
