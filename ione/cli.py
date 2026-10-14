"""IONE CLI: aggregate-evidence decision audit.

    ione audit --study recovery        # built-in verified example
    ione audit --csv subgroups.csv     # name,treat_events,treat_n,ctrl_events,ctrl_n
    ione borrow-check --study recovery --target noO2
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys

from .aggregate import ArmCount, SubgroupTable, EffectSummary
from .identifiability import (audit_decision, borrow_check, LPResult,
                              DecisionVerdict)
from .augmentation import suggest_augmentation
from .proximity import ProximityProfile
from .data import load_builtin


def _load_subgroups(path):
    subs = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            subs.append(SubgroupTable(
                row["name"],
                ArmCount(int(row["treat_events"]), int(row["treat_n"])),
                ArmCount(int(row["ctrl_events"]), int(row["ctrl_n"]))))
    return subs


def main(argv=None):
    p = argparse.ArgumentParser(prog="ione", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit", help="decision-robustness audit")
    a.add_argument("--study", help="built-in study name (recovery)")
    a.add_argument("--csv", help="CSV with subgroup counts")
    a.add_argument("--target", help="target subgroup name (default: last)")
    a.add_argument("--unmeasured-modifier", action="store_true",
                   help="declare a suspected unmeasured modifier")
    a.add_argument("--threshold", type=float, default=0.0,
                   help="nonzero clinical benefit threshold on RD")
    b = sub.add_parser("borrow-check", help="leave-one-subgroup-out check")
    b.add_argument("--study", required=True)
    b.add_argument("--target", required=True)
    args = p.parse_args(argv)

    if args.cmd == "audit":
        if args.study:
            eff = load_builtin(args.study)
        elif args.csv:
            subs = _load_subgroups(args.csv)
            eff = EffectSummary("custom", subs[0], subs[1:])
        else:
            p.error("need --study or --csv")
        report = eff.sufficiency_report()
        # "sufficiency" is a legacy JSON key (original IONE vocabulary);
        # kept for API compatibility. Verdict values are canonical.
        print(json.dumps({"sufficiency": report}, indent=2))
        # decision audit on the target subgroup using overall margins
        p0 = eff.overall.control.risk
        p1 = eff.overall.treat.risk
        names = [s.name for s in eff.subgroups]
        tname = args.target or (names[-1] if names else eff.overall.name)
        tgt = next((s for s in eff.subgroups if s.name == tname), None)
        # consistency of subgroup aggregates with the overall table
        issues = eff.check_consistency()
        errors = [i for i in issues if i.severity == "error"]
        if errors:
            print(json.dumps({"consistency": [
                dict(kind=i.kind, severity=i.severity, detail=i.detail)
                for i in issues]}, indent=2))
        if tgt is None:
            res = audit_decision((p0, p1), target_x=1)  # UNSUPPORTED: no target
        else:
            # Arm-specific stratum prevalence: q1 = P(X=1|treat),
            # q0 = P(X=1|control).  Under balanced randomisation these are
            # equal; we estimate both and use arm_weights whenever they
            # diverge beyond Monte-Carlo noise, else the pooled common q.
            q1 = tgt.treat.n / eff.overall.treat.n
            q0 = tgt.control.n / eff.overall.control.n
            q_pooled = (tgt.treat.n + tgt.control.n) / (
                eff.overall.treat.n + eff.overall.control.n)
            # tolerance: ~2 SE of the difference in proportions
            se = 2 * math.sqrt(q_pooled * (1 - q_pooled) * (
                1 / eff.overall.treat.n + 1 / eff.overall.control.n))
            if abs(q1 - q0) > max(se, 0.01):
                res = audit_decision((p0, p1), target_x=1,
                                     arm_weights=(q0, q1),
                                     threshold=args.threshold)
                res.detail += f"; arm-specific weights used (q0={q0:.3f},q1={q1:.3f})"
            else:
                res = audit_decision((p0, p1), target_x=1,
                                     prev1=q_pooled,
                                     threshold=args.threshold)
        if errors:
            res = LPResult(DecisionVerdict.INFEASIBLE, res.bound_lo,
                           res.bound_hi, res.solver_status, res.residual,
                           res.tol,
                           "subgroup counts inconsistent with overall: "
                           + "; ".join(i.detail for i in errors))
        print(json.dumps({
            "decision_audit": dict(
                verdict=res.verdict.value,
                bound_lo=res.bound_lo, bound_hi=res.bound_hi,
                solver_status=res.solver_status, residual=res.residual,
                detail=res.detail)}, indent=2))
        augs = suggest_augmentation(res,
                                    unmeasured_modifier=args.unmeasured_modifier)
        print(json.dumps({"augmentation": [
            dict(kind=o.kind, label=o.label, classification=o.classification,
                 cost_class=o.cost_class, assumption=o.assumption,
                 note=o.note) for o in augs]}, indent=2))
        prof = ProximityProfile(
            status=res.verdict.value,
            channels=[s.name for s in eff.subgroups],
            top_z=augs[0].label)
        print(json.dumps({"proximity_profile": prof.to_dict()}, indent=2))
    elif args.cmd == "borrow-check":
        eff = load_builtin(args.study)
        print(json.dumps(borrow_check(eff.subgroups, args.target), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
