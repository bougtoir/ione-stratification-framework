# Supplementary materials for IONE: Incoherence-Oriented Neutralisation and Extraction

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


{{PAGE}}

## List of abbreviations

| Abbreviation | Full term |
|---|---|
| ARI | Adjusted Rand Index |
| ATE | Average treatment effect |
| BMI | Body mass index |
| C1 | Coherence indicator 1 (I^2-based) |
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

## Sensitivity analyses

### Sensitivity to the number of strata

Table S1 presents how random-effects ATE bias reduction and ARI changed as the number of strata varied (K = 3, 5, 10). For most methods the gain from increasing K was limited and non-monotonic; increasing strata beyond the true dimensionality of the hidden structure introduced additional sampling variation and did not consistently improve ATE bias reduction. The Oracle baselines did improve with larger K, because more strata allow a finer partition of the true Z-space. In contrast, data-driven methods did not reliably exploit the additional flexibility, suggesting that the number of strata should be chosen conservatively or compared across several values, rather than simply maximised.

| K | Method | ARI | ARI SE | C1 | C1 SE | W_est | W_est SE | RE bias | RE bias SE | Rel reduction RE | Rel reduction RE SE | RE I2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 1A_predicted_prob | 0.028 | 0.001 | 0.849 | 0.037 | 0.086 | 0.014 | 0.01450 | 0.00162 | 0.299 | 0.069 | 0.160 |
| 3 | 1B_residual | 0.032 | 0.001 | 0.976 | 0.015 | 0.075 | 0.012 | 0.00859 | 0.00027 | 0.585 | 0.047 | 0.062 |
| 3 | 1C_cv_decision | 0.028 | 0.001 | 0.849 | 0.037 | 0.086 | 0.014 | 0.01450 | 0.00162 | 0.299 | 0.069 | 0.160 |
| 3 | 2A_PCA_cum60 | 0.017 | 0.001 | 0.771 | 0.038 | 0.060 | 0.010 | 0.01833 | 0.00181 | 0.114 | 0.066 | 0.192 |
| 3 | 2B_clustering | 0.021 | 0.001 | 0.856 | 0.034 | 0.081 | 0.009 | 0.01439 | 0.00187 | 0.304 | 0.062 | 0.159 |
| 3 | GMM | 0.006 | 0.000 | 0.838 | 0.036 | 0.070 | 0.009 | 0.01835 | 0.00170 | 0.113 | 0.049 | 0.194 |
| 3 | PS_propensity_score | 0.006 | 0.001 | 0.888 | 0.028 | 0.059 | 0.009 | 0.01700 | 0.00172 | 0.178 | 0.060 | 0.119 |
| 3 | Prognostic_score | 0.025 | 0.001 | 0.844 | 0.031 | 0.079 | 0.013 | 0.01402 | 0.00178 | 0.322 | 0.071 | 0.130 |
| 3 | baseline_oracle_kmeans | 0.317 | 0.002 | 0.852 | 0.037 | 0.023 | 0.003 | 0.01813 | 0.00173 | 0.124 | 0.041 | 0.162 |
| 3 | baseline_oracle_quantile | 0.058 | 0.001 | 0.846 | 0.034 | 0.033 | 0.005 | 0.01325 | 0.00151 | 0.360 | 0.058 | 0.188 |
| 3 | baseline_random | 0.000 | 0.000 | 0.864 | 0.031 | 0.002 | 0.000 | 0.02081 | 0.00201 | -0.006 | 0.015 | 0.147 |
| 5 | 1A_predicted_prob | 0.029 | 0.001 | 0.891 | 0.025 | 0.111 | 0.015 | 0.01352 | 0.00162 | 0.275 | 0.090 | 0.142 |
| 5 | 1B_residual | 0.032 | 0.001 | 0.927 | 0.025 | 0.078 | 0.011 | 0.00816 | 0.00031 | 0.563 | 0.054 | 0.044 |
| 5 | 1C_cv_decision | 0.029 | 0.001 | 0.891 | 0.025 | 0.111 | 0.015 | 0.01352 | 0.00162 | 0.275 | 0.090 | 0.142 |
| 5 | 2A_PCA_cum60 | 0.016 | 0.001 | 0.881 | 0.030 | 0.080 | 0.013 | 0.01769 | 0.00148 | 0.051 | 0.083 | 0.130 |
| 5 | 2B_clustering | 0.023 | 0.001 | 0.865 | 0.027 | 0.143 | 0.012 | 0.01651 | 0.00168 | 0.115 | 0.064 | 0.146 |
| 5 | GMM | 0.005 | 0.000 | 0.895 | 0.025 | 0.096 | 0.011 | 0.01686 | 0.00180 | 0.096 | 0.049 | 0.127 |
| 5 | PS_propensity_score | 0.005 | 0.001 | 0.881 | 0.029 | 0.059 | 0.009 | 0.01754 | 0.00170 | 0.059 | 0.068 | 0.144 |
| 5 | Prognostic_score | 0.026 | 0.001 | 0.858 | 0.029 | 0.107 | 0.015 | 0.01430 | 0.00164 | 0.233 | 0.086 | 0.141 |
| 5 | baseline_oracle_kmeans | 0.372 | 0.003 | 0.913 | 0.021 | 0.030 | 0.003 | 0.01651 | 0.00161 | 0.115 | 0.088 | 0.124 |
| 5 | baseline_oracle_quantile | 0.095 | 0.001 | 0.897 | 0.024 | 0.042 | 0.007 | 0.01266 | 0.00130 | 0.321 | 0.079 | 0.169 |
| 5 | baseline_random | 0.000 | 0.000 | 0.883 | 0.028 | 0.004 | 0.000 | 0.01901 | 0.00192 | -0.019 | 0.024 | 0.117 |
| 10 | 1A_predicted_prob | 0.025 | 0.001 | 0.943 | 0.017 | 0.106 | 0.014 | 0.01396 | 0.00140 | 0.290 | 0.078 | 0.101 |
| 10 | 1B_residual | 0.026 | 0.001 | 0.955 | 0.016 | 0.093 | 0.012 | 0.00815 | 0.00039 | 0.585 | 0.057 | 0.006 |
| 10 | 1C_cv_decision | 0.025 | 0.001 | 0.943 | 0.017 | 0.106 | 0.014 | 0.01396 | 0.00140 | 0.290 | 0.078 | 0.101 |
| 10 | 2A_PCA_cum60 | 0.014 | 0.001 | 0.966 | 0.012 | 0.089 | 0.013 | 0.01636 | 0.00193 | 0.167 | 0.067 | 0.060 |
| 10 | 2B_clustering | 0.021 | 0.001 | 0.958 | 0.012 | 0.209 | 0.009 | 0.01558 | 0.00171 | 0.207 | 0.065 | 0.059 |
| 10 | GMM | 0.007 | 0.000 | 0.948 | 0.018 | 0.121 | 0.008 | 0.01738 | 0.00207 | 0.116 | 0.050 | 0.086 |
| 10 | PS_propensity_score | 0.005 | 0.001 | 0.967 | 0.013 | 0.051 | 0.009 | 0.01695 | 0.00191 | 0.138 | 0.059 | 0.044 |
| 10 | Prognostic_score | 0.022 | 0.001 | 0.954 | 0.015 | 0.099 | 0.014 | 0.01365 | 0.00146 | 0.306 | 0.072 | 0.079 |
| 10 | baseline_oracle_kmeans | 0.586 | 0.008 | 0.929 | 0.017 | 0.058 | 0.005 | 0.01231 | 0.00145 | 0.374 | 0.063 | 0.122 |
| 10 | baseline_oracle_quantile | 0.086 | 0.001 | 0.965 | 0.014 | 0.049 | 0.006 | 0.01213 | 0.00142 | 0.383 | 0.082 | 0.053 |
| 10 | baseline_random | -0.001 | 0.000 | 0.925 | 0.019 | 0.009 | 0.001 | 0.01922 | 0.00236 | 0.022 | 0.034 | 0.112 |

