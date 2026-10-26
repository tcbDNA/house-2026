# 2026 Montana U.S. Senate general election: polling sources

Collected 2026-10-26 for the forecast's documented polling override.
Candidates: Kurt Alme (R), Seth Bodnar (I), Alani Bankhead (D), Kyle Austin (L).
Every file below was retrieved on **2026-10-26**. Wayback copies carry their capture date in the filename.

## Polling averages (aggregator pages)

| File | URL | Notes |
|---|---|---|
| `rcp_alme_vs_bankhead_vs_bodnar_vs_austin.html` | https://www.realclearpolling.com/polls/senate/general/2026/montana/alme-vs-bankhead-vs-bodnar-vs-austin | RCP Average 8/27-10/18: Alme 41.0, Bodnar 29.0, Bankhead 18.5, Austin 3.5, Alme +12.0. The average uses 2 polls: Quantus 10/15-18 and Montana Free Press/Rutgers-Eagleton 8/27-9/7. Quantus 9/14-15 is listed on the page but is not in the average. |
| `rcp_alme_vs_bankhead_vs_bodnar.html` | https://www.realclearpolling.com/polls/senate/general/2026/montana/alme-vs-bankhead-vs-bodnar | Three-way URL. It shows the same table and average as the four-way page. |
| `270towin_mt_senate_polls.html` | https://www.270towin.com/2026-senate-polls/montana | "Average of 2 Polls": Bankhead 20.0, Bodnar 27.5, Alme 45.5. Those 2 polls are Quantus (10/20, 667 LV) and American Pulse (9/28, 604 LV) under the site's 30-day rule, and their values average exactly to these figures. |
| `poliwave_mt_sen.html` | https://www.poliwave.com/us/mt/sen-fed | Poll average Alme 42.9, Bodnar 30.6, Bankhead 16.6, using polls through Oct 18. The page says "10 recent polls" (each pollster's latest poll from Jul 26 to Oct 18, with newer polls weighted more) but does not list which ones. |
| `callthemap_sen_mt.html` | https://www.callthemap.com/polls/SEN-MT | Edition Oct 26: a weighted average of 16 polls that name every candidate. It reports candidate shares with undecided voters removed: Alme 46.5, Bodnar 29.4, Bankhead 21.3. Per-poll weights are embedded in the page. Its "every candidate named" row for Quantus Oct has Bodnar and Bankhead swapped (Bodnar 21.4, Bankhead 29.6). |
| `fiftyplusone_polls_mt_senate.html` | https://fiftyplusone.news/polls/senate/general/montana | Oct 26: Alme 42.4, Bodnar 30.4, Bankhead 16.7, Alme +12. The poll list is not in the static HTML, so it was not captured. |
| `votehub_averages_list.json` | https://polling.votehub.com/site/averages?limit=200 | VoteHub's list of averages, which is the data behind votehub.com/polls. It has **no Montana Senate average**; the only Montana entry is `h_2026_mt_01` (House). |
| `silverbulletin_2026_model.html` | https://www.natesilver.net/p/nate-silver-2026-midterm-election-polls-model | Paywalled. It contains no Montana numbers. |
| `ddhq_polls_mt_senate_wayback_20261010.html` | https://web.archive.org/web/20261010202242/https://votes.decisiondeskhq.com/polls/general-ballot-test/2026-mt-us-senate/montana | **DO NOT USE.** The live DDHQ page returned a Vercel bot-check page (HTTP 429). This only Wayback capture lists obviously placeholder polls ("Meridian Research", "Vantage Analytics" and similar, with candidates labelled A/B and field dates later than the capture date). |

## Poll databases

| File | URL | Notes |
|---|---|---|
| `votehub_polls_all.json` | https://api.votehub.com/polls | The full VoteHub poll API dump. Montana Senate rows have `subject == "2026 Montana"`. Its Quantus Oct 15-18 row (n=686, Alme 46, **Bankhead 29, Bodnar 21**) has Bodnar and Bankhead swapped compared with the pollster's release. |
| `wikipedia_2026_mt_senate.html` | https://en.wikipedia.org/wiki/2026_United_States_Senate_election_in_Montana | Used only to discover polls and source links. No numbers were taken from it. |

## Pollster and sponsor releases (polls fielded since 2026-08-15)

