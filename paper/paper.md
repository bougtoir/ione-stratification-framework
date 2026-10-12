---
title: "IONE: aggregate-evidence decision audits for published clinical trial data"
tags:
  - Python
  - evidence synthesis
  - partial identification
  - clinical trials
  - decision analysis
authors:
  - name: Tatsuki Onishi
    affiliation: 1
affiliations:
  - name: Independent researcher
    index: 1
date: 11 October 2026
bibliography: paper.bib
---

# Summary

`ione` is a Python package that audits whether published aggregate
evidence — arm-level event counts, subgroup tables, and margins from RCTs
and meta-analyses — can support a specified clinical decision for a
target patient subgroup, without individual patient data. For a binary
stratum, binary outcome, two-arm setting it formulates the compatible
model set as a polytope and computes sharp bounds on the conditional
risk difference via linear programming (HiGHS), returning
`ROBUST_TREAT`, `ROBUST_NO_TREAT`, `REVERSIBLE`, `INFEASIBLE`, or
`UNSUPPORTED` — states kept strictly separate so that inconsistent
inputs, insufficient information, and nonidentification are never
conflated. When the decision is not robust, the package suggests the
cheapest *reportable* augmentation (re-tabulation before new measurement
before new enrollment) without promising resolution, and provides a
retrospective leave-one-subgroup-out borrow check. The package also
preserves the original IONE stratification codebase for detecting hidden
population structure in observational data [@onishi-ione-legacy].

# Statement of need

Subgroup tables in trial publications report aggregate counts, yet
clinicians and meta-researchers routinely ask whether a treatment
decision for a specific subgroup is implied by those counts. Existing
tools either synthesize effects (`metafor`, `netmeta`), quantify bias
sensitivity (`EValue`, `tipr`), or design trials (`OptimalDesign`) —
none audits *identifiability*: whether any set of conditional risks
consistent with the published margins could flip the decision, and what
the cheapest additional aggregate summary would be to resolve it. `ione`
fills that workflow gap with an exact LP engine rather than heuristics,
reports solver status and feasibility residuals, and is explicit about
the assumptions (common stratum prevalence, mixing proportions, decision
threshold) under which each verdict holds.

# State of the field

Partial identification via linear programming on aggregate margins is
classical [@manski2003]. `ione` implements no new estimator: its
contribution is packaging the audit — margin consistency checking,
sharp conditional bounds, three-way verdicts, and cost-ordered
augmentation suggestions including near-zero-cost re-tabulation
requests — into a tested, documented workflow built on verified real
datasets. Borrowing diagnostics follow the retrospective
leave-one-subgroup-out construction; they are demonstrations of what
unexamined pooling would have concluded, not prospective validation.

# Research use cases

- Auditing a published subgroup table before citing it for a
  subgroup-specific decision.
- Deciding whether to request a re-tabulation, a new measurement, or a
  new stratum-restricted trial — ordered by burden.
- Teaching identifiability vs estimation with verified examples
  (RECOVERY dexamethasone, ISIS-2, WHO REACT meta-analysis), where the
  package reproduces a documented real-data borrowing failure.

# Software design

Pure Python, `numpy`+`scipy` only, pip-installable (`ione-audit`), CLI
(`ione audit`, `ione borrow-check`) and Python API with structured JSON
output. All examples run offline from built-in, source-cited aggregate
counts. Tests compare LP optima against closed-form algebraic bounds and
reproduce published effect estimates.

# AI assistance disclosure

Parts of the implementation and documentation were drafted with AI
assistance; all numerical claims are verified against published sources
and independent algebraic references in the test suite.

# Acknowledgements

Uses published aggregate data only; no patient-level records.
