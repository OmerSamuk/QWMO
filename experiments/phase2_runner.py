import os
import time
import json
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed


MODES = {"presmoke", "smoke", "pilot", "final"}

METHOD_SHORT = {
    "M0_random": "M0",
    "M1_forward": "M1",
    "M2_backward": "M2",
    "M3_GA": "M3",
    "M4_BPSO": "M4",
    "M5_ASO": "M5",
    "M6_AOS": "M6",
    "V0_core_binary": "V0",
    "V1_static_qwmo": "V1",
}


def _get_matrix(mode, config=None):
    if mode == "presmoke":
        return {
            "datasets": ["D1"],
            "subspace_regimes": ["ranked", "random"],
            "p_levels": [100, "full"],
            "methods": ["M0_random", "M3_GA", "M4_BPSO", "V1_static_qwmo"],
            "seeds": [0, 1, 2, 3, 4],
            "fitness_budget": 1000,
            "outer_cv_folds": 5,
            "outer_cv_repeats": 2,
            "inner_cv_folds": 3,
        }
    elif mode == "smoke":
        return {
            "datasets": ["D1"],
            "subspace_regimes": ["ranked", "random"],
            "p_levels": [100, "full"],
            "methods": [
                "M0_random", "M1_forward", "M2_backward",
                "M3_GA", "M4_BPSO", "M5_ASO", "M6_AOS",
                "V0_core_binary", "V1_static_qwmo",
            ],
            "seeds": [0, 1, 2],
            "fitness_budget": 500,
            "outer_cv_folds": 3,
            "outer_cv_repeats": 1,
            "inner_cv_folds": 3,
        }
    elif mode == "pilot":
        return {
            "datasets": ["D1"],
            "subspace_regimes": ["ranked", "random"],
            "p_levels": [50, 100, 250, "full"],
            "methods": [
                "M0_random", "M1_forward", "M2_backward",
                "M3_GA", "M4_BPSO", "V0_core_binary", "V1_static_qwmo",
            ],
            "seeds": list(range(10)),
            "fitness_budget": 1000,
            "outer_cv_folds": 5,
            "outer_cv_repeats": 2,
            "inner_cv_folds": 3,
        }
    elif mode == "final":
        return {
            "datasets": ["D1", "D2", "D3"],
            "subspace_regimes": ["ranked", "random"],
            "p_levels": [25, 50, 100, 250, 500, "full"],
            "methods": [
                "M0_random", "M1_forward", "M2_backward",
                "M3_GA", "M4_BPSO", "M5_ASO", "M6_AOS",
                "V0_core_binary", "V1_static_qwmo",
            ],
            "seeds": list(range(30)),
            "fitness_budget": 3000,
            "outer_cv_folds": 5,
            "outer_cv_repeats": 3,
            "inner_cv_folds": 3,
        }


def _get_optimizer(method, evaluator, n_features, seed, **kwargs):
    if method == "M0_random":
        from baselines.random_search import RandomSearch
        return RandomSearch(evaluator, n_features, seed=seed, **kwargs)
    elif method == "M3_GA":
        from baselines.ga_binary import GABinary
        return GABinary(evaluator, n_features, seed=seed, **kwargs)
    elif method == "M4_BPSO":
        from baselines.bpso import BPSO
        return BPSO(evaluator, n_features, seed=seed, **kwargs)
    elif method == "V0_core_binary":
        from core.qwmo_core_binary import QWMOCoreBinary
        return QWMOCoreBinary(evaluator, n_features, seed=seed, **kwargs)
    elif method == "V1_static_qwmo":
        from core.qwmo_binary import QWMOBinary
        return QWMOBinary(evaluator, n_features, seed=seed, **kwargs)
    else:
        raise ValueError(f"Unknown method: {method}")


