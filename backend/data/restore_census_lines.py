"""Replace the given states' districts in frontend/public/districts.geojson
with the Census 119th-Congress (2024-lines) shapes, in place, keeping every
other feature and the feature order unchanged.

Use when a mid-decade map spliced in by merge_geojson.py is overturned —
e.g. Missouri's 2025 map, after which the 2024 lines are back in force:

  python3 restore_census_lines.py MO

(Regenerating the whole file with build_geojson.py + merge_geojson.py is not
used here because it doesn't reproduce the committed Louisiana shapes.)
"""
import json
import sys

from build_geojson import OUT, census_features


def main():
    states = {s.upper() for s in sys.argv[1:]}
    if not states:
        sys.exit("usage: restore_census_lines.py ST [ST ...]")
    census = {f["properties"]["district"]: f for f in census_features()
              if f["properties"]["state"] in states}
    fc = json.loads(OUT.read_text())
    replaced = 0
    for i, f in enumerate(fc["features"]):
        d = f["properties"]["district"]
        if f["properties"].get("state") in states:
            fc["features"][i] = census.pop(d)
            replaced += 1
    if census:
        sys.exit(f"Census districts with no existing feature: {sorted(census)}")
    OUT.write_text(json.dumps(fc, separators=(",", ":")))
    print(f"replaced {replaced} features for {sorted(states)} in {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
