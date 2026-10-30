# 2026 governor general-election polls (fieldwork ending on or after 2026-09-01)

Collected on **2026-10-28, 18:25-18:44 UTC**, for the governor model's polling averages. It covers all 36 races on Nov 3, 2026: AL AK AZ AR CA CO CT FL GA HI ID IL IA KS ME MD MA MI MN NE NV NH NM NY OH OK OR PA RI SC SD TN TX VT WI WY.

All files were downloaded with curl (browser user agent) and are saved as served. They were read only as data: nothing in them was run. Parsing used `python3 -I` with scripts kept outside the repo (in the session scratchpad: `gov_common.py`, `gov_cluster.py`, `gov_overrides.py`, `gov_compile.py`, `gov_verify.py`, plus `pdf_text.py`/`html_text.py` text dumpers).

`gov_polls_compiled.json` is the derived per-poll table (268 polls). Every other file here is a raw source.

## Sources and files

### VoteHub
| File | URL | Retrieved (UTC) | Notes |
|---|---|---|---|
| `votehub_governor_all.json` | https://polling.votehub.com/site/polls?poll_type=governor&limit=2000 | 2026-10-28 18:25:50 | 673 rows (`total` 673); 274 are 2026 general-election rows ending on or after Sept 1. `created_at` = date VoteHub added the poll; empty `average_weights` = VoteHub leaves it out of its own average. No rows for CO, HI or WY. VoteHub has no Rasmussen rows. (Byte-identical to `../governors_2026/votehub_governor_all_2026-10-28.json`, saved by the roster task a few minutes earlier.) |

### RealClearPolling feeds (`https://orig.realclearpolitics.com/poll/race/<id>/polling_data.json`)
Retrieved 2026-10-28 18:33:46-18:34:16 UTC. Rows with `"type":"poll_rcp_avg"` are in the RCP average, `"poll"` rows are listed but not averaged, and the `rcp_average` row is the average itself. As with the Senate feeds, `lastBuildDate` can lag the content (the Alaska feed says Oct 20 but has an ASR row updated Oct 27).

**How the ids were found.** RCP's www pages sit behind a bot check, so feed ids 8500-9450 were requested one by one (0.2 s apart) and each feed's `moduleInfo.title` was read. Ids above 9234 return 404 (9234 is the newest feed, a House race). The probe downloads were not kept. Every 2026 governor feed with the general-election nominees is saved below; the other governor feeds found were primaries, runoffs, superseded match-ups (e.g. 8682-8687 Arizona, 8848-8851/8912-8921 Minnesota with other Republicans) and a set of "Open"/"X vs. Republican" placeholders created Aug 2025 (8804-8839) with no polls. For CO, HI, ID, OK and WY only such placeholders exist, so those are saved to document that RCP has no feed with the nominees.

