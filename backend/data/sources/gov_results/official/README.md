# Official canvass cross-check: governor races that feed 2026 WAR records

Checked 2026-10-28. The rule: cross-check the governor races that feed 2026 WAR records against official state canvasses, and use the official figures wherever they differ from `gov_results.csv`, which was built from Wikipedia.

The result for all 23 races is in `../official_overrides.csv`, one row per race. `differs = yes` means at least one of these differs: d_votes, r_votes or total_votes (any difference), or d_pct or r_pct (by more than 0.01 points). Percentages are recomputed as official votes ÷ official total and rounded to 2 decimals.

**How "total votes" is counted.** Total votes means votes cast for governor, as the canvass counts them. It includes every candidate and write-in or scattering votes, and Nevada's "None of These Candidates". It excludes blank, under, over and void votes wherever the canvass reports them separately. Each row's `diff_note` explains how the total was built.

**Fusion candidates.** Votes on each fusion line were added together:
- 2018 CT: Lamont (D+WFP) and Stefanowski (R+Independent Party).
- 2022 CT: Lamont (D + Griebel Frank for CT + WFP).
- 2022 NY: Hochul (DEM+WOR) and Zeldin (REP+CON).

The 2020 VT canvass prints Zuckerman on a single line with no Progressive/Democratic split, so 99,214 is his full total.

**How the files were handled.** Downloads used curl with a desktop-browser user agent. Every file was parsed as data with `python3 -I` (pypdf, xlrd, csv, json), and nothing in them was executed. The scripts are in the session scratchpad under `gov/canvass_scripts/` (`fetch.sh`, `il_postback.py`, `build_overrides.py`).

## Summary of differences (Wikipedia value → official value)

| race | field | Wikipedia (`gov_results.csv`) | official | D−R margin change (official − Wikipedia) |
|---|---|---|---|---|
| 2022 HI | d_votes | 259,901 | 261,025 | −0.10 pts |
| 2022 HI | r_votes | 151,258 | 152,237 | |
| 2022 HI | total_votes | 411,159 | 413,262 | |
| 2022 HI | d_pct | 63.21 | 63.16 | |
| 2022 HI | r_pct | 36.79 | 36.84 | |
| 2022 ID | total_votes | 592,557 | 592,624 (adds the 67 write-ins) | +0.01 pts |
| 2022 NE | total_votes | 666,795 | 672,593 (adds 5,798 write-in scatterings) | +0.21 pts |
| 2022 NE | d_pct | 36.29 | 35.98 | |
| 2022 NE | r_pct | 59.74 | 59.22 | |
| 2022 NY | total_votes | 5,902,996 | 5,912,286 (adds 9,290 scattering) | −0.01 pts |
| 2022 NY | d_pct | 53.20 | 53.12 | |
| 2022 NY | r_pct | 46.80 | 46.73 | |
| 2022 VT | d_pct | 23.94 | 23.96 | −0.05 pts |
| 2022 VT | r_pct | 70.91 | 70.98 | |

The other 18 races match exactly on D votes, R votes and total. 2018 ID differs only by rounding, which is within the 0.01-point tolerance: r_pct is 59.76 in Wikipedia and 59.77 official. Causes of the five differences:

- **HI 2022:** the Wikipedia overview carries lower candidate counts, apparently from a pre-final count. The official final report matches the Wikipedia state page.
- **ID, NE and NY 2022:** the candidate votes are identical. Wikipedia's total leaves out the write-in or scattering votes.
- **VT 2022:** the votes and the total are identical. Wikipedia's percentages divide by 285,056, which includes the 255 overvotes, instead of by its own total of 284,801.

## Files

All retrieval times are UTC, 2026-10-28.

