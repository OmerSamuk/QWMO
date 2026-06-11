import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon
from statsmodels.stats.multitest import multipletests


def friedman_test(results_dict, function_id):
    func_key = f'F{function_id}'
    if func_key not in results_dict:
        return None
    
    func_results = results_dict[func_key]
    algorithms = list(func_results.keys())
    
    fitness_arrays = []
    for algo in algorithms:
        if func_results[algo]['fitnesses']:
            fitness_arrays.append(func_results[algo]['fitnesses'])
    
    if len(fitness_arrays) < 3:
        return None
    
    min_len = min(len(arr) for arr in fitness_arrays)
    fitness_arrays = [arr[:min_len] for arr in fitness_arrays]
    
    stat, p_value = friedmanchisquare(*fitness_arrays)
    
    return {
        'statistic': stat,
        'p_value': p_value,
        'algorithms': algorithms,
        'n_runs': min_len
    }


def holm_posthoc(results_dict, function_id, control_algorithm='QWMO_Full'):
    func_key = f'F{function_id}'
    if func_key not in results_dict:
        return None
    
    func_results = results_dict[func_key]
    algorithms = list(func_results.keys())
    
    if control_algorithm not in algorithms:
        return None
    
    control_fitness = func_results[control_algorithm]['fitnesses']
    
    p_values = []
    comparisons = []
    
    for algo in algorithms:
        if algo == control_algorithm:
            continue
        
        algo_fitness = func_results[algo]['fitnesses']
        
        min_len = min(len(control_fitness), len(algo_fitness))
        if min_len < 5:
            continue
        
        try:
            stat, p_val = wilcoxon(control_fitness[:min_len], algo_fitness[:min_len])
            p_values.append(p_val)
            comparisons.append(f'{control_algorithm} vs {algo}')
        except:
            continue
    
    if not p_values:
        return None
    
    reject, p_adjusted, _, _ = multipletests(p_values, method='holm')
    
    results = []
    for i, comp in enumerate(comparisons):
        results.append({
            'comparison': comp,
            'p_value': p_values[i],
            'p_adjusted': p_adjusted[i],
            'reject_null': reject[i]
        })
    
    return pd.DataFrame(results)


def vargha_delaney_a12(x, y):
    m = len(x)
    n = len(y)
    
    r1 = 0
    for xi in x:
        for yj in y:
            if xi > yj:
                r1 += 1
            elif xi == yj:
                r1 += 0.5
    
    a12 = r1 / (m * n)
    return a12


def compute_effect_sizes(results_dict, function_id, control_algorithm='QWMO_Full'):
    func_key = f'F{function_id}'
    if func_key not in results_dict:
        return None
    
    func_results = results_dict[func_key]
    algorithms = list(func_results.keys())
    
    if control_algorithm not in algorithms:
        return None
    
    control_fitness = func_results[control_algorithm]['fitnesses']
    
    results = []
    for algo in algorithms:
        if algo == control_algorithm:
            continue
        
        algo_fitness = func_results[algo]['fitnesses']
        
        min_len = min(len(control_fitness), len(algo_fitness))
        if min_len < 5:
            continue
        
        a12 = vargha_delaney_a12(control_fitness[:min_len], algo_fitness[:min_len])
        
        if a12 > 0.5:
            interpretation = 'large' if a12 > 0.71 else 'medium' if a12 > 0.64 else 'small'
        elif a12 < 0.5:
            interpretation = 'large' if a12 < 0.29 else 'medium' if a12 < 0.36 else 'small'
        else:
            interpretation = 'negligible'
        
        results.append({
            'algorithm': algo,
            'A12': a12,
            'interpretation': interpretation
        })
    
    return pd.DataFrame(results)


def full_statistical_analysis(results_dict, function_ids, control_algorithm='QWMO_Full'):
    all_results = {}
    
    for func_id in function_ids:
        print(f"\n{'='*60}")
        print(f"Statistical Analysis for F{func_id}")
        print(f"{'='*60}")
        
        friedman_result = friedman_test(results_dict, func_id)
        if friedman_result:
            print(f"\nFriedman Test:")
            print(f"  Statistic: {friedman_result['statistic']:.4f}")
            print(f"  p-value: {friedman_result['p_value']:.4e}")
            print(f"  Significant: {'Yes' if friedman_result['p_value'] < 0.05 else 'No'}")
        
        holm_result = holm_posthoc(results_dict, func_id, control_algorithm)
        if holm_result is not None and len(holm_result) > 0:
            print(f"\nHolm Post-hoc Test (control: {control_algorithm}):")
            print(holm_result.to_string(index=False))
        
        effect_result = compute_effect_sizes(results_dict, func_id, control_algorithm)
        if effect_result is not None and len(effect_result) > 0:
            print(f"\nEffect Sizes (Vargha-Delaney A12):")
            print(effect_result.to_string(index=False))
        
        all_results[f'F{func_id}'] = {
            'friedman': friedman_result,
            'holm': holm_result,
            'effect_sizes': effect_result
        }
    
    return all_results
