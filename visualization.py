"""
Visualization module: Generate all plots from simulation results.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import os

# Japanese font support
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['figure.facecolor'] = 'white'

OUTPUT_DIR = 'results/figures'


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _method_display_name(m: str) -> str:
    """Convert method code to display name."""
    names = {
        '1A_predicted_prob': '1A: Pred.Prob',
        '1B_residual': '1B: Residual',
        '1C_cv_decision': '1C: CV-Decision',
        '1D_ml_uncertainty': '1D: ML-Uncert.',
        '2A_PCA_cum40': '2A: PCA(40%)',
        '2A_PCA_cum60': '2A: PCA(60%)',
        '2A_PCA_cum80': '2A: PCA(80%)',
        '2A_PCA_k1': '2A: PCA(k=1)',
        '2A_PCA_k2': '2A: PCA(k=2)',
        '2A_PCA_k3': '2A: PCA(k=3)',
        '2B_clustering': '2B: Clustering',
        '2C_autoencoder': '2C: AutoEnc.',
        '2D_rf_proximity': '2D: RF-Prox.',
        'baseline_random': 'Random',
        'baseline_oracle_kmeans': 'Oracle(k-means)',
        'baseline_oracle_quantile': 'Oracle(quantile)',
    }
    return names.get(m, m)


def _method_color(m: str) -> str:
    """Color coding by method family."""
    if m.startswith('1'):
        return '#2196F3'  # Blue for Method 1
    elif m.startswith('2A'):
        return '#4CAF50'  # Green for PCA
    elif m.startswith('2'):
        return '#8BC34A'  # Light green for other Method 2
    elif 'oracle' in m:
        return '#FF9800'  # Orange for oracle
    elif 'random' in m:
        return '#9E9E9E'  # Gray for random
    return '#607D8B'


# ============================================================
# 1. Heatmap: ARI/NMI by method x parameter
# ============================================================

def plot_heatmap_ari_nmi(df: pd.DataFrame, filename: str = 'heatmap_ari_nmi.png'):
    """Heatmap of ARI and NMI across methods and Z->X influence strengths."""
    ensure_output_dir()

    df_clean = df[df['error'].isna()].copy()

    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    for col_idx, metric in enumerate(['ARI', 'NMI']):
        for row_idx, n_strata in enumerate(sorted(df_clean['n_strata'].unique())):
            ax = axes[row_idx, col_idx]
            subset = df_clean[df_clean['n_strata'] == n_strata]

            pivot = subset.pivot_table(
                values=metric,
                index='method',
                columns='zx_influence_scale',
                aggfunc='mean'
            )

            # Sort by mean performance
            pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

            # Rename for display
            pivot.index = [_method_display_name(m) for m in pivot.index]

            sns.heatmap(pivot, annot=True, fmt='.3f', cmap='YlOrRd',
                        vmin=0, vmax=max(0.5, pivot.max().max()),
                        ax=ax, cbar_kws={'label': metric})
            ax.set_title(f'{metric} (n_strata={n_strata})', fontsize=12, fontweight='bold')
            ax.set_xlabel('Z->X Influence Scale')
            ax.set_ylabel('')

    plt.suptitle('Cluster Agreement: ARI & NMI by Method and Z->X Influence',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


# ============================================================
# 2. Coherence indicators comparison
# ============================================================

def plot_coherence_comparison(df: pd.DataFrame, filename: str = 'coherence_comparison.png'):
    """Compare coherence indicators (C1-C4) across methods."""
    ensure_output_dir()

    df_clean = df[df['error'].isna()].copy()

    coherence_cols = ['C1_heterogeneity', 'C2_residual_structure',
                      'C3_prediction_stability', 'C4_entropy']

    # Filter to representative scenario
    mask = (df_clean['zx_influence_scale'] == 1.0) & (df_clean['n_strata'] == 5)
    subset = df_clean[mask]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    for idx, col in enumerate(coherence_cols):
        ax = axes[idx // 2, idx % 2]

        method_means = subset.groupby('method')[col].agg(['mean', 'std']).reset_index()
        method_means = method_means.sort_values('mean', ascending=True)
        method_means['display'] = method_means['method'].apply(_method_display_name)

        colors = [_method_color(m) for m in method_means['method']]
        ax.barh(method_means['display'], method_means['mean'],
                xerr=method_means['std'], color=colors, edgecolor='white', capsize=3)
        ax.set_xlabel(col.replace('_', ' ').title())
        ax.set_title(col, fontsize=12, fontweight='bold')
        ax.axvline(x=0.7, color='red', linestyle='--', alpha=0.5, label='Threshold (0.7)')
        ax.set_xlim(0, 1.05)
        ax.legend(fontsize=8)

    plt.suptitle('Coherence Indicators by Method (zx_scale=1.0, n_strata=5)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


# ============================================================
# 3. Eta-squared: Z capture by method
# ============================================================

def plot_eta_squared(df: pd.DataFrame, filename: str = 'eta_squared.png'):
    """Visualize how well each method captures Z variables."""
    ensure_output_dir()

    df_clean = df[df['error'].isna()].copy()

    eta_cols = ['eta2_Z1_age', 'eta2_Z2_sex', 'eta2_Z3_bmi']
    z_labels = ['Z1 (Age)', 'Z2 (Sex)', 'Z3 (BMI)']

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    mask = (df_clean['n_strata'] == 5)
    subset = df_clean[mask]

    for idx, (col, zlabel) in enumerate(zip(eta_cols, z_labels)):
        ax = axes[idx]

        # Group by method and zx_scale
        for zx in sorted(subset['zx_influence_scale'].unique()):
            sub = subset[subset['zx_influence_scale'] == zx]
            method_means = sub.groupby('method')[col].mean().sort_values(ascending=False)

            x_pos = np.arange(len(method_means))
            labels = [_method_display_name(m) for m in method_means.index]
            ax.plot(x_pos, method_means.values, 'o-', label=f'zx={zx}', markersize=4)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)

        ax.set_title(f'eta-squared: {zlabel}', fontsize=12, fontweight='bold')
        ax.set_ylabel('eta-squared')
        ax.legend(title='Z->X scale')
        ax.set_ylim(0, None)

    plt.suptitle('Z Variable Capture (eta-squared) by Method',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


# ============================================================
# 4. Simpson's Paradox Resolution
# ============================================================

def plot_simpson_resolution(df: pd.DataFrame, filename: str = 'simpson_resolution.png'):
    """Simpson's paradox direction consistency rate by method."""
    ensure_output_dir()

    df_clean = df[df['error'].isna()].copy()

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for idx, n_strata in enumerate(sorted(df_clean['n_strata'].unique())):
        ax = axes[idx]
        subset = df_clean[df_clean['n_strata'] == n_strata]

        method_stats = subset.groupby('method')['direction_consistency_rate'].agg(['mean', 'std'])
        method_stats = method_stats.sort_values('mean', ascending=True)
        method_stats.index = [_method_display_name(m) for m in method_stats.index]

        colors = [_method_color(m.split(':')[0].strip() if ':' in m else m)
                  for m in method_stats.index]

        ax.barh(method_stats.index, method_stats['mean'],
                xerr=method_stats['std'], color='#42A5F5', edgecolor='white', capsize=3)
        ax.set_xlabel('Direction Consistency Rate')
        ax.set_title(f'Simpson\'s Paradox Resolution (n_strata={n_strata})',
                     fontsize=12, fontweight='bold')
        ax.set_xlim(0, 1.05)
        ax.axvline(x=1.0, color='green', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


# ============================================================
# 5. Bias reduction plot
# ============================================================

def plot_bias_reduction(df: pd.DataFrame, filename: str = 'bias_reduction.png'):
    """Compare crude vs stratified bias for each method."""
    ensure_output_dir()

    df_clean = df[df['error'].isna()].copy()

    fig, ax = plt.subplots(figsize=(14, 7))

    mask = (df_clean['n_strata'] == 5) & (df_clean['zx_influence_scale'] == 1.0)
    subset = df_clean[mask]

    method_bias = subset.groupby('method')[['bias_crude', 'bias_stratified']].mean()
    method_bias = method_bias.sort_values('bias_stratified')
    method_bias.index = [_method_display_name(m) for m in method_bias.index]

    x = np.arange(len(method_bias))
    width = 0.35

    ax.bar(x - width/2, method_bias['bias_crude'], width, label='Crude (no stratification)',
           color='#EF5350', alpha=0.8)
    ax.bar(x + width/2, method_bias['bias_stratified'], width, label='After Stratification',
           color='#42A5F5', alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(method_bias.index, rotation=45, ha='right')
    ax.set_ylabel('Absolute Bias')
    ax.set_title('Effect Estimation Bias: Crude vs Stratified (zx_scale=1.0, n_strata=5)',
                 fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


# ============================================================
# 6. PCA cumulative contribution rate analysis
# ============================================================

def plot_pca_contribution_analysis(df: pd.DataFrame, filename: str = 'pca_contribution.png'):
    """Analyze how PCA cumulative contribution rate affects method performance."""
    ensure_output_dir()

    df_clean = df[df['error'].isna()].copy()

    pca_methods = [m for m in df_clean['method'].unique() if m.startswith('2A_PCA')]
    if not pca_methods:
        print("No PCA methods found, skipping.")
        return

    subset = df_clean[df_clean['method'].isin(pca_methods)]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    metrics = ['ARI', 'NMI', 'C1_heterogeneity', 'C4_entropy']
    titles = ['ARI (Cluster Agreement)', 'NMI (Mutual Information)',
              'C1 (Coherence: Heterogeneity)', 'C4 (Coherence: Entropy)']

    for idx, (metric, title) in enumerate(zip(metrics, titles)):
        ax = axes[idx // 2, idx % 2]

        for zx in sorted(subset['zx_influence_scale'].unique()):
            sub = subset[subset['zx_influence_scale'] == zx]
            means = sub.groupby('method')[metric].mean()
            labels = [_method_display_name(m) for m in means.index]
            ax.plot(labels, means.values, 'o-', label=f'zx={zx}', markersize=6)

        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_ylabel(metric)
        ax.legend(title='Z->X scale', fontsize=8)
        ax.tick_params(axis='x', rotation=30)
        ax.grid(alpha=0.3)

    plt.suptitle('PCA Cumulative Contribution Rate vs Performance',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


# ============================================================
# 7. Sensitivity analysis: sample size effect
# ============================================================

def plot_sensitivity_sample_size(df: pd.DataFrame, filename: str = 'sensitivity_sample_size.png'):
    """Show how sample size affects method performance."""
    ensure_output_dir()

    df_clean = df[df['error'].isna()].copy()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    metrics = ['ARI', 'C1_heterogeneity', 'eta2_mean', 'bias_stratified']
    titles = ['ARI', 'C1 (Coherence)', 'Mean eta-squared', 'Stratified Bias']

    for idx, (metric, title) in enumerate(zip(metrics, titles)):
        ax = axes[idx // 2, idx % 2]

        for method in sorted(df_clean['method'].unique()):
            sub = df_clean[df_clean['method'] == method]
            if metric not in sub.columns or sub[metric].isna().all():
                continue
            means = sub.groupby('n')[metric].mean()
            display = _method_display_name(method)
            color = _method_color(method)
            ax.plot(means.index, means.values, 'o-', label=display,
                    color=color, markersize=4, linewidth=1.5)

        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlabel('Sample Size (N)')
        ax.set_ylabel(metric)
        ax.set_xscale('log')
        ax.grid(alpha=0.3)

    # Put legend outside
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='center right', bbox_to_anchor=(1.18, 0.5),
               fontsize=8, title='Method')

    plt.suptitle('Sensitivity Analysis: Effect of Sample Size',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


# ============================================================
# 8. Sensitivity: Z->X influence strength
# ============================================================

def plot_sensitivity_zx_influence(df: pd.DataFrame, filename: str = 'sensitivity_zx_influence.png'):
    """Show how Z->X influence strength affects detection."""
    ensure_output_dir()

    df_clean = df[df['error'].isna()].copy()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    metrics = ['ARI', 'C4_entropy', 'eta2_mean', 'bias_reduction']
    titles = ['ARI', 'C4 (Entropy Coherence)', 'Mean eta-squared', 'Bias Reduction']

    for idx, (metric, title) in enumerate(zip(metrics, titles)):
        ax = axes[idx // 2, idx % 2]

        for method in sorted(df_clean['method'].unique()):
            sub = df_clean[df_clean['method'] == method]
            if metric not in sub.columns or sub[metric].isna().all():
                continue
            means = sub.groupby('zx_influence_scale')[metric].mean()
            display = _method_display_name(method)
            color = _method_color(method)
            ax.plot(means.index, means.values, 'o-', label=display,
                    color=color, markersize=4, linewidth=1.5)

        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlabel('Z->X Influence Scale')
        ax.set_ylabel(metric)
        ax.grid(alpha=0.3)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='center right', bbox_to_anchor=(1.18, 0.5),
               fontsize=8, title='Method')

    plt.suptitle('Sensitivity Analysis: Effect of Z->X Influence Strength',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


# ============================================================
# 9. Comprehensive summary dashboard
# ============================================================

def plot_summary_dashboard(df: pd.DataFrame, filename: str = 'summary_dashboard.png'):
    """Single dashboard with key findings."""
    ensure_output_dir()

    df_clean = df[df['error'].isna()].copy()

    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

    # --- Panel 1: Overall method ranking by ARI ---
    ax1 = fig.add_subplot(gs[0, 0])
    mask = df_clean['n_strata'] == 5
    ranking = df_clean[mask].groupby('method')['ARI'].mean().sort_values(ascending=True)
    colors = [_method_color(m) for m in ranking.index]
    labels = [_method_display_name(m) for m in ranking.index]
    ax1.barh(labels, ranking.values, color=colors, edgecolor='white')
    ax1.set_title('Method Ranking: ARI', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Mean ARI')

    # --- Panel 2: Overall method ranking by C1 ---
    ax2 = fig.add_subplot(gs[0, 1])
    ranking_c1 = df_clean[mask].groupby('method')['C1_heterogeneity'].mean().sort_values(ascending=True)
    colors_c1 = [_method_color(m) for m in ranking_c1.index]
    labels_c1 = [_method_display_name(m) for m in ranking_c1.index]
    ax2.barh(labels_c1, ranking_c1.values, color=colors_c1, edgecolor='white')
    ax2.set_title('Method Ranking: C1 (Coherence)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Mean C1')
    ax2.axvline(x=0.7, color='red', linestyle='--', alpha=0.5)

    # --- Panel 3: C4 (entropy) ranking ---
    ax3 = fig.add_subplot(gs[0, 2])
    ranking_c4 = df_clean[mask].groupby('method')['C4_entropy'].mean().sort_values(ascending=True)
    colors_c4 = [_method_color(m) for m in ranking_c4.index]
    labels_c4 = [_method_display_name(m) for m in ranking_c4.index]
    ax3.barh(labels_c4, ranking_c4.values, color=colors_c4, edgecolor='white')
    ax3.set_title('Method Ranking: C4 (Entropy)', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Mean C4')

    # --- Panel 4: ARI vs zx_influence heatmap ---
    ax4 = fig.add_subplot(gs[1, 0:2])
    pivot = df_clean[df_clean['n_strata'] == 5].pivot_table(
        values='ARI', index='method', columns='zx_influence_scale', aggfunc='mean'
    )
    pivot.index = [_method_display_name(m) for m in pivot.index]
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]
    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax4,
                vmin=0, cbar_kws={'label': 'ARI'})
    ax4.set_title('ARI by Method x Z->X Influence (n_strata=5)', fontsize=11, fontweight='bold')

    # --- Panel 5: Bias comparison ---
    ax5 = fig.add_subplot(gs[1, 2])
    mask2 = (df_clean['n_strata'] == 5) & (df_clean['zx_influence_scale'] == 1.0)
    bias_data = df_clean[mask2].groupby('method')[['bias_crude', 'bias_stratified']].mean()
    bias_data = bias_data.sort_values('bias_stratified')
    bias_data.index = [_method_display_name(m) for m in bias_data.index]
    bias_data.plot(kind='barh', ax=ax5, color=['#EF5350', '#42A5F5'], edgecolor='white')
    ax5.set_title('Bias Comparison', fontsize=11, fontweight='bold')
    ax5.set_xlabel('Absolute Bias')
    ax5.legend(['Crude', 'Stratified'], fontsize=8)

    # --- Panel 6: eta-squared summary ---
    ax6 = fig.add_subplot(gs[2, 0])
    eta_means = df_clean[mask].groupby('method')['eta2_mean'].mean().sort_values(ascending=True)
    labels_eta = [_method_display_name(m) for m in eta_means.index]
    colors_eta = [_method_color(m) for m in eta_means.index]
    ax6.barh(labels_eta, eta_means.values, color=colors_eta, edgecolor='white')
    ax6.set_title('Mean eta-squared (Z capture)', fontsize=11, fontweight='bold')
    ax6.set_xlabel('Mean eta-squared')

    # --- Panel 7: Simpson resolution ---
    ax7 = fig.add_subplot(gs[2, 1])
    simpson = df_clean[mask].groupby('method')['direction_consistency_rate'].mean().sort_values(ascending=True)
    labels_s = [_method_display_name(m) for m in simpson.index]
    ax7.barh(labels_s, simpson.values, color='#66BB6A', edgecolor='white')
    ax7.set_title('Simpson\'s Paradox Resolution', fontsize=11, fontweight='bold')
    ax7.set_xlabel('Direction Consistency Rate')

    # --- Panel 8: SMD ---
    ax8 = fig.add_subplot(gs[2, 2])
    smd = df_clean[mask].groupby('method')['mean_max_SMD'].mean().sort_values(ascending=False)
    labels_smd = [_method_display_name(m) for m in smd.index]
    colors_smd = [_method_color(m) for m in smd.index]
    ax8.barh(labels_smd, smd.values, color=colors_smd, edgecolor='white')
    ax8.set_title('Max SMD (Z imbalance)', fontsize=11, fontweight='bold')
    ax8.set_xlabel('Mean Max SMD')
    ax8.axvline(x=0.1, color='green', linestyle='--', alpha=0.5, label='Good (<0.1)')
    ax8.legend(fontsize=8)

    plt.suptitle('Stratification Methods: Comprehensive Results Dashboard',
                 fontsize=16, fontweight='bold', y=1.01)
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


# ============================================================
# 10. Coherence diagnosis report (example output)
# ============================================================

def plot_coherence_diagnosis_example(df: pd.DataFrame, filename: str = 'coherence_diagnosis.png'):
    """Generate an example coherence diagnosis report visualization."""
    ensure_output_dir()

    # Use best method's results for the example
    df_clean = df[df['error'].isna()].copy()
    mask = (df_clean['n_strata'] == 5) & (df_clean['zx_influence_scale'] == 1.0)
    subset = df_clean[mask]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Panel 1: Coherence degree distribution across methods
    ax = axes[0]
    methods_of_interest = [m for m in subset['method'].unique()
                           if not m.startswith('baseline')]
    c1_data = []
    labels = []
    for m in sorted(methods_of_interest):
        vals = subset[subset['method'] == m]['C1_heterogeneity'].values
        c1_data.append(vals)
        labels.append(_method_display_name(m))

    bp = ax.boxplot(c1_data, labels=labels, vert=True, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('#42A5F5')
        patch.set_alpha(0.7)
    ax.axhline(y=0.7, color='red', linestyle='--', alpha=0.7, label='Threshold')
    ax.set_title('C1 Distribution by Method', fontsize=11, fontweight='bold')
    ax.set_ylabel('C1 (Coherence)')
    ax.tick_params(axis='x', rotation=45)
    ax.legend()

    # Panel 2: C1 vs C4 scatter
    ax2 = axes[1]
    for m in sorted(methods_of_interest[:6]):  # top 6
        sub = subset[subset['method'] == m]
        ax2.scatter(sub['C4_entropy'], sub['C1_heterogeneity'],
                    alpha=0.3, s=20, label=_method_display_name(m))
    ax2.set_xlabel('C4 (Entropy-based, simulation only)')
    ax2.set_ylabel('C1 (Heterogeneity-based, applicable to real data)')
    ax2.set_title('C1 vs C4: Coherence Indicator Agreement', fontsize=11, fontweight='bold')
    ax2.legend(fontsize=7, loc='lower right')
    ax2.axhline(y=0.7, color='red', linestyle='--', alpha=0.3)
    ax2.axvline(x=0.3, color='blue', linestyle='--', alpha=0.3)

    # Panel 3: Example diagnosis output
    ax3 = axes[2]
    ax3.axis('off')

    # Get representative results for best method
    best_method = subset.groupby('method')['ARI'].mean().idxmax()
    best_data = subset[subset['method'] == best_method].iloc[0]

    report_text = f"""
    Coherence Diagnosis Report
    {'='*40}

    Method: {_method_display_name(best_method)}
    N strata: 5

    Overall Coherence: C1 = {best_data.get('C1_heterogeneity', 0):.3f}
    {'  -> Sufficiently coherent' if best_data.get('C1_heterogeneity', 0) >= 0.7 else '  -> Sub-analysis RECOMMENDED'}

    Detailed Indicators:
      C1 (heterogeneity):  {best_data.get('C1_heterogeneity', 0):.3f}
      C2 (residual):       {best_data.get('C2_residual_structure', 0):.3f}
      C3 (stability):      {best_data.get('C3_prediction_stability', 0):.3f}
      C4 (entropy):        {best_data.get('C4_entropy', 0):.3f}

    Cluster Agreement:
      ARI:    {best_data.get('ARI', 0):.3f}
      NMI:    {best_data.get('NMI', 0):.3f}

    Z Capture (eta-squared):
      Age:  {best_data.get('eta2_Z1_age', 0):.3f}
      Sex:  {best_data.get('eta2_Z2_sex', 0):.3f}
      BMI:  {best_data.get('eta2_Z3_bmi', 0):.3f}

    Bias Reduction:
      Crude:      {best_data.get('bias_crude', 0):.4f}
      Stratified: {best_data.get('bias_stratified', 0):.4f}
    """

    ax3.text(0.05, 0.95, report_text, transform=ax3.transAxes,
             fontsize=9, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    ax3.set_title('Example Diagnosis Output', fontsize=11, fontweight='bold')

    plt.suptitle('Coherence Diagnosis: From Indicators to Clinical Decision',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")


# ============================================================
# Main: Generate all plots
# ============================================================

def generate_all_plots(phase1_csv: str = 'results/phase1_results.csv',
                       sensitivity_csv: str = 'results/sensitivity_results.csv'):
    """Generate all visualization plots from saved results."""

    print("Loading Phase 1 results...")
    df1 = pd.read_csv(phase1_csv)
    print(f"  {len(df1)} rows, {df1['error'].isna().sum()} successful")

    print("\nGenerating Phase 1 plots...")
    plot_heatmap_ari_nmi(df1)
    plot_coherence_comparison(df1)
    plot_eta_squared(df1)
    plot_simpson_resolution(df1)
    plot_bias_reduction(df1)
    plot_pca_contribution_analysis(df1)
    plot_coherence_diagnosis_example(df1)
    plot_summary_dashboard(df1)

    if os.path.exists(sensitivity_csv):
        print("\nLoading sensitivity results...")
        df2 = pd.read_csv(sensitivity_csv)
        print(f"  {len(df2)} rows, {df2['error'].isna().sum()} successful")

        print("\nGenerating sensitivity plots...")
        plot_sensitivity_sample_size(df2)
        plot_sensitivity_zx_influence(df2)

    print(f"\nAll plots saved to {OUTPUT_DIR}/")


if __name__ == '__main__':
    generate_all_plots()
