# Point-by-point response to reviewers — IONE resubmission

> This response accompanies the revised manuscript for submission to *Statistical Methods in Medical Research* (with *Statistics in Medicine* and *Journal of Causal Inference* as alternative targets). The manuscript has been reframed as an **exploratory diagnostic-sensitivity study** rather than a mature two-stage workflow. All numerical results in the revised manuscript are generated from an updated, version-locked simulation pipeline; the revisions described below reflect the final analytical plan.

---

## Editor (BMC Medical Research Methodology — decision letter)

### Editorial assessment
> The revised manuscript should clarify the conceptual scope, align the motivation with the evaluation design, include appropriate comparator methods, report uncertainty around simulation results, address the limited extraction performance, complete all missing supplementary/code/materials, and substantially temper claims that are not supported by the current evidence.

**Response.** We have restructured the manuscript around a single, well-defined scope: detecting hidden population structure caused by **unmeasured effect modification and confounding** in observational studies. Simpson’s paradox is now treated as an extreme manifestation of these two phenomena; ecological fallacy and non-collapsibility are explicitly noted as related but distinct and are not claimed to be addressed by IONE. The evaluation design has been realigned: the data-generating mechanism now generates a binary treatment A, includes both confounding (Z → A, Z → Y) and effect modification (Z × A → Y), and reports Monte Carlo standard errors for every summary statistic. Three active comparators (propensity-score quintiles, Gaussian mixture model, prognostic score) are included in the revised simulation. Extraction performance is described as “modest” and conditional on strong Z→X traces; the primary contribution is repositioned as the C1/W diagnostic indicators. All supplementary tables, the ADEMP checklist, the STROBE-Sim checklist and a permanent code archive (tagged GitHub release / Zenodo DOI) will be supplied.

---

## Reviewer 1

### R1.1 — W is an oracle metric
> W is computed from the true CATE and is therefore not available in a real observational study. The claim that W may be “the more useful diagnostic in practice” is not supported.

**Response.** W has been split into two distinct quantities:
- **W_true** = 1 − (weighted within-stratum CATE variance / overall CATE variance), computed from the known DGM and reported **only as a simulation evaluation metric**.
- **W_est** = the same quantity computed from an estimated CATE based only on observed (X, A, Y), using a flexible outcome model. W_est is reported alongside W_true as an operational diagnostic.

The Abstract, Methods, Results and Conclusions now describe W as a **simulation-limited performance measure** when based on the true CATE, and as an **exploratory diagnostic** (with calibration caveats) when based on an estimated CATE. We no longer claim that W is “more useful in practice” without empirical calibration.

### R1.2 — C1 is given too much diagnostic weight
> In the primary simulation C1 values are very similar across methods (0.77–0.88), including random stratification, so C1 does not separate proposed methods from noise. Either calibrate C1 empirically or further downgrade its role.

**Response.** We downgrade C1 to an **exploratory, uncalibrated diagnostic** rather than a formal decision rule. The provisional threshold C1 < 0.05 has been removed from claims and replaced with a calibration narrative. We added a **calibration-curve figure** that shows C1 distributions across regimes (random stratification, weak/strong Z→X, discrete/continuous Z, finite samples and oracle baselines). The Discussion explicitly states that C1 based on stratum-specific log odds ratios has limited discriminating power in the primary simulation and requires external calibration before applied use.

### R1.3 — Extraction performance is very small in the realistic simulation
> The best proposed method has ARI = 0.021 vs. oracle k-means ARI = 0.353. ARI > 0.7 appears only in the optimistic semi-synthetic examples. The abstract and conclusions should frame extraction as not yet convincingly successful.

**Response.** We agree. The Abstract and Conclusions now state that stratification-based extraction is **conditionally and partially successful**: it is strongest when the confounder leaves strong traces in measured variables and the hidden structure is discrete or low-dimensional, and is modest under the primary simulation. The term “two-tier workflow” has been removed; the paper is positioned as a **sensitivity/diagnostic study** that asks whether a population shows evidence of hidden structure, not as a tool that reliably recovers that structure.

