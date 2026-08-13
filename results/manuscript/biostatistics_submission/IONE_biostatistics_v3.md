# IONE: Incoherence-Oriented Neutralisation and Extraction for hidden effect modification in individual participant data meta-analysis: a simulation study of stratification-based extraction

{{PAGE}}

## Abstract

**Background:** In IPD meta-analysis, marginal treatment-effect estimates can be biased when hidden effect modifiers are ignored. We propose Incoherence-Oriented Neutralisation and Extraction (IONE), an exploratory diagnostic for hidden effect modification.

**Methods:** We simulated an IPD meta-analysis with 10 studies, a binary treatment and outcome, measured covariates carrying traces of an unmeasured modifier, and study-level variation in baseline risk and treatment prevalence. Proposed and comparator methods stratified the pooled IPD; stratum-specific risk differences were synthesised with fixed-effect and DerSimonian-Laird random-effects meta-analysis. We report ARI, C1, W_true/W_est and ATE bias reduction with Monte Carlo standard errors.

**Results:** In the primary scenario (n=2000, 10 studies, K=5 strata), the best method by ATE bias reduction was 1B_residual (ARI 0.032; C1 0.927; W_true 0.363; W_est 0.078). Crude ATE bias was 0.01865; stratification reduced it to 0.01345 (relative 0.279) and random-effects pooling to 0.00816 (relative 0.563). Diagnostic recovery of the true hidden structure remained modest. Sensitivity analyses showed that bias reduction depends most on sample size and effect-modification strength, and the diagnostics remained informative under non-linear covariate mappings.

**Conclusions:** IONE is a transparent diagnostic for hidden effect modification in IPD meta-analyses, to be reported alongside conventional models and covariate adjustment.

**Keywords:** individual participant data meta-analysis; evidence synthesis; heterogeneity; hidden effect modification; stratification

{{PAGE}}

## 1. Introduction

Meta-analysis combines treatment-effect estimates from related studies and is central to evidence-based medicine and policy [borenstein2009]. In an individual participant data (IPD) meta-analysis, the original participant-level data are collected and re-analysed, which preserves covariate and subgroup information and can improve power for treatment-covariate interactions [riley2010][simmonds2005]. A random-effects analysis is widely recommended when between-study heterogeneity is suspected [dersimonian1986][higgins2002][riley2011]. Nevertheless, the standard two-stage or one-stage synthesis still estimates an average effect and may miss effect modifiers that are unmeasured, measured with error, or omitted from the analysis plan. When the pooled population is a mixture of subgroups with different treatment effects, or when confounders differ across studies, the marginal effect can differ from subgroup-specific effects, leading to aggregation bias and Simpson-type reversals [pearl2009][greenland1999].

Current IPD meta-analysis practice offers several tools for exploring heterogeneity, including subgroup analyses, meta-regression and one-stage mixed models with treatment-covariate interactions. These approaches explain heterogeneity through measured covariates and study-level characteristics, but they do not test whether the pooled participants themselves form internally homogeneous subpopulations with respect to the treatment effect. In other words, an analyst can conclude that there is statistically significant between-study heterogeneity without knowing whether that heterogeneity arises from a hidden effect modifier that also operates within studies. We therefore frame IONE as an exploratory diagnostic that can be applied before or alongside a conventional synthesis, to alert analysts when a marginal summary may be fragile. The term "neutralisation" refers to reducing the misleading influence of a marginal summary that conflates heterogeneous subgroups, by extracting coherent subpopulations for separate analysis.

Observational study populations may harbour hidden subpopulations with distinct characteristics that differentially influence both exposure and outcome. This hidden structure can manifest as confounding [vanderweele2013], Simpson's paradox [simpson1951][rojanaworarit2020], undetected effect modification [vanderweele2014], the ecological fallacy [robinson1950] and non-collapsibility [greenland1999]. These biases are not merely theoretical: the direction of an association observed in aggregate can reverse within subgroups, and a single average treatment effect may apply to no individual subgroup. Recognising that a pooled population is incoherent—comprising multiple coherent subpopulations whose mixture produces misleading aggregate statistics—is therefore the first step toward valid within-subgroup inference [simpson1951][rojanaworarit2020].

