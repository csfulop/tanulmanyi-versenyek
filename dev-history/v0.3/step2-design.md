# Detailed Design Document: Data Quality & Notebook Enhancements - v0.3.0

## 1. Introduction

### 1.1. Purpose

This document provides a detailed technical design for implementing the v0.3.0 release of the Hungarian Academic Competition Results Pipeline project. This release focuses on data quality improvements through city name cleaning and notebook usability enhancements.

### 1.2. Scope

This design covers:
- City validation module architecture and implementation
- City mapping CSV format and processing logic
- Integration with the merger phase (step 3)
- Standalone city checker execution
- Validation report updates
- Notebook enhancements (TOC, city filter, display settings)
- Documentation updates
- Testing strategy

### 1.3. Design Principles

Based on the requirements and project conventions:

1. **Human-in-the-Loop**: Automated detection, manual decision-making for data quality
2. **Separation of Concerns**: Validation logic isolated in dedicated module
3. **Optional Features**: System works without mapping file (graceful degradation)
4. **Transparency**: All mappings logged and auditable
5. **Backward Compatibility**: No breaking changes to existing functionality
6. **Clean Code**: Self-documenting code with minimal comments
7. **Idempotency**: Running multiple times produces same result

### 1.4. References

- **Requirements**: `dev-history/v0.3/step1-requirements.md`
- **v0.2 Design**: `dev-history/v0.2/step2-design.md`
- **v0.1 Design**: `dev-history/v0.1/step2-design.md`
- **City Issues Analysis**: `!local-notes/data-integrity-issue/city-issues-analysis.txt`
- **Master Dataset**: `data/kaggle/master_bolyai_anyanyelv.csv`

---

## 2. Architecture Overview

### 2.1. Component Structure

```
v0.3.0 Components:
├── src/tanulmanyi_versenyek/
│   └── validation/
│       ├── __init__.py                    # New module
│       └── city_checker.py                # City validation logic
├── config/
│   └── city_mapping.csv                   # Manual mapping file (optional)
├── config.yaml                            # Updated with validation section
├── 03_merger_and_excel.py                 # Updated to use city validation
├── notebooks/
│   └── competition_analysis.ipynb         # Enhanced with TOC, filters, display
├── templates/kaggle/
│   ├── README.hu.md                       # Updated with cleaning section
│   └── README.en.md                       # Updated with cleaning section
└── tests/
    └── test_city_checker.py               # New test file
```

### 2.2. Data Flow

```
Step 3 (Merger Phase):
    ↓
Load city_mapping.csv (optional)
    ↓
Merge all CSV files → master DataFrame
    ↓
Apply city mapping (corrections)
    ↓
Check for unmapped variations (warnings)
    ↓
Generate validation report (with city stats)
    ↓
Save master CSV + Excel reports
```

### 2.3. Module Dependencies

```
03_merger_and_excel.py
    ↓ imports
validation/city_checker.py
    ↓ uses
common/config.py
common/logger.py
pandas
```

---

## 3. City Validation Module Design

### 3.1. Module Structure

**File**: `src/tanulmanyi_versenyek/validation/city_checker.py`

**Public Functions:**
1. `load_city_mapping(config, log)` → dict
2. `apply_city_mapping(df, mapping, log)` → (DataFrame, int)
3. `check_city_variations(df, mapping, log)` → dict
4. `main()` → None (for standalone execution)

**Private Functions:**
5. `_parse_mapping_csv(filepath, log)` → dict
6. `_is_valid_entry(comment)` → bool
7. `_detect_variations(df)` → dict

### 3.2. Data Structures

**City Mapping Dictionary:**
```python
{
    ("School Name", "Original City"): {
        "corrected_city": "Corrected City" or "",
        "comment": "Human explanation",
        "is_valid": True/False
    }
}
```

