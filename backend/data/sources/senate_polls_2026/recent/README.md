# Recent 2026 Senate general-election polls (fieldwork ending on or after 2026-10-01)

Collected on **2026-10-26**, 16:40-16:55 US Eastern, to check whether the Senate polling averages are stale. All files were downloaded with curl and are saved as served. They were read only as data: no script or code from any downloaded file was run.

It covers 17 races: OH, TX, AK, FL, IA, KS, ME, SC, MI, MS, NC, NH, MN, LA, GA, NE, MT.

`recent_polls_compiled.json` is the derived per-poll table built from these files. Its fields are described under "Compiled table conventions" below. Every other file here is a raw source.

## Sources and files

### VoteHub (poll database behind votehub.com/polls)
| File | URL | Notes |
|---|---|---|
| `votehub_senate_all.json` | https://polling.votehub.com/site/polls?poll_type=us-senator&limit=2000 | Every Senate poll VoteHub has: 730 rows, `total` 730. The `subject` field is "2026 <State>" for general elections. `created_at` is the date VoteHub added the poll. `average_weights` is empty when VoteHub leaves the poll out of its own average. VoteHub has **no Rasmussen rows**. |
| `votehub_averages_list.json` | https://polling.votehub.com/site/averages?limit=200 | VoteHub's list of averages. Every race here except Montana has an `s_2026_xx_02/03` average, all updated around 2026-10-26 20:50 UTC. |

### RealClearPolling data feeds (`https://orig.realclearpolitics.com/poll/race/<id>/polling_data.json`)
Rows with `"type":"poll_rcp_avg"` are in the RCP average. Rows with `"type":"poll"` are listed but not averaged. The `rcp_average` row holds the average itself.

The `lastBuildDate` field can lag behind the content. For example, the NH feed says Oct 22 but already contains a Rasmussen row added Oct 26.

| File | Race id | Feed title / notes |
|---|---|---|
| `rcp_oh_8689.json` | 8689 | Ohio Special - Husted vs. Brown (two-way average) |
| `rcp_oh_multi_9218.json` | 9218 | Ohio Senate - Multi-Candidate |
| `rcp_tx_8867.json` | 8867 | Texas - Paxton vs. Talarico |
| `rcp_tx_3way_8985.json` | 8985 | Texas - Paxton vs. Talarico vs. Brown |
| `rcp_ak_8754.json` | 8754 | Alaska - Sullivan vs. Peltola (final ranked-choice round) |
| `rcp_ak_rcv1_9171.json` | 9171 | Alaska - RCV 1st Round (no average) |
| `rcp_fl_8948.json` | 8948 | Florida Special - Moody vs. Nixon |
| `rcp_ia_8930.json` | 8930 | Iowa - Hinson vs Turek |
| `rcp_ia_3way_9215.json` | 9215 | Iowa - Hinson vs. Turek vs. Laehn |
| `rcp_ks_9106.json` | 9106 | Kansas - Marshall vs. Hamilton (last built Oct 15) |
| `rcp_ks_3way_9221.json` | 9221 | Kansas - Marshall vs. Hamilton vs. Graham |
| `rcp_me_9100.json` | 9100 | Maine - Collins vs. Jackson |
| `rcp_sc_9115.json` | 9115 | South Carolina - Graham Nordone vs. Andrews |
| `rcp_sc_multi_9230.json` | 9230 | South Carolina - Multi-Candidate |
| `rcp_sc_grahamvsandrews_9031.json` | 9031 | Older SC page (Graham vs. Andrews), with no polls since July |
| `rcp_mi_8802.json` | 8802 | Michigan - Rogers vs. El-Sayed (built Oct 26 15:18 -0500) |
| `rcp_mi_multi_9216.json` | 9216 | Michigan - Multi-Candidate |
| `rcp_ms_9233.json` | 9233 | Mississippi - Hyde-Smith vs. Colom. **No average.** Its only row is a "*PLACEHOLDER*" entry (10/24-25, values 1/1). |
| `rcp_nc_8753.json` | 8753 | North Carolina - Whatley vs. Cooper |
| `rcp_nc_3way_9217.json` | 9217 | North Carolina - Whatley vs. Cooper vs. Bray |
| `rcp_nh_8845.json` | 8845 | New Hampshire - Sununu vs. Pappas |
| `rcp_nh_multi_9219.json` | 9219 | New Hampshire - Multi-Candidate |
| `rcp_mn_8922.json` | 8922 | Minnesota - Tafoya vs. Flanagan |
| `rcp_mn_multi_9220.json` | 9220 | Minnesota - Multi-Candidate |
| `rcp_la_9041.json` | 9041 | Louisiana - Letlow vs. Davis. **No polls** (built Jul 7). |
| `rcp_ga_8718.json` | 8718 | Georgia - Collins vs. Ossoff |
| `rcp_ga_3way_9223.json` | 9223 | Georgia - Collins vs. Ossoff vs. Buckley (no October polls) |
| `rcp_ne_9035.json` | 9035 | Nebraska - Ricketts vs. Osborn. **No average row.** Lists only YouGov. |
| `rcp_mt_9034.json` | 9034 | Montana - Alme vs. Bankhead vs. Bodnar vs. Austin |

**How the race ids were found.** The ids for MI, GA, MN, NH and NC come from the `pollingDataUrl` in the RCP pages saved in `../mi`, `../ga` and so on. NE (9035) comes from `polls_id` in `../../ne_senate_2026/rcp_ricketts_vs_osborn_wayback_20261026.html`, and MT (9034) from `../../mt_senate_2026/`. MS (9233), LA (9041) and the multi-candidate feeds were found by requesting feed ids 8680-9290 and reading each feed's `moduleInfo.title`. Those probe downloads were not kept. RCP's www pages are behind a DataDome bot check; the orig.realclearpolitics.com feeds are not.

### Poliwave
| File | URL | Notes |
|---|---|---|
| `poliwave_<st>_sen.html` (17 files) | https://www.poliwave.com/us/<st>/sen-fed | The race page's poll table lists about the 20 most recent polls. It has a sample n but **no LV/RV label**. Poliwave's "(R)"/"(D)" after a pollster name is its own label, not a sponsor flag. |
| `poliwave_poll_sc_impact.html` | https://www.poliwave.com/us/fed/polls/2026oct21-impact-research-d-usfed-s1434 | Poll detail page. It links the Impact memo below. |
| `poliwave_poll_sc_onpoint.html` | https://www.poliwave.com/us/fed/polls/2026oct19-onpointpolitics1-usfed-s1432 | Poll detail page for "onpointpolitics[1]". It says "Source: Not recorded". |
| `poliwave_poll_redbox_s1436.html` | https://www.poliwave.com/us/fed/polls/2026oct23-redbox-research-usfed-s1436 | Linked from the FL table. The page shows the **Michigan** RedBox poll, because the detail slug is shared across states. |

### 270toWin
| File | URL | Notes |
|---|---|---|
| `270towin_<st>_senate_polls.html` (16 files) | https://www.270towin.com/2026-senate-polls/<state-name> | The **date column is a single date** (the release or entry date), not field dates. For example, Fox TX 9/24-28 is shown as 10/01, and UMass Lowell TX 9/18-28 as 10/08. Field dates were taken from the other sources. Rows with class `in_average_calculation` count toward 270toWin's own average. |
| `270towin_ms_senate_polls_404.json` | https://www.270towin.com/2026-senate-polls/mississippi | HTTP 404, body `{"status":"not_available"}`. |

