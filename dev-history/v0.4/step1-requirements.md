# Software Requirements Specification (SRS): School Name Normalization - v0.4.0

## 1. Introduction

### 1.1. Purpose

This document specifies the requirements for **version 0.4.0** of the Hungarian Academic Competition Results Pipeline project. This release focuses on **automated school name normalization** using the official Hungarian school database (KIR - Köznevelési Információs Rendszer).

### 1.2. Document Conventions

- **FR-XXX:** Denotes a specific Functional Requirement
- **NFR-XXX:** Denotes a specific Non-Functional Requirement
- **MVP:** Minimum Viable Product - keeping features simple and focused for initial release

### 1.3. Intended Audience

- **Lead Developer / Coding Agent:** Primary audience for implementation
- **Project Owner:** For validation of requirements
- **Data Analysts:** Users who will create and maintain mapping files

### 1.4. Product Scope

**In Scope for v0.4.0:**

**School Name Normalization:**
- Download official KIR database (feladatellátási helyek)
- Automated school name matching using fuzzy algorithms
- Manual override system via mapping file
- Audit trail generation
- Add vármegye (county) and régió (region) columns
- Simplified city mapping (preprocessing step)

**Notebook Enhancements:**
- County rankings (count + weighted)
- Region rankings (count + weighted)
- County and region filters for existing rankings

**Data Quality:**
- Remove schools that don't match official database
- Replace city names with official normalized versions
- Comprehensive audit file for transparency

**Out of Scope for v0.4.0:**

- Closed schools database (kir_megszűnt_intézmények) - will be naturally dropped
- School merger/successor tracking
- Historical name change tracking
- Additional competitions beyond Bolyai Anyanyelv
- Interactive matching UI

### 1.5. References

1. **v0.3.0 Documentation:** `dev-history/v0.3/` - Previous version (city name cleaning)
2. **School Name Analysis:** `!local-notes/school-name-cleaning/` - Matching algorithm analysis
3. **KIR Database:** https://kir.oktatas.hu/kirpub/index - Official Hungarian school database
4. **Dataset:** `data/kaggle/master_bolyai_anyanyelv.csv` - Current master dataset

---

## 2. Overall Description

### 2.1. Product Perspective

Version 0.4.0 builds on the existing data pipeline (v0.1), analysis notebook (v0.2), and city cleaning (v0.3) by integrating with the official Hungarian school database. This is a major quality improvement that:

- Validates all school names against official source
- Adds missing geographic data (county, region)
- Removes invalid/closed schools
- Provides full audit trail

### 2.2. Background: School Name Variations

Analysis of competition results revealed 22 variation groups affecting 47 school names (193 records, 6% of dataset).

**Common patterns:**
1. **AMI abbreviation:** "Alapfokú Művészeti Iskola" ↔ "AMI"
2. **Added/removed "és Óvoda":** School adds kindergarten over time
3. **Type changes:** "Szakközépiskola" → "Szakgimnázium"
4. **Branch/location additions:** "székhely", "Tagiskolája", "telephelye"
5. **Minor wording:** "Intézmény" ↔ "Iskola"

**Solution:** Match against official KIR database using fuzzy string matching.

### 2.3. KIR Database Overview

**Source:** https://kir.oktatas.hu/kirpub/index

**Files to use:**
- **feladatellátási helyek** (facility locations): 13,637 rows
  - Contains: Institution name, facility city, county, region
  - Updated daily by Hungarian government
  - Handles multi-location schools correctly

**Why facility locations file:**
- Includes specific location cities (handles schools with multiple buildings)
- Has all needed geographic data
- More granular than main institutions file

### 2.4. Design Philosophy

**For School Matching:**
- **Automated with oversight:** High-confidence matches auto-applied, low-confidence dropped
- **Manual override system:** Users can force specific matches via mapping file
- **Transparency:** Full audit trail of all decisions
- **City-aware:** Only match schools in same city (prevents false positives)

