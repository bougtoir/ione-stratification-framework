# FINAL SUBMISSION DECISION — IONE / Austrian Journal of Statistics

**Verdict: CONDITIONAL GO** — submission package is scientifically
sound, journal-compliant, and internally consistent. Remaining items
are author-side confirmations, not blockers to preparing the
submission.

Submission commit: `fc160fa62e72b82862e40cf68a0184421f62fbd2`
(branch `devin/1791939580-ione-ajs-micro`).

## Why not HOLD

- All numeric claims reproduce from `ajs/analysis/reproduce_r.py` and
  match `r_levels.csv`; LP bounds verified against closed-form algebra
  (max err ~1.8e-15); pytest 34/34.
- The two substantive honesty issues are resolved: L1/L2 are labelled
  ablations where L3 is published (RECOVERY); post-treatment variables
  can no longer appear as strata (REACT SAE excluded, flagged).
- ISIS-2 subgroup reporting is described accurately — odds reductions
  existed; only the arm-by-stratum counts the ladder needs were never
  printed.
- ROBUST labels are explicitly scoped to sign stability of the
  identified set, not clinical recommendation; L3 point and its CI are
  not conflated.
- AJS compliance re-verified: official `ajs.cls`/`ajs.bst`, author-date
  citations, vector PDF figures, LaTeX tables, software cited, no
  submission/processing fee, CC-BY (per A1 gate records).
- JOSS submission history disclosed in the cover letter per AJS
  fairness rules.

## Conditions the author must close before pressing "submit"

1. **Affiliation/ORCID**: confirm the legal affiliation string
   ("Shiga University, Data Science AI Innovation Research Promotion
   Center" and the Banba address) and supply ORCID if available —
   currently left as provided, ORCID not invented.
2. **Git lineage**: `main` (`eec5849`) does not contain the
   aggregate-audit package; the submission lineage is the `21a253e`
   family (PRs #13, #14, and this branch). Verify intended base and
   merge publicly before or alongside submission so the linked
   repository contains the audited code. Suggested reviewers
   (Palmer/Shpitser/Mathur) need the author's conflict-of-interest
   check.
3. **License/repo polish**: package README already documents the
   audited features; ensure the public repo reflects this commit
   (done once PR is merged by the author).

## Not done (per instructions)

No journal submission, no PR merge, no release tag, no force-push.
