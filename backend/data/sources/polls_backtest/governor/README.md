# Final RealClearPolitics governor averages (2018, 2022) and 2018 generic ballot, for the backtest

These are RCP's last pre-election averages for the 2018 and 2022 governor races and for the 2018 generic congressional ballot. Each race comes with every poll RCP listed and a flag for the polls inside the average. They complement `../senate_20xx_rcp_final.csv` and `../generic_ballot_rcp_final.csv` (2022, 2024) and were built with the same method (see `../README.md`).

- **Retrieved:** 2026-10-28, for every file here. Pages and feeds were fetched 18:37–19:11 UTC, and each folder's `_fetch_log.tsv` gives the exact time per file. The CDX listings were queried 18:31–19:20 UTC.
- **Sources:**
  - RCP's own race pages as archived by the Wayback Machine. Raw copies were fetched with the `id_` suffix: `https://web.archive.org/web/<timestamp>id_/<url>`.
  - RCP's data feed, `https://orig.realclearpolitics.com/poll/race/<id>/polling_data.json`. The feed shows each race as it stands today.
  - The Wayback CDX index, used to list captures. Its listings are saved in `cdx_listings/`.
  - No news stories, Wikipedia pages or search snippets were used, and no number was estimated or typed in by hand.
- **Live pages:** the live RCP pages block bots, so none were fetched.
- **Code:** nothing in the downloaded files was run. Everything was parsed as plain text by `scripts/`, run with `python3 -I`.

## CSV files

