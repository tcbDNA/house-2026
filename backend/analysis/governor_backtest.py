"""Governor calibration, 2018 and 2022: the governors model's structure rerun
on each year's inputs (only what was known before the election), fitted to the
official results with a separate intercept per year.

Inputs (as in analysis/senate_backtest.py, whose helpers this reuses):
  previous presidential margin (2016 for 2018, 2020 for 2022; FEC), the
  0.5 × residual trend between the two previous presidential elections, the
  final generic-ballot average (RCP, excluded pollsters removed) minus the
  previous national presidential margin, candidate WAR from records before
  that year (Split Ticket House / Senate; governor records computed as in
  data/governor_data.py, netted of incumbency with the fitted bonus), and
  ± incumbency for an incumbent who had won a governor's election.
  Simplification as in the Senate backtest: no demographic group shifts.

Fit (OLS, races with a Democrat and a Republican):
  actual − WAR_a = α_year + slope × F + β × (inc_sign + WAR_b) + ε
  F = previous presidential margin + 0.5 × residual trend + uniform swing.
  β is the governor incumbency bonus: it enters both the incumbency term and
  the computed WAR records' incumbency adjustment (WAR = WAR_a + β × WAR_b).
  σ = residual SD (year intercepts removed).
Poll weight (races with an RCP final average, two-party, excluded pollsters
and polls RCP marks (D)/(R) removed):
  actual − model = γ_year + w × (polls − model),  model = the fitted structure
  without the year intercept.

Usage (from backend/): python3 analysis/governor_backtest.py > analysis/governor_backtest.txt
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "data"))
sys.path.insert(0, str(BACKEND / "analysis"))
import governor_data as gd  # noqa: E402
import senate_backtest as sbt  # noqa: E402
import senate_data as sd  # noqa: E402

SRC = BACKEND / "data" / "sources"
POLLS = SRC / "polls_backtest"
TREND_WEIGHT = 0.5
YEARS = (2018, 2022)
PREV = {2018: 2016, 2022: 2020}
EXCLUDED = ("rasmussen", "activote", "wedgewood", "median strategies", "mclaughlin")


def pres_by_year() -> tuple[dict, dict, dict]:
    """year -> state -> margin; year -> state -> total votes; year -> national margin."""
    m, tot, nat = defaultdict(dict), defaultdict(dict), {}
    with (SRC / "gov_results" / "pres_state_2008_2012.csv").open() as f:
        for r in csv.DictReader(f):
            m[int(r["year"])][r["state"]] = float(r["d_pct"]) - float(r["r_pct"])
            tot[int(r["year"])][r["state"]] = float(r["total_votes"])
    with (SRC / "fec_backtest" / "pres_2016_by_state.csv").open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            m[2016][r["state"]] = float(r["margin"])
            tot[2016][r["state"]] = float(r["total"])
    with (BACKEND / "data" / "state_pres_results.csv").open() as f:
        for r in csv.DictReader(f):
            m[2020][r["state"]] = float(r["margin_2020"])
            tot[2020][r["state"]] = float(r["total_2020"])
    for (y, office), v in gd.national_margins().items():
        if office == "president":
            nat[y] = v
    return m, tot, nat


def generic_ballot(year: int) -> tuple[float, int, float]:
    path = (POLLS / "governor" / "generic_ballot_2018_rcp_final.csv" if year == 2018
            else POLLS / "generic_ballot_rcp_final.csv")
    rows = [r for r in csv.DictReader(path.open()) if int(r["year"]) == year]
    pub = next(r for r in rows if r["pollster"].strip().lower() == "rcp average")
    keep = [r for r in rows if r["pollster"].strip().lower() != "rcp average" and r["in_average"] == "yes"
            and r.get("excluded_pollster", "").lower() != "yes"
            and not any(x in r["pollster"].lower() for x in EXCLUDED)]
    return (sum(float(r["dem"]) - float(r["rep"]) for r in keep) / len(keep), len(keep),
            float(pub["dem"]) - float(pub["rep"]))


def poll_averages(year: int) -> dict[str, dict]:
    """state -> RCP's final average, two-party, recomputed without excluded
    pollsters and polls RCP marks (D) / (R)."""
    by = defaultdict(list)
    for r in csv.DictReader((POLLS / "governor" / f"governor_{year}_rcp_final.csv").open()):
        if r["pollster"].strip().lower() != "rcp average" and r["in_average"] == "yes":
            by[r["state"]].append(r)
    out = {}
    for st, rows in by.items():
        keep = [r for r in rows if r.get("excluded_pollster", "").lower() != "yes"
                and not any(x in r["pollster"].lower() for x in EXCLUDED)
                and not re.search(r"\((D|R)\)", r["pollster"])]
        if not keep:
            continue
        d = sum(float(r["dem"]) for r in keep) / len(keep)
        rr = sum(float(r["rep"]) for r in keep) / len(keep)
        out[st] = {"two_party": 100 * (d - rr) / (d + rr), "n": len(keep), "removed": len(rows) - len(keep)}
    return out


def wars_before(year: int, records: list[dict]) -> dict:
    """House / Senate Split Ticket records and computed governor records from
    before `year`, with the 2026 windows shifted back (as senate_backtest);
    governor records carry margin, baseline, incumbent side, opponent and the
    third-candidate flag (data/governor_data.governor_wars)."""
    split = sbt.wars_for(year)
    allw = {k: [x for x in v if x["chamber"] != "Governor"] for k, v in split.items()}
    first = sd.WAR_FIRST_YEAR["Governor"] - (2026 - year)
    for rec in records:
        if not (first <= rec["year"] < year):
            continue
        for letter, name, opp in (("D", rec["d_candidate"], rec["r_candidate"]),
                                  ("R", rec["r_candidate"], rec["d_candidate"])):
            key = (rec["state"], sd._strip_accents(sd._clean_name(name)), letter)
            allw.setdefault(key, []).append({
                "year": rec["year"], "geo": sd.STATE_NAMES[rec["state"]], "chamber": "Governor",
                "sortable": -rec["war"], "k": rec["k"], "war_text": f"computed {rec['war']:+.2f}",
                "margin": rec["margin"], "baseline": rec["baseline"], "opponent": opp,
                "third_candidate": rec["third_candidate"], "other": ""})
    for v in allw.values():
        v.sort(key=lambda x: x["year"], reverse=True)
    return allw


def races(year: int, results: list[dict], records: list[dict], m, tot, nat, variant: str) -> list[dict]:
    prev, prev2 = PREV[year], PREV[year] - 4
    nat_shift = nat[prev] - nat[prev2]
    resid = sbt.residual_trends(m[prev2], m[prev], nat_shift, tot[prev])
    gb, n_gb, gb_pub = generic_ballot(year)
    swing = gb - nat[prev]
    allw = wars_before(year, records)
    polls = poll_averages(year)
    winners = defaultdict(set)   # state -> names that won a governor's general election before `year`
    for r in results:
        if int(r["year"]) < year and r["winner"]:
            winners[r["state"]].add(sbt.last_name(r["winner"]))
    print(f"== {year}: generic ballot (RCP final, excluded pollsters removed) {gb:+.2f} from {n_gb} polls "
          f"(published {gb_pub:+.2f}); {prev} national presidential {nat[prev]:+.2f}; uniform swing {swing:+.2f}")
    out = []
    for r in results:
        if int(r["year"]) != year or r["special"] == "yes" or not (r["d_candidate"] and r["r_candidate"]):
            continue
        st = r["state"]
        inc_sign = 0
        if r["incumbent_ran"] == "yes" and sbt.last_name(r["incumbent"]) in winners[st]:
            inc_sign = 1 if r["incumbent_party"].startswith("D") else -1 if r["incumbent_party"].startswith("R") else 0
        sitting = r["incumbent"] if r["incumbent_ran"] == "yes" else None
        w = {}
        for letter, name in (("D", r["d_candidate"]), ("R", r["r_candidate"])):
            own = sitting and sbt.last_name(sitting) == sbt.last_name(name)
            w[letter] = gd.candidate_war(st, name, letter, allw, None if own else sitting)["variants"][variant]
        p = polls.get(st)
        out.append({"year": year, "state": st, "actual": float(r["d_pct"]) - float(r["r_pct"]),
                    "F": m[prev][st] + TREND_WEIGHT * resid.get(st, 0.0) + swing, "inc": inc_sign,
                    "a0": w["D"]["a0"] + w["R"]["a0"], "c": w["D"]["c"] + w["R"]["c"], "b": w["D"]["b"] + w["R"]["b"],
                    "poll": p["two_party"] if p else None, "n_polls": p["n"] if p else 0,
                    "d": r["d_candidate"], "r": r["r_candidate"]})
    return out


def ols(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, int]:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    df = len(y) - X.shape[1]
    s2 = float(res @ res) / df
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return beta, se, float(np.sqrt(s2)), df


def gap_mle(r: np.ndarray, gap: np.ndarray) -> dict:
    """r_i ~ N(0, σ0² + (κ gap_i)²): maximum likelihood over a grid, the
    likelihood-ratio test of κ = 0, and κ's profile-likelihood 95% interval."""
    def ll(s0, k):
        v = s0 ** 2 + (k * gap) ** 2
        return float(-0.5 * np.sum(np.log(2 * np.pi * v) + r ** 2 / v))
    s0s = np.linspace(0.5, 12, 231)
    ks = np.linspace(0, 1.5, 301)
    prof = np.array([max(ll(s0, k) for s0 in s0s) for k in ks])
    k_hat = float(ks[int(np.argmax(prof))])
    s0_hat = float(max(s0s, key=lambda s0: ll(s0, k_hat)))
    lr = 2 * (prof.max() - prof[0])
    inside = ks[prof >= prof.max() - 1.92]
    return {"kappa": k_hat, "sigma0": s0_hat, "lr": float(lr), "p": float(np.exp(-lr / 2)) if lr < 50 else 0.0,
            "kappa_lo": float(inside.min()), "kappa_hi": float(inside.max()),
            "sigma0_kappa0": float(max(s0s, key=lambda s0: ll(s0, 0.0)))}


