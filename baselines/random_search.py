import numpy as np


class RandomSearch:
    """M0: Random feature subset selection baseline."""

    def __init__(self, evaluator, n_features, lower_bound=-5.0, upper_bound=5.0,
                 population_size=50, max_fes=1000, seed=None):
        self.evaluator = evaluator
        self.n_features = n_features
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.population_size = population_size
        self.max_fes = max_fes
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
        selected = np.where(mask == 1)[0]
        if len(selected) == 0:
            fitness = 1.0
        else:
            fitness = self.evaluator(mask)
        self.fes_count += 1
        return fitness

    def run(self):
        best_fitness = float("inf")
        best_position = None

        while self.fes_count < self.max_fes:
            position = self.rng.uniform(
                self.lower_bound, self.upper_bound, self.n_features
            )
            fitness = self._evaluate(position)
            if fitness < best_fitness:
                best_fitness = fitness
                best_position = position
            self.convergence_history.append(best_fitness)

        return best_position, best_fitness
