"""Monte Carlo probabilistic layer over the deterministic projection.

Given a projection result (list of districts with `projection` field), draws
N simulations of a correlated national shock plus independent per-district
shock, and returns:

  - `p_win` per district (probability the D-margin candidate wins)
  - `seat_distribution` summary (median, 10th/90th, P(D maj), P(R maj))

Model:
  simulated_margin_i = projection_i + national_shock + district_shock_i
  national_shock  ~ N(0, SIGMA_NATIONAL)   shared across all districts
  district_shock  ~ N(0, SIGMA_DISTRICT)   independent per district

Lockouts (|projection|=100) bypass the shock entirely — they're deterministic.
"""
from __future__ import annotations

import numpy as np

SIGMA_NATIONAL = 2.5   # polling / late-swing correlated error
SIGMA_DISTRICT = 4.0   # idiosyncratic per-district error
N_SIMS = 10000
_RNG = np.random.default_rng(20260918)


def add_win_probabilities(result: dict, majority_threshold: int = 218) -> dict:
    """Mutate `result` in place, adding `p_d` to each district row and
    `seat_distribution` to `result['summary']`. Returns the same dict."""
    rows = result.get("districts") or result.get("seats") or []
    if not rows:
        return result

    proj = np.array([r["projection"] for r in rows], dtype=float)
    lockout = np.abs(proj) >= 99.5

    nat = _RNG.normal(0.0, SIGMA_NATIONAL, size=(N_SIMS, 1))
    dist = _RNG.normal(0.0, SIGMA_DISTRICT, size=(N_SIMS, len(proj)))
    dist[:, lockout] = 0.0

    sims = proj[None, :] + nat + dist
    sims[:, lockout] = proj[lockout]

    d_wins = sims > 0
    p_d = d_wins.mean(axis=0)

    for r, p in zip(rows, p_d):
        r["p_d"] = round(float(p), 3)

    # Seat distribution (House only — Senate handled separately with holdovers)
    if "districts" in result:
        seats_d = d_wins.sum(axis=1)
        summary = result.setdefault("summary", {})
        summary["seat_distribution"] = {
            "d_median": int(np.median(seats_d)),
            "d_mean": round(float(seats_d.mean()), 1),
            "d_p10": int(np.quantile(seats_d, 0.10)),
            "d_p90": int(np.quantile(seats_d, 0.90)),
            "p_d_majority": round(float((seats_d >= majority_threshold).mean()), 3),
            "p_r_majority": round(float((seats_d <= (435 - majority_threshold)).mean()), 3),
        }
    return result


def add_senate_win_probabilities(result: dict, holdover_d: int, holdover_r: int,
                                 holdover_i_caucus_d: int = 0) -> dict:
    """Senate version. `result['seats']` contains 33 Class-II + 2 specials.
    Holdovers (not-up seats) are added deterministically to each simulated
    seat count. Independents caucusing with D count toward D majority.
    """
    rows = result.get("seats") or []
    if not rows:
        return result

    proj = np.array([r["projection"] for r in rows], dtype=float)
    lockout = np.abs(proj) >= 99.5

    nat = _RNG.normal(0.0, SIGMA_NATIONAL, size=(N_SIMS, 1))
    dist = _RNG.normal(0.0, SIGMA_DISTRICT, size=(N_SIMS, len(proj)))
    dist[:, lockout] = 0.0

    sims = proj[None, :] + nat + dist
    sims[:, lockout] = proj[lockout]

    d_wins = sims > 0
    p_d = d_wins.mean(axis=0)
    for r, p in zip(rows, p_d):
        r["p_d"] = round(float(p), 3)

    # 100-seat control: D + holdovers ≥ 51 (or 50 with a D VP tiebreak)
    total_d = d_wins.sum(axis=1) + holdover_d + holdover_i_caucus_d
    total_r = (~d_wins).sum(axis=1) + holdover_r
    summary = result.setdefault("summary", {})
    summary["seat_distribution"] = {
        "d_median": int(np.median(total_d)),
        "d_mean": round(float(total_d.mean()), 1),
        "d_p10": int(np.quantile(total_d, 0.10)),
        "d_p90": int(np.quantile(total_d, 0.90)),
        "p_d_majority": round(float((total_d >= 51).mean()), 3),
        "p_r_majority": round(float((total_r >= 51).mean()), 3),
    }
    return result
