# Coherence diagnostics (C1 and W) for hidden effect modification in individual participant data meta-analysis: the IONE framework and a simulation study

{{PAGE}}

## Abstract

**Background:** In IPD meta-analysis, marginal treatment-effect estimates can be biased when hidden effect modifiers are ignored. We propose two coherence diagnostics, C1 (1 minus the I^2 statistic applied to stratum-specific log odds ratios) and W (the proportion of CATE variance explained by the stratification), and evaluate them within Incoherence-Oriented Neutralisation and Extraction (IONE), an exploratory diagnostic framework for hidden effect modification.

**Methods:** We simulated an IPD meta-analysis with 10 studies, a binary treatment and outcome, measured covariates carrying traces of an unmeasured modifier, and study-level variation in baseline risk and treatment prevalence. Proposed and comparator methods stratified the pooled IPD; stratum-specific risk differences were synthesised with fixed-effect and DerSimonian-Laird random-effects meta-analysis. We report ARI, C1, W_true/W_est and ATE bias reduction with Monte Carlo standard errors, and we examined the empirical null distribution of the diagnostics and the sensitivity of W_est to outcome-model misspecification.

**Results:** In the primary scenario (n=2000, 10 studies, K=5 strata), the best method by ATE bias reduction was 1B_residual (ARI 0.032; C1 0.927; W_true 0.363; W_est 0.078). Crude ATE bias was 0.01865; stratification reduced it to 0.01345 (relative 0.279) and random-effects pooling to 0.00816 (relative 0.563). Diagnostic recovery of the true hidden structure remained modest. Under the null of no true effect modification, C1 and W_est were distributed close to their chance-reference values; a main-effects outcome model inflated W_est, whereas the default interaction model was robust. Sensitivity analyses showed that bias reduction depends most on sample size and effect-modification strength, and the diagnostics remained informative under non-linear covariate mappings.

**Conclusions:** IONE is a transparent diagnostic flag for hidden effect modification in IPD meta-analyses. It should be reported alongside conventional models and covariate adjustment, not used as a replacement for rigorous causal inference.

**Keywords:** individual participant data meta-analysis; evidence synthesis; heterogeneity; hidden effect modification; stratification

{{PAGE}}

## 1. Introduction

Meta-analysis pools treatment-effect estimates across studies and is central to evidence-based medicine [borenstein2009]. IPD meta-analysis preserves participant-level covariates and can improve power for treatment-covariate interactions [riley2010][simmonds2005]. Random-effects syntheses are recommended when between-study heterogeneity is suspected [dersimonian1986][higgins2002][riley2011], yet conventional summaries estimate a marginal effect and may miss effect modifiers that are unmeasured or omitted [pearl2009][greenland1999]. When the pooled population is a mixture of subgroups with different treatment effects, the marginal effect can reverse or mislead within strata, producing Simpson-type paradoxes [simpson1951][rojanaworarit2020].

IPD meta-analysis offers subgroup analyses, meta-regression and one-stage mixed models, but these explain heterogeneity through measured covariates and study-level factors. They do not test whether the pooled participants themselves form internally homogeneous subpopulations with respect to the treatment effect. We therefore frame Incoherence-Oriented Neutralisation and Extraction (IONE) as an exploratory diagnostic: it flags when a marginal summary may be fragile and, when incoherence is indicated, extracts more homogeneous subgroups from multivariate patterns in measured variables. "Neutralisation" means reducing the misleading influence of a marginal summary by separating it into coherent subpopulations.

Hidden population structure is documented across medicine and social science: kidney-stone treatments [charig1986], university admissions [bickel1975], COVID-19 case-fatality comparisons [vonkuegelgen2021], national vaccine-surveillance data [haas2021], and smoking-mortality studies [appleton1996]. Established methods—propensity scores [rosenbaum1983], prognostic scores [hansen2008], disease-risk scores [miettinen1976], instrumental variables [angrist1996] and high-dimensional propensity scores [schneeweiss2009]—adjust for measured confounders but do not detect unmeasured population structure. Proximal causal inference and latent-class models use proxy variables [tchetgen2024][mclachlan2000] but do not report a transparent between-stratum heterogeneity diagnostic. We operationalise IONE through two coherence diagnostics: C1, derived from the I^2 heterogeneity statistic [higgins2002] applied to stratum-specific log odds ratios, and W, the proportion of total CATE variance explained by the stratification. Stratum-specific risk differences are synthesised with fixed-effect or DerSimonian-Laird random-effects meta-analysis.

