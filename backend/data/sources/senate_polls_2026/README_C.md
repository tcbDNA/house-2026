# 2026 Senate polling, set C (18 low-salience races)

Set C covers AL, AR, CO, DE, ID, IL, KY, MA, NJ, NM, OK, OR, RI, SD, TN, VA, WV and WY.

All files were retrieved on **2026-10-26** between 16:27 and 16:40 US Eastern (UTC-4), using curl. They were saved as served (Wayback pages decompressed) and read as text only. No numbers come from news summaries or search snippets. Every number is from an aggregator page or feed, or from a pollster or sponsor release.

The poll window is polls ending on or after **2026-07-01**.

## Result by race

| State | RCP average? | Polls ending 2026-07-01 or later |
|---|---|---|
| AL | **Yes.** 9/21-10/16: Moore 55.0, Wess 34.0 (R +21.0), from 2 polls | RCP: The Alabama Poll, RMG. Not on RCP: Cygnal (Gray TV/ALDN) and yes. every kid. foundation |
| AR | No. The page lists polls but `show_rcp_avg` = 0 | Hendrix/TB&P Oct and Aug, J.L. Partners Aug, GrayHouse Sep 30-Oct 4, 2040 Strategy Group (Shoffner internal) Jul |
| CO | No. The page has only a blank placeholder row | **None found** |
| DE | No. Generic page with no polls | **None found** |
| ID | No. Generic page with no polls | Poliwave lists VoteNexus (D/campaign), Peak Insights (R) x2, ATR and Bullfinch |
| IL | No. Generic page with no polls | PPP (D) for Chicago News Weekly; ActiVote (**excluded**) |
| KY | No. Generic page with no polls | GSG (D) for the Booker campaign, Aug |
| MA | **Yes.** 9/14-10/18: Markey 55.8, Deaton 29.8 (D +26.0), from 4 polls | See the RCP feed |
| NJ | No. The page has only a `*PLACEHOLDER*` row | **None found** |
| NM | **Yes.** 8/21-9/30: Lujan 53.5, Marker 37.0 (D +16.5), from 2 polls | See the RCP feed |
| OK | No. Generic "Mullin vs. Democrat" page with no polls | CHS & Associates, Aug |
| OR | No. Generic page with no polls | **None found** |
| RI | **Yes.** 9/17-10/11: Reed 55.7, McKay 30.0 (D +25.7), from 3 polls | See the RCP feed |
| SD | **Yes.** 10/12-10/20: Rounds 54.3, Bengs 38.7 (R +15.6), from 3 polls | Poliwave lists 7 more polls since July, mostly partisan |
| TN | No. The page lists 1 poll but `show_rcp_avg` = 0 | Beacon Center/Targoz, Aug 15-26 |
| VA | No. Generic page with no polls | **None found** after 7/1. The latest poll anywhere is TPSI, Jun 12-16 |
| WV | No. Generic page with no polls | **None found** |
| WY | No. Generic "Lummis vs. Democrat" page with no polls | **None found** |

Each RCP average equals the mean of its `poll_rcp_avg` rows, rounded to 0.1.

**Excluded pollsters.** There is **no Rasmussen Reports poll** for any of the 18 races in RCP, Poliwave or VoteHub. **ActiVote** appears only in **IL**: Sep 26-Oct 20, 400 LV, Stratton 58.5 / Tracy 41.5 on Poliwave (VoteHub and 270toWin give 59/42). Poliwave's IL "poll average" (55.2/39.6) includes that ActiVote poll.

## How the RCP race IDs were found

- **RCP blocks direct access.** realclearpolling.com still returns HTTP 403 (DataDome). The feed `https://orig.realclearpolitics.com/poll/race/<id>/polling_data.json` returns 200.
- **IDs from earlier sets.** The IDs for AL (9229), AR (9120), MA (8899), RI (8954), SD (9232) and NM (9122) were read from the embedded JSON in `rcp_latest_polls_senate.html`. That file belongs to set B and was read only, not modified.
- **IDs from Wayback.** The Wayback CDX listed 2026 RCP pages for CO, NJ and TN. The race ID is the page's `article-id` (CO 9040, NJ 9039, TN 9123). The page's `pollingDataUrl` points to a 2014 side-chart race and is not the race ID.
- **Scan for missing races.** To make sure no other 2026 race page was missed, IDs 8600-9300 were scanned by fetching the first 250 bytes of each feed. Every ID from 8600 to 9260 with no title returned 404, and 9261-9300 returned no title. The highest live ID is 9233. The result is in `rcp_race_id_scan_C.txt`.
- **What the scan found.** For DE, ID, IL, KY, OK, OR, VA, WV and WY, the only 2026 general-election RCP pages are the generic placeholders 8767-8801 (e.g. "Coons vs. Republican"). All of them have no poll rows. The scan also found only primary-election pages for IL, KY, OK and CO.