**For Data Quality:**
- **Official source of truth:** KIR database is authoritative
- **Remove invalid data:** Schools not in KIR are dropped (likely closed or data entry errors)
- **Normalize geography:** Use official city/county/region names

---

## 3. Functional Requirements

### 3.1. KIR Database Download (New Step 03)

#### FR-001: Download Helper Data Script

**Description:** Create new script `03_download_helper_data.py` to download KIR database files.

**Details:**
- **Location:** Project root (alongside 01, 02 scripts)
- **Execution:** Manual - user runs when they want fresh data
- **Behavior:** Always downloads fresh files, clears old ones

**Files to download:**
```
https://kir.oktatas.hu/download/kozerdeku/kir_mukodo_feladatellatasi_helyek_YYYY_MM_DD.xlsx
```

**Output location:**
- `data/helper_data/kir_feladatellatasi_helyek.xlsx`

**Configuration:**
```yaml
paths:
  helper_data_dir: "data/helper_data"
  kir_locations_file: "data/helper_data/kir_feladatellatasi_helyek.xlsx"

kir:
  # Note: Latest file URL must be obtained from https://kir.oktatas.hu/kirpub/index
  # The download link changes daily with the date in the filename
  index_url: "https://kir.oktatas.hu/kirpub/index"
  locations_filename_pattern: "kir_mukodo_feladatellatasi_helyek_{date}.xlsx"

matching:
  high_confidence_threshold: 90
  medium_confidence_threshold: 80
```

**Acceptance Criteria:**
- Script downloads latest KIR file from official website
- Clears `data/helper_data/` directory before download
- Saves file with consistent name (no date in filename)
- Logs download progress and file size
- Exits with error if download fails

---

#### FR-002: Script Renumbering

**Description:** Rename existing step 03 to step 04 to make room for new helper data download step.

**Changes:**
- Rename: `03_merger_and_excel.py` → `04_merger_and_excel.py`
- New: `03_download_helper_data.py`

**Acceptance Criteria:**
- Scripts numbered sequentially: 01, 02, 03, 04
- No breaking changes to module imports
- Documentation updated with new script names

---

#### FR-003: KIR File Validation

**Description:** Step 04 (merger) must validate KIR file exists before proceeding.

**Details:**
- Check if `data/helper_data/kir_feladatellatasi_helyek.xlsx` exists
- If missing: Log ERROR and exit with clear message
- Message: "KIR database file not found. Please run: poetry run python 03_download_helper_data.py"

**Acceptance Criteria:**
- Step 04 fails fast if KIR file missing
- Error message is clear and actionable
- No partial processing occurs

---

### 3.2. Simplified City Mapping (Preprocessing)

#### FR-004: Simplified City Mapping File

**Description:** Simplify existing city mapping to city-only format (no school+city composite keys).

**Details:**
- **Location:** `config/city_mapping.csv` (existing file, new format)
- **Format:** Three columns (semicolon-separated, UTF-8)
  ```csv
  original_city;corrected_city;comment
  MISKOLC;Miskolc;Normalize case
  Debrecen-Józsa;Debrecen;Map suburb to parent city
  ```

**Budapest special case:**
- Do NOT add district automatically (there are 20+ districts)
- Leave "Budapest" as-is in city mapping
- Handle in school matcher: if city is "Budapest" (no district), search all Budapest schools
- After match found, use the matched school's city (with correct district)

**Acceptance Criteria:**
- File is optional (system works without it)
- Simple city-to-city mapping (no school name column)
- Applied before school matching
- Logged INFO: "Applied N city corrections"
- Logged DEBUG: Each individual correction

---

#### FR-005: Simplified City Checker Module

**Description:** Simplify `city_checker.py` to only handle city mapping (remove variation detection).

**Details:**
- **Module:** `src/tanulmanyi_versenyek/validation/city_checker.py` (existing, simplified)
- **Functions to keep:**
  - `load_city_mapping(config)` - Load mapping file
  - `apply_city_mapping(df, mapping, log)` - Apply corrections