## 2. Methods

This simulation study follows the ADEMP framework [morris2019].

### Aims

Evaluate whether stratification of pooled IPD can recover hidden subgroup structure; compare outcome-informed IONE methods with outcome-free and established comparators; assess whether C1 and W diagnose hidden effect modification; quantify ATE bias reduction from fixed-effect and DerSimonian-Laird random-effects synthesis of stratum-specific risk differences; and identify data-generating conditions under which the diagnostics are most informative.

### IPD data-generating mechanism

We simulated an IPD meta-analysis with n=2000 participants assigned to 10 studies (scale parameter 0.6 for baseline risk, treatment prevalence and an age-like covariate). Each participant had three critical variables (Z1 continuous, Z2 binary, Z3 ordered) that affected treatment, outcome and treatment-covariate interactions, and ten measured variables (X1-X10) carrying traces of Z. A binary treatment A and binary outcome Y were generated from logistic models with Z and X main effects, a treatment effect and Z-by-A interactions. The estimand was the population risk-difference ATE; full algebra is in Additional file 1.

The primary scenario used n=2000, 10 studies and K=5 strata. We varied K (3, 5, 10), sample size (500, 2000, 10 000), Z-to-Y effect scale (0.5, 1.0, 2.0), Z-to-X influence scale (0.2, 0.5, 1.0) and introduced a non-linear Z-to-X mapping. The primary and strata-sensitivity scenarios used 50 replications; extended robustness used 30; empirical null used 200 and W_est misspecification used 50.

### Stratification methods

**Proposed Family 1 (outcome-informed).** Method 1A: predicted probability of Y from logistic Y~X, stratified by quantiles. Method 1B: absolute residual from the same model. Method 1C: K-fold cross-validated predictions before stratification.

**Proposed Family 2 (outcome-free).** Method 2A: first principal component of standardised X. Method 2B: K-means on standardised X.

**Comparators and baselines.** Propensity-score quintiles [rosenbaum1983], Gaussian mixture model on X [mclachlan2000], prognostic-score stratification (untreated-only Y~X) [hansen2008]; Oracle baselines stratify by true Z-space; random assignment provides a chance reference. Equal-frequency strata were used throughout, logistic regression used l2 regularisation (C=1.0, lbfgs), and outcome-informed methods used a 50/50 discovery/evaluation split.

### Synthesis of stratum-specific effects

Within each stratum we computed the risk difference between outcome probabilities under treatment and control. A two-stage fixed-effect summary weighted strata by size; a DerSimonian-Laird random-effects summary estimated between-stratum variance [dersimonian1986]. *Neutralisation* reduces the misleading influence of a marginal summary by extracting coherent subpopulations.

Three caveats apply. Discovered strata are not independent estimates; they are formed from the same IPD sample, so their stratum-specific risk differences are dependent. The DerSimonian-Laird tau^2 and SE therefore describe between-stratum heterogeneity and should be interpreted cautiously. The SE of the pooled random-effects risk difference is conditional on the chosen stratification and does not account for stratum-formation uncertainty. C1 is computed from stratum-specific log odds ratios while ATE bias is on the risk-difference scale, so C1 is an indirect diagnostic.

### Evaluation metrics

**ARI** [hubert1985]: agreement between estimated strata and a true-Z partition, corrected for chance. **C1** = 1 - I^2 applied to stratum-specific log odds ratios [higgins2002]; lower C1 indicates stronger between-stratum heterogeneity. **W_true / W_est:** proportion of total CATE variance explained by the stratification; W_est requires a correctly specified outcome model. **ATE bias reduction:** absolute differences between crude, stratified and random-effects estimates, plus relative ratios. Monte Carlo SE and 95% CI accompany every mean. The true-Z partition is a k-means clustering of standardised Z-space with K strata.

