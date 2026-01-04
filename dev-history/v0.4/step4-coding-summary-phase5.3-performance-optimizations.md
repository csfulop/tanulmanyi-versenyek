# Step 4 Coding Summary: Phase 5.3 - Performance Optimizations

## 1. Completed Tasks and Key Implementation Details

### Task 1: Profiling Baseline Establishment

**Purpose**: Establish performance baseline before optimization

**Implementation**:
- Created `profile_04_script.py` to profile the entire 04_merger_and_excel.py execution
- Generated two baseline reports:
  - `01-baseline-by-time.txt` - Sorted by cumulative time
  - `01-baseline-by-calls.txt` - Sorted by call count
  - `01-baseline-summary.md` - Human-readable analysis

**Baseline Results**:
- Total execution time: 539 seconds (~9 minutes)
- School matching: 521 seconds (96.7% of total)
- `iterrows()` calls: 9.8 million
- `normalize_city()` calls: 19.7 million

**Key Bottleneck Identified**: `DataFrame.iterrows()` called 9.8M times during school matching

---

### Task 2: KIR Database Restructuring

**Purpose**: Replace DataFrame with city-indexed dictionary for O(1) lookups

**Implementation**:

1. **Added module-level constant**:
```python
REQUIRED_KIR_COLUMNS = [
    'Intézmény megnevezése',
    'A feladatellátási hely települése',
    'A feladatellátási hely vármegyéje',
    'A feladatellátási hely régiója',
    'A feladatellátási hely megnevezése'
]
```

2. **Restructured `load_kir_database()` to return `Dict[str, DataFrame]`**:
```python
def load_kir_database(config) -> Dict[str, pd.DataFrame]:
    # Load Excel
    # Validate required columns (using module constant)
    # Apply case normalization
    # Keep only required columns
    # Group by normalized city
    # Create special "budapest" entry (merge all districts)
    # Return dict: {normalized_city: DataFrame}
```

3. **Removed `kir.required_columns` from config.yaml** (breaking change)

**Benefits**:
- O(1) city lookup instead of O(n) iteration
- Pre-normalized cities (done once at load)
- Reduced memory (only required columns)

---

### Task 3: City Filtering Optimization

**Purpose**: Filter KIR data to only cities present in competition data

**Implementation**:

Updated `match_all_schools()`:
```python
def match_all_schools(our_df, kir_dict, manual_mapping, config):
    # Collect unique normalized cities from competition data
    unique_cities = set(our_df['varos'].apply(normalize_city).unique())
    
    # Filter KIR dict to only cities in competition data
    filtered_kir_dict = {city: df for city, df in kir_dict.items() if city in unique_cities}
    
    # Log filtering statistics
    log.info(f"Filtered KIR to {len(filtered_kir_dict)} cities (from {len(kir_dict)} total)")
    
    # Continue with matching using filtered dict
```

**Benefits**:
- Reduces search space from 13,637 schools to ~800 schools
- 95% reduction in candidate pool
- Logged for transparency: "Filtered KIR to 260 cities (from 2230 total)"

---

### Task 4: Budapest Special Case Handling

**Purpose**: Eliminate special case logic by pre-merging Budapest districts

**Implementation**:

In `load_kir_database()`:
```python
# Create special "budapest" entry by merging all Budapest districts
budapest_dfs = []
for city_key in list(kir_dict.keys()):
    if city_key.startswith('budapest'):
        budapest_dfs.append(kir_dict[city_key])

if budapest_dfs:
    kir_dict['budapest'] = pd.concat(budapest_dfs, ignore_index=True)
```

**Benefits**:
- Handles both "Budapest" (no district) and "Budapest III." (with district) automatically
- Eliminated `cities_match()` function (no longer needed)
- Simplified matching logic

---

### Task 5: Simplified Candidate Lookup

**Purpose**: Replace iterrows() loop with direct dict lookup

**Implementation**:

Updated `match_school()`:
```python
def match_school(our_name, our_city, kir_dict, manual_mapping, config):
    # Check manual mapping first
    if key in manual_mapping:
        # ... handle manual match
    
    # Direct dict lookup by normalized city
    normalized_city = normalize_city(our_city)
    candidates_df = kir_dict.get(normalized_city, pd.DataFrame())
    
    if candidates_df.empty:
        return NO_MATCH
    
    # Iterate only candidates from matching city (small DataFrame)
    for _, candidate in candidates_df.iterrows():
        score = _calculate_best_match_score(our_name, candidate)
        # ... find best match
```

**Benefits**:
- No more iterating through entire KIR database
- Only iterate schools from matching city (~50-100 schools)
- 99.3% reduction in iterrows() calls (9.88M → 65K)

---

### Task 6: Removed Obsolete Function

**Removed**: `cities_match()` function

**Rationale**: No longer needed with dict-based lookup. City matching is now implicit in the dict key lookup.

---

### Task 7: Test Updates

**Updated**:
- Test fixture `kir_sample.xlsx` - Added facility name column
- All tests updated to expect `Dict[str, DataFrame]` instead of `DataFrame`
- Removed `cities_match` import and tests
- Updated integration test to remove manual filtering

**Results**: All 100 tests pass

---

### Task 8: Excel Template Simplification

**Purpose**: Remove manual ranking sheet generation (pivot tables now work)

**Background**:
- Excel template recreated with Microsoft Office (was LibreOffice)
- Pivot tables now work correctly after data population
- Column names updated in template (vármegye, régió added)

**Implementation**:

Simplified `generate_excel_report()`:
```python
def generate_excel_report(df, cfg):
    # Copy template
    # Load workbook
    # Clear existing data rows
    # Populate Data sheet
    # Save workbook
    # (No longer creates Ranking_by_School and Ranking_by_City sheets)
```

**Removed**:
- Manual `Ranking_by_School` sheet creation
- Manual `Ranking_by_City` sheet creation
- openpyxl Font and styling imports

**Benefits**:
- Simpler code
- Faster execution
- Relies on template's pivot tables for analysis

---

### Task 9: Performance Measurement

**Created optimized profiling reports**:
- `02-optimized-by-time.txt`
- `02-optimized-by-calls.txt`
- `02-optimized-summary.md`

**Results**:
- Total execution time: 23 seconds (was 539s)
- School matching: 4.5 seconds (was 522s)
- `iterrows()` calls: 65K (was 9.88M)
- `normalize_city()` calls: 27K (was 19.7M)

---

## 2. Issues Encountered and Solutions Applied

### Issue 1: Test Fixture Missing Facility Name Column

**Problem**: Test fixture `kir_sample.xlsx` only had 4 columns, missing the facility name column that is now required.

**Root Cause**: Fixture was created before facility name column was added to requirements.

**Solution**: Added facility name column to fixture with same values as institution name:
```python
df['A feladatellátási hely megnevezése'] = df['Intézmény megnevezése']
df.to_excel('tests/fixtures/kir_sample.xlsx', index=False)
```

---

### Issue 2: Integration Test Manual Filtering

**Problem**: Integration test had manual city filtering logic that used the removed `cities_match()` function.

**Root Cause**: Test was written before optimization, manually filtered KIR data for performance.

**Solution**: Removed manual filtering since `match_all_schools()` now handles filtering internally:
```python
# Before: Manual filtering with cities_match()
# After: Just load kir_dict and pass to match_all_schools()
kir_dict = load_kir_database(temp_config)
match_results = match_all_schools(test_df, kir_dict, school_mapping, temp_config)
```

---

### Issue 3: openpyxl Header/Footer Warning

**Problem**: Warning appears when loading KIR Excel file:
```
UserWarning: Cannot parse header or footer so it will be ignored
```