| File | Rows |
|---|---|
| `governor_2018_rcp_final.csv` | 22 races: 22 `RCP Average` rows + 245 poll rows |
| `governor_2022_rcp_final.csv` | 17 races: 17 `RCP Average` rows + 338 poll rows |
| `generic_ballot_2018_rcp_final.csv` | 2018: 1 `RCP Average` row + 309 poll rows (RCP's full list for the cycle) |

The columns are the same as in `../senate_20xx_rcp_final.csv` and `../generic_ballot_rcp_final.csv`; the column table in `../README.md` applies. The differences:

| Column | Meaning |
|---|---|
| `third_candidate`, `third` | **Governor files only, the last two columns.** A third candidate in RCP's table, with RCP's share, such as `Lord (L)` in Nevada 2018 or `Johnson (I)` in Oregon 2022. Blank when RCP's table has only two candidates. |
| `dem`, `rep` | The Democrat and the Republican. In every race kept here the Republican's main opponent is a Democrat (see caveat 11 on Alaska). |
| `excluded_pollster` | `yes` for Rasmussen Reports or ActiVote, as before. ActiVote and Wedgewood appear in no list here. |
| `data_source` | `wayback_page`, or `rcp_feed_current_2026-10-28` for the 5 races taken from the feed (caveat 1). |
| `notes` | Every caveat that applies to a race is repeated on its rows. |

**Check:** in all 40 averages (22 + 17 governor races, plus the generic ballot), the simple mean of the `in_average == yes` polls rounds to RCP's published figures. That holds for D, R and the third candidate, if any. RCP's spread is the difference of its rounded figures (PA 2018: 56.3 − 36.7 = Wolf +19.6, while the unrounded lead is 19.67), and every spread matches on that basis. No race fails. See `check_means_log.txt`.

## Final averages

**Which capture was used.** As in the Senate work, each page's capture is the last good Wayback capture before 08:00 UTC the day after the election (2018-11-07 08:00 UTC; 2022-11-09 08:00 UTC). "Good" means it was served with HTTP 200 and has RCP's poll table. Wayback "revisit" records count as captures; they hold the same bytes as an earlier capture, re-confirmed by the crawler at the revisit time (17 of the captures used). Each average was compared with RCP's current feed (`verify_log.txt`).

**One extension of the method, used for 5 races.** Many 2018 governor pages were last crawled on Sunday, Nov 4, 2018, around 22:20 UTC, and a few 2022 pages on Nov 7, 2022. RCP's feed stores an `updated` stamp for every poll entry. In some races the feed shows a later average than the capture, and an entry is stamped after the capture but before the cutoff. That is direct evidence RCP updated the race before the election. For those races, the CSV takes the race from the feed (data_source `rcp_feed_current_2026-10-28`, blank `archive_url`). This is the treatment the Senate work gave VA 2024. The archived copy is kept, and the `notes` give its earlier average and the stamps. Where the feed differs but no entry is stamped in that interval (TX 2018), the archived page is kept, as in the Senate method.

#### 2018 governor (22 averages)

| State | Race | Window | D | R | Third | RCP spread | Polls in avg (of which Rasmussen) | Polls listed | Source |
|---|---|---|---|---|---|---|---|---|---|
| AZ | Ducey vs. Garcia (6614) | 10/24–11/4 | 38.5 | 54.8 | | Ducey +16.3 | 4 (0) | 18 | **RCP feed** (see caveats) |
| CA | Cox vs. Newsom (6593) | 10/19–11/5 | 55.3 | 38.8 | | Newsom +16.5 | 4 (0) | 18 | **RCP feed** (see caveats) |
| CO | Stapleton vs. Polis (6409) | 10/25–10/30 | 47.5 | 41.0 | | Polis +6.5 | 2 (0) | 4 | Wayback 2018-11-04 22:18 |
| CT | Stefanowski vs. Lamont (6577) | 10/22–11/1 | 44.3 | 39.8 | | Lamont +4.5 | 4 (0) | 9 | Wayback 2018-11-04 22:16 |
| FL | DeSantis vs. Gillum (6518) | 10/29–11/5 | 49.4 | 45.8 | | Gillum +3.6 | 5 (0) | 37 | Wayback 2018-11-06 17:20 |
| GA | Kemp vs. Abrams (6628) | 10/14–11/3 | 45.8 | 48.8 | | Kemp +3.0 | 5 (0) | 13 | Wayback 2018-11-06 22:20 |
| IA | Reynolds vs. Hubbell (6477) | 10/8–11/2 | 45.0 | 44.3 | | Hubbell +0.7 | 3 (0) | 5 | Wayback 2018-11-04 22:16 |
| IL | Rauner vs. Pritzker (6439) | 6/9–9/29 | 43.7 | 28.0 | | Pritzker +15.7 | 3 (0) | 4 | Wayback 2018-11-05 14:54 |
| MA | Baker vs. Gonzalez (6418) | 10/1–10/28 | 26.3 | 66.0 | | Baker +39.7 | 4 (0) | 11 | Wayback 2018-11-04 22:19 |
| MD | Hogan vs. Jealous (6273) | 9/11–10/7 | 35.8 | 54.5 | | Hogan +18.7 | 4 (0) | 11 | Wayback 2018-10-27 18:43 |
| MI | Schuette vs. Whitmer (6441) | 10/24–11/5 | 50.0 | 40.0 | | Whitmer +10.0 | 3 (0) | 20 | Wayback 2018-11-06 23:37 |
| MN | Johnson vs. Walz (6443) | 10/15–10/31 | 47.0 | 40.0 | | Walz +7.0 | 2 (0) | 7 | Wayback 2018-11-04 22:22 |
| NH | Sununu vs. Kelly (6561) | 10/27–11/4 | 46.0 | 50.0 | | Sununu +4.0 | 2 (0) | 7 | **RCP feed** (see caveats) |
| NM | Pearce vs. Grisham (6440) | 10/24–11/1 | 52.3 | 44.3 | | Grisham +8.0 | 3 (0) | 6 | Wayback 2018-11-04 22:24 |
| NV | Laxalt vs. Sisolak vs. Lord (6692) | 9/30–10/29 | 43.0 | 44.5 | Lord 5.0 | Laxalt +1.5 | 2 (0) | 4 | Wayback 2018-11-04 22:17 |
| NY | Molinaro vs. Cuomo (6536) | 10/10–11/1 | 53.5 | 35.5 | | Cuomo +18.0 | 2 (0) | 8 | Wayback 2018-11-04 22:55 |
| OK | Stitt vs. Edmondson (6633) | 9/25–11/3 | 42.7 | 48.0 | | Stitt +5.3 | 3 (0) | 7 | Wayback 2018-11-06 11:51 |
| OR | Buehler vs. Brown (6428) | 10/4–10/30 | 44.0 | 39.7 | | Brown +4.3 | 3 (0) | 9 | Wayback 2018-11-04 22:17 |
| PA | Wagner vs. Wolf (6542) | 9/12–11/1 | 56.3 | 36.7 | | Wolf +19.6 | 3 (1) | 11 | Wayback 2018-11-06 19:51 |
| RI | Fung vs. Raimondo (6544) | 9/27–10/24 | 46.5 | 34.0 | | Raimondo +12.5 | 2 (0) | 5 | Wayback 2018-11-04 22:23 |
| TN | Lee vs. Dean (6644) | 10/22–10/30 | 39.2 | 53.0 | | Lee +13.8 | 5 (0) | 12 | Wayback 2018-11-04 22:20 |
| TX | Abbott vs. Valdez (6435) | 10/8–10/30 | 37.8 | 55.7 | | Abbott +17.9 | 6 (0) | 19 | Wayback 2018-11-04 22:18 |

#### 2022 governor (17 averages)

| State | Race | Window | D | R | Third | RCP spread | Polls in avg (of which Rasmussen) | Polls listed | Source |
|---|---|---|---|---|---|---|---|---|---|
| AZ | Lake vs. Hobbs (7842) | 11/1–11/7 | 47.3 | 50.8 | | Lake +3.5 | 4 (0) | 29 | Wayback 2022-11-09 06:55 |
| CO | Ganahl vs. Polis (7774) | 10/26–11/5 | 53.0 | 42.3 | | Polis +10.7 | 3 (0) | 9 | Wayback 2022-11-09 02:37 |
| CT | Stefanowski vs. Lamont (7684) | 10/10–10/23 | 52.7 | 41.7 | | Lamont +11.0 | 3 (0) | 8 | Wayback 2022-11-06 07:37 |
| FL | DeSantis vs. Crist (7324) | 10/17–11/6 | 42.2 | 54.4 | | DeSantis +12.2 | 5 (0) | 21 | Wayback 2022-11-09 06:09 |
| GA | Kemp vs. Abrams (7538) | 11/1–11/7 | 44.5 | 52.8 | | Kemp +8.3 | 6 (0) | 46 | Wayback 2022-11-09 02:08 |
| MA | Diehl vs. Healey (7609) | 10/13–10/26 | 58.5 | 33.0 | | Healey +25.5 | 2 (0) | 8 | Wayback 2022-11-07 11:43 |
| MD | Cox vs. Moore (7841) | 9/8–10/23 | 57.0 | 28.7 | | Moore +28.3 | 3 (0) | 3 | Wayback 2022-11-08 00:54 |
| MI | Dixon vs. Whitmer (7545) | 10/30–11/7 | 48.3 | 47.3 | | Whitmer +1.0 | 4 (0) | 25 | Wayback 2022-11-09 02:08 |
| MN | Jensen vs. Walz (7405) | 10/10–10/30 | 48.0 | 43.7 | | Walz +4.3 | 3 (0) | 11 | Wayback 2022-11-08 19:22 |
| NH | Sununu vs. Sherman (7498) | 10/28–11/6 | 39.4 | 56.4 | | Sununu +17.0 | 5 (0) | 17 | **RCP feed** (see caveats) |
| NV | Lombardo vs. Sisolak (7394) | 10/24–11/7 | 45.0 | 47.8 | | Lombardo +2.8 | 5 (0) | 27 | Wayback 2022-11-09 02:38 |
| NY | Zeldin vs. Hochul (7749) | 10/26–10/31 | 52.0 | 45.0 | | Hochul +7.0 | 3 (0) | 17 | Wayback 2022-11-09 02:08 |
| OH | DeWine vs. Whaley (7697) | 10/30–11/5 | 35.6 | 58.0 | | DeWine +22.4 | 5 (0) | 19 | Wayback 2022-11-09 02:37 |
| OR | Drazan vs. Kotek vs. Johnson (7908) | 10/17–11/6 | 42.3 | 41.0 | Johnson 11.5 | Kotek +1.3 | 4 (0) | 10 | Wayback 2022-11-08 00:08 |
| PA | Mastriano vs. Shapiro (7696) | 11/1–11/3 | 51.0 | 42.7 | | Shapiro +8.3 | 3 (0) | 33 | Wayback 2022-11-09 05:39 |
| TX | Abbott vs. O'Rourke (7376) | 10/16–10/26 | 42.3 | 52.7 | | Abbott +10.4 | 3 (0) | 33 | Wayback 2022-11-09 07:53 |
| WI | Michels vs. Evers (7761) | 10/24–11/5 | 47.8 | 48.4 | | Michels +0.6 | 5 (0) | 22 | **RCP feed** (see caveats) |

#### 2018 generic ballot (1 average)

| State | Race | Window | D | R | RCP spread | Polls in avg (of which Rasmussen) | Polls listed | Source |
|---|---|---|---|---|---|---|---|---|
| US | Generic Congressional Vote (6185) | 10/13–11/3 | 49.7 | 42.4 | Democrats +7.3 | 11 (1) | 309 | Wayback 2018-11-07 00:05 |

Rasmussen Reports appears in the governor lists for FL and PA 2018 and GA and PA 2022. Only PA 2018 has one in the average: Rasmussen 9/12–9/13, Wolf 52 / Wagner 40. The 2018 generic-ballot list has 29 Rasmussen polls; one is in the average, Rasmussen 10/28–11/1, D 45 / R 46.

## Races without an RCP average

Each of the 36 states held a governor race in both years. The states below are left out of the CSVs. Raw copies and feeds are kept.

**2018 (14 states):**
- **The last capture before the cutoff shows no `RCP Average` row:**
  - AK (Dunleavy vs. Begich, Nov 6)
  - AR (Nov 4)
  - KS (the map's 3-way Kobach vs. Kelly vs. Orman, Nov 6; the 2-way page 6630, Nov 3, has none either)
  - ME (Nov 4)
  - SC (Nov 4)
  - VT (Nov 4)
  - SD (Nov 5; caveat 3)
  - **OH** (Nov 6; RCP removed its average on election day, caveat 4)
- **No capture before the cutoff, and the current feed shows no average:**
  - AL, HI, ID, NE, WY (the feeds list 0–2 polls)
  - **WI** (caveat 6)

**2022 (19 states):**
- **The last capture before the cutoff shows no `RCP Average` row:**
  - AK (RCP's page was an empty placeholder, Oct 27)
  - AL (Nov 1)
  - AR (Nov 8)
  - IA (Nov 9, 05:07 UTC)
  - IL (Nov 8)
  - KS (Nov 4)
  - ME (Nov 3; the www1 mirror's Nov 3, 12:11 copy also has none, `other_captures/`)
  - OK (Nov 9, 05:53 UTC)
  - RI (Oct 11)
  - VT (Sep 11)
  - **NM** (Nov 8; RCP removed its average on election day, caveat 5)
- **No capture before the cutoff, and the current feed shows no average:**
  - SC (7505)
  - SD (7927)
  - TN (7925)
  - AK's three ranked-choice pages (7918, 7919, 7920)
- **No RCP race page found at all**, on either RCP site in the Wayback index: HI, ID, NE, WY.
- **Average left out because the final one cannot be retrieved:** **CA** (caveat 8).

## How the race pages were found

- **2018.** RCP's governor map, `rcp_index/gov2018_map_wayback_20181104222031.html` (captured 2018-11-04 22:20), links one page in each of the 36 states. Those 36 pages are the races used. The CDX index was then searched for every page under `epolls/2018/governor/<state>/` from Sep 1 to Nov 8, 2018, with an all-time search for states that had nothing in that window. That turned up these alternative general-election matchups of the actual nominees:
  - GA 3-way, 6696
  - KS 2-way, 6630
  - NV 2-way, 6422
  - WI 2-way, 6606
  - CT 4-way, 6667
  - AK 3-way with Walker, 6669

  They were checked and kept, but left out of the CSV, as the Senate work did with Georgia's 3-way page. Primary pages and pre-primary hypothetical matchups were not used: FL DeSantis vs. Graham 6521, GA Cagle vs. Abrams 6411, IA Reynolds vs. Boulton 6415, NH Sununu vs. Marchand 6423, AK Dunleavy vs. Walker 6406.
- **2022.** RCP's governor map, `rcp_index/gov2022_map_wayback_20221108161622.html` (captured 2022-11-08 16:16), links 25 race pages, covering the competitive races, plus a link to `Alaska.html`, whose only capture is from May 2022. The same CDX search, Sep 1 to Nov 10, 2022, plus all-time searches, found the only general-election page for AK (7484), AL, AR, CA, NH, SC and TN, and AK's ranked-choice pages 7918–7920. A CDX search of RCP's newer site (`realclearpolling.com/polls/governor/general/2022/`) found no page for HI, ID, NE, SD, TN or WY. The pre-primary matchup FL DeSantis vs. Fried 7325 was not used.
- `scripts/races.json` lists every page checked, with its role. `build_log.tsv` gives each one's outcome, and each `_captures.tsv` maps a race tag to the capture used (`NONE` = no usable capture before the cutoff).

## Caveats and gaps

1. **5 races taken from RCP's feed because the archived copy predates RCP's last pre-election update.** In each case the newer entries are stamped before the cutoff, and the feed's average reproduces from its flagged polls.

   | Race | Last archived copy (UTC) and its average | Final average (feed) | Entries edited after the capture, before the cutoff |
   |---|---|---|---|
   | AZ 2018 | Nov 5, 20:02: 10/24–11/3, Ducey +15.0 (54.5/39.5) | 10/24–11/4, Ducey +16.3 (54.8/38.5) | Gravis 10/24–11/2 (in avg), Nov 5 22:09; HarrisX 10/28–11/3 (dropped), Nov 6 21:30 |
   | CA 2018 | Nov 4, 22:21: 10/10–10/26, Newsom +16.9 (53.3/36.4) | 10/19–11/5, Newsom +16.5 (55.3/38.8) | KABC/SurveyUSA 11/1–11/5 and KFI-NBC 4 10/25–10/27 (both in avg), Nov 6 06:21–06:26 |
   | NH 2018 | Nov 4, 22:19: 10/10–10/29, Sununu +9.5 (50.5/41.0) | 10/27–11/4, Sununu +4.0 (50.0/46.0) | UNH* 11/1–11/4 (in avg), Nov 5 04:46 |
   | NH 2022 | Nov 7, 14:25: 10/28–11/6, Sununu +16.7 (56.0/39.3) | 10/28–11/6, Sununu +17.0 (56.4/39.4) | Data for Progress (D)** 11/2–11/5 (in avg), Nov 7 22:44 |
   | WI 2022 | Nov 7, 18:09: 10/24–11/4, Michels +0.4 (48.0/47.6) | 10/24–11/5, Michels +0.6 (48.4/47.8) | Data for Progress (D)** 11/2–11/5 (in avg), Nov 7 22:52 |

   - **AZ 2018:** the HarrisX 10/29–11/4 entry now in the average carries a later stamp (Nov 15, 2021), so its own entry time is unknown.
   - **Re-saved stamps:** RCP re-saved many entries later. For example, all Emerson entries carry Dec 3, 2021. So a stamp was used only as evidence of an edit inside the capture-to-cutoff interval, never to date anything else.
   - **Hidden feed entries:** for feed-based races, entries the feed marks `data_show` ≠ 1 were left out. RCP does not display them: in the feeds of the races with an archived copy, none of the 52 entries with `data_show` 0 or 2 appears on the archived page, while 998 of the 1,015 `data_show = 1` entries do. They include `*PLACEHOLDER*` rows. Each race's `RCP Average` row lists what was left out.
2. **TX 2018, archived page kept although the feed differs.** The Nov 4, 22:18 copy shows 10/8–10/30, Abbott 55.7 / Valdez 37.8, from 6 polls. Today's feed shows 10/15–10/30, 55.0/38.3, from 4 polls: CNN 10/9–10/13 and NYT/Siena 10/8–10/11 were dropped. No entry is stamped between the capture and the cutoff, so it is unknown whether RCP made that change before the election.
3. **SD 2018.** The Nov 5, 22:17 copy lists 3 polls and no average. Today's feed shows an average, 10/29–11/4, Noem 47.5 / Sutton 45.5, from 2 polls (Emerson 11/1–11/4 and KELO/Mason-Dixon 10/29–10/31). Nothing dates when RCP switched it on, so SD is listed as having no average.
4. **OH 2018: average removed on election day.** The Nov 5, 01:22 copy shows Cordray +4.7 (D 47.7 / R 43.0; Gravis, Emerson and Suffolk, 10/4–10/30). It is saved as `other_captures/oh2018_6426_wayback_20181105012231.html`. The last copy before the cutoff (Nov 6, 19:51; page last modified Nov 6, 13:54 UTC) has no `RCP Average` row. Today's feed hides the average and holds Cordray 48.5 / DeWine 44.5, the mean of Gravis and Emerson alone, with no date and no polls flagged. Following the method, as for the 2024 Senate pages that hid their averages, OH is not in the CSV.
5. **NM 2022: average removed on election day.** The Nov 6, 16:35 copy shows Lujan Grisham +4.0 (48.0 / 44.0, 4 polls, 10/19–10/28). It is saved as `other_captures/nm2022_7646_wayback_20221106163554.html`. The last copy before the cutoff (Nov 8, 13:25; page modified 12:30 UTC) has no `RCP Average` row in its poll table. Its editorial "Snapshot" box still reads "RCP Average: Lujan Grisham +4.0". Today's feed hides the same 48.0/44.0. NM is not in the CSV.
6. **WI 2018: no average can be retrieved.**
   - The 2018 map linked the 3-way Walker vs. Evers vs. Anderson page (6682). The Wayback index has no copy of it before Nov 24, 2018. That copy (`other_captures/wi2018_6682_wayback_20181124135640.html`) shows only a Final Results row (Evers +1.2) and no average.
   - Today's feed for 6682 hides an average of Evers 47.3 / Walker 44.3 / Anderson 3.3, with no date and no polls flagged, so it cannot be reproduced.
   - The 2-way page 6606 (Nov 6, 19:51) lists 11 polls and no average. Its feed hides Evers 49.0 / Walker 46.5.
7. **NV 2018, two averages.** The CSV uses the page the map linked, the 3-way Laxalt vs. Sisolak vs. Lord (6692). Its Nov 4 copy shows Laxalt +1.5 (44.5 / 43.0 / Lord 5.0) from 2 polls, 9/30–10/29. Today's feed hides that average but keeps the same values. The 2-way page 6422 was averaged too, and kept more current:
   - its Nov 4 copy shows Laxalt +1.0 (45.6 / 44.6, 5 polls, 10/8–11/1);
   - today's feed shows Laxalt +0.6 (46.3 / 45.7, 3 polls, 10/29–11/4), with entries edited after that copy.

   It is left out of the CSV, as the Senate work did with Georgia's 3-way page, but its raw copy and feed are kept.
8. **CA 2022 left out.** The only copy before the cutoff is from Oct 20, before the election-eve window. It shows 9/2–10/10, Newsom 56.0 / Dahle 32.7. Today's feed hides the average and holds different values, Newsom 58.0 / Dahle 34.0, with no polls flagged. The Senate work kept CT 2022 from a similar early copy, but there the feed confirmed the values; here it shows the average changed, and the final one cannot be retrieved. The raw copy is kept.
9. **Copies from before the election-eve window** (before Nov 4, 2018 or Nov 6, 2022) that are used in the CSV:
   - **MD 2018** (Oct 27; page last modified Oct 12): today's feed shows the same average, 9/11–10/7, Hogan +18.7, from the same 4 polls, so it is confirmed.
   - **CT 2022** (Nov 6, 07:37 UTC, just inside the window): the average is 10/10–10/23, Lamont +11.0; the page was last modified Oct 27.

   Both carry notes.
10. **The current feed hides an average but keeps the same values** (CO, IL, MN, NV, RI 2018; CT, MA, MD 2022), so it cannot confirm which polls were averaged. The rows note this.
    - **OR 2022:** the feed's hidden values (Kotek 40.8 / Drazan 40.8 / Johnson 12.8) differ from the page's (42.3 / 41.0 / 11.5). They equal the mean of the four polls averaged before Data for Progress 11/1–11/6 was entered (stamped Nov 7, 21:41 UTC). The Nov 8, 00:08 copy is later and includes that poll, so it is used.
    - **ME 2022:** the feed hides 49.0 / 40.8, but neither Nov 3 copy shows an average.
11. **Alaska and independents.**
    - In 2018 independent Bill Walker withdrew on Oct 19. The map's AK page is Dunleavy (R) vs. Begich (D) (6711), which listed 5 polls and no average. The 3-way page with Walker (6669) has no copy before the cutoff, and its feed has no average.
    - In 2022, RCP's AK page (7484) was an empty "Dunleavy (R) vs. Democrat (D)" placeholder. The ranked-choice pages 7918–7920 have no pre-election copy, and their feeds show no average.
    - So every race in the CSVs is a Democrat vs. a Republican. Third candidates appear only in NV 2018 (Lord, L) and OR 2022 (Johnson, I).
12. **Quirks of the current feed** (the CSV follows the archived page): the averages are identical, but the 2018 generic-ballot feed flags two extra Rasmussen polls as averaged, 4/23–4/25/2018 and 10/12–10/16/2017. The OH 2022 feed flags an extra Cygnal (R) 10/18–10/22 entry that the page never showed.
13. **One redirect.** OK 2018's capture of Nov 6, 14:50 UTC is served as a redirect, so the previous one (Nov 6, 11:51, a revisit) was used.
14. **The www1 mirror** (`www1.realclearpolitics.com`) had a later capture than `www` for one page only, ME 2022. It also shows no average.

## Rebuilding the CSVs

```
cd backend/data/sources/polls_backtest/governor
python3 -I scripts/build_gov.py "$PWD" scripts/races.json > build_log.tsv          # writes the three CSVs
python3 -I -u scripts/check_means.py governor_2018_rcp_final.csv governor_2022_rcp_final.csv \
    generic_ballot_2018_rcp_final.csv > check_means_log.txt 2>&1                   # simple-mean check
python3 -I scripts/verify_gov.py "$PWD" scripts/races.json > verify_log.txt        # archive vs. current feed
python3 -I scripts/readme_tables.py "$PWD"                                         # the tables in this README
```

**Scripts** (copied from the working folder and run from here, which gave identical outputs):
- `parse_epolls.py`: a copy of `../scripts/parse22.py`.
- `build_gov.py`: adapted from `../scripts/build.py`. It adds the third-candidate columns, the 2018 windows, the feed-evidence rule in caveat 1, the notes for hidden feed averages, and the skipping of undisplayed feed entries.
- `verify_gov.py`: adapted from `../scripts/verify.py`.
- `check_means.py`: the simple-mean check.
- Retrieval: `cdx_state.sh` (CDX listings), `select_captures.py` and `fetch_pages.py` (pick and fetch the last good capture), `wb_fetch.sh` (one raw `id_` fetch, logs the archive headers) and `fetch_feeds.sh`.

## Files

All retrieved **2026-10-28**.

- `rcp_2018_governor/`, `rcp_2022_governor/`, `rcp_generic_ballot/`: the captures used, with `_captures.tsv` and `_fetch_log.tsv`. The fetch log gives the memento time and the archived response's original `Last-Modified` and `Date` headers.
- `other_captures/`: other copies cited above (OH 2018 Nov 5, NM 2022 Nov 6, WI 2018 3-way Nov 24, ME 2022 www1 Nov 3).
- `rcp_index/`: the two governor maps.
- `rcp_feeds/`: RCP's feeds, with `_fetch_log.tsv`.
- `cdx_listings/`: the CDX listings, one per state and year. `*_window.txt` covers Sep 1 to Nov 8/10 and lists timestamp, URL, status and length; `*_alltime.txt` is the all-time search.
- `build_log.tsv`, `verify_log.txt`, `check_means_log.txt`: the outputs of the scripts above.

### Archived pages
| File | Live URL | Archive URL | Capture (UTC) | Page last modified (orig. header) | What the page shows |
|---|---|---|---|---|---|
| `rcp_2018_governor/ak_6711_wayback_20181106164955.html` | https://www.realclearpolitics.com/epolls/2018/governor/ak/alaska_governor_dunleavy_vs_begich-6711.html | https://web.archive.org/web/20181106164955/https://www.realclearpolitics.com/epolls/2018/governor/ak/alaska_governor_dunleavy_vs_begich-6711.html | 2018-11-06 16:49 | Fri, 02 Nov 2018 02:10:55 GMT | No RCP Average row; 5 polls listed |
| `rcp_2018_governor/ar_6408_wayback_20181104222156.html` | https://www.realclearpolitics.com/epolls/2018/governor/ar/arkansas_governor_hutchinson_vs_henderson-6408.html | https://web.archive.org/web/20181104222156/https://www.realclearpolitics.com/epolls/2018/governor/ar/arkansas_governor_hutchinson_vs_henderson-6408.html | 2018-11-04 22:21 | Sun, 04 Nov 2018 17:06:47 GMT | No RCP Average row; 4 polls listed |
| `rcp_2018_governor/az_6614_wayback_20181105200240.html` | https://www.realclearpolitics.com/epolls/2018/governor/az/arizona_governor_ducey_vs_garcia-6614.html | https://web.archive.org/web/20181105200240/https://www.realclearpolitics.com/epolls/2018/governor/az/arizona_governor_ducey_vs_garcia-6614.html | 2018-11-05 20:02 | Mon, 05 Nov 2018 19:34:46 GMT | RCP Average 10/24 - 11/3: Ducey 54.5 / Garcia 39.5 (Ducey +15.0); 4 of 16 listed polls in average |
| `rcp_2018_governor/ca_6593_wayback_20181104222116.html` | https://www.realclearpolitics.com/epolls/2018/governor/ca/california_governor_cox_vs_newsom-6593.html | https://web.archive.org/web/20181104222116/https://www.realclearpolitics.com/epolls/2018/governor/ca/california_governor_cox_vs_newsom-6593.html | 2018-11-04 22:21 | Sat, 03 Nov 2018 15:47:11 GMT | RCP Average 10/10 - 10/26: Newsom 53.3 / Cox 36.4 (Newsom +16.9); 7 of 16 listed polls in average |
| `rcp_2018_governor/co_6409_wayback_20181104221801.html` | https://www.realclearpolitics.com/epolls/2018/governor/co/colorado_governor_stapleton_vs_polis-6409.html | https://web.archive.org/web/20181104221801/https://www.realclearpolitics.com/epolls/2018/governor/co/colorado_governor_stapleton_vs_polis-6409.html | 2018-11-04 22:18 | Thu, 01 Nov 2018 15:15:58 GMT | RCP Average 10/25 - 10/30: Polis 47.5 / Stapleton 41.0 (Polis +6.5); 2 of 4 listed polls in average |
| `rcp_2018_governor/ct_6577_wayback_20181104221649.html` | https://www.realclearpolitics.com/epolls/2018/governor/ct/connecticut_governor_stefanowski_vs_lamont-6577.html | https://web.archive.org/web/20181104221649/https://www.realclearpolitics.com/epolls/2018/governor/ct/connecticut_governor_stefanowski_vs_lamont-6577.html | 2018-11-04 22:16 | Fri, 02 Nov 2018 11:45:57 GMT | RCP Average 10/22 - 11/1: Lamont 44.3 / Stefanowski 39.8 (Lamont +4.5); 4 of 9 listed polls in average |
| `rcp_2018_governor/fl_6518_wayback_20181106172052.html` | https://www.realclearpolitics.com/epolls/2018/governor/fl/florida_governor_desantis_vs_gillum-6518.html | https://web.archive.org/web/20181106172052/https://www.realclearpolitics.com/epolls/2018/governor/fl/florida_governor_desantis_vs_gillum-6518.html | 2018-11-06 17:20 | Tue, 06 Nov 2018 16:28:32 GMT | RCP Average 10/29 - 11/5: Gillum 49.4 / DeSantis 45.8 (Gillum +3.6); 5 of 37 listed polls in average |
| `rcp_2018_governor/ga_6628_wayback_20181106222013.html` | https://www.realclearpolitics.com/epolls/2018/governor/ga/georgia_governor_kemp_vs_abrams-6628.html | https://web.archive.org/web/20181106222013/https://www.realclearpolitics.com/epolls/2018/governor/ga/georgia_governor_kemp_vs_abrams-6628.html | 2018-11-06 22:20 | Tue, 06 Nov 2018 21:26:19 GMT | RCP Average 10/14 - 11/3: Kemp 48.8 / Abrams 45.8 (Kemp +3.0); 5 of 13 listed polls in average |
| `rcp_2018_governor/ga_6696_wayback_20181104143459.html` | https://www.realclearpolitics.com/epolls/2018/governor/ga/georgia_governor_kemp_vs_abrams_vs_metz-6696.html | https://web.archive.org/web/20181104143459/https://www.realclearpolitics.com/epolls/2018/governor/ga/georgia_governor_kemp_vs_abrams_vs_metz-6696.html | 2018-11-04 14:34 | Fri, 02 Nov 2018 01:59:46 GMT | No RCP Average row; 7 polls listed |
| `rcp_2018_governor/ia_6477_wayback_20181104221622.html` | https://www.realclearpolitics.com/epolls/2018/governor/ia/iowa_governor_reynolds_vs_hubbell-6477.html | https://web.archive.org/web/20181104221622/https://www.realclearpolitics.com/epolls/2018/governor/ia/iowa_governor_reynolds_vs_hubbell-6477.html | 2018-11-04 22:16 | Sat, 03 Nov 2018 23:31:13 GMT | RCP Average 10/8 - 11/2: Hubbell 45.0 / Reynolds 44.3 (Hubbell +0.7); 3 of 5 listed polls in average |
| `rcp_2018_governor/il_6439_wayback_20181105145413.html` | https://www.realclearpolitics.com/epolls/2018/governor/il/illinois_governor_rauner_vs_pritzker-6439.html | https://web.archive.org/web/20181105145413/https://www.realclearpolitics.com/epolls/2018/governor/il/illinois_governor_rauner_vs_pritzker-6439.html | 2018-11-05 14:54 | Fri, 12 Oct 2018 22:57:43 GMT | RCP Average 6/9 - 9/29: Pritzker 43.7 / Rauner 28.0 (Pritzker +15.7); 3 of 4 listed polls in average |
| `rcp_2018_governor/ks_6630_wayback_20181103135534.html` | https://www.realclearpolitics.com/epolls/2018/governor/ks/kansas_governor_kobach_vs_kelly-6630.html | https://web.archive.org/web/20181103135534/https://www.realclearpolitics.com/epolls/2018/governor/ks/kansas_governor_kobach_vs_kelly-6630.html | 2018-11-03 13:55 | Tue, 30 Oct 2018 12:54:15 GMT | No RCP Average row; 4 polls listed |
| `rcp_2018_governor/ks_6660_wayback_20181106181330.html` | https://www.realclearpolitics.com/epolls/2018/governor/ks/kansas_governor_kobach_vs_kelly_vs_orman-6660.html | https://web.archive.org/web/20181106181330/https://www.realclearpolitics.com/epolls/2018/governor/ks/kansas_governor_kobach_vs_kelly_vs_orman-6660.html | 2018-11-06 18:13 | Tue, 30 Oct 2018 12:22:51 GMT | No RCP Average row; 5 polls listed |
| `rcp_2018_governor/ma_6418_wayback_20181104221911.html` | https://www.realclearpolitics.com/epolls/2018/governor/ma/massachusetts_governor_baker_vs_gonzalez-6418.html | https://web.archive.org/web/20181104221911/https://www.realclearpolitics.com/epolls/2018/governor/ma/massachusetts_governor_baker_vs_gonzalez-6418.html | 2018-11-04 22:19 | Thu, 01 Nov 2018 15:56:20 GMT | RCP Average 10/1 - 10/28: Baker 66.0 / Gonzalez 26.3 (Baker +39.7); 4 of 11 listed polls in average |
| `rcp_2018_governor/md_6273_wayback_20181027184317.html` | https://www.realclearpolitics.com/epolls/2018/governor/md/maryland_governor_hogan_vs_jealous-6273.html | https://web.archive.org/web/20181027184317/https://www.realclearpolitics.com/epolls/2018/governor/md/maryland_governor_hogan_vs_jealous-6273.html | 2018-10-27 18:43 | Fri, 12 Oct 2018 22:58:08 GMT | RCP Average 9/11 - 10/7: Hogan 54.5 / Jealous 35.8 (Hogan +18.7); 4 of 11 listed polls in average |
| `rcp_2018_governor/me_6643_wayback_20181104222306.html` | https://www.realclearpolitics.com/epolls/2018/governor/me/maine_governor_moody_vs_mills-6643.html | https://web.archive.org/web/20181104222306/https://www.realclearpolitics.com/epolls/2018/governor/me/maine_governor_moody_vs_mills-6643.html | 2018-11-04 22:23 | Wed, 31 Oct 2018 14:28:42 GMT | No RCP Average row; 3 polls listed |
| `rcp_2018_governor/mi_6441_wayback_20181106233751.html` | https://www.realclearpolitics.com/epolls/2018/governor/mi/michigan_governor_schuette_vs_whitmer-6441.html | https://web.archive.org/web/20181106233751/https://www.realclearpolitics.com/epolls/2018/governor/mi/michigan_governor_schuette_vs_whitmer-6441.html | 2018-11-06 23:37 | Tue, 06 Nov 2018 14:09:12 GMT | RCP Average 10/24 - 11/5: Whitmer 50.0 / Schuette 40.0 (Whitmer +10.0); 3 of 20 listed polls in average |
| `rcp_2018_governor/mn_6443_wayback_20181104222227.html` | https://www.realclearpolitics.com/epolls/2018/governor/mn/minnesota_governor_johnson_vs_walz-6443.html | https://web.archive.org/web/20181104222227/https://www.realclearpolitics.com/epolls/2018/governor/mn/minnesota_governor_johnson_vs_walz-6443.html | 2018-11-04 22:22 | Fri, 02 Nov 2018 14:20:46 GMT | RCP Average 10/15 - 10/31: Walz 47.0 / Johnson 40.0 (Walz +7.0); 2 of 7 listed polls in average |
| `rcp_2018_governor/nh_6561_wayback_20181104221900.html` | https://www.realclearpolitics.com/epolls/2018/governor/nh/new_hampshire_governor_sununu_vs_kelly-6561.html | https://web.archive.org/web/20181104221900/https://www.realclearpolitics.com/epolls/2018/governor/nh/new_hampshire_governor_sununu_vs_kelly-6561.html | 2018-11-04 22:19 | Wed, 31 Oct 2018 14:36:28 GMT | RCP Average 10/10 - 10/29: Sununu 50.5 / Kelly 41.0 (Sununu +9.5); 2 of 6 listed polls in average |
| `rcp_2018_governor/nm_6440_wayback_20181104222418.html` | https://www.realclearpolitics.com/epolls/2018/governor/nm/new_mexico_governor_pearce_vs_grisham-6440.html | https://web.archive.org/web/20181104222418/https://www.realclearpolitics.com/epolls/2018/governor/nm/new_mexico_governor_pearce_vs_grisham-6440.html | 2018-11-04 22:24 | Sun, 04 Nov 2018 15:02:10 GMT | RCP Average 10/24 - 11/1: Grisham 52.3 / Pearce 44.3 (Grisham +8.0); 3 of 6 listed polls in average |
| `rcp_2018_governor/nv_6422_wayback_20181104221834.html` | https://www.realclearpolitics.com/epolls/2018/governor/nv/nevada_governor_laxalt_vs_sisolak-6422.html | https://web.archive.org/web/20181104221834/https://www.realclearpolitics.com/epolls/2018/governor/nv/nevada_governor_laxalt_vs_sisolak-6422.html | 2018-11-04 22:18 | Sat, 03 Nov 2018 23:47:23 GMT | RCP Average 10/8 - 11/1: Laxalt 45.6 / Sisolak 44.6 (Laxalt +1.0); 5 of 12 listed polls in average |
| `rcp_2018_governor/nv_6692_wayback_20181104221708.html` | https://www.realclearpolitics.com/epolls/2018/governor/nv/nevada_governor_laxalt_vs_sisolak_vs_lord-6692.html | https://web.archive.org/web/20181104221708/https://www.realclearpolitics.com/epolls/2018/governor/nv/nevada_governor_laxalt_vs_sisolak_vs_lord-6692.html | 2018-11-04 22:17 | Wed, 31 Oct 2018 17:38:52 GMT | RCP Average 9/30 - 10/29: Laxalt 44.5 / Sisolak 43.0 / Lord 5.0 (Laxalt +1.5); 2 of 4 listed polls in average |
| `rcp_2018_governor/ny_6536_wayback_20181104225547.html` | https://www.realclearpolitics.com/epolls/2018/governor/ny/new_york_governor_molinaro_vs_cuomo-6536.html | https://web.archive.org/web/20181104225547/https://www.realclearpolitics.com/epolls/2018/governor/ny/new_york_governor_molinaro_vs_cuomo-6536.html | 2018-11-04 22:55 | Sun, 04 Nov 2018 15:10:53 GMT | RCP Average 10/10 - 11/1: Cuomo 53.5 / Molinaro 35.5 (Cuomo +18.0); 2 of 8 listed polls in average |
| `rcp_2018_governor/oh_6426_wayback_20181106195131.html` | https://www.realclearpolitics.com/epolls/2018/governor/oh/ohio_governor_dewine_vs_cordray-6426.html | https://web.archive.org/web/20181106195131/https://www.realclearpolitics.com/epolls/2018/governor/oh/ohio_governor_dewine_vs_cordray-6426.html | 2018-11-06 19:51 | Tue, 06 Nov 2018 13:54:48 GMT | No RCP Average row; 8 polls listed |
| `rcp_2018_governor/ok_6633_wayback_20181106115137.html` | https://www.realclearpolitics.com/epolls/2018/governor/ok/oklahoma_governor_stitt_vs_edmondson-6633.html | https://web.archive.org/web/20181106115137/https://www.realclearpolitics.com/epolls/2018/governor/ok/oklahoma_governor_stitt_vs_edmondson-6633.html | 2018-11-06 11:51 | Mon, 05 Nov 2018 00:48:55 GMT | RCP Average 9/25 - 11/3: Stitt 48.0 / Edmondson 42.7 (Stitt +5.3); 3 of 7 listed polls in average |
| `rcp_2018_governor/or_6428_wayback_20181104221757.html` | https://www.realclearpolitics.com/epolls/2018/governor/or/oregon_governor_buehler_vs_brown-6428.html | https://web.archive.org/web/20181104221757/https://www.realclearpolitics.com/epolls/2018/governor/or/oregon_governor_buehler_vs_brown-6428.html | 2018-11-04 22:17 | Fri, 02 Nov 2018 11:29:08 GMT | RCP Average 10/4 - 10/30: Brown 44.0 / Buehler 39.7 (Brown +4.3); 3 of 9 listed polls in average |
| `rcp_2018_governor/pa_6542_wayback_20181106195129.html` | https://www.realclearpolitics.com/epolls/2018/governor/pa/pennsylvania_governor_wagner_vs_wolf-6542.html | https://web.archive.org/web/20181106195129/https://www.realclearpolitics.com/epolls/2018/governor/pa/pennsylvania_governor_wagner_vs_wolf-6542.html | 2018-11-06 19:51 | Sat, 03 Nov 2018 02:40:26 GMT | RCP Average 9/12 - 11/1: Wolf 56.3 / Wagner 36.7 (Wolf +19.6); 3 of 11 listed polls in average |
| `rcp_2018_governor/ri_6544_wayback_20181104222322.html` | https://www.realclearpolitics.com/epolls/2018/governor/ri/rhode_island_governor_fung_vs_raimondo-6544.html | https://web.archive.org/web/20181104222322/https://www.realclearpolitics.com/epolls/2018/governor/ri/rhode_island_governor_fung_vs_raimondo-6544.html | 2018-11-04 22:23 | Wed, 31 Oct 2018 14:44:17 GMT | RCP Average 9/27 - 10/24: Raimondo 46.5 / Fung 34.0 (Raimondo +12.5); 2 of 5 listed polls in average |
| `rcp_2018_governor/sc_6431_wayback_20181104222324.html` | https://www.realclearpolitics.com/epolls/2018/governor/sc/south_carolina_governor_mcmaster_vs_smith-6431.html | https://web.archive.org/web/20181104222324/https://www.realclearpolitics.com/epolls/2018/governor/sc/south_carolina_governor_mcmaster_vs_smith-6431.html | 2018-11-04 22:23 | Fri, 02 Nov 2018 18:53:11 GMT | No RCP Average row; 3 polls listed |
| `rcp_2018_governor/sd_6433_wayback_20181105221739.html` | https://www.realclearpolitics.com/epolls/2018/governor/sd/south_dakota_governor_noem_vs_sutton-6433.html | https://web.archive.org/web/20181105221739/https://www.realclearpolitics.com/epolls/2018/governor/sd/south_dakota_governor_noem_vs_sutton-6433.html | 2018-11-05 22:17 | Mon, 05 Nov 2018 16:39:49 GMT | No RCP Average row; 3 polls listed |
| `rcp_2018_governor/tn_6644_wayback_20181104222002.html` | https://www.realclearpolitics.com/epolls/2018/governor/tn/tennessee_governor_lee_vs_dean-6644.html | https://web.archive.org/web/20181104222002/https://www.realclearpolitics.com/epolls/2018/governor/tn/tennessee_governor_lee_vs_dean-6644.html | 2018-11-04 22:20 | Sat, 03 Nov 2018 15:02:46 GMT | RCP Average 10/22 - 10/30: Lee 53.0 / Dean 39.2 (Lee +13.8); 5 of 12 listed polls in average |
| `rcp_2018_governor/tx_6435_wayback_20181104221848.html` | https://www.realclearpolitics.com/epolls/2018/governor/tx/texas_governor_abbott_vs_valdez-6435.html | https://web.archive.org/web/20181104221848/https://www.realclearpolitics.com/epolls/2018/governor/tx/texas_governor_abbott_vs_valdez-6435.html | 2018-11-04 22:18 | Thu, 01 Nov 2018 14:02:34 GMT | RCP Average 10/8 - 10/30: Abbott 55.7 / Valdez 37.8 (Abbott +17.9); 6 of 19 listed polls in average |
| `rcp_2018_governor/vt_6657_wayback_20181104222425.html` | https://www.realclearpolitics.com/epolls/2018/governor/vt/vermont_governor_scott_vs_hallquist-6657.html | https://web.archive.org/web/20181104222425/https://www.realclearpolitics.com/epolls/2018/governor/vt/vermont_governor_scott_vs_hallquist-6657.html | 2018-11-04 22:24 | Fri, 02 Nov 2018 11:51:54 GMT | No RCP Average row; 2 polls listed |
| `rcp_2018_governor/wi_6606_wayback_20181106195132.html` | https://www.realclearpolitics.com/epolls/2018/governor/wi/wisconsin_governor_walker_vs_evers-6606.html | https://web.archive.org/web/20181106195132/https://www.realclearpolitics.com/epolls/2018/governor/wi/wisconsin_governor_walker_vs_evers-6606.html | 2018-11-06 19:51 | Sun, 04 Nov 2018 16:35:54 GMT | No RCP Average row; 11 polls listed |
| `rcp_2022_governor/ak_7484_wayback_20221027174209.html` | https://www.realclearpolitics.com/epolls/2022/governor/ak/alaska_governor_-7484.html | https://web.archive.org/web/20221027174209/https://www.realclearpolitics.com/epolls/2022/governor/ak/alaska_governor_-7484.html | 2022-10-27 17:42 | Fri, 30 Sep 2022 20:24:34 GMT | No polls listed (header only: Dunleavy (R) *, Democrat (D)) |
| `rcp_2022_governor/al_7755_wayback_20221101192844.html` | https://www.realclearpolitics.com/epolls/2022/governor/al/alabama_governor_ivery_vs_flowers-7755.html | https://web.archive.org/web/20221101192844/https://www.realclearpolitics.com/epolls/2022/governor/al/alabama_governor_ivery_vs_flowers-7755.html | 2022-11-01 19:28 | Tue, 01 Nov 2022 00:32:33 GMT | No RCP Average row; 1 polls listed |
| `rcp_2022_governor/ar_7698_wayback_20221108042623.html` | https://www.realclearpolitics.com/epolls/2022/governor/ar/arkansas_governor_huckabee_sanders_vs_jones-7698.html | https://web.archive.org/web/20221108042623/https://www.realclearpolitics.com/epolls/2022/governor/ar/arkansas_governor_huckabee_sanders_vs_jones-7698.html | 2022-11-08 04:26 | Thu, 03 Nov 2022 20:54:34 GMT | No RCP Average row; 3 polls listed |
| `rcp_2022_governor/az_7842_wayback_20221109065543.html` | https://www.realclearpolitics.com/epolls/2022/governor/az/arizona_governor_lake_vs_hobbs-7842.html | https://web.archive.org/web/20221109065543/https://www.realclearpolitics.com/epolls/2022/governor/az/arizona_governor_lake_vs_hobbs-7842.html | 2022-11-09 06:55 | Tue, 08 Nov 2022 12:14:04 GMT | RCP Average 11/1 - 11/7: Lake 50.8 / Hobbs 47.3 (Lake +3.5); 4 of 29 listed polls in average |
| `rcp_2022_governor/ca_7488_wayback_20221020155803.html` | https://www.realclearpolitics.com/epolls/2022/governor/ca/california_governor_dahle_vs_newsom-7488.html | https://web.archive.org/web/20221020155803/https://www.realclearpolitics.com/epolls/2022/governor/ca/california_governor_dahle_vs_newsom-7488.html | 2022-10-20 15:58 | Wed, 12 Oct 2022 03:12:20 GMT | RCP Average 9/2 - 10/10: Newsom 56.0 / Dahle 32.7 (Newsom +23.3); 3 of 4 listed polls in average |
| `rcp_2022_governor/co_7774_wayback_20221109023753.html` | https://www.realclearpolitics.com/epolls/2022/governor/co/colorado_governor_ganahl_vs_polis-7774.html | https://web.archive.org/web/20221109023753/https://www.realclearpolitics.com/epolls/2022/governor/co/colorado_governor_ganahl_vs_polis-7774.html | 2022-11-09 02:37 | Mon, 07 Nov 2022 23:42:23 GMT | RCP Average 10/26 - 11/5: Polis 53.0 / Ganahl 42.3 (Polis +10.7); 3 of 9 listed polls in average |
| `rcp_2022_governor/ct_7684_wayback_20221106073702.html` | https://www.realclearpolitics.com/epolls/2022/governor/ct/connecticut_governor_stefanowski_vs_lamont-7684.html | https://web.archive.org/web/20221106073702/https://www.realclearpolitics.com/epolls/2022/governor/ct/connecticut_governor_stefanowski_vs_lamont-7684.html | 2022-11-06 07:37 | Thu, 27 Oct 2022 18:36:16 GMT | RCP Average 10/10 - 10/23: Lamont 52.7 / Stefanowski 41.7 (Lamont +11.0); 3 of 8 listed polls in average |
| `rcp_2022_governor/fl_7324_wayback_20221109060931.html` | https://www.realclearpolitics.com/epolls/2022/governor/fl/florida_governor_desantis_vs_crist-7324.html | https://web.archive.org/web/20221109060931/https://www.realclearpolitics.com/epolls/2022/governor/fl/florida_governor_desantis_vs_crist-7324.html | 2022-11-09 06:09 | Wed, 09 Nov 2022 03:20:15 GMT | RCP Average 10/17 - 11/6: DeSantis 54.4 / Crist 42.2 (DeSantis +12.2); 5 of 21 listed polls in average |
| `rcp_2022_governor/ga_7538_wayback_20221109020839.html` | https://www.realclearpolitics.com/epolls/2022/governor/ga/georgia_governor_kemp_vs_abrams-7538.html | https://web.archive.org/web/20221109020839/https://www.realclearpolitics.com/epolls/2022/governor/ga/georgia_governor_kemp_vs_abrams-7538.html | 2022-11-09 02:08 | Tue, 08 Nov 2022 11:12:17 GMT | RCP Average 11/1 - 11/7: Kemp 52.8 / Abrams 44.5 (Kemp +8.3); 6 of 46 listed polls in average |
| `rcp_2022_governor/ia_7494_wayback_20221109050731.html` | https://www.realclearpolitics.com/epolls/2022/governor/ia/iowa_governor_reynolds_vs_dejear-7494.html | https://web.archive.org/web/20221109050731/https://www.realclearpolitics.com/epolls/2022/governor/ia/iowa_governor_reynolds_vs_dejear-7494.html | 2022-11-09 05:07 | Sun, 06 Nov 2022 15:14:50 GMT | No RCP Average row; 5 polls listed |
| `rcp_2022_governor/il_7768_wayback_20221108010931.html` | https://www.realclearpolitics.com/epolls/2022/governor/il/illinois_governor_bailey_vs_pritzker-7768.html | https://web.archive.org/web/20221108010931/https://www.realclearpolitics.com/epolls/2022/governor/il/illinois_governor_bailey_vs_pritzker-7768.html | 2022-11-08 01:09 | Thu, 27 Oct 2022 18:39:12 GMT | No RCP Average row; 3 polls listed |
| `rcp_2022_governor/ks_7388_wayback_20221104013552.html` | https://www.realclearpolitics.com/epolls/2022/governor/ks/kansas-governor-schmidt-vs-kelly-7388.html | https://web.archive.org/web/20221104013552/https://www.realclearpolitics.com/epolls/2022/governor/ks/kansas-governor-schmidt-vs-kelly-7388.html | 2022-11-04 01:35 | Wed, 02 Nov 2022 11:23:34 GMT | No RCP Average row; 2 polls listed |
| `rcp_2022_governor/ma_7609_wayback_20221107114353.html` | https://www.realclearpolitics.com/epolls/2022/governor/ma/massachusetts_governor_diehl_vs_healey-7609.html | https://web.archive.org/web/20221107114353/https://www.realclearpolitics.com/epolls/2022/governor/ma/massachusetts_governor_diehl_vs_healey-7609.html | 2022-11-07 11:43 | Fri, 28 Oct 2022 16:54:49 GMT | RCP Average 10/13 - 10/26: Healey 58.5 / Diehl 33.0 (Healey +25.5); 2 of 8 listed polls in average |
| `rcp_2022_governor/md_7841_wayback_20221108005422.html` | https://www.realclearpolitics.com/epolls/2022/governor/md/maryland_governor_cox_vs_moore_-7841.html | https://web.archive.org/web/20221108005422/https://www.realclearpolitics.com/epolls/2022/governor/md/maryland_governor_cox_vs_moore_-7841.html | 2022-11-08 00:54 | Fri, 28 Oct 2022 02:17:38 GMT | RCP Average 9/8 - 10/23: Moore 57.0 / Cox 28.7 (Moore +28.3); 3 of 3 listed polls in average |
| `rcp_2022_governor/me_7623_wayback_20221103005705.html` | https://www.realclearpolitics.com/epolls/2022/governor/me/maine_governor_lepage_vs_mills-7623.html | https://web.archive.org/web/20221103005705/https://www.realclearpolitics.com/epolls/2022/governor/me/maine_governor_lepage_vs_mills-7623.html | 2022-11-03 00:57 | Thu, 27 Oct 2022 18:39:25 GMT | No RCP Average row; 7 polls listed |
| `rcp_2022_governor/mi_7545_wayback_20221109020844.html` | https://www.realclearpolitics.com/epolls/2022/governor/mi/michigan_governor_dixon_vs_whitmer-7545.html | https://web.archive.org/web/20221109020844/https://www.realclearpolitics.com/epolls/2022/governor/mi/michigan_governor_dixon_vs_whitmer-7545.html | 2022-11-09 02:08 | Tue, 08 Nov 2022 06:03:52 GMT | RCP Average 10/30 - 11/7: Whitmer 48.3 / Dixon 47.3 (Whitmer +1.0); 4 of 25 listed polls in average |
| `rcp_2022_governor/mn_7405_wayback_20221108192223.html` | https://www.realclearpolitics.com/epolls/2022/governor/mn/minnesota_governor_jensen_vs_walz-7405.html | https://web.archive.org/web/20221108192223/https://www.realclearpolitics.com/epolls/2022/governor/mn/minnesota_governor_jensen_vs_walz-7405.html | 2022-11-08 19:22 | Thu, 03 Nov 2022 15:05:15 GMT | RCP Average 10/10 - 10/30: Walz 48.0 / Jensen 43.7 (Walz +4.3); 3 of 11 listed polls in average |
| `rcp_2022_governor/nh_7498_wayback_20221107142546.html` | https://www.realclearpolitics.com/epolls/2022/governor/nh/new_hampshire_governor_sununu_vs_sherman-7498.html | https://web.archive.org/web/20221107142546/https://www.realclearpolitics.com/epolls/2022/governor/nh/new_hampshire_governor_sununu_vs_sherman-7498.html | 2022-11-07 14:25 | Mon, 07 Nov 2022 00:38:37 GMT | RCP Average 10/28 - 11/6: Sununu 56.0 / Sherman 39.3 (Sununu +16.7); 4 of 16 listed polls in average |
| `rcp_2022_governor/nm_7646_wayback_20221108132517.html` | https://www.realclearpolitics.com/epolls/2022/governor/nm/new_mexico_governor_ronchetti_vs_lujan_grisham-7646.html | https://web.archive.org/web/20221108132517/https://www.realclearpolitics.com/epolls/2022/governor/nm/new_mexico_governor_ronchetti_vs_lujan_grisham-7646.html | 2022-11-08 13:25 | Tue, 08 Nov 2022 12:30:12 GMT | No RCP Average row; 11 polls listed |
| `rcp_2022_governor/nv_7394_wayback_20221109023843.html` | https://www.realclearpolitics.com/epolls/2022/governor/nv/nevada_governor_lombardo_vs_sisolak-7394.html | https://web.archive.org/web/20221109023843/https://www.realclearpolitics.com/epolls/2022/governor/nv/nevada_governor_lombardo_vs_sisolak-7394.html | 2022-11-09 02:38 | Tue, 08 Nov 2022 11:21:34 GMT | RCP Average 10/24 - 11/7: Lombardo 47.8 / Sisolak 45.0 (Lombardo +2.8); 5 of 27 listed polls in average |
| `rcp_2022_governor/ny_7749_wayback_20221109020842.html` | https://www.realclearpolitics.com/epolls/2022/governor/ny/new_york_governor_zeldin_vs_hochul-7749.html | https://web.archive.org/web/20221109020842/https://www.realclearpolitics.com/epolls/2022/governor/ny/new_york_governor_zeldin_vs_hochul-7749.html | 2022-11-09 02:08 | Mon, 07 Nov 2022 21:38:20 GMT | RCP Average 10/26 - 10/31: Hochul 52.0 / Zeldin 45.0 (Hochul +7.0); 3 of 17 listed polls in average |
| `rcp_2022_governor/oh_7697_wayback_20221109023749.html` | https://www.realclearpolitics.com/epolls/2022/governor/oh/ohio_governor_dewine_vs_whaley-7697.html | https://web.archive.org/web/20221109023749/https://www.realclearpolitics.com/epolls/2022/governor/oh/ohio_governor_dewine_vs_whaley-7697.html | 2022-11-09 02:37 | Mon, 07 Nov 2022 23:03:29 GMT | RCP Average 10/30 - 11/5: DeWine 58.0 / Whaley 35.6 (DeWine +22.4); 5 of 19 listed polls in average |
| `rcp_2022_governor/ok_7775_wayback_20221109055333.html` | https://www.realclearpolitics.com/epolls/2022/governor/ok/oklahoma_governor_stitt_vs_hofmeister-7775.html | https://web.archive.org/web/20221109055333/https://www.realclearpolitics.com/epolls/2022/governor/ok/oklahoma_governor_stitt_vs_hofmeister-7775.html | 2022-11-09 05:53 | Fri, 04 Nov 2022 02:08:24 GMT | No RCP Average row; 7 polls listed |
| `rcp_2022_governor/or_7908_wayback_20221108000804.html` | https://www.realclearpolitics.com/epolls/2022/governor/or/oregon_governor_drazan_vs_kotek_vs_johnson-7908.html | https://web.archive.org/web/20221108000804/https://www.realclearpolitics.com/epolls/2022/governor/or/oregon_governor_drazan_vs_kotek_vs_johnson-7908.html | 2022-11-08 00:08 | Mon, 07 Nov 2022 21:45:39 GMT | RCP Average 10/17 - 11/6: Kotek 42.3 / Drazan 41.0 / Johnson 11.5 (Kotek +1.3); 4 of 10 listed polls in average |
| `rcp_2022_governor/pa_7696_wayback_20221109053900.html` | https://www.realclearpolitics.com/epolls/2022/governor/pa/pennsylvania_governor_mastriano_vs_shapiro-7696.html | https://web.archive.org/web/20221109053900/https://www.realclearpolitics.com/epolls/2022/governor/pa/pennsylvania_governor_mastriano_vs_shapiro-7696.html | 2022-11-09 05:39 | Tue, 08 Nov 2022 11:24:59 GMT | RCP Average 11/1 - 11/3: Shapiro 51.0 / Mastriano 42.7 (Shapiro +8.3); 3 of 33 listed polls in average |
| `rcp_2022_governor/ri_7913_wayback_20221011111455.html` | https://www.realclearpolitics.com/epolls/2022/governor/ri/rhode_island_governor_kalus_vs_mckee-7913.html | https://web.archive.org/web/20221011111455/https://www.realclearpolitics.com/epolls/2022/governor/ri/rhode_island_governor_kalus_vs_mckee-7913.html | 2022-10-11 11:14 | Tue, 11 Oct 2022 11:06:09 GMT | No RCP Average row; 2 polls listed |
| `rcp_2022_governor/tx_7376_wayback_20221109075355.html` | https://www.realclearpolitics.com/epolls/2022/governor/tx/texas-governor-abbott-vs-orourke-7376.html | https://web.archive.org/web/20221109075355/https://www.realclearpolitics.com/epolls/2022/governor/tx/texas-governor-abbott-vs-orourke-7376.html | 2022-11-09 07:53 | Mon, 07 Nov 2022 22:37:33 GMT | RCP Average 10/16 - 10/26: Abbott 52.7 / O'Rourke 42.3 (Abbott +10.4); 3 of 33 listed polls in average |
| `rcp_2022_governor/vt_7906_wayback_20220911125513.html` | https://www.realclearpolitics.com/epolls/2022/governor/vt/vermont_governor_scott_vs_siegel-7906.html | https://web.archive.org/web/20220911125513/https://www.realclearpolitics.com/epolls/2022/governor/vt/vermont_governor_scott_vs_siegel-7906.html | 2022-09-11 12:55 | Sat, 10 Sep 2022 03:50:00 GMT | No RCP Average row; 1 polls listed |
| `rcp_2022_governor/wi_7761_wayback_20221107180953.html` | https://www.realclearpolitics.com/epolls/2022/governor/wi/wisconsin_governor_michels_vs_evers-7761.html | https://web.archive.org/web/20221107180953/https://www.realclearpolitics.com/epolls/2022/governor/wi/wisconsin_governor_michels_vs_evers-7761.html | 2022-11-07 18:09 | Sat, 05 Nov 2022 21:34:47 GMT | RCP Average 10/24 - 11/4: Michels 48.0 / Evers 47.6 (Michels +0.4); 5 of 21 listed polls in average |
| `rcp_generic_ballot/gcb2018_6185_wayback_20181107000538.html` | https://www.realclearpolitics.com/epolls/other/2018_generic_congressional_vote-6185.html | https://web.archive.org/web/20181107000538/https://www.realclearpolitics.com/epolls/other/2018_generic_congressional_vote-6185.html | 2018-11-07 00:05 | Mon, 05 Nov 2018 15:05:02 GMT | RCP Average 10/13 - 11/3: Democrats 49.7 / Republicans 42.4 (Democrats +7.3); 11 of 309 listed polls in average |
| `other_captures/nm2022_7646_wayback_20221106163554.html` | https://www.realclearpolitics.com/epolls/2022/governor/nm/new_mexico_governor_ronchetti_vs_lujan_grisham-7646.html | https://web.archive.org/web/20221106163554/https://www.realclearpolitics.com/epolls/2022/governor/nm/new_mexico_governor_ronchetti_vs_lujan_grisham-7646.html | 2022-11-06 16:35 | Tue, 01 Nov 2022 00:11:19 GMT | RCP Average 10/19 - 10/28: Lujan Grisham 48.0 / Ronchetti 44.0 (Lujan Grisham +4.0); 4 of 11 listed polls in average |
| `other_captures/oh2018_6426_wayback_20181105012231.html` | https://www.realclearpolitics.com/epolls/2018/governor/oh/ohio_governor_dewine_vs_cordray-6426.html | https://web.archive.org/web/20181105012231/https://www.realclearpolitics.com/epolls/2018/governor/oh/ohio_governor_dewine_vs_cordray-6426.html | 2018-11-05 01:22 | Fri, 02 Nov 2018 11:36:56 GMT | RCP Average 10/4 - 10/30: Cordray 47.7 / DeWine 43.0 (Cordray +4.7); 3 of 8 listed polls in average |
| `other_captures/wi2018_6682_wayback_20181124135640.html` | https://www.realclearpolitics.com/epolls/2018/governor/wi/wisconsin_governor_walker_vs_evers_vs_anderson-6682.html | https://web.archive.org/web/20181124135640/https://www.realclearpolitics.com/epolls/2018/governor/wi/wisconsin_governor_walker_vs_evers_vs_anderson-6682.html | 2018-11-24 13:56 | Wed, 07 Nov 2018 15:53:02 GMT | Final Results row (Evers +1.2); no RCP Average row; 6 polls listed |
| `rcp_index/gov2018_map_wayback_20181104222031.html` | https://www.realclearpolitics.com/epolls/2018/governor/2018_elections_governor_map.html | https://web.archive.org/web/20181104222031/https://www.realclearpolitics.com/epolls/2018/governor/2018_elections_governor_map.html | 2018-11-04 22:20 | Sat, 03 Nov 2018 23:31:41 GMT | RCP governor map (index of race pages) |
| `rcp_index/gov2022_map_wayback_20221108161622.html` | https://www.realclearpolitics.com/epolls/2022/governor/elections-map.html | https://web.archive.org/web/20221108161622/https://www.realclearpolitics.com/epolls/2022/governor/elections-map.html | 2022-11-08 16:16 | Mon, 07 Nov 2022 21:46:16 GMT | RCP governor map (index of race pages) |

### RCP data feeds (current state, retrieved 2026-10-28)
| File | URL | Title | RCP average in feed |
|---|---|---|---|
| `rcp_feeds/race_6185_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6185/polling_data.json | 2018 Generic Congressional Vote | shown: 10/13 - 11/3, Democrats 49.7, Republicans 42.4 (13 polls flagged) |
| `rcp_feeds/race_6273_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6273/polling_data.json | 2018 Maryland Governor - Hogan vs. Jealous | shown: 9/11 - 10/7, Hogan 54.5, Jealous 35.8 (4 polls flagged) |
| `rcp_feeds/race_6405_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6405/polling_data.json | Alabama Governor - Ivey vs. Maddox | none |
| `rcp_feeds/race_6408_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6408/polling_data.json | 2018 Arkansas Governor - Hutchinson vs. Henderson | none |
| `rcp_feeds/race_6409_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6409/polling_data.json | 2018 Colorado Governor - Stapleton vs. Polis | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Polis 47.5, Stapleton 41.0 |
| `rcp_feeds/race_6412_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6412/polling_data.json | 2018 Hawaii Governor - Tupola vs. Ige | none |
| `rcp_feeds/race_6413_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6413/polling_data.json | Idaho Governor - Little vs. Jordan | none |
| `rcp_feeds/race_6418_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6418/polling_data.json | 2018 Massachusetts Governor - Baker vs. Gonzalez | shown: 10/1 - 10/28, Baker 66.0, Gonzalez 26.3 (4 polls flagged) |
| `rcp_feeds/race_6421_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6421/polling_data.json | Nebraska Governor - Ricketts vs. Krist | none |
| `rcp_feeds/race_6422_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6422/polling_data.json | 2018 Nevada Governor - Laxalt vs. Sisolak | shown: 10/29 - 11/4, Laxalt 46.3, Sisolak 45.7 (3 polls flagged) |
| `rcp_feeds/race_6426_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6426/polling_data.json | 2018 Ohio Governor - DeWine vs. Cordray | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Cordray 48.5, DeWine 44.5 |
| `rcp_feeds/race_6428_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6428/polling_data.json | 2018 Oregon Governor - Buehler vs. Brown | shown: 10/4 - 10/30, Brown 44.0, Buehler 39.7 (3 polls flagged) |
| `rcp_feeds/race_6431_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6431/polling_data.json | 2018 South Carolina Governor - McMaster vs. Smith | none |
| `rcp_feeds/race_6433_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6433/polling_data.json | 2018 South Dakota Governor - Noem vs. Sutton | shown: 10/29 - 11/4, Noem 47.5, Sutton 45.5 (2 polls flagged) |
| `rcp_feeds/race_6435_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6435/polling_data.json | 2018 Texas Governor - Abbott vs. Valdez | shown: 10/15 - 10/30, Abbott 55.0, Valdez 38.3 (4 polls flagged) |
| `rcp_feeds/race_6439_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6439/polling_data.json | 2018 Illinois Governor - Rauner vs. Pritzker | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Pritzker 43.7, Rauner 28.0 |
| `rcp_feeds/race_6440_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6440/polling_data.json | 2018 New Mexico Governor - Pearce vs. Grisham | shown: 10/24 - 11/1, Grisham 52.3, Pearce 44.3 (3 polls flagged) |
| `rcp_feeds/race_6441_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6441/polling_data.json | 2018 Michigan Governor - Schuette vs. Whitmer | shown: 10/24 - 11/5, Whitmer 50.0, Schuette 40.0 (3 polls flagged) |
| `rcp_feeds/race_6443_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6443/polling_data.json | 2018 Minnesota Governor - Johnson vs. Walz | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Walz 47.0, Johnson 40.0 |
| `rcp_feeds/race_6477_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6477/polling_data.json | 2018 Iowa Governor - Reynolds vs. Hubbell | shown: 10/8 - 11/2, Hubbell 45.0, Reynolds 44.3 (3 polls flagged) |
| `rcp_feeds/race_6518_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6518/polling_data.json | 2018 Florida Governor - DeSantis vs. Gillum | shown: 10/29 - 11/5, Gillum 49.4, DeSantis 45.8 (5 polls flagged) |
| `rcp_feeds/race_6536_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6536/polling_data.json | 2018 New York Governor - Molinaro vs. Cuomo | shown: 10/10 - 11/1, Cuomo 53.5, Molinaro 35.5 (2 polls flagged) |
| `rcp_feeds/race_6542_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6542/polling_data.json | 2018 Pennsylvania Governor - Wagner vs. Wolf | shown: 9/12 - 11/1, Wolf 56.3, Wagner 36.7 (3 polls flagged) |
| `rcp_feeds/race_6544_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6544/polling_data.json | 2018 Rhode Island Governor - Fung vs. Raimondo | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Raimondo 46.5, Fung 34.0 |
| `rcp_feeds/race_6561_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6561/polling_data.json | 2018 New Hampshire Governor - Sununu vs. Kelly | shown: 10/27 - 11/4, Sununu 50.0, Kelly 46.0 (2 polls flagged) |
| `rcp_feeds/race_6577_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6577/polling_data.json | 2018 Connecticut Governor - Stefanowski vs. Lamont | shown: 10/22 - 11/1, Lamont 44.3, Stefanowski 39.8 (4 polls flagged) |
| `rcp_feeds/race_6593_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6593/polling_data.json | 2018 California Governor - Cox vs. Newsom | shown: 10/19 - 11/5, Newsom 55.3, Cox 38.8 (4 polls flagged) |
| `rcp_feeds/race_6606_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6606/polling_data.json | 2018 Wisconsin Governor - Walker vs. Evers | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Evers 49.0, Walker 46.5 |
| `rcp_feeds/race_6614_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6614/polling_data.json | 2018 Arizona Governor - Ducey vs. Garcia | shown: 10/24 - 11/4, Ducey 54.8, Garcia 38.5 (4 polls flagged) |
| `rcp_feeds/race_6628_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6628/polling_data.json | 2018 Georgia Governor - Kemp vs. Abrams | shown: 10/14 - 11/3, Kemp 48.8, Abrams 45.8 (5 polls flagged) |
| `rcp_feeds/race_6630_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6630/polling_data.json | 2018 Kansas Governor - Kobach vs. Kelly | none |
| `rcp_feeds/race_6633_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6633/polling_data.json | 2018 Oklahoma Governor - Stitt vs. Edmondson | shown: 9/25 - 11/3, Stitt 48.0, Edmondson 42.7 (3 polls flagged) |
| `rcp_feeds/race_6643_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6643/polling_data.json | 2018 Maine Governor - Moody vs. Mills | none |
| `rcp_feeds/race_6644_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6644/polling_data.json | 2018 Tennessee Governor - Lee vs. Dean | shown: 10/22 - 10/30, Lee 53.0, Dean 39.2 (5 polls flagged) |
| `rcp_feeds/race_6657_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6657/polling_data.json | 2018 Vermont Governor - Scott vs. Hallquist | none |
| `rcp_feeds/race_6660_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6660/polling_data.json | 2018 Kansas Governor - Kobach vs. Kelly vs. Orman | none |
| `rcp_feeds/race_6666_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6666/polling_data.json | Wyoming Governor - Gordon vs. Throne | none |
| `rcp_feeds/race_6667_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6667/polling_data.json | 2018 Connecticut Governor - Stefanowski vs. Lamont vs. Hanscomb vs. Griebel | none |
| `rcp_feeds/race_6669_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6669/polling_data.json | 2018 Alaska Governor - Dunleavy vs. Begich vs. Walker | none |
| `rcp_feeds/race_6682_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6682/polling_data.json | 2018 Wisconsin Governor - Walker vs. Evers vs. Anderson | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Evers 47.3, Walker 44.3, Anderson 3.3 |
| `rcp_feeds/race_6692_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6692/polling_data.json | 2018 Nevada Governor - Laxalt vs. Sisolak vs. Lord | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Laxalt 44.5, Sisolak 43.0, Lord 5.0 |
| `rcp_feeds/race_6696_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6696/polling_data.json | 2018 Georgia Governor - Kemp vs. Abrams vs. Metz | none |
| `rcp_feeds/race_6711_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/6711/polling_data.json | 2018 Alaska Governor - Dunleavy vs. Begich | none |
| `rcp_feeds/race_7324_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7324/polling_data.json | 2022 Florida Governor - DeSantis vs. Crist | shown: 10/17 - 11/6, DeSantis 54.4, Crist 42.2 (5 polls flagged) |
| `rcp_feeds/race_7376_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7376/polling_data.json | 2022 Texas Governor - Abbott vs. O'Rourke | shown: 10/16 - 10/26, Abbott 52.7, O'Rourke 42.3 (3 polls flagged) |
| `rcp_feeds/race_7388_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7388/polling_data.json | 2022 Kansas Governor - Schmidt vs. Kelly | none |
| `rcp_feeds/race_7394_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7394/polling_data.json | 2022 Nevada Governor - Lombardo vs. Sisolak | shown: 10/24 - 11/7, Lombardo 47.8, Sisolak 45.0 (5 polls flagged) |
| `rcp_feeds/race_7405_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7405/polling_data.json | 2022 Minnesota Governor - Jensen vs. Walz | shown: 10/10 - 10/30, Walz 48.0, Jensen 43.7 (3 polls flagged) |
| `rcp_feeds/race_7484_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7484/polling_data.json | Alaska Governor - | none |
| `rcp_feeds/race_7488_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7488/polling_data.json | 2022 California Governor - Dahle vs. Newsom | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Newsom 58.0, Dahle 34.0 |
| `rcp_feeds/race_7494_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7494/polling_data.json | 2022 Iowa Governor - Reynolds vs. DeJear | none |
| `rcp_feeds/race_7498_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7498/polling_data.json | 2022 New Hampshire Governor - Sununu vs. Sherman | shown: 10/28 - 11/6, Sununu 56.4, Sherman 39.4 (5 polls flagged) |
| `rcp_feeds/race_7505_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7505/polling_data.json | 2022 South Carolina Governor - McMaster vs. Cunningham | none |
| `rcp_feeds/race_7538_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7538/polling_data.json | 2022 Georgia Governor - Kemp vs. Abrams | shown: 11/1 - 11/7, Kemp 52.8, Abrams 44.5 (6 polls flagged) |
| `rcp_feeds/race_7545_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7545/polling_data.json | 2022 Michigan Governor - Dixon vs. Whitmer | shown: 10/30 - 11/7, Whitmer 48.3, Dixon 47.3 (4 polls flagged) |
| `rcp_feeds/race_7609_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7609/polling_data.json | 2022 Massachusetts Governor - Diehl vs. Healey | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Healey 58.5, Diehl 33.0 |
| `rcp_feeds/race_7623_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7623/polling_data.json | 2022 Maine Governor - LePage vs. Mills | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Mills 49.0, LePage 40.8 |
| `rcp_feeds/race_7646_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7646/polling_data.json | 2022 New Mexico Governor - Ronchetti vs. Lujan Grisham | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Lujan Grisham 48.0, Ronchetti 44.0 |
| `rcp_feeds/race_7684_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7684/polling_data.json | 2022 Connecticut Governor - Stefanowski vs. Lamont | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Lamont 52.7, Stefanowski 41.7 |
| `rcp_feeds/race_7696_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7696/polling_data.json | 2022 Pennsylvania Governor - Mastriano vs. Shapiro | shown: 11/1 - 11/3, Shapiro 51.0, Mastriano 42.7 (3 polls flagged) |
| `rcp_feeds/race_7697_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7697/polling_data.json | 2022 Ohio Governor - DeWine vs. Whaley | shown: 10/30 - 11/5, DeWine 58.0, Whaley 35.6 (6 polls flagged) |
| `rcp_feeds/race_7698_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7698/polling_data.json | 2022 Arkansas Governor - Huckabee Sanders vs. Jones | none |
| `rcp_feeds/race_7749_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7749/polling_data.json | 2022 New York Governor - Zeldin vs. Hochul | shown: 10/26 - 10/31, Hochul 52.0, Zeldin 45.0 (3 polls flagged) |
| `rcp_feeds/race_7755_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7755/polling_data.json | 2022 Alabama Governor - Ivery vs. Flowers | none |
| `rcp_feeds/race_7761_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7761/polling_data.json | 2022 Wisconsin Governor - Michels vs. Evers | shown: 10/24 - 11/5, Michels 48.4, Evers 47.8 (5 polls flagged) |
| `rcp_feeds/race_7768_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7768/polling_data.json | 2022 Illinois Governor - Bailey vs. Pritzker | none |
| `rcp_feeds/race_7774_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7774/polling_data.json | 2022 Colorado Governor - Ganahl vs. Polis | shown: 10/26 - 11/5, Polis 53.0, Ganahl 42.3 (3 polls flagged) |
| `rcp_feeds/race_7775_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7775/polling_data.json | 2022 Oklahoma Governor - Stitt vs. Hofmeister | none |
| `rcp_feeds/race_7841_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7841/polling_data.json | 2022 Maryland Governor - Cox vs. Moore  | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Moore 57.0, Cox 28.7 |
| `rcp_feeds/race_7842_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7842/polling_data.json | 2022 Arizona Governor - Lake vs. Hobbs | shown: 11/1 - 11/7, Lake 50.8, Hobbs 47.3 (4 polls flagged) |
| `rcp_feeds/race_7906_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7906/polling_data.json | 2022 Vermont Governor - Scott vs. Siegel | none |
| `rcp_feeds/race_7908_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7908/polling_data.json | 2022 Oregon Governor - Drazan vs. Kotek vs. Johnson | hidden (`show_rcp_avg: 0`, date 12/31 - 12/31): Kotek 40.8, Drazan 40.8, Johnson 12.8 |
| `rcp_feeds/race_7913_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7913/polling_data.json | 2022 Rhode Island Governor - Kalus vs. McKee | none |
| `rcp_feeds/race_7918_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7918/polling_data.json | 2022 Alaska Governor - Dunleavy vs. Pierce vs. Gara vs. Walker | none |
| `rcp_feeds/race_7919_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7919/polling_data.json | 2022 Alaska Governor - Dunleavy vs. Gara vs. Walker (2nd Round) | none |
| `rcp_feeds/race_7920_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7920/polling_data.json | 2022 Alaska Governor - Dunleavy vs. Gara (Final Round) | none |
| `rcp_feeds/race_7925_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7925/polling_data.json | 2022 Tennessee Governor - Lee vs. Martin | none |
| `rcp_feeds/race_7927_polling_data_2026-10-28.json` | https://orig.realclearpolitics.com/poll/race/7927/polling_data.json | 2022 South Dakota Governor - Noem vs. Smith | none |