### Pollster and sponsor releases
| File | URL | Notes |
|---|---|---|
| `afwh_redbox_polling_index.html` | https://afightworthhaving.com/polling | The RedBox Research (A Fight Worth Having super PAC) October poll index. Senate polls: FL, KS, MI, NC, OH, all fielded Oct 20-23 and released Oct 25. |
| `afwh_redbox_florida.html`, `afwh_redbox_kansas.html`, `afwh_redbox_michigan.html`, `afwh_redbox_north-carolina.html`, `afwh_redbox_ohio.html` | https://afightworthhaving.com/polling/2026/<state> | Full results. FL: 4,823 LV, Moody 49.6, Nixon 42.8. KS: 1,301 LV, Marshall 45.7, Hamilton 45.0. MI: 2,696 LV, El-Sayed 48.9, Rogers 44.0. NC: 3,292 LV, Cooper 49.8, Whatley 43.5. OH: 2,998 LV, Brown 46.9, Husted 44.2. |
| `freshstartpac_impact_sc_2026-10-15_21_memo.pdf` | https://freshstartpac.org/wp-content/uploads/2026/10/SC-Senate-Track-Public-Memo.pdf | Impact Research memo dated Oct 22: Oct 15-21, n=800 LV, full ballot Andrews 45, Graham 44, Whitener 3, Hackett 2, undecided 5. It names no client. |
| `dfp_alaska_oct_2026.pdf` | https://www.filesforprogress.org/datasets/2026/10/dfp_alaska_oct_2026.pdf | Data for Progress, Oct 8-16, 694 LV. Q15 first round: Peltola 47, Sullivan 44, D. Sullivan Jr. 4, Heikes 1, not sure 3. Q18 final round (N=671): 51/49. |
| `mdw_florida_oct_2026.html` | https://www.mdwcomm.com/media/florida-statewide-poll-october-2026.html | MDW Communications + EDGE Communications, released Oct 14: online, 2,351 LV, Oct 4-10, Moody 47.6, Nixon 42.4. |
| `votehub_verasight_oct_2026_ohio.pdf`, `votehub_verasight_oct_2026_texas.pdf` | https://cdn.votehub.com/pdfs/VoteHub_Verasight_Oct_2026_Ohio_Report_D1CB7735.pdf, https://cdn.votehub.com/pdfs/VoteHub_Verasight_Oct_2026_Texas_Report_D8A925D0.pdf | Saved but **not read**: no PDF text tool was available. The VoteHub API rows were used instead (VoteHub is the sponsor). |

Releases already saved elsewhere in the repo were reused for MT and NE: `../../mt_senate_2026/` (Concord, Peak Insights memo image, Quantus release) and `../../ne_senate_2026/` (NPA, Impact, GBAO and Concord memos). See the READMEs in those folders.

## Compiled table conventions (`recent_polls_compiled.json`)

- **anti_r / r.** The full-ballot (multi-candidate) numbers when the poll reports one; otherwise the only ballot reported. In Alaska, these are the first ranked-choice round. In Montana, anti_r is Bodnar (I), and Bankhead (D) is given in the poll's note.
- **h2h_anti_r / h2h_r.** A separate two-way question, or for Alaska the final ranked-choice round. Null when no separate two-way result was found in a source.
- **released.** VoteHub `created_at` when the poll is in VoteHub. Otherwise the release date, or the RCP row's `updated` timestamp (noted).
- **in_rcp_average.** Whether the poll is a `poll_rcp_avg` row in RCP's main (two-way) feed. It is null where RCP has no average (NE, MS).
- **partisan.** VoteHub's `partisan` flag (REP→"R", DEM→"D"). Where VoteHub has no row, the sponsor or memo affiliation is used (Impact SC, RedBox OH/NC).
- **excluded_pollster.** True for Rasmussen Reports and ActiVote. Per the project rule, they are never used in any average.
- **Conflicting numbers.** Where sources disagree, the value backed by the pollster release or by most aggregators is used, and the poll's `note` records the alternatives.

## Gaps and caveats
- **"onpointpolitics" SC poll (Oct 18-19, n=511, Andrews 45, Graham 42).** It appears on Poliwave only, with no source recorded, and no release was found. Treat it as unverified.
- **VoteHub data errors found:** MT Peak Insights has Alme and Bodnar swapped; MT Quantus has Bodnar and Bankhead swapped; NC ECU reads 53/46 (other sources 50/43); OH and TX VoteHub/Verasight n differs from RCP (531 vs 623 and 601 vs 969).
- **Not resolved:** Emerson TX (48/46 vs 49/48), Quantus GA (51.8/44.9 vs 54/46), GBAO KS (46/41 vs 49/44), GQR MN (50/42 vs 53/44) and Harper NC (49/39 vs 51.6/42.0). The pollster releases were not checked for these.
- **Pollster releases not retrieved for most polls.** The numbers are aggregator values.
- **No poll found** with fieldwork ending on or after Oct 1 for **Louisiana**.

## Update, 2026-10-27 (manual poll check)

Retrieved **2026-10-27 16:21-16:30 UTC** with curl, saved as served (read only as data). Every RCP feed in `build_senate_poll_averages.py`, VoteHub's Senate dump and Poliwave's page for all 35 races were downloaded again and compared with the saved copies; files that changed are overwritten here (git history keeps the Oct 26 versions). `RETRIEVED` in the build script is now 2026-10-27.

| File | URL | Notes |
|---|---|---|
| `rcp_tx_8867.json`, `rcp_me_9100.json`, `rcp_mi_8802.json`, `rcp_nc_8753.json` | `https://orig.realclearpolitics.com/poll/race/<id>/polling_data.json` | The only RCP feeds that changed. TX (built Oct 27 08:17 CT) adds Univision/YouGov 10/13-21 to the average; ME (built Oct 27 05:39) replaces Marist 10/1-4 (RV) with Marist 10/22-25 (LV) and lists Echelon Insights** 10/16-23 unaveraged; MI (lastBuildDate Oct 26 15:19, content Oct 27 08:06) adds Detroit News/Glengariff 10/19-22 and drops Trafalgar 9/28-30 and Fox 9/24-28; NC (lastBuildDate Oct 24, content Oct 26 17:06) adds Quantus 10/24-25. The other feeds were unchanged. |
| `votehub_senate_all.json` | https://polling.votehub.com/site/polls?poll_type=us-senator&limit=2000 | Refreshed. New 2026 rows since Oct 26: ME Marist, SC Targoz, NC Quantus and RedBox, OH RedBox, MI Glengariff and MSU/YouGov, TX Univision/YouGov (all `created_at` Oct 27). No new rows for the other races. |
| `poliwave_me_sen.html`, `poliwave_nc_sen.html`, `poliwave_sc_sen.html` | https://www.poliwave.com/us/<st>/sen-fed | Refreshed (new rows: Marist ME, Quantus NC, Targoz SC). Poliwave's other new rows were RedBox OH (already compiled from its release) and two Rasmussen NH polls (excluded). |
| `marist_maine_oct22-25_2026.html` | https://maristpoll.marist.edu/polls/the-midterm-elections-in-maine-october-2026/ | Marist release: Maine likely voters Oct 22-25, Jackson 49, Collins 47 (LV MOE +/-6.6). |
| `Marist-Poll_Maine-NOS-and-Tables_202610261228-3_43sjl2.pdf` | https://maristpoll.marist.edu/wp-content/uploads/2026/10/Marist-Poll_Maine-NOS-and-Tables_202610261228-3_43sjl2.pdf | Marist tables. Methodology p.1: 1,449 RV (LV n not published). Senate full ballot p.7 (SNVT26R): LV 49/47, another party 1, undecided 3. |
| `univision_texas_october_2026_poll.html` | https://www.univision.com/noticias/politica/poll-univision-texas-latinos | Univision article (published Oct 27): Talarico 50, Paxton 45. |
| `n-univision-texas-october-poll-crosstabs-base-final.pdf` | https://st1.uvnimg.com/f0/3a/9fe2c0c445b7bd44b43fb9236c8e/n-univision-texas-october-poll-crosstabs-base-final.pdf | Base crosstabs: online sample of 1,000 Texas voters, Oct 13-21 (YouGov per VoteHub/RCP). Senate full ballot p.25: 50/45, other 1, undecided 5. |
| `foxcarolina_targoz_scpc_sc_2026-10-26.html` | https://www.foxcarolina.com/2026/10/26/new-poll-shows-neck-and-neck-senate-race-double-digit-lead-governor-sc-midterms/ | FOX Carolina (published Oct 26): South Carolina Policy Council poll by Targoz Market Research, Oct 16-25, 1,200 RV, results among 895 likely or already-voted voters: Graham 47, Andrews 46, Whitener 2, Hackett 1, undecided 4. No sponsor release found. |
| `quantus_nc_senate_2026-10-24_25.html` | https://quantusinsights.org/polling/f/north-carolina-senate-cooper-holds-a-9-point-lead-over-whatley | Quantus release (text is in the page's embedded JSON): 722 LV, Oct 24-25, Cooper 51.4, Whatley 42.8, undecided 3.4; with leaners 52.4/43.4. |
| `wdiv_glengariff_mi_senate_2026-10-27.html` | https://www.clickondetroit.com/news/local/2026/10/27/democratic-candidate-el-sayed-leads-michigan-us-senate-race-new-poll-finds/ | WDIV article (published Oct 27), linked from RCP: Glengariff Group for WDIV/The Detroit News, 600 LV live phone, Oct 19-22: El-Sayed 51.4, Rogers 45.1, undecided 3.6. The Detroit News article returned HTTP 402 (paywall). |
| `msu_ippsr_soss95_release_2026-10-26.html` | https://ippsr.msu.edu/news/msu-poll-shows-benson-large-lead-while-el-sayed-roger-race-tight | MSU IPPSR release (Oct 26): El-Sayed 48, Rogers 45.5. |
| `msu_ippsr_soss95_topline.pdf` | https://ippsr.msu.edu/sites/default/files/soss/soss95.pdf | SOSS 95 topline (YouGov, Oct 2-19): 836 LV; with leaners 48.0/45.5, without 47.7/44.2. The compiled entry was corrected from RCP's 48/46, n=863. |

