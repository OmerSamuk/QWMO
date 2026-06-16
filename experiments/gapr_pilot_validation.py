"""QWMO-GAPR Pilot Validation Runner.

Validates the Geometry-Adaptive Pauli Radius (GAPR) by running a pilot on
F10 and F20 with all 8 ablation configs, 10 seeds at 30D / 300k FE.
Produces a JSON with all mechanism logs and a markdown report with pass/fail
status for the K1-K9 criteria.

Usage:
    python experiments/gapr_pilot_validation.py [--max-workers N] [--output-dir DIR]
"""

import os
import sys
import json
import argparse
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.config import GAPR_PILOT_CONFIG
from experiments.runner import ExperimentRunner, ALGO_TO_QWMO_CONFIG

PAULI_CONFIGS = [
    "QWMO_OrbitalPauli_Static",
    "QWMO_OrbitalPauli_Dynamic",
    "QWMO_OrbitalPauli_Adaptive",
    "QWMO_Full_Static",
    "QWMO_Full_Dynamic",
    "QWMO_Full_Adaptive",
]
ESCAPE_CONFIGS = [
    "QWMO_OrbitalEscape",
    "QWMO_Full_Static",
    "QWMO_Full_Dynamic",
    "QWMO_Full_Adaptive",
]
ADAPTIVE_CONFIGS = [
    "QWMO_OrbitalPauli_Adaptive",
    "QWMO_Full_Adaptive",
]


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
    print(f"GAPR Pilot: funcs={funcs} dim={dim} pop={pop} max_fes={max_fes} "
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

    aggregated = _aggregate_results(raw_results)

    json_path = os.path.join(output_dir, config['json_name'])
    with open(json_path, 'w') as f:
        json.dump(aggregated, f, indent=2, default=str)
    print(f"\nSaved GAPR pilot results to {json_path}")

    return aggregated, json_path


def _aggregate_results(raw_results):
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
                'epsilon_history_list': [r['result']['epsilon_history'] for r in runs],
                'escape_attempt_history_list': [r['result']['escape_attempt_history'] for r in runs],
                'escape_executed_history_list': [r['result']['escape_executed_history'] for r in runs],
                'escape_success_history_list': [r['result']['escape_success_history'] for r in runs],
                'escape_delta_history_list': [r['result']['escape_delta_history'] for r in runs],
                'escape_phase_counts_list': [r['result']['escape_phase_counts'] for r in runs],
            }
            aggregated[fid][cfg] = entry
    return aggregated


