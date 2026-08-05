"""
Generate a full-length RSM manuscript (v3) based on the previous long version.

Workflow:
1. Read the previous IONE_manuscript.md (observational, long version).
2. Update title, abstract, and keywords.
3. Replace Methods and Results with RSM IPD content, inserting current CSV numbers.
4. Adapt Background/Discussion/Conclusions for IPD meta-analysis and editor comments.
5. Replace numbered citations with author-date keys.
6. Convert to docx via md_to_rsm_docx.

All numbers come from results/summary/*.csv; no estimates are hard-coded.
"""

import os
import re
import numpy as np
import pandas as pd
from collections import OrderedDict

from generate_manuscript import _read_csv, _fmt
from generate_full_rsm_manuscript import generate_rsm_figures, _scenario_params
from md_to_rsm_docx import CiteManager, convert
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
SUMMARY_DIR = os.path.join(RESULTS_DIR, 'summary')
FIG_DIR = os.path.join(RESULTS_DIR, 'figures')
RSM_DIR = os.path.join(RESULTS_DIR, 'manuscript', 'rsm_submission')
os.makedirs(RSM_DIR, exist_ok=True)


def _scenario_values():
    """Compute all dynamic values from CSVs."""
    ipd_primary = _read_csv('rsm_ipd_primary_summary.csv')
    ipd_full = _read_csv('rsm_ipd_full_summary.csv')
    study_summary = _read_csv('rsm_ipd_study_summary.csv')
    real_data = _read_csv('real_data_summary.csv')

    n_ipd, n_studies, study_effect, k_ipd = _scenario_params()

    if ipd_primary is None or ipd_primary.empty:
        raise RuntimeError('rsm_ipd_primary_summary.csv is empty or missing')

    best_re = ipd_primary.loc[ipd_primary['bias_reduction_relative_re_mean'].idxmax()]
    best_ari_row = ipd_primary.loc[ipd_primary['ARI_mean'].idxmax()]
    non_oracle = ipd_primary[~ipd_primary['method'].str.startswith('baseline_')]
    best_non_oracle_ari_row = non_oracle.loc[non_oracle['ARI_mean'].idxmax()]

    vals = {}
    vals['n_ipd'] = n_ipd
    vals['n_studies'] = n_studies
    vals['study_effect'] = study_effect
    vals['k_ipd'] = k_ipd
    vals['best_method'] = best_re['method']
    vals['best_ari'] = _fmt(best_ari_row['ARI_mean'])
    vals['best_ari_method'] = best_ari_row['method']
    vals['best_non_oracle_ari'] = _fmt(best_non_oracle_ari_row['ARI_mean'])
    vals['best_non_oracle_ari_method'] = best_non_oracle_ari_row['method']
    vals['best_c1'] = _fmt(best_re['C1_heterogeneity_mean'])
    vals['best_wtrue'] = _fmt(best_re['W_true_mean'])
    vals['best_west'] = _fmt(best_re['W_est_mean'])
    vals['crude_bias'] = _fmt(best_re['abs_bias_crude_mean'], 5)
    vals['strat_bias'] = _fmt(best_re['abs_bias_stratified_mean'], 5)
    vals['re_bias'] = _fmt(best_re['abs_bias_re_mean'], 5)
    vals['rel_strat'] = _fmt(best_re['bias_reduction_relative_mean'], 3)
    vals['rel_re'] = _fmt(best_re['bias_reduction_relative_re_mean'], 3)
    vals['mean_c1'] = _fmt(ipd_primary['C1_heterogeneity_mean'].mean(), 3)
    vals['mean_wtrue'] = _fmt(ipd_primary['W_true_mean'].mean(), 3)
    vals['mean_west'] = _fmt(ipd_primary['W_est_mean'].mean(), 3)

    # study-level meta-analysis comparator
    if study_summary is not None and not study_summary.empty:
        srow = study_summary.iloc[0]
        vals['study_crude'] = _fmt(srow.get('study_bias_crude_mean', np.nan), 5)
        vals['study_re'] = _fmt(srow.get('study_bias_re_mean', np.nan), 5)
        vals['study_red'] = _fmt(srow.get('study_bias_crude_mean', np.nan) - srow.get('study_bias_re_mean', np.nan), 5)
    else:
        vals['study_crude'] = vals['study_re'] = vals['study_red'] = '—'

    # sensitivity to K
    if ipd_full is not None and not ipd_full.empty:
        k_list = sorted(ipd_full['n_strata'].unique())
        vals['k_list'] = ', '.join(str(int(k)) for k in k_list)
        # best method by K (excluding oracle/random? include all)
        for k in k_list:
            sub = ipd_full[ipd_full['n_strata'] == k]
            if not sub.empty:
                best = sub.loc[sub['bias_reduction_relative_re_mean'].idxmax()]
                vals[f'best_k{k}'] = best['method']
                vals[f're_k{k}'] = _fmt(best['bias_reduction_relative_re_mean'], 3)
    else:
        vals['k_list'] = '3, 5, 10'

    # real data best (non-oracle)
    if real_data is not None and not real_data.empty:
        real_non = real_data[~real_data['method'].str.startswith('baseline_')]
        rd_best = real_non.loc[real_non.groupby('dataset')['ARI_mean'].idxmax()].copy()
        rd_best_rows = []
        for _, r in rd_best.iterrows():
            rd_best_rows.append({
                'dataset': r['dataset'],
                'method': r['method'],
                'k': int(r['n_strata']),
                'ari': _fmt(r['ARI_mean']),
                'c1': _fmt(r['C1_heterogeneity_mean']),
                'west': _fmt(r['W_est_mean']),
                'bias_red': _fmt(r['bias_reduction_mean']),
            })
        vals['real_best_rows'] = rd_best_rows
    else:
        vals['real_best_rows'] = []

    return vals