**Variation Detection Result:**
```python
{
    "School Name": {
        "cities": ["City1", "City2", ...],
        "count": 2,
        "mapped": True/False,
        "valid": True/False
    }
}
```

### 3.3. Configuration Changes

**Add to `config.yaml`:**
```yaml
validation:
  city_mapping_file: "config/city_mapping.csv"
```

---

## 4. Detailed Function Specifications

### 4.1. load_city_mapping()

**Purpose**: Load and parse the city mapping CSV file.

**Signature**:
```python
def load_city_mapping(config: dict, log: logging.Logger) -> dict:
```

**Algorithm**:
1. Get mapping file path from config
2. Check if file exists
   - If not: log INFO "No city mapping file found", return empty dict
3. Try to read CSV with pandas (sep=';', encoding='utf-8')
   - On error: log ERROR with details, return empty dict
4. Validate columns: school_name, original_city, corrected_city, comment
   - If missing: log ERROR, return empty dict
5. Parse each row into dictionary structure
6. Log INFO: "Loaded N city mappings from {filepath}"
7. Return mapping dictionary

**Error Handling**:
- File not found: Continue without mapping (INFO log)
- Malformed CSV: Log error, continue without mapping
- Missing columns: Log error, continue without mapping

**Returns**: Dictionary keyed by (school_name, original_city)

---

### 4.2. apply_city_mapping()

**Purpose**: Apply city name corrections to DataFrame.

**Signature**:
```python
def apply_city_mapping(df: pd.DataFrame, mapping: dict, log: logging.Logger) -> tuple[pd.DataFrame, int]:
```

**Algorithm**:
1. If mapping is empty: return (df, 0)
2. Initialize correction counter = 0
3. Create a copy of DataFrame to avoid modifying original
4. For each row in DataFrame:
   - Get key = (row['iskola_nev'], row['varos'])
   - If key in mapping:
     - If is_valid: skip (keep original)
     - Else if corrected_city not empty:
       - Replace row['varos'] with corrected_city
       - Log DEBUG: "Applied mapping: school='{name}', '{orig}' → '{corrected}'"
       - Increment counter
5. Log INFO: "Applied {counter} city corrections"
6. Return (modified_df, counter)

**Returns**: Tuple of (corrected DataFrame, number of corrections applied)

---

### 4.3. check_city_variations()

**Purpose**: Detect and warn about unmapped city variations.

**Signature**:
```python
def check_city_variations(df: pd.DataFrame, mapping: dict, log: logging.Logger) -> dict:
```

**Algorithm**:
1. Call _detect_variations(df) to get all schools with multiple cities
2. Initialize counters: mapped=0, valid=0, unmapped=0
3. For each school with variations:
   - For each city of that school:
     - Check if (school, city) in mapping:
       - If yes and is_valid: increment valid counter
       - If yes and not is_valid: increment mapped counter (corrected_city should match current city)
       - If no: 
         - Log WARNING: "Unmapped combination: school='{name}', city='{city}'"
         - Increment unmapped counter
     - Log DEBUG: Details about each variation
4. Log INFO: Summary statistics (total variations, mapped, valid, unmapped)
5. Return statistics dict

**Returns**: Dictionary with statistics:
```python
{
    "total_schools_with_variations": int,
    "mapped_combinations": int,
    "valid_combinations": int,
    "unmapped_combinations": int
}
```

---

### 4.4. main() - Standalone Execution

**Purpose**: Allow standalone execution for analysis.

**Signature**:
```python
def main() -> None:
```

**Algorithm**:
1. Setup logging using project's logger module
2. Load config using project's config module
3. Get master CSV path from config
4. Load master CSV with pandas
5. Load city mapping
6. Call check_city_variations() - this will log all warnings
7. Exit

**Execution**:
```bash
python -m tanulmanyi_versenyek.validation.city_checker
```

---

## 5. Integration with Merger Script

### 5.1. Changes to 03_merger_and_excel.py

