export function Methodology() {
  return (
    <div className="bg-white rounded-lg shadow p-4 text-xs text-slate-600 leading-relaxed">
      <h2 className="text-sm font-semibold text-slate-800 mb-2">Methodology</h2>
      <p className="mb-2">
        Each district / state projection is{" "}
        <code className="px-1 bg-slate-100 rounded">
          pres_margin_2024 + uniform_swing + rel_trend × 0.5 + WAR_blend + incumbency + challenger + demographic_shift
        </code>
        , where <b>pres_margin_2024</b> is the Harris-Trump margin (D-positive) in
        that district / state. The national environment defaults to <b>D+7.4</b>{" "}
        (current generic-ballot average per{" "}
        <a className="underline" href="https://votehub.com" target="_blank" rel="noreferrer">VoteHub</a>
        ); change it via the slider. <b>Uniform swing</b> = environment minus the 2024
        House popular vote (R+2.6) — i.e. how much the national vote moves vs. 2024.{" "}
        <b>Relative trend</b> is each district's 2020→2024 presidential movement vs.
        its state, applied at 0.5× by default (partial mean-reversion).
      </p>
      <p className="mb-2">
        <b>WAR (Wins Above Replacement)</b> is the candidate-quality adjustment from{" "}
        <a className="underline" href="https://split-ticket.org" target="_blank" rel="noreferrer">Split-Ticket</a>
        , measuring how much a candidate over/underperforms the presidential baseline
        in their seat. We use <b>per-record windowing</b>: each record is windowed
        by its own election type. A candidate's records are grouped by office (House
        / Senate / Governor); within each office group, records are sorted year-desc
        and the top three slot at weights 0.50 / 0.30 / 0.20 by recency rank — so a
        recent race is never discarded merely because the candidate is now seeking a
        longer-term-cycle office. Records from a different office than the race
        being projected (e.g. a House record feeding a Senate projection, or a
        gubernatorial record into either) take an additional <b>0.5× cross-chamber
        discount</b>, reflecting that personal vote partially but not fully transfers
        across office types. Sample-size shrinkage then applies on the surviving
        records: blend × n/(n+k) / (3/(3+k)) with k=1, normalized so three-record
        candidates are unaffected; n=1 candidates shrink to 0.667× of blend; n=2 to
        0.889×. The two adjustments are independent — weights discount <i>old</i>{" "}
        information, shrinkage discounts <i>thin</i> information. Same-race
        head-to-heads aren't double-counted.
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
        which the auto-match rejects on state mismatch (WV ≠ NC). It's also a
        single-cycle, high-shrinkage data point earned under WV-2018-specific
        conditions (teacher strike, coalfield-D pitch) that don't transfer to
        NC-09 2026. The override documents these reasons explicitly so the zero
        is auditable, not accidental. <i>Nick Begich (AK-AL, R) = 0</i>{" "}
        — 2024 race vs. Mary Peltola is a high-WAR outlier that won't repeat in 2026.{" "}
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
        differently than it did in 2024, as a deliberate counterfactual.{" "}
        <b>Electorate composition shares</b> use Catalist 2022 (prior-midterm) values,
        since midterm turnout shape is the better analog for the 2026 voter pool than
        presidential-year turnout. Both the 2024 group margins and the 2022
        composition shares come from the same source —{" "}
        <a className="underline" href="https://catalist.us/whathappened2024/" target="_blank" rel="noreferrer">
          Catalist's "What Happened 2024" national crosstabs
        </a>
        , with 2022 as the prior-cycle column. When two or more axes (race /
        education / age) are moved at once, total demographic shift is halved to
        prevent double-counting overlapping voter groups.
      </p>
      <p className="mb-2">
        <b>Senate</b> projections add a state-level relative trend (state vs. national
        2020→2024 shift), applied at 0.5× — the same partial-mean-reversion discount
        used for district relative trend, since both are extrapolated 2020→2024
        movements subject to the same decay. 65 not-up seats are assumed to hold
        their current party.
        Independents like Dan Osborn are assumed to caucus with Democrats for majority
        purposes. Primary-unresolved seats (e.g. Cornyn TX) suppress incumbent WAR and
        incumbency until the runoff resolves.
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
        approximations. Not a forecast or probabilistic model.
      </p>
    </div>
  );
}
