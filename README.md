# QWMO: Quantum Wave-function Metaheuristic Optimizer

QWMO is a quantum-inspired population-based optimization framework that combines three probabilistic operators to balance exploration and exploitation in multimodal optimization landscapes.

## Features

- **Adaptive Orbital Sampling:** Controls Gaussian search dispersion according to relative solution quality
- **Pauli-Inspired Exclusion:** Preserves population diversity through orthogonal displacement dynamics
- **Adaptive Quantum Escape:** Enables stagnating agents to probabilistically leave local optima through stochastic relocation

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

# Create benchmark function (F10 Rastrigin, 30D)
benchmark = CEC2017Benchmark(func_id=10, dimension=30)

# Run QWMO optimization
optimizer = QWMO(
    func=benchmark,
    dimension=30,
    lower_bound=-100,
    upper_bound=100,
    population_size=50,
    max_fes=3_000_000,
    seed=42
)

best_position, best_fitness = optimizer.run()
print(f"Best fitness: {best_fitness:.6e}")
```

## Running Experiments

```bash
# Run full benchmark suite (30D/50D/100D, 9 functions, 13 algorithms)
python experiments/run_experiments.py

# Run specific dimension
python experiments/run_experiments.py --dimensions 30

# Run sensitivity analysis
python -c "from analysis.sensitivity import full_sensitivity_analysis; full_sensitivity_analysis()"

# Run runtime analysis
python -c "from analysis.runtime import full_runtime_analysis; full_runtime_analysis()"
```

## Project Structure

```
QWMO/
├── core/              # QWMO algorithm and Agent class
├── operators/         # Orbital, Pauli, Escape operators
├── baselines/         # Competitor algorithms (ASO, AOS, QPSO)
├── benchmark/         # CEC2017 wrapper
├── experiments/       # Experiment runner and configuration
├── analysis/          # Statistical and visual analysis
├── docs/              # Documentation
└── cec2017-py/        # CEC2017 benchmark functions
```

## Acknowledgments

This work builds upon several open-source implementations:

- **ASO (Atom Search Optimization):** Original MATLAB implementation by Zhao et al. (2019), BSD-3-Clause license. Python reimplementation in `baselines/aso.py`.
- **AOS (Atomic Orbital Search):** Original MATLAB implementation by Azizi (2021). Python reimplementation in `baselines/aos.py`.
- **QPSO (Quantum Particle Swarm Optimization):** Reference MATLAB implementation for economic load dispatch. Python reimplementation in `baselines/qpso.py`.
- **CEC2017 Benchmark Functions:** Python implementation by Duncan Tilley (2022), MIT license. Included in `cec2017-py/` directory.

## Citation

[DOI will be added after Zenodo upload]

## License

MIT License - see [LICENSE](LICENSE) file for details.
