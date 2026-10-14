"""Information-level (L1/L2/L3) audit of aggregate evidence.

Levels, for a pre-specified pre-treatment stratum X of a randomized trial:

  L1  arm-level totals and event counts only (the stratum counts are
      withheld): the stratum-specific risk difference is unidentified;
      the sharp bounds are the trivial [-1, +1] interval.
  L2  L1 plus the stratum size (prevalence) per arm: the published arm
      margins bound the stratum-specific risks through the marginal
      consistency equations (Cross & Manski 2002-type LP bounds).
  L3  L2 plus arm-by-stratum event counts: the stratum-specific crude
      risk difference is point-identified and equals the crude
      difference of proportions.  Sampling uncertainty (a confidence
      interval around that point) is reported separately and never
      conflated with the identified set.

L1 and L2 are *deliberate ablations* when L3 information was in fact
published: they quantify what a reader who ignored the arm-by-stratum
table could still conclude, not a genuine publication gap.  When L3
information was never published, the ladder stops at the highest
reachable level and `reachable` records it.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from scipy.optimize import linprog

from .aggregate import SubgroupTable
from .identifiability import DecisionVerdict, _lp_bounds, _unequal_weight_lp


@dataclass
class LevelResult:
    level: str                    # 'L1' | 'L2' | 'L3'
    reachable: bool               # was this information level available?
    identified_lo: float          # identified-set lower bound (NaN if unreachable)
    identified_hi: float
    point_estimate: float = math.nan   # L3 only: the identified point
    ci: tuple = ()                # L3 only: Wald CI (sampling, not identification)
    verdict: DecisionVerdict = DecisionVerdict.UNSUPPORTED
    constraints: tuple = ()       # the constraints actually used at this level
    note: str = ""


def _verdict(lo, hi, threshold, tol=1e-9):
    if hi < -threshold - tol:
        return DecisionVerdict.ROBUST_TREAT
    if lo > -threshold + tol:
        return DecisionVerdict.ROBUST_NO_TREAT
    return DecisionVerdict.REVERSIBLE


def _verdict_point(rd, threshold, tol=1e-9):
    return (DecisionVerdict.ROBUST_TREAT if rd < -threshold - tol
            else DecisionVerdict.ROBUST_NO_TREAT)


def audit_levels(effect, stratum_name, threshold=0.0,
                 l3_published=True):
    """Run the L1 -> L2 -> L3 audit for one stratum of an EffectSummary.

    `l3_published=False` marks the ablation as a *real* publication gap
    rather than a deliberate withholding of published counts.
    Returns [LevelResult, LevelResult, LevelResult].
    """
    ov, sub = effect.overall, None
    for s in effect.subgroups:
        if s.name == stratum_name:
            sub = s
            break
    out = []

    # ---- L1: overall arm margins only; stratum size withheld ----
    # With no stratum information the stratum RD is bounded by [-1, 1].
    l1 = LevelResult(
        "L1", True, -1.0, 1.0,
        verdict=_verdict(-1.0, 1.0, threshold),
        constraints=("overall arm event counts",),
        note="stratum counts withheld; no prevalence -> trivial bounds")
    out.append(l1)

    # ---- L2: + stratum prevalence (per arm if published separately) ----
    if sub is None or sub.treat.n == 0 or sub.control.n == 0:
        out.append(LevelResult(
            "L2", False, math.nan, math.nan,
            verdict=DecisionVerdict.UNSUPPORTED,
            note="stratum denominators per arm not published -> L2 unreachable"))
        out.append(LevelResult(
            "L3", False, math.nan, math.nan,
            verdict=DecisionVerdict.UNSUPPORTED,
            note="arm-by-stratum event counts not published -> L3 unreachable"))
        return out

    q1 = sub.treat.n / ov.treat.n
    q0 = sub.control.n / ov.control.n
    p0, p1 = ov.control.risk, ov.treat.risk
    cons = ("overall arm event counts",
            "arm-by-stratum denominators (prevalence)")
    if abs(q1 - q0) > 1e-9:
        res = _unequal_weight_lp(q0, q1, p0, p1, 1, threshold)
    else:
        res, _ = _lp_bounds(q0, p0, p1, 1, threshold=threshold)
    l2 = LevelResult(
        "L2", True, res.bound_lo, res.bound_hi,
        verdict=res.verdict, constraints=cons,
        note=(f"LP bounds on stratum RD; q0={q0:.4f}, q1={q1:.4f}"
              + ("; deliberate ablation" if l3_published
                 else "; maximal published level")))
    out.append(l2)

    # ---- L3: + arm-by-stratum event counts -> point-identified crude RD ----
    if not l3_published or sub.treat.events is None:
        out.append(LevelResult(
            "L3", False, math.nan, math.nan,
            verdict=DecisionVerdict.UNSUPPORTED,
            note="arm-by-stratum event counts not published -> L3 unreachable"))
        return out
    rd, lo_ci, hi_ci = sub.rd()
    l3 = LevelResult(
        "L3", True, rd, rd, point_estimate=rd, ci=(lo_ci, hi_ci),
        verdict=_verdict_point(rd, threshold),
        constraints=cons + ("arm-by-stratum event counts",),
        note="crude stratum RD point-identified; CI is sampling uncertainty")
    out.append(l3)
    return out


def check_monotone(results, tol=1e-8):
    """Regression check: adding constraints must not enlarge the
    identified set (L1 superset-of L2 superset-of L3 point in interval)."""
    l1, l2, l3 = results
    ok = True
    msgs = []
    if l2.reachable:
        if l2.identified_lo < l1.identified_lo - tol or \
           l2.identified_hi > l1.identified_hi + tol:
            ok = False; msgs.append("L2 escapes L1 bounds")
    if l3.reachable:
        if not (l2.identified_lo - tol <= l3.point_estimate <=
                l2.identified_hi + tol):
            ok = False; msgs.append("L3 point outside L2 identified set")
    return ok, msgs
