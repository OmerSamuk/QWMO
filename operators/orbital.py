import numpy as np


def adaptive_orbital_sampling(agent, best_fitness, worst_fitness, t, T_max,
                               gamma, c_base, lower_bound, upper_bound,
                               sigma_floor=1e-8, epsilon=1e-10):
    qi = agent.compute_qi(best_fitness, worst_fitness, epsilon)
    
    search_range = upper_bound - lower_bound
    sigma_max = gamma * search_range * (2 - qi)
    c_i = c_base * qi
    
    sigma_t = max(sigma_max * np.exp(-c_i * t / T_max), sigma_floor)
    
    new_position = np.random.normal(agent.position, sigma_t)
    new_position = np.clip(new_position, lower_bound, upper_bound)
    
    return new_position
