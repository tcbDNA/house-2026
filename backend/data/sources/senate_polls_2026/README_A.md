# 2026 Senate polling averages, set A (RealClearPolling)

These were collected on **2026-10-26** to compare against the forecast model. They cover OH, TX, AK, FL, IA, KS, ME and SC.

RealClearPolling (RCP) publishes an average for all 8 races, so Poliwave and FiftyPlusOne were not needed.

## How the pages were obtained

- **RCP's bot check.** RCP race pages sit behind a DataDome bot check. Two Maine pages downloaded live before the check started returning HTTP 403 on every other race page, through both curl and WebFetch.
- **Current numbers come from RCP's data feed.** For every race, the current figures come from `https://orig.realclearpolitics.com/poll/race/<id>/polling_data.json`. The race page itself names this URL as its `pollingDataUrl`. It holds the RCP average and every poll, and polls counted in the average have `"type": "poll_rcp_avg"`. Its `lastBuildDate` is the time RCP last rebuilt that race. For Maine, the feed matches the live HTML exactly.
- **Page HTML for the other races comes from the Wayback Machine.** It is the latest capture taken before RCP blocked access (original HTML via `id_`). For **OH, AK and FL** that capture is older than the feed and shows a different average (see Notes). For **TX, IA, KS and SC**, the captured average and its polls match the feed.
- **How the average is calculated.** Each RCP average checked here equals the simple mean of the polls marked as in the average, rounded to 0.1.
- **Asterisks after pollster names.** RCP's poll table shows each pollster's raw name. Some carry `*` or `**` (e.g. `InsiderAdvantage*`, `PPP**`). Neither the page nor the feed explains what the asterisks mean.
- **Trafalgar's "(R)".** RCP's pollster-group metadata labels Trafalgar as "Trafalgar Group (R)", but the table shows only "Trafalgar Group".

## Files

All retrieval times are 2026-10-26, US Eastern (UTC-4).

