import numpy as np
from core.kdtree_util import build_kdtree, query_pairs


def compute_dynamic_epsilon(t, T_max, lower_bound, upper_bound,
                            epsilon_max_ratio=0.1, epsilon_min_ratio=0.01):
    search_range = upper_bound - lower_bound
    epsilon_max = epsilon_max_ratio * search_range
    epsilon_min = epsilon_min_ratio * search_range
    epsilon_t = epsilon_max * (1 - t / T_max) + epsilon_min
    return epsilon_t


def pauli_exclusion(agents, t, T_max, lower_bound, upper_bound,
                    epsilon_max_ratio=0.1, epsilon_min_ratio=0.01):
    epsilon_t = compute_dynamic_epsilon(t, T_max, lower_bound, upper_bound,
                                        epsilon_max_ratio, epsilon_min_ratio)
    
    positions = np.array([agent.position for agent in agents])
    kdtree = build_kdtree(positions)
    
    pairs = query_pairs(kdtree, epsilon_t)
    
    collision_count = 0
    for i, j in pairs:
        if agents[i].fitness > agents[j].fitness:
            weaker_idx, stronger_idx = i, j
        else:
            weaker_idx, stronger_idx = j, i
        
        v = agents[weaker_idx].position - agents[stronger_idx].position
        v_norm_sq = np.dot(v, v)
        
        if v_norm_sq < 1e-10:
            continue
        
        r = np.random.normal(0, 1, len(agents[weaker_idx].position))
        p = r - (np.dot(r, v) / (v_norm_sq + 1e-10)) * v
        p_norm = np.linalg.norm(p)
        
        if p_norm < 1e-10:
            continue
        
        alpha = np.random.uniform(0.5 * epsilon_t, 1.5 * epsilon_t)
        displacement = alpha * p / (p_norm + 1e-10)
        
        new_position = agents[weaker_idx].position + displacement
        new_position = np.clip(new_position, lower_bound, upper_bound)
        agents[weaker_idx].position = new_position
        
        collision_count += 1
    
    return collision_count
