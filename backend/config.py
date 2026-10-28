"""Model settings. Every model-v4 change sits behind a flag (default on) so
runs can be compared with and without it. API requests may override any
field via `settings`; unknown keys are rejected.

Settings is frozen (hashable) so derived quantities can be cached per
settings value.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, replace

# Catalist's 2022 electorate share for white voters, reproduced exactly when
# the white-share target is switched off.
CATALIST_2022_WHITE_SHARE = 0.7581

# Default trend weight (multiplier on the carried 2020→2024 trend, after the
# demographic part is removed). 0.5 is a judgment call: half the residual
# trend persists. The 2025 NJ/VA governor check (county coefficient +0.02,
# robust SE 0.11; analysis/trend_weight_nj_va_2025.txt) is a limited test —
# governor's races differ from federal ones — not the basis for the
# default. 0, 1 and −0.5 remain scenario options. A scenario parameter, not
# a Settings flag.
DEFAULT_TREND_WEIGHT = 0.5

GROUP_BASELINES = ("catalist", "pew_validated")

# Design effect for poll sampling errors: SE of a two-way margin ≈
# 200 × sqrt(p(1 − p) × DESIGN_EFFECT / n). Used for the inverse-variance
# weights on pollster-matched changes and for the group-error sigmas.
DESIGN_EFFECT = 1.5


@dataclass(frozen=True)
class Settings:
    # Item 1 — electorate composition. Target white share of the 2026 national
    # electorate (Catalist: 76% in 2022, 72% in 2024). 0.74 keeps the midterm
    # logic while allowing for demographic drift since 2022 and a more diverse
    # early vote. Reached by scaling every non-white turnout factor by one
    # common factor; age factors are untouched.
    white_share_enabled: bool = True
    white_share: float = 0.74

    # Item 2 data fixes — scale the new-lines rules by core retention instead
    # of all-or-nothing: incumbent WAR × (1 − 0.5 × share of the district the
    # incumbent didn't represent on the 2024 lines), and the simulation's
    # new-lines error × (share of the district new vs. its largest 2024
    # predecessor). Off: WAR × 0.5 and the full extra error on any district
    # whose lines label isn't "2024".
    core_retention_scaling: bool = True

    # Item 5 — House incumbency bonus (D−R margin points) for a sitting D/R
    # incumbent running again. Default 3.0: Split Ticket's most recent
    # estimate (2024 write-up), and the 2024 WAR records — half of each
    # incumbent's WAR weight — were measured with it already removed. 1.7
    # (Split Ticket's 2020 House WAR analysis) is a scenario.
    house_incumbency: float = 3.0

    # Senate poll blend (senate_model). Every Senate race with a polling
    # average (data/senate_poll_averages.csv: RCP-style, Rasmussen removed,
    # two-party) is projected as w × (polling average + scenario change) +
    # (1 − w) × the model's projection. w = senate_poll_weight with at least
    # senate_poll_full_n recent polls, scaled down linearly below that, 0 with
    # none. Independent races (NE, MT, ID, SD) use polls only (w = 1, same
    # scaling). 0.7 is the 2022/2024 backtest's best weight with a separate
    # intercept per year (analysis/senate_backtest.txt).
    senate_poll_blend: bool = True
    senate_poll_weight: float = 0.7
    senate_poll_full_n: float = 3.0
    # Nebraska (Osborn (I) vs Ricketts) blends polls and model like a
    # two-party race (w = senate_poll_weight) instead of polls only (user
    # decision, Oct 27). It keeps the independent races' extra error.
    senate_nebraska_model_blend: bool = True

    # Governors (governor_model). Fundamentals = governor_partisan_slope ×
    # (2024 presidential margin + national swing + demographic shift + trend,
    # each as in the state's Senate race) + candidate effects: the WAR blend
    # with Governor as the office, and ± governor_incumbency for an incumbent
    # who has won a governor's election (successors get none). The same
    # governor_incumbency nets the incumbent's edge out of computed governor
    # WAR records (subtracted for the incumbent, added back for the opponent).
    # Polls blend as in the Senate (w with at least governor_poll_full_n
    # polls, scaled down below; polls only for independents). Governor races
    # get governor_race_sigma_extra more race-level error, in quadrature.
    # Defaults from the 2018/2022 calibration with a single governor record at
    # full weight (analysis/governor_backtest.txt, user decision Oct 28):
    # slope 0.677 (SE 0.057), incumbency 6.55 (SE 1.53), w 0.788 (SE 0.058);
    # race error from the blended projection's error (SD 4.20 -> extra 1.6)
    # and the model's alone (SD 9.79 -> 9.0). The free fit with half-weighted
    # single records (incumbency 9.3) was rejected: about 3 points came from
    # four blue-state Republican landslides and about 2.7 from the half weight.
    governor_partisan_slope: float = 0.68
    governor_incumbency: float = 6.55
    governor_poll_blend: bool = True
    governor_poll_weight: float = 0.79
    governor_poll_full_n: float = 3.0
    governor_race_sigma_extra: float = 1.6
    # Race error scaled by the poll weight (user decision, Oct 28): extra² =
    # f × governor_race_sigma_extra² + (1 − f) × governor_race_sigma_extra_no_polls²,
    # f = the race's poll weight / governor_poll_weight (1 on polls only).
    governor_race_sigma_extra_no_polls: float = 9.0
    # Governor WAR rules (user decisions, Oct 28). Rematch: a challenger's
    # governor record from a race against the sitting incumbent is dropped
    # (the incumbent keeps it, as in the House model). Third candidate:
    # computed records from races where a third candidate won more than 5%
    # are left out (they measure that candidate as much as the nominees).
    governor_war_drop_rematch: bool = True
    # A candidate whose only governor record is one race gets full weight on it
    # instead of 0.5 (governor WAR only; user decision Oct 28: it fits the
    # 2018/2022 races better, MAE 7.16 vs 7.47). House and Senate unchanged.
    governor_war_single_record_full: bool = True
    # Parameter uncertainty (user decision, Oct 28): each simulation draws one
    # slope and one incumbency value (the calibration's SEs and correlation),
    # shared by every governor race; a race moves by its sensitivity to each
    # ((1 − w) × its fundamentals for the slope, (1 − w) × its incumbency
    # terms for incumbency).
    governor_param_draws: bool = True
    governor_slope_se: float = 0.057
    governor_incumbency_se: float = 1.53
    governor_slope_incumbency_corr: float = -0.22
    # Model–poll disagreement (user decision, Oct 28): a race whose polls and
    # model disagree gets governor_gap_sigma_factor × |model − polls| more
    # race-level error, in quadrature (model and polls at the default
    # scenario; races without polls, or on polls only, get none). 0 turns it off.
    # The 2018/2022 backtest finds no relation between the gap and the blend's
    # error where polls are plentiful (kappa 0, 95% interval 0-0.17); it has no
    # sparse-poll races, so 0.5 (the user's fallback) applies only where there
    # are fewer than governor_gap_max_polls effective polls (user decision Oct 28).
    governor_gap_sigma_factor: float = 0.5
    # Apply the gap term only where polling is sparse: fewer than this many
    # effective polls (user decision, Oct 28: option (c)). 0 = every race.
    governor_gap_max_polls: float = 3.0
    governor_war_exclude_third_candidate: bool = True

    # Item 7 — county overlay (overlay.py). Project each county slice from its
    # own 2024 margin, demographic shift and residual trend (shrunk toward its
    # district's / state's with weight votes / (votes + k), 2024 votes), plus
    # the district's / state's swing and candidate effects and one reconciling
    # shift. Off: every slice shifted by the same amount. Overlay only.
    overlay_slice_projections: bool = True
    overlay_shrink_k: float = 25000.0
    # In the 12 states without 2024 precinct results (AK AR CT ID ME MI ND NJ
    # OK OR PA SD), estimate each slice's 2024 votes by raking its 2020
    # precinct D and R votes to the actual 2024 county and district totals
    # (build_slices_from_github.py). Off: 2020 margin + the district's
    # 2020→2024 shift, weighted by 2020 votes. Overlay only.
    overlay_raked_slices: bool = True
    # In those 12 states the county results are real (only the split within
    # a county is estimated), so each slice takes its county's residual
    # trend, shrunk toward the district's, as elsewhere — except Alaska,
    # whose borough results are estimated and keep the district's. Off:
    # every slice there takes the district's residual. Overlay only.
    overlay_estimated_slice_trends: bool = True

    # District weights (model.district_turnout): each district's 2024
    # presidential votes, which set the national total, the electorate
    # composition fit and the trend regression. In the 12 states without
    # 2024 precinct results the slice totals were 2020 votes until Oct 27;
    # now they are the raked 2024 totals (official 2024 county results split
    # by district). A data correction (user decision, Oct 27). Off: those
    # states' 2020 votes, as before.
    district_weights_2024_votes: bool = True

    # Item 2 — residualized trend (trend.py). Remove from the carried trend
    # the part explained by the active frame's demographic shares (+ age, +
    # intercept) and/or the 2024 battleground-state part; trend_discount then
    # applies to what's left. Both off = the raw 2020→2024 trend, as before.
    # Demographic part removed by default, so the trend doesn't double count
    # group movement the sliders already model. Battleground part kept by
    # default: all seven 2024 battlegrounds (AZ GA MI NV NC PA WI) have a
    # Senate or governor's race in 2026, so the campaign effect may repeat.
    trend_remove_demographic: bool = True
    trend_remove_battleground: bool = False
    # The regression basis always includes the age shares (fixed per frame);
    # this switch exists only to measure what including age does.
    trend_include_age: bool = True
    # Center the states' carried trend on its national mean (weighted by
    # official 2024 votes across all 50 states, so it doesn't depend on which
    # seats are up) when residualizing. The district regression's
    # intercept absorbs a turnout-composition offset (+0.99: districts weight
    # 2020 margins by 2024 votes) that state-level trends don't share (+0.43),
    # so uncentered state residuals average -0.6 and would tilt every Senate
    # race ~0.3 pts R. The House needs no centering: its calibration absorbs
    # any constant.
    trend_center_states: bool = True

    # Item 3 — group shifts (environment.py). Weight each pollster's group
    # margin by the square root of that group's sample size (published
    # subgroup n, or total n × the group's published share where only
    # percentages are given) instead of the poll's total n.
    subgroup_n_weights: bool = True
    # Count polls whose race breakdown is only White vs Non-white (Marist,
    # Oct 19-20): they enter the white and white × education averages, and
    # so the national level, but no other group (user decision, Oct 27).
    # Off: only polls that report Black or Hispanic voters separately.
    crosstab_white_only_polls: bool = True
    # Take the pattern across groups from pollster-matched comparisons: for
    # each pollster, r = (2026 group margin − 2024 group margin) − (2026
    # topline − 2024 topline), averaged across pollsters; group shift =
    # S + (r_avg − c), with S the current method's national shift and c the
    # share-weighted mean of r_avg, so the national level is unchanged.
    # Off: each group's shift is its 2026 poll average minus its 2024 margin.
    pollster_matched_shifts: bool = True
    # Combine each group's pollster-level r with inverse-variance weights
    # (1/SE_r², SE_r from both years' sampling error at DESIGN_EFFECT) rather
    # than √n_eff, so a noisy subgroup counts for less.
    matched_inverse_variance: bool = True
    # If leaving out any one pollster moves a group's r_avg by more than
    # 1.5 pts, use the weighted median for that group (flagged).
    matched_median_fallback: bool = True
    # Source of the 2024 group margins the current method measures from:
    # "catalist" (Catalist, What Happened 2024) or "pew_validated" (Pew's
    # 2024 validated-voter study). With matched shifts on, it moves only the
    # national level S.
    group_baseline: str = "catalist"

    # Item 4 — error model (probability.py). Group errors: each simulation
    # draws a deviation per slider group in the active frame, demeaned with
    # national shares (so the national total is unchanged), and loads it on
    # every district and state by its electorate share — heavily Hispanic
    # seats miss together across states. σ_g = sqrt(SE_g² + τ_g²): SE_g is
    # the sampling error of the group's shift (environment.estimate); τ_g is
    # non-sampling error. The τ values are JUDGMENT CALLS, not estimates.
    group_errors: bool = True
    group_tau_white_nh: float = 1.0
    group_tau_black: float = 3.0
    group_tau_hispanic: float = 4.0
    group_tau_asian: float = 5.0
    group_tau_other: float = 3.0      # any other slider group (the race × education cells)
    # Two national terms applied uniformly to every race, on top of the 2.5
    # national polling error: composition (who turns out) and level
    # measurement (crosstab sampling and the choice of 2024 baseline source).
    national_extra_errors: bool = True
    sigma_composition: float = 1.0
    sigma_level: float = 1.0

    def __post_init__(self):
        if self.group_baseline not in GROUP_BASELINES:
            raise ValueError(f"group_baseline must be one of {GROUP_BASELINES}")

    def group_tau(self, group: str) -> float:
        return getattr(self, f"group_tau_{group}", self.group_tau_other)

    @property
    def effective_white_share(self) -> float:
        return self.white_share if self.white_share_enabled else CATALIST_2022_WHITE_SHARE


DEFAULT_SETTINGS = Settings()


def settings_from(overrides: dict | None) -> Settings:
    """DEFAULT_SETTINGS with `overrides` applied (validated against the fields)."""
    if not overrides:
        return DEFAULT_SETTINGS
    known = {f.name for f in fields(Settings)}
    unknown = set(overrides) - known
    if unknown:
        raise ValueError(f"unknown settings: {sorted(unknown)}")
    return replace(DEFAULT_SETTINGS, **overrides)


def settings_dict(s: Settings) -> dict:
    return asdict(s)
