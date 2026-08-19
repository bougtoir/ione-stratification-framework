# Reviewer-perspective review: IONE SMMR v1 submission package

**Target journal:** *Statistical Methods in Medical Research* (SAGE)  
**Package version:** `results/manuscript/smmr_submission/v1_ione_smmr_submission_package.zip`  
**Git branch:** `devin/ione-smmr-v1` (head commit `744e0d4`, commit used for generation `7b2a32d` recorded in `results/commit_hash.txt`)  
**Date of review:** 19 August 2026

---

## Executive verdict

The revised package is now close to submission-ready for *Statistical Methods in Medical Research*.  
The manuscript fits the journal's medical-statistics scope, the abstract is within the 200-word limit, figures and tables are cited in order, references follow a Vancouver-style sequence, and the main scientific weakness—the weak empirical-null discrimination of C1 and W_est—is now reported honestly rather than overstated.  

During this review the following items were already corrected:

- Abstract/Results/Discussion narrative around the residual method's sample-size floor (n = 500/2 000/10 000) was reconciled with the CSV values.
- The misleading "higher C1 means a better method" wording was replaced with the finding that C1 alone does not separate useful from chance stratifications.
- An explanation of C1 AUCs below 0.5 was added in Methods and Results.
- Cover-letter header, date and author address were filled in.
- In-text citations and the reference list were formatted as SAGE Vancouver superscript numerals with comma separators.
- `README.md` was updated to reflect the SMMR target and the current reproduction pipeline.

The remaining pre-submission actions are mechanical: add 3–5 suggested reviewers, run one clean-clone reproduction pass, and tidy a couple of abbreviation/placeholder details.

---

## 1. Manuscript scope, structure and narrative

### Fit with SMMR
- The paper is framed as a methodological benchmark study in medical statistics: an exploratory diagnostic for hidden effect modification in IPD meta-analysis.  This aligns well with the SMMR aims/scope statement (*medical statistics, methods development and evaluation*).
- The simulation design follows ADEMP and includes STROBE-Sim checklists in the supplementary document, which will satisfy SMMR reviewers.

### What works
- **Title** is informative and within the SMMR long-title tolerance.
- **Abstract** is structured (Background/Methods/Results/Conclusions), ~189–190 words depending on the exact counting convention, and consistent with the main text.
- **Introduction–Methods–Results–Discussion flow** is coherent: the Intro sets up marginal bias / Simpson-type paradoxes; Methods defines C1, W, the empirical null and the study-level benchmark; Results reports the modest ARI and bias-reduction findings; Discussion frames the diagnostics as sensitivity tools.
- **All 7 figures and 4 tables are cited in order** in `IONE_smmr_v1.md` and the generated `IONE_smmr_v1.docx`; there are no orphan figures or phantom references.
- **No references to older versions** (「旧版」「以前の解析」) remain.
- The Discussion repeatedly qualifies claims (e.g. "descriptive sensitivity tool, not an inferential test") and does not over-causalise stratification-based bias reduction.

### Must-fix / high-priority points

#### 1.1 C1 AUC below 0.5 needs to be defensible (HIGH)
- Table 4 reports residual-method C1 AUC = 0.460 and several other methods at or just below 0.5.  The new text in Methods ("...for some methods C1 AUC fell below 0.5, indicating that the alternative DGM shifted C1 in the opposite direction to the lower-tail hypothesis") and Results ("50/545; the C1 AUCs at or below 0.5 for several methods confirm that the lower-tail null threshold does not match the direction of the alternative DGM shift...") correctly explains this as a directional mismatch rather than a coding error.
- **Reviewer risk:** a statistical referee may still ask why a one-sided lower-tail test is reported if the sign is method-dependent.  Consider adding a short supplementary note (or an extra sentence in the Discussion) that an absolute-deviation score was also tested and did not rescue residual C1, confirming that C1 is structurally weak as a universal classifier.  This is optional but would preempt a major-revision request.

#### 1.2 Overall message is a negative result (HIGH)
- In the primary scenario none of the diagnostics distinguish the alternative DGM from the empirical null above chance level (best C1 AUC 0.545; best W AUC 0.561; TPRs 0–8 %).  The Discussion handles this carefully.
- **Risk:** SMMR editors may ask what the *practical recommendation* is if the diagnostics are so weak.  The Conclusion already says "report alongside conventional models" — consider sharpening the recommendation sentence to two concrete actions: (1) use C1/W as sensitivity flags only, and (2) pre-specify potential effect modifiers rather than rely on data-driven stratification for decision-making.