## Files

| File | URL | Retrieved (EDT) | Notes |
|---|---|---|---|
| `al/rcp_polling_data_9229.json` | https://orig.realclearpolitics.com/poll/race/9229/polling_data.json | 16:27 | RCP Moore vs. Wess. lastBuildDate Tue 20 Oct 2026 12:54 -0500. Page: https://www.realclearpolling.com/polls/senate/general/2026/alabama/moore-vs-wess |
| `al/poliwave_al_sen.html` | https://www.poliwave.com/us/al/sen-fed | 16:29 | 4 polls, including Cygnal (R) 10/16-17 and yes. every kid. 7/8-11 |
| `al/release_aldailynews_cygnal_20261022.html` | https://aldailynews.com/poll-barry-moore-leads-everett-wess-in-u-s-senate-race/ | 16:37 | Sponsor release (ALDN/Gray TV): 500 likely voters, Oct 16-17, Moore 50, Wess 35 |
| `al/release_yeseverykid_alabama_topline_jul2026.pdf` | https://yeseverykidfoundation.org/wp-content/uploads/YESF_Alabama-Statewide-Survey_Topline.pdf | 16:37 | n=601 LV, July 8-11, Moore 47, Wess 32 |
| `ar/rcp_polling_data_9120.json` | https://orig.realclearpolitics.com/poll/race/9120/polling_data.json | 16:27 | RCP Cotton vs. Shoffner vs. Wadlin. `show_rcp_avg` 0, no average row. lastBuildDate 16 Oct 2026 |
| `ar/poliwave_ar_sen.html` | https://www.poliwave.com/us/ar/sen-fed | 16:29 | 6 polls |
| `ar/270towin_arkansas_senate.html` | https://www.270towin.com/2026-senate-polls/arkansas | 16:36 | 3 polls, dated by release date, no average |
| `ar/release_talkbusiness_hendrix_oct2026.html` | https://talkbusiness.net/2026/10/poll-cotton-takes-lead-over-shoffner/ | 16:37 | Conducted **Oct 8-13**, 709 LV. RCP shows 10/10-10/15 |
| `ar/release_talkbusiness_hendrix_aug2026.html` | https://talkbusiness.net/2026/08/poll-tight-race-for-us-senate-between-cotton-shoffner/ | 16:37 | Aug 11-12, 1,217 LV, Shoffner 47.4, Cotton 44 |
| `ar/release_jlpartners_ar_memo_aug2026.pdf` | https://static1.squarespace.com/static/663253f0bc87b7070102f41f/t/6a84d771481c4817e92f0eee/1787090801301/AR+Aug+26+Polling+Memo.pdf | 16:37 | Aug 14-18, 803 LV, 51-35-4. No sponsor named |
| `co/rcp_polling_data_9040.json` | https://orig.realclearpolitics.com/poll/race/9040/polling_data.json | 16:32 | Baisley vs. Hickenlooper. Its only row is Economist/YouGov 7/3-7/6 "1024 A" with **empty** candidate values. No average |
| `co/rcp_polling_data_8770.json` | https://orig.realclearpolitics.com/poll/race/8770/polling_data.json | 16:34 | Generic "Hickenlooper vs. Republican" page, no polls |
| `co/rcp_baisley-vs-hickenlooper_wayback_20260722060040.html` | https://web.archive.org/web/20260722060040id_/https://www.realclearpolling.com/polls/senate/general/2026/colorado/baisley-vs-hickenlooper | 16:32 | Source of race ID 9040 (`article-id`) |
| `co/poliwave_co_sen.html` | https://www.poliwave.com/us/co/sen-fed | 16:30 | "Public polls 0" / "No polls in our database yet" |
| `co/270towin_colorado_senate.html` | https://www.270towin.com/2026-senate-polls/colorado | 16:36 | Only a June Democratic-primary poll |
| `de/rcp_polling_data_8771.json` | https://orig.realclearpolitics.com/poll/race/8771/polling_data.json | 16:34 | Generic page, no polls |
| `de/poliwave_de_sen.html` | https://www.poliwave.com/us/de/sen-fed | 16:30 | 0 polls |
| `id/rcp_polling_data_8774.json` | https://orig.realclearpolitics.com/poll/race/8774/polling_data.json | 16:34 | Generic "Risch vs. Democrat" page, no polls |
| `id/poliwave_id_sen.html` | https://www.poliwave.com/us/id/sen-fed | 16:30 | 7 polls (5 since July) |
| `id/release_atr_idaho_sep2026.pdf` | https://www.advancedtargetingresearch.com/_files/ugd/03a624_0fca9a6dd7f846f7bc96f97429561064.pdf | 16:37 | 700 RV, Sep 13-16. Three-way: Achilles 45.5, Risch 39.4, Loesby 4.5. Two-way: 50.1-38.5. "Not commissioned by any candidate" |
| `id/release_bullfinch_idaho_aug13_2026.html` | https://www.thebullfinchgroup.com/post/for-immediate-release-independent-todd-achilles-within-4-points-among-likely-voters | 16:37 | LV. Three-way: Risch 34, Achilles 30, Loesby 4. No n, field dates or sponsor stated |
| `id/release_bullfinch_idaho_aug19_2026.html` | https://www.thebullfinchgroup.com/post/for-immediate-release-independent-todd-achilles-leads-incumbent-jim-risch-in-two-way-head-to-head-m | 16:39 | Same survey, two-way: Achilles 38, Risch 33 |
| `il/rcp_polling_data_8775.json` | https://orig.realclearpolitics.com/poll/race/8775/polling_data.json | 16:34 | Generic page, no polls |
| `il/poliwave_il_sen.html` | https://www.poliwave.com/us/il/sen-fed | 16:30 | 2 polls: ActiVote (excluded) and PPP (D) |
| `il/270towin_illinois_senate.html` | https://www.270towin.com/2026-senate-polls/illinois | 16:36 | Same 2 polls. Its "average of 2 polls" includes ActiVote |
| `il/release_cnw_ppp_oct2026.html` | https://www.cnwmedia.com/article/cnw-poll-pritzker-leads-bailey-by-20-points-democrats-ahead-in-four-other-statewide-races | 16:37 | Sponsor's release: PPP, Sep 30-Oct 1, "569 Illinois voters" (LV/RV not stated), Stratton 49, Tracy 36 |
| `ky/rcp_polling_data_8778.json` | https://orig.realclearpolitics.com/poll/race/8778/polling_data.json | 16:34 | Generic page, no polls |
| `ky/poliwave_ky_sen.html` | https://www.poliwave.com/us/ky/sen-fed | 16:30 | GSG (D) Aug 24-27, plus PPP Dec 2025 |
| `ky/270towin_kentucky_senate.html` | https://www.270towin.com/2026-senate-polls/kentucky | 16:36 | Primary polls only |
| `ma/rcp_polling_data_8899.json` | https://orig.realclearpolitics.com/poll/race/8899/polling_data.json | 16:27 | RCP Deaton vs. Markey. lastBuildDate 19 Oct 2026 |
| `ma/poliwave_ma_sen.html` | https://www.poliwave.com/us/ma/sen-fed | 16:30 | 13 polls |
| `nj/rcp_polling_data_9039.json` | https://orig.realclearpolitics.com/poll/race/9039/polling_data.json | 16:32 | Murphy vs. Booker. Only a `*PLACEHOLDER*` row (1-1) |
| `nj/rcp_polling_data_8788.json` | https://orig.realclearpolitics.com/poll/race/8788/polling_data.json | 16:34 | Generic page, no polls |
| `nj/rcp_murphy-vs-booker_wayback_20260903185852.html` | https://web.archive.org/web/20260903185852id_/https://www.realclearpolling.com/polls/senate/general/2026/new-jersey/murphy-vs-booker | 16:32 | Source of race ID 9039 |
| `nj/poliwave_nj_sen.html` | https://www.poliwave.com/us/nj/sen-fed | 16:30 | 0 polls |
| `nm/rcp_polling_data_9122.json` | https://orig.realclearpolitics.com/poll/race/9122/polling_data.json | 16:27 | RCP Marker vs. Lujan. lastBuildDate 6 Oct 2026 |
| `nm/poliwave_nm_sen.html` | https://www.poliwave.com/us/nm/sen-fed | 16:30 | 1 poll (Albuquerque Journal) |
| `ok/rcp_polling_data_8792.json` | https://orig.realclearpolitics.com/poll/race/8792/polling_data.json | 16:34 | Generic "Mullin vs. Democrat" page, no polls |
| `ok/poliwave_ok_sen.html` | https://www.poliwave.com/us/ok/sen-fed | 16:30 | CHS & Associates, Aug 3-6 |
| `ok/270towin_oklahoma_senate.html` | https://www.270towin.com/2026-senate-polls/oklahoma | 16:36 | Primary poll only |
| `ok/release_chs_sooner_survey_aug2026.html` | https://chs-inc.com/general-election-rep/ | 16:37 | Sooner Survey Vol. 37 No. 11 (Aug 20, 2026): Hern 49, Thomas 25, others 8. Also Hern 48, Priest 27. No n, dates or population printed |
| `or/rcp_polling_data_8793.json` | https://orig.realclearpolitics.com/poll/race/8793/polling_data.json | 16:34 | Generic page, no polls |
| `or/poliwave_or_sen.html` | https://www.poliwave.com/us/or/sen-fed | 16:30 | 0 polls |
| `ri/rcp_polling_data_8954.json` | https://orig.realclearpolitics.com/poll/race/8954/polling_data.json | 16:27 | RCP McKay vs. Reed. lastBuildDate 20 Oct 2026 |
| `ri/poliwave_ri_sen.html` | https://www.poliwave.com/us/ri/sen-fed | 16:30 | 6 polls |
| `sd/rcp_polling_data_9232.json` | https://orig.realclearpolitics.com/poll/race/9232/polling_data.json | 16:27 | RCP Rounds vs. Bengs. lastBuildDate Mon 26 Oct 2026 13:35. **RCP tags Bengs (an independent) "Democrat".** |
| `sd/poliwave_sd_sen.html` | https://www.poliwave.com/us/sd/sen-fed | 16:30 | 14 polls |
| `tn/rcp_polling_data_9123.json` | https://orig.realclearpolitics.com/poll/race/9123/polling_data.json | 16:32 | Hagerty vs. Bradshaw. `show_rcp_avg` 0. One row: Beacon Center 8/15-8/26 LV, 58-33 |
| `tn/rcp_hagerty-vs-bradshaw_wayback_20260903173637.html` | https://web.archive.org/web/20260903173637id_/https://www.realclearpolling.com/polls/senate/general/2026/tennessee/hagerty-vs-bradshaw | 16:32 | Source of race ID 9123 |
| `tn/poliwave_tn_sen.html` | https://www.poliwave.com/us/tn/sen-fed | 16:30 | Beacon RV figure, 51-31, n=1,157 |
| `tn/270towin_tennessee_senate.html` | https://www.270towin.com/2026-senate-polls/tennessee | 16:36 | Beacon 51-31, "1,200 RV" (the full-sample n) |
| `tn/fiftyplusone_polls_tn_senate.html` | https://fiftyplusone.news/polls/senate/general/tennessee | 16:36 | Kept for FiftyPlusOne's race list: no ★ average for any of the 18 states, and no general-election page for CO, DE, NJ, OR, WV or WY. Poll rows are not in the static HTML |
| `tn/release_tennsight_beacon_aug2026.html` | https://tennsight.com/polls/august-2026/ | 16:37 | "Hagerty leads ... (58%-33%) among likely voters" |
| `tn/release_beacon_tn_aug2026_marginals.pdf` | https://tennsight.com/wp-content/uploads/2026/09/Beacon-Poll-of-TN-August-2026-Marginals.pdf | 16:38 | Senate ballot: **LV n=607: Hagerty 58, Bradshaw 33**. All RV n=1,157: 51-31 |
| `tn/release_beacon_tn_aug2026_crosstabs.pdf` | https://tennsight.com/wp-content/uploads/2026/08/Beacon-Poll-of-TN-August-2026-Crosstabs-Party-Ideology-and-Region-1.pdf | 16:37 | RV crosstabs, Aug 15-26 |
| `va/rcp_polling_data_8799.json` | https://orig.realclearpolitics.com/poll/race/8799/polling_data.json | 16:34 | Generic page, no polls |
| `va/poliwave_va_sen.html` | https://www.poliwave.com/us/va/sen-fed | 16:30 | 3 polls, the latest ending Jun 16, 2026 |
| `wv/rcp_polling_data_8800.json` | https://orig.realclearpolitics.com/poll/race/8800/polling_data.json | 16:34 | Generic page, no polls |
| `wv/poliwave_wv_sen.html` | https://www.poliwave.com/us/wv/sen-fed | 16:30 | 0 polls |
| `wy/rcp_polling_data_8801.json` | https://orig.realclearpolitics.com/poll/race/8801/polling_data.json | 16:34 | Generic page, no polls |
| `wy/poliwave_wy_sen.html` | https://www.poliwave.com/us/wy/sen-fed | 16:30 | 0 polls |
| `votehub_polls_api_C.json` | https://api.votehub.com/polls | 16:35 | Full VoteHub poll dump (`poll_type` "us-senator", `subject` "2026 <State>"). It has no poll for CO, DE, KY, NJ, OK, OR, WV or WY |
| `270towin_senate_latest_poll_by_state_C.html` | https://www.270towin.com/polls/php/get-polls-list-v2.php?election_year=2026&election_types[]=S&election_subtypes[]=PE&election_subtypes[]=PR&election_subtypes[]=GE&election_subtypes[]=GR&limit=0 | 16:35 | 270toWin's "latest poll by state" list. It has no DE, NJ, OR, VA, WV or WY entry. `/2026-senate-polls/{delaware,new-jersey,oregon,west-virginia,wyoming}` returned 404, and idaho and virginia redirected to the national list |
| `rcp_race_id_scan_C.txt` | https://orig.realclearpolitics.com/poll/race/{8600..9300}/polling_data.json | 16:31-16:36 | ID and title of every live RCP race feed in that range (first 250 bytes of each fetched). Every other ID from 8600 to 9260 returned 404, and 9261-9300 returned no title |

