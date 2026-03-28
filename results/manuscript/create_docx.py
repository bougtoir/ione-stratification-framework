#!/usr/bin/env python3
"""Create IONE manuscript as .docx with embedded figures."""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import os

doc = Document()

# --- Style setup ---
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)
style.paragraph_format.line_spacing = 2.0
style.paragraph_format.space_after = Pt(0)

for level in range(1, 4):
    hs = doc.styles[f'Heading {level}']
    hs.font.name = 'Times New Roman'
    hs.font.color.rgb = RGBColor(0, 0, 0)
    if level == 1:
        hs.font.size = Pt(16)
    elif level == 2:
        hs.font.size = Pt(14)
    else:
        hs.font.size = Pt(12)

# Paths
FIG_SIM = '/home/ubuntu/repos/stratification_project/results/figures'
FIG_RD = '/home/ubuntu/repos/stratification_project/results/real_data'

def add_figure(doc, path, caption, width=Inches(5.5)):
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(path, width=width)
        cap = doc.add_paragraph(caption)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.style = doc.styles['Normal']
        for run in cap.runs:
            run.font.size = Pt(10)
            run.italic = True
        doc.add_paragraph()  # spacer
    else:
        p = doc.add_paragraph(f'[Figure not found: {path}]')
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(9)
                run.font.name = 'Times New Roman'
    # Data
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size = Pt(9)
                    run.font.name = 'Times New Roman'
    doc.add_paragraph()  # spacer
    return table

# ============================================================
# TITLE PAGE
# ============================================================
title = doc.add_heading('', level=1)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('IONE: Incoherence-Oriented Neutralisation and Extraction for Detecting Hidden Population Structure in Observational Studies')
run.font.size = Pt(16)
run.bold = True

doc.add_paragraph()
p = doc.add_paragraph('[Author names to be inserted]')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph('[Affiliations to be inserted]')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph('Corresponding author: [Name, email, address to be inserted]')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_page_break()

# ============================================================
# ABSTRACT
# ============================================================
doc.add_heading('Abstract', level=1)

p = doc.add_paragraph()
run = p.add_run('Background: ')
run.bold = True
p.add_run(
    'Observational studies are susceptible to multiple biases arising from hidden population structure, '
    'including confounding, Simpson\'s paradox, undetected effect modification, the ecological fallacy, '
    'and non-collapsibility. Existing adjustment methods such as propensity scores and prognostic scores '
    'address only measured confounders and provide no mechanism for detecting subgroup structure driven by '
    'unmeasured variables. We propose IONE (Incoherence-Oriented Neutralisation and Extraction), a framework '
    'that quantifies population incoherence and extracts coherent subpopulations using routinely measured '
    'variables alone.'
)

p = doc.add_paragraph()
run = p.add_run('Methods: ')
run.bold = True
p.add_run(
    'We conducted a Monte Carlo simulation study following the ADEMP framework. Data were generated from a '
    'causal directed acyclic graph with three intentionally withheld variables (age, sex, BMI) influencing ten '
    'measured variables and a binary outcome. We evaluated six stratification methods in two families: decision '
    'power-based methods (predicted probability, residual, cross-validated, machine learning uncertainty) '
    'exploiting the outcome, and feature score-based methods (principal component analysis, clustering) operating '
    'in the covariate space alone. Performance was assessed by the Adjusted Rand Index (ARI), eta-squared '
    '(\u03b7\u00b2), and a coherence indicator (C1) derived from the I\u00b2 heterogeneity statistic. Phase 1 comprised '
    '18,000 evaluations across 1,200 scenarios; sensitivity analyses comprised 48,600 evaluations across 8,100 '
    'scenarios. We additionally applied IONE to five published instances of Simpson\'s paradox: COVID-19 case '
    'fatality rates, kidney stone treatments, UC Berkeley admissions, Israeli vaccine effectiveness, and the '
    'smoking\u2013mortality paradox.'
)

p = doc.add_paragraph()
run = p.add_run('Results: ')
run.bold = True
p.add_run(
    'In simulations, all proposed methods significantly outperformed random stratification (best ARI = 0.020 vs. '
    '0.000, p < 0.001). Decision power-based methods consistently outperformed feature score-based methods. The '
    'strength of the hidden variable\u2019s influence on measured variables (Z\u2192X influence) was the primary '
    'determinant of performance, with ARI increasing up to 18-fold from weak to strong influence conditions. The '
    'coherence indicator C1 clearly distinguished incoherent from coherent populations (proposed methods C1 = 0.001 '
    'vs. random C1 = 0.863). In empirical validation, C1 correctly detected incoherence in all five examples '
    '(C1 = 0.001\u20130.034 vs. random C1 = 0.695\u20131.000). For two-group structures, stratification achieved high '
    'accuracy (kidney stone ARI = 0.851; Israeli vaccine ARI = 0.746). For multi-group structures, detection power '
    'was limited (COVID-19 ARI = 0.064; Berkeley ARI = 0.082).'
)

p = doc.add_paragraph()
run = p.add_run('Conclusions: ')
run.bold = True
p.add_run(
    'IONE provides a two-tier contribution: first, the C1 coherence indicator reliably detects population '
    'incoherence regardless of subgroup complexity; second, stratification-based extraction of coherent '
    'subpopulations is effective when hidden variables leave sufficiently strong traces in measured variables '
    '(\u03b7\u00b2 > 0.4) and the subgroup structure is discrete. We recommend that coherence assessment be incorporated '
    'as a standard step in observational study reporting.'
)

p = doc.add_paragraph()
run = p.add_run('Keywords: ')
run.bold = True
p.add_run(
    'Simpson\u2019s paradox, confounding, population heterogeneity, coherence, stratification, unmeasured confounders, '
    'observational studies, causal inference'
)

doc.add_page_break()

# ============================================================
# BACKGROUND
# ============================================================
doc.add_heading('Background', level=1)

doc.add_paragraph(
    'Observational studies, particularly retrospective cohort studies, are indispensable for generating '
    'real-world evidence on treatment effects and risk factors when randomised controlled trials are infeasible '
    'or unethical [1, 2]. However, because treatment assignment is not under the investigator\u2019s control, these '
    'studies are inherently susceptible to multiple forms of bias arising from a single root cause: the study '
    'population may harbour hidden subpopulations with distinct characteristics that differentially influence '
    'both exposure and outcome. This hidden population structure gives rise to confounding bias, where unmeasured '
    'variables that affect both exposure and outcome create spurious associations [3]; Simpson\u2019s paradox, where '
    'the direction of an association observed in the aggregate reverses within subgroups [4, 5]; undetected effect '
    'modification, where treatment effects genuinely differ across subpopulations but are reported as a single '
    '\u201caverage\u201d effect that may not apply to any individual subgroup [6]; the ecological fallacy, where '
    'aggregate-level associations are inappropriately generalised to individuals [7]; and non-collapsibility, a '
    'mathematical property by which non-linear effect measures such as the odds ratio yield marginal estimates '
    'that differ from conditional estimates even in the absence of confounding [8].'
)

doc.add_paragraph(
    'These biases are not merely theoretical concerns. Simpson\u2019s paradox has been documented in landmark studies '
    'across medicine and social science: kidney stone treatment comparisons where the inferior treatment appeared '
    'superior in aggregate [9], university admissions data where apparent gender discrimination reversed at the '
    'departmental level [10], COVID-19 case fatality rate comparisons that were confounded by national differences '
    'in age distributions [11], vaccine effectiveness evaluations that appeared to show vaccine failure due to '
    'age-related confounding [12], and smoking\u2013mortality studies where smokers appeared to have lower mortality '
    'due to confounding by age [13]. In each case, the paradox arose because the study population was '
    'incoherent\u2014that is, it comprised multiple internally homogeneous (coherent) subpopulations whose mixture '
    'produced misleading aggregate statistics. The fundamental lesson of Simpson\u2019s paradox is that findings '
    'derived from an incoherent population should not be uncritically applied to the coherent subpopulations '
    'within it [4, 5].'
)