### Empirical null distribution of C1 and W_est

We ran 200 additional replications under the primary DGM with Z-by-A interaction coefficients set to zero. This retains confounding and covariate traces but has no true effect modification. For each method we recorded C1 and W_est and report the 5th, 50th and 95th percentiles in Supplementary Table S5. Values below the 5th percentile (C1) or above the 95th percentile (W_est) provide conservative method-specific thresholds for flagging incoherence.

### W_est outcome-model misspecification sensitivity

W_est is computed from an estimated individual-level CATE. Omitting treatment-covariate interactions can inflate or deflate W_est, so we repeated the primary scenario with three outcome-model specifications for W_est: main effects only (Y ~ X + A), linear interactions (Y ~ X + A + X*A, default), and linear plus quadratic interactions. Results are in Supplementary Table S6.

### Semi-synthetic illustrations

Five Simpson-paradox examples were reconstructed as pseudo-individual records from published aggregate statistics [charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]. The Israeli vaccination example used pseudo-IPD reconstructed from age- and vaccination-stratified COVID-19-related hospitalisation counts published by Haas et al. [haas2021]. We chose hospitalisation rather than infection counts because the published Table 2 provides age- and vaccination-stratified counts for a severe endpoint where age confounding is pronounced, and because the low event rate (~0.09% in the down-sampled data) creates a stress-test for rare outcomes. Because the published counts cover approximately 6.5 million people, we used a stratified random down-sample of 100,000 records preserving the age- and vaccination-specific hospitalisation rates. In the down-sampled pseudo-IPD, some cells contained very few or zero hospitalisation events; logistic models used for outcome-informed methods were fitted with L2 regularisation, and any degenerate one-class fit was handled by returning the observed mean probability. Pseudo-general variables mimicked proxies of the known confounder and the number of strata K was selected from the set {2, 3, min(K_true, 4), K_true}, where K_true is the true number of published strata, keeping the value that maximised ARI. These are illustrations, not real-IPD validation.

### Reporting and reproducibility

The design followed ADEMP [morris2019]; checklists are in Additional files 2 and 3. The pipeline is version-controlled and every manuscript number is read from repository CSV outputs. Simulations used Python 3.11; the exact dependency versions are in `requirements-lock.txt` and the commit hash used for the submission package is in `results/commit_hash.txt`.


## 3. Results

### Primary IPD scenario

Table 1 reports the primary scenario (n=2000, 10 studies, K=5). Recovery of the true hidden structure was modest (Oracle ARI 0.372; best non-Oracle 1B_residual 0.032). Methods closer to the Oracle had C1 nearer to 1 and higher W, while random stratification yielded C1 0.883; W_true exceeded W_est, reflecting that the estimated CATE captures only part of the true CATE variation. The best bias reduction was for 1B_residual: crude 0.01865, stratified 0.01345 (relative 0.279) and random-effects 0.00816 (relative 0.563). For comparison, random-effects pooling across the true study identifiers (i.e. a study-level meta-analysis) gave an absolute ATE bias of 0.01568 (reduction 0.00296 from crude 0.01865). Pooling strata with DerSimonian-Laird improved over the fixed-effect summary, showing that stratum-specific effects should be allowed to vary.

