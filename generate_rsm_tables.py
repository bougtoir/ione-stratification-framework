"""Generate a separate editable .docx containing RSM tables."""

import os
import numpy as np
import pandas as pd
from docx import Document
from docx.shared import Pt

SUMMARY_DIR = os.path.join(os.path.dirname(__file__), 'results', 'summary')
OUT_DIR = os.path.join(os.path.dirname(__file__), 'results', 'manuscript', 'rsm_submission')
os.makedirs(OUT_DIR, exist_ok=True)


def _fmt(x, decimals=3):
    if pd.isna(x):
        return '—'
    return f'{x:.{decimals}f}'


def _add_table(doc, df, cols, caption, numeric_cols):
    p = doc.add_paragraph()
    p.alignment = 1  # CENTER
    run = p.add_run(caption)
    run.bold = True
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
    doc.add_paragraph()


def main():
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(11)

    primary = pd.read_csv(os.path.join(SUMMARY_DIR, 'rsm_ipd_primary_summary.csv'))
    _add_table(
        doc, primary,
        ['Method', 'ARI', 'C1', 'W_true', 'W_est', 'Crude bias', 'Stratified bias',
         'RE bias', 'Relative reduction strat', 'Relative reduction RE', 'RE I2'],
        'Table 1. Primary IPD scenario (n=2000, 10 studies, K=5): means over 50 simulations.',
        {
            'Method': 'method', 'ARI': 'ARI_mean', 'C1': 'C1_heterogeneity_mean',
            'W_true': 'W_true_mean', 'W_est': 'W_est_mean',
            'Crude bias': 'abs_bias_crude_mean', 'Stratified bias': 'abs_bias_stratified_mean',
            'RE bias': 'abs_bias_re_mean',
            'Relative reduction strat': 'bias_reduction_relative_mean',
            'Relative reduction RE': 'bias_reduction_relative_re_mean',
            'RE I2': 're_I2_mean'
        }
    )

    real = pd.read_csv(os.path.join(SUMMARY_DIR, 'real_data_summary.csv'))
    real_non_oracle = real[~real['method'].str.startswith('baseline_')]
    rd_best = real_non_oracle.loc[real_non_oracle.groupby('dataset')['ARI_mean'].idxmax()].copy()
    _add_table(
        doc, rd_best,
        ['Dataset', 'Method', 'K', 'ARI', 'C1', 'W_est', 'Bias reduction'],
        'Table 2. Best real-data illustration result per dataset.',
        {
            'Dataset': 'dataset', 'Method': 'method', 'K': 'n_strata',
            'ARI': 'ARI_mean', 'C1': 'C1_heterogeneity_mean', 'W_est': 'W_est_mean',
            'Bias reduction': 'bias_reduction_mean'
        }
    )

    out = os.path.join(OUT_DIR, 'rsm_tables_separate.docx')
    doc.save(out)
    print(f'[generate_rsm_tables] {out}')


if __name__ == '__main__':
    main()
