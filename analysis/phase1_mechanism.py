import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


FUNCTION_NAMES = {5: "Schwefel", 10: "Rastrigin", 20: "Hybrid", 28: "Composition"}
VARIANT_COLORS = {"V0": "#888888", "V1": "#2196F3", "V2": "#FF9800", "V3": "#F44336"}
WINDOW = 5


def load_iteration_metrics(iter_dir="results/phase1/iteration_metrics"):
    files = [f for f in os.listdir(iter_dir) if f.endswith("_iter.csv")]
    dfs = []
    for f in sorted(files):
        df = pd.read_csv(os.path.join(iter_dir, f))
        dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def compute_mechanism_analysis(iter_dir="results/phase1/iteration_metrics",
                                out_dir="results/phase1"):
    df = load_iteration_metrics(iter_dir)
    if df.empty:
        print("No iteration metrics found.")
        return

    os.makedirs(os.path.join(out_dir, "phase1_mechanism_summary.csv"), exist_ok=True)
    plot_dir = os.path.join(out_dir, "phase1_plots")
    for sub in ["epsilon", "collision", "escape", "diversity", "correlation"]:
        os.makedirs(os.path.join(plot_dir, sub), exist_ok=True)

    functions = sorted(df["function_id"].unique())
    variants = ["V0", "V1", "V2", "V3"]

    mechanism_rows = []

    for func_id in functions:
        fdf = df[df["function_id"] == func_id]
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        print(f"\n--- F{func_id} ({fname}) ---")

        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(f"F{func_id} ({fname}) — Phase-1 Mechanism Analysis", fontsize=14)

        for vidx, variant in enumerate(variants):
            vdf = fdf[fdf["variant_id"] == variant]
            if vdf.empty:
                continue

            avg = vdf.groupby("iteration").mean(numeric_only=True).reset_index()

            t = avg["iteration"].values

            if "epsilon_value" in avg.columns and avg["epsilon_value"].max() > 0:
                axes[0, 0].plot(t, avg["epsilon_value"],
                                label=variant, color=VARIANT_COLORS.get(variant),
                                alpha=0.8)
            axes[0, 1].plot(t, avg["collision_count"],
                            label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)
            axes[0, 2].plot(t, avg["escape_triggered_count"],
                            label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)
            axes[1, 0].plot(t, avg["population_diversity_center"],
                            label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)
            if "epsilon_to_mean_knn_ratio" in avg.columns:
                axes[1, 1].plot(t, avg["epsilon_to_mean_knn_ratio"],
                                label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)

            # Escape success ratio
            total_esc = avg.get("escape_triggered_count", pd.Series(0))
            succ_esc = avg.get("escape_success_count", pd.Series(0))
            esc_ratio = np.where(total_esc > 0, succ_esc / total_esc, 0)
            axes[1, 2].plot(t, esc_ratio,
                            label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)

            # Mechanism summary
            v_avg = vdf.mean(numeric_only=True)
            mechanism_rows.append({
                "function": func_id,
                "function_name": fname,
                "variant": variant,
                "mean_epsilon": v_avg.get("epsilon_value", 0),
                "epsilon_saturation_ratio": (
                    (vdf["epsilon_value"] >= vdf["epsilon_value"].max() - 1e-9).mean()
                    if "epsilon_value" in vdf.columns and vdf["epsilon_value"].max() > 0
                    else 0
                ),
                "mean_collision": v_avg.get("collision_count", 0),
                "mean_displacement": v_avg.get("displacement_count", 0),
                "total_escape_triggered": vdf["escape_triggered_count"].sum(),
                "total_escape_success": vdf["escape_success_count"].sum(),
                "total_escape_failure": vdf["escape_failure_count"].sum(),
                "escape_success_ratio": (
                    vdf["escape_success_count"].sum() / vdf["escape_triggered_count"].sum()
                    if vdf["escape_triggered_count"].sum() > 0 else 0
                ),
                "total_pauli_success": vdf["pauli_success_count"].sum(),
                "total_pauli_failure": vdf["pauli_failure_count"].sum(),
                "mean_diversity_center": v_avg.get("population_diversity_center", 0),
                "mean_knn_distance": v_avg.get("mean_knn_distance", 0),
            })

        axes[0, 0].set_xlabel("Iteration")
        axes[0, 0].set_ylabel("epsilon")
        axes[0, 0].legend()
        axes[0, 0].set_title("Epsilon(t)")

        axes[0, 1].set_xlabel("Iteration")
        axes[0, 1].set_ylabel("Collisions")
        axes[0, 1].legend()
        axes[0, 1].set_title("Collisions per Iteration")

        axes[0, 2].set_xlabel("Iteration")
        axes[0, 2].set_ylabel("Escape Triggered")
        axes[0, 2].legend()
        axes[0, 2].set_title("Escapes per Iteration")

        axes[1, 0].set_xlabel("Iteration")
        axes[1, 0].set_ylabel("Diversity (Center)")
        axes[1, 0].legend()
        axes[1, 0].set_title("Population Diversity")

        axes[1, 1].set_xlabel("Iteration")
        axes[1, 1].set_ylabel("Epsilon / mean_kNN")
        axes[1, 1].legend()
        axes[1, 1].set_title("Epsilon / mean_kNN Ratio")

        axes[1, 2].set_xlabel("Iteration")
        axes[1, 2].set_ylabel("Escape Success Ratio")
        axes[1, 2].legend()
        axes[1, 2].set_title("Escape Success / Total")

        plt.tight_layout()
        fig_path = os.path.join(plot_dir, f"F{func_id}_mechanism.png")
        fig.savefig(fig_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Plot saved: {fig_path}")

    mech_df = pd.DataFrame(mechanism_rows)
    mech_path = os.path.join(out_dir, "phase1_mechanism_summary.csv")
    mech_df.to_csv(mech_path, index=False)
    print(f"\nMechanism summary saved: {mech_path}")
    print(mech_df.to_string(index=False))

    return mech_df


def chain_analysis(iter_dir="results/phase1/iteration_metrics",
                   event_dir="results/phase1/raw_events",
                   out_dir="results/phase1"):
    import glob
    event_files = sorted(glob.glob(os.path.join(event_dir, "*_events.csv")))
    if not event_files:
        print("No event files found.")
        return

    chain_rows = []

    for ef in event_files:
        ev_df = pd.read_csv(ef)
        if ev_df.empty:
            continue

        func_id = ev_df["function_id"].iloc[0]
        variant = ev_df["variant_id"].iloc[0]
        seed = ev_df["seed"].iloc[0]

        base = ef.replace("_events.csv", "_iter.csv").replace("raw_events", "iteration_metrics")
        if not os.path.exists(base):
            continue
        it_df = pd.read_csv(base)
        if it_df.empty:
            continue

        it_df = it_df.sort_values("iteration")
       
        collision_iters = set(it_df[it_df["collision_count"] > 0]["iteration"].tolist())
        escape_iters = set(ev_df[ev_df["event_type"] == "escape"]["iteration"].tolist())
 
        total_iters = it_df["iteration"].tolist()
        improvement_iters = set()
        for i in range(1, len(it_df)):
            if it_df["best_fitness"].iloc[i] < it_df["best_fitness"].iloc[i - 1]:
                improvement_iters.add(it_df["iteration"].iloc[i])

        chain_rows.append({
            "function": func_id,
            "function_name": FUNCTION_NAMES.get(func_id, f"F{func_id}"),
            "variant": variant,
            "seed": seed,
            "P_improve_after_collision": _p_given(
                improvement_iters, collision_iters, total_iters, WINDOW),
            "P_improve_after_escape": _p_given(
                improvement_iters, escape_iters, total_iters, WINDOW),
            "P_improve_after_both": _p_given_both(
                improvement_iters, collision_iters, escape_iters, total_iters, WINDOW),
            "P_improve_without_events": _p_without(
                improvement_iters, collision_iters, escape_iters, total_iters, WINDOW),
        })

    chain_df = pd.DataFrame(chain_rows)
    if not chain_df.empty:
        avg = chain_df.groupby(["function", "variant"]).mean(numeric_only=True).reset_index()
        print("\n--- Chain Analysis (averaged) ---")
        print(avg.to_string(index=False))

    return chain_df


def _p_given(improvement_iters, event_iters, total_iters, window):
    if len(total_iters) == 0:
        return 0.0
    numerator = 0
    denominator = 0
    for it in total_iters:
        if it in event_iters:
            denominator += 1
            lookahead = set(range(it + 1, min(it + window + 1, max(total_iters) + 1)))
            if improvement_iters & lookahead:
                numerator += 1
    return numerator / denominator if denominator > 0 else 0.0


def _p_given_both(improvement_iters, collision_iters, escape_iters, total_iters, window):
    both = collision_iters & escape_iters
    return _p_given(improvement_iters, both, total_iters, window)


def _p_without(improvement_iters, collision_iters, escape_iters, total_iters, window):
    none_iters = set(total_iters) - collision_iters - escape_iters
    if len(none_iters) == 0:
        return 0.0
    numerator = 0
    for it in none_iters:
        lookahead = set(range(it + 1, min(it + window + 1, max(total_iters) + 1)))
        if improvement_iters & lookahead:
            numerator += 1
    return numerator / len(none_iters)


if __name__ == "__main__":
    compute_mechanism_analysis()
    chain_analysis()
