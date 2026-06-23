import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


FUNCTION_NAMES = {1: "Sphere", 5: "Schwefel", 10: "Rastrigin"}
VARIANT_COLORS = {
    "Full-old": "#888888",
    "E-old": "#2196F3",
    "Csigma": "#4CAF50",
}
WINDOW = 5


def load_iteration_metrics(iter_dir="results/csigma_diagnostic/iteration_metrics"):
    files = [f for f in os.listdir(iter_dir) if f.endswith("_iter.csv")]
    dfs = []
    for f in sorted(files):
        df = pd.read_csv(os.path.join(iter_dir, f))
        dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def compute_mechanism_analysis(iter_dir="results/csigma_diagnostic/iteration_metrics",
                                out_dir="results/csigma_diagnostic"):
    df = load_iteration_metrics(iter_dir)
    if df.empty:
        print("No iteration metrics found.")
        return

    os.makedirs(out_dir, exist_ok=True)
    plot_dir = os.path.join(out_dir, "csigma_plots")
    for sub in ["sigma", "escape", "k_diagnostics", "convergence"]:
        os.makedirs(os.path.join(plot_dir, sub), exist_ok=True)

    functions = sorted(df["function_id"].unique())
    variants = ["Full-old", "E-old", "Csigma"]

    mechanism_rows = []

    for func_id in functions:
        fdf = df[df["function_id"] == func_id]
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        print(f"\n--- F{func_id} ({fname}) ---")

        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(f"F{func_id} ({fname}) — QWMO-Csigma Mechanism Analysis", fontsize=14)

        for vidx, variant in enumerate(variants):
            vdf = fdf[fdf["variant_id"] == variant]
            if vdf.empty:
                continue

            avg = vdf.groupby("iteration").mean(numeric_only=True).reset_index()
            t = avg["iteration"].values

            axes[0, 0].plot(t, avg["best_fitness"],
                            label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)
            if "sigma_mean" in avg.columns and avg["sigma_mean"].notna().any():
                axes[0, 1].plot(t, avg["sigma_mean"],
                                label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)
            axes[0, 2].plot(t, avg["escape_triggered_count"],
                            label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)
            axes[1, 0].plot(t, avg["population_diversity_center"],
                            label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)
            total_esc = avg.get("escape_triggered_count", pd.Series(0))
            succ_esc = avg.get("escape_success_count", pd.Series(0))
            esc_ratio = np.where(total_esc > 0, succ_esc / total_esc, 0)
            axes[1, 1].plot(t, esc_ratio,
                            label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)

            if "k_mean" in avg.columns and avg["k_mean"].notna().any():
                axes[1, 2].plot(t, avg["k_mean"],
                                label=variant, color=VARIANT_COLORS.get(variant), alpha=0.8)

            v_avg = vdf.mean(numeric_only=True)
            row = {
                "function": func_id,
                "function_name": fname,
                "variant": variant,
                "mean_best_fitness": v_avg.get("best_fitness", 0),
                "mean_escape_triggered": v_avg.get("escape_triggered_count", 0),
            }
            if "sigma_mean" in v_avg.index:
                row["mean_sigma"] = v_avg.get("sigma_mean", 0)
                row["median_sigma"] = v_avg.get("sigma_median", 0)
                row["sigma_min"] = v_avg.get("sigma_min", 0)
                row["sigma_max"] = v_avg.get("sigma_max", 0)
                row["mean_k"] = v_avg.get("k_mean", 0)
                row["stagnant_ratio"] = v_avg.get("k_stagnant_count", 0) / max(len(vdf), 1)
                row["mean_tau"] = v_avg.get("tau_value", 0)
            mechanism_rows.append(row)

        axes[0, 0].set_xlabel("Iteration")
        axes[0, 0].set_ylabel("Best Fitness")
        axes[0, 0].legend()
        axes[0, 0].set_title("Convergence (Best-So-Far)")
        axes[0, 0].set_yscale("log")

        axes[0, 1].set_xlabel("Iteration")
        axes[0, 1].set_ylabel("Mean sigma")
        axes[0, 1].legend()
        axes[0, 1].set_title("Mean Sigma (Csigma only)")

        axes[0, 2].set_xlabel("Iteration")
        axes[0, 2].set_ylabel("Escape Triggered")
        axes[0, 2].legend()
        axes[0, 2].set_title("Escapes per Iteration")

        axes[1, 0].set_xlabel("Iteration")
        axes[1, 0].set_ylabel("Diversity (Center)")
        axes[1, 0].legend()
        axes[1, 0].set_title("Population Diversity")

        axes[1, 1].set_xlabel("Iteration")
        axes[1, 1].set_ylabel("Escape Success Ratio")
        axes[1, 1].legend()
        axes[1, 1].set_title("Escape Success / Total")

        axes[1, 2].set_xlabel("Iteration")
        axes[1, 2].set_ylabel("Mean k_i")
        axes[1, 2].legend()
        axes[1, 2].set_title("Mean Stagnation Counter (Csigma only)")

        plt.tight_layout()
        fig_path = os.path.join(plot_dir, f"F{func_id}_mechanism.png")
        fig.savefig(fig_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Plot saved: {fig_path}")

    mech_df = pd.DataFrame(mechanism_rows)
    mech_path = os.path.join(out_dir, "csigma_mechanism_summary.csv")
    mech_df.to_csv(mech_path, index=False)
    print(f"\nMechanism summary saved: {mech_path}")
    print(mech_df.to_string(index=False))

    return mech_df


if __name__ == "__main__":
    compute_mechanism_analysis()
