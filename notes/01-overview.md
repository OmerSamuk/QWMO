---
tags: [overview, readme]
---

# QWMO: Quantum Wave-function Metaheuristic Optimizer

QWMO is a quantum-inspired population-based optimization framework that combines three probabilistic operators to balance exploration and exploitation in multimodal optimization landscapes.

> 📌 This is the **Obsidian-aware overview**. For the GitHub-facing README, see [[../README.md]].

## Related Notes

- Algorithm details: [[02-algorithm]]
- Architecture: [[05-architecture]]
- Baselines: [[06-baselines]]
- Pilots & decisions: [[03-pilots-overview]]
- Current decision: [[04-phase1-decision]]
- Research diary: [[diary/qwmo-ozet]]

## Three Core Operators

1. **Adaptive Orbital Sampling** — Gaussian search dispersion based on relative solution quality
2. **Pauli-Inspired Exclusion** — k-d tree collision detection + orthogonal displacement
3. **Adaptive Quantum Escape** — β-hybrid stochastic relocation for stagnating agents

## Installation

```bash
git clone https://github.com/OmerSamuk/QWMO.git
cd QWMO
pip install -r requirements.txt
pip install -e cec2017-py/
```

## Quick Start

```python
from core.qwmo import QWMO
from benchmark.cec2017 import CEC2017Benchmark

benchmark = CEC2017Benchmark(func_id=10, dimension=30)

optimizer = QWMO(
    func=benchmark,
    dimension=30,
    lower_bound=-100,
    upper_bound=100,
    population_size=50,
    max_fes=300_000,  # CEC2017 standard: 10,000 * D
    seed=42
)

best_position, best_fitness = optimizer.run()
print(f"Best fitness: {best_fitness:.6e}")
```

## Running Experiments

```bash
python experiments/run_experiments.py --dimensions 30 50 100
```

## Repository Structure

```
qwmo-workspace/
├── core/              # QWMO algorithm and Agent class
├── operators/         # Orbital, Pauli, Escape operators
├── baselines/         # Competitor algorithms (ASO, AOS, QPSO)
├── benchmark/         # CEC2017 wrapper
├── experiments/       # Experiment runner and configuration
├── analysis/          # Statistical and visual analysis
├── notes/             # Obsidian knowledge base (this note)
├── charters/          # Locked experimental protocols
└── papers/            # Manuscript PDFs
```

## License

MIT License — see [LICENSE](../LICENSE) file.