def check_criteria(aggregated, funcs, configs, max_fes=300000):
    results = {}

    adaptive_configs_in_use = [c for c in ADAPTIVE_CONFIGS if c in configs]
    pauli_configs_in_use = [c for c in PAULI_CONFIGS if c in configs]
    escape_configs_in_use = [c for c in ESCAPE_CONFIGS if c in configs]

    search_range = None

    # --- K1: Adaptive epsilon bounded ---
    k1_passed = True
    k1_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in adaptive_configs_in_use:
            if cfg not in aggregated.get(fkey, {}):
                continue
            ep_list_list = aggregated[fkey][cfg].get('epsilon_history_list', [])
            for i, ep_hist in enumerate(ep_list_list):
                if not ep_hist:
                    k1_passed = False
                    k1_evidence.append(f"  {fkey}/{cfg}/seed_{i}: epsilon_history empty")
                    continue
                min_ep = min(ep_hist)
                max_ep = max(ep_hist)
                mean_ep = np.mean(ep_hist)
                k1_evidence.append(
                    f"  {fkey}/{cfg}/seed_{i}: min={min_ep:.6e} max={max_ep:.6e} mean={mean_ep:.6e}"
                )
    results['K1'] = {
        'description': 'Adaptive epsilon bounded (epsilon_min <= epsilon[t] <= epsilon_max)',
        'passed': k1_passed,
        'evidence': '\n'.join(k1_evidence) if k1_evidence else '  No adaptive runs found.',
    }

    # --- K2: Adaptive epsilon changes ---
    k2_passed = False
    k2_votes = 0
    k2_total = 0
    k2_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in adaptive_configs_in_use:
            if cfg not in aggregated.get(fkey, {}):
                continue
            ep_list_list = aggregated[fkey][cfg].get('epsilon_history_list', [])
            for ep_hist in ep_list_list:
                k2_total += 1
                if not ep_hist:
                    continue
                if np.std(ep_hist) > 1e-12:
                    k2_votes += 1
    if k2_total > 0:
        ratio = k2_votes / k2_total
        k2_passed = ratio >= 0.8
        k2_evidence.append(f"  Adaptive runs with std(epsilon) > 1e-12: {k2_votes}/{k2_total} ({ratio*100:.1f}%)")
    else:
        k2_evidence.append("  No adaptive runs to evaluate.")
    results['K2'] = {
        'description': 'Adaptive epsilon varies (std > 1e-12 in >= 80% of adaptive runs)',
        'passed': k2_passed,
        'evidence': '\n'.join(k2_evidence),
    }

    # --- K3: Adaptive differs from Static and Dynamic ---
    k3_passed = False
    k3_votes = 0
    k3_total = 0
    k3_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        for pair_cfg_a, pair_cfg_b in [
            ("QWMO_OrbitalPauli_Adaptive", "QWMO_OrbitalPauli_Static"),
            ("QWMO_OrbitalPauli_Adaptive", "QWMO_OrbitalPauli_Dynamic"),
            ("QWMO_Full_Adaptive", "QWMO_Full_Static"),
            ("QWMO_Full_Adaptive", "QWMO_Full_Dynamic"),
        ]:
            if pair_cfg_a not in configs or pair_cfg_b not in configs:
                continue
            fits_a = aggregated.get(fkey, {}).get(pair_cfg_a, {}).get('fitnesses', [])
            fits_b = aggregated.get(fkey, {}).get(pair_cfg_b, {}).get('fitnesses', [])
            if len(fits_a) == len(fits_b) and len(fits_a) > 0:
                k3_total += 1
                n_diff = sum(1 for x, y in zip(fits_a, fits_b) if x != y)
                if n_diff > 0:
                    k3_votes += 1
                k3_evidence.append(
                    f"  {fkey}: {pair_cfg_a} vs {pair_cfg_b} -> n_different={n_diff}/{len(fits_a)}"
                )
    if k3_total > 0 and k3_votes >= 1:
        k3_passed = True
    results['K3'] = {
        'description': 'Adaptive epsilon differs from Static/Dynamic (final fitness)',
        'passed': k3_passed,
        'evidence': '\n'.join(k3_evidence) if k3_evidence else '  No comparable configs found.',
    }

    # --- K4: Adaptive Pauli active ---
    k4_passed = False
    k4_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in adaptive_configs_in_use:
            if cfg not in aggregated.get(fkey, {}):
                continue
            disp_total = sum(
                sum(run) for run in aggregated[fkey][cfg].get('pauli_displacement_history_list', [])
            )
            k4_evidence.append(f"  {fkey}/{cfg}: total displacements = {disp_total}")
            if disp_total > 0:
                k4_passed = True
    results['K4'] = {
        'description': 'Adaptive Pauli active (total displacement > 0 in every function)',
        'passed': k4_passed,
        'evidence': '\n'.join(k4_evidence) if k4_evidence else '  No adaptive Pauli configs found.',
    }

    # --- K5: Collision efficiency reportable ---
    k5_passed = True
    k5_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in pauli_configs_in_use:
            if cfg not in aggregated.get(fkey, {}):
                continue
            coll_list = aggregated[fkey][cfg].get('pauli_collision_history_list', [])
            disp_list = aggregated[fkey][cfg].get('pauli_displacement_history_list', [])
            succ_list = aggregated[fkey][cfg].get('pauli_success_history_list', [])
            total_coll = sum(sum(run) for run in coll_list)
            total_disp = sum(sum(run) for run in disp_list)
            total_succ = sum(sum(run) for run in succ_list)
            CER = total_succ / max(total_coll, 1)
            DER = total_disp / max(total_coll, 1)
            SER = total_succ / max(total_disp, 1)
            k5_evidence.append(
                f"  {fkey}/{cfg}: CER={CER:.4f} DER={DER:.4f} SER={SER:.4f} "
                f"(coll={total_coll} disp={total_disp} succ={total_succ})"
            )
    results['K5'] = {
        'description': 'Collision efficiency ratios (CER, DER, SER) reportable',
        'passed': k5_passed,
        'evidence': '\n'.join(k5_evidence) if k5_evidence else '  No Pauli configs found.',
    }

    # --- K6: Full_Adaptive performance signal ---
    k6_passed = False
    k6_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        fa_mean = aggregated.get(fkey, {}).get('QWMO_Full_Adaptive', {}).get('mean')
        fs_mean = aggregated.get(fkey, {}).get('QWMO_Full_Static', {}).get('mean')
        fd_mean = aggregated.get(fkey, {}).get('QWMO_Full_Dynamic', {}).get('mean')
        if fa_mean is not None and fs_mean is not None and fd_mean is not None:
            best_other = min(fs_mean, fd_mean)
            if fa_mean <= best_other:
                k6_passed = True
            k6_evidence.append(
                f"  {fkey}: Full_Adaptive={fa_mean:.4e} Full_Static={fs_mean:.4e} "
                f"Full_Dynamic={fd_mean:.4e} -> {'PASS' if fa_mean <= best_other else 'FAIL'}"
            )
        else:
            k6_evidence.append(f"  {fkey}: insufficient data for Full_Adaptive comparison")
    results['K6'] = {
        'description': 'Full_Adaptive <= min(Full_Static, Full_Dynamic) in at least one function',
        'passed': k6_passed,
        'evidence': '\n'.join(k6_evidence),
    }

    # --- K7: OrbitalPauli_Adaptive performance signal ---
    k7_passed = False
    k7_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        opa_mean = aggregated.get(fkey, {}).get('QWMO_OrbitalPauli_Adaptive', {}).get('mean')
        oo_mean = aggregated.get(fkey, {}).get('QWMO_OrbitalOnly', {}).get('mean')
        if opa_mean is not None and oo_mean is not None:
            if opa_mean <= oo_mean:
                k7_passed = True
            k7_evidence.append(
                f"  {fkey}: OrbitalPauli_Adaptive={opa_mean:.4e} OrbitalOnly={oo_mean:.4e} "
                f"-> {'PASS' if opa_mean <= oo_mean else 'FAIL'}"
            )
        else:
            k7_evidence.append(f"  {fkey}: insufficient data for OrbitalPauli_Adaptive comparison")
    results['K7'] = {
        'description': 'OrbitalPauli_Adaptive <= OrbitalOnly in at least one function',
        'passed': k7_passed,
        'evidence': '\n'.join(k7_evidence),
    }

    # --- K8: FE budget respected ---
    k8_passed = True
    k8_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in configs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            fes_list = aggregated[fkey][cfg].get('fes_count_list', [])
            for i, fes in enumerate(fes_list):
                if fes > max_fes:
                    k8_passed = False
                    k8_evidence.append(f"  {fkey}/{cfg}/seed_{i}: fes={fes} > max_fes={max_fes}")
                elif fes < 0.98 * max_fes:
                    k8_evidence.append(f"  WARN {fkey}/{cfg}/seed_{i}: fes={fes} < 0.98*max_fes")
    results['K8'] = {
        'description': f'FE budget respected (fes_count <= {max_fes})',
        'passed': k8_passed,
        'evidence': '\n'.join(k8_evidence) if k8_evidence else f'  All runs within budget (max_fes={max_fes})',
    }

    # --- K9: Diversity and epsilon both saved ---
    k9_passed = True
    k9_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in adaptive_configs_in_use:
            if cfg not in aggregated.get(fkey, {}):
                continue
            div_list = aggregated[fkey][cfg].get('diversity_history_list', [])
            ep_list = aggregated[fkey][cfg].get('epsilon_history_list', [])
            for i, (div, ep) in enumerate(zip(div_list, ep_list)):
                if not div:
                    k9_passed = False
                    k9_evidence.append(f"  {fkey}/{cfg}/seed_{i}: diversity_history empty")
                if not ep:
                    k9_passed = False
                    k9_evidence.append(f"  {fkey}/{cfg}/seed_{i}: epsilon_history empty")
                if div and ep:
                    k9_evidence.append(f"  {fkey}/{cfg}/seed_{i}: diversity={len(div)} eps_len={len(ep)} OK")
    results['K9'] = {
        'description': 'Diversity and epsilon history saved for all adaptive runs',
        'passed': k9_passed,
        'evidence': '\n'.join(k9_evidence) if k9_evidence else '  No adaptive runs to check.',
    }

    return results


