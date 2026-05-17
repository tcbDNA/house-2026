"""Convert Census TIGER county shapefile into per-state GeoJSON files.

Input:  ~/Downloads/cb_2024_us_county_500k.{shp,dbf,shx,prj}
Output: data/county_geojson/<USPS>.geojson  (51 files; one per state + DC)

Each output file is a FeatureCollection of county polygons, with properties:
  - fips: 5-digit county FIPS (state FIPS + county FIPS)
  - state: USPS code (e.g. "MI")
  - name: county name
  - geoidfq: full FIPS reference (useful for joining other Census products)

The shapefile coords are WGS84 (per the .prj — NAD83 GRS80 ellipsoid which is
effectively WGS84 for display purposes), so no reprojection is needed.
"""
import json
import sys
from pathlib import Path
import shapefile

SRC = Path.home() / "Downloads" / "cb_2024_us_county_500k" / "cb_2024_us_county_500k.shp"
OUT_DIR = Path(__file__).resolve().parent / "county_geojson"

# Census state FIPS -> USPS abbreviation
STATE_FIPS = {
    "01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE",
    "11":"DC","12":"FL","13":"GA","15":"HI","16":"ID","17":"IL","18":"IN","19":"IA",
    "20":"KS","21":"KY","22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN",
    "28":"MS","29":"MO","30":"MT","31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM",
    "36":"NY","37":"NC","38":"ND","39":"OH","40":"OK","41":"OR","42":"PA","44":"RI",
    "45":"SC","46":"SD","47":"TN","48":"TX","49":"UT","50":"VT","51":"VA","53":"WA",
    "54":"WV","55":"WI","56":"WY",
}


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC}")
    OUT_DIR.mkdir(exist_ok=True)
    sf = shapefile.Reader(str(SRC))
    fields = [f[0] for f in sf.fields[1:]]   # skip 'DeletionFlag'
    by_state: dict[str, list] = {}

    for shape_rec in sf.iterShapeRecords():
        rec = dict(zip(fields, shape_rec.record))
        state_fips = rec.get("STATEFP")
        usps = STATE_FIPS.get(state_fips)
        if not usps:
            continue   # PR, territories
        county_fips = state_fips + rec.get("COUNTYFP", "")
        # Shapely-free GeoJSON construction: pyshp's __geo_interface__ gives
        # us the geometry as a GeoJSON-compatible dict directly.
        feature = {
            "type": "Feature",
            "properties": {
                "fips": county_fips,
                "state": usps,
                "name": rec.get("NAME", ""),
                "geoidfq": rec.get("GEOIDFQ") or rec.get("GEOID", ""),
            },
            "geometry": shape_rec.shape.__geo_interface__,
        }
        by_state.setdefault(usps, []).append(feature)

    total = 0
    for usps, feats in sorted(by_state.items()):
        out = OUT_DIR / f"{usps}.geojson"
        out.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
        total += len(feats)
        kb = out.stat().st_size // 1024
        print(f"  {usps}: {len(feats):4} counties, {kb:5} KB → {out.name}", file=sys.stderr)
    print(f"\nWrote {len(by_state)} state files, {total} counties total", file=sys.stderr)


if __name__ == "__main__":
    main()
