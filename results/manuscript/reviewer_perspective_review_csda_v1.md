# Reviewer-perspective review: IONE CSDA v1 submission package

**Target journal:** *Computational Statistics & Data Analysis* (Elsevier)  
**Package version:** `results/manuscript/csda_submission/v1_ione_csda_submission_package.zip`  
**Git branch:** `devin/ione-csda-v2`  
**Date of review:** 20 August 2026

---

## Executive verdict

The CSDA v1 package is submission-ready for *Computational Statistics & Data Analysis*. The manuscript has been reframed from the SMMR medical-statistics audience to the CSDA computational-statistics audience (new "Relevance to CSDA readers" paragraph), the output directory and filenames have been changed to `csda_submission`, and the package contains all Elsevier Your Paper Your Way components: main manuscript docx, double-spaced docx/PDF, title page, cover letter, supplementary docx, separate tables docx, editable figures pptx, individual figure PNG/EPS files, and CSDA highlights.

All mechanical checks pass: Vancouver-style numbered references appear in order of first citation, every figure/table is cited before its inline placement, equations are OMML objects in Word, no hard-coded numerical results, and the generator reads all values from `results/summary/*.csv`.

---

## 1. Fit with CSDA scope and author guidelines

### What works
- Computational focus: the title, abstract and discussion emphasise stratification diagnostics, simulation benchmarking and reproducible code, which fit CSDA's scope.
- The abstract is concise (191 words), has no references, and uses six keywords (the journal maximum).
- Highlights are supplied as both `highlights.txt` and `highlights.docx` with 5 bullets, each ≤ 85 characters.
- The reference list is consistent and numbered; CSDA accepts any consistent style at initial submission.
- "Your Paper Your Way" permits a single compiled file at first submission, but the zip also includes all recommended separate files.
- Data/code availability statement includes the public repository, `requirements.txt`/`requirements-lock.txt`, fixed seeds and the recorded commit hash.

### Optional improvements
- Add DOIs to the reference list where available. CSDA does not mandate a style but highly encourages DOIs. The current Vancouver strings contain journal, year, volume and pagination but no DOIs.

---

## 2. Manuscript, scope and narrative

### What works
- Clear negative/qualified message: C1 and W_est do not reliably discriminate the alternative DGM from the empirical null in the primary scenario, and the manuscript repeatedly warns against treating them as inferential tests.
- Two concrete recommendations are given in the Conclusions: (1) C1/W only as descriptive flags, and (2) pre-specify effect modifiers and reserve data-driven stratification for exploratory sensitivity analyses.
- The Discussion frames IONE as a descriptive sensitivity framework, separates subgroup recovery from detection, and explains the structural bias floor observed at n = 500/2 000/10 000.

### High-priority point

#### 2.1 C1 AUC below 0.5 and lower-tail assumption (HIGH, but already explained)
- Table 4 reports C1 AUC as low as 0.460. The text now explains that the one-sided lower-tail null threshold does not match the direction of the alternative shift for every method.
- The added Supplementary Table S7 absolute-deviation scores confirm that an absolute-deviation threshold does not rescue discrimination.

---

## 3. Statistical design and methodology

### What works
- ADEMP structure is explicit; aims, DGM, estimands, methods, performance measures and number of replications are all stated.
- Sensitivity scenarios vary K (3, 5, 10), n (500, 2 000, 10 000), Z-to-Y scale (0.5, 1.0, 2.0), Z-to-X scale (0.2, 0.5, 1.0) and a non-linear Z-to-X mapping.
- Empirical null distribution (200 replications) calibrates C1 and W under no true effect modification.
- W_est misspecification sensitivity (main effects / interactions / polynomial) is reported in Supplementary Table S6.
- The study-level DerSimonian-Laird benchmark contextualises how much bias reduction comes from covariate stratification versus study-level pooling.

### Medium-priority point

#### 3.1 Terminology consistency (MEDIUM)
- Methods define `W_excess = max(W - null mean W, 0)`, an excess (truncated) measure. The abstract/Results refer to "W excess" and "null-centred" somewhat interchangeably. This is unlikely to trigger a desk rejection but a referee may ask for clarification.

---

## 4. Figures and tables

### What works
- 7 figures and 4 main tables are all cited in order of first appearance in the body text.
- Figures and tables are placed inline in the main docx immediately after their first citation.
- `csda_figures.pptx` (1 figure per slide) and individual PNG/EPS files are provided for journal upload.
- `csda_tables_separate.docx` contains all main and supplementary tables in an editable Table Grid format.
- Captions include the key scenario identifiers (n, K, replications, scales) needed for reproduction.

### Issues
- None that would prevent submission.

---

## 5. Reproducibility and data availability

### What works
- No numerical results are hard-coded in the generator; every value is read from `results/summary/*.csv`.
- `results/commit_hash.txt` records the exact commit used to generate the package.
- `generate_summary.py` → `generate_rsm_tables.py` → `generate_ione_rsm_v3.py` regenerates all numbers, figures and docx files.

### Pre-submission action

#### 5.1 Clean-clone reproduction pass (MUST)
Before finalising the submission, run the following on a clean machine:

```bash
git clone https://github.com/bougtoir/ione-stratification-framework.git
cd ione-stratification-framework
git checkout <csda-v2-branch-or-merge-commit>
pip install -r requirements.txt
python3 generate_summary.py
python3 generate_rsm_tables.py
python3 generate_ione_rsm_v3.py
# Compare results/manuscript/csda_submission/ with the prepared package
```

`results/commit_hash.txt` will differ if the checkout commit differs from the one used to author the package, but the generated docx text/tables/figures should be identical for the same generator commit.

---

## 6. Strength of claims

- The claims stay within the evidence: C1 and W are sensitivity diagnostics, not tests; the residual method "best" is conditional on the simulated DGM; the true-Z oracle provides an upper bound, not a clinical benchmark.
- The semi-synthetic examples are explicitly labelled as pseudo-IPD illustrations, not real-IPD validation.
- The main take-away — data-driven stratification can partially reduce marginal bias when measured covariates carry strong traces of hidden effect modification, but it cannot recover hidden subgroups — is well supported by the simulations.

---

## Priority summary

| Priority | Item |
|---|---|
| ** must-fix before submission ** | Run a clean-clone reproduction pass and confirm outputs match the package. |
| ** high ** | Add DOIs to the reference list where available (optional but strongly encouraged by CSDA). |
| ** medium ** | Clarify `W_excess` vs "null-centred W" terminology if any inconsistency remains. |
| ** optional ** | Consider adding a short supplementary note on why absolute-deviation C1 does not rescue the residual method. This is already partially addressed in the main text and Supplementary Table S7. |

---

## Final recommendation

Submit. The package meets CSDA's Your Paper Your Way requirements, follows the requested CSDA framing, and passes the mechanical checks (Vancouver citations, inline figures/tables, OMML equations, non-hard-coded numbers). The only remaining task is a clean-clone reproduction pass and, if time permits, DOI enrichment of the reference list.
