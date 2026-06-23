from analysis.stats import (
    friedman_test_per_function,
    friedman_test_across_functions,
    wilcoxon_per_function,
    a12_per_function,
    vargha_delaney_a12,
    full_statistical_analysis,
)
from analysis.convergence import plot_convergence_curves, plot_all_convergence
from analysis.diversity import plot_diversity_curves, compare_diversity
from analysis.pauli_activation import analyze_pauli_activations, plot_pauli_analysis
from analysis.escape_behavior import analyze_escape_behavior, plot_escape_analysis
from analysis.sensitivity import sensitivity_analysis_single_param, full_sensitivity_analysis
from analysis.runtime import measure_runtime, compare_kdtree_overhead, full_runtime_analysis

friedman_test = friedman_test_per_function
holm_posthoc = wilcoxon_per_function
compute_effect_sizes = a12_per_function

__all__ = [
    'friedman_test', 'friedman_test_per_function', 'friedman_test_across_functions',
    'wilcoxon_per_function', 'holm_posthoc',
    'a12_per_function', 'vargha_delaney_a12', 'compute_effect_sizes',
    'full_statistical_analysis',
    'plot_convergence_curves', 'plot_all_convergence',
    'plot_diversity_curves', 'compare_diversity',
    'analyze_pauli_activations', 'plot_pauli_analysis',
    'analyze_escape_behavior', 'plot_escape_analysis',
    'sensitivity_analysis_single_param', 'full_sensitivity_analysis',
    'measure_runtime', 'compare_kdtree_overhead', 'full_runtime_analysis',
]
