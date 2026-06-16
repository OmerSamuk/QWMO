import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon
from statsmodels.stats.multitest import multipletests


def vargha_delaney_a12(x, y):
    """Vargha-Delaney A12 effect size for minimization.

    Returns P(X < Y): the probability that a random sample from x is *better*
    (smaller) than a random sample from y. So A12 > 0.5 means x is the better
    distribution for minimization. The returned key in the result dict is
    A12_first_better to make this explicit.
    """
    m = len(x)
    n = len(y)

    r1 = 0
    for xi in x:
        for yj in y:
            if xi < yj:
                r1 += 1
            elif xi == yj:
                r1 += 0.5

    a12 = r1 / (m * n)
    return a12


def _interpret_a12(a12):
    if a12 > 0.5:
        return 'large' if a12 > 0.71 else 'medium' if a12 > 0.64 else 'small'
    if a12 < 0.5:
        return 'large' if a12 < 0.29 else 'medium' if a12 < 0.36 else 'small'
    return 'negligible'


def friedman_test_per_function(results_dict, function_id):
    """Per-function Friedman test (algorithms compared within one function,
    blocks = independent runs). Provided for completeness; primary analysis
    should use friedman_test_across_functions.
    """
    func_key = f'F{function_id}'
    if func_key not in results_dict:
        return None

    func_results = results_dict[func_key]
    algorithms = list(func_results.keys())

    fitness_arrays = []
    valid_algos = []
    for algo in algorithms:
        if func_results[algo]['fitnesses']:
            fitness_arrays.append(func_results[algo]['fitnesses'])
            valid_algos.append(algo)

    if len(fitness_arrays) < 3:
        return None

    min_len = min(len(arr) for arr in fitness_arrays)
    fitness_arrays = [arr[:min_len] for arr in fitness_arrays]

    stat, p_value = friedmanchisquare(*fitness_arrays)

    return {
        'statistic': stat,
        'p_value': p_value,
        'algorithms': valid_algos,
        'n_runs': min_len
    }


def friedman_test_across_functions(results_dict, function_ids, control_algorithm='QWMO_Full_Dynamic'):
    """Dimension-level Friedman test: blocks = functions, treatments =
    algorithms. Mean fitness per (algorithm, function) is the cell value;
    algorithms are ranked within each function. Holm post-hoc compares
    every other algorithm to the control.
    """
    function_ids = sorted(function_ids)
    func_keys = [f'F{fid}' for fid in function_ids]
    for fk in func_keys:
        if fk not in results_dict:
            return None

    sample_func = results_dict[func_keys[0]]
    algorithms = list(sample_func.keys())
    if control_algorithm not in algorithms:
        return None

    rank_matrix = []
    valid_algorithms = []
    mean_matrix = []
    for algo in algorithms:
        means = []
        for fk in func_keys:
            algo_results = results_dict[fk].get(algo)
            if not algo_results or not algo_results.get('fitnesses'):
                means = None
                break
            means.append(float(np.mean(algo_results['fitnesses'])))
        if means is None or len(means) != len(func_keys):
            continue
        valid_algorithms.append(algo)
        mean_matrix.append(means)

    if len(valid_algorithms) < 3:
        return None

    mean_matrix = np.array(mean_matrix)
    ranks = np.zeros_like(mean_matrix)
    for j in range(mean_matrix.shape[1]):
        order = np.argsort(mean_matrix[:, j], kind='mergesort')
        r = np.empty_like(order, dtype=float)
        r[order] = np.arange(1, len(order) + 1)
        ranks[:, j] = r

    stat, p_value = friedmanchisquare(*ranks)

    mean_ranks = ranks.mean(axis=1)

    holm_rows = []
    p_values = []
    comparisons = []
    control_idx = valid_algorithms.index(control_algorithm)
    for i, algo in enumerate(valid_algorithms):
        if i == control_idx:
            continue
        try:
            stat_w, p_val = wilcoxon(ranks[control_idx], ranks[i])
        except ValueError:
            p_val = 1.0
        p_values.append(p_val)
        comparisons.append(f'{control_algorithm} vs {algo}')

    if p_values:
        reject, p_adjusted, _, _ = multipletests(p_values, method='holm')
        for comp, p, p_adj, rej in zip(comparisons, p_values, p_adjusted, reject):
            holm_rows.append({
                'comparison': comp,
                'p_value': p,
                'p_adjusted': p_adj,
                'reject_null': rej,
            })

    return {
        'statistic': stat,
        'p_value': p_value,
        'algorithms': valid_algorithms,
        'mean_ranks': dict(zip(valid_algorithms, mean_ranks.tolist())),
        'n_blocks': len(func_keys),
        'holm': pd.DataFrame(holm_rows) if holm_rows else None,
    }


