"""Build district_county_slices.json from DRA's GitHub-published precinct data.

Per state, expects two extracted directories under ~/Downloads/:
  Election_Data_{STATE}.v07/election_data_{state}.v07.csv
  Geojson_{STATE}.v07/{STATE}_2020_VD_tabblock.vtd.datasets.geojson

For each VTD (≈precinct):
  1. county_fips = GEOID20[:5]  (state+county FIPS per Census)
  2. district    = spatial join: which CD polygon contains the VTD centroid
                   (uses our frontend/public/districts.geojson)
  3. aggregate by (county_fips, district) → sum D / R / Total presidential votes

Usage:
  python data/build_slices_from_github.py GA
  python data/build_slices_from_github.py GA TX FL          # multiple states
  python data/build_slices_from_github.py --all              # every state with files in ~/Downloads
"""
from __future__ import annotations
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from shapely.geometry import shape, Point
from shapely.prepared import prep
from shapely.strtree import STRtree

DATA_DIR = Path(__file__).resolve().parent
OUT = DATA_DIR / "district_county_slices.json"
DISTRICTS_JSON = DATA_DIR / "districts.json"  # for 2020→2024 calibration of fallback states
DISTRICTS_GJ = DATA_DIR.parent.parent / "frontend" / "public" / "districts.geojson"
# Look for downloaded VTD data inside the repo (managed by fetch_dra_github.py).
# Falls back to ~/Downloads/ for backward-compatibility with the earlier
# manual workflow.
VTD_DATA_DIR = DATA_DIR / "dra_vtd"
HOME = Path.home()


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
                if not name.lower().endswith("county"):
                    name = f"{name} County"
                names[fips] = name
    return names

COUNTY_NAMES = load_county_names()


def load_district_shifts() -> dict[str, float]:
    """For each district, compute its 2020→2024 margin shift (from districts.json).
    Used to calibrate slice projections when the precinct CSV only has 2020 PRES."""
    if not DISTRICTS_JSON.exists():
        return {}
    raw = json.loads(DISTRICTS_JSON.read_text())
    out = {}
    for d in raw.get("districts", []):
        did = d.get("district")
        m24 = d.get("margin_2024")
        m20 = d.get("margin_2020")
        if did and m24 is not None and m20 is not None:
            out[did] = m24 - m20
    return out

DISTRICT_SHIFTS = load_district_shifts()


def build_district_lookup(state_abbr: str):
    """Return a callable that maps a (lng, lat) point to a district number
    within the given state. Uses STRtree on prepared geometries for speed."""
    gj = json.loads(DISTRICTS_GJ.read_text())
    state_feats = [f for f in gj["features"]
                   if f["properties"].get("state") == state_abbr.upper()]
    if not state_feats:
        raise RuntimeError(f"no district features for state {state_abbr}")

    shapes = []
    district_codes = []
    for f in state_feats:
        g = shape(f["geometry"])
        shapes.append(g)
        d_code = f["properties"]["district"]  # e.g. "GA-03"
        # Strip "STATE-" prefix → "03" → 3 (or "AL" for at-large)
        suffix = d_code.split("-", 1)[1]
        district_codes.append(suffix)

    tree = STRtree(shapes)
    prepared = [prep(s) for s in shapes]

    def lookup(lng: float, lat: float) -> str | None:
        pt = Point(lng, lat)
        # STRtree returns candidate indices; we then do exact contains test
        for i in tree.query(pt):
            if prepared[i].contains(pt):
                return district_codes[i]
        # Fallback: point on boundary or just-outside (rare)
        # Pick nearest shape
        best, best_d = None, float("inf")
        for i, s in enumerate(shapes):
            d = s.distance(pt)
            if d < best_d:
                best, best_d = i, d
        return district_codes[best] if best is not None else None

    return lookup


def vtd_centroid(feature: dict) -> tuple[float, float]:
    """Prefer the labelx/labely interior point if present (DRA includes it
    as the 'good visual center' which is better than raw centroid for
    multipolygon districts), else compute centroid from geometry."""
    p = feature["properties"]
    lx = p.get("labelx") or p.get("labelX")
    ly = p.get("labely") or p.get("labelY")
    if lx is not None and ly is not None:
        try:
            return float(lx), float(ly)
        except (TypeError, ValueError):
            pass
    g = shape(feature["geometry"])
    c = g.representative_point()  # always inside the polygon (unlike centroid)
    return c.x, c.y


