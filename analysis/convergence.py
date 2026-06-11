import numpy as np
import matplotlib.pyplot as plt
from experiments.config import CONVERGENCE_FUNCTIONS, ABLATION_CONFIGS


def plot_convergence_curves(results_dict, function_id, dimension=30, 
                           algorithms=None, save_path=None):
    func_key = f'F{function_id}'
    if func_key not in results_dict:
        print(f"Function {func_key} not found in results")
        return
    
    if algorithms is None:
        algorithms = ABLATION_CONFIGS + ['PSO', 'CMA_ES', 'SHADE']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
              '#9467bd', '#8c564b', '#e377c2']
    
    for i, algo_name in enumerate(algorithms):
        if algo_name not in results_dict[func_key]:
            continue
        
        algo_results = results_dict[func_key][algo_name]
        
        if 'convergence' not in algo_results or not algo_results['convergence']:
            continue
        
        convergence = algo_results['convergence']
        iterations = np.arange(1, len(convergence) + 1)
        
        convergence = np.array(convergence)
        convergence = np.maximum(convergence, 1e-10)
        
        color = colors[i % len(colors)]
        ax.plot(iterations, convergence, label=algo_name, color=color, linewidth=2)
    
    ax.set_xlabel('Iteration', fontsize=12)
    ax.set_ylabel('Best Fitness', fontsize=12)
    ax.set_title(f'Convergence Curves - F{function_id} (D={dimension})', fontsize=14)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved to {save_path}")
    
    plt.close()


def plot_all_convergence(results_dict, function_ids=None, dimensions=None, 
                         output_dir='results/plots'):
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    if function_ids is None:
        function_ids = CONVERGENCE_FUNCTIONS
    
    if dimensions is None:
        dimensions = [30]
    
    for dim in dimensions:
        for func_id in function_ids:
            save_path = os.path.join(output_dir, f'convergence_F{func_id}_D{dim}.png')
            plot_convergence_curves(results_dict, func_id, dim, save_path=save_path)
            print(f"Generated convergence plot for F{func_id} (D={dim})")
