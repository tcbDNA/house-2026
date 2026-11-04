# Alaska 2026 general: ranked-choice tabulation of the Cast Vote Record — not used by the model

Reference/analysis only. These files are never read by the House, Senate or governor models.

## Downloads (Alaska Division of Elections)

All 2026 files were retrieved 2026-11-04 14:35–14:36 UTC. The 2024 files were retrieved at 14:36–14:37 UTC, and the law pages at 14:39 UTC.

The Division's server sends an incomplete certificate chain: it sends GlobalSign's "RSA OV SSL CA 2018" in place of the issuer of its certificate. Connections were verified with that issuer, "GlobalSign GCC R46 OV TLS CA 2025", fetched from the certificate's own Authority Information Access URL (http://secure.globalsign.com/cacert/gsgccr46ovtlsca2025.crt) and added to the system bundle. Verification was not turned off.

| File | URL | Notes |
|---|---|---|
| `doe_2026-11-04/election-results_page_2026-11-04.html` | https://www.elections.alaska.gov/election-results/ | "Page last updated November 4, 2026 at 2:45 am". The RCV rules ("Sample RCV Report & Definitions") and the CVR notes are both on this page. |
| *(not committed)* `CVR_Export.zip` | https://www.elections.alaska.gov/enr/26GENR/results/CVR_Export.zip | Last-Modified Wed, 04 Nov 2026 11:42:46 GMT; 29,966,829 bytes; sha256 `d6b819f7157bb5153968e67dd0dc0cb625293e81ee4b106886a88ec98d73c6eb`. Dominion export 5.17.18.1 with one record per ballot (`CvrExport.json`, 953,544,057 bytes, 204,530 ballots). It is kept local because it is ballot-level. The manifests used for candidate and contest names are committed as `doe_2026-11-04/cvr_*Manifest.json`. |
| `doe_2026-11-04/ElectionSummaryReportRPT_2026-11-04.pdf` | https://www.elections.alaska.gov/enr/26GENR/results/ElectionSummaryReportRPT.pdf | Stamped 11/4/2026 2:19:06 AM. 215,335 ballots cast; 394 of 401 precincts reported; first choices only. |
| `doe_2026-11-04/GA_ENR_Precinct_State_of_Alaska_2026-11-04.csv` | https://www.elections.alaska.gov/enr/26GENR/results/GA_ENR_Precinct_State_of_Alaska.csv | Last-Modified 11:43:00 GMT. First choices by precinct and counting group (215,335 ballots). |
| `doe_2024_validation/RCV-*.pdf`, `ElectionSummaryReport.pdf`, `election-results_24genr_page.html` | https://www.elections.alaska.gov/results/24GENR/RCV-USRep.pdf (and `RCV-HD6`, `RCV-HD36`, `RCV-HD40`, `RCV-SenD`, `RCV-SenF`, `RCV-SenL`); page https://www.elections.alaska.gov/election-results/e/?id=24genr | The Division's official 2024 RCV Detailed Reports (11/30/2024), used to test the tabulator. |
| *(not committed)* 2024 `CVR_Export_20241130154411.zip` | https://www.elections.alaska.gov/results/24GENR/CVR_Export_20241130154411.zip | 43,712,184 bytes; sha256 `368676629e46ad88199f145ce38c0b7c2edc930e70c6a3da70394ad5cbfb9b24`; 340,778 ballots. |
| `law/akleg_statute_15.15.350.html` | https://www.akleg.gov/basis/statutes.asp?media=print&secStart=15.15.350&secEnd=15.15.350 | AS 15.15.350: the rules for rounds, overvotes, skipped rankings, inactive ballots and ties. |
| `law/akleg_aac_6.25.072.html` | https://www.akleg.gov/basis/aac.asp?media=print&secStart=6.25.072&secEnd=6.25.072 | 6 AAC 25.072, duplicate rankings: a candidate ranked more than once counts at the highest ranking, and the other rankings are disregarded. |

| `doe_2022/22SSPG_RcvDetailedReport.pdf`, `election-results_22sspg_page.html` | https://www.elections.alaska.gov/results/22SSPG/RcvDetailedReport.pdf; page https://www.elections.alaska.gov/election-results/e/?id=22sspg | The official RCV report for the Aug 16, 2022 special general election for U.S. House (retrieved 2026-11-04). |
| `doe_2022/22GENR_US_SEN.pdf`, `22GENR_US_REP.pdf`, `22GENR_ElectionSummaryReportRPT.pdf`, `election-results_22genr_page.html` | https://elections.alaska.gov/results/22GENR/US%20SEN.pdf, https://elections.alaska.gov/results/22GENR/US%20REP.pdf, https://elections.alaska.gov/results/22GENR/ElectionSummaryReportRPT.pdf; page https://www.elections.alaska.gov/election-results/e/?id=22genr | The official 2022 general election RCV reports for U.S. Senate and U.S. House, and the summary report. The summary shows Dunleavy/Dahlstrom at 50.29% of first choices for governor, so there was no ranked-choice count for governor in 2022 (retrieved 2026-11-04). |

