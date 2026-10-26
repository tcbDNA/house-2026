# Kalshi 2026 turnout markets

Retrieved 2026-10-26 (markets last updated 2026-10-26T15:17Z) from Kalshi's public API.

| File | URL | What |
|---|---|---|
| `kalshi_markets_KXMIDTERMVOTETURN_p1.json` … `_p5.json` | https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXMIDTERMVOTETURN&limit=1000 (paged with `cursor`) | "Midterm Voter Turnout": per race (35 Senate, 35 governor, 432 House), contracts "Will the total vote count for all participants in <race> be above X?", with yes bid/ask |
| `kalshi_markets_KXHOUSETURNOUT.json` | https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXHOUSETURNOUT&limit=200 | National House turnout bands (no quotes on 2026-10-26) |

`backend/data/build_turnout_2026.py` turns these into `backend/data/turnout_2026.csv`: each race's market-implied median total vote (where the bid/ask mid of P(total > X), made non-increasing, crosses 0.5) and its ratio to the race's 2024 presidential vote. The user cited Georgia ≈ 4.4M, Texas ≈ 11M and Mississippi ≈ 834K from these markets; the implied medians are 4.46M, 10.75M and 0.81M.
