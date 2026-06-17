"""GAPR comprehensive pilot plot generation.

Produces figures under ``figures/{convergence,diversity,epsilon,pauli}/``
within the pilot output directory.

Usage:
    python analysis/gapr_plots.py \
        --input results/gapr_comprehensive_pilot/pilot_results.json \
        --output-dir results/gapr_comprehensive_pilot/figures
"""

import os
import json
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


EPSILON_STYLES = {
    'QWMO_OrbitalPauli_GAPR': ('C0', '-'),
    'QWMO_Full_GAPR': ('C1', '-'),
    'QWMO_Full_GAPR_eps010': ('C4', '-'),
    'QWMO_Full_Static': ('C2', '--'),
    'QWMO_Full_Dynamic': ('C3', '--'),
}
EPSILON_LABELS = {
    'QWMO_OrbitalPauli_GAPR': 'OrbitalPauli_GAPR',
    'QWMO_Full_GAPR': 'Full_GAPR',
    'QWMO_Full_GAPR_eps010': 'Full_GAPR_eps010',
    'QWMO_Full_Static': 'Full_Static',
    'QWMO_Full_Dynamic': 'Full_Dynamic',
}

PAULI_CFGS = [
    'QWMO_OrbitalPauli_Static',
    'QWMO_OrbitalPauli_Dynamic',
    'QWMO_OrbitalPauli_GAPR',
    'QWMO_Full_Static',
    'QWMO_Full_Dynamic',
    'QWMO_Full_GAPR',
    'QWMO_Full_GAPR_eps010',
]
GAPR_PAULI_TRIPLE = [
    'QWMO_OrbitalPauli_Static',
    'QWMO_OrbitalPauli_Dynamic',
    'QWMO_OrbitalPauli_GAPR',
]
GAPR_TRIPLE_LABELS = {
    'QWMO_OrbitalPauli_Static': 'Static',
    'QWMO_OrbitalPauli_Dynamic': 'Dynamic',
    'QWMO_OrbitalPauli_GAPR': 'GAPR',
}


def _ensure_subdirs(base_dir, subdirs):
    paths = {}
    for k, name in subdirs.items():
        p = os.path.join(base_dir, name)
        os.makedirs(p, exist_ok=True)
        paths[k] = p
    return paths


