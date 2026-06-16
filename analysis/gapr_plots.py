"""GAPR pilot plot generation.

Usage:
    python analysis/gapr_plots.py --input results/gapr_pilot/gapr_pilot_D30.json --output-dir results/gapr_pilot/figures
"""

import os
import json
import argparse
import numpy as np
from scipy.stats import pearsonr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


EPSILON_STYLES = {
    'QWMO_OrbitalPauli_Adaptive': ('C0', '-'),
    'QWMO_Full_Adaptive': ('C1', '-'),
    'QWMO_Full_Static': ('C2', '--'),
    'QWMO_Full_Dynamic': ('C3', '--'),
}
EPSILON_LABELS = {
    'QWMO_OrbitalPauli_Adaptive': 'OrbitalPauli_Adaptive',
    'QWMO_Full_Adaptive': 'Full_Adaptive',
    'QWMO_Full_Static': 'Full_Static',
    'QWMO_Full_Dynamic': 'Full_Dynamic',
}

PAULI_CFGS = [
    'QWMO_OrbitalPauli_Static',
    'QWMO_OrbitalPauli_Dynamic',
    'QWMO_OrbitalPauli_Adaptive',
    'QWMO_Full_Static',
    'QWMO_Full_Dynamic',
    'QWMO_Full_Adaptive',
]


