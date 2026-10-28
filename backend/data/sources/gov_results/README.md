# Governor results 2010–2024, state presidential results 2008/2012, national margins

Collected 2026-10-28 for the governor forecast model. Every number in the three CSVs comes from a file saved in this folder (or, for the 2016–2024 FEC files, already saved elsewhere in `backend/data/sources/`). Downloads are saved byte-for-byte as served. They were parsed with `python3 -I` (stdlib `html.parser` for Wikipedia; `xlrd`/`openpyxl` for the FEC files). The parsing scripts ran from a scratch directory outside the repo and are not committed. This README describes what they did.

## Output files

| File | Rows | Contents |
|---|---|---|
| `gov_results.csv` | 153 | Governor general elections: one row per race (see below) |
| `pres_state_2008_2012.csv` | 102 | State presidential results 2008 and 2012, 50 states + DC (FEC) |
| `national_margins.csv` | 9 | National D−R popular-vote margin: House 2010/2014/2018/2022, President 2008–2024 (FEC) |

Rows in `gov_results.csv` by year: 2010: 34, 2012: 3, 2014: 36, 2016: 3, 2018: 36, 2020: 2, 2021: 1, 2022: 36, 2024: 2.
- 2010, 2014, 2018, 2022: the 34 four-year-term states (AL AK AZ AR CA CO CT FL GA HI ID IL IA KS ME MD MA MI MN NE NV NM NY OH OK OR PA RI SC SD TN TX WI WY), plus NH and VT in 2014/2018/2022.
- NH and VT: every cycle from 2012 to 2024.
- Specials (`special = yes`): **WI 2012** recall election (Walker vs Barrett), **OR 2016** special election (Kate Brown), and **CA 2021** recall election (Newsom). The CA 2021 row is a yes/no recall vote, not a candidate race; see the row notes. The overview pages for every year from 2010 to 2024 were saved, odd years included. Their race-summary tables and section headings list no other special or recall governor elections in these 36 states. The other specials they list, UT 2010 and WV 2011, are outside the 36 states.

## gov_results.csv

**Source rule (user decision).** All values come from Wikipedia. The primary source is the per-year overview page "YYYY United States gubernatorial elections". Each of those pages has a race-summary table and a general-election results box for every state. The state's own page ("YYYY <State> gubernatorial election") was also saved for every race and compared field by field. The overview had a vote box for every race, so no race needed the state-page fallback. The one exception is CA 2021, where the overview prints a Yes/No table instead of a box; its question-2 candidates come from the state page.

Columns:
- `year, state, special`: `special = yes` for the WI 2012 recall, the OR 2016 special, and the CA 2021 recall.
- `d_*` / `r_*`: the highest-vote candidate whose ballot line is Democratic (including "Democratic (DFL)" and "Democratic/Progressive") or Republican. Names are spelled as the overview box prints them, minus annotations such as "(incumbent)" or "(withdrawn)" and running-mate names. Any annotation other than "incumbent" is copied into `notes`. Votes and % are as printed; the % sign is dropped. For New York fusion candidates, votes and % come from the page's own "Total" line across all of the candidate's party lines; the notes list each line. No percentage was computed.
- `other_*`: the highest-vote candidate other than the D and R candidates, filled only when that candidate's printed % is ≥ 5.0. Party is as printed.
- `total_votes`: the overview's printed "Total votes". This includes write-ins and, in NV, "None of These Candidates". In 13 races the printed total does not equal the sum of the printed lines (see below). The total was still recorded as printed.
- `incumbent, incumbent_party`: the "Incumbent"/"Governor" and "Party" columns of the overview race-summary table, as printed (MN shows "DFL").
- `incumbent_ran`: "yes" if the summary "Result/Status" text says the incumbent was re-elected, was elected to a full term, was elected to finish the term, or lost re-election. "no" if it says term-limited, retired, lost renomination, or lost nomination. Every row was classified, so none is UNVERIFIED. AK 2018 is a judgment call: the overview says "Incumbent retired", while the box lists Walker "(incumbent, withdrawn)" with 2.03% because his name stayed on the ballot.
- `winner, winner_party`: the highest-vote line in the box. The script checks that this candidate has the most votes among the d/r/other columns.
- `rcv_final_*`: blank in every row. AK 2022 is the only RCV governor general in scope. Both pages print only first-choice results, and the state page says Dunleavy "narrowly received the majority of votes in the first round, preventing an instant runoff". No final round was printed, so these fields are blank rather than copied from round 1. ME governor generals were not RCV on these pages (plain plurality boxes).
- `source_file, source_url`: the overview page. `source_revid` is the Wikipedia revision id of the saved copy (permalink: `https://en.wikipedia.org/w/index.php?oldid=<revid>`).
- `crosscheck_file, crosscheck_url, crosscheck_revid`: the state page. `crosscheck_diffs` is "agree", or it lists every numeric disagreement with the overview.

### Judgment calls and special rows (details are in each row's `notes`)
- **AK 2014**: no D on the ballot; `d_*` is blank. Independent Bill Walker won; he is in `other_*`. The state page says the Walker and Mallott campaigns merged and the Alaska Democratic Party endorsed the ticket.
- **AK 2018**: incumbent Walker (I) suspended his campaign but stayed on the ballot (2.03%). `incumbent_ran = no`, following the overview.
- **AK 2022**: top-four primary + RCV general. First-round shares only; `rcv_final_*` are blank because no later round was printed. Walker (I) has 20.73% in `other_*`. A second Republican, Charlie Pierce, has 4.48%; the "(withdrew)" annotation on the page belongs to his running mate.
- **VT 2020**: both pages label David Zuckerman "Progressive". He is used as the D candidate because the saved state page infobox shows "Alliance: Democratic" and its Democratic primary table shows him winning that primary. VT 2022 and 2024 nominees are printed as "Democratic/Progressive".
- **VT 2014**: no one reached 50%, and the General Assembly elected Shumlin (110–69 on the state page).
- **CA 2021 recall**: `d_*` = "No" (keep Newsom), 7,944,092 (61.88%). `r_*` = "Yes", 4,894,474 (38.12%). `winner` = Gavin Newsom. Question-2 leaders are in the notes. Exclude this row from candidate-race models if needed.
- **CA 2014/2018/2022**: top-two system; each general was D vs R.
- **Independents or third parties who won or finished second**: RI 2010 (Chafee, I, won; Caprio, D, third), AK 2014 (Walker, I, won), ME 2010 (Cutler, I, second; Mitchell, D, third), CO 2010 (Tancredo, Constitution, second; Maes, R, third with 11.14%).
- **Other ≥5% candidates**: 2010 CO Tom Tancredo (Constitution) 36.38%; 2010 ID Jana M. Kemp (Independent) 5.89%; 2010 MA Tim Cahill (Independent) 8.03%; 2010 ME Eliot Cutler (Independent) 35.87%; 2010 MN Tom Horner (Independence) 11.94%; 2010 RI Lincoln Chafee (Independent) 36.10%; 2010 WY Taylor Haynes (Independent) 7.32%; 2014 AK Bill Walker (Independent) 48.10%; 2014 HI Mufi Hannemann (Independent) 11.72%; 2014 ME Eliot Cutler (Independent) 8.43%; 2014 RI Robert J. Healey (Moderate) 21.38%; 2014 WY Don Wills (Independent) 5.89%; 2018 KS Greg Orman (Independent) 6.50%; 2018 ME Terry Hayes (Independent) 5.91%; 2022 AK Bill Walker (Independent) 20.73%; 2022 ID Ammon Bundy (Independent) 17.19%; 2022 OR Betsy Johnson (Independent) 8.63%.
- **2010 AL**: the overview annotates Robert J. Bentley as "(incumbent)", but its own summary table names Bob Riley as the incumbent. `incumbent` = Bob Riley and `incumbent_ran` = no; the stray annotation is noted.
- **2018 TN**: the overview combines 26 independents into one line, "Other candidates" (1.89%). The state page lists them individually; none reaches 5%.

### Where the overview and the state page disagree (numbers)
Recorded values follow the overview. A later step will check these races against official canvasses.