def _func_ids(data):
    out = []
    for key in data:
        try:
            out.append(int(key.replace('F', '')))
        except (ValueError, AttributeError):
            continue
    return out


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
        ax.plot(steps, mean, color=color, linestyle=style,
                label=EPSILON_LABELS[cfg], linewidth=1.5)
        ax.fill_between(steps, mean - std, mean + std, color=color, alpha=0.15)

    ax.set_xlabel('Pauli step index')
    ax.set_ylabel('Epsilon')
    ax.set_title(f'Epsilon History - F{func_id} (mean +/- std, 15 seeds)')
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
    ax.set_xticklabels([c.replace('QWMO_', '') for c in cfgs_present],
                        rotation=30, ha='right')
    ax.set_ylabel('Total count')
    ax.set_title(f'Pauli Mechanism - F{func_id} (15 seeds aggregated)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    fig.tight_layout()
    path = os.path.join(output_dir, f'pauli_mechanism_F{func_id}.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


def plot_pauli_evolution(data, func_id, output_dir):
    """Static vs Dynamic vs GAPR side-by-side: collisions, displacements, SER."""
    fkey = f'F{func_id}'
    coll_vals = []
    disp_vals = []
    ser_vals = []
    present = []

    for cfg in GAPR_PAULI_TRIPLE:
        if cfg not in data.get(fkey, {}):
            continue
        coll = sum(sum(run) for run in data[fkey][cfg].get('pauli_collision_history_list', []))
        disp = sum(sum(run) for run in data[fkey][cfg].get('pauli_displacement_history_list', []))
        succ = sum(sum(run) for run in data[fkey][cfg].get('pauli_success_history_list', []))
        SER = succ / max(disp, 1)
        coll_vals.append(coll)
        disp_vals.append(disp)
        ser_vals.append(SER)
        present.append(cfg)

    if not present:
        return

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    titles = ['Collisions', 'Displacements', 'SER']
    values_list = [coll_vals, disp_vals, ser_vals]
    colors = ['C0', 'C1', 'C2']

    for ax, vals, title, color in zip(axes, values_list, titles, colors):
        x = np.arange(len(present))
        ax.bar(x, vals, color=color, alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([GAPR_TRIPLE_LABELS[c] for c in present])
        ax.set_ylabel(title)
        ax.set_title(f'{title} - F{func_id}')
        ax.grid(True, alpha=0.3, axis='y')

    fig.suptitle(f'Pauli Evolution - F{func_id} (15 seeds aggregated)')
    fig.tight_layout()
    path = os.path.join(output_dir, f'pauli_evolution_F{func_id}.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


def plot_diversity_and_epsilon(data, func_id, output_dir):
    fkey = f'F{func_id}'
    adaptive_cfgs = ['QWMO_OrbitalPauli_GAPR', 'QWMO_Full_GAPR', 'QWMO_Full_GAPR_eps010']

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
        ax.set_title(f'{title} - F{func_id}')
        ax.legend()
        ax.grid(True, alpha=0.3)

    axes[1].set_xlabel('Step index')
    fig.tight_layout()
    path = os.path.join(output_dir, f'diversity_epsilon_F{func_id}.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


def plot_convergence(data, func_id, output_dir):
    fkey = f'F{func_id}'
    cfgs = [
        'QWMO_OrbitalOnly',
        'QWMO_OrbitalPauli_Static',
        'QWMO_OrbitalPauli_Dynamic',
        'QWMO_OrbitalPauli_GAPR',
        'QWMO_OrbitalEscape',
        'QWMO_Full_Static',
        'QWMO_Full_Dynamic',
        'QWMO_Full_GAPR',
        'QWMO_Full_GAPR_eps010',
    ]
    fig, ax = plt.subplots(figsize=(10, 5))
    for cfg in cfgs:
        if cfg not in data.get(fkey, {}):
            continue
        conv_list = data[fkey][cfg].get('convergence_list', [])
        if not conv_list:
            continue
        lens = [len(c) for c in conv_list if c]
        if not lens:
            continue
        min_len = min(lens)
        aligned = np.array([c[:min_len] for c in conv_list if len(c) >= min_len])
        mean = np.mean(aligned, axis=0)
        std = np.std(aligned, axis=0)
        steps = np.arange(len(mean))
        ax.plot(steps, mean, label=cfg.replace('QWMO_', ''), linewidth=1.5)
        ax.fill_between(steps, mean - std, mean + std, alpha=0.15)
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Best Fitness')
    ax.set_yscale('log')
    ax.set_title(f'Convergence - F{func_id} (mean +/- std, 15 seeds)')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(output_dir, f'convergence_F{func_id}.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


def main():
    parser = argparse.ArgumentParser(description='GAPR comprehensive pilot plots')
    parser.add_argument('--input', type=str,
                        default='results/gapr_comprehensive_pilot/pilot_results.json',
                        help='Input JSON path')
    parser.add_argument('--output-dir', type=str,
                        default='results/gapr_comprehensive_pilot/figures',
                        help='Output directory for figures')
    args = parser.parse_args()

    subdirs = _ensure_subdirs(args.output_dir, {
        'convergence': 'convergence',
        'diversity': 'diversity',
        'epsilon': 'epsilon',
        'pauli': 'pauli',
    })

    with open(args.input, 'r') as f:
        data = json.load(f)

    func_ids = _func_ids(data)
    print(f"Generating plots for functions: {func_ids}")

    for fid in func_ids:
        plot_convergence(data, fid, subdirs['convergence'])
        plot_diversity_and_epsilon(data, fid, subdirs['diversity'])
        plot_epsilon_history(data, fid, subdirs['epsilon'])
        plot_pauli_mechanism(data, fid, subdirs['pauli'])
        plot_pauli_evolution(data, fid, subdirs['pauli'])

    print("All plots generated.")


if __name__ == '__main__':
    main()
