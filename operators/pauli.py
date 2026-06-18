import numpy as np
from core.kdtree_util import build_kdtree, query_pairs


def compute_adaptive_epsilon(
    positions,
    lower_bound,
    upper_bound,
    dimension,
    k=3,
    lambda0=0.75,
    epsilon_min_ratio=0.01,
    epsilon_max_ratio=0.15,
):
    """Geometry-Adaptive Pauli Radius (GAPR v2).

    Computes epsilon from the current population geometry using the mean
    k-nearest-neighbor distance normalized by the search-space diagonal
    Lmax = sqrt(D) * search_range, so epsilon reflects relative density.
    """
    positions = np.asarray(positions)
    n_agents = positions.shape[0]

    search_range = upper_bound - lower_bound
    l_max = np.sqrt(dimension) * search_range
    epsilon_min = epsilon_min_ratio * search_range
    epsilon_max = epsilon_max_ratio * search_range

    if n_agents <= 1:
        return float(epsilon_min)

    k_eff = min(k, n_agents - 1)

    tree = build_kdtree(positions)
    distances, _ = tree.query(positions, k=k_eff + 1)

    distances = np.asarray(distances)
    if distances.ndim == 1:
        kth_distances = distances
    else:
        kth_distances = distances[:, k_eff]

    mean_knn = float(np.mean(kth_distances))
    normalized_knn = mean_knn / (l_max + 1e-12)
    epsilon = lambda0 * normalized_knn * search_range

    return float(np.clip(epsilon, epsilon_min, epsilon_max))


def compute_dynamic_epsilon(t, T_max, lower_bound, upper_bound,
                            epsilon_max_ratio=0.1, epsilon_min_ratio=0.01):
    search_range = upper_bound - lower_bound
    epsilon_max = epsilon_max_ratio * search_range
    epsilon_min = epsilon_min_ratio * search_range
    epsilon_t = epsilon_max * (1 - t / T_max) + epsilon_min
    return epsilon_t


def compute_epsilon(
    positions,
    t,
    T_max,
    lower_bound,
    upper_bound,
    dimension,
    mode="dynamic",
    epsilon_max_ratio=0.1,
    epsilon_min_ratio=0.01,
    static_epsilon_ratio=0.05,
    adaptive_k=3,
    adaptive_lambda0=0.75,
    adaptive_epsilon_max_ratio=0.15,
):
    if mode == "static":
        return float(static_epsilon_ratio * (upper_bound - lower_bound))

    if mode == "dynamic":
        return compute_dynamic_epsilon(
            t=t,
            T_max=T_max,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            epsilon_max_ratio=epsilon_max_ratio,
            epsilon_min_ratio=epsilon_min_ratio,
        )

    if mode == "adaptive":
        return compute_adaptive_epsilon(
            positions=positions,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            dimension=dimension,
            k=adaptive_k,
            lambda0=adaptive_lambda0,
            epsilon_min_ratio=epsilon_min_ratio,
            epsilon_max_ratio=adaptive_epsilon_max_ratio,
        )

    raise ValueError(f"Unknown epsilon mode: {mode}")


def pauli_exclusion(agents, evaluate, rng,
                    t, T_max, lower_bound, upper_bound, dimension,
                    epsilon_mode='dynamic',
                    epsilon_max_ratio=0.1,
                    epsilon_min_ratio=0.01,
                    static_epsilon_ratio=0.05,
                    adaptive_k=3,
                    adaptive_lambda0=0.75,
                    adaptive_epsilon_max_ratio=0.15):
    positions = np.array([agent.position for agent in agents])

    epsilon_t = compute_epsilon(
        positions=positions,
        t=t,
        T_max=T_max,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        dimension=dimension,
        mode=epsilon_mode,
        epsilon_max_ratio=epsilon_max_ratio,
        epsilon_min_ratio=epsilon_min_ratio,
        static_epsilon_ratio=static_epsilon_ratio,
        adaptive_k=adaptive_k,
        adaptive_lambda0=adaptive_lambda0,
        adaptive_epsilon_max_ratio=adaptive_epsilon_max_ratio,
    )

    kdtree = build_kdtree(positions)
    pairs = query_pairs(kdtree, epsilon_t)

    collision_count = len(pairs)
    displacement_count = 0
    success_count = 0
    events = []

    for i, j in pairs:
        if agents[i].fitness > agents[j].fitness:
            weaker_idx, stronger_idx = i, j
        else:
            weaker_idx, stronger_idx = j, i

        v = agents[weaker_idx].position - agents[stronger_idx].position
        v_norm_sq = np.dot(v, v)

        if v_norm_sq < 1e-10:
            continue

        r = rng.normal(0, 1, len(agents[weaker_idx].position))
        p = r - (np.dot(r, v) / (v_norm_sq + 1e-10)) * v
        p_norm = np.linalg.norm(p)

        if p_norm < 1e-10:
            continue

        alpha = rng.uniform(0.5 * epsilon_t, 1.5 * epsilon_t)
        displacement = alpha * p / (p_norm + 1e-10)

        new_position = agents[weaker_idx].position + displacement
        new_position = np.clip(new_position, lower_bound, upper_bound)

        old_fitness = agents[weaker_idx].fitness
        new_fitness = evaluate(new_position)

        agents[weaker_idx].position = new_position
        agents[weaker_idx].fitness = new_fitness
        agents[weaker_idx].stagnation_count = 0

        displacement_count += 1
        events.append((weaker_idx, old_fitness, new_fitness))
        if new_fitness < old_fitness:
            success_count += 1

    return {
        "epsilon": epsilon_t,
        "collision_count": collision_count,
        "displacement_count": displacement_count,
        "success_count": success_count,
        "events": events,
    }
