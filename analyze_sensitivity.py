"""
Analyze sensitivity results and generate Table 7 content for the manuscript.
"""
import pandas as pd
import numpy as np

def analyze_sensitivity(csv_path='results/sensitivity_results.csv'):
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows, {df['error'].notna().sum()} errors")
    
    # Remove error rows if any
    df_clean = df[df['error'].isna()].copy()
    print(f"Clean rows: {len(df_clean)}")
    
    # Check columns available
    has_W = 'W' in df_clean.columns
    has_bias = 'bias_reduction' in df_clean.columns
    has_C1 = 'C1_heterogeneity' in df_clean.columns
    
    print(f"\nColumns: W={has_W}, bias_reduction={has_bias}, C1={has_C1}")
    print(f"Methods: {sorted(df_clean['method'].unique())}")
    print(f"zx values: {sorted(df_clean['zx_influence_scale'].unique())}")
    print(f"em values: {sorted(df_clean['em_strength'].unique()) if 'em_strength' in df_clean.columns else 'N/A'}")
    print(f"N values: {sorted(df_clean['n'].unique())}")
    print(f"K values: {sorted(df_clean['n_strata'].unique())}")
    
    # --- Table 7: ARI by Z→X influence strength ---
    print("\n" + "="*80)
    print("TABLE 7: ARI (SE) by Z→X influence strength")
    print("="*80)
    
    methods_order = [
        '1A_predicted_prob', '1C_cv_decision',
        '2A_PCA_cum60', '2B_clustering',
        'comp_PS_quintile', 'comp_GMM', 'comp_prognostic',
        'baseline_oracle_kmeans', 'baseline_random'
    ]
    
    method_labels = {
        '1A_predicted_prob': '1A: Predicted probability',
        '1C_cv_decision': '1C: CV decision power',
        '2A_PCA_cum60': '2A: PCA (cum. 60%)',
        '2B_clustering': '2B: Clustering',
        'comp_PS_quintile': 'PS quintiles',
        'comp_GMM': 'GMM',
        'comp_prognostic': 'Prognostic score',
        'baseline_oracle_kmeans': 'Oracle k-means',
        'baseline_random': 'Random baseline',
    }
    
    zx_vals = sorted(df_clean['zx_influence_scale'].unique())
    
    print(f"\n| Method | " + " | ".join([f"zx = {z}" for z in zx_vals]) + " |")
    print("|" + "--------|" * (len(zx_vals) + 1))
    
    table7_rows = []
    for method in methods_order:
        mdf = df_clean[df_clean['method'] == method]
        if len(mdf) == 0:
            continue
        row = [method_labels.get(method, method)]
        for zx in zx_vals:
            subset = mdf[mdf['zx_influence_scale'] == zx]['ARI']
            mean_val = subset.mean()
            se_val = subset.std() / np.sqrt(len(subset))
            row.append(f"{mean_val:.3f} ({se_val:.4f})")
        table7_rows.append(row)
        print(f"| {row[0]:25s} | " + " | ".join(row[1:]) + " |")
    
    # --- Additional: ARI by EM strength ---
    if 'em_strength' in df_clean.columns:
        print("\n" + "="*80)
        print("TABLE 7b: ARI (SE) by EM strength")
        print("="*80)
        
        em_vals = sorted(df_clean['em_strength'].unique())
        print(f"\n| Method | " + " | ".join([f"em = {e}" for e in em_vals]) + " |")
        print("|" + "--------|" * (len(em_vals) + 1))
        
        for method in methods_order:
            mdf = df_clean[df_clean['method'] == method]
            if len(mdf) == 0:
                continue
            row = [method_labels.get(method, method)]
            for em in em_vals:
                subset = mdf[mdf['em_strength'] == em]['ARI']
                mean_val = subset.mean()
                se_val = subset.std() / np.sqrt(len(subset))
                row.append(f"{mean_val:.3f} ({se_val:.4f})")
            print(f"| {row[0]:25s} | " + " | ".join(row[1:]) + " |")
    
    # --- ARI by sample size ---
    print("\n" + "="*80)
    print("TABLE 7c: ARI (SE) by sample size")
    print("="*80)
    
    n_vals = sorted(df_clean['n'].unique())
    print(f"\n| Method | " + " | ".join([f"N = {n}" for n in n_vals]) + " |")
    print("|" + "--------|" * (len(n_vals) + 1))
    
    for method in methods_order:
        mdf = df_clean[df_clean['method'] == method]
        if len(mdf) == 0:
            continue
        row = [method_labels.get(method, method)]
        for n in n_vals:
            subset = mdf[mdf['n'] == n]['ARI']
            mean_val = subset.mean()
            se_val = subset.std() / np.sqrt(len(subset))
            row.append(f"{mean_val:.3f} ({se_val:.4f})")
        print(f"| {row[0]:25s} | " + " | ".join(row[1:]) + " |")
    
    # --- Bias reduction by Z→X ---
    if has_bias:
        print("\n" + "="*80)
        print("TABLE 7d: Bias reduction (SE) by Z→X influence")
        print("="*80)
        
        print(f"\n| Method | " + " | ".join([f"zx = {z}" for z in zx_vals]) + " |")
        print("|" + "--------|" * (len(zx_vals) + 1))
        
        for method in methods_order:
            mdf = df_clean[df_clean['method'] == method]
            if len(mdf) == 0:
                continue
            row = [method_labels.get(method, method)]
            for zx in zx_vals:
                subset = mdf[mdf['zx_influence_scale'] == zx]['bias_reduction']
                subset_clean = subset.dropna()
                if len(subset_clean) > 0:
                    mean_val = subset_clean.mean()
                    se_val = subset_clean.std() / np.sqrt(len(subset_clean))
                    row.append(f"{mean_val:.3f} ({se_val:.4f})")
                else:
                    row.append("N/A")
            print(f"| {row[0]:25s} | " + " | ".join(row[1:]) + " |")
    
    # --- Key summary stats ---
    print("\n" + "="*80)
    print("KEY SENSITIVITY FINDINGS")
    print("="*80)
    
    # ARI ratio strong/weak for proposed methods
    proposed = ['1A_predicted_prob', '1C_cv_decision', '2A_PCA_cum60', '2B_clustering']
    for method in proposed:
        mdf = df_clean[df_clean['method'] == method]
        weak = mdf[mdf['zx_influence_scale'] == 0.2]['ARI'].mean()
        strong = mdf[mdf['zx_influence_scale'] == 1.0]['ARI'].mean()
        ratio = strong / weak if weak > 0 else float('inf')
        print(f"  {method}: ARI weak={weak:.4f}, strong={strong:.4f}, ratio={ratio:.1f}x")
    
    # Effect of sample size
    print("\n  Sample size effect (all proposed methods pooled):")
    for n in n_vals:
        subset = df_clean[(df_clean['method'].isin(proposed)) & (df_clean['n'] == n)]['ARI']
        print(f"    N={n}: ARI={subset.mean():.4f} (SE={subset.std()/np.sqrt(len(subset)):.5f})")
    
    # Effect of EM strength
    if 'em_strength' in df_clean.columns:
        print("\n  EM strength effect (all proposed methods pooled):")
        for em in sorted(df_clean['em_strength'].unique()):
            subset = df_clean[(df_clean['method'].isin(proposed)) & (df_clean['em_strength'] == em)]['ARI']
            print(f"    em={em}: ARI={subset.mean():.4f} (SE={subset.std()/np.sqrt(len(subset)):.5f})")
    
    return df_clean


if __name__ == '__main__':
    df = analyze_sensitivity()