### R1.4 — Bias-reduction numbers are inconsistent
> The Methods define bias reduction as 1 − |bias_stratified| / |bias_crude|, but the reported 7.4% is the absolute difference, not the relative percentage.

**Response.** We have reconciled the definition and the estimand. Because log-odds ratios are non-collapsible, stratum-specific log-ORs do not average to the marginal treatment effect, so we now target the **population risk-difference ATE** and report bias reduction on the risk-difference scale:

```
absolute bias reduction = |bias_crude| − |bias_stratified|
relative bias reduction = 1 − |bias_stratified| / |bias_crude|
bias = (estimated ATE) − (true ATE)
```

The crude estimate is the marginal risk difference P(Y=1|A=1) − P(Y=1|A=0); the stratified estimate is the sample-size weighted average of stratum-specific risk differences. Both absolute and relative reduction are reported where useful. All tables, figure captions and prose have been edited for internal consistency.

### R1.5 — The recovery target is a post-hoc partition of partly continuous Z
> ARI is often measuring agreement with a constructed clustering target rather than recovery of natural subgroups.

**Response.** We added an explicit caveat in the Methods and Discussion: the “true” subgroup labels are an operational k-means partition of the standardised Z-space with K set to the number of strata, and therefore ARI measures agreement with a **constructed reference partition**, not necessarily with natural clinical subgroups. This distinction is now stated in the ARI definition and in the Discussion.

### R1.6 — “Neutralisation” is not clearly operationalised
> The term in the acronym is not clearly operationalised.

**Response.** “Neutralisation” is now explicitly defined as **“bias reduction achieved by stratification-adjusted estimation relative to the crude marginal estimate.”** We avoid language that suggests a causal removal of confounding. The acronym IONE is retained, but the operational meaning is given on first use.

### R1.7 — Additional file 1 inconsistencies
> Step 1 says A and Y are reconstructed from published tables, but Steps 3–4 describe A and Y as generated from logistic models. Confounder-level counts differ from Table 1.

**Response.** Additional file 1 has been rewritten to distinguish clearly between **reconstructed variables** (Z, A, Y from the published contingency table) and **simulated pseudo-general variables** (X₁–X₁₀ generated to mimic measured proxies of Z). Group counts for every example have been cross-checked against Table 1 and the published sources.

---

## Reviewer 2

### R2.1 — Correct the bias-reduction definition and all reported values
> Choose either absolute or relative bias reduction and make the formula, table headings, Abstract, Results and Discussion consistent.

**Response.** Same as R1.4. We now use **absolute risk-difference bias reduction** as the primary reported quantity because the risk difference is collapsible and directly estimates the population ATE. Relative reduction is provided as a secondary metric. The formula is stated unambiguously in the Methods.

### R2.2 — Clarify the ground-truth subgroup definition and oracle ARI results
> If the true structure is k-means on Z, an oracle that applies k-means to Z should have ARI near 1, not 0.353. If the true partition is based on discrete categories, define it explicitly.

**Response.** We redefined the **primary ground-truth partition** for the simulation as the Cartesian product of **discretised clinical categories**: age (<45, 45–70, >70), sex (0/1) and BMI category (0/1/2). With n_z_vars = 3 this gives up to 18 clinically meaningful cells; for K = 3, 5, 10 strata we either collapse to the ordered Z1 quantiles or to the full Cartesian product where K matches the cell count. The **oracle** is now described as the partition of Z that maximises ARI for the chosen K: quantile-based when K matches the number of Z1 categories, and k-means on standardised Z when K does not. ARI for the oracle is near 1 whenever K equals the number of true discrete categories, and lower when the oracle must approximate a continuous Z via k-means. This explanation is added to the Methods and the Discussion of oracle baselines.

### R2.3 — Reframe W unless a feasible real-data estimator is evaluated
> W is defined using true CATE. Either provide a practical estimation workflow or label W as simulation-only.

**Response.** Same as R1.1. We now report both W_true (simulation-only) and W_est (estimated from observed data), and W is explicitly framed as a **simulation performance metric** unless calibrated.

