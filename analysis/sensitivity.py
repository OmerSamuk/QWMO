import numpy as np
import matplotlib.pyplot as plt
from core.qwmo import QWMO
from benchmark.cec2017 import CEC2017Benchmark
from experiments.config import SENSITIVITY_PARAMS, QWMO_PARAMS


def sensitivity_analysis_single_param(param_name, param_values, function_id=10, 
                                     dimension=30, max_fes=1_000_000, num_runs=10):
    benchmark = CEC2017Benchmark(function_id, dimension)
    
    results = []
    
    for value in param_values:
        fitnesses = []
        
        for run in range(num_runs):
            seed = run + 1
            
            params = QWMO_PARAMS.copy()
            params[param_name] = value
            
            optimizer = QWMO(
                func=benchmark,
                dimension=dimension,
                lower_bound=benchmark.lower_bound,
                upper_bound=benchmark.upper_bound,
                population_size=50,
                max_fes=max_fes,
                seed=seed,
                **params
            )
            
            _, best_fit = optimizer.run()
            fitnesses.append(best_fit)
        
        mean_fit = np.mean(fitnesses)
        std_fit = np.std(fitnesses)
        
        results.append({
            'value': value,
            'mean': mean_fit,
            'std': std_fit,
            'fitnesses': fitnesses
        })
        
        print(f"  {param_name}={value}: {mean_fit:.6e} ± {std_fit:.6e}")
    
    return results


def full_sensitivity_analysis(output_dir='results/sensitivity'):
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    params = SENSITIVITY_PARAMS
    function_id = params['function_id']
    dimension = params['dimension']
    max_fes = params['max_fes']
    num_runs = params['num_runs']
    
    print(f"\n{'='*60}")
    print(f"Sensitivity Analysis - F{function_id} (D={dimension}, FEs={max_fes})")
    print(f"{'='*60}")
    
    all_results = {}
    
    print("\nγ (gamma) sensitivity:")
    gamma_results = sensitivity_analysis_single_param(
        'gamma', params['gamma_range'], function_id, dimension, max_fes, num_runs
    )
    all_results['gamma'] = gamma_results
    
    print("\nκ₀ (kappa_0) sensitivity:")
    kappa_results = sensitivity_analysis_single_param(
        'kappa_0', params['kappa_0_range'], function_id, dimension, max_fes, num_runs
    )
    all_results['kappa_0'] = kappa_results
    
    print("\nk_s sensitivity:")
    ks_results = sensitivity_analysis_single_param(
        'k_s', params['k_s_range'], function_id, dimension, max_fes, num_runs
    )
    all_results['k_s'] = ks_results
    
    print("\nε_max (epsilon_max_ratio) sensitivity:")
    epsilon_results = sensitivity_analysis_single_param(
        'epsilon_max_ratio', params['epsilon_max_range'], function_id, dimension, max_fes, num_runs
    )
    all_results['epsilon_max_ratio'] = epsilon_results
    
    plot_sensitivity_results(all_results, output_dir)
    
    return all_results


def plot_sensitivity_results(all_results, output_dir):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    param_names = ['gamma', 'kappa_0', 'k_s', 'epsilon_max_ratio']
    param_labels = ['γ (gamma)', 'κ₀ (kappa_0)', 'k_s', 'ε_max ratio']
    
    for idx, (param_name, param_label) in enumerate(zip(param_names, param_labels)):
        ax = axes[idx // 2, idx % 2]
        
        results = all_results[param_name]
        values = [r['value'] for r in results]
        means = [r['mean'] for r in results]
        stds = [r['std'] for r in results]
        
        ax.errorbar(values, means, yerr=stds, marker='o', linewidth=2, capsize=5)
        ax.set_xlabel(param_label, fontsize=11)
        ax.set_ylabel('Mean Best Fitness', fontsize=11)
        ax.set_title(f'Sensitivity to {param_label}', fontsize=12)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    save_path = os.path.join(output_dir, 'sensitivity_analysis.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\nSaved sensitivity plot to {save_path}")
    plt.close()
