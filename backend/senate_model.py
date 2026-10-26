"""Senate projection model — state-level, mirrors the House model shape.

Formula per state:
  proj = pres_margin_2024 + state_trend + uniform_swing
       + war_adj_discounted + incumbency_adj + demographic_shift

  uniform_swing = environment - PRES_2024_POPVOTE   (-1.5)
  demographic_shift = Σ_axis w_axis × Σ_g electorate_share_g × (slider_g - baseline_g)

Same slider semantics as the House model: each slider is the group's absolute
D-R margin, baseline is Catalist 2024 values, shares are rescaled to the
electorate, and multiple moved axes are averaged (model.axis_weights).

state_trend is already relative to the nation, so (unlike the House model)
no calibration step is needed: the presidential baseline + swing from the
2024 presidential popular vote is internally consistent.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from config import DEFAULT_SETTINGS, DEFAULT_TREND_WEIGHT, Settings
import trend as trend_mod
from model import (
    ALL_SLIDERS, AXIS_SLIDERS, CATALIST_BASELINES, TOSSUP_THRESHOLD, carried_trend, demographic_shift,
    electorate_shares, population_shares,
)

DATA_PATH = Path(__file__).resolve().parent / "data" / "senate_states.json"
STATE_RESULTS_PATH = Path(__file__).resolve().parent / "data" / "state_pres_results.csv"

PRES_2024_POPVOTE = -1.5   # presidential R+1.5 in 2024


@dataclass
class SenateBundle:
    states: list[dict]            # 50 states, only some with seat_up_2026=True
    seats: list[dict]             # subset where seat_up_2026=True
    # base_margin excludes state_trend so it can be discounted at project time.
    base_margin: np.ndarray       # pres_2024 + war + inc + challenger
    state_trend: np.ndarray       # state-vs-national trend; full-weight at trend_discount=1.0
    battleground: np.ndarray      # 1 if a 2024 presidential battleground state
    pop: dict[str, np.ndarray]    # group -> per-seat ACS population share
    # Every state + DC, for centering the carried trend nationally.
    all_trend: np.ndarray
    all_battleground: np.ndarray
    all_pop: dict[str, np.ndarray]
    all_votes_w: np.ndarray       # official 2024 votes, normalized to sum to 1
    # Polling-average margin (anti-R candidate − R) where the race uses a
    # documented polling override; NaN elsewhere.
    poll_margin: np.ndarray = field(default_factory=lambda: np.zeros(0))

    @property
    def n(self) -> int:
        return len(self.seats)


def load_bundle(path: Path = DATA_PATH) -> SenateBundle:
    raw = json.loads(path.read_text())
    states_dict = raw["states"]
    all_states = sorted(states_dict.values(), key=lambda s: s["state"])
    seats = [s for s in all_states if s.get("seat_up_2026")]

    pres_2024 = np.array([s.get("presidential_margin_2024") or 0.0 for s in seats], dtype=float)
    trend = np.array([s.get("state_trend") or 0.0 for s in seats], dtype=float)
    war = np.array([s.get("war_adj_discounted") or 0.0 for s in seats], dtype=float)
    inc = np.array([s.get("incumbency_adj") or 0.0 for s in seats], dtype=float)
    challenger = np.array([s.get("challenger_adj") or 0.0 for s in seats], dtype=float)
    base_margin = pres_2024 + war + inc + challenger
    with STATE_RESULTS_PATH.open() as f:
        totals = {r["state"]: float(r["total_2024"]) for r in csv.DictReader(f)}
    votes = np.array([totals[s["state"]] for s in all_states], dtype=float)

    return SenateBundle(states=all_states, seats=seats, base_margin=base_margin,
                        state_trend=trend, battleground=trend_mod.battleground([s["state"] for s in seats]),
                        pop=population_shares(seats),
                        all_trend=np.array([s.get("state_trend") or 0.0 for s in all_states], dtype=float),
                        all_battleground=trend_mod.battleground([s["state"] for s in all_states]),
                        all_pop=population_shares(all_states), all_votes_w=votes / votes.sum(),
                        poll_margin=np.array([(s.get("poll_override") or {}).get("margin", np.nan)
                                              for s in seats], dtype=float))


def project(
    bundle: SenateBundle,
    environment: float = 5.0,
    sliders: dict[str, float] | None = None,
    trend_discount: float = DEFAULT_TREND_WEIGHT,
    settings: Settings = DEFAULT_SETTINGS,
    frame: str = "race",
) -> dict:
    """`trend_discount` multiplies ``state_trend`` before adding it in.
    0.5 = partial mean-reversion (default, matches district rel_trend),
    1.0 = full trend persistence, 0.0 = trends ignored entirely, negative =
    the 2020→2024 shift partially reverses.

    Races with a documented polling override (senate_poll_overrides.csv)
    start from the polling average instead of the model baseline: their
    projection is the poll margin plus how far the scenario has moved the
    model's projection from the default scenario for these settings.
    """
    sliders = dict(sliders or {})
    for k in ALL_SLIDERS:
        sliders.setdefault(k, CATALIST_BASELINES[k])
    projections, shifts, weights, demo_shift, state_trend_applied, uniform_swing = _projections(
        bundle, environment, sliders, trend_discount, settings, frame)
    model_projections = projections.copy()
    if np.isfinite(bundle.poll_margin).any():
        projections = np.where(np.isfinite(bundle.poll_margin),
                               bundle.poll_margin + projections
                               - _default_projections(bundle, settings, frame),
                               projections)

    # Senate seat totals require the un-contested 65 seats not up in 2026.
    # Compute D pickups / R pickups based on partisan flip of seats up.
    d_seats_up = 0
    r_seats_up = 0
    pickups_d, pickups_r = [], []
    out_seats = []
    for i, s in enumerate(bundle.seats):
        proj = float(projections[i])
        prior_party = s.get("party") or ""
        was_d = prior_party == "(D)"
        was_r = prior_party == "(R)"
        is_d = proj > 0
        flipped_to_d = is_d and was_r
        flipped_to_r = (not is_d) and was_d
        if is_d:
            d_seats_up += 1
        elif proj < 0:
            r_seats_up += 1
        if flipped_to_d:
            pickups_d.append(s["state"])
        if flipped_to_r:
            pickups_r.append(s["state"])
        out_seats.append({
            "state": s["state"],
            "name": s["name"],
            "incumbent": s.get("incumbent"),
            "party": prior_party,
            "retiring": s.get("retiring", False),
            "appointed": s.get("appointed", False),
            "primary_unresolved": s.get("primary_unresolved", False),
            "seat_type": s.get("seat_type"),
            "presidential_margin_2024": s.get("presidential_margin_2024"),
            "state_trend": s.get("state_trend"),
            "state_trend_applied": round(float(state_trend_applied[i]), 2),
            "war_adj_discounted": s.get("war_adj_discounted"),
            "incumbency_adj": s.get("incumbency_adj"),
            "challenger": s.get("challenger"),
            "challenger_party": s.get("challenger_party"),
            "challenger_adj": s.get("challenger_adj"),
            "challenger_war": s.get("challenger_war"),
            "challenger_war_year": s.get("challenger_war_year"),
            "challenger_war_source": s.get("challenger_war_source"),
            "co_nominee": s.get("co_nominee"),
            "co_nominee_party": s.get("co_nominee_party"),
            "co_nominee_war": s.get("co_nominee_war"),
            "co_nominee_war_year": s.get("co_nominee_war_year"),
            "co_nominee_war_source": s.get("co_nominee_war_source"),
            "co_nominee_adj": s.get("co_nominee_adj"),
            "projection": round(proj, 2) + 0.0,   # + 0.0 turns -0.0 into 0.0
            "demo_shift": round(float(demo_shift[i]), 2),
            "race_shift": round(float(shifts["race"][i]), 2),
            "edu_shift": round(float(shifts["edu"][i]), 2),
            "age_shift": round(float(shifts["age"][i]), 2),
            "is_tossup": abs(proj) <= TOSSUP_THRESHOLD,
            "flip": "to_D" if flipped_to_d else ("to_R" if flipped_to_r else None),
            "poll_override": s.get("poll_override"),
            "model_projection": round(float(model_projections[i]), 2),
        })

    # Pre-2026 Senate composition: 53R / 47D (post-2024-election, pre-2026).
    # Of those, 35 are up in 2026 (we project these); 65 are not up (assumed held).
    # Held seats (not up) carry their current parties forward.
    not_up_d = 47 - sum(1 for s in bundle.seats if s.get("party") == "(D)")
    not_up_r = 53 - sum(1 for s in bundle.seats if s.get("party") == "(R)")
    final_d = d_seats_up + not_up_d
    final_r = r_seats_up + not_up_r

    return {
        "environment": environment,
        "sliders": sliders,
        "axis_weights": weights,
        "uniform_swing": uniform_swing,
        "trend_discount": trend_discount,
        "summary": {
            "seats_up": len(bundle.seats),
            "d_seats_up": d_seats_up,
            "r_seats_up": r_seats_up,
            "tossups_up": sum(1 for s in out_seats if s["is_tossup"]),
            "not_up_d": not_up_d,
            "not_up_r": not_up_r,
            "final_d": final_d,
            "final_r": final_r,
            "majority": ("D" if final_d >= 51 else "R" if final_r >= 51 else
                         "tie" if final_d == 50 else "none"),
            "d_pickups": pickups_d,
            "r_pickups": pickups_r,
        },
        "seats": out_seats,
    }


def _projections(bundle: SenateBundle, environment: float, sliders: dict, trend_discount: float,
                 settings: Settings, frame: str):
    uniform_swing = environment - PRES_2024_POPVOTE
    shares = electorate_shares(bundle.pop, settings)
    shifts, weights = demographic_shift(shares, sliders, settings)
    demo_shift = sum(shifts.values())
    # Residualized like the House trend: same district-fitted coefficients,
    # applied to the state's own shares and battleground status (trend.py).
    state_trend_carried = carried_trend(bundle.state_trend, shares, bundle.battleground, settings, frame)
    if settings.trend_center_states and (settings.trend_remove_demographic
                                         or settings.trend_remove_battleground):
        national = carried_trend(bundle.all_trend, electorate_shares(bundle.all_pop, settings),
                                 bundle.all_battleground, settings, frame) @ bundle.all_votes_w
        state_trend_carried = state_trend_carried - national
    state_trend_applied = state_trend_carried * trend_discount
    projections = bundle.base_margin + state_trend_applied + uniform_swing + demo_shift
    return projections, shifts, weights, demo_shift, state_trend_applied, uniform_swing


def _default_projections(bundle: SenateBundle, settings: Settings, frame: str) -> np.ndarray:
    """Model projections in the default scenario for `settings` and `frame`
    (the frame's default sliders; the wave that gives the same national total)."""
    from environment import default_scenario
    d = default_scenario(settings)
    sliders = dict(CATALIST_BASELINES)
    if frame == "race_edu":
        sliders.update(d["edu_frame_sliders"])
    else:
        sliders.update({k: d["sliders"][k] for k in AXIS_SLIDERS["race"]})
    ns = d["national_shares"]
    env = d["total"] - sum(ns[k] * (sliders[k] - CATALIST_BASELINES[k]) for k in ALL_SLIDERS)
    return _projections(bundle, env, sliders, DEFAULT_TREND_WEIGHT, settings, frame)[0]


def state_detail(bundle: SenateBundle, state: str) -> dict | None:
    for s in bundle.states:
        if s["state"] == state:
            return s
    return None
