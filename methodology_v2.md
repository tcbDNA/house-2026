# House & Senate Projection Model — Methodology (v2)

> v2 changes from v1: clarified open-seat definition, documented redistricting
> discount scope, added the `trend_discount` parameter (with UI selector), and
> stamped Catalist demographic baselines with their vintage and scope.

## Core formula

**House** (per district):
```
projection = margin_2024 + uniform_swing + (rel_trend × trend_discount)
           + war_adj_discounted + incumbency_adj + challenger_adj
           + demographic_shift
```

**Senate** (per state):
```
projection = presidential_margin_2024 + (state_trend × trend_discount) + uniform_swing
           + war_adj_discounted + incumbency_adj + challenger_adj
           + demographic_shift
```

All terms are in **D−R margin points**. Positive = D-favored, negative = R-favored.

---

## Component-by-component

### 1. `margin_2024` / `presidential_margin_2024`

The **2024 presidential** two-party margin (Harris − Trump) in the geography.

- **House**: pop-weighted presidential vote on the new 2026 district lines. For states that redrew lines (CA, TX, OH, NC, TN, MO, UT, FL, LA, AL), DRA block-level 2024 results are overlaid onto the new boundaries via each state's Block Assignment File. For states with unchanged lines, it's the existing district-level pres margin.
- **Senate**: state-level Harris − Trump margin.

Using presidential rather than the prior House race is deliberate: it gives a baseline that's free of House-specific incumbent personal-vote effects, so WAR and structural incumbency can be added cleanly on top without double-counting.

### 2. `uniform_swing`

```
House:  uniform_swing = environment − HOUSE_2024_POPVOTE  (HOUSE_2024_POPVOTE = −2.6)
Senate: uniform_swing = environment − PRES_2024_POPVOTE   (PRES_2024_POPVOTE  = −1.5)
```

The "national environment" slider expresses your scenario as a D popular-vote target. The model subtracts the actual 2024 popular vote to convert to a swing. So `environment = 0` in the House model = "2026 House popvote is tied" → adds +2.6 D swing uniformly across all districts.

The two models use different reference popvotes because what you're projecting differs: the House model targets the House popular vote (2024 = R+2.6); the Senate model uses the presidential popular vote (2024 = R+1.5) as the lens through which to interpret an "environment" applied to a pres-based baseline.

### 3. `rel_trend` (House) / `state_trend` (Senate)

A geography-specific trend term capturing relative movement.

- **House `rel_trend`**: how the district has moved relative to its state across recent cycles (2020 → 2024). Sourced from the v20 sensitivity CSV. Captures things like Hispanic shift in the Rio Grande Valley or college-burb realignment in DuPage that aren't visible in raw 2024 numbers alone.
- **Senate `state_trend`**: state shift (2024 pres − 2020 pres) minus the national pres shift over the same period. So a +3 state_trend means the state moved 3 points more D than the country did between 2020 and 2024.

#### Trend persistence (`trend_discount` parameter)

The trend term is multiplied by `trend_discount` (range 0.0 – 1.0, default **1.0**) before being combined into the projection. This lets you sensitivity-test the assumption that 2020 → 2024 trends repeat into 2026.

| Preset    | Value | Meaning                                                |
| --------- | ----- | ------------------------------------------------------ |
| Full      | 1.0   | Trends persist at full strength (default; preserves prior behavior) |
| Partial   | 0.5   | Partial mean-reversion — recommended for forecasts >1 cycle out     |
| None      | 0.0   | Pure structural baseline — no trend term                            |

Real-world trends rarely persist indefinitely at full magnitude — they tend to decay as the underlying demographic and political dynamics that produced them stabilize. For projecting one cycle out (2024 → 2026), the full-trend default is defensible. For projecting further out (2024 → 2028+), consider applying a discount. Exposed in the UI as a "Trend persistence" three-button selector (Full / Partial / None) marked as advanced; the URL `?trend=0.5` parameter persists the choice across reloads.

### 4. `war_adj_discounted`

