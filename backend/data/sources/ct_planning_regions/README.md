# Connecticut presidential results by town, and the planning-region crosswalk

Retrieved 2026-10-27 13:27 UTC with curl, saved as served.

Since 2022 the Census Bureau treats Connecticut's nine planning regions (FIPS 09110–09190) as county equivalents, so the ACS county demographics and the county map shapes use them. The county results file read by `parse_county_pres.py` still reports the eight old counties (09001–09015), which left Connecticut with no county rows. Towns nest within both the old counties and the planning regions, so `supplement_ct_pres.py` sums these official town results into planning regions, and `build_slices_from_github.py` moves Connecticut's 2020 precincts (named by town) into them.

| File | URL | Notes |
|---|---|---|
| `ct_sots_2024_president_by_town.csv` | https://ct.elstats.civera.com/api/download_contest/36252_table.csv?split_party=false | Connecticut Secretary of the State, election history, Nov 5 2024 General Election, President: one `City/Town` row per town (169) with its polling places beneath, plus a `State` row. Harris 992,053, Trump 736,918, total votes cast 1,759,010; the 169 town rows sum exactly to the state row. |
| `ct_sots_2024_president_contest_36252.html` | https://electionhistory.ct.gov/eng/contests/view/36252 | The contest page that links the CSV above. |
| `ct_sots_2020_president_by_town.csv` | https://ct.elstats.civera.com/api/download_contest/15175_table.csv?split_party=false | Same, Nov 3 2020 General Election, President. Biden 1,080,831, Trump 714,717, total votes cast 1,823,856; town rows sum exactly to the state row. |
| `ct_sots_2020_president_contest_15175.html` | https://electionhistory.ct.gov/eng/contests/view/15175 | The contest page that links the CSV above. |
| `census_ct_cou_to_cousub_crosswalk.txt` | https://www2.census.gov/geo/docs/reference/ct_change/ct_cou_to_cousub_crosswalk.txt | Census Bureau, Connecticut county to county-subdivision crosswalk: each of the 169 towns with its old county and its planning region (pipe-delimited; five "County subdivisions not defined" water rows). |

All 169 town names in both result files and in DRA's 2020 Connecticut precinct names (`../../dra_vtd/Election_Data_CT.v06/`) match the crosswalk's town names (after dropping " town").