| Method | ARI | C1 | W_true | W_est | Crude bias | Stratified bias | RE bias | Rel reduction strat | Rel reduction RE | RE I2 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1A_predicted_prob | 0.029 | 0.891 | 0.352 | 0.111 | 0.01865 | 0.01888 | 0.01352 | -0.013 | 0.275 | 0.142 |
| 1B_residual | 0.032 | 0.927 | 0.363 | 0.078 | 0.01865 | 0.01345 | 0.00816 | 0.279 | 0.563 | 0.044 |
| 1C_cv_decision | 0.029 | 0.891 | 0.352 | 0.111 | 0.01865 | 0.01888 | 0.01352 | -0.013 | 0.275 | 0.142 |
| 2A_PCA_cum60 | 0.016 | 0.881 | 0.158 | 0.080 | 0.01865 | 0.01883 | 0.01769 | -0.010 | 0.051 | 0.130 |
| 2B_clustering | 0.023 | 0.865 | 0.210 | 0.143 | 0.01865 | 0.01796 | 0.01651 | 0.037 | 0.115 | 0.146 |
| GMM | 0.005 | 0.895 | 0.050 | 0.096 | 0.01865 | 0.01797 | 0.01686 | 0.036 | 0.096 | 0.127 |
| PS_propensity_score | 0.005 | 0.881 | 0.050 | 0.059 | 0.01865 | 0.01816 | 0.01754 | 0.026 | 0.059 | 0.144 |
| Prognostic_score | 0.026 | 0.858 | 0.322 | 0.107 | 0.01865 | 0.01849 | 0.01430 | 0.009 | 0.233 | 0.141 |
| baseline_oracle_kmeans | 0.372 | 0.913 | 0.355 | 0.030 | 0.01865 | 0.01901 | 0.01651 | -0.019 | 0.115 | 0.124 |
| baseline_oracle_quantile | 0.095 | 0.897 | 0.447 | 0.042 | 0.01865 | 0.01620 | 0.01266 | 0.131 | 0.321 | 0.169 |
| baseline_random | 0.000 | 0.883 | 0.004 | 0.004 | 0.01865 | 0.01847 | 0.01901 | 0.010 | -0.019 | 0.117 |

*Table 1. Primary IPD scenario (n=2000, 10 studies, K=5): means over 50 simulations.*

Figure 1 visualises the primary scenario across methods.

![Figure 1. Primary IPD scenario: (a) ARI, (b) C1/W coherence diagnostics, and (c) ATE bias reduction by method.](fig1_rsm_ipd_primary.png)

### Sensitivity to the number of strata

Figure 2 and Supplementary Table S1 show random-effects bias reduction across K = 3, 5, 10. Data-driven methods did not reliably improve with larger K; Oracle baselines improved because finer strata better partition the true Z-space. Stratum count should be chosen conservatively and compared across values.

![Figure 2. Random-effects ATE bias reduction as the number of strata varies.](fig2_rsm_ipd_strata_sensitivity.png)

### Semi-synthetic illustrations

Five Simpson-paradox examples were reconstructed as pseudo-individual records [charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]. Table 2 reports the best non-Oracle method per dataset. The Israel hospitalisation example was the most challenging: strong age confounding and a very low hospitalisation rate (~0.09%) meant that the crude marginal association reversed with stratification, yet recovery of the true age groups from multivariate covariate patterns remained modest. The low event rate also produced occasional near-zero or zero-event cells, making this an illustration of the limits of outcome-informed extraction for rare outcomes.

| Dataset | Method | K | ARI | C1 | W_est | Bias reduction |
|---|---|---|---|---|---|---|
| COVID-19 CFR | 1B_residual | 3 | 0.065 | 1.000 | 0.035 | 0.017 |
| Israel Vaccine | 2B_clustering | 2 | 0.644 | 1.000 | 0.557 | 0.001 |
| Kidney Stone | GMM | 2 | 0.966 | 0.830 | 0.167 | 0.094 |
| Smoking Mortality | 1A_predicted_prob | 7 | 0.498 | 1.000 | 0.161 | 0.114 |
| UC Berkeley | PS_propensity_score | 3 | 0.084 | 0.284 | 0.177 | 0.031 |

*Table 2. Best semi-synthetic illustration result per dataset (oracle baselines excluded). Bias reduction is the absolute difference between crude and stratified ATE risk-difference bias.*

Figure 3 displays ARI by dataset and method for the semi-synthetic examples.

![Figure 3. Semi-synthetic illustration: ARI by dataset and method.](fig3_rsm_real_data_ari.png)

### Sensitivity to sample size

Figure 4 and Supplementary Table S2 report n = 500, 2000 and 10 000 (K=5). Crude bias declined with n; the largest relative reductions for leading methods occurred at n = 10 000. The outcome-residual method showed a floor near 0.008-0.009, so its relative reduction decreased with n.

![Figure 4. Sample-size sensitivity of random-effects ATE bias reduction (K=5).](fig4_rsm_ipd_sample_size.png)

### Sensitivity to Z-to-X and Z-to-Y effects