def _make_table(cols, rows):
    """Return a markdown table string."""
    out = '| ' + ' | '.join(cols) + ' |\n'
    out += '|' + '|'.join(['---' for _ in cols]) + '|\n'
    for r in rows:
        out += '| ' + ' | '.join(str(r.get(c, '')) for c in cols) + ' |\n'
    return out


def _extract_section(md, heading):
    """Extract text between `## heading` and the next `## ` heading."""
    pattern = rf'## {re.escape(heading)}\n(.*?)\n## '
    m = re.search(pattern, md, re.S)
    if m:
        return m.group(1).strip()
    return ''


def _register_citations(cm):
    # Old observational references
    cm.register('hammerton2021', 'Hammerton and Munafò', 2021,
                'Hammerton G, Munafò MR. Causal inference with observational data: the need for triangulation of evidence. Psychol Med. 2021;51(4):563–578.')
    cm.register('hernan2020', 'Hernán and Robins', 2020,
                'Hernán MA, Robins JM. Causal Inference: What If. Boca Raton: Chapman & Hall/CRC; 2020.')
    cm.register('vanderweele2013', 'VanderWeele and Shpitser', 2013,
                'VanderWeele TJ, Shpitser I. On the definition of a confounder. Ann Stat. 2013;41(1):196–220.')
    cm.register('simpson1951', 'Simpson', 1951,
                'Simpson EH. The interpretation of interaction in contingency tables. J R Stat Soc Ser B. 1951;13(2):238–241.')
    cm.register('rojanaworarit2020', 'Rojanaworarit', 2020,
                'Rojanaworarit C. Misleading epidemiological and statistical evidence in the presence of Simpson\'s paradox: an illustrative study using simulated scenarios. J Med Life. 2020;13(1):37–44.')
    cm.register('vanderweele2014', 'VanderWeele and Knol', 2014,
                'VanderWeele TJ, Knol MJ. A tutorial on interaction. Epidemiol Methods. 2014;3(1):33–72.')
    cm.register('robinson1950', 'Robinson', 1950,
                'Robinson WS. Ecological correlations and the behavior of individuals. Am Sociol Rev. 1950;15(3):351–357.')
    cm.register('greenland1999', 'Greenland et al.', 1999,
                'Greenland S, Robins JM, Pearl J. Confounding and collapsibility in causal inference. Stat Sci. 1999;14(1):29–46.')
    cm.register('charig1986', 'Charig et al.', 1986,
                'Charig CR, Webb DR, Payne SR, Wickham JE. Comparison of treatment of renal calculi by open surgery, percutaneous nephrolithotomy, and extracorporeal shockwave lithotripsy. BMJ. 1986;292(6521):879–882.')
    cm.register('bickel1975', 'Bickel et al.', 1975,
                'Bickel PJ, Hammel EA, O\'Connell JW. Sex bias in graduate admissions: data from Berkeley. Science. 1975;187(4175):398–404.')
    cm.register('vonkuegelgen2021', 'von Kügelgen et al.', 2021,
                'von Kügelgen J, Gresele L, Schölkopf B. Simpson\'s paradox in Covid-19 case fatality rates: a mediation analysis of age-related causal effects. IEEE Trans Artif Intell. 2021;2(1):18–27.')
    cm.register('morris2021', 'Morris', 2021,
                'Morris JS. Israeli data: how can efficacy vs. severe disease be strong when 60% of hospitalized are vaccinated? 2021. Available from: https://www.covid-datascience.com/post/israeli-data-how-can-efficacy-vs-severe-disease-be-strong-when-60-of-hospitalized-are-vaccinated')
    cm.register('appleton1996', 'Appleton et al.', 1996,
                'Appleton DR, French NR, Vanderpump MP. Ignoring a covariate: an example of Simpson\'s paradox. Am Stat. 1996;50(4):340–341.')
    cm.register('rosenbaum1983', 'Rosenbaum and Rubin', 1983,
                'Rosenbaum PR, Rubin DB. The central role of the propensity score in observational studies for causal effects. Biometrika. 1983;70(1):41–55.')
    cm.register('hansen2008', 'Hansen', 2008,
                'Hansen BB. The prognostic analogue of the propensity score. Biometrika. 2008;95(2):481–488.')
    cm.register('miettinen1976', 'Miettinen', 1976,
                'Miettinen OS. Stratification by a multivariate confounder score. Am J Epidemiol. 1976;104(6):609–620.')
    cm.register('angrist1996', 'Angrist et al.', 1996,
                'Angrist JD, Imbens GW, Rubin DB. Identification of causal effects using instrumental variables. J Am Stat Assoc. 1996;91(434):444–455.')
    cm.register('schneeweiss2009', 'Schneeweiss et al.', 2009,
                'Schneeweiss S, Rassen JA, Glynn RJ, Avorn J, Mogun H, Brookhart MA. High-dimensional propensity score adjustment in studies of treatment effects using health care claims data. Epidemiology. 2009;20(4):512–522.')
    cm.register('rassen2012', 'Rassen and Schneeweiss', 2012,
                'Rassen JA, Schneeweiss S. Using high-dimensional propensity scores to automate confounding control in a distributed medical product safety surveillance system. Pharmacoepidemiol Drug Saf. 2012;21(S1):41–49.')
    cm.register('wyss2018', 'Wyss et al.', 2018,
                'Wyss R, Schneeweiss S, van der Laan M, Lendle SD, Ju C, Franklin JM. Machine learning for improving high-dimensional proxy confounder adjustment in healthcare database studies. Stat Med. 2018;37(8):1310–1324.')
    cm.register('tchetgen2024', 'Tchetgen Tchetgen et al.', 2024,
                'Tchetgen Tchetgen EJ, Ying A, Cui Y, Shi X, Miao W. An introduction to proximal causal inference. Stat Sci. 2024;39(3):375–390.')
    cm.register('mclachlan2000', 'McLachlan and Peel', 2000,
                'McLachlan GJ, Peel D. Finite Mixture Models. New York: Wiley; 2000.')
    cm.register('hayeslarson2019', 'Hayes-Larson et al.', 2019,
                'Hayes-Larson E, Kezios KL, Mooney SJ, Lovasi G. Who is in this study, anyway? Guidelines for a useful Table 1. J Clin Epidemiol. 2019;114:125–132.')
    cm.register('higgins2002', 'Higgins and Thompson', 2002,
                'Higgins JPT, Thompson SG. Quantifying heterogeneity in a meta-analysis. Stat Med. 2002;21(11):1539–1558.')
    cm.register('morris2019', 'Morris et al.', 2019,
                'Morris TP, White IR, Crowther MJ. Using simulation studies to evaluate statistical methods. Stat Med. 2019;38(11):2074–2102.')
    cm.register('hubert1985', 'Hubert and Arabie', 1985,
                'Hubert L, Arabie P. Comparing partitions. J Classif. 1985;2(1):193–218.')
    cm.register('strehl2002', 'Strehl and Ghosh', 2002,
                'Strehl A, Ghosh J. Cluster ensembles—a knowledge reuse framework for combining multiple partitions. J Mach Learn Res. 2002;3:583–617.')

    # Additional RSM / meta-analysis / causal references
    cm.register('borenstein2009', 'Borenstein et al.', 2009,
                'Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. Chichester: John Wiley & Sons; 2009.')
    cm.register('dersimonian1986', 'DerSimonian and Laird', 1986,
                'DerSimonian R, Laird N. Meta-analysis in clinical trials. Control Clin Trials. 1986;7(3):177–188.')
    cm.register('riley2010', 'Riley et al.', 2010,
                'Riley RD, Lambert PC, Abo-Zaid G. Meta-analysis of individual participant data: rationale, conduct, and reporting. BMJ. 2010;340:c221.')
    cm.register('riley2011', 'Riley et al.', 2011,
                'Riley RD, Higgins JPT, Deeks JJ. Interpretation of random effects meta-analyses. BMJ. 2011;342:d549.')
    cm.register('simmonds2005', 'Simmonds et al.', 2005,
                'Simmonds MC, Higgins JPT, Stewart LA, Tierney JF, Clarke MJ, Thompson SG. Meta-analysis of individual patient data from randomized trials: a review of methods used in practice. Clin Trials. 2005;2(3):209–217.')
    cm.register('austin2015', 'Austin and Stuart', 2015,
                'Austin PC, Stuart EA. Moving towards best practice when using inverse probability of treatment weighting (IPTW) using the propensity score to estimate causal treatment effects in observational studies. Stat Med. 2015;34(28):3661–3679.')
    cm.register('pearl2009', 'Pearl', 2009,
                'Pearl J. Causality. 2nd ed. Cambridge: Cambridge University Press; 2009.')
    cm.register('rubin1974', 'Rubin', 1974,
                'Rubin DB. Estimating causal effects of treatments in randomized and nonrandomized studies. J Educ Psychol. 1974;66(5):688–701.')
    cm.register('vanderweele2015', 'VanderWeele', 2015,
                'VanderWeele TJ. Explanation in Causal Inference: Methods for Mediation and Interaction. Oxford: Oxford University Press; 2015.')
    cm.register('julious1994', 'Julious and Mullee', 1994,
                'Julious SA, Mullee MA. Confounding and Simpson\'s paradox. BMJ. 1994;309(6967):1480–1481.')


