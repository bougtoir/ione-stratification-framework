"""
Data generation module: Simulate datasets with a binary treatment and known causal structure.
Based on the causal DAG: Z -> X, Z -> A, X -> A, A -> Y, Z -> Y, Z*A -> Y, X -> Y.
"""

import numpy as np
from scipy.special import expit, logit


def _solve_intercept(
    linear_term: np.ndarray,
    treatment: np.ndarray,
    treatment_effect: np.ndarray,
    target_rate: float,
    n_grid: int = 200,
) -> float:
    """
    Find an intercept b0 such that mean(expit(b0 + linear_term + treatment*treatment_effect))
    is close to target_rate. Use a simple bisection search.
    """
    lo, hi = logit(max(target_rate, 0.001)) - linear_term.mean() - 2.0, logit(min(target_rate, 0.999)) - linear_term.mean() + 2.0
    for _ in range(50):
        mid = (lo + hi) / 2.0
        rate = expit(mid + linear_term + treatment * treatment_effect).mean()
        if rate > target_rate:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


def _solve_treatment_intercept(linear_term: np.ndarray, target_rate: float = 0.5, n_iter: int = 30) -> float:
    """Find intercept for treatment model so that mean(expit(intercept + linear_term)) ≈ target_rate."""
    lo, hi = -linear_term.mean() - 5.0, -linear_term.mean() + 5.0
    for _ in range(n_iter):
        mid = (lo + hi) / 2.0
        rate = expit(mid + linear_term).mean()
        if rate > target_rate:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