Supplementary Tables S3 and S4 report Z-to-X influence (0.2, 0.5, 1.0) and Z-to-Y effect (0.5, 1.0, 2.0). Stronger covariate traces improved ARI, but bias-reduction gains were variable. Weak effect modification produced C1/W near their nulls; stronger effect modification lowered C1, raised W and improved relative bias reduction. The residual method retained useful relative reduction even at z = 0.5.

### Robustness to non-linear Z-to-X mappings

Table 3 compares random-effects bias under linear and non-linear Z-to-X mappings. Effects were method-dependent but no leading method was dramatically degraded, indicating that the diagnostics remain useful when X is a non-linear function of the hidden structure.

| Method | Linear RE bias | Linear RE bias SE | Linear rel reduction | Linear rel reduction SE | Non-linear RE bias | Non-linear RE bias SE | Non-linear rel reduction | Non-linear rel reduction SE |
|---|---|---|---|---|---|---|---|---|
| 1B_residual | 0.00852 | 0.00043 | 0.522 | 0.093 | 0.00724 | 0.00042 | 0.640 | 0.060 |
| PS_propensity_score | 0.01676 | 0.00223 | 0.060 | 0.111 | 0.01653 | 0.00208 | 0.178 | 0.060 |
| GMM | 0.01736 | 0.00272 | 0.027 | 0.082 | 0.01894 | 0.00233 | 0.058 | 0.058 |
| Prognostic_score | 0.01374 | 0.00245 | 0.230 | 0.145 | 0.01464 | 0.00189 | 0.272 | 0.064 |
| 2B_clustering | 0.01684 | 0.00270 | 0.056 | 0.159 | 0.01773 | 0.00200 | 0.118 | 0.064 |

*Table 3. Linear versus non-linear Z-to-X mapping: random-effects ATE bias and relative bias reduction (n=2000, K=5, z=1.0, zx=1.0).*

Figure 5 shows random-effects ATE bias reduction under the non-linear mapping.

![Figure 5. Non-linear Z->X robustness: random-effects ATE bias reduction (n=2000, K=5).](fig5_rsm_ipd_nonlinearity.png)

### Empirical null distribution and W_est misspecification

Under the primary DGM with no Z-by-A interaction, C1 was generally high and W_est near 0; method-specific 5th/95th percentiles are in Supplementary Table S5. A main-effects-only outcome model inflated W_est, whereas the default interaction and polynomial models were more stable (Supplementary Table S6). C1 and W are diagnostic flags, not standalone inferential quantities.


## 4. Discussion

### Principal findings

This study frames IONE as an exploratory diagnostic for hidden effect modification in IPD meta-analysis. C1 and W signal whether a pooled IPD is internally coherent: methods that captured more of the true Z structure produced C1 values close to the Oracle and higher W, especially the residual-based method. Extraction of the true partition remained modest (Oracle ARI 0.372; best non-Oracle 1B_residual 0.032), but the best data-driven method reduced crude ATE bias from 0.01865 to 0.00816 (relative reduction 0.563) with DerSimonian-Laird pooling. These findings suggest that stratum-specific effects should be allowed to vary once incoherence is flagged.

### Detection versus extraction

Detection asks whether the pooled population is internally coherent; C1 and W address this without requiring hidden subgroups to be specified. If C1 is low and W_est is high, the marginal summary is likely incoherent and should be interpreted cautiously. Extraction attempts to recover hidden subgroups, but it is much harder than detection. IONE's practical value therefore lies in detection and partial ATE improvement, not in perfect confounding adjustment.

### Comparison with existing methods

Propensity-score [rosenbaum1983] and prognostic-score [hansen2008] methods adjust for measured confounders but do not detect unmeasured population structure. The high-dimensional propensity-score algorithm [schneeweiss2009] uses proxies to improve propensity-score estimation, not to identify subgroups or report a coherence diagnostic. Latent-class models [mclachlan2000] seek hidden subgroups but require strong distributional assumptions and do not provide a transparent between-stratum heterogeneity statistic like C1.

### Relevance to Biostatistics readers

