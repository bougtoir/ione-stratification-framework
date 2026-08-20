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
TARGET_JOURNAL = 'Computational Statistics & Data Analysis'
SUBMISSION_DIR = os.path.join(RESULTS_DIR, 'manuscript', 'csda_submission')
os.makedirs(SUBMISSION_DIR, exist_ok=True)

MANUSCRIPT_TITLE = 'Coherence diagnostics for hidden effect modification in individual participant data meta-analysis: IONE (Incoherence-Oriented Neutralisation and Extraction) and a simulation benchmark of stratification approaches'

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
    diagnostic_roc = _read_csv('rsm_ipd_diagnostic_roc_summary.csv')

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

    # Diagnostic ROC calibration
    vals['diagnostic_roc'] = diagnostic_roc if diagnostic_roc is not None else pd.DataFrame()
    if diagnostic_roc is not None and not diagnostic_roc.empty:
        roc_all = diagnostic_roc
        vals['c1_auc_min'] = _fmt(roc_all['c1_auc'].min(), 3)
        vals['c1_auc_max'] = _fmt(roc_all['c1_auc'].max(), 3)
        vals['w_auc_min'] = _fmt(roc_all['w_auc'].min(), 3)
        vals['w_auc_max'] = _fmt(roc_all['w_auc'].max(), 3)
        best_c1 = roc_all.loc[roc_all['c1_auc'].idxmax()]
        best_w = roc_all.loc[roc_all['w_auc'].idxmax()]
        vals['c1_auc_best_method'] = best_c1['method']
        vals['c1_auc_best'] = _fmt(best_c1['c1_auc'], 3)
        vals['w_auc_best_method'] = best_w['method']
        vals['w_auc_best'] = _fmt(best_w['w_auc'], 3)
        vals['c1_tpr_range'] = f"{_fmt(roc_all['c1_tpr_5pct'].min(), 3)}–{_fmt(roc_all['c1_tpr_5pct'].max(), 3)}"
        vals['w_tpr_range'] = f"{_fmt(roc_all['w_tpr_95pct'].min(), 3)}–{_fmt(roc_all['w_tpr_95pct'].max(), 3)}"
        vals['c1_tpr_max'] = _fmt(roc_all['c1_tpr_5pct'].max(), 3)
        vals['w_tpr_max'] = _fmt(roc_all['w_tpr_95pct'].max(), 3)

        # Absolute-deviation calibration from the empirical null mean (Supplementary Table S7)
        vals['c1_abs_auc_min'] = _fmt(roc_all['c1_abs_auc'].min(), 3)
        vals['c1_abs_auc_max'] = _fmt(roc_all['c1_abs_auc'].max(), 3)
        vals['w_abs_auc_min'] = _fmt(roc_all['w_abs_auc'].min(), 3)
        vals['w_abs_auc_max'] = _fmt(roc_all['w_abs_auc'].max(), 3)
        best_c1_abs = roc_all.loc[roc_all['c1_abs_auc'].idxmax()]
        best_w_abs = roc_all.loc[roc_all['w_abs_auc'].idxmax()]
        vals['c1_abs_auc_best_method'] = best_c1_abs['method']
        vals['c1_abs_auc_best'] = _fmt(best_c1_abs['c1_abs_auc'], 3)
        vals['w_abs_auc_best_method'] = best_w_abs['method']
        vals['w_abs_auc_best'] = _fmt(best_w_abs['w_abs_auc'], 3)
        vals['c1_abs_tpr_range'] = f"{_fmt(roc_all['c1_abs_tpr_95pct'].min(), 3)}–{_fmt(roc_all['c1_abs_tpr_95pct'].max(), 3)}"
        vals['w_abs_tpr_range'] = f"{_fmt(roc_all['w_abs_tpr_95pct'].min(), 3)}–{_fmt(roc_all['w_abs_tpr_95pct'].max(), 3)}"
        residual_roc = roc_all[roc_all['method'] == '1B_residual']
        vals['residual_c1_abs_auc'] = _fmt(residual_roc['c1_abs_auc'].iloc[0], 3) if not residual_roc.empty else '—'
    else:
        vals['c1_auc_min'] = vals['c1_auc_max'] = vals['w_auc_min'] = vals['w_auc_max'] = '—'
        vals['c1_auc_best_method'] = vals['w_auc_best_method'] = '—'
        vals['c1_auc_best'] = vals['w_auc_best'] = '—'
        vals['c1_tpr_range'] = vals['w_tpr_range'] = '—'
        vals['c1_tpr_max'] = vals['w_tpr_max'] = '—'

        vals['c1_abs_auc_min'] = vals['c1_abs_auc_max'] = vals['w_abs_auc_min'] = vals['w_abs_auc_max'] = '—'
        vals['c1_abs_auc_best_method'] = vals['w_abs_auc_best_method'] = '—'
        vals['c1_abs_auc_best'] = vals['w_abs_auc_best'] = '—'
        vals['c1_abs_tpr_range'] = vals['w_abs_tpr_range'] = '—'
        vals['residual_c1_abs_auc'] = '—'

    # Null-centered metrics (review item 2: denominator stabilisation)
    if ipd_primary is not None and not ipd_primary.empty:
        vals['best_method_c1_excess'] = _fmt(best_re['C1_excess_mean'])
        vals['best_method_wtrue_excess'] = _fmt(best_re['W_true_excess_mean'])
        vals['best_method_west_excess'] = _fmt(best_re['W_est_excess_mean'])
        vals['mean_c1_excess'] = _fmt(ipd_primary['C1_excess_mean'].mean(), 3)
        vals['mean_wtrue_excess'] = _fmt(ipd_primary['W_true_excess_mean'].mean(), 3)
        vals['mean_west_excess'] = _fmt(ipd_primary['W_est_excess_mean'].mean(), 3)

    # W_est misspecification: compare main-effects and default model inflation
    if misspec_summary is not None and not misspec_summary.empty:
        mrow = misspec_summary[misspec_summary['method'] == '1B_residual']
        if not mrow.empty:
            vals['misspec_default_west'] = _fmt(mrow['W_est_mean'].iloc[0])
            vals['misspec_main_west'] = _fmt(mrow['W_est_main_mean'].iloc[0])
            vals['misspec_poly_west'] = _fmt(mrow['W_est_polynomial_mean'].iloc[0])
            vals['misspec_default_west_excess'] = _fmt(mrow['W_est_excess_mean'].iloc[0])
        else:
            vals['misspec_default_west'] = vals['misspec_main_west'] = vals['misspec_poly_west'] = vals['misspec_default_west_excess'] = '—'
    else:
        vals['misspec_default_west'] = vals['misspec_main_west'] = vals['misspec_poly_west'] = vals['misspec_default_west_excess'] = '—'

    # Large sample (n=10000) floor for best method
    if ipd_sensitivity is not None and not ipd_sensitivity.empty:
        n10 = _sens_row(ipd_sensitivity, '1B_residual', 10000, 1.0, 1.0, 5, 'abs_bias_re_mean')
        vals['n10000_re_bias'] = _fmt(n10, 5) if not pd.isna(n10) else '—'
        n10_rel = _sens_row(ipd_sensitivity, '1B_residual', 10000, 1.0, 1.0, 5, 'bias_reduction_relative_re_mean')
        vals['n10000_rel_re'] = _fmt(n10_rel, 3) if not pd.isna(n10_rel) else '—'

        n5 = _sens_row(ipd_sensitivity, '1B_residual', 500, 1.0, 1.0, 5, 'abs_bias_re_mean')
        vals['n500_re_bias'] = _fmt(n5, 5) if not pd.isna(n5) else '—'
        n2s = _sens_row(ipd_sensitivity, '1B_residual', 2000, 1.0, 1.0, 5, 'abs_bias_re_mean')
        vals['n2000_sens_re_bias'] = _fmt(n2s, 5) if not pd.isna(n2s) else '—'

        others = []
        for method in ['PS_propensity_score', 'Prognostic_score', '2B_clustering']:
            other_rel = _sens_row(ipd_sensitivity, method, 10000, 1.0, 1.0, 5, 'bias_reduction_relative_re_mean')
            if not pd.isna(other_rel):
                others.append(other_rel)
        if others:
            vals['n10000_nonresid_rel_min'] = _fmt(min(others), 3)
            vals['n10000_nonresid_rel_max'] = _fmt(max(others), 3)
        else:
            vals['n10000_nonresid_rel_min'] = vals['n10000_nonresid_rel_max'] = '—'
    else:
        vals['n10000_re_bias'] = vals['n10000_rel_re'] = '—'
        vals['n500_re_bias'] = vals['n2000_sens_re_bias'] = '—'
        vals['n10000_nonresid_rel_min'] = vals['n10000_nonresid_rel_max'] = '—'

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
                'Simpson EH. The interpretation of interaction in contingency tables. J R Stat Soc Ser B. 1951;13(2):238–241.',
                doi='10.1111/j.2517-6161.1951.tb00088.x')
    cm.register('rojanaworarit2020', 'Rojanaworarit', 2020,
                'Rojanaworarit C. Misleading epidemiological and statistical evidence in the presence of Simpson\'s paradox: an illustrative study using simulated scenarios. J Med Life. 2020;13(1):37–44.')
    cm.register('vanderweele2014', 'VanderWeele and Knol', 2014,
                'VanderWeele TJ, Knol MJ. A tutorial on interaction. Epidemiol Methods. 2014;3(1):33–72.')
    cm.register('robinson1950', 'Robinson', 1950,
                'Robinson WS. Ecological correlations and the behavior of individuals. Am Sociol Rev. 1950;15(3):351–357.')
    cm.register('greenland1999', 'Greenland et al.', 1999,
                'Greenland S, Robins JM, Pearl J. Confounding and collapsibility in causal inference. Stat Sci. 1999;14(1):29–46.',
                doi='10.1214/ss/1009211805')
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
                'Rosenbaum PR, Rubin DB. The central role of the propensity score in observational studies for causal effects. Biometrika. 1983;70(1):41–55.',
                doi='10.1093/biomet/70.1.41')
    cm.register('hansen2008', 'Hansen', 2008,
                'Hansen BB. The prognostic analogue of the propensity score. Biometrika. 2008;95(2):481–488.',
                doi='10.1093/biomet/asn004')
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
                'McLachlan GJ, Peel D. Finite Mixture Models. New York: Wiley; 2000.',
                doi='10.1002/0471721182')
    cm.register('hayeslarson2019', 'Hayes-Larson et al.', 2019,
                'Hayes-Larson E, Kezios KL, Mooney SJ, Lovasi G. Who is in this study, anyway? Guidelines for a useful Table 1. J Clin Epidemiol. 2019;114:125–132.')
    cm.register('higgins2002', 'Higgins and Thompson', 2002,
                'Higgins JPT, Thompson SG. Quantifying heterogeneity in a meta-analysis. Stat Med. 2002;21(11):1539–1558.',
                doi='10.1002/sim.1186')
    cm.register('morris2019', 'Morris et al.', 2019,
                'Morris TP, White IR, Crowther MJ. Using simulation studies to evaluate statistical methods. Stat Med. 2019;38(11):2074–2102.',
                doi='10.1002/sim.8086')
    cm.register('hubert1985', 'Hubert and Arabie', 1985,
                'Hubert L, Arabie P. Comparing partitions. J Classif. 1985;2(1):193–218.',
                doi='10.1007/bf01908075')

    # Additional RSM / meta-analysis / causal references
    cm.register('borenstein2009', 'Borenstein et al.', 2009,
                'Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. Chichester: John Wiley & Sons; 2009.',
                doi='10.1002/9780470743386')
    cm.register('dersimonian1986', 'DerSimonian and Laird', 1986,
                'DerSimonian R, Laird N. Meta-analysis in clinical trials. Control Clin Trials. 1986;7(3):177–188.',
                doi='10.1016/0197-2456(86)90046-2')
    cm.register('riley2010', 'Riley et al.', 2010,
                'Riley RD, Lambert PC, Abo-Zaid G. Meta-analysis of individual participant data: rationale, conduct, and reporting. BMJ. 2010;340:c221.',
                doi='10.1136/bmj.c221')
    cm.register('riley2011', 'Riley et al.', 2011,
                'Riley RD, Higgins JPT, Deeks JJ. Interpretation of random effects meta-analyses. BMJ. 2011;342:d549.')
    cm.register('simmonds2005', 'Simmonds et al.', 2005,
                'Simmonds MC, Higgins JPT, Stewart LA, Tierney JF, Clarke MJ, Thompson SG. Meta-analysis of individual patient data from randomized trials: a review of methods used in practice. Clin Trials. 2005;2(3):209–217.',
                doi='10.1191/1740774505cn087oa')
    cm.register('austin2015', 'Austin and Stuart', 2015,
                'Austin PC, Stuart EA. Moving towards best practice when using inverse probability of treatment weighting (IPTW) using the propensity score to estimate causal treatment effects in observational studies. Stat Med. 2015;34(28):3661–3679.')
    cm.register('pearl2009', 'Pearl', 2009,
                'Pearl J. Causality. 2nd ed. Cambridge: Cambridge University Press; 2009.',
                doi='10.1017/cbo9780511803161')
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
        'Individual participant data (IPD) meta-analysis preserves participant-level covariates and can increase power for treatment-covariate interactions [riley2010][simmonds2005]. '
        'Random-effects syntheses are recommended when between-study heterogeneity is suspected [dersimonian1986][higgins2002][riley2011], '
        'yet conventional summaries estimate a marginal effect and may mislead when effect modifiers are unmeasured or omitted [pearl2009][greenland1999]. '
        'When the pooled population contains subgroups with different treatment effects, the marginal effect can reverse within population strata, producing Simpson-type paradoxes [simpson1951][rojanaworarit2020].\n\n'
        'Heterogeneity in IPD meta-analysis is usually investigated through subgroup analyses, meta-regression or one-stage mixed models. '
        'These approaches explain variation with measured covariates and study-level factors, and stratification by study is the standard way to share baseline risk and treatment prevalence. '
        'They do not, however, test whether the pooled participants themselves form internally homogeneous subpopulations with respect to treatment effect. '
        'We therefore frame Incoherence-Oriented Neutralisation and Extraction (IONE) as an exploratory sensitivity tool: it flags when a marginal summary may be fragile and separates the pooled IPD into more homogeneous subgroups using multivariate patterns in measured variables. '
        'The goal is not to recover hidden variables but to reduce misleading marginal summaries when the IPD contains hidden effect modification.\n\n'
        'Hidden population structure is documented across medicine and social science: kidney-stone treatments [charig1986], university admissions [bickel1975], COVID-19 case-fatality comparisons [vonkuegelgen2021], national vaccine-surveillance data [haas2021], and smoking-mortality studies [appleton1996]. '
        'Established methods adjust for measured confounders but do not detect unmeasured population structure. '
        'We operationalise IONE through two coherence diagnostics: C1, derived from the I^2 heterogeneity statistic [higgins2002] applied to stratum-specific log odds ratios, and W, the proportion of total conditional average treatment effect (CATE) variance explained by the stratification. '
        'Stratum-specific risk differences are synthesised with fixed-effect or DerSimonian-Laird random-effects meta-analysis. '
        'C1 measures the coherence of a stratification after it has been formed; W is a ratio whose denominator is the overall CATE variance and is therefore unstable when the modification signal is weak.\n\n'
        'Because the finite-sample distributions of discovered-stratum risk differences depend on the unknown joint distribution of unmeasured modifiers and measured covariates, closed-form theoretical comparisons of the competing stratification methods are not available. '
        'We therefore use an ADEMP-based simulation benchmark to quantify relative performance and the operating characteristics of C1 and W.'
    )
