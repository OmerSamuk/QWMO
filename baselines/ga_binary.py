import numpy as np


class GABinary:
    """M3: Genetic Algorithm for binary feature selection."""

    def __init__(self, evaluator, n_features, lower_bound=-5.0, upper_bound=5.0,
                 population_size=50, max_fes=1000,
                 crossover_rate=0.8, mutation_rate=0.05, tournament_k=3,
                 seed=None):
        self.evaluator = evaluator
        self.n_features = n_features
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.population_size = population_size
        self.max_fes = max_fes
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_k = tournament_k

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

    def _tournament_select(self, population, fitnesses):
        indices = self.rng.choice(len(population), self.tournament_k, replace=False)
        best_idx = indices[np.argmin([fitnesses[i] for i in indices])]
        return population[best_idx].copy()

    def _crossover(self, parent1, parent2):
        if self.rng.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        point = self.rng.integers(1, self.n_features - 1)
        child1 = np.concatenate([parent1[:point], parent2[point:]])
        child2 = np.concatenate([parent2[:point], parent1[point:]])
        return child1, child2

    def _mutate(self, position):
        mask = self.rng.random(self.n_features) < self.mutation_rate
        noise = self.rng.uniform(-0.5, 0.5, self.n_features) * mask
        return np.clip(position + noise, self.lower_bound, self.upper_bound)

    def run(self):
        population = self.rng.uniform(
            self.lower_bound, self.upper_bound,
            (self.population_size, self.n_features)
        )

        fitnesses = [self._evaluate(ind) for ind in population]
        best_idx = np.argmin(fitnesses)
        best_position = population[best_idx].copy()
        best_fitness = fitnesses[best_idx]
        self.convergence_history.append(best_fitness)

        while self.fes_count < self.max_fes:
            new_population = []

            while len(new_population) < self.population_size:
                p1 = self._tournament_select(population, fitnesses)
                p2 = self._tournament_select(population, fitnesses)
                c1, c2 = self._crossover(p1, p2)
                c1 = self._mutate(c1)
                c2 = self._mutate(c2)
                new_population.append(c1)
                if len(new_population) < self.population_size:
                    new_population.append(c2)

            population = np.array(new_population[:self.population_size])
            fitnesses = [self._evaluate(ind) for ind in population]

            for i, f in enumerate(fitnesses):
                if f < best_fitness:
                    best_fitness = f
                    best_position = population[i].copy()

            self.convergence_history.append(best_fitness)

        return best_position, best_fitness
