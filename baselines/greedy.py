import numpy as np


class ForwardSelection:
    """M1: Greedy forward feature selection."""

    def __init__(self, evaluator, n_features, lower_bound=None, upper_bound=None,
                 population_size=None, max_fes=1000, seed=None):
        self.evaluator = evaluator
        self.n_features = n_features
        self.max_fes = max_fes
        self.rng = np.random.default_rng(seed)
        self.fes_count = 0
        self.convergence_history = []

    def run(self):
        selected = []
        remaining = list(range(self.n_features))
        best_fitness = float("inf")

        for _ in range(self.n_features):
            if self.fes_count >= self.max_fes:
                break

            candidates = []
            for feat in remaining:
                mask = np.zeros(self.n_features, dtype=int)
                mask[selected + [feat]] = 1
                fitness = self.evaluator(mask)
                self.fes_count += 1
                candidates.append((feat, fitness))
                if self.fes_count >= self.max_fes:
                    break

            if not candidates:
                break

            best_feat, best_candidate_fitness = min(candidates, key=lambda x: x[1])

            if best_candidate_fitness < best_fitness:
                best_fitness = best_candidate_fitness
                selected.append(best_feat)
                remaining.remove(best_feat)
            else:
                break

            self.convergence_history.append(best_fitness)

        best_mask = np.zeros(self.n_features, dtype=int)
        best_mask[selected] = 1
        return best_mask, best_fitness


class BackwardSelection:
    """M2: Greedy backward feature selection."""

    def __init__(self, evaluator, n_features, lower_bound=None, upper_bound=None,
                 population_size=None, max_fes=1000, seed=None):
        self.evaluator = evaluator
        self.n_features = n_features
        self.max_fes = max_fes
        self.rng = np.random.default_rng(seed)
        self.fes_count = 0
        self.convergence_history = []

    def run(self):
        selected = list(range(self.n_features))
        best_fitness = float("inf")

        mask = np.ones(self.n_features, dtype=int)
        best_fitness = self.evaluator(mask)
        self.fes_count += 1
        self.convergence_history.append(best_fitness)

        while len(selected) > 1 and self.fes_count < self.max_fes:
            candidates = []
            for feat in selected:
                candidate = [f for f in selected if f != feat]
                mask = np.zeros(self.n_features, dtype=int)
                mask[candidate] = 1
                fitness = self.evaluator(mask)
                self.fes_count += 1
                candidates.append((feat, fitness, candidate))
                if self.fes_count >= self.max_fes:
                    break

            if not candidates:
                break

            worst_feat, candidate_fitness, candidate_set = min(candidates, key=lambda x: x[1])

            if candidate_fitness < best_fitness:
                best_fitness = candidate_fitness
                selected = candidate_set
            else:
                break

            self.convergence_history.append(best_fitness)

        best_mask = np.zeros(self.n_features, dtype=int)
        best_mask[selected] = 1
        return best_mask, best_fitness
