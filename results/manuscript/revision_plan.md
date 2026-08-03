# IONE revision plan after BMC Medical Research Methodology rejection

## Overall direction

Reframe the paper as a **proof-of-concept diagnostic framework** rather than a mature two-tier workflow. The strongest, best-supported contribution is the C1 coherence indicator as an exploratory warning tool. Claims about extracting/recovering hidden subgroups and reducing bias must be matched to the actual ARI and bias-reduction values.

---

## 1. Internal consistency and metrics

### 1.1 Bias reduction

| Issue | Action |
|-------|--------|
| Reviewer 1/2: reported bias-reduction value is inconsistent with the formula. | Reconcile the formula with the reported numbers. Either use the relative reduction \(1 - \|bias_stratified\| / \|bias_crude\|\) consistently **or** use the absolute reduction and label it correctly. Update the formula, all tables, figure captions, abstract, and discussion. |
| Reviewer 2: methods 1B outperforms oracle baselines on this metric. | Add a short explanation: outcome-informed stratification can condition on the observed outcome in a way that oracle k-means on Z does not, so the metric is not an upper-bound reference for outcome-informed methods. |

### 1.2 W metric

| Issue | Action |
|-------|--------|
| Reviewer 1: W is computed from the true CATE and is an oracle metric. | Either (a) implement and evaluate an estimated-CATE version of W using only observable data, **or** (b) remove practical diagnostic language, relabel W as a simulation-only performance metric, and move it to a supplementary metric section. |

### 1.3 C1 coherence indicator

| Issue | Action |
|-------|--------|
| Reviewer 1/2: C1 values overlap heavily between proposed methods and random stratification in the primary simulation. | Present C1 as an **exploratory, not yet calibrated** diagnostic. Report calibration curves across regimes (random stratification, weak/strong Z→X, discrete/continuous Z, finite sample) instead of a fixed threshold. Remove claims that C1 "reliably detects" incoherence. |
| Provisional threshold C1 < 0.05 is unsupported. | Replace the threshold with a sensitivity-based interpretation. State that the threshold is provisional and requires external calibration. |

---

## 2. Ground truth, oracle, and method taxonomy

| Issue | Action |
|-------|--------|
| Reviewer 2/3: true subgroup structure defined by k-means on Z is crude; oracle ARI should be near 1 for the same K. | Define the ground truth using **the discrete critical-variable categories** when K matches the true number of categories. If k-means on Z is retained as a continuous approximation, explain that it is a reference partition, not a biological truth, and report oracle ARI near 1 for the same K. |
| Reviewer 2: oracle is not an upper bound for all metrics. | Add a paragraph explaining why oracle k-means on Z can be outperformed by outcome-informed methods for bias-related metrics. |
| Reviewer 2: method taxonomy is inconsistent (3 vs 4 active comparators, 18 methods count). | Create one exact method inventory and use it consistently in the abstract, methods, tables, and response letter. |
| Reviewer 3: latent class models also identify hidden subgroups; the distinction is unclear. | Add a paragraph clarifying that latent class/finite mixture models discover subgroups **from observed variables** under distributional assumptions, whereas IONE treats the observed population as potentially incoherent and provides a coherence diagnostic before any subgroup analysis. |

---

## 3. Outcome model and outcome-informed methods

| Issue | Action |
|-------|--------|
| Reviewer 3: outcome model only includes A×Z interactions; why not X×Z or X×A? | Either add selected X–Z and X–A interaction terms in a sensitivity analysis, or explicitly justify the parsimonious model and state that generalizability to models with richer interactions is tested in the sensitivity analysis. |
| Reviewer 3: interpretation of τ as a main treatment effect is unclear when A interacts with Z. | Clarify that τ is the conditional log-odds ratio at the reference level of Z, not a marginal main effect. |
| Reviewer 2: residual stratification uses the observed outcome, creating circularity/collider risk. | Restrict residual-based stratification to **exploratory diagnostics**; for downstream treatment-effect estimation, require a discovery/evaluation split or a hold-out sample. Add a sensitivity analysis quantifying the induced bias. |

---

## 4. Framing and claims

| Issue | Action |
|-------|--------|
| Reviewer 2: extraction performance in primary simulation is very low (best ARI 0.021 vs oracle 0.353). | Reframe throughout: extraction is **conditionally and partially successful**, not a usable two-tier workflow. Lead with the diagnostic value of C1. |
| Reviewer 2: semi-synthetic claim that all methods achieved ARI > 0.7 is over-stated. | Revise the abstract and results to report the full set: 2-group examples reach ARI > 0.7, but multi-group examples (COVID-19 CFR, UC Berkeley) remain below 0.1. |
| Reviewer 1/2/3: "neutralisation" is not operationalised. | Define "neutralisation" explicitly as "bias reduction through stratification" and avoid language implying causal elimination of confounding. |
| Reviewer 1: recovery target is a post-hoc partition of partly continuous Z. | State plainly that ARI measures agreement with a constructed clustering target, not natural subgroups. |

---

## 5. Empirical examples and reproducibility

| Issue | Action |
|-------|--------|
| Reviewer 1: Additional file 1 inconsistencies (reconstructed vs simulated variables, group counts). | Clarify in Additional file 1 which variables were reconstructed from published contingency tables and which were generated from logistic models. Ensure group counts match Table 1. |
| Reviewer 2: Morris 2021 source is a blog post. | In the main text, describe the Morris example as a publicly available data-analysis example, not a peer-reviewed study. |
| Reviewer 2: implementation details are missing. | Add a supplement or appendix with logistic regression regularisation, standardisation, random-forest settings, k-means initialisations and starts, GMM covariance, convergence, and random seeds. |
| Reviewer 2: add permanent code archive. | Create a tagged GitHub release or Zenodo archive and report the commit hash/DOI in the data availability statement. |

---

## 6. Target journal strategy

See `next_journal_proposal.md` for candidates and the recommended order.

---

## Files needed before editing

- The current repository branch (`IONE-stratification-framework`) contains the first-round manuscript. The reviewer comments reference a later version (e.g. W metric, Tables 8–11). Before applying the plan, obtain or confirm the latest submitted version so revisions are made on the correct base.