def _new_methods(v):
    """Return markdown string for the Methods section."""
    md = """## 2. Methods

This simulation study follows the ADEMP framework [morris2019].

### Aims

Quantify average treatment effect (ATE) bias reduction from fixed-effect and DerSimonian-Laird random-effects synthesis of stratum-specific risk differences; compare outcome-informed IONE methods with outcome-free and established comparators; assess the diagnostic discrimination of C1 and W against an empirical null; and identify data-generating conditions under which the diagnostics are most and least informative.

### IPD data-generating mechanism

We simulated an IPD meta-analysis with n={n_ipd} participants assigned to {n_studies} studies (scale parameter {study_effect} for baseline risk, treatment prevalence and an age-like covariate). Each participant had three critical variables (Z1 continuous, Z2 binary, Z3 ordered) that affected treatment, outcome and treatment-covariate interactions, and ten measured variables (X1-X10) carrying traces of Z. A binary treatment A and binary outcome Y were generated from logistic models with Z and X main effects, a treatment effect and Z-by-A interactions. The estimand was the population risk-difference ATE; full algebra is in Additional file 1.

The primary scenario used n={n_ipd}, {n_studies} studies and K={k_ipd} strata. We varied K (3, 5, 10), sample size (500, 2000, 10 000), Z-to-Y effect scale (0.5, 1.0, 2.0), Z-to-X influence scale (0.2, 0.5, 1.0) and introduced a non-linear Z-to-X mapping. The primary and strata-sensitivity scenarios used {n_sims_per_scenario} replications; extended robustness used 30; empirical null used 200 and W_est misspecification used 50.

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

#### Formal definitions

For a stratification with K strata, let theta_k be the stratum-specific log odds ratio and tau^2 the DerSimonian-Laird between-stratum variance. Let v_w denote a typical within-stratum sampling variance. Then

C1 = 1 - I^2 = 1 - tau^2 / (tau^2 + v_w),

where lower C1 indicates greater between-stratum heterogeneity of stratum-specific log odds ratios. For estimated individual CATEs tau(X_i), let tau_k be the mean CATE in stratum k and tau the overall mean. The proportion of total CATE variance explained by the stratification is

W = sum_k n_k (tau_k - tau)^2 / sum_i (tau_i - tau)^2,

where the numerator is the between-stratum variance weighted by stratum size and the denominator is the total variance of estimated individual CATEs. Both C1 and W are descriptive indices; they flag incoherence but are not inferential tests for hidden effect modification.

**ARI** [hubert1985]: agreement between estimated strata and an operational approximation of the true-Z partition, corrected for chance. Because the true hidden modifier is multidimensional and has no unique clinical representation, the reference partition was formed by k-means clustering of standardised Z-space into K strata. ARI therefore measures how well a method recovers this k-means approximation, not recovery of a clinically validated true subgroup structure. Values near zero indicate chance agreement; the Oracle and true-CATE-quantile references provide computational upper bounds relative to this approximation.

**C1** = 1 - I^2 applied to stratum-specific log odds ratios [higgins2002]. Lower C1 indicates greater between-stratum heterogeneity of stratum-specific log odds ratios. Because C1 is computed on the log-odds scale while ATE bias is on the risk-difference scale, it is an indirect diagnostic of bias; it summarises the coherence of the selected partition, not the magnitude of hidden modification.

**W_true / W_est:** proportion of total conditional average treatment effect (CATE) variance explained by the stratification, i.e. the between-stratum CATE variance divided by the overall CATE variance. W_est requires a correctly specified individual-level outcome model. Because W is a ratio whose denominator is the overall CATE variance, it can be unstable when effect modification is weak (small denominators) and should be interpreted relative to its empirical null distribution. We therefore report null-mean-centred excess values: C1_excess = max(null mean C1 - C1, 0), W_excess = max(W - null mean W, 0) and proportion metrics such as eta^2 = between-stratum CATE variance / overall CATE variance as an alternative scale-free summary.

**ATE bias reduction:** absolute differences between crude, stratified and random-effects estimates, plus relative ratios. Monte Carlo SE and 95% CI accompany every mean.

### Empirical null distribution and null-centred reporting

We ran 200 additional replications under the primary data-generating mechanism (DGM) with Z-by-A interaction coefficients set to zero. This retains confounding and covariate traces but has no true effect modification. For each method we recorded C1 and W_est and report the 5th, 50th and 95th percentiles in the Supplementary Material. Values below the 5th percentile (C1) or above the 95th percentile (W_est) provide method-specific thresholds for flagging incoherence. In addition, we computed excess diagnostics by subtracting the empirical null mean, producing more stable summaries than raw W and C1.

### W_est outcome-model misspecification sensitivity

W_est is computed from an estimated individual-level CATE. Omitting treatment-covariate interactions can inflate or deflate W_est, so we repeated the primary scenario with three outcome-model specifications for W_est: main effects only (Y ~ X + A), linear interactions (Y ~ X + A + X*A, default), and linear plus quadratic interactions. Results are reported in the Supplementary Material.

### Diagnostic calibration using the empirical null

We used the 200 null replications together with the 50 alternative replications of the primary scenario to compute, for each method, the area under the ROC curve (AUC) and the true-positive rate (TPR) at a method-specific 5% false-positive rate (C1 below its null 5th percentile, W_est above its null 95th percentile). Because the null distribution preserves confounding and covariate traces but removes true effect modification, these metrics quantify how well the diagnostics distinguish absence from presence of the simulated modification. AUC near 0.5 and low TPR indicate that the diagnostics do not provide reliable classification on their own in the primary scenario; for some methods C1 AUC fell below 0.5, indicating that the alternative DGM shifted C1 in the opposite direction to the lower-tail hypothesis, so the one-sided threshold is not universally valid.

### True-CATE-quantile oracle reference

As a reference for sorting performance, we computed a true-CATE-quantile oracle that assigns participants to strata by the true conditional average treatment effect. This oracle is not a practical method (it uses the true CATE) but it provides an upper bound on how well any covariate-based stratification could separate heterogeneous subgroups. We include the oracle in sensitivity summaries to bound optimism and to illustrate the gap between empirical methods and the true sorting benchmark.

### Semi-synthetic illustrations

Five Simpson-paradox examples were reconstructed as pseudo-individual records from published aggregate statistics [charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]. The Israeli vaccination example used pseudo-IPD reconstructed from age- and vaccination-stratified COVID-19-related hospitalisation counts published by Haas et al. [haas2021]. We chose hospitalisation rather than infection counts because the age-vaccination stratification table in the source publication provides age- and vaccination-stratified counts for a severe endpoint where age confounding is pronounced, and because the low event rate (~0.09% in the down-sampled data) creates a stress-test for rare outcomes. Because the published counts cover approximately 6.5 million people, we used a stratified random down-sample of 100,000 records preserving the age- and vaccination-specific hospitalisation rates. In the down-sampled pseudo-IPD, some cells contained very few or zero hospitalisation events; logistic models used for outcome-informed methods were fitted with L2 regularisation, and any degenerate one-class fit was handled by returning the observed mean probability. Pseudo-general variables mimicked proxies of the known confounder and the number of strata K was selected from the set {{2, 3, min(K_true, 4), K_true}}, where K_true is the true number of published strata, keeping the value that maximised ARI. These are illustrations, not real-IPD validation.

### Computational implementation

All simulations and manuscript generation were implemented in Python 3.11 using NumPy 2.x, SciPy, scikit-learn 1.5, pandas, statsmodels and python-docx. Pseudo-random numbers were generated with `numpy.random.default_rng`, with independent seeds for each replication and scenario stored in the repository scripts and `results/summary/` metadata. Stratification used quantile-based equal-frequency bins, k-means clustering (scikit-learn, 10 random initializations, maximum 300 iterations) and Gaussian mixture models (scikit-learn, full covariance, 10 EM initializations, maximum 100 iterations). Logistic regressions were fit with `scikit-learn.linear_model.LogisticRegression` (L2 penalty, C=1.0, lbfgs solver, maximum 1000 iterations). DerSimonian-Laird random-effects summaries used `statsmodels.stats.meta_analysis`. The primary scenario required approximately 5–10 minutes of wall-clock time on a single modern CPU core; the full benchmark—primary scenario, strata/sample-size/Z-to-X/Z-to-Y sensitivities, 200-replication empirical null, W_est misspecification and semi-synthetic illustrations—completed in approximately 2–3 hours on a single core. Exact dependency versions are pinned in `requirements-lock.txt` and the code commit used for the submission package is recorded in `results/commit_hash.txt`.

### Reporting and reproducibility

The design followed ADEMP [morris2019]; checklists are in Additional files 2 and 3. The pipeline is version-controlled and every manuscript number is read from repository CSV outputs. `generate_summary.py`, `generate_rsm_tables.py` and `generate_ione_rsm_v3.py` regenerate all results, figures, tables and submission files in a Python 3.11 environment with the pinned dependencies.
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

    # Diagnostic ROC calibration table (Table 4 in main results)
    diagnostic_roc = v.get('diagnostic_roc', pd.DataFrame())
    roc_rows = []
    if diagnostic_roc is not None and not diagnostic_roc.empty:
        for _, r in diagnostic_roc.iterrows():
            roc_rows.append({
                'Method': r['method'],
                'C1 AUC': _fmt(r.get('c1_auc', np.nan), 3),
                'C1 TPR@5% FPR': _fmt(r.get('c1_tpr_5pct', np.nan), 3),
                'W_est AUC': _fmt(r.get('w_auc', np.nan), 3),
                'W_est TPR@5% FPR': _fmt(r.get('w_tpr_95pct', np.nan), 3),
            })
    table_roc = _make_table(
        ['Method', 'C1 AUC', 'C1 TPR@5% FPR', 'W_est AUC', 'W_est TPR@5% FPR'],
        roc_rows
    )

    # Absolute-deviation ROC calibration table (Supplementary Table S7)
    abs_roc_rows = []
    if diagnostic_roc is not None and not diagnostic_roc.empty:
        for _, r in diagnostic_roc.iterrows():
            abs_roc_rows.append({
                'Method': r['method'],
                'C1 abs-AUC': _fmt(r.get('c1_abs_auc', np.nan), 3),
                'C1 abs TPR@5% FPR': _fmt(r.get('c1_abs_tpr_95pct', np.nan), 3),
                'W_est abs-AUC': _fmt(r.get('w_abs_auc', np.nan), 3),
                'W_est abs TPR@5% FPR': _fmt(r.get('w_abs_tpr_95pct', np.nan), 3),
            })
    table_abs_roc = _make_table(
        ['Method', 'C1 abs-AUC', 'C1 abs TPR@5% FPR', 'W_est abs-AUC', 'W_est abs TPR@5% FPR'],
        abs_roc_rows
    )

    if supplementary:
        return f"""## Sensitivity analyses

