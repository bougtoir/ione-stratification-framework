# Reproducibility and code–manuscript alignment note

## Summary

The R2 manuscript (`results/manuscript/r2_source/IONE_manuscript_r2_cleaned.docx`) and the current public/private code repositories are **not yet aligned**. Before a revised manuscript can be submitted to *Statistics in Medicine* or *Statistical Methods in Medical Research*, the simulation code must be updated and the numerical results regenerated from that updated code.

This note lists the discrepancies and the required code changes. The point-by-point response and cover letters in this folder assume the changes described here will be implemented before final submission.

## Discrepancies found

### 1. No treatment variable A in `data_generation.py`
- The manuscript describes a binary treatment A generated from a logistic model: Z → A, X → A.
- The current `data_generation.py` only generates X, Y and Z; there is no A.
- Consequence: the reported treatment-effect values (crude ATE 0.156, true ATE 0.069, bias reduction 0.074 / 7.4%) cannot be reproduced from the current code.

### 2. `compute_effect_estimation_bias` uses a Z-median split as the “treatment”
- In `evaluation.py` the function defines `treatment = (Z[:, 0] > np.median(Z[:, 0])).astype(float)`.
- This is not the treatment A described in the paper; the crude/stratified/oracle effect columns in `phase1_results.csv` and `sensitivity_results.csv` therefore do not match the manuscript.

### 3. C1 in the current code is computed from mean Y per stratum, not from stratum-specific log odds ratios of A → Y
- The manuscript defines C1 = 1 − I² based on stratum-specific **treatment-effect** log odds ratios.
- `compute_coherence_c1` in `evaluation.py` uses `effects = [y_s.mean() for y_s in strata]`.
- With no treatment A, a log-OR-based C1 cannot be computed.

### 4. The W metric is not implemented in the code
- The manuscript reports W = 0.292 for Method 1B, W = 0.557 for oracle quantile, etc.
- No function in `evaluation.py` computes W; `C1_heterogeneity`, `C2_residual_structure`, `C3_prediction_stability`, `C4_entropy` are different quantities.

### 5. Active comparators are not implemented
- The manuscript lists propensity-score quintiles, Gaussian mixture model (GMM) and prognostic score as active comparators.
- `methods.py` and `run_simulation.py` contain only the proposed IONE methods, PCA variants and baselines (random/oracle). GMM, propensity-score and prognostic-score stratification are missing.

### 6. The reported simulation size differs from the code
- Manuscript: 240,300 evaluations (21,600 + 109,350 + 109,350).
- `run_simulation.py` generates 18,000 phase-1 and 48,600 sensitivity rows (using 4 methods in sensitivity, not the 9 stated in the manuscript).
- The non-linear robustness analysis (the second 109,350) is not present in `run_simulation.py`.

### 7. Reported numbers in `phase1_results.csv` do not match the manuscript tables
- Example: Method 1B, K = 5, zx = 1.0 in the CSV has mean ARI ≈ 0.028 (SE ≈ 0.0025 from SD), whereas the manuscript reports ARI = 0.021 (SE 0.0002).
- The difference is partly because the CSV contains 200 replications per scenario, but the standard-error formula in the manuscript divides by √n_reps.
- C1 values in the CSV also differ from the manuscript (e.g. random C1 ≈ 0.85 in CSV, but the manuscript reports 0.872; method 1B C1 ≈ 0.0017 in CSV, but the manuscript reports 0.859). This suggests either a different C1 computation or hand-entered values.

### 8. Semi-synthetic-illustration results in `real_data_results.csv` show different method coverage
- The CSV contains methods `1A_predicted_prob`, `1B_residual`, `1C_cv_decision`, `1D_ml_uncertainty`, `2A_pca`, `2B_clustering`, `random`.
- It does not contain the active comparators, so the manuscript’s Table 9 (which reports PS quintiles, GMM, prognostic score) cannot be reproduced from the current `real_data_analysis.py`.

## Required code changes

1. **Add binary treatment A to `data_generation.py`.**
   - `logit(P(A=1)) = γ₀ + γ_Z·Z_std + γ_X·X` with prevalence calibrated to ~50%.
   - Add `A` to the returned data dict.

2. **Update the outcome model in `data_generation.py`.**
   - `logit(P(Y=1)) = β₀ + β_Z·Z_std + β_X·X + τ·A + δ·(Z×A) + noise`.
   - Calibrate β₀ to the target event rate (~15%).
   - Add a function to compute the **true individual-level CATE** and the **true ATE** for each scenario.

3. **Implement active comparators in `methods.py`.**
   - `propensity_score_strata(X, A, Y, n_strata)`.
   - `gaussian_mixture_strata(X, Y, n_strata)`.
   - `prognostic_score_strata(X, A, Y, n_strata)` (fit on untreated A=0 only).

4. **Update `evaluation.py`.**
   - `compute_coherence_c1`: compute stratum-specific log odds ratios of A → Y and then I²/C1.
   - `compute_w_true(strata, true_cate)` and `compute_w_est(strata, A, Y, X)`.
   - `compute_effect_estimation_bias`: use actual A and true ATE from DGM; report both absolute and relative bias reduction.

5. **Update `run_simulation.py`.**
   - Add the active comparators to `build_method_specs`.
   - Add a non-linear Z → X robustness grid that replicates the sensitivity design.
   - Ensure the reported total evaluation count matches the manuscript.

6. **Update `real_data_analysis.py`.**
   - Run the active comparators on each semi-synthetic example.
   - Generate pseudo-general X variables correlated with the known confounder.

7. **Add a manuscript-generation script that reads the CSV results.**
   - Avoid hard-coded numbers.
   - Generate tables, figures and text from the updated `phase1_results.csv`, `sensitivity_results.csv` and `real_data_results.csv`.

## Suggested immediate next steps

1. Decide whether to implement the code changes in the current `bougtoir/wip` repository, in the public `ione-stratification-framework` repository, or in both (with sync).
2. Implement the changes above and rerun the full simulation grid.
3. Update the manuscript text, tables and figures using the regenerated results.
4. Add a tagged release / Zenodo DOI.
5. Run a clean-environment reproducibility check: clone the public repo, install dependencies, run the pipeline, and verify that the numbers in the manuscript are reproduced.

## Files in this folder

- `response_to_reviewers.md` / `.docx` — point-by-point response to the BMC MRM reviewers.
- `cover_letter_statmed.md` / `.docx` — cover letter for *Statistics in Medicine*.
- `cover_letter_smmr.md` / `.docx` — cover letter for *Statistical Methods in Medical Research*.
- `reproducibility_alignment_note.md` — this note.
