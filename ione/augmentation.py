"""Minimal additional-information (augmentation) suggestions.

Ordered preference — cheaper, less burdensome options considered first:
  (i)   re-tabulation of already-collected data   (cost ~ 0)
  (ii)  new measurement on existing cohorts       (cost medium)
  (iii) new prospective enrollment / stratum RCT  (cost high)
  (iv)  abstain — nothing publishable resolves it

Honesty rules (F2): no option carries an unconditional `resolves=True`.
Each option is classified:
  sufficient_assumed     demonstrably sufficient ONLY under stated assumptions
  potentially_informative may reduce bounds but no guarantee of resolution
  irrelevant             does not constrain the current estimand
  infeasible             cannot be produced / not available
  unknown                effect on the audit cannot be predicted
No unjustified minimum sample size is emitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from .identifiability import DecisionVerdict


@dataclass
class AugmentationOption:
    kind: str            # 're_tabulation' | 'new_measurement' | 'new_enrollment' | 'abstain' | 'none'
    label: str
    classification: str  # sufficient_assumed | potentially_informative | irrelevant | infeasible | unknown
    cost_class: int      # 0..3 ascending burden
    assumption: str      # assumptions under which classification holds
    note: str = ""


CATALOG = {
    "arm_by_stratum_crosstab": AugmentationOption(
        "re_tabulation",
        "arm × stratum outcome cross-tabulation of existing records",
        "sufficient_assumed", 0,
        "joint table is publishable & consented; table values unknown a priori —"
        " post-information decision still depends on the actual cells",
        "yields 2 equations/stratum -> feasible set shrinks to a point for a"
        " binary stratum; identifiability gain is structural"),
    "stratum_baseline_risk": AugmentationOption(
        "re_tabulation",
        "per-stratum baseline (control-arm) risk",
        "sufficient_assumed", 0,
        "combined with a P(Y|X) margin at known mixing proportion it pins the"
        " treated risk; without the margin it only halves the feasible width",
        "half-identifiability without companion summary"),
    "stratum_prev_alone": AugmentationOption(
        "re_tabulation",
        "per-arm stratum prevalence (arm-specific P(X=1|arm))",
        "potentially_informative", 0,
        "removes equal-composition assumption; does not constrain risks"),
    "extra_endpoint_or_horizon": AugmentationOption(
        "re_tabulation",
        "already-collected alternative endpoint / horizon table",
        "irrelevant", 0,
        "addresses a different estimand; does not bound the current RD"),
    "measure_new_modifier": AugmentationOption(
        "new_measurement",
        "measure the suspected unmeasured effect modifier",
        "sufficient_assumed", 1,
        "only if the measured variable is in fact the ambiguity channel and a"
        " joint cross-tab becomes available; otherwise unknown"),
    "stratum_rct": AugmentationOption(
        "new_enrollment",
        "prospective randomized cohort restricted to the target stratum",
        "sufficient_assumed", 3,
        "yields unbiased stratum-specific RD if feasible size/assent exist;"
        " sample-size claims require a scenario-conditional calculation"),
    "abstain": AugmentationOption(
        "abstain", "no publishable summary can be shown to resolve the decision",
        "unknown", 4, "audit output should carry the abstention"),
}


def suggest_augmentation(audit_result, unmeasured_modifier=False,
                         crosstab_available=True):
    """Ordered augmentation plan for the LP verdict — no guarantees."""
    v = audit_result.verdict
    if v in (DecisionVerdict.ROBUST_TREAT, DecisionVerdict.ROBUST_NO_TREAT,
             DecisionVerdict.SUFFICIENT):
        return [AugmentationOption("none", "decision already robust over M(T)",
                                   "irrelevant", 0,
                                   "no augmentation required")]
    if v is DecisionVerdict.INFEASIBLE:
        return [AugmentationOption(
            "none", "inputs inconsistent — fix reporting, not design",
            "irrelevant", 0, "empty feasible set, not nonidentification")]
    if v is DecisionVerdict.UNSUPPORTED:
        return [CATALOG["stratum_prev_alone"], CATALOG["abstain"]]
    # REVERSIBLE
    if unmeasured_modifier:
        return [CATALOG["measure_new_modifier"], CATALOG["stratum_rct"],
                CATALOG["abstain"]]
    opts = [CATALOG["arm_by_stratum_crosstab"], CATALOG["stratum_baseline_risk"]]
    if not crosstab_available:
        opts += [CATALOG["stratum_rct"], CATALOG["abstain"]]
    else:
        opts += [CATALOG["stratum_rct"]]
    return opts
