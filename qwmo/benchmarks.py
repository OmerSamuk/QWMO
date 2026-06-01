import numpy as np


def sphere(X):
    """Sphere function. Global minimum: f(0,...,0) = 0."""
    X = np.asarray(X, dtype=float)
    return np.sum(X**2, axis=1)


def schwefel(X):
    """Schwefel function. Global minimum is near x_i = 420.9687."""
    X = np.asarray(X, dtype=float)
    d = X.shape[1]
    return 418.9829 * d - np.sum(X * np.sin(np.sqrt(np.abs(X))), axis=1)


def rastrigin(X):
    """Rastrigin function. Global minimum: f(0,...,0) = 0."""
    X = np.asarray(X, dtype=float)
    A = 10.0
    d = X.shape[1]
    return A * d + np.sum(X**2 - A * np.cos(2.0 * np.pi * X), axis=1)


def hybrid_f20(X):
    """
    CEC-style hybrid benchmark.

    First half: Rastrigin.
    Second half: scaled Schwefel.
    """
    X = np.asarray(X, dtype=float)
    d = X.shape[1]
    h = d // 2

    return rastrigin(X[:, :h]) + schwefel(X[:, h:]) * (10.0 / 418.9829)


def composition_f28(X):
    """
    CEC-style composition benchmark.

    This is a lightweight approximation intended for reproducible
    experiments, not an official CEC implementation.
    """
    X = np.asarray(X, dtype=float)
    n, d = X.shape

    sigma = 100.0 * np.sqrt(d)

    centers = [
        np.zeros(d),
        np.full(d, 30.0),
        np.full(d, -30.0),
    ]

    funcs = [rastrigin, schwefel, rastrigin]

    weights = np.zeros((n, len(centers)))

    for k, center in enumerate(centers):
        dist2 = np.sum((X - center) ** 2, axis=1)
        weights[:, k] = np.exp(-dist2 / (2.0 * d * sigma**2))

    row_sum = np.sum(weights, axis=1, keepdims=True)
    row_sum[row_sum == 0.0] = 1.0
    weights /= row_sum

    result = np.zeros(n)

    for k, (center, func) in enumerate(zip(centers, funcs)):
        result += weights[:, k] * func(X - center)

    return result


BENCHMARKS = {
    "Sphere": {
        "func": sphere,
        "bounds": (-100.0, 100.0),
        "description": "Unimodal baseline function.",
    },
    "Schwefel": {
        "func": schwefel,
        "bounds": (-500.0, 500.0),
        "description": "Multimodal deceptive function.",
    },
    "Rastrigin": {
        "func": rastrigin,
        "bounds": (-5.12, 5.12),
        "description": "Highly multimodal benchmark function.",
    },
    "Hybrid": {
        "func": hybrid_f20,
        "bounds": (-5.12, 5.12),
        "description": "CEC-style hybrid landscape.",
    },
    "Composition": {
        "func": composition_f28,
        "bounds": (-5.12, 5.12),
        "description": "CEC-style composition landscape.",
    },
}