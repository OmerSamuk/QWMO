"""QWMO-GAPR Revision Pilot v2.0 Runner.

Tests whether reducing epsilon_max_ratio from 0.15 to 0.10:
- preserves epsilon adaptivity (R1)
- reduces saturation (R2)
- preserves Pauli activation (R3)
- preserves performance competitiveness (R4)
- improves F15 behaviour (R5)

4 configs x 5 functions x 10 seeds = 200 runs.

Usage:
    python experiments/gapr_revision_pilot.py [--max-workers N]
"""

import os
import sys
import csv
import json
import argparse
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.config import GAPR_REVISION_PILOT_CONFIG
from experiments.runner import ExperimentRunner, ALGO_TO_QWMO_CONFIG

REVISION_GAPR_CFG = "QWMO_Full_GAPR_eps010"
EPS010_OVERRIDE = {"adaptive_epsilon_max_ratio": 0.10}

FULL_CONFIGS = [
    "QWMO_Full_Static",
    "QWMO_Full_Dynamic",
    "QWMO_Full_GAPR_eps010",
]
ALL_CONFIGS = [
    "QWMO_OrbitalEscape",
    "QWMO_Full_Static",
    "QWMO_Full_Dynamic",
    "QWMO_Full_GAPR_eps010",
]


def _run_single(func_id, dimension, algo_name, seed, pop_size, max_fes):
    runner = ExperimentRunner(
        dimensions=dimension, population_size=pop_size, max_fes=max_fes,
        num_runs=1, seed_list=[seed], max_workers=1,
    )
    overrides = EPS010_OVERRIDE if algo_name == REVISION_GAPR_CFG else None
    return (
        func_id, algo_name, seed,
        runner.run_single_experiment(func_id, algo_name, seed,
                                     qwmo_param_overrides=overrides),
    )


def run_pilot(config, max_workers=None):
    funcs = config['functions']
    dim = config['dimension']
    pop = config['population_size']
    max_fes = config['max_fes']
    seeds = config['seeds']
    cfgs = config['ablation_configs']
    output_dir = config['output_dir']
    os.makedirs(output_dir, exist_ok=True)

    if max_workers is None:
        max_workers = int(os.environ.get('MAX_WORKERS', 8))
    n_workers = min(max_workers, os.cpu_count() or 1)

    print(f"GAPR Revision Pilot v2.0: funcs={funcs} dim={dim} pop={pop} "
          f"max_fes={max_fes} seeds={seeds[0]}-{seeds[-1]} "
          f"configs={len(cfgs)} workers={n_workers}")

    tasks = [(fid, cfg, seed) for fid in funcs for cfg in cfgs for seed in seeds]
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
    print(f"\nSaved revision pilot results to {json_path}")

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
    rows = {}
    for fid in funcs:
        fkey = f'F{fid}'
        rows[fkey] = {}
        for cfg in pauli_configs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            entry = aggregated[fkey][cfg]
            seeds = entry.get('seeds', list(range(len(entry.get('fitnesses', [])))))
            coll_list = entry.get('pauli_collision_history_list', [])
            disp_list = entry.get('pauli_displacement_history_list', [])
            succ_list = entry.get('pauli_success_history_list', [])
            seed_metrics = []
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


def _aggregate_pauli_totals(aggregated, fkey, cfg):
    if cfg not in aggregated.get(fkey, {}):
        return None
    entry = aggregated[fkey][cfg]
    coll = sum(sum(run) for run in entry.get('pauli_collision_history_list', []))
    disp = sum(sum(run) for run in entry.get('pauli_displacement_history_list', []))
    succ = sum(sum(run) for run in entry.get('pauli_success_history_list', []))
    SER = succ / max(disp, 1)
    return {'coll': coll, 'disp': disp, 'succ': succ, 'SER': SER}


def _saturation_flag(ratio):
    if ratio > 0.5:
        return 'RED'
    if ratio > 0.2:
        return 'YELLOW'
    return 'GREEN'


