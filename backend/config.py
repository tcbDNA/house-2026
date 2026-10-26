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
    # Center the states' carried trend on its national (2024-vote-weighted,
    # all states + DC) mean when residualizing. The district regression's
    # intercept absorbs a turnout-composition offset (+0.99: districts weight
    # 2020 margins by 2024 votes) that state-level trends don't share (+0.43),
    # so uncentered state residuals average -0.6 and would tilt every Senate
    # race ~0.3 pts R. The House needs no centering: its calibration absorbs
    # any constant.
    trend_center_states: bool = True

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
