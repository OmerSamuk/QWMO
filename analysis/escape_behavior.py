import numpy as np
import matplotlib.pyplot as plt


def analyze_escape_behavior(results_dict, function_id, dimension=30, save_path=None):
    func_key = f'F{function_id}'
    if func_key not in results_dict:
        print(f"Function {func_key} not found in results")
        return
    
    configs_with_escape = ['QWMO_Full', 'QWMO_OrbitalEscape']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    for idx, config_name in enumerate(configs_with_escape):
        if config_name not in results_dict[func_key]:
            continue
        
        config_results = results_dict[func_key][config_name]
        
        if 'escape_activations' not in config_results or not config_results['escape_activations']:
            continue
        
        escapes = config_results['escape_activations']
        iterations = np.arange(1, len(escapes) + 1)
        
        ax1 = axes[idx, 0]
        ax1.plot(iterations, escapes, alpha=0.6, linewidth=1, color='blue')
        
        window = min(100, len(escapes) // 10)
        if window > 1:
            smoothed = np.convolve(escapes, np.ones(window)/window, mode='valid')
            ax1.plot(np.arange(window-1, len(escapes)), smoothed, 
                    color='red', linewidth=2, label=f'Moving Average (w={window})')
        
        ax1.set_xlabel('Iteration', fontsize=11)
        ax1.set_ylabel('Escape Activations', fontsize=11)
        ax1.set_title(f'{config_name} - Escape Count', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2 = axes[idx, 1]
        cumulative = np.cumsum(escapes)
        ax2.plot(iterations, cumulative, color='green', linewidth=2)
        ax2.set_xlabel('Iteration', fontsize=11)
        ax2.set_ylabel('Cumulative Escapes', fontsize=11)
        ax2.set_title(f'{config_name} - Cumulative Escapes', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        total_escapes = sum(escapes)
        avg_escapes = np.mean(escapes)
        max_escapes = max(escapes)
        
        print(f"\n{config_name}:")
        print(f"  Total escapes: {total_escapes}")
        print(f"  Average per iteration: {avg_escapes:.2f}")
        print(f"  Max escapes in single iteration: {max_escapes}")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved to {save_path}")
    
    plt.close()


def plot_escape_analysis(results_dict, function_id=10, dimension=30, output_dir='results/plots'):
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    save_path = os.path.join(output_dir, f'escape_behavior_F{function_id}_D{dimension}.png')
    analyze_escape_behavior(results_dict, function_id, dimension, save_path=save_path)
    print(f"Generated escape behavior plot for F{function_id} (D={dimension})")