*Table S1. Sensitivity of random-effects ATE bias reduction and coherence diagnostics to the number of strata.*

### Sensitivity to sample size

Table S2 summarises the primary scenario repeated with n = 500, 2000 and 10 000, fixing K = 5 and the moderate Z-to-X and Z-to-Y effects. Because this extended sensitivity used 30 replications per cell, the point estimates are still noisier than the primary scenario; Monte Carlo SEs are reported to help gauge this uncertainty. The crude marginal ATE bias decreased with sample size, as expected from a more precisely estimated risk difference. The absolute random-effects bias declined for propensity-score, prognostic-score and clustering-based approaches, and these methods achieved their largest relative bias reductions at n = 10 000. In contrast, the outcome-residual approach showed a floor near 0.008-0.009 and its relative bias reduction therefore decreased with n, while GMM improved only gradually. This mixed pattern confirms that the practical value of IONE depends on the interplay between sample size and method choice: with small samples, estimation error dominates; with large samples, remaining bias reflects structural limits of the selected stratification.

| Condition | Method | ARI | ARI SE | C1 | C1 SE | W_est | W_est SE | RE bias | RE bias SE | Rel reduction RE | Rel reduction RE SE | RE I2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n=500 | 1B_residual | 0.026 | 0.002 | 0.933 | 0.031 | 0.079 | 0.013 | 0.00824 | 0.00095 | 0.815 | 0.030 | 0.034 |
| n=500 | PS_propensity_score | 0.003 | 0.001 | 0.913 | 0.029 | 0.054 | 0.011 | 0.03992 | 0.00481 | 0.104 | 0.043 | 0.115 |
| n=500 | GMM | 0.008 | 0.001 | 0.936 | 0.024 | 0.116 | 0.012 | 0.03727 | 0.00533 | 0.163 | 0.057 | 0.129 |
| n=500 | Prognostic_score | 0.017 | 0.001 | 0.909 | 0.027 | 0.097 | 0.019 | 0.03453 | 0.00406 | 0.225 | 0.063 | 0.141 |
| n=500 | 2B_clustering | 0.023 | 0.002 | 0.939 | 0.027 | 0.160 | 0.016 | 0.03294 | 0.00457 | 0.260 | 0.073 | 0.086 |
| n=2000 | 1B_residual | 0.032 | 0.001 | 0.911 | 0.035 | 0.071 | 0.014 | 0.00852 | 0.00043 | 0.522 | 0.093 | 0.018 |
| n=2000 | PS_propensity_score | 0.007 | 0.001 | 0.845 | 0.043 | 0.074 | 0.015 | 0.01676 | 0.00223 | 0.060 | 0.111 | 0.162 |
| n=2000 | GMM | 0.006 | 0.001 | 0.895 | 0.032 | 0.061 | 0.010 | 0.01736 | 0.00272 | 0.027 | 0.082 | 0.142 |
| n=2000 | Prognostic_score | 0.025 | 0.001 | 0.880 | 0.034 | 0.106 | 0.022 | 0.01374 | 0.00245 | 0.230 | 0.145 | 0.170 |
| n=2000 | 2B_clustering | 0.024 | 0.001 | 0.852 | 0.038 | 0.120 | 0.014 | 0.01684 | 0.00270 | 0.056 | 0.159 | 0.158 |
| n=10000 | 1B_residual | 0.034 | 0.000 | 0.943 | 0.031 | 0.101 | 0.017 | 0.00864 | 0.00011 | 0.348 | 0.067 | 0.048 |
| n=10000 | PS_propensity_score | 0.012 | 0.001 | 0.870 | 0.044 | 0.070 | 0.020 | 0.00618 | 0.00091 | 0.533 | 0.060 | 0.138 |
| n=10000 | GMM | 0.005 | 0.000 | 0.864 | 0.038 | 0.047 | 0.007 | 0.01130 | 0.00140 | 0.146 | 0.043 | 0.171 |
| n=10000 | Prognostic_score | 0.031 | 0.000 | 0.913 | 0.034 | 0.135 | 0.023 | 0.00438 | 0.00082 | 0.669 | 0.074 | 0.172 |
| n=10000 | 2B_clustering | 0.025 | 0.000 | 0.839 | 0.043 | 0.143 | 0.013 | 0.00580 | 0.00107 | 0.562 | 0.066 | 0.239 |

