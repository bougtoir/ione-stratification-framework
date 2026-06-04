"""
Compare linear vs non-linear Z->X results (robustness check, R1 major 7).
A) Phase-1:  phase1_results.csv (linear) vs phase1_nonlinear.csv
B) Sensitivity: sensitivity_results.csv (linear) vs sensitivity_nonlinear.csv
No manuscript revision; reporting only.
"""
import pandas as pd
import numpy as np

METHOD_LABELS = {
    '1A_predicted_prob': '1A Predicted prob',
    '1B_residual': '1B Residual',
    '1C_cv_decision': '1C CV decision',
    '1D_ml_uncertainty': '1D ML uncertainty',
    '2A_PCA_cum60': '2A PCA cum60',
    '2B_clustering': '2B Clustering',
    'comp_PS_quintile': 'PS quintiles',
    'comp_GMM': 'GMM',
    'comp_kmeans_X': 'k-means X',
    'comp_prognostic': 'Prognostic score',
    'baseline_oracle_kmeans': 'Oracle k-means',
    'baseline_oracle_quantile': 'Oracle quantile',
    'baseline_random': 'Random baseline',
}


def _mse(series):
    s = series.dropna()
    if len(s) == 0:
        return (np.nan, np.nan)
    return (s.mean(), s.std() / np.sqrt(len(s)))


def compare(linear_csv, nonlinear_csv, label, metrics, method_order):
    dl = pd.read_csv(linear_csv, low_memory=False)
    dn = pd.read_csv(nonlinear_csv, low_memory=False)
    dl = dl[dl['error'].isna()].copy()
    dn = dn[dn['error'].isna()].copy()

    print("\n" + "=" * 100)
    print(f"{label}: linear (n={len(dl)}) vs non-linear (n={len(dn)})")
    print("=" * 100)

    for metric in metrics:
        if metric not in dl.columns or metric not in dn.columns:
            continue
        print(f"\n--- {metric}: mean (SE) ---")
        print(f"| {'Method':22s} | {'Linear':>18s} | {'Non-linear':>18s} | {'Delta':>10s} |")
        print("|" + "-" * 24 + "|" + "-" * 20 + "|" + "-" * 20 + "|" + "-" * 12 + "|")
        for m in method_order:
            ml, sl = _mse(dl[dl['method'] == m][metric])
            mn, sn = _mse(dn[dn['method'] == m][metric])
            if np.isnan(ml) and np.isnan(mn):
                continue
            delta = mn - ml
            lab = METHOD_LABELS.get(m, m)
            print(f"| {lab:22s} | {ml:8.4f} ({sl:7.5f}) | {mn:8.4f} ({sn:7.5f}) | {delta:+10.4f} |")


if __name__ == '__main__':
    import os
    phase1_methods = [
        '1A_predicted_prob', '1B_residual', '1C_cv_decision', '1D_ml_uncertainty',
        '2A_PCA_cum60', '2B_clustering',
        'comp_PS_quintile', 'comp_GMM', 'comp_kmeans_X', 'comp_prognostic',
        'baseline_oracle_kmeans', 'baseline_random',
    ]
    sens_methods = [
        '1A_predicted_prob', '1C_cv_decision', '2A_PCA_cum60', '2B_clustering',
        'comp_PS_quintile', 'comp_GMM', 'comp_prognostic',
        'baseline_oracle_kmeans', 'baseline_random',
    ]
    metrics = ['ARI', 'C1', 'W', 'bias_reduction', 'eta2_mean', 'cate_eta2']

    # phase1 method names: 2A label may differ; detect
    compare('results/phase1_linear_current.csv', 'results/phase1_nonlinear.csv',
            'A) PHASE 1', metrics, phase1_methods)

    if os.path.exists('results/sensitivity_nonlinear.csv'):
        compare('results/sensitivity_results.csv', 'results/sensitivity_nonlinear.csv',
                'B) SENSITIVITY', metrics, sens_methods)
    else:
        print("\n[B sensitivity non-linear not finished yet]")
