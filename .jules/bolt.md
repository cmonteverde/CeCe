## 2026-01-30 - [Vectorization of Grid Generation]
**Learning:** Python loops for grid generation (even small ones like 10x10) are significantly slower than numpy vectorization (~50% overhead for 100 points).
**Action:** Use `np.meshgrid` and vectorized operations for spatial data generation whenever possible.

## 2026-02-18 - [Vectorization of Spatial Interpolation]
**Learning:** Nested loops for Inverse Distance Weighting (IDW) interpolation are extremely slow (O(N*M)). Vectorizing with `scipy.spatial.distance.cdist` and numpy broadcasting reduced execution time from ~3.3s to ~0.005s for a 400-point grid.
**Action:** Always prefer `scipy.spatial.distance.cdist` over manual distance calculations in loops for spatial data processing.
