"""Build district_county_slices.json from DRA's GitHub-published precinct data.

Per state, expects two extracted directories under ~/Downloads/:
  Election_Data_{STATE}.v07/election_data_{state}.v07.csv
  Geojson_{STATE}.v07/{STATE}_2020_VD_tabblock.vtd.datasets.geojson

For each VTD (≈precinct):
  1. county_fips = GEOID20[:5]  (state+county FIPS per Census); Connecticut's
     VTDs carry the old county codes, so they are moved by town into the
     planning regions the Census has used as county equivalents since 2022
  2. district    = spatial join: which CD polygon contains the VTD centroid
                   (uses our frontend/public/districts.geojson)
  3. aggregate by (county_fips, district) → sum D / R / Total presidential votes

States whose file has no 2024 presidential results (AK AR CT ID ME MI ND NJ
OK OR PA SD) get 2024 estimates: D and R raked from each slice's 2020
votes to the official 2024 county totals (county_pres.csv) and The
Downballot's 2024 district totals (sources/downballot_2024_pres_by_cd/),
other votes split within each county by 2020 shares (rake_state). The
earlier estimate — 2020 margin + the district's 2020→2024 shift, 2020
totals — is kept in each slice's district_shift_estimate (setting
overlay_raked_slices off), and total_2020 keeps the 2020 votes the model's
district weights used there before Oct 27 (model.district_turnout, setting
district_weights_2024_votes off).

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
COUNTIES_JSON = DATA_DIR / "counties.json"  # for real county-level m24/m20 (fallback override)
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
                if not name.lower().endswith(("county", "planning region")):
                    name = f"{name} County"
                names[fips] = name
    return names

COUNTY_NAMES = load_county_names()

CT_CROSSWALK = DATA_DIR / "sources" / "ct_planning_regions" / "census_ct_cou_to_cousub_crosswalk.txt"


def ct_town_regions() -> dict[str, str]:
    """Connecticut town name -> planning-region FIPS (Census county-subdivision
    crosswalk). DRA's 2020 VTD GEOIDs use the eight old counties; the ACS,
    the county shapes and counties.json use the nine planning regions."""
    rows = list(csv.reader(CT_CROSSWALK.open(encoding="utf-8-sig"), delimiter="|"))
    hdr = [h.split("\n")[0] for h in rows[0]]
    out = {}
    for r in rows[1:]:
        rec = dict(zip(hdr, r)) if len(r) == len(hdr) else {}
        if rec.get("COUSUB_NAMELSAD", "").endswith(" town"):
            out[rec["COUSUB_NAMELSAD"][:-len(" town")]] = "09" + rec["NEW_COUNTYFP"]
    return out


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


def load_county_margins() -> dict[str, tuple[float, float]]:
    """county FIPS → (margin_2024, margin_2020) from counties.json. Used to
    override fallback-state slices that are wholly contained in one district —
    we already have the county's real 2024 margin in counties.json, no need
    to synthesize from 2020 + district shift."""
    if not COUNTIES_JSON.exists():
        return {}
    raw = json.loads(COUNTIES_JSON.read_text())
    out = {}
    for c in raw.get("counties", []):
        fips = c.get("fips")
        m24 = c.get("margin_2024")
        m20 = c.get("margin_2020")
        if fips and m24 is not None and m20 is not None:
            out[fips] = (m24, m20)
    return out

COUNTY_MARGINS = load_county_margins()

COUNTY_PRES = DATA_DIR / "county_pres.csv"
DOWNBALLOT_XLSX = DATA_DIR / "sources" / "downballot_2024_pres_by_cd" / "downballot_presbycd_current_lines.xlsx"


def load_county_votes_2024() -> dict[str, tuple[float, float, float]]:
    """county FIPS → official 2024 (Harris, Trump, other) votes from
    county_pres.csv. Targets for raking the fallback states' slices."""
    out = {}
    with COUNTY_PRES.open() as f:
        for r in csv.DictReader(f):
            d, rep, t = (float(r[k]) for k in ("harris_2024", "trump_2024", "total_2024"))
            out[r["fips"]] = (d, rep, t - d - rep)
    return out


def load_district_votes_2024() -> dict[str, tuple[float, float, float]]:
    """district → The Downballot's 2024 (Harris, Trump, other) votes on the
    current lines ('Vote totals' sheet). Targets for raking the fallback
    states' slices."""
    from xlsx_table import read_sheet
    out = {}
    for r in read_sheet(DOWNBALLOT_XLSX, "Vote totals"):
        if len(r) > 6 and "-" in r[0] and r[0][:2].isalpha() and r[4]:
            d, rep, t = float(r[4]), float(r[5]), float(r[6])
            out[r[0]] = (d, rep, t - d - rep)
    return out

COUNTY_VOTES_2024 = load_county_votes_2024()
DISTRICT_VOTES_2024 = load_district_votes_2024()


