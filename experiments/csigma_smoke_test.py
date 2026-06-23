import os
import time
import numpy as np
from benchmark.cec2017 import CEC2017Benchmark
from core.qwmo import QWMO, BudgetExceeded
from core.phase1_logger import Phase1Logger
from experiments.config import CSIGMA_CONFIG

FUNCTION_NAMES = CSIGMA_CONFIG["function_names"]
VARIANT_NAMES = CSIGMA_CONFIG["variant_labels"]

QWMO_PARAMS = {
    "gamma": 0.05, "c_base": 5, "kappa_0": 8,
    "k_s": 10, "eta_r": 0.001,
    "epsilon_max_ratio": 0.1, "epsilon_min_ratio": 0.01,
    "static_epsilon_ratio": 0.05,
    "adaptive_k": 3, "adaptive_lambda0": 0.75,
    "adaptive_epsilon_max_ratio": 0.15,
}

REQUIRED_COLS = [
    "iteration", "function_id", "variant_id", "run_id", "seed",
    "best_fitness", "mean_fitness", "worst_fitness",
    "population_diversity_center", "population_diversity_pairwise",
    "mean_agent_distance", "mean_knn_distance",
    "epsilon_value", "epsilon_to_mean_knn_ratio",
    "collision_count", "displacement_count",
    "escape_triggered_count", "escape_success_count",
    "escape_failure_count", "escape_neutral_count",
    "pauli_success_count", "pauli_failure_count",
    "pauli_neutral_count", "boundary_clipping_count",
]

CSIGMA_COLS = [
    "sigma_mean", "sigma_median", "sigma_min", "sigma_max",
    "k_mean", "k_stagnant_count", "tau_value",
]


def run_smoke():
    dimension = CSIGMA_CONFIG["dimension"]
    pop_size = CSIGMA_CONFIG["population_size"]
    seeds = CSIGMA_CONFIG["smoke_seeds"]
    max_fes = CSIGMA_CONFIG["smoke_max_fes"]
    variants = CSIGMA_CONFIG["ablation_configs"]
    functions = CSIGMA_CONFIG["functions"]

    results = []
    all_ok = True

    print("=" * 70)
    print(f"QWMO-Csigma Smoke Test: D={dimension}, N={pop_size}, FE={max_fes}")
    print(f"Functions: {[FUNCTION_NAMES.get(f, f'F{f}') for f in functions]}")
    print(f"Seeds: {seeds}")
    print(f"Variants: {len(variants)}")
    print("=" * 70)

    for func_id in functions:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        for variant in variants:
            vid = VARIANT_NAMES.get(variant, variant)
            for seed in seeds:
                run_label = f"F{func_id}({fname}) {vid} seed={seed}"

                benchmark = CEC2017Benchmark(func_id, dimension)
                logger = Phase1Logger(
                    function_id=func_id,
                    variant_id=vid,
                    run_id=seed,
                    seed=seed,
                    lower_bound=benchmark.lower_bound,
                    upper_bound=benchmark.upper_bound,
                    dimension=dimension,
                )

                optimizer = QWMO(
                    func=benchmark,
                    dimension=dimension,
                    lower_bound=benchmark.lower_bound,
                    upper_bound=benchmark.upper_bound,
                    population_size=pop_size,
                    max_fes=max_fes,
                    **QWMO_PARAMS,
                    ablation_config=variant,
                    seed=seed,
                    phase1_logger=logger,
                )

                try:
                    start = time.time()
                    best_pos, best_fit = optimizer.run()
                    elapsed = time.time() - start

                    iter_df = logger.get_iteration_metrics_df()
                    event_df = logger.get_event_logs_df()

                    missing = [c for c in REQUIRED_COLS if c not in iter_df.columns]
                    n_rows = len(iter_df)
                    has_events = len(event_df) > 0
                    row_ok = len(missing) == 0
                    all_ok = all_ok and row_ok

                    has_sigma = all(c in iter_df.columns for c in CSIGMA_COLS)
                    sigma_ok = has_sigma if variant == "csigma_csigma" else True
                    all_ok = all_ok and sigma_ok

                    print(f"  [{run_label}] fit={best_fit:.4e} time={elapsed:.2f}s "
                          f"rows={n_rows} cols_ok={row_ok} sigma_ok={sigma_ok} events={has_events}")

                    results.append({
                        "function": func_id,
                        "function_name": fname,
                        "variant": variant,
                        "variant_id": vid,
                        "seed": seed,
                        "best_fitness": best_fit,
                        "elapsed": elapsed,
                        "iterations": n_rows,
                        "events": len(event_df),
                        "cols_ok": row_ok,
                        "sigma_ok": sigma_ok,
                    })

                except Exception as e:
                    import traceback
                    print(f"  [{run_label}] ERROR: {e}")
                    traceback.print_exc()
                    all_ok = False

    print(f"\n{'=' * 70}")
    print(f"Smoke Test Result: {'ALL PASS' if all_ok else 'SOME FAILURES'}")
    print(f"{'=' * 70}")

    report_path = os.path.join(CSIGMA_CONFIG["output_dir"], "csigma_smoke_test_report.md")
    os.makedirs(CSIGMA_CONFIG["output_dir"], exist_ok=True)
    with open(report_path, "w") as f:
        f.write("# QWMO-Csigma Smoke Test Report\n\n")
        f.write(f"**Dimension:** {dimension}\n")
        f.write(f"**Population:** N={pop_size}\n")
        f.write(f"**FE Budget:** {max_fes}\n")
        f.write(f"**Seeds:** {seeds}\n\n")
        f.write(f"## Result: {'ALL PASS' if all_ok else 'SOME FAILURES'}\n\n")
        f.write("| Function | Variant | Seed | Fitness | Time (s) | Iterations | Events | Cols OK | Sigma OK |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| F{r['function']} ({r['function_name']}) | {r['variant_id']} "
                    f"| {r['seed']} | {r['best_fitness']:.4e} | {r['elapsed']:.2f} "
                    f"| {r['iterations']} | {r['events']} | {r['cols_ok']} | {r['sigma_ok']} |\n")

        if all_ok:
            f.write("\n## Verdict\n\n**PASS** — All checks passed.\n")
        else:
            f.write("\n## Verdict\n\n**FAIL** — See details above.\n")

    print(f"Report written to {report_path}")
    return all_ok


if __name__ == "__main__":
    run_smoke()
