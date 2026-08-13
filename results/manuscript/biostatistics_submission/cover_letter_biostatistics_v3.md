Dear Editor,

We are pleased to submit our manuscript, **"IONE: Incoherence-Oriented Neutralisation and Extraction for hidden effect modification in individual participant data meta-analysis: a simulation study of stratification-based extraction"**, for consideration by *Biostatistics*.

## Why *Biostatistics* is the right venue

The paper addresses a methodological problem at the heart of modern biostatistics: how to diagnose and reduce bias from hidden effect modification when individual participant data are pooled across studies. We frame the problem as an exploratory IPD meta-analysis problem, propose a new diagnostic toolkit (IONE) built on coherence diagnostics, and evaluate it through Monte Carlo simulation and semi-synthetic illustrations. The work therefore fits the journal's scope of statistical methods with direct application to health and disease data, rather than being a disease-specific clinical study.

## What the paper contributes

1. **A diagnostic, not a black-box estimator.** IONE separates two tasks: detecting whether a marginal IPD summary is incoherent with respect to a conditional treatment effect, and extracting coherent subpopulations when covariate traces of hidden modifiers are available. We formalise this through two metrics, C1 and W, and show how they relate to ATE bias reduction on the risk-difference scale.
2. **IPD meta-analysis framing.** The motivating examples and the simulation design are presented as a two-stage IPD meta-analysis: first stratification, then DerSimonian-Laird random-effects synthesis. The method is therefore evaluated in the context in which it would actually be used.
3. **Transparent, reproducible simulation.** Every numerical result is read from CSV summary files produced by a public repository (https://github.com/bougtoir/ione-stratification-framework). The repository contains the data-generating code, fixed random seeds, all scenario definitions, a `requirements.txt` file, and the manuscript generator itself. A Zenodo archive with a DOI will be created before acceptance.

## How we have addressed likely reviewer concerns

- **Supplementary materials.** The Additional files, the list of abbreviations, and the extended sensitivity tables (K selection, sample size, Z-to-X and Z-to-Y effects) are now collected in `biostatistics_supplementary_v3.docx`. The main manuscript references them at the appropriate points.
- **Definitions.** The term "neutralisation" is now defined explicitly in the Methods, and the a-priori rule used to choose the number of strata in the semi-synthetic illustrations is reported.
- **Reproducibility.** We have expanded the Data/Code Availability and AI declarations. A double-spaced PDF for initial submission is included in the package, together with the editable docx files.
- **Figures and tables.** All figures and tables are cited in order in the main text, and the separate `biostatistics_tables_separate.docx` and `biostatistics_figures.pptx` files provide editable versions.

We hope that readers of *Biostatistics* will find the framework useful as a sensitivity step when reporting IPD meta-analyses.

Sincerely,

Onishi Tatsuki
Data Science AI Innovation Research Promotion Center, Shiga University
bougtoir@gmail.com
ORCID: 0000-0001-7261-9062
