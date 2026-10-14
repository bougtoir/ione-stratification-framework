"""IONE (Identifiability-Oriented Navigation of Evidence) — aggregate-evidence decision audit toolkit.

Implements, on top of the historical stratification framework:
- aggregate evidence sufficiency audit from published arm-level counts
- identifiability / compatible-model (M(T)) decision-robustness verdicts
- minimal additional-information suggestions (re-tabulation -> new
  measurement -> new enrollment -> abstain)

No individual-patient data is required or produced.
"""

from .aggregate import ArmCount, SubgroupTable, EffectSummary
from .identifiability import audit_decision, DecisionVerdict
from .augmentation import suggest_augmentation, AugmentationOption
from .proximity import ProximityProfile

__version__ = "0.1.0"
__all__ = [
    "ArmCount", "SubgroupTable", "EffectSummary",
    "audit_decision", "DecisionVerdict",
    "suggest_augmentation", "AugmentationOption",
    "ProximityProfile",
]
