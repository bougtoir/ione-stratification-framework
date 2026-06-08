# Point-by-Point Response to Reviewers

## IONE: Incoherence-Oriented Neutralisation and Extraction for Detecting Hidden Population Structure in Observational Studies — a Monte Carlo Simulation Study

Submission ID: 7f49c954-3442-436d-8bdd-ea6aa9468caf

---

We thank the Editor and all four Reviewers for their thoughtful and constructive comments. Their feedback has led to substantial improvements in the manuscript. Below we provide a point-by-point response to each comment, with references to the relevant changes in the revised manuscript. Throughout, **bold text** indicates the reviewer's comment in summary, and our response follows.

### Summary of major changes

The following major changes were made in response to reviewer feedback:

1. **Treatment variable added to the simulation** (R1§2, R2§2, R3§1, R4§5): The data-generating mechanism now includes a binary treatment A with confounding (Z→A), treatment effect (A→Y), and effect modification (Z×A→Y). The true conditional average treatment effect (CATE) is computed for each individual as ground truth.

2. **Active comparators added** (R1§1, R4§4): Four active comparator methods are now benchmarked alongside proposed IONE methods: propensity score quintile stratification, Gaussian mixture model, prognostic score, and k-means on covariates.

3. **Monte Carlo standard errors reported throughout** (R1§3, R2§3, R2§6, R4§2): All point estimates now carry MC SEs (SD/√n_reps) and 2.5th/97.5th percentile confidence intervals.

4. **C1 interpretation clarified** (R1§5, R2§1, R4§2–3): The formula C1 = 1 − I² is retained, but the interpretation is now internally consistent throughout: C1 near 0 = high between-stratum heterogeneity = evidence of population incoherence. The distinction between between-stratum heterogeneity (C1) and within-stratum homogeneity (new indicator W) is explicitly articulated.

5. **Within-stratum homogeneity indicator W added** (R4§2): A new metric W = 1 − (weighted within-stratum CATE variance / overall CATE variance) directly measures whether strata are internally homogeneous, addressing the conceptual gap that C1 alone cannot fill.

6. **Scope narrowed** (R1§8, R2§2, R3§3): The framing now centres on unmeasured effect modification as the primary target, with unmeasured confounding as a secondary concern. Ecological fallacy and non-collapsibility are mentioned as related but distinct phenomena that IONE does not directly address.

7. **Claims substantially tempered** (R1§4, R1§10, R2§3, R2§8, R4§4): The Abstract and Conclusions no longer recommend C1 as a "standard component of reporting." Extraction performance is described as "modest" rather than "effective." C1 is positioned as an "exploratory diagnostic."

8. **"Empirical validation" relabelled to "semi-synthetic illustrations"** (R1§9, R2§5, R4§6): The section acknowledges that pseudo-general variables are engineered by design and that the encouraging ARI values cannot be read as evidence of out-of-the-box performance.

9. **Sample splitting implemented** (R2§4, R4§5): Outcome-informed methods (1A, 1B, 1D) now employ sample splitting (train on first 50%, assign strata to full dataset) to separate model building from evaluation.

10. **Title updated** (R2 minor§2): "— a Monte Carlo Simulation Study" appended to the title.

11. **Treatment effect bias reduction evaluated** (R4§5): New metrics quantify ATE bias reduction achieved by stratification-adjusted estimation vs. crude estimation.

---

## Editor

**The revised manuscript should clarify the conceptual scope of the proposed framework, align the motivation with the evaluation design, include appropriate comparator methods, report uncertainty around simulation results, address the limited extraction performance, complete all missing supplementary/code/materials, and substantially temper claims that are not supported by the current evidence.**

