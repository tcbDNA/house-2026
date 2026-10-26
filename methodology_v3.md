# Methodology — v3

## Projection formula

Each district / state projection is

    pres_margin_2024 + uniform_swing + trend_weight × residual_trend + WAR_blend + incumbency + challenger + demographic_shift

where `pres_margin_2024` is the Harris–Trump margin (D-positive) in that district / state.

- **National environment** defaults to **D+8.5**, estimated from poll race crosstabs rather than toplines (see *Generic ballot from crosstabs* below); adjustable via the slider.
- **Uniform swing (House)** is calibrated at projection time: it's whatever constant makes the 2024-turnout-weighted average of all 435 district margins (before demographic sliders) equal the environment (the uniform wave). With the demographic sliders at their 2024 values the wave *is* the national House popular vote; with the default sliders, the national margin is the panel's **Total** (wave R+1.2 + sliders +9.7 = D+8.5). Turnout weights are 2024 presidential votes per district, summed from the precinct-aggregated district × county slices.
  - Why not "environment − 2024 House vote (R+2.6)": the district baseline is the presidential map, which averages R+1.45, not R+2.6. Swinging the presidential map from the House result silently added ~1.1 pts of D lean (plus ~0.25 from the trend term) — D+8.9 actually ran as D+10.3.
- **Uniform swing (Senate)** = environment − 2024 presidential popular vote (R+1.5). Presidential baseline and presidential reference, so no calibration step is needed.
- **Trend** starts from each district's / state's 2020→2024 presidential movement **relative to the nation** (2020 D+4.5 → 2024 R+1.5, a 6.0-pt national shift). A 2024-vote-weighted regression of district trend on the active frame's electorate shares (always plus age shares) and a 2024 battleground-state indicator (AZ, GA, MI, NV, NC, PA, WI) splits it into a demographic part (with the intercept), a battleground part and the rest (`trend.py`; a setting for each part). **By default the demographic part is removed**, so the trend doesn't double count group movement the sliders already model, and **the battleground part is kept**: all seven 2024 battlegrounds have a Senate or governor's race in 2026, so the campaign effect may repeat. States use the same coefficients on their own shares and battleground status, centered on the national mean (weighted by official 2024 votes across all 50 states). Fits: race frame R² 0.63 (0.59 without the battleground term), battleground coefficient +2.1 (SE 0.3); race × education R² 0.57, +2.4.
- **Trend weight defaults to 0.5 — a judgment call** (half the remaining movement persists); 0 (none), 1 (full) and −0.5 (reversal) are scenario options. **A limited check, not the basis for the default:** in the 2025 New Jersey and Virginia governor's races, regressing each county's 2025 governor margin minus its 2024 presidential margin on its 2020→2024 trend, with the same race and age shares and a state fixed effect, weighted by 2025 votes, gives −0.05 (robust SE 0.11, n = 154); without the demographic controls the coefficient is −0.83, i.e. the demographic part reversed (`analysis/trend_weight_nj_va_2025.txt`). Governor's races differ from federal ones, and the test covers two states (neither a 2024 battleground), an off-year election and county-level data.

## Generic ballot from crosstabs

The default environment is built from each poll's race breakdown instead of its topline (`backend/data/crosstab_environment.py`, data in `backend/data/generic_ballot_crosstabs.csv`):