**Root Cause**: KIR Excel file (from government website) has header/footer formatting that openpyxl can't parse.

**Solution**: No action taken - this is harmless and informational. The warning doesn't affect functionality since we only read data, not headers/footers.

**Decision**: Leave warning as-is rather than suppress it, as it confirms file is being read and doesn't hide potential real issues.

---

## 3. Key Learnings and Takeaways

### Insight 1: Profiling Before Optimization is Essential

Profiling revealed that 96.7% of time was spent in school matching, with `iterrows()` being the main culprit. Without profiling, we might have optimized the wrong parts.

**Application**: Always profile before optimizing. Measure, don't guess.

---

### Insight 2: Data Structure Choice Matters More Than Algorithm

Switching from DataFrame to Dict provided 100x+ speedup in matching, while the fuzzy matching algorithm remained unchanged. The data structure (O(1) dict lookup vs O(n) iteration) was the key.

**Application**: Consider data structure optimization before algorithm optimization.

---

### Insight 3: Pre-Processing Eliminates Redundant Work

Pre-normalizing cities once at load time eliminated 19.7M redundant normalization calls. Pre-filtering by city eliminated 95% of candidate searches.

**Application**: Do expensive operations once upfront, not repeatedly in loops.

---

### Insight 4: Special Cases Can Be Eliminated by Pre-Processing

The Budapest special case (matching "Budapest" to any district) was handled by pre-merging all districts into a single "budapest" key. This eliminated special case logic in the matching loop.

**Application**: Look for opportunities to handle special cases during data preparation rather than during processing.

---

### Insight 5: Simplification Often Follows Optimization

After optimization, we could remove the `cities_match()` function entirely and simplify the Excel generation. Good optimization often leads to simpler code.

**Application**: Optimization can reveal opportunities for simplification.

---

## 4. Project Best Practices

### Working Practices

1. **Profiling-driven optimization**: Establish baseline, identify bottlenecks, optimize, measure improvement
2. **Module-level constants for internal details**: `REQUIRED_KIR_COLUMNS` is implementation detail, not configuration
3. **Pre-processing for performance**: Normalize once, filter early, structure data for fast access
4. **Logging for transparency**: Log filtering statistics so users understand what's happening
5. **Test-driven refactoring**: All 100 tests pass after major restructuring
6. **Breaking changes documented**: Removed config key documented in requirements

### Non-Working Practices

1. **Configuration for implementation details**: `kir.required_columns` was config but should have been code constant
2. **Manual sheet generation when pivot tables work**: Unnecessary code duplication
3. **Iterating entire dataset when subset needed**: Should filter first, then iterate

### Recommendations

1. **Profile before optimizing**: Use cProfile to identify real bottlenecks
2. **Choose right data structure**: Dict for O(1) lookup, DataFrame for analysis
3. **Pre-process expensive operations**: Normalize, filter, group upfront
4. **Eliminate special cases via pre-processing**: Handle edge cases during data preparation
5. **Keep implementation details in code**: Only put user-facing settings in config
6. **Simplify after optimization**: Look for code that can be removed after restructuring
7. **Document breaking changes**: Config changes should be noted for users
8. **Leave informational warnings**: Don't suppress warnings unless they're noise

---

## 5. Performance Impact Summary

### Before Optimization (Baseline)
- **Total time**: 539 seconds (~9 minutes)
- **School matching**: 521 seconds (96.7%)
- **Function calls**: 1.48 billion
- **iterrows() calls**: 9.88 million
- **normalize_city() calls**: 19.7 million

### After Optimization
- **Total time**: 23 seconds
- **School matching**: 4.5 seconds (20.2%)
- **Function calls**: 79 million
- **iterrows() calls**: 65 thousand
- **normalize_city() calls**: 27 thousand

### Speedup Achieved
| Metric | Improvement |
|--------|-------------|
| **Total Time** | **23.4x faster** |
| **School Matching** | **115.8x faster** |
| **Function Calls** | **18.7x fewer** |
| **iterrows() Calls** | **151x fewer** |
| **normalize_city() Calls** | **730x fewer** |

