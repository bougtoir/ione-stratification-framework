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


def load_builtin(name):
    key = name.lower()
    if key in ("recovery", "recovery_dex", "dexamethasone"):
        return RECOVERY
    raise KeyError(f"unknown built-in study {name!r}; available: recovery")
