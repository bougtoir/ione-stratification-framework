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

from data_generation import generate_dataset
from methods import (
    method_1a_predicted_probability,
    method_1b_residual,
    method_1d_ml_uncertainty,
    method_2a_pca,
    method_2b_clustering,
    method_2d_rf_proximity,
    method_ps_propensity_score,
    method_gmm,
    method_prognostic_score,
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
    n_studies: int = 1,
    study_effect_scale: float = 0.0,
    method_specs: list = None,
    nonlinear: bool = False,
    delta: list = None,
    w_est_specs: list = None,
) -> list:
    """
    Run one scenario: generate data once, apply ALL methods, evaluate each.
    Returns list of result dicts (one per method).
    """
    if method_specs is None:
        method_specs = []
    if w_est_specs is None:
        w_est_specs = ['interaction']
    data = generate_dataset(
        n=n,
        z_effect_scale=z_effect_scale,
        zx_influence_scale=zx_influence_scale,
        x_effect_scale=x_effect_scale,
        noise_level=noise_level,
        n_z_vars=n_z_vars,
        nonlinear=nonlinear,
        seed=seed,
        n_studies=n_studies,
        study_effect_scale=study_effect_scale,
        delta=delta,
    )

    X, A, Y, Z = data['X'], data['A'], data['Y'], data['Z']
    study_id = data.get('study_id')
    Z_clusters = data['Z_clusters']
    true_cate = data['true_cate']
    true_ate_riskdiff = data['true_ate_riskdiff']

    base_info = {
        'sim_id': sim_id,
        'n': n,
        'n_strata': n_strata,
        'z_effect_scale': z_effect_scale,
        'zx_influence_scale': zx_influence_scale,
        'x_effect_scale': x_effect_scale,
        'noise_level': noise_level,
        'n_z_vars': n_z_vars,
        'nonlinear': nonlinear,
        'n_studies': data['params'].get('n_studies', 1),
        'study_effect_scale': data['params'].get('study_effect_scale', 0.0),
        'actual_event_rate': data['params']['actual_event_rate'],
        'actual_treatment_prevalence': data['params']['actual_treatment_prevalence'],
        'true_ate_riskdiff': true_ate_riskdiff,
    }
    if delta is not None:
        base_info['delta'] = ','.join(str(v) for v in delta)

    # Discovery/evaluation split (fixed per scenario) to prevent outcome-informed overfitting
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    split = n // 2
    discovery_idx = perm[:split]
    eval_idx = perm[split:]

    baseline_funcs = get_baseline_methods()
    results = []

    # Methods that use the outcome Y for stratification: apply discovery/evaluation split
    outcome_informed_prefixes = ('1A_', '1B_', '1D_', 'Prognostic_')

    for method_name, method_func, method_kwargs in method_specs:
        try:
            if method_name.startswith('baseline_'):
                bname = method_name.replace('baseline_', '')
                strata = baseline_funcs[bname](X, A, Y, Z, n_strata, seed=seed)
            else:
                if method_name.startswith(outcome_informed_prefixes):
                    kwargs = {**method_kwargs, 'discovery_idx': discovery_idx}
                else:
                    kwargs = method_kwargs
                strata = method_func(X, A, Y, n_strata, **kwargs)

            metrics = evaluate_stratification(
                X, A, Y, Z, Z_clusters, strata,
                true_cate=true_cate,
                true_ate_riskdiff=true_ate_riskdiff,
                eval_idx=eval_idx,
                study_id=study_id,
                w_est_specs=w_est_specs,
            )
            result = {**base_info, 'method': method_name, 'error': None}
            result.update(metrics)
        except Exception as e:
            result = {**base_info, 'method': method_name, 'error': str(e)}

        results.append(result)

    return results


