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

Item 4 adds, when the settings turn them on (ErrorTerms):

  + Σ_g share_{g,i} × (dev_g − Σ_h w_h dev_h)   group errors, dev_g ~ N(0, σ_g²)
  + composition_shock + level_shock             national, uniform to every race

Group errors: one deviation per slider group in the active frame, demeaned
with the groups' national shares w (renormalized), so heavily Hispanic
seats miss together across states while the national total is unchanged;
σ_g = sqrt(SE_g² + τ_g²) (sampling error of the group's shift + a judgment-
call non-sampling term). Composition (who turns out) and level measurement
(crosstab sampling, choice of 2024 baseline) are polling error around the
scenario, on top of the 2.5 national term. The new draws come after the
existing ones and are always made (scaled by 0 when off), so turning a term
on or off leaves every other draw unchanged.

Lockouts (|projection|=100) bypass all shocks — they're deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from config import DEFAULT_SETTINGS, Settings

SIGMA_NATIONAL = 2.5   # shared across every race (polling / late-swing)
SIGMA_REGION   = 1.2   # census region (Northeast / Midwest / South / West)
SIGMA_STATE    = 1.8   # within-state candidate quality / news / weather
SIGMA_DISTRICT = 3.2   # idiosyncratic per-district error
SIGMA_OPEN_SEAT_EXTRA = 2.5   # added in quadrature when there's no sitting incumbent
SIGMA_NEW_LINES_EXTRA = 2.0   # added in quadrature for House districts not on 2024 lines
# Independent Senate races projected from polls (NE, MT): the polls carry
# extra uncertainty the baseline doesn't (three-way race; few, often partisan
# polls).
SIGMA_POLL_OVERRIDE_EXTRA = 3.0   # added in quadrature (user decision)
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


FRAME_AXIS = {"race": "race", "race_edu": "edu"}


@dataclass
class ErrorTerms:
    """Item 4 error terms for one geography (rows in bundle order)."""
    groups: tuple[str, ...] = ()
    sigma: np.ndarray = field(default_factory=lambda: np.zeros(0))       # (G,) σ_g (0 when off)
    se: np.ndarray = field(default_factory=lambda: np.zeros(0))          # (G,) sampling part
    tau: np.ndarray = field(default_factory=lambda: np.zeros(0))         # (G,) non-sampling part
    nat_share: np.ndarray = field(default_factory=lambda: np.zeros(0))   # (G,) demeaning weights
    loadings: np.ndarray | None = None                                   # (n_rows, G) electorate shares
    sigma_composition: float = 0.0
    sigma_level: float = 0.0

    def describe(self) -> dict:
        return {
            "groups": {g: {"sigma": round(float(s), 2), "se": round(float(e), 2), "tau": round(float(t), 2)}
                       for g, s, e, t in zip(self.groups, self.sigma, self.se, self.tau)},
            "composition": self.sigma_composition,
            "level": self.sigma_level,
        }


def error_terms(pop: dict[str, np.ndarray], settings: Settings = DEFAULT_SETTINGS,
                frame: str = "race") -> ErrorTerms:
    """Group-error loadings and σs for a geography with ACS population
    shares `pop` (bundle.pop), plus the two national terms."""
    from environment import default_scenario
    from model import AXIS_SLIDERS, electorate_shares, national_shares

    groups = AXIS_SLIDERS[FRAME_AXIS[frame]]
    se = np.array([default_scenario(settings)["group_se"][g] for g in groups])
    tau = np.array([settings.group_tau(g) for g in groups])
    on = 1.0 if settings.group_errors else 0.0
    shares = electorate_shares(pop, settings)
    ns = national_shares(settings)
    nat = np.array([ns[g] for g in groups])
    extra = 1.0 if settings.national_extra_errors else 0.0
    return ErrorTerms(groups=tuple(groups), sigma=on * np.sqrt(se ** 2 + tau ** 2), se=se, tau=tau,
                      nat_share=nat / nat.sum(),
                      loadings=np.column_stack([shares[g] for g in groups]),
                      sigma_composition=extra * settings.sigma_composition,
                      sigma_level=extra * settings.sigma_level)


