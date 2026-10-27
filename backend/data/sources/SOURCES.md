# External sources

Every external number the model uses must trace to a file in this directory
(or a file with a URL recorded here). Raw downloads are committed as-is
because pollster PDFs and news pages get moved or edited.

| File | URL | Retrieved | Used for |
|---|---|---|---|
| `2026_nominees/wwno_2026-06-27_letlow_davis.html` | https://www.wwno.org/politics/2026-06-27/letlow-davis-advance-in-louisianas-u-s-senate-race | 2026-10-26 | LA Senate: Letlow (R) and Davis (D) won June 27 runoffs |
| `2026_nominees/newsnation_2026-06-16_al_senate_runoffs.html` | https://www.newsnationnow.com/us-news/southeast/alabama-senate-runoff-results-2026/amp/ | 2026-10-26 | AL Senate: Moore (R) and Wess (D) won June 16 runoffs (DDHQ projections) |
| `2026_nominees/wfae_balkcom_replaces_edwards_nc11_2026-08-10.html` | https://www.wfae.org/2026-08-10/state-rep-jennifer-balkcom-to-replace-rep-chuck-edwards-on-nc-11-ballot | 2026-10-26 | NC-11: Edwards (R) withdrew; district GOP committee chose state Rep. Jennifer Balkcom (Aug 10) |
| `2026_nominees/notus_balkcom_replaces_edwards_nc11.html` | https://www.notus.org/2026-election/north-carolina-chuck-edwards-replace-ballot-jennifer-balkcom | 2026-10-26 | NC-11: same (second source) |
| `2026_nominees/cbs42_2026-06-16_moore_runoff.html` | https://www.cbs42.com/news/trump-backed-us-rep-barry-moore-wins-gop-primary-runoff-for-the-us-senate-in-alabama/amp/ | 2026-10-26 | AL Senate: Moore R runoff win; Wess vs Larriett D runoff |

## Unverified inputs

| File | Status |
|---|---|
| `backend/data/raw_war.csv` | **Verified (model-v4 item 5):** rows 1–2527 are identical, in order, to Split Ticket's Full WAR Database (Datawrapper chart Eq2Z0 version 46, published 2026-05-11; https://split-ticket.org/full-wins-above-replacement-war-database/), with headers renamed (CD→Geography, SORTABLE→Sortable). The last two rows — Governor, North Carolina 2020 (Cooper D+5.85) and 2016 (D+3.86) — are **not** Split Ticket's (it publishes no governor WAR); they are Cooper's raw margin minus the presidential margin, added by hand. **Kept by user decision (2026-10-26)** — the user expects Cooper to overperform; they contribute +2.04 to NC through the 0.5× cross-chamber discount. Copies in `split_ticket_war/`. |
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

## FEC official presidential results by state

| File | URL | Retrieved | Used for |
|---|---|---|---|
| `fec_pres/2024presgeresults.xlsx` | https://www.fec.gov/documents/5645/2024presgeresults.xlsx | 2026-10-26 | Official 2024 state results → `data/state_pres_results.csv` (build_state_results.py) |
| `fec_pres/federalelections2020.xlsx` | https://www.fec.gov/resources/cms-content/documents/federalelections2020.xlsx | 2026-10-26 | Federal Elections 2020, Table 2 → 2020 state results |
| `fec_pres/fec_elections.html` | https://www.fec.gov/introduction-campaign-finance/election-and-voting-information/ | 2026-10-26 | Index page linking the 2024 file |

v20's 2024 state margins differed from official by up to 4.2 pts (TN R+25.5 vs R+29.72; AR 1.6; MD 1.5); 2020 matched within 0.05. National from these files: 2024 R+1.47, 2020 D+4.46.

## 2025 governor results (NJ, VA) — trend-weight backtest

| File | URL | Retrieved | Used for |
|---|---|---|---|
| `gov_2025/nj_2025-official-general-results-governor.pdf` (+ `.txt` text extract via pdfplumber) | https://nj.gov/state/elections/assets/pdf/election-results/2025/2025-official-general-results-governor.pdf | 2026-10-26 | NJ official list (12/03/2025), tally by county for every candidate |
| `gov_2025/va_2025_governor_elstats_search.csv` (+ `.url` with the exact query) | https://va2.elstats.civera.com/api/download_search.csv (Virginia Dept. of Elections historical database, office = Governor, 2025) | 2026-10-26 | VA official results by locality (133) and precinct |