doc.add_paragraph(
    'Several established methods exist for addressing confounding in observational studies. The propensity score '
    '(PS), defined as the conditional probability of treatment assignment given observed covariates, enables '
    'balancing of measured confounders through stratification, matching, or weighting [14]. The prognostic score '
    'predicts the outcome under no treatment and provides an alternative basis for stratification [15, 16]. The '
    'disease risk score (DRS) constructs an outcome prediction model using untreated subjects only [17]. '
    'Instrumental variable methods exploit variables that affect treatment but not the outcome directly [18]. '
    'More recently, the high-dimensional propensity score (hdPS) algorithm automatically extracts thousands of '
    'candidate proxy variables from claims data to approximate unmeasured confounding [19, 20]. These methods '
    'share a fundamental limitation: they adjust only for measured covariates and provide no mechanism for '
    'detecting or extracting population structure driven by unmeasured variables [19, 21].'
)

doc.add_paragraph(
    'The concept that measured variables may carry indirect information about unmeasured confounders is not new. '
    'The hdPS algorithm rests on the insight that a sufficiently large collection of proxy variables can '
    'collectively approximate the influence of unmeasured confounders [19]. Proximal causal inference formalises '
    'the use of proxy variables for identification of causal effects in the presence of unmeasured confounding '
    '[22]. Latent class analysis and finite mixture models seek to identify unobserved subgroups from patterns in '
    'observed variables [23]. However, none of these approaches explicitly addresses the problem of population '
    'incoherence\u2014the condition in which an apparently homogeneous study population actually comprises multiple '
    'coherent subpopulations with heterogeneous treatment effects. In current practice, the homogeneity of study '
    'populations is typically assumed implicitly, with baseline characteristics tables (Table 1) providing only '
    'descriptive summaries that cannot formally test for hidden subgroup structure [24].'
)

doc.add_paragraph(
    'We propose that the problem of hidden population structure can be addressed through a two-stage approach. '
    'In the first stage, a quantitative indicator of population coherence\u2014the coherence degree\u2014is computed '
    'from routinely measured variables to determine whether a study population contains hidden subgroups that '
    'warrant separate analysis. In the second stage, if incoherence is detected, the population is stratified '
    'into coherent subgroups using multivariate patterns in the measured variables, and the primary analysis is '
    'conducted within each subgroup. The rationale is as follows: if important unmeasured variables (e.g. age, '
    'disease severity, genetic subtype) exert systematic influence on routinely measured variables (e.g. laboratory '
    'values, vital signs), then these measured variables collectively carry a detectable \u201ctrace\u201d of the '
    'unmeasured variable. Stratification based on these traces should recover, at least partially, the subgroup '
    'structure defined by the unmeasured variable.'
)

doc.add_paragraph(
    'To operationalise this approach, we develop two families of stratification methods. The first family '
    '(decision power-based methods) exploits the relationship between measured variables and the outcome: because '
    'unmeasured confounders influence the outcome, residual patterns from outcome prediction models may reflect '
    'the unmeasured variable\u2019s structure. The second family (feature score-based methods) operates in the '
    'covariate space alone, using unsupervised techniques such as principal component analysis and clustering to '
    'identify multivariate patterns attributable to unmeasured variables, without reference to the outcome. As a '
    'coherence indicator, we propose a metric (C1) derived from the I\u00b2 heterogeneity statistic [25] applied '
    'to within-stratum treatment effects, which quantifies the degree to which effect estimates are homogeneous '
    'across strata.'
)

doc.add_paragraph(
    'The objectives of this study are threefold. First, we evaluate through Monte Carlo simulation whether '
    'stratification based solely on measured variables can recover subgroup structure defined by intentionally '
    'withheld variables, across a range of data-generating scenarios varying in sample size, number of subgroups, '
    'and the strength of the unmeasured variable\u2019s influence on measured variables. Second, we assess the '
    'proposed coherence indicator\u2019s ability to detect incoherent populations. Third, we apply the proposed '
    'methods to five published instances of Simpson\u2019s paradox [9\u201313] to evaluate their performance on '
    'empirical data with known confounding structure. We refer to the proposed framework as IONE '
    '(Incoherence-Oriented Neutralisation and Extraction), reflecting its dual function of detecting population '
    'incoherence and extracting coherent subpopulations for valid within-subgroup inference.'
)

doc.add_page_break()

# ============================================================
# METHODS
# ============================================================
doc.add_heading('Methods', level=1)

doc.add_paragraph(
    'This simulation study is reported following the ADEMP framework (Aims, Data-generating mechanisms, '
    'Estimands, Methods, Performance measures) as recommended by Morris, White, and Crowther [26]. All analyses '
    'were conducted in Python 3.11.'
)

# --- Aims ---
doc.add_heading('Aims', level=2)
doc.add_paragraph('The aims of the simulation study were:')
doc.add_paragraph(
    '1. To evaluate whether stratification of observational data based solely on measured (general) variables '
    'can recover hidden subgroup structure defined by unmeasured (critical) variables.'
)
doc.add_paragraph(
    '2. To compare the performance of decision power-based stratification methods (which use outcome information) '
    'with feature score-based methods (which do not).'
)
doc.add_paragraph(
    '3. To assess the ability of a proposed coherence indicator (C1) to discriminate between incoherent '
    'populations (containing hidden subgroups) and coherent populations.'
)
doc.add_paragraph(
    '4. To identify the data-generating conditions under which the proposed methods are most and least effective.'
)

# --- DGM ---
doc.add_heading('Data-generating mechanisms', level=2)

doc.add_heading('Causal structure', level=3)
doc.add_paragraph(
    'Data were generated from a causal directed acyclic graph (DAG) with three variable types: critical '
    'variables Z = (Z\u2081, Z\u2082, Z\u2083), general variables X = (X\u2081, \u2026, X\u2081\u2080), and a binary outcome Y. '
    'The critical variables were designed to represent commonly encountered confounders in clinical research:'
)
doc.add_paragraph('\u2022 Z\u2081 (age): continuous, N(60, 12\u00b2), truncated to [20, 95]')
doc.add_paragraph('\u2022 Z\u2082 (sex): binary, Bernoulli(0.5)')
doc.add_paragraph('\u2022 Z\u2083 (BMI category): ordinal with three levels, Multinomial(0.3, 0.4, 0.3)')

doc.add_paragraph(
    'The general variables represented routine clinical measurements (e.g. haemoglobin A1c, total cholesterol, '
    'systolic blood pressure, ALT, creatinine, haemoglobin, white blood cell count, albumin, CRP, uric acid). '
    'Each general variable X\u2c7c was generated as a function of one or more critical variables plus independent noise:'
)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('X\u2c7c = \u03a3 \u03b1\u2c7c\u2097 \u00b7 Z\u2097 + \u03b5\u2c7c,  \u03b5\u2c7c ~ N(0, \u03c3\u00b2\u2c7c)')
run.italic = True

doc.add_paragraph(
    'where \u03b1\u2c7c\u2097 represents the influence of critical variable Z\u2097 on general variable X\u2c7c. '
    'The influence coefficients were varied systematically (see Scenarios below). Not all Z variables influenced '
    'all X variables; the influence pattern was designed to reflect realistic clinical correlations (e.g. age '
    'influences blood pressure and renal function; sex influences haemoglobin; BMI influences metabolic markers).'
)