def _extra_shocks(rng, n_rows: int, terms: ErrorTerms | None) -> np.ndarray:
    """(N_SIMS, n_rows) group + composition + level shocks. Draws are made
    even when a σ is 0, so toggling a term keeps common random numbers."""
    terms = terms or ErrorTerms()
    G = len(terms.groups)
    dev = rng.standard_normal((N_SIMS, G)) * terms.sigma[None, :]
    comp = rng.standard_normal((N_SIMS, 1)) * terms.sigma_composition
    level = rng.standard_normal((N_SIMS, 1)) * terms.sigma_level
    out = np.broadcast_to(comp + level, (N_SIMS, n_rows)).copy()
    if G:
        if terms.loadings is None or terms.loadings.shape[0] != n_rows:
            raise ValueError("group-error loadings don't match the result rows")
        dev = dev - (dev @ terms.nat_share)[:, None]
        out += dev @ terms.loadings.T
    return out


def error_model_summary(terms: ErrorTerms | None, senate: bool = False) -> dict:
    """Every error term in the simulation, for display."""
    t = (terms or ErrorTerms()).describe()
    race = (f"{np.sqrt(SIGMA_STATE ** 2 + SIGMA_DISTRICT ** 2):.1f} (state {SIGMA_STATE} + race "
            f"{SIGMA_DISTRICT} combined)") if senate else SIGMA_DISTRICT
    out = {"national": SIGMA_NATIONAL, "composition": t["composition"], "level": t["level"],
           "region": SIGMA_REGION, "state": 0.0 if senate else SIGMA_STATE, "race": race,
           "open_seat_extra": SIGMA_OPEN_SEAT_EXTRA, "groups": t["groups"], "n_sims": N_SIMS}
    if not senate:
        out["new_lines_extra"] = SIGMA_NEW_LINES_EXTRA
    else:
        out["poll_override_extra"] = SIGMA_POLL_OVERRIDE_EXTRA
    return out


def _race_sigma(base: float, open_seat: np.ndarray, new_lines: np.ndarray) -> np.ndarray:
    """Per-race idiosyncratic σ: `base`, widened in quadrature for open seats
    and redrawn districts. `new_lines` is a 0..1 weight on the new-lines
    term (the share of the district that is new when core-retention scaling
    is on; 0/1 otherwise)."""
    var = (base ** 2
           + open_seat * SIGMA_OPEN_SEAT_EXTRA ** 2
           + (new_lines * SIGMA_NEW_LINES_EXTRA) ** 2)
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


def house_sims(rows: list[dict], terms: ErrorTerms | None = None) -> np.ndarray:
    """(N_SIMS, n_rows) simulated House margins."""
    rng = np.random.default_rng(SEED)
    proj = np.array([r["projection"] for r in rows], dtype=float)
    lockout = np.abs(proj) >= 99.5
    open_seat = np.array([bool(r.get("open_seat")) for r in rows], dtype=float)
    new_lines = np.array([r.get("new_lines_weight", (r.get("lines") or "2024") != "2024")
                          for r in rows], dtype=float)

    nat = rng.normal(0.0, SIGMA_NATIONAL, size=(N_SIMS, 1))
    corr = _draw_correlated_shocks(rng, rows, SIGMA_STATE, SIGMA_REGION,
                                   _race_sigma(SIGMA_DISTRICT, open_seat, new_lines))
    corr += _extra_shocks(rng, len(rows), terms)
    corr[:, lockout] = 0.0

    sims = proj[None, :] + nat + corr
    sims[:, lockout] = proj[lockout]
    return sims


def add_win_probabilities(result: dict, majority_threshold: int = 218,
                          terms: ErrorTerms | None = None) -> dict:
    """Mutate `result` in place, adding `p_d` to each district row and
    `seat_distribution` and `error_model` to `result['summary']`. Returns
    the same dict."""
    rows = result.get("districts") or result.get("seats") or []
    if not rows:
        return result

    sims = house_sims(rows, terms)
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
        summary["error_model"] = error_model_summary(terms)
    return result