- **Functions to remove:**
  - `check_city_variations()` - No longer needed
  - `_detect_variations()` - No longer needed

**Acceptance Criteria:**
- Module loads and applies city mapping
- No variation detection logic
- Returns corrected DataFrame
- Logs number of corrections applied

---

### 3.3. School Name Matching System

#### FR-006: School Mapping Configuration File

**Description:** Create manual school mapping file for overrides and low-confidence cases.

**Details:**
- **Location:** `config/school_mapping.csv` (new file)
- **Path configuration:** Add to `config.yaml`
  ```yaml
  validation:
    city_mapping_file: "config/city_mapping.csv"
    school_mapping_file: "config/school_mapping.csv"
  ```
- **Format:** Four columns (semicolon-separated, UTF-8)
  ```csv
  school_name;city;corrected_school_name;comment
  Apáczai Csere János Gyakorló Általános Iskola;Nyíregyháza;Nyíregyházi Apáczai Csere János Általános Iskola és Alapfokú Művészeti Iskola;Manual override - low confidence
  ```

**Acceptance Criteria:**
- File is optional (system works without it)
- Composite key: (school_name, city)
- All entries must have corrected_school_name (no VALID flag)
- Comment field for human notes

---

#### FR-007: School Matcher Module

**Description:** Create school matching module in validation package.

**Details:**
- **Module location:** `src/tanulmanyi_versenyek/validation/school_matcher.py` (new)
- **Dependencies:** rapidfuzz library (add to pyproject.toml)

**Core Functions:**

1. **`load_school_mapping(config, log)`**
   - Load manual mapping file
   - Return dict keyed by (school_name, city)
   - Log: "Loaded N manual school mappings"

2. **`load_kir_database(config, log)`**
   - Load KIR feladatellátási helyek Excel file
   - Extract relevant columns:
     - School name: "Intézmény megnevezése"
     - City: "A feladatellátási hely települése"
     - County: "A feladatellátási hely vármegyéje"
     - Region: "A feladatellátási hely régiója"
   - Return DataFrame
   - Log: "Loaded N schools from KIR database"

3. **`normalize_city(city)`**
   - Strip whitespace, lowercase
   - Remove " kerület" and " ker." suffixes
   - Handle NaN values
   - Return normalized string

4. **`cities_match(our_city, kir_city)`**
   - Normalize both cities
   - Exact match after normalization
   - Special case: "budapest" matches any "budapest X."
   - Return boolean

5. **`match_school(our_name, our_city, kir_df, manual_mapping, config, log)`**
   - Check manual mapping first (if exists, return immediately)
   - Filter KIR candidates by city (using cities_match)
   - Calculate token_set_ratio for each candidate
   - Return best match with score
   - Return None if no candidates or score < config['matching']['medium_confidence_threshold']

6. **`match_all_schools(our_df, kir_df, manual_mapping, config, log)`**
   - Iterate all unique (school_name, city) combinations
   - Call match_school for each
   - Categorize by confidence (using config thresholds):
     - MANUAL: From mapping file
     - AUTO_HIGH: score ≥ config['matching']['high_confidence_threshold']
     - AUTO_MEDIUM: score ≥ config['matching']['medium_confidence_threshold'] and < high_threshold
     - DROPPED: score < medium_threshold or no match
   - Return results DataFrame with columns:
     - our_school_name, our_city
     - matched_school_name, matched_city, matched_county, matched_region
     - confidence_score, match_method, status
   - Log statistics

7. **`apply_matches(our_df, match_results, log)`**
   - For each row in our_df, find corresponding match in match_results
   - For MANUAL and AUTO (HIGH/MEDIUM):
     - Update iskola_nev with matched_school_name
     - Update varos with normalized matched_city
     - Add vármegye column with matched_county
     - Add régió column with matched_region
   - For DROPPED:
     - Mark row for removal
   - Return updated DataFrame (with dropped rows removed)
   - Log: "Applied N matches, dropped M schools"

