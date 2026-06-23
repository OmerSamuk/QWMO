import numpy as np


QWMO_PARAMS = {
    'gamma': 0.05,
    'c_base': 5,
    'kappa_0': 8,
    'k_s': 10,
    'eta_r': 0.001,
    'epsilon_max_ratio': 0.1,
    'epsilon_min_ratio': 0.01,
    'static_epsilon_ratio': 0.05,
    'adaptive_k': 3,
    'adaptive_lambda0': 0.75,
    'adaptive_epsilon_max_ratio': 0.15,
}

EXPERIMENTAL_PARAMS = {
    'dimensions': [30, 50, 100],
    'population_size': 50,
    'max_fes_per_dim': {30: 300_000, 50: 500_000, 100: 1_000_000},
    'independent_runs': 30,
    'seed_list': list(range(1, 31)),
}

CEC2017_FUNCTIONS = [1, 3, 5, 9, 10, 15, 20, 23, 28]

CONVERGENCE_FUNCTIONS = [5, 10, 20, 28]

ABLATION_CONFIGS = [
    'QWMO_OrbitalOnly',
    'QWMO_OrbitalPauli_Static',
    'QWMO_OrbitalPauli_Dynamic',
    'QWMO_OrbitalPauli_Adaptive',
    'QWMO_OrbitalPauli_GAPR',
    'QWMO_OrbitalEscape',
    'QWMO_Full_Static',
    'QWMO_Full_Dynamic',
    'QWMO_Full_Adaptive',
    'QWMO_Full_GAPR',
    'QWMO_Full_GAPR_eps010',
    'QWMO_Phase1_V0',
    'QWMO_Phase1_V1',
    'QWMO_Phase1_V2',
    'QWMO_Phase1_V3',
]

DEPRECATED_ALIASES = {
    'QWMO_Full': 'QWMO_Full_Dynamic',
    'QWMO_OrbitalPauli': 'QWMO_OrbitalPauli_Dynamic',
    'QWMO_OrbitalPauli_Adaptive': 'QWMO_OrbitalPauli_GAPR',
    'QWMO_Full_Adaptive': 'QWMO_Full_GAPR',
}

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

PILOT_CONFIG = {
    'functions': [1, 3, 10, 20],
    'dimension': 30,
    'population_size': 50,
    'max_fes': 300_000,
    'seeds': list(range(1, 11)),
    'ablation_configs': ABLATION_CONFIGS,
    'output_dir': 'result',
    'json_name': 'pilot_D30.json',
    'report_name': 'pilot_validation_report.md',
}

GAPR_PILOT_CONFIG = {
    "functions": [10, 20],
    "dimension": 30,
    "population_size": 50,
    "max_fes": 300_000,
    "seeds": list(range(1, 11)),
    "search_range": 200,
    "ablation_configs": [
        "QWMO_OrbitalOnly",
        "QWMO_OrbitalPauli_Static",
        "QWMO_OrbitalPauli_Dynamic",
        "QWMO_OrbitalPauli_Adaptive",
        "QWMO_OrbitalEscape",
        "QWMO_Full_Static",
        "QWMO_Full_Dynamic",
        "QWMO_Full_Adaptive",
    ],
    "output_dir": "results/gapr_pilot",
    "json_name": "gapr_pilot_D30.json",
    "report_name": "gapr_pilot_validation_report.md",
}

GAPR_COMPREHENSIVE_PILOT_CONFIG = {
    "functions": [5, 10, 15, 20, 23],
    "dimension": 30,
    "population_size": 50,
    "max_fes": 300_000,
    "seeds": list(range(1, 16)),
    "search_range": 200,
    "ablation_configs": [
        "QWMO_OrbitalOnly",
        "QWMO_OrbitalPauli_Static",
        "QWMO_OrbitalPauli_Dynamic",
        "QWMO_OrbitalPauli_GAPR",
        "QWMO_OrbitalEscape",
        "QWMO_Full_Static",
        "QWMO_Full_Dynamic",
        "QWMO_Full_GAPR",
    ],
    "output_dir": "results/gapr_comprehensive_pilot",
    "json_name": "pilot_results.json",
    "report_name": "pilot_report.md",
    "validation_report_name": "validation_report.md",
    "decision_name": "pilot_decision.md",
    "summary_csv_name": "pilot_summary.csv",
    "figures_subdirs": {
        "convergence": "convergence",
        "diversity": "diversity",
        "epsilon": "epsilon",
        "pauli": "pauli",
    },
}

GAPR_REVISION_PILOT_CONFIG = {
    "functions": [5, 10, 15, 20, 23],
    "dimension": 30,
    "population_size": 50,
    "max_fes": 300_000,
    "seeds": list(range(1, 11)),
    "search_range": 200,
    "ablation_configs": [
        "QWMO_OrbitalEscape",
        "QWMO_Full_Static",
        "QWMO_Full_Dynamic",
        "QWMO_Full_GAPR_eps010",
    ],
    "gapr_override": {
        "adaptive_epsilon_max_ratio": 0.10,
        "adaptive_lambda0": 0.75,
        "adaptive_k": 3,
    },
    "output_dir": "results/gapr_revision_pilot_eps010",
    "json_name": "revision_pilot_results.json",
    "report_name": "revision_pilot_report.md",
    "validation_report_name": "revision_validation_report.md",
    "decision_name": "revision_decision.md",
    "summary_csv_name": "revision_summary.csv",
    "figures_subdirs": {
        "convergence": "convergence",
        "diversity": "diversity",
        "epsilon": "epsilon",
        "pauli": "pauli",
    },
}

PHASE1_CONFIG = {
    "functions": [5, 10, 20, 28],
    "dimension": 30,
    "population_size": 50,
    "max_fes": 300_000,
    "seeds": list(range(0, 30)),
    "search_range": 200,
    "ablation_configs": [
        "phase1_v0",
        "phase1_v1",
        "phase1_v2",
        "phase1_v3",
    ],
    "v2_override": {
        "epsilon_min_ratio": 0.005,
    },
    "output_dir": "results/phase1",
    "run_prefix": "PHASE1",
    "smoke_seeds": list(range(0, 5)),
    "smoke_max_fes": 30_000,
}

CSIGMA_CONFIG = {
    "functions": [1, 5, 10],
    "function_names": {1: "Sphere", 5: "Schwefel", 10: "Rastrigin"},
    "dimension": 30,
    "population_size": 50,
    "max_fes": 300_000,
    "seeds": list(range(1, 31)),
    "search_range": 200,
    "ablation_configs": [
        "csigma_full_old",
        "csigma_e_old",
        "csigma_csigma",
    ],
    "variant_labels": {
        "csigma_full_old": "Full-old",
        "csigma_e_old": "E-old",
        "csigma_csigma": "Csigma",
    },
    "output_dir": "results/csigma_diagnostic",
    "run_prefix": "CSIGMA",
    "smoke_seeds": list(range(1, 6)),
    "smoke_max_fes": 30_000,
}
