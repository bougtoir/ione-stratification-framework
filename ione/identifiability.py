"""Identifiability and decision-robustness audit over the compatible
model set M(T).

Given published margins (arm-level event rates, subgroup table, Table-1
margin), enumerate compatible conditional models and test whether the
clinical decision is invariant for a target subgroup.  Exact
enumeration on a grid — no sampling.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import Enum

from .aggregate import SubgroupTable


class DecisionVerdict(str, Enum):
    SUFFICIENT = "SUFFICIENT"        # one action optimal in all compatible models
    REVERSIBLE = "REVERSIBLE"        # decision flips across compatible models
    UNIDENTIFIABLE = "UNIDENTIFIABLE"  # required summary cannot be produced at all


@dataclass
class AuditResult:
    verdict: DecisionVerdict
    n_compatible: int
    actions: dict           # action -> count of compatible models choosing it
    detail: str


def _compatible_models(p0bar, p1bar, prev1, grid):
    """Enumerate models consistent with margins, in O(grid^2).

    Margins: p0bar = (1-q)*p0_0 + q*p0_1 ; p1bar = (1-q)*p1_0 + q*p1_1.
    Parametrize by (p0_0, p1_0); the x=1 values are then determined.
    """
    q = prev1
    sols = []
    for p00, p10 in itertools.product(grid, repeat=2):
        p01 = (p0bar - (1 - q) * p00) / q
        p11 = (p1bar - (1 - q) * p10) / q
        if 0 <= p01 <= 1 and 0 <= p11 <= 1:
            sols.append({0: (p00, p10), 1: (p01, p11)})
    return sols


def _compatible_with_margin_py(models, prev1, pY):
    """Restrict to models that also match published outcome margin p(Y|X)
    under balanced arms: p(Y|x) = 0.5*(p0_x + p1_x)."""
    out = []
    for m in models:
        ok = all(abs(0.5 * (m[x][0] + m[x][1]) - pY[x]) < 1e-9 for x in m)
        if ok:
            out.append(m)
    return out


def audit_decision(study_margins, target_x=1, prev1=0.5,
                   outcome_margin=None, resolution=41):
    """Audit whether the treat/not-treat decision at subgroup target_x is
    robust across all models compatible with the published margins.

    study_margins: (p0bar, p1bar) overall arm-level event rates.
    outcome_margin: optional {x: p(Y|x)} published combined-arm margin.
    Returns AuditResult with explicit counts (data nonidentification,
    not a model-based interval).
    """
    grid = [i / (resolution - 1) for i in range(resolution)]
    p0bar, p1bar = study_margins
    models = _compatible_models(p0bar, p1bar, prev1, grid)
    if outcome_margin is not None:
        models = _compatible_with_margin_py(models, prev1, outcome_margin)
    if not models:
        return AuditResult(DecisionVerdict.UNIDENTIFIABLE, 0, {},
                           "no compatible model (reports inconsistent)")
    acts = {}
    for m in models:
        p0x, p1x = m[target_x]
        a = "treat" if p1x < p0x else "notreat"
        acts[a] = acts.get(a, 0) + 1
    verdict = (DecisionVerdict.SUFFICIENT if len(acts) == 1
               else DecisionVerdict.REVERSIBLE)
    return AuditResult(verdict, len(models), acts,
                       f"{len(models)} compatible models; actions {acts}")


def borrow_check(subgroups, target_name):
    """Leave-one-subgroup-out borrow check on real subgroup tables.

    Pool the other subgroups' log-RRs (fixed effect) and compare with the
    held-out subgroup's actual RR.  Returns dict with direction_reversal
    flag — the documented failure mode of unexamined borrowing.
    """
    import math
    others = [s for s in subgroups if s.name != target_name]
    tgt = [s for s in subgroups if s.name == target_name][0]
    ws, es = [], []
    for s in others:
        rr, lo, hi = s.rr()
        se = (math.log(hi) - math.log(lo)) / 3.92
        ws.append(1 / se**2); es.append(math.log(rr))
    mu = sum(w * e for w, e in zip(ws, es)) / sum(ws)
    se = math.sqrt(1 / sum(ws))
    pred = (math.exp(mu), math.exp(mu - 1.96 * se), math.exp(mu + 1.96 * se))
    act = tgt.rr()
    reversal = (pred[0] < 1) != (act[0] < 1)
    overlap = not (pred[2] < act[1] or act[2] < pred[1])
    return dict(target=target_name, pooled_pred=tuple(round(v, 3) for v in pred),
                actual=tuple(round(v, 3) for v in act),
                direction_reversal=reversal, ci_overlap=overlap)
