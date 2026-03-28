"""
Simulation runner with parallelization.
Optimized: generates data once per scenario, runs all methods on same dataset.
"""

import numpy as np
import pandas as pd
import time
import os
from joblib import Parallel, delayed
import warnings

from data_generation import generate_dataset, define_true_strata
from methods import (
    method_1a_predicted_probability,
    method_1b_residual,
    method_1c_cv_decision,
    method_1d_ml_uncertainty,
    method_2a_pca,
    method_2b_clustering,
    method_2d_rf_proximity,
    get_pca_variants,
    get_baseline_methods,
)
from evaluation import evaluate_stratification

warnings.filterwarnings('ignore')


def run_scenario(
    sim_id: int,
    n: int,
    n_strata: int,
    z_effect_scale: float,
    zx_influence_scale: float,
    x_effect_scale: float,
    noise_level: float,
    n_z_vars: int,
    seed: int,
    method_specs: list,
) -> list:
    """
    Run one scenario: generate data once, apply ALL methods, evaluate each.
    Returns list of result dicts (one per method).
    """
    data = generate_dataset(
        n=n,
        z_effect_scale=z_effect_scale,
        zx_influence_scale=zx_influence_scale,
        x_effect_scale=x_effect_scale,
        noise_level=noise_level,
        n_z_vars=n_z_vars,
        seed=seed,
    )

    X, Y, Z = data['X'], data['Y'], data['Z']
    Z_clusters = data['Z_clusters']

    base_info = {
        'sim_id': sim_id,
        'n': n,
        'n_strata': n_strata,
        'z_effect_scale': z_effect_scale,
        'zx_influence_scale': zx_influence_scale,
        'x_effect_scale': x_effect_scale,
        'noise_level': noise_level,
        'n_z_vars': n_z_vars,
        'actual_event_rate': data['params']['actual_event_rate'],
    }

    baseline_funcs = get_baseline_methods()
    results = []

    for method_name, method_func, method_kwargs in method_specs:
        try:
            if 'baseline' in method_name:
                bname = method_name.replace('baseline_', '')
                strata = baseline_funcs[bname](X, Y, Z, n_strata, seed=seed)
            elif method_name.startswith('2A_'):
                strata = method_func(X, Y, n_strata, **method_kwargs)
            else:
                strata = method_func(X, Y, n_strata)

            metrics = evaluate_stratification(X, Y, Z, Z_clusters, strata)
            result = {**base_info, 'method': method_name, 'error': None}
            result.update(metrics)
        except Exception as e:
            result = {**base_info, 'method': method_name, 'error': str(e)}

        results.append(result)

    return results


def build_method_specs(include_slow: bool = False) -> list:
    """Build list of (name, func, kwargs) for all methods."""
    specs = [
        ('1A_predicted_prob', method_1a_predicted_probability, {}),
        ('1B_residual', method_1b_residual, {}),
        ('1C_cv_decision', method_1c_cv_decision, {}),
        ('1D_ml_uncertainty', method_1d_ml_uncertainty, {}),
        ('2B_clustering', method_2b_clustering, {}),
    ]

    if include_slow:
        specs.append(('2D_rf_proximity', method_2d_rf_proximity, {}))

    # PCA variants
    for pca_var in get_pca_variants():
        label = f"2A_{pca_var['label']}"
        specs.append((label, method_2a_pca, {
            'cumulative_threshold': pca_var['cumulative_threshold'],
            'fixed_k': pca_var['fixed_k'],
        }))

    # Baselines
    specs.append(('baseline_random', None, {}))
    specs.append(('baseline_oracle_kmeans', None, {}))
    specs.append(('baseline_oracle_quantile', None, {}))

    return specs


