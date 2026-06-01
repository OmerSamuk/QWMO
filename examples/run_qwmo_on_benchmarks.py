"""
Run QWMO on all benchmark functions.
"""

from qwmo import QWMO
from qwmo.benchmarks import BENCHMARKS


DIM = 30
POPULATION = 50
MAX_ITER = 5000


def main():

    print("=" * 60)
    print("QWMO Benchmark Demonstration")
    print("=" * 60)

    for name, info in BENCHMARKS.items():

        print(f"\n{name}")

        optimizer = QWMO(
            func=info["func"],
            dim=DIM,
            bounds=info["bounds"],
            population_size=POPULATION,
            max_iter=MAX_ITER,
            seed=42,
        )

        _, best_fitness, _ = optimizer.optimize()

        print(f"Best fitness: {best_fitness:.6e}")

    print("\nDone.")


if __name__ == "__main__":
    main()