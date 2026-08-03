"""
Real-data application of IONE stratification to known Simpson's-paradox datasets.
Datasets are expanded to pseudo-individual records; methods and metrics are drawn
from the same modules used in the simulation study to keep the analysis reproducible.
"""

import numpy as np
import pandas as pd
import os
import time
import warnings

import methods
import evaluation as ev

warnings.filterwarnings('ignore')

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results', 'real_data')
os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# Dataset preparation
# ============================================================

def prepare_covid19_data():
    """COVID-19 CFR: China vs Italy, stratified by age."""
    print("\n" + "=" * 60)
    print("Dataset: COVID-19 CFR (China vs Italy)")
    print("=" * 60)

    data = {
        'age_group': ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+'],
        'china_cases': [416, 549, 3619, 7600, 8571, 10008, 8583, 3918, 1408],
        'china_deaths': [0, 1, 7, 18, 38, 130, 309, 312, 208],
        'italy_cases': [0, 1, 56, 177, 505, 1022, 1413, 1518, 1095],
        'italy_deaths': [0, 0, 0, 0, 3, 4, 17, 78, 134],
    }
    df = pd.DataFrame(data)
    age_midpoints = [5, 15, 25, 35, 45, 55, 65, 75, 85]

    records = []
    for i, row in df.iterrows():
        age_mid = age_midpoints[i]
        for country, cases_col, deaths_col in [(0, 'china_cases', 'china_deaths'),
                                                (1, 'italy_cases', 'italy_deaths')]:
            n_cases = row[cases_col]
            n_deaths = row[deaths_col]
            if n_cases == 0:
                continue
            for k in range(n_cases):
                died = 1 if k < n_deaths else 0
                age_noisy = age_mid + np.random.default_rng(42 + i * 10000 + k).normal(0, 3)
                records.append({
                    'A': float(country),
                    'age': age_noisy,
                    'age_group_idx': i,
                    'Y': float(died),
                })

    df_indiv = pd.DataFrame(records)
    rng = np.random.default_rng(42)
    n = len(df_indiv)
    age_std = (df_indiv['age'].values - 50) / 20

    X = np.column_stack([
        0.6 * age_std + rng.normal(0, 1, n),
        0.4 * age_std + rng.normal(0, 1, n),
        0.3 * age_std + rng.normal(0, 1, n),
        0.2 * age_std + rng.normal(0, 1, n),
        rng.normal(0, 1, n),
        0.15 * age_std + rng.normal(0, 1, n),
        0.35 * age_std + rng.normal(0, 1, n),
        rng.normal(0, 1, n),
        0.25 * age_std + rng.normal(0, 1, n),
        rng.normal(0, 1, n),
    ])

    A = df_indiv['A'].values.astype(float)
    Y = df_indiv['Y'].values.astype(float)
    true_labels = df_indiv['age_group_idx'].values.astype(int)
    Z = df_indiv[['age']].values

    print(f"  N = {n}, Event rate = {Y.mean():.4f}")
    _print_paradox(A, Y, 'China', 'Italy')
    return X, A, Y, true_labels, Z, 'COVID-19 CFR'