**Acceptance Criteria:**
- Uses rapidfuzz.fuzz.token_set_ratio for matching
- City filtering prevents false positives
- Manual mappings take precedence
- Thresholds loaded from config.yaml
- apply_matches function updates DataFrame and removes dropped schools
- Returns comprehensive results for audit

---

#### FR-008: School Matching Integration

**Description:** Integrate school matching into step 04 (merger script).

**Process Flow:**

**Step 1: Load and prepare data**
- Load all processed CSVs (existing logic)
- Merge into master DataFrame (existing logic)

**Step 2: Apply city corrections**
- Load city_mapping.csv
- Apply city corrections to master DataFrame
- Log: "Applied N city corrections"

**Step 3: Load KIR and mappings**
- Load KIR database
- Load school_mapping.csv (if exists)

**Step 4: Match schools**
- Call match_all_schools()
- Get match_results DataFrame with match decisions

**Step 5: Apply matches**
- Call apply_matches(master_df, match_results)
- Returns updated DataFrame with:
  - Matched school names
  - Normalized cities
  - New vármegye and régió columns
  - Dropped schools removed

**Step 6: Generate outputs**
- Save audit file (see FR-008)
- Update validation report (see FR-009)
- Save master CSV with new columns
- Generate Excel report (unchanged)

**Acceptance Criteria:**
- City corrections applied before matching
- Manual mappings override automatic matches
- Thresholds loaded from config.yaml
- apply_matches function handles DataFrame updates
- Schools with confidence ≥ medium_threshold are kept
- Schools with confidence < medium_threshold are dropped
- All decisions logged and audited

---

#### FR-009: Audit File Generation

**Description:** Generate comprehensive audit CSV for all matching decisions.

**Details:**
- **Location:** `data/school_matching_audit.csv`
- **Format:** Semicolon-separated, UTF-8
- **Columns:**
  ```csv
  our_school_name;our_city;matched_school_name;matched_city;confidence_score;match_method;status;comment
  ```

**Column definitions:**
- **our_school_name:** Original name from competition data
- **our_city:** City after city_mapping corrections
- **matched_school_name:** KIR school name (or empty if dropped)
- **matched_city:** KIR city (or empty if dropped)
- **confidence_score:** token_set_ratio score (0-100, or empty for MANUAL)
- **match_method:** MANUAL | AUTO_HIGH | AUTO_MEDIUM | DROPPED
- **status:** APPLIED | NOT_APPLIED
- **comment:** 
  - MANUAL: Copy from mapping file
  - AUTO: Empty or "Auto-matched"
  - DROPPED: "Low confidence - needs manual review"

**Acceptance Criteria:**
- One row per unique (school_name, city) combination
- All decisions documented
- Sorted by match_method, then school_name
- Logged: "Generated audit file: N schools processed, M applied, K dropped"

---

#### FR-010: Validation Report Update

**Description:** Add school matching statistics to validation_report.json.

**Details:**
- **Location:** `data/validation_report.json` (existing file, add section)
- **New section:**
  ```json
  {
    "school_matching": {
      "total_schools": 773,
      "manual_matches": 5,
      "auto_high_confidence": 650,
      "auto_medium_confidence": 100,
      "dropped_low_confidence": 18,
      "records_kept": 3150,
      "records_dropped": 83
    }
  }
  ```

**Acceptance Criteria:**
- Statistics added to existing validation report
- Counts match audit file
- JSON remains valid

---

### 3.4. Data Schema Changes

#### FR-011: Column Renaming and Addition

**Description:** Update master CSV schema with new geographic columns.

**Changes:**
1. **Rename:** `megye` → `vármegye`
2. **Add:** `régió` (new column)
3. **Update:** `varos` (replace with normalized KIR city)
4. **Update:** `iskola_nev` (replace with KIR school name)