def _latest_versioned_dir(parent: Path, prefix: str) -> Path | None:
    """Find ~/Downloads/{prefix}.v{NN}/ with the highest NN."""
    import re
    cands = [p for p in parent.iterdir()
             if p.is_dir() and p.name.startswith(prefix)]
    if not cands:
        return None
    def version(p: Path) -> int:
        m = re.search(r"\.v(\d+)$", p.name)
        return int(m.group(1)) if m else 0
    return max(cands, key=version)


def process_state(state_abbr: str) -> dict[str, list[dict]]:
    sa = state_abbr.upper()
    # Prefer the in-repo VTD download dir; fall back to ~/Downloads for older runs
    elec_dir = _latest_versioned_dir(VTD_DATA_DIR, f"Election_Data_{sa}") \
        if VTD_DATA_DIR.exists() else None
    gj_dir = _latest_versioned_dir(VTD_DATA_DIR, f"Geojson_{sa}") \
        if VTD_DATA_DIR.exists() else None
    if elec_dir is None:
        elec_dir = _latest_versioned_dir(HOME / "Downloads", f"Election_Data_{sa}")
    if gj_dir is None:
        gj_dir = _latest_versioned_dir(HOME / "Downloads", f"Geojson_{sa}")
    if elec_dir is None or gj_dir is None:
        print(f"  {sa}: missing files (elec_dir={elec_dir}, gj_dir={gj_dir})")
        return {}
    # Find the actual CSV / GeoJSON file inside each versioned dir
    csv_candidates = list(elec_dir.glob(f"election_data_{sa}*.csv"))
    gj_candidates = list(gj_dir.glob(f"{sa}_2020_VD_tabblock.vtd.datasets.geojson"))
    if not csv_candidates or not gj_candidates:
        print(f"  {sa}: dirs found but missing inner files (csv={csv_candidates}, gj={gj_candidates})")
        return {}
    csv_path = csv_candidates[0]
    gj_path = gj_candidates[0]

    # 1. Pull presidential results per GEOID20. Prefer 2024 if present; fall
    # back to 2020 for states where DRA hasn't published 2024 PRES yet
    # (AR, CT, ID, ME, MI, ND, NJ, OK, OR, PA, SD as of this writing).
    pres_by_geoid: dict[str, tuple[int, int, int]] = {}
    pres_year = "2024"
    with csv_path.open() as f:
        rdr = csv.DictReader(f)
        cols = rdr.fieldnames or []
        if "E_24_PRES_Total" in cols:
            d_col, r_col, t_col = "E_24_PRES_Dem", "E_24_PRES_Rep", "E_24_PRES_Total"
        elif "E_20_PRES_Total" in cols:
            d_col, r_col, t_col = "E_20_PRES_Dem", "E_20_PRES_Rep", "E_20_PRES_Total"
            pres_year = "2020"
        else:
            print(f"  {sa}: no E_24_PRES_Total nor E_20_PRES_Total columns — skipping")
            return {}
        for row in rdr:
            g = (row.get("GEOID20") or "").strip()
            if not g:
                continue
            d = int(row.get(d_col) or 0)
            r = int(row.get(r_col) or 0)
            t = int(row.get(t_col) or 0)
            pres_by_geoid[g] = (d, r, t)
    print(f"  {sa}: {len(pres_by_geoid)} VTDs with {pres_year} PRES results")

    # 2. Pull VTD geometries and assign each to a district via centroid lookup
    lookup = build_district_lookup(sa)
    gj = json.loads(gj_path.read_text())
    vtd_to_district: dict[str, str] = {}
    unassigned = 0
    for feat in gj["features"]:
        # GEOID20 may be in 'id' (per README) or 'GEOID20' (per CSV column)
        p = feat["properties"]
        gid = (p.get("id") or p.get("GEOID20") or "").strip()
        if not gid:
            continue
        try:
            lng, lat = vtd_centroid(feat)
        except Exception:
            unassigned += 1
            continue
        d = lookup(lng, lat)
        if d is None:
            unassigned += 1
            continue
        vtd_to_district[gid] = d
    print(f"  {sa}: assigned {len(vtd_to_district)} VTDs to CDs ({unassigned} unassigned)")

    # 3. Aggregate by (county_fips, district)
    slice_data: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"d": 0, "r": 0, "t": 0})
    county_totals: dict[str, dict[str, int]] = defaultdict(
        lambda: {"d": 0, "r": 0, "t": 0})
    for gid, (d, r, t) in pres_by_geoid.items():
        if t == 0:
            continue
        district = vtd_to_district.get(gid)
        if district is None:
            continue
        county_fips = gid[:5]
        slice_data[(county_fips, district)]["d"] += d
        slice_data[(county_fips, district)]["r"] += r
        slice_data[(county_fips, district)]["t"] += t
        county_totals[county_fips]["d"] += d
        county_totals[county_fips]["r"] += r
        county_totals[county_fips]["t"] += t

    # 4. Format output. For fallback (2020) states, calibrate each slice's
    # margin to estimated 2024 by adding the district-level 2020→2024 shift.
    # Slice's relative pattern (which slices are D-leaning vs R-leaning within
    # the district) is preserved; only the absolute baseline is shifted.
    out: dict[str, list[dict]] = defaultdict(list)
    for (fips, district), v in slice_data.items():
        county_t = county_totals[fips]["t"]
        share = v["t"] / county_t if county_t > 0 else 0.0
        raw_margin = ((v["d"] - v["r"]) / v["t"] * 100.0) if v["t"] > 0 else 0.0
        d_id = f"{sa}-{district}"  # e.g. "GA-03", "AK-AL"
        if pres_year == "2020":
            shift = DISTRICT_SHIFTS.get(d_id, 0.0)
            adjusted_margin = raw_margin + shift
        else:
            adjusted_margin = raw_margin
        out[d_id].append({
            "fips": fips,
            "name": COUNTY_NAMES.get(fips, f"FIPS {fips}"),
            "d_2024": v["d"],
            "r_2024": v["r"],
            "total_2024": v["t"],
            "margin_2024": round(adjusted_margin, 1),
            "share_of_county_2024": round(share, 4),
            "fully_contained": share >= 0.99,
            "pres_year_source": int(pres_year),  # 2020 (fallback) or 2024
        })
    for d_id in out:
        out[d_id].sort(key=lambda x: -x["share_of_county_2024"])
    return dict(out)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__); return 1
    args = argv[1:]
    if args == ["--all"]:
        # Discover states with both election + geojson dirs present (any version).
        # Prefer in-repo dir, fall back to ~/Downloads.
        import re
        search_dirs = []
        if VTD_DATA_DIR.exists():
            search_dirs.append(VTD_DATA_DIR)
        search_dirs.append(HOME / "Downloads")
        states = set()
        ver_re = re.compile(r"^Election_Data_([A-Z]{2})\.v\d+$")
        for d in search_dirs:
            if not d.exists(): continue
            for p in d.iterdir():
                if not p.is_dir(): continue
                m = ver_re.match(p.name)
                if not m: continue
                sa = m.group(1)
                gj_match = any(q.is_dir() and q.name.startswith(f"Geojson_{sa}.v")
                               for q in d.iterdir())
                if gj_match:
                    states.add(sa)
        args = sorted(states)
        print(f"Discovered states: {', '.join(args)}\n")

    existing: dict[str, list[dict]] = {}
    if OUT.exists():
        existing = json.loads(OUT.read_text())

    new_total_pairs = 0
    for state in args:
        result = process_state(state)
        if not result:
            continue
        sa = state.upper()
        for d_id in list(existing.keys()):
            if d_id.startswith(f"{sa}-"):
                del existing[d_id]
        existing.update(result)
        pairs = sum(len(v) for v in result.values())
        new_total_pairs += pairs
        print(f"  {sa}: {len(result)} districts, {pairs} (district,county) pairs added")

    OUT.write_text(json.dumps(existing, separators=(",", ":")))
    print(f"\nWrote {OUT}")
    print(f"  total districts covered: {len(existing)}")
    print(f"  pairs added this run:    {new_total_pairs}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
