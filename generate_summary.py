"""
Generate reproducible summary tables from simulation and real-data CSVs.
All numbers written to results/summary/ are the source for the manuscript.
"""

import os
import numpy as np
import pandas as pd

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
OUT_DIR = os.path.join(RESULTS_DIR, 'summary')
os.makedirs(OUT_DIR, exist_ok=True)


def _mc_stats(s: pd.Series):
    """Mean, standard deviation, Monte Carlo SE, and 95% CI half-width."""
    s = s.dropna()
    if len(s) == 0:
        return (np.nan, np.nan, np.nan, np.nan)
    mean = s.mean()
    std = s.std(ddof=1)
    se = std / np.sqrt(len(s))
    ci = 1.96 * se
    return (mean, std, se, ci)


def _summarise(df: pd.DataFrame, group_cols: list, metric_cols: list) -> pd.DataFrame:
    """Return a tidy summary with mean, sd, se and 95% CI for each metric by group."""
    rows = []
    for grp, sub in df.groupby(group_cols):
        row = {}
        if isinstance(grp, tuple):
            for c, v in zip(group_cols, grp):
                row[c] = v
        else:
            row[group_cols[0]] = grp
        for m in metric_cols:
            if m not in sub.columns:
                raise KeyError(f'Metric {m!r} not in columns: {sub.columns.tolist()}')
            mean, std, se, ci = _mc_stats(sub[m])
            row[f'{m}_mean'] = mean
            row[f'{m}_sd'] = std
            row[f'{m}_se'] = se
            row[f'{m}_ci95'] = ci
        # Robust relative bias reduction from absolute bias means, not from per-simulation ratios
        if 'bias_crude' in metric_cols and 'bias_stratified' in metric_cols:
            abs_crude_ser = sub['bias_crude'].abs()
            abs_strat_ser = sub['bias_stratified'].abs()
            abs_crude = abs_crude_ser.mean()
            abs_strat = abs_strat_ser.mean()
            row['abs_bias_crude_mean'] = float(abs_crude)
            row['abs_bias_stratified_mean'] = float(abs_strat)
            row['abs_bias_crude_se'] = float(abs_crude_ser.std() / np.sqrt(len(abs_crude_ser)))
            row['abs_bias_stratified_se'] = float(abs_strat_ser.std() / np.sqrt(len(abs_strat_ser)))
            if abs_crude > 0:
                row['bias_reduction_relative_mean'] = float(1.0 - abs_strat / abs_crude)
            else:
                row['bias_reduction_relative_mean'] = float(np.nan)
            if 'bias_re' in metric_cols:
                abs_re_ser = sub['bias_re'].abs()
                abs_re = abs_re_ser.mean()
                row['abs_bias_re_mean'] = float(abs_re)
                row['abs_bias_re_se'] = float(abs_re_ser.std() / np.sqrt(len(abs_re_ser)))
                if abs_crude > 0:
                    row['bias_reduction_relative_re_mean'] = float(1.0 - abs_re / abs_crude)
                else:
                    row['bias_reduction_relative_re_mean'] = float(np.nan)
        rows.append(row)
    return pd.DataFrame(rows)


def summarise_phase1():
    path = os.path.join(RESULTS_DIR, 'phase1_results.csv')
    if not os.path.exists(path):
        print(f'[generate_summary] {path} not found; skipping phase1 summary')
        return

    df = pd.read_csv(path)
    # Error rows are retained but metrics are NaN; drop them for clean summaries
    df = df[df['error'].isna()].copy()
    metric_cols = ['ARI', 'C1_heterogeneity', 'W_true', 'W_est',
                     'bias_crude', 'bias_stratified', 'bias_reduction', 'bias_reduction_relative']

    # Main primary scenario
    primary = df[(df['n'] == 2000) & (df['z_effect_scale'] == 1.0) &
                 (df['zx_influence_scale'] == 1.0) & (df['n_strata'] == 5)]
    primary_summary = _summarise(primary, ['method'], metric_cols)
    primary_summary.to_csv(os.path.join(OUT_DIR, 'phase1_primary_summary.csv'), index=False)

    # All phase1 scenarios grouped by n_strata and zx_influence_scale
    full_summary = _summarise(df, ['method', 'n_strata', 'zx_influence_scale'], metric_cols)
    full_summary.to_csv(os.path.join(OUT_DIR, 'phase1_full_summary.csv'), index=False)

    print(f'[generate_summary] phase1 primary: {len(primary_summary)} methods, '
          f'based on {len(primary)} evaluations')


def summarise_sensitivity(name: str = 'sensitivity'):
    path = os.path.join(RESULTS_DIR, f'{name}_results.csv')
    if not os.path.exists(path):
        print(f'[generate_summary] {path} not found; skipping {name} summary')
        return

    df = pd.read_csv(path)
    df = df[df['error'].isna()].copy()
    metric_cols = ['ARI', 'C1_heterogeneity', 'W_true', 'W_est',
                     'bias_crude', 'bias_stratified', 'bias_reduction', 'bias_reduction_relative']

    # Group by method and key DGM factors
    summary = _summarise(df, ['method', 'n', 'z_effect_scale', 'zx_influence_scale', 'n_strata'], metric_cols)
    summary.to_csv(os.path.join(OUT_DIR, f'{name}_full_summary.csv'), index=False)
    print(f'[generate_summary] {name} summary: {len(summary)} rows')