We have addressed each of these points as detailed in the summary above and in the individual responses below. In brief: (a) the scope has been narrowed to focus on unmeasured effect modification and confounding (§Background, §Discussion: Scope and framing); (b) the simulation now includes a treatment variable with confounding and effect modification, aligning the evaluation with the causal-inference motivation (§Methods: Data-generating mechanisms); (c) four active comparators have been added (§Methods: Methods under comparison); (d) all estimates carry MC SEs (§Results, all tables); (e) extraction performance is discussed honestly with appropriate caveats (§Discussion: Strengths and limitations); (f) placeholders have been removed; (g) claims have been substantially tempered (§Abstract, §Conclusions).

---

## Reviewer 1

### Major Concerns

**1. Add active comparator methods to the simulation.**

We agree that active comparators are essential. We have added four: (1) propensity score quintile stratification, (2) Gaussian mixture model (finite mixture model), (3) prognostic score (estimated from untreated subjects), and (4) k-means on covariates. All comparators are evaluated using the same metrics as proposed IONE methods. See §Methods: Methods under comparison (Active comparators) and all Results tables. This allows readers to judge whether IONE adds value over established approaches.

**2. Resolve the mismatch between motivation and evaluation.**

This was a fundamental deficiency. The simulation now includes a binary treatment variable A generated from a logistic model: logit(P(A=1)) = γ₀ + γ_Z·Z + γ_X·X, creating confounding (Z→A). The outcome model includes both a main treatment effect (τA) and effect modification (δ·Z×A), so that the true CATE varies across individuals. See §Methods: Treatment model and Outcome model. The primary estimands now include treatment effect bias reduction and CATE heterogeneity, in addition to subgroup recovery (ARI) and the C1/W diagnostic indicators.

**3. Report uncertainty for every point estimate.**

All tables now report mean (MC SE) for every metric. Figures include confidence bands. MC SE = SD/√n_reps, where n_reps = 200 (Phase 1) or 50 (sensitivity). See §Methods: Performance measures (final paragraph) and all Results tables.

**4. Extraction tier performance is practically negligible in simulation.**

We agree that this is a critical limitation and have revised the framing accordingly. The Abstract and Conclusions no longer claim that extraction "recovers" hidden structure. Instead, we describe extraction performance as "modest" and position the primary contribution of IONE as the C1/W diagnostic indicators rather than subgroup extraction. The best proposed method (1B: residual) achieved ARI = 0.021 (SE 0.0002) vs. oracle ARI = 0.353 (SE 0.0009), confirming a substantial gap. The Discussion includes a candid assessment of this gap (§Discussion: Strengths and limitations).

**5. The C1 statistic measures something narrower than "population coherence".**

We agree and have made three changes: (1) C1 is now explicitly described as a "between-stratum heterogeneity indicator" rather than a "coherence indicator" (§Methods: Performance measures); (2) the Discussion acknowledges that low C1 can arise from low within-stratum power or weak treatment effects, not only from genuine population incoherence (§Discussion: Two-tier diagnostic); (3) a new within-stratum homogeneity indicator W is introduced to address the distinction between between-stratum heterogeneity and within-stratum homogeneity.

**6. Binary confounders are nearly undetectable.**

We acknowledge this limitation explicitly in the revised Discussion (§Strengths and limitations, fourth paragraph). The η² values for binary critical variables remain low, and we note that IONE is better suited to detecting continuous or ordinal effect modifiers. This is a fundamental limitation arising from the weak trace that binary variables leave in continuous measured variables.

**7. Simplistic data-generating mechanism.**

We have addressed this by implementing a non-linear Z→X variant and conducting a full robustness analysis (109,350 additional evaluations). The non-linear variant replaces the linear Z→X mapping with a mixture of threshold functions, quadratic terms, and Z×Z interactions. Under non-linear encoding, linear-projection methods (1A, 1C, PS, prognostic score) degraded moderately (ARI −29% to −41% at strong signal), but mixture/clustering methods (2B clustering, GMM) improved (+29% to +53%), revealing complementary robustness properties across the two method families. This finding strengthens the paper's practical recommendation to apply both families jointly. Results are presented in Table 8 and a new Results subsection (§Robustness to non-linear Z→X relationships). We acknowledge that the DGM still does not incorporate missing data, measurement error, or complex interactions among measured variables, which remain priorities for future research (see §Limitations, second paragraph).

