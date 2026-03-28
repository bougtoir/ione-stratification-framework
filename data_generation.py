"""
Data generation module: Simulate datasets with known causal structure.
Based on the causal DAG specified in the spec v0.2.
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
    seed: int | None = None,
) -> dict:
    """
    Generate a simulated dataset with known causal structure.

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
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    dict with keys:
        'X': ndarray (n, 10) - general variables
        'Z': ndarray (n, 3) - critical variables (Z1=age, Z2=sex, Z3=BMI)
        'Y': ndarray (n,) - binary outcome
        'Z_clusters': ndarray (n,) - true cluster labels from Z
        'params': dict - generation parameters
    """
    rng = np.random.default_rng(seed)

    # --- Generate Z (critical variables) ---
    # Z1: Age ~ N(60, 12^2), clipped [20, 95]
    Z1 = np.clip(rng.normal(60, 12, n), 20, 95)
    # Z2: Sex ~ Bernoulli(0.5)
    Z2 = rng.binomial(1, 0.5, n).astype(float)
    # Z3: BMI category ~ Multinomial(0.3, 0.4, 0.3) -> 0, 1, 2
    Z3 = rng.choice([0, 1, 2], size=n, p=[0.3, 0.4, 0.3]).astype(float)

    Z = np.column_stack([Z1, Z2, Z3])

    # Standardize Z for generating X
    Z1_std = (Z1 - 60) / 12
    Z3_std = (Z3 - 1) / 0.8  # center around middle category

    # --- Generate X (general variables) influenced by Z ---
    # Influence matrix: Z -> X pathways
    # Each X_i = sum(alpha_ij * Z_j_std) + noise
    # Influence strengths: strong=0.5, medium=0.3, weak=0.15

    s = zx_influence_scale
    nl = noise_level

    # X1: HbA1c - Z1: strong, Z3: strong
    X1 = s * (0.5 * Z1_std + 0.5 * Z3_std) + rng.normal(0, nl, n)
    # X2: Total cholesterol - Z1: medium, Z2: weak
    X2 = s * (0.3 * Z1_std + 0.15 * Z2) + rng.normal(0, nl, n)
    # X3: Systolic BP - Z1: strong
    X3 = s * (0.5 * Z1_std) + rng.normal(0, nl, n)
    # X4: ALT - Z3: medium
    X4 = s * (0.3 * Z3_std) + rng.normal(0, nl, n)
    # X5: Creatinine - Z1: medium, Z2: weak
    X5 = s * (0.3 * Z1_std + 0.15 * Z2) + rng.normal(0, nl, n)
    # X6: Hemoglobin - Z2: strong
    X6 = s * (0.5 * Z2) + rng.normal(0, nl, n)
    # X7: WBC - Z1: weak
    X7 = s * (0.15 * Z1_std) + rng.normal(0, nl, n)
    # X8: Albumin - Z1: medium
    X8 = s * (0.3 * Z1_std) + rng.normal(0, nl, n)
    # X9: CRP - Z1: weak, Z3: weak
    X9 = s * (0.15 * Z1_std + 0.15 * Z3_std) + rng.normal(0, nl, n)
    # X10: Uric acid - Z2: medium, Z3: weak
    X10 = s * (0.3 * Z2 + 0.15 * Z3_std) + rng.normal(0, nl, n)

    X = np.column_stack([X1, X2, X3, X4, X5, X6, X7, X8, X9, X10])

    # --- Generate Y (binary outcome) ---
    # logit(P(Y=1)) = beta_0 + beta_Z * Z_std + beta_X * X + interaction + noise

    ze = z_effect_scale
    xe = x_effect_scale

    # Z effects (log-OR scale): age ~log(2.5), sex ~log(1.8), BMI ~log(2.0)
    logit_y = (
        ze * (0.9 * Z1_std + 0.6 * Z2 + 0.7 * Z3_std)  # Z -> Y
        + ze * 0.3 * Z1_std * Z2  # Z1 x Z2 interaction
    )

    # Mask Z effects based on n_z_vars
    if n_z_vars < 3:
        # Remove Z3 effect
        logit_y = ze * (0.9 * Z1_std + 0.6 * Z2 + ze * 0.3 * Z1_std * Z2)
    if n_z_vars < 2:
        # Remove Z2 effect
        logit_y = ze * 0.9 * Z1_std

    # X -> Y direct effects (weak: log-OR ~0.05-0.25)
    x_betas = xe * np.array([0.15, 0.10, 0.12, 0.08, 0.10, 0.05, 0.05, 0.08, 0.06, 0.07])
    logit_y += X @ x_betas

    # Calibrate intercept to achieve target event rate
    intercept = np.log(event_rate / (1 - event_rate)) - np.mean(logit_y)
    logit_y += intercept

    prob_y = expit(logit_y)
    Y = rng.binomial(1, prob_y, n).astype(float)

    # --- Define true cluster labels from Z ---
    # Z1: 3 categories (young <45, middle 45-70, old >70)
    Z1_cat = np.digitize(Z1, bins=[45, 70])  # 0, 1, 2
    # Z2: 2 categories (0, 1)
    Z2_cat = Z2.astype(int)
    # Z3: 3 categories (0, 1, 2) - already categorical

    if n_z_vars == 3:
        Z_clusters = Z1_cat * 6 + Z2_cat * 3 + Z3.astype(int)  # up to 18 clusters
    elif n_z_vars == 2:
        Z_clusters = Z1_cat * 2 + Z2_cat  # up to 6 clusters
    else:
        Z_clusters = Z1_cat  # up to 3 clusters

    params = {
        'n': n,
        'z_effect_scale': z_effect_scale,
        'zx_influence_scale': zx_influence_scale,
        'x_effect_scale': x_effect_scale,
        'noise_level': noise_level,
        'n_z_vars': n_z_vars,
        'event_rate': event_rate,
        'actual_event_rate': float(Y.mean()),
        'seed': seed,
    }

    return {
        'X': X,
        'Z': Z,
        'Y': Y,
        'Z_clusters': Z_clusters.astype(int),
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
        # Use Z1 (age) quantiles as simple stratification
        quantiles = np.percentile(Z[:, 0], np.linspace(0, 100, n_strata + 1)[1:-1])
        return np.digitize(Z[:, 0], quantiles)
    else:
        raise ValueError(f"Unknown method: {method}")
