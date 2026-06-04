# IONE: Incoherence-Oriented Neutralisation and Extraction for Detecting Hidden Population Structure in Observational Studies — a Monte Carlo Simulation Study

---

**Tatsuki Onishi**

**[Affiliation to be confirmed by author]**

**Corresponding author:** Tatsuki Onishi (bougtoir@gmail.com)

---

## Abstract

**Background:** Observational studies are susceptible to bias from unmeasured effect modification and confounding. When an unmeasured variable modifies the treatment effect, marginal estimates may misrepresent the treatment's impact on specific subpopulations. Existing adjustment methods address measured confounders but provide no mechanism for detecting subgroup structure driven by unmeasured effect modifiers. We propose IONE (Incoherence-Oriented Neutralisation and Extraction), an exploratory framework that detects population incoherence—heterogeneity in subgroup-specific treatment effects—and extracts coherent subpopulations using routinely measured variables.

**Methods:** We conducted a Monte Carlo simulation study following the ADEMP framework. Data were generated from a causal directed acyclic graph with three unmeasured variables (age, sex, BMI) influencing ten measured variables, a binary treatment, and a binary outcome. The unmeasured variables acted as both confounders (Z→A, Z→Y) and effect modifiers (Z×A→Y). We evaluated six proposed stratification methods in two families, benchmarked against four active comparators (propensity score quintiles, Gaussian mixture model, prognostic score, k-means on covariates) and two baselines (random, oracle). Performance was assessed by the Adjusted Rand Index (ARI), treatment effect bias reduction, a between-stratum heterogeneity indicator (C1, derived from I²), and a within-stratum homogeneity indicator (W). All estimates carry Monte Carlo standard errors. Phase 1 comprised 21,600 evaluations; sensitivity analyses comprised 109,350 evaluations. We additionally applied IONE to five published instances of Simpson's paradox as semi-synthetic illustrations.

**Results:** The best proposed method (1B: residual-based stratification) achieved ARI = 0.021 (SE 0.0002) vs. random 0.000, modestly outperforming all active comparators (prognostic score 0.014, PS quintiles 0.012, GMM 0.008). W (within-stratum homogeneity) effectively discriminated methods: W = 0.292 for Method 1B vs. 0.001 for random stratification. C1 (between-stratum heterogeneity) showed limited discriminating power (range 0.81–0.87 across all methods). Method 1B achieved the largest ATE bias reduction (7.4%, SE 0.0016). Performance depended strongly on Z→X influence strength (ARI ratio 19–34× from weak to strong signal in sensitivity analysis), while effect modification strength and sample size had minor effects. Binary unmeasured variables were poorly captured (η² < 0.02). In semi-synthetic illustrations, all methods achieved ARI > 0.7 when pseudo-general variables carried strong traces of the known confounder.

**Conclusions:** IONE provides a two-tier diagnostic: C1 detects between-stratum heterogeneity in treatment effects, and W quantifies within-stratum effect homogeneity. Together, they offer an exploratory assessment of population incoherence. Stratification-based extraction is most effective when unmeasured effect modifiers leave strong traces in measured variables. These indicators are intended as exploratory diagnostics to complement, not replace, established confounding adjustment methods.

**Keywords:** effect modification, unmeasured confounders, population heterogeneity, stratification, coherence indicator, Simpson's paradox, observational studies, Monte Carlo simulation

---

## Background

Observational studies are indispensable for generating real-world evidence on treatment effects when randomised controlled trials are infeasible or unethical [1, 2]. However, because treatment assignment is not under the investigator's control, these studies are susceptible to bias from unmeasured variables that create hidden population structure. Two phenomena are of primary concern. First, *unmeasured effect modification*: when an unmeasured variable modifies the treatment effect, the marginal (average) treatment effect may misrepresent the treatment's impact on specific subpopulations, and subgroup-specific effects may be hidden within an aggregate estimate that applies to no individual subgroup [6]. Second, *unmeasured confounding*: when an unmeasured variable affects both treatment assignment and outcome, spurious associations arise [3]. When both phenomena co-occur—an unmeasured variable simultaneously confounds and modifies the treatment effect—the resulting bias can be severe enough to reverse the direction of the observed association, a phenomenon known as Simpson's paradox [4, 5]. Related concepts such as the ecological fallacy [7] and non-collapsibility [8] are connected but distinct: the ecological fallacy involves cross-level inference from groups to individuals, whilst non-collapsibility is a mathematical property of non-linear effect measures rather than a form of hidden population structure.

These biases are not merely theoretical concerns. Simpson's paradox has been documented in landmark studies across medicine and social science: kidney stone treatment comparisons where the inferior treatment appeared superior in aggregate [9], university admissions data where apparent gender discrimination reversed at the departmental level [10], COVID-19 case fatality rate comparisons that were confounded by national differences in age distributions [11], vaccine effectiveness evaluations that appeared to show vaccine failure due to age-related confounding [12], and smoking–mortality studies where smokers appeared to have lower mortality due to confounding by age [13]. In each case, the paradox arose because the study population was *incoherent*—that is, it comprised multiple internally homogeneous (*coherent*) subpopulations whose mixture produced misleading aggregate statistics. The fundamental lesson of Simpson's paradox is that findings derived from an incoherent population should not be uncritically applied to the coherent subpopulations within it [4, 5].

Several established methods exist for addressing confounding in observational studies. The propensity score (PS), defined as the conditional probability of treatment assignment given observed covariates, enables balancing of measured confounders through stratification, matching, or weighting [14]. The prognostic score predicts the outcome under no treatment and provides an alternative basis for stratification [15, 16]. The disease risk score (DRS) constructs an outcome prediction model using untreated subjects only [17]. Instrumental variable methods exploit variables that affect treatment but not the outcome directly [18]. More recently, the high-dimensional propensity score (hdPS) algorithm automatically extracts thousands of candidate proxy variables from claims data to approximate unmeasured confounding [19, 20]. These methods share a fundamental limitation: they adjust only for *measured* covariates and provide no mechanism for detecting or extracting population structure driven by *unmeasured* variables [19, 21].

The concept that measured variables may carry indirect information about unmeasured confounders is not new. The hdPS algorithm rests on the insight that a sufficiently large collection of proxy variables can collectively approximate the influence of unmeasured confounders [19]. Proximal causal inference formalises the use of proxy variables for identification of causal effects in the presence of unmeasured confounding [22]. Latent class analysis and finite mixture models seek to identify unobserved subgroups from patterns in observed variables [23]. However, none of these approaches explicitly addresses the problem of *population incoherence*—the condition in which an apparently homogeneous study population actually comprises multiple coherent subpopulations with heterogeneous treatment effects. In current practice, the homogeneity of study populations is typically assumed implicitly, with baseline characteristics tables (Table 1) providing only descriptive summaries that cannot formally test for hidden subgroup structure [24].

We propose that the problem of hidden population structure can be addressed through a two-stage approach. In the first stage, a quantitative indicator of population coherence—the *coherence degree*—is computed from routinely measured variables to determine whether a study population contains hidden subgroups that warrant separate analysis. In the second stage, if incoherence is detected, the population is stratified into coherent subgroups using multivariate patterns in the measured variables, and the primary analysis is conducted within each subgroup. The rationale is as follows: if important unmeasured variables (e.g. age, disease severity, genetic subtype) exert systematic influence on routinely measured variables (e.g. laboratory values, vital signs), then these measured variables collectively carry a detectable "trace" of the unmeasured variable. Stratification based on these traces should recover, at least partially, the subgroup structure defined by the unmeasured variable.

To operationalise this approach, we develop two families of stratification methods. The first family (decision power-based methods) exploits the relationship between measured variables and the outcome: because unmeasured effect modifiers influence both measured covariates and the treatment effect, residual patterns from outcome prediction models may reflect the unmeasured variable's structure. To mitigate overfitting, outcome-informed methods employ sample splitting (training on one half of the data, assigning strata on the full dataset). The second family (feature score-based methods) operates in the covariate space alone, using unsupervised techniques such as principal component analysis and clustering to identify multivariate patterns attributable to unmeasured variables, without reference to the outcome. As diagnostic indicators, we propose two complementary metrics: C1, a between-stratum heterogeneity indicator derived from the I² statistic [25] applied to stratum-specific treatment effects (log odds ratios), and W, a within-stratum homogeneity indicator quantifying how much residual treatment effect heterogeneity remains within each stratum after stratification. C1 near 0 indicates strong between-stratum heterogeneity (evidence of population incoherence); W near 1 indicates that within-stratum effects are homogeneous (successful extraction of coherent subpopulations). It is important to note that between-stratum heterogeneity (measured by C1) and within-stratum homogeneity (measured by W) are related but conceptually distinct: strata that differ from one another do not necessarily have homogeneous effects within each stratum.

