"""QWMO Pilot Validation Runner.

Validates Aşama 1 fixes by running a focused 240-run pilot on 4 functions,
6 QWMO ablation configs, 10 seeds at 30D / 300k FE. Produces a JSON with
all mechanism logs and a markdown report with pass/fail status for the
K1-K6 criteria.

Usage:
    python experiments/pilot_validation.py [--max-workers N] [--output-dir DIR]
"""

import os
import sys
import json
import argparse
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.config import PILOT_CONFIG
from experiments.runner import ExperimentRunner, ALGO_TO_QWMO_CONFIG


def _run_single(func_id, dimension, algo_name, seed, pop_size, max_fes):
    runner = ExperimentRunner(
        dimensions=dimension, population_size=pop_size, max_fes=max_fes,
        num_runs=1, seed_list=[seed], max_workers=1
    )
    return (func_id, algo_name, seed, runner.run_single_experiment(func_id, algo_name, seed))


def run_pilot(config, max_workers=None):
    funcs = config['functions']
    dim = config['dimension']
    pop = config['population_size']
    max_fes = config['max_fes']
    seeds = config['seeds']
    configs = config['ablation_configs']
    output_dir = config['output_dir']
    os.makedirs(output_dir, exist_ok=True)

    if max_workers is None:
        max_workers = int(os.environ.get('MAX_WORKERS', 8))

    n_workers = min(max_workers, os.cpu_count() or 1)
    print(f"Pilot config: funcs={funcs} dim={dim} pop={pop} max_fes={max_fes} "
          f"seeds={seeds[0]}-{seeds[-1]} configs={len(configs)} workers={n_workers}")

    tasks = [
        (fid, cfg, seed)
        for fid in funcs
        for cfg in configs
        for seed in seeds
    ]
    total = len(tasks)
    print(f"Total tasks: {total}")

    raw_results = {}
    completed = 0
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        fut_to_task = {
            ex.submit(_run_single, fid, dim, cfg, seed, pop, max_fes): (fid, cfg, seed)
            for fid, cfg, seed in tasks
        }
        for fut in as_completed(fut_to_task):
            fid, cfg, seed = fut_to_task[fut]
            try:
                _, _, _, result = fut.result()
                if result:
                    raw_results.setdefault(f'F{fid}', {}).setdefault(cfg, []).append({
                        'seed': seed,
                        'result': result,
                    })
                    completed += 1
                    print(f"  [{completed}/{total}] F{fid} | {cfg} | seed={seed} "
                          f"f={result['best_fitness']:.4e} fes={result['fes_count']}")
                else:
                    print(f"  [{completed + 1}/{total}] F{fid} | {cfg} | seed={seed}: FAILED")
                    completed += 1
            except Exception as e:
                completed += 1
                print(f"  [{completed}/{total}] F{fid} | {cfg} | seed={seed}: ERROR {e}")

    aggregated = {}
    for fid, func_results in raw_results.items():
        aggregated[fid] = {}
        for cfg, runs in func_results.items():
            fitnesses = [r['result']['best_fitness'] for r in runs]
            fes_counts = [r['result']['fes_count'] for r in runs]
            times = [r['result']['elapsed_time'] for r in runs]
            entry = {
                'fitnesses': fitnesses,
                'mean': float(np.mean(fitnesses)),
                'std': float(np.std(fitnesses)),
                'fes_count_list': fes_counts,
                'times': times,
                'mean_time': float(np.mean(times)),
                'convergence_list': [r['result']['convergence'] for r in runs],
                'diversity_history_list': [r['result']['diversity_history'] for r in runs],
                'pauli_collision_history_list': [r['result']['pauli_collision_history'] for r in runs],
                'pauli_displacement_history_list': [r['result']['pauli_displacement_history'] for r in runs],
                'pauli_success_history_list': [r['result']['pauli_success_history'] for r in runs],
                'escape_attempt_history_list': [r['result']['escape_attempt_history'] for r in runs],
                'escape_success_history_list': [r['result']['escape_success_history'] for r in runs],
                'escape_delta_history_list': [r['result']['escape_delta_history'] for r in runs],
                'escape_phase_counts_list': [r['result']['escape_phase_counts'] for r in runs],
            }
            aggregated[fid][cfg] = entry

    json_path = os.path.join(output_dir, config['json_name'])
    with open(json_path, 'w') as f:
        json.dump(aggregated, f, indent=2, default=str)
    print(f"\nSaved pilot results to {json_path}")

    return aggregated, json_path


