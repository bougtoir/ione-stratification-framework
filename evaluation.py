"""
Evaluation module: All metrics for assessing stratification quality.
- Cluster agreement (ARI, NMI, V-measure)
- Z distribution homogeneity (eta-squared, entropy)
- Simpson's paradox resolution
- Coherence degree indicators (C1-C4)
- Pseudo-randomization metrics (SMD, bias, RMSE, coverage)
"""

import numpy as np
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, v_measure_score
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


# ============================================================
# 1. Cluster Agreement Metrics (Section 5.3a)
# ============================================================

def compute_cluster_agreement(true_labels: np.ndarray, pred_labels: np.ndarray) -> dict:
    """Compute ARI, NMI, V-measure between true Z clusters and predicted strata."""
    return {
        'ARI': adjusted_rand_score(true_labels, pred_labels),
        'NMI': normalized_mutual_info_score(true_labels, pred_labels),
        'V_measure': v_measure_score(true_labels, pred_labels),
    }


# ============================================================
# 2. Z Distribution Homogeneity (Section 5.3b)
# ============================================================

def compute_eta_squared(Z: np.ndarray, strata: np.ndarray) -> dict:
    """
    Compute eta-squared for each Z variable across strata.
    eta² = SS_between / SS_total
    """
    results = {}
    z_names = ['Z1_age', 'Z2_sex', 'Z3_bmi']
    for j in range(Z.shape[1]):
        z_col = Z[:, j]
        ss_total = np.sum((z_col - z_col.mean()) ** 2)
        if ss_total == 0:
            results[f'eta2_{z_names[j]}'] = 0.0
            continue
        ss_between = 0
        for s in np.unique(strata):
            mask = strata == s
            n_s = mask.sum()
            if n_s > 0:
                ss_between += n_s * (z_col[mask].mean() - z_col.mean()) ** 2
        results[f'eta2_{z_names[j]}'] = float(ss_between / ss_total)
    results['eta2_mean'] = float(np.mean(list(results.values())))
    return results


def compute_within_strata_entropy(Z: np.ndarray, strata: np.ndarray) -> dict:
    """
    Compute entropy of Z2 (sex) within each stratum.
    Lower entropy = better capture of sex distribution.
    """
    unique_strata = np.unique(strata)
    entropies = []
    for s in unique_strata:
        mask = strata == s
        z2_in_stratum = Z[mask, 1]
        p = z2_in_stratum.mean()
        if p == 0 or p == 1:
            entropies.append(0.0)
        else:
            entropies.append(-p * np.log2(p) - (1 - p) * np.log2(1 - p))

    weights = np.array([np.sum(strata == s) for s in unique_strata]) / len(strata)
    weighted_entropy = float(np.sum(np.array(entropies) * weights))
    max_entropy = 1.0  # max binary entropy

    return {
        'weighted_entropy_Z2': weighted_entropy,
        'entropy_reduction_Z2': 1.0 - weighted_entropy / max_entropy if max_entropy > 0 else 0.0,
    }


# ============================================================
# 3. Simpson's Paradox Resolution (Section 5.3c)
# ============================================================

def compute_simpson_resolution(X: np.ndarray, Y: np.ndarray, strata: np.ndarray) -> dict:
    """
    Check if Simpson's paradox is resolved by stratification.
    Compare overall X->Y direction with within-strata directions.
    """
    n_vars = X.shape[1]
    overall_directions = []
    strata_consistent = []

    unique_strata = np.unique(strata)

    for j in range(n_vars):
        # Overall correlation direction
        if np.std(X[:, j]) > 0 and np.std(Y) > 0:
            overall_corr = np.corrcoef(X[:, j], Y)[0, 1]
        else:
            overall_corr = 0.0
        overall_dir = np.sign(overall_corr)
        overall_directions.append(overall_dir)

        # Within-strata directions
        within_dirs = []
        for s in unique_strata:
            mask = strata == s
            if mask.sum() < 10:
                continue
            x_s = X[mask, j]
            y_s = Y[mask]
            if np.std(x_s) > 0 and np.std(y_s) > 0:
                corr_s = np.corrcoef(x_s, y_s)[0, 1]
                within_dirs.append(np.sign(corr_s))

        if len(within_dirs) > 0:
            # All strata agree with overall?
            all_same = all(d == overall_dir for d in within_dirs)
            strata_consistent.append(all_same)

    direction_consistency = float(np.mean(strata_consistent)) if strata_consistent else 1.0

    return {
        'direction_consistency_rate': direction_consistency,
        'n_variables_checked': len(strata_consistent),
    }


# ============================================================
# 4. Coherence Degree Indicators (Section 5.5b)
# ============================================================

