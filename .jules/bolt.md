## 2026-01-30 - [Vectorization of Grid Generation]
**Learning:** Python loops for grid generation (even small ones like 10x10) are significantly slower than numpy vectorization (~50% overhead for 100 points).
**Action:** Use `np.meshgrid` and vectorized operations for spatial data generation whenever possible.

## 2026-05-23 - [Vectorized Interpolation Speedup]
**Learning:** Replacing nested loop IDW interpolation with `scipy.spatial.distance.cdist` and numpy vectorization reduced execution time from 0.22s to 0.03s (~6.7x speedup) for 10x10 grids.
**Action:** Always prefer `cdist` for distance matrices over manual loops. Ensure to restore exact values for sampled points when using global interpolation/smoothing to avoid regression in data accuracy.