Compiled-table additions: TX Univision/YouGov; ME Marist (Oct 22-25) and Echelon Insights (Oct 16-23, RCP only, no release found; not in any average); MI Glengariff; NC Quantus; SC Targoz. With these, North Carolina uses RCP's own average again (it now includes a poll newer than RedBox), and South Carolina's recomputed average has three polls (Trafalgar, Impact, Targoz).

### Echelon Insights for NetChoice (added 2026-10-27, after the user pasted the NYT poll list)

Retrieved **2026-10-27 16:33 UTC** with curl. VoteHub (re-downloaded 16:33 UTC, not saved: unchanged for these races) had no rows for these polls yet; RCP listed only the Maine result (Oct 25).

| File | URL | Notes |
|---|---|---|
| `netchoice_echelon_insights_poll_2026-10-27.html` | https://netchoice.org/netchoice-echelon-insights-poll-voters-rank-ai-regulation-far-behind-cost-of-living-want-one-national-ai-standard/ | NetChoice release (published 2026-10-27 14:30 UTC), linking the two PDFs below. |
| `Echelon-Insights-Release-Memo.pdf` | https://netchoice.org/wp-content/uploads/2026/10/Echelon-Insights-Release-Memo.pdf | Echelon memo dated Oct 26. Methodology p.7: 3,644 LV nationwide, Oct 16-23, text-to-web and online; base sample 1,004 plus oversamples FL 515, OH 508, GA 508, IA 403, NE 407, ME 413 (weighted down to national shares). Senate results p.2. |
| `NetChoice-October-2026-Antitrust-Tech-Survey-Topline.pdf` | https://netchoice.org/wp-content/uploads/2026/10/NetChoice-October-2026-Antitrust-Tech-Survey-Topline.pdf | Topline. Senate full ballot with leaners (early voters merged): GA Q12 p.7 Ossoff 55, Collins 40; OH Q16 p.9 Husted 47, Brown 47; ME Q19 p.10 Jackson 51, Collins 44; NE Q21 p.11 Ricketts 47, Osborn 46; FL Q23 p.12 Moody 51, Nixon 43; IA Q26 p.15 Turek 45, Hinson 43. No separate two-way questions. Generic ballot Q7 p.3 (51/46) has no race breakdown. |

The NYT poll list the user pasted (Oct 27) shows the same FL, NE, ME, OH and GA numbers; Iowa is in the release but was not in the pasted excerpt. Effect: Georgia and Iowa are now recomputed (the Echelon poll ended after the latest poll in RCP's average and came out after RCP's last update); Florida, Ohio and Nebraska (already recomputed) gain a poll; Maine stays on RCP's average (Marist 10/22-25 is newer). Follow-up (user decision, Oct 27): the Maine poll is counted in Maine's RCP average ahead of RCP (`RCP_PENDING` / `COUNT_RCP_PENDING` in the build script), since RCP lists it and is expected to add it.

### Cor Strategies for Heritage Action, Texas (added 2026-10-27, from the user's NYT poll list paste)

| File | URL | Notes |
|---|---|---|
| `nyt_poll_list_user_paste_2026-10-27_tx_cor_strategies.txt` | NYT poll list (pasted by the user) | Talarico 44, Paxton 40, Oct 10-15, Republican sponsor Heritage Action. The only record of the Senate numbers. |
| `heritage_action_cor_texas_poll_release_2026-10-26.html` | https://heritageaction.com/press/new-heritage-action-poll-82-of-texas-voters-support-proof-of-citizenship-to-register-to-vote | Retrieved 2026-10-27 17:34 UTC. Release dated Oct 26: Oct 10-15, 1,409 likely Texas voters, MOE 2.61, with Cor Strategies; no Senate numbers. Its linked Daily Signal article (https://www.dailysignal.com/2026/10/23/texas-poll-election-integrity-proof-citizenship-support/) returned 403 (curl and WebFetch) and has no Wayback copy. |

RCP (feed re-downloaded 17:34 UTC), VoteHub and Poliwave did not list it. RCP's Texas average (built Oct 27, polls through 10/21) is current and this poll ended Oct 15, so it is recorded but not averaged.


## Update, 2026-10-28 (manual poll check, from the user's NYT poll list paste)

Retrieved **2026-10-28 11:59-12:03 UTC** with curl, saved as served (read only as data). Every RCP feed in `build_senate_poll_averages.py`, VoteHub's Senate dump and Poliwave's page for all 35 races were downloaded again and compared with the saved copies; files that changed are overwritten here (git history keeps the older versions). `RETRIEVED` in the build script is now 2026-10-28.