def check_revision_criteria(aggregated, funcs, full_configs, search_range=200,
                            epsilon_min_ratio=0.01, adaptive_epsilon_max_ratio=0.10):
    results = {}
    eps_min = epsilon_min_ratio * search_range
    eps_max = adaptive_epsilon_max_ratio * search_range

    # --- R1: Epsilon adaptivity ---
    r1_pass_count = 0
    r1_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        if REVISION_GAPR_CFG not in aggregated.get(fkey, {}):
            continue
        ep_list_list = aggregated[fkey][REVISION_GAPR_CFG].get('epsilon_history_list', [])
        f_passed = True
        for i, ep_hist in enumerate(ep_list_list):
            if not ep_hist:
                f_passed = False
                r1_evidence.append(f"  {fkey}/{REVISION_GAPR_CFG}/seed_{i}: FAIL (empty)")
                continue
            std_ep = float(np.std(ep_hist))
            uniq_ep = len(np.unique(np.round(ep_hist, 9)))
            cond = (std_ep > 1e-12) and (uniq_ep > 5)
            if cond:
                r1_evidence.append(
                    f"  {fkey}/{REVISION_GAPR_CFG}/seed_{i}: PASS (std={std_ep:.4e}, unique={uniq_ep})"
                )
            else:
                f_passed = False
                r1_evidence.append(
                    f"  {fkey}/{REVISION_GAPR_CFG}/seed_{i}: FAIL (std={std_ep:.4e}, unique={uniq_ep})"
                )
        if f_passed:
            r1_pass_count += 1
    r1_passed = r1_pass_count >= 4
    results['R1'] = {
        'description': 'Epsilon adaptivity: std(eps) > 0 AND unique(eps) > 5 in >= 4/5 functions',
        'passed': r1_passed,
        'evidence': '\n'.join(r1_evidence) if r1_evidence else '  No GAPR runs found.',
    }

    # --- R2: Saturation reduction ---
    r2_functions_with_mean = 0
    r2_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        if REVISION_GAPR_CFG not in aggregated.get(fkey, {}):
            continue
        ep_list_list = aggregated[fkey][REVISION_GAPR_CFG].get('epsilon_history_list', [])
        sat_ratios = []
        for i, ep_hist in enumerate(ep_list_list):
            if not ep_hist:
                continue
            arr = np.asarray(ep_hist, dtype=float)
            n_at_max = int(np.sum(arr >= eps_max - 1e-9))
            sat = n_at_max / len(arr)
            sat_ratios.append(sat)
        if sat_ratios:
            mean_sat = float(np.mean(sat_ratios))
            flag = _saturation_flag(mean_sat)
            r2_evidence.append(
                f"  {fkey}: mean_eps_max_saturation={mean_sat:.4f} ({flag})"
            )
            if mean_sat < 0.50:
                r2_functions_with_mean += 1
        else:
            r2_evidence.append(f"  {fkey}: no epsilon data")
    r2_passed = r2_functions_with_mean >= 4
    results['R2'] = {
        'description': 'Saturation reduction: mean eps_max_saturation_ratio < 0.50 in >= 4/5 functions',
        'passed': r2_passed,
        'evidence': '\n'.join(r2_evidence),
    }

    # --- R3: Pauli activation preserved ---
    r3_pass_count = 0
    r3_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        totals = _aggregate_pauli_totals(aggregated, fkey, REVISION_GAPR_CFG)
        if totals is None:
            r3_evidence.append(f"  {fkey}: no data")
            continue
        if totals['coll'] > 0 and totals['disp'] > 0:
            r3_pass_count += 1
            r3_evidence.append(
                f"  {fkey}: PASS (coll={totals['coll']}, disp={totals['disp']})"
            )
        else:
            r3_evidence.append(
                f"  {fkey}: FAIL (coll={totals['coll']}, disp={totals['disp']})"
            )
    r3_passed = r3_pass_count >= 5
    results['R3'] = {
        'description': 'Pauli activation: collision > 0 AND displacement > 0 in 5/5 functions',
        'passed': r3_passed,
        'evidence': '\n'.join(r3_evidence),
    }

    # --- R4: Performance competitiveness ---
    r4_pass_count = 0
    r4_evidence = []
    for fid in funcs:
        fkey = f'F{fid}'
        fg = aggregated.get(fkey, {}).get(REVISION_GAPR_CFG, {}).get('mean')
        fs = aggregated.get(fkey, {}).get('QWMO_Full_Static', {}).get('mean')
        fd = aggregated.get(fkey, {}).get('QWMO_Full_Dynamic', {}).get('mean')
        if fg is not None and fs is not None and fd is not None:
            best_other = min(fs, fd)
            threshold = 1.05 * best_other
            if fg <= threshold:
                r4_pass_count += 1
                r4_evidence.append(
                    f"  {fkey}: Full_GAPR_eps010={fg:.4e} <= 1.05*min({fs:.4e},{fd:.4e})={threshold:.4e} -> PASS"
                )
            else:
                r4_evidence.append(
                    f"  {fkey}: Full_GAPR_eps010={fg:.4e} > 1.05*min({fs:.4e},{fd:.4e})={threshold:.4e} -> FAIL"
                )
        else:
            r4_evidence.append(f"  {fkey}: insufficient data")
    r4_passed = r4_pass_count >= 4
    results['R4'] = {
        'description': 'Performance competitiveness: mean(Full_GAPR_eps010) <= 1.05 * min(Static, Dynamic) in >= 4/5 functions',
        'passed': r4_passed,
        'evidence': '\n'.join(r4_evidence),
    }

    # --- R5: F15 special observation ---
    r5_evidence = []
    if 15 in funcs:
        fkey = 'F15'
        for cfg_name in ['QWMO_Full_GAPR_eps010', 'QWMO_Full_Static', 'QWMO_Full_Dynamic', 'QWMO_OrbitalEscape']:
            m = aggregated.get(fkey, {}).get(cfg_name, {}).get('mean')
            s = aggregated.get(fkey, {}).get(cfg_name, {}).get('std')
            if m is not None:
                r5_evidence.append(f"  {cfg_name}: mean={m:.4e} +/- {s:.4e}" if s else f"  {cfg_name}: mean={m:.4e}")
        r5_evidence.append(
            "  NOTE: Compare with v1.0 pilot: Full_GAPR had mean=5.0528e+04 on F15. "
            "Manual comparison required."
        )
    results['R5'] = {
        'description': 'F15 special observation: Full_GAPR_eps010 degradation vs v1.0',
        'passed': True,
        'evidence': '\n'.join(r5_evidence),
    }

    return results