The objectives of this study are fourfold. First, we evaluate through Monte Carlo simulation whether stratification based solely on measured variables can recover subgroup structure defined by intentionally withheld variables that act as both confounders and effect modifiers, across a range of data-generating scenarios. Second, we benchmark the proposed methods against established approaches including propensity score quintile stratification, Gaussian mixture models, and prognostic scores. Third, we assess the ability of C1 and W to diagnose population incoherence and within-stratum coherence, respectively. Fourth, we apply the proposed methods to five published instances of Simpson's paradox [9–13] as semi-synthetic illustrations with known confounding structure. We refer to the proposed framework as IONE (Incoherence-Oriented Neutralisation and Extraction), reflecting its dual function of detecting population incoherence and extracting coherent subpopulations for valid within-subgroup inference.

---

## Methods

This simulation study is reported following the ADEMP framework (Aims, Data-generating mechanisms, Estimands, Methods, Performance measures) as recommended by Morris, White, and Crowther [26]. All analyses were conducted in Python 3.11.

### Aims

The aims of the simulation study were:

1. To evaluate whether stratification of observational data based solely on measured (general) variables can recover hidden subgroup structure defined by unmeasured (critical) variables that act as both confounders and effect modifiers.
2. To compare the performance of proposed IONE stratification methods with established approaches (propensity score quintiles, Gaussian mixture models, prognostic scores).
3. To assess the ability of C1 (between-stratum heterogeneity indicator) and W (within-stratum homogeneity indicator) to diagnose population incoherence.
4. To quantify treatment effect bias reduction achieved by stratification.
5. To identify the data-generating conditions under which the proposed methods are most and least effective.

### Data-generating mechanisms

#### Causal structure

Data were generated from a causal directed acyclic graph (DAG) with four variable types: critical variables **Z** = (Z₁, Z₂, Z₃), general variables **X** = (X₁, …, X₁₀), a binary treatment A, and a binary outcome Y. The causal pathways were: Z→X (traces in measured variables), Z→A (confounding), X→A (partial), A→Y (treatment effect), Z→Y (direct effect), Z×A→Y (effect modification), and X→Y (weak direct effects). The critical variables represented commonly encountered confounders and effect modifiers in clinical research:

- Z₁ (age): continuous, N(60, 12²), truncated to [20, 95]
- Z₂ (sex): binary, Bernoulli(0.5)
- Z₃ (BMI category): ordinal with three levels, Multinomial(0.3, 0.4, 0.3)

The general variables represented routine clinical measurements (e.g. haemoglobin A1c, total cholesterol, systolic blood pressure, ALT, creatinine, haemoglobin, white blood cell count, albumin, CRP, uric acid). Each general variable Xⱼ was generated as a function of one or more critical variables plus independent noise:

$$X_j = \sum_{l=1}^{3} \alpha_{jl} \cdot Z_l + \epsilon_j, \quad \epsilon_j \sim N(0, \sigma^2_j)$$

where αⱼₗ represents the influence of critical variable Zₗ on general variable Xⱼ. The influence coefficients were varied systematically (see Scenarios below).

#### Treatment model

A binary treatment A was generated from a logistic model incorporating both confounding and measured covariate effects:

$$\text{logit}(P(A=1)) = \gamma_0 + \gamma_{Z_1} Z_1 + \gamma_{Z_2} Z_2 + \gamma_{Z_3} Z_3 + \gamma_{X_1} X_1 + \gamma_{X_3} X_3$$

The Z→A pathway creates confounding (unmeasured variables influence treatment assignment). The X→A pathway represents the partial influence of measured covariates on treatment decisions. The intercept γ₀ was calibrated to achieve approximately 50% treatment prevalence.

#### Outcome model

The binary outcome was generated from a logistic model incorporating direct effects of Z, X, A, and the Z×A interaction (effect modification):

$$\text{logit}(P(Y=1)) = \beta_0 + \boldsymbol{\beta}_Z \cdot \mathbf{Z} + \boldsymbol{\beta}_X \cdot \mathbf{X} + \tau A + \boldsymbol{\delta} \cdot (\mathbf{Z} \times A)$$

where τ is the main treatment effect (log-OR scale, default 0.5), and **δ** represents the effect modification coefficients (Z×A interactions). Specifically, older patients (higher Z₁) and those with higher BMI (Z₃) benefited more from treatment, whilst males (Z₂ = 1) benefited less. This creates heterogeneous conditional average treatment effects (CATEs) across the population, with the true individual-level CATE computed as:

$$\text{CATE}_i = P(Y=1 | A=1, Z_i, X_i) - P(Y=1 | A=0, Z_i, X_i)$$

Critical variable effects were set to odds ratios of 1.5–3.0 and general variable effects to 1.0–1.3. The intercept β₀ was calibrated to achieve an overall event rate of approximately 15%.

#### Scenarios

The following factors were varied in a factorial design:

**Phase 1 (proof of concept):**

| Factor | Levels | Values |
|--------|--------|--------|
| Sample size (N) | 1 | 2,000 |
| Z→X influence scale | 3 | 0.3 (weak), 0.5 (moderate), 1.0 (strong) |
| Number of strata (K) | 2 | 3, 5 |
| Treatment effect (τ) | 1 | 0.5 (log-OR) |
| EM strength (δ) | 1 | 0.4 |
| Simulation repetitions | — | 200 per scenario |

This yielded 1,200 data-generating scenarios. Each scenario was evaluated with 18 methods (6 proposed + 4 comparators + 6 PCA variants + 2 baselines), producing 21,600 total evaluations.

**Sensitivity analyses:**

| Factor | Levels | Values |
|--------|--------|--------|
| Sample size (N) | 3 | 500, 2,000, 10,000 |
| Z→Y effect scale | 3 | 0.5, 1.0, 2.0 |
| Z→X influence scale | 3 | 0.2, 0.5, 1.0 |
| Number of strata (K) | 3 | 3, 5, 10 |
| EM strength (δ) | 3 | 0.0 (none), 0.4 (moderate), 0.8 (strong) |

This yielded 12,150 scenarios with 9 representative methods (4 proposed + 3 comparators + 2 baselines), producing 109,350 evaluations.

The total number of evaluations across both phases was 130,950. All estimates are reported with Monte Carlo standard errors (SE = SD/√n_reps).

### Estimands

The primary estimands were:

1. **Subgroup recovery**: the degree to which strata formed by general variables X alone correspond to the true subgroup structure defined by critical variables Z (measured by ARI).
2. **Trace capture**: the proportion of variance in Z explained by the stratification (η²).
3. **Between-stratum heterogeneity**: the degree to which stratum-specific treatment effects (log odds ratios of A→Y) differ across strata (C1 = 1 − I², where I² is the between-stratum heterogeneity in log ORs). C1 near 0 indicates high heterogeneity (evidence of population incoherence); C1 near 1 indicates homogeneous effects across strata.
4. **Within-stratum homogeneity**: the proportion of total treatment effect variance explained by the stratification (W = 1 − weighted within-stratum CATE variance / overall CATE variance). W near 1 indicates homogeneous effects within strata; W near 0 indicates residual heterogeneity.
5. **Treatment effect bias**: the reduction in average treatment effect (ATE) bias achieved by stratification-adjusted estimation compared to crude (marginal) estimation, using the true CATE as ground truth.

The true subgroup structure was defined by applying k-means clustering to the standardised Z-space, with the number of clusters set equal to the number of strata K.

### Methods under comparison

Eighteen methods were evaluated: six proposed IONE methods, four active comparators, six PCA variants, and two baselines.

**Family 1: Decision power-based methods (outcome-informed)**

These methods build a predictive model for Y using X alone, then stratify observations based on properties of the model output. Methods 1A, 1B, and 1D employ sample splitting: the model is trained on the first 50% of observations, and stratum assignments are generated for the full dataset using the trained model. This prevents overfitting by separating the model-building and stratum-assignment steps.

- **Method 1A (Predicted probability):** A logistic regression model predicting Y from X₁–X₁₀ is fitted on the training half. Observations in the full dataset are stratified by quantiles of the predicted probability p̂.