**Import Addition**:
```python
from tanulmanyi_versenyek.validation.city_checker import (
    load_city_mapping,
    apply_city_mapping,
    check_city_variations
)
```

**Integration Point** (in main() function):
```python
# After: master_df, duplicates_removed = merge_processed_data(cfg)
# Before: generate_validation_report(master_df, cfg, duplicates_removed)

# Load city mapping
city_mapping = load_city_mapping(cfg, logging.getLogger(__name__))

# Apply corrections
master_df, corrections_applied = apply_city_mapping(
    master_df, 
    city_mapping, 
    logging.getLogger(__name__)
)

# Check for unmapped variations
city_stats = check_city_variations(
    master_df, 
    city_mapping, 
    logging.getLogger(__name__)
)

# Pass city_stats to validation report generation
generate_validation_report(master_df, cfg, duplicates_removed, city_stats)
```

### 5.2. Changes to data_merger.py

**Update generate_validation_report() signature**:
```python
def generate_validation_report(
    df: pd.DataFrame, 
    config: dict, 
    duplicates_removed: int,
    city_stats: dict = None  # New parameter
) -> None:
```

**Add city_mapping section to report**:
```python
report = {
    "timestamp": datetime.now().isoformat(),
    "total_records": len(df),
    "unique_schools": df['iskola_nev'].nunique(),
    "unique_cities": df['varos'].nunique(),
    "years_covered": sorted(df['ev'].unique().tolist()),
    "duplicates_removed": duplicates_removed,
}

# Add city mapping stats if provided
if city_stats:
    report["city_mapping"] = {
        "corrections_applied": city_stats.get("corrections_applied", 0),
        "valid_variations": city_stats.get("valid_combinations", 0),
        "unmapped_variations": city_stats.get("unmapped_combinations", 0)
    }
```

---

## 6. City Mapping CSV Format

### 6.1. File Specification

**Location**: `config/city_mapping.csv`
**Encoding**: UTF-8
**Delimiter**: Semicolon (;)
**Header**: Required

**Columns**:
1. `school_name` (string, required): Exact school name from data
2. `original_city` (string, required): City name as it appears in source
3. `corrected_city` (string, optional): Corrected city name (empty for VALID)
4. `comment` (string, required): Human explanation

### 6.2. Example File

```csv
school_name;original_city;corrected_city;comment
Diósgyőri Szent Ferenc Római Katolikus Általános Iskola és Óvoda;MISKOLC;Miskolc;Normalize case to proper case
Debreceni Gönczy Pál Általános Iskola;Debrecen-Józsa;Debrecen;Map suburb to parent city
Baár-Madas Református Gimnázium és Általános Iskola;Budapest;Budapest II.;Add missing district based on school location
Gárdonyi Géza Általános Iskola;Budapest XIII.;;VALID - different schools with same name in different districts
Gárdonyi Géza Általános Iskola;Győr;;VALID - different schools with same name in different cities
```

### 6.3. Validation Rules

1. All columns must be present
2. school_name and original_city cannot be empty
3. If comment contains "VALID", corrected_city should be empty
4. If corrected_city is not empty, it will be applied
5. Duplicate (school_name, original_city) keys: last one wins (log warning)

---

## 7. Notebook Enhancements Design

### 7.1. Table of Contents

**Location**: After introduction, before imports

**Cell 1: Warning (Markdown)**
```markdown
⚠️ **Important / Fontos:**

Before jumping to any analysis section, you must first execute the following setup sections in order:
1. Imports & Configuration
2. Data Loading
3. Helper Functions Definition

Mielőtt bármelyik elemzési részhez ugranál, először sorrendben végre kell hajtanod az alábbi előkészítő részeket:
1. Importok és beállítások
2. Adatok betöltése
3. Segédfüggvények definiálása
```

