# IONE: Incoherence-Oriented Neutralisation and Extraction

A framework for detecting hidden population structure in observational studies and extracting coherent subpopulations for valid within-subgroup inference.

## Overview

IONE addresses multiple biases arising from hidden population structure in observational studies:
- **Confounding bias**
- **Simpson's paradox**
- **Undetected effect modification**
- **Ecological fallacy**
- **Non-collapsibility**

The framework operates in two stages:
1. **Detection**: The C1 coherence indicator (derived from I² heterogeneity statistic) quantifies population incoherence
2. **Extraction**: Stratification-based methods extract coherent subpopulations using routinely measured variables alone

## Methods

Two families of stratification methods are implemented:

**Family 1: Decision power-based (outcome-informed)**
- 1A: Predicted probability stratification
- 1B: Residual-based stratification
- 1C: Cross-validated decision power
- 1D: Machine learning uncertainty (Random Forest)

**Family 2: Feature score-based (outcome-free)**
- 2A: PCA-based stratification
- 2B: k-means clustering

## Project Structure

```
├── data_generation.py          # Monte Carlo data generation (DAG-based)
├── methods.py                  # IONE stratification methods
├── evaluation.py               # Performance evaluation (ARI, η², C1)
├── run_simulation.py           # Main simulation runner (66,600 evaluations)
├── visualization.py            # Simulation result visualisation
├── real_data_analysis.py       # Application to 5 Simpson's paradox datasets
├── real_data_visualization.py  # Real data result visualisation
├── docs/                       # Specifications and background documents
│   ├── spec_stratification_pseudo_randomization.md      # Spec v0.1
│   ├── spec_stratification_pseudo_randomization_v0.2.md # Spec v0.2
│   ├── prognostic_score_and_hdPS_explanation.md
│   └── scope_check.md
├── results/
│   ├── figures/                # Simulation figures (10 PNG, 300 DPI colour)
│   ├── real_data/              # Real data analysis results & figures
│   ├── manuscript/             # Publication-ready outputs
│   │   ├── IONE_manuscript.md / .docx          # English manuscript
│   │   ├── IONE_manuscript_japanese_summary.md / .docx  # Japanese summary
│   │   ├── IONE_figures_tables_EN.pptx         # English figures/tables
│   │   ├── IONE_figures_tables_JA.pptx         # Japanese figures/tables
│   │   ├── create_pptx_en.py / create_pptx_ja.py       # PPTX generators
│   │   ├── create_docx.py / create_japanese_docx.py     # DOCX generators
│   │   └── background.md
│   ├── phase1_results.csv      # Phase 1 simulation results
│   ├── sensitivity_results.csv # Sensitivity analysis results
│   ├── evaluation_report.md
│   ├── simulation_summary.md
│   ├── journal_recommendation.md
│   └── simpson_paradox_examples.md
```

## Target Journal

**BMC Medical Research Methodology** — Special Collection "Causal inference and observational data vol. 2" (Deadline: 30 July 2026)

## Key Results

- **Simulation**: 66,600 evaluations across 1,200+ scenarios. All proposed methods significantly outperform random stratification.
- **C1 indicator**: Reliably detects incoherent populations in both simulation and 5 real-world datasets.
- **Real data**: Applied to kidney stone (ARI=0.851), Israeli vaccine (ARI=0.746), COVID-19 CFR, UC Berkeley admissions, and smoking-mortality datasets.

## Requirements

- Python 3.11+
- numpy, pandas, scikit-learn, scipy, matplotlib, seaborn
- python-pptx, python-docx (for manuscript generation)