- **Method 1B (Residual):** From the same logistic regression trained on the first half, the absolute residual |Y − p̂| is computed for all observations. Observations are stratified by quantiles of |Y − p̂|. The rationale is that large residuals indicate observations poorly explained by X alone, suggesting strong influence of unmeasured Z. For binary outcomes, |Y − p̂| reduces to 1 − p̂ for Y = 1 and p̂ for Y = 0, making this essentially a stratification by predicted probability with a label-dependent transformation.

- **Method 1C (Cross-validated decision power):** A 5-fold cross-validation procedure is used, where the model is trained on 4 folds and predictions are generated for the held-out fold. This provides an alternative overfitting protection mechanism.

- **Method 1D (Machine learning uncertainty):** A random forest model predicting Y from X is fitted on the training half. The variance of predictions across trees serves as an uncertainty measure. Observations in the full dataset are stratified by quantiles of this uncertainty.

**Family 2: Feature score-based methods (outcome-free)**

These methods operate solely in the covariate space of X, without reference to Y, and do not require sample splitting.

- **Method 2A (PCA):** Principal component analysis is applied to the standardised X₁–X₁₀. Observations are stratified by quantiles of the first principal component score. Six variants were evaluated using PC1 through PC6.

- **Method 2B (Clustering):** K-means clustering is applied to the standardised X₁–X₁₀ with the number of clusters set to K. Cluster assignments define the strata directly.

**Active comparators:**

- **Propensity score quintiles (PS-Q):** A logistic regression model estimates P(A=1|X) (the propensity score). Observations are stratified into K groups by quantiles of the estimated propensity score. This is a standard approach in pharmacoepidemiology for adjusting measured confounding [14].

- **Gaussian mixture model (GMM):** A finite mixture model with K Gaussian components is fitted to the standardised covariate space X₁–X₁₀. Component assignments define strata. This represents the latent class analysis approach to hidden subgroup discovery [23].

- **Prognostic score (Prog):** A logistic regression model estimates P(Y=1|X, A=0) from untreated subjects only (A=0). Observations are stratified by quantiles of this prognostic score [15].

- **K-means on X (KM-X):** K-means clustering is applied to X₁–X₁₀, identical to Method 2B but included as an explicit comparator label for clarity.

**Baselines:**

- **Random:** Observations are randomly assigned to K strata of equal size.
- **Oracle (k-means on Z):** K-means clustering is applied to the standardised Z-space. This represents the theoretical upper bound, as it uses the withheld critical variables directly.

### Performance measures

Performance was assessed using the following measures:

**Primary measures:**

- **Adjusted Rand Index (ARI)** [27]: Measures agreement between estimated strata and true Z-based clusters, corrected for chance. Range [−1, 1]; 1 = perfect agreement; 0 = chance level.

- **Eta-squared (η²)**: The proportion of variance in each critical variable Z explained by the stratification. Computed as the between-stratum sum of squares divided by the total sum of squares. Higher η² indicates better capture of the hidden variable's trace.

- **Between-stratum heterogeneity indicator (C1)**: Defined as C1 = 1 − I², where I² is Higgins and Thompson's [25] heterogeneity statistic applied to stratum-specific treatment effect estimates (log odds ratios of A→Y). Each stratum is treated as a "study" in a meta-analytic framework. C1 near 0 indicates strong between-stratum heterogeneity in treatment effects (evidence that the population is incoherent—i.e. contains subgroups with different treatment responses). C1 near 1 indicates homogeneous treatment effects across strata (no evidence of incoherence). It is important to note that C1 repurposes I² from its original meta-analytic context (independent studies) to strata within a single dataset. This circular construction may alter the statistical properties of I²; formal calibration is beyond the scope of this study. Additionally, low C1 can arise from low within-stratum sample size or weak treatment effects, not only from genuine population incoherence. C1 should therefore be interpreted as an exploratory diagnostic rather than a formal hypothesis test.

- **Within-stratum homogeneity indicator (W)**: Defined as W = 1 − (weighted within-stratum CATE variance / overall CATE variance), where CATE is the true conditional average treatment effect computed from the known data-generating mechanism. W quantifies how much of the total heterogeneity in individual treatment effects is explained by the stratification. W near 1 indicates that individuals within each stratum have similar treatment effects (homogeneous strata); W near 0 indicates substantial residual within-stratum heterogeneity. W addresses a conceptual gap that C1 alone cannot fill: strata may differ from one another (low C1) without each stratum being internally homogeneous (which requires high W).

- **Treatment effect bias reduction**: The reduction in average treatment effect (ATE) bias achieved by stratification-adjusted estimation versus crude estimation. The crude ATE is the unadjusted log odds ratio; the stratified ATE is the inverse-variance weighted average of stratum-specific log odds ratios. Bias reduction is computed as 1 − |bias_stratified| / |bias_crude|.

**Secondary measures:**

- **Normalised Mutual Information (NMI)** [28]: An information-theoretic measure of cluster agreement. Range [0, 1].

- **Direction consistency rate**: The proportion of strata in which the direction of the treatment–outcome association (positive or negative log OR) is consistent with the overall direction.

- **CATE heterogeneity (η²_CATE)**: The proportion of variance in individual-level true CATEs explained by stratum membership. Higher values indicate that the stratification successfully separates individuals with different treatment effects.

All performance measures are reported as means across simulation repetitions, with Monte Carlo standard errors (MC SE = SD / √n_reps) and 2.5th/97.5th percentile confidence intervals.

### Semi-synthetic illustrations: application to published Simpson's paradox examples

To illustrate IONE's behaviour on data with known confounding and effect modification structure, we applied the proposed methods to five published instances of Simpson's paradox (Table 1). These serve as semi-synthetic illustrations rather than fully empirical validation, because the general variables are generated by design rather than genuinely measured. For each example, we:

1. Reconstructed individual-level data from published aggregate statistics.
2. Generated pseudo-general variables (6–10 variables) correlated with the known confounding variable, simulating a scenario in which the confounder is unmeasured but leaves traces in other measured variables.
3. Applied all proposed methods, active comparators, and baselines.
4. Evaluated performance using ARI, C1, W, η², bias reduction, and direction consistency.

**Table 1.** Published Simpson's paradox examples used for semi-synthetic illustration.

| Example | Source | N | Hidden confounder (Z) | No. of groups | Paradox |
|---------|--------|---|----------------------|---------------|---------|
| COVID-19 CFR | von Kügelgen et al. 2021 [11] | 50,459 | Age group (9 groups) | 9 | Italy CFR > China overall, but Italy < China within every age group |
| Kidney stone | Charig et al. 1986 [9] | 700 | Stone size (2 groups) | 2 | Treatment B > A overall, but A > B for both small and large stones |
| UC Berkeley | Bickel et al. 1975 [10] | 4,425 | Department (6 groups) | 6 | Males admitted at higher rate overall, but females ≥ males in most departments |
| Israeli vaccine | Morris 2021 [12] | 6,100 | Age group (2 groups) | 2 | Vaccine appears ineffective overall, but effective in both age groups |
| Smoking–mortality | Appleton et al. 1996 [13] | 1,314 | Age group (7 groups) | 7 | Smokers have lower mortality overall, but higher mortality in every age group |

It should be noted that these semi-synthetic illustrations use pseudo-general variables rather than genuine clinical measurements. This design permits evaluation of the method's capacity to detect known confounding and effect modification structure under controlled conditions, but does not constitute a fully realistic application. The encouraging results from these illustrations should not be interpreted as evidence of out-of-the-box performance on real clinical data, where the relationship between measured variables and unmeasured confounders is neither known nor engineered. The procedure is described in detail in Additional file 1.

### Computational implementation

All simulations were parallelised across 8 CPU cores using the joblib library. Phase 1 completed in 6.0 minutes; sensitivity analyses in 9.4 minutes. Each scenario was assigned a fixed random seed for reproducibility. Code is available at https://github.com/bougtoir/ione-stratification-framework.

---

## Results

### Simulation study

Results are reported as mean (MC SE) across 200 repetitions per scenario (Phase 1) or 50 repetitions (sensitivity analysis). All proposed methods, comparators, and baselines were evaluated under each scenario.

#### Overall method performance

Table 2 summarises the performance of all methods averaged across Phase 1 scenarios (N = 2,000; 200 repetitions per scenario). All estimates are reported as mean (MC SE).

