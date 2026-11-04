"""Alaska's 40 state house districts as county-map units (setting
ak_house_district_map): ak_house_districts.json, in counties.json's row
format, and county_geojson/AK_house.geojson.

Alaska reports results by house district, not borough; the borough rows in
counties.json carry estimated results. Here:
  2024 presidential votes  the Division of Elections' 2024 general results by
                           precinct (sources/ak_house_districts/ENRbyPrecinct_24GENR.csv),
                           summed by the district number that begins each precinct
                           name, each district's Absentee, Early Voting and Question
                           rows included; the federal-only overseas ballots ("HD99 Fed
                           Overseas Absentee") have no district and are left out
  2020 presidential votes  DRA's 2020 VTD results (dra_vtd/Election_Data_AK.v07), each
                           VTD's votes split among the current districts by its 2020
                           Census population in each: blocks to VTDs by the Census 2020
                           block assignment file, blocks to districts by their interior
                           points in the Census TIGER/Line districts (tl_2024_02_sldl;
                           blocks nest in them). Printed beside the totals with each
                           VTD wholly in the district holding its label point, as
                           build_slices_from_github.py assigns VTDs elsewhere.
  boundaries (map)         Census cartographic boundary file cb_2024_02_sldl_500k
  demographics             ACS 5-year by state legislative district (lower chamber),
                           2020-2024 and, as demo_acs2023, 2019-2023, with
                           fetch_acs_counties.normalize's definitions
Also writes sources/ak_house_districts/dra_vtd_2020_pres_by_hd.csv (each VTD's
pieces by district: 2020 population, share, 2020 votes). The 2020 block file
(130 MB) is read from data/cache/tl_2020_02_tabblock20/ (gitignored; URL in
sources/ak_house_districts/README.md).

usage: python data/build_ak_house_districts.py [--fetch-acs]
  --fetch-acs: first refresh the saved ACS responses from the Census API
  (needs CENSUS_API_KEY)
"""
import csv, io, json, os, re, sys, zipfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import shapefile
from shapely.geometry import Point, shape
from shapely.prepared import prep
from shapely.strtree import STRtree

from build_counties import NATIONAL_PRES_SHIFT, NUMERIC_DEMOS
from build_slices_from_github import vtd_centroid
from fetch_acs import VARS_A, VARS_B, load_env
from fetch_acs_counties import normalize

DATA = Path(__file__).resolve().parent
SRC = DATA / "sources" / "ak_house_districts"
ENR = SRC / "ENRbyPrecinct_24GENR.csv"
MAP_ZIP = SRC / "cb_2024_02_sldl_500k.zip"      # drawn: clipped to the shoreline
TIGER_ZIP = SRC / "tl_2024_02_sldl.zip"         # blocks and VTDs to districts
BAF_ZIP = SRC / "BlockAssign_ST02_AK.zip"       # 2020 blocks to VTDs
BLOCKS_ZIP = DATA / "cache" / "tl_2020_02_tabblock20" / "tl_2020_02_tabblock20.zip"
DRA_CSV = DATA / "dra_vtd" / "Election_Data_AK.v07" / "election_data_AK.v07.csv"
DRA_GJ = DATA / "dra_vtd" / "Geojson_AK.v07" / "AK_2020_VD_tabblock.vtd.datasets.geojson"
ACS_YEARS = ("2024", "2023")
GEO = "state legislative district (lower chamber)"
OUT_JSON = DATA / "ak_house_districts.json"
OUT_GJ = DATA / "county_geojson" / "AK_house.geojson"
OUT_VTD = SRC / "dra_vtd_2020_pres_by_hd.csv"


def hd_id(n: int) -> str:
    return f"02HD{n:02d}"


def acs_path(year: str, part: str) -> Path:
    return SRC / f"acs5_{year}_sldl_AK_{part}.json"


def fetch_acs():
    load_env()
    key = os.environ.get("CENSUS_API_KEY")
    if not key:
        sys.exit("CENSUS_API_KEY not set")
    for year in ACS_YEARS:
        for part, vars_list in (("A", VARS_A), ("B", VARS_B)):
            params = {"get": ",".join(["NAME"] + vars_list), "for": f"{GEO}:*", "in": "state:02"}
            with urlopen(f"https://api.census.gov/data/{year}/acs/acs5?{urlencode(params | {'key': key})}",
                         timeout=120) as r:
                acs_path(year, part).write_bytes(r.read())
            print(f"saved {acs_path(year, part).name}", file=sys.stderr)