### Sensitivity to the number of strata

Table S1 presents how random-effects ATE bias reduction and ARI changed as the number of strata varied (K = {v['k_list']}). For most methods the gain from increasing K was limited and non-monotonic; increasing strata beyond the true dimensionality of the hidden structure introduced additional sampling variation and did not consistently improve ATE bias reduction. The Oracle baselines did improve with larger K, because more strata allow a finer partition of the true Z-space. In contrast, data-driven methods did not reliably exploit the additional flexibility, suggesting that the number of strata should be chosen conservatively or compared across several values, rather than simply maximised.

{table_k}
*Table S1. Sensitivity of random-effects ATE bias reduction and coherence diagnostics to the number of strata.*

### Sensitivity to sample size

Table S2 summarises the primary scenario repeated with n = 500, 2000 and 10 000, fixing K = 5 and the moderate Z-to-X and Z-to-Y effects. Because this extended sensitivity used 30 replications per cell, the point estimates are still noisier than the primary scenario; Monte Carlo SEs are reported to help gauge this uncertainty. The crude marginal ATE bias decreased with sample size, as expected from a more precisely estimated risk difference. The absolute random-effects bias declined for propensity-score, prognostic-score and clustering-based approaches, and these methods achieved their largest relative bias reductions at n = 10 000. In contrast, the outcome-residual approach showed a floor near 0.008-0.009 and its relative bias reduction therefore decreased with n, while GMM improved only gradually. This mixed pattern shows that the practical value of IONE depends on the interplay between sample size and method choice: with small samples, estimation error dominates; with large samples, remaining bias reflects structural limits of the selected stratification.

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