**Cell 2: TOC (Markdown)**
```markdown
## Table of Contents / Tartalomjegyzék

### Setup / Előkészítés
- [Introduction](#Introduction) / [Bevezetés](#Bevezetés)
- [Imports & Configuration](#Imports-&-Configuration) / [Importok és beállítások](#Importok-és-beállítások)
- [Data Loading](#Data-Loading) / [Adatok betöltése](#Adatok-betöltése)
- [Dataset Overview](#Dataset-Overview) / [Adathalmaz áttekintése](#Adathalmaz-áttekintése)
- [Helper Functions](#Helper-Functions) / [Segédfüggvények](#Segédfüggvények)

### Analysis / Elemzések
- [School Rankings (Count-based)](#School-Rankings-(Count-based)) / [Iskolai rangsor (darabszám alapján)](#Iskolai-rangsor-(darabszám-alapján))
- [School Rankings (Weighted)](#School-Rankings-(Weighted)) / [Iskolai rangsor (súlyozott pontszám)](#Iskolai-rangsor-(súlyozott-pontszám))
- [City Rankings (Count-based)](#City-Rankings-(Count-based)) / [Városi rangsor (darabszám alapján)](#Városi-rangsor-(darabszám-alapján))
- [City Rankings (Weighted)](#City-Rankings-(Weighted)) / [Városi rangsor (súlyozott pontszám)](#Városi-rangsor-(súlyozott-pontszám))
- [School Search](#School-Search) / [Iskola keresése](#Iskola-keresése)
```

**Implementation Notes**:
- Manual markdown links (Kaggle-compatible)
- Links use header anchors (spaces become hyphens)
- Dual links per row for bilingual support

---

### 7.2. City Filter for School Rankings

**Affected Sections**:
- School Rankings (Count-based)
- School Rankings (Weighted)

**Parameter Addition** (in each section):
```python
# Filter by city/cities (optional)
# "all" = all cities (default)
# Single city: CITY_FILTER = "Budapest II."
# Multiple cities: CITY_FILTER = ["Budapest II.", "Budapest VII.", "Debrecen"]
CITY_FILTER = "all"
```

**Filter Logic** (before ranking calculation):
```python
# Apply city filter
if CITY_FILTER != "all":
    if isinstance(CITY_FILTER, str):
        filtered_df = filtered_df[filtered_df['varos'] == CITY_FILTER]
    elif isinstance(CITY_FILTER, list):
        filtered_df = filtered_df[filtered_df['varos'].isin(CITY_FILTER)]
    else:
        print("⚠️ Invalid CITY_FILTER format. Using all cities.")
```

**Documentation Updates**:
- Add Hungarian explanation of city filter
- Add English explanation of city filter
- Include examples in comments

---

### 7.3. Pandas Display Settings

**Affected Sections**:
- School Rankings (Count-based) - use DISPLAY_TOP_N
- School Rankings (Weighted) - use DISPLAY_TOP_N
- City Rankings (Count-based) - use DISPLAY_TOP_N
- City Rankings (Weighted) - use DISPLAY_TOP_N
- School Search - use None (unlimited)

**Implementation Pattern** (wrap each display):
```python
# Save original setting
original_max_rows = pd.options.display.max_rows

# Set to match DISPLAY_TOP_N (or None for School Search)
pd.options.display.max_rows = DISPLAY_TOP_N  # or None

# Display table
display(result_df)

# Restore original setting
pd.options.display.max_rows = original_max_rows
```

**Placement**: Immediately before and after each `display()` call

---

## 8. Documentation Updates

### 8.1. Kaggle Dataset README Updates

**Files to Update**:
- `templates/kaggle/README.hu.md`
- `templates/kaggle/README.en.md`

**New Section** (add before "Known Data Quality Limitations"):

