# Step 4 Coding Summary: Phase 5.2 - On-the-Fly Improvements

## Requirements Overview

This phase addresses four data quality and matching improvements identified during audit file review:

1. **City-level DROP functionality**: Remove international/unwanted cities via mapping file
2. **School-level DROP functionality**: Remove closed/unwanted schools via mapping file
3. **Dual-column name matching**: Match against both institution and facility names
4. **UPPERCASE name normalization**: Fix all-caps entries in KIR database

---

## Requirement 1: DROP Functionality in City Mapping

### Problem Statement
Some competitions allow international participants (e.g., Hungarian minorities from neighboring countries like Transilvania). These schools should be excluded from statistics but currently require manual filtering.

### Requirements
- **Mapping file syntax**: If `corrected_city == "DROP"` in `config/city_mapping.csv`, remove all schools from that city
- **Implementation location**: `apply_city_mapping()` function
- **Immediate removal**: Drop rows during city mapping phase (before school matching)
- **Tracking**: Change `corrections_count` from integer to dict with keys:
  - `corrected`: Number of city name corrections applied
  - `dropped`: Number of schools dropped due to city DROP rules
- **Validation report**: Update to include both counts
- **Logging**: Update existing log message to include drop count:
  ```python
  log.info(f"Applied {corrections['corrected']} city corrections, dropped {corrections['dropped']} schools from excluded cities")
  ```

### Example Mapping Entry
```csv
original_city;corrected_city;comment
Kolozsvár;DROP;International participant - exclude from statistics
```

### Return Value Change
```python
# Before
def apply_city_mapping(df, mapping) -> pd.DataFrame

# After  
def apply_city_mapping(df, mapping) -> Tuple[pd.DataFrame, dict]
# Returns: (corrected_df, {'corrected': int, 'dropped': int})
```

---

## Requirement 2: DROP Functionality in School Mapping

### Problem Statement
Some schools appear in historical competition data but are now closed. Currently, attempting to map them to empty string causes NO_MATCH errors. Need explicit DROP mechanism.

### Requirements
- **Mapping file syntax**: If `corrected_school_name == "DROP"` in `config/school_mapping.csv`, mark school for removal
- **Implementation location**: `match_school()` function (when checking manual_mapping)
- **No KIR lookup**: Don't attempt to find "DROP" in KIR database
- **New match method**: `MANUAL_DROP`
- **Status**: `NOT_APPLIED` (like DROPPED and NO_MATCH)
- **Comment**: Use comment from mapping file (same as MANUAL matches)
- **Validation report**: Add `manual_drop` count under `school_matching` section

### Example Mapping Entry
```csv
school_name;city;corrected_school_name;comment
Closed School Name;Budapest;DROP;School closed in 2020
```

### Match Result Structure
```python
{
    'matched_school_name': None,
    'matched_city': None,
    'matched_county': None,
    'matched_region': None,
    'confidence_score': None,
    'match_method': 'MANUAL_DROP',
    'comment': manual_entry['comment']  # From mapping file
}
```

---

## Requirement 3: Dual-Column Name Matching

### Problem Statement
Competition results sometimes use facility names ("A feladatellátási hely megnevezése") instead of institution names ("Intézmény megnevezése"). Current matching only checks institution names, causing false negatives.

### Requirements
- **Match against both columns**:
  - "Intézmény megnevezése" (institution name) - current behavior
  - "A feladatellátási hely megnevezése" (facility name) - NEW
- **Best score wins**: Take highest fuzzy match score from either column
- **Always return institution data**: Final result uses "Intézmény megnevezése" regardless of which column matched
- **No audit tracking**: Don't store which column gave best match (internal detail)
- **Implementation**: Refactor matching loop for clarity

### Implementation Approach
```python
def _calculate_best_match_score(our_name: str, candidate: pd.Series) -> float:
    """Calculate best fuzzy match score across both name columns."""
    scores = []
    for column in ['Intézmény megnevezése', 'A feladatellátási hely megnevezése']:
        kir_name = candidate[column]
        if pd.notna(kir_name):
            score = fuzz.token_set_ratio(our_name, kir_name)
            scores.append(score)
    return max(scores) if scores else 0

# In match_school()
for candidate in candidates:
    score = _calculate_best_match_score(our_name, candidate)
    if score > best_score:
        best_score = score
        best_match = candidate
```

### Data Flow
```
Competition name: "Budakeszi Német Iskola"
  ↓
Check candidate:
  - Intézmény megnevezése: "Budakeszi Német Nemzetiségi Általános Iskola" → score: 85
  - A feladatellátási hely megnevezése: "Budakeszi Német Iskola" → score: 100
  ↓
Best score: 100 (from facility name)
  ↓
Return: "Budakeszi Német Nemzetiségi Általános Iskola" (institution name)
```

---

## Requirement 4: UPPERCASE Name Normalization

### Problem Statement
Some KIR database entries have FULL UPPERCASE names (e.g., "BUDAKESZI NÉMET NEMZETISÉGI ÁLTALÁNOS ISKOLA"). This:
- Breaks fuzzy matching (case-sensitive comparison)
- Looks unprofessional in output/statistics
- Only affects name columns; other data (city, county) is correct

### Requirements

#### Phase 4a: Analysis Script
**Purpose**: Identify lowercase words in normal-cased entries to build exception list

**Location**: `!local-notes/school-name-case-issue/analyze_lowercase_words.py`

**Logic**:
1. Load KIR database
2. Get unique values from both name columns:
   - "Intézmény megnevezése"
   - "A feladatellátási hely megnevezése"