def wilcoxon_per_function(results_dict, function_id, control_algorithm='QWMO_Full_Dynamic'):
    func_key = f'F{function_id}'
    if func_key not in results_dict:
        return None
    func_results = results_dict[func_key]
    if control_algorithm not in func_results:
        return None

    control_fitness = func_results[control_algorithm]['fitnesses']
    rows = []
    p_values = []
    comparisons = []
    for algo, data in func_results.items():
        if algo == control_algorithm:
            continue
        algo_fitness = data.get('fitnesses', [])
        min_len = min(len(control_fitness), len(algo_fitness))
        if min_len < 5:
            continue
        try:
            stat, p_val = wilcoxon(control_fitness[:min_len], algo_fitness[:min_len])
        except ValueError:
            p_val = 1.0
        p_values.append(p_val)
        comparisons.append(f'{control_algorithm} vs {algo}')

    if p_values:
        reject, p_adjusted, _, _ = multipletests(p_values, method='holm')
        for comp, p, p_adj, rej in zip(comparisons, p_values, p_adjusted, reject):
            rows.append({
                'comparison': comp,
                'p_value': p,
                'p_adjusted': p_adj,
                'reject_null': rej,
            })
    return pd.DataFrame(rows) if rows else None


def a12_per_function(results_dict, function_id, control_algorithm='QWMO_Full_Dynamic'):
    """A12 reported as A12_control_better. For minimization, A12_control_better
    = P(control < competitor). Values > 0.5 mean control is better.
    """
    func_key = f'F{function_id}'
    if func_key not in results_dict:
        return None
    func_results = results_dict[func_key]
    if control_algorithm not in func_results:
        return None

    control_fitness = func_results[control_algorithm]['fitnesses']
    rows = []
    for algo, data in func_results.items():
        if algo == control_algorithm:
            continue
        algo_fitness = data.get('fitnesses', [])
        min_len = min(len(control_fitness), len(algo_fitness))
        if min_len < 5:
            continue
        a12 = vargha_delaney_a12(control_fitness[:min_len], algo_fitness[:min_len])
        rows.append({
            'algorithm': algo,
            'A12_control_better': a12,
            'A12_QWMO_better': a12,
            'interpretation': _interpret_a12(a12),
        })
    return pd.DataFrame(rows) if rows else None


def compute_effect_sizes(results_dict, function_id, control_algorithm='QWMO_Full_Dynamic'):
    return a12_per_function(results_dict, function_id, control_algorithm)


def holm_posthoc(results_dict, function_id, control_algorithm='QWMO_Full_Dynamic'):
    return wilcoxon_per_function(results_dict, function_id, control_algorithm)


def full_statistical_analysis(results_dict, function_ids, control_algorithm='QWMO_Full_Dynamic'):
    all_results = {}
    for func_id in function_ids:
        print(f"\n{'='*60}")
        print(f"Statistical Analysis for F{func_id}")
        print(f"{'='*60}")

        friedman_per = friedman_test_per_function(results_dict, func_id)
        if friedman_per:
            print(f"\nFriedman Test (per-function, blocks=runs):")
            print(f"  Statistic: {friedman_per['statistic']:.4f}")
            print(f"  p-value: {friedman_per['p_value']:.4e}")
            print(f"  Significant: {'Yes' if friedman_per['p_value'] < 0.05 else 'No'}")

        holm_per = wilcoxon_per_function(results_dict, func_id, control_algorithm)
        if holm_per is not None and len(holm_per) > 0:
            print(f"\nWilcoxon + Holm (per-function, control: {control_algorithm}):")
            print(holm_per.to_string(index=False))

        effect_per = a12_per_function(results_dict, func_id, control_algorithm)
        if effect_per is not None and len(effect_per) > 0:
            print(f"\nEffect Sizes (Vargha-Delaney A12, control: {control_algorithm}):")
            print(effect_per.to_string(index=False))

        all_results[f'F{func_id}'] = {
            'friedman_per_function': friedman_per,
            'wilcoxon_holm_per_function': holm_per,
            'effect_sizes_per_function': effect_per,
        }

    print(f"\n{'='*60}")
    print(f"Global Friedman Test across functions (blocks=functions)")
    print(f"{'='*60}")
    global_friedman = friedman_test_across_functions(results_dict, function_ids, control_algorithm)
    if global_friedman:
        print(f"\nFriedman Statistic: {global_friedman['statistic']:.4f}")
        print(f"p-value: {global_friedman['p_value']:.4e}")
        print(f"Significant: {'Yes' if global_friedman['p_value'] < 0.05 else 'No'}")
        print(f"\nMean Ranks (lower = better for minimization):")
        for algo, rank in sorted(global_friedman['mean_ranks'].items(), key=lambda kv: kv[1]):
            print(f"  {algo:30s} {rank:.3f}")
        if global_friedman['holm'] is not None and len(global_friedman['holm']) > 0:
            print(f"\nHolm Post-hoc (control: {control_algorithm}):")
            print(global_friedman['holm'].to_string(index=False))
        all_results['_global'] = global_friedman

    return all_results
