import numpy as np
import matplotlib.pyplot as plt


def analyze_pauli_activations(results_dict, function_id, dimension=30, save_path=None):
    func_key = f'F{function_id}'
    if func_key not in results_dict:
        print(f"Function {func_key} not found in results")
        return
    
    configs_with_pauli = ['QWMO_Full', 'QWMO_OrbitalPauli']
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    for idx, config_name in enumerate(configs_with_pauli):
        if config_name not in results_dict[func_key]:
            continue
        
        config_results = results_dict[func_key][config_name]
        
        if 'pauli_collisions' not in config_results or not config_results['pauli_collisions']:
            continue
        
        collisions = config_results['pauli_collisions']
        iterations = np.arange(1, len(collisions) + 1)
        
        ax = axes[idx]
        ax.plot(iterations, collisions, alpha=0.6, linewidth=1)
        
        window = min(100, len(collisions) // 10)
        if window > 1:
            smoothed = np.convolve(collisions, np.ones(window)/window, mode='valid')
            ax.plot(np.arange(window-1, len(collisions)), smoothed, 
                   color='red', linewidth=2, label=f'Moving Average (w={window})')
        
        ax.set_xlabel('Iteration', fontsize=11)
        ax.set_ylabel('Collision Count', fontsize=11)
        ax.set_title(f'{config_name} - Pauli Collisions (F{function_id}, D={dimension})', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved to {save_path}")
    
    plt.close()
    
    for config_name in configs_with_pauli:
        if config_name in results_dict[func_key]:
            collisions = results_dict[func_key][config_name].get('pauli_collisions', [])
            if collisions:
                total_collisions = sum(collisions)
                avg_collisions = np.mean(collisions)
                print(f"\n{config_name}:")
                print(f"  Total collisions: {total_collisions}")
                print(f"  Average per iteration: {avg_collisions:.2f}")


def plot_pauli_analysis(results_dict, function_id=10, dimension=30, output_dir='results/plots'):
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    save_path = os.path.join(output_dir, f'pauli_activation_F{function_id}_D{dimension}.png')
    analyze_pauli_activations(results_dict, function_id, dimension, save_path=save_path)
    print(f"Generated Pauli activation plot for F{function_id} (D={dimension})")
