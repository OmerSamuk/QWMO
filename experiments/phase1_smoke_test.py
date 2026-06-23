import os
import time
import numpy as np
from benchmark.cec2017 import CEC2017Benchmark
from core.qwmo import QWMO, BudgetExceeded
from core.phase1_logger import Phase1Logger
from experiments.config import PHASE1_CONFIG

FUNCTION_NAMES = {5: "Schwefel", 10: "Rastrigin", 20: "Hybrid", 28: "Composition"}
VARIANT_NAMES = {"phase1_v0": "V0 (Orbital+Escape)",
                 "phase1_v1": "V1 (Static QWMO)",
                 "phase1_v2": "V2 (Dynamic Epsilon QWMO)",
                 "phase1_v3": "V3 (GAPR Final)"}

QWMO_PARAMS = {
    "gamma": 0.05, "c_base": 5, "kappa_0": 8,
    "k_s": 10, "eta_r": 0.001,
    "epsilon_max_ratio": 0.1, "epsilon_min_ratio": 0.01,
    "static_epsilon_ratio": 0.05,
    "adaptive_k": 3, "adaptive_lambda0": 0.75,
    "adaptive_epsilon_max_ratio": 0.15,
}

def run_smoke():
    func_id = 10
    dimension = PHASE1_CONFIG["dimension"]
    pop_size = PHASE1_CONFIG["population_size"]
    seeds = PHASE1_CONFIG["smoke_seeds"]
    max_fes = PHASE1_CONFIG["smoke_max_fes"]
    variants = PHASE1_CONFIG["ablation_configs"]
    search_range = PHASE1_CONFIG["search_range"]

    results = []
    all_ok = True

    print("=" * 70)
    print(f"Phase-1 Smoke Test: F10 (Rastrigin), D={dimension}, N={pop_size}")
    print(f"FE budget: {max_fes}, Seeds: {seeds}")
    print(f"Variants: {len(variants)}")
    print("=" * 70)

    for variant in variants:
        for seed in seeds:
            variant_id = variant.replace("phase1_", "V")
            run_label = f"{VARIANT_NAMES.get(variant, variant)} seed={seed}"

            benchmark = CEC2017Benchmark(func_id, dimension)
            logger = Phase1Logger(
                function_id=func_id,
                variant_id=variant_id,
                run_id=seed,
                seed=seed,
                lower_bound=-100,
                upper_bound=100,
                dimension=dimension,
            )

            params = dict(QWMO_PARAMS)
            if variant == "phase1_v2":
                params["epsilon_min_ratio"] = PHASE1_CONFIG["v2_override"]["epsilon_min_ratio"]

            optimizer = QWMO(
                func=benchmark,
                dimension=dimension,
                lower_bound=benchmark.lower_bound,
                upper_bound=benchmark.upper_bound,
                population_size=pop_size,
                max_fes=max_fes,
                **params,
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

                required_cols = [
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
                missing = [c for c in required_cols if c not in iter_df.columns]
                n_rows = len(iter_df)
                has_events = len(event_df) > 0

                row_ok = len(missing) == 0
                all_ok = all_ok and row_ok

                print(f"  [{run_label}] fit={best_fit:.4e} time={elapsed:.2f}s "
                      f"rows={n_rows} cols_ok={row_ok} events={has_events}")

                results.append({
                    "variant": variant,
                    "seed": seed,
                    "best_fitness": best_fit,
                    "elapsed": elapsed,
                    "iterations": n_rows,
                    "events": len(event_df),
                    "cols_ok": row_ok,
                    "missing_cols": missing if missing else "",
                })

                if variant == "phase1_v3" and n_rows > 10:
                    epsilon_col = iter_df["epsilon_value"]
                    has_adaptivity = epsilon_col.nunique() > 1
                    print(f"    -> epsilon adaptivity: {has_adaptivity} "
                          f"(unique={epsilon_col.nunique()}, "
                          f"mean={epsilon_col.mean():.2e})")

            except Exception as e:
                print(f"  [{run_label}] ERROR: {e}")
                all_ok = False

    print(f"\n{'=' * 70}")
    print(f"Smoke Test Result: {'ALL PASS' if all_ok else 'SOME FAILURES'}")
    print(f"{'=' * 70}")

    report_path = "phase1_smoke_test_report.md"
    with open(report_path, "w") as f:
        f.write("# Phase-1 Smoke Test Report\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Function:** F10 (Rastrigin)\n")
        f.write(f"**Dimension:** {dimension}\n")
        f.write(f"**Population:** N={pop_size}\n")
        f.write(f"**FE Budget:** {max_fes}\n")
        f.write(f"**Seeds:** {seeds}\n")
        f.write(f"**Variants:** {len(variants)}\n\n")
        f.write(f"## Result: {'ALL PASS' if all_ok else 'SOME FAILURES'}\n\n")

        f.write("| Variant | Seed | Fitness | Time (s) | Iterations | Events | Cols OK |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| {VARIANT_NAMES.get(r['variant'], r['variant'])} "
                    f"| {r['seed']} | {r['best_fitness']:.4e} "
                    f"| {r['elapsed']:.2f} | {r['iterations']} "
                    f"| {r['events']} | {r['cols_ok']} |\n")

        times = [r["elapsed"] for r in results]
        if times:
            f.write(f"\n**Timing Summary:** mean={np.mean(times):.2f}s, "
                    f"max={np.max(times):.2f}s, total={np.sum(times):.2f}s\n")
            f.write(f"\n**Estimated 480 runs (300k FE):** "
                    f"mean_per_run={np.mean(times):.2f}s × 480 = "
                    f"{np.sum(times) / len(times) * 480 / 60:.1f} minutes "
                    f"(~{np.sum(times) / len(times) * 480 / 3600:.1f} hours)\n")

        if all_ok:
            f.write("\n## Verdict\n\n**PASS** — All variant/logging checks passed.\n")
        else:
            f.write("\n## Verdict\n\n**FAIL** — See details above.\n")

    print(f"\nReport written to {report_path}")
    return all_ok


if __name__ == "__main__":
    run_smoke()
