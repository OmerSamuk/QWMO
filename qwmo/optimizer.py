import numpy as np
from scipy.spatial import KDTree


class QWMO:
    """
    Quantum Wave-function Metaheuristic Optimizer.

    Reference implementation for continuous minimization problems.
    """

    def __init__(
        self,
        func,
        dim,
        bounds=(-100.0, 100.0),
        population_size=None,
        max_iter=None,
        seed=None,
        sigma_ratio=0.05,
        c_base=5.0,
        kappa_0=8.0,
        epsilon_ratio=0.05,
        k_stagnation=10,
        noise_ratio=0.001,
        enable_pauli=True,
        enable_tunneling=True,
    ):
        self.func = func
        self.dim = int(dim)
        self.lo, self.hi = float(bounds[0]), float(bounds[1])
        self.population_size = population_size or max(30, 10 * self.dim)
        self.max_iter = max_iter or 10_000 * self.dim
        self.seed = seed

        self.rng = np.random.default_rng(seed)

        bounds_range = self.hi - self.lo
        self.sigma_base = sigma_ratio * bounds_range
        self.sigma_noise = noise_ratio * bounds_range
        self.epsilon = epsilon_ratio * bounds_range

        self.c_base = c_base
        self.kappa_0 = kappa_0
        self.k_stagnation = k_stagnation
        self.enable_pauli = enable_pauli
        self.enable_tunneling = enable_tunneling

        self.l_max = np.linalg.norm(
            np.full(self.dim, self.hi) - np.full(self.dim, self.lo)
        )

        self.n_evals = 0

        self.X = self.rng.uniform(
            self.lo, self.hi, size=(self.population_size, self.dim)
        )
        self.fitness = self._evaluate(self.X)

        best_idx = np.argmin(self.fitness)
        self.best_position = self.X[best_idx].copy()
        self.best_fitness = float(self.fitness[best_idx])

        self.stagnation = np.zeros(self.population_size, dtype=int)
        self.history = [self.best_fitness]

    def _evaluate(self, X):
        X = np.clip(np.asarray(X, dtype=float), self.lo, self.hi)
        values = np.asarray(self.func(X), dtype=float)

        if values.shape != (X.shape[0],):
            raise ValueError(
                "Objective function must accept X with shape (n, dim) "
                "and return an array with shape (n,)."
            )

        self.n_evals += X.shape[0]
        return values

    def _clip(self, X):
        return np.clip(X, self.lo, self.hi)

    def _update_best(self):
        idx = np.argmin(self.fitness)
        if self.fitness[idx] < self.best_fitness:
            self.best_fitness = float(self.fitness[idx])
            self.best_position = self.X[idx].copy()

    def _orbital_sampling(self, t):
        f_best = np.min(self.fitness)
        f_worst = np.max(self.fitness)
        denom = f_worst - f_best + 1e-12

        for i in range(self.population_size):
            quality = (f_worst - self.fitness[i]) / denom

            sigma_max_i = self.sigma_base * (2.0 - quality)
            c_i = self.c_base * quality
            sigma_i = max(
                sigma_max_i * np.exp(-c_i * t / self.max_iter),
                1e-12,
            )

            candidate = self.rng.normal(self.X[i], sigma_i, size=self.dim)
            candidate = self._clip(candidate)
            candidate_f = self._evaluate(candidate.reshape(1, -1))[0]

            if candidate_f < self.fitness[i]:
                self.X[i] = candidate
                self.fitness[i] = candidate_f
                self.stagnation[i] = 0
            else:
                self.stagnation[i] += 1

    def _pauli_exclusion(self):
        tree = KDTree(self.X)
        pairs = list(tree.query_pairs(r=self.epsilon))

        for i, j in pairs:
            bad, good = (i, j) if self.fitness[i] > self.fitness[j] else (j, i)

            v = self.X[bad] - self.X[good]
            v_norm = np.linalg.norm(v)

            if v_norm < 1e-12:
                perp = self.rng.normal(size=self.dim)
                perp_norm = np.linalg.norm(perp)
                perp = perp / (perp_norm + 1e-12)
            else:
                r = self.rng.normal(size=self.dim)
                perp = r - (np.dot(r, v) / (v_norm**2 + 1e-12)) * v
                perp_norm = np.linalg.norm(perp)

                if perp_norm < 1e-12:
                    perp = self.rng.normal(size=self.dim)
                    perp_norm = np.linalg.norm(perp)

                perp = perp / (perp_norm + 1e-12)

            alpha = self.rng.uniform(0.5, 1.5) * self.epsilon

            self.X[bad] = self._clip(self.X[bad] + alpha * perp)
            self.fitness[bad] = self._evaluate(self.X[bad].reshape(1, -1))[0]
            self.stagnation[bad] = 0

    def _quantum_tunneling(self, t):
        kappa_t = self.kappa_0 * (t / self.max_iter)

        for i in range(self.population_size):
            if self.stagnation[i] <= self.k_stagnation:
                continue

            distance = np.linalg.norm(self.X[i] - self.best_position)
            distance_norm = distance / (self.l_max + 1e-12)

            p_escape = np.exp(-2.0 * kappa_t * distance_norm)

            if self.rng.random() < p_escape:
                beta = self.rng.random()
                random_point = self.rng.uniform(self.lo, self.hi, size=self.dim)
                noise = self.rng.normal(0.0, self.sigma_noise, size=self.dim)

                destination = (
                    beta * (self.best_position + noise)
                    + (1.0 - beta) * random_point
                )

                self.X[i] = self._clip(destination)
                self.fitness[i] = self._evaluate(self.X[i].reshape(1, -1))[0]
                self.stagnation[i] = 0

    def step(self, t):
        self._orbital_sampling(t)
        self._update_best()

        if self.enable_pauli:
            self._pauli_exclusion()
            self._update_best()

        if self.enable_tunneling:
            self._quantum_tunneling(t)
            self._update_best()

    def optimize(self):
        for t in range(1, self.max_iter + 1):
            self.step(t)
            self.history.append(self.best_fitness)

        return self.best_position, self.best_fitness, self.history

    def __repr__(self):
        return (
            f"QWMO(dim={self.dim}, population_size={self.population_size}, "
            f"max_iter={self.max_iter})"
        )