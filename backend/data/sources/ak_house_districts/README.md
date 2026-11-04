# Alaska state house districts for the county maps

Inputs to `data/build_ak_house_districts.py`, which writes `data/ak_house_districts.json`
(40 districts in `counties.json`'s row format) and `data/county_geojson/AK_house.geojson`.
They are used by the Senate, governor and AK-AL county maps when the setting
`ak_house_district_map` is on (the default; user request, Nov 4 2026). With the setting
off, the maps use Alaska's 30 boroughs, whose results in `counties.json` are estimated
(each borough's 2024 total vote equals its 2020 total, e.g. Anchorage 132,899 both years).

The districts are the 2022 Proclamation Plan's, used in the 2022, 2024 and 2026 elections.

| File | URL | Retrieved (UTC) | sha256 | Used for |
|---|---|---|---|---|
| `ENRbyPrecinct_24GENR.csv` (+ `_headers.txt`, the response headers: Last-Modified Aug 6 2026) | https://www.elections.alaska.gov/results/24GENR/ENRbyPrecinct.csv (linked from https://www.elections.alaska.gov/election-results/e/?id=24genr) | 2026-11-04 16:41 | aca7ab6e949d1319b48692ab8e8b694835ff6a9bd862fc9efbac91550c25f957 | 2024 presidential votes by district. Each precinct name begins with its district (`01-600 Ketchikan No. 1`); each district also has `District N - Absentee`, `- Early Voting` and `- Question` rows, which are included. `HD99 Fed Overseas Absentee` (401 presidential votes, federal-only ballots) has no district and is left out. The file's presidential votes total 338,177 (Trump 184,458, Harris 140,026), equal to the Division's official 2024 Election Summary Report (`../ak_rcv_2026/doe_2024_validation/ElectionSummaryReport.pdf`, "Total Votes 338,177"). |
| `cb_2024_02_sldl_500k.zip` | https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_02_sldl_500k.zip | 2026-11-04 16:41 | cf18bf3d0dd0a6530a216289ebe5ab24d16b1991e12ae2bdfa3d7c392320ca76 | The map's district shapes (cartographic boundaries, clipped to the shoreline) |
| `tl_2024_02_sldl.zip` | https://www2.census.gov/geo/tiger/TIGER2024/SLDL/tl_2024_02_sldl.zip | 2026-11-04 16:44 | 2f24f574e086dedcf817355f0adbf0fe0a03e9022679c7fced471da8c9347dbe | TIGER/Line districts (not clipped, like the Census blocks and VTDs), for placing blocks in districts |
| `BlockAssign_ST02_AK.zip` | https://www2.census.gov/geo/docs/maps-data/data/baf2020/BlockAssign_ST02_AK.zip | 2026-11-04 16:45 | 686f4283976326621be7173a21036ba2ea65e0b08346e6aac0952718d23b31db | 2020 Census block assignment files; `BlockAssign_ST02_AK_VTD.txt` puts each 2020 block in its 2020 VTD. Its SLDL file is the pre-2022 plan and is not used. The Census Bureau's BAF page (https://www.census.gov/geographies/reference-files/time-series/geo/block-assignment-files.html) lists only the 2020 files. |
| not committed (130 MB): `data/cache/tl_2020_02_tabblock20/tl_2020_02_tabblock20.zip` | https://www2.census.gov/geo/tiger/TIGER2020/TABBLOCK20/tl_2020_02_tabblock20.zip | 2026-11-04 16:45 | 6fe96f3a8bbaf78945ee3a3897264ed74f1b72bc0cb46ffd434039729dccf493 | 2020 blocks' population (POP20) and interior points (only the .dbf is read) |
| `acs5_2024_sldl_AK_{A,B}.json`, `acs5_2023_sldl_AK_{A,B}.json` | https://api.census.gov/data/2024/acs/acs5 and https://api.census.gov/data/2023/acs/acs5, `for=state legislative district (lower chamber):*&in=state:02`, the variables of `data/fetch_acs.py` (VARS_A, VARS_B; API key not recorded) | 2026-11-04 16:43 | 3cb492ac…be40, 4ef1f312…7be047 (2024); 04756dea…5384, 5b89e322…4694 (2023) | Demographics: 2020-2024 5-year, and 2019-2023 as `demo_acs2023` (setting `acs_2020_2024` off), with `fetch_acs_counties.normalize`'s definitions |
| Dave's Redistricting Alaska VTD data, cached in `data/dra_vtd/` (gitignored): `Election_Data_AK.v07.zip`, `Geojson_AK.v07.zip` | https://github.com/dra2020/vtd_data (2020_VTD/AK, v07) | 2025-05 (cached, as for the other states in `../SOURCES.md`) | 08ddd987…b553, 723bd90d…a127 | 2020 presidential votes per 2020 VTD (`E_20_PRES_Dem/Rep/Total`), and each VTD's label point |

## Method

- **2024:** the precinct file's presidential votes summed by district (D = DEM, R = REP,
  total = every presidential candidate). 337,776 votes in the 40 districts.
- **2020:** each DRA VTD's 2020 presidential votes are split among the current districts
  by its 2020 Census population in each. Blocks go to VTDs by the block assignment file
  and to districts by their interior points in the TIGER/Line districts (blocks nest in
  them). A VTD with no population would go wholly to the district holding its label
  point; the 8 such VTDs have no votes. Statewide: D 153,778, R 189,951, total 357,569 (DRA's totals).
  `dra_vtd_2020_pres_by_hd.csv` lists every VTD's pieces: district, 2020 population,
  share and votes.
  - 45 of the 456 VTDs have more than 5% of their 2020 population outside their
    largest district; they hold 55,060 of the 2020 votes (15.4%).
  - For comparison, placing each VTD wholly in the district holding its label point,
    as `build_slices_from_github.py` assigns VTDs elsewhere, would put 17,642 votes in
    other districts and change 14 districts' 2020 margins by more than a point (HD 18 by
    16.0).
- **Margins:** total-vote margins, 100 × (D − R) / total. The trend is (2024 margin −
  2020 margin) + 6.0, as in `build_counties.py`.