**English Version**:
```markdown
## Data Cleaning Process

### City Name Normalization

The dataset includes manual city name cleaning to address variations in the source data:

- **Case normalization**: "MISKOLC" → "Miskolc"
- **Suburb mapping**: "Debrecen-Józsa" → "Debrecen"  
- **Budapest districts**: Missing districts added where identifiable (e.g., "Budapest" → "Budapest II." for specific schools)

The cleaning process uses a manually maintained mapping file that preserves data authenticity while improving consistency. Valid variations (e.g., schools with the same name in different cities) are documented but not modified.

For details on the cleaning methodology, see the project repository.
```

**Hungarian Version**:
```markdown
## Adatminőség-javítási folyamat

### Városnevek normalizálása

Az adathalmaz manuális városnév-tisztítást tartalmaz a forrásadatok eltéréseinek kezelésére:

- **Kis- és nagybetűk normalizálása**: "MISKOLC" → "Miskolc"
- **Külterületek leképezése**: "Debrecen-Józsa" → "Debrecen"
- **Budapesti kerületek**: Hiányzó kerületek hozzáadása, ahol azonosítható (pl. "Budapest" → "Budapest II." adott iskolák esetén)

A tisztítási folyamat egy manuálisan karbantartott leképezési fájlt használ, amely megőrzi az adatok hitelességét, miközben javítja a konzisztenciát. Az érvényes eltérések (pl. azonos nevű iskolák különböző városokban) dokumentálva vannak, de nem módosulnak.

A tisztítási módszertan részleteiért lásd a projekt repository-ját.
```

**Update "Known Data Quality Limitations" Section**:
- Note that city name variations have been partially addressed
- School name variations remain (planned for future release)
- Budapest district normalization is limited (requires school name cleaning)

### 8.2. Main README.md

**No changes required** - keep high-level only, as specified in requirements.

---

## 9. Testing Strategy

### 9.1. Unit Tests for City Checker

**File**: `tests/test_city_checker.py`

**Test Cases**:

1. **test_load_city_mapping_success**
   - Create valid CSV file
   - Verify correct parsing
   - Check dictionary structure

2. **test_load_city_mapping_missing_file**
   - No file exists
   - Should return empty dict
   - Should log INFO message

3. **test_load_city_mapping_malformed**
   - Invalid CSV format
   - Should return empty dict
   - Should log ERROR message

4. **test_apply_city_mapping_corrections**
   - DataFrame with cities needing correction
   - Verify corrections applied
   - Verify count returned

5. **test_apply_city_mapping_valid_entries**
   - DataFrame with VALID entries
   - Verify no changes made
   - Verify count is 0

6. **test_apply_city_mapping_composite_key**
   - Same school name, different cities
   - Different corrections for each
   - Verify correct mapping applied

7. **test_check_city_variations_all_mapped**
   - All variations in mapping
   - No warnings logged
   - Correct statistics returned

8. **test_check_city_variations_unmapped**
   - Some variations not in mapping
   - Warnings logged for unmapped
   - Correct statistics returned

9. **test_check_city_variations_all_valid**
   - All marked as VALID
   - No warnings logged
   - Correct statistics returned

10. **test_standalone_execution**
    - Mock config and data
    - Verify main() runs without errors
    - Verify logging output

### 9.2. Integration Tests

**Test Cases**:

1. **test_full_pipeline_with_mapping**
   - Run complete pipeline with mapping file
   - Verify corrections in master CSV
   - Verify corrections in Excel
   - Verify validation report statistics

2. **test_full_pipeline_without_mapping**
   - Run pipeline without mapping file
   - Should work as before
   - No errors about missing file

3. **test_notebook_with_cleaned_data**
   - Load notebook with cleaned data
   - Verify rankings reflect cleaned cities
   - Verify city filter works
   - No errors

### 9.3. Notebook Enhancement Tests

**Manual Testing Checklist**:

1. **Table of Contents**
   - [ ] All links work (jump to sections)
   - [ ] Warning is visible
   - [ ] Structure matches notebook