## 2026 generic-ballot crosstabs (polls_2026/) — data in `generic_ballot_crosstabs.csv`

Binary files here and in polls_2024/ are stored with Git LFS (`.gitattributes`). Retrieved 2026-10-26 (copies of the files the 2026 crosstab rows were read from).

| Pollster | Saved file(s) | URL |
|---|---|---|
| NYT/Siena (Oct 12–19, LV) | `nyt_siena/nyt_times-siena-poll-crosstabs_2026-10-21_archive.ph.html` | https://www.nytimes.com/interactive/2026/10/21/polls/times-siena-poll-crosstabs.html (archive.ph copy) |
| CBS/YouGov (Oct 21–23, LV) | `cbs_yougov/cbsnews_20261025_sun.pdf` | https://assets1.cbsnewsstatic.com/hub/cms/prod_cms_alt/file/2026/10/25/8ad451c3-2d1f-4f7f-a3c8-97f923271e92/cbsnews_20261025_sun.pdf |
| Marist/NPR/PBS News (Oct 19–20, LV; retrieved 2026-10-27; race only as White vs Non-white, counts for the white groups via `crosstab_white_only_polls`) | `marist/marist_us_midterm_elections_october_2026.html`, `marist/NPR_PBS-News_Marist-Poll_USA-NOS-and-Tables_202610211808AS.pdf` (methodology p.1: 1,289 RV, likely-voter weight, LV MOE ±3.8; Nature of the Sample p.3: LV White 73%, white college 36%, white non-college 37%; generic ballot p.7 USCNGS01) | https://maristpoll.marist.edu/polls/u-s-midterm-elections-october-2026/ ; tables https://maristpoll.marist.edu/wp-content/uploads/2026/10/NPR_PBS-News_Marist-Poll_USA-NOS-and-Tables_202610211808AS.pdf |
| Economist/YouGov (Oct 23–26, RV; retrieved 2026-10-27, link from the user) | `economist_yougov/econTabReport_nJaupnc.pdf` (p.17 table 12, 2026 Congressional Vote) | https://d3nkl3psvxxpe9.cloudfront.net/documents/econTabReport_nJaupnc.pdf |
| Economist/YouGov (Oct 19–20, RV; superseded by Oct 23–26 on 2026-10-27, kept for the record) | `economist_yougov/econTabReport_AjDiUmp.pdf` | https://d3nkl3psvxxpe9.cloudfront.net/documents/econTabReport_AjDiUmp.pdf |
| Echelon (Oct 15–19, LV) | `echelon/echelon_october_2026_omnibus_crosstabs.xlsx`, `echelon/october_2026_voter_omnibus_topline.pdf` | https://echeloninsights.com/insights/october-2026-verified-voter-omnibus |
| Pew (Sep 28–Oct 4, RV) | `pew/pew_oct2026_detailed_tables_1Xm-bp_u.xlsx`, `pew/pew_detailed_tables_2026-10.csv`, `pew/PP_2026.10.8_midterms_report.pdf` (methodology p.30: no subgroup n published), `pew/PP_2026.10.8_midterms-economy_topline.pdf`, `pew/midterm-vote-preferences-by-race.html` | https://www.pewresearch.org/politics/2026/10/08/midterm-vote-preferences-by-race-and-ethnicity-age-and-other-demographics/ ; tables https://docs.google.com/spreadsheets/d/1Xm-bp_uZKnHqbFwyRAhisydugmJ2Q8tECL3GA1t2WrM |
| Fox News (Oct 9–12, RV) | `fox/fox_october-9-12-2026_complete_national_cross-tabs_october-14-release.pdf` (+ topline) | https://static.foxnews.com/foxnews.com/content/uploads/2026/10/fox_october-9-12-2026_complete_national_cross-tabs_october-14-release.pdf |
| Emerson (Sep 21–22, LV) | `emerson/emerson_september_2026_national_full_results.xlsx`, `emerson/september-2026-national-poll-democrats.html` | https://docs.google.com/spreadsheets/d/1fPJgYdp3a18AbCbArB1FRC6EcsQ8AqjS (export ?format=xlsx) |
| Cygnal (Oct 1–2, LV) | `cygnal/24822-Cygnal-National-Early-Oct26-NVT-Deck-Midterm-Political.pdf` | https://www.cygn.al/wp-content/uploads/2026/10/24822-Cygnal-National-Early-Oct26-NVT-Deck-Midterm-Political.pdf (race results p.28 are an image; the 2026 values were read from the user's screenshot) |

