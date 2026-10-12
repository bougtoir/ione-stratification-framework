"""
Evaluation module: metrics for assessing stratification quality.
"""

import numpy as np
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, v_measure_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


def _safe_logit(p: float) -> float:
    """Bounded logit to avoid infinities."""
    p = np.clip(p, 1e-10, 1 - 1e-10)
    return np.log(p / (1.0 - p))


def _compute_log_or(A: np.ndarray, Y: np.ndarray) -> tuple[float, float]:
    """
    Compute log odds ratio of Y on A from a 2x2 table.
    Uses Haldane-Anscombe (+0.5) continuity correction for empty cells.
    Returns (logOR, standard_error).
    """
    a = ((A == 1) & (Y == 1)).sum()
    b = ((A == 0) & (Y == 1)).sum()
    c = ((A == 1) & (Y == 0)).sum()
    d = ((A == 0) & (Y == 0)).sum()

    # Haldane-Anscombe correction
    a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5

    log_or = np.log(a / c) - np.log(b / d)
    se = np.sqrt(1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d)
    return float(log_or), float(se)


def _subset(*arrays, idx):
    """Index a sequence of arrays by idx (or return arrays if idx is None)."""
    if idx is None:
        return arrays
    idx = np.asarray(idx)
    return tuple(a[idx] for a in arrays)


# ============================================================
# 1. Cluster agreement
# ============================================================

def compute_cluster_agreement(true_labels: np.ndarray, pred_labels: np.ndarray) -> dict:
    """Compute ARI, NMI, V-measure between true Z clusters and predicted strata."""
    return {
        'ARI': adjusted_rand_score(true_labels, pred_labels),
        'NMI': normalized_mutual_info_score(true_labels, pred_labels),
        'V_measure': v_measure_score(true_labels, pred_labels),
    }


# ============================================================
# 2. Z distribution homogeneity
# ============================================================

def compute_eta_squared(Z: np.ndarray, strata: np.ndarray) -> dict:
    """Compute eta-squared for each Z variable across strata."""
    results = {}
    z_names = ['Z1_age', 'Z2_sex', 'Z3_bmi']
    for j in range(Z.shape[1]):
        z_col = Z[:, j]
        name = z_names[j] if j < len(z_names) else f'Z{j+1}'
        ss_total = np.sum((z_col - z_col.mean()) ** 2)
        if ss_total == 0:
            results[f'eta2_{name}'] = 0.0
            continue
        ss_between = 0
        for s in np.unique(strata):
            mask = strata == s
            n_s = mask.sum()
            if n_s > 0:
                ss_between += n_s * (z_col[mask].mean() - z_col.mean()) ** 2
        results[f'eta2_{name}'] = float(ss_between / ss_total)
    results['eta2_mean'] = float(np.mean(list(results.values())))
    return results


def compute_within_strata_entropy(Z: np.ndarray, strata: np.ndarray) -> dict:
    """Compute entropy of Z2 (binary second confounder) within each stratum, if available."""
    if Z.shape[1] < 2:
        return {'weighted_entropy_Z2': float(np.nan), 'entropy_reduction_Z2': float(np.nan)}

    unique_strata = np.unique(strata)
    entropies = []
    for s in unique_strata:
        mask = strata == s
        z2_in_stratum = Z[mask, 1]
        if len(z2_in_stratum) == 0:
            continue
        p = z2_in_stratum.mean()
        if p == 0 or p == 1:
            entropies.append(0.0)
        else:
            entropies.append(-p * np.log2(p) - (1 - p) * np.log2(1 - p))

    if len(entropies) == 0:
        return {'weighted_entropy_Z2': float(np.nan), 'entropy_reduction_Z2': float(np.nan)}

    weights = np.array([np.sum(strata == s) for s in unique_strata]) / len(strata)
    weighted_entropy = float(np.sum(np.array(entropies) * weights))
    max_entropy = 1.0

    return {
        'weighted_entropy_Z2': weighted_entropy,
        'entropy_reduction_Z2': 1.0 - weighted_entropy / max_entropy if max_entropy > 0 else 0.0,
    }


# ============================================================
# 3. Coherence indicators
# ============================================================

