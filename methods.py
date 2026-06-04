"""
Stratification methods module.
Revised: adds active comparators (LCA, PS quintile, GMM),
sample splitting for outcome-informed methods, and treatment variable support.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict, KFold
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
import warnings

warnings.filterwarnings('ignore')


# ============================================================
# Method 1: Decision Power-based Stratification (outcome-informed)
# Now with sample splitting: train on first half, assign strata to second half
# ============================================================

def method_1a_predicted_probability(X: np.ndarray, Y: np.ndarray, n_strata: int,
                                    A: np.ndarray | None = None,
                                    split: bool = True) -> np.ndarray:
    """
    Method 1A: Predicted probability-based stratification.
    If split=True, trains on first half, assigns strata to all observations.
    """
    n = len(Y)
    if split:
        half = n // 2
        model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
        model.fit(X[:half], Y[:half])
        p_hat = model.predict_proba(X)[:, 1]
    else:
        model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
        model.fit(X, Y)
        p_hat = model.predict_proba(X)[:, 1]
    return _quantile_stratify(p_hat, n_strata)


def method_1b_residual(X: np.ndarray, Y: np.ndarray, n_strata: int,
                       A: np.ndarray | None = None,
                       split: bool = True) -> np.ndarray:
    """
    Method 1B: Prediction residual-based stratification.
    """
    n = len(Y)
    if split:
        half = n // 2
        model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
        model.fit(X[:half], Y[:half])
        p_hat = model.predict_proba(X)[:, 1]
    else:
        model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
        model.fit(X, Y)
        p_hat = model.predict_proba(X)[:, 1]
    residuals = np.abs(Y - p_hat)
    return _quantile_stratify(residuals, n_strata)


def method_1c_cv_decision(X: np.ndarray, Y: np.ndarray, n_strata: int,
                          A: np.ndarray | None = None,
                          split: bool = True) -> np.ndarray:
    """
    Method 1C: Cross-validation-based decision power score.
    Uses out-of-fold predictions (inherently avoids overfitting).
    """
    model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    p_hat_cv = cross_val_predict(model, X, Y, cv=cv, method='predict_proba')[:, 1]
    return _quantile_stratify(p_hat_cv, n_strata)


def method_1d_ml_uncertainty(X: np.ndarray, Y: np.ndarray, n_strata: int,
                             A: np.ndarray | None = None,
                             split: bool = True) -> np.ndarray:
    """
    Method 1D: ML model uncertainty-based stratification.
    """
    n = len(Y)
    if split:
        half = n // 2
        model = RandomForestClassifier(n_estimators=100, max_depth=10,
                                       random_state=42, n_jobs=-1)
        model.fit(X[:half], Y[:half])
    else:
        model = RandomForestClassifier(n_estimators=100, max_depth=10,
                                       random_state=42, n_jobs=-1)
        model.fit(X, Y)
    tree_preds = np.array([tree.predict_proba(X)[:, 1] for tree in model.estimators_])
    uncertainty = np.var(tree_preds, axis=0)
    return _quantile_stratify(uncertainty, n_strata)


# ============================================================
# Method 2: Feature Score-based Stratification (outcome-free)
# ============================================================

def method_2a_pca(X: np.ndarray, Y: np.ndarray, n_strata: int,
                  A: np.ndarray | None = None,
                  cumulative_threshold: float | None = None,
                  fixed_k: int | None = None) -> np.ndarray:
    """
    Method 2A: PCA-based stratification (Y is ignored).
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA()
    scores = pca.fit_transform(X_scaled)

    if fixed_k is not None:
        k = min(fixed_k, X.shape[1])
    elif cumulative_threshold is not None:
        cumvar = np.cumsum(pca.explained_variance_ratio_)
        k = int(np.searchsorted(cumvar, cumulative_threshold) + 1)
        k = min(k, X.shape[1])
    else:
        k = 1

    if k == 1:
        score = scores[:, 0]
    else:
        weights = pca.explained_variance_ratio_[:k]
        weights = weights / weights.sum()
        score = scores[:, :k] @ weights

    return _quantile_stratify(score, n_strata)


def method_2b_clustering(X: np.ndarray, Y: np.ndarray, n_strata: int,
                         A: np.ndarray | None = None) -> np.ndarray:
    """
    Method 2B: k-means clustering on standardized X (Y is ignored).
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    km = KMeans(n_clusters=n_strata, n_init=10, random_state=42)
    return km.fit_predict(X_scaled)


# ============================================================
# Active Comparators (new for revision)
# ============================================================

def comparator_ps_quintile(X: np.ndarray, Y: np.ndarray, n_strata: int,
                           A: np.ndarray | None = None) -> np.ndarray:
    """
    Comparator: Propensity score quintile stratification.
    Stratifies by estimated P(A=1|X).
    Requires treatment variable A.
    """
    if A is None:
        raise ValueError("PS quintile requires treatment variable A")
    model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
    model.fit(X, A)
    ps = model.predict_proba(X)[:, 1]
    return _quantile_stratify(ps, n_strata)


def comparator_gmm(X: np.ndarray, Y: np.ndarray, n_strata: int,
                   A: np.ndarray | None = None) -> np.ndarray:
    """
    Comparator: Gaussian Mixture Model (finite mixture model).
    Approximation of latent class analysis for continuous covariates.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    gmm = GaussianMixture(n_components=n_strata, covariance_type='full',
                          n_init=5, random_state=42)
    return gmm.fit_predict(X_scaled)


