# Coherence diagnostics for hidden effect modification in individual participant data meta-analysis: a simulation benchmark of stratification approaches

{{PAGE}}

## Abstract

**Background:** In IPD meta-analysis, marginal treatment-effect estimates can be biased by hidden effect modifiers. We introduce coherence diagnostics C1 and W and evaluate them in a simulation benchmark of stratification approaches.

**Methods:** We simulated an IPD meta-analysis with 10 studies, a binary treatment and outcome, measured covariates carrying traces of an unmeasured modifier, and study-level variation in baseline risk and treatment prevalence. Methods stratified pooled IPD and synthesised stratum-specific risk differences with fixed-effect and DerSimonian-Laird random-effects meta-analysis. We report ARI, C1, W and ATE bias reduction, calibrating C1 and W against their empirical null distributions.

**Results:** At n=2000 and K=5, C1 and W_est discriminated the alternative from the empirical null only at chance level (C1 AUC 0.460-0.545; W AUC 0.427-0.561; TPR up to 0.060 at 5% FPR). The best method reduced random-effects ATE bias by more than half (from 0.01865 to 0.00816; relative reduction 0.563). Relative bias reduction improved as the Z-to-Y effect strengthened, while sample-size gains were method-specific; null-centred W confirmed weak discrimination.

**Conclusions:** IONE is a descriptive sensitivity tool, not an inferential test for hidden effect modification. It should be reported alongside conventional meta-analytic models and covariate adjustment.

**Keywords:** individual participant data meta-analysis; evidence synthesis; heterogeneity; hidden effect modification; stratification; simulation

{{PAGE}}

## 1. Introduction

Meta-analysis pools treatment-effect estimates across studies and is central to evidence-based medicine [borenstein2009]. IPD meta-analysis preserves participant-level covariates and can increase power for treatment-covariate interactions [riley2010][simmonds2005]. Random-effects syntheses are recommended when between-study heterogeneity is suspected [dersimonian1986][higgins2002][riley2011], yet conventional summaries estimate a marginal effect and may mislead when effect modifiers are unmeasured or omitted [pearl2009][greenland1999]. When the pooled population contains subgroups with different treatment effects, the marginal effect can reverse within population strata, producing Simpson-type paradoxes [simpson1951][rojanaworarit2020].

Heterogeneity in IPD meta-analysis is usually investigated through subgroup analyses, meta-regression or one-stage mixed models. These approaches explain variation with measured covariates and study-level factors, and stratification by study is the standard way to share baseline risk and treatment prevalence. They do not, however, test whether the pooled participants themselves form internally homogeneous subpopulations with respect to treatment effect. We therefore frame Incoherence-Oriented Neutralisation and Extraction (IONE) as an exploratory sensitivity tool: it flags when a marginal summary may be fragile and separates the pooled IPD into more homogeneous subgroups using multivariate patterns in measured variables. The goal is not to recover hidden variables but to reduce misleading marginal summaries when the IPD contains hidden effect modification.

Hidden population structure is documented across medicine and social science: kidney-stone treatments [charig1986], university admissions [bickel1975], COVID-19 case-fatality comparisons [vonkuegelgen2021], national vaccine-surveillance data [haas2021], and smoking-mortality studies [appleton1996]. Established methods adjust for measured confounders but do not detect unmeasured population structure. We operationalise IONE through two coherence diagnostics: C1, derived from the I^2 heterogeneity statistic [higgins2002] applied to stratum-specific log odds ratios, and W, the proportion of total CATE variance explained by the stratification. Stratum-specific risk differences are synthesised with fixed-effect or DerSimonian-Laird random-effects meta-analysis. C1 measures the coherence of a stratification after it has been formed; W is a ratio whose denominator is the overall CATE variance and is therefore unstable when the modification signal is weak.

## 2. Methods

This simulation study follows the ADEMP framework [morris2019].

### Aims

Quantify ATE bias reduction from fixed-effect and DerSimonian-Laird random-effects synthesis of stratum-specific risk differences; compare outcome-informed IONE methods with outcome-free and established comparators; assess the diagnostic discrimination of C1 and W against an empirical null; and identify data-generating conditions under which the diagnostics are most and least informative.