| Race | Disagreement |
|---|---|
| 2022 AL | total votes: overview 1,411,756, state page 1,415,283 |
| 2010 CO | Jaimes Brown %: overview 0.74, state page 0.75 |
| 2022 CO | total votes: overview 2,508,830, state page 2,540,680 |
| 2010 HI | Neil Abercrombie %: overview 58.61, state page 58.22; Duke Aiona %: overview 41.39, state page 41.12; total: overview 380,035, state page has no Total row (Turnout 382563) |
| 2022 HI | Josh Green votes: overview 259,901, state page 261,025; Josh Green %: overview 63.21, state page 63.16; Duke Aiona votes: overview 151,258, state page 152,237; Duke Aiona %: overview 36.79, state page 36.84; total votes: overview 411,159, state page 413,262 |
| 2018 ID | Brad Little %: overview 59.76, state page 59.77 |
| 2022 ID | Brad Little %: overview 60.52, state page 60.51; Ammon Bundy %: overview 17.19, state page 17.18; total votes: overview 592,557, state page 592,603 |
| 2010 ME | Eliot Cutler %: overview 35.87, state page 35.88 |
| 2014 ME | Paul LePage votes: overview 294,519, state page 294,533; Paul LePage %: overview 48.19, state page 48.18; Mike Michaud votes: overview 265,114, state page 265,125; Eliot Cutler votes: overview 51,515, state page 51,518; total votes: overview 611,227, state page 611,255 |
| 2014 MA | Charlie Baker %: overview 48.39, state page 48.40 |
| 2022 NE | Jim Pillen %: overview 59.74, state page 59.22; Carol Blood %: overview 36.29, state page 35.98; Scott Zimmerman votes: overview 26,445, state page 26,455; Scott Zimmerman %: overview 3.97, state page 3.93; total votes: overview 666,795, state page 672,593 |
| 2014 NH | Maggie Hassan %: overview 52.38, state page 52.37 |
| 2010 NM | total votes: overview 602,832, state page 602,827 |
| 2010 NY | Andrew Cuomo %: overview 63.05, state page 62.49; Carl Paladino %: overview 33.53, state page 33.23; Howie Hawkins %: overview 1.30, state page 1.29; Warren Redlich %: overview 1.05, state page 1.04; Jimmy McMillan %: overview 0.89, state page 0.88; total votes: overview 4,769,741, state page 4,657,955 |
| 2018 NY | Andrew Cuomo %: overview 59.62, state page 59.55; Marc Molinaro %: overview 36.21, state page 36.16; total votes: overview 6,097,362, state page 6,104,447 |
| 2022 NY | Kathy Hochul %: overview 53.20, state page 53.12; Lee Zeldin %: overview 46.80, state page 46.73; total votes: overview 5,902,996, state page 5,912,286 |
| 2018 OH | Mike DeWine %: overview 50.39, state page 50.40; Richard Cordray %: overview 46.68, state page 46.67; Travis Irvine votes: overview 79,985, state page 80,055; Travis Irvine %: overview 1.81, state page 1.80; Constance Gadell-Newton votes: overview 49,475, state page 49,536; total votes: overview 4,429,582, state page 4,435,820 |
| 2014 OK | Mary Fallin %: overview 55.80, state page 55.81 |
| 2022 OR | Betsy Johnson %: overview 8.63, state page 8.62 |
| 2018 PA | Tom Wolf %: overview 57.77, state page 57.74; Scott Wagner %: overview 40.70, state page 40.67; total votes: overview 5,012,555, state page 5,015,261 |
| 2022 PA | Josh Shapiro %: overview 56.49, state page 56.44; Doug Mastriano %: overview 41.71, state page 41.68; Christina DiGiulio %: overview 0.46, state page 0.45; total votes: overview 5,366,179, state page 5,370,763 |
| 2022 TX | Greg Abbott votes: overview 4,437,099, state page 4,435,558; Greg Abbott %: overview 54.76, state page 54.75; state page lists Jacqueline Abernathy (American Solidarity) 1,243 votes (0.02%), not in overview; total votes: overview 8,102,908, state page 8,101,994 |
| 2010 WI | Scott Walker %: overview 52.29, state page 52.25; Tom Barrett %: overview 46.52, state page 46.48; overview line Terry Virgil (Libertarian) 6,790 votes; the state page prints the same 6,790 votes as "Libertarian No Candidate" (non-candidate line); total votes: overview 2,158,974, state page 2,160,832 |
| 2021 CA (special) | Yes votes: overview 4,894,474, state page 4,894,473; Total votes: overview 12,838,566 (valid votes), state page 12,892,578 (includes 54,013 blank and invalid) |

### Where the overview and the state page differ only in names, party labels, or the total-row label
These do not change any recorded number. "Turnout row equals overview total" means the state page prints no "Total votes" row.

| Race | Difference |
|---|---|
| 2010 AK | state page prints no "Total votes" row; its "Turnout" row (256,192) equals the overview total |
| 2010 AZ | Jan Brewer (overview) = Janice Kay Brewer (state page); Terry Goddard (overview) = Samuel Pearson Goddard III (state page); state page prints no "Total votes" row; its "Turnout" row (1,728,081) equals the overview total |
| 2010 CO | Paul Fiorino (overview) = Paul Noel Fiorino (state page); state page prints no "Total votes" row; its "Turnout" row (1,793,148) equals the overview total |
| 2014 CO | Paul Fiorino (overview) = Paul Noel Fiorino (state page); state page prints no "Total votes" row; its "Turnout" row (2,041,605) equals the overview total |
| 2018 CO | state page prints no "Total votes" row; its "Turnout" row (2,525,062) equals the overview total |
| 2022 CO | Paul Noel Fiorino (overview) = Paul Noël Fiorino (state page) |
| 2010 CT | party label for Dannel Malloy: overview Democratic, state page Democratic + Working Families |
| 2014 CT | party label for Dannel Malloy: overview Democratic, state page Democratic + Working Families; party label for Thomas C. Foley: overview Republican, state page Republican + Independent Party |
| 2018 CT | party label for Ned Lamont: overview Democratic, state page Democratic + Working Families; party label for Bob Stefanowski: overview Republican, state page Republican + Independent Party; party label for Oz Griebel: overview Independent, state page Griebel-Frank for CT Party; party label for Mark Greenstein: overview Constitution, state page Amigo Constitution Liberty; state page names the 74-vote line "Lee Whitnum"; overview labels it "Write-in" (not a candidate line) |
| 2022 CT | party label for Ned Lamont: overview Democratic, state page Democratic + Working Families + Griebel-Frank for CT |
| 2010 FL | state page prints no "Total votes" row; its "Turnout" row (5,359,735) equals the overview total |
| 2018 FL | Kyle Gibson (overview) = Kyle "KC" Gibson (state page); Ryan C. Foley (overview) = Ryan Christopher Foley (state page) |
| 2010 HI | party label for Daniel Cunningham: overview Free Energy, state page Free Energy Party; party label for Tom Pollard: overview Nonpartisan, state page Independent politician |
| 2010 ID | state page prints no "Total votes" row; its "Turnout" row (452,535) equals the overview total |
| 2014 ID | A. J. Balukoff (overview) = A.J. Balukoff (state page) |
| 2018 ID | Bev Boeck (overview) = Bev "Angel" Boeck (state page) |
| 2018 IL | J. B. Pritzker (overview) = JB Pritzker (state page) |
| 2022 IL | J. B. Pritzker (overview) = JB Pritzker (state page) |
| 2010 IA | party label for Jonathan Narcisse: overview Iowa, state page Iowa Party |
| 2014 IA | Lee Hieb (overview) = Lee Deakins Hieb (state page); party label for Jim Hennager: overview Independent, state page New Independent Party Iowa; Jonathan Narcisse (overview) = Jonathan R. Narcisse (state page); party label for Jonathan Narcisse: overview Independent, state page Iowa |
| 2010 KS | state page prints no "Total votes" row; its "Turnout" row (838,790) equals the overview total |
| 2010 ME | state page prints no "Total votes" row; its "Turnout" row (580,538) equals the overview total |
| 2010 MD | state page prints no "Total votes" row; its "Turnout" row (1,857,880) equals the overview total |
| 2010 MI | Virgil Bernero (overview) = Virg Bernero (state page); state page prints no "Total votes" row; its "Turnout" row (3,226,088) equals the overview total |
| 2010 MN | party label for Linda Eno: overview Resource, state page Resource Party |
| 2014 MN | party label for Chris Wright: overview Grassroots, state page Grassroots—LC |
| 2010 NV | Arthur Forest Lampitt (overview) = Arthur Forest Lampitt, Jr. (state page) |
| 2014 NM | Gary King (overview) = Gary K. King (state page) |
| 2010 OR | state page prints no "Total votes" row; its "Turnout" row (1,453,548) equals the overview total |
| 2010 RI | Frank T. Caprio (overview) = Frank Caprio (state page); Joseph Lusi (overview) = Joeseph Lusi (state page); state page prints no "Total votes" row; its "Turnout" row (342,290) equals the overview total |
| 2014 RI | state page prints no "Total votes" row; its "Turnout" row (324,055) equals the overview total |
| 2018 RI | Luis-Daniel Munoz (overview) = Luis Daniel Muñoz (state page) |
| 2010 SC | state page prints no "Total votes" row; its "Turnout" row (1,344,198) equals the overview total |
| 2010 TN | state page prints no "Total votes" row; its "Turnout" row (1,601,567) equals the overview total |
| 2014 TN | party label for Daniel Lewis: overview Libertarian, state page Independent |
| 2010 TX | state page prints no "Total votes" row; its "Turnout" row (4,979,870) equals the overview total |
| 2014 WI | party label for Robert Burke: overview Libertarian, state page Independent |
| 2018 WI | Maggie Turnbull (overview) = Margaret Turnbull (state page); Michael White (overview) = Michael J. White (state page) |
| 2010 WY | state page prints no "Total votes" row; its "Turnout" row (190,822) equals the overview total |
| 2012 WI | Hariprasad Trivedi (overview) = Hari Trivedi (state page) |
| 2016 OR | party label for Cliff Thomason: overview Independent Party (Oregon), state page Independent Party |