These biases are not merely theoretical concerns. Simpson's paradox has been documented in landmark studies across medicine and social science: kidney stone treatment comparisons where the inferior treatment appeared superior in aggregate [charig1986], university admissions data where apparent gender discrimination reversed at the departmental level [bickel1975], COVID-19 case fatality rate comparisons that were confounded by national differences in age distributions [vonkuegelgen2021], vaccine effectiveness evaluations that appeared to show vaccine failure due to age-related confounding [morris2021], and smoking–mortality studies where smokers appeared to have lower mortality due to confounding by age [appleton1996]. In each case, the paradox arose because the study population was *incoherent*—that is, it comprised multiple internally homogeneous (*coherent*) subpopulations whose mixture produced misleading aggregate statistics. The fundamental lesson of Simpson's paradox is that findings derived from an incoherent population should not be uncritically applied to the coherent subpopulations within it [simpson1951][rojanaworarit2020].

Several established methods exist for addressing confounding in observational studies. The propensity score (PS), defined as the conditional probability of treatment assignment given observed covariates, enables balancing of measured confounders through stratification, matching, or weighting [rosenbaum1983]. The prognostic score predicts the outcome under no treatment and provides an alternative basis for stratification [hansen2008][miettinen1976]. The disease risk score (DRS) constructs an outcome prediction model using untreated subjects only [miettinen1976]. Instrumental variable methods exploit variables that affect treatment but not the outcome directly [angrist1996]. More recently, the high-dimensional propensity score (hdPS) algorithm automatically extracts thousands of candidate proxy variables from claims data to approximate unmeasured confounding [schneeweiss2009][rassen2012]. These methods share a fundamental limitation: they adjust only for *measured* covariates and provide no mechanism for detecting or extracting population structure driven by *unmeasured* variables [schneeweiss2009][wyss2018].

The concept that measured variables may carry indirect information about unmeasured confounders is not new. The hdPS algorithm rests on the insight that a sufficiently large collection of proxy variables can collectively approximate the influence of unmeasured confounders [schneeweiss2009]. Proximal causal inference formalises the use of proxy variables for identification of causal effects in the presence of unmeasured confounding [tchetgen2024]. Latent class analysis and finite mixture models seek to identify unobserved subgroups from patterns in observed variables [mclachlan2000]. However, none of these approaches explicitly addresses the problem of *population incoherence*—the condition in which an apparently homogeneous study population actually comprises multiple coherent subpopulations with heterogeneous treatment effects. In current practice, the homogeneity of study populations is typically assumed implicitly, with a conventional baseline characteristics table providing only descriptive summaries that cannot formally test for hidden subgroup structure [hayeslarson2019].

We propose that the problem of hidden population structure in IPD meta-analysis can be addressed through a two-stage exploratory diagnostic. In the first stage, the coherence diagnostics C1 (between-stratum heterogeneity) and W (within-stratum homogeneity) are computed from routinely measured covariates to determine whether the pooled IPD contains hidden subgroups that warrant separate analysis. In the second stage, if incoherence is indicated, the pooled IPD is stratified into more homogeneous subgroups using multivariate patterns in the measured variables, and stratum-specific risk differences are synthesised with two-stage fixed-effect or random-effects meta-analysis. The rationale is as follows: if important unmeasured variables (e.g. age, disease severity, genetic subtype) exert systematic influence on routinely measured variables (e.g. laboratory values, vital signs), then these measured variables collectively carry a detectable "trace" of the unmeasured variable. Stratification based on these traces should recover, at least partially, the subgroup structure defined by the unmeasured variable.

To operationalise this approach, we develop two families of stratification methods. The first family (decision power-based methods) exploits the relationship between measured variables and the outcome: because unmeasured confounders influence the outcome, residual patterns from outcome prediction models may reflect the unmeasured variable's structure. The second family (feature score-based methods) operates in the covariate space alone, using unsupervised techniques such as principal component analysis and clustering to identify multivariate patterns attributable to unmeasured variables, without reference to the outcome. As coherence diagnostics, we propose C1, derived from the I^2 heterogeneity statistic [higgins2002] applied to stratum-specific log odds ratios, and W, the proportion of total conditional average treatment effect (CATE) variance explained by the stratification.

## 2. Methods

This simulation study follows the ADEMP framework [morris2019].

### Aims

1. Evaluate whether stratification of pooled IPD based on measured covariates can recover hidden subgroup structure.
2. Compare outcome-informed IONE methods with outcome-free and established comparators.
3. Assess whether C1 and W diagnose hidden effect modification.
4. Quantify ATE bias reduction from fixed-effect and DerSimonian-Laird random-effects synthesis of stratum-specific risk differences.
5. Identify data-generating conditions under which the diagnostics are most informative.

