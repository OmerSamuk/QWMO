import numpy as np


class AOS:
    def __init__(self, func, dimension, lower_bound, upper_bound,
                 population_size=50, max_fes=3000000,
                 layer_number=5, foton_rate=0.1, seed=None):
        self.func = func
        self.dimension = dimension
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.population_size = population_size
        self.max_fes = max_fes
        self.layer_number = layer_number
        self.foton_rate = foton_rate
        
        if seed is not None:
            np.random.seed(seed)
        
        self.positions = None
        self.fitness = None
        self.best_position = None
        self.best_fitness = None
        self.fes_count = 0
        self.convergence_history = []
    
    def run(self):
        self.positions = np.random.uniform(self.lower_bound, self.upper_bound, 
                                          (self.population_size, self.dimension))
        
        self.fitness = np.zeros(self.population_size)
        for i in range(self.population_size):
            self.fitness[i] = self.func(self.positions[i])
            self.fes_count += 1
        
        sorted_indices = np.argsort(self.fitness)
        self.positions = self.positions[sorted_indices]
        self.fitness = self.fitness[sorted_indices]
        
        self.best_position = self.positions[0].copy()
        self.best_fitness = self.fitness[0]
        mean_pop = np.mean(self.positions, axis=0)
        
        self.convergence_history.append(self.best_fitness)
        
        while self.fes_count < self.max_fes:
            max_lay = np.random.randint(1, self.layer_number + 1)
            
            nor_disp_input = np.arange(1, max_lay + 1)
            mu = 0
            sigma = max_lay / 6
            from scipy.stats import norm
            nor_disp = norm.pdf(nor_disp_input, mu, sigma)
            
            nor_disp_cal = np.zeros((5, len(nor_disp)))
            nor_disp_cal[0] = nor_disp
            nor_disp_cal[1] = nor_disp_cal[0] / np.sum(nor_disp_cal[0])
            nor_disp_cal[2] = self.population_size * nor_disp_cal[1]
            nor_disp_cal[3] = np.round(nor_disp_cal[2])
            nor_disp_cal[4] = np.cumsum(nor_disp_cal[3])
            
            lay_col = np.concatenate([[0], nor_disp_cal[4]])
            lay_col = lay_col.astype(int)
            lay_col[lay_col > self.population_size] = self.population_size
            
            pop_c = []
            cost_c = []
            
            for i in range(max_lay):
                start_idx = lay_col[i]
                end_idx = lay_col[i + 1]
                
                if start_idx >= end_idx:
                    continue
                
                pop_a = self.positions[start_idx:end_idx]
                cost_a = self.fitness[start_idx:end_idx]
                
                if len(cost_a) == 0:
                    continue
                
                energy = np.mean(cost_a)
                orbit = i + 1
                
                pop_b = np.zeros_like(pop_a)
                cost_b = np.zeros(len(pop_a))
                
                for j in range(len(pop_a)):
                    if np.random.random() > self.foton_rate:
                        if cost_a[j] > energy:
                            ir = np.random.uniform(0, 1, 2)
                            jr = np.random.uniform(0, 1, self.dimension)
                            x_old = pop_a[j]
                            x_best = self.best_position
                            x_mean = mean_pop
                            pop_b[j] = x_old + jr * (ir[0] * x_best - ir[1] * x_mean) / orbit
                        else:
                            ir = np.random.uniform(0, 1, 2)
                            jr = np.random.uniform(0, 1, self.dimension)
                            x_old = pop_a[j]
                            x_best = pop_a[0] if len(pop_a) > 0 else self.best_position
                            x_mean = np.mean(pop_a, axis=0) if len(pop_a) > 1 else pop_a[0]
                            pop_b[j] = x_old + jr * (ir[0] * x_best - ir[1] * x_mean)
                    else:
                        pop_b[j] = np.random.uniform(self.lower_bound, self.upper_bound, self.dimension)
                    
                    pop_b[j] = np.clip(pop_b[j], self.lower_bound, self.upper_bound)
                    cost_b[j] = self.func(pop_b[j])
                    self.fes_count += 1
                
                pop_c.append(pop_b)
                cost_c.append(cost_b)
            
            if len(pop_c) > 0:
                pop_c = np.vstack(pop_c)
                cost_c = np.concatenate(cost_c)
                
                self.positions = np.vstack([self.positions, pop_c])
                self.fitness = np.concatenate([self.fitness, cost_c])
                
                sorted_indices = np.argsort(self.fitness)
                self.positions = self.positions[sorted_indices]
                self.fitness = self.fitness[sorted_indices]
                
                if self.fitness[0] < self.best_fitness:
                    self.best_position = self.positions[0].copy()
                    self.best_fitness = self.fitness[0]
                
                mean_pop = np.mean(self.positions[:self.population_size], axis=0)
                
                self.positions = self.positions[:self.population_size]
                self.fitness = self.fitness[:self.population_size]
            
            self.convergence_history.append(self.best_fitness)
        
        return self.best_position, self.best_fitness