### Overview boxes whose printed total ≠ sum of printed lines
`total_votes` and every % are recorded as printed. The largest gaps are 2010 NY (+111,786; the state page prints 4,657,955) and 2010 ME (+10,396).

- 2022 AL: overview candidate+write-in votes sum 1,415,283 != printed total 1,411,756 (diff -3,527)
- 2014 FL: overview candidate+write-in votes sum 5,951,561 != printed total 5,951,571 (diff 10)
- 2010 HI: overview candidate+write-in votes sum 382,563 != printed total 380,035 (diff -2,528)
- 2010 ME: overview candidate+write-in votes sum 570,142 != printed total 580,538 (diff 10,396)
- 2010 MN: overview candidate+write-in votes sum 2,107,021 != printed total 2,106,979 (diff -42)
- 2022 NE: overview candidate+write-in votes sum 666,785 != printed total 666,795 (diff 10)
- 2010 NM: overview candidate+write-in votes sum 602,827 != printed total 602,832 (diff 5)
- 2010 NY: overview candidate+write-in votes sum 4,657,955 != printed total 4,769,741 (diff 111,786)
- 2014 NY: overview candidate+write-in votes sum 3,818,888 != printed total 3,819,086 (diff 198)
- 2018 OH: overview candidate+write-in votes sum 4,435,689 != printed total 4,429,582 (diff -6,107)
- 2010 TN: overview candidate+write-in votes sum 1,601,549 != printed total 1,601,567 (diff 18)
- 2022 TX: overview candidate+write-in votes sum 8,101,271 != printed total 8,102,908 (diff 1,637)
- 2010 WY: overview candidate+write-in votes sum 188,463 != printed total 190,822 (diff 2,359)

Rows where a printed % differs from votes ÷ printed total by more than 0.06 points. Use the printed % with care in these rows:

- 2010 NY Andrew Cuomo: printed 63.05%, votes/total 61.03%
- 2010 NY Carl Paladino: printed 33.53%, votes/total 32.45%
- 2010 WY Leslie Petersen: printed 22.94%, votes/total 22.66%
- 2010 WY Matt Mead: printed 65.68%, votes/total 64.87%
- 2010 WY Taylor Haynes: printed 7.32%, votes/total 7.23%
- 2018 OH Mike DeWine: printed 50.39%, votes/total 50.47%
- 2022 AL Yolanda Rochelle Flowers: printed 29.18%, votes/total 29.25%
- 2022 AL Kay Ivey: printed 66.91%, votes/total 67.07%
- 2022 VT Phil Scott: printed 70.91%, votes/total 70.98%

## pres_state_2008_2012.csv

Source: FEC *Federal Elections 2008* and *2012*, sheet "Table 2. Electoral & Pop Vote" (popular-vote columns: Obama (D), McCain/Romney (R), All Others, Total Vote). `d_pct`, `r_pct` and `margin` are **derived from these votes** (100·votes/Total Vote); Table 2 prints no state percentages. Checks: D + R + All Others = Total in every state. The state rows sum to the printed national totals. In all 51 rows, Obama, McCain/Romney and Total match the per-candidate sheet "2008/2012 Pres General Results" (NY uses its "Combined Parties" line).

2016, 2020 and 2024 state presidential results are already in the repo and were not duplicated: `backend/data/sources/fec_backtest/pres_2016_by_state.csv` (FEC 2016 Table 2) and `backend/data/state_pres_results.csv` (2020 and 2024, FEC).

## national_margins.csv

`margin` = d_pct − r_pct in percentage points of the total vote; pct values are derived from the printed FEC vote totals. Columns `d_votes, r_votes, total_votes` were added.
- **President** (50 states + DC): FEC Table 2 "Total" rows for 2008, 2012 (this folder), 2016 (`../fec_backtest/federalelections2016.xlsx`), 2020 (`../fec_pres/federalelections2020.xlsx`; the FEC header misspells "Trunp"), and the 2024 official results (`../fec_pres/2024presgeresults.xlsx`).
- **House**: FEC "Table 5. House by Party", general-election Democratic/Republican/Other totals, for 2010 and 2014 (this folder), 2018 (`../fec_backtest/federalelections2018.xlsx`) and 2022 (`../fec_backtest/federalelections2022.xlsx`, sheet "6. Table 5 House by Party"). The 2022 value matches the existing `../fec_backtest/house_national_popular_vote.csv` "all" row (−2.4677). Scope is all 50 states + DC + territories, as printed. The 50-state-only margin is in `notes`. D and R are party-line votes: fusion lines such as NY WF/Conservative count as Other.
- **2014 House correction (flagged)**: Table 5's Nevada row prints R 28,053 / Other 304,809. The same workbook's race-level sheet "2014 US House Results by State" gives NV Republicans 304,809 (Teijeiro 30,413 + Amodei 122,402 + Heck 88,528 + Hardy 63,466) and minor parties 28,053, so Table 5 swapped the two columns for NV. The recorded 2014 row uses R = 40,344,770 (printed 40,068,014). Margin: −5.4520 (printed table gives −5.1027). Both are in `notes`.
- Other Table 5 vs race-level differences (2010 CA/IL/MI/OR, 2014 LA/NJ/NY/OR/MP, 2018 AK/CA/NY/OR) come from party labels: fusion or "DEM/IND"-style labels, Louisiana's December runoff votes added to the 2014 general (per the FEC's own note), and AK 2018, where Galvin is labelled "D(UND)" on the race-level sheet but counted as Democratic in Table 5. They are not errors and were not changed.

| year | office | d_pct | r_pct | margin |
|---|---|---|---|---|
| 2010 | house | 44.8025 | 51.3726 | -6.5701 |
| 2014 | house | 45.4760 | 50.9280 | -5.4520 |
| 2018 | house | 53.2658 | 44.2833 | 8.9825 |
| 2022 | house | 47.7280 | 50.1957 | -2.4677 |
| 2008 | president | 52.9255 | 45.6527 | 7.2728 |
| 2012 | president | 51.0637 | 47.2040 | 3.8597 |
| 2016 | president | 48.1846 | 46.0856 | 2.0990 |
| 2020 | president | 51.3057 | 46.8498 | 4.4559 |
| 2024 | president | 48.3242 | 49.7961 | -1.4719 |

## UNVERIFIED / blank fields
- No value was filled from memory. Every cell is either copied from a saved page or derived as described above.
- `rcv_final_d_pct`, `rcv_final_r_pct`: blank in all rows. For AK 2022, the only RCV race, the pages print no final round (Dunleavy won in round 1).
- `d_*` blank: AK 2014 (no Democrat on the ballot).
- `other_*` blank wherever no non-D/R candidate reached 5%.
- Judgment calls rather than gaps: VT 2020 D assignment, AK 2018 `incumbent_ran`, and the CA 2021 recall mapping (all described above).

## Saved files

All retrieved 2026-10-28 with curl (HTTP 200 for every file). The Wikipedia pages are the standard /wiki/ HTML as served; none was a redirect. FEC xls links redirect to `https://www.fec.gov/resources/cms-content/documents/<file>`. The FEC PDF editions were downloaded too but deleted because they duplicate the Excel files; their URLs are on the saved FEC index pages.

