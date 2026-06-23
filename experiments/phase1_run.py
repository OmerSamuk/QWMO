import os
import time
import json
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from benchmark.cec2017 import CEC2017Benchmark
from core.qwmo import QWMO, BudgetExceeded
from core.phase1_logger import Phase1Logger
from experiments.config import PHASE1_CONFIG

FUNCTION_NAMES = {5: "Schwefel", 10: "Rastrigin", 20: "Hybrid", 28: "Composition"}
VARIANT_LABELS = {"phase1_v0": "V0", "phase1_v1": "V1", "phase1_v2": "V2", "phase1_v3": "V3"}

QWMO_PARAMS = {
    "gamma": 0.05, "c_base": 5, "kappa_0": 8,
    "k_s": 10, "eta_r": 0.001,
    "epsilon_max_ratio": 0.1, "epsilon_min_ratio": 0.01,
    "static_epsilon_ratio": 0.05,
    "adaptive_k": 3, "adaptive_lambda0": 0.75,
    "adaptive_epsilon_max_ratio": 0.15,
}


def _run_single(func_id, variant, seed):
    dimension = PHASE1_CONFIG["dimension"]
    pop_size = PHASE1_CONFIG["population_size"]
    max_fes = PHASE1_CONFIG["max_fes"]
    vid = VARIANT_LABELS.get(variant, variant)

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

    start = time.time()
    best_pos, best_fit = optimizer.run()
    elapsed = time.time() - start

    iter_df = logger.get_iteration_metrics_df()
    event_df = logger.get_event_logs_df()

    return {
        "func_id": func_id,
        "variant": variant,
        "seed": seed,
        "best_fitness": best_fit,
        "best_position": best_pos.tolist() if hasattr(best_pos, 'tolist') else list(best_pos),
        "fes_count": optimizer.fes_count,
        "elapsed": elapsed,
        "iter_df": iter_df,
        "event_df": event_df,
    }


