# Software Requirements Specification (SRS): Data Quality & Notebook Enhancements - v0.3.0

## 1. Introduction

### 1.1. Purpose

This document specifies the requirements for **version 0.3.0** of the Hungarian Academic Competition Results Pipeline project. This release focuses on two main areas:
1. **Data Quality Improvement**: Implementing city name cleaning through a manual mapping system
2. **Notebook Enhancements**: Adding usability improvements to the Jupyter notebook

### 1.2. Document Conventions

- **FR-XXX:** Denotes a specific Functional Requirement
- **NFR-XXX:** Denotes a specific Non-Functional Requirement
- **MVP:** Minimum Viable Product - keeping features simple and focused for initial release

### 1.3. Intended Audience

- **Lead Developer / Coding Agent:** Primary audience for implementation
- **Project Owner:** For validation of requirements
- **Data Analysts:** Users who will create and maintain the city mapping file
- **Notebook Users:** Researchers using the Jupyter notebook for analysis

### 1.4. Product Scope

**In Scope for v0.3.0:**

**City Name Cleaning:**
- Manual city name mapping system using CSV configuration
- City variation detection and validation
- Integration into the merger phase (step 3)
- Standalone checker script for analysis
- Validation report updates
- Dataset documentation updates

**Notebook Enhancements:**
- Table of Contents with bilingual structure
- City filter for school rankings
- Pandas display settings aligned with DISPLAY_TOP_N

**Out of Scope for v0.3.0:**

- School name normalization (future release)
- Automated city name detection using external databases
- County data enrichment (requires external database)
- Budapest district normalization (requires school name cleaning first)
- Interactive widgets or visualizations
- Additional competitions beyond Bolyai Anyanyelv

### 1.5. References

1. **v0.2.0 Documentation:** `dev-history/v0.2/` - Previous version's requirements and design
2. **Data Integrity Analysis:** `!local-notes/data-integrity-issue/` - Detailed analysis of data quality issues
3. **City Issues Analysis:** `!local-notes/data-integrity-issue/city-issues-analysis.txt` - Manual review of city variations
4. **Dataset:** `data/kaggle/master_bolyai_anyanyelv.csv` - Current master dataset

---

## 2. Overall Description

### 2.1. Product Perspective

Version 0.3.0 builds on the existing data pipeline (v0.1) and analysis notebook (v0.2) by addressing known data quality issues and improving notebook usability. The city name cleaning feature is the first step in a broader data quality improvement roadmap.

### 2.2. Background: Data Quality Issues

Analysis of the competition results revealed systematic data quality issues in city names:

**Issue Categories Identified:**

1. **Case variations** (1 case)
   - Example: "MISKOLC" vs "Miskolc"
   - Solution: Normalize to proper case

2. **Hyphenated suburbs** (1 case)
   - Example: "Debrecen-Józsa" vs "Debrecen"
   - Solution: Map to parent city

3. **Budapest district missing** (8 cases)
   - Example: "Budapest" vs "Budapest II."
   - Challenge: Requires school name + city composite key
   - Note: Official Hungarian school database always includes district in city field

4. **Valid variations** (5 cases)
   - Different schools with same name in different cities
   - Same school with multiple locations
   - Solution: Mark as "VALID" in mapping, no correction needed

**Total affected schools:** 15 schools with city variations
**Approach:** Manual mapping CSV maintained by humans, with automated detection and validation

### 2.3. Design Philosophy

**For City Cleaning:**
- **Human-in-the-loop:** Automated detection, manual decision-making
- **Transparency:** All mappings documented and auditable
- **Opt-in:** Mapping file is optional; system works without it
- **Composite keys:** Support school name + city combinations for Budapest districts

**For Notebook Enhancements:**
- **Usability first:** Make common tasks easier
- **Backward compatible:** Don't break existing notebook usage
- **Self-documenting:** Clear structure and navigation

---

## 3. Functional Requirements

### 3.1. City Name Cleaning System

#### FR-001: City Mapping Configuration File

**Description:** The system shall support a CSV-based city mapping configuration file.

**Details:**
- **Location:** `config/city_mapping.csv`
- **Path configuration:** Configurable in `config.yaml` under new `validation:` section
  ```yaml
  validation:
    city_mapping_file: "config/city_mapping.csv"
  ```