def check_criteria(aggregated, funcs, configs):
    """Return dict of (K, description, passed, evidence)."""
    results = {}

    pauli_configs = [c for c in configs if 'pauli' in c.lower() or 'full' in c.lower()]
    pauli_displacements_by_func = {}
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in pauli_configs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            disp_total = sum(
                sum(run)
                for run in aggregated[fkey][cfg].get('pauli_displacement_history_list', [])
            )
            pauli_displacements_by_func.setdefault(fkey, {})[cfg] = disp_total

    k1_passed = False
    k1_evidence = []
    for fkey, cfg_disp in pauli_displacements_by_func.items():
        for cfg, total in cfg_disp.items():
            if total > 0:
                k1_passed = True
                k1_evidence.append(f"  {fkey}/{cfg}: total displacements = {total}")
    results['K1'] = {
        'description': 'Pauli active (mean displacement > 0 in at least one (F,config))',
        'passed': k1_passed,
        'evidence': '\n'.join(k1_evidence) if k1_evidence else '  No Pauli displacements detected in any (function, config).',
    }

    k2_evidence = []
    k2_passed = False
    for fid in funcs:
        fkey = f'F{fid}'
        op = aggregated.get(fkey, {}).get('QWMO_OrbitalOnly', {}).get('fitnesses', [])
        opd = aggregated.get(fkey, {}).get('QWMO_OrbitalPauli_Dynamic', {}).get('fitnesses', [])
        if len(op) == len(opd) and len(op) > 0:
            n_diff = sum(1 for x, y in zip(op, opd) if x != y)
            identical = n_diff == 0
            k2_evidence.append(f"  {fkey}: identical={identical} (n_different={n_diff}/{len(op)})")
            if not identical:
                k2_passed = True
        else:
            k2_evidence.append(f"  {fkey}: insufficient data (len op={len(op)}, opd={len(opd)})")
    results['K2'] = {
        'description': 'OrbitalPauli_Dynamic differs from OrbitalOnly (final fitness)',
        'passed': k2_passed,
        'evidence': '\n'.join(k2_evidence),
    }

    k3_evidence = []
    k3_passed = False
    for fid in funcs:
        fkey = f'F{fid}'
        s = aggregated.get(fkey, {}).get('QWMO_OrbitalPauli_Static', {}).get('fitnesses', [])
        d = aggregated.get(fkey, {}).get('QWMO_OrbitalPauli_Dynamic', {}).get('fitnesses', [])
        if len(s) == len(d) and len(s) > 0:
            n_diff = sum(1 for x, y in zip(s, d) if x != y)
            identical = n_diff == 0
            k3_evidence.append(f"  {fkey}: identical={identical} (n_different={n_diff}/{len(s)})")
            if not identical:
                k3_passed = True
    results['K3'] = {
        'description': 'OrbitalPauli_Static differs from OrbitalPauli_Dynamic',
        'passed': k3_passed,
        'evidence': '\n'.join(k3_evidence),
    }

    escape_configs = [c for c in configs if 'escape' in c.lower() or 'full' in c.lower()]
    k4_evidence = []
    k4_passed = False
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in escape_configs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            attempts = sum(
                sum(run) for run in aggregated[fkey][cfg].get('escape_attempt_history_list', [])
            )
            successes = sum(
                sum(run) for run in aggregated[fkey][cfg].get('escape_success_history_list', [])
            )
            k4_evidence.append(f"  {fkey}/{cfg}: attempts={attempts} successes={successes}")
            if attempts > 0 and successes >= 0:
                k4_passed = True
    results['K4'] = {
        'description': 'Escape log reportable (attempts > 0 and successes computable)',
        'passed': k4_passed,
        'evidence': '\n'.join(k4_evidence),
    }

    k5_evidence = []
    k5_passed = True
    max_fes = aggregated.get('F1', {}).get('QWMO_Full_Dynamic', {}).get('fes_count_list', [None])[0]
    if max_fes is None:
        k5_passed = False
        k5_evidence.append("  Could not determine max_fes from data")
    else:
        for fid in funcs:
            fkey = f'F{fid}'
            for cfg in configs:
                if cfg not in aggregated.get(fkey, {}):
                    continue
                fes_list = aggregated[fkey][cfg].get('fes_count_list', [])
                for i, fes in enumerate(fes_list):
                    if fes > max_fes:
                        k5_passed = False
                        k5_evidence.append(f"  {fkey}/{cfg}/seed_{i}: fes={fes} > max_fes={max_fes}")
                    elif fes < 0.98 * max_fes:
                        k5_evidence.append(f"  WARN {fkey}/{cfg}/seed_{i}: fes={fes} < 0.98*max_fes")
    results['K5'] = {
        'description': f'FE budget respected (fes_count <= {max_fes})',
        'passed': k5_passed,
        'evidence': '\n'.join(k5_evidence) if k5_evidence else f'  All runs within budget (max_fes={max_fes})',
    }

    k6_evidence = []
    k6_passed = True
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in configs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            div_list = aggregated[fkey][cfg].get('diversity_history_list', [])
            for i, div in enumerate(div_list):
                if not div or len(div) == 0:
                    k6_passed = False
                    k6_evidence.append(f"  {fkey}/{cfg}/seed_{i}: diversity_history empty")
    results['K6'] = {
        'description': 'Diversity logs saved (non-empty for every QWMO run)',
        'passed': k6_passed,
        'evidence': '\n'.join(k6_evidence) if k6_evidence else '  All QWMO runs have non-empty diversity_history',
    }

    return results


