# QWMO: Quantum Wave-function Metaheuristic Optimizer

## Overview

QWMO (Quantum Wave-function Metaheuristic Optimizer) is a quantum-inspired population-based optimization framework that combines three probabilistic operators to balance exploration and exploitation in multimodal optimization landscapes.

## Core Operators

### 1. Adaptive Orbital Sampling

**OrbitalSampling** `uses` Gaussian distributions to generate candidate positions around each agent.

**OrbitalSampling** `produces` new candidate positions by sampling from N(xi, σ²i(t)I).

**OrbitalSampling** `activates` dynamic sigma adjustment based on relative solution quality qi.

**OrbitalSampling** `triggers` position updates for all agents in the population.

**OrbitalSampling** `is consumed by` the main QWMO loop at each iteration.

**OrbitalSampling** `is compared against` static sampling mechanisms in ablation studies.

#### Pseudo-code

```python
def adaptive_orbital_sampling(agent, best_fitness, worst_fitness, t, T_max):
    # Calculate relative quality
    q_i = (worst_fitness - agent.fitness) / (worst_fitness - best_fitness + epsilon)
    
    # Dynamic orbital radius
    sigma_max = gamma * (upper_bound - lower_bound) * (2 - q_i)
    c_i = c_base * q_i
    
    # Time-decaying sigma
    sigma_i = max(sigma_max * exp(-c_i * t / T_max), sigma_floor)
    
    # Sample new position
    x_new = sample_gaussian(agent.position, sigma_i)
    x_new = clip_to_bounds(x_new)
    
    return x_new
```

---

### 2. Pauli-Inspired Exclusion

**PauliExclusion** `uses` k-d tree data structure to detect spatial collisions between agents.

**PauliExclusion** `produces` orthogonal displacement vectors when agents violate exclusion radius.

**PauliExclusion** `activates` when distance between two agents falls below ε(t).

**PauliExclusion** `triggers` position corrections to maintain population diversity.

**PauliExclusion** `is consumed by` the diversity maintenance mechanism.

**PauliExclusion** `is compared against` no-exclusion baseline in ablation studies.

#### Dynamic Epsilon Formula

```
ε(t) = ε_max * (1 - t / T_max) + ε_min
```

Where:
- ε_max = 0.1 * (upper_bound - lower_bound)
- ε_min = 0.01 * (upper_bound - lower_bound)

#### Pseudo-code

```python
def pauli_exclusion(agents, t, T_max):
    # Dynamic epsilon
    epsilon_t = epsilon_max * (1 - t / T_max) + epsilon_min
    
    # Build k-d tree
    kdtree = build_kdtree([agent.position for agent in agents])
    
    # Query neighbors within epsilon
    for i, agent in enumerate(agents):
        neighbors = kdtree.query_radius(agent.position, epsilon_t)
        
        for j in neighbors:
            if i != j and agents[j].fitness < agent.fitness:
                # Agent i is weaker, apply displacement
                v = agent.position - agents[j].position
                r = sample_gaussian(0, 1, dim)
                
                # Orthogonal projection
                p = r - (dot(r, v) / (norm(v)**2 + 1e-10)) * v
                alpha = uniform(0.5 * epsilon_t, 1.5 * epsilon_t)
                
                # Update weaker agent
                agent.position = clip(agent.position + alpha * p / (norm(p) + 1e-10))
```

---

### 3. Adaptive Quantum Escape

**QuantumEscape** `uses` stagnation counters to detect trapped agents.

**QuantumEscape** `produces` escape trajectories using β-hybrid stochastic relocation.

**QuantumEscape** `activates` when stagnation_count > kappa_0.

**QuantumEscape** `triggers` position reset for stagnated agents with probability P_esc.

**QuantumEscape** `is consumed by` the stagnation recovery mechanism.

**QuantumEscape** `is compared against` random restart in ablation studies.

#### Escape Probability

```
P_esc(t) = exp(-2 * κ(t) * L_norm)
```

Where:
- κ(t) = κ_0 * (t / T_max)
- L_norm = ||xi - x*|| / L_max
- L_max = sqrt(D) * (upper_bound - lower_bound)

#### Pseudo-code