**Table 2.** Method performance ranking in Phase 1 simulation (averaged across all scenarios; N = 2,000; 200 reps/scenario). Values are mean (MC SE).

| Rank | Method | Family | ARI (SE) | C1 (SE) | W (SE) | Bias red. (SE) |
|------|--------|--------|----------|---------|--------|----------------|
| 1 | Oracle (k-means on Z) | Baseline (upper) | 0.353 (0.0009) | 0.825 (0.0071) | 0.286 (0.0042) | 0.024 (0.0004) |
| 2 | Oracle (quantile on Z) | Baseline (upper) | 0.073 (0.0006) | 0.805 (0.0072) | 0.549 (0.0008) | 0.046 (0.0003) |
| 3 | **1B: Residual** | Decision power | 0.021 (0.0002) | 0.859 (0.0068) | 0.292 (0.0024) | 0.052 (0.0009) |
| 4 | **1A: Predicted probability** | Decision power | 0.014 (0.0003) | 0.858 (0.0065) | 0.216 (0.0039) | 0.028 (0.0005) |
| 5 | **1C: Cross-validated** | Decision power | 0.014 (0.0003) | 0.850 (0.0065) | 0.218 (0.0039) | 0.026 (0.0005) |
| 6 | Prognostic score | Comparator | 0.014 (0.0003) | 0.811 (0.0073) | 0.209 (0.0038) | 0.026 (0.0005) |
| 7 | PS quintiles | Comparator | 0.012 (0.0003) | 0.855 (0.0066) | 0.180 (0.0036) | 0.028 (0.0005) |
| 8 | **2B: Clustering** | Feature score | 0.011 (0.0003) | 0.867 (0.0062) | 0.130 (0.0029) | 0.015 (0.0004) |
| 9 | **1D: ML uncertainty** | Decision power | 0.010 (0.0002) | 0.858 (0.0064) | 0.148 (0.0021) | 0.045 (0.0004) |
| 10 | 2A: PCA (PC1) | Feature score | 0.011 (0.0003) | 0.858 (0.0063) | 0.188 (0.0042) | 0.022 (0.0005) |
| 11 | GMM | Comparator | 0.008 (0.0002) | 0.851 (0.0065) | 0.093 (0.0023) | 0.011 (0.0003) |
| 12 | Random | Baseline (lower) | −0.000 (0.0000) | 0.863 (0.0062) | 0.001 (0.0000) | −0.000 (0.0000) |

The best proposed IONE method (1B: Residual, ARI = 0.021) modestly outperformed all active comparators (prognostic score ARI = 0.014, PS quintiles ARI = 0.012, GMM ARI = 0.008). However, the gap between all proposed and comparator methods and the oracle baseline (ARI = 0.353) remained substantial. W (within-stratum homogeneity) was more discriminating than C1 (between-stratum heterogeneity) in this setting: Random stratification produced W ≈ 0.001, whilst Method 1B achieved W = 0.292 and the oracle quantile-based stratification achieved the highest W = 0.549. C1 values were similar across all methods (range 0.805–0.867), suggesting that C1 based on stratum-specific log odds ratios is a noisier diagnostic than C1 computed from stratum-specific outcome means. Method 1D achieved the highest bias reduction among proposed methods (0.045), followed by 1B (0.052).

#### Effect of Z→X influence strength

The strength of the hidden variable's influence on measured variables was expected to be the single most important determinant of method performance (Table 3).

**Table 3.** ARI (SE) by Z→X influence strength (averaged across K = 3, 5 strata).

| Method | zx = 0.3 (weak) | zx = 0.5 (moderate) | zx = 1.0 (strong) | Strong/weak ratio |
|--------|-----------------|--------------------|--------------------|-------------------|
| **1B: Residual** | 0.015 (0.0001) | 0.019 (0.0001) | 0.028 (0.0002) | 1.9 |
| **1A: Predicted prob.** | 0.003 (0.0001) | 0.009 (0.0001) | 0.029 (0.0002) | 8.6 |
| **1C: Cross-validated** | 0.003 (0.0001) | 0.009 (0.0001) | 0.029 (0.0001) | 8.7 |
| Prognostic score | 0.003 (0.0001) | 0.009 (0.0001) | 0.029 (0.0002) | 8.9 |
| PS quintiles | 0.003 (0.0001) | 0.008 (0.0001) | 0.026 (0.0002) | 10.0 |
| **2B: Clustering** | 0.002 (0.0001) | 0.006 (0.0001) | 0.025 (0.0002) | 15.7 |
| GMM | 0.001 (0.0001) | 0.004 (0.0001) | 0.018 (0.0002) | 15.1 |
| Oracle (k-means on Z) | 0.352 (0.0016) | 0.353 (0.0015) | 0.354 (0.0015) | 1.0 |
| Random | 0.000 (0.0000) | −0.000 (0.0000) | 0.000 (0.0000) | — |

Under strong Z→X influence (zx = 1.0), all proposed and comparator methods showed substantial improvement. Method 1B (residual) was the most robust under weak signal conditions (ARI = 0.015 at zx = 0.3 vs. 0.002–0.003 for other methods), consistent with its partial use of outcome information. The improvement ratio from weak to strong signal ranged from 1.9× (1B) to 15.7× (2B clustering), confirming that Z→X influence strength remains the primary determinant of extraction performance.

#### Capture of individual critical variables

**Table 4.** Eta-squared (η²) for each critical variable (K = 5 strata, zx = 1.0). Mean values.

| Method | Z₁ (age, cont.) | Z₂ (sex, binary) | Z₃ (BMI, ordinal) | Mean |
|--------|----------|----------|----------|------|
| Oracle (k-means on Z) | 0.157 | 0.845 | 0.685 | 0.562 |
| **1A: Predicted prob.** | 0.303 | 0.006 | 0.087 | 0.132 |
| **1C: Cross-validated** | 0.306 | 0.006 | 0.086 | 0.133 |
| Prognostic score | 0.297 | 0.007 | 0.084 | 0.129 |
| **1B: Residual** | 0.273 | 0.008 | 0.088 | 0.123 |
| PS quintiles | 0.275 | 0.004 | 0.081 | 0.120 |
| **2B: Clustering** | 0.241 | 0.018 | 0.088 | 0.116 |
| GMM | 0.183 | 0.014 | 0.061 | 0.086 |
| **1D: ML uncertainty** | 0.179 | 0.005 | 0.058 | 0.081 |
| Random | 0.001 | 0.002 | 0.002 | 0.002 |

Age (Z₁, continuous) was captured most effectively (η² up to 0.306 for Method 1C), followed by BMI (Z₃, ordinal; η² up to 0.088). Sex (Z₂, binary) was poorly captured by all proposed methods and comparators (η² < 0.02), confirming that binary variables leave weak traces in continuous measured covariates. This represents a fundamental limitation: IONE and comparator methods are more effective at detecting continuous or ordinal effect modifiers than binary ones.

#### C1 and W indicators

**Table 5.** C1 and W by method (K = 5 strata, zx = 1.0). Mean (MC SE).

| Method | C1 (SE) | W (SE) | CATE η² |
|--------|---------|--------|---------|
| Oracle (quantile on Z) | 0.838 (0.0150) | 0.557 (0.0009) | 0.557 |
| Oracle (k-means on Z) | 0.818 (0.0167) | 0.411 (0.0085) | 0.411 |
| **1C: Cross-validated** | 0.844 (0.0156) | 0.413 (0.0013) | 0.413 |
| **1B: Residual** | 0.771 (0.0177) | 0.410 (0.0014) | 0.410 |
| **1A: Predicted prob.** | 0.876 (0.0139) | 0.409 (0.0014) | 0.409 |
| Prognostic score | 0.877 (0.0135) | 0.398 (0.0016) | 0.398 |
| PS quintiles | 0.869 (0.0143) | 0.361 (0.0027) | 0.361 |
| **1D: ML uncertainty** | 0.883 (0.0137) | 0.254 (0.0017) | 0.254 |
| **2B: Clustering** | 0.868 (0.0146) | 0.254 (0.0013) | 0.254 |
| GMM | 0.860 (0.0150) | 0.174 (0.0026) | 0.174 |
| Random | 0.872 (0.0140) | 0.002 (0.0001) | 0.002 |