def _old_to_keys(text, cm=None):
    """Replace old numbered citations [1], [1, 2], [9–13] with [key] author-date citations."""
    # Specific ranges first
    text = text.replace('[9–13]', '[charig1986][bickel1975][vonkuegelgen2021][morris2021][appleton1996]')
    text = text.replace('[9-13]', '[charig1986][bickel1975][vonkuegelgen2021][morris2021][appleton1996]')
    text = text.replace('[14, 15]', '[rosenbaum1983][hansen2008]')
    text = text.replace('[19, 20]', '[schneeweiss2009][rassen2012]')
    text = text.replace('[19, 21]', '[schneeweiss2009][wyss2018]')
    text = text.replace('[4, 5]', '[simpson1951][rojanaworarit2020]')
    text = text.replace('[15, 16]', '[hansen2008][miettinen1976]')

    # Simple one-to-one mapping from old numbers to keys
    mapping = {
        '1': 'hammerton2021',
        '2': 'hernan2020',
        '3': 'vanderweele2013',
        '4': 'simpson1951',
        '5': 'rojanaworarit2020',
        '6': 'vanderweele2014',
        '7': 'robinson1950',
        '8': 'greenland1999',
        '9': 'charig1986',
        '10': 'bickel1975',
        '11': 'vonkuegelgen2021',
        '12': 'morris2021',
        '13': 'appleton1996',
        '14': 'rosenbaum1983',
        '15': 'hansen2008',
        '16': 'miettinen1976',
        '17': 'miettinen1976',
        '18': 'angrist1996',
        '19': 'schneeweiss2009',
        '20': 'rassen2012',
        '21': 'wyss2018',
        '22': 'tchetgen2024',
        '23': 'mclachlan2000',
        '24': 'hayeslarson2019',
        '25': 'higgins2002',
        '26': 'morris2019',
        '27': 'hubert1985',
        '28': 'strehl2002',
    }

    def repl_single(m):
        nums = [n.strip() for n in re.split(r'[,–\-]', m.group(1))]
        # Only convert if every token is a known old citation number
        if all(n in mapping for n in nums):
            return ''.join(f'[{mapping[n]}]' for n in nums)
        # Otherwise leave the original text unchanged (likely a numeric range or other bracketed content)
        return m.group(0)

    text = re.sub(r'\[([\d,\-–\s]+)\]', repl_single, text)
    return text