| file | URL | retrieved (UTC) | notes |
|---|---|---|---|
| 2014_tx_race_summary_report.htm | https://elections.sos.state.tx.us/elchist175_state.htm | 19:04:09 | TX SOS historical "Race Summary Report", 2014 General, canvass votes. Governor: Race Total 4,718,268 (incl. 1,062 write-in). |
| 2018_tx_race_summary_report.htm | https://elections.sos.state.tx.us/elchist331_state.htm | 19:04:11 | TX SOS Race Summary Report, 2018 General. The server copy carries a "saved from url" comment. Race Total 8,343,443. |
| 2022_tx_statewide_results.json | https://results.texas-election.com/static/data/election/47009/242/StateWide.json | 19:05:10 | Statewide results data from the TX SOS results site (results.texas-election.com, linked from sos.state.tx.us "Election Results 2019-2024"). Governor T = 8,102,908, including 1,637 write-in votes. |
| 2022_tx_results_version.json | https://results.texas-election.com/static/data/election/47009/Version.json | 19:05:10 | Data version (242) for election 47009 (2022 November 8th General). |
| 2022_tx_election_constants.json | https://results.texas-election.com/static/data/ElectionConstants_404.json | 19:05:23 | Election list for the site. Election 47009 has `O: "Y"`, which the site displays as "Official Results". |
| 2022_ar_governor_contest_results.json | https://enr-results-api.totalresults.com/Contest/GetSingleContestResults?cId=arkansas&electionID=1844&contestType=STW&contestID=286 | 19:20:55 | Arkansas results system (arkansas.tally-enr.com, linked from sos.arkansas.gov as "2022 General Election and Nonpartisan Judicial Runoff Election"). `isOfficial: true`. Governor totalVotes 907,037. No PDF canvass for the 2022 general is posted on sos.arkansas.gov. |
| 2022_ar_contest_list.json | https://enr-results-api.totalresults.com/Contest/GetContestSearchList?cId=arkansas&electionID=1844 | 19:21:06 | Maps contest 286 choice IDs to names: 528 Chris Jones, 529 Ricky Dale Harrington Jr., 530 Sarah Huckabee Sanders. |
| 2022_ar_election_info.json | https://enr-results-api.totalresults.com/Election/GetElectionInfo?cId=arkansas&electionID=1844 | 19:20:56 | Election metadata ("2022 General", `isOfficial: true`). |
| 2022_az_statewide_canvass.pdf | https://web.archive.org/web/20240718140941id_/https://apps.azsos.gov/election/2022/General/canvass/2022dec05_general_election_canvass_web.pdf | 19:06:28 | "STATE OF ARIZONA OFFICIAL CANVASS", 2022 General, report date 12/5/2022. azsos.gov returned HTTP 403 to every request, so this is the **Wayback copy** of the official PDF. The URL comes from a Wayback copy of the azsos.gov "2022 General Election Canvass" page. No race total is printed: the total is Hobbs + Lake + 7 write-in candidates (820). |
| 2018_ct_statement_of_vote.pdf | https://portal.ct.gov/-/media/sots/electionservices/statementofvote_pdfs/2018-sov.pdf?rev=8be496593b194904b09d6d73879214e2&hash=5FDE8C5C85345BD3A060FE6A8E947F31 | 19:07:43 | CT SOTS Statement of Vote 2018, linked from the SOTS "General Elections Statement of Vote 1922-" page. **Scanned, with no text layer.** Governor figures were read visually from the rendered page 7 (printed p. 5, "Summarized by Congressional Districts"). Each column's 5 district rows sum to the printed Total. |
| 2022_ct_statement_of_vote.pdf | https://portal.ct.gov/-/media/sots/electionservices/statementofvote_pdfs/sov_2022.pdf | 19:02:58 | CT SOTS Statement of Vote 2022, page 7 Totals row. "Total Votes Cast" 1,268,893 (incl. 98 write-ins). |
| 2022_hi_statewide_final_summary.pdf | https://files.hawaii.gov/elections/files/results/2022/general/histatewide.pdf | 19:02:58 | HI Office of Elections, General Election 2022 Statewide "SUMMARY REPORT – FINAL REPORT", printed 11/22/2022. |
| 2018_id_governor_by_county.csv | https://canvass.sos.idaho.gov/eng/contests/download/7607/show_granularity_dt_id:3/.csv | 19:12:23 | Idaho SOS canvass database, contest 7607 (2018 General, Governor). "Total Votes Cast" 605,131. |
| 2022_id_governor_by_county.csv | https://canvass.sos.idaho.gov/eng/contests/download/17251/show_granularity_dt_id:3/.csv | 19:12:23 | Idaho SOS canvass database, contest 17251 (2022 General, Governor). "Total Votes Cast" 592,624 (incl. 67 write-in). |
| 2018_2022_id_governor_contest_search.html | https://canvass.sos.idaho.gov/eng/contests/search/year_from:2018/year_to:2022/office_id:4/stage:General | 19:12:24 | Search page used to identify contest IDs 7607 and 17251. |
| 2018_il_sbe_vote_totals.html | https://www.elections.il.gov/ElectionOperations/ElectionVoteTotals.aspx (POST, ddlElections=54 "2018 GENERAL ELECTION") | 19:11:41 | Illinois State Board of Elections vote totals page, fetched by ASP.NET postback (`il_postback.py`). Governor Vote Totals 4,547,657. |
| 2022_il_sbe_vote_totals.html | same page (POST, ddlElections=62 "2022 GENERAL ELECTION") | 19:11:38 | Governor Vote Totals 4,104,636. |
| 2022_ma_governor_by_municipality.csv | https://electionstats.state.ma.us/elections/download/154338/precincts_include:0/ | 19:12:41 | Secretary of the Commonwealth PD43+ archive, election 154338 (2022 Governor General). TOTALS row: Total Votes Cast 2,511,461, including 25,665 blanks. |
| 2022_ma_governor_election_page.html | https://electionstats.state.ma.us/elections/view/154338/ | 19:12:41 | PD43+ page for the same election. |
| 2022_md_official_results_governor.html | https://elections.maryland.gov/elections/archive/2022/general_results/gen_results_2022_1_P.html | 19:13:07 | MD SBE "Official 2022 Gubernatorial General Election Results for Governor / Lt. Governor", last refreshed 12/07/2022. Totals 2,005,223 (incl. write-ins). The non-archive URL now returns a 404 page. |
| 2022_ne_canvass_book.pdf | https://sos.nebraska.gov/sites/default/files/doc/elections/2022/2022%20General%20Canvass%20Book.pdf | 19:02:58 | NE SOS official 2022 General Canvass Book, page 13 Total row. No race total is printed: the total is the 3 candidates plus 5,798 write-in scatterings. |
| 2024_nh_governor.xls | https://web.archive.org/web/20251013021303id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-governor_3.xls | 19:27:14 | NH SOS 2024 General, Governor (sheet "summary gov", TOTALS row). sos.nh.gov returned Akamai 403 "Access Denied", so this is the **Wayback copy**. `_3.xls` is the file the results page links (the file was saved 11/25/2024). An earlier `_0.xls` existed in Nov 2024 and was not used. |
| 2024_nh_general_election_results_page.html.gz | https://web.archive.org/web/20261023162153id_/https://www.sos.nh.gov/2024-general-election-results | 19:27:15 | Wayback copy of the NH SOS "2024 General Election Results" page, which links `2024-ge-governor_3.xls`. Stored as the gzip bytes transferred (gunzip to read). |
| 2022_nv_official_abstract_of_votes.pdf | https://web.archive.org/web/20250623041405id_/https://www.nvsos.gov/sos/home/showpublisheddocument/11241/638059319239170000 | 19:29:40 | "2022 OFFICIAL State of Nevada General Election Returns … official abstract … as canvassed by the Justices of the Supreme Court on Tuesday, November 22, 2022". nvsos.gov serves an Imperva bot-check page to scripted requests, so this is the **Wayback copy**. The link comes from the nvsos.gov "2022 Election Information" page ("2022 Official General Election Abstract of Votes"). The PDF is scanned: page 5 values come from its OCR text layer and were confirmed against the rendered page. |
| 2022_nv_election_summary_unofficial.html.gz | https://web.archive.org/web/20261013125451id_/https://www.nvsos.gov/SOSelectionPages/results/2022StateWideGeneral/ElectionSummary.aspx | 19:16:11 | **Not used.** The page is titled "2022 Unofficial Statewide General Election Results". Its governor numbers equal the official abstract. Gzip bytes as transferred. |
| 2022_ny_general_results_certified.pdf | https://ny.elstats-staging.com/eng/files/serve/70 (redirected to ny.staging.elstats2.civera.com) | 19:11:02 | NYS Board of Elections "2022 General Election Results … Compiled from official records", compiled June 30, 2023. Governor is on pp. 35–36. This is the source document that results.elections.ny.gov/contest/1 cites ("11-8-2022 General Results by County…", file 70, 870,994 bytes). results.elections.ny.gov is behind a Cloudflare 403, so the file came from the vendor (Civera ElectionStats) host named in that page's metadata. The page metadata was read from Wayback capture 20260620120445. |
| 2022_ny_governor_by_county_split_party.csv | https://ny.elstats.civera.com/api/download_contest/1_table.csv?split_party=true (redirected to ny.elstats3.civera.com) | 19:10:29 | The "Download" CSV linked on results.elections.ny.gov/contest/1. Every number is identical to the certified PDF; the script asserts this. |
| 2022_or_abstract_of_votes.pdf | https://web.archive.org/web/20251113092311id_/https://sos.oregon.gov/elections/Documents/results/november-general-2022.pdf | 19:18:30 | OR SOS "November 8, 2022, General Election Abstract of Votes", Governor TOTAL row on page 4. The original URL now returns 404, so this is the **Wayback copy**. All 32 PDF captures from 2022-12 to 2025-11 have the same digest. |
| 2022_pa_summary_results.xml | https://www.electionreturns.pa.gov/api/ElectionReturn/GET?methodName=GetSummaryData&electionid=94&electiontype=G&isactive=0 | 19:19:18 | PA Department of State official returns site (electionreturns.pa.gov) summary data for the 2022 General Election: XML-wrapped JSON, as served. The site reports the 5 ballot candidates only and no write-ins, so the total is their sum (5,366,179). |
| 2020_vt_canvass_report_statewide_offices.pdf | https://outside.vermont.gov/dept/sos/Elections_Division/election_info_resources/elections_results_data/2020_general_election_official_report_canvassing_committee_united_states_vermont_statewide_offices.pdf | 19:09:23 | VT "Official Report of the Canvassing Committee", 11/03/2020. Governor: Total votes counted 370,968, with overvotes 170 and blanks 8,087. |
| 2022_vt_canvass_report_statewide_offices.pdf | https://outside.vermont.gov/dept/sos/Elections_Division/election_info_resources/elections_results_data/2022_general_election_official_report_canvassing_committee_vermont_statewide_public_questions.pdf | 19:09:24 | VT Official Report of the Canvassing Committee, 11/08/2022. The SOS page links it as "2022 General Election Canvass Report"; despite the "public_questions" URL, it contains the U.S. and statewide offices. Saved under a descriptive name. Governor: 291,955 counted, with 255 overvotes and 6,899 blanks. |
| 2024_vt_canvass_report_statewide_offices.pdf | https://outside.vermont.gov/dept/sos/Elections_Division/election_info_resources/elections_results_data/2024_general_election_official_report_canvassing_committee_united_states_vermont_statewide_offices.pdf | 19:09:24 | VT Official Report of the Canvassing Committee, 11/05/2024. Governor: 372,885 counted, with 167 overvotes and 9,877 blanks. |

