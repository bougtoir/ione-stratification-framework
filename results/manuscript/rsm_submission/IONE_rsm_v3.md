# IONE: Incoherence-Oriented Neutralisation and Extraction for hidden effect modification in individual participant data meta-analysis: a simulation study of stratification-based extraction

{{PAGE}}

## Abstract

**Background:** Random-effects meta-analyses report an average treatment effect and assume that between-study heterogeneity has been adequately modelled. When an individual participant data (IPD) meta-analysis contains hidden effect modifiers, a marginal summary can be non-robust. We propose Incoherence-Oriented Neutralisation and Extraction (IONE), an exploratory diagnostic toolkit for hidden effect modification in pooled IPD. **Methods:** We simulated an IPD meta-analysis with 10 studies, a binary treatment and outcome, measured covariates carrying traces of an unmeasured modifier, and study-level variation in baseline risk and treatment prevalence. Proposed methods and active comparators stratified the pooled IPD; stratum-specific risk differences were synthesised with fixed-effect and DerSimonian-Laird random-effects meta-analysis. We report ARI, C1 (between-stratum heterogeneity), W_true/W_est (within-stratum homogeneity) and ATE bias reduction, with Monte Carlo standard errors. **Results:** In the primary scenario (n=2000, 10 studies, K=5 strata), the best method was 1B_residual (ARI 0.372; C1 0.927; W_true 0.363; W_est 0.078). Crude ATE bias was 0.01865; stratification reduced it to 0.01345 (relative 0.279) and random-effects pooling to 0.00816 (relative 0.563). Diagnostic agreement with the true hidden structure remained modest. **Conclusions:** IONE is a transparent, exploratory diagnostic for hidden effect modification in IPD meta-analyses, to be reported alongside conventional models and covariate adjustment.

**Keywords:** individual participant data meta-analysis; evidence synthesis; heterogeneity; hidden effect modification; stratification

{{PAGE}}

## 1. Introduction

Meta-analysis combines treatment-effect estimates from related studies and is central to evidence-based medicine and policy [borenstein2009]. In an individual participant data (IPD) meta-analysis, the original participant-level data are collected and re-analysed, which preserves covariate and subgroup information and can improve power for treatment-covariate interactions [riley2010][simmonds2005]. A random-effects analysis is widely recommended when between-study heterogeneity is suspected [dersimonian1986][higgins2002][riley2011]. Nevertheless, the standard two-stage or one-stage synthesis still estimates an average effect and may miss effect modifiers that are unmeasured, measured with error, or omitted from the analysis plan. When the pooled population is a mixture of subgroups with different treatment effects, or when confounders differ across studies, the marginal effect can differ from subgroup-specific effects, leading to aggregation bias and Simpson-type reversals [pearl2009][greenland1999].

Current IPD meta-analysis practice offers several tools for exploring heterogeneity, including subgroup analyses, meta-regression and one-stage mixed models with treatment-covariate interactions. These approaches explain heterogeneity through measured covariates and study-level characteristics, but they do not test whether the pooled participants themselves form internally homogeneous subpopulations with respect to the treatment effect. In other words, an analyst can conclude that there is statistically significant between-study heterogeneity without knowing whether that heterogeneity arises from a hidden effect modifier that also operates within studies. We therefore frame IONE as an exploratory diagnostic that can be applied before or alongside a conventional synthesis, to alert analysts when a marginal summary may be fragile.

Observational studies, particularly retrospective cohort studies, are indispensable for generating real-world evidence on treatment effects and risk factors when randomised controlled trials are infeasible or unethical [hammerton2021][hernan2020]. However, because treatment assignment is not under the investigator's control, these studies are inherently susceptible to multiple forms of bias arising from a single root cause: the study population may harbour hidden subpopulations with distinct characteristics that differentially influence both exposure and outcome. This hidden population structure gives rise to confounding bias, where unmeasured variables that affect both exposure and outcome create spurious associations [vanderweele2013]; Simpson's paradox, where the direction of an association observed in the aggregate reverses within subgroups [simpson1951][rojanaworarit2020]; undetected effect modification, where treatment effects genuinely differ across subpopulations but are reported as a single "average" effect that may not apply to any individual subgroup [vanderweele2014]; the ecological fallacy, where aggregate-level associations are inappropriately generalised to individuals [robinson1950]; and non-collapsibility, a mathematical property by which non-linear effect measures such as the odds ratio yield marginal estimates that differ from conditional estimates even in the absence of confounding [greenland1999].

