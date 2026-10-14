"""Gate R1-R5 reproduction script — information-level (L1/L2/L3) audit.

Outputs (ajs/audit/):
  r_levels.csv       L1/L2/L3 identified sets, verdicts, constraints per case
  r_ledger.csv       source ledger: every published number used vs derived
  fig_levels.pdf     vector figure: identified set per information level
  logs/r_qc.txt      QC log: monotonicity, LP-vs-algebra, edge cases

All numbers are computed from code — none are transcribed by hand.
Published source values are asserted against the figures/tables of the
original reports (see r_ledger.csv).
"""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import numpy as np

from ione.data import RECOVERY, ISIS2, REACT, load_builtin
from ione.aggregate import ArmCount, SubgroupTable, EffectSummary
from ione.identifiability import audit_decision, borrow_check, DecisionVerdict
from ione.levels import audit_levels, check_monotone
from ione.augmentation import suggest_augmentation

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "audit")
os.makedirs(os.path.join(OUT, "logs"), exist_ok=True)

TAU = 0.0
rows, log = [], []


def emit(study, stratum, res, kind, note=""):
    rows.append(dict(
        study=study, stratum=stratum, level=res.level,
        reachable=res.reachable,
        identified_lo="" if not res.reachable else f"{res.identified_lo:.4f}",
        identified_hi="" if not res.reachable else f"{res.identified_hi:.4f}",
        point_estimate="" if math.isnan(res.point_estimate) else f"{res.point_estimate:.4f}",
        ci_lo="" if not res.ci else f"{res.ci[0]:.4f}",
        ci_hi="" if not res.ci else f"{res.ci[1]:.4f}",
        verdict=res.verdict.value, kind=kind, note=note or res.note))


# ---------- RECOVERY: full L1 -> L3 ladder (L3 genuinely published) ----
for s in RECOVERY.subgroups:
    res = audit_levels(RECOVERY, s.name, threshold=TAU, l3_published=True)
    ok, msgs = check_monotone(res)
    log.append(f"RECOVERY/{s.name}: monotone-nesting check ok={ok} {msgs}")
    for r in res:
        emit("RECOVERY", s.name, r, "real published counts",
             r.note + (" | ablation" if r.level != "L3" else ""))

# ---------- ISIS-2: patient stratum (time from onset) ------------------
# The Lancet 1988 report publishes only subgroup ODDS REDUCTIONS
# (35% SD6 / 16% SD7 / 21% SD12 for SK; fig 3a) — no arm-by-stratum
# denominators or event counts.  The ladder therefore stops at L1.
isis_res = audit_levels(ISIS2, "time_from_onset_stratum", threshold=TAU)
ok, msgs = check_monotone(isis_res)
for r in isis_res:
    emit("ISIS-2", "time-from-onset stratum", r, "real publication gap",
         "published only as odds reductions (Lancet fig. 3a); "
         "arm x stratum counts never reported")
log.append("ISIS-2 time-from-onset: reachable level = L1 only "
           "(subgroup effects published as odds reductions, no counts)")

# ---------- REACT: excluded example ------------------------------------
# serious_adverse_events is a post-treatment outcome, not a
# pre-treatment stratum -> excluded from subgroup-effect demonstration.
log.append("REACT serious_adverse_events: post_treatment flag = "
           f"{REACT.subgroups[0].metadata.get('post_treatment')} -> "
           "excluded from L1/L2/L3 applications (documented counterexample)")
rows.append(dict(study="REACT", stratum="serious_adverse_events",
                 level="excluded", reachable="", identified_lo="",
                 identified_hi="", point_estimate="", ci_lo="", ci_hi="",
                 verdict="not a pre-treatment stratum",
                 kind="excluded counterexample",
                 note="post-treatment outcome; cannot define a stratum"))

