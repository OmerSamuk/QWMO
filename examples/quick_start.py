"""
Minimal QWMO example.
"""

from qwmo import QWMO
from qwmo.benchmarks import rastrigin


def main():

    optimizer = QWMO(
        func=rastrigin,
        dim=30,
        bounds=(-5.12, 5.12),
        population_size=50,
        max_iter=1000,
        seed=42,
    )

    best_position, best_fitness, history = optimizer.optimize()

    print("\nOptimization completed.")
    print(f"Best fitness: {best_fitness:.6e}")
    print(f"Function evaluations: {optimizer.n_evals}")
    print(f"Iterations: {len(history)-1}")


if __name__ == "__main__":
    main()