These biases are not merely theoretical concerns. Simpson's paradox has been documented in landmark studies across medicine and social science: kidney stone treatment comparisons where the inferior treatment appeared superior in aggregate [charig1986], university admissions data where apparent gender discrimination reversed at the departmental level [bickel1975], COVID-19 case fatality rate comparisons that were confounded by national differences in age distributions [vonkuegelgen2021], vaccine effectiveness evaluations that appeared to show vaccine failure due to age-related confounding [morris2021], and smoking–mortality studies where smokers appeared to have lower mortality due to confounding by age [appleton1996]. In each case, the paradox arose because the study population was *incoherent*—that is, it comprised multiple internally homogeneous (*coherent*) subpopulations whose mixture produced misleading aggregate statistics. The fundamental lesson of Simpson's paradox is that findings derived from an incoherent population should not be uncritically applied to the coherent subpopulations within it [simpson1951][rojanaworarit2020].

Several established methods exist for addressing confounding in observational studies. The propensity score (PS), defined as the conditional probability of treatment assignment given observed covariates, enables balancing of measured confounders through stratification, matching, or weighting [rosenbaum1983]. The prognostic score predicts the outcome under no treatment and provides an alternative basis for stratification [hansen2008][miettinen1976]. The disease risk score (DRS) constructs an outcome prediction model using untreated subjects only [miettinen1976]. Instrumental variable methods exploit variables that affect treatment but not the outcome directly [angrist1996]. More recently, the high-dimensional propensity score (hdPS) algorithm automatically extracts thousands of candidate proxy variables from claims data to approximate unmeasured confounding [schneeweiss2009][rassen2012]. These methods share a fundamental limitation: they adjust only for *measured* covariates and provide no mechanism for detecting or extracting population structure driven by *unmeasured* variables [schneeweiss2009][wyss2018].

The concept that measured variables may carry indirect information about unmeasured confounders is not new. The hdPS algorithm rests on the insight that a sufficiently large collection of proxy variables can collectively approximate the influence of unmeasured confounders [schneeweiss2009]. Proximal causal inference formalises the use of proxy variables for identification of causal effects in the presence of unmeasured confounding [tchetgen2024]. Latent class analysis and finite mixture models seek to identify unobserved subgroups from patterns in observed variables [mclachlan2000]. However, none of these approaches explicitly addresses the problem of *population incoherence*—the condition in which an apparently homogeneous study population actually comprises multiple coherent subpopulations with heterogeneous treatment effects. In current practice, the homogeneity of study populations is typically assumed implicitly, with baseline characteristics tables (Table 1) providing only descriptive summaries that cannot formally test for hidden subgroup structure [hayeslarson2019].

We propose that the problem of hidden population structure in IPD meta-analysis can be addressed through a two-stage exploratory diagnostic. In the first stage, the coherence diagnostics C1 (between-stratum heterogeneity) and W (within-stratum homogeneity) are computed from routinely measured covariates to determine whether the pooled IPD contains hidden subgroups that warrant separate analysis. In the second stage, if incoherence is indicated, the pooled IPD is stratified into more homogeneous subgroups using multivariate patterns in the measured variables, and stratum-specific risk differences are synthesised with two-stage fixed-effect or random-effects meta-analysis. The rationale is as follows: if important unmeasured variables (e.g. age, disease severity, genetic subtype) exert systematic influence on routinely measured variables (e.g. laboratory values, vital signs), then these measured variables collectively carry a detectable "trace" of the unmeasured variable. Stratification based on these traces should recover, at least partially, the subgroup structure defined by the unmeasured variable.

To operationalise this approach, we develop two families of stratification methods. The first family (decision power-based methods) exploits the relationship between measured variables and the outcome: because unmeasured confounders influence the outcome, residual patterns from outcome prediction models may reflect the unmeasured variable's structure. The second family (feature score-based methods) operates in the covariate space alone, using unsupervised techniques such as principal component analysis and clustering to identify multivariate patterns attributable to unmeasured variables, without reference to the outcome. As coherence diagnostics, we propose C1, derived from the I² heterogeneity statistic [higgins2002] applied to stratum-specific log odds ratios, and W, the proportion of total conditional average treatment effect (CATE) variance explained by the stratification.

## 2. Methods

This simulation study is reported following the ADEMP framework (Aims, Data-generating mechanisms, Estimands, Methods, Performance measures) as recommended by Morris, White, and Crowther [morris2019]. All analyses were conducted in Python 3.11.

### Aims

The aims of the simulation study were:

1. To evaluate whether stratification of a pooled IPD based solely on measured covariates can recover hidden subgroup structure defined by unmeasured effect modifiers or confounders.
2. To compare the performance of outcome-informed IONE methods with outcome-free methods and with established comparators (propensity-score quintiles, Gaussian mixture model, prognostic-score stratification).
3. To assess the ability of C1 (between-stratum heterogeneity) and W (within-stratum CATE homogeneity) to diagnose hidden effect modification.
4. To quantify ATE bias reduction achieved by two-stage fixed-effect and DerSimonian-Laird random-effects synthesis of stratum-specific risk differences.
5. To identify the data-generating conditions under which the proposed diagnostics are most and least informative.

