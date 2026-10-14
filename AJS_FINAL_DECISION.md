# Gate A7 — Final decision: CONDITIONAL GO

Date: 2026-10-13 (UTC). Branch `devin/1791902572-ione-ajs`, base commit
21a253e (PR #12 head — see discrepancy note below).

## Verdict: CONDITIONAL GO

Mathematical implementation verified (LP = closed-form bounds to
~1e-15 over 200 random margins; 27/27 tests pass; edge cases disjoint);
real-data reproduction verified against primary sources; AJS rules
satisfied from primary documents (LaTeX mandatory, no fees, CC-BY,
author retains copyright, author-date references, vector figures,
embedded tables). The paper claims a reproducible audit workflow and
applications — no new theory — which fits AJS's applied/computational
scope.

## Remaining items before submission (fix list)

1. **Author confirmations required**: ORCID; official English
   affiliation name and postal address (currently "Shiga University,
   Data Science and AI Innovation Research Promotion Center, 1-1-1 Banba,
   Hikone" — guessed address, must confirm); consent to list suggested
   reviewers (Palmer, Shpitser, Mathur — no CoI confirmed by author).
2. **Main-branch discrepancy (informational)**: handoff stated
   "main merged"; actually `main` (eec5849) does NOT contain the JOSS
   package — it lives only at 21a253e (PR #12 head, shown merged on
   GitHub but absent from main, consistent with a sync force-push).
   The AJS branch is based on 21a253e; the PR targets `main` and will
   effectively restore this lineage. Reviewer should verify before
   merging.
3. Optional: release tag v0.2.0 still uncreated (not AJS-blocking).
4. Optional: AI-assistance statement — author to confirm preferred
   wording consistent with his other submissions.

## Changes in this branch

- `ajs/manuscript/` — `ione_ajs.tex`, `ione_ajs.bib`, `ione_ajs.pdf`
  (9 pp, AJS style), `cover_letter.md`, `ajs.cls`, `ajs.bst`, `oesg.png`,
  `fig_bounds_vs_q.pdf`, `fig_verdicts.pdf`.
- `ajs/analysis/reproduce_a3.py` — all manuscript numbers from code.
- `ajs/audit/` — A0_INPUT_AUDIT, A1_JOURNAL_FIT, A1_CLOSEST_PRIOR.csv,
  A1_CITATION_ECOLOGY, A2_CLAIM_EVIDENCE_MATRIX.csv, A3_REPRO_REPORT,
  A5_EDITORIAL_FIT, A6_SUBMISSION_CHECKLIST, CSVs, logs, figures.
- `AJS_FINAL_DECISION.md` — this file.

## Key verified numbers

- RECOVERY audits: IMV REVERSIBLE [-1.000,+1.000]; O2 REVERSIBLE
  [-0.425,+0.379]; noO2 REVERSIBLE [-1.000,+0.959].
- ISIS-2: streptokinase ROBUST_TREAT [-0.025,-0.025] (degenerate q=1);
  combo REVERSIBLE [-0.236,+0.187].
- REACT SAE REVERSIBLE [-1.000,+0.627] (arm-specific weights).
- Borrow check RECOVERY/noO2: pooled 0.835 vs actual 1.267 — direction
  reversal reproduced.
- LP vs algebra: max err 1.78e-15 (200 margins); pytest 27/27.

## SHAs

- Base: 21a253ee93e7e25833a95afeed2469865b41a609
- This branch: see `git rev-parse HEAD` at PR.
- `ione_ajs.pdf` SHA-256: see package manifest in zip (MANIFEST.txt).

## Stopped per instructions

No submission, no merge, no release, no extra gates.

---

## Addendum — R-gate revision (2026-10-13)

An information-level (L1/L2/L3) revision was performed per
`IONE_AJS_INFORMATION_LEVEL_FINAL_REVISION_PROMPT.txt` on branch
`devin/1791935328-ione-ajs-l123`; see `ajs/audit/R_GATE_REPORT.md`,
`R_CLAIM_MATRIX.csv`, `r_levels.csv`, `r_ledger.csv`, `logs/r_qc.txt`.

Verdict remains **CONDITIONAL GO**. The revision fixed two real
problems found in the A0-A7 package: (a) RECOVERY results had been
presented as decision-reversible although arm-by-stratum counts were
published (ablation vs genuine gap now separated by the L1/L2/L3
ladder); (b) the REACT serious-adverse-events "subgroup" was a
post-treatment variable and has been excluded. ISIS-2 subgroup claims
were corrected to reflect that only odds reductions were published.
Residual conditions are unchanged (affiliation/ORCID confirmation,
reviewer CoI, main-branch lineage).