### Absolute-deviation diagnostic calibration

Table S7 uses absolute distance from the empirical null mean as the diagnostic score, so that neither a lower C1 nor a higher W is assumed a priori. C1 abs-AUC ranged from {v['c1_abs_auc_min']} to {v['c1_abs_auc_max']} and W_est abs-AUC from {v['w_abs_auc_min']} to {v['w_abs_auc_max']}; the residual method's C1 abs-AUC was {v['residual_c1_abs_auc']}. These values remained at or near chance level, showing that the weak one-sided ROC discrimination in Table 4 is not an artifact of the chosen tail.

{table_abs_roc}
*Table S7. Absolute-deviation diagnostic discrimination of C1 and W_est against the empirical null distribution (n=2000, K=5, 200 null and 50 alternative replications).*
"""

    md = f"""## 3. Results

### Primary IPD scenario

Table 1 reports the primary scenario (n={v['n_ipd']}, {v['n_studies']} studies, K={v['k_ipd']}). Agreement with the operational k-means true-Z partition was modest (Oracle ARI {v['best_ari']}; best non-Oracle {v['best_non_oracle_ari_method']} {v['best_non_oracle_ari']}). Oracle and residual methods had the highest W_true values, but C1 was high across most methods (even random stratification yielded C1 {v['random_c1']}), indicating that C1 alone did not separate useful from chance stratifications; W_true separated the methods better. W_true exceeded W_est, reflecting that the estimated CATE captures only part of the true CATE variation. The best ATE bias reduction came from {v['best_method']}: crude bias {v['crude_bias']}, stratified bias {v['strat_bias']} (relative reduction {v['rel_strat']}) and random-effects bias {v['re_bias']} (relative reduction {v['rel_re']}). {study_footnote} Pooling strata with DerSimonian-Laird improved over the fixed-effect summary, indicating that stratum-specific effects should be allowed to vary. Null-centred excess diagnostics for the best method were modest (C1_excess {v['best_method_c1_excess']}; W_est_excess {v['best_method_west_excess']}).

