"""Built-in, source-verified aggregate datasets (published counts only)."""
from __future__ import annotations

from .aggregate import ArmCount, SubgroupTable, EffectSummary

# RECOVERY Collaborative Group, NEJM 2021;384:693-704. DOI 10.1056/NEJMoa2021436.
# 28-day mortality by baseline respiratory support; counts cross-verified
# against the published figure and independent tabulations (see docs).
RECOVERY = EffectSummary(
    study="RECOVERY dexamethasone (NEJM 2021)",
    overall=SubgroupTable(
        "overall", ArmCount(482, 2104), ArmCount(1110, 4321),
        metadata=dict(doi="10.1056/NEJMoa2021436", outcome="28d mortality")),
    subgroups=[
        SubgroupTable("IMV", ArmCount(95, 324), ArmCount(283, 683)),
        SubgroupTable("O2", ArmCount(298, 1279), ArmCount(682, 2604)),
        SubgroupTable("noO2", ArmCount(89, 501), ArmCount(145, 1034)),
    ])


# ISIS-2 Collaborative Group, Lancet 1988;2:349-360. doi:10.1016/S0140-6736(88)92833-4.
# 5-week vascular mortality, 2x2 factorial (aspirin x streptokinase).
ISIS2 = EffectSummary(
    study="ISIS-2 aspirin/streptokinase (Lancet 1988)",
    overall=SubgroupTable(
        "overall_aspirin", ArmCount(804, 8587), ArmCount(1016, 8600),
        metadata=dict(doi="10.1016/S0140-6736(88)92833-4",
                      outcome="5-week vascular mortality")),
    subgroups=[
        SubgroupTable("streptokinase", ArmCount(791, 8592), ArmCount(1029, 8595)),
        SubgroupTable("combo", ArmCount(343, 4292), ArmCount(568, 4300)),
    ])

# WHO REACT Working Group / Sterne JAC et al., JAMA 2020;324(13):1330-1341.
# doi:10.1001/jama.2020.17023. Prospective meta-analysis, 7 RCTs, critically ill.
REACT = EffectSummary(
    study="WHO REACT corticosteroid meta-analysis (JAMA 2020)",
    overall=SubgroupTable(
        "overall", ArmCount(222, 678), ArmCount(425, 1025),
        metadata=dict(doi="10.1001/jama.2020.17023",
                      outcome="28-day all-cause mortality",
                      effect_measure_published="OR 0.66 (0.53-0.82) fixed-effect")),
    subgroups=[
        SubgroupTable("serious_adverse_events", ArmCount(64, 354), ArmCount(80, 342)),
    ])


def load_builtin(name):
    key = name.lower()
    if key in ("recovery", "recovery_dex", "dexamethasone"):
        return RECOVERY
    if key in ("isis2", "isis-2"):
        return ISIS2
    if key in ("react", "who_react"):
        return REACT
    raise KeyError(f"unknown built-in study {name!r}; "
                   "available: recovery, isis2, react")