| File | Race id | Feed title | lastBuildDate | Rows | RCP average |
|---|---|---|---|---|---|
| `rcp_gov_al_8891.json` | 8891 | 2026 Alabama Governor - Tuberville vs. Jones | 21 Oct 2026 12:31 | 4 | 9/21 - 10/17: Tuberville 50.7, Jones 38.7 |
| `rcp_gov_ak_9190.json` | 9190 | 2026 Alaska Govenor - Wilson vs. Kreiss-Tompkins (final RCV round) | 20 Oct 2026 13:52 | 6 | 9/8 - 10/25: Kreiss-Tomkins 53.3, Wilson 46.8 |
| `rcp_gov_ak_rcv1_9016.json` | 9016 | 2026 Alaska Governor - RCV 1st Round | 20 Oct 2026 13:53 | 9 | no average |
| `rcp_gov_az_8683.json` | 8683 | 2026 Arizona Governor - Biggs vs. Hobbs | 27 Oct 2026 13:15 | 15 | 7/26 - 10/25: Hobbs 49.6, Biggs 39.0 |
| `rcp_gov_az_multi_9225.json` | 9225 | 2026 Arizona Governor - Multi-Candidate | 19 Oct 2026 14:35 | 4 | 8/10 - 10/8: Hobbs 48.7, Biggs 34.3, Hourihan 2.0, Lombardo 1.3 |
| `rcp_gov_ar_3way_9121.json` | 9121 | 2026 Arkansas Governor - Sanders vs. Love vs. Shelby | 19 Oct 2026 12:39 | 2 | no average |
| `rcp_gov_ca_9014.json` | 9014 | 2026 California Governor - Hilton vs. Becerra | 28 Oct 2026 10:46 | 12 | 9/15 - 10/24: Becerra 57.6, Hilton 34.0 |
| `rcp_gov_co_open_8809.json` | 8809 | 2026 Colorado Governor - Open (placeholder) | 15 May 2026 14:57 | 0 | no average |
| `rcp_gov_ct_9118.json` | 9118 | 2026 Connecticut Governor - Fazio vs. Lamont | 19 Oct 2026 12:12 | 10 | 9/16 - 10/12: Lamont 53.6, Fazio 37.6 |
| `rcp_gov_fl_8881.json` | 8881 | 2026 Florida Governor - Donalds vs. Jolly | 28 Oct 2026 09:25 | 17 | 10/2 - 10/27: Donalds 48.8, Jolly 43.8 |
| `rcp_gov_ga_9028.json` | 9028 | 2026 Georgia Governor - Jackson vs. Lance Bottoms | 20 Oct 2026 05:51 | 15 | 9/15 - 10/17: Jackson 47.8, Lance Bottoms 46.6 |
| `rcp_gov_hi_placeholder_8813.json` | 8813 | 2026 Hawaii Governor - Green vs. Republican (placeholder) | 25 Aug 2025 15:35 | 0 | no average |
| `rcp_gov_id_placeholder_8814.json` | 8814 | 2026 Idaho Governor - Little vs. Democrat (placeholder) | 25 Aug 2025 15:37 | 0 | no average |
| `rcp_gov_il_8904.json` | 8904 | 2026 Illinois Governor - Bailey vs. Pritzker | 06 Oct 2026 10:30 | 2 | no average |
| `rcp_gov_ia_9032.json` | 9032 | 2026 Iowa Governor - Lahn vs. Sand | 21 Oct 2026 16:04 | 20 | 10/5 - 10/19: Sand 50.6, Lahn 44.4 |
| `rcp_gov_ks_9017.json` | 9017 | 2026 Kansas Governor - Masterson vs. Holscher | 06 Oct 2026 15:19 | 4 | 9/8 - 10/4: Masterson 49.5, Holscher 43.8 |
| `rcp_gov_me_9030.json` | 9030 | 2026 Maine Governor - Charles vs. Pingree | 27 Oct 2026 05:38 | 18 | 9/17 - 10/25: Pingree 49.3, Charles 39.8 |
| `rcp_gov_me_3way_9101.json` | 9101 | 2026 Maine Governor - Charles vs. Pingree vs. Bennett | 27 Oct 2026 12:19 | 12 | 9/17 - 10/25: Pingree 48.5, Charles 39.3, Bennett 7.5 |
| `rcp_gov_md_9222.json` | 9222 | 2026 Maryland Governor - Cox vs. Moore | 06 Oct 2026 10:06 | 1 | no average |
| `rcp_gov_ma_8937.json` | 8937 | 2026 Massachusetts Governor - Minogue vs. Healey | 19 Oct 2026 13:20 | 11 | 9/14 - 10/18: Healey 56.0, Minogue 34.5 |
| `rcp_gov_mi_8992.json` | 8992 | 2026 Michigan Governor - James vs. Benson | 26 Oct 2026 15:18 | 25 | 9/24 - 10/22: Benson 50.5, James 43.3 |
| `rcp_gov_mi_multi_9226.json` | 9226 | 2026 Michigan Governor - Multi-Candidate | (no date: 31 Dec 1969) | 2 | 9/16 - 9/21: Benson 48.0, James 36.0, Hudson 2.0, Campbell 1.5, Brandenburg 0.0 |
| `rcp_gov_mn_8915.json` | 8915 | 2026 Minnesota Governor - Demuth vs. Klobuchar | 16 Oct 2026 21:53 | 11 | 10/2 - 10/25: Klobuchar 50.5, Demuth 39.8 |
| `rcp_gov_ne_9136.json` | 9136 | 2026 Nebraska Governor - Pillen vs. Walz | 28 Oct 2026 10:43 | 10 | no average |
| `rcp_gov_nv_8874.json` | 8874 | 2026 Nevada Governor - Lombardo vs. Ford | 21 Sep 2026 10:20 | 11 | 9/5 - 9/26: Lombardo 42.0, Ford 42.0 |
| `rcp_gov_nh_8953.json` | 8953 | 2026 New Hampshire Governor - Ayotte vs. Warmington | 27 Oct 2026 05:49 | 14 | 9/15 - 10/23: Ayotte 50.8, Warmington 41.3 (includes Rasmussen) |
| `rcp_gov_nh_3way_9227.json` | 9227 | 2026 New Hampshire Governor - Ayotte vs. Warmington vs. Villee | 19 Oct 2026 14:41 | 2 | no average |
| `rcp_gov_nm_9029.json` | 9029 | 2026 New Mexico Governor - Hull vs. Haaland | 05 Oct 2026 11:04 | 3 | 9/25 - 10/9: Haaland 48.0, Hull 41.5 |
| `rcp_gov_ny_8742.json` | 8742 | 2026 New York Governor - Blakeman vs. Hochul | 28 Oct 2026 10:44 | 17 | 9/11 - 10/25: Hochul 52.5, Blakeman 41.0 |
| `rcp_gov_oh_8720.json` | 8720 | 2026 Ohio Governor - Ramaswamy vs. Acton | 24 Oct 2026 12:27 | 25 | 9/29 - 10/26: Acton 48.6, Ramaswamy 44.3 |
| `rcp_gov_oh_3way_9228.json` | 9228 | 2026 Ohio Governor - Ramaswamy vs. Acton vs. Kissick | 21 Oct 2026 13:07 | 6 | 9/23 - 10/13: Acton 47.8, Ramaswamy 44.4, Kissick 4.2 |
| `rcp_gov_ok_open_8829.json` | 8829 | 2026 Oklahoma Governor - Open (placeholder) | 25 Aug 2025 16:11 | 0 | no average |
| `rcp_gov_or_9027.json` | 9027 | 2026 Oregon Governor - Drazan vs. Kotek | 30 Sep 2026 10:40 | 6 | no average |
| `rcp_gov_pa_8860.json` | 8860 | 2026 Pennsylvania Governor - Garrity vs. Shapiro | 22 Oct 2026 10:10 | 19 | 9/15 - 10/18: Shapiro 57.2, Garrity 33.4 |
| `rcp_gov_ri_multi_9119.json` | 9119 | 2026 Rhode Island Governor - Multi-Candidate | 21 Oct 2026 12:29 | 4 | no average |
| `rcp_gov_sc_9025.json` | 9025 | 2026 South Carolina Governor - Wilson vs. Johnson | 28 Oct 2026 09:49 | 3 | 10/14 - 10/26: Wilson 48.7, Johnson 37.3 |
| `rcp_gov_sd_9231.json` | 9231 | 2026 South Dakota Governor - Rhoden vs. Ahlers | 19 Oct 2026 13:35 | 1 | no average |
| `rcp_gov_tn_8761.json` | 8761 | 2026 Tennessee Governor - Blackburn vs. Green | 03 Sep 2026 10:46 | 2 | 8/5 - 8/26: Blackburn 52.0, Green 31.0 (stale; includes an Aug 2025 Quantus poll) |
| `rcp_gov_tx_8910.json` | 8910 | 2026 Texas Governor - Abbott vs. Hinojosa | 24 Oct 2026 08:56 | 42 | 10/5 - 10/21: Abbott 49.6, Hinojosa 46.4 |
| `rcp_gov_tx_3way_9200.json` | 9200 | 2026 Texas Governor - Abbott vs. Hinojosa vs. Dixon | 21 Oct 2026 16:05 | 16 | 9/8 - 10/19: Abbott 48.7, Hinojosa 45.3, Dixon 1.7 |
| `rcp_gov_vt_9209.json` | 9209 | 2026 Vermont Governor - Scott vs. Janoo | 28 Sep 2026 12:21 | 2 | no average |
| `rcp_gov_wi_9105.json` | 9105 | 2026 Wisconsin Governor - Tiffany vs. Crowley | 28 Oct 2026 12:33 | 8 | 8/12 - 10/22: Crowley 48.7, Tiffany 43.7 |
| `rcp_gov_wy_open_8839.json` | 8839 | 2026 Wyoming Governor - Open (placeholder) | 25 Aug 2025 16:27 | 0 | no average |

**RCP id per race (the feed whose average is "the RCP average" in the compiled table):** AL 8891, AK 9190 (final round; 9016 first round), AZ 8683 (multi 9225), AR none (9121 three-way, no average), CA 9014, CO none, CT 9118, FL 8881, GA 9028, HI none, ID none, IL none (8904, no average), IA 9032, KS 9017, ME 9030 (three-way 9101 also averaged), MD none (9222, no average), MA 8937, MI 8992 (multi 9226), MN 8915, NE none (9136, no average), NV 8874, NH 8953 (three-way 9227, no average), NM 9029, NY 8742, OH 8720 (three-way 9228), OK none, OR none (9027, no average), PA 8860, RI none (multi 9119, no average), SC 9025, SD none (9231, no average), TN 8761, TX 8910 (three-way 9200), VT none (9209, no average), WI 9105, WY none.

**No RCP average (13):** AR, CO, HI, ID, IL, MD, NE, OK, OR, RI, SD, VT, WY. Stale RCP averages: TN (built Sept 3, Aug polls), NV (built Sept 21), NM (Oct 5), KS (Oct 6); AZ's window starts 7/26 and WI's 8/12.

