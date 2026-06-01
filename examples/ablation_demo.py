"""
Small ablation demonstration.
"""

from qwmo import QWMO
from qwmo.benchmarks import rastrigin


CONFIGS = {
    "Orbital Only": {
        "enable_pauli": False,
        "enable_tunneling": False,
    },
    "Orbital + Pauli": {
        "enable_pauli": True,
        "enable_tunneling": False,
    },
    "Full QWMO": {
        "enable_pauli": True,
        "enable_tunneling": True,
    },
}


def main():

    for name, kwargs in CONFIGS.items():

        optimizer = QWMO(
            func=rastrigin,
            dim=30,
            bounds=(-5.12, 5.12),
            population_size=50,
            max_iter=3000,
            seed=42,
            **kwargs
        )

        _, best_fitness, _ = optimizer.optimize()

        print(f"{name:<20} -> {best_fitness:.6e}")


if __name__ == "__main__":
    main()