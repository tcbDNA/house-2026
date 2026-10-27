# Methodology — v3

## Projection formula

Each district / state projection is

    pres_margin_2024 + uniform_swing + trend_weight × residual_trend + WAR_blend + incumbency + challenger + demographic_shift

where `pres_margin_2024` is the Harris–Trump margin (D-positive) in that district / state.

- **National environment** defaults to **D+9.5**, estimated from poll race crosstabs rather than toplines (see *Generic ballot from crosstabs* below); adjustable via the slider.
- **Uniform swing (House)** is calibrated at projection time: it's whatever constant makes the 2024-turnout-weighted average of all 435 district margins (before demographic sliders) equal the environment (the uniform wave). With the demographic sliders at their 2024 values the wave *is* the national House popular vote; with the default sliders, the national margin is the panel's **Total** (wave R+1.2 + sliders +9.7 = D+8.5). Turnout weights are 2024 presidential votes per district, summed from the precinct-aggregated district × county slices.
  - Why not "environment − 2024 House vote (R+2.6)": the district baseline is the presidential map, which averages R+1.45, not R+2.6. Swinging the presidential map from the House result silently added ~1.1 pts of D lean (plus ~0.25 from the trend term) — D+8.9 actually ran as D+10.3.
- **Uniform swing (Senate)** = environment − 2024 presidential popular vote (R+1.5). Presidential baseline and presidential reference, so no calibration step is needed.
- **Trend** starts from each district's / state's 2020→2024 presidential movement **relative to the nation** (2020 D+4.5 → 2024 R+1.5, a 6.0-pt national shift). A 2024-vote-weighted regression of district trend on the active frame's electorate shares (always plus age shares) and a 2024 battleground-state indicator (AZ, GA, MI, NV, NC, PA, WI) splits it into a demographic part (with the intercept), a battleground part and the rest (`trend.py`; a setting for each part). **By default the demographic part is removed**, so the trend doesn't double count group movement the sliders already model, and **the battleground part is kept**: all seven 2024 battlegrounds have a Senate or governor's race in 2026, so the campaign effect may repeat. States use the same coefficients on their own shares and battleground status, centered on the national mean (weighted by official 2024 votes across all 50 states). Fits: race frame R² 0.63 (0.59 without the battleground term), battleground coefficient +2.1 (SE 0.3); race × education R² 0.57, +2.4.
- **Trend weight defaults to 0.5 — a judgment call** (half the remaining movement persists); 0 (none), 1 (full) and −0.5 (reversal) are scenario options. **A limited check, not the basis for the default:** in the 2025 New Jersey and Virginia governor's races, regressing each county's 2025 governor margin minus its 2024 presidential margin on its 2020→2024 trend, with the same race and age shares and a state fixed effect, weighted by 2025 votes, gives +0.02 (robust SE 0.11, n = 154); without the demographic controls the coefficient is −0.88, i.e. the demographic part reversed (`analysis/trend_weight_nj_va_2025.txt`). Governor's races differ from federal ones, and the test covers two states (neither a 2024 battleground), an off-year election and county-level data.

## Generic ballot from crosstabs

The default environment is built from each poll's race breakdown instead of its topline (`backend/data/crosstab_environment.py`, data in `backend/data/generic_ballot_crosstabs.csv`):