```python
def adaptive_quantum_escape(agent, best_position, t, T_max, kappa_0, eta_r):
    if agent.stagnation_count > kappa_0:
        # Calculate escape probability
        kappa_t = kappa_0 * (t / T_max)
        L_norm = norm(agent.position - best_position) / L_max
        P_esc = exp(-2 * kappa_t * L_norm)
        
        if random() < P_esc:
            # β-hybrid stochastic relocation
            beta = uniform(0, 1)
            eta = sample_gaussian(0, sigma_noise)
            x_r = sample_uniform(lower_bound, upper_bound)
            
            x_new = beta * (best_position + eta) + (1 - beta) * x_r
            agent.position = clip_to_bounds(x_new)
            agent.stagnation_count = 0
```

---

## Benchmark Functions (CEC2017)

**BenchmarkFunction** `is evaluated by` QWMO and baseline algorithms.

**BenchmarkFunction** `is consumed by` the experimental runner for performance comparison.

**BenchmarkFunction** `is compared against` theoretical optima to compute fitness errors.

### Function List

| ID | Name | Type | Characteristics |
|----|------|------|-----------------|
| F1 | Bent Cigar | Unimodal | Smooth, convex |
| F3 | Zakharov | Unimodal | Quadratic + quartic |
| F5 | Rastrigin | Multimodal | Separable, many local minima |
| F9 | Levy | Multimodal | Rotated, shifted |
| F10 | Schwefel | Multimodal | Non-separable, deceptive |
| F15 | Griewank+Rosenbrock | Composite | Hybrid structure |
| F20 | Hybrid Function 6 | Hybrid | Mixed landscapes |
| F23 | Composition Function 3 | Composition | Multiple basins |
| F28 | Composition Function 8 | Composition | Highly multimodal |

---

## Baseline Algorithms

**BaselineAlgorithm** `is compared against` QWMO using statistical tests.

**BaselineAlgorithm** `is evaluated on` the same benchmark functions as QWMO.

**BaselineAlgorithm** `uses` the same experimental settings (N=50, FEs=3M, 30 runs).

### Algorithm Categories

| Category | Algorithms | Source |
|----------|-----------|--------|
| Classical/Swarm | PSO, GA, GWO | mealpy library |
| Physics-based | GSA, ASO, AOS | mealpy / custom implementation |
| Quantum-inspired | QPSO | GitHub repository (qpsopy/pyqps) |
| Modern Elite | LSHADE-SPACMA, CMA-ES, HHO | pymoo / cma / mealpy |

---

## Ablation Configurations

**AblationConfig** `is compared against` Full QWMO to measure operator contributions.

**AblationConfig** `is evaluated on` the same benchmark suite.

**AblationConfig** `uses` identical parameter settings except for operator activation.

### Configuration Variants

1. **OrbitalOnly**: Only Adaptive Orbital Sampling active
2. **OrbitalPlusPauli**: Orbital Sampling + Pauli Exclusion
3. **OrbitalPlusEscape**: Orbital Sampling + Quantum Escape
4. **FullQWMO**: All three operators active

---

## Experimental Settings

### QWMO Parameters

```python
gamma = 0.05          # Orbital sampling sensitivity
c_base = 5            # Base decay coefficient
kappa_0 = 8           # Escape activation threshold
epsilon_r = 0.05      # Exclusion radius ratio
k_s = 10              # Stagnation window
eta_r = 0.001         # Noise ratio for escape
```

### Experimental Protocol

```python
dimensions = [30, 50, 100]
population_size = 50
max_fes = 3_000_000
independent_runs = 30
seed_list = list(range(1, 31))
```

---

## Statistical Analysis

**StatisticalAnalysis** `uses` Friedman test for global ranking.

**StatisticalAnalysis** `uses` Holm post-hoc test for pairwise comparisons.

**StatisticalAnalysis** `uses` Vargha-Delaney A12 for effect size measurement.

**StatisticalAnalysis** `produces` significance reports comparing QWMO vs baselines.

---

## Repository Structure

```
qwmo-workspace/
├── core/              # Agent class, QWMO algorithm, k-d tree utility
├── operators/         # Orbital, Pauli, Escape operators
├── benchmark/         # CEC2017 wrapper
├── baselines/         # Competitor algorithms
├── experiments/       # Runner and configuration
├── analysis/          # Statistical and visual analysis
└── docs/              # Documentation (this file)
```
