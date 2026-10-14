# IONE (Identifiability-Oriented Navigation of Evidence) — aggregate-evidence audit (`ione` package)

The current IONE product: **decision audits on published aggregate
evidence** — no IPD, no pseudo-IPD.

## Features

- **Sufficiency audit**: crude RR/RD/OR with 95% CIs from published
  arm-level subgroup counts; non-estimable cells flagged, never
  re-normalized.
- **Exact identifiability engine**: the compatible model set is a
  polytope; sharp bounds on the conditional risk difference come from
  linear programming (HiGHS), with solver status and residuals reported —
  not finite-grid enumeration. Verdicts: `ROBUST_TREAT`,
  `ROBUST_NO_TREAT`, `REVERSIBLE`, `INFEASIBLE`, `UNSUPPORTED`
  (separate states; empty feasible set ≠ nonidentification). Stratum
  prevalence and arm mixing proportions are required inputs; nonzero
  decision thresholds and unequal arm compositions supported.
- **Borrow check**: RETROSPECTIVE leave-one-subgroup-out demonstration —
  not prospective validation, not a Bayesian method; crude vs adjusted
  RR caveats enforced.
- **Augmentation suggestion**: cost-ordered options —
  re-tabulation → new measurement → new enrollment → abstain — each
  classified `sufficient_assumed / potentially_informative / irrelevant /
  infeasible / unknown` with its assumptions; nothing claims
  unconditional resolution.
- **Decision-evidence proximity profile**: (status, channels,
  margin⁻, top-z); descriptive only, not a scalar or borrowing weight.
- **Verified datasets**: RECOVERY (NEJM 2021), ISIS-2 (Lancet 1988),
  WHO REACT (JAMA 2020).

## Differentiation

- Not another borrowing method (robust MAP / power prior exist): the
  audit decides *whether* to borrow rather than *how much*.
- Not a sensitivity-analysis package: it returns concrete, cost-ordered
  *reportable* augmentations, including re-tabulation requests at
  ~zero cost that standard trial-design tools never propose.
- Built-in verified example: RECOVERY dexamethasone subgroup counts
  (NEJM 2021; PMC7383595), cross-verified against three independent
  sources; the pooled-other-subgroup estimate (RR 0.835, benefit) is
  shown to reverse direction vs the actual no-O2 estimate (1.267, harm).

## Python API

```python
from ione import load_builtin, audit_decision, suggest_augmentation
from ione.identifiability import borrow_check

eff = load_builtin("recovery")
print(eff.sufficiency_report())
print(borrow_check(eff.subgroups, "noO2"))

res = audit_decision((0.20, 0.16), target_x=1, prev1=0.5)
for o in suggest_augmentation(res):
    print(o.kind, o.label)
```

## CLI

```bash
pip install -e .[test]
ione audit --study recovery --target noO2
ione borrow-check --study recovery --target noO2
ione audit --csv my_subgroups.csv --unmeasured-modifier --threshold 0.05
```

CSV columns: `name,treat_events,treat_n,ctrl_events,ctrl_n`.

## Tests

```bash
python -m pytest tests/test_aggregate_audit.py -v
```

## Limitations

- Binary outcomes and binary covariates only in this release;
  nonlinear/nonconvex or unmodeled-covariate settings are abstained on,
  never silently bounded.
- Crude (unadjusted) estimands — adjusted published estimates cannot be
  reproduced from aggregate counts (documented limit).
- Audit scope is restricted to studies that publish subgroup event
  counts; that availability itself is the binding real-world constraint.

## Input CSV specification

Columns (header required):
`name,treat_events,treat_n,ctrl_events,ctrl_n`

- One row per published subgroup stratum; counts are *published* integers
  from the trial report, not reconstructed IPD.
- `ione audit` checks subgroup-vs-overall consistency and reports
  `error` (contradiction → INFEASIBLE) vs `warning` (rounding /
  reporting gap, handled explicitly).
- Target-stratum share is estimated per arm; when arm shares diverge
  beyond ~2 SE the audit uses arm-specific weights instead of silently
  assuming common composition.

## Output status interpretation

| verdict | meaning | not meaning |
|---|---|---|
| ROBUST_TREAT | every model compatible with the margins gives RD < -τ | a clinical recommendation |
| ROBUST_NO_TREAT | every compatible model gives RD > -τ | proof of harm |
| REVERSIBLE | bounds straddle -τ | "effect uncertain" in the estimation sense — this is nonidentification |
| INFEASIBLE | no model satisfies the margins | insufficient information |
| UNSUPPORTED | input lacks required specification (prevalence, mixing) | infeasibility |

## Failure modes (by design)

- Missing stratum prevalence → UNSUPPORTED.
- Outcome margin without arm mixing proportion → UNSUPPORTED.
- Subgroup counts contradicting the overall table → INFEASIBLE.
- Solver failure → UNSUPPORTED, never ROBUST.
