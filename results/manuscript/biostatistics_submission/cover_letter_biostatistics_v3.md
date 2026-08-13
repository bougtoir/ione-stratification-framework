Dear Editor,

We are pleased to submit our manuscript, **"Coherence diagnostics (C1 and W) for hidden effect modification in individual participant data meta-analysis: the IONE framework and a simulation study"**, for consideration by *Biostatistics*.

## Why *Biostatistics* is the right venue

The paper addresses a methodological problem at the heart of modern biostatistics: how to diagnose hidden effect modification when individual participant data are pooled across studies. We frame the problem as an exploratory IPD meta-analysis problem, propose two coherence diagnostics (C1 and W), and evaluate them through Monte Carlo simulation and semi-synthetic illustrations. The work therefore fits the journal's scope of statistical methods with direct application to health and disease data, rather than being a disease-specific clinical study.

## What the paper contributes

1. **A diagnostic toolkit, not a black-box estimator.** IONE separates two tasks: detecting whether a marginal IPD summary is incoherent with respect to a conditional treatment effect, and extracting coherent subpopulations when covariate traces of hidden modifiers are available. We formalise this through C1 (between-stratum heterogeneity) and W (within-stratum homogeneity), and show how they relate to ATE bias reduction on the risk-difference scale.
2. **IPD meta-analysis framing.** The motivating examples and the simulation design are presented as a two-stage IPD meta-analysis: first stratification, then DerSimonian-Laird random-effects synthesis. We explicitly discuss why strata are not independent study estimates and how the resulting tau^2 and standard errors should be interpreted.
3. **Empirical calibration and misspecification checks.** We report the empirical null distribution of C1 and W under no true effect modification (Supplementary Table S5) and a sensitivity analysis of W_est to outcome-model specification (Supplementary Table S6). These additions help readers interpret the diagnostics as flags rather than as formal tests.
4. **Transparent, reproducible simulation.** Every numerical result is read from CSV summary files produced by a public repository (https://github.com/bougtoir/ione-stratification-framework). The repository contains the data-generating code, fixed random seeds, all scenario definitions, a `requirements.txt` and `requirements-lock.txt` file, and the manuscript generator itself. The commit hash used to build the submission package is recorded in `results/commit_hash.txt`. A Zenodo archive with a DOI will be created before acceptance.

## How we have addressed likely reviewer concerns

- **Diagnostic framing.** The title, abstract and conclusions now frame IONE as a diagnostic flag for hidden effect modification, not as a guaranteed adjustment method. The limitations section states this explicitly.
- **Supplementary materials.** The Additional files, the list of abbreviations, the extended sensitivity tables (K selection, sample size, Z-to-X and Z-to-Y effects), the empirical null-distribution table and the W_est misspecification table are collected in `biostatistics_supplementary_v3.docx`. The main manuscript references them at the appropriate points.
- **Definitions and caveats.** The term "neutralisation" is defined explicitly in the Methods, the DerSimonian-Laird within-stratum dependence caveat is discussed, and the "Bias reduction" column in Table 2 is defined as an absolute difference.
- **Reproducibility.** We have expanded the Data/Code Availability and AI declarations, added a `requirements-lock.txt` file and a `results/commit_hash.txt` record, and kept all manuscript numbers reproducible from repository CSVs.
- **Figures and tables.** All figures and tables are cited in order in the main text, and the separate `biostatistics_tables_separate.docx` and `biostatistics_figures.pptx` files provide editable versions.

We hope that readers of *Biostatistics* will find the framework useful as a sensitivity step when reporting IPD meta-analyses.

Sincerely,

Onishi Tatsuki
Data Science AI Innovation Research Promotion Center, Shiga University
bougtoir@gmail.com
ORCID: 0000-0001-7261-9062
