# Gate A3 — Computation & real-data validation report

Date: 2026-10-13 (UTC). Script: `ajs/analysis/reproduce_a3.py` (all
numbers computed, none transcribed). Environment: Python 3.10.12,
scipy 1.15.3 (HiGHS), numpy 2.2.6. Commit base 21a253e.

## 1. Test suite & numeric agreement

- `pytest tests/ -q` → **27/27 pass** (`logs/pytest_a0.txt`).
- Independent LP-vs-algebra check, 200 random (q, p0bar, p1bar):
  max abs error on bounds = **1.78e-15** (`a3_math_tests.csv`).
- Edge cases (`logs/extended_checks.txt`): zero-event arm → `rr()` raises
  (undefined, caller must abstain), `orr()` finite via Haldane; q→1
  collapses bounds to the marginal (−0.10); q→0 widens to [−1,1];
  subgroup counts exceeding overall → consistency `error` (INFEASIBLE
  path); INFEASIBLE vs UNSUPPORTED verified disjoint.

## 2. Real-data decision audits (`a3_verdicts.csv`)

| study/target | prevalence | verdict | bounds |
|---|---|---|---|
| RECOVERY IMV | q=0.157 | REVERSIBLE | [−1.000, +1.000] |
| RECOVERY O2 | q=0.604 | REVERSIBLE | [−0.425, +0.379] |
| RECOVERY noO2 | q=0.239 | REVERSIBLE | [−1.000, +0.959] |
| ISIS-2 streptokinase | q=1.000 | **ROBUST_TREAT** | [−0.025, −0.025] (point) |
| ISIS-2 combo | q=0.500 | REVERSIBLE | [−0.236, +0.187] |
| REACT SAE | q0=0.334,q1=0.522 | REVERSIBLE | [−1.000, +0.627] |

Real-data coverage of the verdict taxonomy: ROBUST occurs for ISIS-2
(streptokinase stratum ≈ the whole arm population, so the conditional RD
equals the marginal — a degenerate-prevalence case, labelled as such).
REVERSIBLE dominates the meaningful subgroup targets. INFEASIBLE and
UNSUPPORTED do **not** occur on these published datasets and are shown
as **constructed examples** (margins > 1; prevalence not supplied).

## 3. Real-data effect reproduction

RECOVERY subgroup counts re-verified 2026-10-13 against the primary
report (NEJMoa2021436 / PMC7383595): IMV 29.3% vs 41.4%, O2 23.3% vs
26.2%, noO2 17.8% vs 14.0%; overall 22.9% vs 25.7% — all match
`ione/data.py` exactly. Published *age-adjusted* rate ratios
(0.64/0.82/1.19) differ from our crude RRs (0.71/0.89/1.27) — both
reported distinctly; manuscript uses crude values only.

- Borrow check (retrospective): pooled IMV+O2 prediction RR 0.835
  (0.755–0.923) vs actual noO2 1.267 (0.995–1.613) → direction reversal,
  CIs do not overlap (`cli_borrowcheck_recovery_noO2.json`).
- ISIS-2 crude figures match published proportions (9.2%/12.0% SK
  subgroup; 8.0%/13.2% combo). REACT crude OR 0.66±0.03 reproduces the
  published fixed-effect OR — flagged as model-based vs crude.

## 4. Augmentation demonstration

On REVOVERY noO2 (REVERSIBLE), `suggest_augmentation` returns, in
burden order: arm×stratum cross-tabulation (re-tabulation, cost 0,
`sufficient_assumed` — structurally resolves to a point *if produced*);
per-stratum baseline risk (cost 0); stratum-restricted RCT (cost 3).
No option claims unconditional resolution — consistent with F2 honesty.

## 5. Figures (vector PDF)

- `fig_bounds_vs_q.pdf` — identified RD interval vs prevalence q at
  RECOVERY margins; dashed line at reported noO2 prevalence (0.239).
- `fig_verdicts.pdf` — bound intervals: real REVERSIBLE case, constructed
  ROBUST_TREAT/ROBUST_NO_TREAT/INFEASIBLE (all labelled).

## 6. Performance

LP solves in <1 ms per audit; 400-point q-sweep + 200 LP solves complete
in seconds — runtime claims limited to "interactive speed", no benchmark
inflation.