## Discrepancies and caveats

- **AR Hendrix (Oct).** RCP's dates (10/10-10/15) do not match the release, which says Oct 8-13.
- **AR GrayHouse (Sep 30-Oct 4, n=550).** The only source is an X post by GrayHouse's Landon Wall, and grayhouse.com has no release. The aggregators disagree:
  - Poliwave: Cotton 50, Shoffner 39, flagged (R).
  - VoteHub: Cotton 51, Shoffner 40, Wadlin 4, LV, no partisan flag.
- **AR 2040 Strategy Group (Jul 17-25, n=586).** Only Poliwave lists it, as an internal poll for Shoffner (D). It links a Google Drive file that was not retrieved.
- **ID polls.**
  - **Peak Insights (R).** The Aug 11-13 and Sep 28-30 polls are sourced on Poliwave to X posts only. Population is not given.
  - **VoteNexus (D) (Oct 21-22).** Sourced to a Google Drive file that was not retrieved. Per Poliwave, it was commissioned by Knock Every Door PAC and Todd Achilles for Idaho.
  - **Bullfinch.** Poliwave's n=608 and Aug 4-7 dates came from Wikipedia, per Poliwave's own note. The release gives neither.
- **KY GSG and OK CHS.** Field dates and n come from Poliwave, which says they were taken from Wikipedia and are not printed in the releases. Population is unknown for both.
- **IL PPP.** The release says only "569 Illinois voters". VoteHub records it as LV and 270toWin as RV.
- **TN Beacon.** RCP uses the LV figure (58-33, no n). Poliwave, VoteHub and 270toWin use the RV figure (51-31).
- **MA.**
  - Boston Globe/Suffolk dates: RCP 10/10-10/18, Poliwave 10/14-10/18, VoteHub 10/14-10/17.
  - WCVB/UMass Amherst 10/5-12: Poliwave stores 54-28, while RCP and VoteHub give 56-29.
  - UMass Amherst 8/5-12 (not in the average): RCP gives n=445 LV, while VoteHub and Poliwave give 800 RV.
- **SD Quantus.** RCP gives 657 LV and 57-37. Poliwave gives n=633 and 57-37. VoteHub gives 657 and 59-37.
- **NM SurveyUSA.** RCP and 270toWin give 567 LV. VoteHub gives 576.
- **FiftyPlusOne** loads its poll rows client-side, and its terms bar scraping beyond documented endpoints. Only its race list (★ = has an average) was used.
