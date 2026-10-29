"""Aggregate DRA block-level demographics to district level using a
user-provided Block Assignment File (BAF) for each redrawn state.

Inputs (per state):
  baf_{state_lower}.csv  -- DRA Block Assignment File. Two columns
                            (header optional): BLOCKID (15-digit GEOID20)
                            and DISTRICT (integer 1..N). Common header
                            variants accepted.
  Block demographic ZIP  -- downloaded automatically from data.dra2020.net,
                            cached in cache/ inside this directory.

Output: demographics_dra.csv (all redrawn districts combined)

Race basis: V_20_VAP_NH_* (clean Hispanic-aware partition on voting-age
population). Differs slightly from Path A (ACS total-pop basis); the
small definitional gap doesn't affect the model meaningfully.
"""

import csv
import io
import re
import sys
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

DATA_DIR = Path(__file__).resolve().parent
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

DRA_BLOCK_URL = "https://data.dra2020.net/file/dra-block-data/Demographic_Data_Block_{state}.v06.zip"

REDRAWN_STATES = ["CA", "TX", "OH", "NC", "MO", "UT", "TN", "FL", "LA", "AL"]

AT_LARGE = {"AK", "DE", "ND", "SD", "VT", "WY"}  # none redrawn, but kept for safety

# States whose block assignment is an official file saved under sources/
# instead of a local baf_{state}.csv. Louisiana: the Legislature's block
# equivalency file for Act 2 of the 2026 R.S. (SB 121), the enacted map
# (Oct 29). The earlier local baf_la.csv was a different plan (New Orleans in
# District 6), so Louisiana's demographics didn't match its election results.
OFFICIAL_BAF = {
    "LA": DATA_DIR / "sources" / "la_congress_act2_2026" / "block_equivalency_act2_2026rs_congress.txt",
}


def read_official_baf(state: str) -> dict[str, int]:
    """{GEOID20 -> district} from an OFFICIAL_BAF file (two whitespace-separated
    columns, no header)."""
    out = {}
    for line in OFFICIAL_BAF[state].read_text().splitlines():
        if line.strip():
            geoid, district = line.split()
            out[geoid] = int(district)
    return out


def fill_from_block_groups(baf: dict[str, int], block_ids) -> int:
    """The Legislature's file uses its own blocks (2020 Census blocks split or
    merged to follow later precinct changes), so some 2020 blocks are missing
    from it. Give each missing block its block group's district when every
    listed block in that block group is in one district; blocks in split block
    groups stay unassigned. Returns the number of blocks filled."""
    groups: dict[str, set[int]] = {}
    for geoid, d in baf.items():
        groups.setdefault(geoid[:12], set()).add(d)
    filled = 0
    for geoid in block_ids:
        if geoid not in baf and len(groups.get(geoid[:12], ())) == 1:
            baf[geoid] = next(iter(groups[geoid[:12]]))
            filled += 1
    return filled


def merge_rows(path: Path, new_rows: list[dict], states: list[str]) -> list[dict]:
    """Rows for `path` with the given states' rows replaced by `new_rows` and
    every other state's existing rows kept, in the file's existing order."""
    if not path.exists():
        return new_rows
    by_state: dict[str, list[dict]] = {}
    for r in new_rows:
        by_state.setdefault(r["district"].split("-")[0], []).append(r)
    out, done = [], set()
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            st = r["district"].split("-")[0]
            if st not in states:
                out.append(r)
            elif st not in done:
                out.extend(by_state.get(st, []))
                done.add(st)
    for st in states:
        if st not in done:
            out.extend(by_state.get(st, []))
    return out


def download_block_zip(state: str) -> Path:
    out = CACHE_DIR / f"block_{state}.zip"
    if out.exists() and out.stat().st_size > 1000:
        return out
    url = DRA_BLOCK_URL.format(state=state)
    print(f"  downloading {url} ...", file=sys.stderr)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 house-2026-scenario-tool"})
    with urlopen(req, timeout=300) as r:
        out.write_bytes(r.read())
    return out


def load_baf(state: str) -> dict[str, int]:
    """Return {GEOID20 -> district_num} from baf_{state}.csv (or the state's
    OFFICIAL_BAF file)."""
    if state in OFFICIAL_BAF:
        return read_official_baf(state)
    path = DATA_DIR / f"baf_{state.lower()}.csv"
    if not path.exists():
        raise FileNotFoundError(f"missing {path.name} (DRA Block Assignment File)")

    with path.open(newline="") as f:
        # Sniff header
        first = f.readline()
        f.seek(0)
        has_header = bool(re.search(r"[a-zA-Z]", first.split(",")[0]))
        reader = csv.reader(f)
        rows = list(reader)

    header_aliases = {
        "geoid": "blockid", "geoid20": "blockid", "geoid_20": "blockid",
        "blockid": "blockid", "block_id": "blockid", "block": "blockid",
        "district": "district", "district_id": "district",
        "districtid": "district", "cd": "district",
    }
    block_col = dist_col = None
    if has_header:
        header = [h.strip().lower() for h in rows[0]]
        for i, h in enumerate(header):
            tgt = header_aliases.get(h)
            if tgt == "blockid": block_col = i
            elif tgt == "district": dist_col = i
        if block_col is None or dist_col is None:
            # Fallback: assume first two columns
            block_col, dist_col = 0, 1
        data_rows = rows[1:]
    else:
        block_col, dist_col = 0, 1
        data_rows = rows

    assignment = {}
    for r in data_rows:
        if len(r) <= max(block_col, dist_col):
            continue
        bid = r[block_col].strip().lstrip("'")  # DRA sometimes prefixes with '
        d_raw = r[dist_col].strip()
        if not bid or not d_raw:
            continue
        try:
            d = int(d_raw)
        except ValueError:
            continue
        if d <= 0:
            continue  # unassigned blocks
        assignment[bid] = d
    return assignment