### Current Bottleneck
KIR Excel file loading (15.6 seconds, 69% of total) is now the main bottleneck, but this is acceptable since:
- It's I/O bound (reading 6MB file)
- Only happens once per run
- Further optimization would require changing data source format

---

## 6. Files Modified

### Core Implementation
- `src/tanulmanyi_versenyek/validation/school_matcher.py`
  - Added `REQUIRED_KIR_COLUMNS` constant
  - Changed `load_kir_database()` return type to `Dict[str, DataFrame]`
  - Updated `match_school()` to use dict lookup
  - Updated `match_all_schools()` to filter by competition cities
  - Removed `cities_match()` function
- `src/tanulmanyi_versenyek/merger/data_merger.py`
  - Simplified `generate_excel_report()` (removed manual sheet generation)

### Configuration
- `config.yaml`
  - Removed `kir.required_columns` section

### Tests
- `tests/fixtures/kir_sample.xlsx`
  - Added facility name column
- `tests/test_school_matcher.py`
  - Updated all tests to use `kir_dict` instead of `kir_df`
  - Removed `cities_match` tests
  - Updated fixture to return dict
- `tests/test_integration.py`
  - Removed manual city filtering logic

### Profiling
- `profile_04_script.py` (new)
- `!local-notes/profiling/01-baseline-by-time.txt`
- `!local-notes/profiling/01-baseline-by-calls.txt`
- `!local-notes/profiling/01-baseline-summary.md`
- `!local-notes/profiling/02-optimized-by-time.txt`
- `!local-notes/profiling/02-optimized-by-calls.txt`
- `!local-notes/profiling/02-optimized-summary.md`

---

## 7. Breaking Changes

### Configuration File
**Removed**: `kir.required_columns` from `config.yaml`

**Impact**: None for end users (was internal implementation detail)

**Migration**: No action needed - column list now hardcoded in `school_matcher.py`

### Excel Template
**Updated**: Template recreated with Microsoft Office (was LibreOffice)

**Changes**:
- Pivot tables now work correctly
- Column names updated (vármegye, régió added)
- Manual ranking sheets removed from code generation

**Impact**: Users must use updated template

---

## 8. Test Results

**Total tests**: 100 (all passing ✅)

**Test execution time**: ~17 seconds (was ~17 seconds before, no regression)

**Coverage**:
- Unit tests: School matcher, city checker, merger
- Integration tests: Full pipeline with real KIR data
- All tests updated for new Dict structure
- No test failures or regressions

---

## 9. Suggestion for Commit Message

```
perf(matching): optimize school matching with city-indexed dictionary

Restructured KIR database loading and school matching for massive performance improvement.

Performance Impact:
- Total execution time: 539s → 23s (23.4x faster)
- School matching: 522s → 4.5s (115.8x faster)
- iterrows() calls: 9.88M → 65K (99.3% reduction)
- normalize_city() calls: 19.7M → 27K (99.9% reduction)

Key Changes:
- load_kir_database() now returns Dict[str, DataFrame] indexed by normalized city
- Pre-filter KIR data to only cities in competition data (95% reduction)
- Pre-merge all Budapest districts into single "budapest" entry
- Remove cities_match() function (no longer needed)
- Move REQUIRED_KIR_COLUMNS to module constant (was in config)

Excel Template:
- Simplified generate_excel_report() to only populate Data sheet
- Removed manual Ranking_by_School and Ranking_by_City generation
- Template now uses working pivot tables (recreated with MS Office)
- Template updated with new column names (vármegye, régió)

Breaking Changes:
- Removed kir.required_columns from config.yaml (now hardcoded)
- Test fixture updated to include facility name column

All 100 tests pass. Profiling reports included in !local-notes/profiling/.
```
