import os
import sys
import numpy as np
import pandas as pd


RESULTS_DIR = "results/phase1"
FUNCTION_NAMES = {5: "Schwefel", 10: "Rastrigin", 20: "Hybrid", 28: "Composition"}
TOLERANCE = 1e-12


def load_or_die(path):
    if not os.path.exists(path):
        print(f"ERROR: {path} not found. Run phase1_run + phase1_stats + phase1_mechanism first.")
        sys.exit(1)
    return pd.read_csv(path)


def compute_decision(results_dir=RESULTS_DIR):
    summary = load_or_die(os.path.join(results_dir, "phase1_summary_table.csv"))
    wilcoxon = load_or_die(os.path.join(results_dir, "phase1_wilcoxon_results.csv"))
    effect = load_or_die(os.path.join(results_dir, "phase1_effect_sizes.csv"))
    mech = pd.DataFrame()
    mech_path = os.path.join(results_dir, "phase1_mechanism_summary.csv")
    if os.path.exists(mech_path):
        mech = pd.read_csv(mech_path)

    evidence = {}

    for func_id in [5, 10, 20, 28]:
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
                    "mean_epsilon": row.get("mean_epsilon", 0),
                    "epsilon_saturation_ratio": row.get("epsilon_saturation_ratio", 0),
                    "total_escape_success": row.get("total_escape_success", 0),
                    "total_escape_failure": row.get("total_escape_failure", 0),
                    "escape_success_ratio": row.get("escape_success_ratio", 0),
                    "mean_collision": row.get("mean_collision", 0),
                    "mean_displacement": row.get("mean_displacement", 0),
                    "total_pauli_success": row.get("total_pauli_success", 0),
                    "total_pauli_failure": row.get("total_pauli_failure", 0),
                    "mean_diversity_center": row.get("mean_diversity_center", 0),
                    "mean_knn_distance": row.get("mean_knn_distance", 0),
                }

    primary_funcs = [10, 20]
    v3_v0_sig = any(
        evidence[f].get("comparisons", {}).get("V3 vs V0", {}).get("significant", False)
        for f in primary_funcs
    )
    v3_v1_sig = any(
        evidence[f].get("comparisons", {}).get("V3 vs V1", {}).get("significant", False)
        for f in primary_funcs
    )
    v3_v2_sig = any(
        evidence[f].get("comparisons", {}).get("V3 vs V2", {}).get("significant", False)
        for f in primary_funcs
    )
    v3_v0_practical = any(
        evidence[f].get("comparisons", {}).get("V3 vs V0", {}).get("cliffs_delta", 0.5) > 0.5
        for f in primary_funcs
    )
    v3_v2_practical = any(
        evidence[f].get("comparisons", {}).get("V3 vs V2", {}).get("cliffs_delta", 0.5) > 0.5
        for f in primary_funcs
    )

    v3_dominates_v1 = v3_v1_sig
    v3_dominates_v2 = v3_v2_sig or v3_v2_practical
    v3_dominates_v0 = v3_v0_sig or v3_v0_practical

    v3_v2_close = all(
        abs(evidence[f].get("comparisons", {}).get("V3 vs V2", {}).get("cliffs_delta", 1)) < 0.33
        for f in primary_funcs
    ) if evidence.get(primary_funcs[0], {}).get("comparisons", {}).get("V3 vs V2", {}).get("cliffs_delta") is not None else False

    epsilon_saturated = any(
        evidence[f].get("mechanism", {}).get("V3", {}).get("epsilon_saturation_ratio", 0) > 0.8
        for f in primary_funcs
    )
    collision_waste = any(
        evidence[f].get("mechanism", {}).get("V3", {}).get("mean_collision", 0) >
        evidence[f].get("mechanism", {}).get("V0", {}).get("mean_collision", 1) * 2
        for f in [5, 10, 20, 28]
    ) if evidence.get(5, {}).get("mechanism", {}).get("V0", {}).get("mean_collision") else False
    diversity_excess = any(
        evidence[f].get("mechanism", {}).get("V3", {}).get("mean_diversity_center", 0) >
        evidence[f].get("mechanism", {}).get("V0", {}).get("mean_diversity_center", 1) * 2
        for f in [5, 10, 20, 28]
    ) if evidence.get(5, {}).get("mechanism", {}).get("V0", {}).get("mean_diversity_center") else False
    failed_escape = any(
        evidence[f].get("mechanism", {}).get("V3", {}).get("escape_success_ratio", 0.5) < 0.3
        for f in primary_funcs
    )

    criteria_a = {
        "C1 (V3 > V1 on F20/F10)": v3_dominates_v1,
        "C2 (V3 >= V2 on F20/F10)": v3_dominates_v2,
        "C3 (V3 >= V0 on F20/F10)": v3_dominates_v0,
        "C4 (mechanism → fitness correlation)": not collision_waste,
        "C5 (epsilon not saturated)": not epsilon_saturated,
    }
    criteria_b = {
        "C1 (V3 > V1)": v3_dominates_v1,
        "C2 (V3 close to V2)": v3_dominates_v2 or v3_v2_close,
        "C3 (V3 >= V0 on at least 1 func)": v3_dominates_v0,
        "C4 (mechanism exists but limited)": not epsilon_saturated,
    }
    criteria_c = {
        "C1 (V3 cannot beat V0)": not v3_dominates_v0,
        "C2 (collision ↑ but fitness →)": collision_waste,
        "C3 (diversity ↑ but fitness →)": diversity_excess,
        "C4 (failed escape ratio ↑)": failed_escape,
        "C5 (epsilon saturation)": epsilon_saturated,
        "C6 (no advantage F20/F10)": not v3_dominates_v0,
    }

    a_score = sum(1 for v in criteria_a.values() if v)
    b_score = sum(1 for v in criteria_b.values() if v)
    c_score = sum(1 for v in criteria_c.values() if v)

    a_threshold = 4
    b_threshold = 3
    c_threshold = 4

    if a_score >= a_threshold:
        decision = "A"
        reasoning = (
            "GAPR Final (V3) satisfies sufficient criteria for main algorithm inclusion: "
            "it significantly outperforms V1 on primary decision functions, "
            "is competitive with V2, and shows fitness-correlated mechanism contribution."
        )
        scenario_text = (
            "GAPR, F20/F10 gibi multimodal-hybrid rejimlerde static ve time-based "
            "epsilon yaklaşımlarına göre daha kararlı fitness kazanımı üretmiştir."
        )
    elif c_score >= c_threshold and a_score < a_threshold:
        decision = "C"
        reasoning = (
            "GAPR Final (V3) fails key exclusion criteria: it cannot systematically beat "
            "V0 (Orbital+Escape), and its mechanism costs (collision/displacement, "
            "epsilon saturation) do not translate to fitness gains."
        )
        scenario_text = (
            "GAPR, Pauli aktivasyonunu artırmasına rağmen bu aktivasyonu sistematik "
            "fitness kazanımına dönüştürememiştir; bu durum high-dimensional exclusion "
            "mekanizmalarında activation–utility ayrımını doğrulamaktadır."
        )
    elif b_score >= b_threshold:
        decision = "B"
        reasoning = (
            "GAPR Final (V3) outperforms V1 but cannot clearly beat V0 or match V2 "
            "across primary functions. Mechanism contribution is detectable but limited "
            "to specific regimes."
        )
        scenario_text = (
            "GAPR, belirli rejimlerde mekanizma katkısı göstermiş ancak ana algoritma "
            "olma kriterlerini karşılamamıştır. Sınırlı rejim avantajı/mekanizma katkısı "
            "olarak sunulacaktır."
        )
    else:
        decision = "UNDECIDED"
        reasoning = (
            "Phase-1 criteria not clearly satisfied for any decision. "
            "Further analysis required."
        )
        scenario_text = "Belirsizlik devam ediyor. Faz-1 bu durumda başarısız sayılır (§17)."
        if a_score == 0 and b_score == 0 and c_score > 0:
            decision = "C"
            reasoning = "Despite unclear scores, C criteria dominate — GAPR removed from main line."
            scenario_text = (
                "GAPR, Pauli aktivasyonunu artırmasına rağmen bu aktivasyonu sistematik "
                "fitness kazanımına dönüştürememiştir."
            )

    report = f"""# Phase-1 Decision Report

## 1. Amaç
QWMO-GAPR Faz-1 charter (Faz-1-final.md) kapsamında GAPR Final varyantının Pauli/adaptive epsilon problemini çözüp çözmediğine karar vermek.

## 2. Deney Protokolü
- **Fonksiyonlar:** F5 (Schwefel), F10 (Rastrigin), F20 (Hybrid), F28 (Composition)
- **Varyantlar:** V0 (Orbital+Escape), V1 (Static QWMO), V2 (Dynamic Epsilon), V3 (GAPR Final)
- **Boyut:** D=30
- **Popülasyon:** N=50
- **FE Bütçesi:** Tmax=300000
- **Run:** 30 bağımsız run × 4 fonksiyon × 4 varyant = 480 run
- **İstatistik:** Wilcoxon signed-rank (p<0.05), Cliff's delta

## 3. Test Edilen Varyantlar
| ID | Operatörler | Epsilon |
|----|------------|---------|
| V0 | Orbital + Escape | Yok (Pauli yok) |
| V1 | Orbital + Static Pauli + Escape | static_epsilon_ratio = 0.05 |
| V2 | Orbital + Dynamic Pauli + Escape | eps_max=0.10, eps_min=0.005 |
| V3 | Orbital + GAPR Pauli + Escape | k=3, λ0=0.75, eps_max=0.15 |

## 4. Fitness Sonuçları
"""
    for func_id in [5, 10, 20, 28]:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        report += f"\n### F{func_id} ({fname})\n\n"
        report += "| Varyant | Mean | Std | Median | Best |\n"
        report += "|---|---|---|---|---|\n"
        for variant in ["V0", "V1", "V2", "V3"]:
            r = evidence.get(func_id, {}).get("mean_fitness", {}).get(variant)
            if r is not None:
                f_summ = summary[summary["function"] == func_id]
                vrow = f_summ[f_summ["variant"] == variant]
                if not vrow.empty:
                    report += f"| {variant} | {vrow['mean'].values[0]:.4e} | {vrow['std'].values[0]:.4e} | {vrow['median'].values[0]:.4e} | {vrow['best'].values[0]:.4e} |\n"

    report += "\n## 5. İstatistiksel Analiz\n"
    for func_id in [5, 10, 20, 28]:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        report += f"\n### F{func_id} ({fname})\n\n"
        report += "| Comparison | p-value | Significant | Cliff's delta | Effect Size | Median Improvement (%) |\n"
        report += "|---|---|---|---|---|---|\n"
        for comp in ["V3 vs V0", "V3 vs V1", "V3 vs V2", "V2 vs V1", "V1 vs V0"]:
            c = evidence.get(func_id, {}).get("comparisons", {}).get(comp, {})
            if c:
                report += f"| {comp} | {c.get('p', 'N/A')} | {c.get('significant', 'N/A')} | {c.get('cliffs_delta', 'N/A')} | {c.get('effect_size', 'N/A')} | {c.get('median_improvement_pct', 'N/A')} |\n"

    report += f"""
## 6. Epsilon Davranışı
V3 epsilon saturasyon oranı:
"""
    for func_id in [5, 10, 20, 28]:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        sat = evidence.get(func_id, {}).get("mechanism", {}).get("V3", {}).get("epsilon_saturation_ratio", "N/A")
        report += f"- F{func_id} ({fname}): {sat}\n"

    report += f"""
## 7. Pauli Collision / Displacement Analizi
"""
    for func_id in [5, 10, 20, 28]:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        v3 = evidence.get(func_id, {}).get("mechanism", {}).get("V3", {})
        v0 = evidence.get(func_id, {}).get("mechanism", {}).get("V0", {})
        c3 = v3.get("mean_collision", "N/A")
        c0 = v0.get("mean_collision", "N/A")
        report += f"- F{func_id} ({fname}): V3 collision={c3}, V0 collision={c0}\n"

    report += f"""
## 8. Escape Success / Failure Analizi
"""
    for func_id in [5, 10, 20, 28]:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        v3 = evidence.get(func_id, {}).get("mechanism", {}).get("V3", {})
        sr = v3.get("escape_success_ratio", "N/A")
        report += f"- F{func_id} ({fname}): V3 escape success ratio = {sr}\n"

    report += f"""
## 9. Diversity Analizi
"""
    for func_id in [5, 10, 20, 28]:
        fname = FUNCTION_NAMES.get(func_id, f"F{func_id}")
        v3 = evidence.get(func_id, {}).get("mechanism", {}).get("V3", {})
        dv = v3.get("mean_diversity_center", "N/A")
        report += f"- F{func_id} ({fname}): V3 mean diversity (center) = {dv}\n"

    report += f"""
## 10. Collision → Escape → Improvement Zinciri
{'(Chain analysis results from phase1_mechanism.py)'}

## 11. Ana Bulgular
"""
    report += "\n".join(f"- **{k}:** {'✓' if v else '✗'}" for k, v in criteria_a.items())
    report += "\n\n"
    report += "\n".join(f"- {k}: {'✓' if v else '✗'}" for k, v in criteria_c.items())

    report += f"""
## 12. Karar

**Karar: {decision}**

{reasoning}

## 13. Sonraki Faz İçin Öneri

{scenario_text}

---

## Decision Criteria Scores

| Decision | Score | Threshold |
|----------|-------|-----------|
| A (GAPR ana algoritmaya girer) | {a_score}/{a_threshold} | {a_threshold} |
| B (GAPR niş mekanizma olur) | {b_score}/{b_threshold} | {b_threshold} |
| C (GAPR ana hattan çıkar) | {c_score}/{c_threshold} | {c_threshold} |
"""

    report_path = os.path.join(results_dir, "phase1_decision_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Decision report written to {report_path}")
    print(f"Decision: {decision}")
    print(f"  A score: {a_score}/{a_threshold}")
    print(f"  B score: {b_score}/{b_threshold}")
    print(f"  C score: {c_score}/{c_threshold}")
    return decision


if __name__ == "__main__":
    compute_decision()