**New schema:**
```csv
ev;targy;iskola_nev;varos;vármegye;régió;helyezes;evfolyam
2024-25;Anyanyelv;Abádszalóki Kovács Mihály Általános Iskola;Abádszalók;Jász-Nagykun-Szolnok;Észak-Alföld;1;8
```

**City normalization:**
- "Budapest III. kerület" → "Budapest III."
- Remove " kerület" suffix
- Keep district number

**Acceptance Criteria:**
- All matched schools have vármegye and régió
- City names normalized (no " kerület")
- School names match KIR exactly
- CSV remains semicolon-separated, UTF-8

---

### 3.5. Notebook Enhancements

#### FR-012: County Rankings

**Description:** Add county rankings to Jupyter notebook (count-based and weighted).

**Details:**
- **Location:** `notebooks/competition_analysis.ipynb`
- **New sections:** After City Rankings
  - "County Rankings (Count-based)" / "Vármegyék rangsora (darabszám alapján)"
  - "County Rankings (Weighted)" / "Vármegyék rangsora (súlyozott pontszám alapján)"

**Parameters:**
```python
DISPLAY_TOP_N = 20
YEAR_FILTER = "all"  # or "2024-25" or ["2024-25", "2023-24"]
GRADE_FILTER = "all"  # or 8 or [7, 8]
REGION_FILTER = "all"  # or "Közép-Magyarország" or ["Közép-Magyarország", "Észak-Alföld"]
```

**Logic:**
- Apply YEAR_FILTER, GRADE_FILTER, REGION_FILTER (if specified)
- Group by vármegye
- Count: Number of teams
- Weighted: Sum of (max_helyezes - helyezes + 1) per year/grade
- Sort by count/score descending, then by name (Hungarian sort)

**Acceptance Criteria:**
- Both count and weighted rankings
- YEAR_FILTER, GRADE_FILTER, REGION_FILTER support (all, string, list)
- Dual language (Hungarian/English)
- Pandas display settings aligned with DISPLAY_TOP_N

---

#### FR-013: Region Rankings

**Description:** Add region rankings to Jupyter notebook (count-based and weighted).

**Details:**
- **Location:** `notebooks/competition_analysis.ipynb`
- **New sections:** After County Rankings
  - "Region Rankings (Count-based)" / "Régiók rangsora (darabszám alapján)"
  - "Region Rankings (Weighted)" / "Régiók rangsora (súlyozott pontszám alapján)"

**Parameters:**
```python
DISPLAY_TOP_N = 20
YEAR_FILTER = "all"  # or "2024-25" or ["2024-25", "2023-24"]
GRADE_FILTER = "all"  # or 8 or [7, 8]
# No REGION_FILTER for region rankings
```

**Logic:**
- Apply YEAR_FILTER, GRADE_FILTER (if specified)
- Group by régió
- Count: Number of teams
- Weighted: Sum of (max_helyezes - helyezes + 1) per year/grade
- Sort by count/score descending, then by name (Hungarian sort)