C1 values were similar across all methods, including random stratification (C1 ≈ 0.87), indicating that C1 based on stratum-specific log odds ratios has limited discriminating power in this setting. The exception was Method 1B (C1 = 0.771), which showed slightly more between-stratum heterogeneity. In contrast, W was highly discriminating: random stratification produced W = 0.002, whilst the best proposed methods achieved W ≈ 0.41, comparable to the oracle k-means baseline (W = 0.411). The oracle quantile-based stratification achieved the highest W = 0.557. This finding supports the value of W as a complementary diagnostic to C1.

**Figure 1.** ARI by Z→X influence strength for proposed methods and active comparators. Shaded bands represent 95% confidence intervals based on MC SEs. Method 1B (residual) showed the most robust performance under weak signal conditions.

**Figure 2.** Within-stratum homogeneity indicator W by method (K = 5 strata, zx = 1.0). Error bars represent 95% confidence intervals. W effectively discriminated methods capturing hidden structure from random stratification.

**Figure 3.** Treatment effect bias reduction by method (K = 5 strata, zx = 1.0). Error bars represent 95% confidence intervals. Method 1B achieved the largest ATE bias reduction.

**Figure 4.** C1 (between-stratum heterogeneity) vs. W (within-stratum homogeneity) for all methods (K = 5 strata, zx = 1.0). The ideal position is low C1 (high between-stratum heterogeneity) and high W (high within-stratum homogeneity), corresponding to the lower-right quadrant.

#### Treatment effect bias reduction

**Table 6.** Treatment effect bias metrics by method (K = 5 strata, zx = 1.0). Log-OR scale.

| Method | Crude ATE | Stratified ATE | True ATE | Bias crude | Bias strat. | Bias red. (SE) |
|--------|-----------|----------------|----------|------------|-------------|----------------|
| **1B: Residual** | 0.156 | 0.064 | 0.069 | 0.087 | 0.013 | 0.074 (0.0016) |
| **1D: ML uncertainty** | 0.156 | 0.099 | 0.069 | 0.087 | 0.031 | 0.056 (0.0007) |
| Oracle (quantile on Z) | 0.156 | 0.100 | 0.069 | 0.087 | 0.032 | 0.055 (0.0007) |
| PS quintiles | 0.156 | 0.104 | 0.069 | 0.087 | 0.036 | 0.051 (0.0006) |
| **1A: Predicted prob.** | 0.156 | 0.105 | 0.069 | 0.087 | 0.036 | 0.050 (0.0006) |
| **1C: Cross-validated** | 0.156 | 0.106 | 0.069 | 0.087 | 0.037 | 0.050 (0.0006) |
| Prognostic score | 0.156 | 0.106 | 0.069 | 0.087 | 0.037 | 0.049 (0.0006) |
| Oracle (k-means on Z) | 0.156 | 0.117 | 0.069 | 0.087 | 0.049 | 0.038 (0.0008) |
| **2B: Clustering** | 0.156 | 0.126 | 0.069 | 0.087 | 0.057 | 0.030 (0.0005) |
| GMM | 0.156 | 0.135 | 0.069 | 0.087 | 0.066 | 0.021 (0.0004) |
| Random | 0.156 | 0.156 | 0.069 | 0.087 | 0.087 | 0.000 (0.0001) |

All methods reduced ATE bias relative to the crude estimate. Method 1B achieved the largest bias reduction (7.4%), bringing the stratified ATE (0.064) closest to the true ATE (0.069). Notably, the oracle k-means baseline, which optimises for Z-recovery (highest ARI), did not achieve the largest bias reduction; the oracle quantile-based stratification (5.5%) and several proposed methods outperformed it, suggesting that ARI and bias reduction capture different aspects of stratification quality. Among active comparators, PS quintiles (5.1%) and prognostic score (4.9%) performed comparably to proposed IONE methods, whilst GMM (2.1%) was less effective.

#### Sensitivity analyses

The sensitivity analysis comprised 109,350 evaluations (9 methods × 243 parameter combinations × 50 replications). We varied five parameters: sample size N ∈ {500, 2,000, 10,000}, Z→Y effect scale ∈ {0.5, 1.0, 2.0}, Z→X influence ∈ {0.2, 0.5, 1.0}, number of strata K ∈ {3, 5, 10}, and effect modification strength ∈ {0.0, 0.4, 0.8}.

Z→X influence strength was the dominant determinant of performance (Table 7). ARI increased 19- to 34-fold from weak (zx = 0.2) to strong (zx = 1.0) signal conditions across all proposed methods. Method 1A (predicted probability) and 1C (CV decision power) achieved the highest ARI at strong signal (0.027, SE 0.0001), followed by prognostic score (0.026), 2B clustering (0.024), PS quintiles (0.023), and GMM (0.017). At weak signal, all methods converged toward the random baseline (ARI ≈ 0.001).

**Table 7.** ARI (SE) by Z→X influence strength in sensitivity analysis (109,350 evaluations).

| Method | zx = 0.2 (weak) | zx = 0.5 (moderate) | zx = 1.0 (strong) |
|--------|-----------------|--------------------|--------------------|
| 1A: Predicted probability | 0.001 (0.0000) | 0.008 (0.0000) | 0.027 (0.0001) |
| 1C: CV decision power | 0.001 (0.0000) | 0.008 (0.0000) | 0.027 (0.0001) |
| 2A: PCA (cum. 60%) | 0.001 (0.0000) | 0.004 (0.0000) | 0.015 (0.0001) |
| 2B: Clustering | 0.001 (0.0000) | 0.006 (0.0000) | 0.024 (0.0001) |
| PS quintiles | 0.001 (0.0000) | 0.007 (0.0000) | 0.023 (0.0001) |
| GMM | 0.001 (0.0000) | 0.004 (0.0000) | 0.017 (0.0001) |
| Prognostic score | 0.001 (0.0000) | 0.008 (0.0000) | 0.026 (0.0001) |
| Oracle k-means | 0.431 (0.0020) | 0.430 (0.0019) | 0.429 (0.0020) |
| Random baseline | −0.000 (0.0000) | 0.000 (0.0000) | −0.000 (0.0000) |

Effect modification strength had negligible impact on ARI: pooling all proposed methods, ARI was 0.0101 (SE 0.00008) at em = 0.0 and 0.0103 (SE 0.00008) at em = 0.8. Sample size had a modest effect: ARI increased from 0.0094 (N = 500) to 0.0109 (N = 10,000) across proposed methods.

W (within-stratum homogeneity) showed consistent sensitivity to Z→X influence: Method 1A achieved W = 0.059 (zx = 0.2), 0.166 (zx = 0.5), and 0.361 (zx = 1.0), vs. random baseline W ≈ 0.004 regardless of condition. Bias reduction followed a similar pattern: Method 1A achieved 0.8% (zx = 0.2), 2.2% (zx = 0.5), and 4.9% (zx = 1.0) reduction in ATE bias.

### Semi-synthetic illustrations

#### Overview of results

Table 8 summarises the performance of IONE and comparator methods across the five published Simpson's paradox examples.

**Table 8.** Summary of semi-synthetic illustration results.

| Example | K | Best IONE method | Best ARI | Oracle ARI | C1 (best) | C1 (random) |
|---------|---|-----------------|----------|------------|-----------|-------------|
| Kidney stone [9] | 2 | 2B: Clustering | 0.851 | 1.000 | 0.034 | 0.391 |
| Israel vaccine [12] | 2 | 2B: Clustering | 0.746 | 1.000 | 0.005 | 1.000 |
| Smoking mortality [13] | 7 | 1A: Predicted prob. | 0.498 | 1.000 | 0.005 | 1.000 |
| UC Berkeley [10] | 3 | 1A: Predicted prob. | 0.082 | 1.000 | 0.011 | 1.000 |
| COVID-19 CFR [11] | 3 | 1B: Residual | 0.064 | 1.000 | 0.002 | 1.000 |

#### Key findings from semi-synthetic illustrations

The semi-synthetic illustrations showed markedly higher subgroup recovery than the primary simulation: ARI ranged from 0.064 (COVID-19 CFR) to 0.851 (kidney stone), compared with ARI ≈ 0.021 in simulation. This discrepancy arises because the pseudo-general variables were engineered to carry strong traces of the known confounder, a condition that is optimistic relative to real clinical data.

