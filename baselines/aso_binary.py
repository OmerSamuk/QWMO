import numpy as np

from baselines.aso import ASO


class ASOBinary:
    def __init__(self, evaluator, n_features, lower_bound=-5.0, upper_bound=5.0,
                 population_size=50, max_fes=1000,
                 alpha=50, beta=0.2, seed=None):
        self.evaluator = evaluator
        self.n_features = n_features
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.population_size = population_size
        self.max_fes = max_fes
        self.alpha = alpha
        self.beta = beta

        self.rng = np.random.default_rng(seed)
        self.fes_count = 0
        self.convergence_history = []

        self._aso = None

    def _decode_mask(self, latent_position):
        p = 1.0 / (1.0 + np.exp(-latent_position))
        return (p > 0.5).astype(int)

    def _eval_func(self, latent_position):
        if self.fes_count >= self.max_fes:
            return 1.0
        mask = self._decode_mask(latent_position)
        fitness = self.evaluator(mask)
        self.fes_count += 1
        return fitness

    def run(self):
        self._aso = ASO(
            func=self._eval_func,
            dimension=self.n_features,
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound,
            population_size=self.population_size,
            max_fes=self.max_fes,
            alpha=self.alpha,
            beta=self.beta,
            seed=int(self.rng.integers(0, 2**31)),
        )

        best_pos, best_fit = self._aso.run()
        self.fes_count = self._aso.fes_count
        self.convergence_history = self._aso.convergence_history

        return best_pos, best_fit
