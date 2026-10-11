"""Minimal additional-information (augmentation) suggestions.

Ordered output hierarchy — cheaper, less burdensome options first:
  (i)   re-tabulation of already-collected data   (cost ~ 0)
  (ii)  new measurement on existing cohorts       (cost medium)
  (iii) new prospective enrollment / stratum RCT  (cost high)
  (iv)  abstain — nothing publishable resolves it
"""
from __future__ import annotations

from dataclasses import dataclass
from .identifiability import DecisionVerdict


@dataclass
class AugmentationOption:
    kind: str            # 're_tabulation' | 'new_measurement' | 'new_enrollment' | 'abstain'
    label: str
    resolves: bool       # whether it can resolve the current ambiguity
    cost_class: int      # 0..3 ascending burden
    note: str = ""


CATALOG = {
    "arm_by_stratum_crosstab": AugmentationOption(
        "re_tabulation",
        "arm × stratum outcome cross-tabulation of existing records",
        True, 0, "two equations per stratum -> collapses M(T)"),
    "stratum_baseline_risk": AugmentationOption(
        "re_tabulation",
        "per-stratum baseline (control-arm) risk",
        True, 0, "plus p(Y|X) margin recovers treated risk"),
    "extra_endpoint_or_horizon": AugmentationOption(
        "re_tabulation",
        "already-collected alternative endpoint / horizon table",
        False, 0, "resolves other estimands, not effect modification"),
    "measure_new_modifier": AugmentationOption(
        "new_measurement",
        "measure the suspected unmeasured effect modifier",
        True, 1, "only option when ambiguity lives in an unmeasured channel"),
    "stratum_rct": AugmentationOption(
        "new_enrollment",
        "prospective randomized cohort restricted to the target stratum",
        True, 3, "last resort when no summary can fix the decision"),
    "abstain": AugmentationOption(
        "abstain", "no publishable summary resolves the decision",
        False, 4, "return UNIDENTIFIABLE / INSUFFICIENT_AGGREGATE_DATA"),
}


def suggest_augmentation(audit_result, unmeasured_modifier=False,
                         crosstab_available=True):
    """Order the cheapest sufficient augmentation for the verdict.

    - SUFFICIENT -> nothing needed.
    - REVERSIBLE -> prefer re-tabulation; if ambiguity is in an
      unmeasured modifier, re-tabulation cannot resolve -> new
      measurement; escalate to stratum RCT only when measurement is
      infeasible; abstain if even that cannot help.
    - UNIDENTIFIABLE -> abstain or stratum RCT if the stratum is
      enrollable.
    """
    v = audit_result.verdict
    if v is DecisionVerdict.SUFFICIENT:
        return [AugmentationOption("none", "decision already robust",
                                 True, 0, "no augmentation required")]
    if v is DecisionVerdict.REVERSIBLE:
        if unmeasured_modifier:
            return [CATALOG["measure_new_modifier"], CATALOG["stratum_rct"],
                    CATALOG["abstain"]]
        opts = [CATALOG["arm_by_stratum_crosstab"],
                CATALOG["stratum_baseline_risk"]]
        if not crosstab_available:
            opts += [CATALOG["stratum_rct"], CATALOG["abstain"]]
        else:
            opts += [CATALOG["stratum_rct"]]
        return opts
    # UNIDENTIFIABLE
    return [CATALOG["stratum_rct"], CATALOG["abstain"]]