def main_cli():
    results = gd.results()
    base_records = gd.computed_records()
    m, tot, nat = pres_by_year()
    variant = "rematch1_third1_single0"
    print("WAR rules as in the 2026 model: rematch records dropped for the challenger, third-candidate (>5%) "
          "records left out; computed records = margin − slope × baseline − k × incumbency.\n")
    rows = []
    for y in YEARS:
        rows += races(y, results, base_records, m, tot, nat, variant)
    yr = np.array([r["year"] for r in rows])
    F = np.array([r["F"] for r in rows]); inc = np.array([r["inc"] for r in rows], dtype=float)
    a0 = np.array([r["a0"] for r in rows]); c = np.array([r["c"] for r in rows]); b = np.array([r["b"] for r in rows])
    act = np.array([r["actual"] for r in rows])
    D = np.column_stack([(yr == 2018).astype(float), (yr == 2022).astype(float)])
    Z = inc + b

    # Refit until the slope stops changing: WAR records recomputed at the
    # current slope (war = a0 − s × c), then the regression refit.
    s, path = 1.0, []
    for it in range(100):
        X = np.column_stack([D, F, Z])
        beta, se, sigma, df = ols(X, act - (a0 - s * c))
        path.append((it, s, beta[2], beta[3]))
        if abs(beta[2] - s) < 1e-6:
            break
        s = float(beta[2])
    a18, a22, slope, binc = beta
    print(f"Fit on {len(rows)} races ({sum(yr == 2018)} in 2018, {sum(yr == 2022)} in 2022): "
          f"actual − WAR(slope) = α_year + slope × F + β × (inc + WAR_b)")
    print("  refit path (slope used for the WAR records -> fitted slope, incumbency): " +
          "; ".join(f"{s0:.4f} -> {s1:.4f}, {b1:.2f}" for _, s0, s1, b1 in path[:6]) +
          (f"; ... ({len(path)} fits)" if len(path) > 6 else ""))
    print(f"  slope      {slope:6.3f}  (SE {se[2]:.3f})")
    print(f"  incumbency {binc:6.2f}  (SE {se[3]:.2f})")
    print(f"  intercepts 2018 {a18:+.2f} (SE {se[0]:.2f}), 2022 {a22:+.2f} (SE {se[1]:.2f})")
    print(f"  model-only residual SD {sigma:.2f}  (SE {sigma / np.sqrt(2 * df):.2f}, df {df})")
    bj, sej, _, _ = ols(np.column_stack([D, F - c, Z]), act - a0)
    print(f"  (for reference, the one-step joint fit with WAR's slope term inside the regressor: slope {bj[2]:.3f} "
          f"(SE {sej[2]:.3f}), incumbency {bj[3]:.2f} (SE {sej[3]:.2f}))")
    model = slope * F + binc * Z + a0 - slope * c
    resid = act - (model + D @ np.array([a18, a22]))
    print(f"\n  {'race':8} {'F':>6} {'inc':>4} {'WAR':>6} {'model':>7} {'polls':>6} {'actual':>7} {'resid':>6}")
    for r, mo, rs, war in sorted(zip(rows, model, resid, a0 - slope * c + binc * b),
                                 key=lambda t: (t[0]["year"], t[0]["state"])):
        pp = f"{r['poll']:+6.1f}" if r["poll"] is not None else "     -"
        print(f"  {r['year']} {r['state']}  {r['F']:+6.1f} {r['inc']:+4d} {war:+6.1f} {mo:+7.1f} {pp} {r['actual']:+7.1f} {rs:+6.1f}")

    # Poll weight on races with an RCP final average.
    has = np.array([r["poll"] is not None for r in rows])
    poll = np.array([r["poll"] if r["poll"] is not None else np.nan for r in rows])
    Xw = np.column_stack([D[has], poll[has] - model[has]])
    bw, sew, sw, dfw = ols(Xw, act[has] - model[has])
    w = float(bw[2])
    print(f"\nPoll weight, {has.sum()} races with an RCP final average: actual − model = γ_year + w × (polls − model)")
    print(f"  w = {w:.3f}  (SE {sew[2]:.3f})")
    for y in YEARS:
        k = has & (yr == y)
        by, sey, _, _ = ols(np.column_stack([np.ones(k.sum()), poll[k] - model[k]]), act[k] - model[k])
        print(f"  {y} alone: w = {by[1]:.3f} (SE {sey[1]:.3f}, {k.sum()} races)")

    # Race-level error of the blended projection, and the model-poll gap term.
    blend = model[has] + w * (poll[has] - model[has])
    rb = act[has] - blend
    for y in YEARS:
        rb[yr[has] == y] -= rb[yr[has] == y].mean()
    nb = has.sum() - 3
    sb = float(np.sqrt((rb @ rb) / nb))
    senate_race = float(np.sqrt(1.2 ** 2 + 1.8 ** 2 + 3.2 ** 2))
    print(f"\nBlended projection (races with polls, year intercepts removed): error SD {sb:.2f} (SE {sb / np.sqrt(2 * nb):.2f})")
    print(f"  the Senate's region + state + race σ is {senate_race:.2f}; implied governor extra in quadrature "
          f"{np.sqrt(max(0.0, sb ** 2 - senate_race ** 2)):.2f}")
    gap = model[has] - poll[has]
    gm = gap_mle(rb, gap)
    bg, seg, _, _ = ols(np.column_stack([np.ones(nb + 3), np.abs(gap)]), np.abs(rb))
    print(f"Model–poll gap term: error_i ~ N(0, σ0² + (κ × gap_i)²), gap = model − polls "
          f"(range {gap.min():+.1f} to {gap.max():+.1f}, median |gap| {np.median(np.abs(gap)):.1f})")
    print(f"  κ = {gm['kappa']:.3f} (95% profile interval {gm['kappa_lo']:.3f}-{gm['kappa_hi']:.3f}), σ0 = {gm['sigma0']:.2f} "
          f"(σ with κ = 0: {gm['sigma0_kappa0']:.2f}); likelihood-ratio test of κ = 0: LR {gm['lr']:.2f}, p ≈ {gm['p']:.3f}")
    print(f"  check: |error| on |gap|: slope {bg[1]:.3f} (SE {seg[1]:.3f}), intercept {bg[0]:.2f}")
    sigma_extra_fit = float(np.sqrt(max(0.0, gm["sigma0"] ** 2 - senate_race ** 2)))
    print(f"  with the gap term, the remaining race-level σ0 {gm['sigma0']:.2f} implies a governor extra of {sigma_extra_fit:.2f}")
    json.dump({"slope": slope, "slope_se": se[2], "incumbency": binc, "incumbency_se": se[3],
               "model_sigma": sigma, "model_sigma_se": sigma / np.sqrt(2 * df),
               "w": w, "w_se": sew[2], "blend_sigma": sb, "blend_sigma_se": sb / np.sqrt(2 * nb),
               "governor_extra_blend": float(np.sqrt(max(0.0, sb ** 2 - senate_race ** 2))),
               "gap_kappa": gm["kappa"], "gap_kappa_lo": gm["kappa_lo"], "gap_kappa_hi": gm["kappa_hi"],
               "gap_lr": gm["lr"], "gap_p": gm["p"], "gap_sigma0": gm["sigma0"],
               "governor_extra_with_gap": sigma_extra_fit, "n": len(rows), "n_polls": int(has.sum()),
               "refit_path": path}, open(BACKEND / "analysis" / "governor_backtest.json", "w"), indent=1)