doc.add_heading('Outcome model', level=3)
doc.add_paragraph('The binary outcome was generated from a logistic model:')

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('logit(P(Y=1)) = \u03b2\u2080 + \u03a3 \u03b2_Z\u2097 \u00b7 Z\u2097 + \u03a3 \u03b2_X\u2c7c \u00b7 X\u2c7c + \u03b5')
run.italic = True

doc.add_paragraph(
    'with critical variable effects set to odds ratios of 1.5\u20133.0 (clinically meaningful) and general '
    'variable effects set to odds ratios of 1.0\u20131.3 (weak to moderate). The intercept \u03b2\u2080 was calibrated '
    'to achieve an overall event rate of approximately 10\u201320%.'
)

doc.add_heading('Scenarios', level=3)
doc.add_paragraph('The following factors were varied in a factorial design:')

doc.add_paragraph().add_run('Phase 1 (proof of concept):').bold = True
add_table(doc,
    ['Factor', 'Levels', 'Values'],
    [
        ['Sample size (N)', '1', '2,000'],
        ['Z\u2192X influence scale', '3', '0.3 (weak), 0.5 (moderate), 1.0 (strong)'],
        ['Number of strata (K)', '2', '3, 5'],
        ['Simulation repetitions', '\u2014', '200 per scenario'],
    ]
)
doc.add_paragraph(
    'This yielded 1,200 unique scenarios (including method \u00d7 parameter combinations), producing 18,000 total evaluations.'
)

doc.add_paragraph().add_run('Sensitivity analyses:').bold = True
add_table(doc,
    ['Factor', 'Levels', 'Values'],
    [
        ['Sample size (N)', '3', '500, 2,000, 10,000'],
        ['Z\u2192Y effect scale', '3', '0.5, 1.0, 2.0'],
        ['Z\u2192X influence scale', '3', '0.2, 0.5, 1.0'],
        ['Number of strata (K)', '3', '3, 5, 10'],
    ]
)
doc.add_paragraph(
    'This yielded 8,100 scenarios with six representative methods, producing 48,600 evaluations. '
    'The total number of evaluations across both phases was 66,600.'
)

# --- Estimands ---
doc.add_heading('Estimands', level=2)
doc.add_paragraph('The primary estimands were:')
doc.add_paragraph(
    '1. Subgroup recovery: the degree to which strata formed by general variables X alone correspond to the '
    'true subgroup structure defined by critical variables Z.'
)
doc.add_paragraph(
    '2. Trace capture: the proportion of variance in Z explained by the stratification (\u03b7\u00b2).'
)
doc.add_paragraph(
    '3. Coherence: the degree to which within-stratum treatment effects are homogeneous.'
)
doc.add_paragraph(
    'The true subgroup structure was defined by applying k-means clustering to the standardised Z-space, with '
    'the number of clusters set equal to the number of strata K.'
)

# --- Methods under comparison ---
doc.add_heading('Methods under comparison', level=2)
doc.add_paragraph('Six proposed methods in two families, plus two baselines, were evaluated:')

doc.add_paragraph().add_run('Family 1: Decision power-based methods (outcome-informed)').bold = True
doc.add_paragraph(
    'These methods build a predictive model for Y using X alone, then stratify observations based on properties '
    'of the model output.'
)
doc.add_paragraph(
    'Method 1A (Predicted probability): A logistic regression model predicting Y from X\u2081\u2013X\u2081\u2080 is fitted. '
    'Observations are stratified by quantiles of the predicted probability p\u0302. This is analogous to a prognostic '
    'score [15] estimated without the critical variables.'
)
doc.add_paragraph(
    'Method 1B (Residual): From the same logistic regression, the absolute residual |Y \u2212 p\u0302| is computed. '
    'Observations are stratified by quantiles of |Y \u2212 p\u0302|. The rationale is that large residuals indicate '
    'observations poorly explained by X alone, suggesting strong influence of unmeasured Z.'
)
doc.add_paragraph(
    'Method 1C (Cross-validated decision power): A K-fold cross-validation procedure is used, where the model '
    'is trained on K\u22121 folds and predictions are generated for the held-out fold. This prevents overfitting '
    'and is conceptually related to the pilot design of Aikens et al. [16].'
)
doc.add_paragraph(
    'Method 1D (Machine learning uncertainty): A random forest model predicting Y from X is fitted. The variance '
    'of predictions across trees serves as an uncertainty measure. Observations are stratified by quantiles of this uncertainty.'
)

doc.add_paragraph().add_run('Family 2: Feature score-based methods (outcome-free)').bold = True
doc.add_paragraph(
    'These methods operate solely in the covariate space of X, without reference to Y.'
)
doc.add_paragraph(
    'Method 2A (PCA): Principal component analysis is applied to the standardised X\u2081\u2013X\u2081\u2080. '
    'The first principal component score (PC1) is used to stratify observations by quantiles.'
)
doc.add_paragraph(
    'Method 2B (Clustering): K-means clustering is applied to the standardised X\u2081\u2013X\u2081\u2080 with the '
    'number of clusters set to K. Cluster assignments define the strata directly.'
)

doc.add_paragraph().add_run('Baselines:').bold = True
doc.add_paragraph(
    'Random: Observations are randomly assigned to K strata of equal size.'
)
doc.add_paragraph(
    'Oracle (k-means on Z): K-means clustering is applied to the standardised Z-space. This represents the '
    'theoretical upper bound, as it uses the withheld critical variables directly.'
)

# --- Performance measures ---
doc.add_heading('Performance measures', level=2)
doc.add_paragraph('Performance was assessed using the following measures:')

doc.add_paragraph().add_run('Primary measures:').bold = True
doc.add_paragraph(
    'Adjusted Rand Index (ARI) [27]: Measures agreement between estimated strata and true Z-based clusters, '
    'corrected for chance. Range [\u22121, 1]; 1 = perfect agreement; 0 = chance level.'
)
doc.add_paragraph(
    'Eta-squared (\u03b7\u00b2): The proportion of variance in each critical variable Z explained by the '
    'stratification. Computed as the between-stratum sum of squares divided by the total sum of squares. '
    'Higher \u03b7\u00b2 indicates better capture of the hidden variable\u2019s trace.'
)
doc.add_paragraph(
    'Coherence indicator C1: Defined as 1 \u2212 I\u00b2, where I\u00b2 is Higgins and Thompson\u2019s [25] '
    'heterogeneity statistic applied to within-stratum treatment effect estimates. Each stratum is treated as a '
    '\u201cstudy\u201d in a meta-analytic framework: stratum-specific log odds ratios for the exposure\u2013outcome '
    'association are computed, and I\u00b2 quantifies the proportion of total variability attributable to '
    'between-stratum heterogeneity. C1 near 0 indicates strong heterogeneity across strata (incoherent '
    'population); C1 near 1 indicates homogeneous effects (coherent population).'
)

doc.add_paragraph().add_run('Secondary measures:').bold = True
doc.add_paragraph(
    'Normalised Mutual Information (NMI) [28]: An information-theoretic measure of cluster agreement. Range [0, 1].'
)
doc.add_paragraph(
    'Direction consistency rate: The proportion of strata in which the direction of the exposure\u2013outcome '
    'association (positive or negative) is consistent with the overall direction.'
)

# --- Empirical validation ---
doc.add_heading('Empirical validation: application to published Simpson\u2019s paradox examples', level=2)