def plot_epsilon_history(data, func_id, output_dir):
    fkey = f'F{func_id}'
    fig, ax = plt.subplots(figsize=(10, 5))

    for cfg, (color, style) in EPSILON_STYLES.items():
        if cfg not in data.get(fkey, {}):
            continue
        ep_list_list = data[fkey][cfg].get('epsilon_history_list', [])
        if not ep_list_list:
            continue
        lens = [len(ep) for ep in ep_list_list if ep]
        if not lens:
            continue
        min_len = min(lens)
        aligned = np.array([ep[:min_len] for ep in ep_list_list if len(ep) >= min_len])
        mean = np.mean(aligned, axis=0)
        std = np.std(aligned, axis=0)
        steps = np.arange(len(mean))
        ax.plot(steps, mean, color=color, linestyle=style, label=EPSILON_LABELS[cfg], linewidth=1.5)
        ax.fill_between(steps, mean - std, mean + std, color=color, alpha=0.15)

    ax.set_xlabel('Pauli step index')
    ax.set_ylabel('Epsilon')
    ax.set_title(f'Epsilon History — F{func_id} (mean ± std, 10 seeds)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(output_dir, f'epsilon_history_F{func_id}.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


def plot_pauli_mechanism(data, func_id, output_dir):
    fkey = f'F{func_id}'
    fig, ax = plt.subplots(figsize=(10, 5))

    cfgs_present = []
    coll_vals = []
    disp_vals = []
    succ_vals = []

    for cfg in PAULI_CFGS:
        if cfg not in data.get(fkey, {}):
            continue
        coll = sum(sum(run) for run in data[fkey][cfg].get('pauli_collision_history_list', []))
        disp = sum(sum(run) for run in data[fkey][cfg].get('pauli_displacement_history_list', []))
        succ = sum(sum(run) for run in data[fkey][cfg].get('pauli_success_history_list', []))
        cfgs_present.append(cfg)
        coll_vals.append(coll)
        disp_vals.append(disp)
        succ_vals.append(succ)

    x = np.arange(len(cfgs_present))
    width = 0.25
    ax.bar(x - width, coll_vals, width, label='Collisions', color='C0', alpha=0.8)
    ax.bar(x, disp_vals, width, label='Displacements', color='C1', alpha=0.8)
    ax.bar(x + width, succ_vals, width, label='Successes', color='C2', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace('QWMO_', '') for c in cfgs_present], rotation=30, ha='right')
    ax.set_ylabel('Total count')
    ax.set_title(f'Pauli Mechanism — F{func_id} (10 seeds aggregated)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    fig.tight_layout()
    path = os.path.join(output_dir, f'pauli_mechanism_F{func_id}.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


def plot_diversity_and_epsilon(data, func_id, output_dir):
    fkey = f'F{func_id}'
    adaptive_cfgs = ['QWMO_OrbitalPauli_Adaptive', 'QWMO_Full_Adaptive']

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=False)

    for ax, metric, ylabel, title in [
        (axes[0], 'diversity_history_list', 'Diversity', 'Diversity over time'),
        (axes[1], 'epsilon_history_list', 'Epsilon', 'Epsilon over time'),
    ]:
        for cfg in adaptive_cfgs:
            if cfg not in data.get(fkey, {}):
                continue
            hist_list = data[fkey][cfg].get(metric, [])
            if not hist_list:
                continue
            lens = [len(h) for h in hist_list if h]
            if not lens:
                continue
            min_len = min(lens)
            aligned = np.array([h[:min_len] for h in hist_list if len(h) >= min_len])
            mean = np.mean(aligned, axis=0)
            std = np.std(aligned, axis=0)
            steps = np.arange(len(mean))
            label = cfg.replace('QWMO_', '')
            ax.plot(steps, mean, label=label, linewidth=1.5)
            ax.fill_between(steps, mean - std, mean + std, alpha=0.15)

        ax.set_ylabel(ylabel)
        ax.set_title(f'{title} — F{func_id}')
        ax.legend()
        ax.grid(True, alpha=0.3)

    axes[1].set_xlabel('Step index')
    fig.tight_layout()
    path = os.path.join(output_dir, f'diversity_epsilon_F{func_id}.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


def plot_epsilon_diversity_correlation(data, func_id, output_dir):
    fkey = f'F{func_id}'
    adaptive_cfgs = ['QWMO_OrbitalPauli_Adaptive', 'QWMO_Full_Adaptive']

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax_idx, cfg in enumerate(adaptive_cfgs):
        ax = axes[ax_idx]
        if cfg not in data.get(fkey, {}):
            ax.set_title(f'{cfg.replace("QWMO_", "")} — no data')
            continue

        div_list_list = data[fkey][cfg].get('diversity_history_list', [])
        ep_list_list = data[fkey][cfg].get('epsilon_history_list', [])
        if not div_list_list or not ep_list_list:
            ax.set_title(f'{cfg.replace("QWMO_", "")} — no data')
            continue

        all_r = []
        for div_hist, ep_hist in zip(div_list_list, ep_list_list):
            if len(div_hist) < 2 or len(ep_hist) < 2:
                continue
            sample_indices = [i * 500 for i in range(1, len(div_hist))]
            sample_indices = [i for i in sample_indices if i <= len(ep_hist)]
            if len(sample_indices) < 2:
                continue
            eps_samples = [ep_hist[i - 1] for i in sample_indices]
            div_samples = [div_hist[i // 500] for i in sample_indices]
            r, p = pearsonr(div_samples, eps_samples)
            all_r.append(r)
            ax.scatter(div_samples, eps_samples, alpha=0.5, s=10)

        if all_r:
            mean_r = np.mean(all_r)
            ax.set_title(f'{cfg.replace("QWMO_", "")}\nPearson r = {mean_r:.3f}')
        else:
            ax.set_title(f'{cfg.replace("QWMO_", "")} — no correlation data')

        ax.set_xlabel('Diversity')
        ax.set_ylabel('Epsilon')
        ax.grid(True, alpha=0.3)

    fig.tight_layout()
    path = os.path.join(output_dir, f'epsilon_diversity_correlation_F{func_id}.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


def main():
    parser = argparse.ArgumentParser(description='GAPR plot generation')
    parser.add_argument('--input', type=str, default='results/gapr_pilot/gapr_pilot_D30.json',
                        help='Input JSON path')
    parser.add_argument('--output-dir', type=str, default='results/gapr_pilot/figures',
                        help='Output directory for figures')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.input, 'r') as f:
        data = json.load(f)

    func_ids = []
    for key in data:
        try:
            fid = int(key.replace('F', ''))
            func_ids.append(fid)
        except (ValueError, AttributeError):
            continue

    print(f"Generating plots for functions: {func_ids}")

    for fid in func_ids:
        plot_epsilon_history(data, fid, args.output_dir)
        plot_pauli_mechanism(data, fid, args.output_dir)
        plot_diversity_and_epsilon(data, fid, args.output_dir)
        plot_epsilon_diversity_correlation(data, fid, args.output_dir)

    print("All plots generated.")


if __name__ == '__main__':
    main()
