# Kalshi 2026 turnout markets

Retrieved 2026-11-03 at 20:29Z (Election Day; markets last updated 2026-11-02T18:29Z) from Kalshi's public API. Earlier downloads are in git history: 2026-10-26 (markets last updated 2026-10-26T15:17Z) and 2026-11-01 (markets last updated 2026-10-29T16:37Z). From Nov 1 to Nov 3, 153 of 500 race medians moved more than 1% (95 up, 58 down); Alabama's governor market lost its median (above the highest quoted threshold, 1.7M).

| File | URL | What |
|---|---|---|
| `kalshi_markets_KXMIDTERMVOTETURN_p1.json` … `_p6.json` | https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXMIDTERMVOTETURN&limit=1000 (paged with `cursor`) | "Midterm Voter Turnout": per race (35 Senate, 35 governor, 432 House), contracts "Will the total vote count for all participants in <race> be above X?", with yes bid/ask |
| `kalshi_markets_KXHOUSETURNOUT.json` | https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXHOUSETURNOUT&limit=200 | National House turnout bands. No quotes on 2026-10-26; on 2026-11-01 the bid/ask mids of the 5M-wide bands put the median near 117M House votes (115-120M band 0.28, 110-115M 0.24, above 125M 0.18), above the 112.4M the per-district markets add up to; on 2026-11-03 the median is still in the 115-120M band (115-120M 0.255, 110-115M 0.225, 120-125M 0.20, above 125M 0.17), against 112.2M from the per-district markets. Not used by the model. |

`backend/data/build_turnout_2026.py` turns these into `backend/data/turnout_2026.csv`: each race's market-implied median total vote (where the bid/ask mid of P(total > X), made non-increasing, crosses 0.5) and its ratio to the race's 2024 presidential vote. The user cited Georgia ≈ 4.4M, Texas ≈ 11M and Mississippi ≈ 834K from the Oct 26 markets, whose implied medians were 4.46M, 10.75M and 0.81M; in the Nov 1 download they were 4.22M, 10.52M and 0.91M (80%, 92% and 74% of 2024), and in the Nov 3 download 4.10M, 10.25M and 1.08M (78%, 90% and 88%).