def compute_coherence_c1(A: np.ndarray, Y: np.ndarray, strata: np.ndarray) -> float:
    """
    C1 (between-stratum heterogeneity of treatment effects):
    1 - I^2 computed from stratum-specific log odds ratios of A -> Y.
    """
    unique_strata = np.unique(strata)
    if len(unique_strata) < 2:
        return 1.0

    log_ors, variances = [], []
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s < 2:
            continue
        a_s, y_s = A[mask], Y[mask]
        if len(np.unique(a_s)) < 2 or len(np.unique(y_s)) < 2:
            continue
        log_or_s, se_s = _compute_log_or(a_s, y_s)
        if not np.isfinite(log_or_s):
            continue
        log_ors.append(log_or_s)
        variances.append(max(se_s ** 2, 1e-10))

    if len(log_ors) < 2:
        return 1.0

    log_ors = np.array(log_ors)
    variances = np.array(variances)
    weights = 1.0 / variances

    pooled = np.sum(weights * log_ors) / np.sum(weights)
    Q = np.sum(weights * (log_ors - pooled) ** 2)
    df = len(log_ors) - 1

    if Q > df:
        I_squared = (Q - df) / Q
    else:
        I_squared = 0.0

    return float(1.0 - I_squared)


def compute_w_true(strata: np.ndarray, true_cate: np.ndarray) -> float:
    """
    W_true: within-stratum homogeneity of the true individual-level CATE.
    W = 1 - (weighted within-stratum CATE variance) / (overall CATE variance).
    """
    overall_var = np.var(true_cate, ddof=0)
    if overall_var == 0:
        return 1.0

    unique_strata = np.unique(strata)
    n = len(true_cate)
    weighted_within_var = 0.0
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s < 2:
            continue
        weighted_within_var += n_s * np.var(true_cate[mask], ddof=0)

    return float(1.0 - (weighted_within_var / n) / overall_var)


def compute_w_est(A: np.ndarray, X: np.ndarray, Y: np.ndarray, strata: np.ndarray,
                  model_spec: str = 'interaction', degree: int = 2) -> float:
    """
    W_est: within-stratum homogeneity of an estimated CATE.
    Fit an outcome model, predict potential outcomes under A=0 and A=1,
    and compute CATE estimates. Then compute W as for W_true.

    model_spec:
      'main'        : Y ~ X + A (no effect modification)
      'interaction' : Y ~ X + A + X*A (default, flexible linear interactions)
      'polynomial'  : Y ~ X + X^2 + A + X*A + X^2*A (linear + quadratic interactions)
    """
    n = X.shape[0]
    if n < 20 or len(np.unique(Y)) < 2:
        return float(np.nan)

    X_std = StandardScaler().fit_transform(X)
    A_col = A.reshape(-1, 1)

    if model_spec == 'main':
        design = np.hstack([X_std, A_col])
        design_a0 = np.hstack([X_std, np.zeros((n, 1))])
        design_a1 = np.hstack([X_std, np.ones((n, 1))])
    elif model_spec == 'interaction':
        AX = X_std * A_col
        design = np.hstack([X_std, A_col, AX])
        design_a0 = np.hstack([X_std, np.zeros((n, 1)), np.zeros((n, X.shape[1]))])
        design_a1 = np.hstack([X_std, np.ones((n, 1)), X_std])
    elif model_spec == 'polynomial':
        X2 = X_std ** 2
        design = np.hstack([X_std, X2, A_col, X_std * A_col, X2 * A_col])
        design_a0 = np.hstack([X_std, X2, np.zeros((n, 1)), np.zeros((n, X.shape[1])), np.zeros((n, X.shape[1]))])
        design_a1 = np.hstack([X_std, X2, np.ones((n, 1)), X_std, X2])
    else:
        raise ValueError(f"Unknown model_spec: {model_spec}")

    try:
        model = LogisticRegression(max_iter=1000, penalty='l2', C=0.5, solver='lbfgs')
        model.fit(design, Y)
        proba0 = model.predict_proba(design_a0)
        proba1 = model.predict_proba(design_a1)
        if proba0.shape[1] < 2 or proba1.shape[1] < 2:
            return float(np.nan)
        p0 = proba0[:, 1]
        p1 = proba1[:, 1]
    except Exception:
        return float(np.nan)

    cate_est = p1 - p0
    overall_var = np.var(cate_est, ddof=0)
    if overall_var == 0:
        return float(np.nan)

    unique_strata = np.unique(strata)
    weighted_within_var = 0.0
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s < 2:
            continue
        weighted_within_var += n_s * np.var(cate_est[mask], ddof=0)

    return float(1.0 - (weighted_within_var / n) / overall_var)


