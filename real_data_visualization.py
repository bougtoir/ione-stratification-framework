"""
Visualization for real-data Simpson's paradox analysis.
Generates comprehensive figures for the report.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import os

plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.family'] = 'Noto Sans CJK JP'

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results', 'real_data')
os.makedirs(RESULTS_DIR, exist_ok=True)


def load_results():
    csv_path = os.path.join(RESULTS_DIR, 'real_data_results.csv')
    return pd.read_csv(csv_path)


def fig1_paradox_demonstration(save_dir):
    """Figure 1: Visual demonstration of Simpson's paradox in each dataset."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))

    # 1a: Kidney Stone
    ax = axes[0, 0]
    categories = ['Overall', 'Small\nStones', 'Large\nStones']
    treat_a = [78.0, 93.1, 73.0]
    treat_b = [82.6, 86.7, 68.8]
    x = np.arange(len(categories))
    w = 0.35
    bars_a = ax.bar(x - w/2, treat_a, w, label='Treatment A\n(Open Surgery)', color='#2196F3', alpha=0.85)
    bars_b = ax.bar(x + w/2, treat_b, w, label='Treatment B\n(PCNL)', color='#FF5722', alpha=0.85)
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('1. Kidney Stone (Charig et al. 1986)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(fontsize=9, loc='lower left')
    ax.set_ylim(60, 100)
    ax.axhline(y=80, color='gray', linestyle='--', alpha=0.3)
    # Annotate paradox arrow
    ax.annotate('', xy=(0.15, 84), xytext=(0.15, 77),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.text(0.4, 80, 'Reversal!', color='red', fontsize=10, fontweight='bold')

    # 1b: UC Berkeley
    ax = axes[0, 1]
    depts = ['A', 'B', 'C', 'D', 'E', 'F', 'Overall']
    male_rates = [62, 63, 37, 33, 28, 6, 46]
    female_rates = [82, 68, 34, 35, 24, 7, 30]
    x = np.arange(len(depts))
    ax.bar(x - w/2, male_rates, w, label='Male', color='#1976D2', alpha=0.85)
    ax.bar(x + w/2, female_rates, w, label='Female', color='#E91E63', alpha=0.85)
    ax.set_ylabel('Admission Rate (%)')
    ax.set_title('2. UC Berkeley (Bickel et al. 1975)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(depts)
    ax.set_xlabel('Department')
    ax.legend(fontsize=9)
    ax.axvline(x=5.5, color='red', linestyle='--', alpha=0.5)
    ax.text(6.0, 70, 'Reversal!', color='red', fontsize=10, fontweight='bold')

    # 1c: COVID-19 CFR
    ax = axes[0, 2]
    age_groups = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+', 'Overall']
    china_cfr = [0, 0.18, 0.19, 0.24, 0.44, 1.30, 3.60, 7.97, 14.77, 2.29]
    italy_cfr = [0, 0, 0, 0, 0.59, 0.39, 1.20, 5.14, 12.24, 4.08]
    x = np.arange(len(age_groups))
    ax.bar(x - w/2, china_cfr, w, label='China', color='#F44336', alpha=0.85)
    ax.bar(x + w/2, italy_cfr, w, label='Italy', color='#4CAF50', alpha=0.85)
    ax.set_ylabel('CFR (%)')
    ax.set_title('3. COVID-19 CFR (von Kügelgen et al. 2021)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(age_groups, rotation=45, ha='right', fontsize=8)
    ax.legend(fontsize=9)
    ax.axvline(x=8.5, color='red', linestyle='--', alpha=0.5)
    ax.text(8.7, 12, 'Reversal!', color='red', fontsize=10, fontweight='bold')

    # 1d: Smoking Mortality
    ax = axes[1, 0]
    age_grps = ['18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75+', 'Overall']
    smoker_mort = [3.6, 2.4, 12.8, 20.8, 44.3, 80.6, 100, 23.9]
    nonsmoker_mort = [1.6, 3.2, 5.8, 15.4, 33.1, 78.3, 100, 31.4]
    x = np.arange(len(age_grps))
    ax.bar(x - w/2, smoker_mort, w, label='Smoker', color='#795548', alpha=0.85)
    ax.bar(x + w/2, nonsmoker_mort, w, label='Non-smoker', color='#009688', alpha=0.85)
    ax.set_ylabel('Mortality Rate (%)')
    ax.set_title('4. Smoking Mortality (Appleton et al. 1996)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(age_grps, rotation=45, ha='right', fontsize=9)
    ax.legend(fontsize=9)
    ax.axvline(x=6.5, color='red', linestyle='--', alpha=0.5)
    ax.text(6.7, 80, 'Reversal!', color='red', fontsize=10, fontweight='bold')

    # 1e: Israel Vaccine
    ax = axes[1, 1]
    groups = ['<60', '≥60', 'Overall']
    vacc_rate = [0.31, 15.55, 3.96]
    unvacc_rate = [3.31, 24.00, 6.07]
    x = np.arange(len(groups))
    ax.bar(x - w/2, vacc_rate, w, label='Vaccinated', color='#4CAF50', alpha=0.85)
    ax.bar(x + w/2, unvacc_rate, w, label='Unvaccinated', color='#F44336', alpha=0.85)
    ax.set_ylabel('Severe Case Rate (per 1000)')
    ax.set_title('5. Israel Vaccine (Morris 2021)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.legend(fontsize=9)
    ax.text(1.5, 20, 'Vaccine effective\nin both groups', color='green', fontsize=9, fontweight='bold')

    # 1f: Summary diagram
    ax = axes[1, 2]
    ax.axis('off')
    summary_text = (
        "Simpson's Paradox: Common Mechanism\n\n"
        "1. Hidden confounder Z exists\n"
        "   (age, stone size, department, etc.)\n\n"
        "2. Z affects exposure distribution\n"
        "   (severe cases -> surgery A, etc.)\n\n"
        "3. Overall vs within-group reversal\n\n"
        "4. Our proposal:\n"
        "   Detect Z structure from general\n"
        "   variables X -> split into\n"
        "   coherent subpopulations"
    )
    ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
            fontsize=12, verticalalignment='top', fontfamily='sans-serif',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    path = os.path.join(save_dir, 'fig1_paradox_demonstration.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def fig2_method_comparison(df, save_dir):
    """Figure 2: Method comparison across all datasets (ARI, NMI, C1, C4)."""
    # Best n_strata for each dataset (use the one with best oracle)
    methods_to_show = ['1A_predicted_prob', '1B_residual', '1C_cv_decision',
                       '1D_ml_uncertainty', '2A_pca', '2B_clustering', 'random', 'oracle']
    method_labels = ['1A\nPred.Prob', '1B\nResidual', '1C\nCV-Decision', '1D\nML-Uncert.',
                     '2A\nPCA', '2B\nClustering', 'Random', 'Oracle']

    datasets = ['COVID-19 CFR', 'Kidney Stone', 'UC Berkeley', 'Israel Vaccine', 'Smoking Mortality']
    colors = ['#2196F3', '#FF5722', '#4CAF50', '#FF9800', '#9C27B0']

    fig, axes = plt.subplots(2, 2, figsize=(18, 13))
    metrics = [('ARI', 'Adjusted Rand Index'), ('NMI', 'Normalized Mutual Information'),
               ('C1', 'Coherence C1 (1 - I²)'), ('C4', 'Coherence C4 (Entropy-based)')]

    for ax_idx, (metric, metric_label) in enumerate(metrics):
        ax = axes[ax_idx // 2, ax_idx % 2]
        x = np.arange(len(methods_to_show))
        width = 0.15
        offsets = np.linspace(-2 * width, 2 * width, len(datasets))

        for ds_idx, ds_name in enumerate(datasets):
            ds_df = df[df['dataset'] == ds_name]
            values = []
            for m in methods_to_show:
                m_df = ds_df[ds_df['method'] == m]
                if len(m_df) > 0:
                    # Pick best n_strata
                    if m == 'oracle':
                        values.append(m_df[metric].values[0])
                    else:
                        best_idx = m_df['ARI'].idxmax()
                        values.append(m_df.loc[best_idx, metric])
                else:
                    values.append(0)
            ax.bar(x + offsets[ds_idx], values, width, label=ds_name if ax_idx == 0 else '',
                   color=colors[ds_idx], alpha=0.8)

        ax.set_title(metric_label, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(method_labels, fontsize=9)
        ax.grid(axis='y', alpha=0.3)
        if ax_idx == 0:
            ax.legend(fontsize=9, ncol=3, loc='upper right')

    plt.suptitle('Method Comparison Across Simpson\'s Paradox Datasets', fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()
    path = os.path.join(save_dir, 'fig2_method_comparison.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def fig3_coherence_analysis(df, save_dir):
    """Figure 3: Coherence C1 comparison - random vs proposed methods vs oracle."""
    datasets = ['COVID-19 CFR', 'Kidney Stone', 'UC Berkeley', 'Israel Vaccine', 'Smoking Mortality']
    method_groups = {
        'Random': 'random',
        'Best Method 1\n(Decision Power)': None,  # will pick best of 1A-1D
        'Best Method 2\n(Feature Score)': None,    # will pick best of 2A-2B
        'Oracle': 'oracle',
    }

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # C1 values
    ax = axes[0]
    bar_data = {ds: [] for ds in datasets}
    group_labels = list(method_groups.keys())

    for ds_name in datasets:
        ds_df = df[df['dataset'] == ds_name]

        # Random
        rand_df = ds_df[ds_df['method'] == 'random']
        bar_data[ds_name].append(rand_df['C1'].mean() if len(rand_df) > 0 else 1.0)

        # Best Method 1
        m1_methods = ['1A_predicted_prob', '1B_residual', '1C_cv_decision', '1D_ml_uncertainty']
        m1_df = ds_df[ds_df['method'].isin(m1_methods)]
        if len(m1_df) > 0:
            best_ari_idx = m1_df['ARI'].idxmax()
            bar_data[ds_name].append(m1_df.loc[best_ari_idx, 'C1'])
        else:
            bar_data[ds_name].append(1.0)

        # Best Method 2
        m2_methods = ['2A_pca', '2B_clustering']
        m2_df = ds_df[ds_df['method'].isin(m2_methods)]
        if len(m2_df) > 0:
            best_ari_idx = m2_df['ARI'].idxmax()
            bar_data[ds_name].append(m2_df.loc[best_ari_idx, 'C1'])
        else:
            bar_data[ds_name].append(1.0)

        # Oracle
        oracle_df = ds_df[ds_df['method'] == 'oracle']
        bar_data[ds_name].append(oracle_df['C1'].values[0] if len(oracle_df) > 0 else 1.0)

    x = np.arange(len(group_labels))
    width = 0.15
    colors = ['#2196F3', '#FF5722', '#4CAF50', '#FF9800', '#9C27B0']
    for i, ds_name in enumerate(datasets):
        offset = (i - 2) * width
        ax.bar(x + offset, bar_data[ds_name], width, label=ds_name, color=colors[i], alpha=0.85)

    ax.set_title('C1 (Coherence): Lower = More Heterogeneous\n(Stratification Detected Subgroups)', fontweight='bold')
    ax.set_ylabel('C1 Value')
    ax.set_xticks(x)
    ax.set_xticklabels(group_labels, fontsize=10)
    ax.legend(fontsize=8, ncol=2)
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.4, label='Threshold suggestion')

    # ARI comparison
    ax = axes[1]
    ari_data = {ds: [] for ds in datasets}
    for ds_name in datasets:
        ds_df = df[df['dataset'] == ds_name]
        rand_df = ds_df[ds_df['method'] == 'random']
        ari_data[ds_name].append(max(rand_df['ARI'].mean(), 0) if len(rand_df) > 0 else 0)
        m1_df = ds_df[ds_df['method'].isin(m1_methods)]
        if len(m1_df) > 0:
            ari_data[ds_name].append(m1_df['ARI'].max())
        else:
            ari_data[ds_name].append(0)
        m2_df = ds_df[ds_df['method'].isin(m2_methods)]
        if len(m2_df) > 0:
            ari_data[ds_name].append(m2_df['ARI'].max())
        else:
            ari_data[ds_name].append(0)
        oracle_df = ds_df[ds_df['method'] == 'oracle']
        ari_data[ds_name].append(oracle_df['ARI'].values[0] if len(oracle_df) > 0 else 1.0)

    for i, ds_name in enumerate(datasets):
        offset = (i - 2) * width
        ax.bar(x + offset, ari_data[ds_name], width, label=ds_name, color=colors[i], alpha=0.85)

    ax.set_title('ARI (Cluster Agreement with True Groups)', fontweight='bold')
    ax.set_ylabel('ARI')
    ax.set_xticks(x)
    ax.set_xticklabels(group_labels, fontsize=10)
    ax.legend(fontsize=8, ncol=2)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    path = os.path.join(save_dir, 'fig3_coherence_analysis.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def fig4_eta_squared_heatmap(df, save_dir):
    """Figure 4: Eta-squared heatmap for each dataset x method."""
    datasets = ['Kidney Stone', 'UC Berkeley', 'COVID-19 CFR', 'Israel Vaccine', 'Smoking Mortality']
    methods = ['1A_predicted_prob', '1B_residual', '1C_cv_decision',
               '1D_ml_uncertainty', '2A_pca', '2B_clustering', 'random', 'oracle']
    method_labels = ['1A Pred.Prob', '1B Residual', '1C CV-Decision', '1D ML-Uncert.',
                     '2A PCA', '2B Clustering', 'Random', 'Oracle']

    eta_matrix = np.zeros((len(datasets), len(methods)))
    for i, ds in enumerate(datasets):
        ds_df = df[df['dataset'] == ds]
        for j, m in enumerate(methods):
            m_df = ds_df[ds_df['method'] == m]
            if len(m_df) > 0 and 'eta2_mean' in m_df.columns:
                vals = m_df['eta2_mean'].dropna()
                if len(vals) > 0:
                    eta_matrix[i, j] = vals.max()

    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.imshow(eta_matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels(method_labels, rotation=45, ha='right')
    ax.set_yticks(range(len(datasets)))
    ax.set_yticklabels(datasets)
    ax.set_title('η² (Eta-Squared): Proportion of Hidden Variable Variance\nExplained by Stratification',
                 fontweight='bold')

    for i in range(len(datasets)):
        for j in range(len(methods)):
            color = 'white' if eta_matrix[i, j] > 0.5 else 'black'
            ax.text(j, i, f'{eta_matrix[i, j]:.3f}', ha='center', va='center',
                    color=color, fontsize=10, fontweight='bold')

    plt.colorbar(im, ax=ax, label='η²')
    plt.tight_layout()
    path = os.path.join(save_dir, 'fig4_eta_squared_heatmap.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def fig5_direction_consistency(df, save_dir):
    """Figure 5: Simpson's paradox resolution - direction consistency rate."""
    datasets = ['COVID-19 CFR', 'Kidney Stone', 'UC Berkeley', 'Israel Vaccine', 'Smoking Mortality']
    methods = ['1A_predicted_prob', '1B_residual', '2B_clustering', 'random', 'oracle']
    method_labels = ['1A Pred.Prob', '1B Residual', '2B Clustering', 'Random', 'Oracle']
    colors_m = ['#2196F3', '#FF5722', '#4CAF50', '#9E9E9E', '#FFD700']

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(datasets))
    width = 0.15

    for j, (m, m_label) in enumerate(zip(methods, method_labels)):
        vals = []
        for ds in datasets:
            ds_df = df[(df['dataset'] == ds) & (df['method'] == m)]
            if len(ds_df) > 0:
                vals.append(ds_df['direction_consistency'].mean())
            else:
                vals.append(0)
        offset = (j - 2) * width
        ax.bar(x + offset, vals, width, label=m_label, color=colors_m[j], alpha=0.85)

    ax.set_title('Direction Consistency Rate\n(Higher = Simpson\'s Paradox Better Resolved)', fontweight='bold')
    ax.set_ylabel('Direction Consistency')
    ax.set_xticks(x)
    ax.set_xticklabels(datasets, rotation=15, ha='right')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 1.1)
    ax.axhline(y=1.0, color='green', linestyle='--', alpha=0.3)

    plt.tight_layout()
    path = os.path.join(save_dir, 'fig5_direction_consistency.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def fig6_summary_dashboard(df, save_dir):
    """Figure 6: Summary dashboard - best method per dataset."""
    datasets = ['COVID-19 CFR', 'Kidney Stone', 'UC Berkeley', 'Israel Vaccine', 'Smoking Mortality']
    proposed_methods = ['1A_predicted_prob', '1B_residual', '1C_cv_decision',
                        '1D_ml_uncertainty', '2A_pca', '2B_clustering']

    summary_rows = []
    for ds in datasets:
        ds_df = df[df['dataset'] == ds]
        # Best proposed method by ARI
        prop_df = ds_df[ds_df['method'].isin(proposed_methods)]
        if len(prop_df) > 0:
            best_idx = prop_df['ARI'].idxmax()
            best_row = prop_df.loc[best_idx]
            best_method = best_row['method']
            best_ari = best_row['ARI']
            best_nmi = best_row['NMI']
            best_c1 = best_row['C1']
            best_c4 = best_row['C4']
        else:
            best_method = 'N/A'
            best_ari = best_nmi = best_c1 = best_c4 = 0

        rand_df = ds_df[ds_df['method'] == 'random']
        rand_ari = rand_df['ARI'].mean() if len(rand_df) > 0 else 0

        oracle_df = ds_df[ds_df['method'] == 'oracle']
        oracle_ari = oracle_df['ARI'].values[0] if len(oracle_df) > 0 else 1.0
        oracle_c1 = oracle_df['C1'].values[0] if len(oracle_df) > 0 else 1.0

        summary_rows.append({
            'Dataset': ds,
            'Best Method': best_method,
            'ARI': best_ari,
            'NMI': best_nmi,
            'C1': best_c1,
            'C4': best_c4,
            'Random ARI': rand_ari,
            'Oracle ARI': oracle_ari,
            'Oracle C1': oracle_c1,
        })

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis('off')

    col_labels = ['Dataset', 'Best Method', 'ARI', 'NMI', 'C1', 'C4',
                  'Random\nARI', 'Oracle\nARI', 'Oracle\nC1']
    cell_text = []
    for r in summary_rows:
        cell_text.append([
            r['Dataset'],
            r['Best Method'].replace('_', '\n'),
            f"{r['ARI']:.4f}",
            f"{r['NMI']:.4f}",
            f"{r['C1']:.4f}",
            f"{r['C4']:.4f}",
            f"{r['Random ARI']:.4f}",
            f"{r['Oracle ARI']:.4f}",
            f"{r['Oracle C1']:.4f}",
        ])

    table = ax.table(cellText=cell_text, colLabels=col_labels,
                     cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.2)

    # Color header
    for j in range(len(col_labels)):
        table[0, j].set_facecolor('#1976D2')
        table[0, j].set_text_props(color='white', fontweight='bold')

    # Color ARI cells based on value
    for i in range(len(summary_rows)):
        ari_val = summary_rows[i]['ARI']
        if ari_val > 0.5:
            table[i + 1, 2].set_facecolor('#C8E6C9')
        elif ari_val > 0.1:
            table[i + 1, 2].set_facecolor('#FFF9C4')
        else:
            table[i + 1, 2].set_facecolor('#FFCDD2')

    ax.set_title('Summary: Best Proposed Method per Dataset', fontsize=15, fontweight='bold', pad=20)
    plt.tight_layout()
    path = os.path.join(save_dir, 'fig6_summary_dashboard.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")
    return path


def main():
    df = load_results()
    print(f"Loaded {len(df)} evaluation records")
    print(f"Datasets: {df['dataset'].unique()}")

    paths = []
    paths.append(fig1_paradox_demonstration(RESULTS_DIR))
    paths.append(fig2_method_comparison(df, RESULTS_DIR))
    paths.append(fig3_coherence_analysis(df, RESULTS_DIR))
    paths.append(fig4_eta_squared_heatmap(df, RESULTS_DIR))
    paths.append(fig5_direction_consistency(df, RESULTS_DIR))
    paths.append(fig6_summary_dashboard(df, RESULTS_DIR))

    print(f"\nAll {len(paths)} figures generated.")
    return paths


if __name__ == '__main__':
    main()