**Acceptance Criteria:**
- Both count and weighted rankings
- YEAR_FILTER, GRADE_FILTER support (all, string, list)
- No REGION_FILTER (doesn't make sense to filter regions when ranking regions)
- Dual language (Hungarian/English)
- Pandas display settings aligned with DISPLAY_TOP_N

---

#### FR-014: Filter Enhancements

**Description:** Add county and region filters to existing school and city rankings.

**Details:**

**School Rankings (Count + Weighted):**
- Add COUNTY_FILTER parameter
- Add REGION_FILTER parameter
- Existing CITY_FILTER remains

**City Rankings (Count + Weighted):**
- Add COUNTY_FILTER parameter
- Add REGION_FILTER parameter
- No CITY_FILTER (doesn't make sense)

**Filter logic:**
- `"all"` - no filtering
- `"string"` - single value match
- `["list"]` - multiple values match (OR logic)

**Acceptance Criteria:**
- All filters work consistently across sections
- Filters applied before aggregation
- Dual language documentation
- No breaking changes to existing notebook

---

### 3.6. Documentation Updates

#### FR-015: Main README Update

**Description:** Update main project README.md with v0.4.0 changes.

**File:** `README.md`

**Sections to update:**

1. **Áttekintés (Overview)**
   - Update version to 0.4.0
   - Mention school name normalization
   - Update data statistics (schools, cities after cleaning)

2. **Milyen adatokat gyűjt? (What data is collected)**
   - Add vármegye and régió to list

3. **Lefedett időszak (Coverage period)**
   - Update total records count (after dropping unmatched schools)
   - Update school and city counts

4. **Futtatás (Running)**
   - Add step 03: `poetry run python 03_download_helper_data.py`
   - Update step numbers for 04

5. **Eredmények (Results)**
   - Mention new columns in master CSV
   - Mention audit file

**Acceptance Criteria:**
- Version updated to 0.4.0
- New step 03 documented
- New columns documented
- Statistics updated

---

#### FR-016: Kaggle README Updates

**Description:** Update both English and Hungarian Kaggle README files.

**Files:**
- `templates/kaggle/README.en.md`
- `templates/kaggle/README.hu.md`

**Sections to update:**

1. **File description (master_bolyai_anyanyelv.csv)**
   - Add vármegye and régió columns
   - Update example row

2. **Data Quality**
   - Describe automated school matching
   - Mention KIR database integration

3. **Limitations**
   - Update what's fixed (school names, city names, county/region data)
   - Update what remains (historical name changes not tracked)

4. **Updates & Maintenance**
   - Version: 0.4.0
   - Last updated: 2025-12-28
   - New in 0.4.0: School name normalization, county/region data

5. **Data Cleaning Process**
   - Replace city cleaning description with school matching
   - Describe automated matching with manual override
   - Mention audit trail

6. **Known Data Quality Limitations**
   - Update school name variations status: "Addressed via KIR matching"
   - Note: Schools not in KIR are removed
   - Note: ~7% may need manual review

**Acceptance Criteria:**
- Both language versions updated consistently
- Version number updated to 0.4.0
- Accurate description of new features
- Clear explanation of what changed

---

### 3.7. Testing Requirements

#### FR-017: Unit Tests

**Description:** Create unit tests for new school matching functionality.

**Test file:** `tests/test_school_matcher.py`

**Test coverage:**
- `normalize_city()` - various formats, edge cases
- `cities_match()` - exact match, Budapest special case
- `load_school_mapping()` - valid file, missing file, malformed file
- `match_school()` - manual override, high confidence, low confidence, no match
- `apply_matches()` - DataFrame updates, dropped schools
- Token_set_ratio behavior with test cases
- Simplified city_checker functions

**Test data:**
- Small fixtures (10-20 schools) for unit tests
- Real KIR file for integration tests

**Acceptance Criteria:**
- All new functions have unit tests
- Edge cases covered
- Tests run fast (<5 seconds for unit tests)

---

#### FR-018: Integration Tests

**Description:** Create integration tests for full pipeline with school matching.

**Test file:** `tests/test_integration.py` (update existing)

**Test scenarios:**
- Full pipeline with KIR file present
- Pipeline fails gracefully if KIR file missing
- Manual mappings override automatic matches
- Audit file generated correctly
- Validation report updated correctly

**Test data:**
- Use real downloaded KIR file
- Use real competition data

**Acceptance Criteria:**
- Integration tests cover end-to-end workflow
- Tests verify audit file contents
- Tests verify dropped schools are removed

---

#### FR-019: Notebook Helper Function Tests

**Description:** Add tests for new notebook helper functions (filters).

**Test file:** `tests/test_notebook_helpers.py` (update existing)

**Test coverage:**
- County filter logic (all, string, list)
- Region filter logic (all, string, list)
- Year and grade filters applied correctly
- Filter combinations work together

**Acceptance Criteria:**
- All new filter functions tested
- Edge cases covered (empty results, invalid filter values)
- Tests use sample data fixtures

---

## 4. Non-Functional Requirements

### NFR-001: Performance

**Requirement:** School matching must complete in reasonable time.

**Criteria:**
- Match 700+ schools in <5 minutes on standard hardware
- Use rapidfuzz for performance (10-100x faster than difflib)

---

### NFR-002: Maintainability

**Requirement:** Code must be clean, documented, and follow project conventions.

**Criteria:**
- Follow project coding rules (README-ai-rules.md)
- Self-documenting code (minimal comments)
- Module-level loggers
- Small, focused functions

---

### NFR-003: Transparency

**Requirement:** All matching decisions must be auditable.

**Criteria:**
- Comprehensive audit file
- All decisions logged
- Manual overrides clearly marked
- Confidence scores recorded

---

### NFR-004: Backward Compatibility

**Requirement:** Existing functionality must continue to work.

**Criteria:**
- Excel report generation unchanged
- Existing notebook sections work
- No breaking changes to config.yaml structure
- Old data files remain readable

---

## 5. Dependencies

### 5.1. New Dependencies

**rapidfuzz:**
- Version: ^3.14.3
- Purpose: Fast fuzzy string matching
- Installation: `poetry add rapidfuzz`

### 5.2. External Data Sources

**KIR Database:**
- URL: https://kir.oktatas.hu/kirpub/index
- File: kir_mukodo_feladatellatasi_helyek_YYYY_MM_DD.xlsx
- Update frequency: Daily
- License: Public data from Hungarian government

---

## 6. Constraints

### 6.1. Technical Constraints

- Must work with existing Poetry/Python 3.11+ environment
- Must maintain CSV format (semicolon-separated, UTF-8)
- Must work on Kaggle platform (notebook)

### 6.2. Data Constraints

- KIR database must be downloaded manually (step 03)
- Schools not in KIR will be dropped
- Historical name changes not tracked
- Closed schools not handled (will be dropped)

---

## 7. Acceptance Criteria

### 7.1. Core Functionality

- ✅ Step 03 downloads KIR database successfully
- ✅ Step 04 fails if KIR file missing
- ✅ City mapping applied before school matching
- ✅ School matching uses token_set_ratio with city filtering
- ✅ Manual mappings override automatic matches
- ✅ Schools with confidence ≥80 are kept
- ✅ Schools with confidence <80 are dropped
- ✅ Audit file generated with all decisions
- ✅ Validation report includes school matching stats
- ✅ Master CSV has vármegye and régió columns
- ✅ City names normalized (no " kerület")

### 7.2. Notebook Enhancements

- ✅ County rankings (count + weighted) added
- ✅ Region rankings (count + weighted) added
- ✅ County and region filters work on school/city rankings
- ✅ All filters support "all", string, and list formats
- ✅ Dual language support maintained
- ✅ No breaking changes to existing sections

### 7.3. Documentation

- ✅ Kaggle README updated (both languages)
- ✅ Version updated to 0.4.0
- ✅ New columns documented
- ✅ Data cleaning process described
- ✅ Limitations updated

### 7.4. Testing

- ✅ All unit tests pass
- ✅ Integration tests pass with real data
- ✅ Test coverage for new functionality
- ✅ No regressions in existing tests

---

## 8. Future Enhancements (Out of Scope)

These are explicitly NOT included in v0.4.0 but may be considered for future releases:

1. **Closed schools handling:** Match to successor institutions
2. **Historical name tracking:** Track school name changes over time
3. **Interactive matching UI:** Web interface for manual review
4. **Additional competitions:** OKTV, Zrínyi Ilona, other Bolyai subjects
5. **Automated city detection:** Use external geocoding services
6. **School merger tracking:** Handle institutional mergers

---

**Document Version:** 1.0  
**Date:** 2025-12-28  
**Status:** Final  
**Ready for Design Phase**