def write_report(aggregated, criteria, output_path, funcs, configs):
    lines = []
    lines.append('# QWMO Pilot Validation Report')
    lines.append('')
    lines.append(f'**Functions:** {funcs}  ')
    lines.append(f'**Configs:** {len(configs)} ({", ".join(configs)})  ')
    lines.append(f'**Seeds:** 10  ')
    lines.append(f'**Dimension:** 30  ')
    lines.append(f'**Max FEs:** 300,000 (CEC2017 standard)')
    lines.append('')

    lines.append('## Pass/Fail Summary')
    lines.append('')
    all_passed = True
    for kid in ['K1', 'K2', 'K3', 'K4', 'K5', 'K6']:
        c = criteria[kid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        if not c['passed']:
            all_passed = False
        lines.append(f'- **{kid}** [{mark}] {c["description"]}')
    lines.append('')
    lines.append(f'**Overall:** {"ALL PASS" if all_passed else "REGRESSION — see details"}')
    lines.append('')

    for kid in ['K1', 'K2', 'K3', 'K4', 'K5', 'K6']:
        c = criteria[kid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        lines.append(f'## {kid}: {c["description"]}')
        lines.append(f'**Result:** {mark}')
        lines.append('')
        lines.append('```')
        lines.append(c['evidence'])
        lines.append('```')
        lines.append('')

    lines.append('## Final Fitness Summary (mean ± std)')
    lines.append('')
    lines.append('| Function | ' + ' | '.join(configs) + ' |')
    lines.append('|---|' + '---|' * len(configs))
    for fid in funcs:
        fkey = f'F{fid}'
        row = [fkey]
        for cfg in configs:
            if cfg in aggregated.get(fkey, {}):
                m = aggregated[fkey][cfg]['mean']
                s = aggregated[fkey][cfg]['std']
                row.append(f'{m:.3e} ± {s:.2e}')
            else:
                row.append('—')
        lines.append('| ' + ' | '.join(row) + ' |')
    lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"\nSaved pilot report to {output_path}")


def _sequential_run(func_id, dim, algo_name, seed, pop, max_fes):
    runner = ExperimentRunner(
        dimensions=dim, population_size=pop, max_fes=max_fes,
        num_runs=1, seed_list=[seed], max_workers=1
    )
    return (func_id, algo_name, seed, runner.run_single_experiment(func_id, algo_name, seed))


def run_pilot_sequential(config):
    funcs = config['functions']
    dim = config['dimension']
    pop = config['population_size']
    max_fes = config['max_fes']
    seeds = config['seeds']
    configs = config['ablation_configs']
    output_dir = config['output_dir']
    os.makedirs(output_dir, exist_ok=True)

    print(f"Pilot (sequential): funcs={funcs} dim={dim} pop={pop} max_fes={max_fes} "
          f"seeds={seeds[0]}-{seeds[-1]} configs={len(configs)}")

    raw_results = {}
    completed = 0
    total = len(funcs) * len(configs) * len(seeds)
    for fid in funcs:
        for cfg in configs:
            for seed in seeds:
                _, _, _, result = _sequential_run(fid, dim, cfg, seed, pop, max_fes)
                if result:
                    raw_results.setdefault(f'F{fid}', {}).setdefault(cfg, []).append({
                        'seed': seed,
                        'result': result,
                    })
                completed += 1
                if result:
                    print(f"  [{completed}/{total}] F{fid} | {cfg} | seed={seed} "
                          f"f={result['best_fitness']:.4e} fes={result['fes_count']}")
                else:
                    print(f"  [{completed}/{total}] F{fid} | {cfg} | seed={seed}: FAILED")

    return _aggregate_and_save(raw_results, config)


def _aggregate_and_save(raw_results, config):
    aggregated = {}
    for fid, func_results in raw_results.items():
        aggregated[fid] = {}
        for cfg, runs in func_results.items():
            fitnesses = [r['result']['best_fitness'] for r in runs]
            fes_counts = [r['result']['fes_count'] for r in runs]
            times = [r['result']['elapsed_time'] for r in runs]
            entry = {
                'fitnesses': fitnesses,
                'mean': float(np.mean(fitnesses)),
                'std': float(np.std(fitnesses)),
                'fes_count_list': fes_counts,
                'times': times,
                'mean_time': float(np.mean(times)),
                'convergence_list': [r['result']['convergence'] for r in runs],
                'diversity_history_list': [r['result']['diversity_history'] for r in runs],
                'pauli_collision_history_list': [r['result']['pauli_collision_history'] for r in runs],
                'pauli_displacement_history_list': [r['result']['pauli_displacement_history'] for r in runs],
                'pauli_success_history_list': [r['result']['pauli_success_history'] for r in runs],
                'escape_attempt_history_list': [r['result']['escape_attempt_history'] for r in runs],
                'escape_success_history_list': [r['result']['escape_success_history'] for r in runs],
                'escape_delta_history_list': [r['result']['escape_delta_history'] for r in runs],
                'escape_phase_counts_list': [r['result']['escape_phase_counts'] for r in runs],
            }
            aggregated[fid][cfg] = entry

    json_path = os.path.join(config['output_dir'], config['json_name'])
    with open(json_path, 'w') as f:
        json.dump(aggregated, f, indent=2, default=str)
    print(f"\nSaved pilot results to {json_path}")
    return aggregated, json_path


def main():
    parser = argparse.ArgumentParser(description='QWMO Pilot Validation')
    parser.add_argument('--max-workers', type=int, default=None)
    parser.add_argument('--output-dir', type=str, default=None)
    parser.add_argument('--sequential', action='store_true',
                        help='Run sequentially (Windows-safe).')
    args = parser.parse_args()

    config = dict(PILOT_CONFIG)
    if args.output_dir:
        config['output_dir'] = args.output_dir

    if args.sequential:
        aggregated, json_path = run_pilot_sequential(config)
    else:
        aggregated, json_path = run_pilot(config, max_workers=args.max_workers)
    criteria = check_criteria(aggregated, config['functions'], config['ablation_configs'])
    report_path = os.path.join(config['output_dir'], config['report_name'])
    print('\n=== PILOT PASS/FAIL ===')
    for kid in ['K1', 'K2', 'K3', 'K4', 'K5', 'K6']:
        c = criteria[kid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        print(f'  {kid}: {mark} - {c["description"]}')


if __name__ == '__main__':
    main()