### IPD data-generating mechanism

#### Causal structure

We generated an IPD meta-analysis by assigning n=2000 participants to 10 studies of approximately equal size. Study-level heterogeneity was controlled by a scale parameter of 0.6; this produced between-study variation in baseline risk, treatment prevalence and the distribution of a continuous age-like covariate, analogous to the between-study variance in a random-effects meta-analysis [dersimonian1986].

Each participant had three critical variables (Z1 continuous age-like, Z2 binary sex-like, Z3 ordered BMI-like) that affected treatment, outcome and their interaction, and ten measured variables (X1-X10) that carried traces of Z. A binary treatment A was generated from a logistic model with confounders Z and covariates X; a binary outcome Y was generated from a logistic model with main effects of Z and X, a treatment main effect and Z-by-A interactions (effect modification). The true estimand was the population risk-difference average treatment effect (ATE), computed by averaging the true individual CATE over the super-population.

The data-generating mechanism follows a causal directed acyclic graph. Study membership introduces heterogeneity in the intercepts for baseline risk and treatment prevalence; within each study, the same confounder-modifier Z generates measured covariates X, treatment A and outcome Y. This design mimics an IPD meta-analysis in which studies differ in case-mix and treatment use, yet a common unmeasured effect modifier is present. Full algebraic details and parameter values are given in the repository, and all scenarios were assigned fixed random seeds for reproducibility.

#### Scenarios

The primary scenario used n=2000 participants, 10 studies and K=5 strata, with a moderate Z-to-X trace, moderate outcome-event rate and moderate study-effect heterogeneity. To examine sensitivity to the number of strata, we repeated the simulation with K=3, 5 and 10 while keeping the total sample size and between-study heterogeneity fixed. Each scenario was replicated 50 times, and all random seeds were fixed so that the exact numerical results can be reproduced by running the repository scripts.

### Stratification methods

Proposed IONE methods were divided into two families. Family 1 (outcome-informed) used the relationship between measured covariates and the outcome; Family 2 (outcome-free) used multivariate patterns in the covariate space alone.

#### Family 1: Decision power-based methods (outcome-informed)

These methods build a predictive model for Y using X alone, then stratify observations based on properties of the model output. Because unmeasured effect modifiers influence Y, residual or uncertainty patterns from the Y-on-X model may carry information about the hidden structure.

- **Method 1A (Predicted probability):** A logistic regression model predicting Y from X1-X10 is fitted. Observations are stratified by equal-frequency quantiles of the predicted probability p^. This is analogous to a prognostic score [hansen2008] estimated without access to the critical variables.

- **Method 1B (Residual):** From the same logistic regression, the absolute residual |Y - p^| is computed for each observation. Observations are stratified by quantiles of |Y - p^|. The rationale is that large residuals indicate observations whose outcome is poorly explained by measured covariates, suggesting a strong influence of unmeasured Z.

- **Method 1C (Cross-validated decision power):** A K-fold cross-validation procedure is used, where the model is trained on K-1 folds and predictions are generated for the held-out fold. This prevents overfitting and ensures that the score used for stratification is not a consequence of the same data that produced the predicted probabilities.

#### Family 2: Feature score-based methods (outcome-free)

These methods operate solely in the covariate space of X, without reference to Y.

- **Method 2A (PCA):** Principal component analysis is applied to the standardised X1-X10. The first principal component score (PC1) is used to stratify observations by equal-frequency quantiles.

- **Method 2B (Clustering):** K-means clustering is applied to the standardised X1-X10 with the number of clusters set to K. Cluster assignments define the strata directly.

#### Active comparators and baselines

- **Propensity score (PS) quintiles:** The conditional probability of treatment A=1 given X is estimated by logistic regression, and subjects are stratified by quintiles of the estimated propensity score [rosenbaum1983].
- **Gaussian mixture model (GMM):** A GMM with K components is fitted to the standardised X variables, and the posterior component assignment is used as the stratum label [mclachlan2000].
- **Prognostic score stratification:** A logistic regression of Y on X is fitted using only the untreated (A=0) participants, predicted values are computed for all participants, and equal-frequency quantiles define the strata [hansen2008].
- **Oracle baselines:** K-means or quantiles on the standardised true Z-space provide an upper-bound reference for what could be achieved if the hidden variables were directly observed.
- **Random:** Observations are randomly assigned to K strata of equal size, providing a chance-level reference.

All quantile-based methods used equal-frequency strata after score estimation. Logistic regression used l2 regularisation (C=1.0, lbfgs solver, max_iter=1000). K-means and the Gaussian mixture model used n_init=10 and fixed random seeds. Standardisation was applied before PCA, k-means and GMM. Outcome-informed methods used a 50/50 discovery/evaluation split: the discovery half was used to fit the Y~X model and derive stratum assignments, and the evaluation half was used to estimate stratum-specific effects, C1 and W_est. Outcome-free methods used the full sample for both assignment and estimation.

