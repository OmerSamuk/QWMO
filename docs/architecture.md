# QWMO Architecture

## Module Dependencies

This document describes the relationships between QWMO modules using the `entity → relationship → entity` format for Graphify knowledge graph extraction.

---

## Core Module Relationships

### Agent Class

```
Agent → uses → OrbitalSampling
Agent → uses → PauliExclusion
Agent → uses → QuantumEscape
Agent → produces → fitness_value
Agent → maintains → stagnation_counter
Agent → maintains → position_vector
Agent → is consumed by → QWMOAlgorithm
```

### QWMOAlgorithm (Main Loop)

```
QWMOAlgorithm → uses → Agent
QWMOAlgorithm → uses → OrbitalSampling
QWMOAlgorithm → uses → PauliExclusion
QWMOAlgorithm → uses → QuantumEscape
QWMOAlgorithm → uses → KDTree
QWMOAlgorithm → produces → best_solution
QWMOAlgorithm → is compared against → BaselineAlgorithm
QWMOAlgorithm → is evaluated on → BenchmarkFunction
```

---

## Operator Relationships

### OrbitalSampling

```
OrbitalSampling → uses → gaussian_distribution
OrbitalSampling → uses → dynamic_sigma
OrbitalSampling → uses → relative_quality_qi
OrbitalSampling → produces → candidate_position
OrbitalSampling → activates → position_update
OrbitalSampling → triggers → fitness_evaluation
OrbitalSampling → is consumed by → Agent
OrbitalSampling → is compared against → static_sampling
```

**Dynamic Sigma Calculation:**
```
q_i = (f_worst - f(x_i)) / (f_worst - f_best + ε)
σ_max,i = γ(u - l)(2 - q_i)
c_i = c_base * q_i
σ_i(t) = max(σ_max,i * exp(-c_i * t / T_max), σ_floor)
```

### PauliExclusion

```
PauliExclusion → uses → KDTree
PauliExclusion → uses → dynamic_epsilon
PauliExclusion → uses → orthogonal_displacement
PauliExclusion → produces → displacement_vector
PauliExclusion → activates → collision_detection
PauliExclusion → triggers → diversity_maintenance
PauliExclusion → is consumed by → Agent
PauliExclusion → is compared against → no_exclusion_baseline
```

**Dynamic Epsilon Formula:**
```
ε(t) = ε_max * (1 - t / T_max) + ε_min
```

**Default Values:**
- ε_max = 0.1 * (upper_bound - lower_bound)
- ε_min = 0.01 * (upper_bound - lower_bound)

**Orthogonal Displacement:**
```
v = x_b - x_g  (collision vector)
r ~ N(0, I)    (random vector)
p = r - (r^T * v / ||v||^2) * v  (orthogonal projection)
x_b' = clip(x_b + α * p / ||p||)
α ~ U(0.5ε, 1.5ε)
```

### QuantumEscape

```
QuantumEscape → uses → stagnation_counter
QuantumEscape → uses → levy_flight
QuantumEscape → uses → beta_hybrid_relocation
QuantumEscape → produces → escape_trajectory
QuantumEscape → activates → position_reset
QuantumEscape → triggers → exploration_boost
QuantumEscape → is consumed by → Agent
QuantumEscape → is compared against → random_restart
```

**Escape Probability:**
```
κ(t) = κ_0 * (t / T_max)
L_norm = ||x_i - x*|| / L_max
P_esc(t) = exp(-2 * κ(t) * L_norm)
```

**β-Hybrid Relocation:**
```
x_new = β * (x* + η) + (1 - β) * x_r
β ~ U[0, 1]
η ~ N(0, σ_noise^2 * I)
x_r ~ U[l, u]
```

---

## Utility Relationships

### KDTree

```
KDTree → uses → scipy.spatial.KDTree
KDTree → produces → neighbor_list
KDTree → is consumed by → PauliExclusion
KDTree → enables → collision_detection
KDTree → reduces → computational_complexity from O(N^2) to O(N log N)
```

### BenchmarkFunction

```
BenchmarkFunction → uses → CEC2017_suite
BenchmarkFunction → produces → fitness_value
BenchmarkFunction → is consumed by → QWMOAlgorithm
BenchmarkFunction → is consumed by → BaselineAlgorithm
BenchmarkFunction → is evaluated on → dimensions [30D, 50D, 100D]
```

**Available Functions:**
```
BenchmarkFunction → includes → F1_BentCigar (unimodal)
BenchmarkFunction → includes → F3_Zakharov (unimodal)
BenchmarkFunction → includes → F5_Rastrigin (multimodal, separable)
BenchmarkFunction → includes → F9_Levy (multimodal)
BenchmarkFunction → includes → F10_Schwefel (multimodal, non-separable)
BenchmarkFunction → includes → F15_GriewankRosenbrock (composite)
BenchmarkFunction → includes → F20_Hybrid6 (hybrid)
BenchmarkFunction → includes → F23_Composition3 (composition)
BenchmarkFunction → includes → F28_Composition8 (composition)
```

### BaselineAlgorithm

```
BaselineAlgorithm → uses → mealpy_library
BaselineAlgorithm → uses → pymoo_library
BaselineAlgorithm → uses → cma_library
BaselineAlgorithm → produces → fitness_value
BaselineAlgorithm → is compared against → QWMOAlgorithm
BaselineAlgorithm → is evaluated on → BenchmarkFunction
```

