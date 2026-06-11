import numpy as np


class Agent:
    def __init__(self, position, fitness=None):
        self.position = np.array(position, dtype=float)
        self.fitness = fitness
        self.stagnation_count = 0
        self.dimension = len(position)

    def update_position(self, new_position, new_fitness):
        if new_fitness < self.fitness:
            self.position = new_position
            self.fitness = new_fitness
            self.stagnation_count = 0
            return True
        else:
            self.stagnation_count += 1
            return False

    def compute_qi(self, best_fitness, worst_fitness, epsilon=1e-10):
        if abs(worst_fitness - best_fitness) < epsilon:
            return 1.0
        qi = (worst_fitness - self.fitness) / (worst_fitness - best_fitness + epsilon)
        return np.clip(qi, 0.0, 1.0)

    def copy(self):
        new_agent = Agent(self.position.copy(), self.fitness)
        new_agent.stagnation_count = self.stagnation_count
        return new_agent