1. Take the latest national generic-ballot poll from each pollster that publishes a race breakdown, ending in late September or later (~5 weeks before the update). ActiVote and Rasmussen are excluded.
2. Convert each group's result to a two-way margin, 100 × (D − R) / (D + R), so differing undecided rates don't distort the average (and to match the two-way Catalist slider baselines).
3. Average each group across polls, weighted by √(subgroup n) (capped at 2,000). Published subgroup sizes are used as printed (unweighted for NYT/Siena, Echelon and Economist/YouGov; weighted for CBS/YouGov and Emerson). Where a pollster publishes group margins of error instead (Fox News 2024 and 2026, Pew 2024), subgroup n = total n × (MOE_total / MOE_group)², which carries the pollster's oversampling and weighting; Pew's methodology tables list sample sizes only by party and candidate support, not race. Where neither is published (Pew 2026, Cygnal), subgroup n is total n × the group's electorate share (`environment._estimated_group_n`) — for Pew 2026, which oversampled Hispanic and Asian adults, this likely understates those groups. A group needs at least two polls; otherwise — and always for "other" race — it gets the share-weighted average shift of the measured groups. A poll that reports race only as White vs Non-white (Marist) counts for the white and white × education groups only (setting `crosstab_white_only_polls`, user decision Oct 27).
4. **National level S**: each group's shift = poll average − its 2024 margin (Catalist by default; Pew's 2024 validated-voter study as a setting, `group_baseline`), weighted by electorate share (2026 electorate, white 74%) and added to the 2024 result (R+1.5).
5. **Pattern across groups (pollster-matched).** For each pollster, its 2026 crosstab is compared with its own final 2024 pre-election poll (`backend/data/pollster_2024_crosstabs.csv`; same sample type for all eight matched pollsters; Marist has no 2024 pair and enters only the level): r = (2026 group margin − 2024 group margin) − (2026 topline − 2024 topline), two-way throughout. Comparing within a pollster cancels persistent crosstab bias; subtracting the topline change keeps 2024's polling miss out of the level. r is combined across pollsters with inverse-variance weights, 1/SE_r², where SE_r² is the sum of both years' sampling variance of the group margin, 200² × p(1 − p) × deff / n with deff 1.5. Each group's r_avg is also recomputed with each pollster left out in turn; if any one pollster moves it by more than 1.5 pts, the group uses the weighted median instead (flagged). Each group's shift is S + (r_avg − c), where c is the share-weighted mean of r_avg over the slider groups, so the national level stays S; "other" takes S. A group needs two matched pollsters, and Asian is matched only if every 2026 Asian crosstab (NYT/Siena, Pew, Emerson) has a 2024 pair — NYT/Siena's final 2024 poll had no Asian column, so Asian keeps its poll-average shift (c absorbs it).

October 27, 2026 update — nine 2026 polls (Sep 21–Oct 26): NYT/Siena (LV), CBS/YouGov (LV), Echelon (LV), Cygnal (LV, Oct 1–2; its Oct 7–10 poll has no race breakdown), Emerson (LV, Sep 21–22), Economist/YouGov (RV, Oct 23–26, which replaced its Oct 19–20 poll on Oct 27), Fox News (RV), Pew (RV), and Marist/NPR/PBS (LV, Oct 19–20; White 49/47, white college 63/35, white non-college 35/58; race reported only as White vs Non-white, so it counts for the white groups only; added Oct 27). Asian from NYT/Siena, Pew (both English-speaker samples) and Emerson (n≈46). Matched 2024 polls: NYT/Siena Oct 20–23, CBS/YouGov Oct 23–25, Echelon Oct 28–31, Economist/YouGov Oct 26–29 (RV), Fox News Oct 11–14 (RV), Pew Sep 30–Oct 6 (RV), Emerson Oct 30–Nov 2, Cygnal Oct 24–26. Cygnal's race results were published only as heatmap images; its row uses the deck's generic congressional ballot (p.16 — the same question as its 2026 row, where the other seven use presidential vote), with values read from the image and confirmed by the user.

| Group | Share | 2026 avg | 2024 (Catalist) | Poll-average shift | r_avg (pollsters; method) | Shift used | Contribution |
|---|---|---|---|---|---|---|---|
| White | 74.0% | R+5.3 | R+15.2 | +9.9 (9 polls) | −2.6 (8; mean) | **+9.1** | +6.74 |
| Black | 10.3% | D+75.6 | D+70.8 | +4.8 | +0.0 (8; mean) | **+11.7** | +1.20 |
| Hispanic | 8.6% | D+31.1 | D+8.5 | +22.7 | +9.7 (8; **median**, flagged — mean +7.1; leaving out CBS/YouGov moves the mean 2.6) | **+21.3** | +1.84 |
| Asian | 3.9% | D+42.9 | D+21.4 | +21.5 | (2; not used) | **+21.5** | +0.84 |
| Other | 3.2% | — | D+7.1 | +11.0 | — | **+11.0** (S) | +0.35 |

