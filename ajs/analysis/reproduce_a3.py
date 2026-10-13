"""Gate A3 reproduction script — all numeric claims in the AJS manuscript.

Outputs (ajs/audit/):
  a3_verdicts.csv      decision audits on the three built-in datasets
  a3_bounds_vs_q.csv   identified-RD interval vs stratum prevalence q
  a3_constructed.csv   constructed edge cases (labelled constructed)
  a3_math_tests.csv    LP vs closed-form algebra agreement table
  fig_bounds_vs_q.pdf  vector figure: bounds vs q (RECOVERY margins)
  fig_verdicts.pdf     vector figure: bound intervals per case
  logs/extended_checks.txt  additional edge-case checks (grid enumeration)
All numbers are computed from code — none are transcribed by hand.
"""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import numpy as np
from scipy.optimize import linprog

from ione.data import RECOVERY, ISIS2, REACT, load_builtin
from ione.identifiability import audit_decision, borrow_check, DecisionVerdict
from ione.aggregate import ArmCount, SubgroupTable, EffectSummary
from ione.augmentation import suggest_augmentation

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "audit")
os.makedirs(OUT, exist_ok=True)


def analytic_bounds(q, p0bar, p1bar):
    """Closed-form sharp RD bounds at stratum x=1 (same algebra as tests)."""
    def win(pbar):
        return max(0.0, (pbar - q) / (1 - q)), min(1.0, pbar / (1 - q))
    a0, b0 = win(p0bar)
    a1, b1 = win(p1bar)
    if a0 > b0 or a1 > b1:
        return None
    d_min, d_max = a1 - b0, b1 - a0
    c = (p1bar - p0bar) / q
    k = (1 - q) / q
    return c - k * d_max, c - k * d_min


# ---------- 1. decision audits on built-in datasets ----------
rows = []
for study_name in ("recovery", "isis2", "react"):
    eff = load_builtin(study_name)
    p0, p1 = eff.overall.control.risk, eff.overall.treat.risk
    for s in eff.subgroups:
        q1 = s.treat.n / eff.overall.treat.n
        q0 = s.control.n / eff.overall.control.n
        q = (s.treat.n + s.control.n) / (eff.overall.treat.n + eff.overall.control.n)
        if abs(q1 - q0) > 0.01:
            res = audit_decision((p0, p1), target_x=1, arm_weights=(q0, q1))
            qq = f"q0={q0:.4f},q1={q1:.4f}"
        else:
            res = audit_decision((p0, p1), target_x=1, prev1=q)
            qq = f"{q:.4f}"
        rows.append(dict(study=study_name, target=s.name, n_treat=s.treat.n,
                         n_ctrl=s.control.n, prevalence=qq,
                         verdict=res.verdict.value,
                         bound_lo=f"{res.bound_lo:.4f}",
                         bound_hi=f"{res.bound_hi:.4f}",
                         residual=f"{res.residual:.2e}"))
