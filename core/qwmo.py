import numpy as np
from core.agent import Agent
from operators.orbital import adaptive_orbital_sampling, improvement_aware_orbital_sampling
from operators.pauli import pauli_exclusion
from operators.escape import adaptive_quantum_escape
from core.phase1_logger import Phase1Logger


class BudgetExceeded(Exception):
    pass


ABLATION_CONFIGS = {
    'orbital_only',
    'orbital_pauli_static',
    'orbital_pauli_dynamic',
    'orbital_pauli_adaptive',
    'orbital_pauli_gapr',
    'orbital_escape',
    'full_static',
    'full_dynamic',
    'full_adaptive',
    'full_gapr',
    'full_gapr_eps010',
    'phase1_v0',
    'phase1_v1',
    'phase1_v2',
    'phase1_v3',
    'csigma_full_old',
    'csigma_e_old',
    'csigma_csigma',
}


class QWMO:

    def __init__(self, func, dimension, lower_bound, upper_bound,
                 population_size=50, max_fes=3000000,
                 gamma=0.05, c_base=5, kappa_0=8,
                 k_s=10, eta_r=0.001,
                 epsilon_max_ratio=0.1, epsilon_min_ratio=0.01,
                 static_epsilon_ratio=0.05,
                 adaptive_k=3, adaptive_lambda0=0.75,
                 adaptive_epsilon_max_ratio=0.15,
                 ablation_config='full_dynamic', seed=None,
                 phase1_logger=None):
        if ablation_config not in ABLATION_CONFIGS:
            raise ValueError(
                f"ablation_config must be one of {sorted(ABLATION_CONFIGS)}, "
                f"got '{ablation_config}'"
            )

        self.func = func
        self.dimension = dimension
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.population_size = population_size
        self.max_fes = max_fes
        self.gamma = gamma
        self.c_base = c_base
        self.kappa_0 = kappa_0
        self.k_s = k_s
        self.eta_r = eta_r
        self.epsilon_max_ratio = epsilon_max_ratio
        self.epsilon_min_ratio = epsilon_min_ratio
        self.static_epsilon_ratio = static_epsilon_ratio
        self.adaptive_k = adaptive_k
        self.adaptive_lambda0 = adaptive_lambda0
        self.adaptive_epsilon_max_ratio = adaptive_epsilon_max_ratio
        self.ablation_config = ablation_config
        self.phase1_logger = phase1_logger

        self.use_pauli = ablation_config in (
            'orbital_pauli_static',
            'orbital_pauli_dynamic',
            'orbital_pauli_adaptive',
            'orbital_pauli_gapr',
            'full_static',
            'full_dynamic',
            'full_adaptive',
            'full_gapr',
            'full_gapr_eps010',
            'phase1_v1',
            'phase1_v2',
            'phase1_v3',
            'csigma_full_old',
        )
        if 'adaptive' in ablation_config or 'gapr' in ablation_config or ablation_config == 'phase1_v3':
            self.pauli_epsilon_mode = 'adaptive'
        elif 'static' in ablation_config or ablation_config == 'phase1_v1' or ablation_config == 'csigma_full_old':
            self.pauli_epsilon_mode = 'static'
        elif 'dynamic' in ablation_config or ablation_config == 'phase1_v2':
            self.pauli_epsilon_mode = 'dynamic'
        else:
            self.pauli_epsilon_mode = None
        self.use_escape = ablation_config in (
            'orbital_escape',
            'full_static',
            'full_dynamic',
            'full_adaptive',
            'full_gapr',
            'full_gapr_eps010',
            'phase1_v0',
            'phase1_v1',
            'phase1_v2',
            'phase1_v3',
            'csigma_full_old',
            'csigma_e_old',
            'csigma_csigma',
        )

        self.rng = np.random.default_rng(seed)

        self.orbital_mode = 'improvement_aware' if ablation_config == 'csigma_csigma' else 'time_decay'

        self.agents = []
        self.best_agent = None
        self.fes_count = 0

        self.convergence_history = []

        self.pauli_collision_history = []
        self.pauli_displacement_history = []
        self.pauli_success_history = []
        self.epsilon_history = []

        self.sigma_history = []
        self.k_history = []
        self.tau_history = []

        self.escape_attempt_history = []
        self.escape_executed_history = []
        self.escape_success_history = []
        self.escape_delta_history = []
        self.escape_phase_counts = {'early': 0, 'mid': 0, 'late': 0}

        self.diversity_history = []
        self.diversity_interval = 500

    def _evaluate(self, x):
        if self.fes_count >= self.max_fes:
            raise BudgetExceeded
        value = self.func(x)
        self.fes_count += 1
        return value

    def initialize_population(self):
        self.agents = []
        for _ in range(self.population_size):
            position = self.rng.uniform(
                self.lower_bound, self.upper_bound, self.dimension
            )
            fitness = self._evaluate(position)
            agent = Agent(position, fitness)
            self.agents.append(agent)

        self.best_agent = min(self.agents, key=lambda a: a.fitness)
        self.convergence_history.append(self.best_agent.fitness)
        self._record_diversity()

        if self.orbital_mode == 'improvement_aware':
            fitnesses = [a.fitness for a in self.agents]
            best_f = min(fitnesses)
            worst_f = max(fitnesses)
            search_range = self.upper_bound - self.lower_bound
            for agent in self.agents:
                qi = agent.compute_qi(best_f, worst_f)
                sigma_max_i = self.gamma * search_range * (2 - qi)
                agent.sigma_i = sigma_max_i
                agent.k_i = 0

    def _escape_phase(self, t, T_max):
        ratio = t / T_max
        if ratio < 0.33:
            return 'early'
        if ratio < 0.66:
            return 'mid'
        return 'late'

    def _get_sigma_max_i(self, qi):
        search_range = self.upper_bound - self.lower_bound
        return self.gamma * search_range * (2 - qi)

    def _update_csigma_sigmas(self, pre_fitnesses):
        fitnesses = [a.fitness for a in self.agents]
        best_f = min(fitnesses)
        worst_f = max(fitnesses)

        denom = max(
            worst_f - best_f,
            1e-8 * (abs(best_f) + 1)
        )

        r_values = []
        for i, agent in enumerate(self.agents):
            f_old = pre_fitnesses[i]
            f_new = agent.fitness
            r_raw = (f_old - f_new) / denom
            r_i = np.tanh(r_raw)
            r_values.append(r_i)

        positive_rs = [r for r in r_values if r > 0]
        if positive_rs:
            median_pos = float(np.median(positive_rs))
            tau = max(1e-6, 1e-3 * median_pos)
        else:
            tau = 1e-6

        for i, agent in enumerate(self.agents):
            r_i = r_values[i]
            if r_i > tau:
                agent.sigma_i = agent.sigma_i * (1 - 0.01 * r_i)
                agent.k_i = 0
            else:
                agent.sigma_i = agent.sigma_i * (1 + 0.01)
                agent.k_i += 1
            qi = agent.compute_qi(best_f, worst_f)
            sigma_max_i = self._get_sigma_max_i(qi)
            agent.sigma_i = float(np.clip(agent.sigma_i, 1e-10, sigma_max_i))

        sigmas = [a.sigma_i for a in self.agents]
        ks = [a.k_i for a in self.agents]
        self.sigma_history.append({
            'mean': float(np.mean(sigmas)),
            'median': float(np.median(sigmas)),
            'min': float(np.min(sigmas)),
            'max': float(np.max(sigmas)),
        })
        self.k_history.append({
            'mean': float(np.mean(ks)),
            'stagnant': int(sum(1 for k in ks if k > 0)),
        })
        self.tau_history.append(tau)

    def run(self):
        self.initialize_population()

        T_max = self.max_fes // self.population_size

        for t in range(1, T_max + 1):
            if self.fes_count >= self.max_fes:
                break

            pre_positions = np.array([agent.position for agent in self.agents])

            pre_fitnesses = [agent.fitness for agent in self.agents]
            fitnesses = list(pre_fitnesses)
            best_fitness = min(fitnesses)
            worst_fitness = max(fitnesses)

            new_positions = []
            if self.orbital_mode == 'improvement_aware':
                for agent in self.agents:
                    new_pos = improvement_aware_orbital_sampling(
                        agent, best_fitness, worst_fitness,
                        self.lower_bound, self.upper_bound, self.rng,
                        self.gamma
                    )
                    new_positions.append(new_pos)
            else:
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

            if self.orbital_mode == 'improvement_aware':
                self._update_csigma_sigmas(pre_fitnesses)

            pauli_events = []
            escape_events = []
            escape_attempts = 0
            epsilon_value = None
            collision_count = 0
            displacement_count = 0

            if self.use_pauli:
                try:
                    pauli_info = pauli_exclusion(
                        agents=self.agents,
                        evaluate=self._evaluate,
                        rng=self.rng,
                        t=t,
                        T_max=T_max,
                        lower_bound=self.lower_bound,
                        upper_bound=self.upper_bound,
                        dimension=self.dimension,
                        epsilon_mode=self.pauli_epsilon_mode,
                        epsilon_max_ratio=self.epsilon_max_ratio,
                        epsilon_min_ratio=self.epsilon_min_ratio,
                        static_epsilon_ratio=self.static_epsilon_ratio,
                        adaptive_k=self.adaptive_k,
                        adaptive_lambda0=self.adaptive_lambda0,
                        adaptive_epsilon_max_ratio=self.adaptive_epsilon_max_ratio,
                    )
                except BudgetExceeded:
                    break

                epsilon_value = pauli_info["epsilon"]
                collision_count = pauli_info["collision_count"]
                displacement_count = pauli_info["displacement_count"]
                pauli_events = pauli_info.get("events", [])

                self.epsilon_history.append(epsilon_value)
                self.pauli_collision_history.append(collision_count)
                self.pauli_displacement_history.append(displacement_count)
                self.pauli_success_history.append(pauli_info["success_count"])

                for agent in self.agents:
                    if agent.fitness < self.best_agent.fitness:
                        self.best_agent = agent.copy()

            if self.use_escape:
                escape_executed = 0
                escape_successes = 0
                delta_sum = 0.0
                phase = self._escape_phase(t, T_max)
                for idx, agent in enumerate(self.agents):
                    if agent.stagnation_count <= self.k_s:
                        continue
                    escape_attempts += 1
                    new_position = adaptive_quantum_escape(
                        agent, self.best_agent.position, t, T_max,
                        self.kappa_0, self.k_s, self.eta_r,
                        self.lower_bound, self.upper_bound,
                        self.dimension, self.rng
                    )
                    if new_position is None:
                        continue
                    escape_executed += 1
                    old_fitness_esc = agent.fitness
                    try:
                        new_fitness = self._evaluate(new_position)
                    except BudgetExceeded:
                        break
                    delta = old_fitness_esc - new_fitness
                    agent.position = new_position
                    agent.fitness = new_fitness
                    agent.stagnation_count = 0
                    delta_sum += delta
                    escape_events.append((idx, old_fitness_esc))
                    if new_fitness < old_fitness_esc:
                        escape_successes += 1
                        self.escape_phase_counts[phase] += 1
                    if agent.fitness < self.best_agent.fitness:
                        self.best_agent = agent.copy()

                self.escape_attempt_history.append(escape_attempts)
                self.escape_executed_history.append(escape_executed)
                self.escape_success_history.append(escape_successes)
                mean_delta = (
                    delta_sum / escape_executed if escape_executed > 0 else 0.0
                )
                self.escape_delta_history.append(mean_delta)

            self.convergence_history.append(self.best_agent.fitness)

            if t % self.diversity_interval == 0:
                self._record_diversity()

            sigma_kwargs = {}
            if self.orbital_mode == 'improvement_aware' and self.sigma_history:
                s = self.sigma_history[-1]
                k_info = self.k_history[-1]
                sigma_kwargs = {
                    'sigma_mean': s['mean'],
                    'sigma_median': s['median'],
                    'sigma_min': s['min'],
                    'sigma_max': s['max'],
                    'k_mean': k_info['mean'],
                    'k_stagnant_count': k_info['stagnant'],
                    'tau_value': self.tau_history[-1],
                }

            if self.phase1_logger:
                self.phase1_logger.record_iteration(
                    t=t, agents=self.agents, best_agent=self.best_agent,
                    epsilon_value=epsilon_value,
                    collision_count=collision_count,
                    displacement_count=displacement_count,
                    escape_triggered_count=escape_attempts,
                    pauli_events=pauli_events if pauli_events else None,
                    escape_events=escape_events if escape_events else None,
                    new_positions=new_positions,
                    old_positions_for_clipping=pre_positions,
                    **sigma_kwargs,
                )

        if len(self.convergence_history) == 0 or self.convergence_history[-1] != self.best_agent.fitness:
            self.convergence_history.append(self.best_agent.fitness)

        return self.best_agent.position, self.best_agent.fitness

    def _record_diversity(self):
        from scipy.spatial.distance import pdist
        positions = np.array([agent.position for agent in self.agents])
        if len(positions) > 1:
            distances = pdist(positions, 'euclidean')
            mean_distance = np.mean(distances)
            search_range = self.upper_bound - self.lower_bound
            normalized_distance = mean_distance / (
                search_range * np.sqrt(self.dimension)
            )
            self.diversity_history.append(normalized_distance)