### R2.4 — Address the remaining circularity in outcome-informed residual stratification
> Method 1B assigns strata using |Y − p̂|. Estimating treatment effects within strata defined partly by the outcome risks collider/selection bias. Restrict residual stratification to exploratory diagnostics, use discovery/evaluation split, or add a sensitivity analysis.

**Response.** We have implemented a **discovery/evaluation split** for all outcome-informed methods: stratum assignment is learned on a 50% discovery sample and treatment-effect estimation (risk-difference ATE, C1, W_est) is performed on the independent 50% evaluation sample. A new sensitivity analysis reports the **induced bias** from using the same data for both assignment and estimation, showing that sample splitting materially reduces this bias. The Discussion states that residual-based stratification is **exploratory only** and should not be used for confirmatory effect estimation without an independent evaluation set.

### R2.5 — Temper the claim that C1 detects population incoherence
> C1 values in the main simulation overlap heavily across methods and do not establish detection performance.

**Response.** Same as R1.2. C1 is repositioned as an **exploratory, uncalibrated heterogeneity indicator**. We removed the C1 < 0.05 threshold from applied recommendations and added a calibration-curve analysis across regimes.

### R2.6 — Align the semi-synthetic claims with the reported results
> The Abstract claims all methods achieved ARI > 0.7, but Table 11 shows only kidney stone (0.851) and Israeli vaccine (0.746); smoking mortality (0.498), UC Berkeley (0.082) and COVID-19 CFR (0.064) are much lower.

**Response.** The Abstract has been corrected to state that **some** semi-synthetic examples with strong, simple confounder structures yield ARI > 0.7 (kidney stone, Israeli vaccine), whereas examples with multi-level confounders (UC Berkeley, COVID-19 CFR) remain below 0.1. The Results and Conclusions now include this explicit cross-example comparison and reiterate that the high-ARI cases are optimistic because the pseudo-general variables were engineered to carry strong traces of the known confounder.

### R2.7 — Resolve the method-count and comparator taxonomy inconsistencies
> The response letter says four active comparators were added, including k-means; the Abstract says three active comparators; the Methods text refers to 18 methods; the method list elsewhere refers to three active comparators. Clarify whether k-means on covariates is an IONE method, an active comparator, or both.

**Response.** We have created a single, exact method inventory used throughout, which matches the public repository exactly:

| Class | Methods |
|-------|---------|
| Proposed IONE methods (Family 1: outcome-informed) | 1A predicted probability, 1B residual, 1C cross-validated decision power, 1D ML uncertainty |
| Proposed IONE methods (Family 2: outcome-free) | 2A PCA (six cumulative-variance / fixed-k configurations), 2B k-means on X |
| Active comparators | PS quintiles, Gaussian mixture model, prognostic score |
| Oracle baselines | Oracle k-means on Z, oracle quantile on Z1 |
| Lower baseline | Random stratification |

The Methods enumerate the full list without contradiction. K-means on X (2B) is a proposed IONE method, not a comparator; the three active comparators are PS, GMM and prognostic-score stratification.

### R2.8 — Continue removing language that implies subgroup recovery
> Phrases such as “extracting coherent subpopulations” and “recovering hidden structure” should be used sparingly.

**Response.** We have systematically replaced recovery-oriented language with **exploratory/diagnostic language** throughout the Abstract, Background, Methods, Results and Conclusions. “Recovery” is used only when qualified as partial or conditional.

### R2.9 — Replace or define “coherence degree”
> The Background still refers to a quantitative “coherence degree.”

**Response.** The term “coherence degree” has been removed. The paper now uses only the explicitly defined indicators **C1** (between-stratum heterogeneity) and **W** (within-stratum homogeneity).

### R2.10 — Explain why Method 1B should reveal hidden structure beyond outcome labeling
> Residual stratification for binary outcomes depends directly on Y, so readers need a rationale for why it captures hidden structure rather than grouping by observed outcome and predicted risk.

