# Final RealClearPolitics averages for the backtest (2022, 2024)

These are RCP's last pre-election U.S. Senate averages and generic-ballot averages, with every poll RCP listed and a flag for the polls inside each average. They are for the forecast backtest.

- **Retrieved:** 2026-10-26, for every file here.
- **Sources:** RCP's own race pages, as archived by the Wayback Machine (raw copies fetched with the `id_` suffix), plus RCP's own data feed `https://orig.realclearpolitics.com/poll/race/<id>/polling_data.json`. The feed shows the race as it stands today. No news stories, Wikipedia pages or search snippets were used, and no number was estimated.
- **Live pages:** the live RCP pages block bots, so none were fetched.
- **Code:** nothing in the downloaded files was run. Everything was parsed by `scripts/` as plain data.

## CSV files

| File | Rows |
|---|---|
| `senate_2022_rcp_final.csv` | 14 races: 14 `RCP Average` rows + 297 poll rows |
| `senate_2024_rcp_final.csv` | 11 races: 11 `RCP Average` rows + 439 poll rows |
| `generic_ballot_rcp_final.csv` | 2022 and 2024: 2 `RCP Average` rows + 475 poll rows (RCP's full list for the cycle) |

Each file has one row per (state, poll), plus one row per state where `pollster = RCP Average`.

| Column | Meaning |
|---|---|
| `year`, `state` | Election year and USPS code (`US` for the generic ballot). |
| `pollster` | Pollster name exactly as RCP printed it, including its `(R)`, `(D)`, `*` and `**` marks. |
| `start`, `end` | Field dates in ISO format. The year comes from RCP's feed (`data_end_date`) for the same poll id, or from the election year if the feed has no date. For the `RCP Average` row, these are the first and last dates of the average's window. |
| `population`, `n` | Split from RCP's "Sample" text (`1094 LV` → `LV`, `1094`). `n` is blank when RCP printed only `LV` or `RV`. Both are blank on the average row. |
| `dem`, `rep` | Percentages exactly as RCP printed them. A third candidate's share, such as Oliver (L) in Georgia, is not carried. |
| `in_average` | `yes` if RCP counted the poll in the average. The 2022 pages mark these rows with the `isInRcpAvg` class; the 2024 pages give them `type: poll_rcp_avg`. **The `RCP Average` row itself is `no`**, so `in_average == "yes"` returns exactly the polls RCP averaged. |
| `excluded_pollster` | `yes` for Rasmussen Reports or ActiVote. These rows are listed like any other poll and flagged. |
| `source_url` | RCP's page for the race, or the feed URL for a race taken from the feed. |
| `archive_url` | The Wayback capture used. It is blank for a race taken from the feed. |
| extra columns | `race`, `race_id` (RCP id), `dem_candidate`, `rep_candidate`, `spread` (RCP's spread text), `date_raw`, `sample_raw`, `data_source` (`wayback_page` or `rcp_feed_current_2026-10-26`), `notes` |

**Check:** in all 27 averages, the simple mean of the `in_average == yes` polls rounds to RCP's published D and R figures. That confirms the flags.

## Final averages

Which capture was used: the last good Wayback capture of each page taken before 08:00 UTC on Nov 9, 2022 or Nov 6, 2024. That is no later than midnight Pacific time on election day, and before RCP added any results rows. Each average was also compared with RCP's current feed. Wherever an archived copy exists, the average and the set of averaged polls match the feed exactly; the exceptions are listed under "Caveats and gaps".

### 2022 Senate (14 races with an RCP average)

| State | Race | Window | D | R | RCP spread | Polls in avg (of which Rasmussen) | Polls listed | Source |
|---|---|---|---|---|---|---|---|---|
| AZ | Masters vs. Kelly | 11/1–11/7 | 48.0 | 48.3 | Masters +0.3 | 4 (0) | 28 | Wayback 2022-11-08 19:23 |
| CO | O'Dea vs. Bennet | 10/26–11/5 | 50.0 | 44.3 | Bennet +5.7 | 3 (0) | 10 | Wayback 2022-11-09 02:39 |
| CT | Levy vs. Blumenthal | 10/10–10/23 | 52.7 | 41.7 | Blumenthal +11.0 | 3 (0) | 7 | Wayback 2022-10-27 05:22 (**pre-window**, see caveats) |
| FL | Rubio vs. Demings | 10/17–11/6 | 43.6 | 52.4 | Rubio +8.8 | 5 (0) | 20 | Wayback 2022-11-08 23:20 |
| GA | Walker vs. Warnock | 11/2–11/7 | 47.4 | 48.8 | Walker +1.4 | 5 (0) | 48 | Wayback 2022-11-08 21:36 |
| MO | Schmitt vs. Busch Valentine | 10/24–11/1 | 41.3 | 52.0 | Schmitt +10.7 | 4 (0) | 10 | Wayback 2022-11-07 21:53 |
| NC | Budd vs. Beasley | 11/1–11/6 | 44.8 | 51.0 | Budd +6.2 | 4 (0) | 23 | Wayback 2022-11-08 17:02 |
| NH | Bolduc vs. Hassan | 10/28–11/6 | 48.7 | 47.3 | Hassan +1.4 | 6 (0) | 23 | Wayback 2022-11-08 23:52 |
| NV | Laxalt vs. Cortez Masto | 10/24–11/7 | 45.4 | 48.8 | Laxalt +3.4 | 5 (0) | 29 | Wayback 2022-11-09 02:39 |
| NY | Schumer vs. Pinion | 10/26–10/31 | 54.7 | 39.3 | Schumer +15.4 | 3 (0) | 10 | Wayback 2022-11-09 07:53 |
| OH | Vance vs. Ryan | 10/30–11/5 | 43.8 | 51.8 | Vance +8.0 | 5 (0) | 19 | Wayback 2022-11-08 23:23 |
| PA | Oz vs. Fetterman | 10/28–11/3 | 46.8 | 47.2 | Oz +0.4 | 5 (0) | 34 | Wayback 2022-11-08 15:56 |
| WA | Smiley vs. Murray | 10/25–10/31 | 49.3 | 46.3 | Murray +3.0 | 3 (0) | 14 | Wayback 2022-11-08 00:09 |
| WI | Johnson vs. Barnes | 10/24–11/5 | 46.6 | 50.2 | Johnson +3.6 | 5 (0) | 22 | Wayback 2022-11-08 19:24 |

Rasmussen Reports appears in the 2022 Senate poll lists only for GA and PA, and neither poll is in an average. ActiVote appears in no RCP list, in any year.

### 2024 Senate (11 races with an RCP average)

| State | Race | Window | D | R | RCP spread | Polls in avg (of which Rasmussen) | Polls listed | Source |
|---|---|---|---|---|---|---|---|---|
| AZ | Lake vs. Gallego | 10/25–11/4 | 48.6 | 46.0 | Gallego +2.6 | 8 (1) | 60 | Wayback 2024-11-05 20:34 |
| FL | Scott vs. Mucarsel-Powell | 9/29–11/1 | 44.3 | 48.9 | Scott +4.6 | 7 (0) | 14 | Wayback 2024-11-05 23:27 |
| MI | Rogers vs. Slotkin | 10/24–11/4 | 48.4 | 46.1 | Slotkin +2.3 | 13 (1) | 74 | Wayback 2024-11-05 11:28 |
| MN | White vs. Klobuchar | 10/16–11/4 | 52.0 | 39.0 | Klobuchar +13.0 | 4 (1) | 10 | Wayback 2024-11-06 15:35 (**morning after**, see caveats) |
| MT | Sheehy vs. Tester | 10/5–11/4 | 43.0 | 50.7 | Sheehy +7.7 | 3 (0) | 12 | Wayback 2024-11-05 11:28 |
| NV | Brown vs. Rosen | 10/24–11/4 | 48.8 | 43.9 | Rosen +4.9 | 8 (1) | 44 | Wayback 2024-11-05 11:28 |
| OH | Brown vs. Moreno | 10/23–11/4 | 46.3 | 48.0 | Moreno +1.7 | 4 (0) | 26 | Wayback 2024-11-05 11:28 |
| PA | McCormick vs. Casey | 10/21–11/4 | 48.1 | 46.3 | Casey +1.8 | 16 (1) | 94 | Wayback 2024-11-05 22:50 |
| TX | Cruz vs. Allred | 10/22–11/4 | 44.8 | 49.2 | Cruz +4.4 | 5 (1) | 26 | Wayback 2024-11-05 11:29 |
| VA | Cao vs. Kaine | 10/19–11/4 | 52.0 | 41.2 | Kaine +10.8 | 5 (1) | 15 | **RCP feed** (see caveats) |
| WI | Hovde vs. Baldwin | 10/16–11/4 | 48.9 | 47.1 | Baldwin +1.8 | 14 (1) | 64 | Wayback 2024-11-05 11:28 |

### Generic congressional ballot

| Year | Window | D | R | RCP spread | Polls in avg (of which Rasmussen) | Polls listed | Source |
|---|---|---|---|---|---|---|---|
| 2022 | 10/18–11/6 | 45.5 | 48.0 | Republicans +2.5 | 17 (1: Rasmussen 10/30–11/3, D 43 / R 48) | 297 | Wayback 2022-11-08 17:37 |
| 2024 | 10/14–11/2 | 46.7 | 47.0 | Republicans +0.3 | 11 (0) | 178 | Wayback 2024-11-05 18:09 |

## Races RCP did not average

These races have an RCP page, but the page showed no average on election eve. They are left out of the CSVs. Raw copies and feeds are kept.

- **2022, no `RCP Average` row on the archived page:** AL (Nov 1), CA (Nov 9, 02:40 UTC), IA (Nov 1), IL (Nov 2), KS (Nov 3), ND (Nov 3), OR (Oct 27), **UT, Lee vs. McMullin** (Nov 7, 18:53 UTC; 7 polls listed, none averaged), VT (Oct 21).
- **2022, no archived copy found; the current feed has no average:** AR, KY, LA (open primary), OK (regular), OK (special), SD, SC, MD, and AK (all three ranked-choice pages: 1st round, 2nd round, final round).
- **2024, average hidden (`hideRcpAverageRow: true`) or absent on the archived page:** MD and NM (Nov 5), MO and ND (Nov 5), WV (Oct 27), and CA, CT, DE, HI, IN, MA, ME, MS, NJ, NY, TN, WA, WY and both Nebraska races (all Nov 6, 15:35 UTC, the morning after the election).
  - **NE, Fischer vs. Osborn (I)** (race 8590) listed only two polls, Economist/YouGov 10/21–10/28 (Fischer 50, Osborn 43) and NYT/Siena 10/23–10/26 (Fischer 48, Osborn 46), with no average. The NE special (Ricketts vs. Love, race 8464) also has no average.
- **2024, no archived copy found; the current feed has no average:** RI, UT and VT.

## Caveats and gaps

1. **CT 2022.** No capture between Oct 28 and Nov 9 could be found. The only usable copy is from Oct 27 and shows Blumenthal +11.0 (3 polls, 10/10–10/23). Today's feed has the same 52.7/41.7 but marks the average hidden, with a placeholder date of 12/31. So it is unconfirmed whether that average was still on the page on election eve; every CT row carries a note saying so.
2. **VA 2024.** The only capture before the election is from Nov 1, 23:59 UTC. It shows an earlier average, Kaine +11.3 (D 51.8 / R 40.5, 4 polls, 10/19–10/29). The CSV uses the final average from RCP's feed instead: Kaine +10.8 (5 polls, 10/19–11/4). The four polls in the earlier average are also in the final one. The Nov 1 copy is kept (`rcp_2024_senate/va_cao-vs-kaine_wayback_20241101235957.html`).
3. **MN 2024.** The only capture near the election is from the morning after (Nov 6, 15:35 UTC). It has no results row yet, and its average and averaged polls match RCP's feed exactly.
4. **Same-day updates.** RCP changed some averages on election day. Earlier captures showed CO Bennet +5.3 (Nov 7, 21:34 UTC), NV Laxalt +2.9 (Nov 8, 07:36 UTC) and NY Schumer +14.4 (Nov 6, 17:57 UTC). The CSVs use the later captures, which match RCP's feed, and the superseded copies were not kept. The archive URLs: https://web.archive.org/web/20221107213410/https://www.realclearpolitics.com/epolls/2022/senate/co/colorado_senate_odea_vs_bennet-7773.html, https://web.archive.org/web/20221108073601/https://www.realclearpolitics.com/epolls/2022/senate/nv/nevada_senate_laxalt_vs_cortez_masto-7392.html, https://web.archive.org/web/20221106175721/https://www.realclearpolitics.com/epolls/2022/senate/ny/new_york_senate_schumer_vs_pinion-7771.html.
5. **Georgia 2022, 3-way average.** RCP also averaged Walker vs. Warnock vs. Oliver (race 7936): Walker 47.3, Warnock 45.8, Oliver 3.8, Walker +1.5, window 10/15–10/27, from a Nov 3 capture. It is left out of the CSV so Georgia has a single average. The 2-way race 7329 is the one RCP's Senate map linked. The raw copy is kept.
6. **A quirk in the current feed.** The 2022 generic-ballot feed marks one extra poll as averaged: Rasmussen 4/24–4/26, D 43 / R 42. That poll is **not** in the election-eve page's average. The CSV follows the archived page.
7. **One date typo.** RCP printed the AZ 2024 The Hill/Emerson poll as "10/30 - 10/2". It is kept as published (end 2024-10-02) and flagged in `notes`.
8. **Independents.** UT 2022 (McMullin), NE 2024 (Osborn) and ME 2024 (King) had no RCP average, so none of the CSV rows involve an independent.

## Rebuilding the CSVs

```
cd backend/data/sources/polls_backtest
python3 -I scripts/build.py "$PWD" scripts/races.json > build_log.tsv   # writes the three CSVs
python3 -I scripts/verify.py "$PWD" > verify_log.txt                   # archive vs. current-feed comparison
```

- `scripts/races.json` lists every race page that was checked.
- `build_log.tsv` gives each one's outcome.
- Each `_captures.tsv` maps a race tag to its capture timestamp, URL and file. `NONE` means no usable capture was found.

## Files

All retrieved **2026-10-26**.

### Archived race pages

| File | Live URL | Archive URL | Capture (UTC) | What the page shows |
|---|---|---|---|---|
| `rcp_2022_senate/al_7754_wayback_20221101192852.html` | https://www.realclearpolitics.com/epolls/2022/senate/al/alabama_senate_britt_vs_boyd-7754.html | https://web.archive.org/web/20221101192852/https://www.realclearpolitics.com/epolls/2022/senate/al/alabama_senate_britt_vs_boyd-7754.html | 2022-11-01 19:28 | No RCP Average row |
| `rcp_2022_senate/az_7390_wayback_20221108192332.html` | https://www.realclearpolitics.com/epolls/2022/senate/az/arizona-senate-masters-vs-kelly-7390.html | https://web.archive.org/web/20221108192332/https://www.realclearpolitics.com/epolls/2022/senate/az/arizona-senate-masters-vs-kelly-7390.html | 2022-11-08 19:23 | RCP Average 11-01–11-07: D 48.0 / R 48.3 (Masters +0.3); 4 of 28 listed polls in average |
| `rcp_2022_senate/ca_7513_wayback_20221109024002.html` | https://www.realclearpolitics.com/epolls/2022/senate/ca/california_senate_meuser_vs_padilla-7513.html | https://web.archive.org/web/20221109024002/https://www.realclearpolitics.com/epolls/2022/senate/ca/california_senate_meuser_vs_padilla-7513.html | 2022-11-09 02:40 | No RCP Average row |
| `rcp_2022_senate/co_7773_wayback_20221109023934.html` | https://www.realclearpolitics.com/epolls/2022/senate/co/colorado_senate_odea_vs_bennet-7773.html | https://web.archive.org/web/20221109023934/https://www.realclearpolitics.com/epolls/2022/senate/co/colorado_senate_odea_vs_bennet-7773.html | 2022-11-09 02:39 | RCP Average 10-26–11-05: D 50.0 / R 44.3 (Bennet +5.7); 3 of 10 listed polls in average |
| `rcp_2022_senate/ct_7686_wayback_20221027052247.html` | https://www.realclearpolitics.com/epolls/2022/senate/ct/connecticut_senate_levy_vs_blumenthal-7686.html | https://web.archive.org/web/20221027052247/https://www.realclearpolitics.com/epolls/2022/senate/ct/connecticut_senate_levy_vs_blumenthal-7686.html | 2022-10-27 05:22 | RCP Average 10-10–10-23: D 52.7 / R 41.7 (Blumenthal +11.0); 3 of 7 listed polls in average |
| `rcp_2022_senate/fl_7382_wayback_20221108232016.html` | https://www.realclearpolitics.com/epolls/2022/senate/fl/florida-senate-rubio-vs-demings-7382.html | https://web.archive.org/web/20221108232016/https://www.realclearpolitics.com/epolls/2022/senate/fl/florida-senate-rubio-vs-demings-7382.html | 2022-11-08 23:20 | RCP Average 10-17–11-06: D 43.6 / R 52.4 (Rubio +8.8); 5 of 20 listed polls in average |
| `rcp_2022_senate/ga_7329_wayback_20221108213622.html` | https://www.realclearpolitics.com/epolls/2022/senate/ga/georgia-senate-walker-vs-warnock-7329.html | https://web.archive.org/web/20221108213622/https://www.realclearpolitics.com/epolls/2022/senate/ga/georgia-senate-walker-vs-warnock-7329.html | 2022-11-08 21:36 | RCP Average 11-02–11-07: D 47.4 / R 48.8 (Walker +1.4); 5 of 48 listed polls in average |
| `rcp_2022_senate/ga_7936_wayback_20221103213649.html` | https://www.realclearpolitics.com/epolls/2022/senate/ga/georgia_senate_walker_vs_warnock_vs_oliver-7936.html | https://web.archive.org/web/20221103213649/https://www.realclearpolitics.com/epolls/2022/senate/ga/georgia_senate_walker_vs_warnock_vs_oliver-7936.html | 2022-11-03 21:36 | RCP Average 10-15–10-27: D 45.8 / R 47.3 (Walker +1.5); 4 of 14 listed polls in average |
| `rcp_2022_senate/ia_7738_wayback_20221101192215.html` | https://www.realclearpolitics.com/epolls/2022/senate/ia/iowa_senate_grassley_vs_franken-7738.html | https://web.archive.org/web/20221101192215/https://www.realclearpolitics.com/epolls/2022/senate/ia/iowa_senate_grassley_vs_franken-7738.html | 2022-11-01 19:22 | No RCP Average row |
| `rcp_2022_senate/il_7772_wayback_20221102150844.html` | https://www.realclearpolitics.com/epolls/2022/senate/il/illinois_senate_salvi_vs_duckworth-7772.html | https://web.archive.org/web/20221102150844/https://www.realclearpolitics.com/epolls/2022/senate/il/illinois_senate_salvi_vs_duckworth-7772.html | 2022-11-02 15:08 | No RCP Average row |
| `rcp_2022_senate/ks_7924_wayback_20221103005411.html` | https://www.realclearpolitics.com/epolls/2022/senate/ks/kansas_senate_moran_vs_holland-7924.html | https://web.archive.org/web/20221103005411/https://www.realclearpolitics.com/epolls/2022/senate/ks/kansas_senate_moran_vs_holland-7924.html | 2022-11-03 00:54 | No RCP Average row |
| `rcp_2022_senate/mo_7682_wayback_20221107215322.html` | https://www.realclearpolitics.com/epolls/2022/senate/mo/missouri_senate_schmitt_vs_busch_valentine-7682.html | https://web.archive.org/web/20221107215322/https://www.realclearpolitics.com/epolls/2022/senate/mo/missouri_senate_schmitt_vs_busch_valentine-7682.html | 2022-11-07 21:53 | RCP Average 10-24–11-01: D 41.3 / R 52.0 (Schmitt +10.7); 4 of 10 listed polls in average |
| `rcp_2022_senate/nc_7588_wayback_20221108170204.html` | https://www.realclearpolitics.com/epolls/2022/senate/nc/north_carolina_senate_budd_vs_beasley-7588.html | https://web.archive.org/web/20221108170204/https://www.realclearpolitics.com/epolls/2022/senate/nc/north_carolina_senate_budd_vs_beasley-7588.html | 2022-11-08 17:02 | RCP Average 11-01–11-06: D 44.8 / R 51.0 (Budd +6.2); 4 of 23 listed polls in average |
| `rcp_2022_senate/nd_7527_wayback_20221103005351.html` | https://www.realclearpolitics.com/epolls/2022/senate/nd/north_dakota_senate_hoeven_vs_christiansen-7527.html | https://web.archive.org/web/20221103005351/https://www.realclearpolitics.com/epolls/2022/senate/nd/north_dakota_senate_hoeven_vs_christiansen-7527.html | 2022-11-03 00:53 | No RCP Average row |
| `rcp_2022_senate/nh_7379_wayback_20221108235226.html` | https://www.realclearpolitics.com/epolls/2022/senate/nh/new-hampshire-senate-bolduc-vs-hassan-7379.html | https://web.archive.org/web/20221108235226/https://www.realclearpolitics.com/epolls/2022/senate/nh/new-hampshire-senate-bolduc-vs-hassan-7379.html | 2022-11-08 23:52 | RCP Average 10-28–11-06: D 48.7 / R 47.3 (Hassan +1.4); 6 of 23 listed polls in average |
| `rcp_2022_senate/nv_7392_wayback_20221109023958.html` | https://www.realclearpolitics.com/epolls/2022/senate/nv/nevada_senate_laxalt_vs_cortez_masto-7392.html | https://web.archive.org/web/20221109023958/https://www.realclearpolitics.com/epolls/2022/senate/nv/nevada_senate_laxalt_vs_cortez_masto-7392.html | 2022-11-09 02:39 | RCP Average 10-24–11-07: D 45.4 / R 48.8 (Laxalt +3.4); 5 of 29 listed polls in average |
| `rcp_2022_senate/ny_7771_wayback_20221109075316.html` | https://www.realclearpolitics.com/epolls/2022/senate/ny/new_york_senate_schumer_vs_pinion-7771.html | https://web.archive.org/web/20221109075316/https://www.realclearpolitics.com/epolls/2022/senate/ny/new_york_senate_schumer_vs_pinion-7771.html | 2022-11-09 07:53 | RCP Average 10-26–10-31: D 54.7 / R 39.3 (Schumer +15.4); 3 of 10 listed polls in average |
| `rcp_2022_senate/oh_7624_wayback_20221108232340.html` | https://www.realclearpolitics.com/epolls/2022/senate/oh/ohio_senate_vance_vs_ryan-7624.html | https://web.archive.org/web/20221108232340/https://www.realclearpolitics.com/epolls/2022/senate/oh/ohio_senate_vance_vs_ryan-7624.html | 2022-11-08 23:23 | RCP Average 10-30–11-05: D 43.8 / R 51.8 (Vance +8.0); 5 of 19 listed polls in average |
| `rcp_2022_senate/or_7744_wayback_20221027223416.html` | https://www.realclearpolitics.com/epolls/2022/senate/or/oregon_senate_perkins_vs_wyden-7744.html | https://web.archive.org/web/20221027223416/https://www.realclearpolitics.com/epolls/2022/senate/or/oregon_senate_perkins_vs_wyden-7744.html | 2022-10-27 22:34 | No RCP Average row |
| `rcp_2022_senate/pa_7695_wayback_20221108155619.html` | https://www.realclearpolitics.com/epolls/2022/senate/pa/pennsylvania_senate_oz_vs_fetterman-7695.html | https://web.archive.org/web/20221108155619/https://www.realclearpolitics.com/epolls/2022/senate/pa/pennsylvania_senate_oz_vs_fetterman-7695.html | 2022-11-08 15:56 | RCP Average 10-28–11-03: D 46.8 / R 47.2 (Oz +0.4); 5 of 34 listed polls in average |
| `rcp_2022_senate/ut_7735_wayback_20221107185327.html` | https://www.realclearpolitics.com/epolls/2022/senate/ut/utah_senate_lee_vs_mcmullin-7735.html | https://web.archive.org/web/20221107185327/https://www.realclearpolitics.com/epolls/2022/senate/ut/utah_senate_lee_vs_mcmullin-7735.html | 2022-11-07 18:53 | No RCP Average row |
| `rcp_2022_senate/vt_7905_wayback_20221021154013.html` | https://www.realclearpolitics.com/epolls/2022/senate/vt/vermont_senate_malloy_vs_welch-7905.html | https://web.archive.org/web/20221021154013/https://www.realclearpolitics.com/epolls/2022/senate/vt/vermont_senate_malloy_vs_welch-7905.html | 2022-10-21 15:40 | No RCP Average row |
| `rcp_2022_senate/wa_7400_wayback_20221108000928.html` | https://www.realclearpolitics.com/epolls/2022/senate/wa/washington_senate_smiley_vs_murray-7400.html | https://web.archive.org/web/20221108000928/https://www.realclearpolitics.com/epolls/2022/senate/wa/washington_senate_smiley_vs_murray-7400.html | 2022-11-08 00:09 | RCP Average 10-25–10-31: D 49.3 / R 46.3 (Murray +3.0); 3 of 14 listed polls in average |
| `rcp_2022_senate/wi_7758_wayback_20221108192415.html` | https://www.realclearpolitics.com/epolls/2022/senate/wi/wisconsin_senate_johnson_vs_barnes-7758.html | https://web.archive.org/web/20221108192415/https://www.realclearpolitics.com/epolls/2022/senate/wi/wisconsin_senate_johnson_vs_barnes-7758.html | 2022-11-08 19:24 | RCP Average 10-24–11-05: D 46.6 / R 50.2 (Johnson +3.6); 5 of 22 listed polls in average |
| `rcp_2024_senate/az_lake-vs-gallego_wayback_20241105203413.html` | https://www.realclearpolling.com/polls/senate/general/2024/arizona/lake-vs-gallego | https://web.archive.org/web/20241105203413/https://www.realclearpolling.com/polls/senate/general/2024/arizona/lake-vs-gallego | 2024-11-05 20:34 | RCP Average 10-25–11-04: D 48.6 / R 46.0 (Gallego +2.6); 8 of 60 listed polls in average |
| `rcp_2024_senate/ca_garvey-vs-schiff_wayback_20241106153545.html` | https://www.realclearpolling.com/polls/senate/general/2024/california/garvey-vs-schiff | https://web.archive.org/web/20241106153545/https://www.realclearpolling.com/polls/senate/general/2024/california/garvey-vs-schiff | 2024-11-06 15:35 | RCP Average hidden (`hideRcpAverageRow: true`) |
| `rcp_2024_senate/ct_murphy-vs-corey_wayback_20241106153551.html` | https://www.realclearpolling.com/polls/senate/general/2024/connecticut/murphy-vs-corey | https://web.archive.org/web/20241106153551/https://www.realclearpolling.com/polls/senate/general/2024/connecticut/murphy-vs-corey | 2024-11-06 15:35 | No RCP Average row |
| `rcp_2024_senate/de_blunt-rochester-vs-hansen_wayback_20241106153551.html` | https://www.realclearpolling.com/polls/senate/general/2024/delaware/blunt-rochester-vs-hansen | https://web.archive.org/web/20241106153551/https://www.realclearpolling.com/polls/senate/general/2024/delaware/blunt-rochester-vs-hansen | 2024-11-06 15:35 | No RCP Average row |
| `rcp_2024_senate/fl_scott-vs-mucarsel-powell_wayback_20241105232729.html` | https://www.realclearpolling.com/polls/senate/general/2024/florida/scott-vs-mucarsel-powell | https://web.archive.org/web/20241105232729/https://www.realclearpolling.com/polls/senate/general/2024/florida/scott-vs-mucarsel-powell | 2024-11-05 23:27 | RCP Average 09-29–11-01: D 44.3 / R 48.9 (Scott +4.6); 7 of 14 listed polls in average |
| `rcp_2024_senate/hi_hirono-vs-republican_wayback_20241106153552.html` | https://www.realclearpolling.com/polls/senate/general/2024/hawaii/hirono-vs-republican | https://web.archive.org/web/20241106153552/https://www.realclearpolling.com/polls/senate/general/2024/hawaii/hirono-vs-republican | 2024-11-06 15:35 | No RCP Average row |
| `rcp_2024_senate/in_banks-vs-mccray_wayback_20241106153553.html` | https://www.realclearpolling.com/polls/senate/general/2024/indiana/banks-vs-mccray | https://web.archive.org/web/20241106153553/https://www.realclearpolling.com/polls/senate/general/2024/indiana/banks-vs-mccray | 2024-11-06 15:35 | RCP Average hidden (`hideRcpAverageRow: true`) |
| `rcp_2024_senate/me_king-vs-kouzounas-vs-costello-vs-cherry_wayback_20241106153553.html` | https://www.realclearpolling.com/polls/senate/general/2024/maine/king-vs-kouzounas-vs-costello-vs-cherry | https://web.archive.org/web/20241106153553/https://www.realclearpolling.com/polls/senate/general/2024/maine/king-vs-kouzounas-vs-costello-vs-cherry | 2024-11-06 15:35 | No RCP Average row |
| `rcp_2024_senate/md_hogan-vs-alsobrooks_wayback_20241105232730.html` | https://www.realclearpolling.com/polls/senate/general/2024/maryland/hogan-vs-alsobrooks | https://web.archive.org/web/20241105232730/https://www.realclearpolling.com/polls/senate/general/2024/maryland/hogan-vs-alsobrooks | 2024-11-05 23:27 | RCP Average hidden (`hideRcpAverageRow: true`) |
| `rcp_2024_senate/ma_deaton-vs-warren_wayback_20241106153555.html` | https://www.realclearpolling.com/polls/senate/general/2024/massachusetts/deaton-vs-warren | https://web.archive.org/web/20241106153555/https://www.realclearpolling.com/polls/senate/general/2024/massachusetts/deaton-vs-warren | 2024-11-06 15:35 | RCP Average hidden (`hideRcpAverageRow: true`) |
| `rcp_2024_senate/mi_rogers-vs-slotkin_wayback_20241105112834.html` | https://www.realclearpolling.com/polls/senate/general/2024/michigan/rogers-vs-slotkin | https://web.archive.org/web/20241105112834/https://www.realclearpolling.com/polls/senate/general/2024/michigan/rogers-vs-slotkin | 2024-11-05 11:28 | RCP Average 10-24–11-04: D 48.4 / R 46.1 (Slotkin +2.3); 13 of 74 listed polls in average |
| `rcp_2024_senate/mn_white-vs-klobuchar_wayback_20241106153555.html` | https://www.realclearpolling.com/polls/senate/general/2024/minnesota/white-vs-klobuchar | https://web.archive.org/web/20241106153555/https://www.realclearpolling.com/polls/senate/general/2024/minnesota/white-vs-klobuchar | 2024-11-06 15:35 | RCP Average 10-16–11-04: D 52.0 / R 39.0 (Klobuchar +13.0); 4 of 10 listed polls in average |
| `rcp_2024_senate/ms_wicker-vs-democrat_wayback_20241106153557.html` | https://www.realclearpolling.com/polls/senate/general/2024/mississippi/wicker-vs-democrat | https://web.archive.org/web/20241106153557/https://www.realclearpolling.com/polls/senate/general/2024/mississippi/wicker-vs-democrat | 2024-11-06 15:35 | No RCP Average row |
| `rcp_2024_senate/mo_hawley-vs-kunce_wayback_20241105030820.html` | https://www.realclearpolling.com/polls/senate/general/2024/missouri/hawley-vs-kunce | https://web.archive.org/web/20241105030820/https://www.realclearpolling.com/polls/senate/general/2024/missouri/hawley-vs-kunce | 2024-11-05 03:08 | No RCP Average row |
| `rcp_2024_senate/mt_sheehy-vs-tester_wayback_20241105112842.html` | https://www.realclearpolling.com/polls/senate/general/2024/montana/sheehy-vs-tester | https://web.archive.org/web/20241105112842/https://www.realclearpolling.com/polls/senate/general/2024/montana/sheehy-vs-tester | 2024-11-05 11:28 | RCP Average 10-05–11-04: D 43.0 / R 50.7 (Sheehy +7.7); 3 of 12 listed polls in average |
| `rcp_2024_senate/ne_fischer-vs-osborn-senate-1_wayback_20241106153558.html` | https://www.realclearpolling.com/polls/senate/general/2024/nebraska/fischer-vs-osborn-senate-1 | https://web.archive.org/web/20241106153558/https://www.realclearpolling.com/polls/senate/general/2024/nebraska/fischer-vs-osborn-senate-1 | 2024-11-06 15:35 | No RCP Average row |
| `rcp_2024_senate/ne-special_ricketts-vs-love_wayback_20241106153608.html` | https://www.realclearpolling.com/polls/senate/special-election/2024/nebraska/ricketts-vs-love | https://web.archive.org/web/20241106153608/https://www.realclearpolling.com/polls/senate/special-election/2024/nebraska/ricketts-vs-love | 2024-11-06 15:36 | No RCP Average row |
| `rcp_2024_senate/nv_brown-vs-rosen_wayback_20241105112858.html` | https://www.realclearpolling.com/polls/senate/general/2024/nevada/brown-vs-rosen | https://web.archive.org/web/20241105112858/https://www.realclearpolling.com/polls/senate/general/2024/nevada/brown-vs-rosen | 2024-11-05 11:28 | RCP Average 10-24–11-04: D 48.8 / R 43.9 (Rosen +4.9); 8 of 44 listed polls in average |
| `rcp_2024_senate/nj_bashaw-vs-kim_wayback_20241106153559.html` | https://www.realclearpolling.com/polls/senate/general/2024/new-jersey/bashaw-vs-kim | https://web.archive.org/web/20241106153559/https://www.realclearpolling.com/polls/senate/general/2024/new-jersey/bashaw-vs-kim | 2024-11-06 15:35 | No RCP Average row |
| `rcp_2024_senate/nm_domenici-vs-heinrich_wayback_20241105232728.html` | https://www.realclearpolling.com/polls/senate/general/2024/new-mexico/domenici-vs-heinrich | https://web.archive.org/web/20241105232728/https://www.realclearpolling.com/polls/senate/general/2024/new-mexico/domenici-vs-heinrich | 2024-11-05 23:27 | RCP Average hidden (`hideRcpAverageRow: true`) |
| `rcp_2024_senate/ny_sapraicone-vs-gillibrand_wayback_20241106153601.html` | https://www.realclearpolling.com/polls/senate/general/2024/new-york/sapraicone-vs-gillibrand | https://web.archive.org/web/20241106153601/https://www.realclearpolling.com/polls/senate/general/2024/new-york/sapraicone-vs-gillibrand | 2024-11-06 15:36 | RCP Average hidden (`hideRcpAverageRow: true`) |
| `rcp_2024_senate/nd_cramer-vs-christiansen_wayback_20241105093428.html` | https://www.realclearpolling.com/polls/senate/general/2024/north-dakota/cramer-vs-christiansen | https://web.archive.org/web/20241105093428/https://www.realclearpolling.com/polls/senate/general/2024/north-dakota/cramer-vs-christiansen | 2024-11-05 09:34 | No RCP Average row |
| `rcp_2024_senate/oh_brown-vs-moreno_wayback_20241105112805.html` | https://www.realclearpolling.com/polls/senate/general/2024/ohio/brown-vs-moreno | https://web.archive.org/web/20241105112805/https://www.realclearpolling.com/polls/senate/general/2024/ohio/brown-vs-moreno | 2024-11-05 11:28 | RCP Average 10-23–11-04: D 46.3 / R 48.0 (Moreno +1.7); 4 of 26 listed polls in average |
| `rcp_2024_senate/pa_mccormick-vs-casey_wayback_20241105225040.html` | https://www.realclearpolling.com/polls/senate/general/2024/pennsylvania/mccormick-vs-casey | https://web.archive.org/web/20241105225040/https://www.realclearpolling.com/polls/senate/general/2024/pennsylvania/mccormick-vs-casey | 2024-11-05 22:50 | RCP Average 10-21–11-04: D 48.1 / R 46.3 (Casey +1.8); 16 of 94 listed polls in average |
| `rcp_2024_senate/tn_blackburn-vs-johnson_wayback_20241106153603.html` | https://www.realclearpolling.com/polls/senate/general/2024/tennessee/blackburn-vs-johnson | https://web.archive.org/web/20241106153603/https://www.realclearpolling.com/polls/senate/general/2024/tennessee/blackburn-vs-johnson | 2024-11-06 15:36 | RCP Average hidden (`hideRcpAverageRow: true`) |
| `rcp_2024_senate/tx_cruz-vs-allred_wayback_20241105112953.html` | https://www.realclearpolling.com/polls/senate/general/2024/texas/cruz-vs-allred | https://web.archive.org/web/20241105112953/https://www.realclearpolling.com/polls/senate/general/2024/texas/cruz-vs-allred | 2024-11-05 11:29 | RCP Average 10-22–11-04: D 44.8 / R 49.2 (Cruz +4.4); 5 of 26 listed polls in average |
| `rcp_2024_senate/va_cao-vs-kaine_wayback_20241101235957.html` | https://www.realclearpolling.com/polls/senate/general/2024/virginia/cao-vs-kaine | https://web.archive.org/web/20241101235957/https://www.realclearpolling.com/polls/senate/general/2024/virginia/cao-vs-kaine | 2024-11-01 23:59 | Earlier RCP Average 10/19–10/29: D 51.8 / R 40.5 (Kaine +11.3), 4 polls. Superseded; the CSV uses the final average from the feed |
| `rcp_2024_senate/wa_garcia-vs-cantwell_wayback_20241106153606.html` | https://www.realclearpolling.com/polls/senate/general/2024/washington/garcia-vs-cantwell | https://web.archive.org/web/20241106153606/https://www.realclearpolling.com/polls/senate/general/2024/washington/garcia-vs-cantwell | 2024-11-06 15:36 | No RCP Average row |
| `rcp_2024_senate/wv_justice-vs-elliott_wayback_20241027044521.html` | https://www.realclearpolling.com/polls/senate/general/2024/west-virginia/justice-vs-elliott | https://web.archive.org/web/20241027044521/https://www.realclearpolling.com/polls/senate/general/2024/west-virginia/justice-vs-elliott | 2024-10-27 04:45 | No RCP Average row |
| `rcp_2024_senate/wi_hovde-vs-baldwin_wayback_20241105112827.html` | https://www.realclearpolling.com/polls/senate/general/2024/wisconsin/hovde-vs-baldwin | https://web.archive.org/web/20241105112827/https://www.realclearpolling.com/polls/senate/general/2024/wisconsin/hovde-vs-baldwin | 2024-11-05 11:28 | RCP Average 10-16–11-04: D 48.9 / R 47.1 (Baldwin +1.8); 14 of 64 listed polls in average |
| `rcp_2024_senate/wy_barrasso-vs-democrat_wayback_20241106153608.html` | https://www.realclearpolling.com/polls/senate/general/2024/wyoming/barrasso-vs-democrat | https://web.archive.org/web/20241106153608/https://www.realclearpolling.com/polls/senate/general/2024/wyoming/barrasso-vs-democrat | 2024-11-06 15:36 | No RCP Average row |
| `rcp_generic_ballot/gcb2022_7361_wayback_20221108173748.html` | https://www.realclearpolitics.com/epolls/other/2022-generic-congressional-vote-7361.html | https://web.archive.org/web/20221108173748/https://www.realclearpolitics.com/epolls/other/2022-generic-congressional-vote-7361.html | 2022-11-08 17:37 | RCP Average 10-18–11-06: D 45.5 / R 48.0 (Republicans +2.5); 17 of 297 listed polls in average |
| `rcp_generic_ballot/gcb2024_wayback_20241105180934.html` | https://www.realclearpolling.com/polls/state-of-the-union/2024/generic-congressional-vote | https://web.archive.org/web/20241105180934/https://www.realclearpolling.com/polls/state-of-the-union/2024/generic-congressional-vote | 2024-11-05 18:09 | RCP Average 10-14–11-02: D 46.7 / R 47.0 (Republicans +0.3); 11 of 178 listed polls in average |

### RCP data feeds (current state, retrieved 2026-10-26)

| File | URL | Title | RCP average in feed |
|---|---|---|---|
| `rcp_feeds/race_7329_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7329/polling_data.json | 2022 Georgia Senate - Walker vs. Warnock | shown: 11/2 - 11/7, Walker 48.8, Warnock 47.4 |
| `rcp_feeds/race_7361_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7361/polling_data.json | 2022 Generic Congressional Vote | shown: 10/18 - 11/6, Republicans 48.0, Democrats 45.5 |
| `rcp_feeds/race_7379_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7379/polling_data.json | 2022 New Hampshire Senate - Bolduc vs. Hassan | shown: 10/28 - 11/6, Hassan 48.7, Bolduc 47.3 |
| `rcp_feeds/race_7382_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7382/polling_data.json | 2022 Florida Senate - Rubio vs. Demings | shown: 10/17 - 11/6, Rubio 52.4, Demings 43.6 |
| `rcp_feeds/race_7390_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7390/polling_data.json | 2022 Arizona Senate - Masters vs. Kelly | shown: 11/1 - 11/7, Masters 48.3, Kelly 48.0 |
| `rcp_feeds/race_7392_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7392/polling_data.json | 2022 Nevada Senate - Laxalt vs. Cortez Masto | shown: 10/24 - 11/7, Laxalt 48.8, Cortez Masto 45.4 |
| `rcp_feeds/race_7400_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7400/polling_data.json | 2022 Washington Senate - Smiley vs. Murray | shown: 10/25 - 10/31, Murray 49.3, Smiley 46.3 |
| `rcp_feeds/race_7513_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7513/polling_data.json | 2022 California Senate - Meuser vs. Padilla | hidden (`show_rcp_avg: 0`, placeholder date 12/31 - 12/31) |
| `rcp_feeds/race_7521_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7521/polling_data.json | 2022 Kentucky Senate - Paul vs. Booker | none |
| `rcp_feeds/race_7522_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7522/polling_data.json | 2022 Louisiana Senate - Open Primary | none |
| `rcp_feeds/race_7527_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7527/polling_data.json | North Dakota Senate - Hoeven vs. Christiansen | none |
| `rcp_feeds/race_7530_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7530/polling_data.json | South Carolina Senate - Scott vs. Matthews | none |
| `rcp_feeds/race_7588_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7588/polling_data.json | 2022 North Carolina Senate - Budd vs. Beasley | shown: 11/1 - 11/6, Budd 51.0, Beasley 44.8 |
| `rcp_feeds/race_7624_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7624/polling_data.json | 2022 Ohio Senate - Vance vs. Ryan | shown: 10/30 - 11/5, Vance 51.8, Ryan 43.8 |
| `rcp_feeds/race_7682_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7682/polling_data.json | 2022 Missouri Senate - Schmitt vs. Busch Valentine | shown: 10/24 - 11/1, Schmitt 52.0, Valentine 41.3 |
| `rcp_feeds/race_7686_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7686/polling_data.json | 2022 Connecticut Senate - Levy vs. Blumenthal | hidden (`show_rcp_avg: 0`, placeholder date 12/31 - 12/31) |
| `rcp_feeds/race_7695_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7695/polling_data.json | 2022 Pennsylvania Senate - Oz vs. Fetterman | shown: 10/28 - 11/3, Oz 47.2, Fetterman 46.8 |
| `rcp_feeds/race_7700_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7700/polling_data.json | 2022 Arkansas Senate - Boozman vs. James | none |
| `rcp_feeds/race_7735_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7735/polling_data.json | 2022 Utah Senate - Lee vs. McMullin | none |
| `rcp_feeds/race_7738_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7738/polling_data.json | 2022 Iowa Senate - Grassley vs. Franken | none |
| `rcp_feeds/race_7744_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7744/polling_data.json | 2022 Oregon Senate - Perkins vs. Wyden | none |
| `rcp_feeds/race_7754_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7754/polling_data.json | 2022 Alabama Senate - Britt vs. Boyd | none |
| `rcp_feeds/race_7758_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7758/polling_data.json | 2022 Wisconsin Senate - Johnson vs. Barnes | shown: 10/24 - 11/5, Johnson 50.2, Barnes 46.6 |
| `rcp_feeds/race_7771_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7771/polling_data.json | 2022 New York Senate - Schumer vs. Pinion | shown: 10/26 - 10/31, Schumer 54.7, Pinion 39.3 |
| `rcp_feeds/race_7772_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7772/polling_data.json | 2022 Illinois Senate - Salvi vs. Duckworth | none |
| `rcp_feeds/race_7773_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7773/polling_data.json | 2022 Colorado Senate - O'Dea vs. Bennet | shown: 10/26 - 11/5, Bennet 50.0, O'Dea 44.3 |
| `rcp_feeds/race_7905_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7905/polling_data.json | 2022 Vermont Senate - Malloy vs. Welch | none |
| `rcp_feeds/race_7911_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7911/polling_data.json | 2022 Oklahoma Senate Special Election - Mullin vs. Horn | none |
| `rcp_feeds/race_7912_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7912/polling_data.json | 2022 Oklahoma Senate - Lankford vs. Horn | none |
| `rcp_feeds/race_7915_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7915/polling_data.json | 2022 Alaska Senate - Murkowski vs. Tshibaka vs. Chesbro | none |
| `rcp_feeds/race_7916_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7916/polling_data.json | 2022 Alaska Senate - Murkowski vs. Tshibaka vs. Chesbro (2nd Round) | none |
| `rcp_feeds/race_7917_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7917/polling_data.json | 2022 Alaska Senate - Murkowski vs. Tshibaka (Final Round) | none |
| `rcp_feeds/race_7924_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7924/polling_data.json | 2022 Kansas Senate - Moran vs. Holland | none |
| `rcp_feeds/race_7926_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7926/polling_data.json | 2022 South Dakota Senate - Thune vs. Bengs | none |
| `rcp_feeds/race_7930_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7930/polling_data.json | 2022 Maryland Senate - Chaffee vs. Van Hollen | none |
| `rcp_feeds/race_7936_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7936/polling_data.json | 2022 Georgia Senate - Walker vs. Warnock vs. Oliver | shown: 10/15 - 10/27, Walker 47.3, Warnock 45.8, Oliver 3.8 |
| `rcp_feeds/race_7969_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/7969/polling_data.json | 2024 Generic Congressional Vote | shown: 10/14 - 11/2, Republicans 47.0, Democrats 46.7 |
| `rcp_feeds/race_8089_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8089/polling_data.json | 2024 Hawaii Senate - Hirono vs. Republican | none |
| `rcp_feeds/race_8096_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8096/polling_data.json | 2024 Mississippi Senate - Wicker vs. Democrat | none |
| `rcp_feeds/race_8115_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8115/polling_data.json | 2024 Wyoming Senate - Barrasso vs. Democrat | none |
| `rcp_feeds/race_8166_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8166/polling_data.json | 2024 Pennsylvania Senate - McCormick vs. Casey | shown: 10/21 - 11/4, Casey 48.1, McCormick 46.3 |
| `rcp_feeds/race_8180_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8180/polling_data.json | 2024 Texas Senate - Cruz vs. Allred | shown: 10/22 - 11/4, Cruz 49.2, Allred 44.8 |
| `rcp_feeds/race_8214_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8214/polling_data.json | 2024 Ohio Senate - Brown vs. Moreno | shown: 10/23 - 11/4, Moreno 48.0, Brown 46.3 |
| `rcp_feeds/race_8219_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8219/polling_data.json | 2024 Michigan Senate - Rogers vs. Slotkin | shown: 10/24 - 11/4, Slotkin 48.4, Rogers 46.1 |
| `rcp_feeds/race_8274_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8274/polling_data.json | 2024 Missouri Senate - Hawley vs. Kunce | none |
| `rcp_feeds/race_8278_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8278/polling_data.json | 2024 Indiana Senate - Banks vs. McCray | hidden (`show_rcp_avg: 0`, placeholder date 12/31 - 12/31) |
| `rcp_feeds/race_8282_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8282/polling_data.json | 2024 North Dakota Senate - Cramer vs. Christiansen | none |
| `rcp_feeds/race_8286_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8286/polling_data.json | 2024 Montana Senate - Sheehy vs. Tester | shown: 10/5 - 11/4, Sheehy 50.7, Tester 43.0 |
| `rcp_feeds/race_8287_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8287/polling_data.json | 2024 Tennessee Senate - Blackburn vs. Johnson | hidden (`show_rcp_avg: 0`, placeholder date 12/31 - 12/31) |
| `rcp_feeds/race_8339_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8339/polling_data.json | 2024 Washington Senate - Garcia vs. Cantwell | none |
| `rcp_feeds/race_8387_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8387/polling_data.json | 2024 Maryland Senate - Hogan vs. Alsobrooks | hidden (`show_rcp_avg: 0`, placeholder date 12/31 - 12/31) |
| `rcp_feeds/race_8397_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8397/polling_data.json | 2024 Nevada Senate - Brown vs. Rosen | shown: 10/24 - 11/4, Rosen 48.8, Brown 43.9 |
| `rcp_feeds/race_8412_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8412/polling_data.json | 2024 Wisconsin Senate - Hovde vs. Baldwin | shown: 10/16 - 11/4, Baldwin 48.9, Hovde 47.1 |
| `rcp_feeds/race_8413_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8413/polling_data.json | 2024 California Senate - Garvey vs. Schiff | hidden (`show_rcp_avg: 0`, placeholder date 12/31 - 12/31) |
| `rcp_feeds/race_8435_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8435/polling_data.json | 2024 Arizona Senate - Lake vs. Gallego | shown: 10/25 - 11/4, Gallego 48.6, Lake 46.0 |
| `rcp_feeds/race_8459_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8459/polling_data.json | 2024 Florida Senate - Scott vs. Mucarsel-Powell | shown: 9/29 - 11/1, Scott 48.9, Mucarsel-Powell 44.3 |
| `rcp_feeds/race_8460_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8460/polling_data.json | 2024 New Jersey Senate - Bashaw vs. Kim | none |
| `rcp_feeds/race_8464_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8464/polling_data.json | 2024 Nebraska Senate Special Election - Ricketts vs. Love | none |
| `rcp_feeds/race_8466_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8466/polling_data.json | 2024 New Mexico Senate - Domenici vs. Heinrich | hidden (`show_rcp_avg: 0`, placeholder date 12/31 - 12/31) |
| `rcp_feeds/race_8483_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8483/polling_data.json | 2024 Massachusetts Senate - Deaton vs. Warren | hidden (`show_rcp_avg: 0`, placeholder date 12/31 - 12/31) |
| `rcp_feeds/race_8498_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8498/polling_data.json | 2024 Virginia Senate - Cao vs. Kaine | shown: 10/19 - 11/4, Kaine 52.0, Cao 41.2 |
| `rcp_feeds/race_8499_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8499/polling_data.json | 2024 Minnesota Senate - White vs. Klobuchar | shown: 10/16 - 11/4, Klobuchar 52.0, White 39.0 |
| `rcp_feeds/race_8555_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8555/polling_data.json | 2024 New York Senate - Sapraicone vs. Gillibrand | hidden (`show_rcp_avg: 0`, placeholder date 12/31 - 12/31) |
| `rcp_feeds/race_8567_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8567/polling_data.json | 2024 Vermont Senate - Sanders vs. Malloy vs. Schoville vs. Hill | none |
| `rcp_feeds/race_8568_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8568/polling_data.json | 2024 Maine Senate - King vs. Kouzounas vs. Costello | none |
| `rcp_feeds/race_8581_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8581/polling_data.json | 2024 Utah Senate - Curtis vs. Gleich | none |
| `rcp_feeds/race_8590_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8590/polling_data.json | 2024 Nebraska Senate - Fischer vs. Osborn (I) | none |
| `rcp_feeds/race_8620_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8620/polling_data.json | 2024 West Virginia Senate - Justice vs. Elliott | none |
| `rcp_feeds/race_8627_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8627/polling_data.json | 2024 Rhode Island Senate - Morgan vs. Whitehouse | none |
| `rcp_feeds/race_8635_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8635/polling_data.json | 2024 Delaware Senate - Hansen vs. Blunt Rochester | none |
| `rcp_feeds/race_8638_polling_data_2026-10-26.json` | https://orig.realclearpolitics.com/poll/race/8638/polling_data.json | 2024 Connecticut Senate - Corey vs. Murphy | none |