---

## 2. Statistical design and methodology

### What works
- DGM is described transparently (n, K, Z-to-Y and Z-to-X scales, non-linear mapping, study-level variation, 50/200 replications).
- The study-level DerSimonian-Laird benchmark is included, which contextualises how much bias reduction is due to covariate stratification vs. study-level heterogeneity.
- Sensitivity analyses vary K, n, Z-to-Y scale, Z-to-X scale and the Z-to-X mapping.
- Empirical null distributions are used to calibrate C1 and W, reducing dependence on asymptotic approximations.
- W_est misspecification sensitivity (main effects / interactions / polynomial) is reported in Supplementary Table S6 and acknowledges the instability of W.

### High-priority points

#### 2.1 The C1 lower-tail ROC threshold is methodologically fragile (HIGH)
- The ROC assumes *lower* C1 is abnormal.  For residual stratification the alternative C1 is actually *higher* and more stable than the null, so the AUC collapses below 0.5.  This is now explained but the core assumption is still in the Methods.
- **Suggested mitigation:** in the Discussion/Supplementary, explicitly state that the reported ROC is a one-sided *sensitivity analysis*; the sign of an abnormal C1 is not known a priori and should be method-specific.

#### 2.2 "Null-centred W" vs. "W_excess" terminology (MEDIUM)
- Methods text introduces `W_excess = max(W - null mean W, 0)`.  In the abstract the wording is "null-centred W".  These are not identical (centering can be negative; excess is truncated at zero).  The Results/Discussion should use one term consistently, or note the truncation explicitly.

### Low-priority / optional

#### 2.3 Abbreviations not fully expanded at first main-text use (OPTIONAL)
- "CATE" and "IPD" appear in the abstract and Introduction before being written out in the main text.  The supplementary abbreviation table lists them, so this is unlikely to trigger a rejection, but a copy-editing reviewer may flag it.  Add "individual participant data (IPD)" and "conditional average treatment effect (CATE)" on first main-text use.

---

## 3. Figures and tables

### What works
- All 7 figures and 4 tables are cited sequentially.
- Figures are placed immediately after the paragraph that first cites them.
- The package includes both inline docx figures and separate PNG/EPS files, plus `smmr_figures.pptx` and `smmr_tables_separate.docx`, satisfying both inline and separate-file journal requirements.
- A separate editable PowerPoint of figures is provided.

### Issues

#### 3.1 Supplementary tables reference S3/S4/S5/S6 but their location is clear (LOW)
- The body text refers to Supplementary Tables S3–S6.  They are in `smmr_supplementary_v1.docx`.  No action needed unless SMMR wants tables numbered consecutively in one document.

---

## 4. Reproducibility and data availability

### What works
- The title page and Declarations state data/code availability and the exact commit hash.
- No numbers are hard-coded in the manuscript generator; they are read from `results/summary/*.csv` and `results/manuscript/smmr_submission/*.csv`.
- `requirements.txt` and `requirements-lock.txt` are referenced.
- `README.md` now correctly points to the SMMR submission package and the `generate_summary.py` → `generate_rsm_tables.py` → `generate_ione_rsm_v3.py` pipeline.

### Must-fix before submission

#### 4.1 Run a clean-clone reproduction pass (MUST-FIX)
- Required by the organisation knowledge base before any submission.
- **Command to test on a fresh machine:**
```bash
git clone https://github.com/bougtoir/ione-stratification-framework.git
cd ione-stratification-framework
pip install -r requirements.txt
python generate_summary.py
python generate_rsm_tables.py
python generate_ione_rsm_v3.py
# compare results/manuscript/smmr_submission/* with the submitted package
```
- The generated `results/commit_hash.txt` will differ if the clone is at a different commit, but the `IONE_smmr_v1.md` / `IONE_smmr_v1.docx` content should be identical when the same generator commit is checked out.

---

## 5. Strength of claims and language

### What works
- The manuscript repeatedly frames IONE as a *descriptive sensitivity tool*, not a test or subgroup-recovery algorithm.
- The ARI reference is described as "a constructed true-Z reference partition" rather than clinical truth.
- "Detection" (flags) is separated from "subgroup recovery" (ARI).
- Over-causal phrases have been removed.