The incumbent's **most-recent-cycle WAR** (Wins Above Replacement, per [split-ticket's methodology](https://split-ticket.org/2025/08/15/deconstructing-war/)), party-signed.

- **What WAR is**: the residual from a regression that predicts a candidate's vote share from fundamentals (pres lean, state effects, *and an incumbency indicator with a coefficient ~1.7 House / ~3.0 Senate*). So WAR represents the candidate's **personal** effect above-and-beyond what a typical incumbent of their party would do.
- **Lookup**: from `raw_war.csv`. Primary key is `(name, party)`; state-aware fallback by `(last_name, party, state)` handles nickname/suffix variants (Rob vs Rob Jr., Pfluger vs Pfluer typos, etc.). Manual overrides (`WAR_OVERRIDES`) handle edge cases like Begich where raw data conflates two candidates.
- **Signing**: positive = D-favorable margin contribution. A D incumbent with WAR = +2.0 adds +2.0 (more D). An R incumbent with WAR = +2.0 adds −2.0 (more R, since "+2.0 R-overperformance" hurts the D-R margin).
- **Redistricting discount**: full weight (1.0×) if `lines == "2024"`; **half-weight** (0.5×) if the district was redrawn. A redrawn district means the WAR was earned on different turf and is less applicable to the new geography.
- **Open seats**: `war_adj = 0`. The retired incumbent's personal vote leaves with them.

#### Definition of "open seat"

An open seat is any race where the 2024 incumbent is **not on the 2026 general election ballot for this seat**. This includes:

- **Retirements** (Bacon NE-2, Connolly VA-11 [now refilled by Walkinshaw via special, so technically no longer open], Mark Green TN-7)
- **Deaths and resignations** (the special-election winner is treated as a freshman incumbent for 2026 if they're running again — Walkinshaw VA-11 is exactly this case)
- **Primary defeats** (the new nominee gets no inherited WAR)
- **Ambition-driven openings** (incumbent running for Senate, Governor, or other office — e.g. Moore UT-1 moving to UT-2)

In all of these cases, the previous incumbent's personal vote leaves with them and `war_adj = 0` for the seat they vacated.

#### Note on redistricting discount scope

The half-weight discount for redrawn districts (`lines != "2024"`) applies **only** to `war_adj_discounted`. The other terms (`rel_trend`, `incumbency_adj`, `challenger_adj`, `demographic_shift`) apply at full strength regardless of redistricting status:

- **`rel_trend`**: state-level trends apply uniformly within a state, including to new district shapes.
- **`incumbency_adj`**: structural incumbency benefits an incumbent against new constituents as well as old ones (campaign infrastructure, name recognition, fundraising network all carry over).
- **`challenger_adj`**: a challenger's personal effect applies to their actual race, not their prior one.
- **`demographic_shift`**: applies to the *new* district's demographic composition, not the old one.

Only WAR is discounted because WAR is specifically a *residual measured against a prior district's electorate*. When the electorate substantially changes, WAR's predictive validity decreases. Half-weight is a deliberate-but-imperfect compromise — the true discount likely varies by how much the district changed, but applying a uniform 0.5× is simpler and not obviously wrong.

### 5. `incumbency_adj`

The **structural** incumbency advantage that WAR's regression coefficient explicitly nets out. Because our baseline is presidential margin (no House/Senate incumbency baked in), this must be added separately to recover the incumbent's full expected performance.

```
incumbent running:
  House:  ±1.7   (+1.7 for D, −1.7 for R)
  Senate: ±3.0   (+3.0 for D, −3.0 for R)
open seat (per definition above):
  0       (no incumbent in 2026, and pres baseline never had an incumbency
           boost to remove)
```

For **freshman incumbents with no prior federal WAR** (e.g. Walkinshaw VA-11, who won the 2025 special after Connolly died), the ±1.7 / ±3.0 also serves as the generic incumbency placeholder — WAR can't do its job, so this term carries the full incumbency lift.

The convention `"incumbent_running" == True` means: the 2024 incumbent is running for re-election to the same seat in 2026. Anyone replacing them — special-election winner, primary winner over a defeated incumbent, or a new nominee for an open seat — gets `incumbent_running == False` for the purposes of this adjustment.

Calibrated from split-ticket's 2020 + 2024 WAR regressions (~1.7 House / ~3.0 Senate).

### 6. `challenger_adj`

Mirror of WAR but for **named challengers** listed in `HOUSE_CHALLENGERS` (load_data.py) and `CHALLENGERS` (senate_data.py).

- **Auto-WAR lookup** if the challenger has prior House/Senate data (Shawn Harris ran 2024 GA-14 → 12.5 WAR; Roy Cooper has no House data so a manual estimate is used).
- **Anti-double-count**: if the challenger's most recent race is the same district + same year already attributed to the incumbent's WAR, skip the challenger_adj (otherwise the same race contributes twice — once via the incumbent's WAR residual, once via the challenger's).
- **Manual WAR** (`"war": <value>`) for high-profile challengers without prior federal results (Cooper 5.5, Brown 7.0, Peltola 9.0, Osborn 12.0, LePage 3.0, etc.).
- **Source labels** in API output: `"wikipedia"` (primary-confirmed, no WAR data — UI hides this tag), `"manual"` (user-entered), `"YYYY House XX-NN"` (auto-matched). Default 0 for districts/states with no challenger entry.
- **No redistricting discount applied** — challenger WAR speaks to the candidate's personal effect against the *actual* 2026 electorate, regardless of whether the geometry changed.

### 7. `demographic_shift`

The slider-driven term. For each demographic group g:

```
shift_g = pct_g_in_geography × (slider_g − CATALIST_BASELINES[g])
```

- **Sliders are absolute group D−R margins**. Parking a slider at its Catalist 2024 baseline = "this group voted the same as 2024" → zero contribution.
- **Three axes**: race (white_nh, black, hispanic, asian), edu (college, non_college), age (under_30, 65+).
- **Anti-double-count across axes**: if sliders on ≥2 axes are moved from baseline, each axis's contribution is **half-weighted**. Two different axes describe the same voters from different angles — adding both at full strength counts those voters twice.

#### Catalist 2024 demographic baselines

These are **2024-cycle values** reflecting post-2024-election demographic vote patterns from the Catalist "What Happened" cycle analysis (with exit-poll aggregates filling gaps). Update when Catalist publishes the next cycle's report.

| Group       | Baseline | Interpretation                                  |
| ----------- | -------: | ----------------------------------------------- |
| white_nh    | **−14**  | whites went R+14 in 2024                        |
| black       | **+73**  | Black voters went D+73                          |
| hispanic    |  **+6**  | Hispanic voters went D+6                        |
| asian       | **+15**  | Asian voters went D+15                          |
| college     | **+12**  | college-educated D+12 (all-race; see note below)|
| non_college | **−12**  | non-college R+12 (all-race; see note below)     |
| under_30    | **+12**  | under-30 D+12                                   |
| 65+         |  **−5**  | 65+ R+5                                         |

**Scope note on college / non_college**: `pct_college` in the underlying data comes from ACS B15003 (educational attainment, population 25+, **all races** — not white-only). Many published Catalist reports report "white college / white non-college" splits separately because the racial education gap is large; the +12 / −12 baselines here are calibrated to the **all-race** definition that matches our denominator. If you import a Catalist headline number that's white-only and want to use it here, recompute it against the all-race base before plugging in.

**Future**: a `CATALIST_BASELINES_2020` stub exists in `model.py` (commented out) for eventual support of "2020-pattern" scenario presets (Hispanic D+25, white D−17, etc.). Not currently wired into the UI.

### Demographics data pipeline

- **Census ACS** 5-year tract-level data fetched for race, education, age, income, median age.
- **Redrawn states** (CA/TX/OH/NC/TN/MO/UT/FL/LA/AL): DRA Block Assignment Files map 2020 census blocks → 2026 districts, and tract-level ACS values are pop-weighted onto the new lines.
- `demo_source` field on each row tells you whether demographics are "real" (existing lines), "estimated" (redrawn), or "missing".

---

## Tossup threshold

Any geography with `|projection| ≤ 3.0` is flagged `is_tossup = true`. Still allocated to whichever side is on top in the seat count, but visually marked as competitive.

---

## Senate seat math

Senate uses a two-tier composition since only 35 of 100 seats are up in 2026:

```
pre-2026 baseline: 47 D / 53 R   (post-2024-election Senate)
of those, 35 seats up in 2026 → projected by the model
65 seats not up → assumed held by current party
```

Final D total = (D wins among 35 up-seats projected) + (47 − D incumbents whose seat is up).
Final R total = (R wins among 35 up-seats projected) + (53 − R incumbents whose seat is up).

Majority: D if ≥51, R if ≥51, tie at 50–50, else none.

---

## What the model doesn't do (limitations)

- **No Monte Carlo / uncertainty quantification**: point projections only, no distributions.
- **No within-cycle update mechanism**: the model doesn't ingest fresh polls or fundraising data once initialized.
- **No turnout differential modeling**: sliders adjust support margins, not turnout shares. A scenario where "Hispanics swing D+10 but turn out 30% less" can't be expressed.
- **Demographics are static**: 2023 ACS shares; no population-growth or cohort-aging effects.
- **No demographic-conditional downballot lag**: if a demographic shift implies a presidential pattern (e.g. Hispanic R-shift) but House Hispanics historically lag presidential trends, the model doesn't model that lag.
- **Axis half-weighting is a heuristic**: two- and three-axis activation both halve, which probably under-weights three-axis scenarios.
- **Pre-primary states have no named challenger** (TN, VA most H districts, NM-02, plus various open-primary states). Those races get only generic incumbency, not candidate-specific WAR.
- **Open seats lose both WAR and incumbency_adj**, which is conceptually correct but means the projection collapses to "fundamentals + environment + trend + demos" — any candidate-specific information for the open seat shows up only via the manual `challenger_adj` if entered.

## Versioning

- **v1** (initial): single projection formula, full-trend assumption, ambiguous open-seat definition, baseline vintage implicit.
- **v2** (this doc): added `trend_discount` parameter and UI, clarified open-seat definition, documented redistricting discount scope, stamped baseline vintage and college scope explicitly.
