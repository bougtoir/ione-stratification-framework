"""
Empirical null distribution of C1 and W_est under no true effect modification.
Primary DGM with delta = [0, 0, 0] (no Z-by-A interaction) so there is no log-OR
heterogeneity, but measured covariates still carry traces of Z.
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


def run_rsm_ipd_null(
    n_sims: int = 200,
    n_jobs: int = -1,
    output_dir: str = 'results',
):
    os.makedirs(output_dir, exist_ok=True)
    method_specs = _method_specs()
    n = 2000
    n_studies = 10
    study_effect_scale = 0.6
    z_effect_scale = 1.0
    zx_influence_scale = 1.0
    x_effect_scale = 1.0
    noise_level = 1.0
    n_z_vars = 3
    n_strata = 5
    delta = [0.0, 0.0, 0.0]

    scenarios = []
    for sim_id in range(n_sims):
        seed = sim_id * 10000 + 777 + 555
        scenarios.append((
            sim_id, n, n_strata, z_effect_scale, zx_influence_scale,
            x_effect_scale, noise_level, n_z_vars, seed,
            n_studies, study_effect_scale,
        ))

    n_scenarios = len(scenarios)
    n_methods = len(method_specs)
    print(f'RSM IPD null: {n_scenarios} scenarios x {n_methods} methods = '
          f'{n_scenarios * n_methods} evaluations')
    print(f'Using {n_jobs} parallel jobs')

    start = time.time()
    all_results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(run_scenario)(
            *s, method_specs=method_specs, nonlinear=False,
            delta=delta,
        )
        for s in scenarios
    )
    flat_results = [r for batch in all_results for r in batch]
    elapsed = time.time() - start
    print(f'Completed in {elapsed:.1f}s ({elapsed / 60:.1f}min)')

    df = pd.DataFrame(flat_results)
    out_path = os.path.join(output_dir, 'rsm_ipd_null_results.csv')
    df.to_csv(out_path, index=False)
    print(f'Saved to {out_path} ({len(df)} rows)')
    return df


if __name__ == '__main__':
    n_cpus = multiprocessing.cpu_count()
    print(f'Available CPUs: {n_cpus}')
    print('\n=== RSM IPD Empirical Null Distribution ===')
    run_rsm_ipd_null(n_sims=200, n_jobs=n_cpus, output_dir='results')
    print('\nDone!')