def senate_sims(rows: list[dict], terms: ErrorTerms | None = None) -> np.ndarray:
    """(N_SIMS, n_rows) simulated Senate margins."""
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
    poll_override = np.array([bool(r.get("independent_candidate")) and (r.get("poll_weight") or 0) > 0
                              for r in rows], dtype=float)
    sigma_race = np.sqrt(_race_sigma(sigma_seat, open_seat, np.zeros(len(rows))) ** 2
                         + poll_override * SIGMA_POLL_OVERRIDE_EXTRA ** 2)
    corr = _draw_correlated_shocks(rng, rows, sigma_state=0.0,
                                   sigma_region=SIGMA_REGION, sigma_race=sigma_race)
    corr += _extra_shocks(rng, len(rows), terms)
    corr[:, lockout] = 0.0

    sims = proj[None, :] + nat + corr
    sims[:, lockout] = proj[lockout]
    return sims


def add_senate_win_probabilities(result: dict, holdover_d: int, holdover_r: int,
                                 holdover_i_caucus_d: int = 0,
                                 terms: ErrorTerms | None = None) -> dict:
    """Senate version. `result['seats']` contains 33 Class-II + 2 specials.
    Holdovers (not-up seats) are added deterministically to each simulated
    seat count.

    Independent nominees running as the anti-Republican candidate (Osborn NE,
    Bengs SD, Achilles ID, Bodnar MT — challenger_party "(I)") are assumed to
    caucus with Democrats if they win: the headline P(D control) counts them
    with Democrats. `p_d_control_without_independents` counts their wins for
    neither party (no caucus), and `independent_races` lists the races.
    """
    rows = result.get("seats") or []
    if not rows:
        return result

    sims = senate_sims(rows, terms)
    d_wins = sims > 0
    p_d = d_wins.mean(axis=0)
    for r, p in zip(rows, p_d):
        r["p_d"] = round(float(p), 3)
    indep = np.array([r.get("challenger_party") == "(I)" for r in rows])

    # 100-seat chamber. D control needs 51; R controls at 50 because VP Vance
    # breaks ties. p_*_majority are outright 51+ majorities.
    total_d = d_wins.sum(axis=1) + holdover_d + holdover_i_caucus_d
    total_d_no_ind = d_wins[:, ~indep].sum(axis=1) + holdover_d + holdover_i_caucus_d
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
        # Same simulations, independents' wins caucusing with neither party.
        "d_median_without_independents": int(np.median(total_d_no_ind)),
        "p_d_control_without_independents": round(float((total_d_no_ind >= 51).mean()), 3),
        "independents_assumed": "caucus with Democrats",
        "independent_races": [
            {"state": r["state"], "candidate": r.get("challenger"), "opponent": r.get("co_nominee") or r.get("incumbent"),
             "p_win": round(float(p), 3)}
            for r, p, i in zip(rows, p_d, indep) if i
        ],
    }
    # Races also shown with an excluded WAR cycle included (Alaska): shift
    # that race's simulated margins by the WAR difference, same draws.
    alternatives = []
    for i, r in enumerate(rows):
        alt = r.get("exclusion_alternative")
        if not alt:
            continue
        alt_wins = d_wins.copy()
        alt_wins[:, i] = sims[:, i] + alt["margin_delta"] > 0
        alt_total = alt_wins.sum(axis=1) + holdover_d + holdover_i_caucus_d
        alternatives.append({
            "state": r["state"], "label": alt["label"],
            "projection": r["projection"], "projection_alt": round(r["projection"] + alt["margin_delta"], 2),
            "p_d": r["p_d"], "p_d_alt": round(float(alt_wins[:, i].mean()), 3),
            "p_d_control_alt": round(float((alt_total >= 51).mean()), 3),
        })
        r["projection_alt"] = round(r["projection"] + alt["margin_delta"], 2)
        r["p_d_alt"] = round(float(alt_wins[:, i].mean()), 3)
    summary["seat_distribution"]["exclusion_alternatives"] = alternatives
    summary["error_model"] = error_model_summary(terms, senate=True)
    return result


