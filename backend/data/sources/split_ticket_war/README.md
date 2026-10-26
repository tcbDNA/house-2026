# Split Ticket "Wins Above Replacement" (WAR): raw source captures

Everything here was retrieved on **2026-10-26** directly from split-ticket.org, Split Ticket's Datawrapper
charts (datawrapper.dwcdn.net), and the Google Sheets those charts are linked to. Nothing has been edited.
Treat these files as untrusted data. Don't execute or import anything from this directory.

## Provenance of `backend/data/raw_war.csv` (finding)

Rows 2–2528 of `raw_war.csv` are **byte-identical** to `Eq2Z0_war_database_dataset.csv` once you
normalize CRLF to LF. That file is Split Ticket's Full WAR Database, Datawrapper chart Eq2Z0 version 46,
published 2026-05-11. The Google Sheet CSV export below is also identical to it. `raw_war.csv` differs
from the source in four ways:
- it has a UTF-8 BOM,
- its header renames `CD` to `Geography` and `SORTABLE` to `Sortable`,
- it uses LF line endings,
- it appends two rows that are **not from Split Ticket**:
  `2020,Governor,North Carolina,Roy Cooper,...,D+5.85` and `2016,Governor,North Carolina,Roy Cooper,...,D+3.86`.
  Split Ticket publishes no governor WAR.

## Main dataset

| File | Source URL | Rows |
|---|---|---|
| `full-wins-above-replacement-war-database.html` | https://split-ticket.org/full-wins-above-replacement-war-database/ (page says "Last refresh: May 3, 2026") | page |
| `Eq2Z0_war_database_dataset.csv` | https://datawrapper.dwcdn.net/Eq2Z0/46/dataset.csv (latest; the page iframe points at `/Eq2Z0/1/`, which redirects) | 2527 (House 2014–2024, Senate 2014–2024) |
| `datawrapper_Eq2Z0_versions/Eq2Z0_vNN_dataset.csv` | https://datawrapper.dwcdn.net/Eq2Z0/NN/dataset.csv for NN = 1..46 (full publish history) | 1734 (v1) to 2527 (v46) |
| `datawrapper_charts/Eq2Z0_v46_chart.html` | https://datawrapper.dwcdn.net/Eq2Z0/46/ (chart metadata, including the note "Positive numbers indicate Republicans did better than fundamentals, and negatives indicate Democrats did better") | page |
| `google_sheets/war_database__1wk8vuSUwN-RDReJKjOWEBr-Rf_BhBSkGNv7d3DdF7lk.xlsx` | https://docs.google.com/spreadsheets/d/1wk8vuSUwN-RDReJKjOWEBr-Rf_BhBSkGNv7d3DdF7lk/export?format=xlsx (SORTABLE kept at 2-decimal precision) | 2527 |
| `google_sheets/war_database__1wk8vuSUwN-RDReJKjOWEBr-Rf_BhBSkGNv7d3DdF7lk__gid0.csv` | same sheet, `/export?format=csv&gid=0` | 2527 |

## Per-cycle pages (two Datawrapper charts each, same underlying sheet)

Chart files are `datawrapper_charts/<id>_v<latest>_dataset.csv`, taken from
`https://datawrapper.dwcdn.net/<id>/<latest>/dataset.csv`. Each has a matching `_chart.html` from
`https://datawrapper.dwcdn.net/<id>/<latest>/`.