### Poliwave: no governor pages
Poliwave was checked for about 10 minutes and has no governor polling. `https://www.poliwave.com/us/tx/polls` says "Polling for this jurisdiction is coming soon"; its national poll database (`/us/fed/polls`) only has Senate, House, generic-ballot and approval questions (office codes `senate`, `house`); `/us/tx/{gov,gov-st,gov-sta,governor,gov-state,gov-tx,gov-sub,gov-prov,gov-fed,governor-st,exec}` and `/us/{governor,governors,gov}` all return 404; the sitemap returns 403 (Cloudflare). Nothing was saved (the probe pages were kept only in the session scratchpad).

### Pollster and sponsor releases (Alaska, Georgia, Vermont, and conflicts)
| File | URL | Retrieved (UTC) | Notes |
|---|---|---|---|
| `asr_x_2107585990869348810_fxtwitter_conversation.json` | https://api.fxtwitter.com/2/conversation/2107585990869348810 (thread https://x.com/The_Real_ASR/status/2107585990869348810) | 18:29:07 | Alaska Survey Research thread, Oct 6: Oct 1-3, 1,512 LV. Round 1 KT 48, Wilson 27, Bronson 15, Taylor 10; round 2 50/30/20; final 54/46. |
| `asr_x_2112415183226429942_fxtwitter_conversation.json` | https://api.fxtwitter.com/2/conversation/2112415183226429942 (https://x.com/The_Real_ASR/status/2112415183226429942) | 18:29:07 | ASR thread, Oct 20: Oct 15-18, 2,149 RV / 1,568 LV. Round 1 50/30/12/8; round 2 51/33/16; final 55/45. |
| `asr_x_2114855199819051178_fxtwitter_conversation.json` | https://api.fxtwitter.com/2/conversation/2114855199819051178 (https://x.com/The_Real_ASR/status/2114855199819051178) | 18:29:07 | ASR thread, Oct 26: Oct 23-25, 1,068 LV. Round 1 50.7/30.6/12.1/6.6; round 2 51.4/33.5/15.1; final 53.4/46.6 (Oct 15-18 in parentheses: 49.9/29.9/12.3/7.9, final 54.7/45.3). X itself needs a login; fxtwitter's public API returns the thread text as JSON. |
| `aarp_alaska_2026_midterm_poll.html` | https://www.aarp.org/pri/topics/voter-research/politics/2026-midterm-election-poll-alaska/ | 18:29:44 | Fabrizio Ward (R) / Impact Research (D) for AARP, 800 LV, Sept 8-11: initial 40/20, Bronson 14, Taylor 7; after RCV 55/45. |
| `coefficient_battlegrounds_ak.html` | https://battlegrounds.coefficient.org/ak/ | 18:29:44 | co/efficient, 799 LV, Sept 14-17: KT 43, Wilson 20, Bronson 17, Taylor 6, undecided 14. No final round. |
| `cygnal_AK_GOV_Memo.pdf` | https://www.cygn.al/wp-content/uploads/2026/10/AK_GOV_Memo.pdf | 18:29:44 | Cygnal memo (Sept 30, to "Interested Parties"), 502 LV, Sept 24-27: KT 44, Wilson 24, Taylor 9, Bronson 8, undecided 15. No final round. |
| `siena_nyt_gubernatorial_2026-10-04.html` | https://sri.siena.edu/2026/10/04/nytimes-siena-poll-of-likely-voters-gubernatorial-races-2/ | 18:29:44 | NYT/Siena release (AK, IA, KS, OH, TX). AK first choice 40/20/15/11. The NYT toplines it links were not fetched (they blocked automated downloads in the Senate check). |
| `dfp_alaska_blog_2026-10-20.html` | https://www.dataforprogress.org/blog/2026/10/20/every-statewide-race-in-alaska-is-close-as-7-in-10-voters-worry-about-affording-gas-and-food | 18:29:44 | DFP, 694 LV, Oct 8-16: first choice 46/28/12/9; final round 53/47. The DFP PDF is already in `../senate_polls_2026/recent/dfp_alaska_oct_2026.pdf`. |
| `statenavigate_ga_statewide_poll_october_2026.html` | https://projects.statenavigate.com/interactives/ga/statewide-poll-october-2026/ | 18:30:46 | State Navigate GA: Bottoms 50, Jackson 47 with leaners; 2 undecided, 2 voted/don't remember. |
| `quantus_ga_two_weeks_out_2026-10.html` | https://quantusinsights.org/polling/f/georgia-two-weeks-out-ossoff-ahead-down-ballot-near-even | 18:30:46 | Quantus GA, 755 LV, Oct 15-17: Jackson 48.2, Bottoms 46.6, undecided 4.5; leaners 49.0/47.5. |
| `insideradvantage_ga_jamesmagazine_2026-10-14.html` | https://jamesmagazinega.com/2026/10/14/georgia-governors-poll-from-insideradvantage-jackson-maintains-slight-edge/ | 18:30:46 | InsiderAdvantage GA, 800 LV, Oct 12-13: 49/47, undecided 4. |
| `ajc_gbao_ga_2026-10.html` | https://www.ajc.com/politics/2026/10/rick-jackson-has-outspent-keisha-lance-bottoms-but-democratic-enthusiasm-has-the-race-knotted/ | 18:30:46 | AJC poll by UGA SPIA, 1,000 LV, Oct 7-15: Jackson 46, Bottoms 45, 8 undecided (VoteHub says GBAO, RV, n=2000). |
| `vpr_braun_vt_poll_2026-09-28.html` | https://www.vermontpublic.org/local-news/2026-09-28/vermont-general-election-poll-results-2026 | 18:30:46 | Vermont Public 2026 Poll results page (links the XLSX). |
| `unh_survey_center_polls_1006.html` | https://scholars.unh.edu/survey_center_polls/1006/ | 18:30:46 | UNH Vermont poll landing page (Sept 24 release). |
| `unh_vt_gmsp_2026-09-24_403.html` | https://scholars.unh.edu/cgi/viewcontent.cgi?article=2005&context=survey_center_polls | 18:31:36 | **HTTP 403** (the UNH Vermont PDF could not be retrieved). |
| `statenavigate_vt_scott_3pt_lead_2026-10.html` | https://articles.statenavigate.com/vt/phil-scott-has-a-3-point-lead-in-state-navigates-vermont-governor-poll/ | 18:30:46 | State Navigate VT article (Oct 7). |
| `statenavigate_vt_final_poll_2026-10.html` | https://articles.statenavigate.com/vt/final-vermont-governor-poll-has-phil-scott-holding-a-3-point-lead/ | 18:30:46 | State Navigate VT final poll (Oct 27): 1,752 LV, Oct 23-25, Scott 49, Janoo 46, minor candidates 2 combined, undecided 3. |
| `statenavigate_vt_statewide_poll_october_2026.html` | https://projects.statenavigate.com/interactives/vt/statewide-poll-october-2026/ | 18:30:46 | State Navigate VT, 948 LV, Oct 2-4: 46/43 with leaners, other candidates 4 combined, don't know 8; initial 43/41/2/14. |
| `vermontpublic_2026_poll_full_results_likely_voters.xlsx` | https://app.vermontpublic.org/poll/2026/vermontpublic-2026-poll-full-results-likely-voters.xlsx | 18:31:50 | Braun Research for VPR, "Likely Voters" sheet Q6 (n=732): Scott 43.7, Janoo 34.4, Judd 1.9, Roy 1.1, Goodband 0.5, other 2.5, not sure 15.9. |
| `vpr_janoo_closing_on_scott_2026-09-28.html` | https://www.vermontpublic.org/local-news/2026-09-28/poll-shows-amanda-janoo-closing-on-phil-scott-governors-race | 18:31:50 | VPR article: LV 44/34, 16 undecided. |
| `x_burgessev_2107923538392776875_fxtwitter.json` | https://api.fxtwitter.com/2/status/2107923538392776875 (https://x.com/burgessev/status/2107923538392776875) | 18:38:07 | Post (Oct 7) of the Guidant / Public First Action TX and MI polls (VoteHub's source). |
| `guidant_publicfirstaction_img1_HUDYR71XQAEpjOz.jpg`, `guidant_publicfirstaction_img2_HUDYUWeXoAAfWbH.jpg` | https://pbs.twimg.com/media/HUDYR71XQAEpjOz.jpg?name=small, https://pbs.twimg.com/media/HUDYUWeXoAAfWbH.jpg?name=small | 18:38 | The memo images in that post. img2 (Michigan memo, Oct 6): 800 LV, **Sept 20-27**, Benson 50, James 45, undecided 5. img1 (Texas) was not read. |
| `victoryinsights_PollReport_MN-GE-26_10-28-26.pdf` | https://irp.cdn-website.com/07e08705/files/uploaded/PollReport_MN-GE-26_10-28-26.pdf | 18:38:07 | Victory Insights MN report (Oct 28), "Commissioned by Michele Tafoya": 1,194 LV, Oct 21-22; governor Klobuchar 50.1, Demuth 43.1, others 2.4, undecided 4.4. |
| `emerson_california_2026-10.html` | https://emersoncollegepolling.com/california-2026-poll-xavier-becerra-holds-27-point-lead-over-steve-hilton/ | 18:41:08 | Emerson CA: Becerra 60, Hilton 33, 7 undecided; with leaners 64/36. |
| `wpri_emerson_ri_2026-10_403.html` | https://www.wpri.com/news/elections/5p-wpri-emerson-poll-story/ | 18:41:08 | **HTTP 403** (PerimeterX bot block). |
| `opb_dhm_oregon_2026-09-30.html` | https://www.opb.org/article/2026/09/30/opb-poll-shows-oregon-governors-race-virtually-deadlocked/ | 18:41:08 | OPB/DHM, 915 LV: initial Drazan 46, Kotek 44, Smith 3, undecided 8 (leaner numbers not in the text). |
| `ojp_dhm_oregon_2026-09.html` | https://www.oregonjournalismproject.org/new-poll-shows-drazan-with-slight-lead-in-governors-race | 18:41:08 | DHM for Grow Oregon, "the Sept. 11 poll", 600 LV: Drazan 45, Kotek 43, Smith 4. |
| `quinnipiac_ct_release_3966.html` | https://poll.qu.edu/poll-release?releaseid=3966 | 18:41:08 | Quinnipiac CT (Sept 16): Lamont 55, Fazio 38, 5 undecided, 2 refused (VoteHub says 58/38). |
| `cwb_massinc_topline_2026-09.pdf` | https://commonwealthbeacon.org/wp-content/uploads/2026/09/Topline-2026-09-CWB-Ballot-Questions-TUES-RELEASE.pdf | 18:41:08 | MassINC MA topline: initial Healey 51, Minogue 30, James 3, other 2, undecided 12; with leaners 54/32/4/3/6. |
| `wsfa_gray_alabama_daily_news_poll_2026-10-20.html` | https://www.wsfa.com/2026/10/20/tuberville-leads-jones-51-40-percent-exclusive-gray-alabama-daily-news-poll/ | 18:43:01 | Cygnal for Gray Media Alabama / Alabama Daily News, 500 LV, Oct 16-17: Tuberville 51.2, Jones 40.0, undecided 8.9 (RCP's "Alabama Daily News" row; not in VoteHub). |
| `fandm_poll_release_october_2026.html` | https://www.fandmpoll.org/franklin-marshall-college-poll-release-october-2026/ | 18:43:01 | Franklin & Marshall PA (Oct 22): interviews Oct 7-18, 808 RV; Shapiro 59, Garrity 36 among LV (not in VoteHub). |