- **File format:** CSV with UTF-8 encoding, semicolon delimiter (consistent with project)
- **Columns:**
  - `school_name`: The school name (required for composite key)
  - `original_city`: The city name as it appears in source data
  - `corrected_city`: The corrected city name (empty for VALID entries)
  - `comment`: Human-readable explanation (e.g., "VALID - different schools", "Normalize case", "Add district")

**Example entries:**
```csv
school_name;original_city;corrected_city;comment
Diósgyőri Szent Ferenc Római Katolikus Általános Iskola és Óvoda;MISKOLC;Miskolc;Normalize case
Debreceni Gönczy Pál Általános Iskola;Debrecen-Józsa;Debrecen;Map suburb to parent city
Baár-Madas Református Gimnázium és Általános Iskola;Budapest;Budapest II.;Add missing district
Gárdonyi Géza Általános Iskola;Budapest XIII.;;VALID - different schools with same name
Gárdonyi Géza Általános Iskola;Győr;;VALID - different schools with same name
```

**Acceptance Criteria:**
- File is optional; system works without it (no corrections applied)
- If file exists but is malformed, system logs error and continues without corrections
- Empty `corrected_city` with "VALID" in comment means keep original (no correction)
- Composite key (school_name, original_city) allows different corrections for same school name

---

#### FR-002: City Validation Module

**Description:** Create a new validation module with city checking functionality.

**Details:**
- **Module location:** `src/tanulmanyi_versenyek/validation/city_checker.py`
- **Dual execution mode:**
  1. **Standalone:** `python -m tanulmanyi_versenyek.validation.city_checker`
  2. **Integrated:** Called by `03_merger_and_excel.py` during merge phase

**Core Functions:**
1. `load_city_mapping(config)` - Load and parse the mapping CSV
2. `apply_city_mapping(df, mapping, log)` - Apply corrections to DataFrame
3. `check_city_variations(df, mapping, log)` - Detect and warn about unmapped variations
4. `main()` - Standalone execution entry point

**Acceptance Criteria:**
- Module can be executed standalone using Python's `-m` flag
- Module can be imported and used by other scripts
- Uses project's standard logging configuration
- Reads configuration from `config.yaml`

---

#### FR-003: City Mapping Application

**Description:** Apply city name corrections during the merge phase (step 3).

**Process Flow:**

**Step 1: Load mapping file**
- Read `config/city_mapping.csv` if it exists
- Parse into a dictionary keyed by (school_name, original_city)
- Log INFO: "Loaded N city mappings from config/city_mapping.csv"
- If file doesn't exist: Log INFO: "No city mapping file found, skipping corrections"

**Step 2: Apply corrections**
- After merging all CSV files into master DataFrame
- Before generating validation report and Excel
- For each row in DataFrame:
  - Check if (school_name, city) exists in mapping
  - If exists and comment contains "VALID": skip (keep original)
  - If exists and corrected_city is not empty: replace city with corrected_city
  - Log DEBUG for each applied correction: `Applied mapping: school="<name>", "<original>" → "<corrected>"`
- Log INFO: "Applied N city corrections"

**Step 3: Check for unmapped variations**
- Group DataFrame by school_name, count unique cities
- For schools with 2+ cities:
  - Check if all (school_name, city) combinations are in mapping file
  - Allowed combinations:
    - (school_name, original_city) with "VALID" in comment, OR
    - (school_name, corrected_city) from mapping
  - For unmapped combinations:
    - Log WARNING: `Unmapped combination: school="<name>", city="<city>"`

**Acceptance Criteria:**
- Corrections applied to master DataFrame before saving to CSV
- Corrected cities appear in final `master_bolyai_anyanyelv.csv`
- Corrected cities appear in Excel reports
- Individual CSV files in `processed_csv/` remain unchanged (corrections only in merged data)
- Warnings logged for unmapped variations
- Process is idempotent (running multiple times produces same result)

---

#### FR-004: Standalone City Checker

**Description:** Allow standalone execution of city checker for analysis and mapping file creation.

**Execution:**
```bash
python -m tanulmanyi_versenyek.validation.city_checker
```

