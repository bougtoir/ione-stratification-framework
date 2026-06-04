"""
Driver: run non-linear Z->X robustness analyses (no manuscript revision).

For a valid paired comparison every arm must use the *current* (post-bugfix)
code. The committed phase1_results.csv is stale (pre-bugfix), so we regenerate
the linear Phase-1 baseline here. The committed sensitivity_results.csv is
post-bugfix, so it is reused as the linear sensitivity baseline.

Outputs:
  results/phase1_linear_current.csv   (A linear baseline, current code)
  results/phase1_nonlinear.csv        (A non-linear, already generated)
  results/sensitivity_nonlinear.csv   (B non-linear; pair with sensitivity_results.csv)
"""

import os
import multiprocessing
from run_simulation import run_phase1_simulation, run_sensitivity_simulation

if __name__ == '__main__':
    n_cpus = multiprocessing.cpu_count()
    print(f"Available CPUs: {n_cpus}")

    print("\n=== A0: Phase-1 LINEAR baseline (current code) ===")
    run_phase1_simulation(
        n_sims=200, n_jobs=n_cpus, output_dir='results',
        nonlinear=False, output_name='phase1_linear_current.csv',
    )

    if not os.path.exists('results/phase1_nonlinear.csv'):
        print("\n=== A: Phase-1 NON-LINEAR ===")
        run_phase1_simulation(
            n_sims=200, n_jobs=n_cpus, output_dir='results',
            nonlinear=True, output_name='phase1_nonlinear.csv',
        )
    else:
        print("\n=== A: phase1_nonlinear.csv already exists, skipping ===")

    print("\n=== B: Sensitivity grid NON-LINEAR ===")
    run_sensitivity_simulation(
        n_sims=50, n_jobs=n_cpus, output_dir='results',
        nonlinear=True, output_name='sensitivity_nonlinear.csv',
    )

    print("\nNon-linear analyses complete!")