**Response.** We added a paragraph explaining that under the data-generating model with unmeasured effect modification, the **residual |Y − p̂| is large when the observed Y is poorly explained by the measured covariates X alone**, which occurs precisely where unmeasured Z strongly influences the outcome. Because the residual is computed from a model that does not include Z, systematic residual patterns can reveal the footprint of Z. We also note the limitation: for a binary outcome the residual is a label-dependent transformation of predicted probability, so it is primarily a **ranking of unexplained outcome heterogeneity**, not a direct measure of Z.

### R2.11 — Give enough implementation detail outside the code repository
> Report regularization, standardization, RF settings, k-means initialization/starts, GMM covariance, convergence, random seeds.

**Response.** A new **Supplementary Methods** appendix lists all algorithmic settings: LogisticRegression (l2 penalty, C=1.0, lbfgs solver, max_iter=1000), RandomForest (n_estimators=100, max_depth=10, random_state=42), k-means and GMM (n_init=10, random_state=42, default scikit-learn covariance settings), standardization (StandardScaler before PCA/k-means), seeds and convergence handling. These details are also summarised in a table in the main Methods.

### R2.12 — Explain why oracle baselines are not upper bounds for every metric
> Method 1B appears to outperform oracle baselines for bias reduction, and oracle quantile has higher W than oracle k-means.

**Response.** We added an explanation in the Discussion: the oracle k-means baseline is optimised for **Z-recovery (ARI)**, not for ATE bias reduction. A Z-based partition may not coincide with the partition that minimises ATE bias because the ATE estimand depends on the joint distribution of Z and X and on the outcome model. Similarly, oracle quantile on Z1 can yield more homogeneous within-stratum CATEs than k-means on the full Z when only Z1 drives effect modification. Therefore no oracle is an upper bound for every metric.

### R2.13 — Handle the C1 threshold cautiously
> The Discussion mentions a provisional C1 < 0.05 threshold, but the main simulation produces C1 values around 0.8 for most methods.

**Response.** Same as R1.2/R2.5. The threshold has been removed from recommendations; C1 is presented as an exploratory indicator requiring calibration.

### R2.14 — Check table numbering and supplemental labeling
> Main-text and supplementary tables should be numbered distinctly and cited unambiguously.

**Response.** All tables have been renumbered. Main-text tables are numbered 1–9; supplementary tables are labelled Table S1, S2, … and listed in a Supplementary Materials document. Each table is cited in the main text before it first appears.

### R2.15 — Use comparator names consistently
> Use either “propensity score quintiles” or “PS quintiles” consistently; distinguish prognostic score from disease risk score.

**Response.** Standardised abbreviations are used after first definition: PS-Q (propensity-score quintiles), GMM (Gaussian mixture model), Prog (prognostic score). The prognostic score is explicitly distinguished from the disease risk score (DRS) in the Background.

### R2.16 — Qualify the Morris 2021 source in the main text
> Morris 2021 is a blog post, not a peer-reviewed publication; the Results text should not call all five examples “published instances” without qualification.

**Response.** The main text now describes the Israeli vaccine source as a **publicly available aggregate data-analysis example**, and the reference note states that it is not peer-reviewed. The phrase “five published instances” has been replaced with “five well-known Simpson’s paradox examples, four from peer-reviewed literature and one from a public data analysis.”

### R2.17 — Add a permanent code archive or commit hash
> A GitHub URL improves reproducibility, but a tagged release or DOI would be more durable.

**Response.** We will create a **tagged GitHub release** and, if possible, a Zenodo DOI before final submission. The Data Availability statement will include the exact commit hash and the release DOI.

---

## Reviewer 3

### R3.1 — Population incoherence and latent class models
> Latent class models are a standard approach for identifying hidden subgroups with heterogeneous treatment effects. The distinction from IONE should be clarified.

**Response.** We added a paragraph in the Background/Discussion clarifying the difference: **latent class / finite mixture models** infer unobserved subgroups from the joint distribution of observed variables under parametric distributional assumptions and typically target the latent-class membership distribution. **IONE** treats the observed population as potentially non-coherent, uses routine measured variables to stratify the observed sample, and provides a coherence diagnostic (C1/W) before any subgroup-specific analysis. IONE does not estimate a latent-class model; it is a preprocessing/exploratory diagnostic that can be applied before standard methods.

