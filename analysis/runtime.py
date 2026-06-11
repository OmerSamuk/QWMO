import numpy as np
import time
from core.qwmo import QWMO
from benchmark.cec2017 import CEC2017Benchmark


def measure_runtime(function_id, dimension, max_fes, seed=42, 
                   ablation_configs=['full', 'orbital_only', 'orbital_pauli']):
    benchmark = CEC2017Benchmark(function_id, dimension)
    
    results = {}
    
    for config in ablation_configs:
        print(f"\nMeasuring runtime for {config}...")
        
        optimizer = QWMO(
            func=benchmark,
            dimension=dimension,
            lower_bound=benchmark.lower_bound,
            upper_bound=benchmark.upper_bound,
            population_size=50,
            max_fes=max_fes,
            ablation_config=config,
            seed=seed
        )
        
        start_time = time.perf_counter()
        _, _ = optimizer.run()
        elapsed = time.perf_counter() - start_time
        
        ms_per_fe = (elapsed * 1000) / optimizer.fes_count
        
        results[config] = {
            'elapsed_seconds': elapsed,
            'fes_count': optimizer.fes_count,
            'ms_per_fe': ms_per_fe
        }
        
        print(f"  {config}: {elapsed:.2f}s, {ms_per_fe:.4f} ms/FE")
    
    return results


def compare_kdtree_overhead(function_id=10, dimension=30, max_fes=1_000_000, seed=42):
    print(f"\n{'='*60}")
    print(f"K-D Tree Overhead Analysis - F{function_id} (D={dimension})")
    print(f"{'='*60}")
    
    results = measure_runtime(
        function_id, dimension, max_fes, seed,
        ablation_configs=['orbital_only', 'orbital_pauli']
    )
    
    orbital_time = results['orbital_only']['elapsed_seconds']
    pauli_time = results['orbital_pauli']['elapsed_seconds']
    
    overhead = pauli_time - orbital_time
    overhead_percent = (overhead / orbital_time) * 100
    
    print(f"\nK-D Tree Overhead:")
    print(f"  Orbital Only: {orbital_time:.2f}s")
    print(f"  Orbital + Pauli: {pauli_time:.2f}s")
    print(f"  Overhead: {overhead:.2f}s ({overhead_percent:.1f}%)")
    
    return results


def full_runtime_analysis(function_ids=None, dimensions=None, output_file='results/runtime_analysis.txt'):
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if function_ids is None:
        function_ids = [1, 5, 10, 20, 28]
    
    if dimensions is None:
        dimensions = [30]
    
    all_results = {}
    
    with open(output_file, 'w') as f:
        f.write("QWMO Runtime Analysis\n")
        f.write("="*60 + "\n\n")
        
        for dim in dimensions:
            for func_id in function_ids:
                print(f"\nF{func_id} (D={dim}):")
                
                benchmark = CEC2017Benchmark(func_id, dim)
                max_fes = 3_000_000
                
                results = {}
                for config in ['full', 'orbital_only', 'orbital_pauli', 'orbital_escape']:
                    optimizer = QWMO(
                        func=benchmark,
                        dimension=dim,
                        lower_bound=benchmark.lower_bound,
                        upper_bound=benchmark.upper_bound,
                        population_size=50,
                        max_fes=max_fes,
                        ablation_config=config,
                        seed=42
                    )
                    
                    start_time = time.perf_counter()
                    _, _ = optimizer.run()
                    elapsed = time.perf_counter() - start_time
                    
                    ms_per_fe = (elapsed * 1000) / optimizer.fes_count
                    
                    results[config] = {
                        'elapsed': elapsed,
                        'ms_per_fe': ms_per_fe
                    }
                    
                    print(f"  {config}: {elapsed:.2f}s ({ms_per_fe:.4f} ms/FE)")
                
                all_results[f'F{func_id}_D{dim}'] = results
                
                f.write(f"\nF{func_id} (D={dim}):\n")
                for config, res in results.items():
                    f.write(f"  {config}: {res['elapsed']:.2f}s, {res['ms_per_fe']:.4f} ms/FE\n")
    
    print(f"\nSaved runtime analysis to {output_file}")
    return all_results
