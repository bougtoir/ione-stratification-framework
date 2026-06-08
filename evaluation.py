"""
Evaluation module: All metrics for assessing stratification quality.
Revised: C1 uses treatment-outcome log OR, adds W (within-stratum homogeneity),
adds MC SE computation, and treatment effect bias reduction metrics.
"""

import numpy as np
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, v_measure_score
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


# ============================================================
# 1. Cluster Agreement Metrics
# ============================================================

def compute_cluster_agreement(true_labels: np.ndarray, pred_labels: np.ndarray) -> dict:
    """Compute ARI, NMI, V-measure between true Z clusters and predicted strata."""
    return {
        'ARI': adjusted_rand_score(true_labels, pred_labels),
        'NMI': normalized_mutual_info_score(true_labels, pred_labels),
        'V_measure': v_measure_score(true_labels, pred_labels),
    }


# ============================================================
# 2. Z Distribution Homogeneity
# ============================================================

def compute_eta_squared(Z: np.ndarray, strata: np.ndarray) -> dict:
    """Compute eta-squared for each Z variable across strata."""
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


# ============================================================
# 3. Coherence Indicator C1 (revised: uses treatment-outcome log OR)
# ============================================================

def _stratum_log_or(Y: np.ndarray, A: np.ndarray, continuity: float = 0.5) -> tuple:
    """
    Compute log odds ratio of A-Y association within a stratum.
    Returns (log_OR, variance_log_OR).
    Uses continuity correction for zero cells.
    """
    a = np.sum((A == 1) & (Y == 1)) + continuity
    b = np.sum((A == 1) & (Y == 0)) + continuity
    c = np.sum((A == 0) & (Y == 1)) + continuity
    d = np.sum((A == 0) & (Y == 0)) + continuity
    log_or = np.log(a * d / (b * c))
    var_log_or = 1/a + 1/b + 1/c + 1/d
    return log_or, var_log_or


def compute_coherence_c1(X: np.ndarray, Y: np.ndarray, strata: np.ndarray,
                         A: np.ndarray | None = None) -> float:
    """
    C1 incoherence indicator: 1 - I²(between-stratum treatment effects).
    When A is provided, computes I² from stratum-specific log ORs of A->Y.
    When A is None, falls back to stratum means of Y.

    Interpretation:
    - C1 near 0: high between-stratum heterogeneity in treatment effects,
      indicating the stratification detected population incoherence.
    - C1 near 1: low between-stratum heterogeneity, indicating that
      stratum-specific effects are homogeneous (no detectable structure).
    """
    unique_strata = np.unique(strata)
    if len(unique_strata) < 2:
        return 1.0

    if A is not None:
        effects = []
        variances = []
        for s in unique_strata:
            mask = strata == s
            n_s = mask.sum()
            if n_s < 10:
                continue
            Y_s, A_s = Y[mask], A[mask]
            if len(np.unique(A_s)) < 2 or len(np.unique(Y_s)) < 2:
                continue
            log_or, var_log_or = _stratum_log_or(Y_s, A_s)
            if np.isfinite(log_or) and np.isfinite(var_log_or) and var_log_or > 0:
                effects.append(log_or)
                variances.append(var_log_or)
    else:
        effects = []
        variances = []
        for s in unique_strata:
            mask = strata == s
            n_s = mask.sum()
            if n_s < 2:
                continue
            y_s = Y[mask]
            mean_y = y_s.mean()
            var_y = y_s.var(ddof=1) / n_s
            effects.append(mean_y)
            variances.append(max(var_y, 1e-10))

    if len(effects) < 2:
        return 1.0

    effects = np.array(effects)
    variances = np.array(variances)
    weights = 1.0 / variances

    pooled = np.sum(weights * effects) / np.sum(weights)
    Q = np.sum(weights * (effects - pooled) ** 2)
    df = len(effects) - 1

    I_squared = max(0.0, (Q - df) / Q) if Q > df else 0.0
    return float(1.0 - I_squared)


# ============================================================
# 4. Within-Stratum Homogeneity W (new)
# ============================================================

