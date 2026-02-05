## 2026-01-30 - [Vectorization of Grid Generation]
**Learning:** Python loops for grid generation (even small ones like 10x10) are significantly slower than numpy vectorization (~50% overhead for 100 points).
**Action:** Use `np.meshgrid` and vectorized operations for spatial data generation whenever possible.

## 2026-02-04 - [Vectorization of Heat Index Calculation]
**Learning:** Replacing `df.apply` with vectorized numpy operations for heat index calculation resulted in a ~6.7x speedup (15ms to 2ms).
**Action:** Always prefer vectorized operations over `df.apply` for mathematical computations on DataFrames.
