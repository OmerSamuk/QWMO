import os
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from analysis.stats import cliffs_delta


VARIANT_ORDER = ["V0", "V1", "V2", "V3"]
COMPARISONS = [
    ("V3", "V0"),
    ("V3", "V1"),
    ("V3", "V2"),
    ("V2", "V1"),
    ("V1", "V0"),
]
FUNCTION_NAMES = {5: "Schwefel", 10: "Rastrigin", 20: "Hybrid", 28: "Composition"}


def load_results(results_path):
    df = pd.read_csv(results_path)
    df["function"] = df["function"].astype(int)
    return df


def compute_stats(results_path, out_dir="results/phase1"):
    df = load_results(results_path)
    functions = sorted(df["function"].unique())

    wilcoxon_rows = []
    effect_rows = []
    summary_rows = []

    for func_id in functions:
        func_df = df[df["function"] == func_id]

        for variant in VARIANT_ORDER:
            vdf = func_df[func_df["variant_id"] == variant]
            fits = vdf["best_fitness"].dropna().values
            if len(fits) == 0:
                continue
            summary_rows.append({
                "function": func_id,
                "function_name": FUNCTION_NAMES.get(func_id, f"F{func_id}"),
                "variant": variant,
                "mean": float(np.mean(fits)),
                "std": float(np.std(fits)),
                "median": float(np.median(fits)),
                "min": float(np.min(fits)),
                "max": float(np.max(fits)),
                "best": float(np.min(fits)),
                "worst": float(np.max(fits)),
                "n_runs": len(fits),
            })

        for ctrl, comp in COMPARISONS:
            ctrl_fits = func_df[func_df["variant_id"] == ctrl]["best_fitness"].dropna().values
            comp_fits = func_df[func_df["variant_id"] == comp]["best_fitness"].dropna().values
            min_len = min(len(ctrl_fits), len(comp_fits))
            if min_len < 5:
                continue

            ctrl_fits = ctrl_fits[:min_len]
            comp_fits = comp_fits[:min_len]

            try:
                w_stat, w_p = wilcoxon(ctrl_fits, comp_fits)
            except (ValueError, RuntimeError):
                w_stat, w_p = None, 1.0

            cd = cliffs_delta(ctrl_fits, comp_fits)

            wilcoxon_rows.append({
                "function": func_id,
                "function_name": FUNCTION_NAMES.get(func_id, f"F{func_id}"),
                "comparison": f"{ctrl} vs {comp}",
                "control": ctrl,
                "competitor": comp,
                "wilcoxon_stat": w_stat,
                "wilcoxon_p": w_p,
                "significant": bool(w_p < 0.05) if w_p is not None else False,
                "n_runs": min_len,
            })

            effect_rows.append({
                "function": func_id,
                "function_name": FUNCTION_NAMES.get(func_id, f"F{func_id}"),
                "comparison": f"{ctrl} vs {comp}",
                "control": ctrl,
                "competitor": comp,
                "control_mean": float(np.mean(ctrl_fits)),
                "competitor_mean": float(np.mean(comp_fits)),
                "median_improvement_pct": float(
                    (np.mean(ctrl_fits) - np.mean(comp_fits)) / abs(np.mean(comp_fits)) * 100
                ) if abs(np.mean(comp_fits)) > 1e-12 else 0.0,
                "Cliffs_delta": cd["Cliffs_delta"],
                "effect_size": cd["interpretation"],
            })

    summary_df = pd.DataFrame(summary_rows)
    wilcoxon_df = pd.DataFrame(wilcoxon_rows)
    effect_df = pd.DataFrame(effect_rows)

    os.makedirs(out_dir, exist_ok=True)
    summary_df.to_csv(os.path.join(out_dir, "phase1_summary_table.csv"), index=False)
    wilcoxon_df.to_csv(os.path.join(out_dir, "phase1_wilcoxon_results.csv"), index=False)
    effect_df.to_csv(os.path.join(out_dir, "phase1_effect_sizes.csv"), index=False)

    print(f"Summary table: {len(summary_df)} rows")
    print(f"Wilcoxon results: {len(wilcoxon_df)} rows")
    print(f"Effect sizes: {len(effect_df)} rows")

    for _, row in wilcoxon_df.iterrows():
        sig = "SIGNIFICANT" if row["significant"] else "n.s."
        print(f"  F{int(row['function'])} {row['comparison']}: p={row['wilcoxon_p']:.4e} [{sig}]")

    for _, row in effect_df.iterrows():
        print(f"  F{int(row['function'])} {row['comparison']}: "
              f"delta={row['Cliffs_delta']:.4f} ({row['effect_size']}) "
              f"improvement={row['median_improvement_pct']:.2f}%")

    return summary_df, wilcoxon_df, effect_df


if __name__ == "__main__":
    compute_stats("results/phase1/phase1_results_raw.csv")
