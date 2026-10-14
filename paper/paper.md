---
title: "IONE: Identifiability-Oriented Navigation of Evidence for aggregate clinical trial data"
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
  - name: Shiga University, Data Science and AI Innovation Research Promotion Center
    index: 1
date: 11 October 2026
bibliography: paper.bib
---

# Summary

IONE (Identifiability-Oriented Navigation of Evidence) is an open-source
Python package that audits whether published aggregate
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
preserves the original/legacy IONE (Incoherence-Oriented Neutralisation and
Extraction) stratification codebase for detecting hidden
population structure in observational data [@onishi-ione-legacy].

# Statement of need

Even a statistically sound RCT or meta-analysis does not automatically
justify a treatment decision for the patient in front of a clinician who
differs from the enrolled population: published arm-level margins can be
consistent with many incompatible conditional risk distributions, some
of which reverse the implied subgroup decision. The information needed
to resolve this — individual patient data — is ordinarily inaccessible
to the clinical researcher. What is accessible is the published
aggregate report itself.

Existing tools synthesize effects (`metafor`, `netmeta`), quantify bias
sensitivity (`EValue`, `tipr`), or design trials (`OptimalDesign`) —
none audits *identifiability* on aggregate margins: whether every model
compatible with the published table implies the same decision, and what
the cheapest additional aggregate summary would be to resolve it.
`ione` is an *evidence-audit* tool for researchers: it makes the degree
of under-identification explicit and orders the missing reports by
burden (re-tabulation before new measurement before new enrollment). It
does **not** recommend treatment for any individual patient, does not
claim external validity, and reports only what the published counts
support — including explicit abstention.

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
  (RECOVERY dexamethasone [@recovery2021], ISIS-2 [@isis2_1988],
  WHO REACT meta-analysis [@react2020]), where the package reproduces a
  documented real-data borrowing failure.

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