2. **City Filter**
   - [ ] "all" shows all cities
   - [ ] Single city string filters correctly
   - [ ] Multiple cities list filters correctly
   - [ ] Invalid format shows warning
   - [ ] Works with other filters

3. **Pandas Display**
   - [ ] DISPLAY_TOP_N=20 shows 20 rows (not 10)
   - [ ] School Search shows all results
   - [ ] No side effects on other cells
   - [ ] Original setting restored

---

## 10. Implementation Phases

### Phase 1: City Validation Module (Core)

**Steps**:
1. Create `src/tanulmanyi_versenyek/validation/` directory
2. Create `__init__.py`
3. Implement `city_checker.py`:
   - `_parse_mapping_csv()`
   - `_is_valid_entry()`
   - `load_city_mapping()`
4. Write unit tests for Phase 1 functions
5. Run tests, ensure all pass

**Deliverable**: Working city mapping loader with tests

---

### Phase 2: City Mapping Application

**Steps**:
1. Implement `apply_city_mapping()` in `city_checker.py`
2. Write unit tests for mapping application
3. Test with sample data
4. Run tests, ensure all pass

**Deliverable**: Working city correction logic with tests

---

### Phase 3: Variation Detection

**Steps**:
1. Implement `_detect_variations()` in `city_checker.py`
2. Implement `check_city_variations()` in `city_checker.py`
3. Write unit tests for variation detection
4. Run tests, ensure all pass

**Deliverable**: Working variation checker with tests

---

### Phase 4: Standalone Execution

**Steps**:
1. Implement `main()` in `city_checker.py`
2. Test standalone execution manually
3. Verify logging output

**Deliverable**: Standalone city checker script

---

### Phase 5: Integration with Merger

**Steps**:
1. Update `config.yaml` with validation section
2. Update `03_merger_and_excel.py` to import and call city checker
3. Update `data_merger.py` to accept and use city_stats
4. Create example `config/city_mapping.csv`
5. Run full pipeline with mapping
6. Verify corrections in output files
7. Verify validation report

**Deliverable**: Integrated city cleaning in pipeline

---

### Phase 6: Notebook Enhancements

**Steps**:
1. Add Table of Contents cells (warning + TOC)
2. Add city filter to School Rankings (Count-based)
3. Add city filter to School Rankings (Weighted)
4. Add pandas display settings to all 5 sections
5. Test all enhancements locally
6. Test on Kaggle

**Deliverable**: Enhanced notebook

---

### Phase 7: Documentation

**Steps**:
1. Update `templates/kaggle/README.hu.md`
2. Update `templates/kaggle/README.en.md`
3. Review all changes
4. Generate final dataset files

**Deliverable**: Updated documentation

---

### Phase 8: Testing & Validation

**Steps**:
1. Run all unit tests
2. Run integration tests
3. Manual testing checklist
4. Cross-reference with requirements
5. Fix any issues found

**Deliverable**: Fully tested v0.3.0 release

---

## 11. Error Handling Strategy

### 11.1. City Mapping File Errors

**Scenario**: File not found
- **Action**: Log INFO, continue without mapping
- **User Impact**: None (optional feature)

**Scenario**: Malformed CSV
- **Action**: Log ERROR with details, continue without mapping
- **User Impact**: Warning in logs, no corrections applied

**Scenario**: Missing columns
- **Action**: Log ERROR, continue without mapping
- **User Impact**: Warning in logs, no corrections applied

### 11.2. Data Processing Errors

**Scenario**: Invalid city filter in notebook
- **Action**: Print warning, use "all" cities
- **User Impact**: Clear message, graceful fallback

**Scenario**: Empty DataFrame after filtering
- **Action**: Display empty result with message
- **User Impact**: Clear feedback

### 11.3. Logging Levels

- **DEBUG**: Individual mapping applications, detailed variation info
- **INFO**: Summary statistics, file loading, correction counts
- **WARNING**: Unmapped variations (actionable items)
- **ERROR**: File parsing errors, configuration issues

