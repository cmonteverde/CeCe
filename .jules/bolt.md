## 2026-01-30 - [Vectorization of Grid Generation]
**Learning:** Python loops for grid generation (even small ones like 10x10) are significantly slower than numpy vectorization (~50% overhead for 100 points).
**Action:** Use `np.meshgrid` and vectorized operations for spatial data generation whenever possible.

## 2026-05-21 - [Meshgrid Indexing for Geospatial Data]
**Learning:** When replacing nested loops `for lat in lats: for lon in lons:` with `np.meshgrid`, use `indexing='ij'` to preserve the array shape `(len(lats), len(lons))` and iteration order. Default `xy` indexing transposes dimensions.
**Action:** Use `np.meshgrid(lats, lons, indexing='ij')` when vectorizing map grid generation.