**Behavior:**
- Read configuration from `config.yaml`
- Load master CSV from configured path
- Load city mapping file (if exists)
- Execute same checking logic as integrated mode
- Output to console and log file

**Logging Output:**
- **WARNING level:** Unmapped (school_name, city) combinations
  - Format: `WARNING: Unmapped combination: school="<name>", city="<city>"`
- **INFO level:** Summary statistics
  - Total schools with variations
  - Mapped combinations count
  - Valid combinations count
  - Unmapped combinations count
- **DEBUG level:** Detailed information for each variation found

**Acceptance Criteria:**
- Can be run independently without running full pipeline
- Uses same logging configuration as other scripts
- Produces identical warnings as integrated mode
- Helps users identify what needs to be added to mapping file

---

#### FR-005: Validation Report Updates

**Description:** Update the validation report JSON to include city mapping statistics.

**New Section in `validation_report.json`:**
```json
{
  "total_records": 3233,
  "duplicates_removed": 123,
  "city_mapping": {
    "corrections_applied": 15,
    "valid_variations": 5,
    "unmapped_variations": 3
  },
  ...
}
```

**Statistics Definitions:**
- `corrections_applied`: Number of rows where city was changed (corrected_city applied)
- `valid_variations`: Number of rows matching (school_name, city) marked as VALID
- `unmapped_variations`: Number of unique (school_name, city) combinations that have variations but are not in mapping file

**Acceptance Criteria:**
- New `city_mapping` section added to validation report
- Statistics accurately reflect the mapping process
- Report generated after city mapping is applied

---

### 3.2. Documentation Updates

#### FR-006: Dataset README Updates

**Description:** Update Kaggle dataset README files to document the city cleaning process.

**Changes to `templates/kaggle/README.hu.md` and `README.en.md`:**

**New Section (before "Known Data Quality Limitations"):**
```markdown
## Data Cleaning Process / Adatminőség-javítási folyamat

### City Name Normalization / Városnevek normalizálása

The dataset includes manual city name cleaning to address variations in the source data:

- **Case normalization**: "MISKOLC" → "Miskolc"
- **Suburb mapping**: "Debrecen-Józsa" → "Debrecen"
- **Budapest districts**: Missing districts added where identifiable (e.g., "Budapest" → "Budapest II." for specific schools)

The cleaning process uses a manually maintained mapping file that preserves data authenticity while improving consistency. Valid variations (e.g., schools with the same name in different cities) are documented but not modified.

For details on the cleaning methodology, see the project repository.
```

**Update "Known Data Quality Limitations" section:**
- Note that city name variations have been partially addressed
- School name variations remain (planned for future release)
- Budapest district normalization is limited (requires school name cleaning)

**Acceptance Criteria:**
- Both Hungarian and English READMEs updated
- New section clearly explains what was cleaned and how
- Limitations section updated to reflect current state
- Main project README.md remains unchanged (high-level only)

---

### 3.3. Notebook Enhancements

#### FR-007: Table of Contents

**Description:** Add a navigable Table of Contents at the beginning of the notebook.

**Structure:**

**Cell 1: Warning (before TOC)**
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

**Cell 2: Table of Contents**
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

**Implementation:**
- Manual markdown links to section headers
- Bilingual format (Hungarian / English side-by-side)
- Grouped by Setup vs. Analysis
- Warning prominently displayed before TOC

**Acceptance Criteria:**
- All links work correctly (jump to corresponding sections)
- Warning is clearly visible
- TOC structure matches actual notebook sections
- Both languages included

---

#### FR-008: City Filter for School Rankings

**Description:** Add city filtering capability to school ranking sections.

**Affected Sections:**
- School Rankings (Count-based)
- School Rankings (Weighted)

