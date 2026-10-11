"""Tests for the IONE aggregate-evidence audit toolkit."""
import math

from ione.aggregate import ArmCount, SubgroupTable
from ione.identifiability import (audit_decision, borrow_check,
                                  DecisionVerdict)
from ione.augmentation import suggest_augmentation
from ione.data import RECOVERY, load_builtin


def test_rr_reproduces_published_recovery_counts():
    imv = RECOVERY.subgroups[0]
    rr, lo, hi = imv.rr()
    assert abs(rr - 0.708) < 0.005          # crude RR
    assert imv.treat.risk == 95 / 324
    assert abs(imv.control.risk - 0.414) < 0.001


def test_rd_matches_published_percentages():
    n = RECOVERY.subgroups[2]  # no-O2
    rd, lo, hi = n.rd()
    assert abs(rd - 0.0374) < 0.005         # +3.7pp harm direction


def test_borrow_check_documented_reversal():
    """Pooled IMV+O2 predicts benefit for no-O2; actual is harm."""
    res = borrow_check(RECOVERY.subgroups, "noO2")
    assert res["direction_reversal"] is True
    assert res["pooled_pred"][0] < 1.0 <= res["actual"][0] - 1e-9 or \
        res["actual"][0] > 1.0


def test_decision_audit_reversal_example():
    """I2-(i): identical margins, two compatible models, decision flips."""
    # margins p0bar=0.20, p1bar=0.16 at P(X=1)=0.5 -> REVERSIBLE
    res = audit_decision((0.20, 0.16), target_x=1, prev1=0.5, resolution=41)
    assert res.verdict is DecisionVerdict.REVERSIBLE
    assert res.actions.get("treat", 0) > 0 and res.actions.get("notreat", 0) > 0


def test_decision_audit_sufficient_when_effect_large():
    # p1bar=0 forces p1_x=0 for all x; p0bar=0.60 forces p0_1>=0.2>0
    res = audit_decision((0.60, 0.0), target_x=1, prev1=0.5, resolution=41)
    assert res.verdict is DecisionVerdict.SUFFICIENT


def test_decision_audit_crossover_is_reversible():
    # large overall effect still reverses under extreme compatible models
    res = audit_decision((0.40, 0.05), target_x=1, prev1=0.5, resolution=41)
    assert res.verdict is DecisionVerdict.REVERSIBLE


def test_augmentation_prefers_retination_over_enrollment():
    res = audit_decision((0.20, 0.16), target_x=1, prev1=0.5)
    opts = suggest_augmentation(res)
    assert opts[0].kind == "re_tabulation"
    kinds = [o.kind for o in opts]
    assert kinds.index("new_enrollment") > kinds.index("re_tabulation")


def test_augmentation_unmeasured_modifier_skips_retination():
    res = audit_decision((0.20, 0.16), target_x=1, prev1=0.5)
    opts = suggest_augmentation(res, unmeasured_modifier=True)
    assert opts[0].kind == "new_measurement"


def test_unidentifiable_abstains():
    class R: verdict = DecisionVerdict.UNIDENTIFIABLE
    opts = suggest_augmentation(R())
    assert opts[-1].kind == "abstain"


def test_cli_runs(tmp_path, capsys):
    from ione.cli import main
    main(["borrow-check", "--study", "recovery", "--target", "noO2"])
    out = capsys.readouterr().out
    assert "direction_reversal" in out and "true" in out
