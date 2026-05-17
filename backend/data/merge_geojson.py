"""Splice DRA-exported per-state plan GeoJSONs into districts.geojson,
replacing the Census 119th-Congress shapes for the 7 redrawn states.

Inputs (any subset, in this directory):
  geojson_ca.geojson  geojson_tx.geojson  geojson_oh.geojson  geojson_nc.geojson
  geojson_tn.geojson  geojson_mo.geojson  geojson_ut.geojson

Re-writes frontend/public/districts.geojson in place.
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
GEOJSON_PATH = DATA_DIR.parent.parent / "frontend" / "public" / "districts.geojson"

REDRAWN_STATES = ["CA", "TX", "OH", "NC", "TN", "MO", "UT", "FL", "LA", "AL"]
AT_LARGE = {"AK", "DE", "ND", "SD", "VT", "WY"}

COORD_PRECISION = 5

# Property names DRA / others might use for the district number
DISTRICT_KEYS = ("District", "district", "DISTRICT", "CD", "cd",
                 "DISTRICTID", "districtId", "district_id", "DISTRICT_ID",
                 "name", "Name", "NAME")


def pick_district_id(props: dict) -> str | None:
    for k in DISTRICT_KEYS:
        if k in props and props[k] not in (None, ""):
            return str(props[k])
    return None


def label_for(state: str, raw: str) -> str | None:
    """Normalize DRA's per-state district id to the v18 label
    (e.g. '1' -> 'TX-01', 'AL' -> 'WY-AL' for at-large states)."""
    raw = raw.strip()
    if state in AT_LARGE:
        return f"{state}-AL"
    # If DRA already gave 'TX-01' or similar, accept directly
    if "-" in raw and raw.startswith(state + "-"):
        return raw
    # Strip any state prefix DRA might add ('TX 1', 'TX1')
    cleaned = raw.replace(state, "").strip(" -_")
    try:
        return f"{state}-{int(cleaned):02d}"
    except ValueError:
        return None


def round_coords(coords, geom_type):
    p = COORD_PRECISION
    if geom_type == "Polygon":
        return [[[round(x, p), round(y, p)] for x, y in ring] for ring in coords]
    if geom_type == "MultiPolygon":
        return [[[[round(x, p), round(y, p)] for x, y in ring] for ring in poly]
                for poly in coords]
    return coords


def load_state_features(state: str) -> list[dict] | None:
    path = DATA_DIR / f"geojson_{state.lower()}.geojson"
    if not path.exists():
        return None
    fc = json.loads(path.read_text())
    if fc.get("type") != "FeatureCollection":
        sys.exit(f"{path}: not a FeatureCollection")

    out = []
    skipped = 0
    seen_labels = set()
    for feat in fc["features"]:
        props = feat.get("properties") or {}
        raw_id = pick_district_id(props)
        if raw_id is None:
            skipped += 1
            continue
        label = label_for(state, raw_id)
        if label is None:
            print(f"  [{state}] couldn't parse district id from {raw_id!r}", file=sys.stderr)
            skipped += 1
            continue
        if label in seen_labels:
            print(f"  [{state}] duplicate label {label}; ignoring later occurrence", file=sys.stderr)
            continue
        seen_labels.add(label)

        geom = feat.get("geometry") or {}
        if geom.get("type") in ("Polygon", "MultiPolygon"):
            # cast tuples to lists, round precision
            if geom["type"] == "Polygon":
                geom["coordinates"] = [list(map(list, ring)) for ring in geom["coordinates"]]
            else:
                geom["coordinates"] = [
                    [list(map(list, ring)) for ring in poly] for poly in geom["coordinates"]
                ]
            geom["coordinates"] = round_coords(geom["coordinates"], geom["type"])
        out.append({
            "type": "Feature",
            "id": label,
            "properties": {"district": label, "state": state},
            "geometry": geom,
        })
    print(f"  [{state}] loaded {len(out)} features, skipped {skipped}", file=sys.stderr)
    return out


def main():
    targets = REDRAWN_STATES
    if len(sys.argv) > 1:
        targets = [s.upper() for s in sys.argv[1:]]

    if not GEOJSON_PATH.exists():
        sys.exit(f"missing {GEOJSON_PATH}. Run build_geojson.py first.")
    fc = json.loads(GEOJSON_PATH.read_text())

    replacements: dict[str, list[dict]] = {}
    missing_states = []
    for state in targets:
        feats = load_state_features(state)
        if feats is None:
            missing_states.append(state)
            continue
        replacements[state] = feats

    if not replacements:
        sys.exit("no geojson_*.geojson files found. Nothing to merge.")

    # Keep features whose state is NOT being replaced
    kept = [f for f in fc["features"] if f["properties"].get("state") not in replacements]
    # Append new features
    for state, feats in replacements.items():
        kept.extend(feats)

    fc["features"] = kept
    GEOJSON_PATH.write_text(json.dumps(fc, separators=(",", ":")))
    size_mb = GEOJSON_PATH.stat().st_size / 1024 / 1024
    print(f"\nWrote {GEOJSON_PATH} ({size_mb:.2f} MB, {len(kept)} features)", file=sys.stderr)
    if missing_states:
        print(f"  skipped (no geojson_*.geojson uploaded): {missing_states}", file=sys.stderr)

    # Quick sanity: confirm we still have 435
    label_set = {f["properties"]["district"] for f in kept}
    print(f"  unique district labels: {len(label_set)}", file=sys.stderr)
    if len(label_set) != 435:
        print(f"  WARNING: expected 435, got {len(label_set)}", file=sys.stderr)


if __name__ == "__main__":
    main()
