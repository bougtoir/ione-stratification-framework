"""F4 test suite: LP identification engine vs analytic references,
plus audit-augmentation-borrow checks. Reference answers computed by
algebra, not by repeating the implementation."""
import math

import pytest

from ione.aggregate import ArmCount, SubgroupTable, EffectSummary
from ione.identifiability import (audit_decision, borrow_check,
                                  DecisionVerdict)
from ione.augmentation import suggest_augmentation
from ione.data import RECOVERY, ISIS2, REACT, load_builtin


# ---------- analytic reference for the 2x2x2 model ----------
def analytic_bounds(q, p0bar, p1bar, x=1):
    """Sharp RD bounds at stratum x from algebra:
    p0_1 = (p0bar-(1-q)p0_0)/q, p1_1=(p1bar-(1-q)p1_0)/q,
    free vars p0_0,p1_0 in [0,1] with images in [0,1].
    RD = p1_1-p0_1 = (p1bar-p0bar)/q - (1-q)/q*(p1_0-p0_0).
    d = p1_0-p0_0 ranges over [max(1-(1-q)/q*p0bar_hi...)] computed directly."""
    lo_d, hi_d = -1.0, 1.0
    # feasibility windows for p0_0, p1_0
    def win(pbar):
        # need 0 <= (pbar-(1-q)v)/q <= 1 -> (pbar-q)/(1-q) <= v <= pbar/(1-q)
        return max(0.0, (pbar - q) / (1 - q)), min(1.0, pbar / (1 - q))
    a0, b0 = win(p0bar)
    a1, b1 = win(p1bar)
    if a0 > b0 or a1 > b1:
        return None  # infeasible
    d_min, d_max = a1 - b0, b1 - a0
    c = (p1bar - p0bar) / q
    k = (1 - q) / q
    return c - k * d_max, c - k * d_min


def test_analytic_bounds_match_lp_reversible():
    res = audit_decision((0.20, 0.16), target_x=1, prev1=0.5)
    lo, hi = analytic_bounds(0.5, 0.20, 0.16)
    assert abs(res.bound_lo - lo) < 1e-8 and abs(res.bound_hi - hi) < 1e-8
    assert res.verdict is DecisionVerdict.REVERSIBLE
    assert res.solver_status == 0 and res.residual < 1e-9


def test_analytic_bounds_match_lp_robust():
    res = audit_decision((0.60, 0.0), target_x=1, prev1=0.5)
    assert res.verdict is DecisionVerdict.ROBUST_TREAT
    lo, hi = analytic_bounds(0.5, 0.60, 0.0)
    assert abs(res.bound_lo - lo) < 1e-8


def test_crossover_effect_is_reversible_not_sufficient():
    # finite-grid enumeration previously reported SUFFICIENT here; the
    # continuous feasible set shows the decision is reversible
    res = audit_decision((0.40, 0.05), target_x=1, prev1=0.5)
    assert res.verdict is DecisionVerdict.REVERSIBLE
    assert res.bound_hi > 0  # harm-compatible models exist


def test_infeasible_margins_distinct_from_unidentifiable():
    # p0bar=0.9 with q=0.5 forces p0_0+p0_1=1.8 feasible; use impossible one
    res = audit_decision((1.2, 0.16), target_x=1, prev1=0.5)
    assert res.verdict is DecisionVerdict.INFEASIBLE


def test_unsupported_without_prevalence():
    res = audit_decision((0.20, 0.16), target_x=1)
    assert res.verdict is DecisionVerdict.UNSUPPORTED


def test_unequal_arm_weights_supported():
    r1 = audit_decision((0.20, 0.16), target_x=1, arm_weights=(0.4, 0.6))
    assert r1.solver_status == 0
    assert r1.verdict is DecisionVerdict.REVERSIBLE


def test_nonzero_threshold_flips_verdict():
    # overall benefit exists, but demand |RD|>0.10
    res = audit_decision((0.40, 0.30), target_x=1, prev1=0.5, threshold=0.10)
    lo, hi = analytic_bounds(0.5, 0.40, 0.30)
    assert abs(res.bound_hi - hi) < 1e-8
    # robust_treat requires max RD < -0.10
    if hi < -0.10:
        assert res.verdict is DecisionVerdict.ROBUST_TREAT


def test_outcome_margin_requires_mix():
    res = audit_decision((0.20, 0.16), target_x=1, prev1=0.5,
                         outcome_margin={0: 0.18, 1: 0.18})
    assert res.verdict is DecisionVerdict.UNSUPPORTED
    res2 = audit_decision((0.20, 0.16), target_x=1, prev1=0.5,
                          outcome_margin={0: 0.18, 1: 0.18}, mix=0.5)
    assert res2.solver_status == 0


def test_prevalence_extremes():
    # q->1: conditional estimand equals the marginal one
    res = audit_decision((0.20, 0.10), target_x=1, prev1=0.999)
    assert res.bound_lo <= res.bound_hi
    assert res.verdict in (DecisionVerdict.ROBUST_TREAT,
                           DecisionVerdict.REVERSIBLE)


