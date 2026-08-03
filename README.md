# IONE: Incoherence-Oriented Neutralisation and Extraction

A simulation study of stratification-based diagnostics for hidden population structure in observational studies.

## Overview

IONE proposes two exploratory diagnostics for observational treatment-effect estimates:
- **C1** (between-stratum heterogeneity): 1 − I² from stratum-specific log odds ratios of treatment on outcome.
- **W** (within-stratum homogeneity): variance ratio of estimated or true conditional average treatment effects within strata.

The repository implements the data-generating mechanism, stratification methods, evaluation metrics and manuscript-generation pipeline used in the revised submission to *Statistical Methods in Medical Research*, with an additional RSM-framed IPD meta-analysis scenario and manuscript under `devin/ione-rsm-reframe`.

## Repository structure

```
├── data_generation.py            # Monte Carlo data generation with binary treatment A and outcome Y
├── methods.py                  # Stratification methods (IONE, active comparators, baselines)
├── evaluation.py               # Metrics: ARI, η², C1, W, risk-difference ATE bias reduction
├── run_simulation.py           # Phase 1, sensitivity and non-linearity simulations
├── run_rsm_ipd_simulation.py   # RSM IPD meta-analysis simulation
├── real_data_analysis.py       # Semi-synthetic illustrations from 5 Simpson's-paradox examples
├── generate_summary.py         # Aggregate simulation/real-data CSVs into summary tables
├── generate_manuscript.py      # Generate Word manuscript and figures from summaries
├── generate_rsm_manuscript.py  # Generate RSM-framed Word manuscript and figures
├── generate_tables_docx.py     # Generate separate editable tables .docx
├── md_to_docx.py               # Minimal markdown-to-docx converter
├── requirements.txt            # Python dependencies
└── results/
    ├── phase1_results.csv
    ├── sensitivity_results.csv
    ├── nonlinearity_results.csv
    ├── real_data/
    │   └── real_data_results.csv
    ├── summary/                # Tidy summary tables with Monte Carlo SEs
    ├── figures/                  # PNG figures + editable PowerPoint
    └── manuscript/               # Revised manuscript, cover letters, response, checklists
```

## One-command reproduction

With Python 3.10+:

```bash
pip install -r requirements.txt
python3 run_simulation.py                  # ~30 min on 2 CPUs
python3 run_rsm_ipd_simulation.py          # RSM IPD meta-analysis scenario, ~1 min on 2 CPUs
python3 real_data_analysis.py              # a few minutes
python3 generate_summary.py
python3 generate_tables_docx.py
python3 generate_manuscript.py             # SMMR/Stat Med manuscript
python3 generate_rsm_manuscript.py         # RSM manuscript
```

All numbers in `results/manuscript/IONE_revised_manuscript.docx` are read from `results/summary/*.csv`; no estimates are hard-coded in the manuscript generator.

## Target journal

- **Primary:** *Statistical Methods in Medical Research* (SAGE)
- **Alternatives:** *Journal of Causal Inference* (de Gruyter), *Statistics in Medicine* (Wiley)

## Key methods

- **Proposed IONE**: 1A predicted probability, 1B residual, 1C cross-validated decision power, 1D ML uncertainty; 2A PCA (6 variants), 2B k-means on X.
- **Active comparators**: propensity-score quintiles, Gaussian mixture model, prognostic-score stratification.
- **Oracle baselines**: oracle k-means on Z, oracle quantile on Z1; random stratification as lower baseline.
- Outcome-informed methods use a 50/50 discovery/evaluation split.
- The ATE estimand is the **population risk difference** (collapsible across strata).

## Key results (from the updated simulation)

- Extraction performance (ARI) is modest in the primary simulation, with oracles as expected higher.
- Bias reduction on the risk-difference scale is modest; residual-based outcome-informed methods (1B) and outcome-free clustering perform best among proposed methods.
- Real-data illustrations show high ARI only when the pseudo-measured variables are strongly correlated with a simple, low-dimensional confounder.

## Requirements

- Python 3.10+
- numpy, pandas, scikit-learn, scipy, matplotlib
- python-docx, python-pptx

## Data and code availability

Code and semi-synthetic data are available at https://github.com/bougtoir/ione-stratification-framework.