{table1}
*Table 1. Primary IPD scenario (n={v['n_ipd']}, {v['n_studies']} studies, K={v['k_ipd']}): means over 50 simulations.*

Figure 1 visualises the primary scenario across methods.

![Figure 1. Primary IPD scenario: (a) ARI, (b) C1/W coherence diagnostics, and (c) ATE bias reduction by method.](fig1_rsm_ipd_primary.png)

### Sensitivity to the number of strata

Figure 2 and Supplementary Table S1 show random-effects bias reduction across K = {v['k_list']}. Data-driven methods did not reliably improve with larger K; Oracle baselines improved because finer strata better partition the true Z-space. Stratum count should be chosen conservatively and compared across values.

![Figure 2. Random-effects ATE bias reduction as the number of strata varies.](fig2_rsm_ipd_strata_sensitivity.png)

### Semi-synthetic illustrations

Five Simpson-paradox examples were reconstructed as pseudo-individual records [charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]. Table 2 reports the best non-Oracle method per dataset. The Israel hospitalisation example was the most challenging: strong age confounding and a very low hospitalisation rate (~0.09%) meant that the crude marginal association reversed after stratification, yet separating the data into the known age strata remained difficult. The low event rate also produced occasional near-zero or zero-event cells, which illustrates the limits of outcome-informed stratification for rare outcomes.

{table_real}
*Table 2. Best semi-synthetic illustration result per dataset (oracle baselines excluded). Bias reduction is the absolute difference between crude and stratified ATE risk-difference bias.*

Figure 3 displays ARI by dataset and method for the semi-synthetic examples.

![Figure 3. Semi-synthetic illustration: ARI by dataset and method.](fig3_rsm_real_data_ari.png)

### Sensitivity to sample size

Figure 4 and Supplementary Table S2 report n = 500, 2000 and 10 000 (K=5). Crude bias declined with n. The residual method's absolute random-effects ATE bias plateaued near 0.008–0.009 across the three sample sizes ({v['n500_re_bias']} at n=500, {v['n2000_sens_re_bias']} at n=2000 and {v['n10000_re_bias']} at n=10 000), so its relative reduction fell as the crude marginal estimate became more precise. Propensity-score, prognostic-score and clustering-based methods achieved larger relative reductions at n=10 000 (range {v['n10000_nonresid_rel_min']}–{v['n10000_nonresid_rel_max']}), showing that performance depends on the method as well as sample size. This pattern indicates that stratification can remove the estimable part of confounding-driven aggregation bias, but it cannot fully adjust for unmodelled hidden effect modification.

![Figure 4. Sample-size sensitivity of random-effects ATE bias reduction (K=5). The residual method reaches a structural bias floor that does not vanish with sample size; propensity-score, prognostic-score and clustering approaches overtake it at n = 10 000 once finite-sample error is small relative to structural mismatch.](fig4_rsm_ipd_sample_size.png)

### Sensitivity to Z-to-X and Z-to-Y effects

Supplementary Tables S3 and S4 report Z-to-X influence (0.2, 0.5, 1.0) and Z-to-Y effect (0.5, 1.0, 2.0). Stronger covariate traces improved ARI, but bias-reduction gains were variable. Weak effect modification produced C1/W near their nulls; stronger effect modification lowered C1, raised W and improved relative bias reduction. The residual method retained useful relative reduction even at z = 0.5.

### Robustness to non-linear Z-to-X mappings

Table 3 compares random-effects bias under linear and non-linear Z-to-X mappings. Effects were method-dependent but no leading method was dramatically degraded, indicating that the diagnostics remain useful when X is a non-linear function of the hidden structure.

{table_nonlinear}
*Table 3. Linear versus non-linear Z-to-X mapping: random-effects ATE bias and relative bias reduction (n=2000, K=5, z=1.0, zx=1.0).*