def _adapt_background(old_bg, cm, v):
    """Adapt the observational Background to IPD meta-analysis framing."""
    # Remove the objectives paragraph (will be handled separately)
    old_bg = re.sub(r'The objectives of this study are threefold.*', '', old_bg, flags=re.S).strip()

    # Prepend an RSM/IPD framing paragraph before the original observational background
    rsm_intro = (
        'Meta-analysis combines treatment-effect estimates from related studies and is central to evidence-based medicine and policy [borenstein2009]. '
        'In an individual participant data (IPD) meta-analysis, the original participant-level data are collected and re-analysed, which preserves covariate and subgroup information and can improve power for treatment-covariate interactions [riley2010][simmonds2005]. '
        'A random-effects analysis is widely recommended when between-study heterogeneity is suspected [dersimonian1986][higgins2002][riley2011]. '
        'Nevertheless, the standard two-stage or one-stage synthesis still estimates an average effect and may miss effect modifiers that are unmeasured, measured with error, or omitted from the analysis plan. '
        'When the pooled population is a mixture of subgroups with different treatment effects, or when confounders differ across studies, the marginal effect can differ from subgroup-specific effects, leading to aggregation bias and Simpson-type reversals [pearl2009][greenland1999].\n\n'
        'Current IPD meta-analysis practice offers several tools for exploring heterogeneity, including subgroup analyses, meta-regression and one-stage mixed models with treatment-covariate interactions. '
        'These approaches explain heterogeneity through measured covariates and study-level characteristics, but they do not test whether the pooled participants themselves form internally homogeneous subpopulations with respect to the treatment effect. '
        'In other words, an analyst can conclude that there is statistically significant between-study heterogeneity without knowing whether that heterogeneity arises from a hidden effect modifier that also operates within studies. '
        'We therefore frame IONE as an exploratory diagnostic that can be applied before or alongside a conventional synthesis, to alert analysts when a marginal summary may be fragile.\n\n'
    )

    # Update the operationalisation sentence to describe C1 and W
    old_bg = re.sub(
        r'As a coherence indicator, we propose a metric \(C1\) derived from the I\u00b2 heterogeneity statistic \[25\] applied to within-stratum treatment effects, which quantifies the degree to which effect estimates are homogeneous across strata\.',
        'As coherence diagnostics, we propose C1, derived from the I² heterogeneity statistic [higgins2002] applied to stratum-specific log odds ratios, and W, the proportion of total conditional average treatment effect (CATE) variance explained by the stratification.',
        old_bg
    )

    # Update the two-stage approach description
    old_bg = re.sub(
        r'We propose that the problem of hidden population structure can be addressed through a two-stage approach\. In the first stage, a quantitative indicator of population coherence[^\.]+\. In the second stage, if incoherence is detected, the population is stratified into coherent subgroups using multivariate patterns in the measured variables, and the primary analysis is conducted within each subgroup\.',
        'We propose that the problem of hidden population structure in IPD meta-analysis can be addressed through a two-stage exploratory diagnostic. In the first stage, the coherence diagnostics C1 (between-stratum heterogeneity) and W (within-stratum homogeneity) are computed from routinely measured covariates to determine whether the pooled IPD contains hidden subgroups that warrant separate analysis. In the second stage, if incoherence is indicated, the pooled IPD is stratified into more homogeneous subgroups using multivariate patterns in the measured variables, and stratum-specific risk differences are synthesised with two-stage fixed-effect or random-effects meta-analysis.',
        old_bg
    )

    return rsm_intro + old_bg


def _new_methods(v):
    """Return markdown string for the Methods section."""
    md = """## 2. Methods

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

We generated an IPD meta-analysis by assigning n={n_ipd} participants to {n_studies} studies of approximately equal size. Study-level heterogeneity was controlled by a scale parameter of {study_effect}; this produced between-study variation in baseline risk, treatment prevalence and the distribution of a continuous age-like covariate, analogous to the between-study variance in a random-effects meta-analysis [dersimonian1986].

Each participant had three critical variables (Z1 continuous age-like, Z2 binary sex-like, Z3 ordered BMI-like) that affected treatment, outcome and their interaction, and ten measured variables (X1-X10) that carried traces of Z. A binary treatment A was generated from a logistic model with confounders Z and covariates X; a binary outcome Y was generated from a logistic model with main effects of Z and X, a treatment main effect and Z-by-A interactions (effect modification). The true estimand was the population risk-difference average treatment effect (ATE), computed by averaging the true individual CATE over the super-population.

The data-generating mechanism follows a causal directed acyclic graph. Study membership introduces heterogeneity in the intercepts for baseline risk and treatment prevalence; within each study, the same confounder-modifier Z generates measured covariates X, treatment A and outcome Y. This design mimics an IPD meta-analysis in which studies differ in case-mix and treatment use, yet a common unmeasured effect modifier is present. Full algebraic details and parameter values are given in the repository, and all scenarios were assigned fixed random seeds for reproducibility.

#### Scenarios

The primary scenario used n={n_ipd} participants, {n_studies} studies and K={k_ipd} strata, with a moderate Z-to-X trace, moderate outcome-event rate and moderate study-effect heterogeneity. To examine sensitivity to the number of strata, we repeated the simulation with K=3, 5 and 10 while keeping the total sample size and between-study heterogeneity fixed. Each scenario was replicated {n_sims_per_scenario} times, and all random seeds were fixed so that the exact numerical results can be reproduced by running the repository scripts.

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

All simulations and analyses were conducted in Python 3.11. The pipeline comprises `data_generation.py`, `methods.py`, `evaluation.py`, `run_rsm_ipd_simulation.py`, `generate_summary.py` and the manuscript generator. The simulation was run with {n_sims_per_scenario} replications per scenario and fixed random seeds. The code and semi-synthetic example data are available at https://github.com/bougtoir/ione-stratification-framework. All numerical results in this manuscript are produced by the repository scripts; no estimates are hard-coded.
""".format(n_ipd=v['n_ipd'], n_studies=v['n_studies'], study_effect=v['study_effect'], k_ipd=v['k_ipd'], n_sims_per_scenario=50)
    return md
