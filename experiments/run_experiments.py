import os
import json
import numpy as np
from experiments.runner import ExperimentRunner
from experiments.config import (
    CEC2017_FUNCTIONS, 
    ALL_ALGORITHMS,
    EXPERIMENTAL_PARAMS
)


def run_full_experiment(dimensions=None, output_dir='results'):
    os.makedirs(output_dir, exist_ok=True)
    
    if dimensions is None:
        dimensions = EXPERIMENTAL_PARAMS['dimensions']
    
    all_results = {}
    
    for dim in dimensions:
        print(f"\n{'='*70}")
        print(f"Running experiments for D={dim}")
        print(f"{'='*70}")
        
        runner = ExperimentRunner(
            dimensions=dim,
            population_size=EXPERIMENTAL_PARAMS['population_size'],
            max_fes=EXPERIMENTAL_PARAMS['max_fes'],
            num_runs=EXPERIMENTAL_PARAMS['independent_runs'],
            seed_list=EXPERIMENTAL_PARAMS['seed_list']
        )
        
        dim_results = runner.run_full_experiment(
            func_ids=CEC2017_FUNCTIONS,
            algorithms=ALL_ALGORITHMS
        )
        
        all_results[f'D{dim}'] = dim_results
        
        output_file = os.path.join(output_dir, f'results_D{dim}.json')
        save_results(dim_results, output_file)
        print(f"\nSaved results to {output_file}")
    
    return all_results


def save_results(results, output_file):
    serializable_results = {}
    
    for func_key, func_results in results.items():
        serializable_results[func_key] = {}
        
        for algo_name, algo_results in func_results.items():
            serializable_results[func_key][algo_name] = {
                'fitnesses': algo_results.get('fitnesses', []),
                'mean': algo_results.get('mean'),
                'std': algo_results.get('std'),
                'times': algo_results.get('times', []),
                'mean_time': algo_results.get('mean_time')
            }
    
    with open(output_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)


def load_results(input_file):
    with open(input_file, 'r') as f:
        return json.load(f)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run QWMO experiments')
    parser.add_argument('--dimensions', type=int, nargs='+', default=[30, 50, 100],
                       help='Dimensions to run (default: 30 50 100)')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory (default: results)')
    
    args = parser.parse_args()
    
    results = run_full_experiment(
        dimensions=args.dimensions,
        output_dir=args.output_dir
    )
    
    print("\n" + "="*70)
    print("All experiments completed!")
    print("="*70)
