"""
Simulation runner with parallelization.
Revised: includes treatment variable, active comparators, sample splitting,
and MC SE computation. Generates data once per scenario, runs all methods.
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
    comparator_ps_quintile,
    comparator_gmm,
    comparator_kmeans_x,
    comparator_prognostic_score,
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
    treatment_effect: float = 0.5,
    em_strength: float = 0.4,
    nonlinear: bool = False,
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
        treatment_effect=treatment_effect,
        em_strength=em_strength,
        nonlinear=nonlinear,
        seed=seed,
    )

    X, Y, Z, A = data['X'], data['Y'], data['Z'], data['A']
    Z_clusters = data['Z_clusters']
    true_cate = data['true_cate']

    base_info = {
        'sim_id': sim_id,
        'n': n,
        'n_strata': n_strata,
        'z_effect_scale': z_effect_scale,
        'zx_influence_scale': zx_influence_scale,
        'x_effect_scale': x_effect_scale,
        'noise_level': noise_level,
        'n_z_vars': n_z_vars,
        'treatment_effect': treatment_effect,
        'em_strength': em_strength,
        'nonlinear': nonlinear,
        'actual_event_rate': data['params']['actual_event_rate'],
        'treatment_prevalence': data['params']['treatment_prevalence'],
    }

    baseline_funcs = get_baseline_methods()
    results = []

    for method_name, method_func, method_kwargs in method_specs:
        try:
            if 'baseline' in method_name:
                bname = method_name.replace('baseline_', '')
                strata = baseline_funcs[bname](X, Y, Z, n_strata, A=A, seed=seed)
            elif method_name.startswith('2A_'):
                strata = method_func(X, Y, n_strata, A=A, **method_kwargs)
            elif method_name.startswith('comp_'):
                strata = method_func(X, Y, n_strata, A=A)
            else:
                strata = method_func(X, Y, n_strata, A=A)

            metrics = evaluate_stratification(X, Y, Z, Z_clusters, strata,
                                              A=A, true_cate=true_cate)
            result = {**base_info, 'method': method_name, 'error': None}
            result.update(metrics)
        except Exception as e:
            result = {**base_info, 'method': method_name, 'error': str(e)}

        results.append(result)

    return results


def build_method_specs() -> list:
    """Build list of (name, func, kwargs) for all methods + comparators."""
    specs = [
        # IONE proposed methods
        ('1A_predicted_prob', method_1a_predicted_probability, {}),
        ('1B_residual', method_1b_residual, {}),
        ('1C_cv_decision', method_1c_cv_decision, {}),
        ('1D_ml_uncertainty', method_1d_ml_uncertainty, {}),
        ('2B_clustering', method_2b_clustering, {}),
        # Active comparators
        ('comp_PS_quintile', comparator_ps_quintile, {}),
        ('comp_GMM', comparator_gmm, {}),
        ('comp_kmeans_X', comparator_kmeans_x, {}),
        ('comp_prognostic', comparator_prognostic_score, {}),
    ]

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
    nonlinear: bool = False,
    output_name: str = 'phase1_results.csv',
) -> pd.DataFrame:
    """
    Phase 1: Proof of concept.
    N=2000, all methods + comparators + PCA variants + baselines.
    """
    os.makedirs(output_dir, exist_ok=True)

    n = 2000
    n_strata_list = [3, 5]
    zx_scales = [0.3, 0.5, 1.0]
    method_specs = build_method_specs()

    scenarios = []
    for sim_id in range(n_sims):
        for n_strata in n_strata_list:
            for zx_scale in zx_scales:
                seed = sim_id * 10000 + int(zx_scale * 100) + n_strata
                scenarios.append({
                    'sim_id': sim_id, 'n': n, 'n_strata': n_strata,
                    'z_effect_scale': 1.0, 'zx_influence_scale': zx_scale,
                    'x_effect_scale': 1.0, 'noise_level': 1.0,
                    'n_z_vars': 3, 'seed': seed,
                    'treatment_effect': 0.5, 'em_strength': 0.4,
                })

    n_scenarios = len(scenarios)
    n_methods = len(method_specs)
    print(f"Phase 1 (nonlinear={nonlinear}): {n_scenarios} scenarios x {n_methods} methods "
          f"= {n_scenarios * n_methods} evaluations")
    print(f"Using {n_jobs} parallel jobs")

    start = time.time()

    all_results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(run_scenario)(
            s['sim_id'], s['n'], s['n_strata'],
            s['z_effect_scale'], s['zx_influence_scale'],
            s['x_effect_scale'], s['noise_level'],
            s['n_z_vars'], s['seed'], method_specs,
            s['treatment_effect'], s['em_strength'], nonlinear,
        )
        for s in scenarios
    )

    flat_results = [r for batch in all_results for r in batch]

    elapsed = time.time() - start
    print(f"Completed in {elapsed:.1f}s ({elapsed / 60:.1f}min)")

    df = pd.DataFrame(flat_results)
    df.to_csv(os.path.join(output_dir, output_name), index=False)
    print(f"Saved to {output_dir}/{output_name} ({len(df)} rows)")
    return df


def run_sensitivity_simulation(
    n_sims: int = 100,
    n_jobs: int = -1,
    output_dir: str = 'results',
    nonlinear: bool = False,
    output_name: str = 'sensitivity_results.csv',
) -> pd.DataFrame:
    """
    Sensitivity analysis: vary Z effect, Z->X influence, sample size, EM strength.
    Uses top methods + comparators.
    """
    os.makedirs(output_dir, exist_ok=True)

    sample_sizes = [500, 2000, 10000]
    z_effect_scales = [0.5, 1.0, 2.0]
    zx_influence_scales = [0.2, 0.5, 1.0]
    n_strata_list = [3, 5, 10]
    em_strengths = [0.0, 0.4, 0.8]

    method_specs = [
        ('1A_predicted_prob', method_1a_predicted_probability, {}),
        ('1C_cv_decision', method_1c_cv_decision, {}),
        ('2A_PCA_cum60', method_2a_pca,
         {'cumulative_threshold': 0.6, 'fixed_k': None}),
        ('2B_clustering', method_2b_clustering, {}),
        ('comp_PS_quintile', comparator_ps_quintile, {}),
        ('comp_GMM', comparator_gmm, {}),
        ('comp_prognostic', comparator_prognostic_score, {}),
        ('baseline_oracle_kmeans', None, {}),
        ('baseline_random', None, {}),
    ]

    scenarios = []
    n_idx = {v: i for i, v in enumerate(sample_sizes)}
    ze_idx = {v: i for i, v in enumerate(z_effect_scales)}
    zx_idx = {v: i for i, v in enumerate(zx_influence_scales)}
    ns_idx = {v: i for i, v in enumerate(n_strata_list)}
    em_idx = {v: i for i, v in enumerate(em_strengths)}
    for sim_id in range(n_sims):
        for n_val in sample_sizes:
            for ze in z_effect_scales:
                for zx in zx_influence_scales:
                    for ns in n_strata_list:
                        for em in em_strengths:
                            seed = (sim_id * 10**8
                                    + n_idx[n_val] * 10**6
                                    + ze_idx[ze] * 10**4
                                    + zx_idx[zx] * 10**3
                                    + ns_idx[ns] * 10**2
                                    + em_idx[em] * 10)
                            scenarios.append({
                                'sim_id': sim_id, 'n': n_val, 'n_strata': ns,
                                'z_effect_scale': ze, 'zx_influence_scale': zx,
                                'x_effect_scale': 1.0, 'noise_level': 1.0,
                                'n_z_vars': 3, 'seed': seed,
                                'treatment_effect': 0.5, 'em_strength': em,
                            })

    n_scenarios = len(scenarios)
    n_methods = len(method_specs)
    print(f"Sensitivity (nonlinear={nonlinear}): {n_scenarios} scenarios x {n_methods} methods "
          f"= {n_scenarios * n_methods} evaluations")

    start = time.time()

    all_results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(run_scenario)(
            s['sim_id'], s['n'], s['n_strata'],
            s['z_effect_scale'], s['zx_influence_scale'],
            s['x_effect_scale'], s['noise_level'],
            s['n_z_vars'], s['seed'], method_specs,
            s['treatment_effect'], s['em_strength'], nonlinear,
        )
        for s in scenarios
    )

    flat_results = [r for batch in all_results for r in batch]

    elapsed = time.time() - start
    print(f"Completed in {elapsed:.1f}s ({elapsed / 60:.1f}min)")

    df = pd.DataFrame(flat_results)
    df.to_csv(os.path.join(output_dir, output_name), index=False)
    print(f"Saved to {output_dir}/{output_name} ({len(df)} rows)")
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
