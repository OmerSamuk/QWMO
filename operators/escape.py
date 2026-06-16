import numpy as np


def adaptive_quantum_escape(agent, best_position, t, T_max,
                             kappa_0, k_s, eta_r,
                             lower_bound, upper_bound, dimension, rng):
    if agent.stagnation_count <= k_s:
        return None

    kappa_t = kappa_0 * (t / T_max)

    search_range = upper_bound - lower_bound
    L_max = np.sqrt(dimension) * search_range
    L_norm = np.linalg.norm(agent.position - best_position) / (L_max + 1e-10)

    P_esc = np.exp(-2 * kappa_t * L_norm)

    if rng.random() < P_esc:
        beta = rng.uniform(0, 1)

        sigma_noise = eta_r * search_range
        eta = rng.normal(0, sigma_noise, dimension)

        x_r = rng.uniform(lower_bound, upper_bound, dimension)

        new_position = beta * (best_position + eta) + (1 - beta) * x_r
        new_position = np.clip(new_position, lower_bound, upper_bound)

        return new_position

    return None