S = **+11.0** → R+1.5 + 11.0 = **D+9.5** (equal weight per pollster: D+9.3; total-n weights as before: D+9.4; without Marist: D+8.8). With Pew's validated-voter 2024 margins (white R+12.2, Black D+69.4, Hispanic D+3.0, Asian D+17.5) S is +9.5 → **D+8.0**: at the 2026 composition the two baselines imply 2024 levels 1.5 pts apart. The same polls' toplines average D+9.1 two-way. Full table with each pollster's r: `backend/analysis/group_shifts.txt`.

**How it enters the model.** Each race slider defaults to its Catalist 2024 margin plus the shift used (white R+6.1, Black D+82.5, Hispanic D+29.8, Asian D+42.9), so each group's shift lands on the districts and states where that group lives. Those sliders carry +10.6 nationally; the uniform wave defaults to **R+1.2** (2024 + the "other" group's share of S), so the turnout-weighted national total is D+9.5. In the race × education frame the white college and non-college cells are matched the same way (NYT/Siena, CBS/YouGov, Pew: college r −4.5 by weighted median, flagged — leaving out CBS/YouGov moves the mean 2.1; non-college −2.7; shifts +8.1 and +9.9, averaging to the white race shift) and the non-white cells take 2024 + the non-white race groups' average shift (+16.3). The four cells cover every voter, so in that frame the wave is exactly the 2024 level (R+1.5) and the national total is the same D+9.5 (checked against the model output).

**Composition.** The shifts are weighted by the model's 2026 electorate shares (white 74% by default; 72–76% in the settings, D+9.6 to D+9.4), and uncertainty about who turns out enters the simulation as the composition error term (σ 1.0). The shift formulation uses the crosstabs for what they measure — how each group has moved — rather than applying 2026 group margins to an assumed electorate.

