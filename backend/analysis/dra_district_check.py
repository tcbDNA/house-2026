"""Exact 2020 and 2024 presidential results on the current district lines,
from Dave's Redistricting precinct (VTD) data (github.com/dra2020/vtd_data,
cached under data/dra_vtd/ by data/fetch_dra_github.py).

Each VTD is assigned to the current district containing its representative
point (same assignment as data/build_slices_from_github.py), and its
E_20_PRES / E_24_PRES votes are summed per district. Margins are
(D − R) / Total × 100, matching national_sensitivity_v20.csv.

Writes:
  analysis/dra_district_check.csv                     per-district comparison
  data/sources/dra_vtd_pres/vtd_pres_<ST>.csv.gz      trimmed per-VTD extract
      (current district, 2024-lines district, 2020 Census population, and
      2020/2024 presidential votes — enough to reproduce this check and
      data/core_retention.csv without the ~1 GB raw DRA download)

Usage (from backend/): python3 analysis/dra_district_check.py [ST ...]
"""
from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND / "data"))
import build_slices_from_github as B  # noqa: E402
from build_core_retention import lookup_from  # noqa: E402
from build_geojson import census_features  # noqa: E402

ROOT = BACKEND.parent
OUT = BACKEND / "analysis" / "dra_district_check.csv"
EXTRACT_DIR = BACKEND / "data" / "sources" / "dra_vtd_pres"
# States with districts on post-2024 lines (labeled or not), plus MO to check
# which map its district polygons reflect.
STATES = ["CA", "TX", "FL", "AL", "LA", "UT", "OH", "NC", "TN", "MO"]


def margin(d: int, r: int, t: int) -> float | None:
    return 100.0 * (d - r) / t if t else None


def process(state: str, old_features: list[dict]) -> dict[str, dict]:
    edir = B._latest_versioned_dir(B.VTD_DATA_DIR, f"Election_Data_{state}")
    gdir = B._latest_versioned_dir(B.VTD_DATA_DIR, f"Geojson_{state}")
    votes = {}
    with next(edir.glob("*.csv")).open() as f:
        for row in csv.DictReader(f):
            g = (row.get("GEOID20") or "").strip()
            if g:
                votes[g] = tuple(int(row.get(k) or 0) for k in (
                    "E_20_PRES_Dem", "E_20_PRES_Rep", "E_20_PRES_Total",
                    "E_24_PRES_Dem", "E_24_PRES_Rep", "E_24_PRES_Total"))
    lookup = B.build_district_lookup(state)
    old_lookup = lookup_from([f for f in old_features if f["properties"]["state"] == state])
    gj = json.loads(next(gdir.glob("*.geojson")).read_text())
    sums = defaultdict(lambda: [0] * 6)
    extract = []
    unassigned = 0
    for feat in gj["features"]:
        p = feat["properties"]
        gid = (p.get("id") or p.get("GEOID20") or "").strip()
        if gid not in votes:
            continue
        lng, lat = B.vtd_centroid(feat)
        num = lookup(lng, lat)   # district suffix, e.g. "03" or "AL"
        if num is None:
            unassigned += 1
            continue
        dist = f"{state}-{num}"
        v = votes[gid]
        for i in range(6):
            sums[dist][i] += v[i]
        pop = (p.get("datasets") or {}).get("T_20_CENS", {}).get("Total", 0)
        extract.append((gid, dist, old_lookup(lng, lat), pop, *v))
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with gzip.open(EXTRACT_DIR / f"vtd_pres_{state}.csv.gz", "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["GEOID20", "district", "district_2024_lines", "pop_2020_census",
                    "E_20_PRES_Dem", "E_20_PRES_Rep", "E_20_PRES_Total",
                    "E_24_PRES_Dem", "E_24_PRES_Rep", "E_24_PRES_Total"])
        w.writerows(extract)
    print(f"{state}: {len(extract)} VTDs assigned, {unassigned} unassigned "
          f"(source dirs {edir.name}, {gdir.name})", file=sys.stderr)
    return {d: {"dra_m20": margin(s[0], s[1], s[2]), "dra_m24": margin(s[3], s[4], s[5]),
                "dra_t20": s[2], "dra_t24": s[5]} for d, s in sums.items()}


def main():
    states = sys.argv[1:] or STATES
    v20 = {r["district"]: r for r in csv.DictReader(open(ROOT / "national_sensitivity_v20.csv"))}
    db = {r["district"]: r for r in csv.DictReader(open(BACKEND / "analysis" / "v20_vs_downballot.csv"))}
    rows = []
    old_features = census_features()
    for st in states:
        for d, x in sorted(process(st, old_features).items()):
            r = v20[d]
            rows.append({
                "district": d, "v20_lines": r["lines"],
                "v20_m24": float(r["margin_2024"]), "db_m24": float(db[d]["db_margin_2024"]),
                "dra_m24": round(x["dra_m24"], 2) if x["dra_m24"] is not None else "",
                "v20_m20": float(r["margin_2020"]),
                "dra_m20": round(x["dra_m20"], 2) if x["dra_m20"] is not None else "",
                "gap20_v20_minus_dra": round(float(r["margin_2020"]) - x["dra_m20"], 2) if x["dra_m20"] is not None else "",
                "gap24_v20_minus_dra": round(float(r["margin_2024"]) - x["dra_m24"], 2) if x["dra_m24"] is not None else "",
                "dra_total_2020": x["dra_t20"], "dra_total_2024": x["dra_t24"],
            })
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} districts)", file=sys.stderr)


if __name__ == "__main__":
    main()