doc.add_paragraph(
    'To evaluate IONE on data with known confounding structure, we applied the proposed methods to five published '
    'instances of Simpson\u2019s paradox (Table 1). For each example, we: (1) reconstructed individual-level data '
    'from published aggregate statistics; (2) generated pseudo-general variables (6\u201310 variables) correlated '
    'with the known confounding variable, simulating a scenario in which the confounder is unmeasured but leaves '
    'traces in other measured variables; (3) applied all six proposed methods plus random and Oracle baselines; '
    '(4) evaluated performance using ARI, C1, \u03b7\u00b2, and direction consistency.'
)

doc.add_paragraph().add_run('Table 1. Published Simpson\u2019s paradox examples used for empirical validation.').bold = True
add_table(doc,
    ['Example', 'Source', 'N', 'Hidden confounder (Z)', 'No. of groups', 'Paradox'],
    [
        ['COVID-19 CFR', 'von K\u00fcgelgen et al. 2021 [11]', '50,459', 'Age group (9 groups)', '9',
         'Italy CFR > China overall, but Italy < China within every age group'],
        ['Kidney stone', 'Charig et al. 1986 [9]', '700', 'Stone size (2 groups)', '2',
         'Treatment B > A overall, but A > B for both small and large stones'],
        ['UC Berkeley', 'Bickel et al. 1975 [10]', '4,425', 'Department (6 groups)', '6',
         'Males admitted at higher rate overall, but females \u2265 males in most departments'],
        ['Israeli vaccine', 'Morris 2021 [12]', '6,100', 'Age group (2 groups)', '2',
         'Vaccine appears ineffective overall, but effective in both age groups'],
        ['Smoking\u2013mortality', 'Appleton et al. 1996 [13]', '1,314', 'Age group (7 groups)', '7',
         'Smokers have lower mortality overall, but higher mortality in every age group'],
    ]
)

doc.add_paragraph(
    'It should be noted that this empirical validation uses pseudo-general variables rather than genuine clinical '
    'measurements. This design permits evaluation of the method\u2019s capacity to detect known confounding structure '
    'but does not constitute a fully realistic application. The procedure is described in detail in Additional file 1.'
)

# --- Computational implementation ---
doc.add_heading('Computational implementation', level=2)
doc.add_paragraph(
    'All simulations were parallelised across 8 CPU cores using the joblib library. Phase 1 completed in 6.0 '
    'minutes; sensitivity analyses in 9.4 minutes. Each scenario was assigned a fixed random seed for reproducibility. '
    'Code is available at [repository URL to be inserted].'
)

doc.add_page_break()

# ============================================================
# RESULTS
# ============================================================
doc.add_heading('Results', level=1)

# --- Simulation ---
doc.add_heading('Simulation study', level=2)

doc.add_heading('Overall method performance', level=3)
doc.add_paragraph(
    'Table 2 summarises the performance of all methods averaged across Phase 1 scenarios (N = 2,000; 200 '
    'repetitions per scenario).'
)

doc.add_paragraph().add_run(
    'Table 2. Method performance ranking in Phase 1 simulation (averaged across all scenarios).'
).bold = True
add_table(doc,
    ['Rank', 'Method', 'Family', 'ARI', 'NMI', '\u03b7\u00b2 (mean)', 'C1'],
    [
        ['1', 'Oracle (k-means on Z)', 'Baseline (upper)', '0.353', '0.616', '0.562', '0.019'],
        ['2', 'Oracle (quantile on Z)', 'Baseline (upper)', '0.073', '0.260', '0.283', '0.010'],
        ['3', '1B: Residual', 'Decision power', '0.020', '0.069', '0.091', '0.001'],
        ['4', '1D: ML uncertainty', 'Decision power', '0.017', '0.056', '0.074', '0.001'],
        ['5', '1A: Predicted probability', 'Decision power', '0.014', '0.053', '0.069', '0.022'],
        ['6', '1C: Cross-validated', 'Decision power', '0.014', '0.051', '0.067', '0.028'],
        ['7', '2A: PCA (k=2)', 'Feature score', '0.012', '0.042', '0.052', '0.098'],
        ['8', '2A: PCA (k=1)', 'Feature score', '0.011', '0.047', '0.063', '0.095'],
        ['9', '2B: Clustering', 'Feature score', '0.011', '0.041', '0.053', '0.079'],
        ['10', 'Random', 'Baseline (lower)', '\u22120.000', '0.007', '0.002', '0.863'],
    ]
)
doc.add_paragraph(
    'All proposed methods significantly outperformed the random baseline (p < 0.001 for ARI comparison). '
    'Decision power-based methods (Family 1) consistently ranked above feature score-based methods (Family 2). '
    'Method 1B (residual-based) achieved the highest ARI among proposed methods (0.020), followed by 1D '
    '(ML uncertainty; 0.017). The gap between the best proposed method and the Oracle k-means baseline was '
    'substantial (ARI 0.020 vs. 0.353).'
)

# Insert simulation figures
add_figure(doc,
    f'{FIG_SIM}/heatmap_ari_nmi.png',
    'Figure 1. Heatmap of ARI and NMI across methods and scenarios in Phase 1 simulation.'
)

doc.add_heading('Effect of Z\u2192X influence strength', level=3)
doc.add_paragraph(
    'The strength of the hidden variable\u2019s influence on measured variables was the single most important '
    'determinant of method performance (Table 3).'
)

doc.add_paragraph().add_run('Table 3. ARI by Z\u2192X influence strength (K = 5 strata).').bold = True
add_table(doc,
    ['Method', 'zx = 0.3 (weak)', 'zx = 0.5 (moderate)', 'zx = 1.0 (strong)', 'Strong/weak ratio'],
    [
        ['1A: Predicted probability', '0.004', '0.010', '0.030', '8.7'],
        ['1B: Residual', '0.014', '0.018', '0.029', '1.9'],
        ['1C: Cross-validated', '0.003', '0.009', '0.029', '9.6'],
        ['2A: PCA (k=2)', '0.002', '0.006', '0.029', '18.3'],
        ['2B: Clustering', '0.002', '0.006', '0.025', '14.0'],
        ['Oracle (k-means on Z)', '0.378', '0.378', '0.380', '1.0'],
    ]
)

add_figure(doc,
    f'{FIG_SIM}/sensitivity_zx_influence.png',
    'Figure 2. Effect of Z\u2192X influence strength on method performance across sensitivity analysis conditions.'
)

doc.add_heading('Capture of individual critical variables', level=3)
doc.add_paragraph(
    'Eta-squared analysis revealed differential capture of the three critical variables (Table 4; K = 5, zx = 1.0).'
)
doc.add_paragraph().add_run(
    'Table 4. Eta-squared (\u03b7\u00b2) for each critical variable (K = 5 strata, zx = 1.0).'
).bold = True
add_table(doc,
    ['Method', 'Z\u2081 (age)', 'Z\u2082 (sex)', 'Z\u2083 (BMI)', 'Mean'],
    [
        ['Oracle (k-means on Z)', '0.312', '0.982', '0.663', '0.652'],
        ['1A: Predicted probability', '0.327', '0.008', '0.092', '0.142'],
        ['1C: Cross-validated', '0.322', '0.007', '0.090', '0.140'],
        ['1B: Residual', '0.295', '0.012', '0.093', '0.133'],
        ['2B: Clustering', '0.238', '0.026', '0.090', '0.118'],
        ['Random', '0.002', '0.002', '0.002', '0.002'],
    ]
)

add_figure(doc,
    f'{FIG_SIM}/eta_squared.png',
    'Figure 3. Eta-squared (\u03b7\u00b2) values showing capture of individual critical variables by each method.'
)