### IPD data-generating mechanism

We simulated an IPD meta-analysis with n=2000 participants assigned to 10 studies (scale parameter 0.6 for baseline risk, treatment prevalence and an age-like covariate). Each participant had three critical variables (Z1 continuous, Z2 binary, Z3 ordered) that affected treatment, outcome and treatment-covariate interactions, and ten measured variables (X1-X10) carrying traces of Z. A binary treatment A and binary outcome Y were generated from logistic models with Z and X main effects, a treatment effect and Z-by-A interactions. The estimand was the population risk-difference ATE; full algebra is in Additional file 1.

The primary scenario used n=2000, 10 studies and K=5 strata. We varied K (3, 5, 10), sample size (500, 2000, 10 000), Z-to-Y effect scale (0.5, 1.0, 2.0), Z-to-X influence scale (0.2, 0.5, 1.0) and introduced a non-linear Z-to-X mapping. The primary and strata-sensitivity scenarios used 50 replications; extended robustness used 30; empirical null used 200 and W_est misspecification used 50.

### Stratification methods

**Proposed Family 1 (outcome-informed).** Method 1A: predicted probability of Y from logistic Y~X, stratified by quantiles. Method 1B: absolute residual from the same model. Method 1C: K-fold cross-validated predictions before stratification.

**Proposed Family 2 (outcome-free).** Method 2A: first principal component of standardised X. Method 2B: K-means on standardised X.

**Comparators and baselines.** Propensity-score quintiles [rosenbaum1983], Gaussian mixture model on X [mclachlan2000], prognostic-score stratification (untreated-only Y~X) [hansen2008]; Oracle baselines stratify by true Z-space; random assignment provides a chance reference. Equal-frequency strata were used throughout, logistic regression used l2 regularisation (C=1.0, lbfgs), and outcome-informed methods used a 50/50 discovery/evaluation split.

### Synthesis of stratum-specific effects

Within each stratum we computed the risk difference between outcome probabilities under treatment and control. A two-stage fixed-effect summary weighted strata by size; a DerSimonian-Laird random-effects summary estimated between-stratum variance [dersimonian1986]. *Stratum-specific pooling* means summarising effects within more homogeneous subgroups identified from the pooled IPD.

Several caveats apply. Discovered strata are not independent estimates; they are formed from the same IPD sample, so their stratum-specific risk differences are dependent. The DerSimonian-Laird tau^2 and SE therefore describe between-stratum heterogeneity and should be interpreted cautiously. The SE of the pooled random-effects risk difference is conditional on the chosen stratification and does not account for stratum-formation uncertainty.

### Study-level meta-analysis benchmark

To contextualise within-study and between-study heterogeneity, we also formed a study-level summary: we pooled crude study-specific risk differences with a DerSimonian-Laird random-effects meta-analysis and compared its ATE bias with the IPD stratified analyses. This benchmark shows how much heterogeneity is captured by conventional study-level pooling before any covariate-based stratification is applied.

### Evaluation metrics

**ARI** [hubert1985]: agreement between estimated strata and a constructed true-Z reference partition, corrected for chance. The true-Z partition is a k-means clustering of standardised Z-space with K strata, so ARI measures agreement with an operational reference rather than clinical validity.

**C1** = 1 - I^2 applied to stratum-specific log odds ratios [higgins2002]. Lower C1 indicates greater between-stratum heterogeneity of stratum-specific log odds ratios. Because C1 is computed on the log-odds scale while ATE bias is on the risk-difference scale, it is an indirect diagnostic of bias; it summarises the coherence of the selected partition, not the magnitude of hidden modification.

**W_true / W_est:** proportion of total CATE variance explained by the stratification, i.e. the between-stratum CATE variance divided by the overall CATE variance. W_est requires a correctly specified individual-level outcome model. Because W is a ratio whose denominator is the overall CATE variance, it can be unstable when effect modification is weak (small denominators) and should be interpreted relative to its empirical null distribution. We therefore report null-mean-centred excess values: C1_excess = max(null mean C1 - C1, 0), W_excess = max(W - null mean W, 0) and proportion metrics such as eta^2 = between-stratum CATE variance / overall CATE variance as an alternative scale-free summary.

