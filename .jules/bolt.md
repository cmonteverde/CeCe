## 2026-01-30 - [Vectorization of Grid Generation]
**Learning:** Python loops for grid generation (even small ones like 10x10) are significantly slower than numpy vectorization (~50% overhead for 100 points).
**Action:** Use `np.meshgrid` and vectorized operations for spatial data generation whenever possible.

## 2026-01-30 - [DataFrame Apply vs Vectorization]
**Learning:** `df.apply(..., axis=1)` for mathematical operations (like Heat Index) is extremely slow compared to numpy vectorization (~130x speedup). Even complex conditionals can be vectorized using `np.where`.
**Action:** Always prefer `np.where` and numpy array operations over `df.apply` for row-wise calculations.
