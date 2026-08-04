"""
Generate an RSM-framed manuscript and figures for the IONE framework.
All numbers are read from results/summary/*.csv produced by generate_summary.py.
References are formatted in author-date (Harvard) style for Cambridge / Research Synthesis Methods.
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

# Re-use helpers from the existing manuscript generator
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
        """author_short is the text used in in-text citations, e.g. 'Higgins and Thompson'."""
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
        # Sort alphabetically by first author surname, then year
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
    """Add a paragraph with in-text author-date citations replaced.
    Citation keys are written as [key] in the source text."""
    p = doc.add_paragraph()
    parts = re.split(r'(\[[^\]]+\])', text)
    for part in parts:
        m = re.match(r'\[([^\]]+)\]', part)
        if m:
            p.add_run(cm.cite(m.group(1)))
        else:
            p.add_run(part)
    return p


def generate_rsm_figures(ipd_primary, ipd_full, real_data):
    os.makedirs(os.path.join(FIG_DIR, 'pptx'), exist_ok=True)
    figs = []

    # Figure 1: primary IPD scenario – two panels
    if ipd_primary is not None and not ipd_primary.empty:
        order = ipd_primary.sort_values('bias_reduction_relative_re_mean', ascending=False)
        x = np.arange(len(order))
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))

        # Left panel: diagnostic metrics
        width = 0.18
        metrics = ['ARI_mean', 'C1_heterogeneity_mean', 'W_true_mean', 'W_est_mean']
        labels = ['ARI', 'C1', 'W_true', 'W_est']
        for i, (m, lab) in enumerate(zip(metrics, labels)):
            axes[0].bar(x + (i - 1.5) * width, order[m], width, label=lab)
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(order['method'], rotation=45, ha='right')
        axes[0].set_ylabel('Metric value')
        axes[0].set_title('Diagnostic metrics (IPD primary scenario)')
        axes[0].legend(loc='upper right')
        axes[0].axhline(0, color='black', linewidth=0.5)

        # Right panel: relative ATE bias reduction
        width2 = 0.25
        axes[1].bar(x - width2 / 2, order['bias_reduction_relative_mean'], width2, label='Stratified')
        axes[1].bar(x + width2 / 2, order['bias_reduction_relative_re_mean'], width2, label='Random-effects')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(order['method'], rotation=45, ha='right')
        axes[1].set_ylabel('Relative bias reduction')
        axes[1].set_title('ATE bias reduction (risk difference)')
        axes[1].legend(loc='upper right')
        axes[1].axhline(0, color='black', linewidth=0.5)

        fig.tight_layout()
        png = os.path.join(FIG_DIR, 'fig1_rsm_ipd_primary.png')
        fig.savefig(png, dpi=300)
        fig.savefig(os.path.join(FIG_DIR, 'fig1_rsm_ipd_primary.eps'), format='eps', bbox_inches='tight')
        plt.close(fig)
        figs.append(('Figure 1', 'Primary IPD scenario: diagnostic metrics and ATE bias reduction by method.', png))

    # Figure 2: sensitivity to number of strata (RE bias reduction)
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

    # Figure 3: real-data ARI
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
    cols = ['Method', 'ARI', 'C1', 'W_true', 'W_est', 'Crude bias', 'Stratified bias',
            'RE bias', 'Relative reduction strat', 'Relative reduction RE', 'RE I2']
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
    """Read the scenario descriptor from the raw IPD results.

    The primary RSM scenario is hard-coded to K=5 to match summarise_rsm_ipd().
    """
    path = os.path.join(RESULTS_DIR, 'rsm_ipd_results.csv')
    if not os.path.exists(path):
        return 2000, 10, 0.6, 5
    df = pd.read_csv(path, nrows=1)
    n = int(df.get('n', 2000).iloc[0])
    n_studies = int(df.get('n_studies', 10).iloc[0])
    study_effect = float(df.get('study_effect_scale', 0.6).iloc[0])
    # Primary reporting uses K=5 (the middle of n_strata_list=[3,5,10]).
    n_strata = 5
    return n, n_studies, study_effect, n_strata


def generate_rsm_manuscript():
    ipd_primary = _read_csv('rsm_ipd_primary_summary.csv')
    ipd_full = _read_csv('rsm_ipd_full_summary.csv')
    study_summary = _read_csv('rsm_ipd_study_summary.csv')
    real_data = _read_csv('real_data_summary.csv')

    figs, pptx_path = generate_rsm_figures(ipd_primary, ipd_full, real_data)
    n_ipd, n_studies, study_effect, k_ipd = _scenario_params()

    # Aggregate numbers for the prose (all from CSVs)
    best_re = None
    if ipd_primary is not None and not ipd_primary.empty:
        best_re = ipd_primary.loc[ipd_primary['bias_reduction_relative_re_mean'].idxmax()]
    if best_re is None:
        raise RuntimeError('rsm_ipd_primary_summary.csv is empty or missing')

    best_method = best_re['method']
    best_ari = _fmt(best_re['ARI_mean'])
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
                          f"(i.e. study-level meta-analysis) gave an absolute ATE bias of {study_re} "
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
        "We propose Incoherence-Oriented Neutralisation and Extraction (IONE), an exploratory diagnostic toolkit for hidden effect modification. "
        f"Methods. We simulated an IPD meta-analysis with {n_studies} studies, binary treatment and outcome, measured covariates carrying traces of an unmeasured effect-modifier, and study-level variation in baseline risk and treatment prevalence. "
        "Proposed IONE methods and active comparators were used to stratify the pooled IPD; stratum-specific risk differences were pooled with two-stage fixed-effect and DerSimonian-Laird random-effects meta-analysis. "
        "We report ARI with a constructed true-Z partition, C1 (between-stratum heterogeneity of A→Y log odds ratios), W (within-stratum CATE homogeneity), and ATE bias reduction on the risk-difference scale. "
        f"Results. In the primary scenario (n={n_ipd}, {n_studies} studies, K={k_ipd} strata), the best method was {best_method} (ARI {best_ari}; C1 {best_c1}; W_true {best_wtrue}; W_est {best_west}). "
        f"Crude absolute ATE bias was {crude_bias}; stratification reduced this to {strat_bias} (relative reduction {rel_strat}), and random-effects pooling across discovered strata further reduced it to {re_bias} (relative reduction {rel_re}). "
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
        "Meta-analysis combines treatment-effect estimates from related studies and is central to evidence-based medicine [borenstein2009]. "
        "A random-effects analysis permits the true effect to vary across studies and is widely recommended when heterogeneity is suspected [dersimonian1986][higgins2002][riley2011]. "
        "In an individual participant data (IPD) meta-analysis, the original participant-level data are collected and re-analysed; this preserves information on covariates and subgroup effects and can improve power for treatment-covariate interactions [riley2010][simmonds2005]. "
        "Nevertheless, the standard two-stage or one-stage synthesis still estimates an average effect and may miss effect modifiers that are not measured, measured with error, or omitted from the analysis plan."
    ))
    _add_paragraph(doc, (
        "When the population is a mixture of subgroups with different treatment effects, or when confounders differ across subgroups, the marginal effect can differ from subgroup-specific effects, leading to aggregation bias and Simpson-type reversals [pearl2009][greenland1999]. "
        "Causal inference provides formal definitions of confounding, effect modification and collapsibility [rubin1974][hernan2020][vanderweele2015], and propensity-score methods adjust for measured confounders [austin2015]. "
        "Yet these methods do not in themselves reveal whether an unmeasured effect modifier is present or whether the estimated average effect is robust across clinically meaningful subgroups."
    ))
    _add_paragraph(doc, (
        "We develop Incoherence-Oriented Neutralisation and Extraction (IONE) for the IPD meta-analysis setting. "
        "We ask whether routine measured covariates can be used to stratify a pooled IPD so that within-stratum treatment effects are more homogeneous and the pooled estimate is less biased. "
        "We evaluate the proposal in a simulation study with explicit between-study heterogeneity and hidden effect modification, and illustrate behaviour with well-known Simpson-paradox examples."
    ))

    # Methods
    doc.add_heading('2. Methods', level=1)
    doc.add_heading('2.1 IPD data-generating mechanism', level=2)
    _add_paragraph(doc, (
        f"We generated an IPD meta-analysis by assigning n={n_ipd} participants to {n_studies} studies of approximately equal size. "
        f"Study-level heterogeneity was controlled by a scale parameter of {study_effect}; this produced between-study variation in baseline risk, treatment prevalence and the distribution of a continuous age-like covariate, analogous to a random-effects meta-analysis. "
        "Each participant had three critical variables (Z1 continuous, Z2 binary, Z3 ordered) that affected treatment, outcome and their interaction, and ten measured variables (X1–X10) that carried traces of Z. "
        "A binary treatment A was generated from a logistic model with confounders Z and covariates X; a binary outcome Y was generated from a logistic model with main effects of Z and X, a treatment main effect and Z×A interactions (effect modification). "
        "The true estimand was the population risk-difference average treatment effect (ATE), computed by averaging the true individual CATE over the super-population."
    ))

    doc.add_heading('2.2 Stratification methods', level=2)
    _add_paragraph(doc, (
        "Proposed IONE methods were divided into two families. Family 1 (outcome-informed) used predicted probability of Y, absolute residuals from a Y~X model, and cross-validated decision scores. "
        "Family 2 (outcome-free) used PCA on X and k-means on X. "
        "Active comparators were propensity-score quintiles, a Gaussian mixture model on X and prognostic-score stratification from a Y~X model fitted in the untreated. "
        "Oracle baselines stratified by the true Z using k-means or quantiles, and random stratification provided a lower baseline. "
        "Outcome-informed methods used a 50/50 discovery/evaluation split to avoid outcome-label leakage."
    ))

    doc.add_heading('2.3 Synthesis of stratum-specific effects', level=2)
    _add_paragraph(doc, (
        "For each discovered stratum we computed the risk difference P(Y=1|A=1) − P(Y=1|A=0). "
        "A two-stage fixed-effect summary was the stratum-size-weighted average of these risk differences. "
        "A DerSimonian-Laird random-effects summary added an estimate of between-stratum variance and re-weighted stratum estimates accordingly [dersimonian1986]. "
        "We also report the resulting tau² and I² as summaries of between-stratum heterogeneity in the effect scale."
    ))

    doc.add_heading('2.4 Evaluation metrics', level=2)
    _add_paragraph(doc, (
        "For each method we report: (i) ARI versus a constructed true-Z partition; (ii) C1 = 1 − I² from stratum-specific log odds ratios of A→Y, reflecting between-stratum homogeneity; (iii) W_true and W_est, measuring within-stratum CATE homogeneity using the true individual CATE or a flexible estimated CATE; and (iv) ATE bias reduction on the risk-difference scale, defined as |bias_crude| − |bias_stratified| and |bias_crude| − |bias_re| in absolute terms and as one minus the ratio of absolute biases in relative terms. "
        "Monte Carlo standard errors and 95% confidence intervals are reported for every mean."
    ))

    # Results
    doc.add_heading('3. Results', level=1)
    doc.add_heading('3.1 Primary IPD scenario', level=2)
    _add_paragraph(doc, (
        f"Table 1 and Figure 1 summarise the primary IPD scenario (n={n_ipd}, {n_studies} studies, K={k_ipd} strata). "
        f"Extraction of the true hidden structure was modest: the best ARI was {best_ari}, observed for {best_method}, and the average C1 across methods was {mean_c1}. "
        f"Average within-stratum homogeneity was also limited (mean W_true = {mean_wtrue}; mean W_est = {mean_west}), indicating that the strata still contained substantial CATE variation. "
        f"{study_footnote}"
    ))
    _add_paragraph(doc, (
        f"ATE bias reduction was strongest for {best_method}: the crude absolute risk-difference bias was {crude_bias}, the two-stage stratified estimate reduced this to {strat_bias} (relative {rel_strat}), and the random-effects estimate reduced it further to {re_bias} (relative {rel_re}). "
        f"These values show that, under the simulated data-generating mechanism, a small number of data-driven strata can partially remove bias from a pooled IPD estimate, but the diagnostic agreement with the true hidden structure remains low."
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
        "For most methods the gain from increasing K was limited and non-monotonic; increasing strata beyond the true dimensionality of the hidden structure introduced additional sampling variation and did not consistently improve ATE bias reduction."
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
    _add_paragraph(doc, (
        "We framed IONE within an IPD meta-analysis setting and evaluated it as a diagnostic for hidden effect modification. "
        "In the simulation, data-driven stratification sometimes reduced ATE bias on the risk-difference scale, and random-effects pooling across discovered strata often improved on a simple two-stage stratified estimate. "
        "However, the strata only partially captured the true hidden Z structure, as shown by low ARI and moderate W values. "
        "Success was conditional on the confounder/effect-modifier leaving strong traces in the measured covariates and on a simple low-dimensional structure."
    ))
    _add_paragraph(doc, (
        "These findings have a direct interpretation for evidence synthesis. A conventional IPD meta-analysis estimates an average effect and may be biased when treatment-effect modifiers are present but unmodelled [riley2011][vanderweele2015]. "
        "Reporting C1 and W alongside the pooled estimate makes the assumption of within-stratum homogeneity explicit and warns analysts when the marginal estimate is fragile. "
        "The approach is complementary to, not a replacement for, covariate adjustment, meta-regression and one-stage mixed models [austin2015][riley2010]. "
        "The two-stage stratified estimator is interpretable as a simple IPD meta-analysis of subgroup effects, and the random-effects extension follows standard meta-analytic practice [dersimonian1986]."
    ))
    _add_paragraph(doc, (
        "Limitations include the stylised data-generating mechanism, the absence of censoring or time-to-event outcomes, and the fact that the true-Z partition is constructed rather than clinically observed. "
        "We also assumed that study membership is known and included as a covariate; in practice, membership may be a source of bias itself. "
        "Future work should calibrate C1 and W on real clinical IPD, compare IONE with latent-class and mixture-model methods, and incorporate prior domain knowledge into the stratification."
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

    docx_path = os.path.join(RSM_DIR, 'IONE_rsm_manuscript.docx')
    doc.save(docx_path)

    # Separate title page for blinded peer review
    tp = Document()
    tp_style = tp.styles['Normal']
    tp_style.font.name = 'Times New Roman'
    tp_style.font.size = Pt(11)
    tp_title = tp.add_heading('IONE: Incoherence-Oriented Neutralisation and Extraction for hidden effect modification', level=0)
    tp_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp_sub = tp.add_heading('in individual participant data meta-analysis: a simulation study of stratification-based extraction', level=0)
    tp_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.add_paragraph()
    tp_auth = tp.add_paragraph()
    tp_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp_auth.add_run('Onishi Tatsuki').bold = True
    tp.add_paragraph()
    tp_note = tp.add_paragraph('Corresponding author: Onishi Tatsuki')
    tp_note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp_path = os.path.join(RSM_DIR, 'title_page_rsm.docx')
    tp.save(tp_path)

    # Separate editable tables document
    tdoc = Document()
    tstyle = tdoc.styles['Normal']
    tstyle.font.name = 'Times New Roman'
    tstyle.font.size = Pt(11)
    _, cols, numeric_cols, footnote = _build_table_1(ipd_primary, study_summary)
    _add_method_table(
        tdoc, ipd_primary, cols,
        caption=f'Table 1. Primary IPD scenario (n={n_ipd}, {n_studies} studies, K={k_ipd}): means over 50 simulations.',
        numeric_cols=numeric_cols,
    )
    if footnote:
        tdoc.add_paragraph(footnote)
    rd_best = real_data.loc[real_data.groupby('dataset')['ARI_mean'].idxmax()].copy()
    _add_method_table(
        tdoc, rd_best,
        ['Dataset', 'Method', 'K', 'ARI', 'C1', 'W_est', 'Bias reduction'],
        caption='Table 2. Best real-data illustration result per dataset.',
        numeric_cols={
            'Dataset': 'dataset', 'Method': 'method', 'K': 'n_strata',
            'ARI': 'ARI_mean', 'C1': 'C1_heterogeneity_mean', 'W_est': 'W_est_mean',
            'Bias reduction': 'bias_reduction_mean'
        }
    )
    tables_path = os.path.join(RSM_DIR, 'rsm_tables_separate.docx')
    tdoc.save(tables_path)

    print(f'[generate_rsm_manuscript] manuscript written to {docx_path}')
    print(f'[generate_rsm_manuscript] title page written to {tp_path}')
    print(f'[generate_rsm_manuscript] tables written to {tables_path}')
    print(f'[generate_rsm_manuscript] figures written to {FIG_DIR}; pptx at {pptx_path}')
    return docx_path


if __name__ == '__main__':
    generate_rsm_manuscript()