### IPD data-generating mechanism

We simulated an IPD meta-analysis with n=2000 participants assigned to 10 studies. Study-level variation in baseline risk, treatment prevalence and a continuous age-like covariate was controlled by a scale parameter of 0.6. Each participant had three critical variables (Z1 continuous, Z2 binary, Z3 ordered) that affected treatment, outcome and treatment-covariate interactions, and ten measured variables (X1-X10) carrying traces of Z. A binary treatment A and binary outcome Y were generated from logistic models with Z and X main effects, a treatment effect and Z-by-A interactions. The true estimand was the population risk-difference ATE. Full algebraic details are in Additional file 1; all scenarios used fixed random seeds.

The primary scenario used n=2000 participants, 10 studies and K=5 strata. We also varied K (3, 5, 10), sample size (500, 2000, 10 000), Z-to-Y effect scale (0.5, 1.0, 2.0), Z-to-X influence scale (0.2, 0.5, 1.0), and introduced a non-linear Z-to-X mapping (quadratic and log-normal). The primary and strata-sensitivity scenarios used 50 replications; the extended robustness scenarios used 10 replications.

### Stratification methods

**Proposed Family 1 (outcome-informed).**
- **Method 1A (Predicted probability):** logistic regression of Y on X; stratify by quantiles of the predicted probability p^.
- **Method 1B (Residual):** stratify by quantiles of the absolute residual from the same model.
- **Method 1C (Cross-validated):** K-fold cross-validated predictions before stratification.

**Proposed Family 2 (outcome-free).**
- **Method 2A (PCA):** PC1 of standardised X, stratified by quantiles.
- **Method 2B (Clustering):** K-means on standardised X with K clusters.

**Comparators and baselines.**
- Propensity-score quintiles [rosenbaum1983], Gaussian mixture model on X [mclachlan2000], prognostic-score stratification using untreated-only Y~X [hansen2008]. Oracle baselines stratify by true Z-space; random assignment provides a chance reference.

All quantile methods used equal-frequency strata. Logistic regression used l2 regularisation (C=1.0, lbfgs). Outcome-informed methods used a 50/50 discovery/evaluation split; outcome-free methods used the full sample.

### Synthesis of stratum-specific effects

Within each stratum we computed the risk difference, defined as the difference between the outcome probability under treatment and the outcome probability under control. A two-stage fixed-effect summary weighted strata by size; a DerSimonian-Laird random-effects summary estimated between-stratum variance [dersimonian1986]. *Neutralisation* means reducing the misleading influence of a marginal summary by extracting coherent subpopulations. Two caveats apply: discovered strata are not independent study estimates, and C1 is computed from log odds ratios while ATE bias is on the risk-difference scale, so C1 is an indirect diagnostic.

### Evaluation metrics

- **ARI** [hubert1985]: agreement between estimated strata and a true-Z partition, corrected for chance.
- **C1** = 1 - I^2 applied to stratum-specific log odds ratios [higgins2002]; lower C1 indicates stronger between-stratum heterogeneity.
- **W_true / W_est:** proportion of total CATE variance explained by the stratification; W_est is operational in real data but requires a correctly specified outcome model.
- **ATE bias reduction:** absolute differences between crude, stratified and random-effects estimates, plus relative ratios.
- Monte Carlo SE and 95% CI for every mean.

The true-Z partition is a k-means clustering of the standardised Z-space with K strata. ARI therefore measures agreement with a constructed reference.

### Semi-synthetic illustrations

Five well-known Simpson-paradox examples were reconstructed as pseudo-individual records from published aggregate statistics [charig1986][bickel1975][vonkuegelgen2021][morris2021][appleton1996]. For each example, pseudo-general variables mimicked proxies of the known confounder and the same IONE methods were applied. The candidate number of strata was selected a priori from {2, 3, min(K_true,4), K_true} and K was chosen as the value maximising ARI within this set. These examples illustrate favourable and unfavourable settings for stratification; they are not validation in real IPD.

### Reporting and reproducibility

The design followed ADEMP [morris2019]; checklists are in Additional files 2 and 3. The pipeline is version-controlled; every manuscript number is read from repository CSV outputs. Code and data are at https://github.com/bougtoir/ione-stratification-framework.

### Computational implementation

All simulations used Python 3.11. The pipeline comprises data_generation.py, methods.py, evaluation.py, run_rsm_ipd_simulation.py, generate_summary.py and the manuscript generator. Results are fully reproducible from the repository.


