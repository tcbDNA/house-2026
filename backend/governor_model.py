"""Governor projection model, built on the Senate machinery.

Per race (D-positive margins):

  fundamentals = slope × (pres_margin_2024 + uniform_swing + demographic_shift
                          + state_trend_applied)
  model        = fundamentals + WAR + incumbency
  projection   = model + w × (polling average − model at the default scenario)
               = w × (polling average + scenario change) + (1 − w) × model

The bracket is exactly the Senate model's projection for that state without
its candidate terms (senate_model._projections on the same inputs); slope =
settings.governor_partisan_slope, 1.0 until the 2018/2022 calibration.

WAR is the Senate blend with Governor as the office (data/governor_data.py):
governor records at full weight, House and Senate records at the 0.5×
cross-office discount. Governor records are computed (Split Ticket publishes
none) and netted of the incumbent's edge using settings.governor_incumbency,
so each candidate's WAR is war_a + governor_incumbency × war_b.
Incumbency = ± governor_incumbency for an incumbent running who has won a
governor's election; successors who haven't get none (as appointed senators).

Polls: w = governor_poll_weight with at least governor_poll_full_n polls,
scaled down linearly below that, 0 with none; races whose anti-R candidate is
an independent use polls only (w = 1, same scaling).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

import senate_model as senate
from config import DEFAULT_SETTINGS, DEFAULT_TREND_WEIGHT, Settings
from model import TOSSUP_THRESHOLD, population_shares

DATA_PATH = Path(__file__).resolve().parent / "data" / "governor_states.json"
GOVERNORSHIPS = 50


@dataclass
class GovernorBundle:
    fund: senate.SenateBundle      # the races' fundamentals (base_margin = 2024 presidential margin)
    races: list[dict]
    not_up: dict[str, dict]        # state -> {"governor", "party"}
    war_a: np.ndarray              # D-positive WAR effect at governor_incumbency = 0
    war_b: np.ndarray              # its change per point of governor_incumbency
    inc_sign: np.ndarray           # +1 D / −1 R incumbent eligible for the bonus, else 0
    poll_margin: np.ndarray = field(default_factory=lambda: np.zeros(0))
    poll_n: np.ndarray = field(default_factory=lambda: np.zeros(0))
    independent: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=bool))

    @property
    def n(self) -> int:
        return len(self.races)

    @property
    def pop(self) -> dict[str, np.ndarray]:
        return self.fund.pop


def load_bundle(path: Path = DATA_PATH, senate_bundle: senate.SenateBundle | None = None) -> GovernorBundle:
    raw = json.loads(path.read_text())
    sb = senate_bundle or senate.load_bundle()
    by_state = {s["state"]: s for s in sb.states}
    races = [{**by_state[r["state"]], **r} for r in sorted(raw["races"].values(), key=lambda r: r["state"])]
    pres = np.array([r.get("presidential_margin_2024") or 0.0 for r in races], dtype=float)
    fund = senate.SenateBundle(
        states=sb.states, seats=races, base_margin=pres,
        state_trend=np.array([r.get("state_trend") or 0.0 for r in races], dtype=float),
        battleground=senate.trend_mod.battleground([r["state"] for r in races]),
        pop=population_shares(races), all_trend=sb.all_trend, all_battleground=sb.all_battleground,
        all_pop=sb.all_pop, all_votes_w=sb.all_votes_w)
    pa = [r.get("poll_average") or {} for r in races]
    return GovernorBundle(
        fund=fund, races=races, not_up=raw["not_up"],
        war_a=np.array([r["war_a"] for r in races], dtype=float),
        war_b=np.array([r["war_b"] for r in races], dtype=float),
        inc_sign=np.array([r["inc_sign"] for r in races], dtype=float),
        poll_margin=np.array([p.get("margin", np.nan) for p in pa], dtype=float),
        poll_n=np.array([p.get("n_polls", 0) for p in pa], dtype=float),
        independent=np.array([r.get("anti_r_party") == "(I)" for r in races]))


def poll_weights(bundle: GovernorBundle, settings: Settings) -> np.ndarray:
    """Per-race weight on the polling average (as senate_model.poll_weights)."""
    if not settings.governor_poll_blend or bundle.poll_n.size == 0:
        return np.zeros(bundle.n)
    base = np.where(bundle.independent, 1.0, settings.governor_poll_weight)
    scale = np.minimum(1.0, bundle.poll_n / settings.governor_poll_full_n)
    return np.where(np.isfinite(bundle.poll_margin), base * scale, 0.0)


def candidate_effects(bundle: GovernorBundle, settings: Settings) -> tuple[np.ndarray, np.ndarray]:
    """(WAR, incumbency), D-positive."""
    inc = settings.governor_incumbency
    return bundle.war_a + inc * bundle.war_b, inc * bundle.inc_sign


def _fundamentals(bundle: GovernorBundle, environment: float, sliders: dict, trend_discount: float,
                  settings: Settings, frame: str):
    proj, shifts, weights, demo_shift, trend_applied, swing = senate._projections(
        bundle.fund, environment, sliders, trend_discount, settings, frame)
    return settings.governor_partisan_slope * proj, shifts, weights, demo_shift, trend_applied, swing


def _default_model(bundle: GovernorBundle, settings: Settings, frame: str) -> np.ndarray:
    war, inc = candidate_effects(bundle, settings)
    return settings.governor_partisan_slope * senate._default_projections(bundle.fund, settings, frame) + war + inc


def _flags(r: dict, proj: float) -> list[dict]:
    """Special-case flags: Alaska's ranked-choice count, Georgia's runoff
    rule, Vermont's legislature rule."""
    out = []
    pa = r.get("poll_average") or {}
    third = pa.get("third_party_share")
    if r["state"] == "AK":
        out.append({"code": "rcv", "text": "Ranked-choice voting: the margin is the final-round two-candidate "
                    "margin" + (" (polls' final-round numbers where reported)" if pa.get("rcv_final_polls") else "")})
    if r["state"] == "GA":
        risk = third is not None and third > abs(proj)
        out.append({"code": "runoff", "risk": risk, "text":
                    ("Runoff risk: third-party support in the polls ({:.1f}) exceeds the projected margin ({:.1f})"
                     .format(third, abs(proj)) if risk else "Georgia requires a majority; no runoff flag "
                     + ("(third-party support {:.1f} ≤ projected margin {:.1f})".format(third, abs(proj))
                        if third is not None else "(no third-party share in the polls)"))})
    if r["state"] == "VT":
        risk = third is not None and abs(proj) <= third
        out.append({"code": "legislature", "risk": risk, "text":
                    ("Legislature may choose: the projected margin ({:.1f}) is within the third-party share ({:.1f})"
                     .format(abs(proj), third) if risk else "Vermont's legislature chooses without a majority; "
                     + ("margin {:.1f} exceeds third-party share {:.1f}".format(abs(proj), third)
                        if third is not None else "no third-party share in the polls"))})
    return out


