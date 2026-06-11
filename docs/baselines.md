# Baseline Algorithms

This document provides detailed information about the baseline algorithms used in QWMO benchmark experiments.

## Classical / Swarm-Based

### PSO (Particle Swarm Optimization)
- **Source:** mealpy library v3.0.3
- **Repository:** https://github.com/thieu1995/mealpy
- **License:** MIT
- **Reference:** Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization. In Proceedings of ICNN'95, Vol. 4, pp. 1942-1948.

### GA (Genetic Algorithm)
- **Source:** mealpy library v3.0.3
- **Repository:** https://github.com/thieu1995/mealpy
- **License:** MIT
- **Reference:** Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization and Machine Learning. Addison-Wesley.

### GWO (Grey Wolf Optimizer)
- **Source:** mealpy library v3.0.3
- **Repository:** https://github.com/thieu1995/mealpy
- **License:** MIT
- **Reference:** Mirjalili, S., Mirjalili, S. M., & Lewis, A. (2014). Grey wolf optimizer. Advances in Engineering Software, 69, 46-61.

## Physics-Based

### GSA (Gravitational Search Algorithm)
- **Note:** Not available in mealpy v3.0.3
- **Alternative:** SHADE (Success-History based parameter Adaptation for Differential Evolution) used instead
- **Source:** mealpy library v3.0.3
- **Repository:** https://github.com/thieu1995/mealpy
- **License:** MIT

### ASO (Atom Search Optimization)
- **Source:** Custom Python implementation based on original MATLAB code
- **Original Repository:** MATLAB File Exchange (BSD-3-Clause license)
- **Python Implementation:** `baselines/aso.py`
- **License:** BSD-3-Clause (original), MIT (Python reimplementation)
- **Reference:** Zhao, W., Wang, L., & Zhang, Z. (2019). Atom search optimization and its application to solve a hydrogeologic parameter estimation problem. Knowledge-Based Systems, 163, 283-304.

### AOS (Atomic Orbital Search)
- **Source:** Custom Python implementation based on original MATLAB code
- **Original Repository:** MATLAB File Exchange
- **Python Implementation:** `baselines/aos.py`
- **License:** MIT (Python reimplementation)
- **Reference:** Azizi, M. (2021). Atomic orbital search: A novel metaheuristic algorithm. Applied Mathematical Modelling, 93, 657-683.

## Quantum-Inspired

### QPSO (Quantum Particle Swarm Optimization)
- **Source:** Custom Python implementation based on standard QPSO formulation
- **Python Implementation:** `baselines/qpso.py`
- **License:** MIT
- **Reference:** Sun, J., Feng, B., & Xu, W. (2004). Particle swarm optimization with particles having quantum behavior. In Proceedings of the 2004 Congress on Evolutionary Computation, Vol. 1, pp. 325-331.

## Modern Elite

### HHO (Harris Hawks Optimization)
- **Source:** mealpy library v3.0.3
- **Repository:** https://github.com/thieu1995/mealpy
- **License:** MIT
- **Reference:** Heidari, A. A., Mirjalili, S., Faris, H., Aljarah, I., Mafarja, M., & Chen, H. (2019). Harris hawks optimization: Algorithm and applications. Future Generation Computer Systems, 97, 849-872.

### SHADE (Success-History based parameter Adaptation for Differential Evolution)
- **Source:** mealpy library v3.0.3
- **Repository:** https://github.com/thieu1995/mealpy
- **License:** MIT
- **Note:** Used as alternative to LSHADE-SPACMA (not readily available)
- **Reference:** Tanabe, R., & Fukunaga, A. (2013). Success-history based parameter adaptation for differential evolution. In 2013 IEEE Congress on Evolutionary Computation, pp. 71-78.

### CMA-ES (Covariance Matrix Adaptation Evolution Strategy)
- **Source:** cma package v4.4.4
- **Repository:** https://github.com/CMA-ES/pycma
- **License:** BSD-3-Clause
- **Reference:** Hansen, N., & Ostermeier, A. (2001). Completely derandomized self-adaptation in evolution strategies. Evolutionary Computation, 9(2), 159-195.

## Benchmark Functions

### CEC2017 Benchmark Suite
- **Source:** cec2017-py package
- **Repository:** https://github.com/tilleyd/cec2017-py
- **License:** MIT
- **Copyright:** Duncan Tilley (2022)
- **Functions Used:** F1, F3, F5, F9, F10, F15, F20, F23, F28
- **Reference:** Awad, N. H., Ali, M. Z., Suganthan, P. N., Liang, J. J., & Qu, B. Y. (2016). Problem Definitions and Evaluation Criteria for the CEC 2017 Special Session and Competition on Single Objective Bound Constrained Real-Parameter Numerical Optimization.