def compute_within_stratum_homogeneity(Y: np.ndarray, A: np.ndarray,
                                       strata: np.ndarray,
                                       true_cate: np.ndarray | None = None
                                       ) -> float:
    """
    W: Within-stratum treatment effect homogeneity indicator.
    W = 1 - (weighted mean within-stratum CATE variance) / (overall CATE variance).

    If true_cate is provided (simulation), uses it directly.
    Otherwise estimates from observed data using stratum-specific
    predicted treatment effects.

    W near 1: within-stratum effects are homogeneous (good).
    W near 0: substantial within-stratum heterogeneity remains.
    """
    unique_strata = np.unique(strata)

    if true_cate is not None:
        # Use true CATE (available in simulation)
        overall_var = np.var(true_cate)
        if overall_var < 1e-10:
            return 1.0
        within_var = 0.0
        total_n = 0
        for s in unique_strata:
            mask = strata == s
            n_s = mask.sum()
            if n_s < 2:
                continue
            within_var += n_s * np.var(true_cate[mask])
            total_n += n_s
        if total_n == 0:
            return 1.0
        within_var /= total_n
        return float(1.0 - within_var / overall_var)

    # Observed-data fallback: W requires individual-level CATE estimates.
    # Without true_cate or a CATE estimation model, W is not computable.
    # Return NaN to signal that the metric is unavailable.
    return np.nan


# ============================================================
# 5. Direction Consistency (Simpson's paradox resolution)
# ============================================================

def compute_simpson_resolution(X: np.ndarray, Y: np.ndarray, A: np.ndarray,
                               strata: np.ndarray) -> dict:
    """
    Check if Simpson's paradox is resolved by stratification.
    Compare overall A->Y direction with within-strata A->Y directions.
    """
    unique_strata = np.unique(strata)

    # Overall A->Y direction
    if len(np.unique(A)) < 2 or len(np.unique(Y)) < 2:
        return {'direction_consistency_rate': 1.0, 'simpson_detected': False}

    overall_rd = Y[A == 1].mean() - Y[A == 0].mean()
    overall_dir = np.sign(overall_rd)

    within_dirs = []
    for s in unique_strata:
        mask = strata == s
        if mask.sum() < 20:
            continue
        A_s, Y_s = A[mask], Y[mask]
        if len(np.unique(A_s)) < 2:
            continue
        rd_s = Y_s[A_s == 1].mean() - Y_s[A_s == 0].mean()
        within_dirs.append(np.sign(rd_s))

    if len(within_dirs) == 0:
        return {'direction_consistency_rate': 1.0, 'simpson_detected': False}

    consistent = sum(1 for d in within_dirs if d == overall_dir)
    rate = consistent / len(within_dirs)
    simpson = rate < 1.0  # at least one reversal

    return {
        'direction_consistency_rate': float(rate),
        'simpson_detected': simpson,
    }


# ============================================================
# 6. Treatment Effect Bias Reduction
# ============================================================

def compute_ate_bias(Y: np.ndarray, A: np.ndarray, strata: np.ndarray,
                     true_cate: np.ndarray | None = None) -> dict:
    """
    Compute treatment effect estimation bias before and after stratification.
    True ATE = mean(true_cate) if available.
    """
    if A is None or len(np.unique(A)) < 2:
        return {
            'crude_ate': np.nan, 'stratified_ate': np.nan,
            'true_ate': np.nan, 'bias_crude': np.nan,
            'bias_stratified': np.nan, 'bias_reduction': np.nan,
        }

    # True ATE
    true_ate = float(np.mean(true_cate)) if true_cate is not None else np.nan

    # Crude ATE (unadjusted)
    crude_ate = float(Y[A == 1].mean() - Y[A == 0].mean())

    # Stratified ATE (weighted average of within-stratum RDs)
    unique_strata = np.unique(strata)
    stratum_rds = []
    stratum_ns = []
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s < 10:
            continue
        A_s, Y_s = A[mask], Y[mask]
        if A_s.sum() < 2 or (1 - A_s).sum() < 2:
            continue
        rd = Y_s[A_s == 1].mean() - Y_s[A_s == 0].mean()
        stratum_rds.append(rd)
        stratum_ns.append(n_s)

    if len(stratum_rds) > 0:
        weights = np.array(stratum_ns, dtype=float)
        weights /= weights.sum()
        stratified_ate = float(np.sum(np.array(stratum_rds) * weights))
    else:
        stratified_ate = crude_ate

    result = {
        'crude_ate': crude_ate,
        'stratified_ate': stratified_ate,
        'true_ate': true_ate,
    }

    if np.isfinite(true_ate):
        result['bias_crude'] = float(abs(crude_ate - true_ate))
        result['bias_stratified'] = float(abs(stratified_ate - true_ate))
        result['bias_reduction'] = float(result['bias_crude'] - result['bias_stratified'])
    else:
        result['bias_crude'] = np.nan
        result['bias_stratified'] = np.nan
        result['bias_reduction'] = np.nan

    return result


