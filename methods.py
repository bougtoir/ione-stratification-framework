"""
Stratification methods module.
Method 1: Decision power-based (4 variants)
Method 2: Feature score-based (4 variants)
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_predict, KFold
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import MDS
import warnings

warnings.filterwarnings('ignore')


# ============================================================
# Method 1: Decision Power-based Stratification (Primary)
# ============================================================

def method_1a_predicted_probability(X: np.ndarray, Y: np.ndarray, n_strata: int) -> np.ndarray:
    """
    Method 1A: Predicted probability-based stratification.
    Stratify by predicted P(Y=1|X) quantiles.
    """
    model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
    model.fit(X, Y)
    p_hat = model.predict_proba(X)[:, 1]
    return _quantile_stratify(p_hat, n_strata)


def method_1b_residual(X: np.ndarray, Y: np.ndarray, n_strata: int) -> np.ndarray:
    """
    Method 1B: Prediction residual-based stratification.
    Stratify by |Y - p_hat| magnitude.
    """
    model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
    model.fit(X, Y)
    p_hat = model.predict_proba(X)[:, 1]
    residuals = np.abs(Y - p_hat)
    return _quantile_stratify(residuals, n_strata)


def method_1c_cv_decision(X: np.ndarray, Y: np.ndarray, n_strata: int) -> np.ndarray:
    """
    Method 1C: Cross-validation-based decision power score.
    Uses out-of-fold predictions to avoid overfitting (pilot design).
    """
    model = LogisticRegression(max_iter=1000, penalty='l2', C=1.0, solver='lbfgs')
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    p_hat_cv = cross_val_predict(model, X, Y, cv=cv, method='predict_proba')[:, 1]
    return _quantile_stratify(p_hat_cv, n_strata)


def method_1d_ml_uncertainty(X: np.ndarray, Y: np.ndarray, n_strata: int) -> np.ndarray:
    """
    Method 1D: ML model uncertainty-based stratification.
    Uses RF tree variance as uncertainty measure.
    """
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X, Y)
    # Get individual tree predictions
    tree_preds = np.array([tree.predict_proba(X)[:, 1] for tree in model.estimators_])
    # Uncertainty = variance across trees
    uncertainty = np.var(tree_preds, axis=0)
    return _quantile_stratify(uncertainty, n_strata)


# ============================================================
# Method 2: Feature Score-based Stratification (Complementary)
# ============================================================

def method_2a_pca(X: np.ndarray, Y: np.ndarray, n_strata: int,
                  cumulative_threshold: float | None = None,
                  fixed_k: int | None = None) -> np.ndarray:
    """
    Method 2A: PCA-based stratification.
    Uses PC scores for stratification (Y is ignored).

    Parameters
    ----------
    cumulative_threshold : float or None
        Cumulative variance explained threshold (0.4, 0.6, 0.8).
    fixed_k : int or None
        Fixed number of components (1, 2, 3).
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
        k = 1  # default: PC1 only

    if k == 1:
        score = scores[:, 0]
    else:
        # Weighted composite: weight by explained variance ratio
        weights = pca.explained_variance_ratio_[:k]
        weights = weights / weights.sum()
        score = scores[:, :k] @ weights

    return _quantile_stratify(score, n_strata)


def method_2b_clustering(X: np.ndarray, Y: np.ndarray, n_strata: int) -> np.ndarray:
    """
    Method 2B: Clustering-based stratification (Y is ignored).
    Uses k-means on standardized X.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    km = KMeans(n_clusters=n_strata, n_init=10, random_state=42)
    return km.fit_predict(X_scaled)


def method_2c_autoencoder(X: np.ndarray, Y: np.ndarray, n_strata: int,
                          latent_dim: int = 3) -> np.ndarray:
    """
    Method 2C: Autoencoder latent representation-based stratification (Y is ignored).
    Uses a simple autoencoder with PyTorch.
    """
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

    # Cluster in latent space
    km = KMeans(n_clusters=n_strata, n_init=10, random_state=42)
    return km.fit_predict(latent_np)


def method_2d_rf_proximity(X: np.ndarray, Y: np.ndarray, n_strata: int) -> np.ndarray:
    """
    Method 2D: Random Forest proximity-based stratification (Y is ignored).
    Uses unsupervised RF with synthetic data approach.
    """
    n = X.shape[0]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Generate synthetic data by independently permuting each column
    rng = np.random.default_rng(42)
    X_synthetic = np.column_stack([rng.permutation(X_scaled[:, j]) for j in range(X_scaled.shape[1])])

    # Combine real and synthetic
    X_combined = np.vstack([X_scaled, X_synthetic])
    Y_combined = np.concatenate([np.ones(n), np.zeros(n)])

    # Train RF to distinguish real from synthetic
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_combined, Y_combined)

    # Compute proximity via leaf co-occurrence (vectorized)
    leaves = rf.apply(X_scaled)  # (n, n_trees)
    n_trees = leaves.shape[1]

    # Vectorized: use one-hot encoding per tree and dot product
    # For memory efficiency, process in batches and accumulate PCA
    # Instead of full n×n proximity, use leaf embeddings directly
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

    leaf_matrix = hstack(sparse_parts)  # (n, total_unique_leaves)

    # PCA on sparse leaf embedding for dimensionality reduction
    from sklearn.decomposition import TruncatedSVD
    svd = TruncatedSVD(n_components=min(5, leaf_matrix.shape[1] - 1), random_state=42)
    coords = svd.fit_transform(leaf_matrix)

    km = KMeans(n_clusters=n_strata, n_init=10, random_state=42)
    return km.fit_predict(coords)


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


def _random_stratify(X: np.ndarray, Y: np.ndarray, Z: np.ndarray, n_strata: int,
                     seed: int = 42) -> np.ndarray:
    """Random stratification (lower bound baseline)."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_strata, size=X.shape[0])


def _oracle_kmeans_stratify(X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                            n_strata: int, seed: int = 42) -> np.ndarray:
    """Oracle: stratify using true Z (upper bound baseline)."""
    scaler = StandardScaler()
    Z_scaled = scaler.fit_transform(Z)
    km = KMeans(n_clusters=n_strata, n_init=10, random_state=seed)
    return km.fit_predict(Z_scaled)


def _oracle_quantile_stratify(X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                              n_strata: int, seed: int = 42) -> np.ndarray:
    """Oracle: stratify using Z1 (age) quantiles."""
    quantiles = np.percentile(Z[:, 0], np.linspace(0, 100, n_strata + 1)[1:-1])
    return np.digitize(Z[:, 0], quantiles)