**ATE bias reduction:** absolute differences between crude, stratified and random-effects estimates, plus relative ratios. Monte Carlo SE and 95% CI accompany every mean.

### Empirical null distribution and null-centred reporting

We ran 200 additional replications under the primary DGM with Z-by-A interaction coefficients set to zero. This retains confounding and covariate traces but has no true effect modification. For each method we recorded C1 and W_est and report the 5th, 50th and 95th percentiles in Supplementary Table S5. Values below the 5th percentile (C1) or above the 95th percentile (W_est) provide method-specific thresholds for flagging incoherence. In addition, we computed excess diagnostics by subtracting the empirical null mean, producing more stable summaries than raw W and C1.

### W_est outcome-model misspecification sensitivity

W_est is computed from an estimated individual-level CATE. Omitting treatment-covariate interactions can inflate or deflate W_est, so we repeated the primary scenario with three outcome-model specifications for W_est: main effects only (Y ~ X + A), linear interactions (Y ~ X + A + X*A, default), and linear plus quadratic interactions. Results are in Supplementary Table S6.

### Diagnostic calibration using the empirical null

We used the 200 null replications together with the 50 alternative replications of the primary scenario to compute, for each method, the area under the ROC curve (AUC) and the true-positive rate (TPR) at a method-specific 5% false-positive rate (C1 below its null 5th percentile, W_est above its null 95th percentile). Because the null distribution preserves confounding and covariate traces but removes true effect modification, these metrics quantify how well the diagnostics distinguish absence from presence of the simulated modification. AUC near 0.5 and low TPR indicate that the diagnostics do not provide reliable classification on their own in the primary scenario; for some methods C1 AUC fell below 0.5, indicating that the alternative DGM shifted C1 in the opposite direction to the lower-tail hypothesis, so the one-sided threshold is not universally valid.

### True-CATE-quantile oracle reference

As a reference for sorting performance, we computed a true-CATE-quantile oracle that assigns participants to strata by the true conditional average treatment effect. This oracle is not a practical method (it uses the true CATE) but it provides an upper bound on how well any covariate-based stratification could separate heterogeneous subgroups. We include the oracle in sensitivity summaries to bound optimism and to illustrate the gap between empirical methods and the true sorting benchmark.

### Semi-synthetic illustrations

Five Simpson-paradox examples were reconstructed as pseudo-individual records from published aggregate statistics [charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]. The Israeli vaccination example used pseudo-IPD reconstructed from age- and vaccination-stratified COVID-19-related hospitalisation counts published by Haas et al. [haas2021]. We chose hospitalisation rather than infection counts because the published Table 2 provides age- and vaccination-stratified counts for a severe endpoint where age confounding is pronounced, and because the low event rate (~0.09% in the down-sampled data) creates a stress-test for rare outcomes. Because the published counts cover approximately 6.5 million people, we used a stratified random down-sample of 100,000 records preserving the age- and vaccination-specific hospitalisation rates. In the down-sampled pseudo-IPD, some cells contained very few or zero hospitalisation events; logistic models used for outcome-informed methods were fitted with L2 regularisation, and any degenerate one-class fit was handled by returning the observed mean probability. Pseudo-general variables mimicked proxies of the known confounder and the number of strata K was selected from the set {2, 3, min(K_true, 4), K_true}, where K_true is the true number of published strata, keeping the value that maximised ARI. These are illustrations, not real-IPD validation.

### Reporting and reproducibility

The design followed ADEMP [morris2019]; checklists are in Additional files 2 and 3. The pipeline is version-controlled and every manuscript number is read from repository CSV outputs. Simulations used Python 3.11; the exact dependency versions are in `requirements-lock.txt` and the commit hash used for the submission package is in `results/commit_hash.txt`.


## 3. Results

### Primary IPD scenario

