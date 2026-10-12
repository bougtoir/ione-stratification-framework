# Changelog

## 0.2.0 (2026-10-11) — aggregate-evidence audit (F0–F8 revision)

Breaking changes:
- `audit_decision` now requires `prev1` (stratum prevalence) or
  `arm_weights`; no default prevalence is assumed.
- Verdicts renamed: `SUFFICIENT` → `ROBUST_TREAT`/`ROBUST_NO_TREAT`;
  `UNIDENTIFIABLE` → `INFEASIBLE`/`UNSUPPORTED` as separate states
  (empty feasible set is not nonidentification).
- Augmentation options no longer claim unconditional resolution;
  each carries a `classification` + `assumption` field.

Added:
- Exact LP identification engine (scipy linprog/HiGHS), solver status,
  feasibility residual and sharp RD bounds reported.
- Nonzero clinical decision thresholds; arm-specific stratum weights;
  outcome-margin constraints requiring explicit arm mixing proportions.
- ISIS-2 (Lancet 1988) and WHO REACT (JAMA 2020) verified aggregate
  datasets alongside RECOVERY (NEJM 2021).
- pyproject.toml (pip-installable, `ione` CLI), CITATION.cff, CI
  workflow, F0–F8 gate reports in `docs/aggregate_audit/`.