---

## 12. Acceptance Criteria Checklist

### 12.1. City Name Cleaning

- [ ] City mapping CSV format implemented and documented
- [ ] Validation module created in `src/tanulmanyi_versenyek/validation/`
- [ ] Module executable standalone: `python -m tanulmanyi_versenyek.validation.city_checker`
- [ ] Module importable and usable by merger script
- [ ] City corrections applied during merge phase
- [ ] Warnings logged for unmapped variations (WARNING level)
- [ ] Summary statistics logged (INFO level)
- [ ] Detailed info logged (DEBUG level)
- [ ] Validation report includes city mapping statistics
- [ ] Dataset READMEs updated with cleaning documentation
- [ ] All unit tests passing
- [ ] Integration tests passing

### 12.2. Notebook Enhancements

- [ ] Table of Contents added with warning cell
- [ ] All TOC links work correctly
- [ ] City filter added to School Rankings (Count-based)
- [ ] City filter added to School Rankings (Weighted)
- [ ] City filter supports "all", string, and list
- [ ] City filter works with existing filters
- [ ] Pandas display settings applied to 4 ranking sections
- [ ] Pandas display settings applied to School Search (unlimited)
- [ ] Settings properly saved and restored
- [ ] No side effects on other cells
- [ ] All enhancements work on Kaggle
- [ ] All enhancements work locally

### 12.3. Quality Assurance

- [ ] No breaking changes to existing functionality
- [ ] System works without mapping file
- [ ] Code follows project conventions (see README-ai-rules.md)
- [ ] All new code has appropriate logging
- [ ] Documentation is clear and complete
- [ ] Example mapping file created and documented

---

## 13. Risk Assessment

### 13.1. Technical Risks

**Risk**: Composite key (school_name, city) may not uniquely identify all cases
- **Mitigation**: Document limitations, plan school name normalization for v0.4
- **Impact**: Low - affects only edge cases

**Risk**: Manual TOC maintenance may become outdated
- **Mitigation**: Include TOC verification in testing checklist
- **Impact**: Low - easy to fix

**Risk**: Pandas display settings may conflict with user preferences
- **Mitigation**: Save and restore original settings
- **Impact**: Very Low - proper cleanup implemented

### 13.2. Data Quality Risks

**Risk**: Incorrect mappings in CSV file
- **Mitigation**: Human review required, comment field for documentation
- **Impact**: Medium - affects data accuracy

**Risk**: New variations appear in future data
- **Mitigation**: Warnings logged, easy to add to mapping file
- **Impact**: Low - system handles gracefully

### 13.3. Usability Risks

**Risk**: Users may not understand mapping file format
- **Mitigation**: Clear documentation, example file provided
- **Impact**: Low - format is simple CSV

---

## 14. Future Enhancements (Out of Scope)

### 14.1. School Name Normalization (v0.4+)

**Approach**: Similar to city mapping
- CSV-based manual mapping
- Composite key: (school_name, city) → normalized_school_name
- More complex due to 70+ variations

**Dependencies**: City cleaning must be stable first

### 14.2. Budapest District Normalization

**Challenge**: Requires knowing which school is which
**Approach**: 
1. Complete school name normalization
2. Use official school database
3. Always include district for Budapest

**Impact**: Budapest becomes statistical outlier (many schools)

### 14.3. County Data Enrichment

**Approach**: Integrate official Hungarian city/county database
**Benefits**: Geographical analysis, regional comparisons
**Challenge**: External database integration

### 14.4. Official School Database Integration

**Source**: KIR (Köznevelési Információs Rendszer)
**Uses**: Validate names, add districts, enrich metadata
**Challenge**: Database access, licensing, matching logic

---

**Document Version:** 1.0  
**Date:** 2025-12-23  
**Status:** Final  
**Next Steps:** Create step-by-step breakdown plan (step3-breakdown-plan.md)