### Medium-priority language points

#### 5.1 Avoid "confirm" (MEDIUM)
- The Results sentence "...the C1 AUCs at or below 0.5 for several methods **confirm** that the lower-tail null threshold does not match the direction..." is slightly stronger than the data warrant; "show" or "indicate" is preferable.

#### 5.2 Abstract phrasing (OPTIONAL)
- "Relative bias reduction improved as the Z-to-Y effect strengthened, while sample-size gains were method-specific; null-centred W confirmed weak discrimination." is information-dense but acceptable for a 190-word abstract.  It could be split for readability, though this would increase the word count.

---

## 6. Cover letter and title page

### Title page
- Complete: figures 7, tables 4, abstract 190 words, main text ~3 670 words (SMMR target ~8 000 words; with figures/tables counted as ~200 words each the total is well under the informal ceiling).
- Declarations (ethics, consent, COI, funding, CRediT, acknowledgements, AI disclosure, data/code availability) are all present.
- AI disclosure is thorough and transparent.

### Cover letter
- Header, date, journal address and author signature are now filled in.
- **Must-fix:** suggested reviewers are still listed as `[To be added: 3–5 names with institutions and email addresses.]`.  Some journals require these; SMMR does not always require them, but leaving a visible placeholder in the uploaded cover-letter file is a desk-rejection risk.  Either:
  1. Provide 3–5 plausible reviewers with emails, or
  2. Replace the line with a neutral sentence such as "Suggested reviewers: none to declare." and let the Editorial Manager field handle them.

---

## 7. References and citation style

### What works
- 20 references, real and numbered sequentially 1–20 in the order of first appearance.
- No orphan references; no citations exceed 20.
- The reference list includes key medical-statistics literature (DerSimonian-Laird, Higgins/Thompson I², Riley IPD, Morris et al. ADEMP, Rosenbaum/Rubin propensity score, Hubert/Arabie ARI, etc.).
- Semi-synthetic examples are referenced to published sources.

### What was corrected during this review
- In-text citations were changed from superscript bracketed numbers (`[1]`) to plain superscript numerals (`¹`) separated by commas for consecutive citations, matching SAGE Vancouver STM style.
- The reference list was changed from `[1] ...` to `1. ...` (number followed by a full point), consistent with SAGE Vancouver guidance.

### Optional improvements
- DOIs are not included.  While not required by SMMR, adding DOIs would increase reproducibility and is easy.

---

## 8. Summary of recommended priority actions

| Priority | Item | Action | Location |
|---|---|---|---|
| **MUST** | Suggested reviewers | Add names and emails, or remove placeholder | `cover_letter_smmr_v1.md/docx` |
| **MUST** | Clean-clone reproduction | Run fresh `git clone` + `generate_summary.py` + `generate_rsm_tables.py` + `generate_ione_rsm_v3.py` and diff outputs | repository / CI |
| **HIGH** | C1 AUC <0.5 defensibility | Keep the new caveat, and optionally add a Supplementary paragraph stating absolute-deviation tests did not rescue residual C1 | `IONE_smmr_v1.md`, `smmr_supplementary_v1.md` |
| **HIGH** | Practical recommendation | Sharpen the Conclusion to two concrete recommendations | `generate_ione_rsm_v3.py` Conclusions |
| **MEDIUM** | Abbreviation definitions | Write out IPD and CATE on first main-text use | `IONE_smmr_v1.md` Introduction |
| **MEDIUM** | W terminology | Use "W_excess" consistently or explain "null-centred" = excess | `IONE_smmr_v1.md` Abstract/Methods |
| **MEDIUM** | Replace "confirm" with "show" | Weaken causal/reporting verb | `IONE_smmr_v1.md` Results, diagnostic paragraph |
| **OPTIONAL** | Add DOIs | Include DOIs in reference list | `md_to_rsm_docx.py` / reference registry |
| **OPTIONAL** | Stronger practical takeaway | Add a one-sentence clinical/statistical recommendation | Discussion/Conclusion |

---

## Final recommendation

Submit to *Statistical Methods in Medical Research* after the two **must-fix** items (suggested reviewers and clean-clone reproduction) are completed and the **high-priority** C1/defensibility clarification is checked.  The package now honestly represents a negative-but-informative benchmark and is formatted in SAGE Vancouver style.