1. Take the latest national generic-ballot poll from each pollster that publishes a race breakdown, ending in late September or later (~5 weeks before the update). ActiVote and Rasmussen are excluded.
2. Convert each group's result to a two-way margin, 100 × (D − R) / (D + R), so differing undecided rates don't distort the average (and to match the two-way Catalist slider baselines).
3. Average each group across polls, weighted by √(subgroup n) (capped at 2,000). Published subgroup sizes are used as printed (unweighted for NYT/Siena, Echelon and Economist/YouGov; weighted for CBS/YouGov and Emerson). Where a pollster publishes group margins of error instead (Fox News 2024 and 2026, Pew 2024), subgroup n = total n × (MOE_total / MOE_group)², which carries the pollster's oversampling and weighting; Pew's methodology tables list sample sizes only by party and candidate support, not race. Where neither is published (Pew 2026, Cygnal), subgroup n is total n × the group's electorate share (`environment._estimated_group_n`) — for Pew 2026, which oversampled Hispanic and Asian adults, this likely understates those groups. A group needs at least two polls; otherwise — and always for "other" race — it gets the share-weighted average shift of the measured groups.
4. **National level S**: each group's shift = poll average − its 2024 margin (Catalist by default; Pew's 2024 validated-voter study as a setting, `group_baseline`), weighted by electorate share (2026 electorate, white 74%) and added to the 2024 result (R+1.5).
5. **Pattern across groups (pollster-matched).** For each pollster, its 2026 crosstab is compared with its own final 2024 pre-election poll (`backend/data/pollster_2024_crosstabs.csv`; same sample type for all eight): r = (2026 group margin − 2024 group margin) − (2026 topline − 2024 topline), two-way throughout. Comparing within a pollster cancels persistent crosstab bias; subtracting the topline change keeps 2024's polling miss out of the level. r is combined across pollsters with inverse-variance weights, 1/SE_r², where SE_r² is the sum of both years' sampling variance of the group margin, 200² × p(1 − p) × deff / n with deff 1.5. Each group's r_avg is also recomputed with each pollster left out in turn; if any one pollster moves it by more than 1.5 pts, the group uses the weighted median instead (flagged). Each group's shift is S + (r_avg − c), where c is the share-weighted mean of r_avg over the slider groups, so the national level stays S; "other" takes S. A group needs two matched pollsters, and Asian is matched only if every 2026 Asian crosstab (NYT/Siena, Pew, Emerson) has a 2024 pair — NYT/Siena's final 2024 poll had no Asian column, so Asian keeps its poll-average shift (c absorbs it).

October 26, 2026 update — eight 2026 polls (Sep 21–Oct 23): NYT/Siena (LV), CBS/YouGov (LV), Echelon (LV), Cygnal (LV, Oct 1–2; its Oct 7–10 poll has no race breakdown), Emerson (LV, Sep 21–22), Economist/YouGov (RV), Fox News (RV), Pew (RV). Asian from NYT/Siena, Pew (both English-speaker samples) and Emerson (n≈46). Matched 2024 polls: NYT/Siena Oct 20–23, CBS/YouGov Oct 23–25, Echelon Oct 28–31, Economist/YouGov Oct 26–29 (RV), Fox News Oct 11–14 (RV), Pew Sep 30–Oct 6 (RV), Emerson Oct 30–Nov 2, Cygnal Oct 24–26. Cygnal's race results were published only as heatmap images; its row uses the deck's generic congressional ballot (p.16 — the same question as its 2026 row, where the other seven use presidential vote), with values read from the image and confirmed by the user.

| Group | Share | 2026 avg | 2024 (Catalist) | Poll-average shift | r_avg (pollsters; method) | Shift used | Contribution |
|---|---|---|---|---|---|---|---|
| White | 74.0% | R+6.3 | R+15.2 | +8.9 | −2.6 (8; mean) | **+8.2** | +6.03 |
| Black | 10.3% | D+75.3 | D+70.8 | +4.5 | −0.1 (8; mean) | **+10.6** | +1.09 |
| Hispanic | 8.6% | D+29.7 | D+8.5 | +21.2 | +9.7 (8; **median**, flagged — mean +6.2; leaving out CBS/YouGov moves the mean 2.5) | **+20.4** | +1.76 |
| Asian | 3.9% | D+42.9 | D+21.4 | +21.5 | (2; not used) | **+21.5** | +0.84 |
| Other | 3.2% | — | D+7.1 | +10.0 | — | **+10.0** (S) | +0.32 |

S = **+10.0** → R+1.5 + 10.0 = **D+8.5** (equal weight per pollster: D+8.3; total-n weights as before: D+8.4). With Pew's validated-voter 2024 margins (white R+12.2, Black D+69.4, Hispanic D+3.0, Asian D+17.5) S is +8.5 → **D+7.0**: at the 2026 composition the two baselines imply 2024 levels 1.5 pts apart. The same polls' toplines average D+9.0 two-way. Full table with each pollster's r: `backend/analysis/group_shifts.txt`.

