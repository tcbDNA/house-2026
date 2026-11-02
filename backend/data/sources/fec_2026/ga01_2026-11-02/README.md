# GA-01 campaign finance, retrieved 2026-11-02 (20:35–20:45 UTC)

Answers a question about GA-01 money (Jim Kingston R vs Amanda Hollowell D); not used by the model.
API calls used the public `DEMO_KEY`.

| File | URL |
|---|---|
| `cands.json` | https://api.open.fec.gov/v1/candidates/?state=GA&office=H&district=01&election_year=2026&per_page=50 |
| `totals_<cand>.json` | https://api.open.fec.gov/v1/candidate/<cand>/totals/?cycle=2026&election_full=true (H6GA01109 Kingston, H6GA01158 Hollowell) |
| `committees_<cand>.json` | https://api.open.fec.gov/v1/candidate/<cand>/committees/?cycle=2026 |
| `reports_<cmte>.json` | https://api.open.fec.gov/v1/committee/<cmte>/reports/?cycle=2026&per_page=50&sort=-coverage_end_date (C00908624 Friends of Jim Kingston, C00914465 Amanda for Georgia) |
| `ie_totals_<cand>.json` | https://api.open.fec.gov/v1/schedules/schedule_e/by_candidate/?candidate_id=<cand>&cycle=2026&per_page=100 (processed independent expenditures, by spender) |
| `ie_efile_<cand>.json` | https://api.open.fec.gov/v1/schedules/schedule_e/efile/?candidate_id=<cand>&per_page=100&sort=-expenditure_date (raw e-filed 24/48-hour reports, includes amendments) |
| `ie_processed_H6GA01109.json` | https://api.open.fec.gov/v1/schedules/schedule_e/?candidate_id=H6GA01109&cycle=2026&per_page=100&sort=-expenditure_date (lists notices and reports, so items repeat) |
| `filings_C00908624.json` | https://api.open.fec.gov/v1/committee/C00908624/filings/?cycle=2026&per_page=20&sort=-receipt_date |
| `docquery_C00914465.html` | https://docquery.fec.gov/cgi-bin/forms/C00914465/ (Hollowell filing list; the API was rate-limited) |
| `f6/<n>.fec` | https://docquery.fec.gov/dcdev/posted/<n>.fec — 48-hour notices (contributions of $1,000+ received Oct 15 or later): Kingston 2029775, 2039745, 2040777, 2041698, 2042005, 2042551, 2044170, 2044819, 2045444; Hollowell 2035731, 2040241, 2043961 |