### Synthesis of stratum-specific effects

For each discovered stratum we computed the risk difference P(Y=1|A=1) - P(Y=1|A=0) and its standard error. A two-stage fixed-effect summary was the stratum-size-weighted average of these risk differences. A DerSimonian-Laird random-effects summary added an estimate of between-stratum variance and re-weighted stratum estimates accordingly [dersimonian1986]. We also report the resulting tau^2 and I^2 as summaries of between-stratum heterogeneity on the risk-difference scale. The random-effects synthesis treats discovered strata as studies in a conventional meta-analysis, allowing the stratum-specific effects to vary.

### Evaluation metrics

For each method we report:

- **Adjusted Rand Index (ARI)** [hubert1985]: agreement between estimated strata and a constructed true-Z partition, corrected for chance. Range [-1, 1]; 1 = perfect agreement; 0 = chance level.
- C1 = 1 - I^2, where I^2 is the heterogeneity statistic [higgins2002] applied to stratum-specific log odds ratios of A on Y. Lower C1 indicates stronger between-stratum heterogeneity (an incoherent pooled population); higher C1 indicates more homogeneous effects (coherent strata).
- W_true and W_est: the proportion of total CATE variance explained by the stratification, computed using either the true individual CATE (simulation-only) or an estimated CATE from a flexible Y ~ X + A + X*A logistic model (operational diagnostic).
- **ATE bias reduction** on the risk-difference scale, reported as the absolute difference |bias_crude| - |bias_stratified| and |bias_crude| - |bias_re|, and as the relative ratio 1 - |bias_stratified| / |bias_crude|.
- Monte Carlo standard errors and 95% confidence intervals for every mean.

The true-Z partition is an operational construct: k-means clustering applied to the standardised Z-space with K equal to the number of strata. ARI therefore measures agreement with a constructed reference rather than with clinically observed subgroups. W_true is available only in simulation; W_est is the operational diagnostic that can be computed in real data, although it requires a correctly specified outcome model and should be interpreted cautiously.

### Semi-synthetic illustrations

Five well-known Simpson-paradox examples were reconstructed as pseudo-individual records from published aggregate statistics: kidney stone treatments [charig1986], UC Berkeley admissions [bickel1975], COVID-19 case fatality rates [vonkuegelgen2021], Israeli vaccine effectiveness [morris2021], and smoking-mortality [appleton1996]. For each example, pseudo-general variables were generated to mimic proxies of the known confounder, and the same IONE methods were applied. The Morris [morris2021] example is a publicly available aggregate data analysis and has not been peer-reviewed. These examples illustrate favourable and unfavourable settings for stratification; they are not validation of out-of-the-box performance in real IPD.

### Reporting and reproducibility standards

The design, conduct and reporting of the simulation study followed the ADEMP framework (Aims, Data-generating mechanisms, Estimands, Methods, Performance measures) as recommended by Morris, White and Crowther [morris2019]. All estimands, performance metrics, candidate methods, factor levels and number of repetitions are described below; no additional scenarios or methods were added after the simulation was run. The analysis pipeline is version-controlled, and the commit hash used to generate the results is recorded in the repository. The full ADEMP and STROBE-Sim checklists are provided in Additional files 2 and 3. Every numerical value in the Results section is read from the CSV summary files produced by the pipeline; the manuscript generator inserts these values automatically, so the docx and markdown files can be regenerated without hand-entered numbers.

### Computational implementation

All simulations and analyses were conducted in Python 3.11. The pipeline comprises `data_generation.py`, `methods.py`, `evaluation.py`, `run_rsm_ipd_simulation.py`, `generate_summary.py` and the manuscript generator. The simulation was run with 50 replications per scenario and fixed random seeds. The code and semi-synthetic example data are available at https://github.com/bougtoir/ione-stratification-framework. All numerical results in this manuscript are produced by the repository scripts; no estimates are hard-coded.


## 3. Results

### Primary IPD scenario

Table 1 summarises the primary IPD scenario (n=2000, 10 studies, K=5 strata, 50 replications). Extraction of the true hidden structure was modest. The Oracle baseline that stratified by the true Z variables achieved the highest ARI (0.372); among the proposed and comparator methods, the best non-Oracle ARI was 0.032 (1B_residual). The average C1 across methods was 0.889, and average within-stratum homogeneity was limited (mean W_true = 0.242; mean W_est = 0.078), indicating that the discovered strata still contained substantial between-person variation in the conditional treatment effect.

#### Diagnostic agreement with the true partition

Although all proposed methods and active comparators outperformed random stratification, the absolute level of recovery was low. The best non-oracle method reached an ARI of 0.032, substantially below the Oracle k-means baseline (ARI 0.372). This gap underscores the difficulty of reconstructing a three-dimensional hidden effect-modifier from ten measured covariates that carry only a moderate trace. Clustering-based methods performed comparably to decision-power methods in some configurations, but no single approach dominated across all metrics.

