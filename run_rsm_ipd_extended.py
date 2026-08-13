"""
Extended RSM IPD meta-analysis simulations:
- Sensitivity to sample size, Z->Y effect scale, Z->X influence scale, and K.
- Non-linear Z->X robustness analysis.

All scenarios keep n_studies=10 and study_effect_scale=0.6 to match the primary
IPD meta-analysis design. Results are written to results/rsm_ipd_sensitivity_results.csv
and results/rsm_ipd_nonlinearity_results.csv and summarized by generate_summary.py.
"""

import os
import multiprocessing
import time
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
import warnings

from run_simulation import run_scenario
from methods import (
    method_1a_predicted_probability,
    method_1b_residual,
    method_1c_cv_decision,
    method_ps_propensity_score,
    method_gmm,
    method_prognostic_score,
    method_2a_pca,
    method_2b_clustering,
)

warnings.filterwarnings('ignore')


def _method_specs():
    """Standard set of methods for the RSM IPD extended simulations."""
    return [
        ('1A_predicted_prob', method_1a_predicted_probability, {}),
        ('1B_residual', method_1b_residual, {}),
        ('1C_cv_decision', method_1c_cv_decision, {}),
        ('PS_propensity_score', method_ps_propensity_score, {}),
        ('GMM', method_gmm, {}),
        ('Prognostic_score', method_prognostic_score, {}),
        ('2A_PCA_cum60', method_2a_pca, {'cumulative_threshold': 0.6, 'fixed_k': None}),
        ('2B_clustering', method_2b_clustering, {}),
        ('baseline_random', None, {}),
        ('baseline_oracle_kmeans', None, {}),
        ('baseline_oracle_quantile', None, {}),
    ]


def _run_grid(
    name: str,
    n_sims: int,
    sample_sizes: list,
    z_effect_scales: list,
    zx_influence_scales: list,
    n_strata_list: list,
    nonlinear: bool,
    n_studies: int,
    study_effect_scale: float,
    n_jobs: int,
    output_dir: str,
):
    method_specs = _method_specs()
    scenarios = []
    for sim_id in range(n_sims):
        for n_val in sample_sizes:
            for ze in z_effect_scales:
                for zx in zx_influence_scales:
                    for ns in n_strata_list:
                        seed = (
                            sim_id * 100000
                            + n_val
                            + int(ze * 10)
                            + int(zx * 100)
                            + ns
                            + (10000 if nonlinear else 0)
                        )
                        scenarios.append((
                            sim_id, n_val, ns, ze, zx, 1.0, 1.0, 3, seed,
                            n_studies, study_effect_scale,
                        ))

    n_scenarios = len(scenarios)
    n_methods = len(method_specs)
    print(
        f'RSM IPD {name}: {n_scenarios} scenarios x {n_methods} methods = '
        f'{n_scenarios * n_methods} evaluations'
    )
    print(f'Using {n_jobs} parallel jobs; nonlinear={nonlinear}')

    start = time.time()
    all_results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(run_scenario)(
            *s, method_specs=method_specs, nonlinear=nonlinear,
        )
        for s in scenarios
    )
    flat_results = [r for batch in all_results for r in batch]
    elapsed = time.time() - start
    print(f'Completed in {elapsed:.1f}s ({elapsed / 60:.1f}min)')

    df = pd.DataFrame(flat_results)
    out_name = (
        'rsm_ipd_nonlinearity_results.csv'
        if nonlinear else 'rsm_ipd_sensitivity_results.csv'
    )
    out_path = os.path.join(output_dir, out_name)
    df.to_csv(out_path, index=False)
    print(f'Saved to {out_path} ({len(df)} rows)')
    return df


def run_rsm_ipd_sensitivity(
    n_sims: int = 30,
    n_jobs: int = -1,
    output_dir: str = 'results',
):
    """Sensitivity analysis for the RSM IPD design."""
    os.makedirs(output_dir, exist_ok=True)
    return _run_grid(
        name='sensitivity',
        n_sims=n_sims,
        sample_sizes=[500, 2000, 10000],
        z_effect_scales=[0.5, 1.0, 2.0],
        zx_influence_scales=[0.2, 0.5, 1.0],
        n_strata_list=[5],
        nonlinear=False,
        n_studies=10,
        study_effect_scale=0.6,
        n_jobs=n_jobs,
        output_dir=output_dir,
    )


def run_rsm_ipd_nonlinearity(
    n_sims: int = 50,
    n_jobs: int = -1,
    output_dir: str = 'results',
):
    """Non-linear Z->X robustness analysis for the RSM IPD design."""
    os.makedirs(output_dir, exist_ok=True)
    return _run_grid(
        name='nonlinearity',
        n_sims=n_sims,
        sample_sizes=[2000],
        z_effect_scales=[1.0],
        zx_influence_scales=[1.0],
        n_strata_list=[5],
        nonlinear=True,
        n_studies=10,
        study_effect_scale=0.6,
        n_jobs=n_jobs,
        output_dir=output_dir,
    )


if __name__ == '__main__':
    n_cpus = multiprocessing.cpu_count()
    print(f'Available CPUs: {n_cpus}')

    print('\n=== RSM IPD Sensitivity Analysis ===')
    run_rsm_ipd_sensitivity(n_sims=30, n_jobs=n_cpus, output_dir='results')

    print('\n=== RSM IPD Non-linearity Robustness ===')
    run_rsm_ipd_nonlinearity(n_sims=50, n_jobs=n_cpus, output_dir='results')

    print('\nAll extended RSM IPD simulations complete!')
