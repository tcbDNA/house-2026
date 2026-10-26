# 2026 Senate polling averages, set B (MI, MS, NC, NH, MN, LA, GA)

All files were retrieved on **2026-10-26** with curl, saved as served, and read as text only. No numbers come from news summaries or search snippets.
The source rule was: use RealClearPolling (RCP) where it has an average, otherwise Poliwave (or FiftyPlusOne).

## Averages used

| State | File | URL | Average |
|---|---|---|---|
| MI | `mi/rcp_rogers-vs-el-sayed.html` | https://www.realclearpolling.com/polls/senate/general/2026/michigan/rogers-vs-el-sayed | RCP 9/24-10/22: El-Sayed 47.9, Rogers 46.0 (D +1.9), 8 polls. Includes Rasmussen 10/12-14. |
| GA | `ga/rcp_ossoff-vs-collins.html` | https://www.realclearpolling.com/polls/senate/general/2026/georgia/ossoff-vs-collins | RCP 9/21-10/17: Ossoff 51.2, Collins 43.0 (D +8.2), 5 polls. No Rasmussen or ActiVote poll in it. |
| MN | `mn/rcp_tafoya-vs-flanagan.html` | https://www.realclearpolling.com/polls/senate/general/2026/minnesota/tafoya-vs-flanagan | RCP 10/2-10/21: Flanagan 46.6, Tafoya 43.2 (D +3.4), 5 polls. Includes Rasmussen 10/20-21. |
| NH | `nh/rcp_pappas-vs-sununu.html` | https://www.realclearpolling.com/polls/senate/general/2026/new-hampshire/pappas-vs-sununu | RCP 9/15-10/20: Pappas 49.5, Sununu 43.0 (D +6.5), 6 polls. Includes Rasmussen 10/2-4. |
| NC | `nc/rcp_cooper-vs-whatley.html` | https://www.realclearpolling.com/polls/senate/general/2026/north-carolina/cooper-vs-whatley | RCP 9/27-10/20: Cooper 50.7, Whatley 40.1 (D +10.6), 7 polls. No Rasmussen or ActiVote poll in it. |
| MS | `ms/poliwave_ms_sen.html` | https://www.poliwave.com/us/ms/sen-fed | Poliwave (polls through Oct 22): Hyde-Smith 43.1, Colom 39.8 (R +3.3), 2 polls: Change Research (D) 10/21-22 and Data for Progress (D) 8/5-15. |
| LA | `la/poliwave_la_sen.html` | https://www.poliwave.com/us/la/sen-fed | Poliwave (polls through Sep 19): Letlow 47.1, Davis 43.1 (R +4.0), 2 polls: Hart Research (D) 9/17-19 and PPP (D) 7/21-22. Both were commissioned by the Davis campaign. |

**How to read the RCP files.** The poll table is embedded in the page's Next.js payload (`self.__next_f.push`) as JSON. Rows with `"type":"poll_rcp_avg"` are in the average. Rows with `"type":"poll"` are listed on the page but not averaged. In every RCP file above, the unrounded mean of the averaged rows reproduces the published average. RCP puts `*` or `**` after some pollster names, and the page does not say what the mark means.

## Supporting aggregator pages

| File | URL | Use |
|---|---|---|
| `mi/poliwave_mi_sen.html`, `ga/poliwave_ga_sen.html`, `mn/poliwave_mn_sen.html`, `nh/poliwave_nh_sen.html`, `nc/poliwave_nc_sen.html` | https://www.poliwave.com/us/{mi,ga,mn,nh,nc}/sen-fed | Poliwave's poll lists, used only for its partisan flags ("(R)"/"(D)") and to check for ActiVote. Poliwave lists ActiVote polls in GA (Sep 26-Oct 20, n=400) and NC (Sep 26-Oct 20, n=400). RCP lists neither. |
| `ms/fiftyplusone_polls_ms_senate.html`, `la/fiftyplusone_polls_la_senate.html` | https://fiftyplusone.news/polls/senate/general/mississippi, https://fiftyplusone.news/polls/senate/general/louisiana | FiftyPlusOne has **no average** for MS or LA: neither state carries the ★ "Indicates an average" mark in its race list. The poll list is not in the static HTML. |
| `rcp_latest_polls_senate.html` | https://www.realclearpolling.com/latest-polls/senate | RCP's latest Senate polls (released Sep 25-Oct 26). It has **no Mississippi or Louisiana poll**. |

## Could not retrieve
- **RCP Mississippi and Louisiana race pages.** After five successful RCP fetches, RCP's DataDome bot check returned HTTP 403 for every further request, and WebFetch also got 403. URLs tried: `.../2026/louisiana/letlow-vs-davis` (the slug is linked from a Bayou Progressive article), `.../louisiana/davis-vs-letlow`, `.../mississippi/hyde-smith-vs-colom`, `.../mississippi/colom-vs-hyde-smith`. The Wayback CDX had no Mississippi capture, and the Archive was offline for Louisiana. **So it is not confirmed that RCP has no MS or LA average.** The evidence that it has none is indirect: neither race appears in RCP's latest-polls feed. Poliwave was used for MS and LA.
- **Pollster releases that were blocked:** NYT/Siena NH (403), UNH NH PDF (403), Star Tribune/Mason-Dixon (429), the Politico-hosted Change Research MS memo (403), the Carolina Forward Google Doc (401; the Carolina Forward post was used instead), and Rasmussen NH (the RCP link returned 404).
- **Quantus release pages** are rendered by JavaScript. Their text was read from the embedded JSON, and no sponsor is stated there.

## Release discrepancies found while checking sponsors (RCP values were kept as published)
- **MI YouGov.** RCP lists 9/28-10/5 with 3947 LV and links the NH PDF. The actual MI document (https://d3nkl3psvxxpe9.cloudfront.net/documents/ttw_mi_20260921_lv.pdf) says Sep 22-Oct 4, 3,949 LV, El-Sayed 49, Rogers 48.
- **MI Marist.** RCP gives n=1185 LV, but 1,185 is the release's *registered-voter* sample. The likely-voter n is not printed (LV MoE ±4.3).
- **GA Trafalgar.** RCP's link points to the TX report. The GA report is https://www.thetrafalgargroup.org/wp-content/uploads/2026/10/GA-General-Report-1010.pdf (conducted 10/07/26, 1101 respondents).
- **NC WRAL/SurveyUSA.** RCP lists 10/1-10/7. SurveyUSA's release (#28047) says interviews ran 10/07-10/11/26 (643 LV), and it is an "exclusive WRAL/WSOC Poll".
- **Mississippi Data for Progress.** Poliwave stores the initial three-way ballot (Colom 38, Hyde-Smith 44, Pinkins (I) 7). The DFP head-to-head (Q4) is Colom 41, Hyde-Smith 47.