| File | URL | Notes |
|---|---|---|
| `nyt_poll_list_user_paste_2026-10-28.txt` | NYT poll list (pasted by the user) | The Senate and national entries of the paste: Suffolk OH (Oct 21-26) 47/44; NYT/Siena MN (Oct 19-26) 54/40, SC (Oct 19-26) 48/48, FL (Oct 19-25) 50/44; Bedrock Polling for the Rainey Center generic ballot (Oct 14-20) 52/44. |
| `rcp_oh_8689.json`, `rcp_fl_8948.json`, `rcp_sc_9115.json`, `rcp_mn_8922.json`, `rcp_ak_8754.json` | `https://orig.realclearpolitics.com/poll/race/<id>/polling_data.json` | The only RCP feeds that changed. OH (lastBuildDate still Oct 25 10:05; content through Oct 27) adds Suffolk 10/21-26 to the average and lists Echelon Insights** 10/16-23 unaveraged; FL (lastBuildDate Oct 24; content through Oct 28) adds NYT/Siena 10/19-26; SC (built Oct 28) adds NYT/Siena 10/19-26 and The Citadel 10/14-25; MN (built Oct 28) adds NYT/Siena 10/19-26; AK (built Oct 27 18:30 CT) drops Quantus 9/28-30. |
| `votehub_senate_all.json` | https://polling.votehub.com/site/polls?poll_type=us-senator&limit=2000 | Refreshed. New 2026 rows: the six Echelon/NetChoice polls (already compiled from the release) and ActiVote FL Oct 17-27 (excluded pollster). None of the polls below is in VoteHub yet. |
| `poliwave_{fl,ga,ia,ne,nh,oh}_sen.html` | https://www.poliwave.com/us/<st>/sen-fed | Refreshed. New rows: Echelon/NetChoice (GA, IA, NE, OH), ActiVote FL, and the two Rasmussen NH polls (excluded). Poliwave has none of the polls below yet. |
| `10_28_2026_ohio_statewide_marginals.pdf`, `10_28_2026_ohio_statewide_tables.pdf` | https://www.suffolk.edu/-/media/suffolk/documents/academics/research-at-suffolk/suprc/polls/other-states/2026/10_28_2026_ohio_statewide_marginals.pdf (and `..._tables.pdf`) | Suffolk University / USA TODAY Network Ohio: 500 likely voters, Oct 21-26. Senate full ballot Q7 (p.2): Brown 46.6, Husted 43.8, Levy 1.6, Redpath (L) 1.6, undecided 4.4, refused 2.0. |
| `suffolk_other_states_polls_2026-10-28.html` | https://www.suffolk.edu/academics/research-at-suffolk/political-research-center/polls/other-states | Suffolk's index page linking the two PDFs (the link RCP gives). |
| `siena_nyt_fl_mn_sc_2026-10-28.html` | https://sri.siena.edu/2026/10/28/nytimes-siena-poll-of-likely-voters-florida-minnesota-and-south-carolina/ | Siena release (Oct 28): FL Moody 50, Nixon 44; MN Flanagan 54, Tafoya 40; SC Andrews 48, Graham 48 ("Graham leads by less than one point"). It links the NYT toplines and crosstabs (https://www.nytimes.com/interactive/2026/10/28/polls/times-siena-{fl,mn,sc}-poll-{toplines,crosstabs}.html), which block automated downloads (curl, headless Chrome and WebFetch all refused) and have no archive copy yet, so the sample sizes (FL 813, MN 752, SC 707 LV) and field dates (10/19-26) are RCP's. The NYT list gives Oct 19-25 for Florida. |
| `citadel_sc_2026-10-27.html` | https://poll.citadel.edu/2026/10/27/sc-voters-look-to-pass-the-torch-in-the-midterms/ | The Citadel Poll release (Oct 27): 1,009 registered voters; Graham leads Andrews by 4. |
| `The-Citadel-Poll-Oct2026.pdf` | https://poll.citadel.edu/wp-content/uploads/2026/10/The-Citadel-Poll-Oct2026.pdf | Report. Oct 14-25, 1,009 RV, 890 LV. Q12 (p.4) LV: Andrews 39, Graham 43, Whitener 1, Hackett 1, not sure 15 (RV 40/35); with planned Ralph Norman write-ins reassigned: 39/42, Norman 2. |
| `Methodology-Statement-202610.pdf` | https://poll.citadel.edu/wp-content/uploads/2026/10/Methodology-Statement-202610.pdf | L2 voter-file sample, phone and text-to-web; LV = would definitely vote or already voted, MOE +/-4. |
| `Crosstabs_SC_Oct2026_lv.xlsx` | https://poll.citadel.edu/wp-content/uploads/2026/10/Crosstabs_SC_Oct2026_lv.xlsx | Likely-voter crosstabs. |

Compiled-table additions: OH Suffolk; FL, MN and SC NYT/Siena; SC The Citadel; FL ActiVote (excluded). Effect: Ohio, Florida and South Carolina use RCP's average again (Rasmussen removed), because the newest poll in each now ends after the polls that had made it stale (RedBox and Echelon in OH and FL; Impact and Targoz in SC), and those polls, which RCP has not averaged, drop out. Minnesota and Alaska stay on RCP's average. Ohio's Echelon/NetChoice poll is listed by RCP but was left out when RCP rebuilt the average with Suffolk; it is not counted (only Maine's is, by the Oct 27 user decision).

### Second check, 2026-10-28 13:48 UTC (St. Pete Polls, Florida; from the user's second NYT poll list paste)

Every RCP feed, VoteHub's Senate dump and Poliwave's 35 race pages were downloaded again. VoteHub had no new rows.

