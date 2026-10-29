# Census ACS 2020-2024 5-year estimates (Oct 29 switch)

Retrieved 2026-10-29. The data itself comes from the Census Data API
(`https://api.census.gov/data/2024/acs/acs5`, key in `backend/.env`), fetched by
`data/fetch_acs.py` (congressional districts), `data/fetch_acs_counties.py`
(counties) and `data/aggregate_acs_new_lines.py` (tracts, redrawn states).
Setting `acs_2020_2024` (off: the 2019-2023 values in
`data/demographics_acs2023.csv` and `data/demographics_counties_acs2023.csv`,
the files as they were before the switch).

| File | URL | What it shows |
|---|---|---|
| `census_2024_acs_release_schedule.html` | https://www.census.gov/programs-surveys/acs/news/data-releases/2024/release-schedule.html | Census Bureau: 2020-2024 5-year data released January 29, 2026 |
| `census_2024_acs_revised_release_dates_notice.html` | https://content.govdelivery.com/accounts/CODOLA/bulletins/3fe72bc | Colorado State Demography Office bulletin relaying the Census notice: the shutdown delayed the 2020-2024 5-year release to January 29, 2026 |
| `census_api_2024_acs5_catalog.json` | https://api.census.gov/data/2024/acs/acs5.json | The API's dataset catalog for the 2024 5-year release |
| `census_api_2024_acs5_groups_<table>.json` | https://api.census.gov/data/2024/acs/acs5/groups/<table>.json (B03002, B15003, C15002H, B01001, B01002, B19013, B01003) | Variable labels for every table the fetch scripts read. Every variable has the same label as in the 2019-2023 release except B19013_001E, whose dollars are now 2024 dollars |
| `census_api_ga_districts_2023_vs_2024_acs5.json` | https://api.census.gov/data/2023/acs/acs5 and .../2024/acs/acs5 (`get=NAME,B01003_001E,B03002_003E,B03002_004E&for=congressional district:*&in=state:13`) | The 2019-2023 release names Georgia's districts "(118th Congress)", the 2020-2024 release "(119th Congress)": the earlier tables were on Georgia's pre-2024 map |
| `census_2025_acs_1yr_release_dates_press_release.html` | https://www.census.gov/newsroom/press-releases/2026/dates-announced-for-2025-acs-1-year-estimates.html | The 2025 1-year estimates were released Oct 29, 2026. Not used: no tract data for the redrawn states, and a fifth of the 5-year sample |
| `census_api_2025_acs1_groups_B15003.json` | https://api.census.gov/data/2025/acs/acs1/groups/B15003.json | The 2025 1-year release renumbers the education table (bachelor's degree is B15003_020E, not _022E), so the fetch scripts can't read it as written |