**8. Distinct phenomena are conflated under a single "incoherence" label.**

We have substantially narrowed the scope. The revised manuscript frames unmeasured effect modification as the PRIMARY target, unmeasured confounding as SECONDARY, and Simpson's paradox as an extreme illustration of their co-occurrence. Ecological fallacy and non-collapsibility are mentioned as related but distinct phenomena that IONE does not directly address. See §Background (first paragraph) and §Discussion: Scope and framing.

**9. The Simpson's paradox section overstates what has been demonstrated empirically.**

The section has been relabelled "Semi-synthetic illustrations" throughout. The introductory paragraph now explicitly states: "These serve as semi-synthetic illustrations rather than fully empirical validation, because the general variables are generated by design rather than genuinely measured." A caveat paragraph notes that "the encouraging results from these illustrations should not be interpreted as evidence of out-of-the-box performance on real clinical data." We have chosen the relabelling option rather than adding a real IPD dataset, as the reviewer indicated this would suffice.

**10. Conclusions overstate the evidence.**

The Conclusions have been substantially rewritten. The recommendation that C1 "be considered as a standard component of observational study reporting" has been removed. C1 and W are now described as "exploratory diagnostics to complement, not replace, established confounding adjustment methods." The qualifying phrase "Further calibration and validation on individual-level clinical data are needed before clinical recommendations can be made" has been added.

**11. Manuscript is incomplete.**

All placeholders have been removed. Additional file 1 (supplementary methods) has been completed. The code repository URL has been inserted. Funding and author contribution sections have been completed.

### Minor Comments

**1. Method 1B (residual) equivalence to predicted probability.**

We now explicitly note that for binary outcomes, |Y − p̂| reduces to 1 − p̂ for Y = 1 and p̂ for Y = 0, making it "essentially a stratification by predicted probability with a label-dependent transformation" (§Methods: Methods under comparison, Method 1B).

**2. Number of strata K is set exogenously.**

We have added a discussion of K selection to the Limitations section: "The number of strata K was set exogenously rather than estimated from the data. In practice, the number of hidden subgroups is unknown. Future work should explore data-driven approaches for selecting K" (§Discussion: Strengths and limitations, third paragraph). The sensitivity analysis includes K = 3, 5, 10.

**3. C1 repurposes I² from independent studies to strata within a single dataset.**

This is now explicitly acknowledged in the C1 definition (§Methods: Performance measures) and discussed at length in §Discussion: Two-tier diagnostic. We note that "this circular construction may alter the statistical properties of I²" and that "formal calibration is beyond the scope of this study."

**4. Figure captions are too short.**

Figure captions have been expanded to be self-contained.

**5. Direction consistency rate is defined but barely discussed.**

The direction consistency rate is retained in supplementary results but is no longer discussed in the main text, as it adds limited incremental information beyond ARI and W. Its value was near 1.0 for all methods, providing little discriminating power.

**6. Reference 12 (Morris 2021) is a blog post.**

We have added a note to the reference: "This is a data analysis blog post, not a peer-reviewed publication. It is cited here solely as the source of the aggregate data used to reconstruct individual-level data for the semi-synthetic illustration."

---

## Reviewer 2

### Major Comments

**1. The definition and interpretation of C1 need to be made internally consistent.**

We have resolved the inconsistency. C1 = 1 − I² remains the formula. The interpretation is now consistent throughout: C1 near 0 = strong between-stratum heterogeneity = evidence of population incoherence (good, meaning stratification has separated subgroups with different treatment effects); C1 near 1 = homogeneous effects across strata = no evidence of hidden structure. The confusing prose in the original submission has been corrected in §Methods: Performance measures and throughout the Results section. Additionally, we introduce W (within-stratum homogeneity indicator) to explicitly separate the concept of between-stratum heterogeneity from within-stratum homogeneity.

