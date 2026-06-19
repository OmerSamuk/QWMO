import numpy as np

from core.agent import Agent
from operators.orbital import adaptive_orbital_sampling
from operators.escape import adaptive_quantum_escape


class BudgetExceeded(Exception):
    pass


class QWMOCoreBinary:
    """V0: Pauli-free baseline for binary feature selection.

    Latent continuous optimisation + sigmoid(p > 0.5) mask.
    Orbital + Escape only (no Pauli exclusion).
    """

    def __init__(self, evaluator, n_features, lower_bound=-5.0, upper_bound=5.0,
                 population_size=50, max_fes=1000,
                 gamma=0.05, c_base=5, kappa_0=8,
                 k_s=10, eta_r=0.001,
                 seed=None):
        self.evaluator = evaluator
        self.n_features = n_features
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.population_size = population_size
        self.max_fes = max_fes
        self.gamma = gamma
        self.c_base = c_base
        self.kappa_0 = kappa_0
        self.k_s = k_s
        self.eta_r = eta_r

        self.rng = np.random.default_rng(seed)

        self.agents = []
        self.best_agent = None
        self.fes_count = 0

        self.convergence_history = []
        self.escape_attempt_history = []
        self.escape_executed_history = []
        self.escape_success_history = []

    def _decode_mask(self, latent_position):
        p = 1.0 / (1.0 + np.exp(-latent_position))
        return (p > 0.5).astype(int)

    def _evaluate(self, latent_position):
        if self.fes_count >= self.max_fes:
            raise BudgetExceeded
        mask = self._decode_mask(latent_position)
        selected = np.where(mask == 1)[0]
        if len(selected) == 0:
            fitness = 1.0
        else:
            fitness = self.evaluator(mask)
        self.fes_count += 1
        return fitness

    def initialize_population(self):
        self.agents = []
        for _ in range(self.population_size):
            position = self.rng.uniform(
                self.lower_bound, self.upper_bound, self.n_features
            )
            fitness = self._evaluate(position)
            agent = Agent(position, fitness)
            self.agents.append(agent)

        self.best_agent = min(self.agents, key=lambda a: a.fitness)
        self.convergence_history.append(self.best_agent.fitness)

    def run(self):
        self.initialize_population()

        T_max = self.max_fes // self.population_size

        for t in range(1, T_max + 1):
            if self.fes_count >= self.max_fes:
                break

            fitnesses = [agent.fitness for agent in self.agents]
            best_fitness = min(fitnesses)
            worst_fitness = max(fitnesses)

            new_positions = []
            for agent in self.agents:
                new_pos = adaptive_orbital_sampling(
                    agent, best_fitness, worst_fitness, t, T_max,
                    self.gamma, self.c_base,
                    self.lower_bound, self.upper_bound, self.rng
                )
                new_positions.append(new_pos)

            new_fitnesses = []
            try:
                for p in new_positions:
                    new_fitnesses.append(self._evaluate(p))
            except BudgetExceeded:
                break

            for agent, new_position, new_fitness in zip(
                self.agents, new_positions, new_fitnesses
            ):
                agent.update_position(new_position, new_fitness)
                if agent.fitness < self.best_agent.fitness:
                    self.best_agent = agent.copy()

            if self.fes_count >= self.max_fes:
                break

            phase = self._escape_phase(t, T_max)
            escape_attempts = 0
            escape_executed = 0
            escape_successes = 0
            for agent in self.agents:
                if agent.stagnation_count <= self.k_s:
                    continue
                escape_attempts += 1
                new_position = adaptive_quantum_escape(
                    agent, self.best_agent.position, t, T_max,
                    self.kappa_0, self.k_s, self.eta_r,
                    self.lower_bound, self.upper_bound,
                    self.n_features, self.rng
                )
                if new_position is None:
                    continue
                escape_executed += 1
                old_fitness = agent.fitness
                try:
                    new_fitness = self._evaluate(new_position)
                except BudgetExceeded:
                    break
                agent.position = new_position
                agent.fitness = new_fitness
                agent.stagnation_count = 0
                if new_fitness < old_fitness:
                    escape_successes += 1
                if agent.fitness < self.best_agent.fitness:
                    self.best_agent = agent.copy()

            self.escape_attempt_history.append(escape_attempts)
            self.escape_executed_history.append(escape_executed)
            self.escape_success_history.append(escape_successes)

            self.convergence_history.append(self.best_agent.fitness)

        return self.best_agent.position, self.best_agent.fitness

    @staticmethod
    def _escape_phase(t, T_max):
        ratio = t / T_max
        if ratio < 0.33:
            return 'early'
        if ratio < 0.66:
            return 'mid'
        return 'late'