# ============================================================
# 4. Effect estimation bias
# ============================================================

def _pooled_log_or(A: np.ndarray, Y: np.ndarray, strata: np.ndarray) -> float | None:
    """Inverse-variance weighted pooled log-OR across strata."""
    unique_strata = np.unique(strata)
    log_ors, variances = [], []
    for s in unique_strata:
        mask = strata == s
        if mask.sum() < 2:
            continue
        a_s, y_s = A[mask], Y[mask]
        if len(np.unique(a_s)) < 2 or len(np.unique(y_s)) < 2:
            continue
        log_or_s, se_s = _compute_log_or(a_s, y_s)
        if not np.isfinite(log_or_s):
            continue
        log_ors.append(log_or_s)
        variances.append(max(se_s ** 2, 1e-10))

    if len(log_ors) == 0:
        return None
    if len(log_ors) == 1:
        return float(log_ors[0])

    log_ors = np.array(log_ors)
    variances = np.array(variances)
    weights = 1.0 / variances
    pooled = np.sum(weights * log_ors) / np.sum(weights)
    return float(pooled)


def _risk_difference(A: np.ndarray, Y: np.ndarray, mask: np.ndarray | None = None) -> float:
    """Risk difference P(Y=1|A=1) - P(Y=1|A=0) for a subgroup."""
    if mask is not None:
        A = A[mask]
        Y = Y[mask]
    treated = A == 1
    control = A == 0
    if treated.sum() == 0 or control.sum() == 0:
        return 0.0
    return float(Y[treated].mean() - Y[control].mean())


def _pooled_risk_difference(A: np.ndarray, Y: np.ndarray, strata: np.ndarray) -> float | None:
    """Inverse-variance (sample-size) weighted average of stratum-specific risk differences."""
    unique_strata = np.unique(strata)
    effects, weights = [], []
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s < 2:
            continue
        a_s, y_s = A[mask], Y[mask]
        if len(np.unique(a_s)) < 2:
            continue
        rd_s = _risk_difference(a_s, y_s)
        effects.append(rd_s)
        weights.append(n_s)

    if len(effects) == 0:
        return None
    weights = np.array(weights, dtype=float)
    weights /= weights.sum()
    return float(np.sum(np.array(effects) * weights))


def _random_effects_risk_difference(A: np.ndarray, Y: np.ndarray, strata: np.ndarray) -> tuple[float, float, float] | None:
    """
    DerSimonian-Laird random-effects meta-analysis of stratum-specific risk differences.
    Returns (pooled RE risk difference, tau^2, I^2). Returns None if no stratum is estimable.
    """
    unique_strata = np.unique(strata)
    rd_list, var_list = [], []
    for s in unique_strata:
        mask = strata == s
        a_s, y_s = A[mask], Y[mask]
        treated = a_s == 1
        control = a_s == 0
        n1 = treated.sum()
        n0 = control.sum()
        if n1 == 0 or n0 == 0:
            continue
        # Haldane-Anscombe correction for variance
        y1 = y_s[treated].sum() + 0.5
        n1c = n1 + 1.0
        y0 = y_s[control].sum() + 0.5
        n0c = n0 + 1.0
        p1 = y1 / n1c
        p0 = y0 / n0c
        rd_s = p1 - p0
        var_s = p1 * (1 - p1) / n1c + p0 * (1 - p0) / n0c
        if np.isfinite(rd_s) and var_s > 0:
            rd_list.append(rd_s)
            var_list.append(var_s)

    k = len(rd_list)
    if k == 0:
        return None
    if k == 1:
        return float(rd_list[0]), 0.0, 0.0

    rd = np.array(rd_list)
    var = np.array(var_list)
    w = 1.0 / var
    pooled_fe = np.sum(w * rd) / np.sum(w)
    Q = np.sum(w * (rd - pooled_fe) ** 2)
    df = k - 1
    C = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - df) / C) if C > 0 else 0.0
    w_re = 1.0 / (var + tau2)
    pooled_re = np.sum(w_re * rd) / np.sum(w_re)
    I2 = max(0.0, (Q - df) / Q) if Q > 0 else 0.0
    return float(pooled_re), float(tau2), float(I2)


