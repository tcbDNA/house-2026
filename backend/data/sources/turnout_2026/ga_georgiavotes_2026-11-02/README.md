# Georgia early vote from Georgia Votes, retrieved 2026-11-02 ~20:50 UTC (site "Last updated 2026-11-02 09:18:46")

Georgia Votes (https://georgiavotes.com/about) is a one-person project built from the Georgia Secretary of State's free
absentee and voter history files. The Secretary of State's own pages (sos.ga.gov, mvp.sos.ga.gov) return a Cloudflare
challenge to scripts, so they could not be checked directly. Not used by the model.

| File | URL |
|---|---|
| `georgiavotes_home.html` | https://georgiavotes.com/ (statewide totals, race/sex/age vs 2022 and 2024 at the same point, 2022 vote history) |
| `georgiavotes_primary-voters.html` | https://georgiavotes.com/primary-voters (2026 primary voters by party ballot who have voted early) |
| `georgiavotes_ushouse.html` | https://georgiavotes.com/ushouse (votes by congressional district) |
| `georgiavotes_ushouse_cd1.html` | https://georgiavotes.com/ushouse?cd=1 (GA-01 totals, race vs 2022 and 2024, 2022 vote history) |
| `georgiavotes_county.html` | https://georgiavotes.com/county (every county: registered voters, votes, mail, early) |
| `ga01_counties/county_c<N>_<County>.html` | https://georgiavotes.com/county?c=<N> for GA-01's 15 counties (Appling 1, Bacon 3, Brantley 13, Bryan 15, Camden 20, Charlton 24, Chatham 25, Effingham 51, Glynn 63, Liberty 89, Long 91, McIntosh 98, Pierce 113, Ware 148, Wayne 151); retrieved ~21:00 UTC |
| `ga01_counties/ga01_counties.csv` | Parsed from those pages by `ga01_parse.py`: votes, mail, early, registered, votes at the same point in 2022, race shares 2026/2024/2022, 2024 president and 2022 governor and Senate margins, and 2022 vote history of this year's voters |
