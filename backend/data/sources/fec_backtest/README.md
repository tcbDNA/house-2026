# Official results for the forecast backtest

All files retrieved 2026-10-26. The spreadsheets and PDF are saved exactly as downloaded.

## Downloaded sources

| File | URL | What it is |
|---|---|---|
| `federalelections2016.xlsx` | https://www.fec.gov/documents/1890/federalelections2016.xlsx (redirects to https://www.fec.gov/resources/cms-content/documents/federalelections2016.xlsx), linked from https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/federal-elections-2016/ | FEC, *Federal Elections 2016* |
| `federalelections2022.xlsx` | https://www.fec.gov/documents/5676/federalelections2022.xlsx (redirects to https://www.fec.gov/resources/cms-content/documents/federalelections2022.xlsx), linked from https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/federal-elections-2022/ | FEC, *Federal Elections 2022* |
| `house_clerk_2024election.pdf` | https://history.house.gov/Institution/Election-Statistics/2024election/ (redirects to https://historycms.house.gov/Institution/Election-Statistics/2024election/) | Office of the Clerk, U.S. House: *Statistics of the Presidential and Congressional Election of November 5, 2024*, "from official sources", published 2025-03-10 |

**Why 2024 is not from the FEC.** As of 2026-10-26 the FEC has published no 2024 Senate or House results compilation. Its results page (https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/) lists only *Official 2024 Presidential General Election Results*; that file is already saved as `../fec_pres/2024presgeresults.xlsx`. The "Federal Elections" series stops at 2022, and `.../federal-elections-2024/` returns 404. For 2024 Senate and House results we therefore use the House Clerk's official compilation of certified state returns. We did not use state canvass files directly.

**Check of the Clerk compilation against the FEC.** We compared the Clerk's 2024 presidential vote by state (Republican and Democratic elector lines) with the FEC's official 2024 presidential file. 48 of 51 states plus DC match exactly. NY differs because the Clerk counts only the R and D party lines, while the FEC counts candidate totals that include fusion lines. ME (FEC is +140 R, +301 D) and VA (FEC is about −1k for each) differ slightly.

## Derived CSVs

### `pres_2016_by_state.csv` (51 rows: 50 states and DC)
- Source: `federalelections2016.xlsx`, sheet "Table 2. Electoral & Pop Vote".
- Columns: `state` (USPS code), `dem` (Clinton), `rep` (Trump), `total` (all candidates), `margin` = 100·(dem−rep)/total.
- Checks: dem + rep + "All Others" = total in every state, and the state columns sum to the national totals (Clinton 65,853,514; Trump 62,984,828; total 136,669,276).

### `senate_2022_results.csv` (36 rows: 34 states, with CA and OK each having a full-term and a special race)
- Source: `federalelections2022.xlsx`, sheet "7. US Senate Results by State", GENERAL VOTES column. For fusion candidates we use the FEC's COMBINED GE PARTY TOTALS (CT Blumenthal D+WF; NY Schumer D+WF and Pinion R+CRV).
- Check: for every race, the candidate votes plus write-in/scattered votes equal the FEC "Total State Votes".

### `senate_2024_results.csv` (35 rows: 33 states, with CA and NE each having a full-term and a special race)
- Source: `house_clerk_2024election.pdf`, the "FOR UNITED STATES SENATOR" section of each state. The PDF text was extracted with pypdf.
- Fusion: CT Murphy is D+WF. NY Gillibrand is D+WF and Sapraicone is R+Conservative.
- Check: our totals plus the blank/over/under/void lines equal the Clerk's own recapitulation total for each state.

### Senate CSV schema (2022 and 2024)
`state, special, dem_name, dem_votes, rep_name, rep_votes, ind_name, ind_votes, total_votes, margin_d_minus_r, notes`