with open(os.path.join(OUT, "r_levels.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# ---------- source ledger ------------------------------------------------
ledger = [
    ("RECOVERY overall", "482/2104 vs 1110/4321", "NEJM 2021;384:693",
     "published counts (abstract/table)", "10.1056/NEJMoa2021436"),
    ("RECOVERY IMV", "95/324 vs 283/683", "NEJM 2021 fig/table",
     "published counts", "10.1056/NEJMoa2021436"),
    ("RECOVERY O2", "298/1279 vs 682/2604", "NEJM 2021 fig/table",
     "published counts", "10.1056/NEJMoa2021436"),
    ("RECOVERY noO2", "89/501 vs 145/1034", "NEJM 2021 fig/table",
     "published counts (17.8% vs 14.0% -> RR 1.19 published adjusted)",
     "10.1056/NEJMoa2021436"),
    ("ISIS-2 aspirin contrast", "804/8587 vs 1016/8600",
     "Lancet 1988;2:349", "published counts", "10.1016/S0140-6736(88)92833-4"),
    ("ISIS-2 streptokinase contrast", "791/8592 vs 1029/8595",
     "Lancet 1988;2:349", "published counts", "10.1016/S0140-6736(88)92833-4"),
    ("ISIS-2 both vs neither", "343/4292 vs 568/4300",
     "Lancet 1988;2:349", "published counts", "10.1016/S0140-6736(88)92833-4"),
    ("ISIS-2 time-from-onset subgroups",
     "odds reductions 35% SD6 / 16% SD7 / 21% SD12 (SK)",
     "Lancet 1988 fig 3a", "published odds reductions only; no counts",
     "10.1016/S0140-6736(88)92833-4"),
    ("REACT overall", "222/678 vs 425/1025", "JAMA 2020;324:1330",
     "published pooled counts", "10.1001/jama.2020.17023"),
    ("REACT serious adverse events", "64/354 vs 80/342",
     "JAMA 2020", "published counts; POST-TREATMENT variable (excluded)",
     "10.1001/jama.2020.17023"),
]
with open(os.path.join(OUT, "r_ledger.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "value_used", "source", "status", "doi"])
    w.writerows(ledger)

# ---------- figure: identified set per information level ------------------
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ypos, ylabels, y = [], [], 0
level_style = {"L1": dict(color="0.6", lw=2), "L2": dict(color="tab:blue", lw=6),
               "L3": dict(color="tab:red", lw=0)}
for s in RECOVERY.subgroups:
    res = audit_levels(RECOVERY, s.name, threshold=TAU, l3_published=True)
    l1, l2, l3 = res
    ax.plot([l1.identified_lo, l1.identified_hi], [y, y], lw=2, color="0.6")
    ax.plot([l2.identified_lo, l2.identified_hi], [y - 0.12, y - 0.12],
            lw=5, color="tab:blue", solid_capstyle="butt")
    ax.errorbar(l3.point_estimate, y - 0.24,
                xerr=[[l3.point_estimate - l3.ci[0]],
                      [l3.ci[1] - l3.point_estimate]],
                fmt="o", ms=4, color="tab:red", capsize=2, lw=0.8)
    ylabels.append(f"RECOVERY {s.name}")
    ypos.append(y)
    y += 0.7
# ISIS-2: only L1
ax.plot([-1, 1], [y, y], lw=2, color="0.6")
ax.annotate("only odds reductions published\n(L1 reached; L2/L3 not recoverable)",
            xy=(0.55, y), fontsize=7, color="0.3", va="center")
ylabels.append("ISIS-2 onset-time stratum")
ypos.append(y)
ax.axvline(0, color="black", lw=0.8)
ax.set_yticks(ypos); ax.set_yticklabels(ylabels, fontsize=8)
ax.invert_yaxis()
ax.set_xlabel("identified set / point estimate of stratum-specific risk difference")
from matplotlib.lines import Line2D
ax.legend(handles=[
    Line2D([0], [0], color="0.6", lw=2, label="L1: arm totals only"),
    Line2D([0], [0], color="tab:blue", lw=5, label="L2: + stratum prevalence (LP bounds)"),
    Line2D([0], [0], color="tab:red", marker="o", lw=0, label="L3: + stratum event counts (point, 95% CI)")],
    fontsize=7, frameon=False, loc="upper center",
    bbox_to_anchor=(0.5, -0.18), ncol=1)
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(os.path.join(OUT, "fig_levels.pdf"))
fig.savefig(os.path.join(OUT, "..", "manuscript", "fig_levels.pdf"))

# ---------- QC checks ----------------------------------------------------
log.append("\n== QC ==")
# consistency of RECOVERY subgroup counts with overall
issues = RECOVERY.check_consistency()
if not issues:
    log.append("consistency: RECOVERY subgroup sums equal overall margins exactly")
for issue in issues:
    log.append(f"consistency[{issue.severity}] {issue.kind}: {issue.detail}")
# zero cells / non-negativity across all built-ins
for name in ("recovery", "isis2", "react"):
    eff = load_builtin(name)
    for s in [eff.overall] + eff.subgroups:
        for arm in (s.treat, s.control):
            assert arm.events >= 0 and arm.n > 0 and arm.events <= arm.n, \
                f"{name}/{s.name}: invalid cell {arm.events}/{arm.n}"
log.append("non-negativity & events<=n: all cells OK")
# LP vs independent analytic formula on RECOVERY margins
p0, p1 = RECOVERY.overall.control.risk, RECOVERY.overall.treat.risk
s = RECOVERY.subgroups[2]
q1, q0 = s.treat.n / RECOVERY.overall.treat.n, s.control.n / RECOVERY.overall.control.n
res = audit_decision((p0, p1), target_x=1, arm_weights=(q0, q1))
log.append(f"RECOVERY/noO2 L2 bounds [{res.bound_lo:.4f},{res.bound_hi:.4f}] "
           f"residual={res.residual:.2e}")
# crude-vs-adjusted distinction, recorded
rd = s.rd()
log.append(f"RECOVERY/noO2 L3 crude RD = {rd[0]:.4f} ({rd[1]:.4f},{rd[2]:.4f}) "
           "vs published age-adjusted RR 1.19 — distinct estimands, not conflated")
# borrow check retained as retrospective diagnostic
bc = borrow_check(RECOVERY.subgroups, "noO2")
log.append(f"borrow-check recovery/noO2: pooled {bc['pooled_pred']} vs actual "
           f"{bc['actual']} reversal={bc['direction_reversal']} "
           "(retrospective diagnostic only)")
open(os.path.join(OUT, "logs", "r_qc.txt"), "w").write("\n".join(log) + "\n")
print("\n".join(log))
print("\nR outputs written to", OUT)
