from qwmo import QWMO
from qwmo.benchmarks import BENCHMARKS

import numpy as np


DIM = 30
RUNS = 30
POP_SIZE = 50
MAX_ITER = 10000


def run_single_benchmark(name, info):

    scores = []

    for seed in range(RUNS):

        optimizer = QWMO(
            func=info["func"],
            dim=DIM,
            bounds=info["bounds"],
            population_size=POP_SIZE,
            max_iter=MAX_ITER,
            seed=seed,
        )

        _, best_fitness, _ = optimizer.optimize()

        scores.append(best_fitness)

    scores = np.asarray(scores)

    print(
        f"{name:<15}"
        f"mean={scores.mean():.6e} "
        f"std={scores.std():.6e}"
    )


def main():

    print("=" * 60)
    print("QWMO Paper Reproduction")
    print("=" * 60)

    for name, info in BENCHMARKS.items():
        run_single_benchmark(name, info)


if __name__ == "__main__":
    main()