# ──────────────── Governors ────────────────
# Governor races share the Senate's simulations: the same national, region,
# group, composition and level draws, and — where the state also has a
# Senate race — the state part of that seat's error (the Senate folds the
# state's σ into each seat's idiosyncratic draw, so the governor race takes
# the state component's conditional draw given it: covariance σ_state²).
# The Senate's draws are replayed from its generator in the same order, so
# House and Senate results are untouched. Governor-only draws (the state
# component's residual, the race error) come from a separate generator.
GOV_SEED = SEED + 1


@dataclass
class SenateDraws:
    nat: np.ndarray                 # (N, 1)
    region: dict[str, np.ndarray]   # region code -> (N,)
    seat: dict[str, tuple[np.ndarray, float]]   # state -> (seat draw (N,), its σ)
    dev: np.ndarray                 # (N, G) demeaned group deviations
    common: np.ndarray              # (N, 1) composition + level


def _senate_race_sigma(rows: list[dict]) -> np.ndarray:
    """Per-seat idiosyncratic σ in senate_sims."""
    open_seat = np.array([not r.get("incumbency_adj") for r in rows], dtype=float)
    sigma_seat = float(np.sqrt(SIGMA_STATE ** 2 + SIGMA_DISTRICT ** 2))
    poll_override = np.array([bool(r.get("independent_candidate")) and (r.get("poll_weight") or 0) > 0
                              for r in rows], dtype=float)
    return np.sqrt(_race_sigma(sigma_seat, open_seat, np.zeros(len(rows))) ** 2
                   + poll_override * SIGMA_POLL_OVERRIDE_EXTRA ** 2)


def senate_draws(rows: list[dict], terms: ErrorTerms | None = None) -> SenateDraws:
    """Replay senate_sims' draws for Senate rows `rows` (same calls, same
    order; checked against senate_sims in analysis/governor_checks.py)."""
    rng = np.random.default_rng(SEED)
    nat = rng.normal(0.0, SIGMA_NATIONAL, size=(N_SIMS, 1))
    states = [r["state"] for r in rows]
    regions = [STATE_TO_REGION.get(s, "OTHER") for s in states]
    us_list, ur_list = sorted(set(states)), sorted(set(regions))
    rng.normal(0.0, 0.0, size=(N_SIMS, len(us_list)))          # the Senate's (zero) state draws
    region_draws = rng.normal(0.0, SIGMA_REGION, size=(N_SIMS, len(ur_list)))
    sigma = _senate_race_sigma(rows)
    seat_draws = rng.standard_normal(size=(N_SIMS, len(rows))) * sigma[None, :]
    terms = terms or ErrorTerms()
    G = len(terms.groups)
    dev = rng.standard_normal((N_SIMS, G)) * terms.sigma[None, :]
    comp = rng.standard_normal((N_SIMS, 1)) * terms.sigma_composition
    level = rng.standard_normal((N_SIMS, 1)) * terms.sigma_level
    if G:
        dev = dev - (dev @ terms.nat_share)[:, None]
    seat = {}
    for i, s in enumerate(states):
        seat.setdefault(s, (seat_draws[:, i], float(sigma[i])))
    return SenateDraws(nat=nat, region={r: region_draws[:, k] for k, r in enumerate(ur_list)},
                       seat=seat, dev=dev, common=comp + level)


def governor_race_sigma(rows: list[dict], extra: float) -> np.ndarray:
    """Per-race σ for governor races, besides the shared national, region and
    state parts: the race term, widened in quadrature for open seats (no
    incumbent who has won a governor's election), independent races on
    polls only, and `extra` (settings.governor_race_sigma_extra)."""
    open_seat = np.array([not r.get("incumbency_adj") for r in rows], dtype=float)
    poll_override = np.array([bool(r.get("independent_candidate")) and (r.get("poll_weight") or 0) > 0
                              for r in rows], dtype=float)
    return np.sqrt(_race_sigma(SIGMA_DISTRICT, open_seat, np.zeros(len(rows))) ** 2
                   + poll_override * SIGMA_POLL_OVERRIDE_EXTRA ** 2 + extra ** 2)


