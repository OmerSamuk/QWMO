import numpy as np
import matplotlib.pyplot as plt


def plot_diversity_curves(results_dict, function_id, dimension=30,
                         configs=['QWMO_Full', 'QWMO_OrbitalOnly'], 
                         save_path=None):
    func_key = f'F{function_id}'
    if func_key not in results_dict:
        print(f"Function {func_key} not found in results")
        return
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, config_name in enumerate(configs):
        if config_name not in results_dict[func_key]:
            continue
        
        config_results = results_dict[func_key][config_name]
        
        if 'diversity_history' not in config_results or not config_results['diversity_history']:
            continue
        
        diversity = config_results['diversity_history']
        iterations = np.arange(len(diversity)) * 500
        
        color = colors[i % len(colors)]
        ax.plot(iterations, diversity, label=config_name, color=color, linewidth=2)
    
    ax.set_xlabel('Iteration', fontsize=12)
    ax.set_ylabel('Normalized Mean Pairwise Distance', fontsize=12)
    ax.set_title(f'Population Diversity - F{function_id} (D={dimension})', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved to {save_path}")
    
    plt.close()


def compare_diversity(results_dict, function_id=10, dimension=30, output_dir='results/plots'):
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    save_path = os.path.join(output_dir, f'diversity_F{function_id}_D{dimension}.png')
    plot_diversity_curves(results_dict, function_id, dimension, save_path=save_path)
    print(f"Generated diversity plot for F{function_id} (D={dimension})")
