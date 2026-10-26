"""Monte Carlo probabilistic layer over the deterministic projection.

Given a projection result (list of districts with `projection` field), draws
N correlated simulations and returns:

  - `p_d` per district (probability of D win)
  - `seat_distribution` summary (median, 10th/90th, P(D maj), P(R maj))

Model — four-tier correlated shocks:
  simulated_margin_i = projection_i
                     + national_shock                  (correlated across all)
                     + region_shock[region_of_i]       (correlated within region)
                     + state_shock[state_of_i]         (correlated within state)
                     + district_shock_i                (idiosyncratic)

National shock captures polling / late-swing error affecting every race.
Region and state shocks capture regional and state-specific errors — a
miss in one Michigan district makes misses in other Michigan (and Midwest)
districts more likely. Idiosyncratic shock is per-race unique error.

The variance decomposition
  σ_total² = σ_nat² + σ_region² + σ_state² + σ_district²
gives a per-race σ ≈ √(2.5² + 1.2² + 1.8² + 3.2²) ≈ 4.6 points for an
incumbent running on unchanged lines. Races we know less about get a wider
idiosyncratic term (added in quadrature): open seats (no sitting incumbent —
no personal-vote track record) and House districts on new lines (WAR and
trend were measured on a different electorate). An open seat on new lines
comes to σ ≈ 5.6.
The correlation structure widens the seat-count CI vs. treating races
as independent (which underestimates aggregate uncertainty).

Each call uses a freshly seeded generator, so the same scenario always
returns the same probabilities, and nearby scenarios share random draws
(common random numbers) — moving a slider doesn't add Monte Carlo jitter.

Lockouts (|projection|=100) bypass all shocks — they're deterministic.
"""
from __future__ import annotations

import numpy as np

SIGMA_NATIONAL = 2.5   # shared across every race (polling / late-swing)
SIGMA_REGION   = 1.2   # census region (Northeast / Midwest / South / West)
SIGMA_STATE    = 1.8   # within-state candidate quality / news / weather
SIGMA_DISTRICT = 3.2   # idiosyncratic per-district error
SIGMA_OPEN_SEAT_EXTRA = 2.5   # added in quadrature when there's no sitting incumbent
SIGMA_NEW_LINES_EXTRA = 2.0   # added in quadrature for House districts not on 2024 lines
N_SIMS = 10000
SEED = 20260918

# Census regions (used for regional correlation).
STATE_TO_REGION = {
    # Northeast
    "CT": "NE", "ME": "NE", "MA": "NE", "NH": "NE", "RI": "NE", "VT": "NE",
    "NJ": "NE", "NY": "NE", "PA": "NE",
    # Midwest
    "IL": "MW", "IN": "MW", "IA": "MW", "KS": "MW", "MI": "MW", "MN": "MW",
    "MO": "MW", "NE": "MW", "ND": "MW", "OH": "MW", "SD": "MW", "WI": "MW",
    # South
    "AL": "S", "AR": "S", "DE": "S", "FL": "S", "GA": "S", "KY": "S",
    "LA": "S", "MD": "S", "MS": "S", "NC": "S", "OK": "S", "SC": "S",
    "TN": "S", "TX": "S", "VA": "S", "WV": "S",
    # West
    "AK": "W", "AZ": "W", "CA": "W", "CO": "W", "HI": "W", "ID": "W",
    "MT": "W", "NV": "W", "NM": "W", "OR": "W", "UT": "W", "WA": "W", "WY": "W",
}


def _race_sigma(base: float, open_seat: np.ndarray, new_lines: np.ndarray) -> np.ndarray:
    """Per-race idiosyncratic σ: `base`, widened in quadrature for open seats
    and redrawn districts."""
    var = (base ** 2
           + open_seat * SIGMA_OPEN_SEAT_EXTRA ** 2
           + new_lines * SIGMA_NEW_LINES_EXTRA ** 2)
    return np.sqrt(var)


