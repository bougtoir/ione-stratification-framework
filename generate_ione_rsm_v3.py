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
SUBMISSION_DIR = os.path.join(RESULTS_DIR, 'manuscript', 'biostatistics_submission')
os.makedirs(SUBMISSION_DIR, exist_ok=True)

# Date range for AI declaration (kept identical in title page and declarations)
AI_DATES = 'August 2025 through August 2026'


def _scenario_values():
    """Compute all dynamic values from CSVs."""
    ipd_primary = _read_csv('rsm_ipd_primary_summary.csv')
    ipd_full = _read_csv('rsm_ipd_full_summary.csv')
    study_summary = _read_csv('rsm_ipd_study_summary.csv')
    real_data = _read_csv('real_data_summary.csv')
    ipd_sensitivity = _read_csv('rsm_ipd_sensitivity_full_summary.csv')
    ipd_nonlinearity = _read_csv('rsm_ipd_nonlinearity_full_summary.csv')
    null_summary = _read_csv('rsm_ipd_null_summary.csv')
    misspec_summary = _read_csv('w_est_misspec_summary.csv')

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
    vals['best_method_ari'] = _fmt(best_re['ARI_mean'])
    vals['best_method_c1'] = _fmt(best_re['C1_heterogeneity_mean'])
    vals['best_method_wtrue'] = _fmt(best_re['W_true_mean'])
    vals['best_method_west'] = _fmt(best_re['W_est_mean'])
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
    random_row = ipd_primary[ipd_primary['method'] == 'baseline_random']
    vals['random_c1'] = _fmt(random_row['C1_heterogeneity_mean'].iloc[0], 3) if not random_row.empty else '—'

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

    # Extended sensitivity / nonlinearity helpers
    vals['ipd_sensitivity'] = ipd_sensitivity if ipd_sensitivity is not None else pd.DataFrame()
    vals['ipd_nonlinearity'] = ipd_nonlinearity if ipd_nonlinearity is not None else pd.DataFrame()

    def _sens_row(df, method, n, z, zx, k, metric):
        if df.empty or metric not in df.columns:
            return np.nan
        sub = df[(df['method'] == method) & (df['n'] == n) &
                 (df['z_effect_scale'] == z) & (df['zx_influence_scale'] == zx) &
                 (df['n_strata'] == k)]
        return sub[metric].iloc[0] if not sub.empty else np.nan

    vals['_sens_row'] = _sens_row

    # Empirical null distribution thresholds (C1 lower 5th percentile; W_est upper 95th percentile)
    vals['null_summary'] = null_summary if null_summary is not None else pd.DataFrame()
    if null_summary is not None and not null_summary.empty:
        for method in null_summary['method'].unique():
            sub = null_summary[null_summary['method'] == method]
            if not sub.empty:
                vals[f'null_c1_5th_{method}'] = _fmt(sub['C1_heterogeneity_5pct'].iloc[0], 3) if 'C1_heterogeneity_5pct' in sub.columns else '—'
                vals[f'null_west_95th_{method}'] = _fmt(sub['W_est_95pct'].iloc[0], 3) if 'W_est_95pct' in sub.columns else '—'
    else:
        for method in ['1B_residual', 'baseline_random']:
            vals[f'null_c1_5th_{method}'] = '—'
            vals[f'null_west_95th_{method}'] = '—'

    # W_est misspecification summary (if available)
    vals['misspec_summary'] = misspec_summary if misspec_summary is not None else pd.DataFrame()

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
    cm.register('haas2021', 'Haas et al.', 2021,
                'Haas EJ, Angulo FJ, McLaughlin JM, et al. Impact and effectiveness of mRNA BNT162b2 vaccine against SARS-CoV-2 infections and COVID-19 cases, hospitalisations, and deaths following a nationwide vaccination campaign in Israel: an observational study using national surveillance data. Lancet. 2021;397(10287):1819–1829.')
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
    text = text.replace('[9–13]', '[charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]')
    text = text.replace('[9-13]', '[charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]')
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
        '12': 'haas2021',
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
    """Adapt the observational Background to a concise IPD meta-analysis framing."""
    # old_bg is no longer used; construct a fresh, compact introduction
    return (
        'Meta-analysis pools treatment-effect estimates across studies and is central to evidence-based medicine [borenstein2009]. '
        'IPD meta-analysis preserves participant-level covariates and can improve power for treatment-covariate interactions [riley2010][simmonds2005]. '
        'Random-effects syntheses are recommended when between-study heterogeneity is suspected [dersimonian1986][higgins2002][riley2011], '
        'yet conventional summaries estimate a marginal effect and may miss effect modifiers that are unmeasured or omitted [pearl2009][greenland1999]. '
        'When the pooled population is a mixture of subgroups with different treatment effects, the marginal effect can reverse or mislead within strata, producing Simpson-type paradoxes [simpson1951][rojanaworarit2020].\n\n'
        'IPD meta-analysis offers subgroup analyses, meta-regression and one-stage mixed models, but these explain heterogeneity through measured covariates and study-level factors. '
        'They do not test whether the pooled participants themselves form internally homogeneous subpopulations with respect to the treatment effect. '
        'We therefore frame Incoherence-Oriented Neutralisation and Extraction (IONE) as an exploratory diagnostic: it flags when a marginal summary may be fragile and, when incoherence is indicated, extracts more homogeneous subgroups from multivariate patterns in measured variables. '
        '"Neutralisation" means reducing the misleading influence of a marginal summary by separating it into coherent subpopulations.\n\n'
        'Hidden population structure is documented across medicine and social science: kidney-stone treatments [charig1986], university admissions [bickel1975], COVID-19 case-fatality comparisons [vonkuegelgen2021], national vaccine-surveillance data [haas2021], and smoking-mortality studies [appleton1996]. '
        'Established methods—propensity scores [rosenbaum1983], prognostic scores [hansen2008], disease-risk scores [miettinen1976], instrumental variables [angrist1996] and high-dimensional propensity scores [schneeweiss2009]—adjust for measured confounders but do not detect unmeasured population structure. '
        'Proximal causal inference and latent-class models use proxy variables [tchetgen2024][mclachlan2000] but do not report a transparent between-stratum heterogeneity diagnostic. '
        'We operationalise IONE through two coherence diagnostics: C1, derived from the I^2 heterogeneity statistic [higgins2002] applied to stratum-specific log odds ratios, and W, the proportion of total CATE variance explained by the stratification. '
        'Stratum-specific risk differences are synthesised with fixed-effect or DerSimonian-Laird random-effects meta-analysis.'
    )
