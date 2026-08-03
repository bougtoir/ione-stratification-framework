"""Convenience entry point for the RSM IPD meta-analysis simulation."""

import multiprocessing
from run_simulation import run_rsm_ipd_simulation

if __name__ == '__main__':
    n_cpus = multiprocessing.cpu_count()
    run_rsm_ipd_simulation(n_sims=50, n_jobs=n_cpus, output_dir='results')