**2. The simulation data-generating mechanism appears incomplete for the causal question.**

Fully addressed. See response to R1§2 above. The DGM now includes a binary treatment A with explicit confounding (Z→A), treatment effect (A→Y), and effect modification (Z×A→Y). C1 is now computed from stratum-specific log odds ratios of the treatment–outcome association (A→Y within strata).

**3. The reported subgroup recovery is very small in practical terms.**

Addressed. See response to R1§4. Claims have been substantially tempered. MC SEs now accompany all estimates so readers can assess whether differences are practically meaningful.

**4. Outcome-informed stratification creates a risk of circularity.**

We have implemented sample splitting for outcome-informed methods (1A, 1B, 1D): the predictive model is trained on the first 50% of observations, and stratum assignments are generated for the full dataset using the trained model. Method 1C already uses cross-validation. See §Methods: Methods under comparison (Family 1, opening paragraph).

**5. The empirical validation should be reframed or strengthened.**

Relabelled as "semi-synthetic illustrations" with appropriate caveats. See response to R1§9.

### Minor Comments

**1. Remove all placeholders.**

Done.

**2. The title should indicate this is a simulation study.**

"— a Monte Carlo Simulation Study" has been appended to the title.

**3. Notation would benefit from tightening.**

We now consistently use: Z = critical variables (unmeasured), X = general variables (measured), A = treatment (binary), Y = outcome (binary). A notation table has been considered; we use consistent notation throughout without a separate table, but will add one if the editor or reviewer feels it would improve clarity.

**4. How would K be chosen in a real application?**

See response to R1 minor§2.

**5. Method 2A needs clearer description.**

We have clarified that six PCA variants were evaluated using PC1 through PC6 (i.e., stratifying by quantiles of the k-th principal component score, k = 1, …, 6). See §Methods: Methods under comparison (Method 2A).

**6. Statistical tests and MC SEs for ARI comparisons.**

All estimates now carry MC SEs. Comparisons are within-replicate (paired). [Specific test details to be finalised after results.]

**7. More detail on stratum-specific log OR calculation.**

The C1 computation now uses a continuity correction of 0.5 for zero cells. This is described in §Methods: Performance measures (C1 definition) and implemented in the code. Minimum stratum sizes and handling of unstable estimates are specified.

**8. Language should be toned down.**

Done. See responses to R1§4 and R1§10.

---

## Reviewer 3

**1. What are the rigorous definitions of "critical variables" and "general variables"?**

We have clarified the definitions in the Methods section. Critical variables (Z) are variables that define the hidden subgroup structure and act as both confounders and effect modifiers, but are assumed to be unmeasured (e.g. genetic subtype, disease severity stage). General variables (X) are routinely measured covariates that carry indirect traces of Z through their correlations with Z. In the simulation, Z = (age, sex, BMI) and X = (10 clinical lab values). We acknowledge that in practice, the distinction depends on domain knowledge about which variables are likely to create hidden population structure, and this is discussed as a limitation.

**2. The number of strata K appears to be an important parameter. How is K incorporated into the DGM?**

K determines the number of strata in the stratification methods, not the data-generating mechanism itself. The DGM generates continuous/categorical Z variables without a fixed number of subgroups; the "true" clusters are defined post-hoc by applying k-means to the Z-space with K clusters. We have clarified this in §Methods: Estimands. The sensitivity analysis varies K = 3, 5, 10 to assess robustness. We acknowledge that in practice K is unknown and discuss data-driven selection as future work.

**3. The manuscript never provides a clear definition of hidden population structure.**

We have added explicit definitions. "Hidden population structure" refers to the condition in which a study population comprises subgroups with heterogeneous treatment effects (effect modification) or differential treatment assignment probabilities (confounding), where the grouping variable is not measured. The formal definition is tied to the Z×A→Y interaction in the causal DAG. See revised §Background (first paragraph).