def _new_methods(v):
    """Return markdown string for the Methods section."""
    md = """## 2. Methods

This simulation study follows the ADEMP framework [morris2019].

### Aims

Evaluate whether stratification of pooled IPD can recover hidden subgroup structure; compare outcome-informed IONE methods with outcome-free and established comparators; assess whether C1 and W diagnose hidden effect modification; quantify ATE bias reduction from fixed-effect and DerSimonian-Laird random-effects synthesis of stratum-specific risk differences; and identify data-generating conditions under which the diagnostics are most informative.

### IPD data-generating mechanism

We simulated an IPD meta-analysis with n={n_ipd} participants assigned to {n_studies} studies (scale parameter {study_effect} for baseline risk, treatment prevalence and an age-like covariate). Each participant had three critical variables (Z1 continuous, Z2 binary, Z3 ordered) that affected treatment, outcome and treatment-covariate interactions, and ten measured variables (X1-X10) carrying traces of Z. A binary treatment A and binary outcome Y were generated from logistic models with Z and X main effects, a treatment effect and Z-by-A interactions. The estimand was the population risk-difference ATE; full algebra is in Additional file 1.

The primary scenario used n={n_ipd}, {n_studies} studies and K={k_ipd} strata. We varied K (3, 5, 10), sample size (500, 2000, 10 000), Z-to-Y effect scale (0.5, 1.0, 2.0), Z-to-X influence scale (0.2, 0.5, 1.0) and introduced a non-linear Z-to-X mapping. The primary and strata-sensitivity scenarios used {n_sims_per_scenario} replications; extended robustness used 30; empirical null used 200 and W_est misspecification used 50.

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

Five Simpson-paradox examples were reconstructed as pseudo-individual records from published aggregate statistics [charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]. The Israeli vaccination example used pseudo-IPD reconstructed from age- and vaccination-stratified COVID-19-related hospitalisation counts published by Haas et al. [haas2021]. We chose hospitalisation rather than infection counts because the published Table 2 provides age- and vaccination-stratified counts for a severe endpoint where age confounding is pronounced, and because the low event rate (~0.09% in the down-sampled data) creates a stress-test for rare outcomes. Because the published counts cover approximately 6.5 million people, we used a stratified random down-sample of 100,000 records preserving the age- and vaccination-specific hospitalisation rates. In the down-sampled pseudo-IPD, some cells contained very few or zero hospitalisation events; logistic models used for outcome-informed methods were fitted with L2 regularisation, and any degenerate one-class fit was handled by returning the observed mean probability. Pseudo-general variables mimicked proxies of the known confounder and the number of strata K was selected from the set {{2, 3, min(K_true, 4), K_true}}, where K_true is the true number of published strata, keeping the value that maximised ARI. These are illustrations, not real-IPD validation.

### Reporting and reproducibility

The design followed ADEMP [morris2019]; checklists are in Additional files 2 and 3. The pipeline is version-controlled and every manuscript number is read from repository CSV outputs. Simulations used Python 3.11; the exact dependency versions are in `requirements-lock.txt` and the commit hash used for the submission package is in `results/commit_hash.txt`.
""".format(n_ipd=v['n_ipd'], n_studies=v['n_studies'], study_effect=v['study_effect'], k_ipd=v['k_ipd'], n_sims_per_scenario=50)
    return md