### R3.2 — Recovering stratification from unmeasured confounders
> The claim that stratification based on important measured variables can be recovered from unmeasured confounders is overly strong. The simulation settings are also favourable.

**Response.** We have weakened the claim to **partial recovery under favourable conditions**. The Abstract and Discussion now state that recovery is partial, depends on strong Z→X traces and simple hidden structure, and is modest in the primary simulation. We have also broadened the sensitivity analysis to include weaker Z→X signals, smaller sample sizes and non-linear Z→X mappings.

### R3.3 — Assumption regarding unmeasured effect modifiers
> The assumption that unmeasured effect modifiers influence both measured covariates and the treatment effect is restrictive and unlikely to hold in many practical situations.

**Response.** We added a dedicated **Assumptions and limitations** paragraph. The key assumption (Z → X and Z × A → Y) is now explicitly stated, its plausibility is discussed (e.g. age/severity influencing both lab values and treatment benefit), and the consequences of violations are described. The Discussion notes that IONE is most promising when the hidden modifier is known to influence routinely measured variables.

### R3.4 — Specification of the outcome model
> Why were X–Z and X–A interactions not included? When A interacts with Z, τ is no longer the main treatment effect; clarify the interpretation.

**Response.** We added an **Outcome model** paragraph that justifies the parsimonious model (A + Z + Z×A + X + noise). X–Z and X–A interactions are now explored in a **sensitivity analysis**; the main model is shown to be the primary DGM, with the richer model reported in Supplementary Table S3. We clarify that **τ is the log-OR of A at the reference level of Z** (Z = 0 / standardised mean), not the marginal treatment effect, and that effect modification is represented by the δ·Z×A terms.

### R3.5 — Definition of the true subgroup structure
> The true subgroup structure is defined using k-means, which is crude. What is the precise definition of a hidden subgroup?

**Response.** Same as R2.2. The primary true structure is now defined by **discrete clinical categories of Z** (age group × sex × BMI category). K-means is used only as an approximation when K does not match the number of discrete cells, and this is explicitly stated.

### R3.6 — Definition of the oracle method
> The oracle is not appropriately defined. If Z is observed, a method that does not observe Z should not outperform the oracle.

**Response.** Same as R2.2 and R2.12. We now define the oracle as the Z-based partition that is optimal for the specific metric in question, explain that different oracle definitions (k-means vs. quantile) optimise different objectives, and note that outcome-informed methods can outperform an ARI-optimised oracle on bias-reduction because the two metrics target different partitions.

---

## Reviewer 4

### R4.1 — Define the causal/statistical estimand
> The manuscript should clearly define the estimand targeted by IONE.

**Response.** The revised Methods include an **Estimands** subsection that defines the quantities reported in the simulation:

1. The **population risk-difference ATE**: τ = E[Y(1) − Y(0)], estimated by the sample-size weighted average of stratum-specific risk differences.
2. The **crude marginal risk difference**: P(Y=1|A=1) − P(Y=1|A=0).
3. **Bias reduction**: absolute and relative reduction in |estimated ATE − true ATE|.
4. **C1**: 1 − I² from stratum-specific log odds ratios of A → Y, an exploratory between-stratum heterogeneity indicator.
5. **W**: within-stratum homogeneity of true (W_true, simulation-only) or estimated (W_est) CATE risk differences.

IONE is positioned as an exploratory diagnostic/preprocessing step that identifies populations that may warrant subgroup-specific analysis, not as a complete causal inference method.

### R4.2 — C1 interpretation: between-stratum heterogeneity ≠ within-stratum homogeneity
> The interpretation of C1 needs substantial clarification.

**Response.** Same as R1.2/R2.5/R2.12. The distinction is now explicit: C1 measures whether strata differ from one another; W measures whether individuals within strata are similar. Both are needed to diagnose population incoherence. A new two-by-two diagnostic table (low/high C1 × low/high W) is included to guide interpretation.