**4. The criteria for the proposed measures are unclear.**

We have expanded the description of each performance measure with explicit formulas, scales, and interpretation guidelines. C1 is described with its scale (0–1), direction (low = heterogeneity detected), and caveats. W is described with its scale and meaning. ATE bias reduction is defined with a formula. See §Methods: Performance measures.

**5. Does the proposed method work under the hidden population structure settings assumed in prior studies?**

The revised framing explicitly limits IONE's scope to unmeasured effect modification and confounding (a specific DAG family: Z→X, Z→A, A→Y, Z→Y, Z×A→Y). We do not claim that IONE addresses all forms of hidden population structure considered in the literature. The Discussion now includes a "Scope and framing" subsection that explicitly delineates what IONE targets and what it does not.

---

## Reviewer 4

**§1. The manuscript should more clearly define the causal or statistical estimand targeted by IONE.**

The estimands are now explicitly defined: (1) subgroup-specific treatment effects τ(z) = E[Y(1)−Y(0)|Z=z], (2) ATE bias reduction from stratification-adjusted estimation, (3) between-stratum heterogeneity (C1), (4) within-stratum homogeneity (W). IONE is positioned as an exploratory diagnostic and preprocessing step, not as a complete causal inference method. See §Methods: Estimands and §Discussion: Scope and framing.

**§2. The interpretation of C1 needs substantial clarification. Between-stratum heterogeneity ≠ within-stratum homogeneity.**

This is precisely the point that motivated the introduction of W. C1 measures between-stratum heterogeneity (do strata differ?); W measures within-stratum homogeneity (are individuals within each stratum similar?). These are related but conceptually distinct. We now explicitly state this distinction in §Methods: Performance measures, in the C1/W description in §Background, and in §Discussion: Two-tier diagnostic.

**§3. The proposed threshold C1 < 0.05 appears premature.**

We agree. C1 is now presented as "an exploratory diagnostic rather than a formal hypothesis test" and the threshold of 0.05 is described as "provisional" requiring "formal calibration across a wider range of settings." See §Methods: Performance measures and §Discussion: Two-tier diagnostic.

**§4. The simulation results suggest that subgroup recovery is quite limited.**

See response to R1§4. Claims have been substantially tempered.

**§5. The manuscript should provide stronger evidence that IONE improves downstream inference.**

We have added treatment effect bias reduction as a primary performance measure. The simulation now computes the crude ATE (unadjusted log OR), the stratified ATE (inverse-variance weighted average of stratum-specific log ORs), and the true ATE (from the known DGM). Bias reduction = 1 − |bias_stratified| / |bias_crude|. Additionally, CATE heterogeneity (η²_CATE) measures whether stratification successfully separates individuals with different treatment effects. These directly address whether IONE improves the analysis that applied researchers care about.

**§6. The use of outcome-informed stratification raises concerns about overfitting.**

See response to R2§4. Sample splitting has been implemented for Methods 1A, 1B, and 1D. We acknowledge in the limitations that this does not eliminate the concern entirely.

**§7. The empirical examples should not be described as empirical validation.**

See response to R1§9. Relabelled as "semi-synthetic illustrations."

**§8. The abstract and conclusions should not claim that C1 is a standard reporting component.**

See response to R1§10. This claim has been removed.

### Minor Comments

**Sample size vs. precision distinction.**

We will distinguish between subgroup recovery performance (ARI, which may be insensitive to N) and the precision of C1/treatment-effect estimates (which improve with N). [To be addressed in the results narrative.]

**Empirical examples have different structures — comparability discussion.**

A paragraph discussing how differences in group numbers, sample sizes, and pseudo-variable structures affect comparability has been added to the semi-synthetic illustrations section.

**Summary recommendation: major revision.**

We thank the reviewer for the constructive summary and believe the revisions above address all major concerns.

---

*End of point-by-point response*