| File | URL | Retrieved | Notes |
|---|---|---|---|
| `me/rcp_collins-vs-jackson.html` | https://www.realclearpolling.com/polls/senate/general/2026/maine/collins-vs-jackson (canonical: .../senate/general/2026/collins-vs-jackson) | 15:16 live | Live page. Average 9/23–10/23: Jackson 48.9, Collins 47.5, Jackson +1.4, from 10 polls. |
| `me/rcp_polling_data_9100.json` | https://orig.realclearpolitics.com/poll/race/9100/polling_data.json | 15:27 | lastBuildDate Sat 24 Oct 2026 11:12 -0500. Matches the live HTML. |
| `oh/rcp_polling_data_8689.json` | https://orig.realclearpolitics.com/poll/race/8689/polling_data.json | 15:27 | lastBuildDate Sun 25 Oct 2026 09:58 -0500. Average 9/22–10/22: Brown 48.2, Husted 44.9, Brown +3.3, from 9 polls. **Current source for OH.** |
| `oh/rcp_husted-vs-brown_wayback_20261023184744.html` | https://web.archive.org/web/20261023184744/https://www.realclearpolling.com/polls/senate/special-election/2026/ohio/husted-vs-brown | 15:20 (capture 2026-10-23 18:47Z) | **Stale.** Shows Brown 47.9, Husted 44.8, +3.1 from 12 polls. It still includes Big Data Poll 9/25–27, USA Today/Suffolk 9/23–27 and Quantus 9/21–23, all of which have since left the average. |
| `tx/rcp_polling_data_8867.json` | https://orig.realclearpolitics.com/poll/race/8867/polling_data.json | 15:27 | lastBuildDate Sat 24 Oct 2026 08:00 -0500. Average 10/8–10/21: Talarico 48.4, Paxton 46.9, Talarico +1.5, from 10 polls. |
| `tx/rcp_talarico-vs-paxton_wayback_20261026175401.html` | https://web.archive.org/web/20261026175401/https://www.realclearpolling.com/polls/senate/general/2026/texas/talarico-vs-paxton | 15:20 (capture 2026-10-26 17:54Z) | Same average and polls as the feed. |
| `ak/rcp_polling_data_8754.json` | https://orig.realclearpolitics.com/poll/race/8754/polling_data.json | 15:27 | lastBuildDate Mon 26 Oct 2026 10:05 -0500. Average 9/28–10/16: Peltola 49.0, Sullivan 48.2, Peltola +0.8, from 6 polls. **Current source for AK.** |
| `ak/rcp_peltola-vs-sullivan_wayback_20261023182823.html` | https://web.archive.org/web/20261023182823/https://www.realclearpolling.com/polls/senate/general/2026/alaska/peltola-vs-sullivan | 15:20 (capture 2026-10-23 18:28Z) | **Stale.** Shows Peltola 49.4, Sullivan 48.2, +1.2 from 5 polls. RCP added Rasmussen 10/12–15 on 10/26. |
| `fl/rcp_polling_data_8948.json` | https://orig.realclearpolitics.com/poll/race/8948/polling_data.json | 15:27 | lastBuildDate Wed 21 Oct 2026 15:53 -0500. Average 9/28–10/20: Moody 49.5, Nixon 42.2, Moody +7.3, from 6 polls. **Current source for FL.** |
| `fl/rcp_moody-vs-nixon_wayback_20261023182512.html` | https://web.archive.org/web/20261023182512/https://www.realclearpolling.com/polls/senate/general/2026/florida/moody-vs-nixon | 15:20 (capture 2026-10-23 18:25Z) | **Differs from the feed.** Shows Moody 49.4, Nixon 42.4, +7.0 from 9 polls. It also includes YouGov 9/24–10/3, InsiderAdvantage 9/20–21 and Quantus 9/8–10. Both versions include co/efficient (updated 10/21 15:52 -0500). The feed was built 39 s later (15:53) and has only 6 polls, so this capture is probably a cached render. The live page could not be fetched to confirm which version it shows today. |
| `ia/rcp_polling_data_8930.json` | https://orig.realclearpolitics.com/poll/race/8930/polling_data.json | 15:27 | lastBuildDate Sun 25 Oct 2026 09:55 -0500. Average 9/29–10/22: Hinson 46.1, Turek 45.5, Hinson +0.6, from 8 polls. |
| `ia/rcp_turek-vs-hinson_wayback_20261026045924.html` | https://web.archive.org/web/20261026045924/https://www.realclearpolling.com/polls/senate/general/2026/iowa/turek-vs-hinson | 15:22 (capture 2026-10-26 04:59Z) | Same as the feed. The `iowa/hinson-vs-turek` slug points to the same RCP race (id 8930). |
| `ks/rcp_polling_data_9106.json` | https://orig.realclearpolitics.com/poll/race/9106/polling_data.json | 15:27 | lastBuildDate Thu 15 Oct 2026 18:39 -0500. Average 9/8–10/14: Marshall 46.0, Hamilton 45.7, Marshall +0.3, from 6 polls. |
| `ks/rcp_marshall-vs-hamilton_wayback_20261023182935.html` | https://web.archive.org/web/20261023182935/https://www.realclearpolling.com/polls/senate/general/2026/kansas/marshall-vs-hamilton | 15:22 (capture 2026-10-23 18:29Z) | Same as the feed. |
| `sc/rcp_polling_data_9115.json` | https://orig.realclearpolitics.com/poll/race/9115/polling_data.json | 15:27 | lastBuildDate Sun 18 Oct 2026 21:17 -0500. Average 9/28–10/18: Graham Nordone 48.0, Andrews 45.3, Graham Nordone +2.7, from 3 polls. |
| `sc/rcp_graham-nordone-vs-andrews_wayback_20261023185020.html` | https://web.archive.org/web/20261023185020/https://www.realclearpolling.com/polls/senate/general/2026/south-carolina/graham-nordone-vs-andrews | 15:20 (capture 2026-10-23 18:50Z) | Same as the feed. RCP names the Republican "Graham Nordone" (Darline Graham Nordone). |

`rcp_latest_polls_senate.html` and `README_B.md` in this directory belong to a different collection (set B) and are not part of this list.

## Excluded pollsters (ActiVote, Rasmussen Reports)

- **ActiVote** does not appear anywhere in these 8 RCP feeds.
- **Rasmussen Reports is in the RCP average** for:
  - AK: 10/12–15, 775 LV, Sullivan 48, Peltola 47. This is the ranked-choice "final ballot" question. The first-choice question was Peltola 44, Sullivan 42.
  - ME: 10/5–8, 804 LV.
  - OH: 10/12–14, 901 LV.
  - SC: 10/5–8, 837 LV.
  - TX: 10/20–21, 965 LV.
- **Rasmussen is listed but not in the average** for IA (9/28–30 and 9/8–10).
- FL and KS have no Rasmussen polls.

## Sponsor and partisanship checks

The sponsor column of the returned JSON comes from each pollster's own release, linked from RCP's poll row. The release files are not saved here.

These releases could not be retrieved:
- NYT/Siena: nytimes.com returned 403.
- Bowling Green/YouGov: scholarworks.bgsu.edu returned 403.
- Stetson: stetson.edu returned 403.
- Quantus Insights: the site renders its content with JavaScript, so the text could not be read.

For those, the sponsor is given as RCP's label or as "not stated".
