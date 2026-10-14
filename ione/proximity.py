"""Decision-evidence proximity profile (formal name; 'avatar proximity'
is metaphor only). Deliberately not a single scalar."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProximityProfile:
    """status, missing-information channels, robustness margin, top-z."""
    status: str                        # SUFFICIENT | REVERSIBLE | UNIDENTIFIABLE
    channels: list = field(default_factory=list)   # e.g. ["respiratory_support","age"]
    margin_neg: str = ""               # textual: sign of the point estimate vs threshold
    top_z: str = ""                    # most decision-relevant missing channel
    notes: str = ""

    def to_dict(self):
        return dict(status=self.status, channels=self.channels,
                    margin_neg=self.margin_neg, top_z=self.top_z,
                    notes=self.notes)
