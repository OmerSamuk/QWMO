import numpy as np
from scipy.stats import wilcoxon

from qwmo import QWMO
from qwmo.benchmarks import rastrigin


DIM = 30
RUNS = 30
POP_SIZE = 50
MAX_ITER = 10000


CONFIGS = {
    "Orbital": {
        "enable_pauli": False,
        "enable_tunneling": False,
    },
    "Orbital+Pauli": {
        "enable_pauli": True,
        "enable_tunneling": False,
    },
    "Full_QWMO": {
        "enable_pauli": True,
        "enable_tunneling": True,
    },
}


def evaluate(config):

    scores = []

    for seed in range(RUNS):

        optimizer = QWMO(
            func=rastrigin,
            dim=DIM,
            bounds=(-5.12, 5.12),
            population_size=POP_SIZE,
            max_iter=MAX_ITER,
            seed=seed,
            **config
        )

        _, best_fitness, _ = optimizer.optimize()
        scores.append(best_fitness)

    return np.asarray(scores)


def main():

    results = {}

    for name, config in CONFIGS.items():

        print(f"Running {name}")

        scores = evaluate(config)

        results[name] = scores

        print(
            f"mean={scores.mean():.6e} "
            f"std={scores.std():.6e}"
        )

    print("\nWilcoxon Tests")

    full = results["Full_QWMO"]

    for baseline in ["Orbital", "Orbital+Pauli"]:

        stat, p = wilcoxon(full, results[baseline])

        print(
            f"Full_QWMO vs {baseline}: "
            f"p={p:.6f}"
        )


if __name__ == "__main__":
    main()