# ADEMP checklist for the IONE simulation study

## A — Aims
- Primary aim: evaluate whether routine measured covariates can be used to stratify an observational sample into subgroups with more homogeneous treatment effects, and whether two diagnostics (C1, W) indicate hidden population structure.
- Secondary aim: compare proposed IONE methods against active comparators (propensity-score quintiles, Gaussian mixture model, prognostic-score stratification) and oracle baselines in a controlled simulation.

## D — Data
- Data are synthetic; no real patient data are used in the main simulation.
- Semi-synthetic examples use reconstructed aggregate counts from five published Simpson's-paradox examples.
- Data-generating parameters are fully specified in `data_generation.py` and documented in the Methods.

## E — Estimand
- Population risk-difference ATE: τ = E[Y(1) − Y(0)].
- Crude marginal risk difference: P(Y=1|A=1) − P(Y=1|A=0).
- Bias reduction = absolute / relative reduction in |estimated ATE − true ATE|.
- C1 = 1 − I² from stratum-specific log odds ratios of A → Y (exploratory between-stratum heterogeneity).
- W = 1 − weighted within-stratum CATE variance / overall CATE variance (within-stratum homogeneity).
- ARI with a constructed true-Z partition measures recovery of the operational hidden partition.

## M — Methods
- DGM: binary treatment from logistic model with Z and X; binary outcome from logistic model with Z, X, A, Z×A interactions; measured X influenced by Z.
- Default DGM tuned to realistic low-to-moderate confounding (true risk-difference ATE ≈ 0.01).
- Sensitivity analyses vary sample size, Z→Y strength, Z→X influence, number of strata, and non-linear Z→X mappings.
- Methods include 4 outcome-informed IONE variants, 7 outcome-free variants, 3 active comparators, 2 oracle baselines and random stratification.
- Outcome-informed methods use a 50/50 discovery/evaluation split.
- Metrics are computed on the evaluation split.

## P — Performance
- Monte Carlo means and standard errors are reported for every metric.
- Performance is summarised by method, scenario and DGM factor.
- Bias reduction is reported on the risk-difference scale; relative reduction is derived from absolute-bias means for stability.

## Reproducibility
- All code, parameter defaults and DGM are in the public repository.
- Results CSVs are produced by `run_simulation.py`, `real_data_analysis.py`, `generate_summary.py` and `generate_manuscript.py`.
- No numbers are hard-coded in the manuscript generator.