IONE sits between heterogeneity diagnostics and model-based effect modification in IPD meta-analysis. C1 re-purposes I^2 for discovered strata and W connects the partition to explained CATE variance; both are descriptive sensitivity flags, not inferential tests. The empirical null distribution (Supplementary Table S5) calibrates the diagnostics under no true effect modification, and the misspecification sensitivity (Supplementary Table S6) checks robustness of W_est to the outcome-model specification. IONE is best used alongside conventional IPD meta-analysis, with standard adjustment applied within strata.

### Strengths and limitations

**Strengths.** The study followed ADEMP [morris2019], reported the data-generating mechanism and estimands transparently, and generated all numerical results from version-controlled repository scripts.

**Limitations.** The primary scenario used n=2000 and a moderate Z->X trace; sensitivity analyses examined n=500 to 10 000, Z-to-Y and Z-to-X scales, and a non-linear mapping, but performance may vary with stronger/weaker signals or fewer studies. The true-Z partition is a constructed reference, so ARI should not be over-interpreted as clinical validity. W_est depends on a correctly specified outcome model with interactions; a main-effects-only model can mislead (Supplementary Table S6). DerSimonian-Laird strata are not independent estimates, so tau^2 and I^2 describe between-stratum heterogeneity, not conventional between-study heterogeneity. C1 is computed from log odds ratios while ATE bias is on the risk-difference scale, so it is an indirect diagnostic. Null thresholds (Supplementary Table S5) are method-specific and conditional on the primary DGM. Semi-synthetic examples are pseudo-IPD reconstructions and illustrate settings, not real-IPD validation.



## 5. Conclusions

IONE (Incoherence-Oriented Neutralisation and Extraction) is an exploratory diagnostic framework for hidden effect modification in IPD meta-analysis. Monte Carlo simulation and semi-synthetic examples show that the C1 and W diagnostics can flag incoherence; when hidden variables leave strong traces in measured covariates, stratification can partially reduce ATE bias, but extraction of the true hidden partition remains difficult. The diagnostics should be reported alongside conventional meta-analytic models and covariate adjustment, and should not be used as a replacement for rigorous causal inference. We recommend that coherence assessment using C1 and W be considered as a standard sensitivity step in IPD meta-analysis reporting.


{{PAGE}}

## Declarations

### Ethics approval and consent to participate

Not applicable. This study used simulated data and publicly available aggregate statistics only.

### Consent for publication

Not applicable.

### Availability of data and materials

All simulation code, analysis scripts, semi-synthetic example data, and the manuscript generator are publicly available at https://github.com/bougtoir/ione-stratification-framework. The repository contains a `requirements.txt` file and a `requirements-lock.txt` file with exact package versions, fixed random seeds for every scenario, and `generate_summary.py`, `generate_ione_rsm_v3.py` and `generate_rsm_tables.py` scripts that regenerate all manuscript numbers, figures and tables in a Python 3.11 environment. The exact Git commit hash used to create this submission package is recorded in `results/commit_hash.txt`. An archived Zenodo release with a DOI will be created before acceptance to satisfy long-term reproducibility requirements. The published aggregate datasets used for the semi-synthetic illustrations are referenced in the original publications [charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996].

### Competing interests

The authors declare that they have no competing interests.

### Funding

No external funding supported this work.

### Authors' contributions (CRediT taxonomy)

Onishi Tatsuki: Conceptualisation, methodology, software, formal analysis, writing – original draft, writing – review and editing, visualisation.

### Acknowledgements

Not applicable.

### Supplementary materials

Supplementary methods, abbreviations, the ADEMP/STROBE-Sim checklists, the four extended sensitivity tables, and the empirical null-distribution and W_est misspecification sensitivity tables are provided in `biostatistics_supplementary_v3.docx`.

### Artificial intelligence

Manuscript text, Python code, and some analyses were drafted or revised using large language models (OpenAI GPT-4 and GPT-4o, accessed August 2025 through August 2026) under the direct, iterative supervision of the author. The LLMs were used for drafting prose, formatting references, generating figures, and implementing the computational pipeline. The author designed the study, wrote the simulation code, selected all references, verified every numerical result against the repository outputs, and approved the final scientific content. No LLM-generated text was used without human review.


{{PAGE}}

{{REFS}}

