"""Replace Connecticut's old-county rows in county_pres.csv with planning regions.

Since 2022 the Census Bureau uses Connecticut's nine planning regions as county
equivalents (FIPS 09110-09190): the ACS county demographics and the county map
shapes use them, while the results file parse_county_pres.py reads still
reports the eight old counties (09001-09015), so build_counties.py found no
Connecticut county with both results and demographics. Towns nest within both,
so this script sums the Secretary of the State's official town-level results
(2020 and 2024) into planning regions with the Census town crosswalk. As a
check, it sums the same towns into the old counties and compares them with the
rows being replaced.

Sources and URLs: sources/ct_planning_regions/README.md.
Run AFTER parse_county_pres.py whenever county_pres.csv is regenerated, then
build_counties.py.
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parent
SRC = DATA / "sources" / "ct_planning_regions"
OUT = DATA / "county_pres.csv"


def town_crosswalk() -> dict[str, dict]:
    """Town name -> crosswalk row (old county FIPS, planning region FIPS and name)."""
    rows = list(csv.reader((SRC / "census_ct_cou_to_cousub_crosswalk.txt").open(encoding="utf-8-sig"),
                           delimiter="|"))
    hdr = [h.split("\n")[0] for h in rows[0]]
    out = {}
    for r in rows[1:]:
        if len(r) != len(hdr):
            continue
        rec = dict(zip(hdr, r))
        if rec["COUSUB_NAMELSAD"].endswith(" town"):
            out[rec["COUSUB_NAMELSAD"][:-len(" town")]] = rec
    assert len(out) == 169, len(out)
    return out


def town_results(path: Path) -> dict[str, tuple[int, int, int]]:
    """Town -> (Democratic, Republican, total votes cast); checks the towns sum to the state row."""
    rows = list(csv.reader(path.open(encoding="utf-8-sig")))
    hdr, party = rows[0], rows[1]
    di, ri, ti = party.index("Democratic"), party.index("Republican"), hdr.index("Total Votes Cast")
    towns = {r[1]: (int(r[di]), int(r[ri]), int(r[ti])) for r in rows if r[0] == "City/Town"}
    state = next(r for r in rows if r[0] == "State")
    sums = tuple(sum(v[k] for v in towns.values()) for k in range(3))
    assert len(towns) == 169 and sums == (int(state[di]), int(state[ri]), int(state[ti])), (path, sums)
    return towns


def main():
    xw = town_crosswalk()
    res = {2024: town_results(SRC / "ct_sots_2024_president_by_town.csv"),
           2020: town_results(SRC / "ct_sots_2020_president_by_town.csv")}
    for y, towns in res.items():
        missing = set(towns) ^ set(xw)
        assert not missing, (y, sorted(missing))

    def aggregate(key: str) -> dict[str, dict[int, list[int]]]:
        agg: dict[str, dict[int, list[int]]] = defaultdict(lambda: {2024: [0, 0, 0], 2020: [0, 0, 0]})
        for town, rec in xw.items():
            for y in (2024, 2020):
                for k in range(3):
                    agg["09" + rec[key]][y][k] += res[y][town][k]
        return agg

    with OUT.open() as f:
        rdr = csv.DictReader(f)
        fields = rdr.fieldnames
        rows = list(rdr)
    old = {r["fips"]: r for r in rows if r["state"] == "CT"}

    # Check: towns summed into the old counties vs the rows being replaced.
    print("Old-county check (official town sums vs county_pres.csv), D / R / total:")
    for fips, v in sorted(aggregate("OLD_COUNTYFP").items()):
        r = old.get(fips)
        if r is None:
            print(f"  {fips}: no old row")
            continue
        d = [v[2024][0] - int(r["harris_2024"]), v[2024][1] - int(r["trump_2024"]), v[2024][2] - int(r["total_2024"]),
             v[2020][0] - int(r["biden_2020"]), v[2020][1] - int(r["trump_2020"]), v[2020][2] - int(r["total_2020"])]
        print(f"  {fips} {r['name']:18} 2024 diff {d[0]:+6} {d[1]:+6} {d[2]:+6} | 2020 diff {d[3]:+6} {d[4]:+6} {d[5]:+6}")

    names = {"09" + rec["NEW_COUNTYFP"]: rec["NEW_COUNTY_NAMELSAD"] for rec in xw.values()}
    new_rows = []
    for fips, v in sorted(aggregate("NEW_COUNTYFP").items()):
        (d24, r24, t24), (d20, r20, t20) = v[2024], v[2020]
        new_rows.append({k: "" for k in fields} | {
            "fips": fips, "state": "CT", "name": names[fips],
            "harris_2024": d24, "trump_2024": r24, "total_2024": t24,
            "biden_2020": d20, "trump_2020": r20, "total_2020": t20,
            # two-party, like parse_county_pres.py (build_counties.py recomputes total-vote margins)
            "margin_2024": round(100 * (d24 - r24) / (d24 + r24), 2),
            "margin_2020": round(100 * (d20 - r20) / (d20 + r20), 2),
        })
    rows = [r for r in rows if r["state"] != "CT"] + new_rows
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Replaced {len(old)} old CT county rows with {len(new_rows)} planning regions in {OUT.name}:")
    for r in new_rows:
        tv24 = 100 * (r["harris_2024"] - r["trump_2024"]) / r["total_2024"]
        tv20 = 100 * (r["biden_2020"] - r["trump_2020"]) / r["total_2020"]
        print(f"  {r['fips']} {r['name']:48} 2024 {tv24:+6.1f} (total {r['total_2024']:,})  2020 {tv20:+6.1f}")


if __name__ == "__main__":
    main()
