import numpy as np


QWMO_PARAMS = {
    'gamma': 0.05,
    'c_base': 5,
    'kappa_0': 8,
    'epsilon_r': 0.05,
    'k_s': 10,
    'eta_r': 0.001,
    'epsilon_max_ratio': 0.1,
    'epsilon_min_ratio': 0.01,
}

EXPERIMENTAL_PARAMS = {
    'dimensions': [30, 50, 100],
    'population_size': 50,
    'max_fes': 3_000_000,
    'independent_runs': 30,
    'seed_list': list(range(1, 31)),
}

CEC2017_FUNCTIONS = [1, 3, 5, 9, 10, 15, 20, 23, 28]

CONVERGENCE_FUNCTIONS = [5, 10, 20, 28]

ABLATION_CONFIGS = [
    'QWMO_Full',
    'QWMO_OrbitalOnly',
    'QWMO_OrbitalPauli',
    'QWMO_OrbitalEscape',
]

BASELINE_ALGORITHMS = [
    'PSO',
    'GA',
    'GWO',
    'HHO',
    'SHADE',
    'ASO',
    'AOS',
    'QPSO',
    'CMA_ES',
]

ALL_ALGORITHMS = ABLATION_CONFIGS + BASELINE_ALGORITHMS

DIVERSITY_INTERVAL = 500

SENSITIVITY_PARAMS = {
    'function_id': 10,
    'dimension': 30,
    'max_fes': 1_000_000,
    'num_runs': 10,
    'gamma_range': [0.02, 0.05, 0.08, 0.1],
    'kappa_0_range': [4, 6, 8, 10, 12],
    'k_s_range': [5, 10, 15, 20],
    'epsilon_max_range': [0.05, 0.1, 0.2, 0.3],
}
