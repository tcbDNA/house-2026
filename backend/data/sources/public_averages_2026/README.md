# 2026 generic congressional ballot: public polling averages

Collected 2026-10-26 for the forecast's public-averages comparison panel.
Every file below was retrieved on **2026-10-26**. The Wayback copy has its capture timestamp in the filename.
Margin = Democratic % minus Republican %, computed from each source's own D and R figures.

## Summary (as of Oct 26, 2026)

| Source | D | R | Margin | Source's own headline | As of |
|---|---|---|---|---|---|
| RealClearPolling | 51.1 | 42.8 | D+8.3 | "+8.3" Democrats | RCP Average, polls 10/8 - 10/23 (Wayback capture 2026-10-26 15:38 UTC) |
| Silver Bulletin | 50.81 | 41.84 | D+8.97 (D+9.0) | "D +9" | 2026-10-26 (`modeldate` 10/26/2026; page "Updated October 26, 2026") |
| VoteHub | 50.7 | 42.3 | D+8.4 | n/a (API) | 2026-10-26 (`last_updated` 2026-10-26T19:10:53) |

## Files

| File | URL | Notes |
|---|---|---|
| `rcp_generic_ballot_wayback_20261026153807.html` | Live: https://www.realclearpolling.com/polls/state-of-the-union/generic-congressional-vote <br> Archive: https://web.archive.org/web/20261026153807/https://www.realclearpolling.com/polls/state-of-the-union/generic-congressional-vote | The live page returned HTTP 403 (a bot-check page), so this file is the latest Wayback capture from Oct 26, fetched raw with the `id_` suffix. The RCP Average row (poll id 8670, `type: rcp_average`, date "10/8 - 10/23") shows Democrats 51.1, Republicans 42.8, spread Democrats +8.3. |
| `silver_bulletin_generic_ballot_2026-10-26.html` | https://www.natesilver.net/p/generic-ballot-average-2026-nate-silver-bulletin-congress-polls | Silver Bulletin's generic ballot landing page. The post is marked `only_paid`, but the top section is public: "Updated October 26, 2026 ... their lead on the generic congressional ballot is sitting at D +9." It also says the forecast page uses a likely-voter-adjusted version (D +9.5), which is **not** the figure recorded here. The page's Datawrapper iframes point to old chart versions (rfiFi/31, sEHv2/34), whose data ends in Jan 2026. |
| `silver_bulletin_datawrapper_rfiFi_v4688_dataset_2026-10-26.csv` | https://datawrapper.dwcdn.net/rfiFi/4688/dataset.csv | The data behind the page's average chart (rfiFi), from the current public version, 4688 (https://datawrapper.dwcdn.net/rfiFi/ redirects there; published 2026-10-26T18:01Z, modified 19:01Z). Last row is 10/26/2026: dem 50.81469, rep 41.84453, a margin of 8.97 that rounds to the page's "D +9". |
| `votehub_generic_ballot_2026_2026-10-26.json` | https://polling.votehub.com/site/averages/generic_ballot_2026 | VoteHub average metadata: key `generic_ballot_2026`, "Who leads the 2026 generic congressional ballot?", `last_updated` 2026-10-26T19:10:53. Found through the list at https://polling.votehub.com/site/averages?limit=200. |
| `votehub_generic_ballot_2026_values_2026-10-26.json` | https://polling.votehub.com/site/averages/generic_ballot_2026/values | VoteHub's daily average series, the same endpoint votehub.com/polls uses. The 2026-10-26 entry is dem 50.7 (CI 46.6-54.8) and rep 42.3 (CI 37.8-46.7), so D+8.4. |