def generate_dataset(
    n: int = 2000,
    z_effect_scale: float = 1.0,
    zx_influence_scale: float = 1.0,
    x_effect_scale: float = 1.0,
    noise_level: float = 1.0,
    n_z_vars: int = 3,
    event_rate: float = 0.15,
    treatment_prevalence: float = 0.5,
    nonlinear: bool = False,
    tau: float | None = None,
    delta: list[float] | None = None,
    gamma_z: list[float] | None = None,
    gamma_x: list[float] | None = None,
    seed: int | None = None,
    n_studies: int = 1,
    study_effect_scale: float = 0.0,
) -> dict:
    """
    Generate a simulated dataset with known causal structure including a binary treatment A.

    Optional IPD meta-analysis structure: when n_studies > 1, subjects are assigned to
    distinct studies with study-specific distributions of Z and baseline risks/prevalences.

    Causal pathways:
      Z -> X (trace in measured variables)
      Z -> A (confounding of treatment)
      X -> A (measured covariate influence on treatment)
      A -> Y (main treatment effect)
      Z -> Y (direct confounding)
      Z*A -> Y (effect modification)
      X -> Y (weak direct effects)
      study -> Z, A, Y (study-level heterogeneity in IPD meta-analysis)

    Returns dict with keys:
        'X', 'Z', 'A', 'Y', 'study_id', 'Z_clusters', 'true_cate', 'true_ate_riskdiff', 'true_ate_logor', 'p_y_a1', 'p_y_a0', 'params'
    """
    rng = np.random.default_rng(seed)

    # --- Study assignment (IPD meta-analysis) ---
    n_studies = max(1, int(n_studies))
    if n_studies > n:
        n_studies = n

    study_sizes = np.full(n_studies, n // n_studies)
    remainder = n - study_sizes.sum()
    if remainder > 0:
        study_sizes[:remainder] += 1
    study_id = np.repeat(np.arange(n_studies), study_sizes)

    # Study-specific baseline shifts
    study_z1_shift = rng.normal(0, study_effect_scale * 5.0, n_studies)
    study_z2_prob = 0.5 + rng.normal(0, study_effect_scale * 0.1, n_studies)
    study_z2_prob = np.clip(study_z2_prob, 0.1, 0.9)
    study_treat_intercept = rng.normal(0, study_effect_scale * 0.5, n_studies)
    study_outcome_intercept = rng.normal(0, study_effect_scale * 0.5, n_studies)

    # --- Critical variables Z ---
    Z1 = np.clip(rng.normal(60 + study_z1_shift[study_id], 12, n), 20, 95)
    Z2 = rng.binomial(1, study_z2_prob[study_id], n).astype(float)
    Z3 = rng.choice([0, 1, 2], size=n, p=[0.3, 0.4, 0.3]).astype(float)
    Z = np.column_stack([Z1, Z2, Z3])

    Z1_std = (Z1 - 60) / 12.0
    Z3_std = (Z3 - 1) / 0.8

    # --- General variables X influenced by Z ---
    s = zx_influence_scale
    nl = noise_level

    if nonlinear:
        # Non-linear Z->X mappings: squares and interactions
        X1 = s * (0.5 * Z1_std**2 + 0.5 * Z3_std) + rng.normal(0, nl, n)
        X2 = s * (0.3 * Z1_std * Z2 + 0.15 * Z2) + rng.normal(0, nl, n)
        X3 = s * (0.5 * Z1_std + 0.2 * Z3_std**2) + rng.normal(0, nl, n)
        X4 = s * (0.3 * Z3_std * Z1_std) + rng.normal(0, nl, n)
        X5 = s * (0.3 * Z1_std + 0.15 * Z2 * Z3_std) + rng.normal(0, nl, n)
        X6 = s * (0.5 * Z2 + 0.2 * Z1_std**2) + rng.normal(0, nl, n)
        X7 = s * (0.15 * Z1_std * Z3_std) + rng.normal(0, nl, n)
        X8 = s * (0.3 * Z1_std + 0.15 * Z2) + rng.normal(0, nl, n)
        X9 = s * (0.15 * Z1_std**2 + 0.15 * Z3_std) + rng.normal(0, nl, n)
        X10 = s * (0.3 * Z2 + 0.15 * Z3_std**2) + rng.normal(0, nl, n)
    else:
        X1 = s * (0.5 * Z1_std + 0.5 * Z3_std) + rng.normal(0, nl, n)
        X2 = s * (0.3 * Z1_std + 0.15 * Z2) + rng.normal(0, nl, n)
        X3 = s * (0.5 * Z1_std) + rng.normal(0, nl, n)
        X4 = s * (0.3 * Z3_std) + rng.normal(0, nl, n)
        X5 = s * (0.3 * Z1_std + 0.15 * Z2) + rng.normal(0, nl, n)
        X6 = s * (0.5 * Z2) + rng.normal(0, nl, n)
        X7 = s * (0.15 * Z1_std) + rng.normal(0, nl, n)
        X8 = s * (0.3 * Z1_std) + rng.normal(0, nl, n)
        X9 = s * (0.15 * Z1_std + 0.15 * Z3_std) + rng.normal(0, nl, n)
        X10 = s * (0.3 * Z2 + 0.15 * Z3_std) + rng.normal(0, nl, n)

    X = np.column_stack([X1, X2, X3, X4, X5, X6, X7, X8, X9, X10])

    # Append study identifier as a measured covariate when IPD meta-analysis structure is used
    if n_studies > 1:
        study_cov = (study_id - study_id.mean()) / (study_id.std() + 1e-10)
        X = np.column_stack([X, study_cov])

    # --- Binary treatment A ---
    ze = z_effect_scale
    if gamma_z is None:
        gamma_z = np.array([0.035, 0.025, 0.035]) * ze  # Z -> A coefficients
    else:
        gamma_z = np.asarray(gamma_z, dtype=float)
    if gamma_x is None:
        gamma_x = x_effect_scale * np.array([0.01] * 10)
    else:
        gamma_x = np.asarray(gamma_x, dtype=float)
    if len(gamma_x) < X.shape[1]:
        gamma_x = np.concatenate([gamma_x, np.zeros(X.shape[1] - len(gamma_x))])
    logit_a = (
        gamma_z[0] * Z1_std + gamma_z[1] * Z2 + gamma_z[2] * Z3_std
        + X @ gamma_x
        + study_treat_intercept[study_id]
    )
    if n_z_vars < 3:
        logit_a = (
            gamma_z[0] * Z1_std + gamma_z[1] * Z2
            + X @ gamma_x
            + study_treat_intercept[study_id]
        )
    if n_z_vars < 2:
        logit_a = (
            gamma_z[0] * Z1_std
            + X @ gamma_x
            + study_treat_intercept[study_id]
        )
    gamma_0 = _solve_treatment_intercept(logit_a, target_rate=treatment_prevalence)
    prob_a = expit(gamma_0 + logit_a)
    A = rng.binomial(1, prob_a, n).astype(float)

    # --- Binary outcome Y ---
    ze = z_effect_scale
    xe = x_effect_scale

    # Main Z effects (log-OR scale)
    logit_y0 = (
        ze * (0.9 * Z1_std + 0.6 * Z2 + 0.7 * Z3_std)
        + ze * 0.3 * Z1_std * Z2
        + study_outcome_intercept[study_id]
    )

    if n_z_vars < 3:
        logit_y0 = (
            ze * (0.9 * Z1_std + 0.6 * Z2 + 0.3 * Z1_std * Z2)
            + study_outcome_intercept[study_id]
        )
    if n_z_vars < 2:
        logit_y0 = (
            ze * 0.9 * Z1_std
            + study_outcome_intercept[study_id]
        )

    # Weak X -> Y direct effects
    x_betas_base = np.array([0.15, 0.10, 0.12, 0.08, 0.10, 0.05, 0.05, 0.08, 0.06, 0.07])
    if X.shape[1] > len(x_betas_base):
        x_betas_base = np.concatenate([x_betas_base, np.zeros(X.shape[1] - len(x_betas_base))])
    x_betas = xe * x_betas_base
    logit_y0 += X @ x_betas

    # Treatment effect and effect modification
    if tau is None:
        tau = 0.07  # main treatment effect (log-OR) at reference Z
    if delta is None:
        delta = np.array([0.05, -0.04, 0.05])  # Z1, Z2, Z3 interaction coefficients
    else:
        delta = np.asarray(delta, dtype=float)
    treatment_effect = tau + delta[0] * Z1_std + delta[1] * Z2 + delta[2] * Z3_std

    # Calibrate intercept to target overall event rate
    beta_0 = _solve_intercept(logit_y0, A, treatment_effect, target_rate=event_rate)
    prob_y = expit(beta_0 + logit_y0 + A * treatment_effect)
    Y = rng.binomial(1, prob_y, n).astype(float)

    # Potential outcome probabilities and true CATE
    p_y_a0 = expit(beta_0 + logit_y0)
    p_y_a1 = expit(beta_0 + logit_y0 + treatment_effect)
    true_cate = p_y_a1 - p_y_a0  # individual risk difference

    # True ATE as population risk difference (collapsible)
    true_ate_riskdiff = float(true_cate.mean())

    # True ATE as population marginal log-OR (for reference only; log-OR is non-collapsible)
    mean_p1 = p_y_a1.mean()
    mean_p0 = p_y_a0.mean()
    if 0 < mean_p1 < 1 and 0 < mean_p0 < 1:
        true_ate_logor = logit(mean_p1) - logit(mean_p0)
    else:
        true_ate_logor = float(np.nan)

    # True cluster labels from Z
    Z1_cat = np.digitize(Z1, bins=[45, 70])
    Z2_cat = Z2.astype(int)
    if n_z_vars == 3:
        Z_clusters = Z1_cat * 6 + Z2_cat * 3 + Z3.astype(int)
    elif n_z_vars == 2:
        Z_clusters = Z1_cat * 2 + Z2_cat
    else:
        Z_clusters = Z1_cat

    params = {
        'n': n,
        'z_effect_scale': z_effect_scale,
        'zx_influence_scale': zx_influence_scale,
        'x_effect_scale': x_effect_scale,
        'noise_level': noise_level,
        'n_z_vars': n_z_vars,
        'nonlinear': nonlinear,
        'event_rate': event_rate,
        'treatment_prevalence': treatment_prevalence,
        'n_studies': n_studies,
        'study_effect_scale': float(study_effect_scale),
        'actual_event_rate': float(Y.mean()),
        'actual_treatment_prevalence': float(A.mean()),
        'true_ate_riskdiff': float(true_ate_riskdiff),
        'true_ate_logor': float(true_ate_logor),
        'seed': seed,
        'tau': tau,
        'delta': delta.tolist(),
        'gamma_z': gamma_z.tolist(),
        'gamma_x': gamma_x.tolist(),
    }

    return {
        'X': X,
        'Z': Z,
        'A': A,
        'Y': Y,
        'study_id': study_id.astype(int),
        'Z_clusters': Z_clusters.astype(int),
        'true_cate': true_cate,
        'true_ate_riskdiff': true_ate_riskdiff,
        'true_ate_logor': true_ate_logor,
        'p_y_a1': p_y_a1,
        'p_y_a0': p_y_a0,
        'treatment_effect': treatment_effect,
        'params': params,
    }


def define_true_strata(Z: np.ndarray, n_strata: int, method: str = 'kmeans') -> np.ndarray:
    """
    Define true strata from Z using kmeans or quantile on Z1.

    Parameters
    ----------
    Z : ndarray (n, 3)
    n_strata : int
    method : str - 'kmeans' or 'quantile'

    Returns
    -------
    labels : ndarray (n,)
    """
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    if method == 'kmeans':
        Z_scaled = StandardScaler().fit_transform(Z)
        km = KMeans(n_clusters=n_strata, n_init=10, random_state=42)
        return km.fit_predict(Z_scaled)
    elif method == 'quantile':
        quantiles = np.percentile(Z[:, 0], np.linspace(0, 100, n_strata + 1)[1:-1])
        return np.digitize(Z[:, 0], quantiles)
    else:
        raise ValueError(f"Unknown method: {method}")
