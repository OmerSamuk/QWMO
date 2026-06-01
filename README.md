# QWMO

**Quantum Wave-function Metaheuristic Optimizer**

Reference implementation accompanying the paper:

> **QWMO: A Quantum Wave-function Inspired Metaheuristic for Multimodal Optimization**

---

## Overview

QWMO is a population-based optimization algorithm inspired by probabilistic concepts from quantum mechanics.

The optimizer was developed to investigate how quantum-inspired probabilistic operators influence the exploration–exploitation balance in multimodal continuous optimization problems.

Rather than simulating physical quantum systems directly, QWMO adopts selected quantum-inspired concepts as algorithmic search mechanisms.

The framework consists of three complementary operators:

* Adaptive Orbital Sampling
* Pauli-Inspired Exclusion
* Adaptive Quantum Escape

A central design goal of QWMO is **operator-level interpretability**. Each operator can be independently enabled or disabled, allowing systematic ablation studies and reproducible analysis.

---

## Features

* Continuous single-objective optimization
* Fitness-aware adaptive sampling
* Diversity preservation through exclusion dynamics
* Stagnation recovery mechanism
* Modular operator design
* Reproducible benchmark framework
* Ablation-study support
* Lightweight implementation with minimal dependencies

---

## Installation

Clone the repository:

```bash
git clone https://github.com/OmerSamuk/QWMO.git
cd QWMO
```

Install dependencies:

```bash
pip install -r requirements.txt
```

or install the package in editable mode:

```bash
pip install -e .
```

---

## Quick Start

```python
from qwmo import QWMO
from qwmo.benchmarks import rastrigin

optimizer = QWMO(
    func=rastrigin,
    dim=30,
    bounds=(-5.12, 5.12),
    population_size=50,
    max_iter=5000,
    seed=42,
)

best_position, best_fitness, history = optimizer.optimize()

print(best_fitness)
```

---

## Examples

Run the minimal example:

```bash
python examples/quick_start.py
```

Run benchmark demonstrations:

```bash
python examples/run_qwmo_on_benchmarks.py
```

Run a small ablation demonstration:

```bash
python examples/ablation_demo.py
```

---

## Reproducing Experiments

Main benchmark experiments:

```bash
python experiments/reproduce_paper_results.py
```

Ablation study:

```bash
python experiments/run_ablation.py
```

These scripts reproduce the experimental workflow used in the accompanying paper.

---

## Repository Structure

```text
QWMO/
├── qwmo/
│   ├── __init__.py
│   ├── optimizer.py
│   └── benchmarks.py
│
├── examples/
│   ├── quick_start.py
│   ├── run_qwmo_on_benchmarks.py
│   └── ablation_demo.py
│
├── experiments/
│   ├── reproduce_paper_results.py
│   ├── run_ablation.py
│   └── utils.py
│
├── docs/
│   └── algorithm_overview.md
│
├── paper/
│   └── README.md
│
├── results/
│
├── CITATION.cff
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Documentation

Additional documentation is available in:

```text
docs/algorithm_overview.md
```

This document describes:

* the optimization cycle,
* operator behavior,
* computational complexity,
* design philosophy,
* implementation details.

---

## Benchmark Functions

The repository includes several standard continuous optimization benchmarks:

| Function    | Type                  |
| ----------- | --------------------- |
| Sphere      | Unimodal              |
| Schwefel    | Multimodal            |
| Rastrigin   | Multimodal            |
| Hybrid      | CEC-style Hybrid      |
| Composition | CEC-style Composition |

The hybrid and composition functions are lightweight reproducible approximations intended for experimentation and are not official CEC benchmark implementations.

---

## Reproducibility

The repository provides:

* source code,
* benchmark implementations,
* example scripts,
* ablation studies,
* experiment workflows.

All experiments use deterministic random seeds when specified.

---

## Paper

Information about the manuscript can be found in:

```text
paper/
```

ArXiv preprint:

> Coming soon.

After publication the preprint link will be added here.

---

## Citation

If you use QWMO in academic work, please cite both the repository and the accompanying paper.

GitHub automatically generates citation formats from:

```text
CITATION.cff
```

---

## License

This project is released under the MIT License.

See:

```text
LICENSE
```

for details.

---

## Disclaimer

QWMO is a research-oriented optimization framework developed for studying probabilistic operator interactions in multimodal optimization landscapes.

The implementation is intended for scientific experimentation, reproducibility, and educational purposes.