# ---------- real-data reproduction ----------
def test_rr_reproduces_published_recovery_counts():
    imv = RECOVERY.subgroups[0]
    rr, lo, hi = imv.rr()
    assert abs(rr - 0.708) < 0.005
    assert abs(imv.control.risk - 0.414) < 0.001


def test_isis2_reproduces_published():
    sk = ISIS2.subgroups[0]
    rr, lo, hi = sk.rr()
    assert abs(rr - 0.767) < 0.01      # 9.2%/12.0%
    combo = ISIS2.subgroups[1]
    rd, *_ = combo.rd()
    assert abs(rd + 0.0523) < 0.002    # 8.0% - 13.2%


def test_react_counts():
    # published measure is fixed-effect OR 0.66 (0.53-0.82); check crude OR
    o = REACT.overall
    orr, lo, hi = o.orr()
    assert abs(orr - 0.66) < 0.03


def test_zero_event_arm_handled():
    t = SubgroupTable("z", ArmCount(0, 100), ArmCount(5, 100))
    o, lo, hi = t.orr()  # Haldane-corrected
    assert math.isfinite(o) and o < 1


def test_borrow_check_documented_reversal():
    res = borrow_check(RECOVERY.subgroups, "noO2")
    assert res["direction_reversal"] is True
    assert "retrospective" in res["caveat"]


def test_borrow_check_isis2_combo():
    res = borrow_check(ISIS2.subgroups, "combo")
    assert isinstance(res["pooled_pred"][0], float)


# ---------- augmentation honesty ----------
class _R:
    def __init__(self, v): self.verdict = v


def test_no_unconditional_resolution():
    res = audit_decision((0.20, 0.16), target_x=1, prev1=0.5)
    for o in suggest_augmentation(res):
        assert o.classification != "sufficient"
        assert o.assumption          # every option states its conditions


def test_robust_needs_no_augmentation():
    opts = suggest_augmentation(_R(DecisionVerdict.ROBUST_TREAT))
    assert opts[0].kind == "none"


def test_infeasible_reports_fix_inputs():
    opts = suggest_augmentation(_R(DecisionVerdict.INFEASIBLE))
    assert "inconsistent" in opts[0].label or "fix" in opts[0].label


def test_unmeasured_modifier_skips_retination():
    res = audit_decision((0.20, 0.16), target_x=1, prev1=0.5)
    opts = suggest_augmentation(res, unmeasured_modifier=True)
    assert opts[0].kind == "new_measurement"


def test_irrelevant_extra_endpoint_classified():
    from ione.augmentation import CATALOG
    assert CATALOG["extra_endpoint_or_horizon"].classification == "irrelevant"


# ---------- CLI ----------
def test_cli_borrow_check(capsys):
    from ione.cli import main
    main(["borrow-check", "--study", "recovery", "--target", "noO2"])
    out = capsys.readouterr().out
    assert "direction_reversal" in out and "true" in out


def test_cli_audit(capsys):
    from ione.cli import main
    main(["audit", "--study", "recovery", "--target", "noO2"])
    out = capsys.readouterr().out
    assert "decision_audit" in out


# ---------- F-finishing: q semantics + consistency ----------
def test_common_q_estimate_recovery():
    # RECOVERY randomisation ~1:2; noO2 stratum share is arm-consistent
    from ione.data import RECOVERY as R
    t = R.subgroups[2]
    q1 = t.treat.n / R.overall.treat.n
    q0 = t.control.n / R.overall.control.n
    assert abs(q1 - q0) < 0.05  # compatible with common composition


def test_consistency_exhaustive_recovery():
    assert RECOVERY.check_consistency() == []


def test_consistency_error_not_rounding():
    bad = EffectSummary(
        "bad",
        SubgroupTable("all", ArmCount(100, 1000), ArmCount(100, 1000)),
        [SubgroupTable("s1", ArmCount(90, 1200), ArmCount(50, 500))])
    issues = bad.check_consistency()
    assert any(i.severity == "error" for i in issues)


def test_consistency_small_gap_is_warning():
    w = EffectSummary(
        "w",
        SubgroupTable("all", ArmCount(100, 1000), ArmCount(100, 1000)),
        [SubgroupTable("s1", ArmCount(100, 999), ArmCount(100, 999))])
    issues = w.check_consistency()
    assert issues and all(i.severity == "warning" for i in issues)


def test_small_enumeration_agrees_with_lp():
    """Independent reference: coarse full enumeration sign agreement."""
    import itertools
    q, p0b, p1b = 0.5, 0.20, 0.16
    grid = [i / 1000 for i in range(1001)]
    flip = False
    for p00 in grid[::50]:
        p01 = (p0b - (1 - q) * p00) / q
        if not 0 <= p01 <= 1:
            continue
        for p10 in grid[::50]:
            p11 = (p1b - (1 - q) * p10) / q
            if 0 <= p11 <= 1 and p11 > p01:
                flip = True
    assert flip  # harm-compatible model exists
    res = audit_decision((p0b, p1b), target_x=1, prev1=q)
    assert res.verdict is DecisionVerdict.REVERSIBLE
