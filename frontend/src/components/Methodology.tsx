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
        that district / state. The national environment defaults to <b>D+8.3</b>,
        built from poll <b>race crosstabs</b> rather than toplines: each group's
        generic-ballot margin (White, Black, Hispanic, Asian; two-way, so differing
        undecided rates don't distort it) is averaged across the latest national
        poll from each pollster that publishes a race breakdown (eight polls ending
        Sep 22–Oct 23, 2026: NYT/Siena, CBS/YouGov, Economist/YouGov, Echelon, Fox
        News, Pew, Cygnal, Emerson; weighted by √n; ActiVote and Rasmussen are
        excluded). Asian figures come from three polls (NYT/Siena, Pew, Emerson);
        Economist/YouGov, Fox News and Pew publish race breakdowns for registered
        voters only. Each group's shift from its Catalist 2024 margin is
        weighted by its share of the electorate and added to the 2024 result
        (R+1.5): a +9.8-pt shift, of which white voters contribute +6.8. The same
        polls' toplines average D+9.0.
      </p>
      <p className="mb-2">
        By default the race sliders sit at those poll averages (white R+6.3, Black
        D+74.6, Hispanic D+29.4, Asian D+41.8), so each district swings by its own
        mix of groups (+9.6 nationally). The <b>uniform wave</b> (R+1.25) holds the
        part every district shares: the 2024 starting point (R+1.5) plus ~0.25 for
        "other" race voters, who have no slider — i.e. essentially no swing beyond
        what the demographics explain. The panel's <b>Total</b> (wave + sliders) is
        the national margin, D+8.3. For the House, the <b>uniform swing</b> is
        calibrated so that, with the demographic sliders at their 2024 values, the
        2024-turnout-weighted average of all 435 district margins equals the
        uniform wave; the sliders then add on top. (The Senate swings from the 2024
        presidential popular vote, R+1.5, which is already consistent.){" "}
        <b>Trend</b> starts from each district's / state's 2020→2024 presidential
        movement relative to the nation. Only the part that demographics and
        campaign intensity don't explain is eligible to carry forward: a
        2024-vote-weighted regression of district trend on the active frame's
        electorate shares (plus age) and an indicator for the seven 2024
        battleground states (where Trump gained less than nationally — campaign
        effort a midterm doesn't repeat) removes both parts; states use the same
        coefficients, centered nationally. The <b>residual trend defaults to
        0×</b>: in the 2025 New Jersey and Virginia governor's races, counties'
        2020→2024 trend predicted no further movement once demographics were
        controlled (coefficient −0.05, robust SE 0.11). That test has limits —
        two states, an off-year election, county-level data — so the
        trend-persistence control keeps partial (0.5×), full (1×) and reversal
        (−0.5×) as scenarios.
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
        vote partially but not fully transfers across office types. Incumbents
        running on redrawn lines carry 0.5× of their WAR, since it was earned with a
        different electorate. Same-race head-to-heads aren't double-counted.
        Nominees who aren't sitting members
        (open seats, or an incumbent lost renomination) get their own federal WAR
        record the same way challengers do, but no incumbency bonus.
        For Senate candidates with a gubernatorial track record (e.g. Roy Cooper NC),
        we pull their governor races into the same blend at a 0.5× cross-chamber
        discount — statewide personal vote partially but not fully transfers to a
        federal race. There are currently no per-candidate exemptions to this
        discount; the 2018 Bredesen TN-Senate race is the empirical anchor (his
        federal personal vote came in at roughly half his gubernatorial WAR). A
        small number of <b>per-cycle exclusions</b> apply (Collins 2014 vs Bellows
        was a 68%-31% blowout that would inflate her personal-vote signal; Sullivan
        2014's number reflects Begich's incumbency rather than Sullivan); these
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
        than double-count. California districts where the top-two primary sent two
        candidates of the same party to November are locked to that party.
      </p>
      <p className="mb-2">
        <b>District demographics</b> are American Community Survey (ACS) 2023 5-year
        estimates from the U.S. Census Bureau, computed on current district boundaries
        (post-redistricting where applicable). <b>Group voting baselines</b> (slider
        zero-points) use Catalist 2024 D-R margins per group, matching the 2024
        presidential baseline the rest of the model is built on: a slider at its
        2024 value adds no demographic shift. The defaults are the poll averages
        above, so each group's movement since 2024 lands on the districts where
        that group lives; moving a slider further models a different swing, and the
        shift adds on top of the uniform wave.{" "}
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
        axis was moved. The <b>race × education</b> frame also starts from poll
        data: white college graduates at D+16.6 (+14.7 since 2024) and white
        non-college voters at R+22.4 (+4.9), from NYT/Siena, CBS/YouGov and Pew;
        the non-white cells (reported by only one poll) get their 2024 margin plus
        the non-white shift from the race data. Switching frames adjusts the
        uniform wave so the national total stays the same. Age sliders stay at
        their 2024 values.
      </p>
      <p className="mb-2">
        <b>Senate</b> projections treat the state-level trend (state vs. national
        2020→2024 shift) the same way as the House trend: residualized with the
        district coefficients, centered on its national mean (weighted by 2024
        votes across all 50 states), default weight 0×. 65 not-up seats are assumed to hold
        their current party. Democrats need 51 seats for control; a 50-50 split is
        Republican control via VP Vance's tiebreak. Independents like Dan Osborn are
        counted with Democrats for majority purposes, though neither independent
        nominee is committed to caucusing with them. Appointed senators who haven't
        yet won an election (Moody FL, Husted OH, Graham SC) get no incumbency
        bonus, and a seat whose primary is still unresolved carries no incumbent
        WAR or incumbency until it is.
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
        County (or county-slice) projections are shifted uniformly so they add up
        exactly to the district or Senate projection. Estimated 2026 vote counts assume turnout at 79% of 2024, the midpoint of
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