### R4.3 — The C1 < 0.05 threshold appears premature
> C1 values around 0.8 in the main simulation make a 0.05 threshold inappropriate.

**Response.** Same as R1.2/R2.13. The threshold is removed and replaced with calibration curves and explicit caveats.

### R4.4 — Subgroup recovery is quite limited
> Extraction performance is modest, so claims should be tempered.

**Response.** Same as R1.3/R2.8. The primary contribution is repositioned as diagnostic; extraction is described as conditional and modest.

### R4.5 — Provide stronger evidence that IONE improves downstream inference
> The manuscript should show that IONE improves treatment-effect estimation.

**Response.** We added **ATE bias reduction on the risk-difference scale** as a primary performance measure and report it for every method. The treatment-effect estimation uses an independent evaluation split (see R2.4), and the Discussion explicitly ties the bias-reduction results to the practical question of whether IONE improves downstream inference. We note that gains are modest and require strong Z→X signals.

### R4.6 — Outcome-informed stratification raises overfitting concerns
> Sample splitting should separate model building from evaluation.

**Response.** Same as R2.4. All outcome-informed methods now use a 50/50 discovery/evaluation split; treatment-effect estimation and C1/W_est computation are performed only on the evaluation sample.

### R4.7 — Empirical examples should not be described as empirical validation
> The semi-synthetic examples are illustrations, not validation.

**Response.** The section title has been changed from “Empirical validation” to **“Semi-synthetic illustrations.”** The opening and closing paragraphs explicitly state that pseudo-general variables are generated by design and that results cannot be interpreted as out-of-the-box real-data performance.

### R4.8 — The abstract and conclusions should not claim C1 as a standard reporting component
> C1 should not be claimed as a standard reporting component.

**Response.** The claim has been removed. C1 and W are now described as **exploratory diagnostics to complement, not replace, established confounding-adjustment methods**. The Conclusions add that further calibration on individual-level clinical data is needed before any clinical recommendation can be made.

### R4.9 — Sample size vs. precision distinction
> Distinguish subgroup recovery (ARI) from precision of C1/treatment-effect estimates.

**Response.** A new paragraph in the Results distinguishes **recovery performance** (ARI, which is largely insensitive to N in the tested range) from **estimation precision** (MC SE of C1, W and log-ORs, which decreases with N). This distinction is also noted in the Discussion.

### R4.10 — Empirical examples have different structures
> Discuss comparability across the five examples.

**Response.** We added a **Comparability** paragraph in the Results explaining how differences in group numbers, sample sizes, and pseudo-variable correlation structures affect cross-example comparisons. The kidney-stone and Israeli-vaccine examples are highlighted as simple, high-trace cases; UC Berkeley and COVID-19 CFR as multi-level, low-trace cases.

---

## Summary of principal changes for the revised submission

1. **Scope and framing** — repositioned as an exploratory diagnostic-sensitivity study; removed claims that IONE is a mature two-stage workflow or a standard reporting component.
2. **Data-generating mechanism** — added binary treatment A, explicit confounding and effect modification, and X–Z/X–A interaction sensitivity analyses.
3. **Method inventory** — three active comparators (PS-Q, GMM, prognostic score) plus proposed IONE methods and oracle baselines; taxonomy is now consistent across Abstract, Methods, tables and response.
4. **Metrics and estimand** — redefined the ATE estimand as the risk difference (collapsible) and report bias reduction on that scale; redefined C1 as an exploratory, uncalibrated heterogeneity indicator; added true and estimated W; reconciled bias-reduction formula and values; added calibration curves.
5. **Bias and circularity** — implemented discovery/evaluation split for all outcome-informed methods and quantified induced-bias sensitivity.
6. **Semi-synthetic illustrations** — corrected over-claims; added comparability discussion; renamed section.
7. **Reproducibility** — added ADEMP/STROBE-Sim checklists, detailed algorithm settings, tagged GitHub release / Zenodo DOI to be generated before submission.