3. Filter: Keep only entries that are NOT full uppercase
4. Split into words
5. Filter: Keep only words that start with lowercase letter
6. Display unique lowercase words (sorted, with counts)

**Output**: Print to console (no logging framework needed)

**Example output**:
```
Lowercase words found in KIR database:
  és: 1234 occurrences
  a: 567 occurrences
  az: 234 occurrences
  de: 45 occurrences
  ...
```

#### Phase 4b: Transformation Verification Script
**Purpose**: Preview what will be transformed before applying to production

**Location**: `!local-notes/school-name-case-issue/verify_case_transformation.py`

**Logic**:
1. Load KIR database
2. Extract both name columns into single DataFrame (stack them)
3. Apply proposed transformation (using lowercase words from Phase 4a)
4. Keep both original and transformed columns
5. Filter: Keep only rows where original ≠ transformed
6. Save to CSV file: `case_transformation_preview.csv`

**Output columns**:
- `original_name`: Original value from KIR
- `transformed_name`: After case normalization
- `source_column`: Which column it came from

**Purpose**: Manual review to ensure transformation is correct before production

#### Phase 4c: Production Implementation
**Location**: `load_kir_database()` in `school_matcher.py`

**Logic**:
```python
def _normalize_case_if_uppercase(text: str, lowercase_words: set) -> str:
    """Convert FULL UPPERCASE to normal case with exceptions."""
    if pd.isna(text):
        return text
    
    # Only transform if ENTIRE string is uppercase
    if text != text.upper():
        return text
    
    words = text.split()
    normalized = []
    for word in words:
        if word.lower() in lowercase_words:
            normalized.append(word.lower())
        else:
            normalized.append(word.title())
    
    return ' '.join(normalized)

# In load_kir_database()
lowercase_words = {'és', 'a', 'az', 'de', 'vagy', ...}  # From Phase 4a analysis

df['Intézmény megnevezése'] = df['Intézmény megnevezése'].apply(
    lambda x: _normalize_case_if_uppercase(x, lowercase_words)
)
df['A feladatellátási hely megnevezése'] = df['A feladatellátási hely megnevezése'].apply(
    lambda x: _normalize_case_if_uppercase(x, lowercase_words)
)
```

**Conditions for transformation**:
- Only if ENTIRE string is uppercase (not mixed case)
- Apply to both name columns
- Use lowercase word exceptions from analysis

---

## Implementation Order

1. **Req 1**: City DROP functionality (simplest, no dependencies)
2. **Req 2**: School DROP functionality (builds on Req 1 pattern)
3. **Req 4a**: Analysis script for lowercase words
4. **Req 4b**: Verification script for case transformation
5. **Req 4c**: Production case normalization (after manual review of 4b output)
6. **Req 3**: Dual-column matching (benefits from normalized names in Req 4)

---

## Testing Strategy

### Unit Tests
- `test_city_mapping_drop`: Verify DROP removes schools
- `test_city_mapping_drop_tracking`: Verify corrected/dropped counts
- `test_school_mapping_drop`: Verify MANUAL_DROP method
- `test_dual_column_matching`: Verify both columns checked
- `test_case_normalization`: Verify uppercase conversion

### Integration Tests
- `test_pipeline_with_city_drop`: End-to-end with city DROP
- `test_pipeline_with_school_drop`: End-to-end with school DROP
- `test_validation_report_counts`: Verify all new counts in report

### Manual Verification
- Review `case_transformation_preview.csv` before implementing Req 4c
- Check audit file after Req 3 to verify improved matching

---

## Validation Report Schema Changes

```json
{
  "city_corrections": {
    "corrected": 15,
    "dropped": 3
  },
  "school_matching": {
    "total_schools": 773,
    "manual_matches": 5,
    "manual_drop": 2,
    "auto_high_confidence": 650,
    "auto_medium_confidence": 100,
    "dropped_low_confidence": 15,
    "no_match": 3,
    "records_kept": 3150,
    "records_dropped": 85
  }
}
```

---

## Files to Create/Modify

### New Files
- `!local-notes/school-name-case-issue/analyze_lowercase_words.py`
- `!local-notes/school-name-case-issue/verify_case_transformation.py`

### Modified Files
- `src/tanulmanyi_versenyek/validation/city_checker.py`
  - `apply_city_mapping()`: Return tuple, handle DROP
- `src/tanulmanyi_versenyek/validation/school_matcher.py`
  - `match_school()`: Handle MANUAL_DROP
  - `_calculate_best_match_score()`: New helper function
  - `load_kir_database()`: Add case normalization
- `src/tanulmanyi_versenyek/merger/data_merger.py`
  - `generate_validation_report()`: Update schema
- `04_merger_and_excel.py`
  - Update to handle new return value from `apply_city_mapping()`
- `tests/test_city_checker.py`: Add DROP tests
- `tests/test_school_matcher.py`: Add MANUAL_DROP and dual-column tests
- `tests/test_integration.py`: Add integration tests

---

## Expected Outcomes

1. **Better data quality**: Remove unwanted international/closed schools systematically
2. **Improved matching**: Dual-column matching reduces false negatives
3. **Professional output**: No more UPPERCASE names in statistics
4. **Clear audit trail**: All DROP decisions visible in validation report
5. **Maintainable**: DROP rules in mapping files, not hardcoded

---

## Notes

- Req 4 requires manual review step (Phase 4b) before production deployment
- All DROP functionality is reversible (just edit mapping files)
- Case normalization is one-time fix at data load (doesn't modify KIR source)
- Dual-column matching is backward compatible (still works with single column)