def aggregate_state(state: str) -> list[dict]:
    print(f"\n== {state} ==", file=sys.stderr)
    baf = load_baf(state)
    print(f"  BAF: {len(baf)} block assignments", file=sys.stderr)

    zip_path = download_block_zip(state)
    with zipfile.ZipFile(zip_path) as z:
        csv_name = next(n for n in z.namelist() if n.endswith(".csv"))
        if state in OFFICIAL_BAF:
            with z.open(csv_name) as fbin:
                ids = [r["GEOID"] for r in csv.DictReader(io.TextIOWrapper(fbin, encoding="utf-8"))]
            n = fill_from_block_groups(baf, ids)
            print(f"  filled {n:,} 2020 blocks from their block group", file=sys.stderr)
        with z.open(csv_name) as fbin:
            reader = csv.DictReader(io.TextIOWrapper(fbin, encoding="utf-8"))
            fields = [
                "V_20_VAP_NH_Total", "V_20_VAP_NH_White", "V_20_VAP_NH_Hispanic",
                "V_20_VAP_NH_BlackAlone", "V_20_VAP_NH_AsianAlone",
                "V_20_VAP_NH_NativeAlone", "V_20_VAP_NH_PacificAlone",
                "V_20_VAP_NH_OtherAlone", "V_20_VAP_NH_TwoOrMore",
                "T_20_CENS_Total",
            ]
            totals: dict[int, dict[str, float]] = {}
            unmatched_blocks = 0
            matched_blocks = 0
            for row in reader:
                geoid = row["GEOID"]
                district = baf.get(geoid)
                if district is None:
                    unmatched_blocks += 1
                    continue
                matched_blocks += 1
                t = totals.setdefault(district, {f: 0.0 for f in fields})
                for f in fields:
                    v = row.get(f) or "0"
                    try:
                        t[f] += float(v)
                    except ValueError:
                        pass

    print(f"  matched {matched_blocks:,} blocks, "
          f"unmatched {unmatched_blocks:,}", file=sys.stderr)
    print(f"  districts produced: {len(totals)}", file=sys.stderr)

    out = []
    for d, t in sorted(totals.items()):
        nh_total = t["V_20_VAP_NH_Total"]
        if nh_total == 0:
            continue
        other_n = (t["V_20_VAP_NH_NativeAlone"] + t["V_20_VAP_NH_PacificAlone"]
                   + t["V_20_VAP_NH_OtherAlone"] + t["V_20_VAP_NH_TwoOrMore"])
        if state in AT_LARGE:
            label = f"{state}-AL"
        else:
            label = f"{state}-{d:02d}"
        out.append({
            "district": label,
            "pct_white_nh": round(100 * t["V_20_VAP_NH_White"] / nh_total, 2),
            "pct_black": round(100 * t["V_20_VAP_NH_BlackAlone"] / nh_total, 2),
            "pct_hispanic": round(100 * t["V_20_VAP_NH_Hispanic"] / nh_total, 2),
            "pct_asian": round(100 * t["V_20_VAP_NH_AsianAlone"] / nh_total, 2),
            "pct_other": round(100 * other_n / nh_total, 2),
            "pct_college": "",       # filled later from ACS state avg
            "pct_under_30": "",
            "pct_65_plus": "",
            "median_age": "",
            "median_income": "",
            "total_population": int(t["T_20_CENS_Total"]),
            "source": "DRA_VAP_NH_2020",
        })
    return out


def main():
    targets = REDRAWN_STATES
    if len(sys.argv) > 1:
        targets = [s.upper() for s in sys.argv[1:]]

    all_rows = []
    skipped = []
    for state in targets:
        try:
            all_rows.extend(aggregate_state(state))
        except FileNotFoundError as e:
            print(f"\n[skip {state}] {e}", file=sys.stderr)
            skipped.append(state)

    out_path = DATA_DIR / "demographics_dra.csv"
    if len(sys.argv) > 1:   # some states only: keep the other states' rows
        all_rows = merge_rows(out_path, all_rows, [s for s in targets if s not in skipped])
    cols = ["district", "pct_white_nh", "pct_black", "pct_hispanic", "pct_asian",
            "pct_other", "pct_college", "pct_under_30", "pct_65_plus",
            "median_age", "median_income", "total_population", "source"]
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in all_rows:
            w.writerow(r)
    print(f"\nWrote {out_path} with {len(all_rows)} district rows", file=sys.stderr)
    if skipped:
        print(f"  skipped (no BAF): {skipped}", file=sys.stderr)


if __name__ == "__main__":
    main()
