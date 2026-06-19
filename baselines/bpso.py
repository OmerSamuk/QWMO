import numpy as np


class BPSO:
    """M4: Binary Particle Swarm Optimisation for feature selection.

    Adaptado de QPSO (latent continuous + sigmoid decoding).
    """

    def __init__(self, evaluator, n_features, lower_bound=-5.0, upper_bound=5.0,
                 population_size=50, max_fes=1000,
                 w=0.7, c1=2.0, c2=2.0, v_max=3.0, seed=None):
        self.evaluator = evaluator
        self.n_features = n_features
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.population_size = population_size
        self.max_fes = max_fes
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.v_max = v_max

        self.rng = np.random.default_rng(seed)
        self.fes_count = 0
        self.convergence_history = []

    def _decode_mask(self, latent_position):
        p = 1.0 / (1.0 + np.exp(-latent_position))
        return (p > 0.5).astype(int)

    def _evaluate(self, latent_position):
        if self.fes_count >= self.max_fes:
            return 1.0
        mask = self._decode_mask(latent_position)
        fitness = self.evaluator(mask)
        self.fes_count += 1
        return fitness

    def run(self):
        positions = self.rng.uniform(
            self.lower_bound, self.upper_bound,
            (self.population_size, self.n_features)
        )
        velocities = self.rng.uniform(
            -self.v_max, self.v_max,
            (self.population_size, self.n_features)
        )

        pbest = positions.copy()
        pbest_fitness = np.array([self._evaluate(p) for p in positions])

        gbest_idx = np.argmin(pbest_fitness)
        gbest = positions[gbest_idx].copy()
        gbest_fitness = pbest_fitness[gbest_idx]

        self.convergence_history.append(gbest_fitness)

        while self.fes_count < self.max_fes:
            for i in range(self.population_size):
                r1 = self.rng.random(self.n_features)
                r2 = self.rng.random(self.n_features)

                velocities[i] = (
                    self.w * velocities[i]
                    + self.c1 * r1 * (pbest[i] - positions[i])
                    + self.c2 * r2 * (gbest - positions[i])
                )
                velocities[i] = np.clip(velocities[i], -self.v_max, self.v_max)

                positions[i] = positions[i] + velocities[i]
                positions[i] = np.clip(positions[i], self.lower_bound, self.upper_bound)

                fitness = self._evaluate(positions[i])

                if fitness < pbest_fitness[i]:
                    pbest[i] = positions[i].copy()
                    pbest_fitness[i] = fitness

                    if fitness < gbest_fitness:
                        gbest = positions[i].copy()
                        gbest_fitness = fitness

            self.convergence_history.append(gbest_fitness)

        return gbest, gbest_fitness