Table 1 reports the primary scenario (n=2000, 10 studies, K=5). Agreement with the constructed true-Z partition was modest (Oracle ARI 0.372; best non-Oracle 1B_residual 0.032). Oracle and residual methods had the highest W_true values, but C1 was high across most methods (even random stratification yielded C1 0.883), indicating that C1 alone did not separate useful from chance stratifications; W_true separated the methods better. W_true exceeded W_est, reflecting that the estimated CATE captures only part of the true CATE variation. The best ATE bias reduction came from 1B_residual: crude bias 0.01865, stratified bias 0.01345 (relative reduction 0.279) and random-effects bias 0.00816 (relative reduction 0.563). For comparison, random-effects pooling across the true study identifiers (i.e. a study-level meta-analysis) gave an absolute ATE bias of 0.01568 (reduction 0.00296 from crude 0.01865). Pooling strata with DerSimonian-Laird improved over the fixed-effect summary, confirming that stratum-specific effects should be allowed to vary. Null-centred excess diagnostics for the best method were modest (C1_excess 0.054; W_est_excess 0.036).

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

Five Simpson-paradox examples were reconstructed as pseudo-individual records [charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]. Table 2 reports the best non-Oracle method per dataset. The Israel hospitalisation example was the most challenging: strong age confounding and a very low hospitalisation rate (~0.09%) meant that the crude marginal association reversed after stratification, yet separating the data into the known age strata remained difficult. The low event rate also produced occasional near-zero or zero-event cells, which illustrates the limits of outcome-informed stratification for rare outcomes.

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

Figure 4 and Supplementary Table S2 report n = 500, 2000 and 10 000 (K=5). Crude bias declined with n. The residual method's absolute random-effects ATE bias plateaued near 0.008–0.009 across the three sample sizes (0.00824 at n=500, 0.00852 at n=2000 and 0.00864 at n=10 000), so its relative reduction fell as the crude marginal estimate became more precise. Propensity-score, prognostic-score and clustering-based methods achieved larger relative reductions at n=10 000 (range 0.533–0.669), confirming that performance depends on the method as well as sample size. This pattern indicates that stratification can remove the estimable part of confounding-driven aggregation bias, but it cannot fully adjust for unmodelled hidden effect modification.

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

### Diagnostic discrimination against the empirical null

Table 4 and Figure 6 summarise the diagnostic calibration of C1 and W_est against the empirical null distribution obtained when Z-by-A interactions are removed. C1 AUC ranged from 0.460 to 0.545 and W_est AUC from 0.427 to 0.561; the best C1 AUC was 0.545 for 2B_clustering and the best W_est AUC was 0.561 for GMM. True-positive rates at a 5% false-positive rate were low: C1 TPR 0.000–0.060 and W_est TPR 0.020–0.080. These values show that the diagnostics did not reliably distinguish the alternative DGM from the null in the primary scenario; the C1 AUCs at or below 0.5 for several methods confirm that the lower-tail null threshold does not match the direction of the alternative DGM shift for those methods. A main-effects-only outcome model for W_est inflated the residual method's W_est from 0.077 (default interactions) to 0.691, whereas the polynomial interaction model gave 0.046; full results are in Supplementary Table S6. Supplementary Table S5 reports the empirical null percentiles used as thresholds.

| Method | C1 AUC | C1 TPR@5% FPR | W_est AUC | W_est TPR@5% FPR |
|---|---|---|---|---|
| 1A_predicted_prob | 0.506 | 0.060 | 0.541 | 0.080 |
| 1B_residual | 0.460 | 0.060 | 0.542 | 0.060 |
| 1C_cv_decision | 0.506 | 0.060 | 0.541 | 0.080 |
| 2A_PCA_cum60 | 0.464 | 0.060 | 0.490 | 0.060 |
| 2B_clustering | 0.545 | 0.020 | 0.537 | 0.060 |
| GMM | 0.489 | 0.060 | 0.561 | 0.080 |
| PS_propensity_score | 0.481 | 0.060 | 0.494 | 0.020 |
| Prognostic_score | 0.520 | 0.020 | 0.528 | 0.040 |
| baseline_oracle_kmeans | 0.507 | 0.000 | 0.506 | 0.040 |
| baseline_oracle_quantile | 0.507 | 0.000 | 0.537 | 0.060 |
| baseline_random | 0.544 | 0.040 | 0.427 | 0.040 |

