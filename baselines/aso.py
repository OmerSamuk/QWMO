import numpy as np


class ASO:
    def __init__(self, func, dimension, lower_bound, upper_bound,
                 population_size=50, max_fes=3000000,
                 alpha=50, beta=0.2, seed=None):
        self.func = func
        self.dimension = dimension
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.population_size = population_size
        self.max_fes = max_fes
        self.alpha = alpha
        self.beta = beta
        
        if seed is not None:
            np.random.seed(seed)
        
        self.positions = None
        self.velocities = None
        self.fitness = None
        self.best_position = None
        self.best_fitness = None
        self.fes_count = 0
        self.convergence_history = []
    
    def lj_potential(self, atom1, atom2, iteration, max_iteration, s):
        r = np.linalg.norm(atom1 - atom2)
        c = (1 - (iteration - 1) / max_iteration) ** 3
        
        rsmin = 1.1 + 0.1 * np.sin(iteration / max_iteration * np.pi / 2)
        rsmax = 1.24
        
        if r / s < rsmin:
            rs = rsmin
        elif r / s > rsmax:
            rs = rsmax
        else:
            rs = r / s
        
        potential = c * (12 * (-rs) ** (-13) - 6 * (-rs) ** (-7))
        return potential
    
    def compute_acceleration(self, iteration, max_iteration):
        M = np.exp(-(self.fitness - np.max(self.fitness)) / (np.max(self.fitness) - np.min(self.fitness) + 1e-10))
        M = M / np.sum(M)
        
        G = np.exp(-20 * iteration / max_iteration)
        Kbest = self.population_size - (self.population_size - 2) * (iteration / max_iteration) ** 0.5
        Kbest = int(np.floor(Kbest)) + 1
        
        sorted_indices = np.argsort(-M)
        
        acceleration = np.zeros((self.population_size, self.dimension))
        
        for i in range(self.population_size):
            E = np.zeros(self.dimension)
            MK = np.mean(self.positions[sorted_indices[:Kbest]], axis=0)
            distance = np.linalg.norm(self.positions[i] - MK)
            
            for k in range(Kbest):
                j = sorted_indices[k]
                potential = self.lj_potential(self.positions[i], self.positions[j], 
                                             iteration, max_iteration, distance)
                E += np.random.random(self.dimension) * potential * \
                     ((self.positions[j] - self.positions[i]) / (np.linalg.norm(self.positions[i] - self.positions[j]) + 1e-10))
            
            E = self.alpha * E + self.beta * (self.best_position - self.positions[i])
            acceleration[i] = E / (M[i] + 1e-10)
        
        return acceleration * G
    
    def run(self):
        self.positions = np.random.uniform(self.lower_bound, self.upper_bound, 
                                          (self.population_size, self.dimension))
        self.velocities = np.random.uniform(self.lower_bound, self.upper_bound, 
                                           (self.population_size, self.dimension))
        
        self.fitness = np.zeros(self.population_size)
        for i in range(self.population_size):
            self.fitness[i] = self.func(self.positions[i])
            self.fes_count += 1
        
        best_idx = np.argmin(self.fitness)
        self.best_position = self.positions[best_idx].copy()
        self.best_fitness = self.fitness[best_idx]
        self.convergence_history.append(self.best_fitness)
        
        max_iteration = self.max_fes // self.population_size
        
        for iteration in range(2, max_iteration + 1):
            if self.fes_count >= self.max_fes:
                break
            
            acceleration = self.compute_acceleration(iteration, max_iteration)
            
            self.velocities = np.random.random((self.population_size, self.dimension)) * self.velocities + acceleration
            self.positions = self.positions + self.velocities
            
            for i in range(self.population_size):
                out_of_bounds = (self.positions[i] > self.upper_bound) | (self.positions[i] < self.lower_bound)
                if np.any(out_of_bounds):
                    self.positions[i, out_of_bounds] = np.random.uniform(self.lower_bound, self.upper_bound, 
                                                                         np.sum(out_of_bounds))
                
                self.fitness[i] = self.func(self.positions[i])
                self.fes_count += 1
            
            min_fitness = np.min(self.fitness)
            
            if min_fitness < self.best_fitness:
                best_idx = np.argmin(self.fitness)
                self.best_fitness = min_fitness
                self.best_position = self.positions[best_idx].copy()
            else:
                r = np.random.randint(0, self.population_size)
                self.positions[r] = self.best_position.copy()
            
            self.convergence_history.append(self.best_fitness)
        
        return self.best_position, self.best_fitness