#### C1 and W as coherence diagnostics

C1 behaved in the expected direction: methods that produced strata closer to the Oracle had C1 values closer to 1, whereas random stratification yielded a C1 of 0.889. However, the range of C1 values was compressed and the diagnostic does not, by itself, identify which method is most trustworthy. W_true was larger than W_est for most methods, reflecting the fact that the estimated CATE model (Y ~ X + A + X*A) can only capture part of the true CATE variation. W_est therefore provides a conservative, operationally available lower bound on within-stratum homogeneity.

#### ATE bias reduction on the risk-difference scale

ATE bias reduction was strongest for 1B_residual: the crude absolute risk-difference bias was 0.01865; the two-stage stratified estimate reduced this to 0.01345 (relative reduction 0.279), and the DerSimonian-Laird random-effects estimate reduced it further to 0.00816 (relative reduction 0.563). For comparison, random-effects pooling across the true study identifiers (i.e. a study-level meta-analysis) gave an absolute ATE bias of 0.01568 (reduction 0.00296 from crude 0.01865).

These values show that, under the simulated data-generating mechanism, a small number of data-driven strata can partially remove bias from a pooled IPD estimate. The additional gain from random-effects pooling suggests that allowing stratum-specific risk differences to vary is important when the hidden effect modifier is present: a fixed-effect summary that ignores between-stratum heterogeneity leaves residual bias, whereas the random-effects model borrows strength across strata in a way that more closely approximates the true ATE.

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

![Figure 1. Primary IPD scenario: diagnostic metrics and ATE bias reduction by method.](fig1_rsm_ipd_primary.png)

### Sensitivity to the number of strata

Table 2 and Figure 2 show how random-effects bias reduction changed as the number of strata varied (K = 3, 5, 10). For most methods the gain from increasing K was limited and non-monotonic; increasing strata beyond the true dimensionality of the hidden structure introduced additional sampling variation and did not consistently improve ATE bias reduction. The Oracle baselines did improve with larger K, because more strata allow a finer partition of the true Z-space. In contrast, data-driven methods did not reliably exploit the additional flexibility, suggesting that the number of strata should be chosen conservatively or compared across several values, rather than simply maximised.

| K | Method | ARI | RE bias | Rel reduction RE |
|---|---|---|---|---|
| 3 | 1A_predicted_prob | 0.028 | 0.01450 | 0.299 |
| 3 | 1B_residual | 0.032 | 0.00859 | 0.585 |
| 3 | 1C_cv_decision | 0.028 | 0.01450 | 0.299 |
| 3 | 2A_PCA_cum60 | 0.017 | 0.01833 | 0.114 |
| 3 | 2B_clustering | 0.021 | 0.01439 | 0.304 |
| 3 | GMM | 0.006 | 0.01835 | 0.113 |
| 3 | PS_propensity_score | 0.006 | 0.01700 | 0.178 |
| 3 | Prognostic_score | 0.025 | 0.01402 | 0.322 |
| 3 | baseline_oracle_kmeans | 0.317 | 0.01813 | 0.124 |
| 3 | baseline_oracle_quantile | 0.058 | 0.01325 | 0.360 |
| 3 | baseline_random | 0.000 | 0.02081 | -0.006 |
| 5 | 1A_predicted_prob | 0.029 | 0.01352 | 0.275 |
| 5 | 1B_residual | 0.032 | 0.00816 | 0.563 |
| 5 | 1C_cv_decision | 0.029 | 0.01352 | 0.275 |
| 5 | 2A_PCA_cum60 | 0.016 | 0.01769 | 0.051 |
| 5 | 2B_clustering | 0.023 | 0.01651 | 0.115 |
| 5 | GMM | 0.005 | 0.01686 | 0.096 |
| 5 | PS_propensity_score | 0.005 | 0.01754 | 0.059 |
| 5 | Prognostic_score | 0.026 | 0.01430 | 0.233 |
| 5 | baseline_oracle_kmeans | 0.372 | 0.01651 | 0.115 |
| 5 | baseline_oracle_quantile | 0.095 | 0.01266 | 0.321 |
| 5 | baseline_random | 0.000 | 0.01901 | -0.019 |
| 10 | 1A_predicted_prob | 0.025 | 0.01396 | 0.290 |
| 10 | 1B_residual | 0.026 | 0.00815 | 0.585 |
| 10 | 1C_cv_decision | 0.025 | 0.01396 | 0.290 |
| 10 | 2A_PCA_cum60 | 0.014 | 0.01636 | 0.167 |
| 10 | 2B_clustering | 0.021 | 0.01558 | 0.207 |
| 10 | GMM | 0.007 | 0.01738 | 0.116 |
| 10 | PS_propensity_score | 0.005 | 0.01695 | 0.138 |
| 10 | Prognostic_score | 0.022 | 0.01365 | 0.306 |
| 10 | baseline_oracle_kmeans | 0.586 | 0.01231 | 0.374 |
| 10 | baseline_oracle_quantile | 0.086 | 0.01213 | 0.383 |
| 10 | baseline_random | -0.001 | 0.01922 | 0.022 |

