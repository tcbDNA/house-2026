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
| `national_sensitivity_v20.csv` | Provenance not recorded. Treated as unverified; checked against a precinct-based compilation under model-v4 item 2. |