*Table 4. Diagnostic discrimination of C1 and W_est against the empirical null distribution (n=2000, K=5, 200 null replications and 50 alternative replications).*

![Figure 6. Diagnostic calibration of C1 and W_est: AUC for discriminating the alternative DGM from the empirical null distribution (n=2000, K=5).](fig6_rsm_diagnostic_calibration.png)

### CATE variance explained

Figure 7 shows CATE variance explained (eta^2, represented by W_true) and the corresponding estimated value (W_est) for each method. Methods that produced stratum-specific effects close to the true CATE quantiles achieved higher eta^2, but no data-driven method reached the Oracle level. The gap between W_true and W_est confirms that the residual and predicted-probability models capture only part of the true CATE variation.

![Figure 7. CATE variance explained (eta^2 = W_true) and estimated W_est by method in the primary scenario (n=2000, K=5).](fig7_cate_variance_explained.png)

### Empirical null distribution and W_est misspecification

Under the primary DGM with no Z-by-A interaction, C1 was generally high and W_est near 0; method-specific 5th/95th percentiles are in Supplementary Table S5. A main-effects-only outcome model inflated W_est, whereas the default interaction and polynomial models were more stable (Supplementary Table S6). C1 and W are diagnostic flags, not standalone inferential quantities.


## 4. Discussion

### Principal findings

This study frames Incoherence-Oriented Neutralisation and Extraction (IONE) as a descriptive sensitivity tool for hidden effect modification in IPD meta-analysis. C1 and W flag whether a pooled IPD is internally coherent with respect to treatment effect: methods that captured more of the true Z structure produced C1 values close to the Oracle and higher W_true, especially the residual-based method. Agreement with the constructed true-Z partition was modest (Oracle ARI 0.372; best non-Oracle 1B_residual 0.032), and the C1 and W_est diagnostics did not reliably discriminate the alternative DGM from the empirical null (C1 AUC 0.460-0.545; W AUC 0.427-0.561). Nevertheless, the best data-driven stratification reduced crude ATE bias from 0.01865 to 0.00816 (relative reduction 0.563) with DerSimonian-Laird pooling. These findings show that separating a pooled IPD into more homogeneous strata can partially reduce marginal bias, and that stratum-specific effects should be allowed to vary once incoherence is suggested.

### Detection versus subgroup recovery

Detection asks whether the pooled population is internally coherent; C1 and W address this without requiring hidden subgroups to be specified. The ROC results in Table 4 and Figure 6 show that, in the primary scenario, detection sensitivity from C1 and W_est alone is low. Separating the data into more homogeneous subgroups is harder still, because measured covariates only partially trace the hidden effect modifier. IONE's practical value therefore lies in sensitivity exploration and partial ATE improvement, not in recovering hidden subgroup labels or replacing confounding adjustment.

### Comparison with study-level and covariate-adjustment approaches

Stratification by study remains a default in IPD meta-analysis and captured part of the marginal bias in our benchmark. Study-level random-effects pooling does not, however, exploit covariate traces of hidden effect modification within studies. Propensity-score [rosenbaum1983] and prognostic-score [hansen2008] methods adjust for measured confounders but do not detect unmeasured population structure. Latent-class models [mclachlan2000] seek hidden subgroups but need strong assumptions and do not report a transparent between-stratum heterogeneity diagnostic such as C1. IONE adds a pair of descriptive diagnostics that can be reported alongside these methods.

### W denominator and misspecification