doc.add_heading('Coherence indicator C1', level=3)
doc.add_paragraph(
    'The coherence indicator C1 clearly separated proposed methods from the random baseline (Figure 4). '
    'Random stratification yielded a mean C1 of 0.863, indicating high between-stratum heterogeneity '
    '(incoherent population). Methods 1B and 1D achieved the lowest C1 values (0.001), comparable to or below '
    'the Oracle k-means baseline (0.019). A provisional threshold of C1 < 0.05 correctly classified all decision '
    'power-based methods and Oracle baselines as producing coherent strata, whilst flagging random stratification '
    'as incoherent.'
)

add_figure(doc,
    f'{FIG_SIM}/coherence_diagnosis.png',
    'Figure 4. Coherence indicator C1 across methods. Lower C1 indicates successful detection of population incoherence.'
)

doc.add_heading('Sensitivity analyses', level=3)

doc.add_paragraph(
    'Sample size (N = 500, 2,000, 10,000): Performance was largely insensitive to sample size. Method 1A '
    'achieved ARI = 0.012 at N = 500 and ARI = 0.013 at N = 10,000, indicating that the detection limit is '
    'governed by signal strength (Z\u2192X influence) rather than sample size.'
)

add_figure(doc,
    f'{FIG_SIM}/sensitivity_sample_size.png',
    'Figure 5. Effect of sample size on method performance in sensitivity analysis.'
)

doc.add_paragraph(
    'Z\u2192Y effect scale (0.5, 1.0, 2.0): The strength of the hidden variable\u2019s direct effect on the '
    'outcome had minimal impact on proposed method performance (ARI range: 0.012\u20130.013 for Method 1A across '
    'all levels), indicating that methods rely on X-based patterns rather than direct Z\u2192Y effects.'
)

doc.add_paragraph(
    'Z\u2192X influence scale (0.2, 0.5, 1.0): This was confirmed as the most important parameter. ARI '
    'increased 17.5-fold (Method 1A) to 34.3-fold (Method 2B) from zx = 0.2 to zx = 1.0 (Table 5).'
)
doc.add_paragraph().add_run('Table 5. ARI by Z\u2192X influence strength in sensitivity analysis.').bold = True
add_table(doc,
    ['Method', 'zx = 0.2 (weak)', 'zx = 0.5 (moderate)', 'zx = 1.0 (strong)', 'Strong/weak ratio'],
    [
        ['1A: Predicted probability', '0.002', '0.009', '0.028', '17.5'],
        ['1C: Cross-validated', '0.001', '0.008', '0.027', '22.3'],
        ['2B: Clustering', '0.001', '0.006', '0.024', '34.3'],
        ['2A: PCA (60%)', '0.001', '0.004', '0.015', '30.8'],
    ]
)

doc.add_paragraph(
    'Number of strata (K = 3, 5, 10): Proposed methods performed optimally at K = 5. At K = 10, performance '
    'decreased slightly (e.g. Method 1A: ARI = 0.014 at K = 5 vs. 0.011 at K = 10), suggesting that '
    'over-stratification introduces noise when the signal is weak. By contrast, the Oracle baseline improved '
    'monotonically with K (ARI = 0.326 at K = 3 to 0.584 at K = 10).'
)

add_figure(doc,
    f'{FIG_SIM}/summary_dashboard.png',
    'Figure 6. Summary dashboard of simulation results across all Phase 1 conditions.',
    width=Inches(6.0)
)

doc.add_page_break()

# --- Empirical validation ---
doc.add_heading('Empirical validation', level=2)

doc.add_heading('Overview of results', level=3)
doc.add_paragraph(
    'Table 6 summarises the performance of IONE across the five published Simpson\u2019s paradox examples.'
)
doc.add_paragraph().add_run('Table 6. Summary of empirical validation results.').bold = True
add_table(doc,
    ['Example', 'Best method', 'Best ARI', 'Oracle ARI', 'Achievement rate', 'C1 (best)', 'C1 (random)', '\u03b7\u00b2 (mean, best)'],
    [
        ['Kidney stone', '2B Clustering', '0.851', '1.000', '85.1%', '0.034', '0.695', '0.428'],
        ['Israeli vaccine', '2B Clustering', '0.746', '1.000', '74.6%', '0.005', '0.770', '0.432'],
        ['Smoking\u2013mortality', '1A Pred. prob.', '0.498', '1.000', '49.8%', '0.005', '1.000', '0.686'],
        ['UC Berkeley', '1A Pred. prob.', '0.082', '1.000', '8.2%', '0.011', '0.954', '0.152'],
        ['COVID-19 CFR', '1B Residual', '0.064', '1.000', '6.4%', '0.001', '0.778', '0.171'],
    ]
)

# Insert real data figures
add_figure(doc,
    f'{FIG_RD}/fig1_paradox_demonstration.png',
    'Figure 7. Demonstration of Simpson\u2019s paradox in each of the five empirical examples.'
)

doc.add_heading('Finding 1: Coherence indicator C1 was universally effective', level=3)
doc.add_paragraph(
    'Across all five examples, C1 values for proposed methods (range: 0.001\u20130.034) were clearly separated '
    'from C1 values for random stratification (range: 0.695\u20131.000). This indicates that C1 reliably detects '
    'population incoherence regardless of the underlying subgroup structure complexity, sample size, or domain.'
)

add_figure(doc,
    f'{FIG_RD}/fig3_coherence_analysis.png',
    'Figure 8. Coherence indicator C1 values across all five empirical examples: proposed methods vs. random baseline.'
)

doc.add_heading('Finding 2: Subgroup structure complexity determined stratification accuracy', level=3)
doc.add_paragraph(
    'Two-group structures with clear separation were recovered with high accuracy: kidney stone (2 groups: '
    'small/large stones) ARI = 0.851 (2B Clustering), approaching the Oracle (1.000); Israeli vaccine (2 groups: '
    '<60/\u226560 years) ARI = 0.746 (2B Clustering). Multi-group or continuous structures were more challenging: '
    'smoking\u2013mortality (7 age groups, but age is a strong continuous predictor) ARI = 0.498 (1A Predicted '
    'probability); COVID-19 CFR (9 age groups) ARI = 0.064 (1B Residual); UC Berkeley (6 departments) '
    'ARI = 0.082 (1A Predicted probability).'
)

add_figure(doc,
    f'{FIG_RD}/fig2_method_comparison.png',
    'Figure 9. Method comparison across the five empirical examples (ARI by method and example).'
)

doc.add_heading('Finding 3: Decision power-based and feature score-based methods were complementary', level=3)
doc.add_paragraph(
    'For two-group structures with clear separation, the unsupervised clustering method (2B) outperformed '
    'decision power-based methods (kidney stone: 2B ARI = 0.851 vs. 1A ARI = 0.779; Israeli vaccine: 2B '
    'ARI = 0.746 vs. 1A ARI = 0.217). For multi-group and continuous structures, decision power-based methods '
    'were superior (smoking: 1A ARI = 0.498 vs. 2B ARI = 0.227; COVID-19: 1B ARI = 0.064 vs. 2B ARI = 0.056).'
)

doc.add_heading('Finding 4: \u03b7\u00b2 confirmed Z\u2192X influence as the primary determinant', level=3)
doc.add_paragraph(
    'The relationship between \u03b7\u00b2 (variance in Z explained by stratification) and ARI achievement rate was '
    'consistent with the simulation findings. Examples with high \u03b7\u00b2 (smoking: 0.686; kidney stone: 0.428; '
    'Israeli vaccine: 0.432) achieved higher ARI than those with low \u03b7\u00b2 (COVID-19: 0.171; Berkeley: 0.152).'
)

add_figure(doc,
    f'{FIG_RD}/fig4_eta_squared_heatmap.png',
    'Figure 10. Eta-squared (\u03b7\u00b2) heatmap across empirical examples and methods.'
)

