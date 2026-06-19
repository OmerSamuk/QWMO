---
tags: [moc, index]
---

# QWMO Workspace

> Quantum Wave-function Metaheuristic Optimizer — research vault

Bu vault QWMO araştırma hattının tüm dokümantasyon, karar ve charter kayıtlarını içerir.

## Hızlı Erişim

**Şu anki durum:** [[04-phase1-decision|Phase-1 Decision = C — GAPR ana hattan çıkarıldı]]

## Project Documentation

- [[01-overview|01 — Project Overview]]
- [[02-algorithm|02 — Algorithm & Operators]]
- [[05-architecture|05 — Architecture & Module Graph]]
- [[06-baselines|06 — Baseline Algorithms]]
- [[notes/phase2-plan.md|Phase2 plan]]
- [[notes/phase2-design-review.md|Phase2 design review]]

## Pilots & Decisions

- [[03-pilots-overview|03 — Pilot History Overview]]
- [[04-phase1-decision|04 — Phase-1 Decision (FINAL: C — Stop GAPR line)]]

## Locked Charters

- [[../charters/qwmo-gapr-test|Faz-1 Final Charter v1.0]]
- [[../charters/gapr-revision-pilot|GAPR Revision Pilot v2.0]]
- [[../charters/dynamic-update-plan|Dynamic Update Plan]]
- [[../charters/radiomics-landscape|Faz-2 Radiomics Landscape & Pauli Response Pilot]]

## Research Diary

- [[diary/qwmo-ozet|qwmo-ozet — Araştırma Günlüğü (TR)]]
- [[diary/phase1-audit|phase1-audit — Phase-1 Audit Note]]
- [[diary/sessions/3-review|3-review — Review Notes]]
- [[diary/sessions/4-session-log|4-session-log — SSH Session Log]]

## Manuscript

- [[../papers/QWMO_Algorithm.pdf|QWMO Algorithm (PDF)]]

## Source Code

- `core/` — QWMO algorithm core, Agent class, Phase1Logger
- `operators/` — orbital.py, pauli.py, escape.py
- `baselines/` — ASO, AOS, QPSO Python reimplementations
- `benchmark/` — CEC2017 wrapper
- `experiments/` — runners + config.py
- `analysis/` — stats + plotting
- `cec2017-py/` — vendored third-party (DO NOT EDIT)

## Experiment Results

- `results/phase1/` — Final 480-run matrix (Decision C)
- `results/gapr_revision_pilot_eps010/` — Revision pilot (Decision D)
- `results/gapr_comprehensive_pilot/` — Comprehensive pilot (Decision D)
- `results/gapr_pilot/` — Original pilot (Outcome C)
- `result/` — Older single-pilot

---

**Workspace root:** QWMO research vault
**Obsidian:** Vault at `.obsidian/` (workspace root)
**Opencode:** Configured at `.opencode/opencode.json`