C1 was consistently low for the best methods (C1 < 0.04 in all examples), indicating strong between-stratum heterogeneity. In four of five examples, random stratification yielded C1 = 1.000, confirming that the low C1 values reflect genuine structure recovered by the methods rather than noise. The kidney stone example showed the strongest recovery (ARI = 0.851, C1 = 0.034), consistent with its simple binary confounder (stone size) and strong Z→X traces. The UC Berkeley and COVID-19 examples were harder due to multi-level confounders (6 departments, 9 age groups), yielding lower ARI values despite low C1. This pattern is concordant with the simulation finding that subgroup recovery depends on the complexity of the hidden structure.

---

## Discussion

### Principal findings

This study introduces IONE, a framework for detecting and extracting hidden population structure arising from unmeasured effect modification and confounding in observational studies. The evaluation comprised 130,950 Monte Carlo evaluations and five semi-synthetic illustrations from published Simpson's paradox examples.

The principal findings are threefold. First, the within-stratum homogeneity indicator W effectively separated methods that captured hidden population structure (W ≈ 0.41 for best proposed methods) from random stratification (W ≈ 0.001), whilst C1 (between-stratum heterogeneity indicator based on stratum-specific log odds ratios) had limited discriminating power in this setting (C1 ≈ 0.77–0.88 across all methods). This suggests that W may be the more useful diagnostic in practice. Second, proposed IONE methods modestly outperformed active comparators: Method 1B (residual) achieved ARI = 0.021 vs. prognostic score (0.014), PS quintiles (0.012), and GMM (0.008). However, the gap between all methods and the oracle baseline (ARI = 0.353) remained substantial, and the practical significance of these ARI values is limited. Third, all methods reduced ATE bias, with Method 1B achieving the largest reduction (7.4%), bringing the stratified estimate close to the true value. The strength of the hidden variable's influence on measured variables (Z→X) was the primary determinant of performance. In the sensitivity analysis, ARI increased 19- to 34-fold from weak (zx = 0.2) to strong (zx = 1.0) signal conditions, while effect modification strength and sample size had comparatively minor effects.

### Two-tier diagnostic: C1 and W

The distinction between detection (C1) and within-stratum quality (W) addresses a fundamental conceptual point raised during peer review: between-stratum heterogeneity and within-stratum homogeneity are related but distinct concepts. Strata may differ from one another (low C1) without each stratum being internally homogeneous (which requires high W). C1 detects whether the population contains subgroups with heterogeneous treatment effects; W assesses whether the stratification has successfully isolated individuals with similar treatment effects within each stratum.

C1 repurposes the I² statistic from its original meta-analytic context (independent studies) to strata within a single dataset. In this circular construction, the statistical properties of I² may differ from its standard interpretation: strata are formed from the same data used to compute within-stratum effects, potentially inflating or deflating apparent heterogeneity. Low C1 can also arise from low within-stratum power or weak treatment effects, not only from genuine population incoherence. For these reasons, C1 should be interpreted as an exploratory diagnostic rather than a formal hypothesis test. The provisional threshold of C1 < 0.05 used here requires formal calibration across a wider range of settings.

W provides a complementary perspective by directly quantifying within-stratum treatment effect homogeneity using the true CATE (available in simulation) or estimated CATE (in practice). High W with low C1 represents the ideal outcome: strata that are different from each other and internally homogeneous.

### Comparison with existing methods

The inclusion of active comparators allows direct assessment of IONE's added value. The best proposed method (1B: Residual, ARI = 0.021) outperformed all comparators: prognostic score (ARI = 0.014), PS quintiles (ARI = 0.012), and GMM (ARI = 0.008). On the W metric, the advantage was more pronounced: Method 1B achieved W = 0.292 (overall) and W = 0.410 (at zx = 1.0, K = 5), comparable to or exceeding PS quintiles (W = 0.361) and prognostic score (W = 0.398). In terms of ATE bias reduction, Method 1B (7.4%) outperformed all comparators including PS quintiles (5.1%) and prognostic score (4.9%). These results suggest that IONE's outcome-informed stratification captures aspects of the hidden structure that covariate-only approaches miss, albeit with modest absolute effect sizes.

IONE differs from existing confounding adjustment methods in its primary target. Propensity score methods [14] and prognostic scores [15] aim to balance or adjust for *measured* confounders; they are not designed to detect *unmeasured* population structure or effect modification. The hdPS algorithm [19] shares IONE's insight that proxy variables may carry information about unmeasured confounders, but uses this information to improve propensity score estimation rather than to identify discrete subpopulations. Latent class analysis [23] seeks hidden subgroups but typically requires strong distributional assumptions and does not provide a coherence diagnostic.

IONE is best understood as complementary to these methods rather than as a replacement. We envision a workflow in which IONE is applied as an exploratory preliminary step: if C1 indicates between-stratum heterogeneity (low C1) and W indicates within-stratum homogeneity (high W), the population may be stratified into more homogeneous subgroups before conventional methods (e.g. propensity score analysis) are applied within each subgroup.

### Scope and framing

The original motivation for IONE referenced five related phenomena: confounding, Simpson's paradox, effect modification, ecological fallacy, and non-collapsibility. On further reflection, these have distinct causal structures and remedies. We have narrowed the framing to focus on unmeasured effect modification as the primary target, with unmeasured confounding as a secondary concern. Simpson's paradox is understood as an extreme manifestation of combined effect modification and confounding, where the direction of the treatment effect reverses between subgroups. Ecological fallacy (cross-level inference) and non-collapsibility (a mathematical property of non-linear effect measures) are related but distinct issues that IONE does not directly address; they are noted for completeness but removed from the claims.

This narrower framing aligns the Background motivation with the evaluation design: the data-generating mechanism includes both effect modification (Z×A→Y) and confounding (Z→A, Z→Y), and the primary estimands—subgroup-specific treatment effects—are directly relevant to detecting and recovering effect modification.

### Strengths and limitations

**Strengths.** This study employed a comprehensive simulation design with 130,950 evaluations spanning a wide range of data-generating conditions, including systematic variation of the key parameters (Z→X influence strength, effect modification strength, sample size, number of strata). The ADEMP framework ensured transparent reporting of all design choices. Active comparators (propensity score quintiles, GMM, prognostic score) were included to benchmark IONE against established methods. Monte Carlo standard errors accompany all point estimates, enabling assessment of estimation precision. The data-generating mechanism includes both a treatment variable and effect modification, aligning the evaluation with the causal-inference framing. Semi-synthetic illustrations on five published Simpson's paradox examples provided additional context, with appropriate caveats about their engineered nature.

**Limitations.** Several limitations should be acknowledged. First, the semi-synthetic illustrations used pseudo-general variables generated from published aggregate data, rather than genuine clinical measurements. The encouraging ARI values from these illustrations cannot be read as evidence of out-of-the-box performance on real clinical data. Validation on clinical databases with individual-level data (e.g. MIMIC-IV, UK Biobank) where a known confounder is intentionally withheld is an important next step.

Second, the simulation employed a relatively simple data-generating mechanism with three critical variables, ten general variables, linear Z→X relationships, and a logistic outcome model. Real clinical data may involve more complex causal structures, non-linear relationships, interactions among measured variables, missing data, and measurement error. The sensitivity of IONE to these complications requires further investigation.

Third, the number of strata K was set exogenously rather than estimated from the data. In practice, the number of hidden subgroups is unknown. Future work should explore data-driven approaches for selecting K (e.g. based on information criteria or stability analysis), and the sensitivity of results to misspecification of K should be characterised.

Fourth, binary critical variables (e.g. sex) were poorly captured (η² < 0.03), suggesting that IONE is better suited to detecting continuous or ordinal effect modifiers that leave stronger traces in measured variables. This is a substantial limitation given that binary variables (sex, treatment status, disease presence) are common in epidemiology.

Fifth, outcome-informed methods (1A, 1B, 1D) stratify on a function of the outcome, which risks inducing selection or collider bias in downstream within-stratum analyses. We mitigate this through sample splitting (training on the first 50% of data, assigning strata to the full dataset), but this does not eliminate the concern entirely. The extent of residual bias from outcome-informed stratification warrants further theoretical and empirical investigation.

Sixth, the C1 threshold of 0.05 proposed here is provisional. Formal calibration across a wider range of datasets and clinical settings is needed before recommendations can be made about clinical thresholds.

### Implications for practice