def compute_coherence_c1(X: np.ndarray, Y: np.ndarray, strata: np.ndarray) -> float:
    """
    C1 (heterogeneity-based): 1 - I²(between strata).
    Treats each stratum as a "sub-study" in meta-analysis.
    """
    unique_strata = np.unique(strata)
    if len(unique_strata) < 2:
        return 1.0

    # Compute effect (mean Y) in each stratum
    effects = []
    variances = []
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s < 2:
            continue
        y_s = Y[mask]
        mean_y = y_s.mean()
        var_y = y_s.var(ddof=1) / n_s  # variance of the mean
        effects.append(mean_y)
        variances.append(max(var_y, 1e-10))

    if len(effects) < 2:
        return 1.0

    effects = np.array(effects)
    variances = np.array(variances)
    weights = 1.0 / variances

    # Fixed-effects pooled estimate
    pooled = np.sum(weights * effects) / np.sum(weights)

    # Cochran's Q
    Q = np.sum(weights * (effects - pooled) ** 2)
    df = len(effects) - 1

    # I²
    if Q > df:
        I_squared = (Q - df) / Q
    else:
        I_squared = 0.0

    return float(1.0 - I_squared)


def compute_coherence_c2(X: np.ndarray, Y: np.ndarray, strata: np.ndarray) -> float:
    """
    C2 (residual structure-based): 1 - (systematic residual / total variance).
    Checks if within-strata residuals show systematic patterns.
    """
    from sklearn.linear_model import LogisticRegression

    unique_strata = np.unique(strata)
    total_residual_var = 0.0
    systematic_component = 0.0
    total_n = 0

    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s < 20:
            continue

        X_s = X[mask]
        Y_s = Y[mask]

        # Fit model within stratum
        if len(np.unique(Y_s)) < 2:
            continue

        model = LogisticRegression(max_iter=500, penalty='l2', C=1.0, solver='lbfgs')
        try:
            model.fit(X_s, Y_s)
            p_hat = model.predict_proba(X_s)[:, 1]
        except Exception:
            continue

        residuals = Y_s - p_hat
        total_var_s = np.var(residuals)
        total_residual_var += total_var_s * n_s

        # Systematic component: check if residuals correlate with X
        systematic_var = 0.0
        for j in range(X_s.shape[1]):
            if np.std(X_s[:, j]) > 0:
                corr = np.corrcoef(X_s[:, j], residuals)[0, 1]
                systematic_var += corr ** 2
        systematic_var /= X_s.shape[1]
        systematic_component += systematic_var * n_s
        total_n += n_s

    if total_n == 0 or total_residual_var == 0:
        return 1.0

    ratio = systematic_component / total_n
    return float(1.0 - min(ratio, 1.0))


def compute_coherence_c3(X: np.ndarray, Y: np.ndarray, strata: np.ndarray,
                         n_bootstrap: int = 100) -> float:
    """
    C3 (prediction stability-based): 1 - CV(bootstrap variance of stratified effects).
    """
    unique_strata = np.unique(strata)
    n = len(Y)
    rng = np.random.default_rng(42)

    bootstrap_effects = []
    for _ in range(n_bootstrap):
        idx = rng.choice(n, n, replace=True)
        strata_b = strata[idx]
        Y_b = Y[idx]

        stratum_effects = []
        for s in unique_strata:
            mask = strata_b == s
            if mask.sum() > 5:
                stratum_effects.append(Y_b[mask].mean())

        if len(stratum_effects) > 1:
            bootstrap_effects.append(np.var(stratum_effects))

    if len(bootstrap_effects) < 2:
        return 1.0

    mean_var = np.mean(bootstrap_effects)
    std_var = np.std(bootstrap_effects)
    cv = std_var / mean_var if mean_var > 0 else 0.0

    return float(1.0 - min(cv, 1.0))


def compute_coherence_c4(Z: np.ndarray, strata: np.ndarray) -> float:
    """
    C4 (entropy-based): 1 - H(within-strata Z distribution) / H_max.
    Simulation-only metric (requires Z knowledge).
    """
    unique_strata = np.unique(strata)
    n = len(strata)

    # Discretize Z for entropy calculation
    Z1_cat = np.digitize(Z[:, 0], bins=[45, 70])  # 3 categories
    Z2_cat = Z[:, 1].astype(int)  # 2 categories
    Z3_cat = Z[:, 2].astype(int)  # 3 categories

    # Combined category
    Z_combined = Z1_cat * 6 + Z2_cat * 3 + Z3_cat

    # Maximum entropy (uniform distribution over all Z categories)
    n_categories = len(np.unique(Z_combined))
    H_max = np.log2(n_categories) if n_categories > 1 else 1.0

    # Weighted within-strata entropy
    H_within = 0.0
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s == 0:
            continue

        z_s = Z_combined[mask]
        _, counts = np.unique(z_s, return_counts=True)
        probs = counts / n_s
        entropy_s = -np.sum(probs * np.log2(probs + 1e-10))
        H_within += (n_s / n) * entropy_s

    return float(1.0 - H_within / H_max) if H_max > 0 else 1.0


