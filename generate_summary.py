"""
Generate reproducible summary tables from simulation and real-data CSVs.
All numbers written to results/summary/ are the source for the manuscript.
"""

import os
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
OUT_DIR = os.path.join(RESULTS_DIR, 'summary')
os.makedirs(OUT_DIR, exist_ok=True)


def _mc_stats(s: pd.Series):
    """Mean, standard deviation, Monte Carlo SE, and 95% CI half-width."""
    s = s.dropna()
    if len(s) == 0:
        return (np.nan, np.nan, np.nan, np.nan)
    if len(s) < 2:
        mean = float(s.iloc[0])
        return (mean, np.nan, np.nan, np.nan)
    mean = s.mean()
    std = s.std(ddof=1)
    se = std / np.sqrt(len(s))
    ci = 1.96 * se
    return (mean, std, se, ci)


def _read_summary(name: str):
    path = os.path.join(OUT_DIR, name)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def _add_null_centered_metrics(df: pd.DataFrame, null_summary: pd.DataFrame):
    """Add null-mean-centered metrics: excess C1 and W above the empirical null mean.

    Because W is a ratio whose denominator (overall CATE variance) is small under
    the null, raw W values can be unstable. Centering by the empirical null mean
    gives a diagnostic of how much a value exceeds what is expected when no true
    effect modification is present.
    """
    if null_summary is None or null_summary.empty or df is None or df.empty:
        df['C1_excess'] = np.nan
        df['W_true_excess'] = np.nan
        df['W_est_excess'] = np.nan
        return df
    maps = {
        'C1_excess': ('C1_heterogeneity', 'C1_heterogeneity_mean', True),
        'W_true_excess': ('W_true', 'W_true_mean', False),
        'W_est_excess': ('W_est', 'W_est_mean', False),
    }
    # Force default float dtype for new columns
    for new_col in maps:
        df[new_col] = np.nan
    for method, sub_null in null_summary.groupby('method'):
        mask = df['method'] == method
        if not mask.any():
            continue
        for new_col, (src, null_mean_col, invert) in maps.items():
            if src not in df.columns or null_mean_col not in sub_null.columns:
                continue
            null_mean = sub_null[null_mean_col].mean()
            if pd.isna(null_mean):
                continue
            vals = df.loc[mask, src].astype(float)
            if invert:
                diff = null_mean - vals
            else:
                diff = vals - null_mean
            df.loc[mask, new_col] = np.where(diff > 0, diff, 0.0)
    return df


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
        # Robust relative bias reduction from absolute bias means, not from per-simulation ratios.
        # Delta-method SEs use the joint sampling variation of absolute crude and reduced biases.
        if 'bias_crude' in metric_cols and 'bias_stratified' in metric_cols:
            abs_crude_ser = sub['bias_crude'].abs()
            abs_strat_ser = sub['bias_stratified'].abs()
            n = len(abs_crude_ser)
            abs_crude = abs_crude_ser.mean()
            abs_strat = abs_strat_ser.mean()
            row['abs_bias_crude_mean'] = float(abs_crude)
            row['abs_bias_stratified_mean'] = float(abs_strat)
            row['abs_bias_crude_se'] = float(abs_crude_ser.std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan
            row['abs_bias_stratified_se'] = float(abs_strat_ser.std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan
            if abs_crude > 1e-12:
                r = 1.0 - abs_strat / abs_crude
                row['bias_reduction_relative_mean'] = float(r)
                if n > 1:
                    cov = np.cov(abs_crude_ser.values, abs_strat_ser.values, ddof=1)
                    var_c = cov[0, 0] / n
                    var_s = cov[1, 1] / n
                    cov_cs = cov[0, 1] / n
                    var_r = (var_s / abs_crude**2) + (abs_strat**2 * var_c / abs_crude**4) - 2 * (abs_strat * cov_cs / abs_crude**3)
                    row['bias_reduction_relative_se'] = float(np.sqrt(max(var_r, 0.0)))
                else:
                    row['bias_reduction_relative_se'] = np.nan
            else:
                row['bias_reduction_relative_mean'] = float(np.nan)
                row['bias_reduction_relative_se'] = float(np.nan)
            if 'bias_re' in metric_cols:
                abs_re_ser = sub['bias_re'].abs()
                abs_re = abs_re_ser.mean()
                row['abs_bias_re_mean'] = float(abs_re)
                row['abs_bias_re_se'] = float(abs_re_ser.std(ddof=1) / np.sqrt(len(abs_re_ser))) if len(abs_re_ser) > 1 else np.nan
                if abs_crude > 1e-12:
                    r_re = 1.0 - abs_re / abs_crude
                    row['bias_reduction_relative_re_mean'] = float(r_re)
                    if n > 1 and len(abs_re_ser) > 1:
                        cov_re = np.cov(abs_crude_ser.values, abs_re_ser.values, ddof=1)
                        var_c = cov_re[0, 0] / n
                        var_re = cov_re[1, 1] / n
                        cov_cre = cov_re[0, 1] / n
                        var_r_re = (var_re / abs_crude**2) + (abs_re**2 * var_c / abs_crude**4) - 2 * (abs_re * cov_cre / abs_crude**3)
                        row['bias_reduction_relative_re_se'] = float(np.sqrt(max(var_r_re, 0.0)))
                    else:
                        row['bias_reduction_relative_re_se'] = np.nan
                else:
                    row['bias_reduction_relative_re_mean'] = float(np.nan)
                    row['bias_reduction_relative_re_se'] = float(np.nan)
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
    null_summary = _read_summary('rsm_ipd_null_summary.csv')
    df = _add_null_centered_metrics(df, null_summary)
    metric_cols = ['ARI', 'C1_heterogeneity', 'C1_excess', 'W_true', 'W_true_excess',
                   'W_est', 'W_est_excess', 'bias_crude', 'bias_stratified', 'bias_re',
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
    null_summary = _read_summary('rsm_ipd_null_summary.csv')
    df = _add_null_centered_metrics(df, null_summary)
    metric_cols = ['ARI', 'C1_heterogeneity', 'C1_excess', 'W_true', 'W_true_excess',
                   'W_est', 'W_est_excess', 'bias_crude', 'bias_stratified', 'bias_re',
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


def summarise_rsm_ipd_null():
    path = os.path.join(RESULTS_DIR, 'rsm_ipd_null_results.csv')
    if not os.path.exists(path):
        print(f'[generate_summary] {path} not found; skipping null distribution summary')
        return
    df = pd.read_csv(path)
    df = df[df['error'].isna()].copy()
    metric_cols = ['ARI', 'C1_heterogeneity', 'W_true', 'W_est',
                   'bias_crude', 'bias_stratified', 'bias_re',
                   'bias_reduction', 'bias_reduction_relative',
                   'bias_reduction_re', 'bias_reduction_relative_re',
                   're_tau2', 're_I2']
    summary = _summarise(df, ['method'], metric_cols)
    # Empirical percentiles for null thresholds
    q_metrics = ['C1_heterogeneity', 'W_est']
    qs = [0.05, 0.95]
    try:
        quantiles = df.groupby('method')[q_metrics].quantile(qs).unstack(level=-1)
        quantiles.columns = [f'{m}_{int(q*100)}pct' for m, q in quantiles.columns]
        summary = summary.merge(quantiles.reset_index(), on='method', how='left')
    except Exception as e:
        print(f'[generate_summary] could not compute null quantiles: {e}')
    summary.to_csv(os.path.join(OUT_DIR, 'rsm_ipd_null_summary.csv'), index=False)
    print(f'[generate_summary] rsm_ipd_null summary: {len(summary)} rows')


def summarise_w_est_misspec():
    path = os.path.join(RESULTS_DIR, 'w_est_misspec_results.csv')
    if not os.path.exists(path):
        print(f'[generate_summary] {path} not found; skipping W_est misspec summary')
        return
    df = pd.read_csv(path)
    df = df[df['error'].isna()].copy()
    null_summary = _read_summary('rsm_ipd_null_summary.csv')
    df = _add_null_centered_metrics(df, null_summary)
    metric_cols = ['ARI', 'C1_heterogeneity', 'C1_excess', 'W_true', 'W_true_excess',
                   'W_est', 'W_est_excess', 'W_est_main', 'W_est_polynomial',
                   'bias_crude', 'bias_stratified', 'bias_re',
                   'bias_reduction', 'bias_reduction_relative',
                   'bias_reduction_re', 'bias_reduction_relative_re',
                   're_tau2', 're_I2']
    summary = _summarise(df, ['method'], metric_cols)
    summary.to_csv(os.path.join(OUT_DIR, 'w_est_misspec_summary.csv'), index=False)
    print(f'[generate_summary] w_est_misspec summary: {len(summary)} rows')


def summarise_diagnostic_roc():
    """Compute diagnostic ROC/AUC/TPR for C1 and W_est using the empirical null distribution."""
    alt_path = os.path.join(RESULTS_DIR, 'rsm_ipd_results.csv')
    null_path = os.path.join(RESULTS_DIR, 'rsm_ipd_null_results.csv')
    if not os.path.exists(alt_path) or not os.path.exists(null_path):
        print('[generate_summary] rsm_ipd_results.csv or rsm_ipd_null_results.csv not found; skipping ROC')
        return

    alt = pd.read_csv(alt_path).dropna(subset=['C1_heterogeneity', 'W_est'])
    null = pd.read_csv(null_path).dropna(subset=['C1_heterogeneity', 'W_est'])

    cond = {
        'n': 2000,
        'n_strata': 5,
        'z_effect_scale': 1.0,
        'zx_influence_scale': 1.0,
        'n_studies': 10,
        'study_effect_scale': 0.6,
    }
    for k, v in cond.items():
        if k in alt.columns:
            alt = alt[alt[k] == v]
        if k in null.columns:
            null = null[null[k] == v]
    if 'nonlinear' in alt.columns:
        alt = alt[alt['nonlinear'] == False]
    if 'nonlinear' in null.columns:
        null = null[null['nonlinear'] == False]

    rows = []
    for method in sorted(alt['method'].unique()):
        a = alt[alt['method'] == method]
        n = null[null['method'] == method]
        if a.empty or n.empty:
            continue
        c1_null = n['C1_heterogeneity'].values
        c1_alt = a['C1_heterogeneity'].values
        w_null = n['W_est'].values
        w_alt = a['W_est'].values

        c1_5 = float(np.percentile(c1_null, 5))
        w_95 = float(np.percentile(w_null, 95))
        tpr_c1 = float((c1_alt < c1_5).mean())
        tpr_w = float((w_alt > w_95).mean())

        y_c1 = np.array([0] * len(c1_null) + [1] * len(c1_alt))
        s_c1 = np.concatenate([-c1_null, -c1_alt])  # lower C1 more abnormal
        auc_c1 = float(roc_auc_score(y_c1, s_c1)) if len(np.unique(y_c1)) == 2 else np.nan

        y_w = np.array([0] * len(w_null) + [1] * len(w_alt))
        s_w = np.concatenate([w_null, w_alt])  # higher W_est more abnormal
        auc_w = float(roc_auc_score(y_w, s_w)) if len(np.unique(y_w)) == 2 else np.nan

        # Absolute-deviation from the null mean: neither assumes lower C1 nor higher W.
        c1_null_mean = float(c1_null.mean())
        w_null_mean = float(w_null.mean())
        abs_c1_null = np.abs(c1_null - c1_null_mean)
        abs_c1_alt = np.abs(c1_alt - c1_null_mean)
        abs_w_null = np.abs(w_null - w_null_mean)
        abs_w_alt = np.abs(w_alt - w_null_mean)

        c1_abs_95 = float(np.percentile(abs_c1_null, 95))
        w_abs_95 = float(np.percentile(abs_w_null, 95))
        tpr_c1_abs = float((abs_c1_alt > c1_abs_95).mean())
        tpr_w_abs = float((abs_w_alt > w_abs_95).mean())

        s_c1_abs = np.concatenate([abs_c1_null, abs_c1_alt])
        auc_c1_abs = float(roc_auc_score(y_c1, s_c1_abs)) if len(np.unique(y_c1)) == 2 else np.nan

        s_w_abs = np.concatenate([abs_w_null, abs_w_alt])
        auc_w_abs = float(roc_auc_score(y_w, s_w_abs)) if len(np.unique(y_w)) == 2 else np.nan

        rows.append({
            'method': method,
            'n_null': len(n),
            'n_alt': len(a),
            'c1_null_mean': c1_null_mean,
            'c1_alt_mean': float(c1_alt.mean()),
            'c1_5pct_threshold': c1_5,
            'c1_tpr_5pct': tpr_c1,
            'c1_auc': auc_c1,
            'c1_abs_95pct_threshold': c1_abs_95,
            'c1_abs_tpr_95pct': tpr_c1_abs,
            'c1_abs_auc': auc_c1_abs,
            'w_null_mean': w_null_mean,
            'w_alt_mean': float(w_alt.mean()),
            'w_95pct_threshold': w_95,
            'w_tpr_95pct': tpr_w,
            'w_auc': auc_w,
            'w_abs_95pct_threshold': w_abs_95,
            'w_abs_tpr_95pct': tpr_w_abs,
            'w_abs_auc': auc_w_abs,
        })

    if not rows:
        print('[generate_summary] no diagnostic ROC rows produced')
        return
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT_DIR, 'rsm_ipd_diagnostic_roc_summary.csv'), index=False)
    print(f'[generate_summary] diagnostic ROC summary: {len(df)} methods')


def main():
    summarise_phase1()
    summarise_sensitivity('sensitivity')
    summarise_sensitivity('nonlinearity')
    summarise_real_data()
    summarise_rsm_ipd_null()  # needed as a reference for null-centered metrics
    summarise_rsm_ipd()
    summarise_rsm_ipd_sensitivity()
    summarise_rsm_ipd_nonlinearity()
    summarise_w_est_misspec()
    summarise_diagnostic_roc()
    print('[generate_summary] all summaries written to', OUT_DIR)


if __name__ == '__main__':
    main()