def summarise_real_data():
    path = os.path.join(RESULTS_DIR, 'real_data', 'real_data_results.csv')
    if not os.path.exists(path):
        print(f'[generate_summary] {path} not found; skipping real data summary')
        return

    df = pd.read_csv(path)
    df = df[df['error'].isna()].copy()
    metric_cols = ['ARI', 'C1_heterogeneity', 'W_est', 'bias_crude',
                   'bias_stratified', 'bias_reduction', 'bias_reduction_relative']

    summary = _summarise(df, ['dataset', 'method', 'n_strata'], metric_cols)
    summary.to_csv(os.path.join(OUT_DIR, 'real_data_summary.csv'), index=False)
    print(f'[generate_summary] real data summary: {len(summary)} rows')


def summarise_rsm_ipd():
    path = os.path.join(RESULTS_DIR, 'rsm_ipd_results.csv')
    if not os.path.exists(path):
        print(f'[generate_summary] {path} not found; skipping rsm_ipd summary')
        return

    df = pd.read_csv(path)
    df = df[df['error'].isna()].copy()
    metric_cols = ['ARI', 'C1_heterogeneity', 'W_true', 'W_est',
                   'bias_crude', 'bias_stratified', 'bias_re',
                   'bias_reduction', 'bias_reduction_relative',
                   'bias_reduction_re', 'bias_reduction_relative_re',
                   're_tau2', 're_I2']

    # Primary IPD scenario: n=2000, 10 studies, moderate study heterogeneity, K=5
    primary = df[(df['n'] == 2000) & (df['n_studies'] == 10) &
                 (df['study_effect_scale'] == 0.6) & (df['n_strata'] == 5) &
                 (df['z_effect_scale'] == 1.0) & (df['zx_influence_scale'] == 1.0)]
    primary_summary = _summarise(primary, ['method'], metric_cols)
    primary_summary.to_csv(os.path.join(OUT_DIR, 'rsm_ipd_primary_summary.csv'), index=False)

    # Study-stratified oracle: true study IDs are the same for every method, so collapse to one row
    study_metric_cols = ['study_bias_crude', 'study_bias_stratified', 'study_bias_re',
                         'study_bias_reduction', 'study_bias_reduction_relative',
                         'study_bias_reduction_re', 'study_bias_reduction_relative_re',
                         'study_re_tau2', 'study_re_I2']
    primary_study = primary.drop_duplicates(subset=['sim_id', 'n_strata'])
    available_study_cols = [m for m in study_metric_cols if m in primary_study.columns]
    if available_study_cols:
        row = {'method': 'Study_stratified'}
        for m in available_study_cols:
            row[f'{m}_mean'] = float(primary_study[m].mean())
        study_summary = pd.DataFrame([row])
    else:
        study_summary = pd.DataFrame()
    study_summary.to_csv(os.path.join(OUT_DIR, 'rsm_ipd_study_summary.csv'), index=False)

    # Full grid across strata counts
    full_summary = _summarise(df, ['method', 'n_strata'], metric_cols)
    full_summary.to_csv(os.path.join(OUT_DIR, 'rsm_ipd_full_summary.csv'), index=False)

    print(f'[generate_summary] rsm_ipd primary: {len(primary_summary)} methods, '
          f'based on {len(primary)} evaluations')
    print(f'[generate_summary] rsm_ipd study summary: {len(study_summary)} rows')


def _summarise_rsm_ipd_file(path: str, label: str):
    """Generic summariser for an RSM IPD results CSV (sensitivity or nonlinearity)."""
    if not os.path.exists(path):
        print(f'[generate_summary] {path} not found; skipping {label} summary')
        return

    df = pd.read_csv(path)
    df = df[df['error'].isna()].copy()
    metric_cols = ['ARI', 'C1_heterogeneity', 'W_true', 'W_est',
                   'bias_crude', 'bias_stratified', 'bias_re',
                   'bias_reduction', 'bias_reduction_relative',
                   'bias_reduction_re', 'bias_reduction_relative_re',
                   're_tau2', 're_I2']

    # Full factorial summary
    full = _summarise(
        df,
        ['method', 'n', 'z_effect_scale', 'zx_influence_scale', 'n_strata', 'nonlinear'],
        metric_cols,
    )
    full.to_csv(os.path.join(OUT_DIR, f'{label}_full_summary.csv'), index=False)

    # Method-only marginal (for figures)
    method_marginal = _summarise(df, ['method'], metric_cols)
    method_marginal.to_csv(os.path.join(OUT_DIR, f'{label}_method_summary.csv'), index=False)

    print(f'[generate_summary] {label}: full {len(full)} rows, marginal {len(method_marginal)} rows')


def summarise_rsm_ipd_sensitivity():
    path = os.path.join(RESULTS_DIR, 'rsm_ipd_sensitivity_results.csv')
    _summarise_rsm_ipd_file(path, 'rsm_ipd_sensitivity')


def summarise_rsm_ipd_nonlinearity():
    path = os.path.join(RESULTS_DIR, 'rsm_ipd_nonlinearity_results.csv')
    _summarise_rsm_ipd_file(path, 'rsm_ipd_nonlinearity')


def main():
    summarise_phase1()
    summarise_sensitivity('sensitivity')
    summarise_sensitivity('nonlinearity')
    summarise_real_data()
    summarise_rsm_ipd()
    summarise_rsm_ipd_sensitivity()
    summarise_rsm_ipd_nonlinearity()
    print('[generate_summary] all summaries written to', OUT_DIR)


if __name__ == '__main__':
    main()
