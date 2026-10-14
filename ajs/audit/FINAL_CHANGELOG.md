# FINAL_CHANGELOG — micro revision for AJS submission

Base commit: `fc160fa62e72b82862e40cf68a0184421f62fbd2` on branch
`devin/1791939580-ione-ajs-micro` (parent `2d3fe12`, the L1/L2/L3
revision; lineage root `21a253e` = PR #12 head — note `main`/`eec5849`
still does not contain the aggregate-audit package).

Input package: `IONE_AJS_SUBMISSION_PACKAGE.zip` (R-revision build).

## Changes (diff vs 2d3fe12)

1. **ISIS-2 accuracy (Step 1)** — `ione_ajs.tex` Abstract and the
   ISIS-2 Results paragraph now state that subgroup *effects were
   published as odds reductions* but not as arm-by-stratum counts, so
   the *event-count ladder* stops at L1; added one clarifying sentence
   that this is "a property of the event-count ladder, not an absence
   of published subgroup evidence". No counts inferred from odds
   reductions.
2. **ROBUST semantics (Step 2)** — after the verdict list in Methods:
   "The ROBUST labels refer exclusively to sign stability within the
   identified set conditional on the observed margins and stated
   assumptions; they do not incorporate sampling uncertainty and do
   not constitute clinical treatment recommendations." In Results, the
   no-oxygen L3 sentence now notes the 95% CI crosses zero, separating
   point-identified direction from sampling precision. API/CLI label
   names unchanged.
3. **Cover letter burden realism (Step 3)** —
   "near-zero-cost cross-tabulation request" → "a potentially
   low-burden cross-tabulation request — recognizing that even
   re-tabulation carries real data-management and privacy costs for
   trial groups". Single-author I-voice and novelty framing unchanged.

## Verified, unchanged (Step 4)

- Author block: Onishi Tatsuki; affiliation "Shiga University, Data
  Science AI Innovation Research Promotion Center" retained as
  provided in earlier sessions; ORCID remains unconfirmed — no value
  invented (recorded in FINAL_SUBMISSION_DECISION.md).
- Bibliography: 18 entries, all real (DOIs verified during A1 gate);
  every bib entry cited; figure/table cited in order (Table 1, Table 2,
  Figure 1); `fig_levels.pdf` exists and is included.
- No new affiliations, journals, or claims created.

## QC (Step 5)

- `pdflatex`/`bibtex` build clean: 10 pages, 0 errors/undefined refs.
- `pytest tests/ -q`: **34/34 passed** (measured; log in
  `ajs/audit/logs/pytest_final_r2.txt`).
- Numbers in text/table/figure match `ajs/audit/r_levels.csv` exactly
  (RECOVERY −0.121/−0.029/+0.037; L2 bounds; ISIS-2 L1-only).
- No REACT post-treatment variable used as a baseline stratum anywhere.
- No new statistical theory claimed anywhere in text.
