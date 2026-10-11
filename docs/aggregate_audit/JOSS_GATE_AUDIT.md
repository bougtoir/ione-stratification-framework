# Final Gate: JOSS submission-readiness audit

Date of audit: 2026-10-11 (UTC). Criteria source: JOSS submission
requirements, https://joss.readthedocs.io/en/latest/submitting.html
(review criteria: https://joss.readthedocs.io/en/latest/review_criteria.html).

## Evidence ledger

| Requirement | Evidence | Verdict |
|---|---|---|
| Public repository start date | `git log --reverse`: first commit 8a662e1, **2026-03-28**, on public repo bougtoir/ione-stratification-framework | PASS |
| ≥6 months of public development history | 2026-03-28 → 2026-10-11 = **6.5 months elapsed**. Commit activity dates (all refs): 2026-03-28, 03-30, 06-04, 08-03, 08-20, 08-21, 10-11 — activity is periodic, not continuous | PASS (elapsed) / NOTE: active-commit span ~4.3 months before this PR |
| Ongoing development record | devin/* feature branches through 2026-08-21 + this audit-feature PR 2026-10-11 | PASS |
| OSI-approved license | LICENSE (MIT) added in this PR — previously absent | PASS (after PR) |
| Obvious research application | hidden-population-structure detection + aggregate-evidence decision audits for clinical evidence interpretation | PASS |
| Feature-complete (not trivial) | `ione` package: sufficiency audit, M(T) identifiability, borrow-check, augmentation planner, proximity profile; Python API + CLI | PASS |
| Functionality verified | `pytest tests/test_aggregate_audit.py` — 10/10 pass; RECOVERY built-in counts reproduce published RRs (IMV 0.708; pooled-borrow prediction 0.835 vs actual harm 1.267) | PASS |
| Documentation | `docs/aggregate_audit/README.md` (API, CLI, differentiation, limits) + existing README/specs | PASS |
| Real-data demonstration | RECOVERY dexamethasone NEJM 2021 subgroup counts (provenance in `ione/data.py`; cross-verified AD package) | PASS |
| Differentiation from existing software | audit decides *whether* to borrow, not how much; outputs cost-ordered *reportable* augmentations incl. re-tabulation requests | documented |
| JOSS paper.md / submission | **not yet drafted** — requires user approval per project rules | PENDING |

## Gate verdict

**PASS with one pending item.** Repository eligibility criteria are met
after this PR merges (license). JOSS submission itself additionally
requires `paper.md` (~250–1000 words), author metadata, and a GitHub
release/tag — proceed only on explicit user approval.

## Honest caveats

- Active commit history before this PR spans ~4.3 months (Mar–Aug 2026);
  the ≥6-month criterion is satisfied by elapsed public existence, which
  a strict reviewer could still question.
- `audit_decision` uses grid enumeration (binary covariate, balanced
  margins); multi-level covariates are out of scope for this release.
- Crude estimands only; adjusted published estimates are not
  reproducible from aggregate counts (documented limit).
