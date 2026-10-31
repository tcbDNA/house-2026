"""Group two-way margins from Catalist's "What Happened 2024" national crosstabs -> catalist_baselines.json.

For every demographic slider: 2024 president (the model's group baselines, checked against
model.CATALIST_BASELINES) and 2022 House ("CD 2022"; no presidential race that year), which the governor
county maps use for counties whose starting map is an incumbent's 2022 race. Margin = 2 x two-way D share
- 100; the nonwhite-by-education cells are the Black, Latino, AAPI and Other cells weighted by that year's
composition. Source and URL: sources/catalist/README.md.
Usage (from backend/data/): python3 build_catalist_baselines.py
"""
import json
import sys
from pathlib import Path

import openpyxl

DATA = Path(__file__).resolve().parent
SRC = DATA / "sources" / "catalist" / "Catalist_What_Happened_2024_Public_National_Crosstabs_2025_05_19.xlsx"
OUT = DATA / "catalist_baselines.json"
COLUMNS = {"pres_2024": ("2024", "Pres\n2024"), "house_2022": ("2022", "CD\n2022")}   # (composition, two-way share)
SIMPLE = {"white_nh": "White", "black": "Black", "hispanic": "Latino", "asian": "AAPI",
          "white_college": "White College", "white_non_college": "White Non-College",
          "under_30": "18-29", "age_30_44": "30-44", "age_45_64": "45-64", "age_65_plus": "65+"}


def main() -> None:
    ws = openpyxl.load_workbook(SRC, data_only=True).worksheets[0]
    raw = list(ws.iter_rows(values_only=True))
    hdr = next(r for r in raw if r[0] == "Group 1")
    col = {str(h): i for i, h in enumerate(hdr) if h is not None}
    rows = {r[0]: r for r in raw if r[0]}
    out = {}
    for key, (comp, share) in COLUMNS.items():
        ci, si = col[comp], col[share]
        m = {k: round(2 * rows[v][si] - 100, 4) for k, v in SIMPLE.items()}
        for k, edu in (("nonwhite_college", "College"), ("nonwhite_non_college", "Non-College")):
            cells = [f"{g} {edu}" for g in ("Black", "Latino", "AAPI", "Other")]
            w = [rows[c][ci] for c in cells]
            m[k] = round(sum(wi * (2 * rows[c][si] - 100) for wi, c in zip(w, cells)) / sum(w), 4)
        out[key] = m
    sys.path.insert(0, str(DATA.parent))
    from model import CATALIST_BASELINES
    bad = {k: (v, out["pres_2024"][k]) for k, v in CATALIST_BASELINES.items() if abs(v - out["pres_2024"][k]) > 0.01}
    assert not bad, f"2024 column doesn't reproduce model.CATALIST_BASELINES: {bad}"
    OUT.write_text(json.dumps({"source": "sources/catalist/" + SRC.name, **out}, indent=1) + "\n")
    for k in CATALIST_BASELINES:
        print(f"{k:22s} 2024 pres {out['pres_2024'][k]:+7.2f}   2022 House {out['house_2022'][k]:+7.2f}")
    print(f"wrote {OUT.name}; 2024 matches model.CATALIST_BASELINES")


if __name__ == "__main__":
    main()
