# IONE: Incoherence-Oriented Neutralisation and Extraction

A simulation study of stratification-based diagnostics for hidden population structure in observational studies.

## Overview

IONE proposes two exploratory diagnostics for observational treatment-effect estimates:
- **C1** (between-stratum heterogeneity): 1 − I² from stratum-specific log odds ratios of treatment on outcome.
- **W** (within-stratum homogeneity): variance ratio of estimated or true conditional average treatment effects within strata.

The repository implements the data-generating mechanism, stratification methods, evaluation metrics and manuscript-generation pipeline used in the current submission to *Statistical Methods in Medical Research* (SMMR).

## Repository structure

```
├── data_generation.py            # Monte Carlo data generation with binary treatment A and outcome Y
├── methods.py                  # Stratification methods (IONE, active comparators, baselines)
├── evaluation.py               # Metrics: ARI, η², C1, W, risk-difference ATE bias reduction
├── run_simulation.py           # Phase 1, sensitivity and non-linearity simulations
├── run_rsm_ipd_simulation.py   # RSM IPD meta-analysis primary simulation
├── run_rsm_ipd_extended.py     # RSM IPD sample-size, Z-to-Y, Z-to-X and non-linearity robustness simulations
├── real_data_analysis.py       # Semi-synthetic illustrations from 5 Simpson's-paradox examples
├── generate_summary.py         # Aggregate simulation/real-data CSVs into summary tables
├── generate_ione_rsm_v3.py     # Generate full SMMR Word manuscript, title page, cover letter and figures
├── generate_full_rsm_manuscript.py # Generate SMMR figures and widescreen figures .pptx
├── generate_rsm_tables.py      # Generate separate editable tables .docx
├── md_to_rsm_docx.py           # Markdown-to-docx converter with Vancouver citations and OMML math
├── requirements.txt            # Python dependencies
└── results/
    ├── rsm_ipd_results.csv
    ├── rsm_ipd_sensitivity_results.csv
    ├── rsm_ipd_nonlinearity_results.csv
    ├── real_data/
    │   └── real_data_results.csv
    ├── summary/                # Tidy summary tables with Monte Carlo SEs
    ├── figures/                  # PNG/EPS figures + editable PowerPoint
    └── manuscript/smmr_submission/  # SMMR submission package (docx, pptx, zip)
```

## Reproduction

With Python 3.10+:

```bash
pip install -r requirements.txt
python3 run_rsm_ipd_simulation.py          # primary IPD scenario (~2 min)
python3 run_rsm_ipd_extended.py            # sensitivity and non-linearity robustness (~30 min)
python3 real_data_analysis.py              # a few minutes
python3 generate_summary.py
python3 generate_ione_rsm_v3.py            # main manuscript, title page, cover letter, figures and .pptx
python3 generate_rsm_tables.py             # separate editable tables docx
```

To regenerate only the reproducible figures and summary numbers from the committed CSVs:

```bash
make
```

This writes `results/summary/*.csv`, `results/figures/*.{png,eps}` and `results/figures/pptx/rsm_figures.pptx`, without creating the Word/PDF/zip submission package.

To build the full CSDA submission package from the same committed CSVs:

```bash
make submission
```

Equivalent commands:

```bash
python3 generate_summary.py
python3 generate_ione_rsm_v3.py --figures-only   # numbers + figures only

python3 generate_summary.py
python3 generate_rsm_tables.py
python3 generate_ione_rsm_v3.py                  # full CSDA submission package
```

All numbers in the manuscript are read from `results/summary/*.csv`; no estimates are hard-coded in the generator.

## Target journal

- **Primary:** *Statistical Methods in Medical Research* (SAGE)
- **Previously considered:** *Research Synthesis Methods* (Wiley), *Biostatistics* (Oxford)

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
