"""IONE CLI: aggregate-evidence decision audit.

    ione audit --study recovery        # built-in verified example
    ione audit --csv subgroups.csv     # name,treat_events,treat_n,ctrl_events,ctrl_n
    ione borrow-check --study recovery --target noO2
"""
from __future__ import annotations

import argparse
import csv
import json
import sys

from .aggregate import ArmCount, SubgroupTable, EffectSummary
from .identifiability import audit_decision, borrow_check
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
        print(json.dumps({"sufficiency": report}, indent=2))
        # decision audit on the target subgroup using overall margins
        p0 = eff.overall.control.risk
        p1 = eff.overall.treat.risk
        names = [s.name for s in eff.subgroups]
        tname = args.target or (names[-1] if names else eff.overall.name)
        res = audit_decision((p0, p1), target_x=1)
        print(json.dumps({
            "decision_audit": dict(
                verdict=res.verdict.value, n_compatible=res.n_compatible,
                actions=res.actions, detail=res.detail)}, indent=2))
        augs = suggest_augmentation(res,
                                    unmeasured_modifier=args.unmeasured_modifier)
        print(json.dumps({"augmentation": [
            dict(kind=o.kind, label=o.label, cost_class=o.cost_class,
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