def project(bundle: GovernorBundle, environment: float, sliders: dict | None = None,
            trend_discount: float = DEFAULT_TREND_WEIGHT, settings: Settings = DEFAULT_SETTINGS,
            frame: str = "race") -> dict:
    sliders = dict(sliders or {})
    for k in senate.ALL_SLIDERS:
        sliders.setdefault(k, senate.CATALIST_BASELINES[k])
    fund, shifts, weights, demo_shift, trend_applied, swing = _fundamentals(
        bundle, environment, sliders, trend_discount, settings, frame)
    war, inc = candidate_effects(bundle, settings)
    model = fund + war + inc
    w = poll_weights(bundle, settings)
    proj = model + np.where(w > 0, w * (bundle.poll_margin - _default_model(bundle, settings, frame)), 0.0)

    rows = []
    for i, r in enumerate(bundle.races):
        p = float(proj[i])
        prior = r.get("party") or ""
        winner = ("D" if r.get("anti_r_party") != "(I)" else "I") if p > 0 else "R"
        flip = None
        if prior and prior.strip("()") != winner:
            flip = f"to_{winner}"
        rows.append({
            "state": r["state"], "name": r["name"], "party": prior,
            "incumbent": r.get("incumbent"), "incumbent_party": r.get("incumbent_party"),
            "incumbent_status": r.get("incumbent_status"),
            "incumbent_won_gov_election": r.get("incumbent_won_gov_election"),
            "d_nominee": r.get("d_nominee"), "r_nominee": r.get("r_nominee"),
            "anti_r_candidate": r.get("anti_r_candidate"), "anti_r_party": r.get("anti_r_party"),
            "other_candidates": r.get("other_candidates") or [],
            "presidential_margin_2024": r.get("presidential_margin_2024"),
            "state_trend_applied": round(float(trend_applied[i]), 2),
            "demo_shift": round(float(demo_shift[i]), 2),
            "fundamentals": round(float(fund[i]), 2),
            "war_effect": round(float(war[i]), 2), "war_detail": r.get("war_detail"),
            "incumbency_adj": round(float(inc[i]), 2),
            "model_projection": round(float(model[i]), 2),
            "poll_average": r.get("poll_average"),
            "poll_weight": round(float(w[i]), 3),
            "independent_candidate": bool(bundle.independent[i]),
            "projection": round(p, 2) + 0.0,
            "is_tossup": abs(p) <= TOSSUP_THRESHOLD,
            "flip": flip,
            "flags": _flags(r, p),
            "note": r.get("note"),
        })
    up_party = {r["state"]: r.get("party") for r in bundle.races}
    not_up = {k: v["party"] for k, v in bundle.not_up.items() if k not in up_party}
    return {
        "environment": environment, "sliders": sliders, "axis_weights": weights,
        "uniform_swing": swing, "trend_discount": trend_discount,
        "summary": {
            "races_up": bundle.n,
            "d_up": sum(1 for x in rows if x["projection"] > 0 and x["anti_r_party"] != "(I)"),
            "i_up": sum(1 for x in rows if x["projection"] > 0 and x["anti_r_party"] == "(I)"),
            "r_up": sum(1 for x in rows if x["projection"] < 0),
            "not_up_d": sum(1 for p in not_up.values() if p == "(D)"),
            "not_up_r": sum(1 for p in not_up.values() if p == "(R)"),
            "not_up_i": sum(1 for p in not_up.values() if p not in ("(D)", "(R)")),
            "d_pickups": [x["state"] for x in rows if x["flip"] == "to_D"],
            "r_pickups": [x["state"] for x in rows if x["flip"] == "to_R"],
            "i_pickups": [x["state"] for x in rows if x["flip"] == "to_I"],
            "slope": settings.governor_partisan_slope,
        },
        "races": rows,
    }
