# FINAL SUBMISSION DECISION — IONE / Austrian Journal of Statistics

**Verdict: CONDITIONAL GO** — submission package is scientifically
sound, journal-compliant, and internally consistent. Remaining items
are author-side confirmations, not blockers to preparing the
submission.

Submission commit: `fc160fa62e72b82862e40cf68a0184421f62fbd2`
(branch `devin/1791939580-ione-ajs-micro`; the zip was packaged at branch HEAD — see git log for the two doc-only commits above this SHA).

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
   ("Shiga University, Data Science and AI Innovation Research Promotion
   Center" and the Banba address) and supply ORCID if available —
   currently left as provided, ORCID not invented.
2. ~~**Git lineage**~~ — RESOLVED 2026-10-14: PRs #13, #14, #15 merged;
   `main` @ `b0e62d7` contains the audited package and the `ajs/` tree.
   Remaining: merge this minor-fix branch so the repo exactly matches
   the submitted manuscript version (or submit as-is and merge before
   publication; the differences are prose-only). Suggested reviewers
   (Palmer/Shpitser/Mathur) still need the author's conflict-of-interest
   check.
3. **Version tag** (optional): no git tag/release exists for v0.2.0;
   tagging the submission commit after merge is recommended but not
   required.

## Minor-fix update (this commit)

All adversarial-review issues I-01..I-10 handled — see
`MINOR_FIX_CHANGELOG.md`. Prose-only edits; no numeric results changed.
pytest 34/34; PDF rebuilds clean (10 pp).

## Not done (per instructions)

No journal submission, no PR merge, no release tag, no force-push.
