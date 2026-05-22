"""One-time precompute: for each congressional district, find counties that
touch the district polygon and the fraction of each county's area that lies
inside the district.

Output: data/district_counties.json
  { "AZ-06": [ {"fips": "04013", "name": "Maricopa County",
                "overlap_fraction": 0.42, "fully_contained": False}, ... ],
    ... }

Phase 1 approach (per docs): use raw area overlap. This is fine for rural
districts that wholly contain counties, but for urban splits the area
fraction overstates rural / understates urban political weight. The UI
should label any county with overlap_fraction < 0.99 as "partial".
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict

from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.prepared import prep
from shapely.validation import make_valid

DATA_DIR = Path(__file__).resolve().parent
DISTRICTS_GJ = DATA_DIR.parent.parent / "frontend" / "public" / "districts.geojson"
COUNTY_GJ_DIR = DATA_DIR / "county_geojson"
OUT = DATA_DIR / "district_counties.json"

# A county is "fully contained" if at least this fraction of its area is in
# the district. Allows for tiny boundary-line slivers from polygon imprecision.
FULL_THRESHOLD = 0.99
# Don't emit pairs with less than this overlap — likely boundary noise.
MIN_OVERLAP = 0.005  # 0.5%


def _safe_shape(feature):
    g = shape(feature["geometry"])
    if not g.is_valid:
        g = make_valid(g)
    return g


def main():
    districts = json.loads(DISTRICTS_GJ.read_text())
    # Group districts by state for efficiency
    state_districts: dict[str, list[tuple[str, object]]] = defaultdict(list)
    for f in districts["features"]:
        d_id = f["properties"]["district"]
        state = f["properties"]["state"]
        state_districts[state].append((d_id, _safe_shape(f)))

    out: dict[str, list[dict]] = {}
    total_pairs = 0
    states_done = 0
    for state, dists in sorted(state_districts.items()):
        county_path = COUNTY_GJ_DIR / f"{state}.geojson"
        if not county_path.exists():
            print(f"  {state}: no county geojson — skipping")
            continue
        counties = json.loads(county_path.read_text())
        # Pre-shape counties once
        county_shapes = []
        for cf in counties["features"]:
            props = cf["properties"]
            # Common Census Tiger field names; try a few
            fips = (props.get("GEOID") or props.get("GEOID20")
                    or props.get("fips") or props.get("FIPS")
                    or props.get("COUNTYFP"))
            name = (props.get("NAME") or props.get("NAMELSAD")
                    or props.get("name") or "unknown")
            geom = _safe_shape(cf)
            county_shapes.append((fips, name, geom, geom.area))

        for d_id, d_geom in dists:
            d_prep = prep(d_geom)
            entries = []
            for fips, name, c_geom, c_area in county_shapes:
                if not d_prep.intersects(c_geom):
                    continue
                if d_prep.contains(c_geom):
                    overlap = 1.0
                else:
                    inter = d_geom.intersection(c_geom)
                    overlap = inter.area / c_area if c_area > 0 else 0.0
                if overlap < MIN_OVERLAP:
                    continue
                entries.append({
                    "fips": fips,
                    "name": name,
                    "overlap_fraction": round(overlap, 4),
                    "fully_contained": overlap >= FULL_THRESHOLD,
                })
            # Sort by overlap fraction desc so the dashboard shows
            # most-relevant counties first
            entries.sort(key=lambda e: -e["overlap_fraction"])
            out[d_id] = entries
            total_pairs += len(entries)
        states_done += 1
        print(f"  {state}: {len(dists)} districts, "
              f"{sum(len(out[d]) for d, _ in dists)} (district,county) pairs")

    OUT.write_text(json.dumps(out, separators=(",", ":")))
    print(f"\nWrote {OUT}")
    print(f"  states covered:        {states_done}")
    print(f"  districts with counties: {len(out)}")
    print(f"  total (district,county) pairs: {total_pairs}")


if __name__ == "__main__":
    main()
