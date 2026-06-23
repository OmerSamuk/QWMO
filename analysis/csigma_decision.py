import os
import sys
import numpy as np
import pandas as pd

RESULTS_DIR = "results/csigma_diagnostic"
FUNCTION_NAMES = {1: "Sphere", 5: "Schwefel", 10: "Rastrigin"}
TOLERANCE = 1e-12


def load_or_die(path):
    if not os.path.exists(path):
        print(f"ERROR: {path} not found. Run csigma_stats first.")
        sys.exit(1)
    return pd.read_csv(path)


def compute_decision(results_dir=RESULTS_DIR):
    summary = load_or_die(os.path.join(results_dir, "csigma_summary_table.csv"))
    wilcoxon = load_or_die(os.path.join(results_dir, "csigma_wilcoxon_results.csv"))
    effect = load_or_die(os.path.join(results_dir, "csigma_effect_sizes.csv"))
    mech = pd.DataFrame()
    mech_path = os.path.join(results_dir, "csigma_mechanism_summary.csv")
    if os.path.exists(mech_path):
        mech = pd.read_csv(mech_path)

    evidence = {}

    for func_id in [1, 5, 10]:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        f_summ = summary[summary["function"] == func_id]
        f_wilc = wilcoxon[wilcoxon["function"] == func_id]
        f_eff = effect[effect["function"] == func_id]
        f_mech = mech[mech["function"] == func_id] if not mech.empty else pd.DataFrame()

        evidence[func_id] = {}
        evidence[func_id]["name"] = fname
        evidence[func_id]["mean_fitness"] = dict(
            zip(f_summ["variant"], f_summ["mean"])
        ) if not f_summ.empty else {}
        evidence[func_id]["comparisons"] = {}
        evidence[func_id]["mechanism"] = {}

        for _, row in f_wilc.iterrows():
            ctrl = row["comparison"]
            evidence[func_id]["comparisons"][ctrl] = {
                "p": row["wilcoxon_p"],
                "significant": row["significant"],
            }

        for _, row in f_eff.iterrows():
            ctrl = row["comparison"]
            if ctrl not in evidence[func_id]["comparisons"]:
                evidence[func_id]["comparisons"][ctrl] = {}
            evidence[func_id]["comparisons"][ctrl]["cliffs_delta"] = row["Cliffs_delta"]
            evidence[func_id]["comparisons"][ctrl]["effect_size"] = row["effect_size"]
            evidence[func_id]["comparisons"][ctrl]["median_improvement_pct"] = row["median_improvement_pct"]

        if not f_mech.empty:
            for _, row in f_mech.iterrows():
                evidence[func_id]["mechanism"][row["variant"]] = {
                    "mean_sigma": row.get("mean_sigma", 0),
                    "mean_k": row.get("mean_k", 0),
                    "stagnant_ratio": row.get("stagnant_ratio", 0),
                    "mean_tau": row.get("mean_tau", 0),
                }

    sphere = evidence.get(1, {})
    rastrigin = evidence.get(10, {})
    schwefel = evidence.get(5, {})

    sphere_csigma_vs_full = sphere.get("comparisons", {}).get("Csigma vs Full-old", {})
    sphere_csigma_vs_eold = sphere.get("comparisons", {}).get("Csigma vs E-old", {})

    rast_csigma_vs_full = rastrigin.get("comparisons", {}).get("Csigma vs Full-old", {})
    rast_csigma_vs_eold = rastrigin.get("comparisons", {}).get("Csigma vs E-old", {})

    schw_csigma_vs_eold = schwefel.get("comparisons", {}).get("Csigma vs E-old", {})
    schw_eold_vs_full = schwefel.get("comparisons", {}).get("E-old vs Full-old", {})

    sphere_improves = (
        sphere_csigma_vs_full.get("significant", False) or
        sphere_csigma_vs_eold.get("significant", False) or
        sphere_csigma_vs_full.get("cliffs_delta", 0) > 0.5
    )

    rastrigin_preserved = not (
        rast_csigma_vs_full.get("significant", False) and
        rast_csigma_vs_full.get("cliffs_delta", 0) < -0.3
    )

    schwefel_not_worse = not (
        schw_csigma_vs_eold.get("significant", False) and
        schw_csigma_vs_eold.get("cliffs_delta", 0) < -0.3
    )

    eold_equals_full = (
        not schw_eold_vs_full.get("significant", True)
    )

    csigma_beats_eold = (
        sphere_csigma_vs_eold.get("significant", False) or
        rast_csigma_vs_eold.get("significant", False) or
        sphere_csigma_vs_eold.get("cliffs_delta", 0) > 0.3 or
        rast_csigma_vs_eold.get("cliffs_delta", 0) > 0.3
    )

    csigma_beats_full = (
        sphere_csigma_vs_full.get("significant", False) or
        rast_csigma_vs_full.get("significant", False) or
        sphere_csigma_vs_full.get("cliffs_delta", 0) > 0.3 or
        rast_csigma_vs_full.get("cliffs_delta", 0) > 0.3
    )

    if sphere_improves and rastrigin_preserved and schwefel_not_worse:
        decision = "A"
        reasoning = (
            "QWMO-Csigma satisfies all strong success criteria: "
            "Sphere improves, Rastrigin preserved, Schwefel not degraded."
        )
        scenario_text = (
            "QWMO-C hattı devam eder. "
            "Improvement-aware sigma, time-decay orbital mekanizmasına "
            "üstünlük sağlamıştır."
        )
    elif sphere_improves and not rastrigin_preserved:
        decision = "B"
        reasoning = (
            "Sphere improves but Rastrigin degraded. "
            "Escape-Sigma interaction likely."
        )
        scenario_text = (
            "Escape-Sigma etkileşimi araştırılır. "
            "Rastrigin bozulması Escape ile sigma etkileşiminden kaynaklanıyor olabilir."
        )
    elif not sphere_improves:
        decision = "C"
        reasoning = (
            "QWMO-Csigma fails to improve on Sphere. "
            "Improvement-aware sigma does not provide meaningful benefit."
        )
        scenario_text = (
            "QWMO-C başarısız kabul edilir. "
            "Improvement-aware sigma, time-decay orbital mekanizmasına "
            "üstünlük sağlayamamıştır."
        )
    elif eold_equals_full:
        # D check: only if Cσ failed (otherwise A takes priority)
        if not csigma_beats_eold and not csigma_beats_full:
            decision = "D"
            reasoning = (
                "QWMO-E-old ≈ QWMO-Full-old suggests Pauli is unnecessary "
                "in continuous domain. QWMO-Csigma also fails to outperform."
            )
            scenario_text = (
                "Pauli continuous-domain için gereksizdir. "
                "QWMO-Csigma da ek fayda sağlamamıştır."
            )
        else:
            decision = "E"
            reasoning = (
                "QWMO-Csigma beats E-old but cannot beat Full-old. "
                "Signal is weak; additional evidence required."
            )
            scenario_text = (
                "Sinyal zayıftır. QWMO-C hattının devamı için ek kanıt gerekir."
            )
    elif csigma_beats_eold and not csigma_beats_full:
        decision = "E"
        reasoning = (
            "QWMO-Csigma beats E-old but cannot beat Full-old. "
            "Signal is weak; additional evidence required."
        )
        scenario_text = (
            "Sinyal zayıftır. QWMO-C hattının devamı için ek kanıt gerekir."
        )
    else:
        decision = "C"
        reasoning = (
            "No scenario criteria clearly met. "
            "QWMO-Csigma does not demonstrate sufficient advantage."
        )
        scenario_text = (
            "QWMO-C başarısız kabul edilir. "
            "Hiçbir senaryo kriteri net olarak karşılanmamıştır."
        )

    report = f"""# QWMO-Csigma Diagnostic Decision Report

## 1. Amaç

Yeni improvement-aware sigma mekanizmasının (QWMO-Cσ) time-decay orbital mekanizmasına
performans üstünlüğü sağlayıp sağlamadığını belirlemek.

## 2. Deney Protokolü

- **Fonksiyonlar:** F1 (Sphere), F5 (Schwefel), F10 (Rastrigin)
- **Varyantlar:** Full-old (Pauli+Escape), E-old (Escape only), Csigma (improvement-aware sigma)
- **Boyut:** D=30
- **Popülasyon:** N=50
- **FE Bütçesi:** Tmax=300000
- **Run:** 30 bağımsız run × 3 fonksiyon × 3 varyant = 270 run
- **İstatistik:** Wilcoxon signed-rank (p<0.05), Cliff's delta

## 3. Fitness Sonuçları
"""
    for func_id in [1, 5, 10]:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        report += f"\n### F{func_id} ({fname})\n\n"
        report += "| Varyant | Mean | Std | Median | Best |\n"
        report += "|---|---|---|---|---|\n"
        for variant in ["Full-old", "E-old", "Csigma"]:
            r = evidence.get(func_id, {}).get("mean_fitness", {}).get(variant)
            if r is not None:
                f_summ = summary[summary["function"] == func_id]
                vrow = f_summ[f_summ["variant"] == variant]
                if not vrow.empty:
                    report += f"| {variant} | {vrow['mean'].values[0]:.4e} | {vrow['std'].values[0]:.4e} | {vrow['median'].values[0]:.4e} | {vrow['best'].values[0]:.4e} |\n"

    report += "\n## 4. Istatistiksel Analiz\n"
    for func_id in [1, 5, 10]:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        report += f"\n### F{func_id} ({fname})\n\n"
        report += "| Comparison | p-value | Significant | Cliff's delta | Effect Size | Median Improvement (%) |\n"
        report += "|---|---|---|---|---|---|\n"
        for comp in ["Csigma vs Full-old", "Csigma vs E-old", "E-old vs Full-old"]:
            c = evidence.get(func_id, {}).get("comparisons", {}).get(comp, {})
            if c:
                report += f"| {comp} | {c.get('p', 'N/A')} | {c.get('significant', 'N/A')} | {c.get('cliffs_delta', 'N/A')} | {c.get('effect_size', 'N/A')} | {c.get('median_improvement_pct', 'N/A')} |\n"

    report += "\n## 5. Mekanizma Analizi\n"
    for func_id in [1, 5, 10]:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        csigma = evidence.get(func_id, {}).get("mechanism", {}).get("Csigma", {})
        report += f"\n### F{func_id} ({fname})\n"
        if csigma:
            report += f"- Mean sigma: {csigma.get('mean_sigma', 'N/A')}\n"
            report += f"- Mean k (stagnation): {csigma.get('mean_k', 'N/A')}\n"
            report += f"- Stagnant ratio: {csigma.get('stagnant_ratio', 'N/A')}\n"
            report += f"- Mean tau: {csigma.get('mean_tau', 'N/A')}\n"

    report += f"""
## 6. Karar

**Karar: {decision}**

{reasoning}

## 7. Senaryo

{scenario_text}

---

## 8. Karar Kriterleri

| Kriter | Sonuc |
|--------|-------|
| Sphere iyilesir | {'Evet' if sphere_improves else 'Hayir'} |
| Rastrigin korunur | {'Evet' if rastrigin_preserved else 'Hayir'} |
| Schwefel korunur | {'Evet' if schwefel_not_worse else 'Hayir'} |
| E-old ≈ Full-old (Pauli gereksiz) | {'Evet' if eold_equals_full else 'Hayir'} |
| Csigma > E-old | {'Evet' if csigma_beats_eold else 'Hayir'} |
| Csigma > Full-old | {'Evet' if csigma_beats_full else 'Hayir'} |

| Senaryo | Karar |
|---------|-------|
| A (C hatti devam) | {'PASS' if sphere_improves and rastrigin_preserved and schwefel_not_worse else 'FAIL'} |
| B (Escape-Sigma etkilesimi) | {'PASS' if sphere_improves and not rastrigin_preserved else 'FAIL'} |
| C (C basarisiz) | {'PASS' if not sphere_improves else 'FAIL'} |
| D (Pauli gereksiz) | {'PASS' if eold_equals_full else 'FAIL'} |
| E (Sinyal zayif) | {'PASS' if csigma_beats_eold and not csigma_beats_full else 'FAIL'} |
"""

    report_path = os.path.join(results_dir, "csigma_decision_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Decision report written to {report_path}")
    print(f"Decision: {decision}")
    return decision


if __name__ == "__main__":
    compute_decision()