def run_phase1_simulation(
    n_sims: int = 200,
    n_jobs: int = -1,
    output_dir: str = 'results',
) -> pd.DataFrame:
    """
    Phase 1: Proof of concept (N=2000, all methods + PCA variants + baselines).
    Optimized: one data generation per scenario, all methods evaluated on same data.
    """
    os.makedirs(output_dir, exist_ok=True)

    n = 2000
    n_strata_list = [3, 5]
    zx_scales = [0.3, 0.5, 1.0]
    method_specs = build_method_specs(include_slow=True)

    # Build scenario list (each = one data generation + all methods)
    scenarios = []
    for sim_id in range(n_sims):
        for n_strata in n_strata_list:
            for zx_scale in zx_scales:
                seed = sim_id * 10000 + int(zx_scale * 100) + n_strata
                scenarios.append((sim_id, n, n_strata, 1.0, zx_scale, 1.0, 1.0, 3, seed))

    n_scenarios = len(scenarios)
    n_methods = len(method_specs)
    print(f"Phase 1: {n_scenarios} scenarios x {n_methods} methods = {n_scenarios * n_methods} evaluations")
    print(f"Using {n_jobs} parallel jobs")

    start = time.time()

    all_results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(run_scenario)(
            *s, method_specs=method_specs,
        )
        for s in scenarios
    )

    # Flatten list of lists
    flat_results = [r for batch in all_results for r in batch]

    elapsed = time.time() - start
    print(f"Completed in {elapsed:.1f}s ({elapsed / 60:.1f}min)")

    df = pd.DataFrame(flat_results)
    df.to_csv(os.path.join(output_dir, 'phase1_results.csv'), index=False)
    print(f"Saved to {output_dir}/phase1_results.csv ({len(df)} rows)")
    return df


def run_sensitivity_simulation(
    n_sims: int = 100,
    n_jobs: int = -1,
    output_dir: str = 'results',
) -> pd.DataFrame:
    """
    Sensitivity analysis: vary Z effect, Z->X influence, sample size.
    Uses top methods only for speed.
    """
    os.makedirs(output_dir, exist_ok=True)

    sample_sizes = [500, 2000, 10000]
    z_effect_scales = [0.5, 1.0, 2.0]
    zx_influence_scales = [0.2, 0.5, 1.0]
    n_strata_list = [3, 5, 10]

    method_specs = [
        ('1A_predicted_prob', method_1a_predicted_probability, {}),
        ('1C_cv_decision', method_1c_cv_decision, {}),
        ('2A_PCA_cum60', method_2a_pca, {'cumulative_threshold': 0.6, 'fixed_k': None}),
        ('2B_clustering', method_2b_clustering, {}),
        ('baseline_oracle_kmeans', None, {}),
        ('baseline_random', None, {}),
    ]

    scenarios = []
    for sim_id in range(n_sims):
        for n_val in sample_sizes:
            for ze in z_effect_scales:
                for zx in zx_influence_scales:
                    for ns in n_strata_list:
                        seed = sim_id * 100000 + n_val + int(ze * 10) + int(zx * 100) + ns
                        scenarios.append((sim_id, n_val, ns, ze, zx, 1.0, 1.0, 3, seed))

    n_scenarios = len(scenarios)
    n_methods = len(method_specs)
    print(f"Sensitivity: {n_scenarios} scenarios x {n_methods} methods = {n_scenarios * n_methods} evaluations")

    start = time.time()

    all_results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(run_scenario)(
            *s, method_specs=method_specs,
        )
        for s in scenarios
    )

    flat_results = [r for batch in all_results for r in batch]

    elapsed = time.time() - start
    print(f"Completed in {elapsed:.1f}s ({elapsed / 60:.1f}min)")

    df = pd.DataFrame(flat_results)
    df.to_csv(os.path.join(output_dir, 'sensitivity_results.csv'), index=False)
    print(f"Saved to {output_dir}/sensitivity_results.csv ({len(df)} rows)")
    return df


if __name__ == '__main__':
    import multiprocessing
    n_cpus = multiprocessing.cpu_count()
    print(f"Available CPUs: {n_cpus}")

    print("\n=== Phase 1: Proof of Concept ===")
    df1 = run_phase1_simulation(n_sims=200, n_jobs=n_cpus, output_dir='results')

    print("\n=== Sensitivity Analysis ===")
    df2 = run_sensitivity_simulation(n_sims=100, n_jobs=n_cpus, output_dir='results')

    print("\nAll simulations complete!")