# ============================================================
# 7. CATE heterogeneity across strata
# ============================================================

def compute_cate_heterogeneity(true_cate: np.ndarray, strata: np.ndarray) -> dict:
    """
    Quantify how much the true CATE varies across discovered strata.
    Higher between-stratum CATE variance = better at separating effect-modified groups.
    """
    unique_strata = np.unique(strata)
    overall_mean = true_cate.mean()
    overall_var = true_cate.var()

    if overall_var < 1e-10 or len(unique_strata) < 2:
        return {'cate_eta2': 0.0, 'cate_range': 0.0}

    ss_between = 0.0
    stratum_means = []
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s == 0:
            continue
        mean_s = true_cate[mask].mean()
        stratum_means.append(mean_s)
        ss_between += n_s * (mean_s - overall_mean) ** 2

    ss_total = overall_var * len(true_cate)
    cate_eta2 = float(ss_between / ss_total) if ss_total > 0 else 0.0
    cate_range = float(max(stratum_means) - min(stratum_means)) if stratum_means else 0.0

    return {
        'cate_eta2': cate_eta2,
        'cate_range': cate_range,
    }


# ============================================================
# 8. SMD of Z across strata
# ============================================================

def compute_smd(Z: np.ndarray, strata: np.ndarray) -> dict:
    """Compute max standardized mean differences of Z across strata pairs."""
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


# ============================================================
# 9. Combined evaluation
# ============================================================

def evaluate_stratification(X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                            Z_clusters: np.ndarray, strata: np.ndarray,
                            A: np.ndarray | None = None,
                            true_cate: np.ndarray | None = None) -> dict:
    """Run all evaluation metrics on a single stratification result."""
    results = {}

    # Cluster agreement
    results.update(compute_cluster_agreement(Z_clusters, strata))

    # Z distribution homogeneity
    results.update(compute_eta_squared(Z, strata))

    # C1 (using treatment variable if available)
    results['C1'] = compute_coherence_c1(X, Y, strata, A=A)
    results['C1_heterogeneity'] = results['C1']  # backward compat

    # W (within-stratum homogeneity)
    if A is not None:
        results['W'] = compute_within_stratum_homogeneity(Y, A, strata,
                                                          true_cate=true_cate)

    # Direction consistency / Simpson's detection
    if A is not None:
        results.update(compute_simpson_resolution(X, Y, A, strata))

    # ATE bias reduction
    if A is not None:
        results.update(compute_ate_bias(Y, A, strata, true_cate=true_cate))

    # CATE heterogeneity across strata
    if true_cate is not None:
        results.update(compute_cate_heterogeneity(true_cate, strata))

    # SMD
    results.update(compute_smd(Z, strata))

    return results


# ============================================================
# 10. Monte Carlo Summary Statistics
# ============================================================

def compute_mc_summary(values: np.ndarray) -> dict:
    """
    Compute MC summary statistics for a set of simulation repetitions.
    Returns mean, MC SE, and 2.5/97.5 percentile bounds.
    """
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return {'mean': np.nan, 'mc_se': np.nan, 'ci_lo': np.nan, 'ci_hi': np.nan}
    return {
        'mean': float(np.mean(values)),
        'mc_se': float(np.std(values, ddof=1) / np.sqrt(len(values))),
        'ci_lo': float(np.percentile(values, 2.5)),
        'ci_hi': float(np.percentile(values, 97.5)),
    }