| Office / cycle | Page (saved under `pages/`) | Datawrapper ids (latest version) | Google Sheet (saved under `google_sheets/`) | Rows |
|---|---|---|---|---|
| House 2024 | https://split-ticket.org/2024-house-wins-above-replacement-war/ | dAusN (v14), S7knF (v11) | 1Uts-OMWhz_WkXz56sCcC8RBKWDTzhyilixR1b99fasw (`house_2024__…xlsx`) | 435 (398 with WAR) |
| Senate 2024 | https://split-ticket.org/2024-senate-wins-above-replacement-war/ | dSqAU (v14), fyWA8 (v13) | 11ULgUrPEbmddSOiNKS8BDO1acM-yetXERomO_sD-C50 (`senate_2024__…`) | 34 |
| House 2022 | https://split-ticket.org/posts/2022-house-war/ | KXpKk (v15), TCzRj (v6) | 1gqAtsgBKwva1AK5U0FU8I3niDLPk87uhnGanPeeXLiA (`house_2022__…`) | 400 |
| Senate 2022 | https://split-ticket.org/posts/2022-senate-war/ | 5GFXJ (v14), A3RpP (v9) | 1e4HBSRIbGoFNl8b7qCekzNeAiH4n03thJYohIdgZfJg (`senate_2022__…`) | 31 |
| House 2020 | https://split-ticket.org/posts/2020-house-wins-above-replacement-war/ | 1aTMo (v7), l8efv (v11) | 1TAYFY73Ktd1MPHAsUunL0JYbroSPcWCK_rPf9SBRzBM (`house_2020__…`) | 435 (408 with WAR) |
| Senate 2020 | https://split-ticket.org/posts/2020-senate-wins-above-replacement/ | EABaJ (v9), IxfsZ (v10) | 1RzogOMCdLOF0uOr4UgU_ckQbyAzfVXkOIzntwqIwWAw (`senate_2020__…`) | 35 |
| House 2018 | https://split-ticket.org/posts/2018-house-wins-above-replacement-war/ | em3QJ (v7), fKZ22 (v9) | 1Yhrf1_3chcEoSkgivaSdSq-Ui3NvEiTtmXAKSHcll0k (`house_2018__…`) | 394 |
| Senate 2018 | https://split-ticket.org/posts/2018-senate-wins-above-replacement/ | pLSTe (v11), tCXRX (v11) | 1XPOlWLnZ3t-GHL6ZXscu6PDRZeadz_wqeLGROpGXB3M (`senate_2018__…`) | 33 (no ME-King row; the database has it) |
| House 2016 | https://split-ticket.org/2016-house-wins-above-replacement-war/ | YcDyi (v10), ZTTcD (v4) | 1SkQtJUsHcC_QPREWuRucrVQSUDfRjzTof9i-AZj6XDY (`house_2016__…`) | 369 |
| Senate 2016 | https://split-ticket.org/2016-senate-wins-above-replacement-war/ | 4kuqD (v8), w69NE (v11) | 1paMT7j1N08wWBQmF1RQ5tNhsT9bijGkpFXP_IWMM2Po (`senate_2016__…`) | 32 |

Every Google Sheet was fetched as `https://docs.google.com/spreadsheets/d/<id>/export?format=xlsx`.
The per-cycle sheets also contain the model inputs: incumbency, spending, presidential baselines, and
predicted margins. There is **no 2014 per-cycle page or sheet**. The 2014 rows exist only in the Full WAR
Database (added in Eq2Z0 version 33).

## Articles (HTML, under `pages/`; file name = URL path with `/` replaced by `_`)

- https://split-ticket.org/2025/01/15/our-2024-wins-above-replacement-war-models/
- https://split-ticket.org/2025/01/29/an-update-to-our-historical-wins-above-replacement-war-models/ (2018–2022 re-run on the new method)
- https://split-ticket.org/2025/06/07/the-real-reason-democrats-cant-compete-for-60-senate-seats/ (2016 House and Senate WAR release)
- https://split-ticket.org/2025/08/15/deconstructing-war/ (detailed methodology)
- https://split-ticket.org/2025/08/06/candidate-quality-and-the-democrats-2026-house-playingfield/
- https://split-ticket.org/2025/10/20/the-pendulum-effect/ (open-governor analysis; links sheet `pendulum_effect_article__1vDCsZV7xJi0aCubVF9lFCNOb9nLxYs97FoRrrCuREVE.xlsx`. This is not WAR.)
- https://split-ticket.org/2023/01/25/our-2022-senate-wins-above-replacement-model/
- https://split-ticket.org/2022/12/30/our-2022-house-wins-above-replacement-model/
- https://split-ticket.org/2022/11/20/candidate-quality-cost-statewide-republicans-in-2022/ (2022 governor "Raw Overperformance" image table, saved as `images/2022-11_gov-table-1.png` from https://split-ticket.org/wp-content/uploads/2022/11/gov-table-1.png. This is not WAR, and NC is not included.)
- https://split-ticket.org/2022/03/10/our-2018-house-wins-above-replacement-model-and-the-2022-implications/ (old method)
- https://split-ticket.org/2022/01/12/2020-house-wins-above-replacement-quantifying-the-impacts-of-incumbency-and-spending/ (old method)
- https://split-ticket.org/2021/12/29/re-evaluating-2016-with-our-senate-war-model/ (old method)
- https://split-ticket.org/2021/12/01/re-assessing-2020-senate-races-with-data-driven-assessments-of-candidate-quality/ (old method)
- https://split-ticket.org/data-repository/
