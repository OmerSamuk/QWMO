import os
import time
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
from benchmark.cec2017 import CEC2017Benchmark, get_cec2017_functions
from core.qwmo import QWMO
from baselines.aso import ASO
from baselines.aos import AOS
from baselines.qpso import QPSO
from mealpy import PSO, GA, GWO, HHO, SHADE
import cma


def _run_single_experiment(func_id, dimension, algo_name, seed, pop_size, max_fes):
    runner = ExperimentRunner(dimensions=dimension, population_size=pop_size, max_fes=max_fes, num_runs=1, seed_list=[seed])
    return (func_id, algo_name, seed, runner.run_single_experiment(func_id, algo_name, seed))


class ExperimentRunner:
    def __init__(self, dimensions=30, population_size=50, max_fes=3000000, 
                 num_runs=30, seed_list=None):
        self.dimensions = dimensions
        self.population_size = population_size
        self.max_fes = max_fes
        self.num_runs = num_runs
        self.seed_list = seed_list if seed_list is not None else list(range(1, num_runs + 1))
        
        self.results = {}
    
    def run_qwmo(self, benchmark, ablation_config='full', seed=None):
        optimizer = QWMO(
            func=benchmark,
            dimension=self.dimensions,
            lower_bound=benchmark.lower_bound,
            upper_bound=benchmark.upper_bound,
            population_size=self.population_size,
            max_fes=self.max_fes,
            gamma=0.05,
            c_base=5,
            kappa_0=8,
            epsilon_r=0.05,
            k_s=10,
            eta_r=0.001,
            epsilon_max_ratio=0.1,
            epsilon_min_ratio=0.01,
            ablation_config=ablation_config,
            seed=seed
        )
        
        start_time = time.time()
        best_pos, best_fit = optimizer.run()
        elapsed = time.time() - start_time
        
        return {
            'best_fitness': best_fit,
            'best_position': best_pos,
            'convergence': optimizer.convergence_history,
            'fes_count': optimizer.fes_count,
            'elapsed_time': elapsed,
            'pauli_collisions': optimizer.pauli_collision_history,
            'escape_activations': optimizer.escape_activation_history
        }
    
    def run_aso(self, benchmark, seed=None):
        optimizer = ASO(
            func=benchmark,
            dimension=self.dimensions,
            lower_bound=benchmark.lower_bound,
            upper_bound=benchmark.upper_bound,
            population_size=self.population_size,
            max_fes=self.max_fes,
            alpha=50,
            beta=0.2,
            seed=seed
        )
        
        start_time = time.time()
        best_pos, best_fit = optimizer.run()
        elapsed = time.time() - start_time
        
        return {
            'best_fitness': best_fit,
            'best_position': best_pos,
            'convergence': optimizer.convergence_history,
            'fes_count': optimizer.fes_count,
            'elapsed_time': elapsed
        }
    
    def run_aos(self, benchmark, seed=None):
        optimizer = AOS(
            func=benchmark,
            dimension=self.dimensions,
            lower_bound=benchmark.lower_bound,
            upper_bound=benchmark.upper_bound,
            population_size=self.population_size,
            max_fes=self.max_fes,
            layer_number=5,
            foton_rate=0.1,
            seed=seed
        )
        
        start_time = time.time()
        best_pos, best_fit = optimizer.run()
        elapsed = time.time() - start_time
        
        return {
            'best_fitness': best_fit,
            'best_position': best_pos,
            'convergence': optimizer.convergence_history,
            'fes_count': optimizer.fes_count,
            'elapsed_time': elapsed
        }
    
    def run_qpso(self, benchmark, seed=None):
        optimizer = QPSO(
            func=benchmark,
            dimension=self.dimensions,
            lower_bound=benchmark.lower_bound,
            upper_bound=benchmark.upper_bound,
            population_size=self.population_size,
            max_fes=self.max_fes,
            alpha_max=1.0,
            alpha_min=0.5,
            seed=seed
        )
        
        start_time = time.time()
        best_pos, best_fit = optimizer.run()
        elapsed = time.time() - start_time
        
        return {
            'best_fitness': best_fit,
            'best_position': best_pos,
            'convergence': optimizer.convergence_history,
            'fes_count': optimizer.fes_count,
            'elapsed_time': elapsed
        }
    
    def run_mealpy_algorithm(self, benchmark, algorithm_class, seed=None):
        from mealpy import Problem, FloatVar
        
        problem = Problem(
            lb=[benchmark.lower_bound] * self.dimensions,
            ub=[benchmark.upper_bound] * self.dimensions,
            minmax="min",
            fit_func=lambda x: benchmark(x),
            save_population=False
        )
        
        termination = {
            "max_fe": self.max_fes
        }
        
        if seed is not None:
            np.random.seed(seed)
        
        start_time = time.time()
        
        try:
            optimizer = algorithm_class(
                epoch=self.max_fes // self.population_size,
                pop_size=self.population_size
            )
            optimizer.solve(problem, termination=termination)
            
            best_pos = optimizer.g_best.solution
            best_fit = optimizer.g_best.target.fitness
            convergence = optimizer.convergence
            
            elapsed = time.time() - start_time
            
            return {
                'best_fitness': best_fit,
                'best_position': best_pos,
                'convergence': convergence,
                'fes_count': self.max_fes,
                'elapsed_time': elapsed
            }
        except Exception as e:
            print(f"Error running {algorithm_class.__name__}: {e}")
            return None
    
    def run_cma_es(self, benchmark, seed=None):
        if seed is not None:
            np.random.seed(seed)
        
        sigma0 = (benchmark.upper_bound - benchmark.lower_bound) / 4
        x0 = np.random.uniform(benchmark.lower_bound, benchmark.upper_bound, self.dimensions)
        
        opts = {
            'maxfevals': self.max_fes,
            'bounds': [benchmark.lower_bound, benchmark.upper_bound],
            'verbose': -1,
            'seed': seed
        }
        
        start_time = time.time()
        
        es = cma.CMAEvolutionStrategy(x0.tolist(), sigma0, opts)
        
        convergence = []
        fes_count = 0
        
        while not es.stop() and fes_count < self.max_fes:
            solutions = es.ask()
            fitnesses = [benchmark(np.array(x)) for x in solutions]
            fes_count += len(solutions)
            es.tell(solutions, fitnesses)
            convergence.append(es.result.fbest)
        
        elapsed = time.time() - start_time
        
        result = es.result
        return {
            'best_fitness': result.fbest,
            'best_position': np.array(result.xbest),
            'convergence': convergence,
            'fes_count': fes_count,
            'elapsed_time': elapsed
        }
    
    def run_single_experiment(self, func_id, algorithm_name, seed):
        benchmark = CEC2017Benchmark(func_id, self.dimensions)
        
        if algorithm_name == 'QWMO_Full':
            return self.run_qwmo(benchmark, 'full', seed)
        elif algorithm_name == 'QWMO_OrbitalOnly':
            return self.run_qwmo(benchmark, 'orbital_only', seed)
        elif algorithm_name == 'QWMO_OrbitalPauli':
            return self.run_qwmo(benchmark, 'orbital_pauli', seed)
        elif algorithm_name == 'QWMO_OrbitalEscape':
            return self.run_qwmo(benchmark, 'orbital_escape', seed)
        elif algorithm_name == 'ASO':
            return self.run_aso(benchmark, seed)
        elif algorithm_name == 'AOS':
            return self.run_aos(benchmark, seed)
        elif algorithm_name == 'QPSO':
            return self.run_qpso(benchmark, seed)
        elif algorithm_name == 'PSO':
            return self.run_mealpy_algorithm(benchmark, PSO, seed)
        elif algorithm_name == 'GA':
            return self.run_mealpy_algorithm(benchmark, GA, seed)
        elif algorithm_name == 'GWO':
            return self.run_mealpy_algorithm(benchmark, GWO, seed)
        elif algorithm_name == 'HHO':
            return self.run_mealpy_algorithm(benchmark, HHO, seed)
        elif algorithm_name == 'SHADE':
            return self.run_mealpy_algorithm(benchmark, SHADE, seed)
        elif algorithm_name == 'CMA_ES':
            return self.run_cma_es(benchmark, seed)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")
    
    def run_full_experiment(self, func_ids=None, algorithms=None, parallel=True):
        if func_ids is None:
            func_ids = get_cec2017_functions()
        
        if algorithms is None:
            algorithms = [
                'QWMO_Full', 'QWMO_OrbitalOnly', 'QWMO_OrbitalPauli', 'QWMO_OrbitalEscape',
                'PSO', 'GA', 'GWO', 'HHO', 'SHADE', 'ASO', 'AOS', 'QPSO', 'CMA_ES'
            ]
        
        self.results = {}
        for func_id in func_ids:
            self.results[f'F{func_id}'] = {}
            for algo_name in algorithms:
                self.results[f'F{func_id}'][algo_name] = {
                    'fitnesses': [], 'times': []
                }
        
        if parallel:
            n_workers = min(8, os.cpu_count() or 1)
            print(f"Using {n_workers} workers for parallel execution")
            
            tasks = [(func_id, algo_name, seed)
                     for func_id in func_ids
                     for algo_name in algorithms
                     for seed in self.seed_list]
            
            completed = 0
            total = len(tasks)
            
            with ProcessPoolExecutor(max_workers=n_workers) as executor:
                fut_to_task = {
                    executor.submit(
                        _run_single_experiment, func_id, self.dimensions,
                        algo_name, seed, self.population_size, self.max_fes
                    ): (func_id, algo_name, seed)
                    for func_id, algo_name, seed in tasks
                }
                
                for future in as_completed(fut_to_task):
                    func_id, algo_name, seed = fut_to_task[future]
                    completed += 1
                    try:
                        _, _, _, result = future.result()
                        if result:
                            self.results[f'F{func_id}'][algo_name]['fitnesses'].append(result['best_fitness'])
                            self.results[f'F{func_id}'][algo_name]['times'].append(result['elapsed_time'])
                            print(f"  [{completed}/{total}] F{func_id} | {algo_name} | seed={seed}: "
                                  f"f={result['best_fitness']:.6e} t={result['elapsed_time']:.2f}s")
                        else:
                            print(f"  [{completed}/{total}] F{func_id} | {algo_name} | seed={seed}: FAILED")
                    except Exception as e:
                        print(f"  [{completed}/{total}] F{func_id} | {algo_name} | seed={seed}: ERROR {e}")
        else:
            for func_id in func_ids:
                print(f"\n{'='*60}")
                print(f"Function F{func_id} (D={self.dimensions})")
                print(f"{'='*60}")
                
                for algo_name in algorithms:
                    print(f"\n{algo_name}:")
                    
                    for i, seed in enumerate(self.seed_list):
                        result = self.run_single_experiment(func_id, algo_name, seed)
                        
                        if result:
                            self.results[f'F{func_id}'][algo_name]['fitnesses'].append(result['best_fitness'])
                            self.results[f'F{func_id}'][algo_name]['times'].append(result['elapsed_time'])
                            print(f"  Run {i+1}/{self.num_runs}: fitness={result['best_fitness']:.6e}, time={result['elapsed_time']:.2f}s")
                        else:
                            print(f"  Run {i+1}/{self.num_runs}: FAILED")
        
        print(f"\n{'='*60}")
        print("Final Summary")
        print(f"{'='*60}")
        for func_id in func_ids:
            for algo_name in algorithms:
                fits = self.results[f'F{func_id}'][algo_name]['fitnesses']
                ts = self.results[f'F{func_id}'][algo_name]['times']
                self.results[f'F{func_id}'][algo_name].update({
                    'mean': np.mean(fits) if fits else None,
                    'std': np.std(fits) if fits else None,
                    'mean_time': np.mean(ts) if ts else None,
                })
                if fits:
                    print(f"F{func_id} | {algo_name}: Mean={np.mean(fits):.6e} ± {np.std(fits):.6e}")
        
        return self.results


if __name__ == '__main__':
    runner = ExperimentRunner(dimensions=30, population_size=50, max_fes=3000000, num_runs=30)
    results = runner.run_full_experiment()
