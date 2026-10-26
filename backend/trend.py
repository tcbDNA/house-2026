"""Residualized trend: carry forward only the part of each district's
2020→2024 shift (relative to the nation) that demographics and presidential
campaign intensity don't explain.

The trend y is regressed, by weighted least squares with an intercept and
weights = 2024 total votes, on

  - the electorate shares the active slider frame moves (race shares in the
    race frame, race × education shares in that frame), always plus the age
    shares — a fixed basis per frame, so nudging an age slider never refits;
    one category per axis is dropped as the reference;
  - an indicator for the seven 2024 presidential battleground states, where
    Trump gained less than he did nationally (campaign effort a midterm
    doesn't repeat).

  y = [β0 + Σ β_g share_g]  +  γ · battleground  +  residual
        demographic part        battleground part

The model applies trend_discount × (y − removed parts), where each part is
removed only if its setting is on (trend_remove_demographic,
trend_remove_battleground). The intercept goes with the demographic part
(with the reference group, β0 + Σβ·share is a share-weighted average of
group-level trends). States (Senate) and counties use the same coefficients
applied to their own shares and battleground status.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

BATTLEGROUND_STATES = frozenset({"AZ", "GA", "MI", "NV", "NC", "PA", "WI"})

# (included groups, dropped reference) per axis
FRAME_GROUPS = {
    "race": (("black", "hispanic", "asian", "other"), "white_nh"),
    "race_edu": (("white_college", "nonwhite_college", "nonwhite_non_college"), "white_non_college"),
}
AGE_GROUPS = (("under_30", "age_30_44", "age_65_plus"), "age_45_64")
FRAMES = tuple(FRAME_GROUPS)


@dataclass(frozen=True)
class TrendFit:
    frame: str
    names: tuple[str, ...]          # "const", share groups..., ["battleground"]
    beta: tuple[float, ...]
    se: tuple[float, ...]           # conventional WLS standard errors
    se_hc1: tuple[float, ...]       # heteroskedasticity-robust (HC1)
    r2: float                       # weighted R²
    n: int

    def coef(self, name: str) -> float:
        return self.beta[self.names.index(name)] if name in self.names else 0.0

    def coef_se(self, name: str) -> tuple[float, float]:
        i = self.names.index(name)
        return self.se[i], self.se_hc1[i]


def battleground(states: list[str]) -> np.ndarray:
    return np.array([1.0 if s in BATTLEGROUND_STATES else 0.0 for s in states])


def share_groups(frame: str, include_age: bool = True) -> tuple[str, ...]:
    groups = FRAME_GROUPS[frame][0]
    return groups + (AGE_GROUPS[0] if include_age else ())


def design(shares: dict[str, np.ndarray], bg: np.ndarray, frame: str,
           include_age: bool = True, include_bg: bool = True) -> tuple[np.ndarray, tuple[str, ...]]:
    groups = share_groups(frame, include_age)
    cols = [np.ones_like(bg)] + [shares[g] for g in groups] + ([bg] if include_bg else [])
    names = ("const",) + groups + (("battleground",) if include_bg else ())
    return np.column_stack(cols), names


def wls(y: np.ndarray, X: np.ndarray, weights: np.ndarray):
    """Weighted least squares → (beta, conventional SE, HC1 SE, weighted R²)."""
    w = weights / weights.mean()
    sw = np.sqrt(w)
    Xw, yw = X * sw[:, None], y * sw
    XtWX_inv = np.linalg.inv(Xw.T @ Xw)
    beta = XtWX_inv @ Xw.T @ yw
    resid = y - X @ beta
    n, k = X.shape
    sigma2 = float((w * resid ** 2).sum() / (n - k))
    se = np.sqrt(np.diag(XtWX_inv) * sigma2)
    meat = (Xw * (sw * resid)[:, None]).T @ (Xw * (sw * resid)[:, None])
    se_hc1 = np.sqrt(np.diag(XtWX_inv @ meat @ XtWX_inv) * n / (n - k))
    ybar = float((w * y).sum() / w.sum())
    r2 = 1 - float((w * resid ** 2).sum()) / float((w * (y - ybar) ** 2).sum())
    return beta, se, se_hc1, r2


def fit_trend(y: np.ndarray, shares: dict[str, np.ndarray], weights: np.ndarray,
              bg: np.ndarray, frame: str, include_age: bool = True,
              include_bg: bool = True) -> TrendFit:
    X, names = design(shares, bg, frame, include_age, include_bg)
    beta, se, se_hc1, r2 = wls(y, X, weights)
    return TrendFit(frame, names, tuple(map(float, beta)), tuple(map(float, se)),
                    tuple(map(float, se_hc1)), r2, len(y))


def parts(fit: TrendFit, shares: dict[str, np.ndarray], bg: np.ndarray
          ) -> tuple[np.ndarray, np.ndarray]:
    """(demographic part incl. intercept, battleground part) for any geography."""
    demo = fit.coef("const") + sum(fit.coef(g) * shares[g]
                                   for g in fit.names if g not in ("const", "battleground"))
    return np.broadcast_to(demo, bg.shape).astype(float), fit.coef("battleground") * bg


def carried_trend(y: np.ndarray, fit: TrendFit, shares: dict[str, np.ndarray], bg: np.ndarray,
                  remove_demographic: bool, remove_battleground: bool) -> np.ndarray:
    """The trend that gets multiplied by trend_discount."""
    demo, bgp = parts(fit, shares, bg)
    return y - (demo if remove_demographic else 0.0) - (bgp if remove_battleground else 0.0)
