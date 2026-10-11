# IONE Aggregate-Evidence Audit (`ione` package)

New module extending the IONE framework to **decision audits on published
aggregate evidence** — no IPD, no pseudo-IPD.

## Features

- **Sufficiency audit**: crude RR/RD/OR with 95% CIs from published
  arm-level subgroup counts; non-estimable cells flagged, never
  re-normalized.
- **Identifiability determination**: enumerates the compatible model set
  M(T) for binary-covariate problems and returns
  `SUFFICIENT / REVERSIBLE / UNIDENTIFIABLE` — data nonidentification,
  not a model-based interval.
- **Borrow check**: leave-one-subgroup-out pooling that detects the
  documented direction-reversal failure of unexamined borrowing.
- **Augmentation suggestion**: cost-ordered options —
  re-tabulation → new measurement → new enrollment → abstain.
- **Decision-evidence proximity profile**: (status, channels,
  margin⁻, top-z); deliberately not a scalar.

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
python -m ione.cli audit --study recovery
python -m ione.cli borrow-check --study recovery --target noO2
python -m ione.cli audit --csv my_subgroups.csv \
    --unmeasured-modifier
```

CSV columns: `name,treat_events,treat_n,ctrl_events,ctrl_n`.

## Tests

```bash
python -m pytest tests/test_aggregate_audit.py -v
```

## Limitations

- Binary outcomes and binary covariates only in this release.
- Crude (unadjusted) estimands — adjusted published estimates cannot be
  reproduced from aggregate counts (documented limit).
- Audit scope is restricted to studies that publish subgroup event
  counts; that availability itself is the binding real-world constraint.