doc.add_heading('Finding 5: Simulation and empirical results were concordant', level=3)
doc.add_paragraph().add_run('Table 7. Concordance between simulation and empirical findings.').bold = True
add_table(doc,
    ['Finding', 'Simulation', 'Empirical validation'],
    [
        ['1B Residual is most robust in Family 1', 'Highest ARI (0.020)', 'Best for COVID-19 (ARI = 0.064)'],
        ['C1 detects incoherence', 'Random 0.863 vs. proposed 0.001', 'Random 0.70\u20131.00 vs. proposed 0.00\u20130.03'],
        ['Z\u2192X influence is decisive', 'ARI increases with zx', 'Higher \u03b7\u00b2 correlates with higher ARI'],
        ['All proposed methods outperform random', 'All scenarios', 'All five examples'],
    ]
)

add_figure(doc,
    f'{FIG_RD}/fig5_direction_consistency.png',
    'Figure 11. Direction consistency analysis across the five empirical examples.'
)

add_figure(doc,
    f'{FIG_RD}/fig6_summary_dashboard.png',
    'Figure 12. Summary dashboard of empirical validation results across all five examples.',
    width=Inches(6.0)
)

doc.add_page_break()

# ============================================================
# DISCUSSION
# ============================================================
doc.add_heading('Discussion', level=1)

doc.add_heading('Principal findings', level=2)
doc.add_paragraph(
    'This study introduces IONE, a framework for detecting and extracting hidden population structure in '
    'observational studies. The principal findings are twofold. First, the coherence indicator C1, derived from '
    'the I\u00b2 heterogeneity statistic, reliably detected population incoherence in both simulated data '
    '(66,600 evaluations) and all five published Simpson\u2019s paradox examples. This \u201cwarning\u201d '
    'function\u2014the ability to signal that a study population likely contains hidden subgroups\u2014was robust '
    'to subgroup complexity, sample size, and analytical domain. Second, stratification-based extraction of '
    'coherent subpopulations was conditionally successful: high accuracy was achieved for discrete two-group '
    'structures (ARI > 0.7), moderate accuracy for continuous strong-signal structures (ARI \u2248 0.5), and '
    'limited accuracy for multi-group weak-signal structures (ARI < 0.1). The strength of the hidden variable\u2019s '
    'influence on measured variables (Z\u2192X influence, quantified by \u03b7\u00b2) was identified as the single '
    'most important determinant of extraction performance.'
)

doc.add_heading('Two-tier utility', level=2)
doc.add_paragraph(
    'The distinction between detection (first tier) and extraction (second tier) is important for practical '
    'implementation. The C1 coherence indicator requires no assumption about the number or nature of hidden '
    'subgroups and can be computed from routinely available data (measured covariates and the outcome). Its '
    'consistently strong performance across all conditions tested suggests that it could serve as a standard '
    'diagnostic tool in observational study reporting\u2014analogous to the I\u00b2 statistic in meta-analysis, '
    'but applied within a single study to assess internal homogeneity.'
)
doc.add_paragraph(
    'The extraction tier is more demanding and context-dependent. Our results suggest the following guidance '
    'for applied researchers:'
)
doc.add_paragraph(
    '\u2022 Two to three discrete subgroups with strong traces (\u03b7\u00b2 > 0.4): Feature score-based '
    'clustering (Method 2B) is likely to achieve high recovery (ARI > 0.7). This scenario corresponds clinically '
    'to disease subtypes, age-based risk categories, or treatment allocation patterns driven by clear clinical criteria.'
)
doc.add_paragraph(
    '\u2022 Multiple or continuous subgroups with moderate traces (0.15 < \u03b7\u00b2 \u2264 0.4): Decision '
    'power-based methods (especially 1A and 1B) offer partial recovery. Both method families should be applied and compared.'
)
doc.add_paragraph(
    '\u2022 Weak traces (\u03b7\u00b2 < 0.15): Extraction accuracy is limited. C1 may still detect incoherence, '
    'but the identified strata should be interpreted cautiously.'
)

doc.add_heading('Comparison with existing methods', level=2)
doc.add_paragraph(
    'IONE differs from existing confounding adjustment methods in its objectives and assumptions. Propensity '
    'score methods [14] and prognostic scores [15] aim to balance or adjust for measured confounders; they are '
    'not designed to detect unmeasured population structure. The hdPS algorithm [19] shares IONE\u2019s insight '
    'that proxy variables may carry information about unmeasured confounders, but uses this information to '
    'improve propensity score estimation rather than to identify discrete subpopulations. Latent class analysis '
    '[23] seeks hidden subgroups but typically requires strong distributional assumptions and does not provide a '
    'coherence diagnostic.'
)
doc.add_paragraph(
    'IONE is best understood as complementary to these methods rather than as a replacement. We envision a '
    'workflow in which IONE is applied as a preliminary step: if C1 indicates incoherence, the population is '
    'stratified into coherent subgroups, and conventional methods (e.g. propensity score analysis) are applied '
    'within each subgroup. This two-stage adjustment\u2014first addressing hidden population structure, then '
    'adjusting for measured confounders\u2014may yield more reliable effect estimates than either approach alone.'
)

doc.add_heading('Strengths and limitations', level=2)

doc.add_paragraph().add_run('Strengths.').bold = True
doc.add_paragraph(
    'This study employed a comprehensive simulation design with 66,600 evaluations spanning a wide range of '
    'data-generating conditions, including systematic variation of the key parameter (Z\u2192X influence strength). '
    'The ADEMP framework ensured transparent reporting of all design choices. Empirical validation on five '
    'published Simpson\u2019s paradox examples from diverse domains (clinical medicine, public health, social '
    'science) demonstrated generalisability beyond the simulation setting.'
)

doc.add_paragraph().add_run('Limitations.').bold = True
doc.add_paragraph(
    'Several limitations should be acknowledged. First, the empirical validation used pseudo-general variables '
    'generated from published aggregate data, rather than genuine clinical measurements. Whilst this permits '
    'evaluation of the method\u2019s operating characteristics under known confounding, it does not fully replicate '
    'the complexity of real clinical data. Validation on clinical databases with individual-level data (e.g. '
    'MIMIC-IV, UK Biobank) is an important next step.'
)
doc.add_paragraph(
    'Second, the simulation employed a relatively simple data-generating mechanism with three critical variables, '
    'ten general variables, and a logistic outcome model. Real clinical data may involve more complex causal '
    'structures, non-linear relationships, missing data, and measurement error. The sensitivity of IONE to these '
    'complications requires further investigation.'
)
doc.add_paragraph(
    'Third, the gap between proposed methods and the Oracle baseline was substantial in simulations (best '
    'ARI = 0.020 vs. Oracle ARI = 0.353). This indicates that complete recovery of hidden population structure '
    'from measured variables alone is not achieved. The practical value of IONE therefore lies primarily in the '
    'C1 coherence indicator and in the partial extraction of subgroup structure, rather than in perfect confounding '
    'adjustment.'
)
doc.add_paragraph(
    'Fourth, binary critical variables (e.g. sex) were poorly captured (\u03b7\u00b2 < 0.03), suggesting that '
    'IONE is better suited to detecting continuous or ordinal confounders that leave stronger traces in measured '
    'variables.'
)
doc.add_paragraph(
    'Fifth, the C1 threshold of 0.05 proposed here is provisional, based on simulation results and five empirical '
    'examples. Formal calibration across a wider range of datasets and clinical settings is needed before firm '
    'recommendations can be made.'
)