# ── Refit variants (user request, Oct 28): how much of the incumbency estimate
# comes from a few landslides, or from under-credited personal vote? ─────────
LANDSLIDES = {(2018, "MA"), (2018, "MD"), (2018, "VT"), (2022, "VT"), (2018, "NH"), (2022, "NH")}  # Baker, Hogan, Scott, Sununu


def sbt_region(state: str) -> str:
    from probability import STATE_TO_REGION
    return STATE_TO_REGION.get(state, "")


def huber_wls(X: np.ndarray, y: np.ndarray, iters: int = 50) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Huber M-estimate (k = 1.345 × MAD scale) by iteratively reweighted least
    squares; returns (beta, approximate SE, weights)."""
    w = np.ones(len(y))
    for _ in range(iters):
        sw = np.sqrt(w)
        beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
        r = y - X @ beta
        s = np.median(np.abs(r - np.median(r))) / 0.6745
        k = 1.345 * s
        w_new = np.where(np.abs(r) <= k, 1.0, k / np.maximum(np.abs(r), 1e-12))
        if np.allclose(w_new, w, atol=1e-8):
            break
        w = w_new
    r = y - X @ beta
    df = len(y) - X.shape[1]
    s2 = float(np.sum(w * r ** 2)) / df
    XtWX = (X * w[:, None]).T @ X
    return beta, np.sqrt(np.diag(s2 * np.linalg.inv(XtWX))), w


def fit_variant(rows_all: list[dict], method: str = "ols", drop: set = frozenset(), fixed_inc: float | None = None,
                northeast: bool = False) -> dict:
    """Fixed-point fit (WAR records rebuilt at the slope), then w, the blended
    and model-only error, for one variant."""
    rows = [r for r in rows_all if (r["year"], r["state"]) not in drop]
    yr = np.array([r["year"] for r in rows])
    F = np.array([r["F"] for r in rows]); inc = np.array([r["inc"] for r in rows], dtype=float)
    a0 = np.array([r["a0"] for r in rows]); c = np.array([r["c"] for r in rows]); b = np.array([r["b"] for r in rows])
    act = np.array([r["actual"] for r in rows]); Z = inc + b
    D = np.column_stack([(yr == 2018).astype(float), (yr == 2022).astype(float)])
    ne = np.array([sbt_region(r["state"]) == "NE" for r in rows], dtype=float)
    if northeast:   # a Northeast indicator alongside the year intercepts
        D = np.column_stack([D, ne])
    k0 = D.shape[1]
    est = (lambda X, y: huber_wls(X, y)[:2]) if method == "huber" else (lambda X, y: ols(X, y)[:2])
    s, fits = 1.0, 0
    for fits in range(1, 101):
        if fixed_inc is None:
            X = np.column_stack([D, F, Z])
            beta, se = est(X, act - (a0 - s * c))
            new_s, binc, binc_se = beta[k0], beta[k0 + 1], se[k0 + 1]
        else:
            X = np.column_stack([D, F])
            beta, se = est(X, act - (a0 - s * c) - fixed_inc * Z)
            new_s, binc, binc_se = beta[k0], fixed_inc, 0.0
        if abs(new_s - s) < 1e-6:
            s = float(new_s)
            break
        s = float(new_s)
    slope_se = se[k0]
    model = s * F + binc * Z + a0 - s * c
    res = act - model - D @ beta[:k0]
    npar = X.shape[1]
    sd_model = float(np.sqrt(res @ res / (len(res) - npar)))
    cov = np.linalg.inv(X.T @ X) * float(res @ res) / (len(res) - npar)
    corr = float(cov[k0, k0 + 1] / np.sqrt(cov[k0, k0] * cov[k0 + 1, k0 + 1])) if fixed_inc is None else 0.0
    aic = len(res) * np.log(float(res @ res) / len(res)) + 2 * npar
    ne_coef = (float(beta[2]), float(se[2])) if northeast else None
    has = np.array([r["poll"] is not None for r in rows])
    poll = np.array([r["poll"] if r["poll"] is not None else np.nan for r in rows])
    Dy = D[:, :2]   # the poll-weight fit keeps year intercepts only
    bw, sew = est(np.column_stack([Dy[has], poll[has] - model[has]]), act[has] - model[has])
    w = float(bw[2])
    rb = act[has] - (model[has] + w * (poll[has] - model[has]))
    for y in YEARS:
        rb[yr[has] == y] -= rb[yr[has] == y].mean()
    sd_blend = float(np.sqrt(rb @ rb / (has.sum() - 3)))
    senate_race = float(np.sqrt(1.2 ** 2 + 1.8 ** 2 + 3.2 ** 2))
    return {"n": len(rows), "slope": s, "slope_se": float(slope_se), "inc": float(binc), "inc_se": float(binc_se),
            "slope_inc_corr": corr, "aic": float(aic), "northeast": ne_coef,
            "w": w, "w_se": float(sew[2]), "sd_model": sd_model, "mae_model": float(np.mean(np.abs(res))),
            "sd_blend": sd_blend, "fits": fits,
            "extra_full": float(np.sqrt(max(0.0, sd_blend ** 2 - senate_race ** 2))),
            "extra_none": float(np.sqrt(max(0.0, sd_model ** 2 - senate_race ** 2)))}


def variants_cli():
    results = gd.results()
    records = gd.computed_records()
    m, tot, nat = pres_by_year()
    rows = {sg: [x for y in YEARS for x in races(y, results, records, m, tot, nat, f"rematch1_third1_single{sg}")]
            for sg in (0, 1)}
    out = {
        "baseline (OLS)": fit_variant(rows[0]),
        "robust: Huber loss": fit_variant(rows[0], method="huber"),
        "robust: Baker, Hogan, Scott, Sununu landslides dropped (6 races)": fit_variant(rows[0], drop=LANDSLIDES),
        "single governor record at full weight (OLS)": fit_variant(rows[1]),
        "incumbency fixed at 6 (OLS)": fit_variant(rows[0], fixed_inc=6.0),
        "single record full weight + Northeast indicator (OLS)": fit_variant(rows[1], northeast=True),
    }
    print(f"\n== Refit variants\n{'variant':66} {'n':>3} {'incumbency':>13} {'slope':>13} {'w':>13} "
          f"{'model SD':>8} {'MAE':>5} {'blend SD':>8} {'AIC':>7} {'corr(s,inc)':>11}")
    for k, v in out.items():
        inc = f"{v['inc']:5.2f} ({v['inc_se']:.2f})" if v["inc_se"] else f"{v['inc']:5.2f} (fixed)"
        print(f"{k:66} {v['n']:3d} {inc:>13} {v['slope']:6.3f} ({v['slope_se']:.3f}) {v['w']:6.3f} ({v['w_se']:.3f}) "
              f"{v['sd_model']:8.2f} {v['mae_model']:5.2f} {v['sd_blend']:8.2f} {v['aic']:7.1f} {v['slope_inc_corr']:11.2f}")
    ne = out["single record full weight + Northeast indicator (OLS)"]["northeast"]
    print(f"Northeast indicator (CT ME MA NH RI VT NJ NY PA), single records at full weight: {ne[0]:+.2f} (SE {ne[1]:.2f})")
    json.dump(out, open(BACKEND / "analysis" / "governor_backtest_variants.json", "w"), indent=1)


if __name__ == "__main__":
    main_cli()
    variants_cli()
