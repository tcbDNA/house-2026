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

# Default trend weight (multiplier on the carried, residualized 2020→2024
# trend). 0: the 2025 NJ/VA governor backtest found no carryover of the
# residual trend once demographics are controlled (county coefficient −0.05,
# robust SE 0.11; analysis/trend_weight_nj_va_2025.txt). 0.5, 1 and −0.5
# remain scenario options. A scenario parameter, not a Settings flag.
DEFAULT_TREND_WEIGHT = 0.0

GROUP_BASELINES = ("catalist", "pew_validated")


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

    # Item 2 — residualized trend (trend.py). Remove from the carried trend
    # the part explained by the active frame's demographic shares (+ age, +
    # intercept) and/or the 2024 battleground-state part; trend_discount then
    # applies to what's left. Both off = the raw 2020→2024 trend, as before.
    trend_remove_demographic: bool = True
    trend_remove_battleground: bool = True
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
    # Take the pattern across groups from pollster-matched comparisons: for
    # each pollster, r = (2026 group margin − 2024 group margin) − (2026
    # topline − 2024 topline), averaged across pollsters; group shift =
    # S + (r_avg − c), with S the current method's national shift and c the
    # share-weighted mean of r_avg, so the national level is unchanged.
    # Off: each group's shift is its 2026 poll average minus its 2024 margin.
    pollster_matched_shifts: bool = True
    # Source of the 2024 group margins the current method measures from:
    # "catalist" (Catalist, What Happened 2024) or "pew_validated" (Pew's
    # 2024 validated-voter study). With matched shifts on, it moves only the
    # national level S.
    group_baseline: str = "catalist"

    def __post_init__(self):
        if self.group_baseline not in GROUP_BASELINES:
            raise ValueError(f"group_baseline must be one of {GROUP_BASELINES}")

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