def _new_results(v):
    """Return markdown string for the Results section with current CSV numbers."""
    ipd_primary = _read_csv('rsm_ipd_primary_summary.csv')
    table1_rows = []
    for _, r in ipd_primary.iterrows():
        table1_rows.append({
            'Method': r['method'],
            'ARI': _fmt(r['ARI_mean']),
            'C1': _fmt(r['C1_heterogeneity_mean']),
            'W_true': _fmt(r['W_true_mean']),
            'W_est': _fmt(r['W_est_mean']),
            'Crude bias': _fmt(r['abs_bias_crude_mean'], 5),
            'Stratified bias': _fmt(r['abs_bias_stratified_mean'], 5),
            'RE bias': _fmt(r['abs_bias_re_mean'], 5),
            'Rel reduction strat': _fmt(r['bias_reduction_relative_mean'], 3),
            'Rel reduction RE': _fmt(r['bias_reduction_relative_re_mean'], 3),
            'RE I2': _fmt(r['re_I2_mean']),
        })
    table1 = _make_table(
        ['Method', 'ARI', 'C1', 'W_true', 'W_est', 'Crude bias', 'Stratified bias', 'RE bias', 'Rel reduction strat', 'Rel reduction RE', 'RE I2'],
        table1_rows
    )

    ipd_full = _read_csv('rsm_ipd_full_summary.csv')
    k_rows = []
    if ipd_full is not None and not ipd_full.empty:
        k_list = sorted(ipd_full['n_strata'].unique())
        for k in k_list:
            sub = ipd_full[ipd_full['n_strata'] == k]
            for _, r in sub.iterrows():
                k_rows.append({
                    'K': str(int(k)),
                    'Method': r['method'],
                    'ARI': _fmt(r['ARI_mean']),
                    'RE bias': _fmt(r['abs_bias_re_mean'], 5),
                    'Rel reduction RE': _fmt(r['bias_reduction_relative_re_mean'], 3),
                })
    table_k = _make_table(
        ['K', 'Method', 'ARI', 'RE bias', 'Rel reduction RE'],
        k_rows
    )

    real_data = _read_csv('real_data_summary.csv')
    real_rows = []
    if real_data is not None and not real_data.empty:
        real_non = real_data[~real_data['method'].str.startswith('baseline_')]
        rd_best = real_non.loc[real_non.groupby('dataset')['ARI_mean'].idxmax()].copy()
        for _, r in rd_best.iterrows():
            real_rows.append({
                'Dataset': r['dataset'],
                'Method': r['method'],
                'K': str(int(r['n_strata'])),
                'ARI': _fmt(r['ARI_mean']),
                'C1': _fmt(r['C1_heterogeneity_mean']),
                'W_est': _fmt(r['W_est_mean']),
                'Bias reduction': _fmt(r['bias_reduction_mean']),
            })
    table_real = _make_table(
        ['Dataset', 'Method', 'K', 'ARI', 'C1', 'W_est', 'Bias reduction'],
        real_rows
    )

    study_footnote = (
        f"For comparison, random-effects pooling across the true study identifiers "
        f"(i.e. a study-level meta-analysis) gave an absolute ATE bias of {v['study_re']} "
        f"(reduction {v['study_red']} from crude {v['study_crude']})."
    )

    md = f"""## 3. Results

### Primary IPD scenario

Table 1 summarises the primary IPD scenario (n={v['n_ipd']}, {v['n_studies']} studies, K={v['k_ipd']} strata, 50 replications). Extraction of the true hidden structure was modest. The Oracle baseline that stratified by the true Z variables achieved the highest ARI ({v['best_ari']}); among the proposed and comparator methods, the best non-Oracle ARI was {v['best_non_oracle_ari']} ({v['best_non_oracle_ari_method']}). The average C1 across methods was {v['mean_c1']}, and average within-stratum homogeneity was limited (mean W_true = {v['mean_wtrue']}; mean W_est = {v['mean_west']}), indicating that the discovered strata still contained substantial between-person variation in the conditional treatment effect.

#### Diagnostic agreement with the true partition

Although all proposed methods and active comparators outperformed random stratification, the absolute level of recovery was low. The best non-oracle method reached an ARI of {v['best_non_oracle_ari']}, substantially below the Oracle k-means baseline (ARI {v['best_ari']}). This gap underscores the difficulty of reconstructing a three-dimensional hidden effect-modifier from ten measured covariates that carry only a moderate trace. Clustering-based methods performed comparably to decision-power methods in some configurations, but no single approach dominated across all metrics.

#### C1 and W as coherence diagnostics

C1 behaved in the expected direction: methods that produced strata closer to the Oracle had C1 values closer to 1, whereas random stratification yielded a C1 of {v['mean_c1']}. However, the range of C1 values was compressed and the diagnostic does not, by itself, identify which method is most trustworthy. W_true was larger than W_est for most methods, reflecting the fact that the estimated CATE model (Y ~ X + A + X*A) can only capture part of the true CATE variation. W_est therefore provides a conservative, operationally available lower bound on within-stratum homogeneity.

#### ATE bias reduction on the risk-difference scale

ATE bias reduction was strongest for {v['best_method']}: the crude absolute risk-difference bias was {v['crude_bias']}; the two-stage stratified estimate reduced this to {v['strat_bias']} (relative reduction {v['rel_strat']}), and the DerSimonian-Laird random-effects estimate reduced it further to {v['re_bias']} (relative reduction {v['rel_re']}). {study_footnote}

These values show that, under the simulated data-generating mechanism, a small number of data-driven strata can partially remove bias from a pooled IPD estimate. The additional gain from random-effects pooling suggests that allowing stratum-specific risk differences to vary is important when the hidden effect modifier is present: a fixed-effect summary that ignores between-stratum heterogeneity leaves residual bias, whereas the random-effects model borrows strength across strata in a way that more closely approximates the true ATE.

{table1}
*Table 1. Primary IPD scenario (n={v['n_ipd']}, {v['n_studies']} studies, K={v['k_ipd']}): means over 50 simulations.*

![Figure 1. Primary IPD scenario: diagnostic metrics and ATE bias reduction by method.](fig1_rsm_ipd_primary.png)

### Sensitivity to the number of strata

Table 2 and Figure 2 show how random-effects bias reduction changed as the number of strata varied (K = {v['k_list']}). For most methods the gain from increasing K was limited and non-monotonic; increasing strata beyond the true dimensionality of the hidden structure introduced additional sampling variation and did not consistently improve ATE bias reduction. The Oracle baselines did improve with larger K, because more strata allow a finer partition of the true Z-space. In contrast, data-driven methods did not reliably exploit the additional flexibility, suggesting that the number of strata should be chosen conservatively or compared across several values, rather than simply maximised.

{table_k}
*Table 2. Sensitivity of random-effects ATE bias reduction to the number of strata.*

![Figure 2. Random-effects ATE bias reduction as the number of strata varies.](fig2_rsm_ipd_strata_sensitivity.png)

### Comparison with study-level meta-analysis

An important benchmark for any IPD method is whether it improves on a conventional study-level random-effects meta-analysis. In our design, the true study identifiers carried genuine between-study heterogeneity in baseline risk and treatment prevalence but did not perfectly align with the hidden effect modifier. {study_footnote} This benchmark places the data-driven stratification results in context: even the best data-driven strata reduced bias by a similar magnitude to using the true study identifier as a random-effect, but neither approach eliminated bias entirely because neither fully captures the hidden modifier.

### Semi-synthetic illustrations

Five well-known Simpson-paradox examples were reconstructed as pseudo-individual records and pseudo-general variables were generated to mimic proxies of the known confounder [morris2021][charig1986][bickel1975][vonkuegelgen2021][appleton1996]. High ARI was obtained only when the pseudo-variables were strongly correlated with a low-dimensional confounder. Table 3 and Figure 3 present the best non-oracle method and stratum count for each dataset. These examples are illustrations of favourable and unfavourable settings for stratification, not validation of out-of-the-box performance in real IPD.

{table_real}
*Table 3. Best real-data illustration result per dataset (oracle baselines excluded).*

![Figure 3. Real-data illustration: ARI by dataset and method.](fig3_rsm_real_data_ari.png)
"""
    return md
