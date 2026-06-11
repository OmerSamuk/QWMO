import numpy as np
from core.agent import Agent
from operators.orbital import adaptive_orbital_sampling
from operators.pauli import pauli_exclusion
from operators.escape import adaptive_quantum_escape


class QWMO:
    def __init__(self, func, dimension, lower_bound, upper_bound,
                 population_size=50, max_fes=3000000,
                 gamma=0.05, c_base=5, kappa_0=8,
                 epsilon_r=0.05, k_s=10, eta_r=0.001,
                 epsilon_max_ratio=0.1, epsilon_min_ratio=0.01,
                 ablation_config='full', seed=None):
        self.func = func
        self.dimension = dimension
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.population_size = population_size
        self.max_fes = max_fes
        self.gamma = gamma
        self.c_base = c_base
        self.kappa_0 = kappa_0
        self.epsilon_r = epsilon_r
        self.k_s = k_s
        self.eta_r = eta_r
        self.epsilon_max_ratio = epsilon_max_ratio
        self.epsilon_min_ratio = epsilon_min_ratio
        self.ablation_config = ablation_config
        
        if seed is not None:
            np.random.seed(seed)
        
        self.agents = []
        self.best_agent = None
        self.fes_count = 0
        self.convergence_history = []
        self.pauli_collision_history = []
        self.escape_activation_history = []
        self.diversity_history = []
        self.diversity_interval = 500
        
    def initialize_population(self):
        self.agents = []
        for _ in range(self.population_size):
            position = np.random.uniform(self.lower_bound, self.upper_bound, self.dimension)
            fitness = self.func(position)
            self.fes_count += 1
            agent = Agent(position, fitness)
            self.agents.append(agent)
        
        self.best_agent = min(self.agents, key=lambda a: a.fitness)
        self.convergence_history.append(self.best_agent.fitness)
        self._record_diversity()
    
    def run(self):
        self.initialize_population()
        
        T_max = self.max_fes // self.population_size
        
        for t in range(1, T_max + 1):
            if self.fes_count >= self.max_fes:
                break
            
            fitnesses = [agent.fitness for agent in self.agents]
            best_fitness = min(fitnesses)
            worst_fitness = max(fitnesses)
            
            for agent in self.agents:
                new_position = adaptive_orbital_sampling(
                    agent, best_fitness, worst_fitness, t, T_max,
                    self.gamma, self.c_base, self.lower_bound, self.upper_bound
                )
                
                new_fitness = self.func(new_position)
                self.fes_count += 1
                agent.update_position(new_position, new_fitness)
                
                if agent.fitness < self.best_agent.fitness:
                    self.best_agent = agent.copy()
            
            if self.ablation_config in ['orbital_pauli', 'full']:
                collision_count = pauli_exclusion(
                    self.agents, t, T_max, self.lower_bound, self.upper_bound,
                    self.epsilon_max_ratio, self.epsilon_min_ratio
                )
                self.pauli_collision_history.append(collision_count)
            
            if self.ablation_config in ['orbital_escape', 'full']:
                escape_count = 0
                for agent in self.agents:
                    if agent.stagnation_count > self.k_s:
                        new_position = adaptive_quantum_escape(
                            agent, self.best_agent.position, t, T_max,
                            self.k_s, self.eta_r, self.lower_bound, self.upper_bound,
                            self.dimension
                        )
                        if new_position is not None:
                            new_fitness = self.func(new_position)
                            self.fes_count += 1
                            agent.position = new_position
                            agent.fitness = new_fitness
                            agent.stagnation_count = 0
                            escape_count += 1
                            
                            if agent.fitness < self.best_agent.fitness:
                                self.best_agent = agent.copy()
                self.escape_activation_history.append(escape_count)
            
            self.convergence_history.append(self.best_agent.fitness)
            
            if t % self.diversity_interval == 0:
                self._record_diversity()
        
        return self.best_agent.position, self.best_agent.fitness
    
    def _record_diversity(self):
        from scipy.spatial.distance import pdist
        positions = np.array([agent.position for agent in self.agents])
        if len(positions) > 1:
            distances = pdist(positions, 'euclidean')
            mean_distance = np.mean(distances)
            search_range = self.upper_bound - self.lower_bound
            normalized_distance = mean_distance / (search_range * np.sqrt(self.dimension))
            self.diversity_history.append(normalized_distance)