**How it enters the model.** Each race slider defaults to its Catalist 2024 margin plus the shift used (white R+7.1, Black D+81.4, Hispanic D+28.9, Asian D+42.9), so each group's shift lands on the districts and states where that group lives. Those sliders carry +9.7 nationally; the uniform wave defaults to **R+1.2** (2024 + the "other" group's share of S), so the turnout-weighted national total is D+8.5. In the race × education frame the white college and non-college cells are matched the same way (NYT/Siena, CBS/YouGov, Pew: college r −4.5 by weighted median, flagged — leaving out CBS/YouGov moves the mean 2.1; non-college −2.7; shifts +7.2 and +8.9, averaging to the white race shift) and the non-white cells take 2024 + the non-white race groups' average shift (+15.4). The four cells cover every voter, so in that frame the wave is exactly the 2024 level (R+1.5) and the national total is the same D+8.5 (checked against the model output).

**Why not reweight the margins to the 2022 midterm electorate?** Applying the group margins directly to Catalist's 2022 composition gives D+6.7, because 2024's margins on that whiter electorate are R+3.1 rather than R+1.5 — a 1.6-pt R composition shift the polls themselves don't show (their likely-voter samples are ~70–73% white, not ~76%). Each point of assumed white share moves that variant ~0.53 pts. The shift formulation uses the crosstabs for what they measure — how each group has moved — without layering on a turnout assumption.

Polls checked without a usable public race breakdown of the ballot: Harvard CAPS/Harris, Morning Consult (blocked), CNN/SSRS (blocked), NBC/SurveyMonkey (blocked), ABC/WaPo/Ipsos, Reuters/Ipsos, Quinnipiac, AP-NORC, Strength In Numbers/Verasight, RMG/Napolitan, TIPP, Noble Predictive. No national poll in the window: Marquette, Marist, Suffolk, AtlasIntel, WSJ, Yahoo/YouGov, The Argument, Quantus, Data for Progress, Navigator.

## WAR (Wins Above Replacement)