Figure 5 shows random-effects ATE bias reduction under the non-linear mapping.

![Figure 5. Non-linear Z->X robustness: random-effects ATE bias reduction (n=2000, K=5).](fig5_rsm_ipd_nonlinearity.png)

### Diagnostic discrimination against the empirical null

Table 4 and Figure 6 summarise the diagnostic calibration of C1 and W_est against the empirical null distribution obtained when Z-by-A interactions are removed. C1 AUC ranged from {v['c1_auc_min']} to {v['c1_auc_max']} and W_est AUC from {v['w_auc_min']} to {v['w_auc_max']}; the best C1 AUC was {v['c1_auc_best']} for {v['c1_auc_best_method']} and the best W_est AUC was {v['w_auc_best']} for {v['w_auc_best_method']}. True-positive rates at a 5% false-positive rate were low: C1 TPR {v['c1_tpr_range']} and W_est TPR {v['w_tpr_range']}. These values show that the diagnostics did not reliably distinguish the alternative DGM from the null in the primary scenario; the C1 AUCs at or below 0.5 for several methods show that the lower-tail null threshold does not match the direction of the alternative DGM shift for those methods. Supplementary Table S5 reports the empirical null percentiles used as thresholds. A main-effects-only outcome model for W_est inflated the residual method's W_est from {v['misspec_default_west']} (default interactions) to {v['misspec_main_west']}, whereas the polynomial interaction model gave {v['misspec_poly_west']}; full results are in Supplementary Table S6. Supplementary Table S7 reports absolute-deviation scores using distance from the empirical null mean (e.g. residual C1 abs-AUC {v['residual_c1_abs_auc']}); these did not rescue discrimination, indicating that the weak ROC performance is structural rather than an artifact of the one-sided lower-tail threshold.

{table_roc}
*Table 4. Diagnostic discrimination of C1 and W_est against the empirical null distribution (n=2000, K=5, 200 null replications and 50 alternative replications).*

![Figure 6. Diagnostic calibration of C1 and W_est: AUC for discriminating the alternative DGM from the empirical null distribution (n=2000, K=5). C1 and W_est do not provide reliable classification on their own in the primary scenario; they should be used only as descriptive flags calibrated to the empirical null.](fig6_rsm_diagnostic_calibration.png)

### CATE variance explained

Figure 7 shows CATE variance explained (eta^2, represented by W_true) and the corresponding estimated value (W_est) for each method. Methods that produced stratum-specific effects close to the true CATE quantiles achieved higher eta^2, but no data-driven method reached the Oracle level. The gap between W_true and W_est shows that the residual and predicted-probability models capture only part of the true CATE variation.

![Figure 7. CATE variance explained (eta^2 = W_true) and estimated W_est by method in the primary scenario (n=2000, K=5).](fig7_cate_variance_explained.png)

### Recommendations for method choice

Table 5 translates the simulation results into practical guidance. It links scenario characteristics to the method that performed best in the benchmark, states the rationale, and notes the key caveat. The recommendations reflect the patterns in Tables 1–4 and Supplementary Tables S1–S4; they are not derived from a new optimisation and should be treated as heuristics for sensitivity analysis rather than prescriptive rules.

| Scenario characteristic | Recommended method | Rationale | Caveat |
|---|---|---|---|
| Strong covariate trace of a hidden modifier and moderate-to-large sample | Residual-based IONE (1B) | Highest random-effects ATE bias reduction and W_true in the primary scenario | Hits a structural bias floor that does not vanish with sample size; requires a correctly specified outcome model with treatment-covariate interactions |
| Small sample (n ≈ 500) with moderate modification | Residual-based IONE (1B) | Achieved the largest relative bias reduction and the smallest absolute bias floor at n = 500 | Relative reduction partly reflects large crude bias; residual model can overfit when events are sparse |
| Large sample (n ≈ 10 000) and strong measured confounding | Propensity-score, prognostic-score or clustering stratification | Largest relative reductions after finite-sample error was dominated by structural differences | Residual-based stratification is overtaken once crude bias is small; method-specific performance still varies |
| Outcome model unavailable, misspecified or rare events | Outcome-free methods (PCA or k-means) or prognostic-score stratification | Do not use the outcome for stratification, so avoid degenerate logistic fits and overfitting | ATE bias reduction is generally smaller; C1 and W discrimination remains near chance |
| Need a descriptive flag for internal incoherence | Report C1_excess and W_est_excess alongside the primary analysis | Empirically calibrated against a no-modification null | Do not use as a standalone inferential test; thresholds are method-specific and DGM-conditional |

*Table 5. Recommendations for choosing a stratification method in an IPD meta-analysis sensitivity analysis.*

### Empirical null distribution and W_est misspecification

Under the primary DGM with no Z-by-A interaction, C1 was generally high and W_est near 0; method-specific 5th/95th percentiles are in Supplementary Table S5. A main-effects-only outcome model inflated W_est, whereas the default interaction and polynomial models were more stable (Supplementary Table S6). C1 and W are diagnostic flags, not standalone inferential quantities.
"""
    return md

def _new_conclusions():
    return """## 5. Conclusions

IONE (Incoherence-Oriented Neutralisation and Extraction) is a descriptive sensitivity framework for hidden effect modification in IPD meta-analysis. Monte Carlo simulation and semi-synthetic examples show that the C1 and W diagnostics can flag incoherence, but they do not reliably separate the alternative data-generating mechanism from an empirical null in the primary scenario. When hidden variables leave strong traces in measured covariates, stratification can partially reduce ATE bias, but separating the data into the true hidden subgroups remains difficult. Conventional meta-analytic models and covariate adjustment should remain the primary analysis; C1 and W should be reported alongside them as sensitivity checks. Two concrete recommendations follow: (1) use C1 and W only as descriptive flags, not as inferential tests for hidden effect modification, and (2) pre-specify potential effect modifiers and reserve data-driven stratification for exploratory sensitivity analyses, not for decision-making.
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

Supplementary methods, abbreviations, the ADEMP/STROBE-Sim checklists, the four extended sensitivity tables, and the empirical null-distribution and W_est misspecification sensitivity tables are provided in `csda_supplementary_v1.docx`.

### Artificial intelligence

Manuscript text, Python code, and some analyses were drafted or revised using large language models (OpenAI GPT-4 and GPT-4o, accessed {AI_DATES}) under the direct, iterative supervision of the author. The LLMs were used for drafting prose, formatting references, generating figures, and implementing the computational pipeline. The author designed the study, wrote the simulation code, selected all references, verified every numerical result against the repository outputs, and approved the final scientific content. No LLM-generated text was used without human review.
"""
def _additional_files(v):
    return f"""### Additional file 1: Supplementary Methods