**Algorithm Sources:**
```
BaselineAlgorithm → includes → PSO (from mealpy)
BaselineAlgorithm → includes → GA (from mealpy)
BaselineAlgorithm → includes → GWO (from mealpy)
BaselineAlgorithm → includes → GSA (from mealpy)
BaselineAlgorithm → includes → HHO (from mealpy)
BaselineAlgorithm → includes → ASO (custom implementation)
BaselineAlgorithm → includes → AOS (custom implementation)
BaselineAlgorithm → includes → QPSO (from GitHub repository)
BaselineAlgorithm → includes → CMA_ES (from cma package)
BaselineAlgorithm → includes → LSHADE_SPACMA (from pymoo or L-SHADE fallback)
```

---

## Analysis Module Relationships

### StatisticalAnalysis

```
StatisticalAnalysis → uses → Friedman_test
StatisticalAnalysis → uses → Holm_posthoc
StatisticalAnalysis → uses → VarghaDelaney_A12
StatisticalAnalysis → produces → significance_report
StatisticalAnalysis → is consumed by → ExperimentRunner
StatisticalAnalysis → compares → QWMO vs BaselineAlgorithm
```

### ConvergenceAnalysis

```
ConvergenceAnalysis → uses → iteration_log
ConvergenceAnalysis → produces → convergence_curve
ConvergenceAnalysis → is applied to → F5_Rastrigin
ConvergenceAnalysis → is applied to → F10_Schwefel
ConvergenceAnalysis → is applied to → F20_Hybrid6
ConvergenceAnalysis → is applied to → F28_Composition8
ConvergenceAnalysis → plots → log_iteration vs log_fitness
```

### DiversityAnalysis

```
DiversityAnalysis → uses → pairwise_euclidean_distance
DiversityAnalysis → produces → diversity_curve
DiversityAnalysis → is consumed by → ExperimentRunner
DiversityAnalysis → compares → OrbitalOnly vs FullQWMO
DiversityAnalysis → measures → mean_pairwise_distance every 500 iterations
```

### SensitivityAnalysis

```
SensitivityAnalysis → uses → parameter_sweep
SensitivityAnalysis → produces → sensitivity_report
SensitivityAnalysis → varies → gamma [0.02, 0.1]
SensitivityAnalysis → varies → kappa_0 [4, 12]
SensitivityAnalysis → varies → k_s [5, 20]
SensitivityAnalysis → varies → epsilon_max [0.05, 0.1, 0.2, 0.3]
SensitivityAnalysis → is applied to → F10_Schwefel (30D, 1M FEs)
```

---

## Experiment Runner Relationships

### ExperimentRunner

```
ExperimentRunner → uses → QWMOAlgorithm
ExperimentRunner → uses → BaselineAlgorithm
ExperimentRunner → uses → BenchmarkFunction
ExperimentRunner → uses → StatisticalAnalysis
ExperimentRunner → produces → experimental_results
ExperimentRunner → manages → seed_list
ExperimentRunner → controls → function_evaluations (FEs = 3,000,000)
ExperimentRunner → controls → population_size (N = 50)
ExperimentRunner → controls → independent_runs (30)
ExperimentRunner → controls → dimensions [30D, 50D, 100D]
```

### AblationConfig

```
AblationConfig → uses → OrbitalOnly
AblationConfig → uses → OrbitalPlusPauli
AblationConfig → uses → OrbitalPlusEscape
AblationConfig → uses → FullQWMO
AblationConfig → is compared against → FullQWMO
AblationConfig → is evaluated on → BenchmarkFunction
AblationConfig → measures → operator_contribution
```

---

## Data Flow Diagram

```
1. ExperimentRunner
   ↓ uses
2. QWMOAlgorithm (with AblationConfig)
   ↓ uses
3. Agent population
   ↓ applies operators
4. OrbitalSampling → produces candidate positions
   ↓
5. PauliExclusion → uses KDTree → produces displacements
   ↓
6. QuantumEscape → uses stagnation counters → produces escapes
   ↓
7. BenchmarkFunction → evaluates fitness
   ↓
8. StatisticalAnalysis → produces significance reports
```

---

## Configuration Parameters

### QWMO Parameters

```
gamma: 0.05          # Orbital sampling sensitivity
c_base: 5            # Base decay coefficient
kappa_0: 8           # Escape activation threshold
epsilon_r: 0.05      # Exclusion radius ratio
k_s: 10              # Stagnation window
eta_r: 0.001         # Noise ratio for escape
epsilon_max: 0.1 * (u - l)
epsilon_min: 0.01 * (u - l)
```

### Experimental Parameters

```
dimensions: [30, 50, 100]
population_size: 50
max_fes: 3,000,000
independent_runs: 30
seed_list: [1, 2, 3, ..., 30]
```

---

## File Structure

```
qwmo-workspace/
├── core/
│   ├── agent.py              # Agent class
│   ├── qwmo.py               # Main QWMO algorithm
│   └── kdtree_util.py        # k-d tree wrapper
├── operators/
│   ├── orbital.py            # Adaptive Orbital Sampling
│   ├── pauli.py              # Pauli-Inspired Exclusion
│   └── escape.py             # Adaptive Quantum Escape
├── benchmark/
│   └── cec2017.py            # CEC2017 wrapper
├── baselines/
│   ├── aso.py                # Atom Search Optimization
│   ├── aos.py                # Atomic Orbital Search
│   └── qpso.py               # Quantum PSO
├── experiments/
│   ├── runner.py             # Experiment runner
│   └── config.py             # Configuration
├── analysis/
│   ├── stats.py              # Statistical analysis
│   ├── convergence.py        # Convergence curves
│   ├── diversity.py          # Diversity analysis
│   ├── pauli_activation.py   # Pauli activation analysis
│   ├── escape_behavior.py    # Escape behavior analysis
│   ├── sensitivity.py        # Sensitivity analysis
│   └── runtime.py            # Runtime analysis
└── docs/
    ├── README.md             # This file
    └── architecture.md       # Architecture document
```