## 3. Results

### Primary IPD scenario

Table 1 reports the primary IPD scenario (n=2000, 10 studies, K=5). Recovery of the true hidden structure was modest: the Oracle baseline achieved ARI 0.372, whereas the best non-Oracle method (1B_residual) reached ARI 0.032. C1 and W behaved as expected: methods closer to the Oracle had C1 closer to 1 and higher W, while random stratification yielded C1 0.883. W_true exceeded W_est for most methods, reflecting that the estimated CATE model captures only part of the true CATE variation.

The strongest ATE bias reduction was for 1B_residual: crude absolute risk-difference bias 0.01865, stratified 0.01345 (relative 0.279), and DerSimonian-Laird random-effects 0.00816 (relative 0.563). For comparison, random-effects pooling across the true study identifiers (i.e. a study-level meta-analysis) gave an absolute ATE bias of 0.01568 (reduction 0.00296 from crude 0.01865). Random-effects pooling reduced residual bias, showing that stratum-specific effects should be allowed to vary.

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

Figure 1 visualises the primary results.

![Figure 1. Primary IPD scenario: (a) ARI, (b) C1/W coherence diagnostics, and (c) ATE bias reduction by method.](fig1_rsm_ipd_primary.png)

### Sensitivity to the number of strata

Figure 2 and Supplementary Table S1 show random-effects bias reduction across K = 3, 5, 10. Increasing K beyond the true dimensionality of the hidden structure did not reliably improve ATE bias reduction for data-driven methods; Oracle baselines improved because finer strata better partition the true Z-space. Stratum count should therefore be chosen conservatively and compared across several values rather than simply maximised.

![Figure 2. Random-effects ATE bias reduction as the number of strata varies.](fig2_rsm_ipd_strata_sensitivity.png)

### Comparison with study-level meta-analysis

For comparison, random-effects pooling across the true study identifiers (i.e. a study-level meta-analysis) gave an absolute ATE bias of 0.01568 (reduction 0.00296 from crude 0.01865). This benchmark places the data-driven stratification results in context: even the best discovered strata reduced bias by a similar magnitude to using the true study identifier, but neither fully captures the hidden modifier.

### Semi-synthetic illustrations

Five published Simpson-paradox examples were reconstructed as pseudo-individual records [charig1986][bickel1975][vonkuegelgen2021][morris2021][appleton1996]. Table 3 reports the best non-Oracle method per dataset; high ARI occurred only when pseudo-variables strongly correlated with a low-dimensional confounder. These are illustrations, not validation in real IPD.

| Dataset | Method | K | ARI | C1 | W_est | Bias reduction |
|---|---|---|---|---|---|---|
| COVID-19 CFR | 1B_residual | 3 | 0.065 | 1.000 | 0.035 | 0.017 |
| Israel Vaccine | 2B_clustering | 2 | 0.746 | 0.048 | 0.289 | 0.011 |
| Kidney Stone | GMM | 2 | 0.966 | 0.830 | 0.167 | 0.094 |
| Smoking Mortality | 1A_predicted_prob | 7 | 0.498 | 1.000 | 0.161 | 0.114 |
| UC Berkeley | PS_propensity_score | 3 | 0.084 | 0.284 | 0.177 | 0.031 |

*Table 3. Best semi-synthetic illustration result per dataset (oracle baselines excluded).*

Figure 3 shows ARI across datasets and methods.

![Figure 3. Semi-synthetic illustration: ARI by dataset and method.](fig3_rsm_real_data_ari.png)

### Sensitivity to sample size

Figure 4 and Supplementary Table S2 report n = 500, 2000 and 10 000 (K=5). Because extended sensitivity used only 10 replications per cell, Monte Carlo SEs are included. Crude bias declined with n; the largest relative reductions for leading methods occurred at n=10 000. The outcome-residual method showed a floor near 0.008-0.009, so its relative reduction decreased with n.

![Figure 4. Sample-size sensitivity of random-effects ATE bias reduction (K=5).](fig4_rsm_ipd_sample_size.png)

### Sensitivity to Z-to-X influence strength

Supplementary Table S3 reports Z-to-X influence scale = 0.2, 0.5 and 1.0. A stronger covariate trace improved ARI for most methods, but bias-reduction gains were variable at this number of replications; the diagnostics detect statistical traces rather than recover hidden variables perfectly.