def compute_effect_estimation_bias(
    A: np.ndarray,
    Y: np.ndarray,
    strata: np.ndarray,
    true_ate_riskdiff: float,
    prefix: str = '',
) -> dict:
    """
    Compute crude, stratified and random-effects risk-difference estimates and their bias
    relative to the true ATE (population risk difference). Returns absolute and relative bias reduction.
    Optional `prefix` is prepended to all returned keys.
    """
    crude_effect = _risk_difference(A, Y)
    stratified_effect = _pooled_risk_difference(A, Y, strata)
    if stratified_effect is None:
        stratified_effect = crude_effect

    re_result = _random_effects_risk_difference(A, Y, strata)
    if re_result is None:
        re_effect, re_tau2, re_I2 = stratified_effect, 0.0, 0.0
    else:
        re_effect, re_tau2, re_I2 = re_result

    bias_crude = abs(crude_effect - true_ate_riskdiff)
    bias_stratified = abs(stratified_effect - true_ate_riskdiff)
    bias_re = abs(re_effect - true_ate_riskdiff)

    abs_reduction = bias_crude - bias_stratified
    rel_reduction = (1.0 - bias_stratified / bias_crude) if bias_crude > 1e-12 else 0.0
    abs_reduction_re = bias_crude - bias_re
    rel_reduction_re = (1.0 - bias_re / bias_crude) if bias_crude > 1e-12 else 0.0

    keys = {
        'crude_effect': float(crude_effect),
        'stratified_effect': float(stratified_effect),
        're_effect': float(re_effect),
        're_tau2': float(re_tau2),
        're_I2': float(re_I2),
        'true_ate': float(true_ate_riskdiff),
        'bias_crude': float(bias_crude),
        'bias_stratified': float(bias_stratified),
        'bias_re': float(bias_re),
        'bias_reduction': float(abs_reduction),
        'bias_reduction_relative': float(rel_reduction),
        'bias_reduction_re': float(abs_reduction_re),
        'bias_reduction_relative_re': float(rel_reduction_re),
    }
    if prefix:
        return {f'{prefix}{k}': v for k, v in keys.items()}
    return keys


# ============================================================
# 5. Combined evaluation
# ============================================================

def evaluate_stratification(
    X: np.ndarray,
    A: np.ndarray,
    Y: np.ndarray,
    Z: np.ndarray,
    Z_clusters: np.ndarray,
    strata: np.ndarray,
    true_cate: np.ndarray,
    true_ate_riskdiff: float,
    eval_idx: np.ndarray | None = None,
    study_id: np.ndarray | None = None,
    w_est_specs: list | None = None,
) -> dict:
    """Run all evaluation metrics on a single stratification result."""
    if w_est_specs is None:
        w_est_specs = ['interaction']
    arrays = [X, A, Y, Z, Z_clusters, strata, true_cate]
    if study_id is not None:
        arrays.append(study_id)
    arrays = _subset(*arrays, idx=eval_idx)
    if study_id is not None:
        X, A, Y, Z, Z_clusters, strata, true_cate, study_id = arrays
    else:
        X, A, Y, Z, Z_clusters, strata, true_cate = arrays

    results = {}
    results.update(compute_cluster_agreement(Z_clusters, strata))
    results.update(compute_eta_squared(Z, strata))
    results.update(compute_within_strata_entropy(Z, strata))
    results['C1_heterogeneity'] = compute_coherence_c1(A, Y, strata)
    results['W_true'] = compute_w_true(strata, true_cate)
    for spec in w_est_specs:
        key = 'W_est' if spec == 'interaction' else f'W_est_{spec}'
        results[key] = compute_w_est(A, X, Y, strata, model_spec=spec)
    results.update(compute_effect_estimation_bias(A, Y, strata, true_ate_riskdiff))
    if study_id is not None and len(np.unique(study_id)) > 1:
        results.update(compute_effect_estimation_bias(A, Y, study_id, true_ate_riskdiff, prefix='study_'))
    return results