Checked, not used (no vote-by-race crosstab): Prolific (Oct 21–22, 1,518 adult citizens; LV 52.6/41.9, D+10.7; RV 50.3/39.7), retrieved 2026-10-27 18:36 UTC, link from the user. The workbook's crosstabs (sheets 06–07, generic ballot RV / LV) break down by party ID and 2024 vote only; race appears only as a weighting target (sheet B1). `prolific/prolific_poll_democrats_lead_by_11_points_2026-10-27.html` (https://www.prolific.com/resources/poll-democrats-lead-by-11-points-here-s-how-we-reached-that-number), `prolific/Prolific_Poll_US_Oct2026_Full_Results_v2.xlsx` (https://docs.google.com/spreadsheets/d/1MsvLv0UnkXC4EyEKjAvpcc5iuTMpiB-k, downloaded via drive.google.com/uc?export=download&id=1MsvLv0UnkXC4EyEKjAvpcc5iuTMpiB-k), `prolific/Prolific_Poll_US_Oct2026_Questionnaire.pdf` (https://drive.google.com/file/d/1ZsrVniE9jCMw0R6nTMKbNTcy8waAv64L). A second, unlabelled link in the article (docs.google.com/spreadsheets/d/1DeStrzYk7XxjS_mfVTfRXnfD28b51RkZ) requires a Google sign-in and was not retrieved.

## Final 2024 pre-election polls, same pollsters (polls_2024/) — data in `pollster_2024_crosstabs.csv`

Retrieved 2026-10-26. Item 3 (pollster-matched group shifts).

| Pollster | Poll | Saved file(s) | URL |
|---|---|---|---|
| NYT/Siena | Oct 20–23, 2024, LV n=2,516; head-to-head with leaners | `nyt_siena/times-siena-poll-crosstabs_wayback_20241025170406.html` | https://www.nytimes.com/interactive/2024/10/25/us/elections/times-siena-poll-crosstabs.html (Wayback 20241025170406). No Asian column. |
| CBS/YouGov | Oct 23–25, 2024, LV n=2,154; Q5 with leaners, doc p.5 | `cbs_yougov/scribd_784786236_cbsnews-20241027-1-SUN_wayback_20241027223053.html`, `cbs_yougov/cbsnews_trump-harris-poll-gender-gap_20241028.html` | https://www.scribd.com/document/784786236/cbsnews-20241027-1-SUN (CBS News's own upload, embedded in https://www.cbsnews.com/news/trump-harris-poll-gender-gap/; Wayback 20241027223053). Weighted N only. |
| Economist/YouGov | Oct 26–29, 2024, RV n=1,444; p.10 table 6 | `economist_yougov/econTabReport_NgtZTja.pdf`, `economist_yougov/econtoplines_xAm5lvg.pdf` | https://d3nkl3psvxxpe9.cloudfront.net/documents/econTabReport_NgtZTja.pdf |
| Echelon | Oct 28–31, 2024, LV n=1,328; full ballot p.115, unweighted bases p.101 | `echelon/October-Omnibus-Crosstabs-Puck.pdf`, `echelon/October-2024-Voter-Omnibus-Topline-PUCK.pdf`, `echelon/echelon_oct-2024-verified-voter-omnibus.html` | https://echeloninsights.com/hubfs/blog-migration/October-Omnibus-Crosstabs-Puck.pdf |
| Pew | Sep 30–Oct 6, 2024 (ATP W156, final pre-election wave), RV n=4,025 | `pew_2024_final/pew_oct2024_detailed_tables_1draephQ.xlsx`, report/topline PDFs, html | https://docs.google.com/spreadsheets/d/1draephQOkZKQuafGRLJhACoX96s5qw4hiEkb4cpNRM0 (from https://www.pewresearch.org/politics/2024/10/10/the-harris-trump-matchup/). No subgroup n (MOE only). |
| Fox News | Oct 11–14, 2024, RV n=1,110; p.4 Q4 | `fox_2024_final/fox_october-11-14-2024_complete_national_cross-tabs_october-21-release.pdf` (+ topline, Oct 17 release) | https://static.foxnews.com/foxnews.com/content/uploads/2024/10/fox_october-11-14-2024_complete_national_cross-tabs_october-21-release.pdf. Latest Fox national poll found before Nov 5 (later releases were state polls). No subgroup n (MOE only). |
| Emerson | Oct 30–Nov 2, 2024, LV n=1,000; Combined Presidential Vote (with leaners) | `emerson/emerson_national_nov2024_1zSMg6ly1Mnj1m9QKd7tmckRkEEPSCjb8.xlsx`, `emerson/november-2024-national-poll-trump-and-harris-remain-locked-in-tight-race.html` | https://docs.google.com/spreadsheets/d/1zSMg6ly1Mnj1m9QKd7tmckRkEEPSCjb8 (export ?format=xlsx) |
| Cygnal | Oct 24–26, 2024, LV n=1,507; generic congressional ballot, deck p.16 | `cygnal/22669-Cygnal-National-NVT-Oct24-2-Deck-Public.pdf`, two html pages | https://www.cygn.al/wp-content/uploads/2024/10/22669-Cygnal-National-NVT-Oct24-2-Deck-Public.pdf. Race results exist only as heatmap images; the p.16 generic-ballot values (same question as Cygnal's 2026 row) were read from the deck and confirmed by the user. The presidential heatmap (p.44) is not used. |

