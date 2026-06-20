import os
import time
import json
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

from sklearn.feature_selection import f_classif
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

from fitness.preprocessing import preprocess_train, preprocess_transform
from fitness.evaluator import FitnessEvaluator, evaluate_on_outer
from radiomics.datasets import get_dataset, load_placeholder_features


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


def decode_mask(position, method):
    """Method-aware mask decoding.

    M1/M2 return binary mask directly from greedy search.
    All others use sigmoid(p > 0.5) on latent continuous position.
    """
    if method in ("M1_forward", "M2_backward"):
        return np.asarray(position, dtype=int)
    p = 1.0 / (1.0 + np.exp(-np.asarray(position, dtype=float)))
    return (p > 0.5).astype(int)


def _get_matrix(mode, config=None):
    if mode == "presmoke":
        return {
            "datasets": ["D1a"],
            "subspace_regimes": ["ranked", "random"],
            "p_levels": [100, "full"],
            "methods": ["M0_random", "M3_GA", "M4_BPSO", "V1_static_qwmo"],
            "seeds": [0, 1, 2, 3, 4],
            "fitness_budget": 1000,
            "outer_cv_folds": 2,
            "outer_cv_repeats": 1,
            "inner_cv_folds": 3,
        }
    elif mode == "smoke":
        return {
            "datasets": ["D1a"],
            "subspace_regimes": ["ranked", "random"],
            "p_levels": [100, "full"],
            "methods": [
                "M0_random", "M1_forward", "M2_backward",
                "M3_GA", "M4_BPSO", "M5_ASO", "M6_AOS",
                "V0_core_binary", "V1_static_qwmo",
            ],
            "seeds": [0, 1, 2],
            "fitness_budget": 500,
            "outer_cv_folds": 2,
            "outer_cv_repeats": 1,
            "inner_cv_folds": 3,
        }
    elif mode == "pilot":
        return {
            "datasets": ["D1a", "D1b"],
            "subspace_regimes": ["ranked", "random"],
            "p_levels": [100, 250, "full"],
            "methods": [
                "M0_random", "M1_forward", "M2_backward",
                "M3_GA", "M4_BPSO", "V0_core_binary", "V1_static_qwmo",
            ],
            "seeds": list(range(10)),
            "fitness_budget": 1000,
            "outer_cv_folds": 5,
            "outer_cv_repeats": 1,
            "inner_cv_folds": 3,
        }
    elif mode == "final":
        return {
            "datasets": ["D1a", "D1b", "D2", "D3"],
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


def _get_optimizer(method, evaluator, n_features, budget, seed, **kwargs):
    if method == "M0_random":
        from baselines.random_search import RandomSearch
        return RandomSearch(evaluator, n_features, max_fes=budget, seed=seed, **kwargs)
    elif method == "M1_forward":
        from baselines.greedy import ForwardSelection
        return ForwardSelection(evaluator, n_features, max_fes=budget, seed=seed, **kwargs)
    elif method == "M2_backward":
        from baselines.greedy import BackwardSelection
        return BackwardSelection(evaluator, n_features, max_fes=budget, seed=seed, **kwargs)
    elif method == "M3_GA":
        from baselines.ga_binary import GABinary
        return GABinary(evaluator, n_features, max_fes=budget, seed=seed, **kwargs)
    elif method == "M4_BPSO":
        from baselines.bpso import BPSO
        return BPSO(evaluator, n_features, max_fes=budget, seed=seed, **kwargs)
    elif method == "V0_core_binary":
        from core.qwmo_core_binary import QWMOCoreBinary
        return QWMOCoreBinary(evaluator, n_features, max_fes=budget, seed=seed, **kwargs)
    elif method == "V1_static_qwmo":
        from core.qwmo_binary import QWMOBinary
        return QWMOBinary(evaluator, n_features, max_fes=budget, seed=seed, **kwargs)
    elif method == "M5_ASO":
        from baselines.aso_binary import ASOBinary
        return ASOBinary(evaluator, n_features, max_fes=budget, seed=seed, **kwargs)
    elif method == "M6_AOS":
        from baselines.aos_binary import AOSBinary
        return AOSBinary(evaluator, n_features, max_fes=budget, seed=seed, **kwargs)
    else:
        raise ValueError(f"Unknown method: {method}")


def _run_nested_cv(dataset_id, subspace_regime, p_level, method, seed,
                   out_dir, outer_cv_folds=5, inner_cv_folds=3, budget=1000):
    """Single run with outer CV loop. Returns list of per-fold result dicts."""

    ds = get_dataset(dataset_id)
    X, y = load_placeholder_features(dataset_id, seed=seed)

    sub_rng = np.random.default_rng(seed)
    random_order = sub_rng.permutation(X.shape[1])

    skf_outer = StratifiedKFold(n_splits=outer_cv_folds, shuffle=True,
                                random_state=seed)

    fold_results = []
    for outer_fold, (train_idx, test_idx) in enumerate(skf_outer.split(X, y)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Preprocessing: fit on train only, transform both
        X_train_pp, preprocessor = preprocess_train(X_train, y_train)
        X_test_pp = preprocess_transform(preprocessor, X_test)

        # Subspace order based on train only
        if subspace_regime == "ranked":
            F, _ = f_classif(X_train_pp, y_train)
            order = np.argsort(-F)
        else:
            order = random_order

        if isinstance(p_level, int) and p_level < X_train_pp.shape[1]:
            selected = order[:p_level]
        else:
            selected = order

        X_train_sub = X_train_pp[:, selected]
        X_test_sub = X_test_pp[:, selected]

        # Inner CV fitness evaluation
        evaluator = FitnessEvaluator(X_train_sub, y_train,
                                     n_splits=inner_cv_folds)

        n_features_sub = X_train_sub.shape[1]
        optimizer = _get_optimizer(method, evaluator, n_features_sub,
                                   budget=budget, seed=seed * 100 + outer_fold)

        start = time.time()
        best_pos, best_fit = optimizer.run()
        elapsed = time.time() - start

        # Decode mask and evaluate on outer test
        mask = decode_mask(best_pos, method)
        outer_auc = evaluate_on_outer(X_train_sub, X_test_sub,
                                      y_train, y_test, mask)
        n_selected = int(mask.sum())

        fold_results.append({
            "dataset": dataset_id,
            "subspace": subspace_regime,
            "p_level": str(p_level),
            "method": method,
            "seed": seed,
            "outer_fold": outer_fold,
            "inner_best_fitness": best_fit,
            "outer_auc": outer_auc,
            "n_selected": n_selected,
            "fes_count": optimizer.fes_count,
            "elapsed": elapsed,
        })

    return fold_results


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

    total_combos = len(tasks)
    total_folds = total_combos * matrix["outer_cv_folds"]
    print(f"Phase-2 mode={mode}: {total_combos} combos × {matrix['outer_cv_folds']} folds = {total_folds} evaluations")
    print(f"  datasets          : {matrix['datasets']}")
    print(f"  subspace_regimes  : {matrix['subspace_regimes']}")
    print(f"  p_levels          : {matrix['p_levels']}")
    print(f"  methods           : {matrix['methods']}")
    print(f"  seeds             : {len(matrix['seeds'])}")
    print(f"  fitness_budget    : {matrix['fitness_budget']}")
    print(f"  outer_cv_folds    : {matrix['outer_cv_folds']}")
    print(f"  outer_cv_repeats  : {matrix['outer_cv_repeats']}")

    max_workers = max_workers or min(8, os.cpu_count() or 1)
    print(f"  workers           : {max_workers}")

    rows = []
    completed = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        fut_map = {}
        for ds, ss, p, m, s in tasks:
            fut = executor.submit(
                _run_nested_cv, ds, ss, p, m, s, out_dir,
                outer_cv_folds=matrix["outer_cv_folds"],
                inner_cv_folds=matrix["inner_cv_folds"],
                budget=matrix["fitness_budget"],
            )
            fut_map[fut] = (ds, ss, p, m, s)

        for fut in as_completed(fut_map):
            ds, ss, p, m, s = fut_map[fut]
            try:
                fold_results = fut.result()
                rows.extend(fold_results)
                m_short = METHOD_SHORT.get(m, m)
                n_folds = len(fold_results)
                best_fit = fold_results[0].get("inner_best_fitness", "?")
                print(f"  [{completed + 1}/{total_combos}] {ds} {ss} p={p} {m_short} "
                      f"seed={s}: {n_folds} folds fit={best_fit:.6e}")

            except Exception as e:
                print(f"  [{completed + 1}/{total_combos}] {ds} {ss} p={p} {m} seed={s}: ERROR {e}")
                for fold in range(matrix["outer_cv_folds"]):
                    rows.append({
                        "dataset": ds, "subspace": ss, "p_level": str(p),
                        "method": m, "seed": s, "outer_fold": fold,
                        "inner_best_fitness": None, "outer_auc": None,
                        "n_selected": None, "fes_count": None, "elapsed": None,
                    })

            completed += 1
            if completed % 50 == 0:
                ckpt_path = os.path.join(out_dir, f"checkpoint_{mode}_{completed}.json")
                with open(ckpt_path, "w") as f:
                    json.dump({"completed": completed, "total": total_combos,
                               "rows": rows}, f, indent=2)

    df = pd.DataFrame(rows)
    out_name = f"phase2_{mode}_results_raw.csv"
    out_path = os.path.join(out_dir, out_name)
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} rows to {out_path}")

    return df


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "presmoke"
    run_phase2(mode=mode)
