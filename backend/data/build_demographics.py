"""Merge Path A (ACS) + Path B (DRA) demographic CSVs into one file
demographics.csv with all 435 districts. Fall back to state averages
(computed from ACS) for any district missing data.

Validates:
  - exactly 435 rows
  - no duplicate districts
  - race percentages sum to 100 (±0.5)
  - prints sample districts and which states fell back to estimates
"""

import csv
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
V18_CSV = DATA_DIR.parent.parent / "national_sensitivity_v20.csv"

NUMERIC_COLS = (
    "pct_white_nh", "pct_black", "pct_hispanic", "pct_asian", "pct_other",
    "pct_college",
    "pct_white_nh_college", "pct_white_nh_non_college",
    "pct_nonwhite_college", "pct_nonwhite_non_college",
    "pct_under_30", "pct_30_44", "pct_45_64", "pct_65_plus",
    "median_age", "median_income", "total_population",
)
ALL_COLS = ("district", *NUMERIC_COLS, "source")


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def all_districts() -> list[tuple[str, str]]:
    """Return (district, state) tuples from v18."""
    with V18_CSV.open() as f:
        return [(r["district"], r["state"]) for r in csv.DictReader(f)]


def to_float(s):
    if s is None or s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def normalize_row(r: dict, default_source: str) -> dict:
    out = {"district": r["district"], "source": r.get("source") or default_source}
    for c in NUMERIC_COLS:
        out[c] = to_float(r.get(c))
    return out


def state_of(district: str) -> str:
    return district.split("-")[0]


def compute_state_avgs(rows: list[dict]) -> dict[str, dict]:
    by_state: dict[str, list[dict]] = {}
    for r in rows:
        by_state.setdefault(state_of(r["district"]), []).append(r)
    avgs = {}
    for state, group in by_state.items():
        agg = {}
        for c in NUMERIC_COLS:
            vals = [r[c] for r in group if r.get(c) is not None]
            agg[c] = sum(vals) / len(vals) if vals else None
        avgs[state] = agg
    return avgs


def main():
    acs = [normalize_row(r, "ACS_2023_5yr") for r in load_csv(DATA_DIR / "demographics_acs.csv")]

    dra_rows = []
    dra_paths = sorted(DATA_DIR.glob("demographics_dra*.csv"))
    for p in dra_paths:
        for r in load_csv(p):
            dra_rows.append(normalize_row(r, "DRA_2025"))

    # tract-level ACS aggregated onto new lines — fills edu/age/income for redrawn districts
    new_lines_acs = {}
    for r in load_csv(DATA_DIR / "demographics_acs_new_lines.csv"):
        nr = normalize_row(r, r.get("source") or "ACS_new_lines")
        new_lines_acs[nr["district"]] = nr
    print(f"ACS rows: {len(acs)}  DRA rows: {len(dra_rows)}  ACS-new-lines rows: {len(new_lines_acs)}",
          file=sys.stderr)

    # ACS provides state-average fallback
    state_avgs = compute_state_avgs(acs) if acs else {}

    by_district: dict[str, dict] = {}
    for r in acs + dra_rows:  # DRA wins (later overwrites)
        by_district[r["district"]] = r

    missing = []
    fallback = []
    output_rows = []
    for district, state in all_districts():
        existing = by_district.get(district)
        if existing and all(existing.get(c) is not None for c in ("pct_white_nh", "pct_black", "pct_hispanic", "pct_asian")):
            # Prefer (1) DRA's race fields, (2) new-lines ACS for edu/age/income, (3) state avg
            filled = dict(existing)
            nl = new_lines_acs.get(district)
            for c in NUMERIC_COLS:
                if filled.get(c) is None and nl is not None and nl.get(c) is not None:
                    filled[c] = nl[c]
            for c in NUMERIC_COLS:
                if filled.get(c) is None:
                    avg = state_avgs.get(state, {}).get(c)
                    if avg is not None:
                        filled[c] = round(avg, 2)
            # If we used new-lines ACS to fill, refine the source label
            source = filled.get("source")
            if nl is not None and source and source.startswith("DRA"):
                source = f"{source}+ACS_tract_new_lines"
            output_rows.append({"district": district,
                                **{c: filled.get(c) for c in NUMERIC_COLS},
                                "source": source})
        else:
            avg = state_avgs.get(state)
            if avg and all(avg.get(c) is not None for c in ("pct_white_nh", "pct_black", "pct_hispanic", "pct_asian")):
                row = {"district": district,
                       **{c: round(avg[c], 2) if avg.get(c) is not None else None for c in NUMERIC_COLS},
                       "source": "STATE_AVG"}
                output_rows.append(row)
                fallback.append(district)
            else:
                missing.append(district)

    # Sort by district for stable output
    output_rows.sort(key=lambda r: r["district"])
    out_path = DATA_DIR / "demographics.csv"
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ALL_COLS)
        w.writeheader()
        for row in output_rows:
            w.writerow(row)

    # Validation
    print(f"\nWrote {out_path} with {len(output_rows)} rows", file=sys.stderr)
    if len(output_rows) != 435:
        print(f"  WARNING: expected 435, got {len(output_rows)}", file=sys.stderr)
    if missing:
        print(f"  MISSING demographics ({len(missing)}): {missing[:10]}...", file=sys.stderr)
    if fallback:
        print(f"  STATE-AVG fallback ({len(fallback)}): {fallback[:10]}...", file=sys.stderr)

    # Race-sum sanity check
    bad_sum = []
    for r in output_rows:
        s = sum(r[c] or 0 for c in ("pct_white_nh", "pct_black", "pct_hispanic", "pct_asian", "pct_other"))
        if abs(s - 100) > 0.5:
            bad_sum.append((r["district"], round(s, 2)))
    if bad_sum:
        print(f"  RACE %s NOT SUMMING TO 100 ({len(bad_sum)}): {bad_sum[:10]}", file=sys.stderr)

    # Sample
    samples = {r["district"]: r for r in output_rows}
    print("\nSample districts:", file=sys.stderr)
    for d in ("TX-28", "CA-22", "NY-15", "FL-26", "AL-07", "WY-AL"):
        if d in samples:
            r = samples[d]
            print(f"  {d}: W{r['pct_white_nh']} B{r['pct_black']} H{r['pct_hispanic']} A{r['pct_asian']} "
                  f"O{r['pct_other']} | coll{r['pct_college']} age{r['median_age']} | {r['source']}",
                  file=sys.stderr)


if __name__ == "__main__":
    main()