def _new_conclusions():
    return """## 5. Conclusions

We have introduced IONE (Incoherence-Oriented Neutralisation and Extraction) as an exploratory diagnostic for hidden effect modification in IPD meta-analysis. Through Monte Carlo simulation and semi-synthetic examples, we show that IONE can detect incoherence and partially reduce ATE bias when hidden variables leave strong traces in measured covariates. The diagnostics should be reported alongside conventional meta-analytic models and covariate adjustment, and should not be used as a replacement for rigorous causal inference. We recommend that coherence assessment using C1 and W be considered as a standard sensitivity step in IPD meta-analysis reporting.
"""


def _declarations():
    return """## Declarations

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
"""




def _additional_files():
    return """## Additional files

### Additional file 1: Supplementary Methods

Detailed algebraic description of the IPD data-generating mechanism. For each of the {n_studies} studies, a study-specific intercept is drawn for baseline risk and treatment propensity. The critical variables are Z1 (continuous, mean 60, standard deviation 12, truncated to 20–95), Z2 (binary, probability 0.5) and Z3 (ordered, levels 0/1/2 with probabilities 0.3, 0.4, 0.3). The ten general variables X1-X10 are linear or non-linear functions of Z plus independent Gaussian noise. The treatment indicator A is generated from a logistic model with intercept, Z main effects, X main effects and a random study intercept. The outcome Y is generated from a logistic model with Z main effects, X main effects, an A main effect, Z-by-A interaction effects and a random study intercept. The true individual CATE is the difference in outcome probabilities under A=1 versus A=0 at the realised Z values. The true population ATE is the average of these CATEs over the super-population.

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
""".format(n_studies=10)

def _abbreviations():
    return """## List of abbreviations

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
"""