def run_phase1(out_dir="results/phase1", max_workers=None):
    if max_workers is None:
        max_workers = int(os.environ.get("MAX_WORKERS", 8))
    n_workers = min(max_workers, os.cpu_count() or 1)

    functions = PHASE1_CONFIG["functions"]
    variants = PHASE1_CONFIG["ablation_configs"]
    seeds = PHASE1_CONFIG["seeds"]

    os.makedirs(out_dir, exist_ok=True)
    iter_dir = os.path.join(out_dir, "iteration_metrics")
    event_dir = os.path.join(out_dir, "raw_events")
    os.makedirs(iter_dir, exist_ok=True)
    os.makedirs(event_dir, exist_ok=True)

    tasks = [(f, v, s) for f in functions for v in variants for s in seeds]
    total = len(tasks)
    nfunc = len(functions)
    nvar = len(variants)
    nseed = len(seeds)
    print(f"Phase-1: {nfunc} functions x {nvar} variants x {nseed} seeds = {total} runs")
    print(f"Parallel: {n_workers} workers, output: {out_dir}\n")

    summary_rows = []
    completed = 0

    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        fut_map = {}
        for func_id, variant, seed in tasks:
            fut = executor.submit(_run_single, func_id, variant, seed)
            fut_map[fut] = (func_id, variant, seed)

        for fut in as_completed(fut_map):
            func_id, variant, seed = fut_map[fut]
            vid = VARIANT_LABELS.get(variant, variant)
            completed += 1
            try:
                result = fut.result()
                fit = result["best_fitness"]
                elapsed = result["elapsed"]

                fname = f"F{func_id}_{vid}_seed{seed}_run{seed}"
                iter_path = os.path.join(iter_dir, f"{fname}_iter.csv")
                event_path = os.path.join(event_dir, f"{fname}_events.csv")

                result["iter_df"].to_csv(iter_path, index=False)
                result["event_df"].to_csv(event_path, index=False)

                summary_rows.append({
                    "function": func_id,
                    "function_name": FUNCTION_NAMES.get(func_id, f"F{func_id}"),
                    "variant": variant,
                    "variant_id": vid,
                    "seed": seed,
                    "best_fitness": fit,
                    "fes_count": result["fes_count"],
                    "elapsed": elapsed,
                })
                print(f"  [{completed}/{total}] F{func_id} {vid} seed={seed}: "
                      f"fit={fit:.6e} time={elapsed:.2f}s")

                if completed % 50 == 0:
                    partial_summary = pd.DataFrame(summary_rows)
                    ckpt_path = os.path.join(out_dir, f"checkpoint_{completed}.json")
                    with open(ckpt_path, "w") as f:
                        json.dump({"completed": completed, "total": total,
                                   "summary": partial_summary.to_dict(orient="records")}, f)
                    print(f"  [checkpoint] {ckpt_path}")

            except Exception as e:
                import traceback
                print(f"  [{completed}/{total}] F{func_id} {vid} seed={seed}: ERROR {e}")
                traceback.print_exc()
                summary_rows.append({
                    "function": func_id,
                    "function_name": FUNCTION_NAMES.get(func_id, f"F{func_id}"),
                    "variant": variant,
                    "variant_id": vid,
                    "seed": seed,
                    "best_fitness": None,
                    "fes_count": None,
                    "elapsed": None,
                })

    summary_df = pd.DataFrame(summary_rows)
    summary_path = os.path.join(out_dir, "phase1_results_raw.csv")
    summary_df.to_csv(summary_path, index=False)
    print(f"\nSummary saved to {summary_path}")

    agg = summary_df.groupby(["function", "variant_id"]).agg(
        mean_fitness=("best_fitness", "mean"),
        std_fitness=("best_fitness", "std"),
        median_fitness=("best_fitness", "median"),
        min_fitness=("best_fitness", "min"),
        max_fitness=("best_fitness", "max"),
        mean_time=("elapsed", "mean"),
        n_runs=("seed", "count"),
    ).reset_index()

    agg_path = os.path.join(out_dir, "phase1_summary_table.csv")
    agg.to_csv(agg_path, index=False)
    print(f"Aggregate summary saved to {agg_path}")

    all_iter_files = sorted(
        os.path.join(iter_dir, f) for f in os.listdir(iter_dir)
        if f.endswith("_iter.csv")
    )
    if all_iter_files:
        combined_iter = pd.concat(
            (pd.read_csv(fp) for fp in all_iter_files), ignore_index=True
        )
        combined_iter.to_csv(
            os.path.join(out_dir, "phase1_iteration_metrics.csv"), index=False
        )
        print(f"Combined iteration metrics: {len(combined_iter)} rows")

    all_event_files = sorted(
        os.path.join(event_dir, f) for f in os.listdir(event_dir)
        if f.endswith("_events.csv")
    )
    if all_event_files:
        combined_events = pd.concat(
            (pd.read_csv(fp) for fp in all_event_files), ignore_index=True
        )
        combined_events.to_csv(
            os.path.join(out_dir, "phase1_event_logs.csv"), index=False
        )
        print(f"Combined event logs: {len(combined_events)} rows")

    print(f"\n{'='*60}")
    print("Phase-1 Summary")
    print(f"{'='*60}")
    for _, row in summary_df.iterrows():
        if row["best_fitness"] is not None:
            print(f"F{int(row['function'])} {row['variant_id']} seed={row['seed']}: "
                  f"{row['best_fitness']:.6e} ({row['elapsed']:.1f}s)")

    print(f"\n{'='*60}")
    print("Aggregate Means")
    for _, row in agg.iterrows():
        f = int(row["function"])
        v = row["variant_id"]
        m = row["mean_fitness"]
        s = row["std_fitness"]
        print(f"F{f} {v}: {m:.6e} ± {s:.6e}")

    return summary_df, agg


if __name__ == "__main__":
    run_phase1()
