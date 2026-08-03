"""
Stratification methods module.

Method families:
- Proposed IONE methods:
  1A: predicted probability (outcome-informed)
  1B: residual (outcome-informed)
  1C: cross-validated decision power (outcome-informed, out-of-fold)
  1D: ML uncertainty (outcome-informed)
  2A: PCA (outcome-free)
  2B: k-means on X (outcome-free)
  2C: autoencoder (outcome-free)
  2D: RF proximity (outcome-free)
- Active comparators:
  PS: propensity-score quintiles
  GMM: Gaussian mixture model on X
  Prog: prognostic-score quintiles
- Baselines:
  random, oracle_kmeans, oracle_quantile

All methods have a unified signature: func(X, A, Y, n_strata, **kwargs).
Methods that do not need A or Y ignore them by convention.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_predict, KFold
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import MDS
from sklearn.mixture import GaussianMixture
import warnings

warnings.filterwarnings('ignore')


def _quantile_stratify(scores: np.ndarray, n_strata: int, discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Stratify by quantile-based equal-size groups.
    If discovery_idx is provided, thresholds are computed on the discovery subset and applied to the full score vector."""
    if n_strata <= 1:
        return np.zeros(len(scores), dtype=int)
    if discovery_idx is None:
        ref_scores = scores
    else:
        ref_scores = scores[np.asarray(discovery_idx)]
    quantiles = np.percentile(ref_scores, np.linspace(0, 100, n_strata + 1)[1:-1])
    return np.digitize(scores, quantiles)


# ============================================================
# Proposed IONE methods (Family 1: outcome-informed)
# ============================================================