def run_rsm_ipd_simulation(
    n_sims: int = 50,
    n_jobs: int = -1,
    output_dir: str = 'results',
) -> pd.DataFrame:
    """
    IPD meta-analysis scenario for Research Synthesis Methods.
    n=2000 subjects distributed across 10 studies; study-level heterogeneity in
    baseline risk, treatment prevalence and Z distribution.
    """
    os.makedirs(output_dir, exist_ok=True)

    n = 2000
    n_studies = 10
    study_effect_scale = 0.6
    z_effect_scale = 1.0
    zx_influence_scale = 1.0
    x_effect_scale = 1.0
    noise_level = 1.0
    n_z_vars = 3
    n_strata_list = [3, 5, 10]

    method_specs = [
        ('1A_predicted_prob', method_1a_predicted_probability, {}),
        ('1B_residual', method_1b_residual, {}),
        ('PS_propensity_score', method_ps_propensity_score, {}),
        ('GMM', method_gmm, {}),
        ('Prognostic_score', method_prognostic_score, {}),
        ('2A_PCA_cum60', method_2a_pca, {'cumulative_threshold': 0.6, 'fixed_k': None}),
        ('2B_clustering', method_2b_clustering, {}),
        ('baseline_random', None, {}),
        ('baseline_oracle_kmeans', None, {}),
        ('baseline_oracle_quantile', None, {}),
    ]

    scenarios = []
    for sim_id in range(n_sims):
        for n_strata in n_strata_list:
            seed = sim_id * 10000 + 777 + n_strata
            scenarios.append((
                sim_id, n, n_strata, z_effect_scale, zx_influence_scale,
                x_effect_scale, noise_level, n_z_vars, seed,
                n_studies, study_effect_scale,
            ))

    n_scenarios = len(scenarios)
    n_methods = len(method_specs)
    print(f'RSM IPD: {n_scenarios} scenarios x {n_methods} methods = {n_scenarios * n_methods} evaluations')
    print(f'Using {n_jobs} parallel jobs')

    start = time.time()
    all_results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(run_scenario)(
            *s, method_specs=method_specs, nonlinear=False,
        )
        for s in scenarios
    )
    flat_results = [r for batch in all_results for r in batch]
    elapsed = time.time() - start
    print(f'Completed in {elapsed:.1f}s ({elapsed / 60:.1f}min)')

    df = pd.DataFrame(flat_results)
    df.to_csv(os.path.join(output_dir, 'rsm_ipd_results.csv'), index=False)
    print(f'Saved to {output_dir}/rsm_ipd_results.csv ({len(df)} rows)')
    return df


def build_method_specs(include_slow: bool = False) -> list:
    """Build list of (name, func, kwargs) for all methods."""
    specs = [
        ('1A_predicted_prob', method_1a_predicted_probability, {}),
        ('1B_residual', method_1b_residual, {}),
        ('1D_ml_uncertainty', method_1d_ml_uncertainty, {}),
        ('PS_propensity_score', method_ps_propensity_score, {}),
        ('GMM', method_gmm, {}),
        ('Prognostic_score', method_prognostic_score, {}),
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
    n_sims: int = 50,
    n_jobs: int = -1,
    output_dir: str = 'results',
) -> pd.DataFrame:
    """
    Phase 1: Proof of concept (N=2000, all methods + PCA variants + baselines + comparators).
    """
    os.makedirs(output_dir, exist_ok=True)

    n = 2000
    n_strata_list = [3, 5]
    zx_scales = [0.3, 0.5, 1.0]
    method_specs = build_method_specs(include_slow=False)

    nonlinear = False
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
            *s, method_specs=method_specs, nonlinear=nonlinear,
        )
        for s in scenarios
    )

    flat_results = [r for batch in all_results for r in batch]

    elapsed = time.time() - start
    print(f"Completed in {elapsed:.1f}s ({elapsed / 60:.1f}min)")

    df = pd.DataFrame(flat_results)
    df.to_csv(os.path.join(output_dir, 'phase1_results.csv'), index=False)
    print(f"Saved to {output_dir}/phase1_results.csv ({len(df)} rows)")
    return df