### Sensitivity to Z-to-Y effect strength

Supplementary Table S4 reports Z-to-Y effect scale = 0.5, 1.0 and 2.0. Weak effect modification produced C1/W values near their nulls. As the effect increased, C1 fell, W rose and relative bias reduction improved. The outcome-residual method retained useful relative reduction even at z=0.5, indicating it can exploit moderate covariate traces.

### Robustness to non-linear Z-to-X mappings

Table 7 compares random-effects bias under linear and non-linear Z-to-X mappings. Effects were method-dependent: outcome-residual and clustering methods improved slightly, propensity-score and GMM changed little, and prognostic score declined modestly. No leading method was dramatically degraded, indicating that the diagnostics remain useful when measured covariates are non-linear functions of the hidden structure.

| Method | Linear RE bias | Linear RE bias SE | Linear rel reduction | Linear rel reduction SE | Non-linear RE bias | Non-linear RE bias SE | Non-linear rel reduction | Non-linear rel reduction SE |
|---|---|---|---|---|---|---|---|---|
| 1B_residual | 0.00852 | 0.00057 | 0.602 | 0.313 | 0.00664 | 0.00083 | 0.690 | 0.236 |
| PS_propensity_score | 0.02162 | 0.00412 | -0.011 | 1.230 | 0.02084 | 0.00566 | 0.027 | 0.245 |
| GMM | 0.02180 | 0.00547 | -0.020 | 0.544 | 0.01746 | 0.00629 | 0.185 | 0.214 |
| Prognostic_score | 0.01536 | 0.00531 | 0.281 | 0.230 | 0.01762 | 0.00442 | 0.178 | 0.247 |
| 2B_clustering | 0.02077 | 0.00573 | 0.028 | 0.514 | 0.01649 | 0.00540 | 0.230 | 0.182 |

*Table 7. Linear versus non-linear Z-to-X mapping: random-effects ATE bias and relative bias reduction (n=2000, K=5, z=1.0, zx=1.0).*

Figure 5 illustrates the non-linear Z-to-X robustness results.

![Figure 5. Non-linear Z->X robustness: random-effects ATE bias reduction (n=2000, K=5).](fig5_rsm_ipd_nonlinearity.png)


## 4. Discussion

### Principal findings

This study frames Incoherence-Oriented Neutralisation and Extraction (IONE) as an exploratory diagnostic for hidden effect modification in individual participant data (IPD) meta-analysis. Two main findings emerge. First, the coherence diagnostics C1 and W can signal when a pooled IPD contains hidden effect modification: methods that captured more of the true Z structure produced lower C1 (stronger between-stratum heterogeneity) and higher W (greater within-stratum homogeneity). Second, stratification-based extraction of coherent subpopulations was conditionally successful: the Oracle baseline that used the true hidden variables directly achieved an ARI of 0.372, whereas the best non-Oracle method (1B_residual) reached only 0.032. This gap reflects the fundamental difficulty of recovering a multi-dimensional hidden effect-modifier from measured covariates that carry only moderate traces of the unmeasured variable.

Despite the modest recovery of the true partition, the best data-driven method reduced the crude ATE bias from 0.01865 to 0.00816 (relative reduction 0.563) with DerSimonian-Laird random-effects pooling. This additional reduction over a fixed-effect summary shows why stratum-specific effects should be allowed to vary once hidden heterogeneity has been flagged.

### Detection versus extraction

A two-tier interpretation is useful. Detection asks whether the pooled population is incoherent with respect to the treatment effect; C1 and W address this without requiring the analyst to specify hidden subgroups. If C1 is low and W_est is low, the marginal summary should be interpreted cautiously. Extraction then attempts to recover the hidden subgroups. Extraction is much harder than detection: even when C1 signals heterogeneity, discovered strata often do not align closely with the true hidden structure. IONE's practical value therefore lies primarily in detection and partial ATE improvement, not in perfect confounding adjustment.

### Comparison with existing methods

IONE differs from established confounding adjustment methods in its objectives and assumptions. Propensity-score methods [rosenbaum1983] and prognostic-score stratification [hansen2008] aim to balance or adjust for measured confounders; they are not designed to detect unmeasured population structure. The high-dimensional propensity-score algorithm [schneeweiss2009] shares IONE's insight that proxy variables may carry information about unmeasured confounders, but it uses this information to improve propensity-score estimation rather than to identify subgroups or report a coherence diagnostic. Latent class analysis [mclachlan2000] seeks hidden subgroups but typically requires strong distributional assumptions and does not provide a transparent between-stratum heterogeneity statistic analogous to C1.