def _run_single(dataset_id, subspace_regime, p_level, method, seed, out_dir):
    import time
    from radiomics.datasets import get_dataset

    ds = get_dataset(dataset_id)
    # TODO: load actual radiomics data from ds.download_path
    X = np.random.rand(ds.n_samples, 500)
    y = np.random.randint(0, 2, ds.n_samples)

    if isinstance(p_level, int) and p_level < X.shape[1]:
        if subspace_regime == "ranked":
            order = np.arange(X.shape[1])
            order = np.random.permutation(order)
            X = X[:, order[:p_level]]
        else:
            X = X[:, np.random.choice(X.shape[1], p_level, replace=False)]

    from fitness.evaluator import FitnessEvaluator
    evaluator = FitnessEvaluator(X, y, n_splits=3)

    n_features = X.shape[1]
    optimizer = _get_optimizer(method, evaluator, n_features, seed=seed)

    start = time.time()
    best_pos, best_fit = optimizer.run()
    elapsed = time.time() - start

    result = {
        "dataset": dataset_id,
        "subspace": subspace_regime,
        "p_level": str(p_level),
        "method": method,
        "seed": seed,
        "best_fitness": best_fit,
        "fes_count": optimizer.fes_count,
        "elapsed": elapsed,
    }

    return result


def run_phase2(mode="presmoke", out_dir="results/phase2", max_workers=None):
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got '{mode}'")

    matrix = _get_matrix(mode)
    os.makedirs(out_dir, exist_ok=True)

    tasks = [
        (ds, ss, p, m, s)
        for ds in matrix["datasets"]
        for ss in matrix["subspace_regimes"]
        for p in matrix["p_levels"]
        for m in matrix["methods"]
        for s in matrix["seeds"]
    ]

    total = len(tasks)
    print(f"Phase-2 mode={mode}: {total} runs")
    print(f"  datasets          : {matrix['datasets']}")
    print(f"  subspace_regimes  : {matrix['subspace_regimes']}")
    print(f"  p_levels          : {matrix['p_levels']}")
    print(f"  methods           : {matrix['methods']}")
    print(f"  seeds             : {len(matrix['seeds'])}")
    print(f"  fitness_budget    : {matrix['fitness_budget']}")

    max_workers = max_workers or min(8, os.cpu_count() or 1)
    print(f"  workers           : {max_workers}")

    rows = []
    completed = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        fut_map = {}
        for ds, ss, p, m, s in tasks:
            fut = executor.submit(_run_single, ds, ss, p, m, s, out_dir)
            fut_map[fut] = (ds, ss, p, m, s)

        for fut in as_completed(fut_map):
            ds, ss, p, m, s = fut_map[fut]
            completed += 1
            try:
                result = fut.result()
                rows.append(result)
                m_short = METHOD_SHORT.get(m, m)
                print(f"  [{completed}/{total}] {ds} {ss} p={p} {m_short} seed={s}: "
                      f"fit={result['best_fitness']:.6e} time={result['elapsed']:.2f}s")

                if completed % 50 == 0:
                    ckpt_path = os.path.join(out_dir, f"checkpoint_{mode}_{completed}.json")
                    with open(ckpt_path, "w") as f:
                        json.dump({"completed": completed, "total": total,
                                   "rows": rows}, f, indent=2)

            except Exception as e:
                m_short = METHOD_SHORT.get(m, m)
                print(f"  [{completed}/{total}] {ds} {ss} p={p} {m_short} seed={s}: ERROR {e}")
                rows.append({
                    "dataset": ds, "subspace": ss, "p_level": str(p),
                    "method": m, "seed": s, "best_fitness": None,
                    "fes_count": None, "elapsed": None,
                })

    df = pd.DataFrame(rows)
    out_name = f"phase2_{mode}_results_raw.csv"
    out_path = os.path.join(out_dir, out_name)
    df.to_csv(out_path, index=False)
    print(f"\nSaved to {out_path}")

    return df


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "presmoke"
    run_phase2(mode=mode)
