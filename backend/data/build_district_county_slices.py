"""Aggregate DRA per-state precinct CSVs into (district, county) vote slices.

Output: data/district_county_slices.json
  { "SC-01": [ {"fips": "45013", "name": "Beaufort", "d_2024": ..., "r_2024": ...,
                "total_2024": ..., "margin_2024": ..., "share_of_county_2024": ...,
                "fully_contained": False}, ... ],
    ... }

Phase 3 (precinct-aggregated): replaces Phase 1's area-overlap data for any
district whose state's precinct CSV is present. The endpoint falls back to
area-overlap for states that haven't been processed yet.

Per-state input expected at:  ~/Downloads/{state-lower}-precinct-data/precinct-data.csv
(e.g. ~/Downloads/sc-precinct-data/precinct-data.csv)

DRA CSV columns used:
  GEOID20         census GEOID; first 5 chars = county FIPS
  District        congressional district number (1-N within state)
  E_24_PRES_Dem   D votes (presidential, 2024)
  E_24_PRES_Rep   R votes (presidential, 2024)
  E_24_PRES_Total total votes (presidential, 2024)
"""
from __future__ import annotations
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
OUT = DATA_DIR / "district_county_slices.json"
HOME = Path.home()

# Quick FIPS → county name lookup. Built from county_pres.csv since we already
# have that data; fall back to FIPS string if not found.
def load_county_names() -> dict[str, str]:
    names = {}
    path = DATA_DIR / "county_pres.csv"
    if not path.exists():
        return names
    with path.open() as f:
        for row in csv.DictReader(f):
            fips = (row.get("fips") or "").strip()
            name = (row.get("county") or row.get("name") or "").strip()
            if fips and name:
                # county_pres.csv "county" field may or may not already end
                # in " County"; normalize so the output is consistent.
                if not name.lower().endswith("county"):
                    name = f"{name} County"
                names[fips] = name
    return names

COUNTY_NAMES = load_county_names()


def process_state(state_abbr: str, csv_path: Path) -> dict[str, list[dict]]:
    """Read one state's precinct CSV; return a partial slice mapping keyed
    by `STATE-NN` district code."""
    # First pass: aggregate by (county_fips, district)
    # Also keep county-wide totals so we can compute share_of_county.
    slice_data: dict[tuple[str, int], dict[str, int]] = defaultdict(
        lambda: {"d": 0, "r": 0, "t": 0})
    county_totals: dict[str, dict[str, int]] = defaultdict(
        lambda: {"d": 0, "r": 0, "t": 0})

    with csv_path.open() as f:
        for row in csv.DictReader(f):
            geoid = (row.get("GEOID20") or "").strip()
            if not geoid or not geoid.isdigit() or len(geoid) < 11:
                continue
            county_fips = geoid[:5]
            district_raw = (row.get("District") or "").strip()
            if not district_raw or not district_raw.isdigit():
                continue
            district = int(district_raw)
            d = int(row.get("E_24_PRES_Dem") or 0)
            r = int(row.get("E_24_PRES_Rep") or 0)
            t = int(row.get("E_24_PRES_Total") or 0)
            slice_data[(county_fips, district)]["d"] += d
            slice_data[(county_fips, district)]["r"] += r
            slice_data[(county_fips, district)]["t"] += t
            county_totals[county_fips]["d"] += d
            county_totals[county_fips]["r"] += r
            county_totals[county_fips]["t"] += t

    # Reshape into output format
    out: dict[str, list[dict]] = defaultdict(list)
    for (fips, district), v in slice_data.items():
        county_t = county_totals[fips]["t"]
        share = v["t"] / county_t if county_t > 0 else 0.0
        margin = ((v["d"] - v["r"]) / v["t"] * 100.0) if v["t"] > 0 else 0.0
        d_id = f"{state_abbr}-{district:02d}"
        out[d_id].append({
            "fips": fips,
            "name": COUNTY_NAMES.get(fips, f"FIPS {fips}"),
            "d_2024": v["d"],
            "r_2024": v["r"],
            "total_2024": v["t"],
            "margin_2024": round(margin, 1),
            "share_of_county_2024": round(share, 4),
            "fully_contained": share >= 0.99,
        })

    # Sort each district's counties by share desc so the dashboard shows
    # most-relevant first
    for d_id in out:
        out[d_id].sort(key=lambda x: -x["share_of_county_2024"])

    return dict(out)


def main(argv: list[str]) -> int:
    # Load existing output if present (so partial runs accumulate)
    existing: dict[str, list[dict]] = {}
    if OUT.exists():
        existing = json.loads(OUT.read_text())

    states_to_process = argv[1:] if len(argv) > 1 else ["sc"]
    new_total_pairs = 0
    for state in states_to_process:
        state_abbr = state.upper()
        csv_path = HOME / "Downloads" / f"{state.lower()}-precinct-data" / "precinct-data.csv"
        if not csv_path.exists():
            print(f"  {state_abbr}: missing {csv_path}")
            continue
        result = process_state(state_abbr, csv_path)
        # Replace any existing entries for districts in this state
        for d_id in list(existing.keys()):
            if d_id.startswith(f"{state_abbr}-"):
                del existing[d_id]
        existing.update(result)
        pairs = sum(len(v) for v in result.values())
        new_total_pairs += pairs
        print(f"  {state_abbr}: {len(result)} districts, {pairs} (district,county) pairs")

    OUT.write_text(json.dumps(existing, separators=(",", ":")))
    print(f"\nWrote {OUT}")
    print(f"  total districts covered: {len(existing)}")
    print(f"  pairs added this run:    {new_total_pairs}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