**Not affected:**
- City Rankings (filtering cities in city rankings doesn't make sense)
- School Search (out of scope)

**Parameter:**
```python
# Filter by city/cities (optional)
# "all" = all cities (default)
# Single city: CITY_FILTER = "Budapest II."
# Multiple cities: CITY_FILTER = ["Budapest II.", "Budapest VII.", "Debrecen"]
CITY_FILTER = "all"
```

**Behavior:**
- If `CITY_FILTER` is `"all"`: show all cities (current behavior)
- If `CITY_FILTER` is a string (other than "all"): filter to that single city
- If `CITY_FILTER` is a list: filter to schools from any of those cities
- Filter applied before ranking calculation
- Works in combination with existing filters (GRADE_FILTER, YEAR_FILTER)

**Acceptance Criteria:**
- Parameter added to both school ranking sections
- Supports "all", single string, and list of strings
- Filtering works correctly with existing filters
- Clear comments explain usage
- Both Hungarian and English explanations updated

---

#### FR-009: Pandas Display Settings

**Description:** Align pandas display settings with DISPLAY_TOP_N to prevent truncation.

**Problem:**
- Pandas default `max_rows` setting truncates tables (shows top 5 and bottom 5)
- Users set `DISPLAY_TOP_N = 20` but only see 10 rows (5 top + 5 bottom)

**Solution:**
- Before displaying each ranking table, set `pd.options.display.max_rows = DISPLAY_TOP_N`
- After display, restore original setting
- Apply to all ranking display sections
- For School Search: set to `None` (unlimited) to show all results for the searched school

**Implementation Pattern:**
```python
# Save original setting
original_max_rows = pd.options.display.max_rows

# Set to match DISPLAY_TOP_N (or None for unlimited)
pd.options.display.max_rows = DISPLAY_TOP_N  # or None for School Search

# Display table
display(result_df)

# Restore original setting
pd.options.display.max_rows = original_max_rows
```

**Affected Sections:**
- School Rankings (Count-based) - use DISPLAY_TOP_N
- School Rankings (Weighted) - use DISPLAY_TOP_N
- City Rankings (Count-based) - use DISPLAY_TOP_N
- City Rankings (Weighted) - use DISPLAY_TOP_N
- School Search - use None (unlimited, show all results)

**Acceptance Criteria:**
- Applied to all five sections (4 rankings + search)
- Original setting properly saved and restored
- No side effects on other cells
- Full table displays when DISPLAY_TOP_N is set
- School Search shows all results without truncation

---

## 4. Non-Functional Requirements

### 4.1. Performance

**NFR-001: City Mapping Performance**
- City mapping application should add < 5 seconds to merge script execution
- Variation checking should complete in < 10 seconds for 3000+ records

**NFR-002: Notebook Performance**
- City filtering should not noticeably slow down ranking calculations
- Display settings changes should be instantaneous

### 4.2. Usability

**NFR-003: Mapping File Maintenance**
- City mapping CSV should be human-readable and editable in any text editor
- Comments should clearly explain each mapping decision
- File format should be consistent with project conventions (UTF-8, semicolon delimiter)

**NFR-004: Warning Clarity**
- Warning messages should clearly identify what needs attention
- Format should be copy-paste friendly for adding to mapping file
- Warnings should not be overwhelming (one per unmapped combination)

**NFR-005: Notebook Navigation**
- Table of Contents should make navigation intuitive
- Warning about setup requirements should be impossible to miss
- Parameter names should be self-explanatory

### 4.3. Maintainability

**NFR-006: Code Organization**
- City validation logic isolated in dedicated module
- Module can be tested independently
- Clear separation between detection and correction logic

**NFR-007: Documentation**
- All new features documented in code comments
- Dataset README clearly explains cleaning process
- Mapping file format documented in comments

### 4.4. Compatibility

**NFR-008: Backward Compatibility**
- System works without mapping file (optional feature)
- Existing notebooks continue to work without modification
- No breaking changes to existing APIs or file formats

**NFR-009: Platform Compatibility**
- Notebook enhancements work on both Kaggle and local environments
- No dependencies on Kaggle-specific features for core functionality

---

## 5. Future Enhancements (Out of Scope for v0.3.0)

### 5.1. School Name Normalization

**Background:**
Analysis revealed 70+ school groups with name variations due to:
- Official name changes over time
- Different formatting conventions
- Addition/removal of institution type suffixes

**Example:**
- "Baár-Madas Református Gimnázium és Általános Iskola" (21 records)
- "Baár-Madas Református Gimnázium, Általános Iskola és Kollégium" (12 records)

**Planned Approach:**
- Similar to city mapping: manual CSV-based mapping
- Composite key: (school_name, city) → normalized_school_name
- More complex than city cleaning due to higher variation count
- Requires careful research of official school names

**Dependencies:**
- Should be done after city cleaning is stable
- May benefit from official school database integration

### 5.2. Budapest District Normalization

**Background:**
Budapest schools often appear with and without district information:
- "Budapest" vs "Budapest II." vs "Budapest VII."
- Official school database always includes district in city field
- District is part of official school name in many cases

**Challenge:**
- Cannot normalize districts without knowing which school is which
- Same school name may exist in multiple districts
- Requires school name normalization first

**Planned Approach:**
1. Complete school name normalization (v0.4 or later)
2. Use official school database to map schools to districts
3. Always include district for Budapest schools
4. Update city mapping to handle district variations

**Impact on Statistics:**
- Budapest will become a "big outlier" with many schools
- Plan to add normalized statistics (divide by number of schools)
- May need separate Budapest district rankings

### 5.3. County Data Enrichment

**Background:**
- Current dataset has empty `megye` (county) column
- Source website doesn't provide county information
- Users want to analyze by geographical regions

**Planned Approach:**
- Integrate official Hungarian city/county database
- Map cities to counties automatically
- Could also help with city name normalization
- Enables county-level rankings and analysis

**Benefits:**
- Better geographical analysis
- Regional comparisons
- Could help identify city name variations

### 5.4. Official School Database Integration

**Background:**
- Hungarian official school database (KIR - Köznevelési Információs Rendszer) contains:
  - Official school names (with city/district in name)
  - Accurate city and district information
  - School type, address, etc.

**Potential Uses:**
- Validate and normalize school names
- Add missing Budapest districts
- Verify city names
- Enrich dataset with additional school metadata

**Challenges:**
- Database access and licensing
- Matching schools across different naming conventions
- Keeping data synchronized over time

---

## 6. Testing Requirements

### 6.1. City Mapping Tests

**Test Cases:**

1. **Test mapping file loading**
   - Valid CSV with all columns
   - Missing file (should continue without errors)
   - Malformed CSV (should log error and continue)
   - Empty file (should work, no mappings)

2. **Test correction application**
   - Simple case normalization
   - Suburb to parent city mapping
   - Budapest district addition
   - VALID entries (should not change)
   - Composite key handling (same school, different cities)

3. **Test variation detection**
   - Schools with 2+ cities
   - All mapped (no warnings)
   - Partially mapped (warnings for unmapped)
   - All marked VALID (no warnings)

4. **Test standalone execution**
   - Runs without errors
   - Produces same warnings as integrated mode
   - Uses correct configuration

5. **Test validation report**
   - Statistics accurately reflect corrections
   - JSON format valid
   - All three metrics present

### 6.2. Notebook Enhancement Tests

**Test Cases:**

1. **Test Table of Contents**
   - All links work (jump to correct sections)
   - Warning is visible
   - Structure matches notebook

2. **Test city filter**
   - "all" (all cities)
   - Single city string
   - Multiple cities list
   - Empty list (should show nothing or all?)
   - Non-existent city (should show empty result)
   - Combination with other filters

3. **Test pandas display settings**
   - Setting applied before display
   - Original setting restored after
   - Works for all ranking sections
   - No side effects on other cells

### 6.3. Integration Tests

**Test Cases:**

1. **Full pipeline with city mapping**
   - Run 01, 02, 03 with mapping file
   - Verify corrections in master CSV
   - Verify corrections in Excel
   - Verify validation report statistics

2. **Full pipeline without mapping file**
   - Should work exactly as before
   - No errors or warnings about missing file

3. **Notebook with cleaned data**
   - Rankings reflect cleaned city names
   - City filter works with cleaned names
   - No errors or unexpected behavior

---

## 7. Acceptance Criteria Summary

### 7.1. City Name Cleaning

- [ ] City mapping CSV format defined and documented
- [ ] Validation module created in `src/tanulmanyi_versenyek/validation/`
- [ ] Module executable standalone and as import
- [ ] City corrections applied during merge phase
- [ ] Warnings logged for unmapped variations
- [ ] Validation report includes city mapping statistics
- [ ] Dataset READMEs updated with cleaning documentation
- [ ] All tests passing

### 7.2. Notebook Enhancements

- [ ] Table of Contents added with warning
- [ ] All TOC links work correctly
- [ ] City filter added to school rankings
- [ ] City filter supports "all", string, and list
- [ ] Pandas display settings aligned with DISPLAY_TOP_N
- [ ] Settings properly saved and restored
- [ ] All enhancements work on Kaggle and locally

### 7.3. Quality Assurance

- [ ] No breaking changes to existing functionality
- [ ] System works without mapping file (optional)
- [ ] Code follows project conventions and style
- [ ] All new code has appropriate logging
- [ ] Documentation is clear and complete

---

## 8. Appendix

### 8.1. Example City Mapping File

```csv
school_name;original_city;corrected_city;comment
Diósgyőri Szent Ferenc Római Katolikus Általános Iskola és Óvoda;MISKOLC;Miskolc;Normalize case to proper case
Debreceni Gönczy Pál Általános Iskola;Debrecen-Józsa;Debrecen;Map suburb to parent city
Budapest-Fasori Református Kollégium Julianna Általános Iskola;Budapest;Budapest VII.;Add missing district based on school location
Baár-Madas Református Gimnázium és Általános Iskola;Budapest;Budapest II.;Add missing district based on school location
Deák Téri Evangélikus Gimnázium;Budapest;Budapest V.;Add missing district based on school location
Pannonhalmi Főapátság Máriaremete-Hidegkúti Ökumenikus Általános Iskolája;Budapest;Budapest II.;Add missing district based on school location
Remetekertvárosi Általános Iskola;Budapest;Budapest II.;Add missing district based on school location
Rózsadombi Általános Iskola;Budapest;Budapest II.;Add missing district based on school location
Újlaki Magyar-Olasz Két Tanítási Nyelvű Általános Iskola;Budapest;Budapest II.;Add missing district based on school location
Gárdonyi Géza Általános Iskola;Budapest XIII.;;VALID - different schools with same name in different districts
Gárdonyi Géza Általános Iskola;Budapest XI.;;VALID - different schools with same name in different districts
Gárdonyi Géza Általános Iskola;Győr;;VALID - different schools with same name in different cities
Jókai Mór Általános Iskola;Budapest XIV.;;VALID - different schools with same name in different districts
Jókai Mór Általános Iskola;Budapest XVI.;;VALID - different schools with same name in different districts
Kazinczy Ferenc Református Általános Iskola és Óvoda;Felsőzsolca;;VALID - different schools with same name in different cities
Kazinczy Ferenc Református Általános Iskola és Óvoda;Tiszaújváros;;VALID - different schools with same name in different cities
Kálvin Téri Református Általános Iskola;Makó;;VALID - different schools with same name in different cities
Kálvin Téri Református Általános Iskola;Veresegyház;;VALID - different schools with same name in different cities
Szent Erzsébet Katolikus Általános Iskola és Óvoda;Isaszeg;;VALID - same school with multiple locations
Szent Erzsébet Katolikus Általános Iskola és Óvoda;Pécel;;VALID - same school with multiple locations
Szent Imre Római Katolikus Általános Iskola és Óvoda;Miskolc;;VALID - different schools with same name in different cities
Szent Imre Római Katolikus Általános Iskola és Óvoda;Komárom;;VALID - different schools with same name in different cities
```

### 8.2. Configuration Changes

**New section in `config.yaml`:**
```yaml
validation:
  city_mapping_file: "config/city_mapping.csv"
```

### 8.3. Validation Report Example

```json
{
  "timestamp": "2025-12-23T17:30:00",
  "total_records": 3233,
  "unique_schools": 766,
  "unique_cities": 264,
  "years_covered": ["2015-16", "2016-17", ..., "2024-25"],
  "duplicates_removed": 123,
  "city_mapping": {
    "corrections_applied": 9,
    "valid_variations": 13,
    "unmapped_variations": 0
  }
}
```

---

**Document Version:** 1.0  
**Date:** 2025-12-23  
**Status:** Final  
**Next Steps:** Create detailed design document (step2-design.md)
