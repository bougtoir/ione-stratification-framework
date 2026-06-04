"""
Data generation module: Simulate datasets with known causal structure.
Revised for major revision: adds treatment variable A with confounding
and effect modification by Z.

DAG:  Z -> X, Z -> A, Z -> Y, X -> A (partial), A -> Y, Z x A -> Y
"""

import numpy as np
from scipy.special import expit


def generate_dataset(
    n: int = 2000,
    z_effect_scale: float = 1.0,
    zx_influence_scale: float = 1.0,
    x_effect_scale: float = 1.0,
    noise_level: float = 1.0,
    n_z_vars: int = 3,
    event_rate: float = 0.15,
    treatment_effect: float = 0.5,
    em_strength: float = 0.4,
    seed: int | None = None,
) -> dict:
    """
    Generate a simulated dataset with known causal structure including
    a binary treatment variable A.

    Parameters
    ----------
    n : int
        Sample size.
    z_effect_scale : float
        Multiplier for Z -> Y effect sizes. 1.0 = default (OR ~1.5-3.0).
    zx_influence_scale : float
        Multiplier for Z -> X pathway strengths. 1.0 = default.
    x_effect_scale : float
        Multiplier for X -> Y direct effect sizes. 1.0 = default (OR ~1.0-1.3).
    noise_level : float
        Multiplier for noise in X generation. 1.0 = default.
    n_z_vars : int
        Number of Z variables to use (1, 2, or 3).
    event_rate : float
        Target event rate (used to calibrate intercept).
    treatment_effect : float
        Main effect of treatment A on Y (log-OR scale). Default 0.5.
    em_strength : float
        Strength of effect modification (Z x A interaction on Y).
        Default 0.4. Higher = stronger effect modification by Z.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    dict with keys:
        'X': ndarray (n, 10) - general variables
        'Z': ndarray (n, 3) - critical variables (Z1=age, Z2=sex, Z3=BMI)
        'A': ndarray (n,) - binary treatment
        'Y': ndarray (n,) - binary outcome
        'Z_clusters': ndarray (n,) - true cluster labels from Z
        'true_cate': ndarray (n,) - true conditional ATE (on probability scale)
        'params': dict - generation parameters
    """
    rng = np.random.default_rng(seed)

    # --- Generate Z (critical variables) ---
    Z1 = np.clip(rng.normal(60, 12, n), 20, 95)
    Z2 = rng.binomial(1, 0.5, n).astype(float)
    Z3 = rng.choice([0, 1, 2], size=n, p=[0.3, 0.4, 0.3]).astype(float)

    Z = np.column_stack([Z1, Z2, Z3])

    Z1_std = (Z1 - 60) / 12
    Z3_std = (Z3 - 1) / 0.8

    # --- Generate X (general variables) influenced by Z ---
    s = zx_influence_scale
    nl = noise_level

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

    # --- Generate A (binary treatment) ---
    # A is confounded by Z: older, male, higher BMI -> more likely treated
    # Also partially influenced by X (through measured covariates)
    logit_a = (
        0.3 * Z1_std          # Z1 (age) -> A
        + 0.2 * Z2            # Z2 (sex) -> A
        + 0.15 * Z3_std       # Z3 (BMI) -> A
        + 0.1 * X[:, 0]       # X1 (HbA1c) -> A (partial)
        + 0.05 * X[:, 2]      # X3 (SBP) -> A (partial)
    )

    # Mask Z -> A based on n_z_vars
    if n_z_vars < 3:
        logit_a = 0.3 * Z1_std + 0.2 * Z2 + 0.1 * X[:, 0] + 0.05 * X[:, 2]
    if n_z_vars < 2:
        logit_a = 0.3 * Z1_std + 0.1 * X[:, 0] + 0.05 * X[:, 2]

    # Calibrate to ~50% treatment prevalence
    logit_a -= np.mean(logit_a)
    prob_a = expit(logit_a)
    A = rng.binomial(1, prob_a, n).astype(float)

    # --- Generate Y (binary outcome) ---
    # Y depends on Z, X, A, and Z x A (effect modification)
    ze = z_effect_scale
    xe = x_effect_scale
    te = treatment_effect
    em = em_strength

    # Z -> Y (direct confounding pathway)
    z_component = ze * (0.9 * Z1_std + 0.6 * Z2 + 0.7 * Z3_std)
    z_component += ze * 0.3 * Z1_std * Z2  # Z1 x Z2 interaction on Y

    if n_z_vars < 3:
        z_component = ze * (0.9 * Z1_std + 0.6 * Z2 + ze * 0.3 * Z1_std * Z2)
    if n_z_vars < 2:
        z_component = ze * 0.9 * Z1_std

    # X -> Y direct effects (weak)
    x_betas = xe * np.array([0.15, 0.10, 0.12, 0.08, 0.10,
                             0.05, 0.05, 0.08, 0.06, 0.07])
    x_component = X @ x_betas

    # A -> Y (main treatment effect)
    a_component = te * A

    # Z x A -> Y (effect modification: treatment effect varies by Z)
    # Older patients benefit more, males benefit less, higher BMI benefits more
    em_component = em * A * (0.5 * Z1_std - 0.3 * Z2 + 0.3 * Z3_std)
    if n_z_vars < 3:
        em_component = em * A * (0.5 * Z1_std - 0.3 * Z2)
    if n_z_vars < 2:
        em_component = em * A * 0.5 * Z1_std

    logit_y = z_component + x_component + a_component + em_component

    # Calibrate intercept
    intercept = np.log(event_rate / (1 - event_rate)) - np.mean(logit_y)
    logit_y += intercept

    prob_y = expit(logit_y)
    Y = rng.binomial(1, prob_y, n).astype(float)

    # --- True CATE (on probability scale) for evaluation ---
    # CATE_i = P(Y=1|A=1, Z_i, X_i) - P(Y=1|A=0, Z_i, X_i)
    base = z_component + x_component + intercept

    # Effect modification term (without A multiplier)
    if n_z_vars == 3:
        em_modifier = em * (0.5 * Z1_std - 0.3 * Z2 + 0.3 * Z3_std)
    elif n_z_vars == 2:
        em_modifier = em * (0.5 * Z1_std - 0.3 * Z2)
    else:
        em_modifier = em * 0.5 * Z1_std

    logit_y_a1 = base + te + em_modifier  # potential outcome under A=1
    logit_y_a0 = base                      # potential outcome under A=0
    true_cate = expit(logit_y_a1) - expit(logit_y_a0)

    # --- Define true cluster labels from Z ---
    Z1_cat = np.digitize(Z1, bins=[45, 70])  # 0, 1, 2
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
        'event_rate': event_rate,
        'actual_event_rate': float(Y.mean()),
        'treatment_effect': treatment_effect,
        'em_strength': em_strength,
        'treatment_prevalence': float(A.mean()),
        'seed': seed,
    }

    return {
        'X': X,
        'Z': Z,
        'A': A,
        'Y': Y,
        'Z_clusters': Z_clusters.astype(int),
        'true_cate': true_cate,
        'params': params,
    }


def define_true_strata(Z: np.ndarray, n_strata: int, method: str = 'kmeans') -> np.ndarray:
    """
    Define true strata from Z using different methods (for evaluation).

    Parameters
    ----------
    Z : ndarray (n, 3)
    n_strata : int
    method : str - 'kmeans' or 'quantile'

    Returns
    -------
    labels : ndarray (n,) - strata labels
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