Our findings suggest several practical implications, though these should be interpreted cautiously given the limitations noted above. First, the C1 and W indicators may serve as exploratory diagnostics when assessing whether a study population contains hidden subgroups with heterogeneous treatment effects. When C1 is low (high between-stratum heterogeneity) and W is high (within-stratum homogeneity), this provides exploratory evidence that the population may benefit from stratified analysis. However, we emphasise that C1 should not be treated as a formal hypothesis test; its properties under the circular construction used here (strata derived from the same data) require further calibration. Second, the complementary strengths of decision power-based and feature score-based methods suggest that both should be applied when assessing population coherence, as their agreement provides stronger evidence for the existence of hidden subgroups. Third, the identification of Z→X influence strength as the primary determinant of performance provides a principled basis for assessing the likely utility of IONE in a given application: the method is most promising in settings where important effect modifiers (age, disease severity, comorbidity) are known to influence routine measurements (laboratory values, vital signs).

### Future directions

Several avenues for future research emerge from this work. Methodological extensions include adaptation to survival outcomes, continuous outcomes, and time-varying confounding. The combination of IONE with propensity score methods in a formal two-stage adjustment framework warrants investigation. Data-driven selection of the number of strata K (currently set exogenously) is needed for practical application. The addition of non-linear Z→X relationships and interactions to the data-generating mechanism would test robustness beyond the linear case. Empirical validation on individual-level clinical databases with genuinely unmeasured confounders (e.g. MIMIC-IV, UK Biobank) would provide a stronger test of the method's practical utility. Formal calibration of C1 and W thresholds across diverse clinical settings is needed before diagnostic recommendations can be made. Finally, the development of software packages (R and Python) implementing the IONE workflow would facilitate adoption.

---

## Conclusions

We have introduced IONE (Incoherence-Oriented Neutralisation and Extraction), a framework for detecting hidden population structure arising from unmeasured effect modification and confounding in observational studies. Through Monte Carlo simulation (130,950 evaluations, benchmarked against active comparators) and five semi-synthetic illustrations from published Simpson's paradox examples, we demonstrate that IONE provides two complementary exploratory diagnostics. C1 (between-stratum heterogeneity indicator) detects whether stratum-specific treatment effects differ across strata, providing evidence of population incoherence. W (within-stratum homogeneity indicator) assesses whether stratification has successfully isolated individuals with similar treatment effects. Stratification-based extraction is most effective when unmeasured effect modifiers leave sufficiently strong traces in measured variables and the subgroup structure is discrete, though extraction accuracy in the primary simulation was modest. The C1 and W indicators are intended as exploratory diagnostics to complement established confounding adjustment methods such as propensity score analysis, not to replace them. Further calibration and validation on individual-level clinical data are needed before clinical recommendations can be made.

---

## List of abbreviations

| Abbreviation | Full term |
|-------------|-----------|
| ADEMP | Aims, Data-generating mechanisms, Estimands, Methods, Performance measures |
| ARI | Adjusted Rand Index |
| ATE | Average treatment effect |
| BMI | Body mass index |
| C1 | Between-stratum heterogeneity indicator (1 − I²) |
| CATE | Conditional average treatment effect |
| CFR | Case fatality rate |
| DAG | Directed acyclic graph |
| DRS | Disease risk score |
| EM | Effect modification |
| GMM | Gaussian mixture model |
| hdPS | High-dimensional propensity score |
| IONE | Incoherence-Oriented Neutralisation and Extraction |
| IV | Instrumental variable |
| MC SE | Monte Carlo standard error |
| NMI | Normalised Mutual Information |
| OR | Odds ratio |
| PCA | Principal component analysis |
| PS | Propensity score |
| RCT | Randomised controlled trial |
| W | Within-stratum homogeneity indicator |

## Declarations

### Ethics approval and consent to participate

Not applicable. This study used simulated data and publicly available aggregate statistics only.

### Consent for publication

Not applicable.

### Availability of data and materials

The simulation code and analysis scripts are available at https://github.com/bougtoir/ione-stratification-framework. The published datasets used for the semi-synthetic illustrations are referenced in the original publications [9–13].

### Competing interests

The authors declare that they have no competing interests.

### Funding

No specific funding was received for this study.

### Authors' contributions

TO conceived the study, developed the framework and simulation code, conducted all analyses, and wrote the manuscript.

### Acknowledgements

Not applicable.

---

## References

1. Hammerton G, Munafò MR. Causal inference with observational data: the need for triangulation of evidence. *Psychol Med*. 2021;51(4):563–78.
2. Hernán MA, Robins JM. *Causal Inference: What If*. Boca Raton: Chapman & Hall/CRC; 2020.
3. VanderWeele TJ, Shpitser I. On the definition of a confounder. *Ann Stat*. 2013;41(1):196–220.
4. Simpson EH. The interpretation of interaction in contingency tables. *J R Stat Soc Ser B*. 1951;13(2):238–41.
5. Rojanaworarit C. Misleading epidemiological and statistical evidence in the presence of Simpson's paradox: an illustrative study using simulated scenarios. *J Med Life*. 2020;13(1):37–44.
6. VanderWeele TJ, Knol MJ. A tutorial on interaction. *Epidemiol Methods*. 2014;3(1):33–72.
7. Robinson WS. Ecological correlations and the behavior of individuals. *Am Sociol Rev*. 1950;15(3):351–7.
8. Greenland S, Robins JM, Pearl J. Confounding and collapsibility in causal inference. *Stat Sci*. 1999;14(1):29–46.
9. Charig CR, Webb DR, Payne SR, Wickham JE. Comparison of treatment of renal calculi by open surgery, percutaneous nephrolithotomy, and extracorporeal shockwave lithotripsy. *BMJ*. 1986;292(6521):879–82.
10. Bickel PJ, Hammel EA, O'Connell JW. Sex bias in graduate admissions: data from Berkeley. *Science*. 1975;187(4175):398–404.
11. von Kügelgen J, Gresele L, Schölkopf B. Simpson's paradox in Covid-19 case fatality rates: a mediation analysis of age-related causal effects. *IEEE Trans Artif Intell*. 2021;2(1):18–27.
12. Morris JA. Israeli data: how can efficacy vs. severe disease be 91.4% when 60% of severe cases are vaccinated? COVID-19 Data Science. 2021 [cited 2026 May 1]. Available from: https://www.covid-datascience.com/post/israeli-data-how-can-efficacy-vs-severe-disease-be-91-when-60-of-severe-cases-are-vaccinated. Note: This is a data analysis blog post, not a peer-reviewed publication. It is cited here solely as the source of the aggregate data used to reconstruct individual-level data for the semi-synthetic illustration.
13. Appleton DR, French JM, Vanderpump MPJ. Ignoring a covariate: an example of Simpson's paradox. *Am Stat*. 1996;50(4):340–1.
14. Rosenbaum PR, Rubin DB. The central role of the propensity score in observational studies for causal effects. *Biometrika*. 1983;70(1):41–55.
15. Hansen BB. The prognostic analogue of the propensity score. *Biometrika*. 2008;95(2):481–8.
16. Aikens RC, Greaves D, Baiocchi M. A pilot design for observational studies: using abundant data thoughtfully. *Stat Med*. 2020;39(29):4349–69.
17. Miettinen OS. Stratification by a multivariate confounder score. *Am J Epidemiol*. 1976;104(6):609–20.
18. Angrist JD, Imbens GW, Rubin DB. Identification of causal effects using instrumental variables. *J Am Stat Assoc*. 1996;91(434):444–55.
19. Schneeweiss S, Rassen JA, Glynn RJ, Avorn J, Mogun H, Brookhart MA. High-dimensional propensity score adjustment in studies of treatment effects using health care claims data. *Epidemiology*. 2009;20(4):512–22.
20. Rassen JA, Schneeweiss S. Using high-dimensional propensity scores to automate confounding control in a distributed medical product safety surveillance system. *Pharmacoepidemiol Drug Saf*. 2012;21(S1):41–9.
21. Wyss R, Schneeweiss S, van der Laan M, Lendle SD, Ju C, Franklin JM. Machine learning for improving high-dimensional proxy confounder adjustment in healthcare database studies. *Stat Med*. 2018;37(8):1310–24.
22. Tchetgen Tchetgen EJ, Ying A, Cui Y, Shi X, Miao W. An introduction to proximal causal inference. *Stat Sci*. 2024;39(3):375–90.
23. McLachlan GJ, Peel D. *Finite Mixture Models*. New York: Wiley; 2000.
24. Hayes-Larson E, Kezios KL, Mooney SJ, Lovasi G. Who is in this study, anyway? Guidelines for a useful Table 1. *J Clin Epidemiol*. 2019;114:125–32.
25. Higgins JPT, Thompson SG. Quantifying heterogeneity in a meta-analysis. *Stat Med*. 2002;21(11):1539–58.
26. Morris TP, White IR, Crowther MJ. Using simulation studies to evaluate statistical methods. *Stat Med*. 2019;38(11):2074–102.
27. Hubert L, Arabie P. Comparing partitions. *J Classif*. 1985;2(1):193–218.
28. Strehl A, Ghosh J. Cluster ensembles—a knowledge reuse framework for combining multiple partitions. *J Mach Learn Res*. 2002;3:583–617.

