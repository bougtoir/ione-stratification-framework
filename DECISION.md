# FINAL DECISION — IONE JOSS submission finishing pass

Date: 2026-10-12 (UTC). Repository: bougtoir/ione-stratification-framework,
PR #11 (branch devin/1791733973-ione-joss).

## Changes in this pass

- `cli.py`/`aggregate.py`: subgroup-vs-overall consistency check
  (`check_consistency`) — contradictions return INFEASIBLE; rounding-scale
  gaps are explicit `warning`s. Target-stratum share is now estimated
  per arm; when q1 vs q0 diverge beyond ~2 SE, the audit uses
  arm-specific weights instead of silently pooling.
- Tests: +5 (common-q estimate, consistency error/warning split,
  coarse full-enumeration cross-check vs LP). Suite: 27/27 PASS.
- `docs/aggregate_audit/README.md`: CSV spec, verdict interpretation
  table (what each state does NOT mean), designed failure modes.
- `paper/paper.md`: Statement of need rewritten — evidence-audit for
  researchers, explicitly not an automated treatment recommender;
  affiliation corrected to Shiga University / DS-AI Center.
- `paper/paper.bib`: Manski 2003 corrected from @article to @book;
  DOIs verified (RECOVERY 10.1056/NEJMoa2021436, ISIS-2
  10.1016/S0140-6736(88)92833-4, REACT 10.1001/jama.2020.17023).

## Verification log

- `pip install .` (pip ≥24) → OK; `ione audit --study recovery --target
  noO2` → REVERSIBLE, RD bounds [-1.00, +0.959], solver status 0,
  residual 2.8e-17; `ione borrow-check --study recovery --target noO2`
  → documented direction reversal (pooled 0.835 vs actual 1.267).
- `pytest`: 27/27 pass, including LP-vs-algebra agreement to 1e-8.

## JOSS requirements audit (current official docs, 2026-10)

OSI license (MIT) ✓; obvious research application ✓; feature-complete
non-trivial software ✓; documented ✓; tests/CI ✓; paper.md+paper.bib
drafted per current template ✓; no codified ≥6-month public-history
rule found in the current submission guidelines — the earlier six-month
criterion was a self-imposed gate.

## Unverified items

- **Public-start date: UNVERIFIED.** Earliest commit 2026-03-28 is
  repository history, not auditable proof of public visibility.
- Author ORCID and exact official affiliation English form: needs
  author confirmation.
- Property-based tests (Hypothesis): future enhancement, non-blocking.

## Judgment: **CONDITIONAL GO**

Software readiness is GO — no blocking defect (math correctness,
reproducibility, license, compliance) remains. The submission step is
conditional on: (1) author confirmation of affiliation/ORCID, (2) user
approval of this PR and of actually submitting, (3) optionally a JOSS
pre-submission eligibility inquiry if public-history evidence is
wanted.

## Social message

For clinicians and meta-researchers who cannot obtain IPD, `ione` makes
the under-identification inside a published aggregate report explicit
and orders the missing summaries by burden — turning "is this decision
justified?" from intuition into a bounded, auditable calculation.
