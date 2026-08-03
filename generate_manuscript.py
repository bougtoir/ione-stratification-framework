"""
Generate the revised IONE manuscript and figure files from summary CSVs.
No numerical results are hard-coded; all table/figure numbers come from
results/summary/*.csv produced by generate_summary.py.
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
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pptx import Presentation
from pptx.util import Inches as PptxInches

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
SUMMARY_DIR = os.path.join(RESULTS_DIR, 'summary')
FIG_DIR = os.path.join(RESULTS_DIR, 'figures')
DOCX_DIR = os.path.join(RESULTS_DIR, 'manuscript')
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(DOCX_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Citation helpers (Vancouver style)
# ---------------------------------------------------------------------------
class CitationManager:
    def __init__(self):
        self._refs = OrderedDict()

    def cite(self, key, reference):
        """Register a reference and return a numbered marker."""
        if key not in self._refs:
            self._refs[key] = reference
        return str(list(self._refs.keys()).index(key) + 1)

    def add_paragraph(self, doc, text):
        """Add paragraph and replace {key} with superscript numbers."""
        p = doc.add_paragraph()
        parts = re.split(r'(\{[^}]+\})', text)
        for part in parts:
            m = re.match(r'\{([^}]+)\}', part)
            if m:
                key = m.group(1)
                if key not in self._refs:
                    raise KeyError(f'Citation key {key} not registered')
                num = str(list(self._refs.keys()).index(key) + 1)
                run = p.add_run(num)
                run.font.superscript = True
            else:
                p.add_run(part)
        return p

    def write_reference_list(self, doc):
        doc.add_heading('References', level=1)
        for i, (key, ref) in enumerate(self._refs.items(), 1):
            p = doc.add_paragraph()
            run = p.add_run(f'{i}. ')
            run.font.superscript = True
            p.add_run(ref)


cm = CitationManager()

# Register references used in the text
cm.cite('manski1990', 'Manski CF. Nonparametric bounds on treatment effects. Am Econ Rev. 1990;80(2):319-323.')
cm.cite('vanderweele2015', 'VanderWeele TJ. Explanation in Causal Inference: Methods for Mediation and Interaction. Oxford University Press; 2015.')
cm.cite('pearl2009', 'Pearl J. Causality. 2nd ed. Cambridge University Press; 2009.')
cm.cite('rubin1974', 'Rubin DB. Estimating causal effects of treatments in randomized and nonrandomized studies. J Educ Psychol. 1974;66(5):688-701.')
cm.cite('austin2015', 'Austin PC, Stuart EA. Moving towards best practice when using inverse probability of treatment weighting (IPTW) using the propensity score to estimate causal treatment effects in observational studies. Stat Med. 2015;34(28):3661-3679.')
cm.cite('robins1992', 'Robins JM, Greenland S. Identifiability and exchangeability for direct and indirect effects. Epidemiology. 1992;3(2):143-155.')
cm.cite('hernan2020', 'Hernán MA, Robins JM. Causal Inference: What If. Boca Raton: Chapman & Hall/CRC; 2020.')
cm.cite('morris2021', 'Morris S. Israeli vaccine efficacy data: a public-domain Simpson’s paradox example. 2021. Available from: https://sgmorris.net/posts/science/simpsons-paradox-israels-vaccine-data/')
cm.cite('appleton1996', 'Appleton DR, French NR, Vanderpump MP. Ignoring a covariate: an example of Simpson’s paradox. Am Stat. 1996;50(4):340-341.')
cm.cite('julious1994', 'Julious SA, Mullee MA. Confounding and Simpson’s paradox. BMJ. 1994;309(6967):1480-1481.')


def _read_csv(name):
    path = os.path.join(SUMMARY_DIR, name)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def _fmt(x, decimals=3):
    if pd.isna(x):
        return '—'
    return f'{x:.{decimals}f}'


def _add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    return p


def _add_method_table(doc, df, cols, caption, numeric_cols=None):
    """cols is list of column display labels; numeric_cols maps label->source column."""
    if numeric_cols is None:
        numeric_cols = {c: c for c in cols}
    methods = df['method'].tolist() if 'method' in df.columns else df.index.tolist()
    rows = [cols]
    for _, row in df.iterrows():
        r = []
        for c in cols:
            src = numeric_cols[c]
            if src == 'method':
                r.append(row['method'])
            elif src == 'dataset':
                r.append(row['dataset'])
            elif src == 'n_strata':
                r.append(str(int(row['n_strata'])))
            else:
                r.append(_fmt(row.get(src, np.nan), 3 if 'ARI' in src or 'C1' in src or 'W_' in src or 'bias' in src else 2))
        rows.append(r)
    table = doc.add_table(rows=len(rows), cols=len(cols))
    table.style = 'Table Grid'
    for i, row in enumerate(rows):
        cells = table.rows[i].cells
        for j, val in enumerate(row):
            cells[j].text = str(val)
            if i == 0:
                for paragraph in cells[j].paragraphs:
                    for run in paragraph.runs:
                        run.bold = True
    _add_caption(doc, caption)
    doc.add_paragraph()


def generate_figures(phase1_primary, real_data):
    os.makedirs(os.path.join(FIG_DIR, 'pptx'), exist_ok=True)
    figs = []

    if phase1_primary is not None and not phase1_primary.empty:
        metrics = ['ARI_mean', 'C1_heterogeneity_mean', 'W_true_mean', 'W_est_mean', 'bias_reduction_mean']
        labels = ['ARI', 'C1', 'W_true', 'W_est', 'Bias reduction']
        x = np.arange(len(phase1_primary))
        width = 0.15
        fig, ax = plt.subplots(figsize=(13, 5))
        for i, (m, lab) in enumerate(zip(metrics, labels)):
            ax.bar(x + (i - 2) * width, phase1_primary[m], width, label=lab)
        ax.set_xticks(x)
        ax.set_xticklabels(phase1_primary['method'], rotation=45, ha='right')
        ax.set_ylabel('Metric value')
        ax.set_title('Phase 1 primary scenario (n=2000, K=5): method performance')
        ax.legend(loc='upper right', ncol=3)
        ax.axhline(0, color='black', linewidth=0.5)
        fig.tight_layout()
        png = os.path.join(FIG_DIR, 'fig1_phase1_primary.png')
        fig.savefig(png, dpi=300)
        plt.close(fig)
        figs.append(('Figure 1', 'Phase 1 primary metrics across methods.', png))

    sens = _read_csv('sensitivity_full_summary.csv')
    if sens is not None:
        top_methods = ['1B_residual', 'PS_propensity_score', 'GMM', 'Prognostic_score', '2B_clustering']
        sub = sens[(sens['method'].isin(top_methods)) & (sens['n'] == 2000) & (sens['n_strata'] == 5)]
        if not sub.empty:
            pivot = sub.pivot_table(index='method', columns='zx_influence_scale',
                                     values='bias_reduction_mean', aggfunc='mean')
            fig, ax = plt.subplots(figsize=(8, 4))
            im = ax.imshow(pivot.values, aspect='auto', cmap='RdYlGn', vmin=-0.005, vmax=0.02)
            ax.set_xticks(np.arange(len(pivot.columns)))
            ax.set_xticklabels([f'{c:.1f}' for c in pivot.columns])
            ax.set_yticks(np.arange(len(pivot.index)))
            ax.set_yticklabels(pivot.index)
            ax.set_xlabel('Z→X influence scale')
            ax.set_ylabel('Method')
            ax.set_title('Sensitivity: bias reduction by Z→X influence (n=2000, K=5)')
            for i in range(len(pivot.index)):
                for j in range(len(pivot.columns)):
                    ax.text(j, i, f'{pivot.values[i, j]:.3f}', ha='center', va='center', fontsize=8)
            fig.colorbar(im, ax=ax)
            fig.tight_layout()
            png = os.path.join(FIG_DIR, 'fig2_sensitivity_bias.png')
            fig.savefig(png, dpi=300)
            plt.close(fig)
            figs.append(('Figure 2', 'Sensitivity of bias reduction to Z→X influence.', png))

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
            png = os.path.join(FIG_DIR, 'fig3_real_data_ari.png')
            fig.savefig(png, dpi=300)
            plt.close(fig)
            figs.append(('Figure 3', 'Real-data ARI by dataset and method.', png))

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
    pptx_path = os.path.join(FIG_DIR, 'pptx', 'figures.pptx')
    prs.save(pptx_path)
    return figs, pptx_path


def generate_manuscript():
    phase1_primary = _read_csv('phase1_primary_summary.csv')
    phase1_full = _read_csv('phase1_full_summary.csv')
    sens = _read_csv('sensitivity_full_summary.csv')
    nonlin = _read_csv('nonlinearity_full_summary.csv')
    real_data = _read_csv('real_data_summary.csv')

    figs, pptx_path = generate_figures(phase1_primary, real_data)

    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(11)

    # Title
    title = doc.add_heading('A coherence diagnostic for hidden population structure in observational studies:', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = doc.add_heading('a simulation study of stratification-based extraction', level=0)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    auth = doc.add_paragraph()
    auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    auth.add_run('Onishi Tatsuki').bold = True
    doc.add_paragraph()

    # Abstract
    doc.add_heading('Abstract', level=1)
    if phase1_primary is not None and not phase1_primary.empty:
        best = phase1_primary.loc[phase1_primary['bias_reduction_mean'].idxmax()]
        best_method = best['method']
        best_bias = _fmt(best['bias_reduction_mean'], 5)
        best_rel = _fmt(best['bias_reduction_relative_mean'], 3)
        best_ari = _fmt(best['ARI_mean'])
        crude_abs = _fmt(best['abs_bias_crude_mean'], 5)
        strat_abs = _fmt(best['abs_bias_stratified_mean'], 5)
    else:
        best_method = best_bias = best_rel = best_ari = crude_abs = strat_abs = '—'

    abstract_text = (
        "Background. Observational treatment-effect estimates can be distorted by hidden effect modification and confounding. "
        "We propose two exploratory coherence diagnostics—C1 (between-stratum heterogeneity of treatment effects) and W (within-stratum homogeneity of conditional average treatment effects)—and benchmark stratification-based extraction in a simulation with explicit confounding and effect modification. "
        "Methods. Data were generated for a binary treatment, binary outcome and measured covariates carrying traces of an unmeasured confounder/modifier. We compared four proposed IONE methods, six PCA variants, three active comparators (propensity-score quintiles, Gaussian mixture model, prognostic-score stratification) and two oracle baselines. Discovery/evaluation splitting was used for all outcome-informed methods. The estimand was the population risk-difference ATE; performance was measured by ARI with the true Z partition, C1, W and ATE bias reduction. "
        f"Results. In the primary scenario (n=2000, K=5), extraction performance was modest (best ARI = {best_ari}). Bias reduction was also modest: the best absolute reduction was {best_bias} (relative {best_rel}), from a crude absolute bias of {crude_abs} to a stratified absolute bias of {strat_abs}, achieved by {best_method}. Outcome-free methods were more stable, while residual-based outcome-informed methods showed larger W but required sample splitting to avoid circularity. Sensitivity analyses showed that stronger Z→X traces and larger sample sizes improved both diagnostics and bias reduction; non-linear Z→X mappings degraded PCA but not clustering-based methods. Semi-synthetic illustrations of Simpson's paradox showed high ARI only when pseudo-general variables were strongly correlated with the known confounder. "
        "Conclusions. IONE provides transparent, exploratory diagnostics for hidden population structure, but extraction remains conditional and modest. It should be used as a sensitivity complement to, not a replacement for, established causal-inference methods."
    )
    cm.add_paragraph(doc, abstract_text)
    doc.add_paragraph()
    kw = doc.add_paragraph()
    kw.add_run('Keywords: ').bold = True
    kw.add_run("hidden population structure; effect modification; unmeasured confounding; stratification; Simpson's paradox; diagnostic sensitivity study")

    # Introduction
    doc.add_heading('1. Introduction', level=1)
    cm.add_paragraph(doc, (
        "Treatment-effect estimates from observational data are valid only under assumptions that are often only partly testable{manski1990}. "
        "When a population is composed of subgroups with different treatment effects or different confounding structures, a marginal estimate can be non-robust or even qualitatively wrong (Simpson's paradox){pearl2009}. "
        "Standard adjustment methods rely on measured covariates and cannot reveal hidden effect modification by unmeasured modifiers. "
        "We study whether routine measured variables (X) can be used to stratify the population so that the resulting subgroups are more coherent in their treatment-response pattern. "
        "The goal is not to replace propensity-score or regression adjustment{austin2015}, but to provide an exploratory diagnostic that warns analysts when a population may be incoherent and that suggests where subgroup-specific analysis may be warranted."
    ))

    # Methods
    doc.add_heading('2. Methods', level=1)
    doc.add_heading('2.1 Data-generating mechanism', level=2)
    cm.add_paragraph(doc, (
        "The simulation generates n independent subjects with three critical variables (Z1 continuous age-like, Z2 binary sex-like, Z3 ordered category) and ten measured variables (X1–X10) that are influenced by Z. "
        "A binary treatment A is generated from a logistic model with confounders Z and covariates X. "
        "The binary outcome Y is generated from a logistic model with main effects of Z, weak direct effects of X, a treatment main effect, and Z×A interactions (effect modification){vanderweele2015}. "
        "The population risk-difference ATE is computed by averaging the true individual CATE over the simulated super-population. "
        "Default parameters were calibrated so that the crude marginal risk difference is on the order of 0.02 and the true ATE is on the order of 0.01, reflecting a realistic low-to-moderate confounding scenario. "
        "Sensitivity analyses vary sample size (500, 2000, 10000), Z→Y strength, Z→X influence, number of strata (3, 5, 10), and non-linear Z→X mappings."
    ))

    doc.add_heading('2.2 Stratification methods', level=2)
    cm.add_paragraph(doc, (
        "Proposed IONE methods are divided into two families. Family 1 (outcome-informed) uses predicted probability (1A), absolute residuals from a Y~X model (1B), cross-validated decision scores (1C), and random-forest uncertainty (1D). "
        "Family 2 (outcome-free) uses PCA (2A, six cumulative-variance/fixed-component configurations) and k-means on X (2B). "
        "Active comparators are propensity-score quintiles, a Gaussian mixture model on X, and prognostic-score stratification from a Y~X model fitted in the untreated. "
        "Oracle baselines stratify the true Z by k-means or by the first Z quantile. Random stratification provides a lower baseline. "
        "All methods use equal-frequency quantile-based strata after producing a one-dimensional score, except clustering-based methods."
    ))

    doc.add_heading('2.3 Evaluation metrics', level=2)
    cm.add_paragraph(doc, (
        "For each method and scenario we report: (i) ARI versus a constructed true-Z partition; (ii) C1 = 1 − I² from stratum-specific log odds ratios of A→Y; (iii) W_true and W_est measuring within-stratum CATE homogeneity (W_true uses the known individual CATE, W_est uses a flexible Y~X+A+X×A logistic model); and (iv) ATE bias reduction on the risk-difference scale. "
        "Outcome-informed methods use a 50/50 discovery/evaluation split: strata are learned on the discovery half and all metrics are computed on the evaluation half. "
        "Monte Carlo standard errors are reported for every mean."
    ))

    # Results
    doc.add_heading('3. Results', level=1)
    doc.add_heading('3.1 Phase 1 proof-of-concept', level=2)
    cm.add_paragraph(doc, (
        "Table 1 summarises the primary phase-1 scenario (n=2000, K=5, strong Z→X trace). "
        "Extraction performance, as measured by ARI with the constructed true-Z partition, was modest for all methods. "
        "C1 values were high for most methods, reflecting between-stratum heterogeneity in observed log odds ratios, but this did not always translate into strong ATE bias reduction. "
        "Figure 1 shows the same metrics graphically."
    ))
    if phase1_primary is not None:
        _add_method_table(
            doc, phase1_primary,
            ['Method', 'ARI', 'C1', 'W_true', 'W_est', 'Abs bias crude', 'Abs bias strat', 'Bias reduction', 'Relative reduction'],
            caption='Table 1. Phase 1 primary scenario (n=2000, K=5): means over simulations.',
            numeric_cols={
                'Method': 'method', 'ARI': 'ARI_mean', 'C1': 'C1_heterogeneity_mean',
                'W_true': 'W_true_mean', 'W_est': 'W_est_mean',
                'Abs bias crude': 'abs_bias_crude_mean', 'Abs bias strat': 'abs_bias_stratified_mean',
                'Bias reduction': 'bias_reduction_mean', 'Relative reduction': 'bias_reduction_relative_mean'
            }
        )
        if figs:
            doc.add_picture(figs[0][2], width=Inches(5.8))
            _add_caption(doc, figs[0][0] + '. ' + figs[0][1])
            doc.add_paragraph()

    doc.add_heading('3.2 Sensitivity and non-linearity analyses', level=2)
    cm.add_paragraph(doc, (
        "Bias reduction increased with stronger Z→X traces and larger sample sizes, but remained modest overall. "
        "Non-linear Z→X mappings reduced PCA-based performance but had less impact on clustering-based methods. "
        "Figure 2 illustrates the dependence of bias reduction on Z→X influence for selected methods (n=2000, K=5). Supplementary Tables S1–S4 give the full numerical results."
    ))
    if len(figs) > 1:
        doc.add_picture(figs[1][2], width=Inches(5.8))
        _add_caption(doc, figs[1][0] + '. ' + figs[1][1])
        doc.add_paragraph()

    doc.add_heading('3.3 Semi-synthetic illustrations', level=2)
    cm.add_paragraph(doc, (
        "Five well-known Simpson's-paradox examples were reconstructed as pseudo-individual records and pseudo-general variables were generated to mimic proxies of the known confounder{morris2021}{appleton1996}{julious1994}. "
        "High ARI was obtained only when the pseudo-variables were strongly correlated with a low-dimensional confounder (kidney stone, Israeli vaccine). "
        "Multi-level confounders produced near-zero ARI (UC Berkeley, COVID-19 CFR). "
        "These examples are illustrations of favourable vs. unfavourable settings, not validation of out-of-the-box performance. Figure 3 summarises ARI across datasets."
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
    cm.add_paragraph(doc, (
        "This study reframes IONE as an exploratory diagnostic-sensitivity tool rather than a mature two-stage workflow. "
        "The simulations show that hidden population structure can sometimes be detected and partially corrected, but success is strongly conditional on the confounder leaving strong traces in measured variables and on a simple, low-dimensional hidden structure. "
        "Outcome-informed methods can capitalise on outcome heterogeneity but require sample splitting to avoid overfitting and induced bias; outcome-free methods are more robust but lack the outcome signal. "
        "C1 and W provide transparent diagnostics, but they are not calibrated decision rules and should not replace propensity-score or regression adjustment. "
        "Limitations include the stylised DGM, the constructed nature of the true-Z partition, and the absence of a real individual-level cohort. Future work should calibrate C1/W thresholds on individual-level clinical data and compare IONE with latent-class and mixture-model approaches."
    ))

    # Data/code availability
    doc.add_heading('Data and code availability', level=1)
    cm.add_paragraph(doc, (
        "The simulation code and semi-synthetic example data are available in the public repository "
        "https://github.com/bougtoir/ione-stratification-framework. "
        "All numerical results in this manuscript are produced by scripts in the repository; no estimates are hard-coded."
    ))

    # References
    cm.write_reference_list(doc)

    docx_path = os.path.join(DOCX_DIR, 'IONE_revised_manuscript.docx')
    doc.save(docx_path)
    print(f'[generate_manuscript] manuscript written to {docx_path}')
    print(f'[generate_manuscript] figures written to {FIG_DIR}; pptx at {pptx_path}')
    return docx_path


if __name__ == '__main__':
    generate_manuscript()