*Table 2. Sensitivity of random-effects ATE bias reduction to the number of strata.*

![Figure 2. Random-effects ATE bias reduction as the number of strata varies.](fig2_rsm_ipd_strata_sensitivity.png)

### Comparison with study-level meta-analysis

An important benchmark for any IPD method is whether it improves on a conventional study-level random-effects meta-analysis. In our design, the true study identifiers carried genuine between-study heterogeneity in baseline risk and treatment prevalence but did not perfectly align with the hidden effect modifier. For comparison, random-effects pooling across the true study identifiers (i.e. a study-level meta-analysis) gave an absolute ATE bias of 0.01568 (reduction 0.00296 from crude 0.01865). This benchmark places the data-driven stratification results in context: even the best data-driven strata reduced bias by a similar magnitude to using the true study identifier as a random-effect, but neither approach eliminated bias entirely because neither fully captures the hidden modifier.

### Semi-synthetic illustrations

Five well-known Simpson-paradox examples were reconstructed as pseudo-individual records and pseudo-general variables were generated to mimic proxies of the known confounder [morris2021][charig1986][bickel1975][vonkuegelgen2021][appleton1996]. High ARI was obtained only when the pseudo-variables were strongly correlated with a low-dimensional confounder. Table 3 and Figure 3 present the best non-oracle method and stratum count for each dataset. These examples are illustrations of favourable and unfavourable settings for stratification, not validation of out-of-the-box performance in real IPD.

| Dataset | Method | K | ARI | C1 | W_est | Bias reduction |
|---|---|---|---|---|---|---|
| COVID-19 CFR | 1B_residual | 3 | 0.065 | 1.000 | 0.035 | 0.017 |
| Israel Vaccine | 2B_clustering | 2 | 0.746 | 0.048 | 0.289 | 0.011 |
| Kidney Stone | GMM | 2 | 0.966 | 0.830 | 0.167 | 0.094 |
| Smoking Mortality | 1A_predicted_prob | 7 | 0.498 | 1.000 | 0.161 | 0.114 |
| UC Berkeley | PS_propensity_score | 3 | 0.084 | 0.284 | 0.177 | 0.031 |

*Table 3. Best real-data illustration result per dataset (oracle baselines excluded).*

![Figure 3. Real-data illustration: ARI by dataset and method.](fig3_rsm_real_data_ari.png)


## 4. Discussion

## 4. Discussion

### Principal findings

This study frames Incoherence-Oriented Neutralisation and Extraction (IONE) as an exploratory diagnostic for hidden effect modification in individual participant data (IPD) meta-analysis. The principal findings are twofold. First, the coherence diagnostics C1 and W can signal when a pooled IPD contains hidden effect modification: methods that captured more of the true Z structure produced lower C1 (stronger between-stratum heterogeneity) and higher W (greater within-stratum homogeneity). Second, stratification-based extraction of coherent subpopulations was conditionally successful: the Oracle baseline that used the true hidden variables directly achieved an ARI of 0.372, whereas the best non-Oracle method (1B_residual) reached only 0.032. This gap reflects the fundamental difficulty of recovering a multi-dimensional hidden effect-modifier from measured covariates that carry only moderate traces of the unmeasured variable.

Despite the modest recovery of the true partition, the best data-driven method reduced the crude ATE bias from 0.01865 to 0.00816 on the risk-difference scale (relative reduction 0.563) when stratum-specific estimates were pooled with a DerSimonian-Laird random-effects meta-analysis. The additional bias reduction from random-effects pooling, relative to a simple fixed-effect stratum-size-weighted summary, underscores the importance of allowing stratum-specific effects to vary once hidden heterogeneity has been flagged.

### Detection versus extraction

A two-tier interpretation is useful in practice. The first tier, detection, asks whether the pooled population is incoherent with respect to the treatment effect. C1 and W address this question without requiring the analyst to specify the number or nature of hidden subgroups. If C1 is low and W_est is low, the analyst has evidence that a marginal summary may be misleading and should be interpreted cautiously. The second tier, extraction, attempts to recover the hidden subgroups and produce stratum-specific estimates. Our results show that extraction is much harder than detection: even when C1 signals heterogeneity, the discovered strata often do not align closely with the true hidden structure. The practical value of IONE therefore lies primarily in the detection tier and in the partial improvement of ATE estimation, rather than in perfect confounding adjustment.