*Table S2. Sample-size sensitivity (K=5, z=1.0, zx=1.0): means over 30 simulations.*

### Sensitivity to Z-to-X influence strength

Table S3 summarises performance for zx influence scale = 0.2, 0.5 and 1.0. A larger trace was associated with higher ARI for most methods, and C1 and W_est moved in the expected direction for several approaches, but the bias-reduction gains were non-monotonic and variable at this number of replications. This pattern indicates that stronger covariate traces improve subgroup recovery in principle, yet finite-sample noise and differences between methods in how the trace is exploited remain important; the diagnostics detect statistical traces rather than recover the hidden variables perfectly.

| Condition | Method | ARI | ARI SE | C1 | C1 SE | W_est | W_est SE | RE bias | RE bias SE | Rel reduction RE | Rel reduction RE SE | RE I2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zx=0.2 | 1B_residual | 0.010 | 0.001 | 1.000 | 0.000 | 0.049 | 0.011 | 0.00903 | 0.00014 | 0.576 | 0.055 | 0.010 |
| zx=0.2 | PS_propensity_score | 0.001 | 0.000 | 0.837 | 0.043 | 0.088 | 0.019 | 0.02011 | 0.00277 | 0.056 | 0.049 | 0.171 |
| zx=0.2 | GMM | 0.001 | 0.000 | 0.829 | 0.041 | 0.128 | 0.019 | 0.02017 | 0.00265 | 0.053 | 0.040 | 0.184 |
| zx=0.2 | Prognostic_score | 0.001 | 0.000 | 0.922 | 0.033 | 0.069 | 0.017 | 0.01934 | 0.00270 | 0.092 | 0.045 | 0.083 |
| zx=0.2 | 2B_clustering | 0.001 | 0.000 | 0.850 | 0.038 | 0.157 | 0.015 | 0.01997 | 0.00270 | 0.062 | 0.036 | 0.157 |
| zx=0.5 | 1B_residual | 0.018 | 0.001 | 1.000 | 0.000 | 0.051 | 0.009 | 0.00872 | 0.00014 | 0.541 | 0.060 | 0.000 |
| zx=0.5 | PS_propensity_score | 0.002 | 0.000 | 0.864 | 0.035 | 0.081 | 0.016 | 0.01814 | 0.00206 | 0.046 | 0.061 | 0.150 |
| zx=0.5 | GMM | 0.002 | 0.000 | 0.868 | 0.039 | 0.101 | 0.013 | 0.01924 | 0.00226 | -0.012 | 0.074 | 0.135 |
| zx=0.5 | Prognostic_score | 0.009 | 0.000 | 0.922 | 0.035 | 0.064 | 0.011 | 0.01796 | 0.00233 | 0.055 | 0.072 | 0.093 |
| zx=0.5 | 2B_clustering | 0.006 | 0.000 | 0.873 | 0.036 | 0.142 | 0.016 | 0.01704 | 0.00208 | 0.104 | 0.058 | 0.156 |
| zx=1.0 | 1B_residual | 0.032 | 0.001 | 0.911 | 0.035 | 0.071 | 0.014 | 0.00852 | 0.00043 | 0.522 | 0.093 | 0.018 |
| zx=1.0 | PS_propensity_score | 0.007 | 0.001 | 0.845 | 0.043 | 0.074 | 0.015 | 0.01676 | 0.00223 | 0.060 | 0.111 | 0.162 |
| zx=1.0 | GMM | 0.006 | 0.001 | 0.895 | 0.032 | 0.061 | 0.010 | 0.01736 | 0.00272 | 0.027 | 0.082 | 0.142 |
| zx=1.0 | Prognostic_score | 0.025 | 0.001 | 0.880 | 0.034 | 0.106 | 0.022 | 0.01374 | 0.00245 | 0.230 | 0.145 | 0.170 |
| zx=1.0 | 2B_clustering | 0.024 | 0.001 | 0.852 | 0.038 | 0.120 | 0.014 | 0.01684 | 0.00270 | 0.056 | 0.159 | 0.158 |