def acs_rows(year: str) -> dict[str, dict]:
    """district id -> normalized ACS row (the county definitions; the district's
    code stands in for the county code)."""
    parts = []
    for part in ("A", "B"):
        data = json.loads(acs_path(year, part).read_text())
        parts.append({r[GEO]: r for r in (dict(zip(data[0], row)) for row in data[1:])})
    raw = [{**a, **{k: v for k, v in parts[1][code].items() if k in VARS_B}, "county": code}
           for code, a in parts[0].items() if code != "ZZZ"]
    return {hd_id(int(r["fips"][2:])): r for r in normalize(raw)}


def results_2024() -> tuple[dict[int, dict], int]:
    """district -> 2024 D, R and total presidential votes; the votes with no district"""
    out = defaultdict(lambda: {"dem": 0, "rep": 0, "total": 0})
    no_district = 0
    with ENR.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["Contest_title"] != "U.S. President / Vice President":
                continue
            if r["Precinct_name"].startswith("HD99 "):
                no_district += int(r["total_votes"])
                continue
            m = re.match(r"(\d\d)-\d{3} ", r["Precinct_name"]) or re.match(r"District (\d+)\s+- ", r["Precinct_name"])
            if not m:
                sys.exit(f"precinct name without a district: {r['Precinct_name']!r}")
            d = out[int(m.group(1))]
            v = int(r["total_votes"])
            d["total"] += v
            if r["Party_Code"] == "DEM": d["dem"] += v
            if r["Party_Code"] == "REP": d["rep"] += v
    return dict(out), no_district