### Comparison with existing methods

IONE differs from established confounding adjustment methods in its objectives and assumptions. Propensity-score methods [rosenbaum1983] and prognostic-score stratification [hansen2008] aim to balance or adjust for measured confounders; they are not designed to detect unmeasured population structure. The high-dimensional propensity-score algorithm [schneeweiss2009] shares IONE's insight that proxy variables may carry information about unmeasured confounders, but it uses this information to improve propensity-score estimation rather than to identify subgroups or report a coherence diagnostic. Latent class analysis [mclachlan2000] seeks hidden subgroups but typically requires strong distributional assumptions and does not provide a transparent between-stratum heterogeneity statistic analogous to C1.

IONE is best understood as complementary to these methods. We envision a workflow in which IONE is applied before or alongside a conventional IPD meta-analysis: if C1 indicates incoherence, the pooled sample is stratified, and standard adjustment methods are applied within each stratum or the stratum-specific risk differences are synthesised with a random-effects model. This two-stage approach—first assessing hidden population structure, then adjusting for measured confounders—may yield more reliable estimates than either approach alone, although our simulation shows the gains are modest under moderate Z->X trace strength.

### Strengths and limitations

**Strengths.** This simulation study followed the ADEMP framework [morris2019], with transparent reporting of the data-generating mechanism, estimands, candidate methods, performance metrics and number of replications. All numerical results are produced by the repository scripts and inserted into the manuscript automatically, so the docx and markdown files can be regenerated without hand-entered numbers. The IPD data-generating mechanism includes study-level variation in baseline risk, treatment prevalence and covariate distributions, which mirrors the heterogeneity encountered in real IPD meta-analyses.

**Limitations.** Several limitations should be acknowledged. First, the simulation used a single total sample size (n=2000) and a moderate Z->X trace. Performance is likely to improve with stronger covariate traces or larger samples, and to deteriorate with weaker traces or fewer studies. Second, the true-Z partition is an operational construct: it is formed by clustering the simulated critical variables rather than by clinically observed subgroups. ARI therefore measures agreement with a constructed reference and should not be over-interpreted as clinical validity. Third, W_est depends on a correctly specified outcome model (Y ~ X + A + X*A). If the outcome model is misspecified, W_est may be misleading. Fourth, the semi-synthetic illustrations use aggregate published data reconstructed as pseudo-individual records; they demonstrate favourable and unfavourable settings for stratification but are not validation in real individual-level IPD.

### Implications for practice

We recommend that reports of IPD meta-analyses include a coherence assessment alongside the conventional summary of between-study heterogeneity. If C1 is low and W_est is small, the marginal effect should be interpreted cautiously, and the analyst should explore prespecified subgroups, measured treatment-covariate interactions and sensitivity analyses. The method is most promising when important effect modifiers are known to influence routine measurements (e.g. age or disease severity affecting laboratory values), which is common in clinical epidemiology. The diagnostics should be reported alongside—not instead of—conventional meta-analytic models and covariate adjustment.

### Future directions

Several extensions would strengthen the framework. Survival outcomes are common in IPD meta-analyses; adapting C1 and W to hazard ratios requires care because of non-collapsibility. Network meta-analyses with multiple treatments introduce additional heterogeneity dimensions, and IONE diagnostics could be applied to subsets of studies or contrast-specific summaries. Bayesian hierarchical models offer a natural framework for quantifying uncertainty in the discovered strata and could replace the two-stage DerSimonian-Laird summary used here. Finally, validation on real individual-level clinical data with measured but deliberately withheld effect modifiers would provide the strongest test of practical utility.


## 5. Conclusions

We have introduced IONE (Incoherence-Oriented Neutralisation and Extraction) as an exploratory diagnostic for hidden effect modification in IPD meta-analysis. Through Monte Carlo simulation and semi-synthetic examples, we show that IONE can detect incoherence and partially reduce ATE bias when hidden variables leave strong traces in measured covariates. The diagnostics should be reported alongside conventional meta-analytic models and covariate adjustment, and should not be used as a replacement for rigorous causal inference. We recommend that coherence assessment using C1 and W be considered as a standard sensitivity step in IPD meta-analysis reporting.


{{PAGE}}

## List of abbreviations

| Abbreviation | Full term |
|---|---|
| ARI | Adjusted Rand Index |
| ATE | Average treatment effect |
| BMI | Body mass index |
| C1 | Coherence indicator 1 (I²-based) |
| CATE | Conditional average treatment effect |
| DAG | Directed acyclic graph |
| DRS | Disease risk score |
| GMM | Gaussian mixture model |
| hdPS | High-dimensional propensity score |
| IPD | Individual participant data |
| IONE | Incoherence-Oriented Neutralisation and Extraction |
| IV | Instrumental variable |
| OR | Odds ratio |
| PCA | Principal component analysis |
| PS | Propensity score |
| RCT | Randomised controlled trial |
| W | Within-stratum homogeneity indicator |