*Table S3. Sensitivity to Z-to-X influence strength (n=2000, K=5, z=1.0, zx=0.2, 0.5, 1.0): means over 30 simulations.*

### Sensitivity to Z-to-Y effect strength

Table S4 summarises results for z effect scale = 0.5, 1.0 and 2.0. When effect modification was weak (z = 0.5), C1 and W_est were close to their null values, reflecting limited detectable heterogeneity. As the effect increased, C1 decreased and W_est increased for most methods, and the relative random-effects bias reduction improved for all leading approaches. The outcome-residual approach already produced a substantial relative bias reduction at z = 0.5, suggesting that it can exploit the moderate covariate trace even when the marginal modification signal is weak. Overall, the diagnostics are most informative when hidden effect modification is strong enough to bias the marginal ATE.

| Condition | Method | ARI | ARI SE | C1 | C1 SE | W_est | W_est SE | RE bias | RE bias SE | Rel reduction RE | Rel reduction RE SE | RE I2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z=0.5 | 1B_residual | 0.026 | 0.001 | 0.982 | 0.015 | 0.060 | 0.016 | 0.00918 | 0.00024 | 0.472 | 0.063 | 0.001 |
| z=0.5 | PS_propensity_score | 0.007 | 0.001 | 0.861 | 0.037 | 0.055 | 0.011 | 0.01692 | 0.00207 | 0.028 | 0.086 | 0.161 |
| z=0.5 | GMM | 0.006 | 0.001 | 0.948 | 0.023 | 0.085 | 0.014 | 0.01586 | 0.00177 | 0.089 | 0.038 | 0.058 |
| z=0.5 | Prognostic_score | 0.024 | 0.001 | 0.867 | 0.034 | 0.089 | 0.021 | 0.01410 | 0.00196 | 0.190 | 0.073 | 0.158 |
| z=0.5 | 2B_clustering | 0.024 | 0.001 | 0.846 | 0.034 | 0.112 | 0.015 | 0.01488 | 0.00196 | 0.145 | 0.072 | 0.169 |
| z=1.0 | 1B_residual | 0.032 | 0.001 | 0.911 | 0.035 | 0.071 | 0.014 | 0.00852 | 0.00043 | 0.522 | 0.093 | 0.018 |
| z=1.0 | PS_propensity_score | 0.007 | 0.001 | 0.845 | 0.043 | 0.074 | 0.015 | 0.01676 | 0.00223 | 0.060 | 0.111 | 0.162 |
| z=1.0 | GMM | 0.006 | 0.001 | 0.895 | 0.032 | 0.061 | 0.010 | 0.01736 | 0.00272 | 0.027 | 0.082 | 0.142 |
| z=1.0 | Prognostic_score | 0.025 | 0.001 | 0.880 | 0.034 | 0.106 | 0.022 | 0.01374 | 0.00245 | 0.230 | 0.145 | 0.170 |
| z=1.0 | 2B_clustering | 0.024 | 0.001 | 0.852 | 0.038 | 0.120 | 0.014 | 0.01684 | 0.00270 | 0.056 | 0.159 | 0.158 |
| z=2.0 | 1B_residual | 0.037 | 0.001 | 0.927 | 0.031 | 0.085 | 0.017 | 0.00565 | 0.00061 | 0.828 | 0.021 | 0.065 |
| z=2.0 | PS_propensity_score | 0.009 | 0.001 | 0.949 | 0.018 | 0.064 | 0.010 | 0.01979 | 0.00251 | 0.399 | 0.056 | 0.100 |
| z=2.0 | GMM | 0.004 | 0.001 | 0.894 | 0.034 | 0.077 | 0.010 | 0.02791 | 0.00356 | 0.153 | 0.049 | 0.136 |
| z=2.0 | Prognostic_score | 0.029 | 0.001 | 0.966 | 0.024 | 0.106 | 0.022 | 0.01376 | 0.00250 | 0.582 | 0.059 | 0.143 |
| z=2.0 | 2B_clustering | 0.023 | 0.001 | 0.892 | 0.034 | 0.106 | 0.013 | 0.01990 | 0.00235 | 0.396 | 0.045 | 0.149 |

