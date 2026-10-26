export function Methodology() {
  return (
    <div className="bg-white rounded-lg shadow p-4 text-xs text-slate-600 leading-relaxed">
      <h2 className="text-sm font-semibold text-slate-800 mb-2">Methodology</h2>
      <p className="mb-2">
        Each district / state projection is{" "}
        <code className="px-1 bg-slate-100 rounded">
          pres_margin_2024 + uniform_swing + trend × 0.5 + WAR_blend + incumbency + challenger + demographic_shift
        </code>
        , where <b>pres_margin_2024</b> is the Harris-Trump margin (D-positive) in
        that district / state. The national environment defaults to <b>D+8.2</b>,
        built from poll <b>race crosstabs</b> rather than toplines: each group's
        generic-ballot margin (White, Black, Hispanic, Asian; two-way, so differing
        undecided rates don't distort it) is averaged across the latest national
        poll from each pollster that publishes a race breakdown (six polls ending
        Oct 4–23, 2026: NYT/Siena, CBS/YouGov, Economist/YouGov, Echelon, Fox News,
        Pew; weighted by √n). Each group's shift from its Catalist 2024 margin is
        weighted by its share of the electorate and added to the 2024 result
        (R+1.5): a +9.7-pt shift, of which white voters contribute +6.4. The same
        polls' toplines average D+8.6. Change it via the slider. For the House, the <b>uniform swing</b> is
        calibrated so that, with demographic sliders at default, the
        2024-turnout-weighted average of all 435 district margins equals the
        environment — i.e. the slider is the national House popular vote. (The
        Senate swings from the 2024 presidential popular vote, R+1.5.){" "}
        <b>Trend</b> is each district's / state's 2020→2024 presidential movement
        relative to the nation, applied at 0.5× by default (partial mean-reversion);
        the trend-persistence control also allows 0× or a partial reversal.
      </p>
      <p className="mb-2">
        <b>WAR (Wins Above Replacement)</b> is the candidate-quality adjustment from{" "}
        <a className="underline" href="https://split-ticket.org" target="_blank" rel="noreferrer">Split-Ticket</a>
        , measuring how much a candidate over/underperforms the presidential baseline
        in their seat. Only each office's last three cycles before 2026 are eligible
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
        vote partially but not fully transfers across office types. Same-race
        head-to-heads aren't double-counted. Nominees who aren't sitting members
        (open seats, or an incumbent lost renomination) get their own federal WAR
        record the same way challengers do, but no incumbency bonus.
        For Senate candidates with a gubernatorial track record (e.g. Roy Cooper NC),
        we pull their governor races into the same blend at a 0.5× cross-chamber
        discount — statewide personal vote partially but not fully transfers to a
        federal race. There are currently no per-candidate exemptions to this
        discount; the 2018 Bredesen TN-Senate race is the empirical anchor (his
        federal personal vote came in at roughly half his gubernatorial WAR). A
        small number of <b>per-cycle exclusions</b> apply (Collins 2014 vs Bellows
        was a 68%-31% blowout that would inflate her personal-vote signal); these
        are listed in code and trigger at blend time.{" "}
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
        <b>Generic incumbency</b> is +1.7 D-positive for D incumbents and -1.7 for R
        (per Split-Ticket's 2020 WAR analysis); Senate uses ±3.0. WAR explicitly
        excludes this structural incumbency baseline, so the two terms compose rather
        than double-count.
      </p>
      <p className="mb-2">
        <b>District demographics</b> are American Community Survey (ACS) 2023 5-year
        estimates from the U.S. Census Bureau, computed on current district boundaries
        (post-redistricting where applicable). <b>Group voting baselines</b> (slider
        zero-points) use Catalist 2024 D-R margins per group, matching the 2024
        presidential baseline the rest of the model is built on. Parking the sliders
        at default means each group votes as it did in 2024 — zero demographic
        deviation from the baseline. Moving a slider models that group voting
        differently than it did in 2024, as a deliberate counterfactual; the shift
        adds on top of the national environment.{" "}
        <b>Electorate composition shares</b> use Catalist 2022 (prior-midterm) values,
        since midterm turnout shape is the better analog for the 2026 voter pool than
        presidential-year turnout. ACS shares describe the whole population
        (including children and non-citizens), so each group's ACS share is rescaled
        by a national turnout factor — fit so that the turnout-weighted national
        average matches Catalist's 2022 share — and renormalized within each
        district / state / county. Both the 2024 group margins and the 2022
        composition shares come from the same source —{" "}
        <a className="underline" href="https://catalist.us/whathappened2024/" target="_blank" rel="noreferrer">
          Catalist's "What Happened 2024" national crosstabs
        </a>
        , with 2022 as the prior-cycle column. Race (or race × education) and age
        are alternative descriptions of the same voters, so when both are moved
        their shifts are averaged rather than stacked, weighted by how far each
        axis was moved.
      </p>
      <p className="mb-2">
        <b>Senate</b> projections add a state-level trend (state vs. national
        2020→2024 shift), applied at 0.5× — the same discount and the same
        national reference as the House trend. 65 not-up seats are assumed to hold
        their current party. Democrats need 51 seats for control; a 50-50 split is
        Republican control via VP Vance's tiebreak. Independents like Dan Osborn are
        counted with Democrats for majority purposes, though neither independent
        nominee is committed to caucusing with them. Primary-unresolved seats (e.g.
        Cornyn TX) suppress incumbent WAR and incumbency until the runoff resolves.
      </p>
      <p className="mb-2">
        <b>Win probabilities</b> come from 10,000 Monte Carlo simulations around the
        projection. Each simulation adds a national error (σ 2.5 pts), a
        census-region error (σ 1.2), a state error (σ 1.8) and a race-specific error
        (σ 3.2), so races in the same state and region miss together. The
        race-specific error is wider where we know less: open seats (+2.5 in
        quadrature) and House districts on new lines (+2.0). These σ values are
        modeling judgments, not fitted.
      </p>
      <p className="mb-2">
        <b>County-level overlays</b> use 2020 + 2024 presidential results aggregated to
        county / borough boundaries; Alaska supplements with{" "}
        <a className="underline" href="https://davesredistricting.org" target="_blank" rel="noreferrer">
          Dave's Redistricting
        </a>{" "}
        per-borough 2020 numbers (state doesn't publish official borough-level results).
        Estimated 2026 vote counts assume turnout at 79% of 2024, the midpoint of
        the last two midterm-to-prior-presidential ratios (2018/2016 ≈ 87%,
        2022/2020 ≈ 71%). These ratios differ substantially; a high-salience 2026
        midterm would fall toward the higher end. This is a tunable parameter and
        affects only the county-overlay vote-count display — not any projection,
        margin, or seat call.
      </p>
      <p className="text-[10px] text-slate-500 italic border-t pt-2 mt-2">
        Bucket thresholds: Tilt ≤3 pts · Lean 3-7 · Likely 7-13 · Safe &gt;13.
        Projections within ±3 pts are tilts, not predictions — model uncertainty is
        wider than the displayed precision. Demographic crosstabs are sample-based
        approximations. Win probabilities are conditional on the scenario you set:
        they capture polling and race-level error around it, not uncertainty in
        the inputs themselves.
      </p>
    </div>
  );
}