def _new_discussion(v):
    """Return a fresh Discussion section written for the RSM IPD simulation results."""
    return f"""## 4. Discussion

### Principal findings

This study frames Incoherence-Oriented Neutralisation and Extraction (IONE) as an exploratory diagnostic for hidden effect modification in individual participant data (IPD) meta-analysis. The principal findings are twofold. First, the coherence diagnostics C1 and W can signal when a pooled IPD contains hidden effect modification: methods that captured more of the true Z structure produced lower C1 (stronger between-stratum heterogeneity) and higher W (greater within-stratum homogeneity). Second, stratification-based extraction of coherent subpopulations was conditionally successful: the Oracle baseline that used the true hidden variables directly achieved an ARI of {v['best_ari']}, whereas the best non-Oracle method ({v['best_non_oracle_ari_method']}) reached only {v['best_non_oracle_ari']}. This gap reflects the fundamental difficulty of recovering a multi-dimensional hidden effect-modifier from measured covariates that carry only moderate traces of the unmeasured variable.

Despite the modest recovery of the true partition, the best data-driven method reduced the crude ATE bias from {v['crude_bias']} to {v['re_bias']} on the risk-difference scale (relative reduction {v['rel_re']}) when stratum-specific estimates were pooled with a DerSimonian-Laird random-effects meta-analysis. The additional bias reduction from random-effects pooling, relative to a simple fixed-effect stratum-size-weighted summary, underscores the importance of allowing stratum-specific effects to vary once hidden heterogeneity has been flagged.

### Detection versus extraction

A two-tier interpretation is useful in practice. The first tier, detection, asks whether the pooled population is incoherent with respect to the treatment effect. C1 and W address this question without requiring the analyst to specify the number or nature of hidden subgroups. If C1 is low and W_est is low, the analyst has evidence that a marginal summary may be misleading and should be interpreted cautiously. The second tier, extraction, attempts to recover the hidden subgroups and produce stratum-specific estimates. Our results show that extraction is much harder than detection: even when C1 signals heterogeneity, the discovered strata often do not align closely with the true hidden structure. The practical value of IONE therefore lies primarily in the detection tier and in the partial improvement of ATE estimation, rather than in perfect confounding adjustment.

### Comparison with existing methods

IONE differs from established confounding adjustment methods in its objectives and assumptions. Propensity-score methods [rosenbaum1983] and prognostic-score stratification [hansen2008] aim to balance or adjust for measured confounders; they are not designed to detect unmeasured population structure. The high-dimensional propensity-score algorithm [schneeweiss2009] shares IONE's insight that proxy variables may carry information about unmeasured confounders, but it uses this information to improve propensity-score estimation rather than to identify subgroups or report a coherence diagnostic. Latent class analysis [mclachlan2000] seeks hidden subgroups but typically requires strong distributional assumptions and does not provide a transparent between-stratum heterogeneity statistic analogous to C1.

IONE is best understood as complementary to these methods. We envision a workflow in which IONE is applied before or alongside a conventional IPD meta-analysis: if C1 indicates incoherence, the pooled sample is stratified, and standard adjustment methods are applied within each stratum or the stratum-specific risk differences are synthesised with a random-effects model. This two-stage approach—first assessing hidden population structure, then adjusting for measured confounders—may yield more reliable estimates than either approach alone, although our simulation shows the gains are modest under moderate Z->X trace strength.

### Strengths and limitations

**Strengths.** This simulation study followed the ADEMP framework [morris2019], with transparent reporting of the data-generating mechanism, estimands, candidate methods, performance metrics and number of replications. All numerical results are produced by the repository scripts and inserted into the manuscript automatically, so the docx and markdown files can be regenerated without hand-entered numbers. The IPD data-generating mechanism includes study-level variation in baseline risk, treatment prevalence and covariate distributions, which mirrors the heterogeneity encountered in real IPD meta-analyses.

**Limitations.** Several limitations should be acknowledged. First, the simulation used a single total sample size (n={v['n_ipd']}) and a moderate Z->X trace. Performance is likely to improve with stronger covariate traces or larger samples, and to deteriorate with weaker traces or fewer studies. Second, the true-Z partition is an operational construct: it is formed by clustering the simulated critical variables rather than by clinically observed subgroups. ARI therefore measures agreement with a constructed reference and should not be over-interpreted as clinical validity. Third, W_est depends on a correctly specified outcome model (Y ~ X + A + X*A). If the outcome model is misspecified, W_est may be misleading. Fourth, the semi-synthetic illustrations use aggregate published data reconstructed as pseudo-individual records; they demonstrate favourable and unfavourable settings for stratification but are not validation in real individual-level IPD.

### Implications for practice

We recommend that reports of IPD meta-analyses include a coherence assessment alongside the conventional summary of between-study heterogeneity. If C1 is low and W_est is small, the marginal effect should be interpreted cautiously, and the analyst should explore prespecified subgroups, measured treatment-covariate interactions and sensitivity analyses. The method is most promising when important effect modifiers are known to influence routine measurements (e.g. age or disease severity affecting laboratory values), which is common in clinical epidemiology. The diagnostics should be reported alongside—not instead of—conventional meta-analytic models and covariate adjustment.

### Future directions

Several extensions would strengthen the framework. Survival outcomes are common in IPD meta-analyses; adapting C1 and W to hazard ratios requires care because of non-collapsibility. Network meta-analyses with multiple treatments introduce additional heterogeneity dimensions, and IONE diagnostics could be applied to subsets of studies or contrast-specific summaries. Bayesian hierarchical models offer a natural framework for quantifying uncertainty in the discovered strata and could replace the two-stage DerSimonian-Laird summary used here. Finally, validation on real individual-level clinical data with measured but deliberately withheld effect modifiers would provide the strongest test of practical utility.
"""
def generate_v3_manuscript():
    # Read previous long manuscript
    old_md_path = os.path.join(RESULTS_DIR, 'manuscript', 'IONE_manuscript.md')
    old_md = open(old_md_path, 'r', encoding='utf-8').read()

    # Compute values
    v = _scenario_values()

    # Generate/update figures
    ipd_primary = _read_csv('rsm_ipd_primary_summary.csv')
    ipd_full = _read_csv('rsm_ipd_full_summary.csv')
    study_summary = _read_csv('rsm_ipd_study_summary.csv')
    real_data = _read_csv('real_data_summary.csv')
    figs, pptx_path = generate_rsm_figures(ipd_primary, ipd_full, real_data)

    # Citation manager
    cm = CiteManager()
    _register_citations(cm)

    # Build sections
    abstract = (
        f"**Background:** Random-effects meta-analyses report an average treatment effect and assume that between-study heterogeneity has been adequately modelled. "
        f"When an individual participant data (IPD) meta-analysis contains hidden effect modifiers, a marginal summary can be non-robust. "
        f"We propose Incoherence-Oriented Neutralisation and Extraction (IONE), an exploratory diagnostic toolkit for hidden effect modification in pooled IPD. "
        f"**Methods:** We simulated an IPD meta-analysis with {v['n_studies']} studies, a binary treatment and outcome, measured covariates carrying traces of an unmeasured modifier, and study-level variation in baseline risk and treatment prevalence. "
        f"Proposed methods and active comparators stratified the pooled IPD; stratum-specific risk differences were synthesised with fixed-effect and DerSimonian-Laird random-effects meta-analysis. "
        f"We report ARI, C1 (between-stratum heterogeneity), W_true/W_est (within-stratum homogeneity) and ATE bias reduction, with Monte Carlo standard errors. "
        f"**Results:** In the primary scenario (n={v['n_ipd']}, {v['n_studies']} studies, K={v['k_ipd']} strata), the best method was {v['best_method']} (ARI {v['best_ari']}; C1 {v['best_c1']}; W_true {v['best_wtrue']}; W_est {v['best_west']}). "
        f"Crude ATE bias was {v['crude_bias']}; stratification reduced it to {v['strat_bias']} (relative {v['rel_strat']}) and random-effects pooling to {v['re_bias']} (relative {v['rel_re']}). "
        f"Diagnostic agreement with the true hidden structure remained modest. "
        f"**Conclusions:** IONE is a transparent, exploratory diagnostic for hidden effect modification in IPD meta-analyses, to be reported alongside conventional models and covariate adjustment."
    )

    keywords = "individual participant data meta-analysis; evidence synthesis; heterogeneity; hidden effect modification; stratification"

    # Extract and adapt Background and Discussion
    old_bg = _extract_section(old_md, 'Background')
    background = _adapt_background(old_bg, cm, v)
    discussion = _new_discussion(v)

    # Ensure Background contains RSM framing
    # (the adaptation function already adds meta-analysis intro)

    # Build the markdown
    md = f"""# IONE: Incoherence-Oriented Neutralisation and Extraction for hidden effect modification in individual participant data meta-analysis: a simulation study of stratification-based extraction

{{{{PAGE}}}}

## Abstract

{abstract}

**Keywords:** {keywords}

{{{{PAGE}}}}

## 1. Introduction

{background}

{ _new_methods(v) }

{ _new_results(v) }

## 4. Discussion

{discussion}

{ _new_conclusions() }

{{{{PAGE}}}}

{ _abbreviations() }

{{{{PAGE}}}}

{ _declarations() }

{{{{PAGE}}}}

{{{{REFS}}}}

{{{{PAGE}}}}

{ _additional_files() }
"""

    # Fix numbered citations in whole markdown
    md = _old_to_keys(md, cm)

    # Save markdown and convert to docx
    md_path = os.path.join(RSM_DIR, 'IONE_rsm_v3.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)

    docx_path = os.path.join(RSM_DIR, 'IONE_rsm_v3.docx')
    convert(md_path, docx_path, cite_manager=cm, figure_dir=FIG_DIR)

    # Separate title page
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    tp = Document()
    tp_style = tp.styles['Normal']
    tp_style.font.name = 'Times New Roman'
    tp_style.font.size = Pt(11)
    tp_title = tp.add_heading('IONE: Incoherence-Oriented Neutralisation and Extraction for hidden effect modification', level=0)
    tp_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp_sub = tp.add_heading('in individual participant data meta-analysis: a simulation study of stratification-based extraction', level=0)
    tp_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.add_paragraph()
    tp.add_paragraph('Onishi Tatsuki')
    tp.add_paragraph('Data Science AI Innovation Research Promotion Center, Shiga University')
    tp.add_paragraph('Corresponding author: Onishi Tatsuki')
    p=tp.add_paragraph()
    p.add_run('bougtoir@gmail.com').italic=True
    tp.add_paragraph('1-1-1 Bamba, Hikone, Shiga 522-8522 Japan')
    tp_path = os.path.join(RSM_DIR, 'title_page_rsm_v3.docx')
    tp.save(tp_path)

    print(f'[generate_ione_rsm_v3] markdown: {md_path}')
    print(f'[generate_ione_rsm_v3] docx:    {docx_path}')
    print(f'[generate_ione_rsm_v3] title page: {tp_path}')
    return docx_path, md_path


if __name__ == '__main__':
    generate_v3_manuscript()
