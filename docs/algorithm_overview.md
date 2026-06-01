# QWMO Algorithm Overview

## Introduction

Quantum Wave-function Metaheuristic Optimizer (QWMO) is a population-based optimization algorithm developed for continuous multimodal optimization.

The algorithm was designed to investigate how quantum-inspired probabilistic operators can influence the exploration–exploitation balance in complex search landscapes.

QWMO does not attempt to simulate physical quantum systems. Instead, it adopts selected probabilistic concepts as algorithmic metaphors.

The optimizer consists of three complementary operators:

1. Adaptive Orbital Sampling
2. Pauli-Inspired Exclusion
3. Adaptive Quantum Escape

---

# Operator 1: Adaptive Orbital Sampling

Orbital Sampling is the primary search mechanism.

Each agent generates candidate solutions by sampling from a Gaussian probability distribution centered at its current position.

The sampling variance depends on solution quality.

### Poor Solutions

Agents with poor fitness values maintain larger sampling radii:

* broader exploration
* larger search coverage
* increased probability of discovering unexplored regions

### Good Solutions

Agents with good fitness values gradually reduce their sampling variance:

* local refinement
* exploitation around promising regions
* improved convergence precision

This creates a fitness-dependent exploration–exploitation transition.

---

# Operator 2: Pauli-Inspired Exclusion

Population collapse is a common issue in many metaheuristic algorithms.

When multiple agents occupy nearly identical regions, diversity decreases and premature convergence becomes more likely.

QWMO addresses this issue through a Pauli-inspired exclusion mechanism.

### Collision Detection

A KD-tree is used to identify neighboring agents within a predefined exclusion radius.

### Orthogonal Diversification

Instead of moving agents directly away from each other, QWMO displaces the weaker agent along an approximately orthogonal direction.

This strategy:

* preserves diversity
* avoids excessive repulsion
* encourages exploration of alternative local regions

---

# Operator 3: Adaptive Quantum Escape

Some agents may remain stagnant for long periods without improvement.

QWMO monitors stagnation for every individual.

When stagnation exceeds a threshold, a probabilistic escape mechanism may be triggered.

### Escape Probability

The probability of escape depends on:

* distance to the current best solution
* adaptive barrier hardness
* optimization progress

### Hybrid Relocation

Escaping agents are relocated using a weighted combination of:

* the current best solution
* random points in the search space
* small Gaussian perturbations

This mechanism attempts to balance:

* exploitation of known good regions
* exploration of unexplored regions

---

# Optimization Cycle

For every iteration:

1. Orbital Sampling
2. Best Solution Update
3. Pauli Exclusion
4. Best Solution Update
5. Quantum Escape
6. Best Solution Update

The process repeats until the maximum iteration budget is exhausted.

---

# Computational Complexity

Let:

* N = population size
* D = problem dimension

Approximate complexity:

| Component            | Complexity |
| -------------------- | ---------- |
| Orbital Sampling     | O(ND)      |
| KD-tree Construction | O(N log N) |
| Neighbor Queries     | O(N log N) |
| Quantum Escape       | O(ND)      |

Overall complexity is dominated by:

O(ND + N log N)

for typical optimization settings.

---

# Design Philosophy

QWMO was developed with four design goals:

1. Fitness-aware exploration
2. Diversity preservation
3. Stagnation recovery
4. Modular operator analysis

Unlike many optimization algorithms that introduce multiple tightly coupled mechanisms, QWMO was intentionally designed so that each operator can be independently enabled or disabled.

This property facilitates ablation studies and operator-level analysis.

---

# Reference

If you use QWMO in academic work, please cite the accompanying paper and repository.