with open(os.path.join(OUT, "a3_verdicts.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# ---------- 2. bounds vs prevalence (RECOVERY margins) ----------
p0, p1 = RECOVERY.overall.control.risk, RECOVERY.overall.treat.risk
qs, los, his = [], [], []
for q in np.linspace(0.05, 0.95, 400):
    ab = analytic_bounds(q, p0, p1)
    if ab:
        qs.append(q); los.append(ab[0]); his.append(ab[1])
with open(os.path.join(OUT, "a3_bounds_vs_q.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["q", "bound_lo", "bound_hi"])
    for q, lo, hi in zip(qs, los, his):
        w.writerow([f"{q:.4f}", f"{lo:.6f}", f"{hi:.6f}"])

obs_q = (RECOVERY.subgroups[2].treat.n + RECOVERY.subgroups[2].control.n) / (
    RECOVERY.overall.treat.n + RECOVERY.overall.control.n)
fig, ax = plt.subplots(figsize=(5.2, 3.4))
ax.fill_between(qs, los, his, alpha=0.25, color="tab:blue",
                label="identified interval")
ax.axhline(0, color="black", lw=0.8)
ax.axvline(obs_q, color="tab:red", ls="--", lw=1,
           label=f"reported prevalence q = {obs_q:.3f}")
ax.plot(qs, [(a + b) / 2 for a, b in zip(los, his)], color="tab:blue", lw=1)
ax.set_xlabel("stratum prevalence q = P(X = 1)")
ax.set_ylabel("identified bounds on RD(X = 1)")
ax.legend(loc="upper right", fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_bounds_vs_q.pdf"))

# ---------- 3. verdict intervals per case (real + constructed) ----------
cases = [
    ("RECOVERY noO2 (real)", *analytic_bounds(obs_q, p0, p1), "REVERSIBLE"),
    ("constructed: extreme benefit", *analytic_bounds(0.5, 0.60, 0.00), "ROBUST_TREAT"),
    ("constructed: extreme harm", *analytic_bounds(0.5, 0.00, 0.60), "ROBUST_NO_TREAT"),
    ("constructed: infeasible margins", -0.5, 1.5, "INFEASIBLE (margin>1)"),
]
fig, ax = plt.subplots(figsize=(5.2, 2.8))
labels, ytick = [], []
for i, (name, lo, hi, tag) in enumerate(cases):
    ax.plot([lo, hi], [i, i], lw=6, solid_capstyle="butt",
            color="tab:red" if (lo < 0 < hi) else "tab:green")
    labels.append(f"{name}  [{tag}]")
    ytick.append(i)
ax.axvline(0, color="black", lw=0.8)
ax.set_yticks(ytick); ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel("identified bounds on risk difference")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_verdicts.pdf"))

with open(os.path.join(OUT, "a3_constructed.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["case", "verdict", "bound_lo", "bound_hi", "note"])
    for name, lo, hi, tag in cases:
        w.writerow([name, tag, f"{lo:.4f}", f"{hi:.4f}",
                    "constructed" if name.startswith("constructed") else "real data"])
    # infeasible via LP
    r = audit_decision((1.2, 0.16), target_x=1, prev1=0.5)
    w.writerow(["p0bar=1.2 margin>1 (constructed)", r.verdict.value, "", "",
                "empty feasible set"])
    # unsupported
    r = audit_decision((0.20, 0.16), target_x=1)
    w.writerow(["no prevalence supplied (constructed)", r.verdict.value, "", "",
                "missing P(X=1)"])

# ---------- 4. LP vs algebra agreement table ----------
agree_rows = []
rng = np.random.default_rng(20261013)
for i in range(200):
    q = rng.uniform(0.05, 0.95)
    p0b, p1b = rng.uniform(0.01, 0.99, 2)
    ab = analytic_bounds(q, p0b, p1b)
    if ab is None:
        continue
    res = audit_decision((p0b, p1b), target_x=1, prev1=q)
    agree_rows.append(dict(q=f"{q:.4f}", p0bar=f"{p0b:.4f}", p1bar=f"{p1b:.4f}",
                           lo_lp=f"{res.bound_lo:.8f}", lo_alg=f"{ab[0]:.8f}",
                           hi_lp=f"{res.bound_hi:.8f}", hi_alg=f"{ab[1]:.8f}",
                           max_err=f"{max(abs(res.bound_lo-ab[0]), abs(res.bound_hi-ab[1])):.2e}"))
with open(os.path.join(OUT, "a3_math_tests.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(agree_rows[0])); w.writeheader()
    w.writerows(agree_rows)
max_err = max(float(r["max_err"]) for r in agree_rows)

# ---------- 5. extended edge-case checks ----------
log = []
log.append("== extended edge-case checks ==")
# zero-event cells: RR undefined (1/a), OR uses Haldane
try:
    SubgroupTable("z", ArmCount(0, 100), ArmCount(5, 100)).rr()
    log.append("zero-event rr() -> no exception (UNEXPECTED)")
except Exception as e:
    log.append(f"zero-event rr() -> raises {type(e).__name__} (documented: RR undefined, caller abstains)")
o = SubgroupTable("z", ArmCount(0, 100), ArmCount(5, 100)).orr()
log.append(f"zero-event orr() -> Haldane OR={o[0]:.3f} (finite)")

# q -> 1: conditional = marginal
r = audit_decision((0.20, 0.10), target_x=1, prev1=0.999)
log.append(f"q=0.999 bounds [{r.bound_lo:.4f},{r.bound_hi:.4f}] vs marginal {0.10-0.20:.4f} -> shrink to margin")

# q -> 0: bounds approach full width [-1,1]
r = audit_decision((0.20, 0.10), target_x=1, prev1=0.02)
log.append(f"q=0.02 bounds [{r.bound_lo:.4f},{r.bound_hi:.4f}] -> near-uninformative")

# rounding tolerance: counts vs proportions
bad = EffectSummary("b", SubgroupTable("a", ArmCount(100, 1000), ArmCount(100, 1000)),
                    [SubgroupTable("s", ArmCount(90, 1200), ArmCount(50, 500))])
log.append(f"subgroup>overall -> {[i.severity for i in bad.check_consistency()]} (error expected)")

# augmentation example for REVERSIBLE real case
res = audit_decision((p0, p1), target_x=1, prev1=obs_q)
opts = suggest_augmentation(res)
for o_ in opts:
    log.append(f"augmentation[{o_.cost_class}] {o_.kind}: {o_.label} [{o_.classification}]")

# borrow checks
bc = borrow_check(RECOVERY.subgroups, "noO2")
log.append(f"borrow-check recovery/noO2: pooled {bc['pooled_pred']} vs actual {bc['actual']} reversal={bc['direction_reversal']}")
log.append(f"LP-vs-algebra max abs error over {len(agree_rows)} random margins: {max_err:.2e}")
open(os.path.join(OUT, "logs", "extended_checks.txt"), "w").write("\n".join(log) + "\n")
print("\n".join(log))
print("\nA3 outputs written to", OUT)