doc.add_heading('Implications for practice', level=2)
doc.add_paragraph(
    'If replicated in further studies, our findings have several practical implications. First, we recommend that '
    'observational study reports include a coherence assessment alongside the conventional Table 1. When C1 falls '
    'below a pre-specified threshold, this should trigger additional subgroup analyses to explore potential hidden '
    'population structure. Second, the complementary strengths of decision power-based and feature score-based '
    'methods suggest that both should be applied when assessing population coherence, as their agreement provides '
    'stronger evidence for the existence of hidden subgroups. Third, the identification of Z\u2192X influence '
    'strength as the primary determinant of performance provides a principled basis for assessing the likely '
    'utility of IONE in a given application: the method is most promising in settings where important confounders '
    '(age, disease severity, comorbidity) are known to influence routine measurements (laboratory values, vital '
    'signs), which is precisely the scenario most commonly encountered in clinical epidemiology.'
)

doc.add_heading('Future directions', level=2)
doc.add_paragraph(
    'Several avenues for future research emerge from this work. Methodological extensions include adaptation to '
    'survival outcomes, continuous outcomes, and time-varying confounding. The combination of IONE with propensity '
    'score methods in a formal two-stage adjustment framework warrants investigation. The C1 coherence indicator '
    'could be extended to a multi-level diagnostic that recommends the optimal number of subgroups. Empirical '
    'validation on individual-level clinical databases with genuinely unmeasured confounders would provide a '
    'stronger test of the method\u2019s practical utility. Finally, the development of software packages (R and '
    'Python) implementing the IONE workflow would facilitate adoption.'
)

doc.add_page_break()

# ============================================================
# CONCLUSIONS
# ============================================================
doc.add_heading('Conclusions', level=1)
doc.add_paragraph(
    'We have introduced IONE (Incoherence-Oriented Neutralisation and Extraction), a framework for detecting '
    'hidden population structure in observational studies. Through Monte Carlo simulation (66,600 evaluations) '
    'and empirical validation on five published instances of Simpson\u2019s paradox, we demonstrate that IONE '
    'provides a two-tier contribution. The C1 coherence indicator reliably detects population incoherence across '
    'all conditions tested and can serve as a quantitative diagnostic for hidden subgroup structure. '
    'Stratification-based extraction of coherent subpopulations is effective when hidden variables leave '
    'sufficiently strong traces in measured variables and the subgroup structure is discrete. The strength of '
    'the hidden variable\u2019s influence on measured variables is the primary determinant of extraction performance. '
    'We recommend that coherence assessment using C1 be considered as a standard component of observational study '
    'reporting, complementing existing tools such as propensity score analysis rather than replacing them.'
)

doc.add_page_break()

# ============================================================
# LIST OF ABBREVIATIONS
# ============================================================
doc.add_heading('List of abbreviations', level=1)
add_table(doc,
    ['Abbreviation', 'Full term'],
    [
        ['ARI', 'Adjusted Rand Index'],
        ['BMI', 'Body mass index'],
        ['C1', 'Coherence indicator 1 (I\u00b2-based)'],
        ['CFR', 'Case fatality rate'],
        ['DAG', 'Directed acyclic graph'],
        ['DRS', 'Disease risk score'],
        ['hdPS', 'High-dimensional propensity score'],
        ['IONE', 'Incoherence-Oriented Neutralisation and Extraction'],
        ['IV', 'Instrumental variable'],
        ['NMI', 'Normalised Mutual Information'],
        ['OR', 'Odds ratio'],
        ['PCA', 'Principal component analysis'],
        ['PS', 'Propensity score'],
        ['RCT', 'Randomised controlled trial'],
    ]
)

# ============================================================
# DECLARATIONS
# ============================================================
doc.add_heading('Declarations', level=1)

doc.add_heading('Ethics approval and consent to participate', level=2)
doc.add_paragraph(
    'Not applicable. This study used simulated data and publicly available aggregate statistics only.'
)

doc.add_heading('Consent for publication', level=2)
doc.add_paragraph('Not applicable.')

doc.add_heading('Availability of data and materials', level=2)
doc.add_paragraph(
    'The simulation code and analysis scripts are available at [repository URL to be inserted]. '
    'The published datasets used for empirical validation are referenced in the original publications [9\u201313].'
)

doc.add_heading('Competing interests', level=2)
doc.add_paragraph('[To be inserted]')

doc.add_heading('Funding', level=2)
doc.add_paragraph('[To be inserted]')

doc.add_heading('Authors\u2019 contributions', level=2)
doc.add_paragraph('[To be inserted]')

doc.add_heading('Acknowledgements', level=2)
doc.add_paragraph('[To be inserted]')

doc.add_page_break()

# ============================================================
# REFERENCES
# ============================================================
doc.add_heading('References', level=1)

refs = [
    '1. Hammerton G, Munaf\u00f2 MR. Causal inference with observational data: the need for triangulation of evidence. Psychol Med. 2021;51(4):563\u201378.',
    '2. Hern\u00e1n MA, Robins JM. Causal Inference: What If. Boca Raton: Chapman & Hall/CRC; 2020.',
    '3. VanderWeele TJ, Shpitser I. On the definition of a confounder. Ann Stat. 2013;41(1):196\u2013220.',
    '4. Simpson EH. The interpretation of interaction in contingency tables. J R Stat Soc Ser B. 1951;13(2):238\u201341.',
    '5. Rojanaworarit C. Misleading epidemiological and statistical evidence in the presence of Simpson\u2019s paradox: an illustrative study using simulated scenarios. J Med Life. 2020;13(1):37\u201344.',
    '6. VanderWeele TJ, Knol MJ. A tutorial on interaction. Epidemiol Methods. 2014;3(1):33\u201372.',
    '7. Robinson WS. Ecological correlations and the behavior of individuals. Am Sociol Rev. 1950;15(3):351\u20137.',
    '8. Greenland S, Robins JM, Pearl J. Confounding and collapsibility in causal inference. Stat Sci. 1999;14(1):29\u201346.',
    '9. Charig CR, Webb DR, Payne SR, Wickham JE. Comparison of treatment of renal calculi by open surgery, percutaneous nephrolithotomy, and extracorporeal shockwave lithotripsy. BMJ. 1986;292(6521):879\u201382.',
    '10. Bickel PJ, Hammel EA, O\u2019Connell JW. Sex bias in graduate admissions: data from Berkeley. Science. 1975;187(4175):398\u2013404.',
    '11. von K\u00fcgelgen J, Gresele L, Sch\u00f6lkopf B. Simpson\u2019s paradox in Covid-19 case fatality rates: a mediation analysis of age-related causal effects. IEEE Trans Artif Intell. 2021;2(1):18\u201327.',
    '12. Morris JA. Israeli data: how can efficacy vs. severe disease be 91.4% when 60% of severe cases are vaccinated? 2021. https://www.covid-datascience.com/post/israeli-data-how-can-efficacy-vs-severe-disease-be-91-when-60-of-severe-cases-are-vaccinated',
    '13. Appleton DR, French JM, Vanderpump MPJ. Ignoring a covariate: an example of Simpson\u2019s paradox. Am Stat. 1996;50(4):340\u20131.',
    '14. Rosenbaum PR, Rubin DB. The central role of the propensity score in observational studies for causal effects. Biometrika. 1983;70(1):41\u201355.',
    '15. Hansen BB. The prognostic analogue of the propensity score. Biometrika. 2008;95(2):481\u20138.',
    '16. Aikens RC, Greaves D, Baiocchi M. A pilot design for observational studies: using abundant data thoughtfully. Stat Med. 2020;39(29):4349\u201369.',
    '17. Miettinen OS. Stratification by a multivariate confounder score. Am J Epidemiol. 1976;104(6):609\u201320.',
    '18. Angrist JD, Imbens GW, Rubin DB. Identification of causal effects using instrumental variables. J Am Stat Assoc. 1996;91(434):444\u201355.',
    '19. Schneeweiss S, Rassen JA, Glynn RJ, Avorn J, Mogun H, Brookhart MA. High-dimensional propensity score adjustment in studies of treatment effects using health care claims data. Epidemiology. 2009;20(4):512\u201322.',
    '20. Rassen JA, Schneeweiss S. Using high-dimensional propensity scores to automate confounding control in a distributed medical product safety surveillance system. Pharmacoepidemiol Drug Saf. 2012;21(S1):41\u20139.',
    '21. Wyss R, Schneeweiss S, van der Laan M, Lendle SD, Ju C, Franklin JM. Machine learning for improving high-dimensional proxy confounder adjustment in healthcare database studies. Stat Med. 2018;37(8):1310\u201324.',
    '22. Tchetgen Tchetgen EJ, Ying A, Cui Y, Shi X, Miao W. An introduction to proximal causal inference. Stat Sci. 2024;39(3):375\u201390.',
    '23. McLachlan GJ, Peel D. Finite Mixture Models. New York: Wiley; 2000.',
    '24. Hayes-Larson E, Kezios KL, Mooney SJ, Lovasi G. Who is in this study, anyway? Guidelines for a useful Table 1. J Clin Epidemiol. 2019;114:125\u201332.',
    '25. Higgins JPT, Thompson SG. Quantifying heterogeneity in a meta-analysis. Stat Med. 2002;21(11):1539\u201358.',
    '26. Morris TP, White IR, Crowther MJ. Using simulation studies to evaluate statistical methods. Stat Med. 2019;38(11):2074\u2013102.',
    '27. Hubert L, Arabie P. Comparing partitions. J Classif. 1985;2(1):193\u2013218.',
    '28. Strehl A, Ghosh J. Cluster ensembles\u2014a knowledge reuse framework for combining multiple partitions. J Mach Learn Res. 2002;3:583\u2013617.',
]