Files reused from elsewhere in the repo (not copied): `../senate_polls_2026/recent/NetChoice-October-2026-Antitrust-Tech-Survey-Topline.pdf` (Echelon Insights governor questions: GA Q11 p.6, OH Q15 p.8, ME Q18 p.10, NE Q20 p.11, FL Q22 p.12, IA Q25 p.14), `../senate_polls_2026/recent/afwh_redbox_ohio.html` (RedBox OH governor 48.2/43.8, sponsor A Fight Worth Having), `../senate_polls_2026/recent/254labs_tx_statewide_poll_2026-10-28.html` (YouGov Blue TX governor 49/46), `../senate_polls_2026/recent/nyt_poll_list_user_paste_2026-10-28_third.txt` (the user's NYT list paste: 254 Labs and Victory Insights governor lines), `../senate_polls_2026/recent/dfp_alaska_oct_2026.pdf`. Candidate party labels for minor candidates come from RCP's `affiliation` field or the roster wikitext in `../governors_2026/`.

## Compiled table conventions (`gov_polls_compiled.json`)

`{state: {"notes": ..., "polls": [...]}}` for all 36 states (CO, HI and WY have empty lists). Each poll has the Senate-compile fields plus the extra governor fields:

- **pollster, sponsor, partisan, start, end, released, population, n.** VoteHub's row when VoteHub has the poll (the LV row when VoteHub also lists an RV version); `released` = VoteHub `created_at`. For polls not in VoteHub: the pollster release, or RCP's row (then `released` = the RCP row's timestamp, noted). Saved releases override VoteHub where they disagree (each case is in the poll's `note`).
- **partisan.** VoteHub's flag (REP → "R", DEM → "D"); where VoteHub has no row, the sponsor's affiliation. One exception: the Opinion Diagnostics poll for independent candidate Ken Block (RI) is set to **"I"**, so that the build step treats it as candidate-sponsored. VoteHub's flags are applied per row and are not always consistent: of the three Change Research / Freedom Project USA Florida polls only Oct 8-10 is flagged DEM; YouGov Blue / 254 Labs (TX) is flagged DEM here, while the Senate compile has that poll's flag null; PPP / Chicago News Weekly (IL) is flagged DEM. co/efficient and Cygnal are flagged REP in some states and not others (no named sponsor, so the build is unaffected).
- **d_candidate, r_candidate, d, r, anti_r.** The Democratic and Republican nominees and their shares. `d`/`r` = a separate head-to-head question if one was found, else the full ballot. **No separate head-to-head question was found in any saved source** (the RCP "two-way" feeds list the D and R shares of the full ballot), so `d`/`r` are the full ballot everywhere, `h2h_anti_r`/`h2h_r` are null outside Alaska, and `full_d`/`full_r` (always the full ballot) equal `d`/`r`. `anti_r` = `d` in every race (no race has an independent as the Republican's main opponent; in Rhode Island the Democrat leads and independent Ken Block runs second). Note that `r` serves both the Senate pair (`anti_r`/`r`) and the governor pair (`d`/`r`); both pairs use the same question.
- **Which ballot.** The pollster's headline (first-reported) ballot, as in the Senate compile; the alternative (with leaners / initial) is in the note (Emerson CA 60/33 vs leaners 64/36; MassINC MA initial 51/30 vs leaners 54/32; Quantus GA 48.2/46.6 vs 49.0/47.5; State Navigate headlines are with leaners).
- **others.** `[{name, party, pct}]` for the other candidates in the poll's full ballot (VoteHub answers, else RCP's multi-candidate feed when its D/R match, else the release). Where a release gives only a combined minor-candidate share, it is one entry named "...combined" with party null.
- **undecided.** Only where a saved release reports it; null otherwise (VoteHub and RCP do not carry it).
- **Alaska.** `d`/`r`/`anti_r` and `others` (Bronson R, Taylor R) are the first-choice round. `rcv_final_d`/`rcv_final_r` = the final ranked-choice round (Kreiss-Tomkins vs Wilson). `h2h_anti_r`/`h2h_r` repeat the final round, following the Senate compile (RCP's Alaska average is a final-round average). co/efficient and Cygnal released no final round.
- **in_rcp_average.** True when the poll is a `poll_rcp_avg` row in the race's main RCP feed (see the id list above); false when it is listed but not averaged, or not listed; null where RCP publishes no average.
- **excluded_pollster.** True for ActiVote (CA, FL, GA, IL, OH, PA, TX x2), Rasmussen Reports (GA, NH; RCP rows only) and Wedgewood Polls (GA, KS, MI, NE). No Median Strategies poll was found. These are recorded but must never be averaged.
- **Deduplication.** The same poll in VoteHub and RCP (and duplicate VoteHub rows: LV/RV versions, first/final-round rows, rounded copies) is one entry: same firm (matched on name tags that include sponsors, e.g. "FOX News" = Beacon/Shaw, "Cook Political Report" = New River, "TPOR" = Slingshot) and end dates within 3 days. Differences between the sources (numbers, n, dates, population) are listed in each poll's `note`.
- **source.** The saved files the entry uses (paths relative to this folder).
- **notes (per state).** RCP average(s) with window, shares, number of polls and lastBuildDate (and the averaged polls; those before Sept 1 are not in the poll list), or why there is none; race oddities; polls left out.

## Data problems found
- **VoteHub errors corrected from releases:** MI Guidant/Public First Action end date 2026-10-27 (memo: Sept 20-27); CT Quinnipiac Sept 8-14 58/38 (release 55/38); GA AJC poll listed as GBAO, RV, n=2000 (AJC: UGA SPIA, 1,000 LV); OH Echelon Kissick 2 (topline 4); AK DFP n=629 (694). Name typos handled: "Alaska Survery Research", "Tret Taylor", "Sarah Huckabee Saners", "Maura Healy", "Tim Pickens" (ID, = Terri Pickens), "Travis Kissick" (OH, = Don Kissick).
- **VoteHub misfiling:** a GQR / Senate Majority PAC poll (Oct 1-4, Flanagan 53, Tafoya 44) is filed under the Minnesota governor race; those are Senate candidates, so it is left out.
- **RCP errors:** VT UNH n=1418 (that is UNH's New Hampshire n; VoteHub 835); Echelon n=3644 in ME/NE/OH (the national total; state n 413/407/508); OR DHM/Grow Oregon dated 9/3-9/9 (article: Sept 11).
- **Not resolved (no release checked):** GA YouGov Sept 15-18 (VoteHub 47/44 n=3069, RCP 46/44 n=3303); IA YouGov Sept 3-8 (VoteHub 51/41 n=2041, RCP 51/40 n=2127); IA New River/Cook (54/43 vs 53/43); RI WPRI/Emerson (RCP 44/35/10 used; VoteHub 48/38/12, labeled "with leaners" in the roster wikitext); OR OPB/DHM leaner ballot (VoteHub 46/47); n differences for TX UT/TPP (841 vs 861), FL UNF (1378 vs 1471), CT Quinnipiac Oct (702 vs 1225), MI MSU (836 vs 863), OH and TX VoteHub/Verasight (531 vs 623, 601 vs 969); several 1-4 day date differences (noted per poll).

## Races with no polls
- **No poll ending on or after Sept 1 in any source: Colorado, Hawaii, Wyoming.** (VoteHub has no rows for them; RCP has only placeholder pages.)
- One poll only: Arkansas (Hendrix), Maryland (UMBC), Oklahoma (Workbench Strategy for the Democratic nominee, Cyndi Munson: partisan sponsor).

## Not retrieved
- Poliwave governor pages: none exist (see above).
- UNH Vermont PDF and the WPRI/Emerson Rhode Island story: HTTP 403.
- NYT/Siena toplines (Alaska final round 52/48 is VoteHub's and RCP's figure), the YouGov Georgia PDF, and most other pollster releases were not fetched: those polls rest on VoteHub and RCP values.
- 270toWin governor pages were not used.

## Verification
15 randomly chosen compiled polls (seed 20261028: CA SurveyUSA 9/15-20, ME co/efficient, AZ HighGround 10/21-25, TX Emerson 10/17-19, GA Echelon, MI YouGov, AK Fabrizio/Impact, TX Marist 9/17-20, MA UMass/WCVB, ME Marist 10/1-4, AZ GrayHouse 10/18-20, AL RMG, PA NYT/Siena, NY Emerson, ME UMass Lowell) were re-read from the saved VoteHub and RCP files (and the AARP page and NetChoice topline for the two release-based entries); all fields matched.

## Update, 2026-10-29 (manual poll check: CNN/SSRS state polls)

Every RCP governor feed above and VoteHub's governor dump were downloaded again at 12:15 UTC. VoteHub had no new rows (only its average weights and a sponsor-name edit changed), so its saved copy is kept. Updated feeds: `rcp_gov_tx_8910.json`, `rcp_gov_tx_3way_9200.json`, `rcp_gov_ks_9017.json`, `rcp_gov_me_9030.json`, `rcp_gov_mi_8992.json`, `rcp_gov_nh_8953.json`, `rcp_gov_wi_9105.json`.

| File | URL | Notes |
|---|---|---|
| `dailysignal_wi_2026-10-28.html` | https://www.dailysignal.com/2026/10/28/new-poll-shows-wisconsin-governors-race-is-up-for-grabs/ | Saved with headless Chrome; curl and WebFetch got HTTP 403. The League of American Workers conducted the poll itself (no sponsor named), Oct 19-23, 1,213 LV: Crowley 47.7, Tiffany 44.6, undecided 7.7. The Daily Signal reports it and quotes the group's founder, Steve Cortes. RCP lists it as "LAW/Daily Signal**" (48/45) in its average. |

Files reused from elsewhere in the repo (not copied):
- `../senate_polls_2026/recent/cnn_ssrs_{texas,kansas,maine,michigan}_october_2026.pdf`: CNN/SSRS, Oct 20-26/27, released Oct 29. GOVVOTE tables: TX Hinojosa 46, Abbott 48; KS Holscher 45, Masterson 50; ME Pingree 53, Charles 39 (two-candidate question, Bennett not offered); MI Benson 53, James 41.
- `../senate_polls_2026/recent/umasslowell_yougov_nh_ma_2026-10-28.html`: UMass Lowell/YouGov, released Oct 28. NH (Oct 2-19, 600 LV): Ayotte 48, Warmington 42, Villee 3. MA (Oct 7-18, 850 LV): Healey 57, Minogue 29, James (I) 4.
- `../senate_polls_2026/al/chism_blueprint_al_2026-10-28.html`: Blueprint Polling (Chism Strategies), Oct 22-24, 695 LV: Tuberville 48, Jones 45. "Not sponsored by any outside campaign or organization."
- TSU/YouGov TX (Oct 21-25, 2,000 LV): Abbott 50, Hinojosa 47, Dixon (L) 2, from RCP's rows only. The WFAA release returned HTTP 403 (see `../senate_polls_2026/recent/README.md`, Oct 29).

Effects on the governor averages:
- RCP added CNN to its Texas, Kansas, Maine and Michigan averages, TSU/YouGov to Texas, UMass Lowell to New Hampshire and LAW to Wisconsin. All of these races use RCP's average.
- **Kansas** goes back to RCP's average. CNN (ending Oct 26) is now its latest poll, so Global Strategy Group (Oct 21-22, which RCP never averaged) is no longer newer. Kansas had been recomputed on the extended window.
- **Alabama** is recomputed. The Blueprint poll ended after the latest poll in RCP's average (Oct 17) and came out after RCP's last update (Oct 21). Its firm is flagged D, but it has no named sponsor, so it counts.
- **Massachusetts** is recorded only. The UMass Lowell poll is not in RCP and ends on the same day as RCP's latest averaged poll, so it is not newer.

### Second check, 2026-10-29 13:33 UTC (from the user's NYT poll list paste)

The RCP governor feeds and VoteHub's governor dump were downloaded again. VoteHub had no new rows. Updated feeds: `rcp_gov_ma_8937.json` (UMass Lowell 10/7-18 added to the average: Healey 56.2, Minogue 33.4, 5 polls), `rcp_gov_me_9030.json` (lastBuildDate only) and `rcp_gov_me_3way_9101.json` (lists CNN; not averaged here).

| File | URL | Notes |
|---|---|---|
| `statenavigate_mn_statewide_poll_october_2026.html` | https://projects.statenavigate.com/interactives/mn/statewide-poll-october-2026/ | State Navigate interactive: Oct 26-28, 806 LV (919 unweighted), MOE 3.5; with leaners Klobuchar 52, Demuth 42, Young (Green) 3, don't know 3. |
| `statenavigate_mn_klobuchar_crossover_appeal_2026-10-29.html` | https://articles.statenavigate.com/mn/new-minnesota-governor-poll-shows-amy-klobuchars-crossover-appeal-fading/ | Article, published Oct 29. Same numbers. No sponsor named; no Senate question. |

The source is the user's NYT poll list paste (`../senate_polls_2026/recent/nyt_poll_list_user_paste_2026-10-29.txt`). Minnesota was already recomputed (newer polls than RCP's Oct 16 build); with State Navigate it averages 5 polls, two-party +11.91 -> +11.65.

## Update, 2026-10-29 (MSU Michigan survey, from the user's link)

The source is MSU's 2026 Michigan Election Survey report (`../senate_polls_2026/recent/msu_ippsr_mi_2026_pre_election_report.pdf`, https://polisci.msu.edu/_assets/MI_2026_pre_election_report.pdf): MSU Political Science with the Office for Survey Research and Verasight, Oct 8-23, 1,383 likely voters, funded by MSU. Governor (MRP, initial response) Benson 48.5, James 38.7, someone else or none 3.3, undecided 9.6. RCP's Michigan governor feeds list the same polls as the saved copies. The poll is not in RCP's average and ends before RCP's latest averaged poll (CNN, Oct 20-27), so Michigan stays on RCP's average.

User decision (Oct 29, after this check): count the MSU poll in RCP's Michigan average anyway (`COUNT_ADDED_TO_RCP` / `ADDED_TO_RCP` in `build_governor_poll_averages.py`). Michigan's average: 8 polls, Benson 50.6, James 42.5, two-party +8.37 -> +8.71.

## Update, 2026-10-29 18:20 UTC (fourth check, user asked)

Every RCP governor feed and VoteHub's governor dump were downloaded again. Only `rcp_gov_ia_9032.json` changed: co/efficient 10/28 (Sand 50, Lahn 45) added to the average, co/efficient 10/15-19 dropped, Echelon Insights 10/16-23 listed but not averaged (10/5-10/28, Sand 50.8, Lahn 44.4). No compiled poll ends after Oct 28, so Iowa is back on RCP's average (two-party +6.54 -> +6.72).

| File | URL | Notes |
|---|---|---|
| `cortes_wick_law_wi_2026-10-29.html` | https://stevecortes.substack.com/p/breaking-news-wisconsin-heads-for | Steve Cortes, president of the League of American Workers: "My newest poll for League of American Workers", conducted by Wick Research, 1,213 LV, Crowley 47.7, Tiffany 44.7. VoteHub (Oct 29) lists pollster Wick, sponsor League of American Workers, partisan REP. A named sponsor with a partisan flag, so it is not counted (user rule, Oct 28) and comes out of RCP's Wisconsin average: 4 polls -> 3, two-party +4.86 -> +5.42. |
| `american_encore_kreate_az_2026-10-29.html` | https://americanencore.org/blog/arizona-governor-survey-showing-our-work | KStrat for American Encore, Oct 25-27, 900 LV: published topline Hobbs +5.1 (VoteHub: Hobbs 48, Biggs 43). VoteHub flags it REP: partisan-sponsored, not counted; not in RCP's feed. |
| `votehub_governor_all.json` | https://polling.votehub.com/site/polls?poll_type=governor&limit=2000 | Refreshed. New 2026 rows: the two above, plus polls already compiled (CNN/SSRS TX, KS, ME, MI; TSU TX; Blueprint AL; UMass Lowell NH, MA; State Navigate MN) and Concord for Democrats for Education Reform in Ohio (DEM-sponsored, fielded Aug 29-31: not counted). |

## Update, 2026-10-30 (manual poll check, user asked: "don't just rely on RCP")

Retrieved **2026-10-30 12:04-12:20 UTC**. Every RCP governor feed above and VoteHub's governor dump were downloaded again and compared with the saved copies, and the polls were cross-checked against each race's Wikipedia page (its poll table, all sources) and the release pages of Emerson, Marist, Siena, Quinnipiac, Suffolk, Marquette, co/efficient, State Navigate, Trafalgar and Fox News. Changed feeds saved: `rcp_gov_az_8683.json`, `rcp_gov_mi_8992.json`; `votehub_governor_all.json` refreshed (its new rows, co/efficient IA Oct 28 and MSU Political Science/Verasight MI, were already compiled).

| File | URL | Notes |
|---|---|---|
| `noble_az_poll_of_record_2026-10-30.html` | https://www.noblepredictiveinsights.com/post/az-poll-of-record-hobbs-6-yee-bucks-the-trend | Noble Predictive Insights' AZPOP poll of record (Oct 30): Oct 26-28, 511 likely voters, MOE +/-4.34; Hobbs 51, Biggs 45, undecided 3. No sponsor named. |
| `noble_az_por_2026_poll_report.xlsx` | https://7453540.fs1.hubspotusercontent-na1.net/hubfs/7453540/AZPOP/2026/PoR/2026%20GE_AZPoR_PR_Poll%20Report.xlsx | The poll report linked from the release. Sheet "Total": weighted N 511; Hobbs 0.51, Biggs 0.45, Hourihan (No Labels) 0.01, Lombardo (G) 0, another candidate 0, undecided 0.03. |
| `cbsdetroit_mitchell_mi_gov_2026-10-29.html` | https://www.cbsnews.com/detroit/news/jocelyn-benson-john-james-october-michigan-gubernatorial-poll/ | CBS Detroit (Oct 29): Mitchell Research & Communications for CBS Detroit and other Michigan TV stations, Oct 26-27, 636 LV, MOE 3.9: Benson 49, James 44 (early October 46/39). The same survey's Senate result is already compiled. |

RCP changes: **Arizona** (row Oct 30 06:31 CT) averages 7/26-10/28, Hobbs 50.2, Biggs 41.0, 5 polls, with Noble's Oct 26-28 poll replacing its Aug 10-13 one; **Michigan** (row Oct 29 16:44 CT) averages 9/24-10/27, Benson 50.9, James 43.0, 7 polls, with CBS News/Mitchell Oct 26-27 replacing Mitchell's Oct 1 poll. Both races stay on RCP's average (Michigan with the MSU/Verasight poll added, user decision Oct 29). Effect: Arizona Hobbs +12.0 -> +10.1 two-party (projection D+13.2 -> D+11.7, P(D) 0.995 -> 0.988); Michigan Benson +8.7 -> +8.35 (D+8.2 -> D+7.9, P(D) 0.922 -> 0.913); P(Democratic majority of governorships) 0.717 -> 0.715.

No other new governor poll was found. Polls on Wikipedia not in RCP's averages were already compiled (Siena NY Oct 19-22, M3 Strategies and McLaughlin/California Post CA, GrayHouse AZ, KStrat/American Encore AZ, RedBox AZ/MI, ActiVote).

### Washington Post-Schar School, Kansas (Oct 30, from the user's link)

Files in `../senate_polls_2026/recent/` (`wapo_schar_kansas_2026-10-30.html`, `wapo_schar_kansas_topline_2026-10-30.pdf`; see that README). Oct 22-26, 801 LV; Q5 governor (two candidates named): Holscher 51, Masterson 45, other 1, would not vote 2, no opinion 1. RCP's governor feed (re-downloaded 12:34 UTC, unchanged) does not list it, though RCP averages the same poll for the Senate. Counted in RCP's Kansas governor average anyway (`ADDED_TO_RCP` in `build_governor_poll_averages.py`; the user linked the poll and asked not to rely only on RCP): Masterson +5.98 -> +3.90 two-party; projection R+5.4 -> R+3.8, P(Holscher) 0.177 -> 0.260; P(Democratic majority of governorships) 0.714 -> 0.720.

### McLaughlin & Associates excluded (user decision, Oct 30)

McLaughlin & Associates is now an excluded pollster, like ActiVote, Rasmussen, Wedgewood and Median Strategies (`EXCLUDED_POLLSTERS` in `build_governor_poll_averages.py` and `build_senate_poll_averages.py`). Its only poll here, California (Oct 17-20, for the California Post), was never averaged (California follows RCP's average, which doesn't include it); it is now marked `excluded_pollster: true`. No average changed.

### Counting the polls RCP leaves out (user decision, Oct 30)

`COUNT_RCP_LEFT_OUT` is on here too (rule in `../senate_polls_2026/recent/README.md`; Alaska counts only final-round polls). Not added (`LEFT_OUT_PARTISAN_LEANING`): Targoz for the South Carolina Policy Council, MDW / EDGE Communications FL, Fabrizio, Lee & Associates FL (no client named), the Manhattan Institute CA, YouGov for City Forward Collective / CFC Action Fund WI. Skipped as internals per VoteHub: David Joy Wolfson CA, Global Strategy Group KS (Holscher). Added (18): AZ GrayHouse Oct 18-20, Equis Oct 1-9, Wick Oct 3-6; CA M3 Strategies, IVC Media for the Independent Voter Project; CT Wesleyan/YouGov for CT Mirror and The Connecticut Project; FL, IA, ME, OH Echelon Insights for NetChoice; IA, NH National Public Affairs; NH UNH Sep 17-21; NY Siena Oct 19-22 (in place of Siena Sep 11-17) and Beacon Research for the Secure AI Project; OH VoteHub/Verasight; PA Z to A Research; TX Pollfinity. P(Democratic majority of governorships) 0.721 -> 0.708.

### Campaign and party internals (Oct 30)

`LEAVE_OUT_VOTEHUB_INTERNAL` applies here too. Out: **Nebraska** PPP Oct 13-14 (Pillen 48, Walz 46; VoteHub internal DEM, sponsored by the Walz campaign per Wikipedia's poll table), so Nebraska's recomputed average has 3 polls, Pillen +3.4 -> +3.9 two-party (projection R+6.5 -> R+6.9, P(D) 0.099 -> 0.086). **Idaho**: the VoteNexus Oct 21-22 survey is the one Poliwave says was commissioned by Knock Every Door PAC and the Achilles campaign; VoteHub's governor row isn't flagged, so the sponsor is now recorded on the compiled entry and the partisan-sponsor rule removes it: Idaho rests on Advanced Targeting Research (Sep 13-16, half weight), projection R+26.2 -> R+28.2. P(Democratic majority of governorships) 0.708 -> 0.707.

### Emerson, Kansas (Oct 30, from the user's link)

Files in `../senate_polls_2026/recent/` (`emerson_kansas_october_2026.html`, `emerson_kansas_october_2026_full_results.xlsx`). Oct 26-28, 800 LV; governor Holscher 46.3, Masterson 50.0, undecided 3.7 (with leaners 47.5/52.5). RCP's governor feed (`rcp_gov_ks_9017.json`, re-downloaded 13:17 UTC, built Oct 30 07:49 CT) now averages 9/8-10/28, Masterson 48.7, Holscher 45.5, 6 polls, with Emerson's Oct 26-28 poll (46/50) in place of its Sep 15-16 one and the Washington Post-Schar School poll (51/45), so the Post poll is no longer in `ADDED_TO_RCP`. Effect: Masterson +3.90 -> +3.36 two-party; projection R+3.7 -> R+3.3, P(Holscher) 0.261 -> 0.285; P(Democratic majority of governorships) 0.707 -> 0.709.

## Update, 2026-10-30 evening (poll check, user asked)

Retrieved 21:40 UTC with the Senate feeds (procedure and the VoteHub comparison in `../senate_polls_2026/recent/README.md`). New VoteHub governor rows not counted: Workbench Strategy FL Oct 18-22 for Angie Nixon (campaign internal), Concord SD Oct 22-26 for Democrats for Education Reform (partisan sponsor), ActiVote TX (excluded pollster).

### InsiderAdvantage, Florida (Oct 28-29), in RCP's average

Release: `../senate_polls_2026/recent/insideradvantage_florida_2026-10-30.html` (1,200 LV, Oct 28-29, no sponsor named): governor Donalds 49, Jolly 45, other 2, undecided 4. `rcp_gov_fl_8881.json` re-downloaded 21:40 UTC: RCP added it to its average (row Oct 30 14:00 CT); average 10/2-10/29, Donalds 48.8, Jolly 44.0.

Effect: Florida's average (7 polls) R+5.6 -> R+5.4 two-party; projection R+4.8 -> R+4.6 (P(Jolly) 0.202 -> 0.208); P(Democratic majority of governorships) 0.709 -> 0.710.

### Quantus Insights, Texas (Oct 26-28), in RCP's average

Release: `../senate_polls_2026/recent/quantus_texas_2026-10-30.html` (Oct 26-28, 1,221 LV, no sponsor named): governor Abbott 50.7, Hinojosa 45.8, Dixon (L) 1.2, undecided 2.3; pushed, 51.6/46.3. `rcp_gov_tx_8910.json` and `rcp_gov_tx_3way_9200.json` re-downloaded 21:40 UTC: RCP added it (52/46) and moved Cook Political Report (Oct 9-13), Marist (Oct 8-11), ReconMR/Siena (Oct 5-8) and University of Houston (Oct 10-14) out of its two-way average; average 10/8-10/28, Abbott 50.3, Hinojosa 46.6.

Effect: Houston, Cook and Marist started inside RCP's window, so `COUNT_RCP_LEFT_OUT` keeps them; ReconMR/Siena started before it and drops out. Texas's average (10 polls) R+3.1 -> R+3.65 two-party; projection R+4.0 -> R+4.4 (P(Hinojosa) 0.217 -> 0.194); P(Democratic majority of governorships) 0.710 -> 0.708.

### UC Berkeley IGS / Los Angeles Times, California (Oct 19-25), in RCP's average

| File | URL | Notes |
|---|---|---|
| `latimes_berkeley_igs_ca_2026-10-30.html` | https://www.latimes.com/california/story/2026-10-30/becerra-widens-lead-in-governors-race-as-voter-focus-shifts-to-trump-new-poll-shows | LA Times article (Oct 30), retrieved 22:00 UTC: poll by the UC Berkeley Institute of Governmental Studies, co-sponsored by the LA Times, online in English and Spanish Oct 19-25; 1,477 who had voted or were likely to vote, of 2,787 registered voters; MOE 3. Becerra 61, Hilton 34. |
| `rcp_gov_ca_9014.json` | https://orig.realclearpolitics.com/poll/race/9014/polling_data.json | Re-downloaded 21:40 UTC: 'LA Times/Berkeley IGS' 10/19-25 (61/34) replaces IGS's Sep 15-20 poll in the average; window now 10/9-10/25, Becerra 58.2, Hilton 34.2. |

Effect: with RCP's window starting Oct 9, IVC Media for the Independent Voter Project (Sep 23-Oct 2) no longer counts as a poll RCP left out. California's average (6 polls) D+23.6 -> D+25.7 two-party; projection D+23.6 -> D+25.2 (P(D) 1.000); P(Democratic majority of governorships) unchanged at 0.708.

### RCP refresh: Connecticut, Massachusetts, Georgia, New York, Nevada (Oct 30 evening)

| File | Notes |
|---|---|
| `rcp_gov_ct_9118.json` | Window now 10/6-10/12 (Lamont 55.0, Fazio 36.3): UNH and co/efficient (Sep 16-21) out of the average; Wesleyan/YouGov (Sep 22-Oct 7) no longer starts inside it, so it stops counting as a poll RCP left out. |
| `rcp_gov_ma_8937.json` | Window now 10/6-10/18 (Healey 57.7, Minogue 32.3): CWB/MassINC and UNH (Sep 14-22) out. |
| `rcp_gov_ny_8742.json` | Siena Oct 19-22 (54/40) now in RCP's average in place of its Sep 11-17 poll (we already counted it as a poll RCP left out); window 10/3-10/25, so Beacon Research for the Secure AI Project (Oct 1-6) no longer counts. |
| `rcp_gov_ga_9028.json` | YouGov Sep 15-18 out of RCP's average (9/21-10/17); Echelon Insights Oct 16-23 listed but not averaged. Georgia already uses the recomputed average (newer polls than RCP's), so nothing changes. |
| `rcp_gov_nv_8874.json` | RCP's average row (dated "12/31 - 12/31", 42.0/42.0) no longer contains any poll: Emerson (Sep 5-8) and Noble (Sep 22-26) are listed but not averaged. Both builds now treat an average with no polls as no RCP average (`load_rcp` returns None; the governor build would otherwise fail), so Nevada is recomputed from the compiled polls as before, with the same result. |

Effect: Connecticut D+18.8 -> D+20.4 two-party (3 polls), projection D+19.0 -> D+20.3; Massachusetts D+25.4 -> D+28.1 (3 polls), D+28.7 -> D+30.9; New York D+15.8 -> D+13.5 (4 polls), D+14.8 -> D+12.9 (P(D) 0.999 -> 0.995); Georgia and Nevada unchanged. P(Democratic majority of governorships) 0.708 -> 0.707.