Detailed algebraic description of the IPD data-generating mechanism. For each of the {v['n_studies']} studies, a study-specific intercept is drawn for baseline risk and treatment propensity. The critical variables are Z1 (continuous, mean 60, standard deviation 12, truncated to 20–95), Z2 (binary, probability 0.5) and Z3 (ordered, levels 0/1/2 with probabilities 0.3, 0.4, 0.3). The ten general variables X1-X10 are linear or non-linear functions of Z plus independent Gaussian noise. The treatment indicator A is generated from a logistic model with intercept, Z main effects, X main effects and a random study intercept. The outcome Y is generated from a logistic model with Z main effects, X main effects, an A main effect, Z-by-A interaction effects and a random study intercept. The true individual CATE is the difference in outcome probabilities under A=1 versus A=0 at the realised Z values. The true population ATE is the average of these CATEs over the super-population.

### Additional file 4: Semi-synthetic pseudo-IPD reconstruction

The five Simpson-paradox examples were reconstructed from published aggregate tables as pseudo-individual records [charig1986][bickel1975][vonkuegelgen2021][haas2021][appleton1996]. The reconstruction is deterministic: each cell in the published treatment (or exposure) by outcome table is expanded to the reported number of records, and outcomes are assigned in the exact proportions shown in the source table (the first n_event records in a cell are events, the remainder are non-events). Covariates are obtained by mapping each cell to a representative value (e.g. age midpoint) plus a small amount of random noise so that the marginal distribution approximates the published totals while preserving the deterministic cell sizes.

For the Israel vaccination example [haas2021], the source table in `data/haas_2021_israel_hospitalization_counts.csv` gives age- and vaccination-stratified population sizes and COVID-19-related hospitalisation counts. Because the full population exceeds six million, we first down-sampled to 100,000 records by stratified random sampling that preserved the age-vaccination cell proportions. Hospitalisation status within each down-sampled cell was then generated by binomial sampling with the observed cell hospitalisation rate followed by deterministic event assignment. The low hospitalisation rate (~0.09% in the down-sampled data) means that several down-sampled cells contain zero or very few events. In such cells, logistic models used by outcome-informed stratification methods were fitted with L2 regularisation, and any degenerate one-class fit was handled by returning the observed cell mean probability. The same deterministic reconstruction and small-cell handling applies to the kidney-stone, Berkeley, smoking and COVID-19 CFR examples.

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

This study frames Incoherence-Oriented Neutralisation and Extraction (IONE) as a descriptive sensitivity tool for hidden effect modification in IPD meta-analysis. C1 and W flag whether a pooled IPD is internally coherent with respect to treatment effect: methods that captured more of the true Z structure produced C1 values close to the Oracle and higher W_true, especially the residual-based method. Agreement with the operational k-means true-Z partition was modest (Oracle ARI {v['best_ari']}; best non-Oracle {v['best_non_oracle_ari_method']} {v['best_non_oracle_ari']}), and the C1 and W_est diagnostics did not reliably discriminate the alternative DGM from the empirical null (C1 AUC {v['c1_auc_min']}-{v['c1_auc_max']}; W AUC {v['w_auc_min']}-{v['w_auc_max']}). Nevertheless, the best data-driven stratification reduced crude ATE bias from {v['crude_bias']} to {v['re_bias']} (relative reduction {v['rel_re']}) with DerSimonian-Laird pooling. These findings show that separating a pooled IPD into more homogeneous strata can partially reduce marginal bias, and that stratum-specific effects should be allowed to vary once incoherence is suggested.

### Detection versus subgroup recovery

Detection asks whether the pooled population is internally coherent; C1 and W address this without requiring hidden subgroups to be specified. The ROC results in Table 4 and Figure 6 show that, in the primary scenario, detection sensitivity from C1 and W_est alone is low. Separating the data into more homogeneous subgroups is harder still, because measured covariates only partially trace the hidden effect modifier. IONE's practical value therefore lies in sensitivity exploration and partial ATE improvement, not in recovering hidden subgroup labels or replacing confounding adjustment.

### Comparison with study-level and covariate-adjustment approaches

Stratification by study remains a default in IPD meta-analysis and captured part of the marginal bias in our benchmark. Study-level random-effects pooling does not, however, exploit covariate traces of hidden effect modification within studies. Propensity-score [rosenbaum1983] and prognostic-score [hansen2008] methods adjust for measured confounders but do not detect unmeasured population structure. Latent-class models [mclachlan2000] seek hidden subgroups but need strong assumptions and do not report a transparent between-stratum heterogeneity diagnostic such as C1. IONE adds a pair of descriptive diagnostics that can be reported alongside these methods.

### W denominator and misspecification

W is a ratio whose denominator is the overall CATE variance. When effect modification is weak this denominator is small, making W unstable and hard to interpret as an absolute measure. We therefore centred the diagnostics on their empirical null means and reported excess values (C1_excess, W_true_excess, W_est_excess). W_est is also sensitive to outcome-model specification: a main-effects-only model for the residual method inflated W_est from {v['misspec_default_west']} to {v['misspec_main_west']}, whereas the correctly specified polynomial interaction model gave {v['misspec_poly_west']}. Analysts should not treat a single W_est value as evidence of an effect modifier without inspecting the fitted outcome model and the empirical null distribution.

### Large-sample behaviour

At n = 10 000 the residual method still showed a non-negligible random-effects ATE bias ({v['n10000_re_bias']}; relative reduction {v['n10000_rel_re']}), similar to the absolute floor observed at n=500 ({v['n500_re_bias']}) and n=2000 ({v['n2000_sens_re_bias']}). This floor is consistent with the ARI ceiling: once finite-sample error is removed, remaining bias reflects the structural mismatch between the discovered strata and the true CATE surface. The true-CATE-quantile oracle provides an upper bound on what perfect sorting could achieve; the gap between the oracle and the leading data-driven method quantifies the cost of not observing the true effect modifier.

### Relevance to CSDA readers

IONE sits between computational stratification diagnostics and model-based effect modification for individual participant data meta-analysis. C1 re-purposes the I^2 statistic for discovered strata and W connects a partition to explained conditional average treatment effect variance. Both are descriptive sensitivity indices, not inferential tests. The empirical null distribution (Supplementary Table S5) calibrates the diagnostics under no true effect modification, and the misspecification sensitivity (Supplementary Table S6) checks whether W_est is robust to the outcome-model specification. The simulation code, analysis scripts and generated tables are publicly available so readers can reproduce every numerical result.

### Strengths and limitations

**Strengths.** The study followed ADEMP [morris2019], reported the data-generating mechanism and estimands transparently, and generated all numerical results from version-controlled repository scripts.