*Table S4. Sensitivity to Z-to-Y effect strength (n=2000, K=5, zx=1.0, z=0.5, 1.0, 2.0): means over 30 simulations.*

### Empirical null distribution of C1 and W_est

Under the primary DGM with the Z-by-A interaction coefficients set to zero, there is no true log-odds effect modification. Table S5 reports the empirical mean, Monte Carlo SE and 5th/95th percentiles of C1 and W_est for each method. A C1 value below the 5th percentile or a W_est value above the 95th percentile of this null provides a conservative threshold for flagging possible incoherence.

| Method | C1 mean | C1 SE | C1 5th | C1 95th | W_est mean | W_est SE | W_est 5th | W_est 95th |
|---|---|---|---|---|---|---|---|---|
| 1A_predicted_prob | 0.903 | 0.012 | 0.511 | 1.000 | 0.094 | 0.007 | 0.006 | 0.309 |
| 1B_residual | 0.893 | 0.015 | 0.446 | 1.000 | 0.067 | 0.005 | 0.004 | 0.232 |
| 1C_cv_decision | 0.903 | 0.012 | 0.511 | 1.000 | 0.094 | 0.007 | 0.006 | 0.309 |
| 2A_PCA_cum60 | 0.876 | 0.013 | 0.469 | 1.000 | 0.084 | 0.006 | 0.003 | 0.280 |
| 2B_clustering | 0.887 | 0.013 | 0.444 | 1.000 | 0.133 | 0.006 | 0.026 | 0.288 |
| GMM | 0.879 | 0.013 | 0.470 | 1.000 | 0.081 | 0.005 | 0.010 | 0.218 |
| PS_propensity_score | 0.879 | 0.013 | 0.461 | 1.000 | 0.065 | 0.006 | 0.003 | 0.246 |
| Prognostic_score | 0.878 | 0.013 | 0.453 | 1.000 | 0.093 | 0.007 | 0.006 | 0.308 |
| baseline_oracle_kmeans | 0.893 | 0.013 | 0.479 | 1.000 | 0.031 | 0.002 | 0.004 | 0.071 |
| baseline_oracle_quantile | 0.883 | 0.013 | 0.481 | 1.000 | 0.037 | 0.003 | 0.002 | 0.129 |
| baseline_random | 0.899 | 0.013 | 0.462 | 1.000 | 0.004 | 0.000 | 0.001 | 0.010 |