def prepare_kidney_stone_data():
    """Kidney stone treatment: open surgery vs PCNL, confounded by stone size."""
    print("\n" + "=" * 60)
    print("Dataset: Kidney Stone Treatment (Charig et al. 1986)")
    print("=" * 60)

    data = [
        ('A', 'small', 87, 81),
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
            stone_size_mm = size_val * 15 + rng.normal(10, 3)
            records.append({
                'A': float(treatment_val),
                'stone_size': size_val,
                'Y': float(outcome),
                'stone_size_mm': stone_size_mm,
                'creatinine': 0.3 * size_val + rng.normal(1.0, 0.2),
                'wbc': 0.2 * size_val + rng.normal(7, 2),
                'pain_score': 0.4 * size_val + rng.normal(5, 2),
                'bmi': rng.normal(25, 4),
                'age': 40 + 5 * size_val + rng.normal(0, 10),
            })

    df = pd.DataFrame(records)
    X = df[['stone_size_mm', 'creatinine', 'wbc', 'pain_score', 'bmi', 'age']].values
    A = df['A'].values.astype(float)
    Y = df['Y'].values.astype(float)
    true_labels = df['stone_size'].values.astype(int)
    Z = df[['stone_size_mm']].values

    print(f"  N = {len(df)}, Success rate = {Y.mean():.4f}")
    _print_paradox(A, Y, 'Treatment A', 'Treatment B')
    return X, A, Y, true_labels, Z, 'Kidney Stone'


def prepare_berkeley_data():
    """UC Berkeley admissions: gender and department."""
    print("\n" + "=" * 60)
    print("Dataset: UC Berkeley Admissions (Bickel et al. 1975)")
    print("=" * 60)

    departments = {
        'A': {'M': (825, 512), 'F': (108, 89)},
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
                records.append({
                    'A': float(gender_val),
                    'dept_idx': dept_idx,
                    'Y': float(admitted),
                    'gpa': 3.0 + 0.3 * (5 - dept_idx) / 5 + rng.normal(0, 0.3),
                    'gre_verbal': 500 + 30 * (5 - dept_idx) / 5 + rng.normal(0, 50),
                    'gre_quant': 550 + 40 * dept_idx / 5 + rng.normal(0, 50),
                    'research_exp': max(0, 2 + dept_idx * 0.3 + rng.normal(0, 1)),
                    'recommendation': 3.0 + 0.2 * (5 - dept_idx) / 5 + rng.normal(0, 0.5),
                    'essay_score': rng.normal(70, 10),
                })
        dept_idx += 1

    df = pd.DataFrame(records)
    X = df[['gpa', 'gre_verbal', 'gre_quant', 'research_exp', 'recommendation', 'essay_score']].values
    A = df['A'].values.astype(float)
    Y = df['Y'].values.astype(float)
    true_labels = df['dept_idx'].values.astype(int)
    Z = df[['gpa', 'gre_verbal', 'gre_quant']].values

    print(f"  N = {len(df)}, Admission rate = {Y.mean():.4f}")
    _print_paradox(A, Y, 'Male', 'Female')
    return X, A, Y, true_labels, Z, 'UC Berkeley'


def prepare_israel_vaccine_data():
    """Israel COVID-19 vaccine efficacy by age."""
    print("\n" + "=" * 60)
    print("Dataset: Israel COVID-19 Vaccine Efficacy (Morris 2021)")
    print("=" * 60)

    data = [
        ('<60', 1, 3500, 11),
        ('<60', 0, 1300, 43),
        ('>=60', 1, 1100, 171),
        ('>=60', 0, 200, 48),
    ]

    records = []
    rng = np.random.default_rng(42)
    for age_grp, vacc, n_pop, n_severe in data:
        is_old = 1 if age_grp == '>=60' else 0
        for k in range(n_pop):
            severe = 1 if k < n_severe else 0
            age = (65 + rng.normal(0, 8)) if is_old else (35 + rng.normal(0, 12))
            age = np.clip(age, 12, 95)
            records.append({
                'A': float(vacc),
                'age_group': is_old,
                'Y': float(severe),
                'age': age,
                'comorbidity_score': 0.5 * is_old + rng.normal(0, 0.3),
                'immune_response': -0.3 * is_old + 0.2 * vacc + rng.normal(0, 0.5),
                'bmi': 25 + 2 * is_old + rng.normal(0, 4),
                'blood_pressure': 120 + 15 * is_old + rng.normal(0, 10),
                'previous_infection': rng.binomial(1, 0.15 + 0.05 * is_old),
                'crp': 0.3 * is_old + rng.exponential(1.0),
            })

    df = pd.DataFrame(records)
    X = df[['age', 'comorbidity_score', 'immune_response', 'bmi',
            'blood_pressure', 'previous_infection', 'crp']].values
    A = df['A'].values.astype(float)
    Y = df['Y'].values.astype(float)
    true_labels = df['age_group'].values.astype(int)
    Z = df[['age', 'comorbidity_score']].values

    print(f"  N = {len(df)}, Severe rate = {Y.mean():.4f}")
    _print_paradox(A, Y, 'Vaccinated', 'Unvaccinated')
    return X, A, Y, true_labels, Z, 'Israel Vaccine'


def prepare_smoking_data():
    """Smoking and mortality: Simpson's paradox by age."""
    print("\n" + "=" * 60)
    print("Dataset: Smoking and Mortality (Appleton et al. 1996)")
    print("=" * 60)

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
        for smoker, n_dead, n_alive in [(1, s_dead, s_alive), (0, ns_dead, ns_alive)]:
            total = n_dead + n_alive
            for k in range(total):
                died = 1 if k < n_dead else 0
                age = age_mid + rng.normal(0, 3)
                records.append({
                    'A': float(smoker),
                    'age_group_idx': i,
                    'Y': float(died),
                    'age': age,
                    'systolic_bp': 110 + 0.5 * age + rng.normal(0, 10),
                    'cholesterol': 180 + 0.8 * age + rng.normal(0, 25),
                    'bmi': 23 + 0.05 * age + rng.normal(0, 3),
                    'exercise_freq': max(0, 5 - 0.05 * age + rng.normal(0, 1.5)),
                    'alcohol': rng.exponential(2.0) + 0.3 * smoker,
                    'lung_function': 100 - 0.3 * age - 5 * smoker + rng.normal(0, 10),
                })

    df = pd.DataFrame(records)
    X = df[['age', 'systolic_bp', 'cholesterol', 'bmi',
            'exercise_freq', 'alcohol', 'lung_function']].values
    A = df['A'].values.astype(float)
    Y = df['Y'].values.astype(float)
    true_labels = df['age_group_idx'].values.astype(int)
    Z = df[['age']].values

    print(f"  N = {len(df)}, Mortality rate = {Y.mean():.4f}")
    _print_paradox(A, Y, 'Smoker', 'Non-smoker')
    return X, A, Y, true_labels, Z, 'Smoking Mortality'


def _print_paradox(A, Y, label0, label1):
    rate0 = Y[A == 0].mean()
    rate1 = Y[A == 1].mean()
    print(f"  {label0} overall: {rate0:.4f}")
    print(f"  {label1} overall: {rate1:.4f}")
    direction = '>' if rate1 > rate0 else '<'
    print(f"  → Crude: {label1} {direction} {label0}")


# ============================================================
# Unified real-data analysis
# ============================================================

def _true_ate_from_labels(A, Y, labels):
    """Reference treatment effect: pooled risk difference by the known confounder groups."""
    ate = ev._pooled_risk_difference(A, Y, labels)
    return float(ate) if ate is not None else 0.0


def _make_method_specs():
    """List of (name, function, kwargs) mirroring the simulation study."""
    proposed = [
        ('1A_predicted_prob', methods.method_1a_predicted_probability, {}),
        ('1B_residual', methods.method_1b_residual, {}),
        ('1C_cv_decision', methods.method_1c_cv_decision, {}),
        ('1D_ml_uncertainty', methods.method_1d_ml_uncertainty, {}),
        ('2A_PCA_cum60', methods.method_2a_pca, {'cumulative_threshold': 0.6, 'fixed_k': None}),
        ('2B_clustering', methods.method_2b_clustering, {}),
    ]
    active = [
        ('PS_propensity_score', methods.method_ps_propensity_score, {}),
        ('GMM', methods.method_gmm, {}),
        ('Prognostic_score', methods.method_prognostic_score, {}),
    ]
    baselines = [
        ('baseline_random', 'random', {}),
        ('baseline_oracle_kmeans', 'oracle_kmeans', {}),
        ('baseline_oracle_quantile', 'oracle_quantile', {}),
    ]
    return proposed + active + baselines


def run_analysis_for_dataset(X, A, Y, true_labels, Z, dataset_name):
    """Apply all methods and active comparators to one real dataset."""
    n_unique = len(np.unique(true_labels))
    n_strata_list = sorted(set([2, 3, min(n_unique, 4), n_unique]))
    n_strata_list = [k for k in n_strata_list if k >= 2]

    true_ate = _true_ate_from_labels(A, Y, true_labels)
    # Dummy true_cate: real data do not provide individual-level CATEs.
    true_cate = np.zeros(len(Y))

    baseline_funcs = methods.get_baseline_methods()
    all_results = []

    for n_strata in n_strata_list:
        for method_name, method_fn_or_key, kwargs in _make_method_specs():
            try:
                if method_name.startswith('baseline_'):
                    bname = method_name.replace('baseline_', '')
                    strata = baseline_funcs[bname](X, A, Y, Z, n_strata, seed=42)
                else:
                    strata = method_fn_or_key(X, A, Y, n_strata, **kwargs)

                metrics = ev.evaluate_stratification(
                    X, A, Y, Z, true_labels, strata,
                    true_cate=true_cate,
                    true_ate_riskdiff=true_ate,
                )
                # W_true is not meaningful without true individual CATEs
                metrics['W_true'] = float(np.nan)
                result = {
                    'dataset': dataset_name,
                    'method': method_name,
                    'n_strata': n_strata,
                    'true_ate_riskdiff': true_ate,
                    'error': None,
                }
                result.update(metrics)
                all_results.append(result)
            except Exception as e:
                print(f"  [WARN] {method_name} k={n_strata}: {e}")

    return all_results


def main():
    print("=" * 70)
    print("Real-Data Application of IONE Stratification")
    print("=" * 70)
    start = time.time()

    datasets = [
        prepare_covid19_data,
        prepare_kidney_stone_data,
        prepare_berkeley_data,
        prepare_israel_vaccine_data,
        prepare_smoking_data,
    ]

    all_results = []
    for prep_fn in datasets:
        X, A, Y, true_labels, Z, name = prep_fn()
        print(f"\n  Running methods on {name}...")
        results = run_analysis_for_dataset(X, A, Y, true_labels, Z, name)
        all_results.extend(results)
        print(f"  -> {len(results)} evaluations completed")

    df = pd.DataFrame(all_results)
    csv_path = os.path.join(RESULTS_DIR, 'real_data_results.csv')
    df.to_csv(csv_path, index=False)
    print(f"\nResults saved to {csv_path}")
    print(f"Total time: {time.time() - start:.1f}s")
    return df


if __name__ == '__main__':
    df = main()
