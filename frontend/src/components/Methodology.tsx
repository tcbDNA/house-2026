export function Methodology() {
  return (
    <div className="bg-white rounded-lg shadow p-4 text-xs text-slate-600 leading-relaxed">
      <h2 className="text-sm font-semibold text-slate-800 mb-2">Methodology</h2>
      <p className="mb-2">
        Each district / state projection is{" "}
        <code className="px-1 bg-slate-100 rounded">
          margin_2024 + uniform_swing + rel_trend × 0.5 + WAR_blend + incumbency + challenger + demographic_shift
        </code>
        . The national environment defaults to <b>D+6.3</b> (current generic-ballot
        average per{" "}
        <a className="underline" href="https://votehub.com" target="_blank" rel="noreferrer">VoteHub</a>
        ); change it via the slider. <b>Uniform swing</b> = environment minus the 2024
        House popular vote (R+2.6). <b>Relative trend</b> is each district's 2020→2024
        movement vs. its state, applied at 0.5× by default (partial mean-reversion).
      </p>
      <p className="mb-2">
        <b>WAR (Wins Above Replacement)</b> is the candidate-quality adjustment from{" "}
        <a className="underline" href="https://split-ticket.org" target="_blank" rel="noreferrer">Split-Ticket</a>
        , measuring how much a candidate over/underperforms the presidential baseline
        in their seat. We use a time-weighted blend over the last three cycles
        (0.50 / 0.30 / 0.20; missing cycles zero-fill for mean regression), applied
        to both incumbent and challenger; same-race head-to-heads aren't double-counted.
        Governor records contribute at 0.5× cross-chamber for Senate candidates (e.g.
        Roy Cooper NC). 2014 cycles are excluded as too stale. <b>Generic incumbency</b>{" "}
        is +1.7 D-positive for D incumbents and -1.7 for R (per Split-Ticket's 2020
        WAR analysis); Senate uses ±3.0.
      </p>
      <p className="mb-2">
        <b>District demographics</b> are American Community Survey (ACS) 2023 5-year
        estimates from the U.S. Census Bureau, computed on current district boundaries
        (post-redistricting where applicable). <b>Group voting baselines</b> ("zero
        point" of the sliders) use{" "}
        <a className="underline" href="https://catalist.us/whathappened2024/" target="_blank" rel="noreferrer">
          Catalist's 2024 "What Happened" national crosstabs
        </a>{" "}
        for vote share by race × education × age; electorate composition uses Catalist
        2022 shares (midterm electorate proxy for 2026). Sliders model what happens if
        a group votes differently than 2022. Race × education and age axes are
        half-weighted when both are moved, to prevent double-counting.
      </p>
      <p className="mb-2">
        <b>Senate</b> projections add a state-level relative trend (state vs. national
        2020→2024 shift). 65 not-up seats are assumed to hold their current party.
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
        Estimated 2026 vote counts assume turnout midway between 2022 and 2024 levels
        (~84.5% of 2024).
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
