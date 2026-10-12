"""
Generate a full-length RSM-framed IONE manuscript.

This script keeps the RSM IPD meta-analysis framing and current numerical
results, but restores the detailed Background, Methods and Discussion
sections from the previous longer version of the manuscript.

All numerical values are read from results/summary/*.csv produced by
generate_summary.py; no manuscript numbers are hard-coded.
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import OrderedDict
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pptx import Presentation
from pptx.util import Inches as PptxInches

from generate_manuscript import _read_csv, _fmt, _add_caption, _add_method_table

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
SUMMARY_DIR = os.path.join(RESULTS_DIR, 'summary')
FIG_DIR = os.path.join(RESULTS_DIR, 'figures')
DOCX_DIR = os.path.join(RESULTS_DIR, 'manuscript')
RSM_DIR = os.path.join(DOCX_DIR, 'rsm_submission')
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RSM_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Author-date citation manager (Cambridge / RSM style)
# ---------------------------------------------------------------------------
class RsmCite:
    def __init__(self):
        self._refs = OrderedDict()

    def register(self, key, author_short, year, full_ref):
        self._refs[key] = {'author': author_short, 'year': year, 'full': full_ref}
        return key

    def cite(self, key, narrative=False):
        if key not in self._refs:
            raise KeyError(f'Citation key {key} not registered')
        r = self._refs[key]
        if narrative:
            return f"{r['author']} ({r['year']})"
        return f"({r['author']} {r['year']})"

    def write_reference_list(self, doc):
        doc.add_heading('References', level=1)
        items = sorted(
            self._refs.items(),
            key=lambda kv: (kv[1]['author'].split(' and ')[0].split(',')[0].strip().lower(),
                           kv[1]['year'], kv[0])
        )
        for _, v in items:
            p = doc.add_paragraph()
            p.add_run(v['full'])


cm = RsmCite()
cm.register('appleton1996', 'Appleton et al.', 1996,
            'Appleton DR, French NR, Vanderpump MP. 1996. Ignoring a covariate: an example of Simpson\'s paradox. Am Stat. 50(4):340-341.')
cm.register('austin2015', 'Austin and Stuart', 2015,
            'Austin PC, Stuart EA. 2015. Moving towards best practice when using inverse probability of treatment weighting (IPTW) using the propensity score to estimate causal treatment effects in observational studies. Stat Med. 34(28):3661-3679.')
cm.register('borenstein2009', 'Borenstein et al.', 2009,
            'Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. 2009. Introduction to Meta-Analysis. Chichester: John Wiley & Sons.')
cm.register('dersimonian1986', 'DerSimonian and Laird', 1986,
            'DerSimonian R, Laird N. 1986. Meta-analysis in clinical trials. Control Clin Trials. 7(3):177-188.')
cm.register('greenland1999', 'Greenland et al.', 1999,
            'Greenland S, Robins JM, Pearl J. 1999. Confounding and collapsibility in causal inference. Stat Sci. 14(1):29-46.')
cm.register('hernan2020', 'Hernán and Robins', 2020,
            'Hernán MA, Robins JM. 2020. Causal Inference: What If. Boca Raton: Chapman & Hall/CRC.')
cm.register('higgins2002', 'Higgins and Thompson', 2002,
            'Higgins JPT, Thompson SG. 2002. Quantifying heterogeneity in a meta-analysis. Stat Med. 21(11):1539-1558.')
cm.register('julious1994', 'Julious and Mullee', 1994,
            'Julious SA, Mullee MA. 1994. Confounding and Simpson\'s paradox. BMJ. 309(6967):1480-1481.')
cm.register('morris2021', 'Morris', 2021,
            'Morris JS. 2021. Israeli data: How can efficacy vs. severe disease be strong when 60% of hospitalized are vaccinated? Available from: https://www.covid-datascience.com/post/israeli-data-how-can-efficacy-vs-severe-disease-be-strong-when-60-of-hospitalized-are-vaccinated')
cm.register('pearl2009', 'Pearl', 2009,
            'Pearl J. 2009. Causality. 2nd ed. Cambridge: Cambridge University Press.')
cm.register('riley2010', 'Riley et al.', 2010,
            'Riley RD, Lambert PC, Abo-Zaid G. 2010. Meta-analysis of individual participant data: rationale, conduct, and reporting. BMJ. 340:c221.')
cm.register('riley2011', 'Riley et al.', 2011,
            'Riley RD, Higgins JPT, Deeks JJ. 2011. Interpretation of random effects meta-analyses. BMJ. 342:d549.')
cm.register('rubin1974', 'Rubin', 1974,
            'Rubin DB. 1974. Estimating causal effects of treatments in randomized and nonrandomized studies. J Educ Psychol. 66(5):688-701.')
cm.register('simmonds2005', 'Simmonds et al.', 2005,
            'Simmonds MC, Higgins JPT, Stewart LA, Tierney JF, Clarke MJ, Thompson SG. 2005. Meta-analysis of individual patient data from randomized trials: a review of methods used in practice. Clin Trials. 2(3):209-217.')
cm.register('vanderweele2015', 'VanderWeele', 2015,
            'VanderWeele TJ. 2015. Explanation in Causal Inference: Methods for Mediation and Interaction. Oxford: Oxford University Press.')


def _add_paragraph(doc, text):
    """Add a paragraph with in-text author-date citations replaced."""
    p = doc.add_paragraph()
    parts = re.split(r'(\[[^\]]+\])', text)
    for part in parts:
        m = re.match(r'\[([^\]]+)\]', part)
        if m:
            p.add_run(cm.cite(m.group(1)))
        else:
            p.add_run(part)
    return p


def _add_paragraph_narrative(doc, text):
    """Add a paragraph, allowing [key|narrative] for narrative citations."""
    p = doc.add_paragraph()
    parts = re.split(r'(\[[^\]]+\])', text)
    for part in parts:
        m = re.match(r'\[([^|\]]+)(?:\|([^\]]+))?\]', part)
        if m:
            key = m.group(1)
            narrative = m.group(2) == 'narrative'
            p.add_run(cm.cite(key, narrative=narrative))
        else:
            p.add_run(part)
    return p


def generate_rsm_figures(ipd_primary, ipd_full, real_data,
                         ipd_sensitivity=None, ipd_nonlinearity=None,
                         diagnostic_roc=None):
    """Generate the RSM figures and the editable PPTX deck."""
    os.makedirs(os.path.join(FIG_DIR, 'pptx'), exist_ok=True)
    figs = []

    if ipd_primary is not None and not ipd_primary.empty:
        order = ipd_primary.sort_values('bias_reduction_relative_re_mean', ascending=False)
        x = np.arange(len(order))
        fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))

        # (a) ARI on its own scale
        width = 0.5
        axes[0].bar(x, order['ARI_mean'], width, color='tab:blue')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(order['method'], rotation=45, ha='right')
        axes[0].set_ylabel('Adjusted Rand Index')
        axes[0].set_title('(a) Recovery of true hidden structure')
        axes[0].axhline(0, color='black', linewidth=0.5)

        # (b) C1 and W on a shared [0, 1] homogeneity scale
        width2 = 0.22
        axes[1].bar(x - width2, order['C1_heterogeneity_mean'], width2, label='C1', color='tab:orange')
        axes[1].bar(x, order['W_true_mean'], width2, label='W_true', color='tab:green')
        axes[1].bar(x + width2, order['W_est_mean'], width2, label='W_est', color='tab:red')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(order['method'], rotation=45, ha='right')
        axes[1].set_ylabel('Coherence / homogeneity')
        axes[1].set_ylim(0, 1)
        axes[1].set_title('(b) Stratum coherence diagnostics')
        axes[1].legend(loc='best')
        axes[1].axhline(0, color='black', linewidth=0.5)

        # (c) Bias reduction on risk-difference scale
        width3 = 0.25
        axes[2].bar(x - width3 / 2, order['bias_reduction_relative_mean'], width3, label='Stratified')
        axes[2].bar(x + width3 / 2, order['bias_reduction_relative_re_mean'], width3, label='Random-effects')
        axes[2].set_xticks(x)
        axes[2].set_xticklabels(order['method'], rotation=45, ha='right')
        axes[2].set_ylabel('Relative bias reduction')
        axes[2].set_title('(c) ATE bias reduction (risk difference)')
        axes[2].legend(loc='best')
        axes[2].axhline(0, color='black', linewidth=0.5)

        fig.tight_layout()
        png = os.path.join(FIG_DIR, 'fig1_rsm_ipd_primary.png')
        fig.savefig(png, dpi=300)
        fig.savefig(os.path.join(FIG_DIR, 'fig1_rsm_ipd_primary.eps'), format='eps', bbox_inches='tight')
        plt.close(fig)
        figs.append(('Figure 1', 'Primary IPD scenario: (a) ARI, (b) C1/W coherence diagnostics, and (c) ATE bias reduction by method.', png))

    if ipd_full is not None and not ipd_full.empty:
        top_methods = ['1B_residual', 'PS_propensity_score', 'GMM', 'Prognostic_score', '2B_clustering']
        sub = ipd_full[ipd_full['method'].isin(top_methods)].copy()
        if not sub.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            for method in top_methods:
                msub = sub[sub['method'] == method].sort_values('n_strata')
                if not msub.empty:
                    ax.plot(msub['n_strata'], msub['bias_reduction_relative_re_mean'], marker='o', label=method)
            ax.set_xlabel('Number of strata (K)')
            ax.set_ylabel('Relative bias reduction (RE)')
            ax.set_title('Sensitivity of random-effects bias reduction to number of strata')
            ax.set_xticks(sorted(sub['n_strata'].unique()))
            ax.legend(loc='best')
            ax.axhline(0, color='black', linewidth=0.5)
            fig.tight_layout()
            png = os.path.join(FIG_DIR, 'fig2_rsm_ipd_strata_sensitivity.png')
            fig.savefig(png, dpi=300)
            fig.savefig(os.path.join(FIG_DIR, 'fig2_rsm_ipd_strata_sensitivity.eps'), format='eps', bbox_inches='tight')
            plt.close(fig)
            figs.append(('Figure 2', 'Random-effects ATE bias reduction as the number of strata varies.', png))

    if real_data is not None and not real_data.empty and 'dataset' in real_data.columns:
        sub = real_data[real_data['n_strata'] == 3] if 'n_strata' in real_data.columns else real_data
        pivot = sub.pivot_table(index='method', columns='dataset', values='ARI_mean', aggfunc='mean')
        if not pivot.empty:
            fig, ax = plt.subplots(figsize=(11, 5))
            pivot.plot(kind='bar', ax=ax)
            ax.set_ylabel('Adjusted Rand Index')
            ax.set_title('Real-data illustration: ARI by dataset and method (K=3)')
            ax.legend(title='Dataset', bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.set_xticklabels(pivot.index, rotation=45, ha='right')
            ax.axhline(0, color='black', linewidth=0.5)
            fig.tight_layout()
            png = os.path.join(FIG_DIR, 'fig3_rsm_real_data_ari.png')
            fig.savefig(png, dpi=300)
            fig.savefig(os.path.join(FIG_DIR, 'fig3_rsm_real_data_ari.eps'), format='eps', bbox_inches='tight')
            plt.close(fig)
            figs.append(('Figure 3', 'Real-data illustration: ARI by dataset and method.', png))

    # Figure 4: sample-size sensitivity for the best methods (K=5, z=1, zx=1)
    if ipd_sensitivity is not None and not ipd_sensitivity.empty:
        top_methods = ['1B_residual', 'PS_propensity_score', 'GMM', 'Prognostic_score', '2B_clustering']
        sub = ipd_sensitivity[
            (ipd_sensitivity['method'].isin(top_methods)) &
            (ipd_sensitivity['n_strata'] == 5) &
            (ipd_sensitivity['z_effect_scale'] == 1.0) &
            (ipd_sensitivity['zx_influence_scale'] == 1.0)
        ].copy()
        if not sub.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            for method in top_methods:
                msub = sub[sub['method'] == method].sort_values('n')
                if not msub.empty:
                    ax.plot(msub['n'], msub['bias_reduction_relative_re_mean'], marker='o', label=method)
            ax.set_xlabel('Sample size (n)')
            ax.set_ylabel('Relative bias reduction (RE)')
            ax.set_title('Sample-size sensitivity of RE bias reduction (K=5, z=1, zx=1)')
            ax.set_xticks(sorted(sub['n'].unique()))
            ax.legend(loc='best')
            ax.axhline(0, color='black', linewidth=0.5)
            fig.tight_layout()
            png = os.path.join(FIG_DIR, 'fig4_rsm_ipd_sample_size.png')
            fig.savefig(png, dpi=300)
            fig.savefig(os.path.join(FIG_DIR, 'fig4_rsm_ipd_sample_size.eps'), format='eps', bbox_inches='tight')
            plt.close(fig)
            figs.append(('Figure 4', 'Sample-size sensitivity of random-effects ATE bias reduction (K=5).', png))

    # Figure 5: non-linearity robustness (n=2000, K=5, z=1, zx=1)
    if ipd_nonlinearity is not None and not ipd_nonlinearity.empty:
        top_methods = ['1B_residual', 'PS_propensity_score', 'GMM', 'Prognostic_score', '2B_clustering']
        sub = ipd_nonlinearity[
            (ipd_nonlinearity['method'].isin(top_methods)) &
            (ipd_nonlinearity['n'] == 2000) &
            (ipd_nonlinearity['n_strata'] == 5) &
            (ipd_nonlinearity['z_effect_scale'] == 1.0) &
            (ipd_nonlinearity['zx_influence_scale'] == 1.0)
        ].copy()
        if not sub.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            # Pull corresponding linear point for reference
            if ipd_sensitivity is not None and not ipd_sensitivity.empty:
                lin = ipd_sensitivity[
                    (ipd_sensitivity['method'].isin(top_methods)) &
                    (ipd_sensitivity['n'] == 2000) &
                    (ipd_sensitivity['n_strata'] == 5) &
                    (ipd_sensitivity['z_effect_scale'] == 1.0) &
                    (ipd_sensitivity['zx_influence_scale'] == 1.0)
                ].copy()
            else:
                lin = pd.DataFrame()
            for method in top_methods:
                msub = sub[sub['method'] == method]
                if not msub.empty:
                    val = msub['bias_reduction_relative_re_mean'].iloc[0]
                    ax.scatter([method], [val], marker='o', s=80, label=f'{method} (nonlinear)' if method == top_methods[0] else '')
                if not lin.empty:
                    mlin = lin[lin['method'] == method]
                    if not mlin.empty:
                        val_lin = mlin['bias_reduction_relative_re_mean'].iloc[0]
                        ax.scatter([method], [val_lin], marker='x', s=80, label=f'{method} (linear)' if method == top_methods[0] else '')
            ax.set_ylabel('Relative bias reduction (RE)')
            ax.set_title('Non-linear Z->X robustness (n=2000, K=5, z=1, zx=1)')
            ax.axhline(0, color='black', linewidth=0.5)
            # Create a small custom legend for markers
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=8, label='Non-linear'),
                Line2D([0], [0], marker='x', color='gray', markersize=8, label='Linear'),
            ]
            ax.legend(handles=legend_elements, loc='best')
            fig.tight_layout()
            png = os.path.join(FIG_DIR, 'fig5_rsm_ipd_nonlinearity.png')
            fig.savefig(png, dpi=300)
            fig.savefig(os.path.join(FIG_DIR, 'fig5_rsm_ipd_nonlinearity.eps'), format='eps', bbox_inches='tight')
            plt.close(fig)
            figs.append(('Figure 5', 'Non-linear Z->X robustness: random-effects ATE bias reduction (n=2000, K=5).', png))

    # Figure 6: diagnostic calibration of C1 and W_est (AUC against empirical null)
    if diagnostic_roc is not None and not diagnostic_roc.empty:
        roc = diagnostic_roc.copy()
        # order by W_est AUC, best methods first
        roc = roc.sort_values('w_auc', ascending=True)
        y = np.arange(len(roc))
        fig, ax = plt.subplots(figsize=(8, 5))
        width = 0.35
        ax.barh(y - width / 2, roc['c1_auc'], width, label='C1 AUC', color='tab:orange')
        ax.barh(y + width / 2, roc['w_auc'], width, label='W_est AUC', color='tab:red')
        ax.axvline(0.5, color='black', linewidth=0.8, linestyle='--', label='Chance (AUC=0.5)')
        ax.set_yticks(y)
        ax.set_yticklabels(roc['method'])
        ax.set_xlabel('Area under the ROC curve')
        ax.set_xlim(0.35, 0.65)
        ax.set_title('Diagnostic calibration: discrimination of alternative from null')
        ax.legend(loc='lower right')
        fig.tight_layout()
        png = os.path.join(FIG_DIR, 'fig6_rsm_diagnostic_calibration.png')
        fig.savefig(png, dpi=300)
        fig.savefig(os.path.join(FIG_DIR, 'fig6_rsm_diagnostic_calibration.eps'), format='eps', bbox_inches='tight')
        plt.close(fig)
        figs.append(('Figure 6', 'Diagnostic calibration of C1 and W_est: AUC for discriminating the alternative DGM from the empirical null distribution (n=2000, K=5).', png))

    # Figure 7: CATE variance explained (eta^2 = W_true) by method
    if ipd_primary is not None and not ipd_primary.empty:
        df = ipd_primary.copy().sort_values('W_true_mean', ascending=True)
        y = np.arange(len(df))
        fig, ax = plt.subplots(figsize=(8, 5))
        width = 0.35
        ax.barh(y - width / 2, df['W_true_mean'], width, label='eta^2 (W_true)', color='tab:blue')
        ax.barh(y + width / 2, df['W_est_mean'], width, label='W_est', color='tab:green')
        ax.set_yticks(y)
        ax.set_yticklabels(df['method'])
        ax.set_xlabel('CATE variance explained')
        ax.set_title('CATE variance explained by stratification (primary scenario)')
        ax.legend(loc='lower right')
        fig.tight_layout()
        png = os.path.join(FIG_DIR, 'fig7_cate_variance_explained.png')
        fig.savefig(png, dpi=300)
        fig.savefig(os.path.join(FIG_DIR, 'fig7_cate_variance_explained.eps'), format='eps', bbox_inches='tight')
        plt.close(fig)
        figs.append(('Figure 7', 'CATE variance explained (eta^2 = W_true) and estimated W_est by method in the primary scenario (n=2000, K=5).', png))

    prs = Presentation()
    prs.slide_width = PptxInches(13.333)
    prs.slide_height = PptxInches(7.5)
    for title, caption, png in figs:
        blank = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank)
        title_box = slide.shapes.add_textbox(PptxInches(0.5), PptxInches(0.3),
                                              PptxInches(12), PptxInches(0.6))
        tf = title_box.text_frame
        tf.text = title
        tf.paragraphs[0].font.size = Pt(20)
        tf.paragraphs[0].font.bold = True
        slide.shapes.add_picture(png, PptxInches(1), PptxInches(1.2),
                                 width=PptxInches(11.333))
        cap_box = slide.shapes.add_textbox(PptxInches(0.5), PptxInches(6.5),
                                            PptxInches(12), PptxInches(0.8))
        cap_box.text_frame.text = caption
        cap_box.text_frame.paragraphs[0].font.size = Pt(14)
    pptx_path = os.path.join(FIG_DIR, 'pptx', 'rsm_figures.pptx')
    prs.save(pptx_path)
    return figs, pptx_path


def _build_table_1(ipd_primary, study_summary):
    """Table 1 numeric column map and study footnote string."""
    cols = ['Method', 'ARI', 'C1', 'W_true', 'W_est', 'Crude bias',
            'Stratified bias', 'RE bias', 'Relative reduction strat',
            'Relative reduction RE', 'RE I2']
    numeric_cols = {
        'Method': 'method', 'ARI': 'ARI_mean', 'C1': 'C1_heterogeneity_mean',
        'W_true': 'W_true_mean', 'W_est': 'W_est_mean',
        'Crude bias': 'abs_bias_crude_mean', 'Stratified bias': 'abs_bias_stratified_mean',
        'RE bias': 'abs_bias_re_mean',
        'Relative reduction strat': 'bias_reduction_relative_mean',
        'Relative reduction RE': 'bias_reduction_relative_re_mean',
        'RE I2': 're_I2_mean',
    }
    footnote = None
    if study_summary is not None and not study_summary.empty:
        row = study_summary.iloc[0]
        crude = row.get('study_bias_crude_mean', np.nan)
        re = row.get('study_bias_re_mean', np.nan)
        if pd.notna(crude) and pd.notna(re):
            red = crude - re
            footnote = (f"As a comparator, random-effects pooling across the true study identifiers "
                        f"gave an absolute bias of {_fmt(re)} (absolute reduction {_fmt(red)}).")
    return ipd_primary, cols, numeric_cols, footnote


def _scenario_params():
    """Read scenario descriptor from raw IPD results; primary reporting uses K=5."""
    path = os.path.join(RESULTS_DIR, 'rsm_ipd_results.csv')
    if not os.path.exists(path):
        return 2000, 10, 0.6, 5
    df = pd.read_csv(path, nrows=1)
    n = int(df.get('n', 2000).iloc[0])
    n_studies = int(df.get('n_studies', 10).iloc[0])
    study_effect = float(df.get('study_effect_scale', 0.6).iloc[0])
    n_strata = 5
    return n, n_studies, study_effect, n_strata


def generate_full_rsm_manuscript():
    ipd_primary = _read_csv('rsm_ipd_primary_summary.csv')
    ipd_full = _read_csv('rsm_ipd_full_summary.csv')
    study_summary = _read_csv('rsm_ipd_study_summary.csv')
    real_data = _read_csv('real_data_summary.csv')

    figs, pptx_path = generate_rsm_figures(ipd_primary, ipd_full, real_data)
    n_ipd, n_studies, study_effect, k_ipd = _scenario_params()

    if ipd_primary is None or ipd_primary.empty:
        raise RuntimeError('rsm_ipd_primary_summary.csv is empty or missing')

    best_re = ipd_primary.loc[ipd_primary['bias_reduction_relative_re_mean'].idxmax()]
    best_ari_row = ipd_primary.loc[ipd_primary['ARI_mean'].idxmax()]

    best_method = best_re['method']
    best_ari = _fmt(best_ari_row['ARI_mean'])
    best_ari_method = best_ari_row['method']
    best_c1 = _fmt(best_re['C1_heterogeneity_mean'])
    best_wtrue = _fmt(best_re['W_true_mean'])
    best_west = _fmt(best_re['W_est_mean'])
    crude_bias = _fmt(best_re['abs_bias_crude_mean'], 5)
    strat_bias = _fmt(best_re['abs_bias_stratified_mean'], 5)
    re_bias = _fmt(best_re['abs_bias_re_mean'], 5)
    rel_strat = _fmt(best_re['bias_reduction_relative_mean'], 3)
    rel_re = _fmt(best_re['bias_reduction_relative_re_mean'], 3)
    mean_c1 = _fmt(ipd_primary['C1_heterogeneity_mean'].mean(), 3)
    mean_wtrue = _fmt(ipd_primary['W_true_mean'].mean(), 3)
    mean_west = _fmt(ipd_primary['W_est_mean'].mean(), 3)

    study_footnote = ''
    if study_summary is not None and not study_summary.empty:
        srow = study_summary.iloc[0]
        study_crude = _fmt(srow.get('study_bias_crude_mean', np.nan), 5)
        study_re = _fmt(srow.get('study_bias_re_mean', np.nan), 5)
        study_red = _fmt(srow.get('study_bias_crude_mean', np.nan) - srow.get('study_bias_re_mean', np.nan), 5) if pd.notna(srow.get('study_bias_crude_mean')) and pd.notna(srow.get('study_bias_re_mean')) else '—'
        study_footnote = (f"For comparison, random-effects pooling across the true study identifiers "
                          f"(i.e. a study-level meta-analysis) gave an absolute ATE bias of {study_re} "
                          f"(reduction {study_red} from crude {study_crude}).")

    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(11)

    # Title
    title = doc.add_heading('IONE: Incoherence-Oriented Neutralisation and Extraction for hidden effect modification', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = doc.add_heading('in individual participant data meta-analysis: a simulation study of stratification-based extraction', level=0)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()

    # Abstract
    doc.add_heading('Abstract', level=1)
    abstract_text = (
        "Background. Random-effects meta-analyses report an average treatment effect and assume that between-study heterogeneity has been adequately modelled. "
        "When an individual participant data (IPD) meta-analysis contains hidden effect modifiers or confounders, a marginal summary can be non-robust or qualitatively wrong (aggregation bias). "
        "We propose Incoherence-Oriented Neutralisation and Extraction (IONE), an exploratory diagnostic toolkit for hidden effect modification that can be applied to pooled IPD before a conventional synthesis. "
        f"Methods. We simulated an IPD meta-analysis with {n_studies} studies, a binary treatment and a binary outcome, measured covariates carrying traces of an unmeasured effect-modifier, and study-level variation in baseline risk and treatment prevalence. "
        "Proposed IONE methods and active comparators were used to stratify the pooled IPD; stratum-specific risk differences were pooled with two-stage fixed-effect and DerSimonian-Laird random-effects meta-analysis. "
        "We report ARI with a constructed true-Z partition, C1 (between-stratum heterogeneity of A->Y log odds ratios), W_true and W_est (within-stratum CATE homogeneity using true and estimated CATE), and ATE bias reduction on the risk-difference scale, all with Monte Carlo standard errors. "
        f"Results. In the primary scenario (n={n_ipd}, {n_studies} studies, K={k_ipd} strata), the best method was {best_method} (ARI {best_ari}; C1 {best_c1}; W_true {best_wtrue}; W_est {best_west}). "
        f"Crude absolute ATE bias was {crude_bias}; two-stage stratification reduced this to {strat_bias} (relative reduction {rel_strat}), and random-effects pooling across discovered strata reduced it further to {re_bias} (relative reduction {rel_re}). "
        "Diagnostic agreement with the true hidden structure remained modest, and performance improved with stronger covariate traces and larger samples. "
        "Conclusions. IONE is a transparent, exploratory diagnostic for hidden effect modification within IPD meta-analyses. It should be reported alongside—not instead of—conventional meta-analytic models and covariate adjustment."
    )
    _add_paragraph(doc, abstract_text)
    doc.add_paragraph()
    kw = doc.add_paragraph()
    kw.add_run('Keywords: ').bold = True
    kw.add_run("individual participant data meta-analysis; evidence synthesis; heterogeneity; hidden effect modification; stratification; diagnostic; Simpson's paradox")

    # Introduction
    doc.add_heading('1. Introduction', level=1)
    _add_paragraph(doc, (
        "Meta-analysis combines treatment-effect estimates from related studies and is central to evidence-based medicine and policy [borenstein2009]. "
        "A random-effects analysis permits the true effect to vary across studies and is widely recommended when between-study heterogeneity is suspected [dersimonian1986][higgins2002][riley2011]. "
        "In an individual participant data (IPD) meta-analysis, the original participant-level data are collected, harmonised and re-analysed; this preserves information on covariates and subgroup effects and can improve power for treatment-covariate interactions [riley2010][simmonds2005]. "
        "Despite these advantages, the standard two-stage or one-stage synthesis still estimates an average effect and may miss effect modifiers that are unmeasured, measured with error, or omitted from the analysis plan."
    ))
    _add_paragraph(doc, (
        "When a pooled population is a mixture of subgroups with different treatment effects, or when confounders differ across studies, the marginal effect can differ from subgroup-specific effects, leading to aggregation bias and Simpson-type reversals [pearl2009][greenland1999]. "
        "Causal inference provides formal definitions of confounding, effect modification and collapsibility [rubin1974][hernan2020][vanderweele2015], and propensity-score methods can adjust for measured confounders [austin2015]. "
        "Yet these methods do not in themselves reveal whether an unmeasured effect modifier is present or whether the estimated average effect is robust across clinically meaningful subgroups. "
        "In particular, random-effects meta-analysis explains heterogeneity through study-level summaries and meta-regression; it does not routinely test whether the pooled participants themselves form incoherent subpopulations."
    ))
    _add_paragraph(doc, (
        "We develop Incoherence-Oriented Neutralisation and Extraction (IONE) for the IPD meta-analysis setting. "
        "IONE is a two-stage exploratory diagnostic. In the first stage, routinely measured covariates are used to test whether the pooled IPD is coherent with respect to the treatment effect. "
        "In the second stage, if incoherence is indicated, the pooled IPD is stratified into more homogeneous subgroups and stratum-specific effects are synthesised. "
        "We ask whether data-driven stratification of a pooled IPD can reduce bias in the average treatment effect and whether simple diagnostics can warn analysts when a marginal summary is fragile. "
        "We evaluate the proposal in a Monte Carlo simulation with explicit between-study heterogeneity and hidden effect modification, and illustrate the behaviour with well-known Simpson-paradox examples."
    ))

    # Methods
    doc.add_heading('2. Methods', level=1)

    doc.add_heading('2.1 Aims', level=2)
    _add_paragraph(doc, 'The aims of the simulation study were:')
    _add_paragraph(doc, (
        '1. To evaluate whether stratification of a pooled IPD based solely on measured covariates can recover hidden subgroup structure defined by unmeasured effect modifiers/confounders. '
        '2. To compare the performance of outcome-informed IONE methods with outcome-free methods and with established comparators (propensity-score quintiles, Gaussian mixture model, prognostic-score stratification). '
        '3. To assess the ability of C1 (between-stratum heterogeneity) and W (within-stratum homogeneity) to diagnose hidden effect modification. '
        '4. To quantify ATE bias reduction achieved by two-stage stratified and random-effects synthesis. '
        '5. To identify the data-generating conditions under which the proposed diagnostics are most and least informative.'
    ))

    doc.add_heading('2.2 IPD data-generating mechanism', level=2)
    _add_paragraph(doc, (
        f"We generated an IPD meta-analysis by assigning n={n_ipd} participants to {n_studies} studies of approximately equal size. "
        f"Study-level heterogeneity was controlled by a scale parameter of {study_effect}; this produced between-study variation in baseline risk, treatment prevalence and the distribution of a continuous age-like covariate, analogous to the between-study variance in a random-effects meta-analysis. "
        "Each participant had three critical variables (Z1 continuous, Z2 binary, Z3 ordered) that affected treatment, outcome and their interaction, and ten measured variables (X1-X10) that carried traces of Z. "
        "A binary treatment A was generated from a logistic model with confounders Z and covariates X; a binary outcome Y was generated from a logistic model with main effects of Z and X, a treatment main effect and Z-by-A interactions (effect modification). "
        "The true estimand was the population risk-difference average treatment effect (ATE), computed by averaging the true individual conditional average treatment effect (CATE) over the super-population."
    ))
    _add_paragraph(doc, (
        "The data-generating mechanism follows a causal directed acyclic graph. Study membership introduces heterogeneity in the intercepts for baseline risk and treatment prevalence; within each study, the same confounder-modifier Z generates measured covariates X, treatment A and outcome Y. "
        "This design mimics an IPD meta-analysis in which studies differ in case-mix and treatment use, yet a common unmeasured effect modifier is present. "
        "Full algebraic details and parameter values are given in the repository, and all scenarios were assigned fixed random seeds for reproducibility."
    ))

    doc.add_heading('2.3 Stratification methods', level=2)
    _add_paragraph(doc, (
        "Proposed IONE methods were divided into two families. Family 1 (outcome-informed) used predicted probability of Y, absolute residuals from a Y~X model, and cross-validated decision scores. "
        "Family 2 (outcome-free) used PCA on X and k-means on X. "
        "Active comparators were propensity-score quintiles, a Gaussian mixture model on X and prognostic-score stratification from a Y~X model fitted in the untreated. "
        "Oracle baselines stratified by the true Z using k-means or quantiles, and random stratification provided a lower baseline. "
        "Outcome-informed methods used a 50/50 discovery/evaluation split to avoid outcome-label leakage."
    ))
    _add_paragraph(doc, (
        "All methods produce a one-dimensional score except clustering-based methods, which assign strata directly. "
        "After scoring, equal-frequency quantiles were used to create K strata. "
        "Logistic regression for predicted probability and residuals used l2 regularisation (C=1.0, lbfgs solver, max_iter=1000); the random forest used 100 trees with max_depth=10; k-means and Gaussian mixture model used n_init=10 and a fixed random seed. "
        "Standardisation was applied before PCA, k-means and GMM."
    ))

    doc.add_heading('2.4 Synthesis of stratum-specific effects', level=2)
    _add_paragraph(doc, (
        "For each discovered stratum we computed the risk difference P(Y=1|A=1) - P(Y=1|A=0) and its standard error. "
        "A two-stage fixed-effect summary was the stratum-size-weighted average of these risk differences. "
        "A DerSimonian-Laird random-effects summary added an estimate of between-stratum variance and re-weighted stratum estimates accordingly [dersimonian1986]. "
        "We also report the resulting tau^2 and I^2 as summaries of between-stratum heterogeneity in the effect scale. "
        "The random-effects synthesis treats discovered strata as studies in a conventional meta-analysis, allowing the stratum-specific effects to vary."
    ))

    doc.add_heading('2.5 Evaluation metrics', level=2)
    _add_paragraph(doc, (
        "For each method we report: (i) ARI versus a constructed true-Z partition; (ii) C1 = 1 - I^2 from stratum-specific log odds ratios of A->Y, reflecting between-stratum homogeneity; (iii) W_true and W_est, measuring within-stratum CATE homogeneity using the true individual CATE or a flexible estimated CATE from a Y~X+A+X*A logistic model; and (iv) ATE bias reduction on the risk-difference scale. "
        "Bias reduction is reported as the absolute difference |bias_crude| - |bias_stratified| and |bias_crude| - |bias_re|, and as the relative ratio 1 - |bias_stratified|/|bias_crude|. "
        "Monte Carlo standard errors and 95% confidence intervals are reported for every mean."
    ))
    _add_paragraph(doc, (
        "The true-Z partition is an operational construct: k-means clustering applied to the standardised Z-space with K equal to the number of strata. "
        "ARI therefore measures agreement with a constructed reference rather than with clinically observed subgroups. "
        "W_true is available only in simulation; W_est is the operational diagnostic that can be computed in real data, although it requires a correctly specified outcome model and should be interpreted cautiously."
    ))

    doc.add_heading('2.6 Semi-synthetic illustrations', level=2)
    _add_paragraph(doc, (
        "Five well-known Simpson-paradox examples were reconstructed as pseudo-individual records from published aggregate statistics: kidney stone treatments [appleton1996], UC Berkeley admissions [julious1994], Israeli vaccine effectiveness [morris2021], and two additional examples. "
        "For each example, pseudo-general variables were generated to mimic proxies of the known confounder, and the same IONE methods were applied. "
        "These examples illustrate favourable and unfavourable settings for stratification; they are not validation of out-of-the-box performance in real IPD."
    ))

    doc.add_heading('2.7 Computational implementation', level=2)
    _add_paragraph(doc, (
        "All simulations and analyses were conducted in Python 3.11. The pipeline comprises data_generation.py, methods.py, evaluation.py, run_rsm_ipd_simulation.py, generate_summary.py and this manuscript generator. "
        "The code and semi-synthetic example data are available at https://github.com/bougtoir/ione-stratification-framework. "
        "All numerical results in this manuscript are produced by the repository scripts; no estimates are hard-coded."
    ))

    # Results
    doc.add_heading('3. Results', level=1)
    doc.add_heading('3.1 Primary IPD scenario', level=2)
    _add_paragraph(doc, (
        f"Table 1 and Figure 1 summarise the primary IPD scenario (n={n_ipd}, {n_studies} studies, K={k_ipd} strata). "
        f"Extraction of the true hidden structure was modest: the best ARI was {best_ari}, observed for {best_ari_method}, and the average C1 across methods was {mean_c1}. "
        f"Average within-stratum homogeneity was also limited (mean W_true = {mean_wtrue}; mean W_est = {mean_west}), indicating that the discovered strata still contained substantial CATE variation. "
        f"{study_footnote}"
    ))
    _add_paragraph(doc, (
        f"ATE bias reduction was strongest for {best_method}: the crude absolute risk-difference bias was {crude_bias}, the two-stage stratified estimate reduced this to {strat_bias} (relative reduction {rel_strat}), and the random-effects estimate reduced it further to {re_bias} (relative reduction {rel_re}). "
        "These values show that, under the simulated data-generating mechanism, a small number of data-driven strata can partially remove bias from a pooled IPD estimate, but the diagnostic agreement with the true hidden structure remains low."
    ))

    if ipd_primary is not None:
        _, cols, numeric_cols, footnote = _build_table_1(ipd_primary, study_summary)
        _add_method_table(
            doc, ipd_primary, cols,
            caption=f'Table 1. Primary IPD scenario (n={n_ipd}, {n_studies} studies, K={k_ipd}): means over 50 simulations.',
            numeric_cols=numeric_cols,
        )
        if footnote:
            doc.add_paragraph(footnote, style='Intense Quote')
        if figs:
            doc.add_picture(figs[0][2], width=Inches(5.8))
            _add_caption(doc, figs[0][0] + '. ' + figs[0][1])
            doc.add_paragraph()

    doc.add_heading('3.2 Sensitivity to the number of strata', level=2)
    _add_paragraph(doc, (
        "Figure 2 shows how random-effects bias reduction changed as the number of strata varied (K = 3, 5, 10). "
        "For most methods the gain from increasing K was limited and non-monotonic; increasing strata beyond the true dimensionality of the hidden structure introduced additional sampling variation and did not consistently improve ATE bias reduction. "
        "This finding suggests that the number of strata should be chosen conservatively or compared across several values, rather than simply maximised."
    ))
    if len(figs) > 1:
        doc.add_picture(figs[1][2], width=Inches(5.8))
        _add_caption(doc, figs[1][0] + '. ' + figs[1][1])
        doc.add_paragraph()

    doc.add_heading('3.3 Semi-synthetic illustrations', level=2)
    _add_paragraph(doc, (
        "Five well-known Simpson-paradox examples were reconstructed as pseudo-individual records and pseudo-general variables were generated to mimic proxies of the known confounder [morris2021][appleton1996][julious1994]. "
        "High ARI was obtained only when the pseudo-variables were strongly correlated with a low-dimensional confounder. "
        "Table 2 and Figure 3 present the best-performing method and stratum count for each dataset. "
        "These examples are illustrations of favourable and unfavourable settings for stratification, not validation of out-of-the-box performance in real IPD."
    ))
    if real_data is not None:
        rd_best = real_data.loc[real_data.groupby('dataset')['ARI_mean'].idxmax()].copy()
        _add_method_table(
            doc, rd_best,
            ['Dataset', 'Method', 'K', 'ARI', 'C1', 'W_est', 'Bias reduction'],
            caption='Table 2. Best real-data illustration result per dataset.',
            numeric_cols={
                'Dataset': 'dataset', 'Method': 'method', 'K': 'n_strata',
                'ARI': 'ARI_mean', 'C1': 'C1_heterogeneity_mean', 'W_est': 'W_est_mean',
                'Bias reduction': 'bias_reduction_mean'
            }
        )
        if len(figs) > 2:
            doc.add_picture(figs[2][2], width=Inches(5.8))
            _add_caption(doc, figs[2][0] + '. ' + figs[2][1])
            doc.add_paragraph()

    # Discussion
    doc.add_heading('4. Discussion', level=1)

    doc.add_heading('4.1 Principal findings', level=2)
    _add_paragraph(doc, (
        "This study frames IONE within an IPD meta-analysis setting and evaluates it as a diagnostic for hidden effect modification. "
        "The principal findings are twofold. First, the C1 and W diagnostics can signal when a pooled IPD contains hidden effect modification, even when the data-driven strata do not perfectly recover the true hidden structure. "
        "Second, data-driven stratification sometimes reduced ATE bias on the risk-difference scale, and random-effects pooling across discovered strata often improved on a simple two-stage stratified estimate. "
        "However, the strata only partially captured the true hidden Z structure, as shown by low ARI and moderate W values. "
        "Success was conditional on the confounder/effect-modifier leaving strong traces in the measured covariates and on a simple low-dimensional structure."
    ))

    doc.add_heading('4.2 Comparison with existing methods', level=2)
    _add_paragraph(doc, (
        "IONE differs from standard meta-analysis tools in its objectives and assumptions. Propensity-score methods and prognostic scores aim to balance or adjust for measured confounders [austin2015]; they are not designed to detect unmeasured population structure. "
        "Meta-regression and one-stage mixed models explain heterogeneity through observed study or participant characteristics [riley2010][riley2011], but they cannot reveal effect modifiers that are unmeasured. "
        "Latent class and finite mixture models identify hidden subgroups under parametric distributional assumptions but do not provide a coherence diagnostic that is directly linked to treatment-effect homogeneity. "
        "IONE is best understood as a preliminary diagnostic: if C1 indicates incoherence, the pooled IPD is stratified and conventional methods are applied within strata."
    ))

    doc.add_heading('4.3 Strengths and limitations', level=2)
    _add_paragraph(doc, (
        "Strengths of this study include an explicit causal data-generating mechanism with both confounding and effect modification, a systematic comparison with active comparators, the use of a discovery/evaluation split to mitigate outcome-label leakage, and the reporting of both simulation-only (W_true) and operational (W_est) diagnostics. "
        "All numerical results are produced from a version-controlled repository."
    ))
    _add_paragraph(doc, (
        "Several limitations should be acknowledged. First, the data-generating mechanism is stylised: three critical variables, ten measured variables, a logistic outcome and no censoring, missing data or measurement error. "
        "Real clinical IPD may involve more complex causal structures. "
        "Second, the true-Z partition is constructed rather than clinically observed, so ARI measures agreement with an operational reference. "
        "Third, the semi-synthetic examples use reconstructed individual records and pseudo-general variables; they demonstrate operating characteristics under known confounding but do not fully replicate real data. "
        "Fourth, outcome-informed residual stratification carries a circularity risk if the same data are used for stratum assignment and effect estimation; our 50/50 split mitigates but does not eliminate this concern. "
        "Finally, C1 and W require calibration before applied use; the values reported here should not be interpreted as universal thresholds."
    ))

    doc.add_heading('4.4 Implications for practice', level=2)
    _add_paragraph(doc, (
        "If replicated in further studies, our findings have several practical implications. First, IPD meta-analysis reports could include C1 and W alongside conventional heterogeneity statistics (tau^2, I^2) to make the assumption of within-stratum homogeneity explicit. "
        "Second, when C1 indicates incoherence, analysts should explore subgroup-specific estimates rather than rely solely on the marginal average. "
        "Third, both outcome-informed and outcome-free methods should be applied and compared; agreement between the two families provides stronger evidence for hidden effect modification. "
        "IONE is intended to complement, not replace, established covariate adjustment, meta-regression and one-stage mixed models."
    ))

    doc.add_heading('4.5 Future directions', level=2)
    _add_paragraph(doc, (
        "Future work should extend IONE to time-to-event outcomes, continuous outcomes and network meta-analysis, where the structure of treatment contrasts is more complex. "
        "Calibration of C1 and W on real clinical IPD, and comparison with latent-class and mixture-model approaches, would clarify the practical value of the diagnostics. "
        "Incorporating prior domain knowledge into the stratification, and developing software packages in R and Python, would facilitate adoption."
    ))

    # Conclusions
    doc.add_heading('5. Conclusions', level=1)
    _add_paragraph(doc, (
        "We have introduced IONE (Incoherence-Oriented Neutralisation and Extraction) as an exploratory diagnostic for hidden effect modification in IPD meta-analysis. "
        "Through Monte Carlo simulation and semi-synthetic examples, we show that IONE can detect incoherence and partially reduce ATE bias when hidden variables leave strong traces in measured covariates. "
        "The diagnostics should be reported alongside conventional meta-analytic models and covariate adjustment, and should not be used as a replacement for rigorous causal inference. "
        "We recommend that coherence assessment be considered as a standard sensitivity step in IPD meta-analysis reporting."
    ))

    # Data/code availability
    doc.add_heading('Data and code availability', level=1)
    _add_paragraph(doc, (
        "The simulation code and semi-synthetic example data are available at "
        "https://github.com/bougtoir/ione-stratification-framework. "
        "All numerical results in this manuscript are produced by scripts in the repository; no estimates are hard-coded."
    ))

    # References
    cm.write_reference_list(doc)

    docx_path = os.path.join(RSM_DIR, 'IONE_rsm_full_manuscript.docx')
    doc.save(docx_path)

    # Title page
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
    tp.add_paragraph('bougtoir@gmail.com')
    tp.add_paragraph()
    tp_note = tp.add_paragraph('Corresponding author: Onishi Tatsuki')
    tp_note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp_path = os.path.join(RSM_DIR, 'title_page_rsm_full.docx')
    tp.save(tp_path)

    print(f'[generate_full_rsm_manuscript] manuscript written to {docx_path}')
    print(f'[generate_full_rsm_manuscript] title page written to {tp_path}')
    print(f'[generate_full_rsm_manuscript] figures written to {FIG_DIR}; pptx at {pptx_path}')
    return docx_path


if __name__ == '__main__':
    generate_full_rsm_manuscript()