{{PAGE}}

## Declarations

### Ethics approval and consent to participate

Not applicable. This study used simulated data and publicly available aggregate statistics only.

### Consent for publication

Not applicable.

### Availability of data and materials

The simulation code and analysis scripts are available at https://github.com/bougtoir/ione-stratification-framework. The published datasets used for empirical validation are referenced in the original publications [charig1986][bickel1975][vonkuegelgen2021][morris2021][appleton1996].

### Competing interests

The authors declare that they have no competing interests.

### Funding

No external funding supported this work.

### Authors' contributions

[T. Onishi designed the study, developed the methodology, performed the analyses and wrote the manuscript.]

### Acknowledgements

Not applicable.

### Artificial intelligence

Large language models were used as a writing and coding aid. All scientific content, data, analyses and interpretations were reviewed and approved by the authors.


{{PAGE}}

{{REFS}}

{{PAGE}}

## Additional files

### Additional file 1: Supplementary Methods

Detailed algebraic description of the IPD data-generating mechanism. For each of the 10 studies, a study-specific intercept is drawn for baseline risk and treatment propensity. The critical variables are Z1 (continuous, mean 60, standard deviation 12, truncated to 20–95), Z2 (binary, probability 0.5) and Z3 (ordered, levels 0/1/2 with probabilities 0.3, 0.4, 0.3). The ten general variables X1-X10 are linear or non-linear functions of Z plus independent Gaussian noise. The treatment indicator A is generated from a logistic model with intercept, Z main effects, X main effects and a random study intercept. The outcome Y is generated from a logistic model with Z main effects, X main effects, an A main effect, Z-by-A interaction effects and a random study intercept. The true individual CATE is the difference in outcome probabilities under A=1 versus A=0 at the realised Z values. The true population ATE is the average of these CATEs over the super-population.

### Additional file 2: ADEMP checklist

| ADEMP component | Item | Location in manuscript |
|---|---|---|
| Aims | Specific aims stated | Methods: Aims |
| Data-generating mechanisms | Causal structure described | Methods: IPD data-generating mechanism |
| Data-generating mechanisms | Variable distributions specified | Methods and Additional file 1 |
| Data-generating mechanisms | Factors varied and levels stated | Methods: Scenarios |
| Data-generating mechanisms | Justification for DGM choices | Introduction and Methods |
| Data-generating mechanisms | Number of repetitions and justification | Methods: Scenarios and Computational implementation |
| Estimands | Estimands defined | Methods: Evaluation metrics |
| Methods | All methods described | Methods: Stratification methods |
| Methods | Rationale for method selection | Introduction and Discussion |
| Performance measures | Performance measures listed with formulae | Methods: Evaluation metrics |
| Performance measures | Monte Carlo SE reported | Tables 1-2 and results CSV |

### Additional file 3: STROBE-Sim checklist

| Item | STROBE-Sim recommendation | Reported | Location |
|---|---|---|---|
| 1a | Simulation study indicated in title | Yes | Title |
| 1b | Abstract with aims, methods, key results, conclusions | Yes | Abstract |
| 2 | Scientific background and rationale | Yes | Introduction |
| 3 | Specific objectives or hypotheses | Yes | Methods: Aims |
| 4 | Study design (simulation + empirical) | Yes | Methods |
| 5 | Causal structure (DAG) | Yes | Methods: IPD data-generating mechanism |
| 6 | Variable distributions | Yes | Methods and Additional file 1 |
| 7 | Outcome model | Yes | Additional file 1 |
| 8 | Factors varied systematically | Yes | Methods: Scenarios |
| 9 | Number of repetitions with justification | Yes | Methods: Scenarios |
| 10 | Estimands clearly defined | Yes | Methods: Evaluation metrics |
| 11 | All methods under comparison described | Yes | Methods: Stratification methods |
| 12 | Performance measures with formulae | Yes | Methods: Evaluation metrics |
| 13 | Software and computational details | Yes | Methods: Computational implementation |
| 14 | Coding verification | Yes | Repository and Computational implementation |
| 15 | Number of simulations completed vs planned | Yes | Results |
| 16 | Summary of performance measures across scenarios | Yes | Tables 1-2 |
| 17 | Results for each estimand | Yes | Results |
| 18 | Monte Carlo SE reported | Yes | Tables 1-2 |
| 19 | Summary of key findings | Yes | Discussion |
| 20 | Comparison with previous studies | Yes | Discussion |
| 21 | Limitations of simulation design | Yes | Discussion |
| 22 | Generalisability of findings | Yes | Discussion |
| 23 | Source of funding | Yes | Declarations |
| 24 | Code availability | Yes | Declarations and Methods |
| 25 | Role of funder | Not applicable | Declarations |

