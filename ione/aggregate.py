"""Aggregate arm-level evidence containers and effect estimates.

All inputs are *published aggregate counts* — never pseudo-IPD.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class ArmCount:
    """Event count for one arm of one subgroup (or the whole study)."""
    events: int
    n: int

    @property
    def risk(self) -> float:
        if self.n <= 0:
            raise ValueError("empty arm: n must be positive")
        return self.events / self.n

    @property
    def nonestimable(self) -> bool:
        return self.n == 0 or self.events == 0


@dataclass
class SubgroupTable:
    """Published treatment-vs-control counts for one subgroup."""
    name: str
    treat: ArmCount
    control: ArmCount
    metadata: dict = field(default_factory=dict)

    def rr(self):
        """Crude risk ratio with Wald CI on log scale."""
        a, n1 = self.treat.events, self.treat.n
        b, n0 = self.control.events, self.control.n
        rr = (a / n1) / (b / n0)
        se = math.sqrt(1 / a - 1 / n1 + 1 / b - 1 / n0)
        return rr, rr * math.exp(-1.96 * se), rr * math.exp(1.96 * se)

    def rd(self):
        """Crude risk difference (treat - control) with Wald CI."""
        a, n1 = self.treat.events, self.treat.n
        b, n0 = self.control.events, self.control.n
        rd = a / n1 - b / n0
        se = math.sqrt(
            a / n1 * (1 - a / n1) / n1 + b / n0 * (1 - b / n0) / n0)
        return rd, rd - 1.96 * se, rd + 1.96 * se

    def orr(self):
        """Crude odds ratio with CI (0 events -> Haldane correction)."""
        a, n1 = self.treat.events, self.treat.n
        b, n0 = self.control.events, self.control.n
        if min(a, b, n1 - a, n0 - b) == 0:
            a, b = a + 0.5, b + 0.5
            n1, n0 = n1 + 1, n0 + 1
        o = (a / (n1 - a)) / (b / (n0 - b))
        se = math.sqrt(1 / a + 1 / (n1 - a) + 1 / b + 1 / (n0 - b))
        return o, o * math.exp(-1.96 * se), o * math.exp(1.96 * se)


@dataclass
class ConsistencyIssue:
    kind: str      # 'n_mismatch' | 'event_mismatch' | 'overlap' | 'rounding'
    detail: str
    severity: str  # 'error' (contradiction) or 'warning' (treatable as rounding/reporting gap)


@dataclass
class EffectSummary:
    """A study's published aggregate results: overall + subgroup tables."""
    study: str
    overall: SubgroupTable
    subgroups: list = field(default_factory=list)

    def check_consistency(self, rel_tol=0.01, abs_tol=1):
        """Verify subgroup aggregates are consistent with overall counts.

        Exhaustive strata must sum to the overall; non-exhaustive strata
        must not exceed it.  Small discrepancies are returned as
        'warning' (rounding/reporting gaps), not contradictions.
        Returns list[ConsistencyIssue]; empty = consistent.
        """
        issues = []
        tn = sum(s.treat.n for s in self.subgroups)
        cn = sum(s.control.n for s in self.subgroups)
        te = sum(s.treat.events for s in self.subgroups)
        ce = sum(s.control.events for s in self.subgroups)
        for label, sub_total, ov in (
                ("treat_n", tn, self.overall.treat.n),
                ("control_n", cn, self.overall.control.n),
                ("treat_events", te, self.overall.treat.events),
                ("control_events", ce, self.overall.control.events)):
            diff = sub_total - ov
            tol = max(abs_tol, rel_tol * ov)
            if diff > tol:
                issues.append(ConsistencyIssue(
                    "n_mismatch" if label.endswith("n") else "event_mismatch",
                    f"{label}: subgroups sum {sub_total} exceeds overall {ov}",
                    "error"))
            elif diff != 0 and abs(diff) <= tol:
                issues.append(ConsistencyIssue(
                    "rounding",
                    f"{label}: subgroups sum {sub_total} vs overall {ov} "
                    f"(within tolerance; likely rounding or unpublished stratum)",
                    "warning"))
        # duplicate stratum names -> overlap risk
        names = [s.name for s in self.subgroups]
        if len(names) != len(set(names)):
            issues.append(ConsistencyIssue(
                "overlap", "duplicate subgroup names; strata may overlap",
                "error"))
        return issues

    def sufficiency_report(self):
        """Return {subgroup: (rr, lo, hi, rd, identifiable, nonestimable)}."""
        out = {}
        for s in [self.overall] + self.subgroups:
            nonest = s.treat.n == 0 or s.control.n == 0
            if nonest:
                out[s.name] = dict(nonestimable=True)
                continue
            rr = s.rr(); rd = s.rd()
            out[s.name] = dict(
                rr=(round(rr[0], 4), round(rr[1], 4), round(rr[2], 4)),
                rd=(round(rd[0], 4), round(rd[1], 4), round(rd[2], 4)),
                treat_n=s.treat.n, control_n=s.control.n,
                identifiable=True, nonestimable=False)
        return out
