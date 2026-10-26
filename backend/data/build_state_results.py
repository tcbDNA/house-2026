"""Official 2020 and 2024 presidential results by state, from the FEC.

Reads (saved under data/sources/fec_pres/, URLs in data/sources/SOURCES.md):
  2024presgeresults.xlsx      — Official 2024 Presidential General Election Results
  federalelections2020.xlsx   — Federal Elections 2020, Table 2 (popular vote)

Writes data/state_pres_results.csv: state, D/R/total votes per year, and
margins (D − R) / total × 100. These replace national_sensitivity_v20.csv's
state margins (its 2024 figures were off by up to 4.2 pts: TN, AR, MD).
"""
from __future__ import annotations

import csv
from pathlib import Path

from xlsx_table import read_sheet

DATA_DIR = Path(__file__).resolve().parent
SRC = DATA_DIR / "sources" / "fec_pres"
OUT = DATA_DIR / "state_pres_results.csv"


def read_2024() -> dict[str, tuple[int, int, int]]:
    rows = read_sheet(SRC / "2024presgeresults.xlsx", "OFFICIAL 2024 PRES GE RESULTS")
    hdr = [h.strip().upper() for h in rows[0]]
    iD, iR, iT = hdr.index("HARRIS"), hdr.index("TRUMP"), hdr.index("TOTAL VOTES")
    out = {}
    for r in rows[1:]:
        if r and len(r[0].strip()) == 2 and r[0].strip().isalpha():
            out[r[0].strip()] = (int(float(r[iD] or 0)), int(float(r[iR] or 0)), int(float(r[iT] or 0)))
    return out


def read_2020() -> dict[str, tuple[int, int, int]]:
    rows = read_sheet(SRC / "federalelections2020.xlsx", "3. Table 2 Electoral & Pop Vote")
    out = {}
    for r in rows:
        st = r[0].strip().rstrip("*") if r else ""   # "ME*", "NE*": split electoral votes
        if len(st) == 2 and st.isalpha() and len(r) > 6 and r[3]:
            # columns: STATE, EV Biden, EV Trump, Biden, Trump, All Others, Total Vote
            out[st] = (int(float(r[3])), int(float(r[4])), int(float(r[6])))
    return out


def main():
    y24, y20 = read_2024(), read_2020()
    assert set(y24) == set(y20), set(y24) ^ set(y20)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["state", "dem_2024", "rep_2024", "total_2024", "margin_2024",
                    "dem_2020", "rep_2020", "total_2020", "margin_2020"])
        for s in sorted(y24):
            d24, r24, t24 = y24[s]
            d20, r20, t20 = y20[s]
            w.writerow([s, d24, r24, t24, round(100 * (d24 - r24) / t24, 3),
                        d20, r20, t20, round(100 * (d20 - r20) / t20, 3)])
    nat = [sum(v[i] for v in y24.values()) for i in range(3)], [sum(v[i] for v in y20.values()) for i in range(3)]
    print(f"wrote {OUT} ({len(y24)} states); national 2024 {100 * (nat[0][0] - nat[0][1]) / nat[0][2]:+.2f}, "
          f"2020 {100 * (nat[1][0] - nat[1][1]) / nat[1][2]:+.2f}")


if __name__ == "__main__":
    main()
