#!/usr/bin/env python3
"""Regenerate all figures at high DPI with vivid colors for manuscript."""

import sys
sys.path.insert(0, '/home/ubuntu/repos/stratification_project')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

# Force high DPI and white background
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'
plt.rcParams['font.family'] = 'DejaVu Sans'

from visualization import (
    plot_heatmap_ari_nmi, plot_coherence_comparison, plot_eta_squared,
    plot_simpson_resolution, plot_bias_reduction, plot_pca_contribution_analysis,
    plot_sensitivity_sample_size, plot_sensitivity_zx_influence,
    plot_summary_dashboard, plot_coherence_diagnosis_example
)

# Phase 1
print("Loading Phase 1 results...")
df1 = pd.read_csv('/home/ubuntu/repos/stratification_project/results/phase1_results.csv')
print(f"  {len(df1)} rows loaded")

print("Generating Phase 1 plots...")
plot_heatmap_ari_nmi(df1)
plot_coherence_comparison(df1)
plot_eta_squared(df1)
plot_simpson_resolution(df1)
plot_bias_reduction(df1)
plot_pca_contribution_analysis(df1)
plot_coherence_diagnosis_example(df1)
plot_summary_dashboard(df1)

# Sensitivity
print("Loading sensitivity results...")
df2 = pd.read_csv('/home/ubuntu/repos/stratification_project/results/sensitivity_results.csv')
print(f"  {len(df2)} rows loaded")

print("Generating sensitivity plots...")
plot_sensitivity_sample_size(df2)
plot_sensitivity_zx_influence(df2)

# Real data figures
print("Generating real data plots...")
from real_data_visualization import (
    fig1_paradox_demonstration, fig2_method_comparison, fig3_coherence_analysis,
    fig4_eta_squared_heatmap, fig5_direction_consistency, fig6_summary_dashboard,
    load_results
)

rd_dir = '/home/ubuntu/repos/stratification_project/results/real_data'
fig1_paradox_demonstration(rd_dir)
rd_df = load_results()
fig2_method_comparison(rd_df, rd_dir)
fig3_coherence_analysis(rd_df, rd_dir)
fig4_eta_squared_heatmap(rd_df, rd_dir)
fig5_direction_consistency(rd_df, rd_dir)
fig6_summary_dashboard(rd_df, rd_dir)

print("\nAll figures regenerated at 300 DPI.")
