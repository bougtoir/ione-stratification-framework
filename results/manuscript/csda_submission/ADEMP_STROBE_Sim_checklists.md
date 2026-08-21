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
- C1 = 1 − I^2 from stratum-specific log odds ratios of A → Y (exploratory between-stratum heterogeneity).
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


{{PAGE}}

# STROBE-Sim checklist for the IONE simulation study

## Title and abstract
- Abstract includes design (simulation study), objectives, methods, key results and conclusion.
- Keywords identify simulation, causal inference, stratification, diagnostics.

## Introduction
- Rationale: hidden effect modification and confounding can distort observational treatment-effect estimates; existing methods rely on measured covariates.
- Objectives: evaluate stratification-based diagnostics and extraction under explicit confounding and effect modification.

## Methods
- Simulation design: fully factorial Monte Carlo.
- Data-generating mechanism: binary treatment and outcome; explicit Z→A, Z→Y, Z→X, and Z×A→Y mechanisms. Parameters in `data_generation.py`.
- Estimands: risk-difference ATE, C1, W, ARI, ATE bias reduction.
- Number of simulated datasets: 50 replications per scenario (phase 1), 30 replications per cell (sensitivity, non-linearity).
- Methods compared: listed in Table 1 and `run_simulation.py`.
- Outcome-informed methods use discovery/evaluation split to prevent circularity.
- Performance measures: mean, SD, Monte Carlo SE and 95% CI half-width.

## Results
- Phase 1 primary scenario, sensitivity grid and non-linearity results are summarised in CSVs and figures.
- Real-data illustrations are reported separately as semi-synthetic examples.

## Discussion
- Strengths: explicit estimand, active comparators, reproducible code.
- Limitations: stylised DGM, constructed true-Z partition, no real individual-level cohort.
- Generalisability: findings are conditional on the DGM and parameter ranges tested.

## Other information
- Funding: none.
- Conflicts of interest: none.
- Data and code availability: public repository.
- No real human data; simulation and reconstructed aggregate data only.