WAR is the candidate-quality adjustment from [Split-Ticket](https://split-ticket.org), measuring how much a candidate over/underperforms the presidential baseline in their seat.

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

There are currently no per-candidate exemptions to this discount.

### Who gets WAR

- **Sitting incumbents**: their own record; halved if the district is on new lines (the WAR was earned with a different electorate). Members who moved districts (Bera CA-03, Sánchez CA-41, Kennedy UT-04) are treated as incumbents.
- **Non-sitting nominees in the incumbent slot** (open seats, or the incumbent lost renomination): their own federal record if one exists, exactly like a challenger, with no incumbency bonus.
- **Challengers**: their own federal record in the same state.

Name matching is accent-insensitive. When an exact name match fails, a last-name + party + state fallback requires a compatible first name (same name, an initial, a known nickname, or a 3+-letter prefix), so same-surname relatives (Trever vs. Troy Nehls) don't collide.

### Per-cycle exclusions

A small number of specific races are excluded at blend time:

- **Collins 2014 vs Bellows** — 68%-31% blowout that would inflate her personal-vote signal.
- **Sullivan 2014 vs Begich** — the extracted "personal vote" reflects Begich's incumbency, not Sullivan's underperformance.

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

**Group voting baselines** (slider zero-points) use **Catalist 2024 D-R margins** per group, matching the 2024 presidential baseline the rest of the model is built on. Parking sliders at default means each group votes as it did in 2024 — zero demographic deviation from the baseline. Moving a slider models that group voting differently than it did in 2024, as a deliberate counterfactual. The resulting shift adds on top of the national environment.

**Electorate composition shares** use **Catalist 2022** (prior-midterm) values, since midterm turnout shape is the better analog for the 2026 voter pool than presidential-year turnout. ACS race shares are of total population (including children and non-citizens) and age / education shares are of adults, so each group's ACS share is multiplied by a national turnout factor and renormalized within each district / state / county. The factors are fit by iterative proportional fitting over the 435 districts so that each group's 2024-turnout-weighted national average equals its Catalist 2022 share (e.g. Hispanic ≈ 0.42×, under-30 ≈ 0.49×, 65+ ≈ 1.53×). Without this, a Hispanic or youth slider moved the national margin about twice as much as the slider panel reported.

Both the 2024 group margins and the 2022 composition shares come from the same source — [Catalist's "What Happened 2024" national crosstabs](https://catalist.us/whathappened2024/), with 2022 as the prior-cycle column.

**Overlapping axes.** Race (or race × education) and age describe the same voters, so when more than one axis is moved their shifts are averaged rather than stacked, weighted by how far each axis was moved (electorate-share-weighted |Δ| from baseline). A lone moved axis gets full weight; two equally-moved axes get 0.5 each; nudging a second axis slightly takes only a sliver of weight (replacing the old step to 0.5×).

## Senate-specific

Senate projections treat the state-level trend (state vs. national 2020→2024 shift) like the House trend: residualized with the district coefficients (demographic part removed, battleground part kept), centered nationally, default weight 0.5.

- 65 not-up seats are assumed to hold their current party.
- Control: D needs **51**; a 50-50 split is **R control** via VP Vance's tiebreak (`p_r_control` counts it; `p_r_majority` is an outright 51+).
- Independents (Osborn NE, Bengs SD) are counted with Democrats for majority purposes; neither is committed to caucusing with them.
- **Montana** is a three-way race (Daines withdrew in March): Kurt Alme (R) vs Seth Bodnar (I), with Alani Bankhead (D) polling a distant third, plus a Libertarian. The D-vs-R baseline can't represent it, so the race uses a documented polling override (`backend/data/senate_poll_overrides.csv`): the RealClearPolling average, Bodnar − Alme = −12.0 as of Oct 18 (Quantus Oct 15–18, Rutgers-Eagleton Aug 27–Sep 7), plus the change in the model's projection between the current scenario and the default one, so sliders and settings still move it. It gets the usual simulation errors. The model's own baseline would be R+12.3.
- Primary-unresolved seats suppress incumbent WAR and incumbency until the runoff resolves.

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
| Group errors (race frame): white / Black / Hispanic / Asian | 1.96 / 4.10 / 5.75 / 8.07 |

**Group errors.** Each simulation draws dev_g ~ N(0, σ_g²) for every slider group in the active frame, subtracts the national-share-weighted mean of the draws (shares renormalized over the slider groups, so the national total is unchanged), and adds Σ_g (electorate share of g) × demeaned dev_g to every district and state — heavily Hispanic seats miss together across states. σ_g = sqrt(SE_g² + τ_g²): SE_g is the sampling error of the group's shift (the inverse-variance pooled SE of the pollster-matched r, both years at design effect 1.5; for Asian, which keeps its poll average, the SE of that average): white 1.69, Black 2.79, Hispanic 4.13, Asian 6.34. τ_g is non-sampling error — **judgment calls**, configurable: white 1, Black 3, Hispanic 4, Asian 5, any other group 3 (the race × education cells, giving σ 4.5 / 4.2 for white college / non-college and 3.6 for the non-white cells). Hispanic's SE is the pooled mean's, though its shift uses the weighted median.

The composition and level terms raise the standard deviation of the simulated national margin (2024-turnout-weighted mean of district margins) from 2.58 to 2.94; the group errors leave it unchanged (2.58 alone) but raise the average pairwise correlation among the five most Hispanic competitive districts (TX-15, FL-26, FL-27, TX-34, CA-22) from 0.36 to 0.56 (`backend/analysis/error_diagnostics.txt`).

Per-race σ (excluding group terms) is ≈ 4.8 for an incumbent on unchanged lines and ≈ 5.8 for an open seat on new lines. Lockouts are deterministic. Each call uses a fixed seed, so a given scenario always returns the same probabilities and slider moves don't add simulation jitter. The σ values are modeling judgments, not fitted. Probabilities are conditional on the scenario inputs.

## County overlay

County-level overlays use 2020 + 2024 presidential results aggregated to county / borough boundaries. Alaska supplements with [Dave's Redistricting](https://davesredistricting.org) per-borough 2020 numbers (state doesn't publish official borough-level results).

Estimated 2026 vote counts assume turnout at **79% of 2024**, the midpoint of the last two midterm-to-prior-presidential ratios (2018/2016 ≈ 87%, 2022/2020 ≈ 71%). These ratios differ substantially; a high-salience 2026 midterm would fall toward the higher end. **This is a tunable parameter and affects only the county-overlay vote-count display — not any projection, margin, or seat call.** Projected D share is clamped to [0, 1] so extreme scenarios can't produce negative vote counts.

## Caveats

- Bucket thresholds: **Tilt ≤ 3 pts · Lean 3–7 · Likely 7–13 · Safe > 13**.
- Projections within ±3 pts are tilts, not predictions — model uncertainty is wider than the displayed precision.
- Demographic crosstabs are sample-based approximations.
- The trend multiplier (default 0.5) is a judgment call, not fitted. The Nov 2025 NJ / VA governor results are a natural test: regress county-level (2025 margin − 2024 pres margin) on 2020→2024 relative trend; a negative coefficient would favor the Reverse setting.
