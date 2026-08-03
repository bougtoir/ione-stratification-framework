# Pre-submission critical review — IONE revised manuscript

Prepared from a mock-reviewer perspective before submission to *Statistical Methods in Medical Research*.

## 1. Novelty and scope

**Strengths.**
- The manuscript is honest about its scope: an exploratory diagnostic-sensitivity study, not a finished causal-inference workflow.
- Reframing IONE as a pair of diagnostics (C1, W) plus stratification benchmarking is a clear conceptual advance over the original two-stage extraction claim.

**Weaknesses / concerns.**
- The novelty may be questioned because stratification diagnostics are not new; the contribution rests on the specific combination of between-stratum heterogeneity (C1) and within-stratum CATE homogeneity (W). Make this combination explicit in the first paragraph of the Introduction.
- The term "neutralisation" in the acronym is still operationalised only as "bias reduction by stratification"; consider whether the acronym adds value or can be de-emphasised further.

## 2. Statistical design and estimands

**Strengths.**
- Switching the ATE estimand to the risk difference (collapsible) is correct and should be highlighted.
- Discovery/evaluation splitting for outcome-informed methods addresses the circularity concern.
- Reporting of Monte Carlo SEs is included in the summary generator.

**Weaknesses / concerns.**
- The primary simulation uses a single default DGM. Reviewers may ask whether the conclusions generalise; the sensitivity and non-linearity analyses help but should be described as such, not as post-hoc robustness checks.
- The "true" Z partition is constructed (k-means/quantile on Z). The manuscript must be explicit that ARI is agreement with an operational target, not necessarily with clinically meaningful subgroups.
- W_true is a simulation-only oracle metric. The Abstract should not imply it is operational; keep W_est as the operational diagnostic.
- Relative bias reduction is reported as a secondary metric and is now computed robustly from absolute-bias means; ensure this is stated in the Methods.

## 3. Figures and tables

**Strengths.**
- Tables are generated from summary CSVs; numbers are reproducible.
- Figures separate into an editable PowerPoint.

**Weaknesses / concerns.**
- Figure 1 has many metrics on one panel with different scales (C1 near 0.9, bias reduction near 0.01). Consider two panels or normalised axes.
- Table 1 is wide; for SMMR it may exceed column width. Prepare a landscape version or split into two tables (one for recovery/ARI, one for bias).
- Real-data figure 3 currently only K=3; the best results per dataset may use K=3 or K=5. Report the K that produced the best ARI in Table 2.

## 4. Reproducibility

**Strengths.**
- All numbers come from code; no hard-coded estimates in the manuscript generator.
- Public repository is referenced.

**Weaknesses / concerns.**
- The simulation run takes ~30 min with 2 CPUs. Provide a README with exact command, expected run time, and dependency versions.
- Commit the final results CSVs (or a tagged release) so the exact numbers are preserved. Distinguish between "reproducible from code" and "frozen for submission".
- Add a `requirements.txt` or `environment.yml` to lock scikit-learn/pandas/numpy/python versions.

## 5. Strength of claims

**Strengths.**
- Claims are tempered: "modest", "conditional", "exploratory".

**Weaknesses / concerns.**
- The Conclusions must avoid language that could be read as recommending clinical use. Phrase should be "may help analysts decide whether to pursue subgroup-specific analysis" rather than "identify populations that warrant treatment".
- The phrase "partially corrected" in the Discussion could be read as causal. Replace with "stratified estimates showed smaller ATE bias in some scenarios".

## Priority actions before submission

1. **Essential.** Add an explicit statement that the true-Z partition is constructed and ARI measures agreement with that operational target.
2. **Essential.** Verify that every numerical claim in the Abstract and Discussion is reproduced by the summary CSVs; regenerate the manuscript after the full simulation.
3. **High.** Split or resize Table 1; add a table of simulation parameters and algorithm settings.
4. **High.** Lock dependency versions and provide a one-command reproduction script.
5. **Medium.** Add an editable separate tables docx and figure png/eps files for SAGE submission.
6. **Medium.** Include the ADEMP and STROBE-Sim checklists as supplementary files.
7. **Anytime.** Convert the SMMR response letter and JoCI cover letter to docx for the submission package.
