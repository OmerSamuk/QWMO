import numpy as np
import pandas as pd
from collections import deque


class Phase1Logger:
    def __init__(self, function_id, variant_id, run_id, seed,
                 window=5, improvement_threshold=1e-12,
                 lower_bound=-100, upper_bound=100, dimension=30):
        self.function_id = function_id
        self.variant_id = variant_id
        self.run_id = run_id
        self.seed = seed
        self.window = window
        self.improvement_threshold = improvement_threshold
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.dimension = dimension
        self.search_range = upper_bound - lower_bound

        self.iteration_metrics = []
        self.agent_fitness_history = {}
        self.pending_escapes = deque()
        self.pending_pauli = deque()
        self.event_logs = []

        self.current_t = 0

    def _ensure_agent_history(self, agent_idx):
        if agent_idx not in self.agent_fitness_history:
            self.agent_fitness_history[agent_idx] = deque(maxlen=self.window + 1)

    def update_agent_fitnesses(self, agents):
        for idx, agent in enumerate(agents):
            self._ensure_agent_history(idx)
            self.agent_fitness_history[idx].append(agent.fitness)

    def record_escape_events(self, events):
        for agent_idx, old_fitness in events:
            self.pending_escapes.append((self.current_t, agent_idx, old_fitness))

    def record_pauli_events(self, events):
        for event in events:
            if len(event) == 3:
                agent_idx, old_fitness, _new_fitness = event
            else:
                agent_idx, old_fitness = event
            self.pending_pauli.append((self.current_t, agent_idx, old_fitness))

    def _resolve_pending(self, pending_queue, event_type):
        success_count = 0
        failure_count = 0
        neutral_count = 0
        while pending_queue:
            trigger_t, agent_idx, old_fitness = pending_queue[0]
            if self.current_t - trigger_t < self.window:
                break
            pending_queue.popleft()
            if agent_idx in self.agent_fitness_history and len(self.agent_fitness_history[agent_idx]) > 0:
                current_fitness = self.agent_fitness_history[agent_idx][-1]
            else:
                current_fitness = old_fitness
            improvement = old_fitness - current_fitness
            if improvement > self.improvement_threshold:
                classification = 'success'
                success_count += 1
            elif improvement < -self.improvement_threshold:
                classification = 'failure'
                failure_count += 1
            else:
                classification = 'neutral'
                neutral_count += 1
            self.event_logs.append({
                'iteration': trigger_t,
                'function_id': self.function_id,
                'variant_id': self.variant_id,
                'run_id': self.run_id,
                'seed': self.seed,
                'event_type': event_type,
                'agent_idx': agent_idx,
                'old_fitness': old_fitness,
                'new_fitness': current_fitness,
                'classification': classification,
                'resolved_at': self.current_t,
            })
        return success_count, failure_count, neutral_count

    def _compute_diversity_center(self, positions):
        center = np.mean(positions, axis=0)
        distances = np.linalg.norm(positions - center, axis=1)
        return float(np.mean(distances))

    def _compute_diversity_pairwise(self, positions):
        from scipy.spatial.distance import pdist
        if len(positions) > 1:
            distances = pdist(positions, 'euclidean')
            return float(np.mean(distances))
        return 0.0

    def _compute_mean_knn(self, positions, k=3):
        n = len(positions)
        if n <= k:
            return float(np.linalg.norm(self.upper_bound - self.lower_bound) * np.sqrt(self.dimension) / 2.0)
        from core.kdtree_util import build_kdtree
        tree = build_kdtree(positions)
        distances, _ = tree.query(positions, k=k + 1)
        distances = np.asarray(distances)
        if distances.ndim == 1:
            kth = distances
        else:
            kth = distances[:, k] if distances.shape[1] > k else distances[:, -1]
        return float(np.mean(kth))

    def _count_boundary_clipping(self, new_positions, old_positions):
        if new_positions is None or old_positions is None:
            return 0
        count = 0
        for new_p, old_p in zip(new_positions, old_positions):
            if np.any(new_p == self.lower_bound) or np.any(new_p == self.upper_bound):
                count += 1
        return count

    def record_iteration(self, t, agents, best_agent,
                          epsilon_value=None, collision_count=0, displacement_count=0,
                          escape_triggered_count=0,
                          pauli_events=None, escape_events=None,
                          new_positions=None, old_positions_for_clipping=None,
                          sigma_mean=None, sigma_median=None, sigma_min=None, sigma_max=None,
                          k_mean=None, k_stagnant_count=None, tau_value=None):
        self.current_t = t
        self.update_agent_fitnesses(agents)
        if pauli_events:
            self.record_pauli_events(pauli_events)
        if escape_events:
            self.record_escape_events(escape_events)
        escape_s, escape_f, escape_n = self._resolve_pending(self.pending_escapes, 'escape')
        pauli_s, pauli_f, pauli_n = self._resolve_pending(self.pending_pauli, 'pauli')

        positions = np.array([agent.position for agent in agents])
        fitnesses = np.array([agent.fitness for agent in agents])
        best_fitness = float(np.min(fitnesses))
        worst_fitness = float(np.max(fitnesses))
        mean_fitness = float(np.mean(fitnesses))
        diversity_center = self._compute_diversity_center(positions)
        diversity_pairwise = self._compute_diversity_pairwise(positions)
        mean_agent_distance = diversity_center
        mean_knn = self._compute_mean_knn(positions)

        epsilon_to_mean_knn_ratio = 0.0
        if epsilon_value is not None and mean_knn > 1e-12:
            epsilon_to_mean_knn_ratio = float(epsilon_value) / mean_knn

        clipping = self._count_boundary_clipping(new_positions, old_positions_for_clipping)

        row = {
            'iteration': t,
            'function_id': self.function_id,
            'variant_id': self.variant_id,
            'run_id': self.run_id,
            'seed': self.seed,
            'best_fitness': best_fitness,
            'mean_fitness': mean_fitness,
            'worst_fitness': worst_fitness,
            'population_diversity_center': diversity_center,
            'population_diversity_pairwise': diversity_pairwise,
            'mean_agent_distance': mean_agent_distance,
            'mean_knn_distance': mean_knn,
            'epsilon_value': epsilon_value if epsilon_value is not None else 0.0,
            'epsilon_to_mean_knn_ratio': epsilon_to_mean_knn_ratio,
            'collision_count': collision_count,
            'displacement_count': displacement_count,
            'escape_triggered_count': escape_triggered_count,
            'escape_success_count': escape_s,
            'escape_failure_count': escape_f,
            'escape_neutral_count': escape_n,
            'pauli_success_count': pauli_s,
            'pauli_failure_count': pauli_f,
            'pauli_neutral_count': pauli_n,
            'boundary_clipping_count': clipping,
        }

        if sigma_mean is not None:
            row['sigma_mean'] = sigma_mean
        if sigma_median is not None:
            row['sigma_median'] = sigma_median
        if sigma_min is not None:
            row['sigma_min'] = sigma_min
        if sigma_max is not None:
            row['sigma_max'] = sigma_max
        if k_mean is not None:
            row['k_mean'] = k_mean
        if k_stagnant_count is not None:
            row['k_stagnant_count'] = k_stagnant_count
        if tau_value is not None:
            row['tau_value'] = tau_value

        self.iteration_metrics.append(row)

    def get_iteration_metrics_df(self):
        return pd.DataFrame(self.iteration_metrics)

    def get_event_logs_df(self):
        return pd.DataFrame(self.event_logs)
