# County results of running incumbents' last governor races

Used by `data/build_gov_county_results.py` to write `data/gov_county_results.csv`. The governor county maps
then use those counties' positions relative to the state (setting `governor_county_incumbent_map`; user
request, Oct 31, 2026). Retrieved 2026-10-31, about 19:00–19:15 UTC.

Sixteen incumbents are running again after winning a governor's race. Fourteen last won in 2022 (AZ AR CT HI
ID IL MD MA NE NV NY OR PA TX) and two in 2024 (NH VT). South Dakota's Rhoden has never won a governor's
race, so South Dakota keeps the presidential map. Idaho (Bundy, 17.2%) and Oregon (Johnson, 8.6%) are built
but not used by default: a third candidate took over 5% in each, the governor WAR records' rule
(`governor_county_incumbent_map_skip_third`).

| Files | URL | States | Notes |
|---|---|---|---|
| `medsl_2022/2022-<st>-local-precinct-general.zip` (ct, id, ma, md, ne, or, pa) | https://raw.githubusercontent.com/MEDSL/2022-elections-official/main/individual_states/2022-<st>-local-precinct-general.zip (repo: https://github.com/MEDSL/2022-elections-official) | CT MA MD NE OR PA | MIT Election Data and Science Lab, 2022 precinct returns. Office "GOVERNOR"; every vote mode summed; undervote, overvote and blank rows dropped; a nominee's votes on every ballot line counted (Lamont's minor-party lines). Connecticut's towns go to its planning regions with `../ct_planning_regions/census_ct_cou_to_cousub_crosswalk.txt`. The Idaho file is saved but not used, because it counts many precincts twice (Little 714,374 against the official 358,598). |
| `medsl_2022/codebook.md` | https://raw.githubusercontent.com/MEDSL/2022-elections-official/main/codebook.md | | The files' codebook. |
| `ar_2022_governor_by_county.json` | https://enr-results-api.totalresults.com/Contest/GetSingleContestResults?cId=arkansas&electionID=1844&contestType=STW&contestID=286&locationTypeID=2 | AR | The Arkansas official results system (the same service as `../gov_results/official/2022_ar_governor_contest_results.json`) with locations: all 75 counties, keyed by FIPS. Choice 528 is Chris Jones (D) and 530 is Sarah Huckabee Sanders (R). MIT's Arkansas file has no Phillips County, so it isn't used. |
| `../gov_results/official/2022_id_governor_by_county.csv` | https://canvass.sos.idaho.gov/eng/contests/download/17251/show_granularity_dt_id:3/.csv | ID | Idaho Secretary of State canvass, by county (already saved; see `../gov_results/official/README.md`). |
| `../../dra_vtd/Election_Data_<ST>.v07/election_data_<ST>.v07.csv` | https://github.com/dra2020/vtd_data (2020_VTD/<ST>/Election_Data_<ST>.v07.zip; raw files gitignored, fetched by `data/fetch_dra_github.py`) | AZ HI IL NV NY TX (E_22_GOV), NH VT (E_24_GOV) | Dave's Redistricting precinct results on 2020 precincts, summed to counties by GEOID20's first five digits. Hawaii's Kalawao is added to Maui, as in the presidential county data. |

**Checks** (`build_gov_county_results.py` prints them), county sums against the official statewide results in
`../gov_results/official_overrides.csv`:
- **Exact D and R votes:** AR, HI, ID, MA, MD, NE, NH, NV, VT, AZ, IL.
- **Off by at most 0.1% of a candidate's votes:** CT (Lamont −1,069), NY (+11 / +10), OR (−40), PA (−105 / −140), TX (+1,116 / −2).
- **Totals:** a few states' totals differ by write-ins (AZ +7,080, NE −5,798, TX +3,860). Every county-summed statewide margin is within 0.2 points of the official one; the largest gap is NE, −23.44 against −23.24.
