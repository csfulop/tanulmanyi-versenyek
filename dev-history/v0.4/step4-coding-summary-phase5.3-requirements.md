# Phase 5.3 Requirements: Performance Optimizations

## Context

Based on profiling baseline (see `!local-notes/profiling/01-baseline-summary.md`):
- Current execution time: ~9 minutes (539 seconds)
- Main bottleneck: School matching phase (96.7% of time)
- Root cause: `DataFrame.iterrows()` called 9.8 million times
- `normalize_city()` called 19.7 million times (redundant)

**Goal**: Reduce execution time from ~9 minutes to ~5-10 seconds (50-100x speedup)

---

## Requirements

### Requirement 1: Restructure KIR Database as City-Indexed Dictionary

**Current State**:
- `load_kir_database()` returns `pd.DataFrame` with all 13,637 schools
- Each `match_school()` call iterates through entire DataFrame using `iterrows()`
- City matching happens inside the loop

**New State**:
- `load_kir_database()` returns `Dict[str, pd.DataFrame]`
- Key: normalized city name (lowercase, no " kerület")
- Value: DataFrame containing only schools from that city (with required columns only)

**Data Processing Flow**:
```
1. Load Excel file
2. Validate required columns exist
3. Apply case normalization to school names
4. Keep only required columns
5. Group schools by normalized city
6. Create special "budapest" entry (see Req 4)
7. Return Dict[str, DataFrame]
```

**Benefits**:
- Pre-normalized cities (done once at load time)
- Pre-filtered by city (O(1) lookup instead of O(n) iteration)
- Reduced memory footprint (only required columns)

---

### Requirement 2: Move Required Columns to Module Level

**Current State**:
- `kir.required_columns` defined in `config.yaml`
- Conditional check for facility name column: `if 'A feladatellátási hely megnevezése' in kir_df.columns:`

**New State**:
- Remove `kir.required_columns` from `config.yaml` (breaking change)
- Add module-level constant in `school_matcher.py`:
  ```python
  REQUIRED_KIR_COLUMNS = [
      'Intézmény megnevezése',
      'A feladatellátási hely települése',
      'A feladatellátási hely vármegyéje',
      'A feladatellátási hely régiója',
      'A feladatellátási hely megnevezése'
  ]
  ```
- Remove conditional check (always expect facility name column)
- Update test fixtures to include facility name column

**Rationale**:
- Required columns are implementation detail, not configuration
- Simplifies code (no conditional logic)
- Makes expectations explicit

---

### Requirement 3: Keep Only Required Columns

**Current State**:
- KIR DataFrame contains all columns from Excel file (~50+ columns)
- Unused columns kept in memory

**New State**:
- After validation, drop all columns except `REQUIRED_KIR_COLUMNS`
- Reduces memory footprint
- Faster DataFrame operations

**Implementation**:
```python
kir_df = kir_df[REQUIRED_KIR_COLUMNS]
```

---

### Requirement 4: Filter KIR by Competition Cities

**Current State**:
- KIR contains schools from all Hungarian cities (~2,500+ cities)
- Competition data only has schools from ~260 cities
- We iterate through all KIR schools regardless

**New State**:
- In `match_all_schools()`: collect unique normalized cities from competition data
- Filter KIR dict to keep only cities present in competition data
- Log filtering statistics: "Filtered KIR to X cities (from Y total)"

**Special Case - Budapest Districts**:
- BEFORE filtering, create special "budapest" entry in KIR dict
- Merge all "budapest i.", "budapest ii.", ..., "budapest xxiii." DataFrames
- Concatenate into single DataFrame under "budapest" key
- Then apply filtering (so "budapest" entry might be dropped if not in competition data)

**Benefits**:
- Reduces search space from 13,637 schools to ~800 schools
- Eliminates special case handling in `cities_match()`
- Handles both "Budapest" (no district) and "Budapest III." (with district) in competition data

---

### Requirement 5: Simplify Candidate Lookup

**Current State**:
```python
# In match_school()
candidates = []
for _, candidate in kir_df.iterrows():  # 9.8M calls
    if cities_match(our_city, candidate['A feladatellátási hely települése']):
        candidates.append(candidate)
```

**New State**:
```python
# In match_school()
normalized_city = normalize_city(our_city)
candidates_df = kir_dict.get(normalized_city, pd.DataFrame())
# Iterate candidates_df (much smaller - only schools from that city)
```

**Changes**:
- Remove `cities_match()` function (no longer needed)
- Keep `normalize_city()` function (needed for dict lookup)
- Candidate collection becomes O(1) dict lookup
- Iteration only over schools from matching city (~50-100 schools instead of 13,637)

---

## Expected Performance Impact

### Before Optimization:
- Total time: 539 seconds (~9 minutes)
- School matching: 521 seconds (96.7%)
- `iterrows()` calls: 9.8 million
- `normalize_city()` calls: 19.7 million

### After Optimization:
- Expected total time: 5-10 seconds
- Expected speedup: 50-100x
- `iterrows()` calls: ~60,000 (779 schools × ~80 candidates avg)
- `normalize_city()` calls: ~1,600 (779 schools × 2 for lookup)

### Optimization Breakdown:
1. **Pre-normalized cities**: Eliminates 19.7M redundant normalizations
2. **City-indexed dict**: O(1) lookup instead of O(n) iteration
3. **Pre-filtered by competition cities**: Reduces search space by 95%
4. **Smaller DataFrames**: Only required columns, faster operations

---

## Breaking Changes

### Configuration File
- **Removed**: `kir.required_columns` section from `config.yaml`
- **Impact**: None (internal implementation detail)
- **Migration**: No action needed (config key was only used internally)

### Test Fixtures
- **Updated**: `tests/fixtures/kir_sample.xlsx` must include facility name column
- **Impact**: Tests will fail if fixture not updated
- **Migration**: Add 'A feladatellátási hely megnevezése' column to fixture

---

## Implementation Checklist

- [ ] Add `REQUIRED_KIR_COLUMNS` constant to `school_matcher.py`
- [ ] Remove `kir.required_columns` from `config.yaml`
- [ ] Update `load_kir_database()` to return `Dict[str, DataFrame]`
  - [ ] Validate required columns
  - [ ] Apply case normalization
  - [ ] Keep only required columns
  - [ ] Group by normalized city
  - [ ] Create special "budapest" entry
- [ ] Update `match_all_schools()` to filter KIR by competition cities
  - [ ] Collect unique normalized cities from competition data
  - [ ] Filter KIR dict
  - [ ] Log filtering statistics
- [ ] Update `match_school()` to use dict lookup
  - [ ] Replace `iterrows()` loop with dict lookup
  - [ ] Remove `cities_match()` calls
- [ ] Remove `cities_match()` function (no longer needed)
- [ ] Update test fixture `kir_sample.xlsx` to include facility name column
- [ ] Update tests to expect `Dict[str, DataFrame]` return type
- [ ] Run profiling again to measure improvement
- [ ] Update documentation

---

## Success Criteria

- [ ] All tests pass
- [ ] Execution time reduced from ~9 minutes to ~5-10 seconds
- [ ] Profiling shows `iterrows()` calls reduced by 99%
- [ ] Profiling shows `normalize_city()` calls reduced by 99%
- [ ] Audit file output unchanged (same matching results)
- [ ] Validation report unchanged (same statistics)