def governor_sims(rows: list[dict], senate_rows: list[dict], senate_terms: ErrorTerms | None,
                  terms: ErrorTerms | None, extra: float) -> np.ndarray:
    """(N_SIMS, n_rows) simulated governor margins, sharing the Senate's draws."""
    shared = senate_draws(senate_rows, senate_terms)
    rng = np.random.default_rng(GOV_SEED)
    n = len(rows)
    proj = np.array([r["projection"] for r in rows], dtype=float)
    eta = rng.standard_normal((N_SIMS, n))
    race = rng.standard_normal((N_SIMS, n)) * governor_race_sigma(rows, extra)[None, :]
    out = proj[None, :] + shared.nat + race + shared.common
    for j, r in enumerate(rows):
        s = r["state"]
        out[:, j] += shared.region[STATE_TO_REGION[s]]
        if s in shared.seat:
            u, su = shared.seat[s]
            b = SIGMA_STATE ** 2 / su ** 2
            out[:, j] += b * u + SIGMA_STATE * np.sqrt(1.0 - b) * eta[:, j]
        else:
            out[:, j] += SIGMA_STATE * eta[:, j]
    terms = terms or ErrorTerms()
    if len(terms.groups):
        if terms.loadings is None or terms.loadings.shape[0] != n:
            raise ValueError("group-error loadings don't match the governor rows")
        out += shared.dev @ terms.loadings.T
    return out


def add_governor_win_probabilities(result: dict, senate_rows: list[dict], senate_terms: ErrorTerms | None,
                                   terms: ErrorTerms | None, extra: float) -> dict:
    """Mutate `result` (governor_model.project) in place: `p_d` per race
    (P(the anti-R candidate wins)) and the governorships after the election
    — races up plus the governorships not up, which keep their party.
    Democrats hold a majority of governorships at 26 of 50."""
    rows = result.get("races") or []
    if not rows:
        return result
    sims = governor_sims(rows, senate_rows, senate_terms, terms, extra)
    wins = sims > 0
    for r, p in zip(rows, wins.mean(axis=0)):
        r["p_d"] = round(float(p), 3)
    # Each race's two sides: the anti-R candidate's party when the margin is
    # positive, the opponent's (R, or an independent in Rhode Island) when not.
    pos = np.array([r.get("anti_r_party") or "(D)" for r in rows])
    neg = np.array([r.get("opponent_party") or "(R)" for r in rows])
    s = result.setdefault("summary", {})
    def total(party):
        return (wins[:, pos == party].sum(axis=1) + (~wins[:, neg == party]).sum(axis=1)
                + s.get(f"not_up_{party.strip('()').lower()}", 0))
    total_d, total_i, total_r = total("(D)"), total("(I)"), total("(R)")
    s["governorships"] = {
        "d_median": int(np.median(total_d)), "d_p10": int(np.quantile(total_d, 0.10)),
        "d_p90": int(np.quantile(total_d, 0.90)), "d_mean": round(float(total_d.mean()), 1),
        "r_median": int(np.median(total_r)), "r_p10": int(np.quantile(total_r, 0.10)),
        "r_p90": int(np.quantile(total_r, 0.90)),
        "i_median": int(np.median(total_i)),
        "p_d_majority": round(float((total_d >= 26).mean()), 3),
        "p_r_majority": round(float((total_r >= 26).mean()), 3),
        "majority_threshold": 26,
    }
    s["error_model"] = {**error_model_summary(terms, senate=True),
                        "race": f"{SIGMA_DISTRICT} + governor extra {extra} (in quadrature)",
                        "state": f"{SIGMA_STATE}, shared with the state's Senate race where there is one",
                        "shared_with_senate": "national, region, state, group, composition and level draws"}
    return result