def method_1a_predicted_probability(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
                                    discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Method 1A: predicted probability-based stratification."""
    train = np.asarray(discovery_idx) if discovery_idx is not None else np.arange(len(X))
    model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
    model.fit(X[train], Y[train])
    p_hat = model.predict_proba(X)[:, 1]
    return _quantile_stratify(p_hat, n_strata, discovery_idx)


def method_1b_residual(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
                        discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Method 1B: prediction residual-based stratification."""
    train = np.asarray(discovery_idx) if discovery_idx is not None else np.arange(len(X))
    model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
    model.fit(X[train], Y[train])
    p_hat = model.predict_proba(X)[:, 1]
    residuals = np.abs(Y - p_hat)
    return _quantile_stratify(residuals, n_strata, discovery_idx)


def method_1c_cv_decision(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
                           discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Method 1C: cross-validation-based decision power score."""
    train = np.asarray(discovery_idx) if discovery_idx is not None else np.arange(len(X))
    model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    p_hat_cv = cross_val_predict(model, X[train], Y[train], cv=cv, method='predict_proba')[:, 1]
    # Predict on full data: use full X for CV scores is not possible; instead fit a model on train and predict full.
    model.fit(X[train], Y[train])
    p_hat_full = model.predict_proba(X)[:, 1]
    return _quantile_stratify(p_hat_full, n_strata, discovery_idx)


def method_1d_ml_uncertainty(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
                              discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Method 1D: ML model uncertainty-based stratification."""
    train = np.asarray(discovery_idx) if discovery_idx is not None else np.arange(len(X))
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X[train], Y[train])
    tree_preds = np.array([tree.predict_proba(X)[:, 1] for tree in model.estimators_])
    uncertainty = np.var(tree_preds, axis=0)
    return _quantile_stratify(uncertainty, n_strata, discovery_idx)


# ============================================================
# Proposed IONE methods (Family 2: outcome-free)
# ============================================================

def method_2a_pca(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
                  cumulative_threshold: float | None = None,
                  fixed_k: int | None = None,
                  discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Method 2A: PCA-based stratification."""
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

    return _quantile_stratify(score, n_strata, discovery_idx)


def method_2b_clustering(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
                         discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Method 2B: clustering-based stratification."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    km = KMeans(n_clusters=n_strata, n_init=10, random_state=42)
    return km.fit_predict(X_scaled)


def method_2c_autoencoder(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
                          latent_dim: int = 3,
                          discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Method 2C: autoencoder latent representation-based stratification."""
    import torch
    import torch.nn as nn

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_tensor = torch.FloatTensor(X_scaled)

    input_dim = X.shape[1]

    class AutoEncoder(nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, 16),
                nn.ReLU(),
                nn.Linear(16, latent_dim),
            )
            self.decoder = nn.Sequential(
                nn.Linear(latent_dim, 16),
                nn.ReLU(),
                nn.Linear(16, input_dim),
            )

        def forward(self, x):
            z = self.encoder(x)
            return self.decoder(z), z

    model = AutoEncoder()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
    criterion = nn.MSELoss()

    model.train()
    for _ in range(200):
        optimizer.zero_grad()
        recon, _ = model(X_tensor)
        loss = criterion(recon, X_tensor)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        _, latent = model(X_tensor)
        latent_np = latent.numpy()

    km = KMeans(n_clusters=n_strata, n_init=10, random_state=42)
    return km.fit_predict(latent_np)


def method_2d_rf_proximity(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
                          discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Method 2D: random forest proximity-based stratification."""
    n = X.shape[0]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    rng = np.random.default_rng(42)
    X_synthetic = np.column_stack([rng.permutation(X_scaled[:, j]) for j in range(X_scaled.shape[1])])

    X_combined = np.vstack([X_scaled, X_synthetic])
    Y_combined = np.concatenate([np.ones(n), np.zeros(n)])

    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_combined, Y_combined)

    leaves = rf.apply(X_scaled)
    n_trees = leaves.shape[1]

    from scipy.sparse import csr_matrix, hstack

    sparse_parts = []
    for t in range(n_trees):
        leaf_ids = leaves[:, t]
        unique_leaves = np.unique(leaf_ids)
        leaf_map = {v: i for i, v in enumerate(unique_leaves)}
        rows = np.arange(n)
        cols = np.array([leaf_map[lid] for lid in leaf_ids])
        data = np.ones(n) / np.sqrt(n_trees)
        sparse_parts.append(csr_matrix((data, (rows, cols)),
                                       shape=(n, len(unique_leaves))))

    leaf_matrix = hstack(sparse_parts)

    from sklearn.decomposition import TruncatedSVD
    svd = TruncatedSVD(n_components=min(5, leaf_matrix.shape[1] - 1), random_state=42)
    coords = svd.fit_transform(leaf_matrix)

    km = KMeans(n_clusters=n_strata, n_init=10, random_state=42)
    return km.fit_predict(coords)


# ============================================================
# Active comparators
# ============================================================

def method_ps_propensity_score(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
                                discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Propensity-score stratification: logistic P(A=1|X) quantiles."""
    if len(np.unique(A)) < 2:
        return np.zeros(X.shape[0], dtype=int)
    train = np.asarray(discovery_idx) if discovery_idx is not None else np.arange(len(X))
    model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
    model.fit(X[train], A[train])
    ps = model.predict_proba(X)[:, 1]
    return _quantile_stratify(ps, n_strata, discovery_idx)


def method_gmm(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
               discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Gaussian mixture model on standardized X."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    gmm = GaussianMixture(n_components=n_strata, n_init=10, random_state=42)
    return gmm.fit_predict(X_scaled)


def method_prognostic_score(X: np.ndarray, A: np.ndarray, Y: np.ndarray, n_strata: int,
                             discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Prognostic-score stratification: predicted P(Y=1|X) among untreated, applied to all."""
    train = np.asarray(discovery_idx) if discovery_idx is not None else np.arange(len(X))
    A_train, Y_train = A[train], Y[train]
    mask_untreated = A_train == 0
    if mask_untreated.sum() < 10 or len(np.unique(Y_train[mask_untreated])) < 2:
        model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
        model.fit(X[train], Y_train)
    else:
        model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
        model.fit(X[train][mask_untreated], Y_train[mask_untreated])
    prog = model.predict_proba(X)[:, 1]
    return _quantile_stratify(prog, n_strata, discovery_idx)


# ============================================================
# Helper functions
# ============================================================

def _random_stratify(X: np.ndarray, A: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                     n_strata: int, seed: int = 42,
                     discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Random stratification (lower bound baseline)."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_strata, size=X.shape[0])


def _oracle_kmeans_stratify(X: np.ndarray, A: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                            n_strata: int, seed: int = 42,
                            discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Oracle: stratify using true Z."""
    scaler = StandardScaler()
    Z_scaled = scaler.fit_transform(Z)
    km = KMeans(n_clusters=n_strata, n_init=10, random_state=seed)
    return km.fit_predict(Z_scaled)


def _oracle_quantile_stratify(X: np.ndarray, A: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                              n_strata: int, seed: int = 42,
                              discovery_idx: np.ndarray | None = None) -> np.ndarray:
    """Oracle: stratify using Z1 (age) quantiles."""
    quantiles = np.percentile(Z[:, 0], np.linspace(0, 100, n_strata + 1)[1:-1])
    return np.digitize(Z[:, 0], quantiles)


# ============================================================
# Registries
# ============================================================

def get_all_methods() -> dict:
    """Return dictionary of all method functions."""
    return {
        '1A_predicted_prob': method_1a_predicted_probability,
        '1B_residual': method_1b_residual,
        '1C_cv_decision': method_1c_cv_decision,
        '1D_ml_uncertainty': method_1d_ml_uncertainty,
        '2A_pca': method_2a_pca,
        '2B_clustering': method_2b_clustering,
        '2C_autoencoder': method_2c_autoencoder,
        '2D_rf_proximity': method_2d_rf_proximity,
        'PS_propensity_score': method_ps_propensity_score,
        'GMM': method_gmm,
        'Prognostic_score': method_prognostic_score,
    }


def get_pca_variants() -> list[dict]:
    """Return PCA variant configurations for cumulative contribution scenarios."""
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