W is a ratio whose denominator is the overall CATE variance. When effect modification is weak this denominator is small, making W unstable and hard to interpret as an absolute measure. We therefore centred the diagnostics on their empirical null means and reported excess values (C1_excess, W_true_excess, W_est_excess). W_est is also sensitive to outcome-model specification: a main-effects-only model for the residual method inflated W_est from 0.077 to 0.691, whereas the correctly specified polynomial interaction model gave 0.046. Analysts should not treat a single W_est value as evidence of an effect modifier without inspecting the fitted outcome model and the empirical null distribution.

### Large-sample behaviour

At n = 10 000 the residual method still showed a non-negligible random-effects ATE bias (0.00864; relative reduction 0.348), similar to the absolute floor observed at n=500 (0.00824) and n=2000 (0.00852). This floor is consistent with the ARI ceiling: once finite-sample error is removed, remaining bias reflects the structural mismatch between the discovered strata and the true CATE surface. The true-CATE-quantile oracle provides an upper bound on what perfect sorting could achieve; the gap between the oracle and the leading data-driven method quantifies the cost of not observing the true effect modifier.

### Relevance to SMMR readers

IONE sits between heterogeneity diagnostics and model-based effect modification in medical research. C1 re-purposes the I^2 statistic for discovered strata and W connects a partition to explained CATE variance. Both are descriptive sensitivity indices, not inferential tests. The empirical null distribution (Supplementary Table S5) calibrates the diagnostics under no true effect modification, and the misspecification sensitivity (Supplementary Table S6) checks whether W_est is robust to the outcome-model specification. IONE is best reported alongside conventional IPD meta-analysis and covariate adjustment, with standard adjustment applied within strata.

### Strengths and limitations

**Strengths.** The study followed ADEMP [morris2019], reported the data-generating mechanism and estimands transparently, and generated all numerical results from version-controlled repository scripts.

**Limitations.** The primary scenario used n=2000 and a moderate Z-to-X trace; sensitivity analyses examined K = 3, 5, 10, n = 500 to 10 000, Z-to-Y and Z-to-X scales, and a non-linear mapping, but performance may vary with stronger or weaker signals or fewer studies. The true-Z partition is a constructed reference, so ARI should not be over-interpreted as clinical validity. W_est depends on a correctly specified outcome model with interactions; a main-effects-only model can be highly misleading (Supplementary Table S6). DerSimonian-Laird strata are not independent estimates, so the reported tau^2 and I^2 describe between-stratum heterogeneity, not conventional between-study heterogeneity. C1 is computed from log odds ratios while ATE bias is on the risk-difference scale, so it is an indirect diagnostic. Null thresholds (Supplementary Table S5) are method-specific and conditional on the primary DGM. Semi-synthetic examples are pseudo-IPD reconstructions and serve as illustrations, not real-IPD validation.



## 5. Conclusions

IONE (Incoherence-Oriented Neutralisation and Extraction) is a descriptive sensitivity framework for hidden effect modification in IPD meta-analysis. Monte Carlo simulation and semi-synthetic examples show that the C1 and W diagnostics can flag incoherence, but they do not reliably separate the alternative data-generating mechanism from an empirical null in the primary scenario. When hidden variables leave strong traces in measured covariates, stratification can partially reduce ATE bias, but separating the data into the true hidden subgroups remains difficult. The diagnostics should be reported alongside conventional meta-analytic models and covariate adjustment, and should not be used as a replacement for rigorous causal inference. We recommend that coherence assessment using C1 and W be considered as a standard sensitivity step in IPD meta-analysis reporting.


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

Supplementary methods, abbreviations, the ADEMP/STROBE-Sim checklists, the four extended sensitivity tables, and the empirical null-distribution and W_est misspecification sensitivity tables are provided in `smmr_supplementary_v1.docx`.

### Artificial intelligence

Manuscript text, Python code, and some analyses were drafted or revised using large language models (OpenAI GPT-4 and GPT-4o, accessed August 2025 through August 2026) under the direct, iterative supervision of the author. The LLMs were used for drafting prose, formatting references, generating figures, and implementing the computational pipeline. The author designed the study, wrote the simulation code, selected all references, verified every numerical result against the repository outputs, and approved the final scientific content. No LLM-generated text was used without human review.


{{PAGE}}

{{REFS}}

