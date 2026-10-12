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
