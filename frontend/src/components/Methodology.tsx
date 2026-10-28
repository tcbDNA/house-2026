export function Methodology() {
  return (
    <div className="bg-white rounded-lg shadow p-4 text-xs text-slate-600 leading-relaxed">
      <h2 className="text-sm font-semibold text-slate-800 mb-2">Methodology</h2>
      <p className="mb-2">
        Each district / state projection is{" "}
        <code className="px-1 bg-slate-100 rounded">
          pres_margin_2024 + uniform_swing + trend_weight × residual_trend + WAR_blend + incumbency + challenger + demographic_shift
        </code>
        , where <b>pres_margin_2024</b> is the Harris-Trump margin (D-positive) in
        that district / state. The national environment defaults to <b>D+9.4</b>,
        built from poll <b>race crosstabs</b> rather than toplines. <b>National
        level:</b> each group's generic-ballot margin (White, Black, Hispanic,
        Asian; two-way, so differing undecided rates don't distort it) is averaged
        across the latest national poll from each pollster that publishes a race
        breakdown (ten polls ending Sep 22–Oct 26, 2026: NYT/Siena, CBS/YouGov,
        Economist/YouGov, Echelon, Fox News, Pew, Cygnal, Emerson, Bedrock Research
        for the Rainey Center, and Marist, which reports race only as White vs
        Non-white and so counts for the white groups only; ActiVote and Rasmussen
        are excluded), weighted by √(subgroup sample size) — derived
        from the group margins of error where only those are published (Fox, Pew
        2024), else total n × the group's electorate share (Pew 2026, Cygnal) or its
        published sample share (Marist, Bedrock).
        Each group's shift from its Catalist 2024 margin,
        weighted by its share of the electorate, sums to a +10.9-pt shift from the
        2024 result (R+1.5). Measured from Pew's 2024 validated-voter margins
        instead, the shift is +9.4 (D+7.9) — an option in the settings. The same
        polls' toplines average D+9.0.{" "}
        <b>Pattern across groups:</b> each pollster's 2026 crosstab is compared
        with its own final 2024 pre-election poll, net of the change in its
        topline, which cancels persistent crosstab bias and keeps 2024's polling
        miss out of the level: r = (2026 group − 2024 group) − (2026 topline −
        2024 topline), combined across pollsters with inverse-variance weights
        (both years' sampling error, design effect 1.5); if leaving out any one
        pollster moves a group's average by more than 1.5 pts, its weighted
        median is used instead. Eight of the ten pollsters have a matched 2024 poll
        (Cygnal's is its 2024 generic congressional ballot, the same question as
        its 2026 poll; the others are presidential vote). Each group's shift is
        the national shift plus its r minus the share-weighted mean r, so the
        national level is unchanged: white +9.0, Black +11.6, Hispanic +21.3
        (weighted median);
        Asian keeps its poll-average shift (+21.5; NYT/Siena's 2024 poll had no
        Asian column), and "other" takes the national shift. In the race ×
        education frame the white college (+8.0, weighted median) and non-college
        (+9.8) cells are
        matched the same way (NYT/Siena, CBS/YouGov, Pew) and the non-white cells
        take the non-white groups' average shift.
      </p>
      <p className="mb-2">
        By default each race slider sits at its group's Catalist 2024 margin plus
        that shift (white R+6.2, Black D+82.4, Hispanic D+29.7, Asian D+42.9), so
        each district swings by its own mix of groups (+10.6 nationally). The
        <b>uniform wave</b> (R+1.2) holds the part every district shares: the 2024
        starting point (R+1.5) plus ~0.3 for "other" race voters, who have no
        slider — i.e. essentially no swing beyond what the demographics explain.
        The panel's <b>Total</b> (wave + sliders) is the national margin, D+9.4. For the House, the <b>uniform swing</b> is
        calibrated so that, with the demographic sliders at their 2024 values, the
        2024-turnout-weighted average of all 435 district margins equals the
        uniform wave; the sliders then add on top. (Correction, Oct 27: in the
        12 states without 2024 precinct results the district weights were 2020
        votes; they are now 2024 totals, which moves every House projection
        0.07–0.11 toward D and takes WI-01 from R+0.01 to D+0.09.) (The Senate swings from the 2024
        presidential popular vote, R+1.5, which is already consistent.){" "}
        <b>Trend</b> starts from each district's / state's 2020→2024 presidential
        movement relative to the nation. A 2024-vote-weighted regression of
        district trend on the active frame's electorate shares (plus age) and an
        indicator for the seven 2024 battleground states splits it into a
        demographic part, a battleground part (Trump gained less there than
        nationally) and the rest. The <b>demographic part is removed</b>, so the
        trend doesn't double count group movement the sliders already model. The
        <b>battleground part is kept</b>: all seven battlegrounds (AZ, GA, MI, NV,
        NC, PA, WI) have a Senate or governor's race this year, so the campaign
        effect may repeat. States use the same coefficients, centered nationally.
        What remains is carried at <b>0.5× by default — a judgment call</b> (half
        the movement persists); the trend-persistence control offers none (0×),
        full (1×) and a partial reversal (−0.5×). A limited check: in the 2025 New
        Jersey and Virginia governor's races, counties' 2020→2024 trend predicted
        no further movement once demographics were controlled (coefficient +0.02,
        robust SE 0.11) — but governor's races differ from federal ones, and the
        test covers two states, an off-year election and county-level data.
      </p>
      <p className="mb-2">
        <b>WAR (Wins Above Replacement)</b> is the candidate-quality adjustment from{" "}
        <a className="underline" href="https://split-ticket.org" target="_blank" rel="noreferrer">Split-Ticket</a>
        . Split Ticket measures each candidate's result against a fundamentals
        baseline — seat partisanship (through the same-year presidential margin),
        incumbency, demographics and money — not just the presidential result, so
        WAR is net of incumbency. Only each office's last three cycles before 2026 are eligible
        (House 2020–2024, Governor 2014+, Senate 2008+). We use <b>per-record
        windowing</b>: a candidate's eligible records are grouped by office (House /
        Senate / Governor); within each office group, records are sorted year-desc
        and the top three slot at weights 0.50 / 0.30 / 0.20 by recency rank — so a
        recent race is never discarded merely because the candidate is now seeking a
        longer-term-cycle office. Missing slots count as zero, which regresses
        thin records toward the mean: one race carries 0.5× of its WAR, two races
        0.8×, three races 1.0×. If records from several offices push the recency
        weights past 1.0 in total, they're rescaled to sum to 1.0. Records from a
        different office than the race being projected (e.g. a House record feeding
        a Senate projection, or a gubernatorial record into either) take an
        additional <b>0.5× cross-chamber discount</b>, reflecting that personal
        vote partially but not fully transfers across office types. Incumbents
        running on redrawn lines carry 0.5× of their WAR, since it was earned with a
        different electorate. Same-race head-to-heads aren't double-counted.
        Nominees who aren't sitting members
        (open seats, or an incumbent lost renomination) get their own federal WAR
        record the same way challengers do, but no incumbency bonus.
        For Senate candidates with a gubernatorial track record (e.g. Roy Cooper NC),
        we pull their governor races into the same blend at a 0.5× cross-chamber
        discount — statewide personal vote partially but not fully transfers to a
        federal race. Every WAR record is Split Ticket's except Cooper's two governor
        races (2016, 2020): Split Ticket publishes no governor WAR, so those are his
        margin minus the same-day presidential margin, kept as a deliberate choice
        (+2.0 to North Carolina). There are currently no per-candidate exemptions to this
        discount; the 2018 Bredesen TN-Senate race is the empirical anchor (his
        federal personal vote came in at roughly half his gubernatorial WAR). A
        small number of <b>per-cycle exclusions</b> apply (Collins 2014 vs Bellows
        was a 68%-31% blowout that would inflate her personal-vote signal; Sullivan
        2014 vs Begich, D+18.8, is excluded as a judgment call — an outlier against
        his 2020 record, from twelve years ago — and Alaska is shown both ways: in
        the model R+2.2 without it, D+3.4 with it; after the poll blend D+0.6 and
        D+2.3); these are listed in code and trigger at blend time.{" "}
        <b>Manual WAR overrides</b> are applied in a small number of cases where the
        blended value would misrepresent expected 2026 performance. Currently:{" "}
        <i>Richard Ojeda (NC-09, D) = 0</i> — his only prior race is 2018 WV-03,
        which is outside the House window and earned under WV-2018-specific
        conditions (teacher strike, coalfield-D pitch) that don't transfer to
        NC-09 2026. The override documents these reasons explicitly so the zero
        is auditable, not accidental. <i>Nick Begich (AK-AL, R) = 0</i>{" "}
        — 2024 race vs. Mary Peltola is a high-WAR outlier that won't repeat in 2026.{" "}
        <i>Cleo Fields (LA-06, D) = 0</i> — a placeholder in the redrawn R+32 seat
        who is unlikely to run; his 2024 WAR was earned on the old D-leaning lines.{" "}
        <b>Generic incumbency</b> in the House is a setting, default ±3.0 (D-positive
        for D incumbents): Split Ticket's most recent estimate, and the 2024 WAR
        records were measured with it already removed. Their 2020 analysis put it at
        1.7, kept as a scenario (House median 241 instead of 238 D — most competitive
        seats are R-held). Senate uses ±3.0. WAR explicitly
        excludes this structural incumbency baseline, so the two terms compose rather
        than double-count. California districts where the top-two primary sent two
        candidates of the same party to November are locked to that party.
      </p>
      <p className="mb-2">
        <b>District demographics</b> are American Community Survey (ACS) 2023 5-year
        estimates from the U.S. Census Bureau, computed on current district boundaries
        (post-redistricting where applicable). <b>Group voting baselines</b> (slider
        zero-points) use Catalist 2024 D-R margins per group, matching the 2024
        presidential baseline the rest of the model is built on: a slider at its
        2024 value adds no demographic shift. The defaults are 2024 plus the
        shifts above, so each group's movement since 2024 lands on the districts where
        that group lives; moving a slider further models a different swing, and the
        shift adds on top of the uniform wave.{" "}
        <b>Electorate composition:</b> ACS shares describe the whole population
        (including children and non-citizens), so each group's ACS share is rescaled
        by a national turnout factor — fit to Catalist's 2022 midterm electorate,
        then with every non-white factor scaled together so the <b>2026 white share
        is 74%</b> — and renormalized within each district / state / county. 74%
        keeps the midterm logic (Catalist: 76% white in 2022, 72% in 2024) while
        allowing for demographic drift since 2022 and a more diverse early vote; the
        settings range is 72–76%, across which the national margin moves only from
        D+9.5 to D+9.3. Turnout uncertainty also enters the simulation as the
        composition error term. Both the 2024 group margins and the 2022
        composition shares come from the same source —{" "}
        <a className="underline" href="https://catalist.us/whathappened2024/" target="_blank" rel="noreferrer">
          Catalist's "What Happened 2024" national crosstabs
        </a>
        , with 2022 as the prior-cycle column. Race (or race × education) and age
        are alternative descriptions of the same voters, so when both are moved
        their shifts are averaged rather than stacked, weighted by how far each
        axis was moved. The <b>race × education</b> frame starts from the matched
        shifts too: white college graduates at D+9.9 (+8.0 since 2024) and white
        non-college voters at R+17.5 (+9.8), matched with NYT/Siena, CBS/YouGov and
        Pew, averaging to the white race shift; the non-white cells get their 2024
        margin plus the non-white groups' average shift (+16.2). The four cells
        cover every voter, so in that frame the uniform wave is the 2024 level
        (R+1.5) and the national total stays the same. Age sliders stay at their
        2024 values.
      </p>
      <p className="mb-2">
        <b>Senate</b> projections treat the state-level trend (state vs. national
        2020→2024 shift) the same way as the House trend: residualized with the
        district coefficients (demographic part removed, battleground part kept),
        centered on its national mean (weighted by 2024 votes across all 50
        states), default weight 0.5×. 65 not-up seats are assumed to hold
        their current party. Democrats need 51 seats for control; a 50-50 split is
        Republican control via VP Vance's tiebreak. The four independent nominees —
        Dan Osborn (NE), Brian Bengs (SD), Todd Achilles (ID) and Seth Bodnar (MT) —
        are assumed to caucus with Democrats if they win, so they count toward
        Democratic control; the Senate summary also shows P(D control) if none of
        them does (69.4% vs 65.3% by default; Osborn's race is nearly all of the
        difference). Appointed senators who haven't
        yet won an election (Moody FL, Husted OH, Graham SC) get no incumbency
        bonus, and a seat whose primary is still unresolved carries no incumbent
        WAR or incumbency until it is.
      </p>
      <p className="mb-2">
        <b>Poll blend.</b> Every Senate race with a polling average is projected as
        w × (polling average + scenario change) + (1 − w) × model, where the
        scenario change is how far the current sliders and settings move the model
        from its default, so the sliders still move every race. w = 0.7 with at
        least three polls in the average, scaled down linearly below that (0.47
        with two, 0.23 with one) and 0 with none. Montana, Idaho and South Dakota,
        whose nominee is an independent, take w = 1 with the same scaling, because
        the partisan baseline can't describe an independent with cross-party
        appeal; Nebraska, the fourth, blends polls and model like a two-party race.
        All four get 3 extra points of race-level error (in quadrature). The averages
        start from RealClearPolling's with any Rasmussen poll removed (ActiVote is
        never used, nor Wedgewood, which admitted its polls were fabricated; in
        Maine, Echelon's NetChoice poll, which RCP lists but hasn't yet averaged,
        is counted ahead of RCP); where a newer poll came out after RCP last updated the
        average, or RCP publishes none, the average is recomputed from the most
        recent poll by each pollster in the last three weeks (as of Oct 28: Kansas,
        Georgia, Iowa and Alabama, plus
        Mississippi, Nebraska, Arkansas and Idaho, which RCP doesn't average).
        Louisiana and 11 safe races have no recent poll and use the model alone.
        The blend takes Texas from the model's R+1.5 to Talarico D+1.0, Nebraska
        from R+4.9 to Ricketts +1.2 and Alaska from R+2.2 to D+0.6; P(D control)
        is 69.4% (59.5% on the model alone; 68.4% / 70.1% with w = 0.6 / 0.8). <b>Montana</b> is a three-way
        race (Daines withdrew in March): Kurt Alme (R) vs Seth Bodnar (I), with
        Alani Bankhead (D) polling a distant third, plus a Libertarian; its polling
        margin is Bodnar − Alme from RCP's three-way average (Alme +12.0, two
        polls, so 2/3 polls and 1/3 model). <b>Nebraska</b> (Osborn vs Ricketts, no
        Democratic nominee) has five recent polls, Osborn +0.4; blended 0.7 / 0.3
        with the model's Ricketts +4.9, it projects Ricketts +1.2 (Osborn 42%). As
        a cross-check, Economist/YouGov had Fischer +7 over
        Osborn in late October 2024 and Fischer won by 6.7; YouGov's 2026 poll has
        Osborn +1, an 8-point move — about the size of the national swing since
        2024.
      </p>
      <p className="mb-2">
        <b>Where w = 0.7 comes from.</b> A backtest reruns the model's structure
        for the 2022 and 2024 Senate races (each year's generic-ballot environment,
        WAR only from records available before that election) and compares it and
        RealClearPolling's final average with the results. With a separate
        intercept per year — each year's polling miss is mostly shared across
        races, which the simulation's national error covers — the best pooled
        weight on polls is 0.71 (error 3.42 points, vs 3.75 for polls alone and
        5.03 for the model alone). Year by year it is unstable (0.74 in 2022, 0.32
        in 2024), so it is pooled and rounded. The sample is only the competitive
        two-party races RCP averaged (14 in 2022, 11 in 2024): no race with an
        independent nominee had an RCP average, so none is in the estimate, and
        the independents' w = 1 is a judgment — the model missed McMullin (2022)
        and Osborn (2024) by 17+ points.
      </p>
      <p className="mb-2">
        <b>Win probabilities</b> come from 10,000 Monte Carlo simulations around the
        projection. Each simulation adds a national error (σ 2.5 pts), a
        census-region error (σ 1.2), a state error (σ 1.8) and a race-specific error
        (σ 3.2), so races in the same state and region miss together. The
        race-specific error is wider where we know less: open seats (+2.5 in
        quadrature) and House districts on new lines (+2.0, scaled by the share of
        the district that is new). Two more national terms apply uniformly to
        every race: <b>composition</b> (σ 1.0, who turns out) and <b>level
        measurement</b> (σ 1.0, crosstab sampling and the choice of 2024 baseline,
        which alone moves the level 1.5 pts). <b>Group errors</b> let places with
        similar electorates miss together across states: each simulation draws a
        deviation for every slider group in the active frame (white σ 2.0, Black
        4.1, Hispanic 5.8, Asian 8.1 — the group's sampling error combined with a
        non-sampling allowance of 1 / 3 / 4 / 5 pts), demeans the draws with
        national shares so the national total is unchanged, and adds each
        district's and state's share-weighted sum. Together they raise the
        standard deviation of the simulated national margin from 2.6 to 2.9 pts
        and the average correlation among the five most Hispanic competitive
        districts from 0.34 to 0.52. These are all polling error around the
        scenario; the σ values and allowances are modeling judgments, not fitted.
      </p>
      <p className="mb-2">
        <b>County-level overlays</b> use 2020 + 2024 presidential results aggregated to
        county / borough boundaries; Alaska supplements with{" "}
        <a className="underline" href="https://davesredistricting.org" target="_blank" rel="noreferrer">
          Dave's Redistricting
        </a>{" "}
        per-borough 2020 numbers (state doesn't publish official borough-level results),
        and Connecticut uses its nine planning regions (the Census Bureau's county
        equivalents since 2022), built from the state's official town results.
        Each county slice of a district (and each county of a Senate state) is
        projected from its own pieces: its 2024 margin, the demographic shift and
        residual trend of its county (item-2 coefficients with the intercept, the
        county's shares and battleground status), the residual shrunk toward the
        district's or state's with weight votes / (votes + 25,000) since small
        counties' shifts are noisy, plus the district's (or Senate's) uniform swing
        and candidate effects. One reconciling shift per district or state then
        makes the slices add up exactly to its projection. In the 12 states
        without 2024 precinct results (AK, AR, CT, ID, ME, MI, ND, NJ, OK, OR,
        PA, SD), a split county's slices are estimated by raking their 2020
        D and R votes to the actual 2024 county and district totals. Their
        slices still take their county's residual, since the county results
        are real, except Alaska's: its borough results are estimated, so its
        slices take the district's residual and its boroughs the state's. This changes only the map shading, never a projection. Estimated 2026 vote counts use each race's own Kalshi turnout market: the
        market-implied median total vote divided by the 2024 presidential vote —
        the state's Senate market (else its governor market) for a state's
        counties, and the district's House market for its slices (e.g. Georgia
        85%, Texas 94%, Mississippi 66% of 2024). It affects only the
        county-overlay vote-count display — not any projection, margin, or seat
        call.
      </p>
      <p className="text-[10px] text-slate-500 italic border-t pt-2 mt-2">
        Bucket thresholds: Tilt ≤3 pts · Lean 3-7 · Likely 7-13 · Safe &gt;13.
        Projections within ±3 pts are tilts, not predictions — model uncertainty is
        wider than the displayed precision. Demographic crosstabs are sample-based
        approximations. Win probabilities are conditional on the scenario you set:
        they capture polling error around it — including composition (who turns
        out), level measurement and group-level crosstab error — and race-level
        error, not uncertainty in the scenario inputs themselves.
      </p>
    </div>
  );
}
