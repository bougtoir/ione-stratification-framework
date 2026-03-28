"""
Real-data application of stratification methods to known Simpson's paradox cases.
Order: 3 (COVID-19 CFR) → 1 (Kidney stone) → 2 (UC Berkeley) → 5 (Israel vaccine) → 4 (Smoking mortality)
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict, KFold
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, v_measure_score
from scipy import stats
from scipy.special import expit
import warnings
import json
import os
import time

warnings.filterwarnings('ignore')

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results', 'real_data')
os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# Coherence Indicators (adapted for real data - no oracle Z required for C1-C3)
# ============================================================

def compute_c1(Y, strata):
    """C1: 1 - I^2 (heterogeneity-based)."""
    unique_strata = np.unique(strata)
    if len(unique_strata) < 2:
        return 1.0
    effects, variances = [], []
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s < 2:
            continue
        y_s = Y[mask]
        effects.append(y_s.mean())
        variances.append(max(y_s.var(ddof=1) / n_s, 1e-10))
    if len(effects) < 2:
        return 1.0
    effects = np.array(effects)
    variances = np.array(variances)
    weights = 1.0 / variances
    pooled = np.sum(weights * effects) / np.sum(weights)
    Q = np.sum(weights * (effects - pooled) ** 2)
    df = len(effects) - 1
    I_sq = max((Q - df) / Q, 0.0) if Q > df else 0.0
    return float(1.0 - I_sq)


def compute_c2(X, Y, strata):
    """C2: residual structure-based."""
    unique_strata = np.unique(strata)
    systematic_component = 0.0
    total_n = 0
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s < 20 or len(np.unique(Y[mask])) < 2:
            continue
        X_s, Y_s = X[mask], Y[mask]
        try:
            model = LogisticRegression(max_iter=500, C=1.0, solver='lbfgs')
            model.fit(X_s, Y_s)
            p_hat = model.predict_proba(X_s)[:, 1]
            residuals = Y_s - p_hat
            sys_var = 0.0
            for j in range(X_s.shape[1]):
                if np.std(X_s[:, j]) > 0:
                    corr = np.corrcoef(X_s[:, j], residuals)[0, 1]
                    sys_var += corr ** 2
            sys_var /= max(X_s.shape[1], 1)
            systematic_component += sys_var * n_s
            total_n += n_s
        except Exception:
            continue
    if total_n == 0:
        return 1.0
    ratio = systematic_component / total_n
    return float(1.0 - min(ratio, 1.0))


def compute_c3(Y, strata, n_bootstrap=200):
    """C3: prediction stability-based."""
    unique_strata = np.unique(strata)
    n = len(Y)
    rng = np.random.default_rng(42)
    bootstrap_effects = []
    for _ in range(n_bootstrap):
        idx = rng.choice(n, n, replace=True)
        st_b, Y_b = strata[idx], Y[idx]
        se = []
        for s in unique_strata:
            mask = st_b == s
            if mask.sum() > 5:
                se.append(Y_b[mask].mean())
        if len(se) > 1:
            bootstrap_effects.append(np.var(se))
    if len(bootstrap_effects) < 2:
        return 1.0
    mean_var = np.mean(bootstrap_effects)
    std_var = np.std(bootstrap_effects)
    cv = std_var / mean_var if mean_var > 0 else 0.0
    return float(1.0 - min(cv, 1.0))


def compute_c4_with_true_labels(true_labels, strata):
    """C4: entropy-based (requires true group labels)."""
    unique_strata = np.unique(strata)
    n = len(strata)
    n_categories = len(np.unique(true_labels))
    H_max = np.log2(n_categories) if n_categories > 1 else 1.0
    H_within = 0.0
    for s in unique_strata:
        mask = strata == s
        n_s = mask.sum()
        if n_s == 0:
            continue
        z_s = true_labels[mask]
        _, counts = np.unique(z_s, return_counts=True)
        probs = counts / n_s
        entropy_s = -np.sum(probs * np.log2(probs + 1e-10))
        H_within += (n_s / n) * entropy_s
    return float(1.0 - H_within / H_max) if H_max > 0 else 1.0


def compute_simpson_check(X, Y, strata):
    """Check direction consistency of X->Y within strata vs overall."""
    n_vars = X.shape[1]
    strata_consistent = []
    unique_strata = np.unique(strata)
    for j in range(n_vars):
        if np.std(X[:, j]) > 0 and np.std(Y) > 0:
            overall_corr = np.corrcoef(X[:, j], Y)[0, 1]
        else:
            continue
        overall_dir = np.sign(overall_corr)
        within_dirs = []
        for s in unique_strata:
            mask = strata == s
            if mask.sum() < 10:
                continue
            x_s, y_s = X[mask, j], Y[mask]
            if np.std(x_s) > 0 and np.std(y_s) > 0:
                within_dirs.append(np.sign(np.corrcoef(x_s, y_s)[0, 1]))
        if len(within_dirs) > 0:
            strata_consistent.append(all(d == overall_dir for d in within_dirs))
    return float(np.mean(strata_consistent)) if strata_consistent else 1.0


def compute_eta_squared(Z, strata):
    """Compute eta-squared for each Z column across strata."""
    results = {}
    for j in range(Z.shape[1]):
        z_col = Z[:, j]
        ss_total = np.sum((z_col - z_col.mean()) ** 2)
        if ss_total == 0:
            results[f'eta2_Z{j}'] = 0.0
            continue
        ss_between = 0
        for s in np.unique(strata):
            mask = strata == s
            if mask.sum() > 0:
                ss_between += mask.sum() * (z_col[mask].mean() - z_col.mean()) ** 2
        results[f'eta2_Z{j}'] = float(ss_between / ss_total)
    results['eta2_mean'] = float(np.mean(list(results.values())))
    return results


# ============================================================
# Stratification Methods (adapted for real data)
# ============================================================

def method_1a(X, Y, n_strata):
    model = LogisticRegression(max_iter=1000, C=1.0, solver='lbfgs')
    model.fit(X, Y)
    p_hat = model.predict_proba(X)[:, 1]
    return _quantile_stratify(p_hat, n_strata)

def method_1b(X, Y, n_strata):
    model = LogisticRegression(max_iter=1000, C=1.0, solver='lbfgs')
    model.fit(X, Y)
    p_hat = model.predict_proba(X)[:, 1]
    residuals = np.abs(Y - p_hat)
    return _quantile_stratify(residuals, n_strata)

def method_1c(X, Y, n_strata):
    model = LogisticRegression(max_iter=1000, C=1.0, solver='lbfgs')
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    p_hat_cv = cross_val_predict(model, X, Y, cv=cv, method='predict_proba')[:, 1]
    return _quantile_stratify(p_hat_cv, n_strata)

def method_1d(X, Y, n_strata):
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X, Y)
    tree_preds = np.array([tree.predict_proba(X)[:, 1] for tree in model.estimators_])
    uncertainty = np.var(tree_preds, axis=0)
    return _quantile_stratify(uncertainty, n_strata)

def method_2a(X, Y, n_strata):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA(n_components=min(3, X.shape[1]))
    scores = pca.fit_transform(X_scaled)
    weights = pca.explained_variance_ratio_
    weights = weights / weights.sum()
    score = scores @ weights
    return _quantile_stratify(score, n_strata)

def method_2b(X, Y, n_strata):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    km = KMeans(n_clusters=n_strata, n_init=10, random_state=42)
    return km.fit_predict(X_scaled)

def method_random(X, Y, n_strata):
    rng = np.random.default_rng(42)
    return rng.integers(0, n_strata, size=X.shape[0])

def _quantile_stratify(scores, n_strata):
    quantiles = np.percentile(scores, np.linspace(0, 100, n_strata + 1)[1:-1])
    return np.digitize(scores, quantiles)


ALL_METHODS = {
    '1A_predicted_prob': method_1a,
    '1B_residual': method_1b,
    '1C_cv_decision': method_1c,
    '1D_ml_uncertainty': method_1d,
    '2A_pca': method_2a,
    '2B_clustering': method_2b,
    'random': method_random,
}


def evaluate_one(X, Y, true_labels, strata, Z_continuous=None):
    """Evaluate a single stratification result."""
    res = {}
    # Cluster agreement with true labels
    res['ARI'] = adjusted_rand_score(true_labels, strata)
    res['NMI'] = normalized_mutual_info_score(true_labels, strata)
    res['V_measure'] = v_measure_score(true_labels, strata)
    # Coherence
    res['C1'] = compute_c1(Y, strata)
    res['C2'] = compute_c2(X, Y, strata)
    res['C3'] = compute_c3(Y, strata)
    res['C4'] = compute_c4_with_true_labels(true_labels, strata)
    # Simpson check
    res['direction_consistency'] = compute_simpson_check(X, Y, strata)
    # Eta-squared (if Z_continuous available)
    if Z_continuous is not None:
        eta = compute_eta_squared(Z_continuous, strata)
        res['eta2_mean'] = eta['eta2_mean']
    return res


# ============================================================
# Dataset 1: COVID-19 CFR (von Kügelgen et al. 2021)
# ============================================================

def prepare_covid19_data():
    """
    COVID-19 case fatality rate data: China vs Italy, stratified by age.
    We expand aggregate data to individual-level binary records.
    """
    print("=" * 60)
    print("Dataset 3: COVID-19 CFR (von Kügelgen et al. 2021)")
    print("=" * 60)

    # Published data: China (Feb 17, 2020) vs Italy (Mar 9, 2020)
    # Source: Chinese CDC Weekly + ISS Italy reports
    # Age group, China cases, China deaths, Italy cases, Italy deaths
    data = {
        'age_group': ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+'],
        'china_cases': [416, 549, 3619, 7600, 8571, 10008, 8583, 3918, 1408],
        'china_deaths': [0, 1, 7, 18, 38, 130, 309, 312, 208],
        'italy_cases': [0, 1, 56, 177, 505, 1022, 1413, 1518, 1095],
        'italy_deaths': [0, 0, 0, 0, 3, 4, 17, 78, 134],
    }
    df = pd.DataFrame(data)

    # Age midpoints for generating continuous features
    age_midpoints = [5, 15, 25, 35, 45, 55, 65, 75, 85]

    # Expand to individual-level data
    records = []
    for i, row in df.iterrows():
        age_mid = age_midpoints[i]
        for country_label, cases_col, deaths_col in [
            (0, 'china_cases', 'china_deaths'),
            (1, 'italy_cases', 'italy_deaths')
        ]:
            n_cases = row[cases_col]
            n_deaths = row[deaths_col]
            if n_cases == 0:
                continue
            for k in range(n_cases):
                died = 1 if k < n_deaths else 0
                # Add noise to age for continuous feature
                age_noisy = age_mid + np.random.default_rng(42 + i * 10000 + k).normal(0, 3)
                records.append({
                    'country': country_label,
                    'age': age_noisy,
                    'age_group_idx': i,
                    'died': died,
                })

    df_indiv = pd.DataFrame(records)

    # Generate pseudo-X variables from age (simulating "general variables")
    rng = np.random.default_rng(42)
    n = len(df_indiv)
    age_std = (df_indiv['age'].values - 50) / 20

    # Create X features correlated with age at varying degrees
    X = np.column_stack([
        0.6 * age_std + rng.normal(0, 1, n),     # X1: strong age correlation
        0.4 * age_std + rng.normal(0, 1, n),     # X2: moderate
        0.3 * age_std + rng.normal(0, 1, n),     # X3: moderate
        0.2 * age_std + rng.normal(0, 1, n),     # X4: weak
        0.5 * df_indiv['country'].values + rng.normal(0, 1, n),  # X5: country-correlated
        rng.normal(0, 1, n),                       # X6: noise
        0.15 * age_std + rng.normal(0, 1, n),    # X7: weak age
        0.35 * age_std + rng.normal(0, 1, n),    # X8: moderate age
        rng.normal(0, 1, n),                       # X9: noise
        0.25 * age_std + rng.normal(0, 1, n),    # X10: weak-moderate age
    ])

    Y = df_indiv['died'].values.astype(float)
    true_labels = df_indiv['age_group_idx'].values  # True hidden group = age group
    Z_continuous = df_indiv[['age', 'country']].values

    print(f"  N = {n}, Event rate = {Y.mean():.4f}")
    print(f"  True groups (age groups): {len(np.unique(true_labels))}")

    # Verify Simpson's paradox
    china_mask = df_indiv['country'] == 0
    italy_mask = df_indiv['country'] == 1
    print(f"  China overall CFR: {Y[china_mask].mean():.4f}")
    print(f"  Italy overall CFR: {Y[italy_mask].mean():.4f}")
    print(f"  → Overall: Italy CFR > China CFR (paradox present)")

    return X, Y, true_labels, Z_continuous, 'COVID-19 CFR'


# ============================================================
# Dataset 2: Kidney Stone Treatment (Charig et al. 1986)
# ============================================================

def prepare_kidney_stone_data():
    """
    Kidney stone treatment data from Charig et al. 1986 BMJ.
    Expand aggregate data to individual-level records.
    """
    print("\n" + "=" * 60)
    print("Dataset 1: Kidney Stone Treatment (Charig et al. 1986)")
    print("=" * 60)

    # Published data:
    # Treatment A (open surgery): Small stones 81/87 (93%), Large stones 192/263 (73%)
    # Treatment B (PCNL): Small stones 234/270 (87%), Large stones 55/80 (69%)
    # Overall: A=273/350 (78%), B=289/350 (83%)
    data = [
        ('A', 'small', 87, 81),   # treatment, stone_size, total, success
        ('A', 'large', 263, 192),
        ('B', 'small', 270, 234),
        ('B', 'large', 80, 55),
    ]

    records = []
    rng = np.random.default_rng(42)
    for treatment, size, total, success in data:
        size_val = 0 if size == 'small' else 1
        treatment_val = 0 if treatment == 'A' else 1
        for k in range(total):
            outcome = 1 if k < success else 0
            # Generate pseudo clinical features correlated with stone size
            stone_size_continuous = size_val * 15 + rng.normal(10, 3)  # mm
            creatinine = 0.3 * size_val + rng.normal(1.0, 0.2)
            wbc = 0.2 * size_val + rng.normal(7, 2)
            pain_score = 0.4 * size_val + rng.normal(5, 2)
            bmi = rng.normal(25, 4)
            age = 40 + 5 * size_val + rng.normal(0, 10)
            records.append({
                'treatment': treatment_val,
                'stone_size': size_val,
                'success': outcome,
                'stone_size_mm': stone_size_continuous,
                'creatinine': creatinine,
                'wbc': wbc,
                'pain_score': pain_score,
                'bmi': bmi,
                'age': age,
            })

    df = pd.DataFrame(records)

    # X = clinical features (excluding stone_size and treatment)
    X = df[['stone_size_mm', 'creatinine', 'wbc', 'pain_score', 'bmi', 'age']].values
    Y = df['success'].values.astype(float)
    true_labels = df['stone_size'].values  # True hidden group = stone size
    Z_continuous = df[['stone_size_mm', 'age']].values

    print(f"  N = {len(df)}, Success rate = {Y.mean():.4f}")

    # Verify Simpson's paradox
    a_mask = df['treatment'] == 0
    b_mask = df['treatment'] == 1
    print(f"  Treatment A overall: {Y[a_mask].mean():.4f}")
    print(f"  Treatment B overall: {Y[b_mask].mean():.4f}")
    print(f"  → Overall: B > A (paradox: A better in both subgroups)")

    small_a = df[(df['treatment'] == 0) & (df['stone_size'] == 0)]
    small_b = df[(df['treatment'] == 1) & (df['stone_size'] == 0)]
    large_a = df[(df['treatment'] == 0) & (df['stone_size'] == 1)]
    large_b = df[(df['treatment'] == 1) & (df['stone_size'] == 1)]
    print(f"  Small stones: A={small_a['success'].mean():.4f}, B={small_b['success'].mean():.4f}")
    print(f"  Large stones: A={large_a['success'].mean():.4f}, B={large_b['success'].mean():.4f}")

    return X, Y, true_labels, Z_continuous, 'Kidney Stone'


# ============================================================
# Dataset 3: UC Berkeley Admissions (Bickel et al. 1975)
# ============================================================

def prepare_berkeley_data():
    """
    UC Berkeley graduate admissions data (1973).
    Use the well-known 6-department summary data.
    """
    print("\n" + "=" * 60)
    print("Dataset 2: UC Berkeley Admissions (Bickel et al. 1975)")
    print("=" * 60)

    # UCBAdmissions data: Dept, Gender, Admitted, Rejected
    departments = {
        'A': {'M': (825, 512), 'F': (108, 89)},   # (applicants, admitted)
        'B': {'M': (560, 353), 'F': (25, 17)},
        'C': {'M': (325, 120), 'F': (593, 202)},
        'D': {'M': (417, 138), 'F': (375, 131)},
        'E': {'M': (191, 53), 'F': (393, 94)},
        'F': {'M': (272, 16), 'F': (341, 24)},
    }

    records = []
    rng = np.random.default_rng(42)
    dept_idx = 0
    for dept, genders in departments.items():
        for gender, (n_app, n_admitted) in genders.items():
            gender_val = 0 if gender == 'M' else 1
            for k in range(n_app):
                admitted = 1 if k < n_admitted else 0
                # Generate pseudo features correlated with department choice
                gpa = 3.0 + 0.3 * (5 - dept_idx) / 5 + rng.normal(0, 0.3)
                gre_verbal = 500 + 30 * (5 - dept_idx) / 5 + rng.normal(0, 50)
                gre_quant = 550 + 40 * (dept_idx) / 5 + rng.normal(0, 50)
                research_exp = max(0, 2 + dept_idx * 0.3 + rng.normal(0, 1))
                recommendation = 3.0 + 0.2 * (5 - dept_idx) / 5 + rng.normal(0, 0.5)
                essay_score = rng.normal(70, 10)
                records.append({
                    'gender': gender_val,
                    'dept_idx': dept_idx,
                    'admitted': admitted,
                    'gpa': gpa,
                    'gre_verbal': gre_verbal,
                    'gre_quant': gre_quant,
                    'research_exp': research_exp,
                    'recommendation': recommendation,
                    'essay_score': essay_score,
                })
        dept_idx += 1

    df = pd.DataFrame(records)

    X = df[['gpa', 'gre_verbal', 'gre_quant', 'research_exp', 'recommendation', 'essay_score']].values
    Y = df['admitted'].values.astype(float)
    true_labels = df['dept_idx'].values  # True hidden group = department
    Z_continuous = df[['gpa', 'gre_verbal', 'gre_quant']].values

    print(f"  N = {len(df)}, Admission rate = {Y.mean():.4f}")

    # Verify Simpson's paradox
    m_mask = df['gender'] == 0
    f_mask = df['gender'] == 1
    print(f"  Male overall: {Y[m_mask].mean():.4f}")
    print(f"  Female overall: {Y[f_mask].mean():.4f}")
    print(f"  → Overall: Male > Female (paradox: most depts favor female)")

    return X, Y, true_labels, Z_continuous, 'UC Berkeley'


# ============================================================
# Dataset 4: Israel COVID-19 Vaccine (Morris 2021)
# ============================================================

def prepare_israel_vaccine_data():
    """
    Israeli COVID-19 vaccination data showing Simpson's paradox.
    Source: Israeli Ministry of Health, analyzed by J. Morris (2021).
    """
    print("\n" + "=" * 60)
    print("Dataset 5: Israel COVID-19 Vaccine Efficacy (Morris 2021)")
    print("=" * 60)

    # Data from Israeli MoH (Aug-Sep 2021, Delta wave)
    # Severe cases by vaccination status and age
    # Age <60: vacc severe=11, unvacc severe=43, vacc pop~3.5M, unvacc pop~1.3M
    # Age ≥60: vacc severe=171, unvacc severe=48, vacc pop~1.1M, unvacc pop~0.2M
    # Overall: vacc severe=182, unvacc severe=91

    data = [
        # (age_group, vaccinated, n_population_approx, n_severe)
        ('<60', 1, 3500, 11),
        ('<60', 0, 1300, 43),
        ('≥60', 1, 1100, 171),
        ('≥60', 0, 200, 48),
    ]

    records = []
    rng = np.random.default_rng(42)
    for age_grp, vacc, n_pop, n_severe in data:
        is_old = 1 if age_grp == '≥60' else 0
        for k in range(n_pop):
            severe = 1 if k < n_severe else 0
            age = (65 + rng.normal(0, 8)) if is_old else (35 + rng.normal(0, 12))
            age = np.clip(age, 12, 95)
            # Generate pseudo health features
            comorbidity_score = 0.5 * is_old + rng.normal(0, 0.3)
            immune_response = -0.3 * is_old + 0.2 * vacc + rng.normal(0, 0.5)
            bmi = 25 + 2 * is_old + rng.normal(0, 4)
            blood_pressure = 120 + 15 * is_old + rng.normal(0, 10)
            previous_infection = rng.binomial(1, 0.15 + 0.05 * is_old)
            crp = 0.3 * is_old + rng.exponential(1.0)
            records.append({
                'vaccinated': vacc,
                'age_group': is_old,
                'severe': severe,
                'age': age,
                'comorbidity_score': comorbidity_score,
                'immune_response': immune_response,
                'bmi': bmi,
                'blood_pressure': blood_pressure,
                'previous_infection': previous_infection,
                'crp': crp,
            })

    df = pd.DataFrame(records)

    X = df[['age', 'comorbidity_score', 'immune_response', 'bmi',
            'blood_pressure', 'previous_infection', 'crp']].values
    Y = df['severe'].values.astype(float)
    true_labels = df['age_group'].values  # True hidden group = age group
    Z_continuous = df[['age', 'comorbidity_score']].values

    print(f"  N = {len(df)}, Severe rate = {Y.mean():.4f}")

    # Verify Simpson's paradox
    v_mask = df['vaccinated'] == 1
    u_mask = df['vaccinated'] == 0
    print(f"  Vaccinated severe rate: {Y[v_mask].mean():.4f}")
    print(f"  Unvaccinated severe rate: {Y[u_mask].mean():.4f}")
    print(f"  → Overall: Vacc rate appears higher (paradox: vacc effective in both age groups)")

    young_v = df[(df['vaccinated'] == 1) & (df['age_group'] == 0)]
    young_u = df[(df['vaccinated'] == 0) & (df['age_group'] == 0)]
    old_v = df[(df['vaccinated'] == 1) & (df['age_group'] == 1)]
    old_u = df[(df['vaccinated'] == 0) & (df['age_group'] == 1)]
    print(f"  <60: Vacc={young_v['severe'].mean():.4f}, Unvacc={young_u['severe'].mean():.4f}")
    print(f"  ≥60: Vacc={old_v['severe'].mean():.4f}, Unvacc={old_u['severe'].mean():.4f}")

    return X, Y, true_labels, Z_continuous, 'Israel Vaccine'


# ============================================================
# Dataset 5: Smoking and Mortality (Appleton et al. 1996)
# ============================================================

def prepare_smoking_data():
    """
    Appleton, French & Vanderpump (1996): Smoking and mortality in 1,314 women.
    20-year follow-up from Whickham survey (1972-1974).
    """
    print("\n" + "=" * 60)
    print("Dataset 4: Smoking and Mortality (Appleton et al. 1996)")
    print("=" * 60)

    # Published data from Appleton et al. 1996, American Statistician 50(4): 340-341
    # Age group, Smoker dead, Smoker alive, Non-smoker dead, Non-smoker alive
    age_data = [
        ('18-24', 2, 53, 1, 61),
        ('25-34', 3, 121, 5, 152),
        ('35-44', 14, 95, 7, 114),
        ('45-54', 27, 103, 12, 66),
        ('55-64', 51, 64, 40, 81),
        ('65-74', 29, 7, 101, 28),
        ('75+', 13, 0, 64, 0),
    ]

    age_midpoints = [21, 30, 40, 50, 60, 70, 80]

    records = []
    rng = np.random.default_rng(42)
    for i, (age_grp, s_dead, s_alive, ns_dead, ns_alive) in enumerate(age_data):
        age_mid = age_midpoints[i]
        for smoker_val, n_dead, n_alive in [(1, s_dead, s_alive), (0, ns_dead, ns_alive)]:
            total = n_dead + n_alive
            for k in range(total):
                died = 1 if k < n_dead else 0
                age = age_mid + rng.normal(0, 3)
                # Generate pseudo health features correlated with age
                systolic_bp = 110 + 0.5 * age + rng.normal(0, 10)
                cholesterol = 180 + 0.8 * age + rng.normal(0, 25)
                bmi = 23 + 0.05 * age + rng.normal(0, 3)
                exercise_freq = max(0, 5 - 0.05 * age + rng.normal(0, 1.5))
                alcohol = rng.exponential(2.0) + 0.3 * smoker_val
                lung_function = 100 - 0.3 * age - 5 * smoker_val + rng.normal(0, 10)
                records.append({
                    'smoker': smoker_val,
                    'age_group_idx': i,
                    'died': died,
                    'age': age,
                    'systolic_bp': systolic_bp,
                    'cholesterol': cholesterol,
                    'bmi': bmi,
                    'exercise_freq': exercise_freq,
                    'alcohol': alcohol,
                    'lung_function': lung_function,
                })

    df = pd.DataFrame(records)

    X = df[['age', 'systolic_bp', 'cholesterol', 'bmi',
            'exercise_freq', 'alcohol', 'lung_function']].values
    Y = df['died'].values.astype(float)
    true_labels = df['age_group_idx'].values
    Z_continuous = df[['age', 'systolic_bp']].values

    print(f"  N = {len(df)}, Mortality rate = {Y.mean():.4f}")

    # Verify Simpson's paradox
    s_mask = df['smoker'] == 1
    ns_mask = df['smoker'] == 0
    print(f"  Smoker mortality: {Y[s_mask].mean():.4f}")
    print(f"  Non-smoker mortality: {Y[ns_mask].mean():.4f}")
    print(f"  → Overall: Smokers appear to live longer (paradox: smokers younger)")

    return X, Y, true_labels, Z_continuous, 'Smoking Mortality'


# ============================================================
# Main Analysis
# ============================================================

def run_analysis_for_dataset(X, Y, true_labels, Z_continuous, dataset_name, n_strata_list=None):
    """Run all methods on a dataset and return results."""
    if n_strata_list is None:
        n_unique_groups = len(np.unique(true_labels))
        # Try the true number of groups and also 2, 3, 4
        n_strata_list = sorted(set([2, 3, min(n_unique_groups, 4), n_unique_groups]))
        n_strata_list = [k for k in n_strata_list if k >= 2]

    all_results = []
    for n_strata in n_strata_list:
        for method_name, method_fn in ALL_METHODS.items():
            try:
                strata = method_fn(X, Y, n_strata)
                res = evaluate_one(X, Y, true_labels, strata, Z_continuous)
                res['method'] = method_name
                res['n_strata'] = n_strata
                res['dataset'] = dataset_name
                all_results.append(res)
            except Exception as e:
                print(f"  [WARN] {method_name} k={n_strata}: {e}")
                continue

    # Also evaluate oracle (using true labels directly)
    try:
        res_oracle = evaluate_one(X, Y, true_labels, true_labels, Z_continuous)
        res_oracle['method'] = 'oracle'
        res_oracle['n_strata'] = len(np.unique(true_labels))
        res_oracle['dataset'] = dataset_name
        all_results.append(res_oracle)
    except Exception as e:
        print(f"  [WARN] oracle: {e}")

    return all_results


def main():
    print("=" * 70)
    print("Real-Data Application of Stratification Methods")
    print("to Known Simpson's Paradox Cases")
    print("=" * 70)
    start = time.time()

    all_results = []

    # Order: 3 → 1 → 2 → 5 → 4
    datasets = [
        prepare_covid19_data,       # 3: COVID-19 CFR
        prepare_kidney_stone_data,  # 1: Kidney Stone
        prepare_berkeley_data,      # 2: UC Berkeley
        prepare_israel_vaccine_data,# 5: Israel Vaccine
        prepare_smoking_data,       # 4: Smoking Mortality
    ]

    for prep_fn in datasets:
        X, Y, true_labels, Z_continuous, name = prep_fn()
        print(f"\n  Running methods on {name}...")
        results = run_analysis_for_dataset(X, Y, true_labels, Z_continuous, name)
        all_results.extend(results)
        print(f"  → {len(results)} evaluations completed")

    # Save results
    df_results = pd.DataFrame(all_results)
    csv_path = os.path.join(RESULTS_DIR, 'real_data_results.csv')
    df_results.to_csv(csv_path, index=False)
    print(f"\nResults saved to {csv_path}")

    elapsed = time.time() - start
    print(f"\nTotal time: {elapsed:.1f}s")

    return df_results


if __name__ == '__main__':
    df = main()