## Pew 2024 validated voters (polls_2024/pew_2024_validated/) — data in `pew_validated_2024.csv`

`pew_validated2024_detailed_tables_1JczVvbr.xlsx` (https://docs.google.com/spreadsheets/d/1JczVvbrlxkLiYYiNPSv0TRlWsbvYEihkZrnH1kQXIH8), report PDF `PP-2025.6.26_validated-voters_report.pdf` and html pages from https://www.pewresearch.org/politics/2025/06/26/voting-patterns-in-the-2024-election/. Retrieved 2026-10-26. Optional 2024 group baseline (`group_baseline = "pew_validated"`).

## Split Ticket WAR (split_ticket_war/) — provenance check for `raw_war.csv`

Retrieved 2026-10-26; full file list with URLs in `split_ticket_war/README.md`. Full WAR Database (House + Senate 2014–2024): https://split-ticket.org/full-wins-above-replacement-war-database/, data https://datawrapper.dwcdn.net/Eq2Z0/46/dataset.csv (`Eq2Z0_war_database_dataset.csv`; all 46 chart versions in `datawrapper_Eq2Z0_versions/`), plus the per-cycle House/Senate pages and sheets for 2016–2024 and the methodology articles (`pages/`). Split Ticket publishes no governor WAR. Its baseline controls for seat partisanship, incumbency, demographics and money (2024 release); incumbency was worth about 3 points in 2024 ("Deconstructing WAR", 2025-08-15).

## Montana Senate 2026 polling (mt_senate_2026/) — data in `senate_poll_averages.csv`

Retrieved 2026-10-26; every file with its URL in `mt_senate_2026/README.md`. Montana is modeled as Alme (R) vs Bodnar (I) (user decision, 2026-10-26: three-way race, Bankhead (D) polling a distant third); its polling average, blended like every Senate race (independent: weight 1 × min(1, polls/3)), is the RealClearPolling average, Alme +12.0 (41.0 / 29.0 / 18.5 / 3.5; https://www.realclearpolling.com/polls/senate/general/2026/montana/alme-vs-bankhead-vs-bodnar-vs-austin), from Quantus Insights Oct 15–18 (686 LV; `quantus_2026-10-15_18_crosstabs.pdf`) and Rutgers-Eagleton for Montana Free Press Aug 27–Sep 7 (845 RV; `mtfp_eagleton_2026-09-11_article_wayback_20261011.html`), both checked against those releases. Other averages saved: Poliwave Alme +12.3, FiftyPlusOne +12.0, 270toWin +18.0 (two polls), Call the Map +17.1 (uses a VoteHub row with Bodnar and Bankhead swapped). VoteHub has no Montana Senate average. No ActiVote or Rasmussen poll of this race. Eight polls since Aug 15 are saved (Peak Insights ×2, Rutgers-Eagleton, Aspect, Quantus ×2, American Pulse, Concord); the Peak (Oct) and Aspect memos are images posted on X.

## Public generic-ballot averages (public_averages_2026/) — data in `public_averages.csv`

Retrieved 2026-10-26 (details in `public_averages_2026/README.md`). Compared against the national margin on every run (item 8) and shown under the national total in the app. RealClearPolling D+8.3 (51.1–42.8; live page blocks downloads, Wayback copy 2026-10-26 15:38 UTC; window Oct 8–23). Silver Bulletin D+8.97 (50.81–41.84; the page's average chart data, Datawrapper rfiFi v4688; the page's public header says "sitting at D +9"; its likely-voter version, D+9.5, is not used). VoteHub D+8.4 (50.7–42.3; daily average series, generic_ballot_2026, updated 2026-10-26 19:10).

## Nebraska Senate 2026 polling (ne_senate_2026/) — data in `senate_poll_averages.csv`

Retrieved 2026-10-26; every file with its URL in `ne_senate_2026/README.md`. Nebraska (Osborn (I) vs Ricketts (R), no Democratic nominee) blends its polling average with the model like a two-party race (user decision, 2026-10-27; it first rested on the polling average alone). RealClearPolling publishes no average for this race (same-day Wayback copy: average row hidden, three polls listed), so `build_senate_poll_averages.py` recomputes one from each pollster's latest poll ending Oct 5 or later (GBAO, Impact Research, NPA, Concord: Osborn +0.75). Other averages saved here, for comparison: Poliwave 46.7–46.7 across 8 polls (https://www.poliwave.com/us/ne/sen-fed), FiftyPlusOne 46.2–46.2, VoteHub Osborn +0.1 (14 polls), Pollsmax Ricketts +2.2 (14 polls), 270toWin Ricketts +2.3 (3 polls). Ten polls since Aug 1 are listed in the README with sponsors; several are partisan-sponsored (GBAO for Working Class Majority PAC, Impact Research for the Osborn campaign, Concord for Education Reform Now Advocacy on one side; NPA and co/efficient flagged R on the other). Not retrieved: Decision Desk HQ (bot check), Silver Bulletin (paywall). No ActiVote or Rasmussen poll of this race.

## Senate polling averages (senate_polls_2026/) — data in `senate_poll_averages.csv`

Retrieved 2026-10-26, refreshed 2026-10-27 (new polls in TX, ME, MI, NC and SC; see the update section of `recent/README.md`); files and URLs in `senate_polls_2026/README_A.md`, `README_B.md` (competitive races), `README_C.md` (the 18 other races) and `recent/README.md` (every poll ending Oct 1 or later in 17 races, for the freshness check, with `recent_polls_compiled.json`). `build_senate_poll_averages.py` builds the averages the Senate poll blend uses (rules in its docstring: RCP minus Rasmussen; recomputed from each pollster's latest poll in the last three weeks where newer polls came out after RCP's last update, or RCP has no average; report in `backend/analysis/senate_poll_averages.txt`). The notes below describe the first, RCP-only version of the file. RealClearPolling where it publishes an average — its live pages began returning 403, so most figures come from RCP's own data feed (`polling_data.json`, the page's `pollingDataUrl`) saved with the latest Wayback copy of the page — else Poliwave (MS, LA; RCP pages blocked and neither race is in RCP's latest-polls feed; FiftyPlusOne has no average). Rasmussen polls inside RCP's averages (AK, ME, MI, MN, NH, OH, SC, TX) are removed per the user's exclusion rule; RCP's averages are simple means, so `margin` is the mean of the remaining polls and `margin_published` is RCP's figure. No ActiVote poll is in any average used.

## Excluded pollsters (excluded_pollsters/)

Retrieved 2026-10-26. Wedgewood Polls (Wedgewood Polling) is excluded from every average (user decision, 2026-10-26): on Oct 20, 2026 it said on X that its polls were fabricated, an "experimental project" to show how easily a fake pollster is picked up by aggregators, after FiftyPlusOne confronted it with evidence from its Mississippi Senate survey's raw data. `kmph_wedgewood_fake_polling_firm.html` (TNND via KMPH, Oct 21: https://kmph.com/news/nation-world/fake-polling-firm-tricked-media-claims-fabricated-surveys-were-for-social-experiment-democrats-republicans-abdul-el-sayed-mallory-mcmorrow-francesca-hong-james-talarico-ken-paxton-rrt) and `newsweek_wedgewood_fake_polling_firm.html` (Newsweek, Oct 21: https://www.newsweek.com/fake-polling-firm-duped-media-in-social-experiment-12599153). Its only poll inside the window was Mississippi's (Oct 12–14); its Iowa and Maine polls were listed by RCP but not averaged. No poll by Median Strategies (the other fake firm in these reports) is in any data used. ActiVote and Rasmussen Reports are excluded by user decision.

## Backtest: final RCP averages, 2022 and 2024 (polls_backtest/)

Final pre-election RealClearPolitics Senate and generic-ballot averages, with each poll RCP listed and a flag for whether it was in the average. They come from Wayback copies of RCP's race pages plus RCP's `polling_data.json` feeds, all retrieved 2026-10-26. Rasmussen and ActiVote rows are flagged (`excluded_pollster`). See `polls_backtest/README.md` for every file, URL, archive URL and caveat. The CSVs are `senate_2022_rcp_final.csv`, `senate_2024_rcp_final.csv` and `generic_ballot_rcp_final.csv`.

## Backtest: official results (fec_backtest/)

Retrieved 2026-10-26; every file with its URL in `fec_backtest/README.md`. FEC *Federal Elections 2016* (presidential results by state → 2016→2020 state trends), *2018* (Senate winners → 2024 incumbents) and *2022* (Senate results, with the FEC incumbent flag). The FEC has not published 2024 Senate results, so 2024 uses the House Clerk's *Statistics of the Presidential and Congressional Election of November 5, 2024* (official compilation of certified state results; its 2024 presidential figures match the FEC's in 48 of 51 states). Tidy CSVs: `pres_2016_by_state.csv`, `senate_2022_results.csv`, `senate_2024_results.csv`, `house_national_popular_vote.csv`. Used by `backend/analysis/senate_backtest.py`.

## Connecticut results by town (ct_planning_regions/) — data in `county_pres.csv` (CT rows)

Retrieved 2026-10-27; files and URLs in `ct_planning_regions/README.md`. The Census Bureau uses Connecticut's nine planning regions as county equivalents since 2022, but the county results file read by `parse_county_pres.py` reports the eight old counties, so Connecticut had no county overlay. `supplement_ct_pres.py` replaces the old-county rows with planning regions summed from the Connecticut Secretary of the State's official 2020 and 2024 presidential results by town (https://electionhistory.ct.gov contests 15175 and 36252, CSV exports), using the Census town crosswalk (https://www2.census.gov/geo/docs/reference/ct_change/ct_cou_to_cousub_crosswalk.txt). The towns sum exactly to the official statewide totals; summed into the old counties they match the replaced rows exactly for 2024 and within 600 votes for 2020. `build_slices_from_github.py` moves Connecticut's 2020 precincts into planning regions by the town in each precinct's name.

## 2026 turnout: Kalshi markets (turnout_2026/) — data in `turnout_2026.csv`

Retrieved 2026-10-26 from Kalshi's public API (markets last updated 2026-10-26T15:17Z); files and URLs in `turnout_2026/README.md`. "Midterm Voter Turnout" (series KXMIDTERMVOTETURN): for each 2026 Senate, governor and House race, contracts on whether the total vote count will be above X. `build_turnout_2026.py` derives each race's market-implied median total and its ratio to the 2024 presidential vote; the county overlay's estimated 2026 vote counts use each race's own ratio (state: Senate, else governor, else House markets; district: its House market), with the 70-race average (79.3%) as the fallback. Display only.
