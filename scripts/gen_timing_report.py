import pandas as pd
import numpy as np

df = pd.read_csv('results/phase2/phase2_presmoke_results_raw.csv')

timing_rows = []
for (p, ss, m), sub in df.groupby(['p_level', 'subspace', 'method']):
    timing_rows.append({
        'p_level': p,
        'subspace': ss,
        'method': m,
        'n_runs': len(sub),
        'mean_time': round(sub['elapsed'].mean(), 2),
        'std_time': round(sub['elapsed'].std(), 2),
        'min_time': round(sub['elapsed'].min(), 2),
        'max_time': round(sub['elapsed'].max(), 2),
        'total_time': round(sub['elapsed'].sum(), 2),
    })

timing_df = pd.DataFrame(timing_rows)
timing_df.to_csv('results/phase2/phase2_presmoke_timing.csv', index=False)
print('phase2_presmoke_timing.csv saved')
print(f'  {len(timing_df)} rows')

total_sec = df['elapsed'].sum()
total_min = total_sec / 60
avg_sec = df['elapsed'].mean()
print(f'Total: {total_sec:.0f}s ({total_min:.1f}m), avg={avg_sec:.2f}s/run')
print(f'Total runs: {len(df)}')