*Table S5. Empirical null distribution of C1 and W_est (n=2000, K=5, 200 replications, no true Z-by-A interaction).*

### W_est outcome-model misspecification sensitivity

Table S6 compares W_est computed under three outcome-model specifications. A main-effects-only model (W_est main) ignores treatment-covariate interactions and is therefore misspecified; the default linear-interaction model (W_est interact) and the polynomial-interaction model (W_est poly) include interactions and provide more flexible estimates. Large discrepancies across these columns indicate that the W_est diagnostic is sensitive to outcome-model specification.

| Method | ARI | C1 | W_true | W_est (main) | W_est (interact) | W_est (poly) | RE bias | Rel reduction RE |
|---|---|---|---|---|---|---|---|---|
| 1A_predicted_prob | 0.028 | 0.919 | 0.348 | 0.808 | 0.108 | 0.064 | 0.01135 | 0.462 |
| 1B_residual | 0.031 | 0.926 | 0.361 | 0.691 | 0.077 | 0.046 | 0.00808 | 0.617 |
| 1C_cv_decision | 0.028 | 0.919 | 0.348 | 0.808 | 0.108 | 0.064 | 0.01135 | 0.462 |
| 2A_PCA_cum60 | 0.017 | 0.932 | 0.161 | 0.420 | 0.057 | 0.034 | 0.01573 | 0.254 |
| 2B_clustering | 0.022 | 0.896 | 0.209 | 0.517 | 0.120 | 0.070 | 0.01591 | 0.245 |
| GMM | 0.006 | 0.879 | 0.059 | 0.131 | 0.076 | 0.058 | 0.01708 | 0.190 |
| PS_propensity_score | 0.007 | 0.888 | 0.072 | 0.170 | 0.083 | 0.043 | 0.01599 | 0.242 |
| Prognostic_score | 0.026 | 0.885 | 0.320 | 0.752 | 0.100 | 0.057 | 0.01192 | 0.435 |
| baseline_oracle_kmeans | 0.378 | 0.897 | 0.361 | 0.174 | 0.033 | 0.020 | 0.01507 | 0.285 |
| baseline_oracle_quantile | 0.096 | 0.890 | 0.441 | 0.316 | 0.047 | 0.027 | 0.01066 | 0.494 |
| baseline_random | -0.000 | 0.857 | 0.004 | 0.004 | 0.004 | 0.005 | 0.02024 | 0.040 |

*Table S6. Sensitivity of W_est to outcome-model specification (n=2000, K=5, 50 replications).*