### What could not be fetched directly

Every race was retrieved; none is missing. Where the state site blocked scripted downloads or had removed the file, the official document was taken from the Internet Archive or the state's vendor host instead:
- **Wayback copies:** AZ (azsos.gov HTTP 403), NH (sos.nh.gov Akamai 403), NV (nvsos.gov Imperva bot check), OR (the PDF was removed and now returns 404).
- **Vendor host:** NY (results.elections.ny.gov behind a Cloudflare 403; the files came from the vendor host that the official page links).

### Kind of official source used

- **Certified or official canvass documents (PDF or XLS):** AZ, CT 2018/2022, HI, NE, NH, NV, NY, OR, VT 2020/2022/2024.
- **The state's official results database or archive:** AR (results system flagged official), ID (SOS canvass database), IL (SBE vote totals), MA (PD43+), MD (SBE official results page), PA (DoS official returns), TX 2014/2018 (SOS historical race summary), TX 2022 (SOS results site, flagged official).

## SHA-256 of the saved files

```
af2db0bb9b286776c65c6f67b9b04c0f026c99d7e20e6fd26ad17e5234d09ea7  2014_tx_race_summary_report.htm
8679546d9dd19d22b19969af2f2d0e2e0441231d772bf46b74304b1d83bd4168  2018_2022_id_governor_contest_search.html
f3c4f52f92c14b3403778a2b6cd5a1541c47def83a248da151a7dd53deea7de8  2018_ct_statement_of_vote.pdf
e382b218c0e5e659b2fe84fb640b4695f890deedbe30d4414fa1618d874c2b1a  2018_id_governor_by_county.csv
a767450f03359fb64bffffaadfbb9c9c31e67b6cce348fb128b132224b46196d  2018_il_sbe_vote_totals.html
09654e0ad3106bbebf89842443a4a46b70cbcb4aa1539daf71d3ee26ac89c4d1  2018_tx_race_summary_report.htm
93f25587026697bb2848fa61df1634ea798daaf3c3d175edd811c32844a247d7  2020_vt_canvass_report_statewide_offices.pdf
2011a8ebc02cd8540e50a09f2e692b10974bae27ce9f6a1d6517dc60fd1b9c03  2022_ar_contest_list.json
8d07b70b37a47a4a174a589ec66f60947452e3208326876b5dfc2b6ce6909677  2022_ar_election_info.json
82483211f6ca0ed9d8d3bc137da30c993fbd99eb9c0093fc24c0a3ae4d7ca964  2022_ar_governor_contest_results.json
ec459c2c24889d3ea685f676907284c1d8a0b2542b5534e73166702b2905673d  2022_az_statewide_canvass.pdf
1b6ca3708890241c387320e68b5e628f27a3bbc08b83b0d172e5d7bd9183664b  2022_ct_statement_of_vote.pdf
2d9c039392169b3932c1ce9e11cdeb6c88e8361d97e560e1aaeb055d40f70669  2022_hi_statewide_final_summary.pdf
5571c71583074b82824dd5bb9cf9f35df90e30ef7f8acd9cae5ac149701a181f  2022_id_governor_by_county.csv
335d963f4488cce7b8a729bc53a357b0c5afe4d6f4bcf459cb2f20aaec4ab071  2022_il_sbe_vote_totals.html
85547c8ea5bd6f88a21d27d5b2adc646a4730fc042765d12cd9b83b5188b2b0c  2022_ma_governor_by_municipality.csv
a8673d96330318a5f9f214dbe97aae098f131dfce80a34197bb524a8cd6a5268  2022_ma_governor_election_page.html
850a91c34dfd6883844d4be03cca96f7a867922a3f931d430c4292f61f10aa1c  2022_md_official_results_governor.html
bf1634f18964b1ab616a474c5f185680058bbb6a8856431c79ab2a04930b6e53  2022_ne_canvass_book.pdf
6c72a4020802d803ee60f75e51aa5ef1e661f9460f09a348e97c0e6052839be2  2022_nv_election_summary_unofficial.html.gz
ab52971bf0b0274d73cf4039df6e3c7ee3725490fd6cde012909c8fe33e67eb8  2022_nv_official_abstract_of_votes.pdf
6ebb360ef2c6cc409c31edb070df314d75131b12e3b266eefbe02906c9e7184b  2022_ny_general_results_certified.pdf
b14ea74bf85e259ae79fc42983f100bdcb9e71d043b59a047a8af69a129819d1  2022_ny_governor_by_county_split_party.csv
8d04f156cc9df40109a0275ee76271fb383d7bf0d88726b5661f54985523667f  2022_or_abstract_of_votes.pdf
87ce057aa2a5a17a692e981f3e2f4eb4d1aa14005f6db3fb0a7a65314c7aa968  2022_pa_summary_results.xml
953553f194d9741e8b80c17a428cfadaa93efa6744fe01eb64deed2e0cb0e023  2022_tx_election_constants.json
28bee47c3eeaef0da3f443d97fced70b27baffe28fbaed5066045fcd0adc5a85  2022_tx_results_version.json
2760bdd6ae8279d66fd52cc4fd0cb543e99b8f09b8b5595a9bc57c9a98a50aa8  2022_tx_statewide_results.json
6f8faca3acdc554b3be877ded5ca3d73c17b99e9f354ec3d0b1626e579e54a53  2022_vt_canvass_report_statewide_offices.pdf
ef406dc57b30e88c663f9d68c484aadacad34d66279b408204682317b09581b6  2024_nh_general_election_results_page.html.gz
1b0d993f679d54afed35c6c68428ce72d8d81b1d0c1ddd2fe80ec999da22295d  2024_nh_governor.xls
bdeb55e77d8774e03ac024b0898e645041266132dfcfb89812a1a78d5012421a  2024_vt_canvass_report_statewide_offices.pdf
```