| `doe_2026-11-04/counting-system-and-schedule_2026-11-04.html` | https://www.elections.alaska.gov/ballot-counting-process/counting-system-and-schedule/ | The Division's counting schedule (retrieved 2026-11-04 15:2x UTC). Early votes cast from the Friday before Election Day through Election Day are counted seven days after it. Absentee and questioned ballots must all be counted within 15 days, and questioned ballots start seven days after. The ranked-choice rounds follow the last count on day 15. |
| `doe_2026-11-04/election-results_page_2026-11-04_1521utc.html` | https://www.elections.alaska.gov/election-results/ | Re-fetched 2026-11-04 15:21 UTC. Its ballots issued/received table was still dated "November 3, 2026 at 12:26 pm". `scripts/ak_remaining.py` compares that table with the counted ballots (`outputs/remaining_20261104.txt`). |

## Method (`scripts/`)

Run Python with `-I`, and pass the extracted CVR folder as an argument.

- **`ak_rcv.py <cvr dir> <out.json> [--all-rounds] [contest ...]`** runs instant runoff per the Division's rules and AS 15.15.350:
  - It eliminates one candidate per round and stops at two candidates, or at a round-1 majority. `--all-rounds` continues past a majority for information.
  - Unresolved write-ins are passed over.
  - An overvote, or two skipped rankings in a row, makes the ballot inactive.
  - Under 6 AAC 25.072, a repeated ranking of a candidate becomes blank, but a rank naming two candidates stays an overvote.
  - Blanks are ballots inactive in round 1 for any reason other than an overvote.
  - A contest with no votes and an undervote count of 0 is not counted in that contest.

  Those last three rules come from matching the official 2024 reports, not from published text.
- **`validate.py`** compares the tabulator's output with the official RCV Detailed Report PDFs. On the 2024 CVR, all 7 contests match the official reports exactly in every round: each candidate's votes and the continuing, blank, exhausted and overvote counts (`outputs/validate_2024.txt`).
- **`cvr_vs_precinct.py`** compares the CVR with the precinct results file, by precinct and counting group.
- **`ak_dash_data.py <cvr dir> <precinct csv> <combined.json> <summary stamp> <cvr last-modified> <out dir>`** writes the dashboard's tables (`outputs/dashboard/*.csv`, all counts over ballots):
  - rounds and transfers;
  - how many candidates each first choice's voters ranked, and their next choice;
  - each state house district under the statewide eliminations;
  - every legislative race;
  - ballots by counting group.

  `validate.py --csv` writes `validation_2024.csv`. The page is `outputs/dashboard/index.html`, published as the "Alaska Ranked-Choice Count" dashboard (https://claude.ai/artifact/BPe75Hq3p5BcatHU1RvEYc, private).
- **`ak_exhaustion_history.py`** reads the exhausted, overvoted and continuing ballots from each official statewide RCV report (2022 special, 2022 and 2024 general) and from the 2026 CVR count, and writes `outputs/exhaustion_history.csv`. The exhaustion rate is final-round exhausted ballots over round-1 continuing ballots.
- **`ak_combine.py`** adds the ballots that are in the precinct results but not in the CVR (first choices only) to the CVR's rounds. It has two parts:
  - **Scenario:** each eliminated candidate's added votes move in the same shares as that candidate's CVR ballots did in that round.
  - **Bounds:** every added vote for a non-finalist or write-in goes entirely to one finalist or entirely to the other.

  Hand-counted write-ins = the summary's write-ins minus the CVR's rank-1 write-ins.

## What the 2026-11-04 files show (`outputs/`)

- **Missing ballots.** The CVR has 204,530 ballots and the precinct file 215,335. The 10,805 missing are all Election Day ballots from 138 precincts that have no ballots in the CVR. Every other precinct matches exactly. The Division says the CVR leaves out ballots "only counted by hand".
- **Senate, CVR only.** Round 1: Sullivan, Dan S. (R) 99,617, Peltola 95,792, Heikes 4,380, Sullivan, Daniel J. Jr. 3,426. Round 3: Sullivan 102,342 (51.17%), Peltola 97,656 (48.83%).
- **Senate, with the hand-counted precincts.** Their first choices are Peltola 7,070, Sullivan 2,605, Heikes 620, Sullivan Jr. 253, plus 47 write-ins.
  - The scenario's final round is Sullivan 105,277, Peltola 104,915 (Sullivan +362, 0.17 pts).
  - The bounds run from Peltola +699 to Sullivan +1,141.
- **U.S. House.** Begich has 50.31% of round 1 on the CVR. With the hand-counted precincts he has 49.55% of round 1, so the count goes to more rounds. The scenario's final round is Begich 108,291, Hill 95,061 (+13,230); the bounds are Begich +12,204 to +15,088.
- **Governor.** The scenario's final round is Kreiss-Tomkins 107,022, Wilson 86,774 (+20,248); the bounds are +18,958 to +23,794.
- **Not final.** The Division counts the remaining ballots over the following two weeks and runs the official tabulation on Nov 18 ("once all eligible ballots are reviewed and counted", per the results page). These files cover only ballots counted by 2:19–2:45 am AKST on Nov 4.