def comparator_kmeans_x(X: np.ndarray, Y: np.ndarray, n_strata: int,
                        A: np.ndarray | None = None) -> np.ndarray:
    """
    Comparator: Simple k-means on X (naive clustering baseline).
    Identical to method_2b but listed as a comparator for clarity.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    km = KMeans(n_clusters=n_strata, n_init=10, random_state=42)
    return km.fit_predict(X_scaled)


def comparator_prognostic_score(X: np.ndarray, Y: np.ndarray, n_strata: int,
                                A: np.ndarray | None = None) -> np.ndarray:
    """
    Comparator: Prognostic score stratification.
    Stratifies by P(Y=1|X, A=0) estimated from untreated subjects only.
    Requires treatment variable A.
    """
    if A is None:
        raise ValueError("Prognostic score requires treatment variable A")
    untreated = A == 0
    if untreated.sum() < 30:
        return _quantile_stratify(np.zeros(len(Y)), n_strata)
    model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
    model.fit(X[untreated], Y[untreated])
    prog_score = model.predict_proba(X)[:, 1]
    return _quantile_stratify(prog_score, n_strata)


# ============================================================
# Helper functions
# ============================================================

def _quantile_stratify(scores: np.ndarray, n_strata: int) -> np.ndarray:
    """Stratify by quantile-based equal-size groups."""
    quantiles = np.percentile(scores, np.linspace(0, 100, n_strata + 1)[1:-1])
    return np.digitize(scores, quantiles)


# ============================================================
# Method registry
# ============================================================

def get_all_methods() -> dict:
    """Return dictionary of all proposed IONE method functions."""
    return {
        '1A_predicted_prob': method_1a_predicted_probability,
        '1B_residual': method_1b_residual,
        '1C_cv_decision': method_1c_cv_decision,
        '1D_ml_uncertainty': method_1d_ml_uncertainty,
        '2A_pca': method_2a_pca,
        '2B_clustering': method_2b_clustering,
    }


def get_comparator_methods() -> dict:
    """Return dictionary of active comparator methods."""
    return {
        'comp_PS_quintile': comparator_ps_quintile,
        'comp_GMM': comparator_gmm,
        'comp_kmeans_X': comparator_kmeans_x,
        'comp_prognostic': comparator_prognostic_score,
    }


def get_pca_variants() -> list[dict]:
    """Return PCA variant configurations."""
    return [
        {'cumulative_threshold': 0.4, 'fixed_k': None, 'label': 'PCA_cum40'},
        {'cumulative_threshold': 0.6, 'fixed_k': None, 'label': 'PCA_cum60'},
        {'cumulative_threshold': 0.8, 'fixed_k': None, 'label': 'PCA_cum80'},
        {'cumulative_threshold': None, 'fixed_k': 1, 'label': 'PCA_k1'},
        {'cumulative_threshold': None, 'fixed_k': 2, 'label': 'PCA_k2'},
        {'cumulative_threshold': None, 'fixed_k': 3, 'label': 'PCA_k3'},
    ]


def get_baseline_methods() -> dict:
    """Return baseline stratification methods for comparison."""
    return {
        'random': _random_stratify,
        'oracle_kmeans': _oracle_kmeans_stratify,
        'oracle_quantile': _oracle_quantile_stratify,
    }


def _random_stratify(X: np.ndarray, Y: np.ndarray, Z: np.ndarray, n_strata: int,
                     A: np.ndarray | None = None, seed: int = 42) -> np.ndarray:
    """Random stratification (lower bound baseline)."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_strata, size=X.shape[0])


def _oracle_kmeans_stratify(X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                            n_strata: int, A: np.ndarray | None = None,
                            seed: int = 42) -> np.ndarray:
    """Oracle: stratify using true Z (upper bound baseline)."""
    scaler = StandardScaler()
    Z_scaled = scaler.fit_transform(Z)
    km = KMeans(n_clusters=n_strata, n_init=10, random_state=seed)
    return km.fit_predict(Z_scaled)


def _oracle_quantile_stratify(X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                              n_strata: int, A: np.ndarray | None = None,
                              seed: int = 42) -> np.ndarray:
    """Oracle: stratify using Z1 (age) quantiles."""
    quantiles = np.percentile(Z[:, 0], np.linspace(0, 100, n_strata + 1)[1:-1])
    return np.digitize(Z[:, 0], quantiles)