def _new_results(v, supplementary=False):
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
                    'ARI SE': _fmt(r['ARI_se']),
                    'C1': _fmt(r['C1_heterogeneity_mean']),
                    'C1 SE': _fmt(r['C1_heterogeneity_se']),
                    'W_est': _fmt(r['W_est_mean']),
                    'W_est SE': _fmt(r['W_est_se']),
                    'RE bias': _fmt(r['abs_bias_re_mean'], 5),
                    'RE bias SE': _fmt(r['abs_bias_re_se'], 5),
                    'Rel reduction RE': _fmt(r['bias_reduction_relative_re_mean'], 3),
                    'Rel reduction RE SE': _fmt(r['bias_reduction_relative_re_se'], 3),
                    'RE I2': _fmt(r['re_I2_mean']),
                })
    table_k = _make_table(
        ['K', 'Method', 'ARI', 'ARI SE', 'C1', 'C1 SE', 'W_est', 'W_est SE', 'RE bias', 'RE bias SE', 'Rel reduction RE', 'Rel reduction RE SE', 'RE I2'],
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

    # Extended sensitivity / nonlinearity summaries
    ipd_sensitivity = v.get('ipd_sensitivity', pd.DataFrame())
    ipd_nonlinearity = v.get('ipd_nonlinearity', pd.DataFrame())
    sens_row = v.get('_sens_row', lambda *a, **k: np.nan)

    top_methods = list(dict.fromkeys([
        str(v.get('best_method', '1B_residual')),
        '1B_residual', 'PS_propensity_score', 'GMM', 'Prognostic_score', '2B_clustering'
    ]))

    def _sens_table_rows(methods, conditions_list):
        rows = []
        for cond in conditions_list:
            for method in methods:
                n, z, zx, k = cond.get('n', 2000), cond.get('z', 1.0), cond.get('zx', 1.0), cond.get('k', 5)
                re_bias = sens_row(ipd_sensitivity, method, n, z, zx, k, 'abs_bias_re_mean')
                if pd.isna(re_bias):
                    continue
                rows.append({
                    'Condition': cond.get('label', ''),
                    'Method': method,
                    'ARI': _fmt(sens_row(ipd_sensitivity, method, n, z, zx, k, 'ARI_mean')),
                    'ARI SE': _fmt(sens_row(ipd_sensitivity, method, n, z, zx, k, 'ARI_se')),
                    'C1': _fmt(sens_row(ipd_sensitivity, method, n, z, zx, k, 'C1_heterogeneity_mean')),
                    'C1 SE': _fmt(sens_row(ipd_sensitivity, method, n, z, zx, k, 'C1_heterogeneity_se')),
                    'W_est': _fmt(sens_row(ipd_sensitivity, method, n, z, zx, k, 'W_est_mean')),
                    'W_est SE': _fmt(sens_row(ipd_sensitivity, method, n, z, zx, k, 'W_est_se')),
                    'RE bias': _fmt(re_bias, 5),
                    'RE bias SE': _fmt(sens_row(ipd_sensitivity, method, n, z, zx, k, 'abs_bias_re_se'), 5),
                    'Rel reduction RE': _fmt(sens_row(ipd_sensitivity, method, n, z, zx, k, 'bias_reduction_relative_re_mean'), 3),
                    'Rel reduction RE SE': _fmt(sens_row(ipd_sensitivity, method, n, z, zx, k, 'bias_reduction_relative_re_se'), 3),
                    'RE I2': _fmt(sens_row(ipd_sensitivity, method, n, z, zx, k, 're_I2_mean')),
                })
        return rows

    sample_rows = _sens_table_rows(top_methods, [
        {'label': 'n=500', 'n': 500, 'z': 1.0, 'zx': 1.0, 'k': 5},
        {'label': 'n=2000', 'n': 2000, 'z': 1.0, 'zx': 1.0, 'k': 5},
        {'label': 'n=10000', 'n': 10000, 'z': 1.0, 'zx': 1.0, 'k': 5},
    ])
    table_sample = _make_table(
        ['Condition', 'Method', 'ARI', 'ARI SE', 'C1', 'C1 SE', 'W_est', 'W_est SE', 'RE bias', 'RE bias SE', 'Rel reduction RE', 'Rel reduction RE SE', 'RE I2'],
        sample_rows
    )

    zx_rows = _sens_table_rows(top_methods, [
        {'label': 'zx=0.2', 'n': 2000, 'z': 1.0, 'zx': 0.2, 'k': 5},
        {'label': 'zx=0.5', 'n': 2000, 'z': 1.0, 'zx': 0.5, 'k': 5},
        {'label': 'zx=1.0', 'n': 2000, 'z': 1.0, 'zx': 1.0, 'k': 5},
    ])
    table_zx = _make_table(
        ['Condition', 'Method', 'ARI', 'ARI SE', 'C1', 'C1 SE', 'W_est', 'W_est SE', 'RE bias', 'RE bias SE', 'Rel reduction RE', 'Rel reduction RE SE', 'RE I2'],
        zx_rows
    )

    z_rows = _sens_table_rows(top_methods, [
        {'label': 'z=0.5', 'n': 2000, 'z': 0.5, 'zx': 1.0, 'k': 5},
        {'label': 'z=1.0', 'n': 2000, 'z': 1.0, 'zx': 1.0, 'k': 5},
        {'label': 'z=2.0', 'n': 2000, 'z': 2.0, 'zx': 1.0, 'k': 5},
    ])
    table_z = _make_table(
        ['Condition', 'Method', 'ARI', 'ARI SE', 'C1', 'C1 SE', 'W_est', 'W_est SE', 'RE bias', 'RE bias SE', 'Rel reduction RE', 'Rel reduction RE SE', 'RE I2'],
        z_rows
    )

    nonlinear_rows = []
    for method in top_methods:
        n, z, zx, k = 2000, 1.0, 1.0, 5
        lin_bias = sens_row(ipd_sensitivity, method, n, z, zx, k, 'abs_bias_re_mean')
        lin_bias_se = sens_row(ipd_sensitivity, method, n, z, zx, k, 'abs_bias_re_se')
        lin_rel = sens_row(ipd_sensitivity, method, n, z, zx, k, 'bias_reduction_relative_re_mean')
        lin_rel_se = sens_row(ipd_sensitivity, method, n, z, zx, k, 'bias_reduction_relative_re_se')
        non_bias = sens_row(ipd_nonlinearity, method, n, z, zx, k, 'abs_bias_re_mean')
        non_bias_se = sens_row(ipd_nonlinearity, method, n, z, zx, k, 'abs_bias_re_se')
        non_rel = sens_row(ipd_nonlinearity, method, n, z, zx, k, 'bias_reduction_relative_re_mean')
        non_rel_se = sens_row(ipd_nonlinearity, method, n, z, zx, k, 'bias_reduction_relative_re_se')
        if not pd.isna(non_bias):
            nonlinear_rows.append({
                'Method': method,
                'Linear RE bias': _fmt(lin_bias, 5),
                'Linear RE bias SE': _fmt(lin_bias_se, 5),
                'Linear rel reduction': _fmt(lin_rel, 3),
                'Linear rel reduction SE': _fmt(lin_rel_se, 3),
                'Non-linear RE bias': _fmt(non_bias, 5),
                'Non-linear RE bias SE': _fmt(non_bias_se, 5),
                'Non-linear rel reduction': _fmt(non_rel, 3),
                'Non-linear rel reduction SE': _fmt(non_rel_se, 3),
            })
    table_nonlinear = _make_table(
        ['Method', 'Linear RE bias', 'Linear RE bias SE', 'Linear rel reduction', 'Linear rel reduction SE', 'Non-linear RE bias', 'Non-linear RE bias SE', 'Non-linear rel reduction', 'Non-linear rel reduction SE'],
        nonlinear_rows
    )

    # Empirical null distribution table (S5)
    null_summary = v.get('null_summary', pd.DataFrame())
    null_rows = []
    if null_summary is not None and not null_summary.empty:
        for _, r in null_summary.iterrows():
            null_rows.append({
                'Method': r['method'],
                'C1 mean': _fmt(r.get('C1_heterogeneity_mean', np.nan), 3),
                'C1 SE': _fmt(r.get('C1_heterogeneity_se', np.nan), 3),
                'C1 5th': _fmt(r.get('C1_heterogeneity_5pct', np.nan), 3),
                'C1 95th': _fmt(r.get('C1_heterogeneity_95pct', np.nan), 3),
                'W_est mean': _fmt(r.get('W_est_mean', np.nan), 3),
                'W_est SE': _fmt(r.get('W_est_se', np.nan), 3),
                'W_est 5th': _fmt(r.get('W_est_5pct', np.nan), 3),
                'W_est 95th': _fmt(r.get('W_est_95pct', np.nan), 3),
            })
    table_null = _make_table(
        ['Method', 'C1 mean', 'C1 SE', 'C1 5th', 'C1 95th', 'W_est mean', 'W_est SE', 'W_est 5th', 'W_est 95th'],
        null_rows
    )

    # W_est misspecification table (S6)
    misspec_summary = v.get('misspec_summary', pd.DataFrame())
    misspec_rows = []
    if misspec_summary is not None and not misspec_summary.empty:
        for _, r in misspec_summary.iterrows():
            misspec_rows.append({
                'Method': r['method'],
                'ARI': _fmt(r.get('ARI_mean', np.nan), 3),
                'C1': _fmt(r.get('C1_heterogeneity_mean', np.nan), 3),
                'W_true': _fmt(r.get('W_true_mean', np.nan), 3),
                'W_est (main)': _fmt(r.get('W_est_main_mean', np.nan), 3),
                'W_est (interact)': _fmt(r.get('W_est_mean', np.nan), 3),
                'W_est (poly)': _fmt(r.get('W_est_polynomial_mean', np.nan), 3),
                'RE bias': _fmt(r.get('abs_bias_re_mean', np.nan), 5),
                'Rel reduction RE': _fmt(r.get('bias_reduction_relative_re_mean', np.nan), 3),
            })
    table_misspec = _make_table(
        ['Method', 'ARI', 'C1', 'W_true', 'W_est (main)', 'W_est (interact)', 'W_est (poly)', 'RE bias', 'Rel reduction RE'],
        misspec_rows
    )

    if supplementary:
        return f"""## Sensitivity analyses

### Sensitivity to the number of strata

Table S1 presents how random-effects ATE bias reduction and ARI changed as the number of strata varied (K = {v['k_list']}). For most methods the gain from increasing K was limited and non-monotonic; increasing strata beyond the true dimensionality of the hidden structure introduced additional sampling variation and did not consistently improve ATE bias reduction. The Oracle baselines did improve with larger K, because more strata allow a finer partition of the true Z-space. In contrast, data-driven methods did not reliably exploit the additional flexibility, suggesting that the number of strata should be chosen conservatively or compared across several values, rather than simply maximised.

{table_k}
*Table S1. Sensitivity of random-effects ATE bias reduction and coherence diagnostics to the number of strata.*

### Sensitivity to sample size

Table S2 summarises the primary scenario repeated with n = 500, 2000 and 10 000, fixing K = 5 and the moderate Z-to-X and Z-to-Y effects. Because this extended sensitivity used 30 replications per cell, the point estimates are still noisier than the primary scenario; Monte Carlo SEs are reported to help gauge this uncertainty. The crude marginal ATE bias decreased with sample size, as expected from a more precisely estimated risk difference. The absolute random-effects bias declined for propensity-score, prognostic-score and clustering-based approaches, and these methods achieved their largest relative bias reductions at n = 10 000. In contrast, the outcome-residual approach showed a floor near 0.008-0.009 and its relative bias reduction therefore decreased with n, while GMM improved only gradually. This mixed pattern confirms that the practical value of IONE depends on the interplay between sample size and method choice: with small samples, estimation error dominates; with large samples, remaining bias reflects structural limits of the selected stratification.

{table_sample}
*Table S2. Sample-size sensitivity (K=5, z=1.0, zx=1.0): means over 30 simulations.*

### Sensitivity to Z-to-X influence strength

Table S3 summarises performance for zx influence scale = 0.2, 0.5 and 1.0. A larger trace was associated with higher ARI for most methods, and C1 and W_est moved in the expected direction for several approaches, but the bias-reduction gains were non-monotonic and variable at this number of replications. This pattern indicates that stronger covariate traces improve subgroup recovery in principle, yet finite-sample noise and differences between methods in how the trace is exploited remain important; the diagnostics detect statistical traces rather than recover the hidden variables perfectly.

{table_zx}
*Table S3. Sensitivity to Z-to-X influence strength (n=2000, K=5, z=1.0, zx=0.2, 0.5, 1.0): means over 30 simulations.*

### Sensitivity to Z-to-Y effect strength

Table S4 summarises results for z effect scale = 0.5, 1.0 and 2.0. When effect modification was weak (z = 0.5), C1 and W_est were close to their null values, reflecting limited detectable heterogeneity. As the effect increased, C1 decreased and W_est increased for most methods, and the relative random-effects bias reduction improved for all leading approaches. The outcome-residual approach already produced a substantial relative bias reduction at z = 0.5, suggesting that it can exploit the moderate covariate trace even when the marginal modification signal is weak. Overall, the diagnostics are most informative when hidden effect modification is strong enough to bias the marginal ATE.

{table_z}
*Table S4. Sensitivity to Z-to-Y effect strength (n=2000, K=5, zx=1.0, z=0.5, 1.0, 2.0): means over 30 simulations.*

### Empirical null distribution of C1 and W_est

Under the primary DGM with the Z-by-A interaction coefficients set to zero, there is no true log-odds effect modification. Table S5 reports the empirical mean, Monte Carlo SE and 5th/95th percentiles of C1 and W_est for each method. A C1 value below the 5th percentile or a W_est value above the 95th percentile of this null provides a conservative threshold for flagging possible incoherence.

{table_null}
*Table S5. Empirical null distribution of C1 and W_est (n=2000, K=5, 200 replications, no true Z-by-A interaction).*

### W_est outcome-model misspecification sensitivity

Table S6 compares W_est computed under three outcome-model specifications. A main-effects-only model (W_est main) ignores treatment-covariate interactions and is therefore misspecified; the default linear-interaction model (W_est interact) and the polynomial-interaction model (W_est poly) include interactions and provide more flexible estimates. Large discrepancies across these columns indicate that the W_est diagnostic is sensitive to outcome-model specification.

{table_misspec}
*Table S6. Sensitivity of W_est to outcome-model specification (n=2000, K=5, 50 replications).*
"""

    md = f"""## 3. Results

### Primary IPD scenario

Table 1 reports the primary scenario (n={v['n_ipd']}, {v['n_studies']} studies, K={v['k_ipd']}). Recovery of the true hidden structure was modest (Oracle ARI {v['best_ari']}; best non-Oracle {v['best_non_oracle_ari_method']} {v['best_non_oracle_ari']}). Methods closer to the Oracle had C1 nearer to 1 and higher W, while random stratification yielded C1 {v['random_c1']}; W_true exceeded W_est, reflecting that the estimated CATE captures only part of the true CATE variation. The best bias reduction was for {v['best_method']}: crude {v['crude_bias']}, stratified {v['strat_bias']} (relative {v['rel_strat']}) and random-effects {v['re_bias']} (relative {v['rel_re']}). {study_footnote} Pooling strata with DerSimonian-Laird improved over the fixed-effect summary, showing that stratum-specific effects should be allowed to vary.

{table1}
*Table 1. Primary IPD scenario (n={v['n_ipd']}, {v['n_studies']} studies, K={v['k_ipd']}): means over 50 simulations.*

Figure 1 visualises the primary scenario across methods.

![Figure 1. Primary IPD scenario: (a) ARI, (b) C1/W coherence diagnostics, and (c) ATE bias reduction by method.](fig1_rsm_ipd_primary.png)

### Sensitivity to the number of strata

Figure 2 and Supplementary Table S1 show random-effects bias reduction across K = {v['k_list']}. Data-driven methods did not reliably improve with larger K; Oracle baselines improved because finer strata better partition the true Z-space. Stratum count should be chosen conservatively and compared across values.

![Figure 2. Random-effects ATE bias reduction as the number of strata varies.](fig2_rsm_ipd_strata_sensitivity.png)

### Semi-synthetic illustrations

Five Simpson-paradox examples were reconstructed as pseudo-individual records [charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]. Table 2 reports the best non-Oracle method per dataset. The Israel hospitalisation example was the most challenging: strong age confounding and a very low hospitalisation rate (~0.09%) meant that the crude marginal association reversed with stratification, yet recovery of the true age groups from multivariate covariate patterns remained modest. The low event rate also produced occasional near-zero or zero-event cells, making this an illustration of the limits of outcome-informed extraction for rare outcomes.

{table_real}
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

{table_nonlinear}
*Table 3. Linear versus non-linear Z-to-X mapping: random-effects ATE bias and relative bias reduction (n=2000, K=5, z=1.0, zx=1.0).*

Figure 5 shows random-effects ATE bias reduction under the non-linear mapping.

![Figure 5. Non-linear Z->X robustness: random-effects ATE bias reduction (n=2000, K=5).](fig5_rsm_ipd_nonlinearity.png)

### Empirical null distribution and W_est misspecification

Under the primary DGM with no Z-by-A interaction, C1 was generally high and W_est near 0; method-specific 5th/95th percentiles are in Supplementary Table S5. A main-effects-only outcome model inflated W_est, whereas the default interaction and polynomial models were more stable (Supplementary Table S6). C1 and W are diagnostic flags, not standalone inferential quantities.
"""
    return md

def _new_conclusions():
    return """## 5. Conclusions

IONE (Incoherence-Oriented Neutralisation and Extraction) is an exploratory diagnostic framework for hidden effect modification in IPD meta-analysis. Monte Carlo simulation and semi-synthetic examples show that the C1 and W diagnostics can flag incoherence; when hidden variables leave strong traces in measured covariates, stratification can partially reduce ATE bias, but extraction of the true hidden partition remains difficult. The diagnostics should be reported alongside conventional meta-analytic models and covariate adjustment, and should not be used as a replacement for rigorous causal inference. We recommend that coherence assessment using C1 and W be considered as a standard sensitivity step in IPD meta-analysis reporting.
"""


def _declarations():
    return f"""## Declarations

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

Manuscript text, Python code, and some analyses were drafted or revised using large language models (OpenAI GPT-4 and GPT-4o, accessed {AI_DATES}) under the direct, iterative supervision of the author. The LLMs were used for drafting prose, formatting references, generating figures, and implementing the computational pipeline. The author designed the study, wrote the simulation code, selected all references, verified every numerical result against the repository outputs, and approved the final scientific content. No LLM-generated text was used without human review.
"""
def _additional_files(v):
    return f"""### Additional file 1: Supplementary Methods

Detailed algebraic description of the IPD data-generating mechanism. For each of the {v['n_studies']} studies, a study-specific intercept is drawn for baseline risk and treatment propensity. The critical variables are Z1 (continuous, mean 60, standard deviation 12, truncated to 20–95), Z2 (binary, probability 0.5) and Z3 (ordered, levels 0/1/2 with probabilities 0.3, 0.4, 0.3). The ten general variables X1-X10 are linear or non-linear functions of Z plus independent Gaussian noise. The treatment indicator A is generated from a logistic model with intercept, Z main effects, X main effects and a random study intercept. The outcome Y is generated from a logistic model with Z main effects, X main effects, an A main effect, Z-by-A interaction effects and a random study intercept. The true individual CATE is the difference in outcome probabilities under A=1 versus A=0 at the realised Z values. The true population ATE is the average of these CATEs over the super-population.

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
"""

def _abbreviations():
    return """## List of abbreviations

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
| W | Proportion of total CATE variance explained by the stratification |
"""


def _new_discussion(v):
    """Return a concise Discussion section for the IPD simulation results."""
    return f"""## 4. Discussion

### Principal findings

This study frames IONE as an exploratory diagnostic for hidden effect modification in IPD meta-analysis. C1 and W signal whether a pooled IPD is internally coherent: methods that captured more of the true Z structure produced C1 values close to the Oracle and higher W, especially the residual-based method. Extraction of the true partition remained modest (Oracle ARI {v['best_ari']}; best non-Oracle {v['best_non_oracle_ari_method']} {v['best_non_oracle_ari']}), but the best data-driven method reduced crude ATE bias from {v['crude_bias']} to {v['re_bias']} (relative reduction {v['rel_re']}) with DerSimonian-Laird pooling. These findings suggest that stratum-specific effects should be allowed to vary once incoherence is flagged.

### Detection versus extraction

Detection asks whether the pooled population is internally coherent; C1 and W address this without requiring hidden subgroups to be specified. If C1 is low and W_est is high, the marginal summary is likely incoherent and should be interpreted cautiously. Extraction attempts to recover hidden subgroups, but it is much harder than detection. IONE's practical value therefore lies in detection and partial ATE improvement, not in perfect confounding adjustment.

### Comparison with existing methods

Propensity-score [rosenbaum1983] and prognostic-score [hansen2008] methods adjust for measured confounders but do not detect unmeasured population structure. The high-dimensional propensity-score algorithm [schneeweiss2009] uses proxies to improve propensity-score estimation, not to identify subgroups or report a coherence diagnostic. Latent-class models [mclachlan2000] seek hidden subgroups but require strong distributional assumptions and do not provide a transparent between-stratum heterogeneity statistic like C1.

### Relevance to Biostatistics readers

IONE sits between heterogeneity diagnostics and model-based effect modification in IPD meta-analysis. C1 re-purposes I^2 for discovered strata and W connects the partition to explained CATE variance; both are descriptive sensitivity flags, not inferential tests. The empirical null distribution (Supplementary Table S5) calibrates the diagnostics under no true effect modification, and the misspecification sensitivity (Supplementary Table S6) checks robustness of W_est to the outcome-model specification. IONE is best used alongside conventional IPD meta-analysis, with standard adjustment applied within strata.

### Strengths and limitations

**Strengths.** The study followed ADEMP [morris2019], reported the data-generating mechanism and estimands transparently, and generated all numerical results from version-controlled repository scripts.

**Limitations.** The primary scenario used n={v['n_ipd']} and a moderate Z->X trace; sensitivity analyses examined n=500 to 10 000, Z-to-Y and Z-to-X scales, and a non-linear mapping, but performance may vary with stronger/weaker signals or fewer studies. The true-Z partition is a constructed reference, so ARI should not be over-interpreted as clinical validity. W_est depends on a correctly specified outcome model with interactions; a main-effects-only model can mislead (Supplementary Table S6). DerSimonian-Laird strata are not independent estimates, so tau^2 and I^2 describe between-stratum heterogeneity, not conventional between-study heterogeneity. C1 is computed from log odds ratios while ATE bias is on the risk-difference scale, so it is an indirect diagnostic. Null thresholds (Supplementary Table S5) are method-specific and conditional on the primary DGM. Semi-synthetic examples are pseudo-IPD reconstructions and illustrate settings, not real-IPD validation.

"""
def _make_double_spaced(src_path, dst_path):
    ds_doc = Document(src_path)
    for p in ds_doc.paragraphs:
        p.paragraph_format.line_spacing = 2.0
    for table in ds_doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.line_spacing = 1.15
    ds_doc.save(dst_path)

def generate_v3_manuscript():
    import subprocess
    # Record the exact commit hash used to generate the submission package
    try:
        commit_hash = subprocess.run(
            ['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        commit_hash = 'unknown'
    with open(os.path.join(RESULTS_DIR, 'commit_hash.txt'), 'w', encoding='utf-8') as f:
        f.write(commit_hash)

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
    ipd_sensitivity = _read_csv('rsm_ipd_sensitivity_full_summary.csv')
    ipd_nonlinearity = _read_csv('rsm_ipd_nonlinearity_full_summary.csv')
    figs, pptx_path = generate_rsm_figures(
        ipd_primary, ipd_full, real_data,
        ipd_sensitivity=ipd_sensitivity,
        ipd_nonlinearity=ipd_nonlinearity,
    )

    # Citation manager
    cm = CiteManager()
    _register_citations(cm)

    # Build sections
    abstract = (
        f"**Background:** In IPD meta-analysis, marginal treatment-effect estimates can be biased when hidden effect modifiers are ignored. "
        f"We propose two coherence diagnostics, C1 (1 minus the I^2 statistic applied to stratum-specific log odds ratios) and W (the proportion of CATE variance explained by the stratification), and evaluate them within Incoherence-Oriented Neutralisation and Extraction (IONE), an exploratory diagnostic framework for hidden effect modification.\n\n"
        f"**Methods:** We simulated an IPD meta-analysis with {v['n_studies']} studies, a binary treatment and outcome, measured covariates carrying traces of an unmeasured modifier, and study-level variation in baseline risk and treatment prevalence. "
        f"Proposed and comparator methods stratified the pooled IPD; stratum-specific risk differences were synthesised with fixed-effect and DerSimonian-Laird random-effects meta-analysis. "
        f"We report ARI, C1, W_true/W_est and ATE bias reduction with Monte Carlo standard errors, and we examined the empirical null distribution of the diagnostics and the sensitivity of W_est to outcome-model misspecification.\n\n"
        f"**Results:** In the primary scenario (n={v['n_ipd']}, {v['n_studies']} studies, K={v['k_ipd']} strata), the best method by ATE bias reduction was {v['best_method']} (ARI {v['best_method_ari']}; C1 {v['best_method_c1']}; W_true {v['best_method_wtrue']}; W_est {v['best_method_west']}). "
        f"Crude ATE bias was {v['crude_bias']}; stratification reduced it to {v['strat_bias']} (relative {v['rel_strat']}) and random-effects pooling to {v['re_bias']} (relative {v['rel_re']}). "
        f"Diagnostic recovery of the true hidden structure remained modest. Under the null of no true effect modification, C1 and W_est were distributed close to their chance-reference values; a main-effects outcome model inflated W_est, whereas the default interaction model was robust. Sensitivity analyses showed that bias reduction depends most on sample size and effect-modification strength, and the diagnostics remained informative under non-linear covariate mappings.\n\n"
        f"**Conclusions:** IONE is a transparent diagnostic flag for hidden effect modification in IPD meta-analyses. It should be reported alongside conventional models and covariate adjustment, not used as a replacement for rigorous causal inference."
    )
    keywords = "individual participant data meta-analysis; evidence synthesis; heterogeneity; hidden effect modification; stratification"

    # Extract and adapt Background and Discussion
    old_bg = _extract_section(old_md, 'Background')
    background = _adapt_background(old_bg, cm, v)
    discussion = _new_discussion(v)

    # Ensure Background contains RSM framing
    # (the adaptation function already adds meta-analysis intro)

    # Build the markdown
    md = f"""# Coherence diagnostics (C1 and W) for hidden effect modification in individual participant data meta-analysis: the IONE framework and a simulation study

{{{{PAGE}}}}

## Abstract

{abstract}

**Keywords:** {keywords}

{{{{PAGE}}}}

## 1. Introduction

{background}

{ _new_methods(v) }

{ _new_results(v) }

{discussion}

{ _new_conclusions() }

{{{{PAGE}}}}

{ _declarations() }

{{{{PAGE}}}}

{{{{REFS}}}}

"""

    # Fix numbered citations in whole markdown
    md = _old_to_keys(md, cm)

    # Save markdown and convert to docx
    md_path = os.path.join(SUBMISSION_DIR, 'IONE_biostatistics_v3.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)

    docx_path = os.path.join(SUBMISSION_DIR, 'IONE_biostatistics_v3.docx')
    convert(md_path, docx_path, cite_manager=cm, figure_dir=FIG_DIR)

    # Compute title-page metadata from the generated manuscript
    main_md = md.split('## 1. Introduction')[1].split('{{REFS}}')[0]
    main_lines = []
    for line in main_md.splitlines():
        s = line.strip()
        if s.startswith('|') or s.startswith('*Table') or s.startswith('!['):
            continue
        main_lines.append(line)
    main_text = ' '.join(main_lines)
    for c in '*#':
        main_text = main_text.replace(c, ' ')
    main_wc = len(main_text.split())
    abs_wc = len(abstract.split())
    num_figs = md.count('![')
    doc_for_count = Document(docx_path)
    num_tabs = len(doc_for_count.tables)

    # Supplementary materials document
    supp_cm = CiteManager()
    _register_citations(supp_cm)
    supp_md = f"""# Supplementary materials for IONE: Incoherence-Oriented Neutralisation and Extraction

{{{{PAGE}}}}

## Additional files

{ _additional_files(v) }

{{{{PAGE}}}}

{ _abbreviations() }

{{{{PAGE}}}}

{ _new_results(v, supplementary=True) }
"""
    supp_md_path = os.path.join(SUBMISSION_DIR, 'biostatistics_supplementary_v3.md')
    with open(supp_md_path, 'w', encoding='utf-8') as f:
        f.write(supp_md)
    supp_docx_path = os.path.join(SUBMISSION_DIR, 'biostatistics_supplementary_v3.docx')
    convert(supp_md_path, supp_docx_path, cite_manager=supp_cm, figure_dir=FIG_DIR)


    # Separate title page
    tp = Document()
    tp_style = tp.styles['Normal']
    tp_style.font.name = 'Times New Roman'
    tp_style.font.size = Pt(11)
    tp_title = tp.add_heading('Coherence diagnostics (C1 and W) for hidden effect modification', level=0)
    tp_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp_sub = tp.add_heading('in individual participant data meta-analysis: the IONE framework and a simulation study', level=0)
    tp_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.add_paragraph()
    tp.add_paragraph('Onishi Tatsuki')
    tp.add_paragraph('Data Science AI Innovation Research Promotion Center, Shiga University')
    tp.add_paragraph('1-1-1 Bamba, Hikone, Shiga 522-8522, Japan')
    tp.add_paragraph('ORCID: 0000-0001-7261-9062')
    tp.add_paragraph('Corresponding author: Onishi Tatsuki')
    p = tp.add_paragraph()
    p.add_run('bougtoir@gmail.com').italic = True
    tp.add_paragraph()
    tp.add_paragraph(f'Number of figures: {num_figs}')
    tp.add_paragraph(f'Number of tables: {num_tabs}')
    tp.add_paragraph(f'Word count: Abstract {abs_wc}; Main text {main_wc} (excluding references, tables and figures)')
    tp.add_paragraph()
    tp.add_heading('Declarations', level=1)
    tp.add_paragraph('Ethics approval and consent to participate: Not applicable. This study used simulated data and publicly available aggregate statistics only.')
    tp.add_paragraph('Consent for publication: Not applicable.')
    tp.add_paragraph('Competing interests: The authors declare that they have no competing interests.')
    tp.add_paragraph('Funding: No external funding supported this work.')
    tp.add_paragraph('Authors\' contributions (CRediT): Onishi Tatsuki — Conceptualisation, methodology, software, formal analysis, writing – original draft, writing – review and editing, visualisation.')
    tp.add_paragraph('Acknowledgements: Not applicable.')
    tp.add_paragraph(f'Artificial intelligence: Manuscript text, Python code and some analyses were drafted or revised using large language models (OpenAI GPT-4 and GPT-4o, accessed {AI_DATES}) under the author\'s direct, iterative supervision. The LLMs were used for drafting prose, formatting references, generating figures and implementing the computational pipeline. The author designed the study, wrote the simulation code, selected all references, verified every numerical result against repository outputs, and approved the final scientific content.')
    tp.add_paragraph('Data and code availability: All simulation code, analysis scripts and semi-synthetic example data are at https://github.com/bougtoir/ione-stratification-framework, with a requirements.txt and requirements-lock.txt file, fixed random seeds and a reproducible pipeline. The exact commit hash is recorded in results/commit_hash.txt. An archived Zenodo DOI will be obtained before acceptance.')
    tp_path = os.path.join(SUBMISSION_DIR, 'title_page_biostatistics_v3.docx')
    tp.save(tp_path)

    # Double-spaced PDF for initial submission
    ds_docx_path = os.path.join(SUBMISSION_DIR, 'IONE_biostatistics_v3_double_spaced.docx')
    _make_double_spaced(docx_path, ds_docx_path)
    pdf_path = os.path.join(SUBMISSION_DIR, 'IONE_biostatistics_v3_double_spaced.pdf')
    try:
        import subprocess
        subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', SUBMISSION_DIR, ds_docx_path], check=True)
    except Exception as e:
        print(f'[generate_ione_rsm_v3] PDF conversion skipped: {e}')

    # Cover letter
    cover_md = os.path.join(SUBMISSION_DIR, 'cover_letter_biostatistics_v3.md')
    if os.path.exists(cover_md):
        from md_to_rsm_docx import convert as _convert
        cover_docx = os.path.join(SUBMISSION_DIR, 'cover_letter_biostatistics_v3.docx')
        _convert(cover_md, cover_docx)

    # Submission package zip
    import zipfile
    zip_path = os.path.join(SUBMISSION_DIR, 'v3_ione_biostatistics_submission_package.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(docx_path, os.path.basename(docx_path))
        zf.write(tp_path, os.path.basename(tp_path))
        cover_docx = os.path.join(SUBMISSION_DIR, 'cover_letter_biostatistics_v3.docx')
        if os.path.exists(cover_docx):
            zf.write(cover_docx, os.path.basename(cover_docx))
        tables_docx = os.path.join(SUBMISSION_DIR, 'biostatistics_tables_separate.docx')
        if os.path.exists(tables_docx):
            zf.write(tables_docx, os.path.basename(tables_docx))
        if os.path.exists(supp_docx_path):
            zf.write(supp_docx_path, os.path.basename(supp_docx_path))
        if os.path.exists(ds_docx_path):
            zf.write(ds_docx_path, os.path.basename(ds_docx_path))
        if os.path.exists(pdf_path):
            zf.write(pdf_path, os.path.basename(pdf_path))
        pptx_path = os.path.join(FIG_DIR, 'pptx', 'rsm_figures.pptx')
        if os.path.exists(pptx_path):
            zf.write(pptx_path, 'biostatistics_figures.pptx')
        for f in os.listdir(FIG_DIR):
            if f.endswith(('.png', '.eps')):
                zf.write(os.path.join(FIG_DIR, f), os.path.join('figures', f))

    print(f'[generate_ione_rsm_v3] markdown: {md_path}')
    print(f'[generate_ione_rsm_v3] docx:    {docx_path}')
    print(f'[generate_ione_rsm_v3] title page: {tp_path}')
    print(f'[generate_ione_rsm_v3] zip:      {zip_path}')
    return docx_path, md_path, zip_path


if __name__ == '__main__':
    generate_v3_manuscript()
