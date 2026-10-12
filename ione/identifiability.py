"""Exact LP-based identification engine for the binary-stratum,
binary-outcome, two-arm aggregate-data model.

Model.  Four latent probabilities (p0_0, p0_1, p1_0, p1_1): control/treat
risk at stratum x in {0,1}.  Published margins impose linear equalities;
all variables are bounded in [0,1], so the feasible set is a polytope and
the sharp bounds of any linear estimand are the LP optima — computed with
scipy.optimize.linprog (HiGHS), not finite-grid enumeration.

Assumptions that must hold and are validated here:
  * a single stratum prevalence P(X=1)=q common to both arms
    (`arm_weights` must be supplied when arm compositions differ, or the
    audit abstains as UNSUPPORTED);
  * outcome margin P(Y|X=x) mixes arms with `mix` = P(T=1|X=x)
    (defaults to the randomized allocation only when supplied — never
    hard-coded 50/50).

Verdicts (separate states, never conflated):
  INFEASIBLE      margins inconsistent (empty feasible set)
  UNSUPPORTED     estimand/information class not supported by input
  ROBUST_TREAT    bound: max RD < -tau
  ROBUST_NO_TREAT bound: min RD > -tau  (adverse outcome; ties unresolved)
  REVERSIBLE      bounds straddle -tau
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy.optimize import linprog


class DecisionVerdict(str, Enum):
    ROBUST_TREAT = "ROBUST_TREAT"
    ROBUST_NO_TREAT = "ROBUST_NO_TREAT"
    REVERSIBLE = "REVERSIBLE"
    INFEASIBLE = "INFEASIBLE"
    UNSUPPORTED = "UNSUPPORTED"
    # legacy aliases kept for API compatibility
    SUFFICIENT = "SUFFICIENT"
    UNIDENTIFIABLE = "UNIDENTIFIABLE"


@dataclass
class LPResult:
    verdict: DecisionVerdict
    bound_lo: float          # min feasible RD at target stratum
    bound_hi: float          # max feasible RD at target stratum
    solver_status: int       # scipy linprog status (0=optimal)
    residual: float          # max |Aeq x - beq| at the optimum
    tol: float               # solver/verdict tolerance
    detail: str

    # backward-compatible helpers
    @property
    def n_compatible(self):
        return -1  # continuous feasible set; count is meaningless


def _lp_bounds(q, p0bar, p1bar, target_x, outcome_margin=None, mix=None,
               threshold=0.0, tol=1e-9):
    """Sharp bounds for RD = p1_x - p0_x via two LPs."""
    # variables: p00, p01, p10, p11
    A_eq = [[1 - q, q, 0, 0],
            [0, 0, 1 - q, q]]
    b_eq = [p0bar, p1bar]
    if outcome_margin is not None:
        if mix is None:
            return None, "outcome margin supplied without arm mixing proportion -> UNSUPPORTED"
        for x, py in outcome_margin.items():
            row = [0, 0, 0, 0]
            row[x] = 1 - mix[x] if isinstance(mix, dict) else 1 - mix
            row[2 + x] = mix[x] if isinstance(mix, dict) else mix
            A_eq.append(row); b_eq.append(py)
    bounds = [(0, 1)] * 4
    c = [0, 0, 0, 0]
    c[2 + target_x], c[target_x] = 1.0, -1.0
    lo_r = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds,
                   method="highs")
    if lo_r.status == 2:  # infeasible
        return LPResult(DecisionVerdict.INFEASIBLE, math.nan, math.nan,
                        lo_r.status, math.nan, tol,
                        "empty feasible set: margins inconsistent"), None
    hi_r = linprog([-v for v in c], A_eq=A_eq, b_eq=b_eq, bounds=bounds,
                   method="highs")
    if lo_r.status != 0 or hi_r.status != 0:
        return LPResult(DecisionVerdict.UNSUPPORTED, math.nan, math.nan,
                        max(lo_r.status, hi_r.status), math.nan, tol,
                        "solver failure"), None
    lo, hi = lo_r.fun, -hi_r.fun
    resid = max(np.max(np.abs(np.array(A_eq) @ lo_r.x - np.array(b_eq))),
                np.max(np.abs(np.array(A_eq) @ hi_r.x - np.array(b_eq))))
    tau = threshold
    if hi < -tau - tol:
        v = DecisionVerdict.ROBUST_TREAT
    elif lo > -tau + tol:
        v = DecisionVerdict.ROBUST_NO_TREAT
    else:
        v = DecisionVerdict.REVERSIBLE
    return LPResult(v, lo, hi, lo_r.status, resid, tol,
                    f"RD(x={target_x}) in [{lo:.6f},{hi:.6f}], threshold {tau}"), None


def audit_decision(study_margins, target_x=1, prev1=None,
                   outcome_margin=None, mix=None, threshold=0.0,
                   arm_weights=None, resolution=None):
    """Audit whether the treat/no-treat decision at stratum target_x is
    robust, given arm-level margins (p0bar, p1bar).

    prev1: P(X=1) — required; there is no default because the feasible set
    depends on it.  arm_weights: optional (q0, q1) when arm stratum
    compositions differ; with unequal weights each arm uses its own q.
    outcome_margin: {x: P(Y|X=x)}; requires `mix` = P(T=1|X=x) per x.
    threshold: nonzero clinical threshold allowed; decision compares
    RD against -threshold for adverse outcomes.
    """
    if prev1 is None and arm_weights is None:
        return LPResult(DecisionVerdict.UNSUPPORTED, math.nan, math.nan, -1,
                        math.nan, math.nan,
                        "stratum prevalence P(X=1) not supplied")
    if arm_weights is not None:
        q0, q1 = arm_weights
        return _unequal_weight_lp(q0, q1, *study_margins, target_x, threshold)
    q = prev1
    res, err = _lp_bounds(q, *study_margins, target_x,
                          outcome_margin=outcome_margin, mix=mix,
                          threshold=threshold)
    if res is None:
        return LPResult(DecisionVerdict.UNSUPPORTED, math.nan, math.nan, -1,
                        math.nan, math.nan, err)
    return res


def _unequal_weight_lp(q0, q1, p0bar, p1bar, target_x, threshold, tol=1e-9):
    A_eq = [[1 - q0, q0, 0, 0], [0, 0, 1 - q1, q1]]
    b_eq = [p0bar, p1bar]
    c = [0, 0, 0, 0]
    c[2 + target_x], c[target_x] = 1.0, -1.0
    lo = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, 1)] * 4, method="highs")
    hi = linprog([-v for v in c], A_eq=A_eq, b_eq=b_eq, bounds=[(0, 1)] * 4,
                 method="highs")
    if lo.status == 2 or hi.status == 2:
        return LPResult(DecisionVerdict.INFEASIBLE, math.nan, math.nan,
                        2, math.nan, tol, "infeasible under arm-specific weights")
    if lo.status != 0 or hi.status != 0:
        return LPResult(DecisionVerdict.UNSUPPORTED, math.nan, math.nan,
                        1, math.nan, tol, "solver failure")
    l, h = lo.fun, -hi.fun
    if h < -threshold - tol:
        v = DecisionVerdict.ROBUST_TREAT
    elif l > -threshold + tol:
        v = DecisionVerdict.ROBUST_NO_TREAT
    else:
        v = DecisionVerdict.REVERSIBLE
    resid = max(np.max(np.abs(np.array(A_eq) @ lo.x - np.array(b_eq))),
                np.max(np.abs(np.array(A_eq) @ hi.x - np.array(b_eq))))
    return LPResult(v, l, h, 0, resid, tol,
                    f"arm-specific weights q0={q0}, q1={q1}; RD in [{l:.6f},{h:.6f}]")


def borrow_check(subgroups, target_name):
    """RETROSPECTIVE leave-one-subgroup-out demonstration.

    This pools the *other* subgroups' log-RRs (fixed effect) and compares
    with the held-out subgroup's actual crude RR.  It is a historical
    diagnostic of what *would have* happened under unexamined pooling —
    NOT prospective validation, NOT a Bayesian borrowing method, and the
    held-out estimate must never be used to select a borrowing policy.
    Pooling is inappropriate when endpoints, populations, or adjustment
    differ; crude RR ≠ adjusted RR.
    """
    others = [s for s in subgroups if s.name != target_name]
    tgt = [s for s in subgroups if s.name == target_name][0]
    ws, es = [], []
    for s in others:
        rr, lo, hi = s.rr()
        se = (math.log(hi) - math.log(lo)) / 3.92
        ws.append(1 / se**2); es.append(math.log(rr))
    mu = sum(w * e for w, e in zip(ws, es)) / sum(ws)
    se = math.sqrt(1 / sum(ws))
    pred = (math.exp(mu), math.exp(mu - 1.96 * se), math.exp(mu + 1.96 * se))
    act = tgt.rr()
    reversal = (pred[0] < 1) != (act[0] < 1)
    overlap = not (pred[2] < act[1] or act[2] < pred[1])
    return dict(target=target_name, pooled_pred=tuple(round(v, 3) for v in pred),
                actual=tuple(round(v, 3) for v in act),
                direction_reversal=reversal, ci_overlap=overlap,
                caveat="retrospective demonstration; crude vs adjusted RR; "
                       "pooling inappropriate across differing endpoints/populations")