| File | URL | Notes |
|---|---|---|
| `nyt_poll_list_user_paste_2026-10-28_st_pete_fl.txt` | NYT poll list (pasted by the user) | St. Pete Polls for Florida Politics, Oct 25-27: Moody 49, Nixon 45. |
| `rcp_fl_8948.json` | https://orig.realclearpolitics.com/poll/race/8948/polling_data.json | Built Oct 28 08:26 CT: St. Pete Polls 10/25-27 (916 LV, MOE 3.2, 49/45) replaces St. Pete's 10/5-7 poll in the average (9/28-10/27, Moody 49.9, Nixon 42.4, 7 polls). |
| `rcp_sc_9115.json`, `rcp_mn_8922.json` | same pattern | Only row timestamps changed (and the MOE of NYT/Siena's MN row, now 4.1); averages unchanged. |
| `poliwave_mn_sen.html`, `poliwave_sc_sen.html` | https://www.poliwave.com/us/<st>/sen-fed | Now list the NYT/Siena polls (MN 54/40, n 752; SC 48/48, n 707; Oct 19-26), matching RCP. |

The release RCP links, https://floridapolitics.com/archives/827487-final-st-pete-polls-byron-donalds-leads-david-jolly-48-to-46-as-long-as-republicans-show-up/, could not be retrieved: curl and headless Chrome got Florida Politics' "Browser Update Required" block (HTTP 403), WebFetch got HTTP 402, archive.ph has no copy and the Wayback Machine was rate-limiting. St. Pete Polls' own site (https://stpetepolls.org/) lists no 2026 polls. The poll's numbers therefore come from RCP's feed, matching the NYT list.

### Third check, 2026-10-28 17:29 UTC (RCP drops two Florida polls; from the user's third NYT poll list paste)

Every RCP feed, VoteHub's Senate dump and Poliwave's 35 race pages were downloaded again (17:29 UTC) and compared with the saved copies.

| File | URL | Notes |
|---|---|---|
| `rcp_fl_8948.json` | https://orig.realclearpolitics.com/poll/race/8948/polling_data.json | Built Oct 28 08:27 CT: NBC 6/Mason-Dixon 9/28-10/1 and Stetson 10/1-10/9 are out of the average, which is now 10/2-10/27, Moody 49.4, Nixon 43.2, 5 polls (NYT/Siena, St. Pete Polls 10/25-27, co/efficient, UNF, Univision/YouGov). |
| `rcp_sc_9115.json`, `rcp_mn_8922.json` | same pattern | lastBuildDate only (SC 09:42 CT, MN 08:23 CT); rows and averages unchanged. |
| `rcp_ne_9035.json` | https://orig.realclearpolitics.com/poll/race/9035/polling_data.json | Rebuilt Oct 28 10:41 CT (was Oct 7). Now lists Echelon Insights 10/16-23, National Public Affairs 10/15-18 and 10/2-5, and Wedgewood 9/14-15 (excluded pollster); still no average row. Not used by the build (Nebraska is recomputed from the compiled polls, which already have the first three). |
| `votehub_senate_all.json` | https://polling.votehub.com/site/polls?poll_type=us-senator&limit=2000 | Five new 2026 rows, all already compiled from other sources: St. Pete Polls FL 10/25-27, NYT/Siena FL, MN and SC, Suffolk OH. |
| `poliwave_oh_sen.html` | https://www.poliwave.com/us/oh/sen-fed | Now lists Suffolk 10/21-26 (47/44, n 500), matching RCP. |

#### YouGov Blue for 254 Labs, Texas; Victory Insights for Tafoya, Minnesota (same paste)

| File | URL | Notes |
|---|---|---|
| `nyt_poll_list_user_paste_2026-10-28_third.txt` | NYT poll list (pasted by the user) | Verbatim: YouGov Blue for 254 Labs TX Senate (Oct 21-26) 51/43 and governor; Cygnal generic ballot (Oct 23-24) 52/43 (used in `../../polls_2026/`); Victory Insights for Michele Tafoya (R) MN Senate (Oct 21-22) 48/44 and governor. |
| `254labs_tx_statewide_poll_2026-10-28.html` | https://254labs.io/news/2026-10-tx | 254 Labs release, Oct 28: YouGov Blue, Oct 21-26, 1,000 Texas registered voters (online and text-to-web) weighted to 254 Labs' likely-voter targets, including early-vote turnout; MOE about 4.6. Senate: Talarico 51, Paxton 43, 5% undecided (total vote with leaners). Crosstabs are for subscribers only. |
| `254labs_2026-10-tx.pdf` | https://254labs.io/news/2026-10-tx.pdf | The same release as a PDF. |

Neither poll is in RCP, VoteHub or Poliwave yet. Texas: the 254 Labs poll ended after the latest poll in RCP's average (10/21) and came out after RCP's last update (Oct 27), so Texas is recomputed. Minnesota: no release was found (web search; victoryinsights.com is a parked domain), so the poll is recorded from the paste alone, with no n or release date; it ended before NYT/Siena (10/19-26), so Minnesota stays on RCP's average.

#### Partisan sponsors (user decision, 2026-10-28)

Polls with a partisan sponsor are not counted: a named sponsor (in the compiled polls or VoteHub's dump) together with a partisan flag, i.e. a candidate, campaign, party, PAC or partisan group. This includes any poll RCP has averaged; such a poll is matched to RCP's row by end date and the pollster's or sponsor's name (`LEAVE_OUT_PARTISAN_SPONSORS`, `same_poll` in the build script). Pollsters flagged partisan with no named sponsor (Trafalgar, co/efficient, PPP in Alaska, Change Research in Mississippi, Impact Research in South Carolina, Peak Insights) are not affected. Left out as of Oct 28: GBAO for Working Class Majority PAC, Impact Research for Dan Osborn and Concord for Education Reform Now Advocacy (Nebraska); RedBox for A Fight Worth Having (Kansas, Ohio, Florida, Michigan, North Carolina); Change Research for Carolina Forward (in RCP's North Carolina average); The Tyson Group for Alliance for a Better Future (Michigan); Victory Insights for Michele Tafoya (Minnesota); Concord for the Bodnar campaign (Montana); Cor Strategies for Heritage Action (Texas, also in `NOT_COUNTED`).

### Fourth check, 2026-10-28 19:23 UTC (from the user's fourth NYT poll list paste)

Every RCP feed, VoteHub's Senate dump and Poliwave's 35 race pages were downloaded again. No RCP feed changed.

| File | URL | Notes |
|---|---|---|
| `nyt_poll_list_user_paste_2026-10-28_fourth.txt` | NYT poll list (pasted by the user) | High Point University NC Senate (Oct 1-20) Cooper 54, Whatley 40; Clarity Campaign Labs generic ballot (Oct 15-21) 52/44 (see `../../SOURCES.md`, checked, not used: no race breakdown). |
| `votehub_senate_all.json` | https://polling.votehub.com/site/polls?poll_type=us-senator&limit=2000 | New rows: YouGov Blue for 254 Labs TX (partisan flag DEM), The Citadel SC, Victory Insights MN (REP, 1,194 LV), Cor Strategies TX (REP). |
| `poliwave_fl_sen.html`, `poliwave_tx_sen.html` | https://www.poliwave.com/us/<st>/sen-fed | Now list NYT/Siena FL and YouGov Blue TX. |
| `victoryinsights_PollReport_MN-GE-26_10-28-26.pdf` | https://irp.cdn-website.com/07e08705/files/uploaded/PollReport_MN-GE-26_10-28-26.pdf | Victory Insights, Oct 21-22, 1,194 LV, "Commissioned by Michele Tafoya": Senate Flanagan 47.8, Tafoya 44.4 (p.6). Found while collecting governor polls (also saved in `../../gov_polls_2026/`). Replaces the paste-only record; still not counted (partisan sponsor). |

Texas: VoteHub now flags the 254 Labs poll Democratic, so under the partisan-sponsor rule (a named sponsor plus a partisan flag) it no longer counts; with no newer poll left, Texas returns to RCP's average. North Carolina: High Point's poll isn't in RCP, VoteHub or Poliwave and no release was found (HPU's Survey Research Center page lists no October Senate poll), so it is recorded from the paste only; it ended before Quantus 10/24-25, the latest poll in RCP's average.

## Update, 2026-10-29 (manual poll check: CNN/SSRS state polls, user asked)

Every RCP feed, VoteHub's Senate dump and Poliwave's 35 race pages were downloaded again at 12:09 UTC. VoteHub had no new rows (only VoteHub's own average weights and a sponsor-name edit changed), so its saved copy is kept. RCP's `lastBuildDate` again lags the content: Kansas still says Oct 20 and Maine Oct 27, but both feeds have CNN rows timestamped Oct 29.

| File | URL | Notes |
|---|---|---|
| `cnn_ssrs_texas_october_2026.pdf` | https://s3.documentcloud.org/documents/28856724/cnn-poll-conducted-by-ssrs-texas-october.pdf (RCP links https://www.documentcloud.org/documents/28856724-cnn-poll-conducted-by-ssrs-texas-october/) | CNN/SSRS topline, embargoed to Oct 29 5:00 a.m.: 923 registered voters, online and phone, Oct 20-27; likely-voter results weight every respondent by predicted probability of voting, MOE +/-4.2. SENVOTETX: Talarico 49, Paxton 43, neither 5, other 3. GOVVOTETX: Hinojosa 46, Abbott 48. |
| `cnn_ssrs_kansas_october_2026.pdf` | https://s3.documentcloud.org/documents/28856723/cnn-poll-conducted-by-ssrs-kansas-october.pdf | 838 RV, Oct 20-26, LV MOE +/-4.5. SENVOTEKS: Hamilton 49, Marshall 45, neither 4, other 1. GOVVOTEKS: Holscher 45, Masterson 50. |
| `cnn_ssrs_maine_october_2026.pdf` | https://s3.documentcloud.org/documents/28856725/cnn-poll-conducted-by-ssrs-maine-october.pdf | 783 RV, Oct 20-26, LV MOE +/-4.5. SENVOTEME: Jackson 49, Collins 45, neither 4, other 2. GOVVOTEME: Pingree 53, Charles 39 (two-candidate question). |
| `cnn_ssrs_michigan_october_2026.pdf` | https://s3.documentcloud.org/documents/28856720/cnn-poll-conducted-by-ssrs-michigan-october.pdf | 768 RV, Oct 20-27, LV MOE +/-4.7. SENVOTEMI: El-Sayed 49, Rogers 42, neither 5, other 3. GOVVOTEMI: Benson 53, James 41. |
| `cbsdetroit_mitchell_mi_2026-10-28.html` | https://www.cbsnews.com/detroit/news/el-sayed-widens-lead-rogers-michigan-senate-poll/ | Mitchell Research & Communications for CBS Detroit and other Michigan TV stations, Oct 26-27, 636 LV, MOE +/-3.9: El-Sayed 51, Rogers 44, undecided 3. |
| `hpu_yougov_nc_2026-10-28.html` | https://www.highpoint.edu/blog/2026/10/hpu-yougov-poll-north-carolina-likely-voters-weigh-in-on-u-s-senate-race-and-more/ | HPU Poll 128 (HPU Survey Research Center with YouGov), Oct 1-20, 800 RV / 620 LV, released Oct 28: Cooper 54, Whatley 40, Bray (L) 2, Dublin (G) 1. Replaces the paste-only record of Oct 28. |
| `umasslowell_yougov_nh_ma_2026-10-28.html` | https://www.uml.edu/news/press-releases/2026/102826-new-england-polls.aspx | UMass Lowell/YouGov, released Oct 28. New Hampshire, Oct 2-19, 600 LV: Senate Pappas 48, Sununu 41, LaPlante 4; governor Ayotte 48, Warmington 42. Massachusetts, Oct 7-18, 850 LV: Senate Markey 55, Deaton 26; governor Healey 57, Minogue 29, James (I) 4. |
| `DFER-MT-GE-PollFindings-OCT2026.pdf` | https://dfer.org/wp-content/uploads/2026/10/DFER-MT-GE-PollFindings-OCT2026.pdf | Published by Democrats for Education Reform; conducted by Concord Public Opinion Partners, Oct 22-23, 410 LV, MOE +/-4.84. Senate (p.7): Bodnar 39, Alme 38, Bankhead 10, Austin 2. |
| `../al/chism_blueprint_al_2026-10-28.html` | https://www.chismstrategies.com/field-notes/new-alabama-poll-governors-race-a-toss-up-as-tuberville-edges-jones-48--45 | Chism Strategies field note (Oct 28): Blueprint Polling, Oct 22-24, 695 LV, text-to-web, MOE +/-3.72; Senate Moore 48, Wess 40; governor Tuberville 48, Jones 45. "This poll was not sponsored by any outside campaign or organization." |
| `rcp_tx_8867.json`, `rcp_ks_9106.json`, `rcp_me_9100.json`, `rcp_mi_8802.json`, `rcp_nc_8753.json`, `rcp_oh_8689.json`, `../al/rcp_polling_data_9229.json` | https://orig.realclearpolitics.com/poll/race/<id>/polling_data.json | See below. |
| `poliwave_tx_sen.html`, `poliwave_mi_sen.html`, `poliwave_mt_sen.html`, `../al/poliwave_al_sen.html` | https://www.poliwave.com/us/<st>/sen-fed | Now list SSRS TX, Mitchell MI, Concord MT (Oct 22-23) and Chism Strategies (D) AL (Oct 22-24). |

RCP changes:
- **Texas** (built Oct 29 05:41 CT): 10/8-10/27, Talarico 48.6, Paxton 46.5, 13 polls; CNN 10/20-27 (49/43) and TSU/YouGov 10/21-25 (2,000 LV, 49/47) added.
- **Kansas**: 9/8-10/26, Hamilton 46.1, Marshall 45.9, 7 polls; CNN 10/20-26 (49/45) added.
- **Maine**: 9/23-10/26, Jackson 48.7, Collins 47.3, 11 polls; CNN 10/20-26 (49/45) added. Echelon Insights 10/16-23 is still listed but not averaged, so it stays in `RCP_PENDING`.
- **Michigan** (built Oct 28 17:42 CT): 9/28-10/27, El-Sayed 48.8, Rogers 45.6, 9 polls; CNN 10/20-27 (49/42) and CBS News/Mitchell 10/26-27 (51/44) added. Mitchell's Oct 1 poll is now listed but not averaged.
- **North Carolina**: High Point University (Oct 1-20, 54/40) added to the average on Oct 28: 9/27-10/25, Cooper 51.1, Whatley 40.4, 9 polls.
- **Ohio** (lastBuildDate Oct 28 05:56 CT): rebuilt to 10/5-10/26, Brown 47.9, Husted 45.3, 7 polls; InsiderAdvantage 10/21-22 in; NYT/Siena 9/22-10/1, CNN 9/29-10/5 and Bowling Green 9/29-10/9 out.
- **Alabama**: lastBuildDate Oct 20 -> Oct 21; average unchanged.

TSU/YouGov (Texas) is recorded from RCP's row only. The release RCP links, https://www.wfaa.com/article/news/politics/elections/new-poll-talarico-abbott-lead-as-early-voting-in-texas-nears-close/287-7f4cca13-6e1d-433c-9041-727931b591cd, returned HTTP 403 to curl, headless Chrome and WebFetch, as did the same article path on WFAA's TEGNA sister sites. TSU's news page lists no 2026 poll, and a web search found no other copy.

Effects on the averages:
- Texas, Kansas, Maine, Michigan, North Carolina and Ohio stay on RCP's average (Rasmussen removed where present). No compiled poll is newer than the polls RCP added.
- **Alabama** stays recomputed. Chism Strategies' Blueprint poll (Poliwave flags the firm D; the release says it had no sponsor, so it counts like other partisan pollsters without a named sponsor) ended Oct 24, after the latest poll in RCP's average (10/16-17). Moore +14.7 raw, +16.7 two-party (3 polls; was +18.0 / +20.5 with 2 polls).
- **Montana**: the Concord poll is published by Democrats for Education Reform. Its `partisan` field is the sponsor's affiliation (VoteHub has no row), so it is out as partisan-sponsored, like the same firm's poll for Education Reform Now Advocacy in Nebraska. Montana stays on RCP's average.
- **New Hampshire**: UMass Lowell/YouGov (Oct 2-19) is not in RCP's Senate feed, VoteHub or Poliwave, so it is recorded from the release. It ends before Rasmussen 10/20-23, the latest poll in RCP's average, so New Hampshire stays on RCP.
- **Massachusetts**: UMass Lowell/YouGov (Oct 7-18) ends on the same day as the latest poll in RCP's average (Boston Globe/Suffolk 10/10-18), so it is not newer and Massachusetts stays on RCP. Massachusetts is not in the compiled table, so the poll is recorded here only.

### Second check, 2026-10-29 13:33 UTC (from the user's NYT poll list paste)

Every RCP feed, VoteHub's Senate and generic-ballot dumps and Poliwave's 35 race pages were downloaded again. VoteHub had no new Senate rows.

| File | URL | Notes |
|---|---|---|
| `nyt_poll_list_user_paste_2026-10-29.txt` | NYT poll list (pasted by the user) | Verbatim: Tufts generic ballot (Oct 23-27) D 52, R 40 and Trump approval 36/61; David Binder Research for Eric Jones (D) in CA-04 (Oct 15-21), Jones 45, Thompson (D) 35; State Navigate Minnesota governor (Oct 26-28), Klobuchar 52, Demuth 42, Young (G) 3 (see `../../gov_polls_2026/`). |
| `rcp_nh_8845.json` | https://orig.realclearpolitics.com/poll/race/8845/polling_data.json | UMass Lowell 10/2-19 (48/41) added to the average: 9/15-10/23, Pappas 49.4, Sununu 42.7 (lastBuildDate Oct 26 14:25 CT; row Oct 29 07:11 CT). |
| `../ma/rcp_polling_data_8899.json` | https://orig.realclearpolitics.com/poll/race/8899/polling_data.json | UMass Lowell 10/7-18 (55/26) added: 9/14-10/18, Markey 55.6, Deaton 29.0. |
| `poliwave_ks_sen.html`, `poliwave_me_sen.html`, `poliwave_mi_sen.html` | https://www.poliwave.com/us/<st>/sen-fed | Now list the CNN/SSRS polls. The Michigan row gives Oct 20-26 and links Maine's PDF; CNN's Michigan topline says Oct 20-27. |

Not used:
- **Tufts, generic ballot (Oct 23-27).** No release was found at first (Tufts' sites, VoteHub, web search). The user then linked the Tufts Public Opinion Lab PDF, which has House vote by race, so the poll now enters the environment estimate: see `../../SOURCES.md` and `../../polls_2026/tufts_tpol/`.
- **CA-04 (Binder for Eric Jones).** A candidate-sponsored poll, and the House model uses no district polls (CA-04 is a Democrat-vs-Democrat race).

### Third check, 2026-10-29 (MSU Michigan survey, from the user's link)

| File | URL | Notes |
|---|---|---|
| `msu_ippsr_mi_2026_pre_election_report.pdf` | https://polisci.msu.edu/_assets/MI_2026_pre_election_report.pdf | MSU's 2026 Michigan Election Survey, pre-election wave (report dated Oct 29): MSU Department of Political Science with MSU's Office for Survey Research and Verasight, Oct 8-23, 1,383 likely voters, funded by MSU. Senate (MRP, initial response) El-Sayed 48.0, Rogers 41.8, other 3.4, undecided 6.8; governor Benson 48.5, James 38.7. A different survey from the IPPSR/YouGov poll (Oct 2-19) already in RCP's average. |

RCP's Michigan feeds (8802, 9216; governor 8992, 9226) were downloaded again and list the same polls as the saved copies, so those are kept. The MSU poll is not in RCP's average, and it ends Oct 23, before the latest polls RCP averages (CNN 10/20-27, CBS News/Mitchell 10/26-27). So it is not newer, and Michigan stays on RCP's average (Rasmussen removed). The poll is recorded in `recent_polls_compiled.json` with `in_rcp_average: false`.

User decision (Oct 29, after this check): count the MSU poll in RCP's Michigan average anyway (`COUNT_ADDED_TO_RCP` / `ADDED_TO_RCP` in `build_senate_poll_averages.py`). Michigan's average: 9 polls, El-Sayed 49.0, Rogers 45.3, two-party +3.56 -> +3.91.

### Fourth check, 2026-10-29 18:20 UTC (user asked)

Every RCP Senate feed, VoteHub's Senate, governor and generic-ballot dumps and Poliwave's 35 race pages were downloaded again.

| File | URL | Notes |
|---|---|---|
| `rcp_ia_8930.json` | https://orig.realclearpolitics.com/poll/race/8930/polling_data.json | Built Oct 29 12:54 CT. co/efficient 10/28 (Hinson 48, Turek 46) added to the average: 9/29-10/28, Hinson 46.3, Turek 45.6. Echelon Insights 10/16-23 now listed, not averaged. |
| `rcp_sc_9115.json` | https://orig.realclearpolitics.com/poll/race/9115/polling_data.json | East Carolina U. 10/19-24 (Graham 51, Andrews 47) added: 9/28-10/26, Graham 47.7, Andrews 45.0. |
| `rcp_mn_8922.json`, `rcp_fl_8948.json` | same pattern | MN lists Victory Insights 10/21-22 (already compiled), not averaged; FL lastBuildDate only. Averages unchanged. |
| `coefficient_ia_2026-10-29.html` | https://battlegrounds.coefficient.org/ia/ | co/efficient's Iowa page: fielded Oct 28, 1,020 LV, MOE 3.05; Senate Hinson 48, Turek 46; governor Sand 50, Lahn 45. No sponsor named. |
| `ecu_sc_2026-10-29.html` | https://surveyresearch-ecu.reportablenews.com/pr/ecu-poll-finds-graham-leading-andrews-by-four-points | ECU Center for Survey Research release (Oct 29): Oct 19-24, 955 LV, Graham 51, Andrews 47. |
| `grayhouse_ar_2026-10-29.html` | https://www.grayhouse.com/post/arkansas-senate-poll-october-2026-cotton | GrayHouse, Oct 27-28, 509 LV: Cotton 55, Shoffner 39 with leaners (51/37 first ballot). VoteHub lists the sponsor as America One Policies, partisan REP: a partisan-sponsored poll, not counted. Arkansas is averaged from VoteHub's earlier dump and Poliwave, which this poll is not in. |
| `votehub_senate_all.json`, `poliwave_{fl,sc,tx}_sen.html`, `../mn/poliwave_mn_sen.html` | as above | Refreshed. VoteHub's new 2026 rows are all compiled already except GrayHouse AR (above) and Concord for Democrats for Education Reform in Ohio (DEM-sponsored, fielded Aug 29-31: not counted). |

Effects:
- **Iowa** is back on RCP's average: RCP's latest averaged poll (co/efficient, Oct 28) now ends after Echelon (Oct 23), the poll that made it stale. Echelon, listed by RCP but not averaged, drops out. Hinson +0.40 -> +0.78 (two-party -0.44 -> -0.85).
- **South Carolina** stays on RCP's average, now with ECU: Graham +2.0 -> +2.4 (Rasmussen removed).

### Fifth check, 2026-10-29 (A2 Insights Texas, from the user's NYT poll list paste)

| File | URL | Notes |
|---|---|---|
| `nyt_poll_list_user_paste_2026-10-29b.txt` | NYT poll list (pasted by the user) | Verbatim: Texas Senate, A2 Insights, Oct 23-27, Talarico 50, Paxton 47. |
| `a2insights_tx_october_2026.pdf` | https://drive.google.com/file/d/1UACnmnM84Dd1hU0l6iqHNgXkyh5oCelO/view (downloaded via drive.google.com/uc?export=download&id=1UACnmnM84Dd1hU0l6iqHNgXkyh5oCelO; linked from VoteHub) | A2 Insights Texas Statewide Survey: Oct 23-27, 631 LV, online opt-in panel, MOE 4.9, "Sponsor: N/A". Talarico 50.2, Paxton 47.2, other 2.3, undecided 0.3. Senate question only. |
| `votehub_senate_all.json` | https://polling.votehub.com/site/polls?poll_type=us-senator&limit=2000 | Refreshed; the only new 2026 row is this poll (no sponsor, no partisan flag). |

RCP's Texas feed (built Oct 29 05:41 CT) is unchanged and lists only A2's June poll, so the saved copy is kept. The A2 poll is not in RCP's average and ends on Oct 27, the same day as the latest poll RCP averages (CNN 10/20-27), so it is not newer: Texas stays on RCP's average (Rasmussen removed). Recorded with `in_rcp_average: false`.

User decision (Oct 29, after this check): count the A2 Insights poll in RCP's Texas average anyway (`ADDED_TO_RCP` in `build_senate_poll_averages.py`). Texas's average: 13 polls, Talarico 49.0, Paxton 46.6, two-party +2.44 -> +2.49; projection D+1.37 -> D+1.41.

## Update, 2026-10-30 (manual poll check, user asked: "don't just rely on RCP")

Retrieved **2026-10-30 12:04-12:20 UTC**. Every RCP Senate feed, VoteHub's Senate dump and Poliwave's 35 race pages were downloaded again and compared with the saved copies, and every race's Wikipedia page (its poll table lists polls from all sources) was parsed for polls ending Oct 15 or later and matched against the compiled polls. Pollster sites checked for releases since Oct 28: Emerson, Marist, Siena, Quinnipiac, Suffolk, co/efficient, Quantus, State Navigate, Cygnal, Data for Progress, Trafalgar, Fox News, Marquette, UNH. VoteHub had no new Senate rows (its saved copy is kept); no main RCP Senate feed changed its averaged polls. Saved: Poliwave `poliwave_{mi,tx,ia,nc}_sen.html` (pages with new rows; the others changed only in formatting) and the multi-candidate RCP feeds `rcp_ia_3way_9215.json`, `rcp_tx_3way_8985.json`, `rcp_nh_multi_9219.json`, `rcp_nc_3way_9217.json` (not used by the build).

| File | URL | Notes |
|---|---|---|
| `x_joshorton_2115882056081346742_fxtwitter.json`, `x_joshorton_2115883461076545615_fxtwitter.json` | https://api.fxtwitter.com/2/status/2115882056081346742 (https://x.com/joshorton/status/2115882056081346742) and .../2115883461076545615 | Posts (Oct 29) by Josh Orton, president of Demand Justice: "NEW SCOTUS MICHIGAN POLL for Demand Justice: [Upswing - Oct 24-28, N505, LV, MOE 4.4]"; "Senate head-to-head: El-Sayed leads Rogers 50%-45%". Wikipedia cites the second post. |

The only new Senate poll found is **Upswing Research for Demand Justice, Michigan** (Oct 24-28, 505 LV, El-Sayed 50, Rogers 45): a partisan sponsor (progressive advocacy group), so it is recorded but not counted. It is not in RCP or VoteHub; Poliwave lists it as "Upswing Research (D)". Other new rows on Poliwave: ActiVote TX Oct 22-28 (excluded pollster). Michigan stays on RCP's average (plus MSU/Verasight, user decision Oct 29). No average changed; `RETRIEVED` is now 2026-10-30, which moves only the as-of date of the recomputed averages (AL, GA, MS, NE, AR, ID).

### Washington Post-Schar School, Kansas (Oct 30, from the user's link)

| File | URL | Notes |
|---|---|---|
| `wapo_schar_kansas_2026-10-30.html` | https://www.washingtonpost.com/tablet/2026/10/30/oct-22-26-2026-washington-post-schar-school-kansas-poll/ | Saved with headless Chrome at 12:33 UTC (curl timed out). The release page ("Statewide survey of Kansas likely voters", Oct 30, 8:00 a.m. EDT) links the topline below. |
| `wapo_schar_kansas_topline_2026-10-30.pdf` | https://www.washingtonpost.com/documents/91bad124-1d3a-437b-b1ba-07af61cb729d.pdf | Fetched from the page's origin in headless Chrome at 12:33 UTC (curl got an HTTP/2 error). Telephone and text-to-web, Oct 22-26, 801 likely voters (L2 registered-voter sample, every voter given a probability of voting), MOE +/-3.9, fieldwork by Braun Research, sponsored by The Washington Post and George Mason University's Schar School. Q2 Senate: Hamilton 52, Marshall 43, Graham (L) 4; Q3 summary with the two-candidate follow-up: Hamilton 54, Marshall 44. Q5 governor: Holscher 51, Masterson 45. Note on p.1: "significantly higher cooperation rates among registered Republicans than Democrats and additional signs of nonresponse error". |
| `rcp_ks_9106.json`, `rcp_ks_3way_9221.json` | https://orig.realclearpolitics.com/poll/race/9106/polling_data.json, .../9221/... | Re-downloaded 12:34 UTC. RCP added the poll (row Oct 30 07:27 CT) as "Washington Post" 10/22-26, 54/44 in the two-way feed and 52/43/4 in the three-way feed, both averaged. Two-way average 9/15-10/26, Hamilton 47.6, Marshall 45.1, 7 polls (co/efficient 9/8-10 out). |

Effect: Kansas stays on RCP's average, Hamilton +0.31 -> +2.62 two-party; projection R+1.2 -> D+0.4 (P(Hamilton) 0.40 -> 0.53), the model alone being R+4.7. Senate: 52 -> 53 D-leaning seats, P(D control) 0.704 -> 0.723 (0.684 -> 0.706 without independents).

### Counting the polls RCP leaves out (user decision, Oct 30)

`COUNT_RCP_LEFT_OUT` in `build_senate_poll_averages.py` (and the governor build) is now on: in a race that uses RCP's average, the latest poll by each pollster RCP doesn't average, or a newer poll by one it does, is counted when it started on or after the start of RCP's averaging window and passes the usual rules. Polls VoteHub marks as campaign or party internals are skipped (`votehub_internal`, from `votehub_senate_all.json`), and so are the polls in `LEFT_OUT_PARTISAN_LEANING` (user: "if your inclination is that it is sponsored by a partisan leaning group, don't add it"): Impact Research SC (memo posted by Fresh Start PAC), Targoz for the South Carolina Policy Council, MDW / EDGE Communications FL. Pollsters are matched across RCP's and the compiled names through `FIRM_ALIASES`. Added: Echelon Insights for NetChoice (OH, FL, IA), Pollfinity (TX), National Public Affairs (IA, NH), Suffolk Oct 1-4 (IA; in RCP's three-way average but not its two-way one) and SurveyUSA NC as SurveyUSA dates it (Oct 7-11, same 54/40 as RCP's Oct 1-7 row). Skipped as internals per VoteHub: GBAO KS (Sep 30-Oct 4), Peak Insights MT (Oct 7-12), Public Opinion Strategies for Mike Rounds SD (Oct 12-16).

### Campaign and party internals (Oct 30)

`LEAVE_OUT_VOTEHUB_INTERNAL` (on): a poll VoteHub marks as a campaign or party internal, or whose sponsor carries a partisan flag, counts as partisan-sponsored even when the compiled record names no sponsor. Found while checking the left-out polls: **Idaho**'s only recent poll, VoteNexus (Oct 21-22, 700 LV, Risch 49, Achilles 43), was "Commissioned by Knock Every Door PAC and Todd Achilles for Idaho" (`../id/poliwave_id_sen.html`; VoteHub: internal, DEM), so Idaho now uses the model alone (projection R+18.3 -> R+24.1, P(Achilles) 0.001 -> <0.001). No other counted Senate poll is affected.

### Emerson, Kansas (Oct 30, from the user's link)

| File | URL | Notes |
|---|---|---|
| `emerson_kansas_october_2026.html` | https://emersoncollegepolling.com/october-2026-kansas-poll-hamilton-maintains-edge-over-marshall/ | Release (Oct 30), retrieved 13:17 UTC: Oct 26-28, 800 Kansas likely voters, +/-3.5. Senate Hamilton 49, Marshall 45, Graham 3, undecided 3; with leaners 50/47. Governor Masterson 50, Holscher 46; with leaners 53/48. |
| `emerson_kansas_october_2026_full_results.xlsx` | https://docs.google.com/spreadsheets/d/1Fsg1YqnPjM1kKMkAQIhpoBRW3J1vwCH0 (export ?format=xlsx) | 'Topline Results': Senate 48.7 / 45.2 / 2.9 / 3.2, combined vote 49.5 / 47.1 / 3.4; governor 46.3 / 50.0 / 3.7, combined 47.5 / 52.5. |
| `rcp_ks_9106.json`, `rcp_ks_3way_9221.json` | https://orig.realclearpolitics.com/poll/race/9106/polling_data.json, .../9221/... | Re-downloaded 13:17 UTC (built Oct 30 07:32 CT): RCP added "Emerson*" 10/26-28 at 50/47 (the combined vote) in place of its 9/15-16 poll; two-way average 9/22-10/28, Hamilton 48.3, Marshall 45.7, 7 polls. |

Effect: Kansas stays on RCP's average, Hamilton +2.62 -> +2.74 two-party; projection D+0.4 -> D+0.5 (P 0.53 -> 0.54). Senate P(D control) 0.724 -> 0.725.

### TPOR as a partisan-leaning sponsor (Oct 30, from the user's link to Steven David's Texas poll-path page)

The page's poll table (`stevenrdavid_texas_poll_path_2026-10-30.html`, https://votes.stevenrdavid.com/texas/poll-path/, retrieved 15:20 UTC; rendered table in `stevenrdavid_texas_poll_path_polls_tab_2026-10-30.txt`) marks TPOR and Pollfinity "(political sponsor)". Both were in our Texas averages. TPOR names no outside sponsor, but Texas Public Opinion Research is run by a Democratic strategist, so it is now a partisan-leaning sponsor (user decision Oct 30: "if your inclination is that it is sponsored by a partisan leaning group, don't add it"; `PARTISAN_LEANING_SPONSORS`, setting `LEAVE_OUT_PARTISAN_LEANING_SPONSORS`), and its Oct 15-18 poll comes out of RCP's Texas averages.

| File | URL | Notes |
|---|---|---|
| `texastribune_tpor_talarico_paxton_2026-07-28.html` | https://www.texastribune.org/2026/07/28/texas-senate-poll-james-talarico-ken-paxton-july-2026/ | "TPOR labels itself as a nonpartisan public opinion research group. It is directed by Democratic strategist Luke Warford." "Warford is also a founding partner of Agave Democratic Infrastructure Fund, a political action committee dedicated to building Democratic campaign infrastructure in Texas." |
| `tpr_the_source_tpor_warford_2024-10-14.html` | https://www.tpr.org/podcast/the-source/2024-10-14/polling-checks-texas-voters-priorities | "Luke Warford is the director of Texas Public Opinion Research. Warford is a former statewide Democratic candidate in Texas and Chief Strategy Officer of the Texas Democratic Party before running for the Texas Railroad Commission in 2022." |
| `tpor_october_poll_2026-10-23.html`, `tpor_about_2026-10-30.html` | https://texaspublicopinionresearch.substack.com/p/october-poll-in-texas-general-election ; https://texaspublicopinionresearch.substack.com/about | The release (Oct 15-18, 969 LV: Talarico 51, Paxton 47; Abbott 51, Hinojosa 48) and TPOR's "nonpartisan initiative" self-description; no funder named. VoteHub lists the poll as fielded by Slingshot Strategies (a Democratic consulting firm) for TPOR, with no partisan flag; Poliwave labels the sponsor (D). |

Effect: RCP's Texas Senate average without TPOR, D+2.57 -> D+2.46 (13 polls); projection D+1.6 -> D+1.5. Governor average R+2.67 -> R+2.64 (11 polls). No other race has a TPOR poll.