---

## Additional files

### Additional file 1: Supplementary Methods

Detailed description of the pseudo-general variable generation procedure for each of the five Simpson's paradox examples, including the correlation structures imposed between pseudo-general variables and the known confounding variable.

#### Pseudo-general variable generation

For each of the five published Simpson's paradox examples, we reconstructed individual-level data from published aggregate tables and generated ten pseudo-general variables X₁–X₁₀ to serve as measured covariates carrying traces of the known confounding variable Z.

**Step 1: Individual-level reconstruction.** From each published 2×2×K contingency table (treatment × outcome × confounder level), we expanded the cell counts into individual-level records. Each individual was assigned Z (the known confounder), A (treatment), and Y (outcome) consistent with the published marginal and stratum-specific frequencies.

**Step 2: Pseudo-general variable generation.** For each individual, ten continuous variables X₁–X₁₀ were generated from a multivariate normal distribution conditional on the confounder value Z:

$$X_j | Z = z \sim N(\mu_j(z), \sigma_j^2)$$

where the conditional mean $\mu_j(z)$ was defined to create a specified correlation between X_j and Z. The first five variables (X₁–X₅) were generated with strong Z-dependence (correlation ≈ 0.7), and the remaining five (X₆–X₁₀) with moderate Z-dependence (correlation ≈ 0.3). Independent noise $\epsilon \sim N(0, 0.5)$ was added to prevent perfect collinearity.

**Step 3: Treatment model.** A binary treatment A was generated from a logistic model incorporating both confounding (Z→A) and measured covariate effects (X→A), calibrated to match the published treatment prevalence within each confounder stratum.

**Step 4: Outcome model.** The binary outcome Y was generated from a logistic model including Z→Y (direct confounding), A→Y (treatment effect), Z×A→Y (effect modification), and X→Y (weak measured covariate effects), calibrated to match the published stratum-specific outcome rates.

#### Example-specific parameters

**Example 1 (Kidney stone treatment [9]):** Z = stone size (small/large), A = treatment type (open surgery/percutaneous nephrolithotomy), Y = success. K = 2 confounder levels.

**Example 2 (Berkeley admissions [10]):** Z = department (A–F), A = sex (male/female), Y = admission. K = 6 confounder levels. For pseudo-variable generation, departments were encoded as ordinal (1–6).

**Example 3 (COVID-19 case fatality [11]):** Z = age group (young/old), A = country (China/Italy), Y = fatality. K = 2 confounder levels.

**Example 4 (Israeli vaccination [12]):** Z = age group (<50/≥50), A = vaccination status, Y = severe disease. K = 2 confounder levels.

**Example 5 (Smoking and survival [13]):** Z = age group (categorised), A = smoking status, Y = 20-year survival. K = 3 confounder levels.

### Additional file 2: ADEMP Checklist

**Table S1.** ADEMP checklist for the simulation study.

| ADEMP component | Item | Section |
|----------------|------|---------|
| **Aims** | | |
|| Specific aims stated | Evaluate subgroup recovery, benchmark against active comparators, assess C1 and W indicators, quantify bias reduction | Methods: Aims |
| **Data-generating mechanisms** | | |
| Causal structure described | DAG with Z→X, Z→A, X→A, A→Y, Z→Y, Z×A→Y pathways | Methods: Data-generating mechanisms |
| Variable distributions specified | Z₁ ~ N(60,144), Z₂ ~ Bern(0.5), Z₃ ~ Multinomial; X generated from Z with specified influence; Y from logistic model | Methods: Data-generating mechanisms |
| Factors varied and levels stated | Z→X influence (0.2–1.0), N (500–10,000), K (3–10), Z→Y effect (0.5–2.0) | Methods: Scenarios |
| Justification for DGM choices | Clinical relevance: Z represents age/sex/BMI; X represents lab values; event rate 10–20% | Methods: Data-generating mechanisms |
| Number of repetitions and justification | 200 per scenario (Phase 1); total 130,950 evaluations | Methods: Scenarios |
| **Estimands** | | |
| Estimands defined | Subgroup recovery (ARI), trace capture (η²), C1, W, ATE bias reduction | Methods: Estimands |
| **Methods** | | |
| All methods described | 6 proposed + 4 comparators + 6 PCA variants + 2 baselines (18 total) | Methods: Methods under comparison |
| Rationale for method selection | Two families testing distinct hypotheses (outcome-informed vs. outcome-free) | Methods: Methods under comparison |
| **Performance measures** | | |
| Performance measures listed with formulae | ARI, η², C1, W, NMI, ATE bias reduction, direction consistency, CATE η² | Methods: Performance measures |
| Monte Carlo SE reported | Yes, for all primary measures | Methods: Performance measures |

### Additional file 3: STROBE-Sim Checklist

**Table S2.** STROBE-Sim reporting checklist for the simulation study (adapted from Burton et al. 2006 and Morris et al. 2019).

| Item | STROBE-Sim recommendation | Reported | Location in manuscript |
|------|--------------------------|----------|----------------------|
| **Title and abstract** | | | |
| 1a | Indicate simulation study in title | Yes | Title explicitly includes "Monte Carlo Simulation Study" |
| 1b | Structured abstract with aims, methods, key results, conclusions | Yes | Abstract |
| **Introduction** | | | |
| 2 | Scientific background and rationale | Yes | Background |
| 3 | Specific objectives or hypotheses | Yes | Background, final paragraph |
| **Methods** | | | |
| 4 | Study design (simulation + empirical) | Yes | Methods: opening paragraph |
| 5 | Data-generating mechanism: causal structure (DAG) | Yes | Methods: Data-generating mechanisms |
| 6 | Data-generating mechanism: variable distributions | Yes | Methods: Data-generating mechanisms |
| 7 | Data-generating mechanism: outcome model | Yes | Methods: Data-generating mechanisms (Outcome model) |
| 8 | Factors varied systematically | Yes | Methods: Scenarios (Tables) |
| 9 | Number of repetitions with justification | Yes | Methods: Scenarios |
| 10 | Estimands clearly defined | Yes | Methods: Estimands |
| 11 | All methods under comparison described | Yes | Methods: Methods under comparison |
| 12 | Performance measures with formulae/definitions | Yes | Methods: Performance measures |
| 13 | Software and computational details | Yes | Methods: Computational implementation |
| 14 | Coding verification / validation | Partial | Reproducibility via fixed seeds; code availability stated |
| **Results** | | | |
| 15 | Number of simulations completed vs. planned | Yes | Results: 130,950 evaluations |
| 16 | Summary of performance measures across scenarios | Yes | Results: Tables 2–7 |
| 17 | Presentation of results for each estimand | Yes | Results (ARI, η², C1 reported separately) |
|| 18 | Monte Carlo standard errors | Yes | All tables in Results section |
| **Discussion** | | | |
| 19 | Summary of key findings | Yes | Discussion: Principal findings |
| 20 | Comparison with previous studies | Yes | Discussion: Comparison with existing methods |
| 21 | Limitations of simulation design | Yes | Discussion: Strengths and limitations |
| 22 | Generalisability of findings | Yes | Discussion: Implications for practice |
| **Other information** | | | |
| 23 | Source of funding | Yes | Declarations: Funding |
| 24 | Code availability | Yes | Declarations: Availability of data and materials |
| 25 | Role of funder | N/A (no specific funding) | Declarations: Funding |

### Additional file 4: Supplementary Results

Full results tables for all sensitivity analysis conditions, including per-scenario ARI, η², C1, W, and bias reduction values. Available as a downloadable CSV file in the code repository.

---

*Manuscript prepared for submission to BMC Medical Research Methodology*
*Target collection: Causal inference and observational data vol. 2*
*Submission deadline: 30 July 2026*