def districts_geo(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as z:
        stem = path.stem
        sf = shapefile.Reader(shp=io.BytesIO(z.read(f"{stem}.shp")), shx=io.BytesIO(z.read(f"{stem}.shx")),
                              dbf=io.BytesIO(z.read(f"{stem}.dbf")))
        fields = [f[0] for f in sf.fields[1:]]
        feats = []
        for sr in sf.iterShapeRecords():
            rec = dict(zip(fields, sr.record))
            if rec["SLDLST"] == "ZZZ":
                continue
            n = int(rec["SLDLST"])
            feats.append({"type": "Feature",
                          "properties": {"fips": hd_id(n), "state": "AK", "name": f"House District {n}",
                                         "geoidfq": rec.get("GEOIDFQ") or rec.get("GEOID", "")},
                          "geometry": sr.shape.__geo_interface__})
    return sorted(feats, key=lambda f: f["properties"]["fips"])


def block_districts(tiger: list[dict]) -> tuple[dict[str, str], dict[str, int]]:
    """2020 block -> current district (the one holding the block's interior
    point; blocks nest in the districts), and its 2020 population"""
    with zipfile.ZipFile(BLOCKS_ZIP) as z:
        sf = shapefile.Reader(dbf=io.BytesIO(z.read("tl_2020_02_tabblock20.dbf")))
        fields = [f[0] for f in sf.fields[1:]]
        recs = [dict(zip(fields, r)) for r in sf.iterRecords()]
    polys = [shape(f["geometry"]) for f in tiger]
    tree = STRtree(polys)
    pts = [Point(float(r["INTPTLON20"]), float(r["INTPTLAT20"])) for r in recs]
    hd = {}
    for p_i, d_i in zip(*tree.query(pts, predicate="within")):
        hd[recs[p_i]["GEOID20"]] = tiger[d_i]["properties"]["fips"]
    for k, r in enumerate(recs):          # interior point on a boundary or offshore
        if r["GEOID20"] not in hd:
            hd[r["GEOID20"]] = tiger[int(tree.query_nearest(pts[k])[0])]["properties"]["fips"]
    return hd, {r["GEOID20"]: int(r["POP20"]) for r in recs}


def results_2020(tiger: list[dict]) -> tuple[dict[str, dict], list[dict], dict]:
    """district -> 2020 D, R and total presidential votes: each DRA VTD's votes
    split among the current districts by its 2020 Census population in each
    (blocks to VTDs by the Census 2020 block assignment file); a VTD with no
    population goes to the district holding its label point. Also the per-VTD
    pieces, and the label-point-only totals for comparison."""
    hd, pop = block_districts(tiger)
    with zipfile.ZipFile(BAF_ZIP) as z:
        lines = z.read("BlockAssign_ST02_AK_VTD.txt").decode().splitlines()
    vtd_pop = defaultdict(lambda: defaultdict(int))
    for line in lines[1:]:
        block, county, vtd = line.split("|")
        vtd_pop[f"02{county}{vtd}"][hd[block]] += pop[block]
    polys = [prep(shape(f["geometry"])) for f in tiger]
    votes = {r["GEOID20"]: r for r in csv.DictReader(DRA_CSV.open(encoding="utf-8-sig"))}
    label = {}
    for f in json.loads(DRA_GJ.read_text())["features"]:
        pt = Point(*vtd_centroid(f))
        label[f["properties"]["id"]] = next((tiger[k]["properties"]["fips"] for k, p in enumerate(polys)
                                             if p.contains(pt)), None)
    out = defaultdict(lambda: {"dem": 0.0, "rep": 0.0, "total": 0.0})
    by_label = defaultdict(lambda: {"dem": 0, "rep": 0, "total": 0})
    pieces = []
    for gid, v in votes.items():
        d, r, t = (int(float(v[f"E_20_PRES_{k}"])) for k in ("Dem", "Rep", "Total"))
        if label.get(gid) is None:
            sys.exit(f"DRA VTD {gid} has no label point in a district")
        L = by_label[label[gid]]
        L["dem"] += d; L["rep"] += r; L["total"] += t
        ps = vtd_pop.get(gid, {})
        n = sum(ps.values())
        shares = {k: x / n for k, x in ps.items() if x} if n else {label[gid]: 1.0}
        for k, s in sorted(shares.items()):
            o = out[k]
            o["dem"] += d * s; o["rep"] += r * s; o["total"] += t * s
            pieces.append({"GEOID20": gid, "name": v["Name"], "house_district": int(k[4:]),
                           "pop_2020": ps.get(k, 0), "share": round(s, 4),
                           "pres20_dem": round(d * s, 2), "pres20_rep": round(r * s, 2), "pres20_total": round(t * s, 2)})
    return dict(out), pieces, dict(by_label)


def margin(x: dict) -> float:
    return round(100.0 * (x["dem"] - x["rep"]) / x["total"], 2)


def main():
    if "--fetch-acs" in sys.argv:
        fetch_acs()
    feats, tiger = districts_geo(MAP_ZIP), districts_geo(TIGER_ZIP)
    assert len(feats) == len(tiger) == 40, (len(feats), len(tiger))
    r24, no_district = results_2024()
    r20, pieces, by_label = results_2020(tiger)
    acs, acs23 = acs_rows("2024"), acs_rows("2023")
    rows = []
    for f in feats:
        fid, n = f["properties"]["fips"], int(f["properties"]["fips"][4:])
        a, b = r24[n], r20[fid]
        m24, m20 = margin(a), margin(b)
        row = {"fips": fid, "state": "AK", "name": f["properties"]["name"],
               "margin_2024": m24, "margin_2020": m20,
               "rel_trend": round((m24 - m20) - NATIONAL_PRES_SHIFT, 2),
               "total_2024": a["total"], "total_2020": round(b["total"]),
               "dem_2024": a["dem"], "rep_2024": a["rep"]}
        row |= {k: acs[fid][k] for k in NUMERIC_DEMOS}
        row["demo_source"] = acs[fid]["source"]
        row["demo_acs2023"] = {k: acs23[fid][k] for k in NUMERIC_DEMOS}
        rows.append(row)
    OUT_JSON.write_text(json.dumps({"counties": rows}, indent=None))
    OUT_GJ.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
    with OUT_VTD.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pieces[0]))
        w.writeheader(); w.writerows(pieces)

    tot = lambda rr, k: sum(x[k] for x in rr.values())
    print(f"2024: {tot(r24, 'total'):,} presidential votes in {len(r24)} districts "
          f"(D {tot(r24, 'dem'):,}, R {tot(r24, 'rep'):,}); {no_district:,} federal-only overseas votes left out")
    print(f"2020 (DRA VTDs): {tot(r20, 'total'):,.0f} votes in {len(r20)} districts "
          f"(D {tot(r20, 'dem'):,.0f}, R {tot(r20, 'rep'):,.0f})")
    vt = defaultdict(float)
    for x in pieces:
        vt[x["GEOID20"]] = max(vt[x["GEOID20"]], x["share"])
    split = {g for g, s in vt.items() if s < 0.95}
    sv = sum(x["pres20_total"] for x in pieces if x["GEOID20"] in split)
    print(f"VTDs with >5% of their 2020 population outside their largest district: {len(split)} of {len(vt)}, "
          f"{sv:,.0f} of the 2020 votes ({100 * sv / tot(r20, 'total'):.1f}%)")
    moved = sum(abs(r20[k]["total"] - by_label[k]["total"]) for k in r20) / 2
    gaps = sorted(((abs(margin(r20[k]) - margin(by_label[k])), k) for k in r20), reverse=True)
    print(f"vs each VTD wholly in its label point's district: {moved:,.0f} votes in other districts; "
          f"2020 margin differs by more than 1 point in {sum(g > 1 for g, _ in gaps)} districts "
          f"(largest {gaps[0][0]:.1f}, {gaps[0][1]})")
    print(f"wrote {OUT_JSON.name} ({len(rows)} districts), {OUT_GJ.name} "
          f"({OUT_GJ.stat().st_size // 1024} KB), {OUT_VTD.name}")


if __name__ == "__main__":
    main()
