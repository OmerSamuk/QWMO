"""QWMO-GAPR Comprehensive Pilot v1.0 Runner.

Implements the comprehensive pilot specified in `gapr-todolist.md`:
- 5 functions: F5, F10, F15, F20, F23
- 15 seeds (1..15)
- 30D, 300k FE
- 8 ablation configs (including QWMO_OrbitalPauli_GAPR and QWMO_Full_GAPR)
- Go/No-Go criteria G1-G5
- Validation V1-V4 + epsilon saturation ratio
- Three reports: pilot_report.md, validation_report.md, pilot_decision.md
- Per-seed CSV: pilot_summary.csv (Function x Config x Seed = 5 x 8 x 15 = 600 rows)

Usage:
    python experiments/gapr_comprehensive_pilot.py [--max-workers N] [--output-dir DIR]
"""

import os
import sys
import csv
import json
import argparse
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.config import GAPR_COMPREHENSIVE_PILOT_CONFIG
from experiments.runner import ExperimentRunner, ALGO_TO_QWMO_CONFIG

GAPR_CONFIGS = [
    "QWMO_OrbitalPauli_GAPR",
    "QWMO_Full_GAPR",
]
PAULI_CONFIGS = [
    "QWMO_OrbitalPauli_Static",
    "QWMO_OrbitalPauli_Dynamic",
    "QWMO_OrbitalPauli_GAPR",
    "QWMO_Full_Static",
    "QWMO_Full_Dynamic",
    "QWMO_Full_GAPR",
]
ESCAPE_CONFIGS = [
    "QWMO_OrbitalEscape",
    "QWMO_Full_Static",
    "QWMO_Full_Dynamic",
    "QWMO_Full_GAPR",
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
    print(f"GAPR Comprehensive Pilot v1.0: funcs={funcs} dim={dim} pop={pop} "
          f"max_fes={max_fes} seeds={seeds[0]}-{seeds[-1]} "
          f"configs={len(configs)} workers={n_workers}")

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
                    completed += 1
                    print(f"  [{completed}/{total}] F{fid} | {cfg} | seed={seed}: FAILED")
            except Exception as e:
                completed += 1
                print(f"  [{completed}/{total}] F{fid} | {cfg} | seed={seed}: ERROR {e}")

    aggregated = _aggregate_results(raw_results)

    json_path = os.path.join(output_dir, config['json_name'])
    with open(json_path, 'w') as f:
        json.dump(aggregated, f, indent=2, default=str)
    print(f"\nSaved pilot results to {json_path}")

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
                'seeds': [r['seed'] for r in runs],
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


def _per_seed_pauli_metrics(aggregated, funcs, pauli_configs):
    """Compute per-seed CER/DER/SER for each (function, config, seed)."""
    rows = {}
    for fid in funcs:
        fkey = f'F{fid}'
        rows[fkey] = {}
        for cfg in pauli_configs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            entry = aggregated[fkey][cfg]
            seeds = entry.get('seeds', list(range(len(entry.get('fitnesses', [])))))
            seed_metrics = []
            coll_list = entry.get('pauli_collision_history_list', [])
            disp_list = entry.get('pauli_displacement_history_list', [])
            succ_list = entry.get('pauli_success_history_list', [])
            for i, seed in enumerate(seeds):
                coll = int(sum(coll_list[i])) if i < len(coll_list) else 0
                disp = int(sum(disp_list[i])) if i < len(disp_list) else 0
                succ = int(sum(succ_list[i])) if i < len(succ_list) else 0
                CER = succ / max(coll, 1)
                DER = disp / max(coll, 1)
                SER = succ / max(disp, 1)
                seed_metrics.append({
                    'seed': int(seed),
                    'coll': coll, 'disp': disp, 'succ': succ,
                    'CER': CER, 'DER': DER, 'SER': SER,
                })
            rows[fkey][cfg] = seed_metrics
    return rows


def check_criteria(aggregated, funcs, configs, search_range=200,
                   epsilon_min_ratio=0.01, adaptive_epsilon_max_ratio=0.15,
                   competitive_ratio=1.05, g2_min_functions=4, g4_min_functions=3,
                   g5_min_functions=3):
    results = {}
    gapr_cfgs = [c for c in GAPR_CONFIGS if c in configs]
    pauli_cfgs = [c for c in PAULI_CONFIGS if c in configs]
    escape_cfgs = [c for c in ESCAPE_CONFIGS if c in configs]

    eps_min = epsilon_min_ratio * search_range
    eps_max = adaptive_epsilon_max_ratio * search_range

    # --- G1: Adaptive epsilon truly varies ---
    g1_passed = True
    g1_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in gapr_cfgs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            ep_list_list = aggregated[fkey][cfg].get('epsilon_history_list', [])
            for i, ep_hist in enumerate(ep_list_list):
                if not ep_hist:
                    g1_passed = False
                    g1_evidence.append(f"  {fkey}/{cfg}/seed_{i}: FAIL (epsilon_history empty)")
                    continue
                std_ep = float(np.std(ep_hist))
                if std_ep > 1e-12:
                    g1_evidence.append(
                        f"  {fkey}/{cfg}/seed_{i}: PASS (std={std_ep:.4e})"
                    )
                else:
                    g1_passed = False
                    g1_evidence.append(
                        f"  {fkey}/{cfg}/seed_{i}: FAIL (std={std_ep:.4e} <= 1e-12)"
                    )
    results['G1'] = {
        'description': 'Adaptive epsilon varies (std(epsilon) > 0 in every adaptive run)',
        'passed': g1_passed,
        'evidence': '\n'.join(g1_evidence) if g1_evidence else '  No adaptive runs found.',
    }

    # --- G2: Pauli active in >= g2_min_functions functions ---
    g2_per_function = {}
    for fid in funcs:
        fkey = f'F{fid}'
        f_passed = False
        per_cfg = []
        for cfg in gapr_cfgs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            coll_total = sum(
                sum(run) for run in aggregated[fkey][cfg].get('pauli_collision_history_list', [])
            )
            disp_total = sum(
                sum(run) for run in aggregated[fkey][cfg].get('pauli_displacement_history_list', [])
            )
            per_cfg.append((cfg, coll_total, disp_total))
            if coll_total > 0 and disp_total > 0:
                f_passed = True
        g2_per_function[fkey] = (f_passed, per_cfg)
    g2_passed_functions = sum(1 for v in g2_per_function.values() if v[0])
    g2_passed = g2_passed_functions >= g2_min_functions
    g2_evidence = []
    for fkey, (passed, per_cfg) in g2_per_function.items():
        cfg_lines = ', '.join(f'{c} coll={cc} disp={dd}' for c, cc, dd in per_cfg)
        g2_evidence.append(f"  {fkey}: {'PASS' if passed else 'FAIL'} ({cfg_lines})")
    g2_evidence.append(
        f"  Functions with active Pauli: {g2_passed_functions}/{len(g2_per_function)} "
        f"(required >= {g2_min_functions})"
    )
    results['G2'] = {
        'description': (
            f'Pauli active in at least {g2_min_functions}/{len(funcs)} functions '
            f'(collision > 0 AND displacement > 0 in any adaptive config)'
        ),
        'passed': g2_passed,
        'evidence': '\n'.join(g2_evidence),
    }

    # --- G3: SER_GAPR > SER_Static in >= 3 functions ---
    g3_passed_functions = 0
    g3_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        opa_means = _aggregate_pauli_ser(aggregated, fkey, 'QWMO_OrbitalPauli_GAPR')
        ops_means = _aggregate_pauli_ser(aggregated, fkey, 'QWMO_OrbitalPauli_Static')
        if opa_means is not None and ops_means is not None:
            if opa_means > ops_means:
                g3_passed_functions += 1
                g3_evidence.append(
                    f"  {fkey}: OrbitalPauli_GAPR SER={opa_means:.4f} > "
                    f"OrbitalPauli_Static SER={ops_means:.4f} -> PASS"
                )
            else:
                g3_evidence.append(
                    f"  {fkey}: OrbitalPauli_GAPR SER={opa_means:.4f} <= "
                    f"OrbitalPauli_Static SER={ops_means:.4f} -> FAIL"
                )
        else:
            g3_evidence.append(f"  {fkey}: insufficient data for SER comparison")
    g3_passed = g3_passed_functions >= 3
    g3_evidence.append(
        f"  Functions where SER_GAPR > SER_Static: "
        f"{g3_passed_functions}/{len(funcs)} (required >= 3)"
    )
    results['G3'] = {
        'description': 'SER_GAPR > SER_Static in at least 3 functions',
        'passed': g3_passed,
        'evidence': '\n'.join(g3_evidence),
    }

    # --- G4: Full_GAPR competitive in >= g4_min_functions functions ---
    g4_passed_functions = 0
    g4_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        fg = aggregated.get(fkey, {}).get('QWMO_Full_GAPR', {}).get('mean')
        fs = aggregated.get(fkey, {}).get('QWMO_Full_Static', {}).get('mean')
        fd = aggregated.get(fkey, {}).get('QWMO_Full_Dynamic', {}).get('mean')
        if fg is not None and fs is not None and fd is not None:
            best_other = min(fs, fd)
            threshold = competitive_ratio * best_other
            if fg <= threshold:
                g4_passed_functions += 1
                g4_evidence.append(
                    f"  {fkey}: Full_GAPR={fg:.4e} <= {competitive_ratio}*"
                    f"min({fs:.4e},{fd:.4e})={threshold:.4e} -> PASS"
                )
            else:
                g4_evidence.append(
                    f"  {fkey}: Full_GAPR={fg:.4e} > {competitive_ratio}*"
                    f"min({fs:.4e},{fd:.4e})={threshold:.4e} -> FAIL"
                )
        else:
            g4_evidence.append(f"  {fkey}: insufficient data for Full_GAPR comparison")
    g4_passed = g4_passed_functions >= g4_min_functions
    g4_evidence.append(
        f"  Functions where Full_GAPR <= {competitive_ratio}*min(Full_Static, Full_Dynamic): "
        f"{g4_passed_functions}/{len(funcs)} (required >= {g4_min_functions})"
    )
    results['G4'] = {
        'description': (
            f'Full_GAPR competitive in at least {g4_min_functions}/{len(funcs)} functions '
            f'(mean(Full_GAPR) <= {competitive_ratio} * min(Full_Static, Full_Dynamic))'
        ),
        'passed': g4_passed,
        'evidence': '\n'.join(g4_evidence),
    }

    # --- G5: Pauli evolution ranking in >= g5_min_functions functions ---
    # In each function: OrbitalPauli_GAPR > Dynamic > Static on (collision, displacement, SER)
    g5_passed_functions = 0
    g5_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        gapr = _aggregate_pauli_totals(aggregated, fkey, 'QWMO_OrbitalPauli_GAPR')
        dyn = _aggregate_pauli_totals(aggregated, fkey, 'QWMO_OrbitalPauli_Dynamic')
        sta = _aggregate_pauli_totals(aggregated, fkey, 'QWMO_OrbitalPauli_Static')
        if gapr and dyn and sta:
            ranking_ok = (gapr['coll'] > dyn['coll'] > sta['coll']
                          and gapr['disp'] > dyn['disp'] > sta['disp']
                          and gapr['SER'] > dyn['SER'] > sta['SER'])
            if ranking_ok:
                g5_passed_functions += 1
                g5_evidence.append(
                    f"  {fkey}: coll({sta['coll']}<{dyn['coll']}<{gapr['coll']}) "
                    f"disp({sta['disp']}<{dyn['disp']}<{gapr['disp']}) "
                    f"SER({sta['SER']:.4f}<{dyn['SER']:.4f}<{gapr['SER']:.4f}) -> PASS"
                )
            else:
                g5_evidence.append(
                    f"  {fkey}: STA coll={sta['coll']} disp={sta['disp']} SER={sta['SER']:.4f}; "
                    f"DYN coll={dyn['coll']} disp={dyn['disp']} SER={dyn['SER']:.4f}; "
                    f"GAPR coll={gapr['coll']} disp={gapr['disp']} SER={gapr['SER']:.4f} -> FAIL"
                )
        else:
            g5_evidence.append(f"  {fkey}: insufficient data for Pauli evolution ranking")
    g5_passed = g5_passed_functions >= g5_min_functions
    g5_evidence.append(
        f"  Functions with Pauli ranking Static < Dynamic < GAPR on all three metrics: "
        f"{g5_passed_functions}/{len(funcs)} (required >= {g5_min_functions})"
    )
    results['G5'] = {
        'description': (
            f'Pauli evolution Static < Dynamic < GAPR in at least '
            f'{g5_min_functions}/{len(funcs)} functions (coll, disp, SER)'
        ),
        'passed': g5_passed,
        'evidence': '\n'.join(g5_evidence),
    }

    return results


def _aggregate_pauli_totals(aggregated, fkey, cfg):
    if cfg not in aggregated.get(fkey, {}):
        return None
    entry = aggregated[fkey][cfg]
    coll = sum(sum(run) for run in entry.get('pauli_collision_history_list', []))
    disp = sum(sum(run) for run in entry.get('pauli_displacement_history_list', []))
    succ = sum(sum(run) for run in entry.get('pauli_success_history_list', []))
    SER = succ / max(disp, 1)
    return {'coll': coll, 'disp': disp, 'succ': succ, 'SER': SER}


def _aggregate_pauli_ser(aggregated, fkey, cfg):
    totals = _aggregate_pauli_totals(aggregated, fkey, cfg)
    return totals['SER'] if totals else None


def check_validation(aggregated, funcs, configs, search_range=200,
                     epsilon_min_ratio=0.01, adaptive_epsilon_max_ratio=0.15):
    results = {}
    gapr_cfgs = [c for c in GAPR_CONFIGS if c in configs]

    eps_min = epsilon_min_ratio * search_range
    eps_max = adaptive_epsilon_max_ratio * search_range

    v_passed = {k: True for k in ['V1', 'V2', 'V3', 'V4']}
    v_evidence = {k: [] for k in ['V1', 'V2', 'V3', 'V4']}
    sat_max_ratios = []
    sat_min_ratios = []

    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in gapr_cfgs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            ep_list_list = aggregated[fkey][cfg].get('epsilon_history_list', [])
            for i, ep_hist in enumerate(ep_list_list):
                if not ep_hist:
                    v_passed['V1'] = False
                    v_evidence['V1'].append(
                        f"  {fkey}/{cfg}/seed_{i}: FAIL (empty)"
                    )
                    continue
                ep_arr = np.asarray(ep_hist, dtype=float)
                std_ep = float(np.std(ep_arr))
                min_ep = float(np.min(ep_arr))
                max_ep = float(np.max(ep_arr))
                uniq_ep = len(np.unique(np.round(ep_arr, 9)))

                if std_ep > 1e-12:
                    v_evidence['V1'].append(
                        f"  {fkey}/{cfg}/seed_{i}: PASS (std={std_ep:.4e})"
                    )
                else:
                    v_passed['V1'] = False
                    v_evidence['V1'].append(
                        f"  {fkey}/{cfg}/seed_{i}: FAIL (std={std_ep:.4e})"
                    )

                if min_ep >= eps_min - 1e-9:
                    v_evidence['V2'].append(
                        f"  {fkey}/{cfg}/seed_{i}: PASS (min={min_ep:.4e} >= {eps_min:.4e})"
                    )
                else:
                    v_passed['V2'] = False
                    v_evidence['V2'].append(
                        f"  {fkey}/{cfg}/seed_{i}: FAIL (min={min_ep:.4e} < {eps_min:.4e})"
                    )

                if max_ep <= eps_max + 1e-9:
                    v_evidence['V3'].append(
                        f"  {fkey}/{cfg}/seed_{i}: PASS (max={max_ep:.4e} <= {eps_max:.4e})"
                    )
                else:
                    v_passed['V3'] = False
                    v_evidence['V3'].append(
                        f"  {fkey}/{cfg}/seed_{i}: FAIL (max={max_ep:.4e} > {eps_max:.4e})"
                    )

                if uniq_ep > 5:
                    v_evidence['V4'].append(
                        f"  {fkey}/{cfg}/seed_{i}: PASS (unique={uniq_ep})"
                    )
                else:
                    v_passed['V4'] = False
                    v_evidence['V4'].append(
                        f"  {fkey}/{cfg}/seed_{i}: FAIL (unique={uniq_ep})"
                    )

                # Saturation ratios
                tol = 1e-9
                n = len(ep_arr)
                n_at_max = int(np.sum(ep_arr >= eps_max - tol))
                n_at_min = int(np.sum(ep_arr <= eps_min + tol))
                sat_max = n_at_max / n
                sat_min = n_at_min / n
                sat_max_ratios.append({
                    'fkey': fkey, 'cfg': cfg, 'seed': i,
                    'ratio': sat_max, 'flag': _saturation_flag(sat_max),
                })
                sat_min_ratios.append({
                    'fkey': fkey, 'cfg': cfg, 'seed': i,
                    'ratio': sat_min, 'flag': _saturation_flag(sat_min),
                })

    for k in ['V1', 'V2', 'V3', 'V4']:
        results[k] = {
            'description': {
                'V1': 'std(epsilon_history) > 0',
                'V2': 'min(epsilon_history) >= eps_min',
                'V3': 'max(epsilon_history) <= eps_max',
                'V4': 'unique(epsilon_history) > 5',
            }[k],
            'passed': v_passed[k],
            'evidence': '\n'.join(v_evidence[k]) if v_evidence[k] else '  No adaptive runs found.',
        }
    results['sat_max_ratios'] = sat_max_ratios
    results['sat_min_ratios'] = sat_min_ratios
    return results


def _saturation_flag(ratio):
    if ratio > 0.5:
        return 'RED'
    if ratio > 0.2:
        return 'YELLOW'
    return 'GREEN'


def write_pilot_report(aggregated, criteria, output_path, funcs, configs):
    lines = []
    lines.append('# QWMO-GAPR Comprehensive Pilot v1.0 Report')
    lines.append('')
    lines.append(f'**Functions:** {funcs}  ')
    lines.append(f'**Configs:** {len(configs)} ({", ".join(configs)})  ')
    lines.append(f'**Seeds:** 15 (1-15)  ')
    lines.append(f'**Dimension:** 30  ')
    lines.append(f'**Max FEs:** 300,000  ')
    lines.append(f'**Adaptive params:** k=3, lambda0=0.75, eps_max_ratio=0.15, eps_min_ratio=0.01')
    lines.append('')

    lines.append('## Go/No-Go Summary (G1-G5)')
    lines.append('')
    all_passed = True
    for gid in ['G1', 'G2', 'G3', 'G4', 'G5']:
        c = criteria[gid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        if not c['passed']:
            all_passed = False
        lines.append(f'- **{gid}** [{mark}] {c["description"]}')
    lines.append('')
    lines.append(f'**Overall Go/No-Go:** {"ALL PASS" if all_passed else "REGRESSION — see details"}')
    lines.append('')

    for gid in ['G1', 'G2', 'G3', 'G4', 'G5']:
        c = criteria[gid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        lines.append(f'## {gid}: {c["description"]}')
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

    lines.append('## Epsilon Statistics (Adaptive only)')
    lines.append('')
    lines.append('| Function | Config | min_eps | max_eps | mean_eps | std_eps |')
    lines.append('|---|---|---|---|---|---|')
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in GAPR_CONFIGS:
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
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in PAULI_CONFIGS:
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
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in ESCAPE_CONFIGS:
            if cfg not in aggregated.get(fkey, {}):
                continue
            attempts = sum(sum(run) for run in aggregated[fkey][cfg].get('escape_attempt_history_list', []))
            executed = sum(sum(run) for run in aggregated[fkey][cfg].get('escape_executed_history_list', []))
            successes = sum(sum(run) for run in aggregated[fkey][cfg].get('escape_success_history_list', []))
            deltas = [d for hist in aggregated[fkey][cfg].get('escape_delta_history_list', []) for d in hist]
            mean_delta = float(np.mean(deltas)) if deltas else 0.0
            ratio = successes / max(executed, 1)
            lines.append(
                f'| F{fid} | {cfg} | {attempts} | {executed} | {successes} | {ratio:.4f} | {mean_delta:.4e} |'
            )
    lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Saved pilot report to {output_path}")


def write_validation_report(aggregated, validation, output_path, funcs, configs,
                            search_range=200, epsilon_min_ratio=0.01,
                            adaptive_epsilon_max_ratio=0.15):
    eps_min = epsilon_min_ratio * search_range
    eps_max = adaptive_epsilon_max_ratio * search_range

    lines = []
    lines.append('# QWMO-GAPR Comprehensive Pilot v1.0 Validation Report')
    lines.append('')
    lines.append(f'**Functions:** {funcs}  ')
    lines.append(f'**Eps bounds:** min={eps_min:.4e}, max={eps_max:.4e}  ')
    lines.append(f'**Tolerance:** 1e-9  ')
    lines.append('')

    lines.append('## V1-V4 Summary')
    lines.append('')
    for k in ['V1', 'V2', 'V3', 'V4']:
        v = validation[k]
        mark = 'PASS' if v['passed'] else 'FAIL'
        lines.append(f'- **{k}** [{mark}] {v["description"]}')
    lines.append('')

    for k in ['V1', 'V2', 'V3', 'V4']:
        v = validation[k]
        mark = 'PASS' if v['passed'] else 'FAIL'
        lines.append(f'## {k}: {v["description"]}')
        lines.append(f'**Result:** {mark}')
        lines.append('')
        lines.append('```')
        lines.append(v['evidence'])
        lines.append('```')
        lines.append('')

    # Epsilon aggregate statistics
    lines.append('## Epsilon Aggregate Statistics')
    lines.append('')
    lines.append('| Function | Config | eps_min | eps_max | eps_mean | eps_std | unique_count |')
    lines.append('|---|---|---|---|---|---|---|')
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in GAPR_CONFIGS:
            if cfg not in aggregated.get(fkey, {}):
                continue
            ep_list_list = aggregated[fkey][cfg].get('epsilon_history_list', [])
            all_eps = [e for hist in ep_list_list for e in hist]
            if all_eps:
                arr = np.asarray(all_eps, dtype=float)
                lines.append(
                    f'| F{fid} | {cfg} | {np.min(arr):.4e} | {np.max(arr):.4e} | '
                    f'{np.mean(arr):.4e} | {np.std(arr):.4e} | '
                    f'{len(np.unique(np.round(arr, 9)))} |'
                )
    lines.append('')

    # mean_knn and normalized_knn estimated from epsilon histories
    # eps = clip(0.75 * mean_knn / L_max * (u-l), eps_min, eps_max)
    # L_max = sqrt(D) * (u-l) ; un-clipped: mean_knn = eps * L_max / (0.75 * (u-l))
    lines.append('## Mean kNN & Normalized kNN (estimated from epsilon history)')
    lines.append('')
    lines.append('| Function | Config | mean_knn (avg) | normalized_knn (avg) |')
    lines.append('|---|---|---|---|')
    D = 30
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in GAPR_CONFIGS:
            if cfg not in aggregated.get(fkey, {}):
                continue
            ep_list_list = aggregated[fkey][cfg].get('epsilon_history_list', [])
            mean_knn_estimates = []
            for hist in ep_list_list:
                if not hist:
                    continue
                arr = np.asarray(hist, dtype=float)
                inside_clip = (arr > eps_min + 1e-9) & (arr < eps_max - 1e-9)
                if not np.any(inside_clip):
                    continue
                clipped_eps = arr[inside_clip]
                knn = clipped_eps * np.sqrt(D) * search_range / (0.75 * search_range)
                mean_knn_estimates.append(float(np.mean(knn)))
            if mean_knn_estimates:
                mk = float(np.mean(mean_knn_estimates))
                lines.append(
                    f'| F{fid} | {cfg} | {mk:.4e} | {mk / (np.sqrt(D) * search_range):.6f} |'
                )
    lines.append('')

    # Saturation ratios
    sat_max = validation.get('sat_max_ratios', [])
    sat_min = validation.get('sat_min_ratios', [])

    lines.append('## Epsilon Saturation Ratios')
    lines.append('')
    lines.append('Threshold legend: GREEN < 0.2, 0.2 <= YELLOW <= 0.5, RED > 0.5')
    lines.append('')
    lines.append('### Saturation at eps_max')
    lines.append('')
    lines.append('| Function | Config | Seed | ratio | flag |')
    lines.append('|---|---|---|---|---|')
    for r in sat_max:
        lines.append(
            f'| {r["fkey"]} | {r["cfg"]} | {r["seed"]} | {r["ratio"]:.4f} | {r["flag"]} |'
        )
    lines.append('')
    lines.append('### Saturation at eps_min')
    lines.append('')
    lines.append('| Function | Config | Seed | ratio | flag |')
    lines.append('|---|---|---|---|---|')
    for r in sat_min:
        lines.append(
            f'| {r["fkey"]} | {r["cfg"]} | {r["seed"]} | {r["ratio"]:.4f} | {r["flag"]} |'
        )
    lines.append('')

    # Pauli totals
    lines.append('## Pauli Totals (aggregated across seeds)')
    lines.append('')
    lines.append('| Function | Config | collisions | displacements | successes |')
    lines.append('|---|---|---|---|---|')
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in PAULI_CONFIGS:
            if cfg not in aggregated.get(fkey, {}):
                continue
            coll = sum(sum(run) for run in aggregated[fkey][cfg].get('pauli_collision_history_list', []))
            disp = sum(sum(run) for run in aggregated[fkey][cfg].get('pauli_displacement_history_list', []))
            succ = sum(sum(run) for run in aggregated[fkey][cfg].get('pauli_success_history_list', []))
            lines.append(f'| F{fid} | {cfg} | {coll} | {disp} | {succ} |')
    lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Saved validation report to {output_path}")


def write_decision(criteria, output_path):
    lines = []
    lines.append('# QWMO-GAPR Comprehensive Pilot v1.0 Decision')
    lines.append('')
    lines.append('## Go/No-Go Results')
    lines.append('')
    for gid in ['G1', 'G2', 'G3', 'G4', 'G5']:
        c = criteria[gid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        lines.append(f'- **{gid}** [{mark}] {c["description"]}')
    lines.append('')

    g1 = criteria['G1']['passed']
    g2 = criteria['G2']['passed']
    g3 = criteria['G3']['passed']
    g4 = criteria['G4']['passed']
    g5 = criteria['G5']['passed']

    if g1 and g2 and g3 and g4 and g5:
        decision = 'A'
        decision_text = (
            'A = Full Benchmark. Tüm G1-G5 kriterleri geçti. '
            'QWMO-GAPR full benchmark ve makale aşamasına geçebilir.'
        )
    elif g1 and g2 and g3:
        decision = 'B'
        decision_text = (
            'B = Mechanism Paper. GAPR mekanizması çalışıyor ancak performans '
            'sinyali karışık. Mekanizma analizi olarak yayınlanabilir.'
        )
    elif not g2 or not g1:
        decision = 'D'
        decision_text = (
            'D = Stop. Adaptif epsilon adaptif davranmadı veya Pauli aktif değil. '
            'Yeni araştırma yönü (ör. Adaptive Collision Epsilon) değerlendirilmeli.'
        )
    else:
        decision = 'C'
        decision_text = (
            'C = Formula Revision. GAPR formülü gözden geçirilmeli, '
            'mekanizma üzerinde ek çalışma gerekli.'
        )

    lines.append('## FINAL DECISION')
    lines.append('')
    lines.append(f'**{decision}** — {decision_text}')
    lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Saved decision to {output_path}")


def write_summary_csv(aggregated, funcs, configs, output_path):
    pauli_cfgs = [c for c in PAULI_CONFIGS if c in configs]
    per_seed = _per_seed_pauli_metrics(aggregated, funcs, pauli_cfgs)

    rows = []
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in configs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            entry = aggregated[fkey][cfg]
            fitnesses = entry.get('fitnesses', [])
            seeds = entry.get('seeds', list(range(len(fitnesses))))
            times = entry.get('times', [])
            ser_lookup = {m['seed']: m for m in per_seed.get(fkey, {}).get(cfg, [])}
            for i, seed in enumerate(seeds):
                fit = float(fitnesses[i]) if i < len(fitnesses) else float('nan')
                rt = float(times[i]) if i < len(times) else float('nan')
                pm = ser_lookup.get(int(seed), {})
                rows.append({
                    'Function': fkey,
                    'Config': cfg,
                    'Seed': int(seed),
                    'Fitness': fit,
                    'CER': float(pm.get('CER', float('nan'))),
                    'DER': float(pm.get('DER', float('nan'))),
                    'SER': float(pm.get('SER', float('nan'))),
                    'Runtime': rt,
                })

    if not rows:
        print("  WARN: no rows to write to summary CSV")
        return

    fieldnames = ['Function', 'Config', 'Seed', 'Fitness', 'CER', 'DER', 'SER', 'Runtime']
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Saved summary CSV ({len(rows)} rows) to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='QWMO-GAPR Comprehensive Pilot v1.0')
    parser.add_argument('--max-workers', type=int, default=None)
    parser.add_argument('--output-dir', type=str, default=None)
    args = parser.parse_args()

    config = dict(GAPR_COMPREHENSIVE_PILOT_CONFIG)
    if args.output_dir:
        config['output_dir'] = args.output_dir

    aggregated, json_path = run_pilot(config, max_workers=args.max_workers)

    criteria = check_criteria(
        aggregated, config['functions'], config['ablation_configs'],
        search_range=config.get('search_range', 200),
    )
    validation = check_validation(
        aggregated, config['functions'], config['ablation_configs'],
        search_range=config.get('search_range', 200),
    )

    output_dir = config['output_dir']
    pilot_report_path = os.path.join(output_dir, config['report_name'])
    validation_report_path = os.path.join(output_dir, config['validation_report_name'])
    decision_path = os.path.join(output_dir, config['decision_name'])
    csv_path = os.path.join(output_dir, config['summary_csv_name'])

    write_pilot_report(
        aggregated, criteria, pilot_report_path,
        config['functions'], config['ablation_configs'],
    )
    write_validation_report(
        aggregated, validation, validation_report_path,
        config['functions'], config['ablation_configs'],
        search_range=config.get('search_range', 200),
    )
    write_decision(criteria, decision_path)
    write_summary_csv(
        aggregated, config['functions'], config['ablation_configs'], csv_path,
    )

    print('\n=== GAPR COMPREHENSIVE PILOT v1.0 G1-G5 ===')
    for gid in ['G1', 'G2', 'G3', 'G4', 'G5']:
        c = criteria[gid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        print(f'  {gid}: {mark} - {c["description"]}')


if __name__ == '__main__':
    main()