Polls checked without a usable public race breakdown of the ballot: Harvard CAPS/Harris, Morning Consult (blocked; its Oct 13–20 poll for the Deseret News publishes only the topline), CNN/SSRS (blocked), NBC/SurveyMonkey (blocked), ABC/WaPo/Ipsos, Reuters/Ipsos (Oct 22–26 topline by party only), Quinnipiac, AP-NORC, Strength In Numbers/Verasight, RMG/Napolitan, TIPP, Noble Predictive, Echelon Insights for NetChoice (Oct 16–23, topline only; Echelon's Oct 15–19 omnibus stays in), Prolific (Oct 21–22, LV D+10.7; crosstabs by party ID and 2024 vote only; files in `polls_2026/prolific/`). Focaldata/Financial Times (Oct 16–20) publishes race only among all adults, not voters, and is left out (user decision Oct 27). No national poll in the window: Marquette, Suffolk, AtlasIntel, WSJ, Yahoo/YouGov, The Argument, Quantus, Data for Progress, Navigator.

## WAR (Wins Above Replacement)

WAR is the candidate-quality adjustment from [Split-Ticket](https://split-ticket.org). Split Ticket measures each candidate's result against a **fundamentals baseline** — seat partisanship (through the same-year presidential margin), incumbency, demographics and money — not just the presidential result, so its WAR is net of incumbency (worth about 3 points in 2024).

### Eligibility window

Only each office's last three cycles before 2026 are eligible: **House 2020–2024**, **Governor 2014+**, **Senate 2008+**. Older races describe a different electorate, and under positional slotting a lone old race would otherwise take the full 0.50 slot.

### Per-record windowing

Each record is windowed by its own election type. A candidate's records are grouped by office (House / Senate / Governor); within each office group, records are sorted year-desc and the top three slot at weights **0.50 / 0.30 / 0.20** by recency rank.

A record's weight is set by its rank within its own office's history — *not* by which office the candidate is now seeking. A recent race is never discarded merely because the candidate is moving between offices with different term lengths.

When records from several offices push the summed recency weights past 1.0 (e.g. 2 Senate + 3 House records = 1.8), the weights are rescaled to sum to 1.0, so the blend stays a weighted average of the candidate's races.

### Thin records

Missing slots count as zero (per the WAR creator's guidance), which regresses thin records toward the mean: one race carries **0.5×** of its WAR, two races **0.8×**, three races **1.0×**. This is the only thin-record adjustment — the earlier n/(n+k) shrinkage was removed because it penalized the same thinness a second time (one race was ending up at 0.33×).

### Cross-chamber discount

Records from a different office than the race being projected take an additional **0.5× cross-chamber discount**. For a Senate projection, this means House and Governor records are halved before contributing to the blend. The empirical anchor is the 2018 Bredesen TN-Senate race: his federal personal vote came in at roughly half his gubernatorial WAR.

**Provenance.** `backend/data/raw_war.csv` is Split Ticket's Full WAR Database (House and Senate, 2014–2024), identical row for row to its current version, plus two rows that are not Split Ticket's: Roy Cooper's North Carolina governor races, 2016 (D+3.86) and 2020 (D+5.85). Split Ticket publishes no governor WAR; those values are his margin minus the same-day presidential margin, so they don't remove incumbency (he was the challenger in 2016 and the incumbent in 2020). They're kept as a deliberate choice; through the 0.5× cross-chamber discount they add +2.04 to NC (D+9.7; D+7.6 without them).

There are currently no per-candidate exemptions to this discount.

### Who gets WAR

- **Sitting incumbents**: their own record; halved if the district is on new lines (the WAR was earned with a different electorate). Members who moved districts (Bera CA-03, Sánchez CA-41, Kennedy UT-04) are treated as incumbents.
- **Non-sitting nominees in the incumbent slot** (open seats, or the incumbent lost renomination): their own federal record if one exists, exactly like a challenger, with no incumbency bonus.
- **Challengers**: their own federal record in the same state.

Name matching is accent-insensitive. When an exact name match fails, a last-name + party + state fallback requires a compatible first name (same name, an initial, a known nickname, or a 3+-letter prefix), so same-surname relatives (Trever vs. Troy Nehls) don't collide.

### Per-cycle exclusions

A small number of specific races are excluded at blend time:

- **Collins 2014 vs Bellows** — 68%-31% blowout that would inflate her personal-vote signal.
- **Sullivan 2014 vs Begich** (Split Ticket WAR D+18.8) — excluded as a judgment call: an outlier against his 2020 record (D+1.5), from a race twelve years old. (An earlier rationale, that it reflects Begich's incumbency, doesn't hold: Split Ticket's baseline controls for incumbency.) Because it matters, Alaska is shown both ways. In the model alone, excluded, Sullivan's WAR moves Alaska 0.75 toward Peltola (R+2.2); included, 6.4 toward her (D+3.5). After the poll blend (below), which scales the difference by 1 − w: excluded D+0.2, P(Peltola) 0.51; included D+1.9, P 0.65, and Senate P(D control) would be 0.708 instead of 0.684.

### Manual WAR overrides

Applied where the blended value would misrepresent expected 2026 performance:

- **Richard Ojeda (NC-09, D) = 0** — his only prior race (WV-03, 2018) is outside the House window and rejected by the auto-match on state mismatch (WV ≠ NC); it was also earned under WV-2018-specific conditions that don't transfer to NC-09 2026. The override documents these reasons explicitly so the zero is auditable, not accidental.
- **Nick Begich (AK-AL, R) = 0** — 2024 race vs. Mary Peltola is a high-WAR outlier that won't repeat in 2026.
- **Cleo Fields (LA-06, D) = 0** — a placeholder in the redrawn R+32 seat who is unlikely to run; his 2024 WAR was earned on the old D-leaning lines.

### Anti-double-count

Same-race head-to-heads (e.g. Bohannan vs Miller-Meeks 2022 and 2024) are dropped from the challenger's blend when the incumbent is a sitting member with a matched WAR, since the incumbent's blend already captures those head-to-heads.

## Incumbency

House generic incumbency is a setting (`house_incumbency`), default **±3.0** (D-positive for D incumbents): Split Ticket's most recent estimate (incumbency worth about 3 points in 2024, "Deconstructing WAR"), and the 2024 WAR records — half of each incumbent's WAR weight — were measured with it already removed. Split Ticket's 2020 House analysis put it at **1.7**, kept as a scenario: at 1.7 the House median is 237 D instead of 234 (P(D majority) 0.962 vs 0.951; PA-08 and WI-01 go D, FL-25 R), because 61 of the 94 seats within 10 points are R-held. Senate uses **±3.0**. WAR explicitly excludes this structural incumbency baseline, so the two terms compose rather than double-count.

Suppressed for: open seats, named-but-not-sitting nominees (TX-02 Toth), primary-unresolved seats, and appointed senators who haven't won an election yet.

## Demographics

**District demographics** are American Community Survey (ACS) 2023 5-year estimates from the U.S. Census Bureau, computed on current district boundaries (post-redistricting where applicable).

**Group voting baselines** (slider zero-points) use **Catalist 2024 D-R margins** per group, matching the 2024 presidential baseline the rest of the model is built on: a slider at its 2024 value adds no demographic shift. The defaults are 2024 plus each group's shift since 2024 (Generic ballot from crosstabs, above), so each group's movement lands on the districts and states where it lives; moving a slider further models a different swing, on top of the uniform wave.

**Electorate composition.** ACS race shares are of total population (including children and non-citizens) and age / education shares are of adults, so each group's ACS share is multiplied by a national turnout factor and renormalized within each district / state / county. The factors are fit by iterative proportional fitting over the 435 districts so that each group's 2024-turnout-weighted national average matches **Catalist 2022** (the prior midterm: white 75.8%), and then every non-white factor is scaled by one common factor so the **2026 white share is 74%** (setting `white_share`; age factors untouched). 74% keeps the midterm logic — midterm electorates are whiter than presidential ones (Catalist: 76% in 2022, 72% in 2024) — while allowing for demographic drift since 2022 and a more diverse early vote. The scenario range is **72–76%** (Model settings); across it the national margin moves only from D+8.6 to D+8.5, because the group shifts are close to one another. Uncertainty about who turns out is also in the simulation as the **composition** error term (σ 1.0, national). Without the turnout factors, a Hispanic or youth slider moved the national margin about twice as much as the slider panel reported.

Both the 2024 group margins and the 2022 composition shares come from the same source — [Catalist's "What Happened 2024" national crosstabs](https://catalist.us/whathappened2024/), with 2022 as the prior-cycle column.

**Overlapping axes.** Race (or race × education) and age describe the same voters, so when more than one axis is moved their shifts are averaged rather than stacked, weighted by how far each axis was moved (electorate-share-weighted |Δ| from baseline). A lone moved axis gets full weight; two equally-moved axes get 0.5 each; nudging a second axis slightly takes only a sliver of weight (replacing the old step to 0.5×).

## Senate-specific

Senate projections treat the state-level trend (state vs. national 2020→2024 shift) like the House trend: residualized with the district coefficients (demographic part removed, battleground part kept), centered nationally, default weight 0.5.

- 65 not-up seats are assumed to hold their current party.
- Control: D needs **51**; a 50-50 split is **R control** via VP Vance's tiebreak (`p_r_control` counts it; `p_r_majority` is an outright 51+).
- The four independent nominees — Osborn (NE), Bengs (SD), Achilles (ID) and Bodnar (MT) — are assumed to caucus with Democrats if they win, so the headline P(D control) counts them with Democrats. The Senate summary also reports P(D control) counting their wins for neither party, from the same simulations: 0.684 vs 0.644 by default. P(win): Osborn 0.42, Bodnar 0.030, Bengs 0.002, Achilles 0.001.
- **Poll blend** (setting `senate_poll_blend`, on by default). Every Senate race with a polling average is projected as

      projection = w × (polling average + scenario change) + (1 − w) × model

  where the scenario change is how far the current sliders and settings move the model from its default projection, so the sliders still move every race. w = 0.7 (`senate_poll_weight`, from the backtest below) with at least three polls in the average, scaled down linearly below that (two polls → 0.47, one → 0.23) and 0 with none (`senate_poll_full_n` = 3). Montana, Idaho and South Dakota, whose nominee is an independent, take w = 1 with the same scaling, because the partisan baseline can't describe an independent with cross-party appeal (in the backtest it missed Osborn 2024 and McMullin 2022 by 17+ points). Nebraska, the fourth independent race, takes the regular w instead — polls and model blended like a two-party race (setting `senate_nebraska_model_blend`, user decision Oct 27). All four get 3 extra points of race-level error. At the default, 23 of the 35 races carry poll weight, and the blend takes Texas from the model's R+1.4 to Talarico D+1.0 (P 0.58), Nebraska from R+4.9 to Ricketts +1.2 (P(Osborn) 0.42) and Alaska from R+2.2 to D+0.2 (P 0.51). Senate P(D control) 0.684 (0.601 on the model alone; 0.698 with Nebraska on polls only); with w = 0.6 or 0.8 it is 0.679 / 0.687, and the only race that changes side is Alaska (R+0.1 at w = 0.6).
- **Polling averages** (`backend/data/senate_poll_averages.csv`, built by `build_senate_poll_averages.py` from the saved RCP feeds, VoteHub and Poliwave records under `sources/senate_polls_2026/`; ActiVote, Rasmussen Reports and Wedgewood Polls are never used — Wedgewood admitted on Oct 20 that its polls were fabricated, `sources/excluded_pollsters/`). Each race starts from RealClearPolling's average with any Rasmussen poll removed (the remaining polls RCP averaged, re-averaged). In Maine, Echelon Insights' poll for NetChoice (Oct 16–23, Jackson 51–44), which RCP lists but has not yet averaged, is counted in RCP's average ahead of RCP (user decision Oct 27; `COUNT_RCP_PENDING` in the build script): Maine's average goes from D+1.1 to D+1.7 and its projection from D+3.1 to D+3.55. Where a newer poll came out after RCP last updated the average — fieldwork ending after the average's latest poll, released on or after RCP's last update — or RCP publishes no average, the average is recomputed from the most recent poll by each pollster whose fieldwork ended in the last three weeks (on or after Oct 5), using a poll's head-to-head question where it released one (as RCP's two-way averages do). As of Oct 27 that applies to Ohio, Florida, Kansas, Georgia and Iowa (Echelon Insights for NetChoice, Oct 16–23, released Oct 27), South Carolina (Impact Research, Oct 22, and Targoz Market Research for the South Carolina Policy Council, Oct 26) and Alabama (Cygnal, Oct 22), and to the races RCP doesn't average: Mississippi, Nebraska, Arkansas and Idaho. Louisiana has no poll in the window and uses the model alone, as do the 11 races with no recent poll at all. One South Carolina poll listed only on Poliwave, with no source recorded anywhere, is left out. The per-race report is `backend/analysis/senate_poll_averages.txt`. The blend uses two-party margins (Montana's three-way race excepted).
- **Montana** is a three-way race (Daines withdrew in March): Kurt Alme (R) vs Seth Bodnar (I), with Alani Bankhead (D) polling a distant third, plus a Libertarian. Its polling margin is Bodnar − Alme from RCP's three-way average (−12.0: Quantus Oct 15–18, Montana Free Press Aug 27–Sep 7); with two polls it is weighted 2/3 polls, 1/3 model (the model has R+12.3). Projection Alme +12.1.
- **Nebraska** (Osborn (I) vs Ricketts (R), no Democratic nominee): RCP publishes no average, so it is recomputed from the five polls ending Oct 5 or later (GBAO, Impact Research, National Public Affairs, Concord, Echelon Insights for NetChoice): Osborn +0.4 two-party. Blended 0.7 / 0.3 with the model's Ricketts +4.9, the projection is Ricketts +1.2, P(Osborn) 0.42 (on polls alone it would be Osborn +0.4, 0.53). A cross-check on the polls: Economist/YouGov had Fischer +7 over Osborn in late October 2024 (50–43, saved in `sources/polls_backtest/`), and Fischer won by 6.7; YouGov's 2026 poll (Sep 24–Oct 3, ended before the window) has Osborn +1 (48–47), an 8-point move toward Osborn — about the size of the national swing since 2024 (RCP's final 2024 generic ballot R+0.3 vs the model's D+9.5 now).
- Primary-unresolved seats suppress incumbent WAR and incumbency until the runoff resolves.

### Senate backtest (2022, 2024)

`backend/analysis/senate_backtest.py` reruns the model's structure for the 2022 and 2024 Senate races — each year's generic-ballot environment (RCP's final average, Rasmussen and ActiVote removed) as the uniform swing from the prior presidential result, trend weight 0.5, Senate incumbency ±3.0, and WAR from only the records available before that election (2022 used 2014–2020; 2024 used 2018–2022) — and compares it and RCP's final polling average with the result (`senate_backtest.txt`).

- Across the 25 races with an RCP final average, two-party polls had RMSE 4.77 and the model 5.50. 2022's polls missed toward the Republicans (bias −3.3), 2024's toward the Democrats (+2.1).
- A fixed blend fit across both years puts 0.62 on polls. Because each year's misses are mostly shared, the weight is fit with a separate intercept per year (the national error, which the simulation's national term covers): pooled, the best weight is **0.71** (demeaned RMSE 3.42, vs 3.75 for polls alone and 5.03 for the model alone), so w = 0.7. Year by year the weight is unstable — 0.74 in 2022, 0.32 in 2024 — which is why it is pooled and rounded.
- **Sample:** only competitive two-party races, the ones RCP averaged (14 in 2022, 11 in 2024). No race with an independent nominee had an RCP average (UT 2022 McMullin, NE 2024 Osborn, ME 2024 King), so none is in the weight estimate; the independents' w = 1 (Montana, Idaho, South Dakota) is a judgment, supported by the model missing McMullin and Osborn by 17+ points.

## Win probabilities

10,000 Monte Carlo simulations around the projection:

    simulated_margin = projection + national + composition + level + region[census region] + state
                     + race-specific + Σ_g share_g × (dev_g − Σ_h w_h dev_h)

| Component | σ (pts) |
|---|---|
| National polling error | 2.5 |
| Composition (who turns out; national, uniform) | 1.0 |
| Level measurement (crosstab sampling, choice of 2024 baseline; national, uniform) | 1.0 |
| Census region | 1.2 |
| State (House only; folded into race-specific for Senate) | 1.8 |
| Race-specific | 3.2 |
| + open seat (no sitting incumbent), in quadrature | 2.5 |
| + House district on new lines, in quadrature (× share of the district that is new) | 2.0 |
| + Senate independent's race carrying poll weight (NE, MT, ID, SD), in quadrature | 3.0 |
| Group errors (race frame): white / Black / Hispanic / Asian | 1.96 / 4.10 / 5.75 / 8.07 |

**Group errors.** Each simulation draws dev_g ~ N(0, σ_g²) for every slider group in the active frame, subtracts the national-share-weighted mean of the draws (shares renormalized over the slider groups, so the national total is unchanged), and adds Σ_g (electorate share of g) × demeaned dev_g to every district and state — heavily Hispanic seats miss together across states. σ_g = sqrt(SE_g² + τ_g²): SE_g is the sampling error of the group's shift (the inverse-variance pooled SE of the pollster-matched r, both years at design effect 1.5; for Asian, which keeps its poll average, the SE of that average): white 1.69, Black 2.79, Hispanic 4.13, Asian 6.34. τ_g is non-sampling error — **judgment calls**, configurable: white 1, Black 3, Hispanic 4, Asian 5, any other group 3 (the race × education cells, giving σ 4.5 / 4.2 for white college / non-college and 3.6 for the non-white cells). Hispanic's SE is the pooled mean's, though its shift uses the weighted median.

The composition and level terms raise the standard deviation of the simulated national margin (2024-turnout-weighted mean of district margins) from 2.58 to 2.94; the group errors leave it unchanged (2.58 alone) but raise the average pairwise correlation among the five most Hispanic competitive districts (TX-15, FL-26, FL-27, TX-34, CA-22) from 0.36 to 0.56 (`backend/analysis/error_diagnostics.txt`).

Per-race σ (excluding group terms) is ≈ 4.8 for an incumbent on unchanged lines and ≈ 5.8 for an open seat on new lines. Lockouts are deterministic. Each call uses a fixed seed, so a given scenario always returns the same probabilities and slider moves don't add simulation jitter. The σ values are modeling judgments, not fitted. Probabilities are conditional on the scenario inputs: they cover polling error around the scenario — now including composition (who turns out), level measurement and group-level crosstab error — and race-level error, not uncertainty in the scenario inputs themselves.

## County overlay

County-level overlays use 2020 + 2024 presidential results aggregated to county / borough boundaries (total-vote margins, 100 × (D − R) / total, like every other margin; the source file's two-party margins put county aggregates up to 1.3 pts off the official statewide results). Alaska supplements with [Dave's Redistricting](https://davesredistricting.org) per-borough 2020 numbers (state doesn't publish official borough-level results). Connecticut uses its nine planning regions, the Census Bureau's county equivalents since 2022 (the ACS and the county map shapes use them; the county results file still has the eight old counties): `supplement_ct_pres.py` sums the Secretary of the State's official 2020 and 2024 town results into planning regions with the Census town crosswalk, and Connecticut's 2020 precincts are moved into them by town for the district slices.

**Slice-level projections** (`backend/overlay.py`, setting `overlay_slice_projections`). Each (district, county) slice — or each county of a Senate state — is projected from its own pieces:

    slice = slice 2024 margin + county demographic shift + trend weight × shrunk residual
          + district (or Senate) uniform swing + candidate effects + reconciling shift

- **Demographics:** slices take their parent county's electorate shares (there are no slice-level demographics).
- **Trend:** the county's residual trend (item-2 coefficients with the intercept, the county's shares and battleground status; Senate states' counties centered with the same national constant as the states), shrunk toward the district's (or state's) residual with weight = votes / (votes + k), 2024 county votes, **k = 25,000** (setting `overlay_shrink_k`) — small counties' 2020→2024 shifts are noisy.
- **Estimated slices:** 12 states (AK, AR, CT, ID, ME, MI, ND, NJ, OK, OR, PA, SD) have no 2024 precinct results, so their slices' 2024 results are estimated. A county wholly inside one district keeps its real result. A split county's slices start from their 2020 precinct D and R votes, raked (iterative proportional fitting, one party at a time) to the official 2024 county totals and The Downballot's 2024 district totals — scaled within each state to the counties' sum, which matters only in Maine (district D votes 1.3% above the county total) — and other votes follow the county's 2024 total, split by 2020 shares (setting `overlay_raked_slices`; off: the slice's 2020 margin + its district's 2020→2024 shift, weighted by 2020 votes). The model's district turnout weights in these states stay on their 2020 votes, as before, so no projection changes. Slice-level trends aren't used anywhere — those slices take the district's residual. Alaska's borough-level 2024 results are estimated too, so its counties take the state's residual in the Senate view.
- **Reconciling shift:** one per district or state so the 2024-vote-weighted slices add up exactly to its projection (locked California seats reconcile to their pre-lock projection; Senate states to their blended projection). `backend/analysis/overlay_check.txt` lists the largest shifts and splits each into a 2024-margin part (an upstream data mismatch between the slices and the district), a demographic part and a trend part. Median |shift| 0.32; 162 of 435 districts exceed 0.5, mostly through the demographic and trend parts — in counties split among several districts every slice gets the county's average — while 30 have a margin part above 0.5 (1 in the estimated-slice states: MI-13, 0.7, where The Downballot and the county results count Wayne County's other votes differently; before Oct 27 it was 51 and 22, then 42 and 13 once the slice file was rebuilt on total-vote margins, and raking took it to 30 and 1). State shifts are mostly the trend part (county shifts weighted by 2024 turnout don't add up to the state's shift).

This changes only the overlay, never a district, state or seat projection.

Estimated 2026 vote counts use **each race's own Kalshi turnout market** (`backend/data/turnout_2026.csv`, built by `build_turnout_2026.py` from the saved KXMIDTERMVOTETURN markets: each race's median total vote, where the bid/ask mid of "total vote above X" crosses 50%, divided by its 2024 presidential vote; for House races in the 12 estimated-slice states, the raked slices' 2024 total). A state's counties use its Senate market, else its governor market, else its House markets combined; a district's slices use its House market, else the state's. Examples: Georgia 85% of 2024, Texas 94%, Mississippi 66%; across all 70 Senate and governor markets the vote-weighted average is 79.3% (the fallback), the 431 House markets 72.5% (≈ 111.5M House votes, between 2022's 107.9M and 2018's). **This is a tunable parameter and affects only the county-overlay vote-count display — not any projection, margin, or seat call.** Projected D share is clamped to [0, 1] so extreme scenarios can't produce negative vote counts.

## Caveats

- Bucket thresholds: **Tilt ≤ 3 pts · Lean 3–7 · Likely 7–13 · Safe > 13**.
- Projections within ±3 pts are tilts, not predictions — model uncertainty is wider than the displayed precision.
- Demographic crosstabs are sample-based approximations.
- The trend multiplier (default 0.5) is a judgment call, not fitted. The Nov 2025 NJ / VA governor check (county coefficient +0.02, robust SE 0.11, with demographic controls) is limited — governor's races differ from federal ones — and isn't the basis for the default.
