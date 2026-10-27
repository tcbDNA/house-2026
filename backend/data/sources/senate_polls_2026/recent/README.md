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