def _draw_correlated_shocks(rng, rows, sigma_state, sigma_region, sigma_race):
    """Return (N_SIMS, n_rows) array of correlated per-race shocks —
    the sum of state + region + idiosyncratic components. `sigma_race` is a
    per-row array of idiosyncratic σ."""
    n = len(rows)
    states = [r.get("state") or r.get("district", r.get("state", ""))[:2] for r in rows]
    regions = [STATE_TO_REGION.get(s, "OTHER") for s in states]

    # Map to compact indices so we draw one shock per unique group.
    us_list = sorted(set(states))
    ur_list = sorted(set(regions))
    us_idx = {s: i for i, s in enumerate(us_list)}
    ur_idx = {r: i for i, r in enumerate(ur_list)}
    state_ix = np.array([us_idx[s] for s in states])
    region_ix = np.array([ur_idx[r] for r in regions])

    state_draws = rng.normal(0.0, sigma_state, size=(N_SIMS, len(us_list)))
    region_draws = rng.normal(0.0, sigma_region, size=(N_SIMS, len(ur_list)))
    dist_draws = rng.standard_normal(size=(N_SIMS, n)) * sigma_race[None, :]
    return state_draws[:, state_ix] + region_draws[:, region_ix] + dist_draws


def add_win_probabilities(result: dict, majority_threshold: int = 218) -> dict:
    """Mutate `result` in place, adding `p_d` to each district row and
    `seat_distribution` to `result['summary']`. Returns the same dict."""
    rows = result.get("districts") or result.get("seats") or []
    if not rows:
        return result

    rng = np.random.default_rng(SEED)
    proj = np.array([r["projection"] for r in rows], dtype=float)
    lockout = np.abs(proj) >= 99.5
    open_seat = np.array([bool(r.get("open_seat")) for r in rows], dtype=float)
    new_lines = np.array([(r.get("lines") or "2024") != "2024" for r in rows], dtype=float)

    nat = rng.normal(0.0, SIGMA_NATIONAL, size=(N_SIMS, 1))
    corr = _draw_correlated_shocks(rng, rows, SIGMA_STATE, SIGMA_REGION,
                                   _race_sigma(SIGMA_DISTRICT, open_seat, new_lines))
    corr[:, lockout] = 0.0

    sims = proj[None, :] + nat + corr
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

    rng = np.random.default_rng(SEED)
    proj = np.array([r["projection"] for r in rows], dtype=float)
    lockout = np.abs(proj) >= 99.5
    # No sitting incumbent who has won the seat: open, appointed, or the
    # incumbent's renomination is unresolved (all carry incumbency_adj = 0).
    open_seat = np.array([not r.get("incumbency_adj") for r in rows], dtype=float)

    nat = rng.normal(0.0, SIGMA_NATIONAL, size=(N_SIMS, 1))
    # Senate: no state-level shock separate from the seat itself (one seat/state
    # among the up-races), so fold state variance into the idiosyncratic term.
    sigma_seat = float(np.sqrt(SIGMA_STATE ** 2 + SIGMA_DISTRICT ** 2))
    corr = _draw_correlated_shocks(rng, rows, sigma_state=0.0,
                                   sigma_region=SIGMA_REGION,
                                   sigma_race=_race_sigma(sigma_seat, open_seat, np.zeros(len(rows))))
    corr[:, lockout] = 0.0

    sims = proj[None, :] + nat + corr
    sims[:, lockout] = proj[lockout]

    d_wins = sims > 0
    p_d = d_wins.mean(axis=0)
    for r, p in zip(rows, p_d):
        r["p_d"] = round(float(p), 3)

    # 100-seat chamber. D control needs 51; R controls at 50 because VP Vance
    # breaks ties. p_*_majority are outright 51+ majorities.
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
        "p_d_control": round(float((total_d >= 51).mean()), 3),
        "p_r_control": round(float((total_r >= 50).mean()), 3),
    }
    return result
