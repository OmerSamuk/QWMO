import numpy as np


class QPSO:
    def __init__(self, func, dimension, lower_bound, upper_bound,
                 population_size=50, max_fes=3000000,
                 alpha_max=1.0, alpha_min=0.5, seed=None):
        self.func = func
        self.dimension = dimension
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.population_size = population_size
        self.max_fes = max_fes
        self.alpha_max = alpha_max
        self.alpha_min = alpha_min
        
        if seed is not None:
            np.random.seed(seed)
        
        self.positions = None
        self.pbest = None
        self.pbest_fitness = None
        self.gbest = None
        self.gbest_fitness = None
        self.fes_count = 0
        self.convergence_history = []
    
    def run(self):
        self.positions = np.random.uniform(self.lower_bound, self.upper_bound, 
                                          (self.population_size, self.dimension))
        
        self.pbest = self.positions.copy()
        self.pbest_fitness = np.zeros(self.population_size)
        
        for i in range(self.population_size):
            self.pbest_fitness[i] = self.func(self.positions[i])
            self.fes_count += 1
        
        best_idx = np.argmin(self.pbest_fitness)
        self.gbest = self.pbest[best_idx].copy()
        self.gbest_fitness = self.pbest_fitness[best_idx]
        
        self.convergence_history.append(self.gbest_fitness)
        
        max_iteration = self.max_fes // self.population_size
        
        for iteration in range(1, max_iteration + 1):
            if self.fes_count >= self.max_fes:
                break
            
            alpha = self.alpha_max - (self.alpha_max - self.alpha_min) * iteration / max_iteration
            
            mbest = np.mean(self.pbest, axis=0)
            
            for i in range(self.population_size):
                fi = np.random.random(self.dimension)
                p = fi * self.pbest[i] + (1 - fi) * self.gbest
                
                u = np.random.random(self.dimension)
                
                if np.random.random() > 0.5:
                    self.positions[i] = p + alpha * np.abs(mbest - self.positions[i]) * np.log(1 / (u + 1e-10))
                else:
                    self.positions[i] = p - alpha * np.abs(mbest - self.positions[i]) * np.log(1 / (u + 1e-10))
                
                self.positions[i] = np.clip(self.positions[i], self.lower_bound, self.upper_bound)
                
                fitness = self.func(self.positions[i])
                self.fes_count += 1
                
                if fitness < self.pbest_fitness[i]:
                    self.pbest[i] = self.positions[i].copy()
                    self.pbest_fitness[i] = fitness
                    
                    if fitness < self.gbest_fitness:
                        self.gbest = self.positions[i].copy()
                        self.gbest_fitness = fitness
            
            self.convergence_history.append(self.gbest_fitness)
        
        return self.gbest, self.gbest_fitness