def write_revision_report(aggregated, criteria, output_path, funcs, configs):
    lines = []
    lines.append('# QWMO-GAPR Revision Pilot v2.0 Report')
    lines.append('')
    lines.append(f'**Functions:** {funcs}  ')
    lines.append(f'**Configs:** {len(configs)} ({", ".join(configs)})  ')
    lines.append(f'**Seeds:** 10 (1-10)  ')
    lines.append(f'**Dimension:** 30  ')
    lines.append(f'**Max FEs:** 300,000  ')
    lines.append(f'**Adaptive params:** k=3, lambda0=0.75, eps_max_ratio=0.10, eps_min_ratio=0.01')
    lines.append('')

    lines.append('## Revision Criteria Summary (R1-R5)')
    lines.append('')
    for rid in ['R1', 'R2', 'R3', 'R4', 'R5']:
        c = criteria[rid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        lines.append(f'- **{rid}** [{mark}] {c["description"]}')
    lines.append('')

    lines.append('## Final Fitness Summary (mean +/- std)')
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
                row.append(f'{m:.3e} +/- {s:.2e}')
            else:
                row.append('---')
        lines.append('| ' + ' | '.join(row) + ' |')
    lines.append('')

    lines.append('## Full_GAPR_eps010 vs Full_Static / Full_Dynamic')
    lines.append('')
    lines.append('| Function | Full_GAPR_eps010 | Full_Static | Full_Dynamic | Best ref | Ratio |')
    lines.append('|---|---|---|---|---|---|')
    for fid in funcs:
        fkey = f'F{fid}'
        fg = aggregated.get(fkey, {}).get('QWMO_Full_GAPR_eps010', {}).get('mean')
        fs = aggregated.get(fkey, {}).get('QWMO_Full_Static', {}).get('mean')
        fd = aggregated.get(fkey, {}).get('QWMO_Full_Dynamic', {}).get('mean')
        if fg is not None and fs is not None and fd is not None:
            best_other = min(fs, fd)
            ratio = fg / best_other
            lines.append(
                f'| F{fid} | {fg:.4e} | {fs:.4e} | {fd:.4e} | {best_other:.4e} | {ratio:.4f} |'
            )
    lines.append('')

    lines.append('## Pauli Mechanism Statistics')
    lines.append('')
    lines.append('| Function | Config | Collisions | Displacements | Successes | CER | DER | SER |')
    lines.append('|---|---|---|---|---|---|---|---|')
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in configs:
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

    lines.append('## Runtime Statistics')
    lines.append('')
    lines.append('| Function | Config | Mean Runtime (s) |')
    lines.append('|---|---|---|')
    for fid in funcs:
        fkey = f'F{fid}'
        for cfg in configs:
            if cfg not in aggregated.get(fkey, {}):
                continue
            mt = aggregated[fkey][cfg].get('mean_time', 0)
            lines.append(f'| F{fid} | {cfg} | {mt:.2f} |')
    lines.append('')

    lines.append('## F15 Special Analysis')
    lines.append('')
    lines.append('| Config | Mean | Std |')
    lines.append('|---|---|---|')
    if 'F15' in [f'F{f}' for f in funcs]:
        for cfg in ['QWMO_Full_GAPR_eps010', 'QWMO_Full_Static', 'QWMO_Full_Dynamic', 'QWMO_OrbitalEscape']:
            m = aggregated.get('F15', {}).get(cfg, {}).get('mean')
            s = aggregated.get('F15', {}).get(cfg, {}).get('std')
            if m is not None:
                lines.append(f'| {cfg} | {m:.4e} | {s:.4e} |')
    lines.append('')
    lines.append('v1.0 reference: Full_GAPR mean=5.0528e+04 on F15. Manual comparison required.')
    lines.append('')

    lines.append('## Preliminary Interpretation')
    lines.append('')
    all_pass = all(criteria[r]['passed'] for r in ['R1', 'R2', 'R3', 'R4'])
    if all_pass:
        lines.append('R1-R4 all PASS. GAPR with eps_max_ratio=0.10 is viable.')
    else:
        lines.append('Some criteria failed. See R1-R4 details for revision guidance.')
    lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Saved revision report to {output_path}")


def write_revision_validation_report(aggregated, criteria, output_path, funcs, configs,
                                      search_range=200, epsilon_min_ratio=0.01,
                                      adaptive_epsilon_max_ratio=0.10):
    eps_min = epsilon_min_ratio * search_range
    eps_max = adaptive_epsilon_max_ratio * search_range

    lines = []
    lines.append('# QWMO-GAPR Revision Pilot v2.0 Validation Report')
    lines.append('')
    lines.append(f'**Functions:** {funcs}  ')
    lines.append(f'**Eps bounds:** min={eps_min:.4e}, max={eps_max:.4e}  ')
    lines.append(f'**Tolerance:** 1e-9  ')
    lines.append('')

    lines.append('## R1-R3 Validation Table')
    lines.append('')
    for rid in ['R1', 'R2', 'R3']:
        c = criteria[rid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        lines.append(f'- **{rid}** [{mark}] {c["description"]}')
    lines.append('')

    lines.append('## Epsilon Aggregate Statistics')
    lines.append('')
    lines.append('| Function | Config | eps_min | eps_max | eps_mean | eps_std | unique_count |')
    lines.append('|---|---|---|---|---|---|---|')
    for fid in funcs:
        fkey = f'F{fid}'
        if REVISION_GAPR_CFG not in aggregated.get(fkey, {}):
            continue
        ep_list_list = aggregated[fkey][REVISION_GAPR_CFG].get('epsilon_history_list', [])
        all_eps = [e for hist in ep_list_list for e in hist]
        if all_eps:
            arr = np.asarray(all_eps, dtype=float)
            lines.append(
                f'| F{fid} | {REVISION_GAPR_CFG} | {np.min(arr):.4e} | {np.max(arr):.4e} | '
                f'{np.mean(arr):.4e} | {np.std(arr):.4e} | '
                f'{len(np.unique(np.round(arr, 9)))} |'
            )
    lines.append('')

    lines.append('## Epsilon Saturation Ratios')
    lines.append('')
    lines.append('Threshold legend: GREEN < 0.2, 0.2 <= YELLOW <= 0.5, RED > 0.5')
    lines.append('')
    lines.append('### Saturation at eps_max')
    lines.append('')
    lines.append('| Function | Seed | ratio | flag |')
    lines.append('|---|---|---|---|')
    for fid in funcs:
        fkey = f'F{fid}'
        if REVISION_GAPR_CFG not in aggregated.get(fkey, {}):
            continue
        ep_list_list = aggregated[fkey][REVISION_GAPR_CFG].get('epsilon_history_list', [])
        for i, ep_hist in enumerate(ep_list_list):
            if not ep_hist:
                continue
            arr = np.asarray(ep_hist, dtype=float)
            n_at_max = int(np.sum(arr >= eps_max - 1e-9))
            ratio = n_at_max / len(arr)
            lines.append(f'| F{fid} | {i} | {ratio:.4f} | {_saturation_flag(ratio)} |')
    lines.append('')
    lines.append('### Saturation at eps_min')
    lines.append('')
    lines.append('| Function | Seed | ratio | flag |')
    lines.append('|---|---|---|---|')
    for fid in funcs:
        fkey = f'F{fid}'
        if REVISION_GAPR_CFG not in aggregated.get(fkey, {}):
            continue
        ep_list_list = aggregated[fkey][REVISION_GAPR_CFG].get('epsilon_history_list', [])
        for i, ep_hist in enumerate(ep_list_list):
            if not ep_hist:
                continue
            arr = np.asarray(ep_hist, dtype=float)
            n_at_min = int(np.sum(arr <= eps_min + 1e-9))
            ratio = n_at_min / len(arr)
            lines.append(f'| F{fid} | {i} | {ratio:.4f} | {_saturation_flag(ratio)} |')
    lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Saved revision validation report to {output_path}")


def write_revision_decision(criteria, output_path):
    r1 = criteria['R1']['passed']
    r2 = criteria['R2']['passed']
    r3 = criteria['R3']['passed']
    r4 = criteria['R4']['passed']

    if r1 and r2 and r3 and r4:
        decision = 'A'
        decision_text = (
            'A = Proceed to full QWMO-GAPR benchmark. '
            'All R1-R4 criteria passed with eps_max_ratio=0.10.'
        )
    elif r1 and r3 and r4:
        decision = 'B'
        decision_text = (
            'B = Keep GAPR as mechanism variant. '
            'Epsilon adaptivity and Pauli activation work, '
            'but saturation remains high.'
        )
    elif r1 and r3:
        decision = 'C'
        decision_text = (
            'C = Further formula revision required. '
            'GAPR mechanism works but needs adjustment.'
        )
    else:
        decision = 'D'
        decision_text = (
            'D = Stop GAPR line. '
            'Epsilon adaptivity or Pauli activation failed '
            'even with eps_max_ratio=0.10.'
        )

    lines = []
    lines.append('# QWMO-GAPR Revision Pilot v2.0 Decision')
    lines.append('')
    lines.append('## Revision Criteria Results')
    lines.append('')
    for rid in ['R1', 'R2', 'R3', 'R4', 'R5']:
        c = criteria[rid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        lines.append(f'- **{rid}** [{mark}] {c["description"]}')
    lines.append('')
    lines.append('## FINAL DECISION')
    lines.append('')
    lines.append(f'**{decision}** — {decision_text}')
    lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Saved revision decision to {output_path}")


def write_revision_summary_csv(aggregated, funcs, configs, output_path,
                                search_range=200, epsilon_min_ratio=0.01,
                                adaptive_epsilon_max_ratio=0.10):
    eps_min = epsilon_min_ratio * search_range
    eps_max = adaptive_epsilon_max_ratio * search_range
    pauli_cfgs = [c for c in configs if c != 'QWMO_OrbitalEscape']
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
            ep_list_list = entry.get('epsilon_history_list', [])

            for i, seed in enumerate(seeds):
                fit = float(fitnesses[i]) if i < len(fitnesses) else float('nan')
                rt = float(times[i]) if i < len(times) else float('nan')
                pm = ser_lookup.get(int(seed), {})

                eps_mean = float('nan')
                eps_std = float('nan')
                eps_uniq = float('nan')
                sat_max = float('nan')
                sat_min = float('nan')
                if i < len(ep_list_list) and ep_list_list[i]:
                    arr = np.asarray(ep_list_list[i], dtype=float)
                    eps_mean = float(np.mean(arr))
                    eps_std = float(np.std(arr))
                    eps_uniq = float(len(np.unique(np.round(arr, 9))))
                    sat_max = float(np.sum(arr >= eps_max - 1e-9)) / len(arr)
                    sat_min = float(np.sum(arr <= eps_min + 1e-9)) / len(arr)

                rows.append({
                    'Function': fkey,
                    'Config': cfg,
                    'Seed': int(seed),
                    'Fitness': fit,
                    'CER': float(pm.get('CER', float('nan'))),
                    'DER': float(pm.get('DER', float('nan'))),
                    'SER': float(pm.get('SER', float('nan'))),
                    'Runtime': rt,
                    'EpsilonMean': eps_mean,
                    'EpsilonStd': eps_std,
                    'EpsilonUnique': eps_uniq,
                    'EpsMaxSaturationRatio': sat_max,
                    'EpsMinSaturationRatio': sat_min,
                })

    if not rows:
        print("  WARN: no rows to write to summary CSV")
        return

    fieldnames = [
        'Function', 'Config', 'Seed', 'Fitness', 'CER', 'DER', 'SER', 'Runtime',
        'EpsilonMean', 'EpsilonStd', 'EpsilonUnique',
        'EpsMaxSaturationRatio', 'EpsMinSaturationRatio',
    ]
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Saved revision summary CSV ({len(rows)} rows) to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='QWMO-GAPR Revision Pilot v2.0')
    parser.add_argument('--max-workers', type=int, default=None)
    parser.add_argument('--output-dir', type=str, default=None)
    args = parser.parse_args()

    config = dict(GAPR_REVISION_PILOT_CONFIG)
    if args.output_dir:
        config['output_dir'] = args.output_dir

    aggregated, json_path = run_pilot(config, max_workers=args.max_workers)

    criteria = check_revision_criteria(
        aggregated, config['functions'], config['ablation_configs'],
        search_range=config.get('search_range', 200),
        adaptive_epsilon_max_ratio=config.get('gapr_override', {}).get('adaptive_epsilon_max_ratio', 0.10),
    )

    output_dir = config['output_dir']
    report_path = os.path.join(output_dir, config['report_name'])
    validation_path = os.path.join(output_dir, config['validation_report_name'])
    decision_path = os.path.join(output_dir, config['decision_name'])
    csv_path = os.path.join(output_dir, config['summary_csv_name'])

    write_revision_report(aggregated, criteria, report_path,
                          config['functions'], config['ablation_configs'])
    write_revision_validation_report(
        aggregated, criteria, validation_path,
        config['functions'], config['ablation_configs'],
        search_range=config.get('search_range', 200),
        adaptive_epsilon_max_ratio=config.get('gapr_override', {}).get('adaptive_epsilon_max_ratio', 0.10),
    )
    write_revision_decision(criteria, decision_path)
    write_revision_summary_csv(
        aggregated, config['functions'], config['ablation_configs'], csv_path,
        search_range=config.get('search_range', 200),
        adaptive_epsilon_max_ratio=config.get('gapr_override', {}).get('adaptive_epsilon_max_ratio', 0.10),
    )

    print('\n=== GAPR REVISION PILOT v2.0 R1-R5 ===')
    for rid in ['R1', 'R2', 'R3', 'R4', 'R5']:
        c = criteria[rid]
        mark = 'PASS' if c['passed'] else 'FAIL'
        print(f'  {rid}: {mark} - {c["description"]}')


if __name__ == '__main__':
    main()
