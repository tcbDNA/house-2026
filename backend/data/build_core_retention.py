"""Population overlap between each current district and the 2024-lines
(119th Congress) districts, for states whose lines changed for 2026.

Each DRA VTD (data/dra_vtd/, github.com/dra2020/vtd_data) is placed in the
current district (frontend/public/districts.geojson) and in the 2024-lines
district (Census cb_2024_us_cd119_5m, via build_geojson.census_features) that
contains its representative point, weighted by 2020 Census population
(T_20_CENS Total).

Writes data/core_retention.csv, one row per (current district, 2024-lines
district) pair with that pair's share of the current district's population.
load_data.py turns it into the share of a district that is new — overall
(vs. its largest 2024 predecessor) and for the incumbent (vs. the district
they represented in 2024).

Usage: python3 build_core_retention.py [ST ...]
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from shapely.geometry import Point, shape
from shapely.prepared import prep
from shapely.strtree import STRtree

import build_slices_from_github as B
from build_geojson import census_features

DATA_DIR = Path(__file__).resolve().parent
OUT = DATA_DIR / "core_retention.csv"
# States with any district on post-2024 lines (labeled or found via The Downballot).
STATES = ["CA", "TX", "FL", "AL", "LA", "UT", "OH", "NC", "TN"]


def lookup_from(features: list[dict]):
    shapes = [shape(f["geometry"]) for f in features]
    labels = [f["properties"]["district"] for f in features]
    tree, prepared = STRtree(shapes), [prep(s) for s in shapes]

    def lookup(lng: float, lat: float) -> str:
        pt = Point(lng, lat)
        for i in tree.query(pt):
            if prepared[i].contains(pt):
                return labels[i]
        return labels[min(range(len(shapes)), key=lambda i: shapes[i].distance(pt))]
    return lookup


def process(state: str, old_features: list[dict], new_features: list[dict]) -> dict:
    old = lookup_from([f for f in old_features if f["properties"]["state"] == state])
    new = lookup_from([f for f in new_features if f["properties"].get("state") == state])
    gdir = B._latest_versioned_dir(B.VTD_DATA_DIR, f"Geojson_{state}")
    gj = json.loads(next(gdir.glob("*.geojson")).read_text())
    pop = defaultdict(float)
    for feat in gj["features"]:
        p = (feat["properties"].get("datasets") or {}).get("T_20_CENS", {}).get("Total", 0)
        if not p:
            continue
        lng, lat = B.vtd_centroid(feat)
        pop[(new(lng, lat), old(lng, lat))] += p
    return pop


def main():
    states = [s.upper() for s in sys.argv[1:]] or STATES
    old_features = census_features()
    new_features = json.loads(B.DISTRICTS_GJ.read_text())["features"]
    rows = []
    for st in states:
        pop = process(st, old_features, new_features)
        totals = defaultdict(float)
        for (nd, _), p in pop.items():
            totals[nd] += p
        for (nd, od), p in sorted(pop.items()):
            rows.append({"district": nd, "old_district": od, "population": round(p),
                         "share": round(p / totals[nd], 4)})
        print(f"{st}: {len(totals)} districts", file=sys.stderr)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["district", "old_district", "population", "share"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