def write_report(aggregated, criteria, output_path, funcs, configs):
    lines = []
    lines.append('# QWMO-GAPR Pilot Validation Report')
    lines.append('')
    lines.append(f'**Functions:** {funcs}  ')
    lines.append(f'**Configs:** {len(configs)} ({", ".join(configs)})  ')
    lines.append(f'**Seeds:** {len(configs)} (1-10)  ')
    lines.append(f'**Dimension:** 30  ')
    lines.append(f'**Max FEs:** 300,000  ')
    lines.append(f'**Adaptive params:** k=3, lambda0=0.75, eps_max_ratio=0.15, eps_min_ratio=0.01')
    lines.append('')

    lines.append('## Pass/Fail Summary')
    lines.append('')
    all_passed = True
    for kid in ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9']:
        c = criteria[kid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        if not c['passed']:
            all_passed = False
        lines.append(f'- **{kid}** [{mark}] {c["description"]}')
    lines.append('')
    lines.append(f'**Overall:** {"ALL PASS" if all_passed else "REGESSION — see details"}')
    lines.append('')

    for kid in ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9']:
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

    lines.append('## Epsilon Statistics')
    lines.append('')
    lines.append('| Function | Config | min_eps | max_eps | mean_eps | std_eps |')
    lines.append('|---|---|---|---|---|---|')
    adaptive_cfgs = ['QWMO_OrbitalPauli_Adaptive', 'QWMO_Full_Adaptive']
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in adaptive_cfgs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            ep_list_list = aggregated[fkey][cfg].get('epsilon_history_list', [])
            all_eps = [e for hist in ep_list_list for e in hist]
            if all_eps:
                lines.append(
                    f'| F{fid} | {cfg} | {min(all_eps):.4e} | {max(all_eps):.4e} | '
                    f'{np.mean(all_eps):.4e} | {np.std(all_eps):.4e} |'
                )
    lines.append('')

    lines.append('## Pauli Mechanism Statistics')
    lines.append('')
    lines.append('| Function | Config | Collisions | Displacements | Successes | CER | DER | SER |')
    lines.append('|---|---|---|---|---|---|---|---|')
    pauli_cfgs = [
        'QWMO_OrbitalPauli_Static', 'QWMO_OrbitalPauli_Dynamic',
        'QWMO_OrbitalPauli_Adaptive', 'QWMO_Full_Static',
        'QWMO_Full_Dynamic', 'QWMO_Full_Adaptive',
    ]
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in pauli_cfgs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            coll = sum(sum(run) for run in aggregated[fkey][cfg].get('pauli_collision_history_list', []))
            disp = sum(sum(run) for run in aggregated[fkey][cfg].get('pauli_displacement_history_list', []))
            succ = sum(sum(run) for run in aggregated[fkey][cfg].get('pauli_success_history_list', []))
            CER = succ / max(coll, 1)
            DER = disp / max(coll, 1)
            SER = succ / max(disp, 1)
            lines.append(
                f'| F{fid} | {cfg} | {coll} | {disp} | {succ} | {CER:.4f} | {DER:.4f} | {SER:.4f} |'
            )
    lines.append('')

    lines.append('## Escape Statistics')
    lines.append('')
    lines.append('| Function | Config | Attempts | Executed | Successes | Succ/Exec | Mean Delta |')
    lines.append('|---|---|---|---|---|---|---|')
    escape_cfgs = ['QWMO_OrbitalEscape', 'QWMO_Full_Static', 'QWMO_Full_Dynamic', 'QWMO_Full_Adaptive']
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in escape_cfgs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            attempts = sum(sum(run) for run in aggregated[fkey][cfg].get('escape_attempt_history_list', []))
            executed = sum(sum(run) for run in aggregated[fkey][cfg].get('escape_executed_history_list', []))
            successes = sum(sum(run) for run in aggregated[fkey][cfg].get('escape_success_history_list', []))
            mean_delta = np.mean(
                [d for hist in aggregated[fkey][cfg].get('escape_delta_history_list', []) for d in hist]
            ) if executed > 0 else 0.0
            ratio = successes / max(executed, 1)
            lines.append(
                f'| F{fid} | {cfg} | {attempts} | {executed} | {successes} | {ratio:.4f} | {mean_delta:.4e} |'
            )
    lines.append('')

    lines.append('## Interpretation')
    lines.append('')
    k1_pass = criteria['K1']['passed']
    k2_pass = criteria['K2']['passed']
    k3_pass = criteria['K3']['passed']
    k4_pass = criteria['K4']['passed']
    k5_pass = criteria['K5']['passed']
    k6_pass = criteria['K6']['passed']
    k8_pass = criteria['K8']['passed']
    if k1_pass and k2_pass and k3_pass and k4_pass and k5_pass and k8_pass:
        if k6_pass:
            lines.append('**Outcome A — Strong success:** Full_Adaptive passed K6. '
                         'GAPR can be promoted to the main Phase-1 experiment.')
        else:
            lines.append('**Outcome B — Mechanism works, performance mixed:** '
                         'GAPR is reportable as a mechanism study.')
    else:
        lines.append('**Outcome C — Needs review:** Some mechanism criteria failed. '
                     'See details above.')
    lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"\nSaved GAPR pilot report to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='QWMO-GAPR Pilot Validation')
    parser.add_argument('--max-workers', type=int, default=None)
    parser.add_argument('--output-dir', type=str, default=None)
    args = parser.parse_args()

    config = dict(GAPR_PILOT_CONFIG)
    if args.output_dir:
        config['output_dir'] = args.output_dir

    aggregated, json_path = run_pilot(config, max_workers=args.max_workers)
    criteria = check_criteria(
        aggregated, config['functions'], config['ablation_configs'],
        max_fes=config['max_fes']
    )
    report_path = os.path.join(config['output_dir'], config['report_name'])
    write_report(aggregated, criteria, report_path, config['functions'], config['ablation_configs'])

    print('\n=== GAPR PILOT PASS/FAIL ===')
    for kid in ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9']:
        c = criteria[kid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        print(f'  {kid}: {mark} - {c["description"]}')


if __name__ == '__main__':
    main()