def rake(seed: dict[tuple, float], row_target: dict, col_target: dict,
         tol: float = 1e-10, max_iter: int = 10_000) -> tuple[dict[tuple, float], int, float]:
    """Iterative proportional fitting: scale the cells {(row, col): seed}
    until every row sums to its row target and every column to its column
    target (the two sets of targets must have the same grand total).
    Returns (cells, iterations, largest relative row error)."""
    cells = dict(seed)
    for it in range(1, max_iter + 1):
        for axis, target in ((0, row_target), (1, col_target)):
            sums: dict = defaultdict(float)
            for k, v in cells.items():
                sums[k[axis]] += v
            cells = {k: v * target[k[axis]] / sums[k[axis]] if sums[k[axis]] > 0 else 0.0
                     for k, v in cells.items()}
        sums = defaultdict(float)
        for k, v in cells.items():
            sums[k[0]] += v
        err = max(abs(sums[r] - t) / t for r, t in row_target.items() if t > 0)
        if err < tol:
            break
    return cells, it, err


def rake_state(sa: str, slice_data: dict) -> dict[tuple[str, str], list[float]]:
    """(county FIPS, district) → estimated 2024 (D, R, other) votes for a
    state without 2024 precinct results. Each slice starts from its 2020
    precinct votes; D and R are raked, one party at a time, to the official
    2024 county totals and The Downballot's 2024 district totals (scaled
    within the state to the counties' sum, since the two sources count a
    few votes differently). Other votes follow the county's 2024 total,
    split by the slices' 2020 shares (the sources' other-vote counts differ
    by up to a third, mostly write-ins). A county wholly inside one district
    is a single cell, so it gets its real result."""
    keys = list(slice_data)
    rows = {f for f, _ in keys}
    cols = {d for _, d in keys}
    out: dict[tuple[str, str], list[float]] = {k: [0.0, 0.0, 0.0] for k in keys}
    for p, (name, key) in enumerate((("D", "d20"), ("R", "r20"))):
        seed = {k: float(slice_data[k][key]) for k in keys}
        row_t = {f: COUNTY_VOTES_2024[f][p] for f in rows}
        col_raw = {d: DISTRICT_VOTES_2024[f"{sa}-{d}"][p] for d in cols}
        scale = sum(row_t.values()) / sum(col_raw.values())
        col_t = {d: v * scale for d, v in col_raw.items()}
        cells, it, err = rake(seed, row_t, col_t)
        print(f"  {sa}: raked {name} votes in {it} iterations (largest county error {err:.1e}; "
              f"district totals scaled by {scale:.4f})")
        for k, v in cells.items():
            out[k][p] = v
    other20 = {k: float(slice_data[k]["t20"] - slice_data[k]["d20"] - slice_data[k]["r20"]) for k in keys}
    county_other20: dict = defaultdict(float)
    for (f, _), v in other20.items():
        county_other20[f] += v
    for k in keys:
        out[k][2] = COUNTY_VOTES_2024[k[0]][2] * other20[k] / county_other20[k[0]] if county_other20[k[0]] else 0.0
    return out


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

    # 1. Pull presidential results per GEOID20. Prefer 2024 if present and
    # ALSO pull 2020 (used for per-slice rel_trend if both available).
    # For fallback states without 2024 PRES, calibrate to 2024 later via the
    # district-level 2020→2024 shift.
    pres24_by_geoid: dict[str, tuple[int, int, int]] = {}
    pres20_by_geoid: dict[str, tuple[int, int, int]] = {}
    # VTD GEOID -> county FIPS where it isn't GEOID20[:5] (Connecticut: by the
    # town in the VTD's name, e.g. "Waterford 002-00").
    county_of: dict[str, str] = {}
    town_regions = ct_town_regions() if sa == "CT" else {}
    with csv_path.open() as f:
        rdr = csv.DictReader(f)
        cols = rdr.fieldnames or []
        has_24 = "E_24_PRES_Total" in cols
        has_20 = "E_20_PRES_Total" in cols
        if not has_24 and not has_20:
            print(f"  {sa}: no E_24_PRES_Total nor E_20_PRES_Total columns — skipping")
            return {}
        for row in rdr:
            g = (row.get("GEOID20") or "").strip()
            if not g:
                continue
            if town_regions:
                town = (row.get("Name") or "").rsplit(" ", 1)[0]
                county_of[g] = town_regions[town]
            if has_24:
                d24 = int(row.get("E_24_PRES_Dem") or 0)
                r24 = int(row.get("E_24_PRES_Rep") or 0)
                t24 = int(row.get("E_24_PRES_Total") or 0)
                pres24_by_geoid[g] = (d24, r24, t24)
            if has_20:
                d20 = int(row.get("E_20_PRES_Dem") or 0)
                r20 = int(row.get("E_20_PRES_Rep") or 0)
                t20 = int(row.get("E_20_PRES_Total") or 0)
                pres20_by_geoid[g] = (d20, r20, t20)
    pres_year = "2024" if has_24 else "2020"
    # `primary` is what drives the base slice margin (will be calibrated for
    # fallback states); `pres24` and `pres20` are the underlying raw data.
    pres_by_geoid = pres24_by_geoid if has_24 else pres20_by_geoid
    print(f"  {sa}: {len(pres_by_geoid)} VTDs ({'2024+2020' if has_24 and has_20 else pres_year} PRES results)")

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

    # 3. Aggregate by (county_fips, district) — tracks both years separately
    slice_data: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"d24": 0, "r24": 0, "t24": 0, "d20": 0, "r20": 0, "t20": 0})
    county_totals: dict[str, dict[str, int]] = defaultdict(
        lambda: {"d24": 0, "r24": 0, "t24": 0, "d20": 0, "r20": 0, "t20": 0})
    for gid in pres_by_geoid:
        district = vtd_to_district.get(gid)
        if district is None:
            continue
        county_fips = county_of.get(gid, gid[:5])
        if gid in pres24_by_geoid:
            d, r, t = pres24_by_geoid[gid]
            slice_data[(county_fips, district)]["d24"] += d
            slice_data[(county_fips, district)]["r24"] += r
            slice_data[(county_fips, district)]["t24"] += t
            county_totals[county_fips]["d24"] += d
            county_totals[county_fips]["r24"] += r
            county_totals[county_fips]["t24"] += t
        if gid in pres20_by_geoid:
            d, r, t = pres20_by_geoid[gid]
            slice_data[(county_fips, district)]["d20"] += d
            slice_data[(county_fips, district)]["r20"] += r
            slice_data[(county_fips, district)]["t20"] += t
            county_totals[county_fips]["d20"] += d
            county_totals[county_fips]["r20"] += r
            county_totals[county_fips]["t20"] += t

    # 4. Format output. For fallback (2020-only) states, calibrate each slice's
    # margin to estimated 2024 by adding the district-level 2020→2024 shift
    # (kept as district_shift_estimate), and rake the slices to the 2024
    # county and district totals (the slice's main fields).
    raked = rake_state(sa, slice_data) if not has_24 else {}
    out: dict[str, list[dict]] = defaultdict(list)
    for (fips, district), v in slice_data.items():
        # Use whichever year has data as the "primary" turnout / share denominator
        primary_t = v["t24"] if v["t24"] > 0 else v["t20"]
        if primary_t == 0:
            continue
        county_primary_t = (county_totals[fips]["t24"]
                            if v["t24"] > 0 else county_totals[fips]["t20"])
        share = primary_t / county_primary_t if county_primary_t > 0 else 0.0
        # 2024 margin (raw, calibrated, or — for fallback wholly-contained slices —
        # overridden with the real county-level 2024 margin from counties.json).
        whole_county_fallback = (v["t24"] == 0 and share >= 0.99
                                 and fips in COUNTY_MARGINS)
        if v["t24"] > 0:
            adjusted_m24 = (v["d24"] - v["r24"]) / v["t24"] * 100.0
        elif whole_county_fallback:
            # Use county-level real 2024 margin — slice IS the whole county
            adjusted_m24 = COUNTY_MARGINS[fips][0]
        else:
            # 2020-only data + partial county: estimate via district shift
            raw_m20 = (v["d20"] - v["r20"]) / v["t20"] * 100.0
            d_id_full = f"{sa}-{district}"
            adjusted_m24 = raw_m20 + DISTRICT_SHIFTS.get(d_id_full, 0.0)
        # 2020 margin — prefer real county-level when slice is whole county,
        # else use precinct-aggregated 2020 if available.
        if whole_county_fallback:
            m20 = COUNTY_MARGINS[fips][1]
        elif v["t20"] > 0:
            m20 = (v["d20"] - v["r20"]) / v["t20"] * 100.0
        else:
            m20 = None
        d_id = f"{sa}-{district}"
        row = {
            "fips": fips,
            "name": COUNTY_NAMES.get(fips, f"FIPS {fips}"),
            "d_2024": v["d24"] or v["d20"],
            "r_2024": v["r24"] or v["r20"],
            "total_2024": primary_t,
            "margin_2024": round(adjusted_m24, 1),
            "margin_2020": round(m20, 1) if m20 is not None else None,
            "share_of_county_2024": round(share, 4),
            "fully_contained": share >= 0.99,
            "pres_year_source": int(pres_year),
        }
        if raked:
            estimate_keys = ("d_2024", "r_2024", "total_2024", "margin_2024",
                             "share_of_county_2024", "fully_contained")
            shift_estimate = {k: row[k] for k in estimate_keys}
            d24, r24, o24 = raked[(fips, district)]
            t24 = d24 + r24 + o24
            share24 = t24 / sum(COUNTY_VOTES_2024[fips])
            row.update({"d_2024": round(d24), "r_2024": round(r24), "total_2024": round(t24),
                        "margin_2024": round(100.0 * (d24 - r24) / t24, 1),
                        "share_of_county_2024": round(share24, 4), "fully_contained": share24 >= 0.99,
                        "total_2020": v["t20"], "district_shift_estimate": shift_estimate})
        out[d_id].append(row)
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