| File | URL | Retrieved (UTC) | Contents |
|---|---|---|---|
| `wikipedia_overview/wikipedia_2010_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2010_United_States_gubernatorial_elections | 2026-10-28T18:26:31Z | Wikipedia "2010 United States gubernatorial elections" (rev 1381848293): race-summary table (incumbent, party, result) and per-state general-election boxes |
| `wikipedia_overview/wikipedia_2012_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2012_United_States_gubernatorial_elections | 2026-10-28T18:26:32Z | Wikipedia "2012 United States gubernatorial elections" (rev 1381848381): race-summary table (incumbent, party, result) and per-state general-election boxes |
| `wikipedia_overview/wikipedia_2014_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2014_United_States_gubernatorial_elections | 2026-10-28T18:26:34Z | Wikipedia "2014 United States gubernatorial elections" (rev 1381849085): race-summary table (incumbent, party, result) and per-state general-election boxes |
| `wikipedia_overview/wikipedia_2016_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2016_United_States_gubernatorial_elections | 2026-10-28T18:26:35Z | Wikipedia "2016 United States gubernatorial elections" (rev 1373406462): race-summary table (incumbent, party, result) and per-state general-election boxes |
| `wikipedia_overview/wikipedia_2018_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2018_United_States_gubernatorial_elections | 2026-10-28T18:26:36Z | Wikipedia "2018 United States gubernatorial elections" (rev 1370818436): race-summary table (incumbent, party, result) and per-state general-election boxes |
| `wikipedia_overview/wikipedia_2020_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2020_United_States_gubernatorial_elections | 2026-10-28T18:26:38Z | Wikipedia "2020 United States gubernatorial elections" (rev 1381789334): race-summary table (incumbent, party, result) and per-state general-election boxes |
| `wikipedia_overview/wikipedia_2022_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2022_United_States_gubernatorial_elections | 2026-10-28T18:26:39Z | Wikipedia "2022 United States gubernatorial elections" (rev 1376686561): race-summary table (incumbent, party, result) and per-state general-election boxes |
| `wikipedia_overview/wikipedia_2024_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2024_United_States_gubernatorial_elections | 2026-10-28T18:26:41Z | Wikipedia "2024 United States gubernatorial elections" (rev 1381789658): race-summary table (incumbent, party, result) and per-state general-election boxes |
| `wikipedia_overview/wikipedia_2021_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2021_United_States_gubernatorial_elections | 2026-10-28T18:27:45Z | Wikipedia "2021 United States gubernatorial elections" (rev 1381849197): race summary and "California (recall)" Yes/No table |
| `wikipedia_state_pages/wikipedia_2010_AL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Alabama_gubernatorial_election | 2026-10-28T18:27:55Z | Wikipedia state page, 2010 AL gubernatorial election (rev 1382382031): cross-check |
| `wikipedia_state_pages/wikipedia_2014_AL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Alabama_gubernatorial_election | 2026-10-28T18:27:57Z | Wikipedia state page, 2014 AL gubernatorial election (rev 1382382223): cross-check |
| `wikipedia_state_pages/wikipedia_2018_AL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Alabama_gubernatorial_election | 2026-10-28T18:27:58Z | Wikipedia state page, 2018 AL gubernatorial election (rev 1382382479): cross-check |
| `wikipedia_state_pages/wikipedia_2022_AL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Alabama_gubernatorial_election | 2026-10-28T18:27:59Z | Wikipedia state page, 2022 AL gubernatorial election (rev 1382382819): cross-check |
| `wikipedia_state_pages/wikipedia_2010_AK_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Alaska_gubernatorial_election | 2026-10-28T18:28:01Z | Wikipedia state page, 2010 AK gubernatorial election (rev 1382385512): cross-check |
| `wikipedia_state_pages/wikipedia_2014_AK_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Alaska_gubernatorial_election | 2026-10-28T18:28:02Z | Wikipedia state page, 2014 AK gubernatorial election (rev 1382385664): cross-check |
| `wikipedia_state_pages/wikipedia_2018_AK_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Alaska_gubernatorial_election | 2026-10-28T18:28:03Z | Wikipedia state page, 2018 AK gubernatorial election (rev 1382385815): cross-check |
| `fec/fec_results_index_page.html` | https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/ | 2026-10-28T18:28:04Z | FEC election results and voting information index page |
| `wikipedia_state_pages/wikipedia_2022_AK_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Alaska_gubernatorial_election | 2026-10-28T18:28:05Z | Wikipedia state page, 2022 AK gubernatorial election (rev 1382385963): cross-check |
| `fec/fec_federal_elections_2008_page.html` | https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/federal-elections-2008/ | 2026-10-28T18:28:05Z | FEC index page for Federal Elections 2008 (links to the xls/pdf) |
| `fec/fec_federal_elections_2010_page.html` | https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/federal-elections-2010/ | 2026-10-28T18:28:06Z | FEC index page for Federal Elections 2010 (links to the xls/pdf) |
| `wikipedia_state_pages/wikipedia_2010_AZ_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Arizona_gubernatorial_election | 2026-10-28T18:28:06Z | Wikipedia state page, 2010 AZ gubernatorial election (rev 1382396490): cross-check |
| `fec/fec_federal_elections_2012_page.html` | https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/federal-elections-2012/ | 2026-10-28T18:28:08Z | FEC index page for Federal Elections 2012 (links to the xls/pdf) |
| `wikipedia_state_pages/wikipedia_2014_AZ_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Arizona_gubernatorial_election | 2026-10-28T18:28:08Z | Wikipedia state page, 2014 AZ gubernatorial election (rev 1382396721): cross-check |
| `fec/fec_federal_elections_2014_page.html` | https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/federal-elections-2014/ | 2026-10-28T18:28:09Z | FEC index page for Federal Elections 2014 (links to the xls/pdf) |
| `wikipedia_state_pages/wikipedia_2018_AZ_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Arizona_gubernatorial_election | 2026-10-28T18:28:09Z | Wikipedia state page, 2018 AZ gubernatorial election (rev 1382396993): cross-check |
| `wikipedia_state_pages/wikipedia_2022_AZ_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Arizona_gubernatorial_election | 2026-10-28T18:28:11Z | Wikipedia state page, 2022 AZ gubernatorial election (rev 1382397328): cross-check |
| `wikipedia_state_pages/wikipedia_2010_AR_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Arkansas_gubernatorial_election | 2026-10-28T18:28:12Z | Wikipedia state page, 2010 AR gubernatorial election (rev 1382403516): cross-check |
| `wikipedia_state_pages/wikipedia_2014_AR_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Arkansas_gubernatorial_election | 2026-10-28T18:28:13Z | Wikipedia state page, 2014 AR gubernatorial election (rev 1382403696): cross-check |
| `wikipedia_state_pages/wikipedia_2018_AR_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Arkansas_gubernatorial_election | 2026-10-28T18:28:15Z | Wikipedia state page, 2018 AR gubernatorial election (rev 1382403874): cross-check |
| `wikipedia_state_pages/wikipedia_2022_AR_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Arkansas_gubernatorial_election | 2026-10-28T18:28:16Z | Wikipedia state page, 2022 AR gubernatorial election (rev 1382404085): cross-check |
| `wikipedia_state_pages/wikipedia_2010_CA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_California_gubernatorial_election | 2026-10-28T18:28:18Z | Wikipedia state page, 2010 CA gubernatorial election (rev 1382411335): cross-check |
| `wikipedia_state_pages/wikipedia_2014_CA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_California_gubernatorial_election | 2026-10-28T18:28:19Z | Wikipedia state page, 2014 CA gubernatorial election (rev 1382411807): cross-check |
| `wikipedia_state_pages/wikipedia_2018_CA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_California_gubernatorial_election | 2026-10-28T18:28:21Z | Wikipedia state page, 2018 CA gubernatorial election (rev 1382412316): cross-check |
| `fec/fec_federalelections2008.xls` | https://www.fec.gov/documents/1666/federalelections2008.xls | 2026-10-28T18:28:22Z | FEC, *Federal Elections 2008* (Excel) |
| `wikipedia_state_pages/wikipedia_2022_CA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_California_gubernatorial_election | 2026-10-28T18:28:22Z | Wikipedia state page, 2022 CA gubernatorial election (rev 1382413055): cross-check |
| `wikipedia_state_pages/wikipedia_2010_CO_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Colorado_gubernatorial_election | 2026-10-28T18:28:24Z | Wikipedia state page, 2010 CO gubernatorial election (rev 1379781100): cross-check |
| `wikipedia_state_pages/wikipedia_2014_CO_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Colorado_gubernatorial_election | 2026-10-28T18:28:25Z | Wikipedia state page, 2014 CO gubernatorial election (rev 1371851910): cross-check |
| `fec/fec_federalelections2010.xls` | https://www.fec.gov/documents/1675/federalelections2010.xls | 2026-10-28T18:28:25Z | FEC, *Federal Elections 2010* (Excel) |
| `wikipedia_state_pages/wikipedia_2018_CO_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Colorado_gubernatorial_election | 2026-10-28T18:28:26Z | Wikipedia state page, 2018 CO gubernatorial election (rev 1375744470): cross-check |
| `wikipedia_state_pages/wikipedia_2022_CO_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Colorado_gubernatorial_election | 2026-10-28T18:28:28Z | Wikipedia state page, 2022 CO gubernatorial election (rev 1376428797): cross-check |
| `fec/fec_federalelections2012.xls` | https://www.fec.gov/documents/1691/federalelections2012.xls | 2026-10-28T18:28:28Z | FEC, *Federal Elections 2012* (Excel) |
| `wikipedia_state_pages/wikipedia_2010_CT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Connecticut_gubernatorial_election | 2026-10-28T18:28:29Z | Wikipedia state page, 2010 CT gubernatorial election (rev 1369952845): cross-check |
| `wikipedia_state_pages/wikipedia_2014_CT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Connecticut_gubernatorial_election | 2026-10-28T18:28:31Z | Wikipedia state page, 2014 CT gubernatorial election (rev 1378397336): cross-check |
| `fec/fec_federalelections2014.xls` | https://www.fec.gov/documents/1700/federalelections2014.xls | 2026-10-28T18:28:31Z | FEC, *Federal Elections 2014* (Excel) |
| `wikipedia_state_pages/wikipedia_2018_CT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Connecticut_gubernatorial_election | 2026-10-28T18:28:32Z | Wikipedia state page, 2018 CT gubernatorial election (rev 1374165777): cross-check |
| `wikipedia_state_pages/wikipedia_2022_CT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Connecticut_gubernatorial_election | 2026-10-28T18:28:33Z | Wikipedia state page, 2022 CT gubernatorial election (rev 1380485714): cross-check |
| `wikipedia_state_pages/wikipedia_2010_FL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Florida_gubernatorial_election | 2026-10-28T18:28:35Z | Wikipedia state page, 2010 FL gubernatorial election (rev 1378530013): cross-check |
| `wikipedia_state_pages/wikipedia_2014_FL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Florida_gubernatorial_election | 2026-10-28T18:28:36Z | Wikipedia state page, 2014 FL gubernatorial election (rev 1378339435): cross-check |
| `wikipedia_state_pages/wikipedia_2018_FL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Florida_gubernatorial_election | 2026-10-28T18:28:37Z | Wikipedia state page, 2018 FL gubernatorial election (rev 1381312943): cross-check |
| `wikipedia_state_pages/wikipedia_2022_FL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Florida_gubernatorial_election | 2026-10-28T18:28:39Z | Wikipedia state page, 2022 FL gubernatorial election (rev 1382245274): cross-check |
| `wikipedia_state_pages/wikipedia_2010_GA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Georgia_gubernatorial_election | 2026-10-28T18:28:40Z | Wikipedia state page, 2010 GA gubernatorial election (rev 1372514392): cross-check |
| `wikipedia_state_pages/wikipedia_2014_GA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Georgia_gubernatorial_election | 2026-10-28T18:28:42Z | Wikipedia state page, 2014 GA gubernatorial election (rev 1371901081): cross-check |
| `wikipedia_state_pages/wikipedia_2018_GA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Georgia_gubernatorial_election | 2026-10-28T18:28:43Z | Wikipedia state page, 2018 GA gubernatorial election (rev 1379206226): cross-check |
| `wikipedia_state_pages/wikipedia_2022_GA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Georgia_gubernatorial_election | 2026-10-28T18:28:44Z | Wikipedia state page, 2022 GA gubernatorial election (rev 1381364047): cross-check |
| `wikipedia_state_pages/wikipedia_2010_HI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Hawaii_gubernatorial_election | 2026-10-28T18:28:46Z | Wikipedia state page, 2010 HI gubernatorial election (rev 1381054388): cross-check |
| `wikipedia_state_pages/wikipedia_2014_HI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Hawaii_gubernatorial_election | 2026-10-28T18:28:47Z | Wikipedia state page, 2014 HI gubernatorial election (rev 1381054482): cross-check |
| `wikipedia_state_pages/wikipedia_2018_HI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Hawaii_gubernatorial_election | 2026-10-28T18:28:48Z | Wikipedia state page, 2018 HI gubernatorial election (rev 1381054559): cross-check |
| `wikipedia_state_pages/wikipedia_2022_HI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Hawaii_gubernatorial_election | 2026-10-28T18:28:50Z | Wikipedia state page, 2022 HI gubernatorial election (rev 1381054637): cross-check |
| `wikipedia_state_pages/wikipedia_2010_ID_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Idaho_gubernatorial_election | 2026-10-28T18:28:51Z | Wikipedia state page, 2010 ID gubernatorial election (rev 1379207371): cross-check |
| `wikipedia_state_pages/wikipedia_2014_ID_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Idaho_gubernatorial_election | 2026-10-28T18:28:52Z | Wikipedia state page, 2014 ID gubernatorial election (rev 1371942246): cross-check |
| `wikipedia_state_pages/wikipedia_2018_ID_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Idaho_gubernatorial_election | 2026-10-28T18:28:54Z | Wikipedia state page, 2018 ID gubernatorial election (rev 1380748655): cross-check |
| `wikipedia_state_pages/wikipedia_2022_ID_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Idaho_gubernatorial_election | 2026-10-28T18:28:55Z | Wikipedia state page, 2022 ID gubernatorial election (rev 1371443614): cross-check |
| `wikipedia_state_pages/wikipedia_2010_IL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Illinois_gubernatorial_election | 2026-10-28T18:28:57Z | Wikipedia state page, 2010 IL gubernatorial election (rev 1376956736): cross-check |
| `wikipedia_state_pages/wikipedia_2014_IL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Illinois_gubernatorial_election | 2026-10-28T18:28:58Z | Wikipedia state page, 2014 IL gubernatorial election (rev 1382006849): cross-check |
| `wikipedia_state_pages/wikipedia_2018_IL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Illinois_gubernatorial_election | 2026-10-28T18:28:59Z | Wikipedia state page, 2018 IL gubernatorial election (rev 1381666098): cross-check |
| `wikipedia_state_pages/wikipedia_2022_IL_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Illinois_gubernatorial_election | 2026-10-28T18:29:01Z | Wikipedia state page, 2022 IL gubernatorial election (rev 1376490781): cross-check |
| `wikipedia_state_pages/wikipedia_2010_IA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Iowa_gubernatorial_election | 2026-10-28T18:29:02Z | Wikipedia state page, 2010 IA gubernatorial election (rev 1376216698): cross-check |
| `wikipedia_state_pages/wikipedia_2014_IA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Iowa_gubernatorial_election | 2026-10-28T18:29:03Z | Wikipedia state page, 2014 IA gubernatorial election (rev 1380317233): cross-check |
| `wikipedia_state_pages/wikipedia_2018_IA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Iowa_gubernatorial_election | 2026-10-28T18:29:05Z | Wikipedia state page, 2018 IA gubernatorial election (rev 1375966807): cross-check |
| `wikipedia_state_pages/wikipedia_2022_IA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Iowa_gubernatorial_election | 2026-10-28T18:29:06Z | Wikipedia state page, 2022 IA gubernatorial election (rev 1364041656): cross-check |
| `wikipedia_state_pages/wikipedia_2010_KS_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Kansas_gubernatorial_election | 2026-10-28T18:29:07Z | Wikipedia state page, 2010 KS gubernatorial election (rev 1377164401): cross-check |
| `wikipedia_state_pages/wikipedia_2014_KS_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Kansas_gubernatorial_election | 2026-10-28T18:29:09Z | Wikipedia state page, 2014 KS gubernatorial election (rev 1379782017): cross-check |
| `wikipedia_state_pages/wikipedia_2018_KS_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Kansas_gubernatorial_election | 2026-10-28T18:29:10Z | Wikipedia state page, 2018 KS gubernatorial election (rev 1379952974): cross-check |
| `wikipedia_state_pages/wikipedia_2022_KS_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Kansas_gubernatorial_election | 2026-10-28T18:29:11Z | Wikipedia state page, 2022 KS gubernatorial election (rev 1382407969): cross-check |
| `wikipedia_state_pages/wikipedia_2010_ME_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Maine_gubernatorial_election | 2026-10-28T18:29:13Z | Wikipedia state page, 2010 ME gubernatorial election (rev 1381233152): cross-check |
| `wikipedia_state_pages/wikipedia_2014_ME_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Maine_gubernatorial_election | 2026-10-28T18:29:14Z | Wikipedia state page, 2014 ME gubernatorial election (rev 1374235509): cross-check |
| `wikipedia_state_pages/wikipedia_2018_ME_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Maine_gubernatorial_election | 2026-10-28T18:29:16Z | Wikipedia state page, 2018 ME gubernatorial election (rev 1374228534): cross-check |
| `wikipedia_state_pages/wikipedia_2022_ME_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Maine_gubernatorial_election | 2026-10-28T18:29:17Z | Wikipedia state page, 2022 ME gubernatorial election (rev 1380532403): cross-check |
| `wikipedia_state_pages/wikipedia_2010_MD_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Maryland_gubernatorial_election | 2026-10-28T18:29:18Z | Wikipedia state page, 2010 MD gubernatorial election (rev 1372481052): cross-check |
| `wikipedia_state_pages/wikipedia_2014_MD_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Maryland_gubernatorial_election | 2026-10-28T18:29:20Z | Wikipedia state page, 2014 MD gubernatorial election (rev 1376275653): cross-check |
| `wikipedia_state_pages/wikipedia_2018_MD_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Maryland_gubernatorial_election | 2026-10-28T18:29:21Z | Wikipedia state page, 2018 MD gubernatorial election (rev 1374231916): cross-check |
| `wikipedia_state_pages/wikipedia_2022_MD_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Maryland_gubernatorial_election | 2026-10-28T18:29:22Z | Wikipedia state page, 2022 MD gubernatorial election (rev 1381841723): cross-check |
| `wikipedia_state_pages/wikipedia_2010_MA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Massachusetts_gubernatorial_election | 2026-10-28T18:29:24Z | Wikipedia state page, 2010 MA gubernatorial election (rev 1370039518): cross-check |
| `wikipedia_state_pages/wikipedia_2014_MA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Massachusetts_gubernatorial_election | 2026-10-28T18:29:25Z | Wikipedia state page, 2014 MA gubernatorial election (rev 1380434705): cross-check |
| `wikipedia_state_pages/wikipedia_2018_MA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Massachusetts_gubernatorial_election | 2026-10-28T18:29:26Z | Wikipedia state page, 2018 MA gubernatorial election (rev 1375585813): cross-check |
| `wikipedia_state_pages/wikipedia_2022_MA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Massachusetts_gubernatorial_election | 2026-10-28T18:29:28Z | Wikipedia state page, 2022 MA gubernatorial election (rev 1376541438): cross-check |
| `wikipedia_state_pages/wikipedia_2010_MI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Michigan_gubernatorial_election | 2026-10-28T18:29:29Z | Wikipedia state page, 2010 MI gubernatorial election (rev 1370043140): cross-check |
| `wikipedia_state_pages/wikipedia_2014_MI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Michigan_gubernatorial_election | 2026-10-28T18:29:31Z | Wikipedia state page, 2014 MI gubernatorial election (rev 1381387777): cross-check |
| `wikipedia_state_pages/wikipedia_2018_MI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Michigan_gubernatorial_election | 2026-10-28T18:29:32Z | Wikipedia state page, 2018 MI gubernatorial election (rev 1382248710): cross-check |
| `wikipedia_state_pages/wikipedia_2022_MI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Michigan_gubernatorial_election | 2026-10-28T18:29:33Z | Wikipedia state page, 2022 MI gubernatorial election (rev 1381008519): cross-check |
| `wikipedia_state_pages/wikipedia_2010_MN_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Minnesota_gubernatorial_election | 2026-10-28T18:29:35Z | Wikipedia state page, 2010 MN gubernatorial election (rev 1376991888): cross-check |
| `wikipedia_state_pages/wikipedia_2014_MN_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Minnesota_gubernatorial_election | 2026-10-28T18:29:36Z | Wikipedia state page, 2014 MN gubernatorial election (rev 1373293439): cross-check |
| `wikipedia_state_pages/wikipedia_2018_MN_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Minnesota_gubernatorial_election | 2026-10-28T18:29:37Z | Wikipedia state page, 2018 MN gubernatorial election (rev 1381307446): cross-check |
| `wikipedia_state_pages/wikipedia_2022_MN_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Minnesota_gubernatorial_election | 2026-10-28T18:29:39Z | Wikipedia state page, 2022 MN gubernatorial election (rev 1380277150): cross-check |
| `wikipedia_state_pages/wikipedia_2010_NE_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Nebraska_gubernatorial_election | 2026-10-28T18:29:40Z | Wikipedia state page, 2010 NE gubernatorial election (rev 1369379615): cross-check |
| `wikipedia_state_pages/wikipedia_2014_NE_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Nebraska_gubernatorial_election | 2026-10-28T18:29:42Z | Wikipedia state page, 2014 NE gubernatorial election (rev 1372014369): cross-check |
| `wikipedia_state_pages/wikipedia_2018_NE_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Nebraska_gubernatorial_election | 2026-10-28T18:29:43Z | Wikipedia state page, 2018 NE gubernatorial election (rev 1374256124): cross-check |
| `wikipedia_state_pages/wikipedia_2022_NE_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Nebraska_gubernatorial_election | 2026-10-28T18:29:45Z | Wikipedia state page, 2022 NE gubernatorial election (rev 1380992852): cross-check |
| `wikipedia_state_pages/wikipedia_2010_NV_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Nevada_gubernatorial_election | 2026-10-28T18:29:46Z | Wikipedia state page, 2010 NV gubernatorial election (rev 1376210836): cross-check |
| `wikipedia_state_pages/wikipedia_2014_NV_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Nevada_gubernatorial_election | 2026-10-28T18:29:47Z | Wikipedia state page, 2014 NV gubernatorial election (rev 1378745092): cross-check |
| `wikipedia_state_pages/wikipedia_2018_NV_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Nevada_gubernatorial_election | 2026-10-28T18:29:49Z | Wikipedia state page, 2018 NV gubernatorial election (rev 1378745015): cross-check |
| `wikipedia_state_pages/wikipedia_2022_NV_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Nevada_gubernatorial_election | 2026-10-28T18:29:50Z | Wikipedia state page, 2022 NV gubernatorial election (rev 1382032305): cross-check |
| `wikipedia_state_pages/wikipedia_2012_NH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2012_New_Hampshire_gubernatorial_election | 2026-10-28T18:29:51Z | Wikipedia state page, 2012 NH gubernatorial election (rev 1371079142): cross-check |
| `wikipedia_state_pages/wikipedia_2014_NH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_New_Hampshire_gubernatorial_election | 2026-10-28T18:29:53Z | Wikipedia state page, 2014 NH gubernatorial election (rev 1371750073): cross-check |
| `wikipedia_state_pages/wikipedia_2016_NH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2016_New_Hampshire_gubernatorial_election | 2026-10-28T18:29:54Z | Wikipedia state page, 2016 NH gubernatorial election (rev 1373280249): cross-check |
| `wikipedia_state_pages/wikipedia_2018_NH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_New_Hampshire_gubernatorial_election | 2026-10-28T18:29:55Z | Wikipedia state page, 2018 NH gubernatorial election (rev 1378399867): cross-check |
| `wikipedia_state_pages/wikipedia_2020_NH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2020_New_Hampshire_gubernatorial_election | 2026-10-28T18:29:57Z | Wikipedia state page, 2020 NH gubernatorial election (rev 1378505805): cross-check |
| `wikipedia_state_pages/wikipedia_2022_NH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_New_Hampshire_gubernatorial_election | 2026-10-28T18:29:58Z | Wikipedia state page, 2022 NH gubernatorial election (rev 1378378124): cross-check |
| `wikipedia_state_pages/wikipedia_2024_NH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2024_New_Hampshire_gubernatorial_election | 2026-10-28T18:29:59Z | Wikipedia state page, 2024 NH gubernatorial election (rev 1380248293): cross-check |
| `wikipedia_state_pages/wikipedia_2010_NM_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_New_Mexico_gubernatorial_election | 2026-10-28T18:30:01Z | Wikipedia state page, 2010 NM gubernatorial election (rev 1372576062): cross-check |
| `wikipedia_state_pages/wikipedia_2014_NM_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_New_Mexico_gubernatorial_election | 2026-10-28T18:30:02Z | Wikipedia state page, 2014 NM gubernatorial election (rev 1378532953): cross-check |
| `wikipedia_state_pages/wikipedia_2018_NM_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_New_Mexico_gubernatorial_election | 2026-10-28T18:30:04Z | Wikipedia state page, 2018 NM gubernatorial election (rev 1374257581): cross-check |
| `wikipedia_state_pages/wikipedia_2022_NM_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_New_Mexico_gubernatorial_election | 2026-10-28T18:30:05Z | Wikipedia state page, 2022 NM gubernatorial election (rev 1378391261): cross-check |
| `wikipedia_state_pages/wikipedia_2010_NY_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_New_York_gubernatorial_election | 2026-10-28T18:30:06Z | Wikipedia state page, 2010 NY gubernatorial election (rev 1370520858): cross-check |
| `wikipedia_state_pages/wikipedia_2014_NY_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_New_York_gubernatorial_election | 2026-10-28T18:30:08Z | Wikipedia state page, 2014 NY gubernatorial election (rev 1379325902): cross-check |
| `wikipedia_state_pages/wikipedia_2018_NY_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_New_York_gubernatorial_election | 2026-10-28T18:30:09Z | Wikipedia state page, 2018 NY gubernatorial election (rev 1378259220): cross-check |
| `wikipedia_state_pages/wikipedia_2022_NY_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_New_York_gubernatorial_election | 2026-10-28T18:30:11Z | Wikipedia state page, 2022 NY gubernatorial election (rev 1378960405): cross-check |
| `wikipedia_state_pages/wikipedia_2010_OH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Ohio_gubernatorial_election | 2026-10-28T18:30:12Z | Wikipedia state page, 2010 OH gubernatorial election (rev 1381534309): cross-check |
| `wikipedia_state_pages/wikipedia_2014_OH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Ohio_gubernatorial_election | 2026-10-28T18:30:13Z | Wikipedia state page, 2014 OH gubernatorial election (rev 1381008473): cross-check |
| `wikipedia_state_pages/wikipedia_2018_OH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Ohio_gubernatorial_election | 2026-10-28T18:30:15Z | Wikipedia state page, 2018 OH gubernatorial election (rev 1381007736): cross-check |
| `wikipedia_state_pages/wikipedia_2022_OH_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Ohio_gubernatorial_election | 2026-10-28T18:30:16Z | Wikipedia state page, 2022 OH gubernatorial election (rev 1381753188): cross-check |
| `wikipedia_state_pages/wikipedia_2010_OK_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Oklahoma_gubernatorial_election | 2026-10-28T18:30:17Z | Wikipedia state page, 2010 OK gubernatorial election (rev 1381816277): cross-check |
| `wikipedia_state_pages/wikipedia_2014_OK_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Oklahoma_gubernatorial_election | 2026-10-28T18:30:19Z | Wikipedia state page, 2014 OK gubernatorial election (rev 1380816793): cross-check |
| `wikipedia_state_pages/wikipedia_2018_OK_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Oklahoma_gubernatorial_election | 2026-10-28T18:30:20Z | Wikipedia state page, 2018 OK gubernatorial election (rev 1373043908): cross-check |
| `wikipedia_state_pages/wikipedia_2022_OK_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Oklahoma_gubernatorial_election | 2026-10-28T18:30:22Z | Wikipedia state page, 2022 OK gubernatorial election (rev 1379310064): cross-check |
| `wikipedia_state_pages/wikipedia_2010_OR_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Oregon_gubernatorial_election | 2026-10-28T18:30:23Z | Wikipedia state page, 2010 OR gubernatorial election (rev 1377318881): cross-check |
| `wikipedia_state_pages/wikipedia_2014_OR_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Oregon_gubernatorial_election | 2026-10-28T18:30:25Z | Wikipedia state page, 2014 OR gubernatorial election (rev 1372036895): cross-check |
| `wikipedia_state_pages/wikipedia_2018_OR_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Oregon_gubernatorial_election | 2026-10-28T18:30:26Z | Wikipedia state page, 2018 OR gubernatorial election (rev 1378671199): cross-check |
| `wikipedia_state_pages/wikipedia_2022_OR_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Oregon_gubernatorial_election | 2026-10-28T18:30:27Z | Wikipedia state page, 2022 OR gubernatorial election (rev 1376594834): cross-check |
| `wikipedia_state_pages/wikipedia_2010_PA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Pennsylvania_gubernatorial_election | 2026-10-28T18:30:29Z | Wikipedia state page, 2010 PA gubernatorial election (rev 1374459498): cross-check |
| `wikipedia_state_pages/wikipedia_2014_PA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Pennsylvania_gubernatorial_election | 2026-10-28T18:30:30Z | Wikipedia state page, 2014 PA gubernatorial election (rev 1379572757): cross-check |
| `wikipedia_state_pages/wikipedia_2018_PA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Pennsylvania_gubernatorial_election | 2026-10-28T18:30:32Z | Wikipedia state page, 2018 PA gubernatorial election (rev 1381819442): cross-check |
| `wikipedia_state_pages/wikipedia_2022_PA_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Pennsylvania_gubernatorial_election | 2026-10-28T18:30:33Z | Wikipedia state page, 2022 PA gubernatorial election (rev 1378353469): cross-check |
| `wikipedia_state_pages/wikipedia_2010_RI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Rhode_Island_gubernatorial_election | 2026-10-28T18:30:34Z | Wikipedia state page, 2010 RI gubernatorial election (rev 1378384297): cross-check |
| `wikipedia_state_pages/wikipedia_2014_RI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Rhode_Island_gubernatorial_election | 2026-10-28T18:30:36Z | Wikipedia state page, 2014 RI gubernatorial election (rev 1369739768): cross-check |
| `wikipedia_state_pages/wikipedia_2018_RI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Rhode_Island_gubernatorial_election | 2026-10-28T18:30:37Z | Wikipedia state page, 2018 RI gubernatorial election (rev 1380143383): cross-check |
| `wikipedia_state_pages/wikipedia_2022_RI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Rhode_Island_gubernatorial_election | 2026-10-28T18:30:38Z | Wikipedia state page, 2022 RI gubernatorial election (rev 1376620270): cross-check |
| `wikipedia_state_pages/wikipedia_2010_SC_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_South_Carolina_gubernatorial_election | 2026-10-28T18:30:40Z | Wikipedia state page, 2010 SC gubernatorial election (rev 1378908061): cross-check |
| `wikipedia_state_pages/wikipedia_2014_SC_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_South_Carolina_gubernatorial_election | 2026-10-28T18:30:41Z | Wikipedia state page, 2014 SC gubernatorial election (rev 1336969906): cross-check |
| `wikipedia_state_pages/wikipedia_2018_SC_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_South_Carolina_gubernatorial_election | 2026-10-28T18:30:42Z | Wikipedia state page, 2018 SC gubernatorial election (rev 1380624957): cross-check |
| `wikipedia_state_pages/wikipedia_2022_SC_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_South_Carolina_gubernatorial_election | 2026-10-28T18:30:44Z | Wikipedia state page, 2022 SC gubernatorial election (rev 1376630518): cross-check |
| `wikipedia_state_pages/wikipedia_2010_SD_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_South_Dakota_gubernatorial_election | 2026-10-28T18:30:45Z | Wikipedia state page, 2010 SD gubernatorial election (rev 1380752259): cross-check |
| `wikipedia_state_pages/wikipedia_2014_SD_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_South_Dakota_gubernatorial_election | 2026-10-28T18:30:46Z | Wikipedia state page, 2014 SD gubernatorial election (rev 1369401408): cross-check |
| `wikipedia_state_pages/wikipedia_2018_SD_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_South_Dakota_gubernatorial_election | 2026-10-28T18:30:48Z | Wikipedia state page, 2018 SD gubernatorial election (rev 1379993578): cross-check |
| `wikipedia_state_pages/wikipedia_2022_SD_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_South_Dakota_gubernatorial_election | 2026-10-28T18:30:49Z | Wikipedia state page, 2022 SD gubernatorial election (rev 1376630811): cross-check |
| `wikipedia_state_pages/wikipedia_2010_TN_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Tennessee_gubernatorial_election | 2026-10-28T18:30:50Z | Wikipedia state page, 2010 TN gubernatorial election (rev 1381533366): cross-check |
| `wikipedia_state_pages/wikipedia_2014_TN_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Tennessee_gubernatorial_election | 2026-10-28T18:30:52Z | Wikipedia state page, 2014 TN gubernatorial election (rev 1379606478): cross-check |
| `wikipedia_state_pages/wikipedia_2018_TN_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Tennessee_gubernatorial_election | 2026-10-28T18:30:53Z | Wikipedia state page, 2018 TN gubernatorial election (rev 1380080699): cross-check |
| `wikipedia_state_pages/wikipedia_2022_TN_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Tennessee_gubernatorial_election | 2026-10-28T18:30:55Z | Wikipedia state page, 2022 TN gubernatorial election (rev 1379606393): cross-check |
| `wikipedia_state_pages/wikipedia_2010_TX_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Texas_gubernatorial_election | 2026-10-28T18:30:56Z | Wikipedia state page, 2010 TX gubernatorial election (rev 1374542414): cross-check |
| `wikipedia_state_pages/wikipedia_2014_TX_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Texas_gubernatorial_election | 2026-10-28T18:30:57Z | Wikipedia state page, 2014 TX gubernatorial election (rev 1379198982): cross-check |
| `wikipedia_state_pages/wikipedia_2018_TX_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Texas_gubernatorial_election | 2026-10-28T18:30:59Z | Wikipedia state page, 2018 TX gubernatorial election (rev 1379198411): cross-check |
| `wikipedia_state_pages/wikipedia_2022_TX_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Texas_gubernatorial_election | 2026-10-28T18:31:00Z | Wikipedia state page, 2022 TX gubernatorial election (rev 1382036263): cross-check |
| `wikipedia_state_pages/wikipedia_2012_VT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2012_Vermont_gubernatorial_election | 2026-10-28T18:31:01Z | Wikipedia state page, 2012 VT gubernatorial election (rev 1371226113): cross-check |
| `wikipedia_state_pages/wikipedia_2014_VT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Vermont_gubernatorial_election | 2026-10-28T18:31:03Z | Wikipedia state page, 2014 VT gubernatorial election (rev 1382308791): cross-check |
| `wikipedia_state_pages/wikipedia_2016_VT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2016_Vermont_gubernatorial_election | 2026-10-28T18:31:04Z | Wikipedia state page, 2016 VT gubernatorial election (rev 1373415431): cross-check |
| `wikipedia_state_pages/wikipedia_2018_VT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Vermont_gubernatorial_election | 2026-10-28T18:31:05Z | Wikipedia state page, 2018 VT gubernatorial election (rev 1379079826): cross-check |
| `wikipedia_state_pages/wikipedia_2020_VT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2020_Vermont_gubernatorial_election | 2026-10-28T18:31:07Z | Wikipedia state page, 2020 VT gubernatorial election (rev 1379387841): cross-check |
| `wikipedia_state_pages/wikipedia_2022_VT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Vermont_gubernatorial_election | 2026-10-28T18:31:08Z | Wikipedia state page, 2022 VT gubernatorial election (rev 1370494663): cross-check |
| `wikipedia_state_pages/wikipedia_2024_VT_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2024_Vermont_gubernatorial_election | 2026-10-28T18:31:09Z | Wikipedia state page, 2024 VT gubernatorial election (rev 1377942284): cross-check |
| `wikipedia_state_pages/wikipedia_2010_WI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Wisconsin_gubernatorial_election | 2026-10-28T18:31:11Z | Wikipedia state page, 2010 WI gubernatorial election (rev 1380317957): cross-check |
| `wikipedia_state_pages/wikipedia_2014_WI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Wisconsin_gubernatorial_election | 2026-10-28T18:31:12Z | Wikipedia state page, 2014 WI gubernatorial election (rev 1376686252): cross-check |
| `wikipedia_state_pages/wikipedia_2018_WI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Wisconsin_gubernatorial_election | 2026-10-28T18:31:14Z | Wikipedia state page, 2018 WI gubernatorial election (rev 1377333939): cross-check |
| `wikipedia_state_pages/wikipedia_2022_WI_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Wisconsin_gubernatorial_election | 2026-10-28T18:31:15Z | Wikipedia state page, 2022 WI gubernatorial election (rev 1378121230): cross-check |
| `wikipedia_state_pages/wikipedia_2010_WY_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2010_Wyoming_gubernatorial_election | 2026-10-28T18:31:16Z | Wikipedia state page, 2010 WY gubernatorial election (rev 1378387823): cross-check |
| `wikipedia_state_pages/wikipedia_2014_WY_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2014_Wyoming_gubernatorial_election | 2026-10-28T18:31:18Z | Wikipedia state page, 2014 WY gubernatorial election (rev 1372164520): cross-check |
| `wikipedia_state_pages/wikipedia_2018_WY_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2018_Wyoming_gubernatorial_election | 2026-10-28T18:31:19Z | Wikipedia state page, 2018 WY gubernatorial election (rev 1374386773): cross-check |
| `wikipedia_state_pages/wikipedia_2022_WY_gubernatorial_election.html` | https://en.wikipedia.org/wiki/2022_Wyoming_gubernatorial_election | 2026-10-28T18:31:21Z | Wikipedia state page, 2022 WY gubernatorial election (rev 1376456133): cross-check |
| `wikipedia_state_pages/wikipedia_2016_OR_gubernatorial_special_election.html` | https://en.wikipedia.org/wiki/2016_Oregon_gubernatorial_special_election | 2026-10-28T18:31:22Z | Wikipedia state page, 2016 OR gubernatorial special election (rev 1382342405): cross-check |
| `wikipedia_state_pages/wikipedia_2012_WI_gubernatorial_recall_election.html` | https://en.wikipedia.org/wiki/2012_Wisconsin_gubernatorial_recall_election | 2026-10-28T18:31:23Z | Wikipedia state page, 2012 WI gubernatorial recall election (rev 1378397852): cross-check |
| `wikipedia_state_pages/wikipedia_2021_CA_gubernatorial_recall_election.html` | https://en.wikipedia.org/wiki/2021_California_gubernatorial_recall_election | 2026-10-28T18:31:25Z | Wikipedia state page, 2021 CA gubernatorial recall election (rev 1382412956): cross-check |
| `wikipedia_overview/wikipedia_2011_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2011_United_States_gubernatorial_elections | 2026-10-28T18:44:43Z | Wikipedia "2011 United States gubernatorial elections" (rev 1381849021): checked only for special/recall elections in the 36 states (none found) |
| `wikipedia_overview/wikipedia_2013_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2013_United_States_gubernatorial_elections | 2026-10-28T18:44:44Z | Wikipedia "2013 United States gubernatorial elections" (rev 1381849055): checked only for special/recall elections in the 36 states (none found) |
| `wikipedia_overview/wikipedia_2015_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2015_United_States_gubernatorial_elections | 2026-10-28T18:44:46Z | Wikipedia "2015 United States gubernatorial elections" (rev 1381849154): checked only for special/recall elections in the 36 states (none found) |
| `wikipedia_overview/wikipedia_2017_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2017_United_States_gubernatorial_elections | 2026-10-28T18:44:47Z | Wikipedia "2017 United States gubernatorial elections" (rev 1348899530): checked only for special/recall elections in the 36 states (none found) |
| `wikipedia_overview/wikipedia_2019_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2019_United_States_gubernatorial_elections | 2026-10-28T18:44:49Z | Wikipedia "2019 United States gubernatorial elections" (rev 1371294260): checked only for special/recall elections in the 36 states (none found) |
| `wikipedia_overview/wikipedia_2023_us_gubernatorial_elections.html` | https://en.wikipedia.org/wiki/2023_United_States_gubernatorial_elections | 2026-10-28T18:44:50Z | Wikipedia "2023 United States gubernatorial elections" (rev 1371051437): checked only for special/recall elections in the 36 states (none found) |

Existing repo files used (not modified): `../fec_backtest/federalelections2016.xlsx`, `../fec_backtest/federalelections2018.xlsx`, `../fec_backtest/federalelections2022.xlsx`, `../fec_pres/federalelections2020.xlsx`, `../fec_pres/2024presgeresults.xlsx` (URLs in `../fec_backtest/README.md` and `../SOURCES.md`).