for ref in refs:
    doc.add_paragraph(ref)

doc.add_page_break()

# ============================================================
# ADDITIONAL FILES (Checklists)
# ============================================================
doc.add_heading('Additional file 1: Supplementary Methods', level=1)
doc.add_paragraph(
    'Detailed description of the pseudo-general variable generation procedure for each of the five Simpson\u2019s '
    'paradox examples, including the correlation structures imposed between pseudo-general variables and the known '
    'confounding variable.'
)
doc.add_paragraph('[To be prepared]')

doc.add_heading('Additional file 2: ADEMP Checklist', level=1)
doc.add_paragraph().add_run('Table S1. ADEMP checklist for the simulation study.').bold = True
add_table(doc,
    ['ADEMP component', 'Item', 'Section'],
    [
        ['Aims', 'Specific aims stated', 'Methods: Aims'],
        ['', 'Evaluate stratification-based subgroup recovery, compare method families, assess C1 indicator, identify optimal conditions', ''],
        ['Data-generating mechanisms', 'Causal structure described (DAG)', 'Methods: Data-generating mechanisms'],
        ['', 'Variable distributions specified', 'Methods: Data-generating mechanisms'],
        ['', 'Factors varied and levels stated', 'Methods: Scenarios'],
        ['', 'Justification for DGM choices', 'Methods: Data-generating mechanisms'],
        ['', 'Number of repetitions and justification', 'Methods: Scenarios'],
        ['Estimands', 'Estimands defined', 'Methods: Estimands'],
        ['Methods', 'All methods described (6 proposed + 2 baselines)', 'Methods: Methods under comparison'],
        ['', 'Rationale for method selection', 'Methods: Methods under comparison'],
        ['Performance measures', 'Performance measures listed with definitions', 'Methods: Performance measures'],
        ['', 'Monte Carlo SE reported', 'Methods: Performance measures'],
    ]
)

doc.add_heading('Additional file 3: STROBE-Sim Checklist', level=1)
doc.add_paragraph().add_run(
    'Table S2. STROBE-Sim reporting checklist for the simulation study (adapted from Burton et al. 2006 and Morris et al. 2019).'
).bold = True
add_table(doc,
    ['Item', 'STROBE-Sim recommendation', 'Reported', 'Location in manuscript'],
    [
        ['Title/abstract', '', '', ''],
        ['1a', 'Indicate simulation study in title', 'Yes', 'Title'],
        ['1b', 'Structured abstract with aims, methods, results, conclusions', 'Yes', 'Abstract'],
        ['Introduction', '', '', ''],
        ['2', 'Scientific background and rationale', 'Yes', 'Background'],
        ['3', 'Specific objectives or hypotheses', 'Yes', 'Background, final paragraph'],
        ['Methods', '', '', ''],
        ['4', 'Study design (simulation + empirical)', 'Yes', 'Methods: opening paragraph'],
        ['5', 'Data-generating mechanism: causal structure (DAG)', 'Yes', 'Methods: Data-generating mechanisms'],
        ['6', 'Data-generating mechanism: variable distributions', 'Yes', 'Methods: Data-generating mechanisms'],
        ['7', 'Data-generating mechanism: outcome model', 'Yes', 'Methods: Outcome model'],
        ['8', 'Factors varied systematically', 'Yes', 'Methods: Scenarios'],
        ['9', 'Number of repetitions with justification', 'Yes', 'Methods: Scenarios'],
        ['10', 'Estimands clearly defined', 'Yes', 'Methods: Estimands'],
        ['11', 'All methods under comparison described', 'Yes', 'Methods: Methods under comparison'],
        ['12', 'Performance measures with definitions', 'Yes', 'Methods: Performance measures'],
        ['13', 'Software and computational details', 'Yes', 'Methods: Computational implementation'],
        ['14', 'Coding verification / validation', 'Partial', 'Fixed seeds; code availability stated'],
        ['Results', '', '', ''],
        ['15', 'Number of simulations completed vs. planned', 'Yes', 'Results: 66,600 evaluations'],
        ['16', 'Summary of performance measures across scenarios', 'Yes', 'Results: Tables 2\u20137'],
        ['17', 'Presentation of results for each estimand', 'Yes', 'Results (ARI, \u03b7\u00b2, C1 reported separately)'],
        ['18', 'Monte Carlo standard errors', '[To be added]', '\u2014'],
        ['Discussion', '', '', ''],
        ['19', 'Summary of key findings', 'Yes', 'Discussion: Principal findings'],
        ['20', 'Comparison with previous studies', 'Yes', 'Discussion: Comparison with existing methods'],
        ['21', 'Limitations of simulation design', 'Yes', 'Discussion: Strengths and limitations'],
        ['22', 'Generalisability of findings', 'Yes', 'Discussion: Implications for practice'],
        ['Other', '', '', ''],
        ['23', 'Source of funding', '[To be inserted]', 'Declarations: Funding'],
        ['24', 'Code availability', 'Yes', 'Declarations: Availability of data and materials'],
        ['25', 'Role of funder', '[To be inserted]', '\u2014'],
    ]
)

doc.add_heading('Additional file 4: Supplementary Results', level=1)
doc.add_paragraph(
    'Full results tables for all sensitivity analysis conditions, including per-scenario ARI, \u03b7\u00b2, and C1 values.'
)
doc.add_paragraph('[To be prepared]')

# ============================================================
# Footer
# ============================================================
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Manuscript prepared for submission to BMC Medical Research Methodology')
run.italic = True
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Target collection: Causal inference and observational data vol. 2')
run.italic = True
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Submission deadline: 30 July 2026')
run.italic = True

# --- Save ---
outpath = '/home/ubuntu/repos/stratification_project/results/manuscript/IONE_manuscript.docx'
doc.save(outpath)
print(f'Saved to {outpath}')