- `special` = yes for unexpired-term races: CA 2022, OK 2022, CA 2024, NE 2024 (Ricketts vs Love). `(state, special)` is unique.
- `dem_*` and `rep_*` hold the top Democratic and top Republican candidate. ND's Democratic-NPL counts as D. In LA 2022 (open election) and AK 2022 (top-4/RCV) several candidates share a party, so the notes give the party-sum votes and the party-sum margin.
- `ind_*` holds the top candidate from neither major party, filled when that candidate has ≥5% of the vote or the race lacks a D or an R. 2022: McMullin UT, Becker ND, Cleveland ID. 2024: Osborn NE, Sanders VT, King ME, Bowen UT.
- `total_votes` = all candidate votes, including write-ins and scattering, plus Nevada's "None of These Candidates" (the FEC counts NOTC in its 2022 totals). Blank, over, under and void ballots are excluded; the Clerk lists them for HI, MA, ME, NY, VT and WY in 2024.
- `margin_d_minus_r` = 100·(dem_votes−rep_votes)/total_votes. It is left blank when no Democrat was on the ballot (UT 2022, NE 2024 regular, VT 2024). For those races the notes give the independent-minus-R margin.
- Name format: 2022 uses the FEC's "Last, First"; 2024 uses the Clerk's "First Last".

Races that need special handling (details are in each row's `notes`):
- **AK 2022**: top-4 primary, then a ranked-choice general. The vote columns hold the official first-choice summary. The notes give RCV rounds 1–3: in the final round Murkowski won 136,330 to Tshibaka's 117,534. The real contest was R vs R, so the D−R margin is not meaningful.
- **GA 2022**: the row holds the Nov 8 general. The notes give the Dec 6 runoff: Warnock 1,820,633, Walker 1,721,244, total 3,541,877, margin +2.81.
- **LA 2022**: the Nov 8 open all-party election. Kennedy won with more than 50%, so there was no runoff.
- **UT 2022**: Lee (R) vs McMullin (Unaffiliated). There was no D nominee.
- **CA 2022/2024 and WA**: top-two generals. Both happened to be D vs R.
- **NE 2024 regular**: Fischer (R) vs Osborn (petition independent). There was no D nominee.
- **ME 2024**: King (I) won in the first round. The D nominee Costello was also on the ballot.
- **VT 2024**: Sanders (I). There was no D nominee.

### `house_national_popular_vote.csv`
| year | scope | dem | rep | other | total | D−R margin |
|---|---|---|---|---|---|---|
| 2022 | all (50 states, DC, territories) | 51,628,838 | 54,298,205 | 2,246,001 | 108,173,044 | −2.47 |
| 2022 | 50 states | 51,410,295 | 54,262,607 | 2,230,181 | 107,903,083 | −2.64 |
| 2024 | 50 states | 70,571,330 | 74,390,864 | 3,034,348 | 147,996,542 | −2.58 |

- 2022: FEC *Federal Elections 2022*, sheet "6. Table 5 House by Party", general-election columns. The printed total matches Table 1's House total. The 50-state row drops AS, DC, GU, MP and VI.
- 2024: Clerk, "Recapitulation of Votes Cast for United States Representatives". D and R are the Clerk's national totals. The Clerk's printed total of 149,543,421 includes 1,546,879 non-votes, which we removed: blank/over/under/void lines in HI, ID, MA, ME, NH, NY, VT and WY, plus ME-2's "continuing/exhausted ballots" lines. We parsed every House race, and the per-state sums match the Clerk's 50 state totals exactly. ME-2's D/R figures in the Clerk compilation are final-round RCV numbers.
- In both years D and R are **party-line** votes. Fusion lines such as NY WF/Conservative and CT WF/Independent are counted in "other".


## Added for the 2024 incumbents

| File | URL | Retrieved | Use |
|---|---|---|---|
| `federalelections2018.xlsx` | https://www.fec.gov/documents/2706/federalelections2018.xlsx | 2026-10-26 | 2018 Senate winners → 2024 incumbents (Senate model backtest) |
| `fec_federal_elections_2018_page.html` | https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/federal-elections-2018/ | 2026-10-26 | index page |