| File | URL | Poll |
|---|---|---|
| `peak_insights_2026-08-23_25_memo.pdf` | https://cdn.sanity.io/files/ifn0l6bs/production/72ac898bdf17c5121988f619a81d80fde4e18325.pdf | Peak Insights memo dated Sep 4. Field dates Aug 23-25, N=600 LV, live calls. |
| `mtfp_eagleton_2026-09-11_article_wayback_20261011.html` | https://web.archive.org/web/20261011190628/https://montanafreepress.org/2026/09/11/alme-holds-an-8-point-lead-over-bodnar-in-senate-race/ (original: https://montanafreepress.org/2026/09/11/alme-holds-an-8-point-lead-over-bodnar-in-senate-race/) | Montana Free Press (the sponsor) article on its Rutgers-Eagleton poll: Aug 27-Sep 7, 845 RV. MTFP blocks direct downloads (HTTP 403), so this is a Wayback copy. The methodology PDF and spreadsheet could not be fetched. |
| `aspect_strategic_2026-09-07_15_memo_p1.jpg`, `aspect_strategic_2026-09-07_15_memo_p2.jpg` | https://pbs.twimg.com/media/HS1n8GbX0AAW-Mz.jpg (p1), https://pbs.twimg.com/media/HS1n7cZXAAAZBwz.jpg (p2); posted at https://x.com/burgessev/status/2102451722702442813 | Aspect Strategic memo images, conducted for Montana Freedom PAC: Sep 7-15, 715 LV. |
| `quantus_2026-09-14_15_release.html` | https://quantusinsights.org/f/latest-survey-alme-leads-as-montana%E2%80%99s-senate-opposition-splits | Quantus release for Sep 14-15. 625 LV analytical base, 644 total respondents. |
| `quantus_2026-09-14_15_crosstabs.pdf` | https://drive.google.com/file/d/1vjVlYWfquYnM82bPyP6BBOws9dgCoRyg/view | Image-only PDF. Q1 (page 6) offers Alme, Bodnar, Bankhead, "Someone else" and Undecided. **Austin is not named.** |
| `kulr_american_pulse_2026-09-19_24_article.html` | https://www.montanarightnow.com/elections/montana-senate-race-kurt-alme-tops-bodnar-and-bankhead-in-new-poll-findings/article_cd8401fb-0470-492c-a53a-c7dfe39552ff.html | Article from the sponsor, KULR-TV/NonStop Local, on its American Pulse poll (Sep 19-24). It gives only Alme, Bodnar and Bankhead. No American Pulse release was found. |
| `concord_cpop_2026-10-06_08_memo.pdf` | https://static1.squarespace.com/static/6a5ff8e3d194df57f8833369/t/6ad1270faee1a77937e9dbec/1792091919214/CPOP+Montana+Statewide+Findings+Memo_10.10.pdf | Concord Public Opinion Partners memo dated Oct 9. Field dates Oct 6-8, 405 LV. |
| `bodnar_campaign_concord_release.html` | https://www.sethformontana.com/news/new-poll-independent-seth-bodnar-takes-the-lead-in-montanas-us-senate-race | The Bodnar campaign's press release of the Concord poll. |
| `peak_insights_2026-10-07_12_memo_image.jpg` | https://pbs.twimg.com/media/HUxR0MLXMAAEDCi.jpg; posted at https://x.com/burgessev/status/2111155739154882819 | Peak Insights memo dated Oct 16. Field dates Oct 7-12, N=500 LV, live calls. |
| `quantus_2026-10-15_18_release.html` | https://quantusinsights.org/polling/f/montana-senate-alme-leads-by-16-as-bodnar-consolidates | Quantus release for Oct 15-18: 686 LV surveyed, 667 on the ballot question. |
| `quantus_2026-10-15_18_crosstabs.pdf` | https://drive.google.com/file/d/1TMRwiyJNkyDCo-tSI1fO_VI111hs8ikL/view | Quantus crosstabs. Q1 is the four-way ballot. Q1+Q2 gives the ballot with leaners. |

## Not retrievable
- Live DDHQ (Vercel bot check), Silver Bulletin (paywall), NYT poll tracker (HTTP 403), FiftyPlusOne poll list (loaded by JavaScript), MTFP methodology PDF and spreadsheet (HTTP 403).
- The Wikipedia-cited Google Drive link for the American Pulse poll (`1yVCO0C-39sMmZfnVqpaDpTBqi2KnDwqT`) is American Pulse's **February 2026** Daines memo, not the September poll, so it was not kept.

## Excluded pollsters (ActiVote, Rasmussen Reports)
No ActiVote or Rasmussen poll of this race was found in VoteHub, RCP, 270toWin, Poliwave, Call the Map or Wikipedia, or by web search.
