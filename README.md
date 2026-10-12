# IONE: Identifiability-Oriented Navigation of Evidence

Open-source Python package for auditing what published aggregate trial
evidence can — and cannot — support for a clinical decision.

## Current product: aggregate-evidence decision audit (`ione` package)

Given published arm-level event counts, subgroup tables and margins
from RCTs / meta-analyses, `ione`:

- computes crude RR/RD/OR with 95% CIs and flags non-estimable cells;
- computes **sharp bounds** on the conditional risk difference via
  linear programming (HiGHS) over the compatible-model polytope, and
  returns `ROBUST_TREAT`, `ROBUST_NO_TREAT`, `REVERSIBLE`, `INFEASIBLE`,
  or `UNSUPPORTED` — separate states, so inconsistent inputs,
  insufficient information, and nonidentification are never conflated;
- suggests the cheapest *reportable* augmentation (re-tabulation → new
  measurement → new enrollment → abstain), each classified with its
  assumptions — never a guarantee of resolution;
- runs a retrospective leave-one-subgroup-out borrow check.

Scope is explicit: binary stratum, binary outcome, two arms; bounds are
conditional on stated assumptions (stratum prevalence, mixing
proportions, decision threshold); verdicts are not clinical treatment
recommendations. No IPD or pseudo-IPD is used.

### Install & use

```bash
pip install .
ione audit --study recovery --target noO2
ione borrow-check --study recovery --target noO2
python -m pytest tests/
```

Python API: `from ione import audit_decision, suggest_augmentation,
load_builtin`. Full docs, CSV spec, verdict interpretation and failure
modes: [docs/aggregate_audit/README.md](docs/aggregate_audit/README.md).
Verified built-in examples: RECOVERY (NEJM 2021), ISIS-2 (Lancet 1988),
WHO REACT (JAMA 2020).

## Legacy IONE (historical)

The repository also preserves the **original/legacy IONE** —
"Incoherence-Oriented Neutralisation and Extraction", a framework for
detecting hidden population structure in observational studies
(C1 coherence indicator, stratification-based extraction). That
research code (`data_generation.py`, `methods.py`, `evaluation.py`,
`run_simulation.py`, `real_data_analysis.py`, `results/`) is retained
unchanged as a research artifact. See
[docs/legacy_ione.md](docs/legacy_ione.md) for its original README.

## Package

- Distribution `ione-audit`, import package `ione`, CLI `ione`.
- License: MIT (see `LICENSE`). Citation: `CITATION.cff`.
- JOSS paper draft: `paper/paper.md`.