def compute_all_coherence(X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                          strata: np.ndarray) -> dict:
    """Compute all coherence indicators."""
    return {
        'C1_heterogeneity': compute_coherence_c1(X, Y, strata),
        'C2_residual_structure': compute_coherence_c2(X, Y, strata),
        'C3_prediction_stability': compute_coherence_c3(X, Y, strata),
        'C4_entropy': compute_coherence_c4(Z, strata),
    }


# ============================================================
# 5. Pseudo-randomization Metrics (Section 6.2)
# ============================================================

def compute_smd(Z: np.ndarray, strata: np.ndarray) -> dict:
    """
    Compute standardized mean differences of Z across strata.
    For each stratum pair, compute SMD for each Z variable.
    """
    unique_strata = np.unique(strata)
    z_names = ['Z1_age', 'Z2_sex', 'Z3_bmi']
    max_smds = {}

    for j in range(Z.shape[1]):
        smds = []
        for i, s1 in enumerate(unique_strata):
            for s2 in unique_strata[i + 1:]:
                z1 = Z[strata == s1, j]
                z2 = Z[strata == s2, j]
                if len(z1) < 2 or len(z2) < 2:
                    continue
                pooled_std = np.sqrt((np.var(z1, ddof=1) + np.var(z2, ddof=1)) / 2)
                if pooled_std > 0:
                    smd = abs(z1.mean() - z2.mean()) / pooled_std
                    smds.append(smd)
        max_smds[f'max_SMD_{z_names[j]}'] = float(max(smds)) if smds else 0.0

    max_smds['mean_max_SMD'] = float(np.mean(list(max_smds.values())))
    return max_smds


def compute_effect_estimation_bias(Y: np.ndarray, Z: np.ndarray, strata: np.ndarray,
                                   true_effect: float | None = None) -> dict:
    """
    Compute bias in effect estimation.
    Uses Z1 (age) median split as "treatment" for evaluation.
    """
    # Define "treatment" as above-median age
    treatment = (Z[:, 0] > np.median(Z[:, 0])).astype(float)

    # Crude (unstratified) effect
    y_treated = Y[treatment == 1].mean()
    y_control = Y[treatment == 0].mean()
    crude_effect = y_treated - y_control

    # Stratified effect (Mantel-Haenszel style weighted average)
    unique_strata = np.unique(strata)
    weighted_effects = []
    weights = []
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s < 10:
            continue
        t_mask = mask & (treatment == 1)
        c_mask = mask & (treatment == 0)
        if t_mask.sum() < 2 or c_mask.sum() < 2:
            continue
        effect_s = Y[t_mask].mean() - Y[c_mask].mean()
        weighted_effects.append(effect_s)
        weights.append(n_s)

    if len(weighted_effects) > 0:
        weights = np.array(weights, dtype=float)
        weights /= weights.sum()
        stratified_effect = float(np.sum(np.array(weighted_effects) * weights))
    else:
        stratified_effect = crude_effect

    # True effect (oracle: stratify by Z itself)
    if true_effect is None:
        # Compute oracle effect using Z-based stratification
        z_strata = np.digitize(Z[:, 0], bins=np.percentile(Z[:, 0], [25, 50, 75]))
        oracle_effects = []
        oracle_weights = []
        for s in np.unique(z_strata):
            mask = z_strata == s
            t_mask = mask & (treatment == 1)
            c_mask = mask & (treatment == 0)
            if t_mask.sum() < 2 or c_mask.sum() < 2:
                continue
            oracle_effects.append(Y[t_mask].mean() - Y[c_mask].mean())
            oracle_weights.append(mask.sum())
        if oracle_effects:
            oracle_weights = np.array(oracle_weights, dtype=float)
            oracle_weights /= oracle_weights.sum()
            true_effect = float(np.sum(np.array(oracle_effects) * oracle_weights))
        else:
            true_effect = crude_effect

    return {
        'crude_effect': float(crude_effect),
        'stratified_effect': stratified_effect,
        'oracle_effect': true_effect,
        'bias_crude': float(abs(crude_effect - true_effect)),
        'bias_stratified': float(abs(stratified_effect - true_effect)),
        'bias_reduction': float(abs(crude_effect - true_effect) - abs(stratified_effect - true_effect)),
    }


# ============================================================
# 6. Combined evaluation
# ============================================================

def evaluate_stratification(X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                            Z_clusters: np.ndarray, strata: np.ndarray) -> dict:
    """Run all evaluation metrics on a single stratification result."""
    results = {}

    # Cluster agreement
    results.update(compute_cluster_agreement(Z_clusters, strata))

    # Z distribution homogeneity
    results.update(compute_eta_squared(Z, strata))

    # Within-strata entropy
    results.update(compute_within_strata_entropy(Z, strata))

    # Simpson's paradox resolution
    results.update(compute_simpson_resolution(X, Y, strata))

    # Coherence indicators
    results.update(compute_all_coherence(X, Y, Z, strata))

    # SMD
    results.update(compute_smd(Z, strata))

    # Effect estimation bias
    results.update(compute_effect_estimation_bias(Y, Z, strata))

    return results