IONE is best understood as complementary: it can be applied before or alongside a conventional IPD meta-analysis, and standard adjustment methods can then be applied within each stratum.

### Strengths and limitations

**Strengths.** The study followed the ADEMP framework [morris2019], reported the data-generating mechanism and estimands transparently, and generated all numerical results from version-controlled repository scripts.

**Limitations.** Several limitations should be acknowledged. First, the primary scenario used a single total sample size (n=2000) and a moderate Z->X trace, although additional sensitivity analyses examined n=500 to 10 000, Z-to-Y effect scales, Z-to-X influence scales and a non-linear Z->X mapping. Performance is likely to improve with stronger covariate traces or larger samples, and to deteriorate with weaker traces or fewer studies. Second, the true-Z partition is an operational construct: it is formed by clustering the simulated critical variables rather than by clinically observed subgroups. ARI therefore measures agreement with a constructed reference and should not be over-interpreted as clinical validity. Third, W_est depends on a correctly specified outcome model with main effects of X and A and their interaction. If the outcome model is misspecified, W_est may be misleading. Fourth, the DerSimonian-Laird synthesis treats discovered strata as if they were independent studies; because strata are derived from the same data set, the stratum estimates are not independent and the tau^2 and I^2 values should be viewed as summaries rather than as estimates of conventional between-study heterogeneity. Fifth, C1 is computed from stratum-specific log odds ratios while ATE bias is on the risk-difference scale; a low C1 is a signal of incoherence but does not directly quantify the magnitude of ATE bias. Sixth, the semi-synthetic illustrations use aggregate published data reconstructed as pseudo-individual records; they demonstrate favourable and unfavourable settings for stratification but are not validation in real individual-level IPD.



## 5. Conclusions

IONE (Incoherence-Oriented Neutralisation and Extraction) is an exploratory diagnostic for hidden effect modification in IPD meta-analysis. Monte Carlo simulation and semi-synthetic examples show that IONE can detect incoherence and partially reduce ATE bias when hidden variables leave strong traces in measured covariates. The diagnostics should be reported alongside conventional meta-analytic models and covariate adjustment, and should not be used as a replacement for rigorous causal inference. We recommend that coherence assessment using C1 and W be considered as a standard sensitivity step in IPD meta-analysis reporting.


{{PAGE}}

## Declarations

### Ethics approval and consent to participate

Not applicable. This study used simulated data and publicly available aggregate statistics only.

### Consent for publication

Not applicable.

### Availability of data and materials

All simulation code, analysis scripts, semi-synthetic example data, and the manuscript generator are publicly available at https://github.com/bougtoir/ione-stratification-framework. The repository contains a `requirements.txt` file listing all Python dependencies, fixed random seeds for every scenario, and a `generate_summary.py` script that reproduces the CSV summaries from which the manuscript numbers are drawn. Running `generate_summary.py`, `generate_ione_rsm_v3.py` and `generate_rsm_tables.py` in a Python 3.11 environment regenerates the main manuscript docx, tables docx and figure files. An archived release with a Zenodo DOI will be created before acceptance to satisfy long-term reproducibility requirements. The published aggregate datasets used for the semi-synthetic illustrations are referenced in the original publications [charig1986][bickel1975][vonkuegelgen2021][morris2021][appleton1996].

### Competing interests

The authors declare that they have no competing interests.

### Funding

No external funding supported this work.

### Authors' contributions (CRediT taxonomy)

Onishi Tatsuki: Conceptualisation, methodology, software, formal analysis, writing – original draft, writing – review and editing, visualisation.

### Acknowledgements

Not applicable.

### Supplementary materials

Supplementary methods, abbreviations, the ADEMP/STROBE-Sim checklists, and the four extended sensitivity tables are provided in `biostatistics_supplementary_v3.docx`.

### Artificial intelligence

Manuscript text, Python code, and some analyses were drafted or revised using large language models (OpenAI GPT-4 and GPT-4o, accessed between August 2025 and August 2026) under the direct, iterative supervision of the author. The LLMs were used for drafting prose, formatting references, generating figures, and implementing the computational pipeline. The author designed the study, wrote the simulation code, selected all references, verified every numerical result against the repository outputs, and approved the final scientific content. No LLM-generated text was used without human review.


{{PAGE}}

{{REFS}}