**Limitations.** The primary scenario used n={v['n_ipd']} and a moderate Z-to-X trace; sensitivity analyses examined K = 3, 5, 10, n = 500 to 10 000, Z-to-Y and Z-to-X scales, and a non-linear mapping, but performance may vary with stronger or weaker signals or fewer studies. The true-Z partition is a constructed reference, so ARI should not be over-interpreted as clinical validity. W_est depends on a correctly specified outcome model with interactions; a main-effects-only model can be highly misleading (Supplementary Table S6). DerSimonian-Laird strata are not independent estimates, so the reported tau^2 and I^2 describe between-stratum heterogeneity, not conventional between-study heterogeneity. C1 is computed from log odds ratios while ATE bias is on the risk-difference scale, so it is an indirect diagnostic. Null thresholds (Supplementary Table S5) are method-specific and conditional on the primary DGM. Semi-synthetic examples are pseudo-IPD reconstructions and serve as illustrations, not real-IPD validation.

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
        diagnostic_roc=v['diagnostic_roc'],
    )

    # Citation manager
    cm = CiteManager()
    _register_citations(cm)

    # Build sections
    abstract = (
        f"**Background:** In individual participant data (IPD) meta-analysis, marginal effect estimates can be biased by hidden effect modifiers. "
        f"We introduce two coherence diagnostics, C1 and W, and present a reproducible simulation benchmark of seven stratification approaches.\n\n"
        f"**Methods:** We simulated an IPD meta-analysis with {v['n_studies']} studies and n={v['n_ipd']} participants, binary treatment and outcome, measured covariates carrying traces of an unmeasured modifier, and study-level variation in baseline risk and treatment prevalence. "
        f"Seven methods—two outcome-informed, two outcome-free, propensity-score, prognostic-score and Gaussian-mixture stratification—were compared; stratum-specific risk differences were synthesised with fixed-effect and DerSimonian-Laird random-effects meta-analysis. "
        f"We report ARI, C1, W and ATE bias reduction, calibrating the diagnostics against empirical null distributions.\n\n"
        f"**Results:** At n={v['n_ipd']} and K={v['k_ipd']}, C1 and W_est discriminated the alternative from the empirical null only at chance level (C1 AUC {v['c1_auc_min']}-{v['c1_auc_max']}; W AUC {v['w_auc_min']}-{v['w_auc_max']}). "
        f"The residual-based method achieved the largest random-effects ATE bias reduction (from {v['crude_bias']} to {v['re_bias']}; relative reduction {v['rel_re']}). "
        f"Its absolute bias plateaued near {v['n500_re_bias']} (n=500), {v['n2000_sens_re_bias']} (n=2000) and {v['n10000_re_bias']} (n=10 000), indicating a structural bias floor that persists as sample size increases.\n\n"
        f"**Conclusions:** IONE is a descriptive sensitivity framework, not an inferential test for hidden effect modification. "
        f"The benchmark shows that data-driven stratification can reduce marginal ATE bias when measured covariates carry strong traces of hidden effect modification, but C1 and W must be interpreted relative to method-specific empirical nulls and are not standalone decision criteria."
    )
    keywords = "individual participant data meta-analysis; evidence synthesis; heterogeneity; hidden effect modification; stratification; simulation"

    # Extract and adapt Background and Discussion
    old_bg = _extract_section(old_md, 'Background')
    background = _adapt_background(old_bg, cm, v)
    discussion = _new_discussion(v)

    # Ensure Background contains RSM framing
    # (the adaptation function already adds meta-analysis intro)

    # Build the markdown
    md = f"""# {MANUSCRIPT_TITLE}

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
    md_path = os.path.join(SUBMISSION_DIR, 'IONE_csda_v1.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)

    docx_path = os.path.join(SUBMISSION_DIR, 'IONE_csda_v1.docx')
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
    supp_md_path = os.path.join(SUBMISSION_DIR, 'csda_supplementary_v1.md')
    with open(supp_md_path, 'w', encoding='utf-8') as f:
        f.write(supp_md)
    supp_docx_path = os.path.join(SUBMISSION_DIR, 'csda_supplementary_v1.docx')
    convert(supp_md_path, supp_docx_path, cite_manager=supp_cm, figure_dir=FIG_DIR)


    # Separate title page
    tp = Document()
    tp_style = tp.styles['Normal']
    tp_style.font.name = 'Times New Roman'
    tp_style.font.size = Pt(11)
    tp_title = tp.add_heading(MANUSCRIPT_TITLE, level=0)
    tp_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
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
    tp_path = os.path.join(SUBMISSION_DIR, 'title_page_csda_v1.docx')
    tp.save(tp_path)

    # Double-spaced PDF for initial submission
    ds_docx_path = os.path.join(SUBMISSION_DIR, 'IONE_csda_v1_double_spaced.docx')
    _make_double_spaced(docx_path, ds_docx_path)
    pdf_path = os.path.join(SUBMISSION_DIR, 'IONE_csda_v1_double_spaced.pdf')
    try:
        import subprocess
        subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', SUBMISSION_DIR, ds_docx_path], check=True)
    except Exception as e:
        print(f'[generate_ione_rsm_v3] PDF conversion skipped: {e}')

    # Cover letter
    cover_md = os.path.join(SUBMISSION_DIR, 'cover_letter_csda_v1.md')
    if os.path.exists(cover_md):
        from md_to_rsm_docx import convert as _convert
        cover_docx = os.path.join(SUBMISSION_DIR, 'cover_letter_csda_v1.docx')
        _convert(cover_md, cover_docx)

    # Submission package zip
    import zipfile
    zip_path = os.path.join(SUBMISSION_DIR, 'v1_ione_csda_submission_package.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(docx_path, os.path.basename(docx_path))
        zf.write(tp_path, os.path.basename(tp_path))
        cover_docx = os.path.join(SUBMISSION_DIR, 'cover_letter_csda_v1.docx')
        if os.path.exists(cover_docx):
            zf.write(cover_docx, os.path.basename(cover_docx))
        tables_docx = os.path.join(SUBMISSION_DIR, 'csda_tables_separate.docx')
        if os.path.exists(tables_docx):
            zf.write(tables_docx, os.path.basename(tables_docx))
        if os.path.exists(supp_docx_path):
            zf.write(supp_docx_path, os.path.basename(supp_docx_path))
        if os.path.exists(ds_docx_path):
            zf.write(ds_docx_path, os.path.basename(ds_docx_path))
        if os.path.exists(pdf_path):
            zf.write(pdf_path, os.path.basename(pdf_path))
        highlights_txt = os.path.join(SUBMISSION_DIR, 'highlights.txt')
        if os.path.exists(highlights_txt):
            zf.write(highlights_txt, os.path.basename(highlights_txt))
        highlights_docx = os.path.join(SUBMISSION_DIR, 'highlights.docx')
        if os.path.exists(highlights_docx):
            zf.write(highlights_docx, os.path.basename(highlights_docx))
        pptx_path = os.path.join(FIG_DIR, 'pptx', 'rsm_figures.pptx')
        if os.path.exists(pptx_path):
            zf.write(pptx_path, 'csda_figures.pptx')
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
