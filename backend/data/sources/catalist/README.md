# Catalist, "What Happened 2024" national crosstabs

| File | URL | Retrieved | Notes |
|---|---|---|---|
| `Catalist_What_Happened_2024_Public_National_Crosstabs_2025_05_19.xlsx` | https://www.dropbox.com/scl/fi/jqvidz01a1t0b59iu3hvm/Catalist_What_Happened_2024_Public_National_Crosstabs_2025_05_19.xlsx?rlkey=yai50nhvydpnpszreuwnlxfih (linked from https://catalist.us/whathappened2024/; downloaded through Dropbox's content host, dl.dropboxusercontent.com, same path) | 2026-10-31 19:39 UTC | One sheet. By group: composition of voters by year (2008–2024), two-way Democratic vote share for president (2012–2024) and for Congress ("CD", 2012–2024), and three-way results. |

**How it's used.** `data/build_catalist_baselines.py` writes `data/catalist_baselines.json`: each slider group's two-way margin, 2 × D share − 100. The nonwhite-by-education cells are the Black, Latino, AAPI and Other cells weighted by that year's composition. There are two years:
- **2024 president ("Pres 2024")**, the model's group baselines. The script checks it against `model.CATALIST_BASELINES`, typed in earlier from the same release; all twelve match to 0.01.
- **2022 House ("CD 2022")**, no presidential race that year. The governor county maps use it for counties whose starting map is an incumbent's 2022 race (setting `governor_county_match_start_year`), so the demographic shift there is each group's 2026 margin minus its 2022 margin.
