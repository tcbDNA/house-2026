# External sources

Every external number the model uses must trace to a file in this directory
(or a file with a URL recorded here). Raw downloads are committed as-is
because pollster PDFs and news pages get moved or edited.

| File | URL | Retrieved | Used for |
|---|---|---|---|
| `2026_nominees/wwno_2026-06-27_letlow_davis.html` | https://www.wwno.org/politics/2026-06-27/letlow-davis-advance-in-louisianas-u-s-senate-race | 2026-10-26 | LA Senate: Letlow (R) and Davis (D) won June 27 runoffs |
| `2026_nominees/newsnation_2026-06-16_al_senate_runoffs.html` | https://www.newsnationnow.com/us-news/southeast/alabama-senate-runoff-results-2026/amp/ | 2026-10-26 | AL Senate: Moore (R) and Wess (D) won June 16 runoffs (DDHQ projections) |
| `2026_nominees/cbs42_2026-06-16_moore_runoff.html` | https://www.cbs42.com/news/trump-backed-us-rep-barry-moore-wins-gop-primary-runoff-for-the-us-senate-in-alabama/amp/ | 2026-10-26 | AL Senate: Moore R runoff win; Wess vs Larriett D runoff |

## Unverified inputs

| File | Status |
|---|---|
| `backend/data/raw_war.csv` | Provenance not recorded (arrived in the initial commit). Treated as unverified; audit under model-v4 item 5. |
| `national_sensitivity_v20.csv` | Provenance not recorded. Checked (model-v4 item 2): 2024 margins match The Downballot's precinct-based compilation in 428 of 435 districts (fixed in `load_data.DOWNBALLOT_FIXES`: MO-01/03/04/06 both years, LA-06/AL-06/TX-37 2024). 2020 and 2024 margins on new lines match DRA precinct sums (median gap ~0.1, max 1.6 level, max 0.29 in trend; `backend/analysis/dra_district_check.csv`). |

## The Downballot — presidential results by congressional district

| File | URL | Retrieved | Used for |
|---|---|---|---|
| `downballot_2024_pres_by_cd/downballot_post_presbycd.html` | https://the-db.co/presbycd (→ https://www.the-downballot.com/p/the-downballots-calculations-of-presidential) | 2026-10-26 | Index page linking the sheets |
| `downballot_2024_pres_by_cd/downballot_presbycd_current_lines.xlsx` | https://docs.google.com/spreadsheets/d/1eZfaFI-c-PFOoKx1-zZA2MP0_dxRq_LVK0re3BOQqy0 | 2026-10-26 | 2020 & 2024 presidential results for the districts used in 2026 (2020 blank for districts on new lines) |
| `downballot_2024_pres_by_cd/downballot_presbycd_2024_lines.xlsx` | https://docs.google.com/spreadsheets/d/1ng1i_Dm_RMDnEvauH44pgE6JCUsapcuu8F2pCfeLWFo | 2026-10-26 | 2020 & 2024 results on the 2024 lines |
| `downballot_2024_pres_by_cd/downballot_methodology.txt` | https://docs.google.com/document/d/1efGEHGAQGaDGnIrdedwxVg1uUrjZYz06IPLTHRCg9zM/ | 2026-10-26 | Methodology: precinct results for split counties, county results for unsplit counties |

Comparison against national_sensitivity_v20.csv: `backend/analysis/v20_vs_downballot.csv`.

## Dave's Redistricting precinct (VTD) data

| File | URL | Retrieved | Used for |
|---|---|---|---|
| `dra_vtd_pres/vtd_pres_<ST>.csv.gz` (CA, TX, FL, AL, LA, UT, OH, NC, TN, MO) | https://github.com/dra2020/vtd_data (2020_VTD/<ST>, v07 releases; raw ~1 GB cached under `data/dra_vtd/`, gitignored) | 2025-05 (cached); extracted 2026-10-26 | Per-VTD extract: current district, 2024-lines district, 2020 Census population, 2020/2024 presidential votes. Reproduces `analysis/dra_district_check.csv` and `data/core_retention.csv`. |

## Census 119th-Congress district boundaries (2024 lines)

| File | URL | Retrieved | Used for |
|---|---|---|---|
| `census_cd119/cb_2024_us_cd119_5m.zip` | https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_cd119_5m.zip | 2025-05 (cached) | 2024-lines shapes: Missouri districts restored after its 2025 map was overturned (`data/restore_census_lines.py MO`); old-district side of `data/core_retention.csv` |