def run_sensitivity_simulation(
    n_sims: int = 30,
    n_jobs: int = -1,
    output_dir: str = 'results',
) -> pd.DataFrame:
    """
    Sensitivity analysis: vary Z effect, Z->X influence, sample size.
    Uses top methods + comparators for speed.
    """
    os.makedirs(output_dir, exist_ok=True)

    sample_sizes = [500, 2000, 10000]
    z_effect_scales = [0.5, 1.0, 2.0]
    zx_influence_scales = [0.2, 0.5, 1.0]
    n_strata_list = [3, 5, 10]

    method_specs = [
        ('1A_predicted_prob', method_1a_predicted_probability, {}),
        ('1B_residual', method_1b_residual, {}),
        ('PS_propensity_score', method_ps_propensity_score, {}),
        ('GMM', method_gmm, {}),
        ('Prognostic_score', method_prognostic_score, {}),
        ('2A_PCA_cum60', method_2a_pca, {'cumulative_threshold': 0.6, 'fixed_k': None}),
        ('2B_clustering', method_2b_clustering, {}),
        ('baseline_oracle_kmeans', None, {}),
        ('baseline_random', None, {}),
    ]

    nonlinear = False
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
            *s, method_specs=method_specs, nonlinear=nonlinear,
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


def run_nonlinearity_simulation(
    n_sims: int = 30,
    n_jobs: int = -1,
    output_dir: str = 'results',
) -> pd.DataFrame:
    """
    Non-linear robustness analysis: use non-linear Z->X mappings.
    Same grid as sensitivity but with data generated using squared Z terms.
    """
    os.makedirs(output_dir, exist_ok=True)

    sample_sizes = [500, 2000, 10000]
    z_effect_scales = [0.5, 1.0, 2.0]
    zx_influence_scales = [0.2, 0.5, 1.0]
    n_strata_list = [3, 5, 10]

    method_specs = [
        ('1A_predicted_prob', method_1a_predicted_probability, {}),
        ('1B_residual', method_1b_residual, {}),
        ('PS_propensity_score', method_ps_propensity_score, {}),
        ('GMM', method_gmm, {}),
        ('Prognostic_score', method_prognostic_score, {}),
        ('2A_PCA_cum60', method_2a_pca, {'cumulative_threshold': 0.6, 'fixed_k': None}),
        ('2B_clustering', method_2b_clustering, {}),
        ('baseline_oracle_kmeans', None, {}),
        ('baseline_random', None, {}),
    ]

    nonlinear = True
    scenarios = []
    for sim_id in range(n_sims):
        for n_val in sample_sizes:
            for ze in z_effect_scales:
                for zx in zx_influence_scales:
                    for ns in n_strata_list:
                        seed = sim_id * 100000 + 1 + n_val + int(ze * 10) + int(zx * 100) + ns
                        scenarios.append((sim_id, n_val, ns, ze, zx, 1.0, 1.0, 3, seed))

    n_scenarios = len(scenarios)
    n_methods = len(method_specs)
    print(f"Non-linearity: {n_scenarios} scenarios x {n_methods} methods = {n_scenarios * n_methods} evaluations")

    start = time.time()

    all_results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(run_scenario)(
            *s, method_specs=method_specs, nonlinear=nonlinear,
        )
        for s in scenarios
    )

    flat_results = [r for batch in all_results for r in batch]

    elapsed = time.time() - start
    print(f"Completed in {elapsed:.1f}s ({elapsed / 60:.1f}min)")

    df = pd.DataFrame(flat_results)
    df.to_csv(os.path.join(output_dir, 'nonlinearity_results.csv'), index=False)
    print(f"Saved to {output_dir}/nonlinearity_results.csv ({len(df)} rows)")
    return df


if __name__ == '__main__':
    import multiprocessing
    n_cpus = multiprocessing.cpu_count()
    print(f"Available CPUs: {n_cpus}")

    print("\n=== Phase 1: Proof of Concept ===")
    df1 = run_phase1_simulation(n_sims=50, n_jobs=n_cpus, output_dir='results')

    print("\n=== Sensitivity Analysis ===")
    df2 = run_sensitivity_simulation(n_sims=30, n_jobs=n_cpus, output_dir='results')

    print("\n=== Non-linearity Robustness ===")
    df3 = run_nonlinearity_simulation(n_sims=30, n_jobs=n_cpus, output_dir='results')

    print("\nAll simulations complete!")
