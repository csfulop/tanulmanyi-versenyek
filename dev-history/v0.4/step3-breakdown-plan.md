# Step-by-Step Implementation Breakdown Plan - v0.4.0

## Overview of Phases

1. **Phase 1: Configuration and Dependencies** - Update config, add dependencies, prepare infrastructure
2. **Phase 2: KIR Downloader Module** - Implement KIR database download functionality
3. **Phase 3: City Checker Simplification** - Simplify existing city validation module
4. **Phase 4: School Matcher Module** - Core school matching implementation
5. **Phase 5: Pipeline Integration** - Integrate matching into step 04, update schema
6. **Phase 6: Notebook Enhancements** - Add county/region rankings and filters
7. **Phase 7: Documentation and Testing** - Update docs, comprehensive testing

---

## Phase 1: Configuration and Dependencies

**Goal:** Prepare project infrastructure for school matching functionality.

• **Step 1.1: Update Configuration File**
  • Add `helper_data_dir` and `audit_file` to `paths` section in `config.yaml`
  • Add `school_mapping_file` to `validation` section
  • Add new `kir` section with index URL, file paths, required columns
  • Add new `matching` section with thresholds and algorithm name
  • Verification: Load config and verify new keys accessible

• **Step 1.2: Add Dependencies**
  • Add `rapidfuzz` to `pyproject.toml` (version ^3.14.3)
  • Add `beautifulsoup4` if not present (for KIR scraper)
  • Run `poetry install` and `poetry lock`
  • Verification: Import rapidfuzz in Python shell

• **Step 1.3: Create Helper Data Directory**
  • Create `data/helper_data/` directory
  • Add to `.gitignore` (KIR files are large, downloaded on demand)
  • Verification: Directory exists and is ignored by git

---

## Phase 2: KIR Downloader Module

**Goal:** Implement automated KIR database download functionality.

• **Step 2.1: Create KIR Downloader Module Structure**
  • Create `src/tanulmanyi_versenyek/kir_downloader/` directory
  • Create `__init__.py` (empty)
  • Create `kir_scraper.py` skeleton with module-level logger
  • Verification: Module imports successfully

• **Step 2.2: Implement URL Discovery Function**
  • Implement `get_latest_kir_url(index_url, pattern)` in `kir_scraper.py`
  • Use requests + BeautifulSoup to scrape index page
  • Find links matching filename pattern, extract most recent by date
  • Return full URL to latest Excel file
  • Verification: Unit test with mock HTML response

• **Step 2.3: Implement File Download Function**
  • Implement `download_kir_file(url, output_path)` in `kir_scraper.py`
  • Use requests with streaming for large files
  • Write to output path in chunks
  • Log file size and progress
  • Verification: Unit test with small test file

• **Step 2.4: Implement Directory Cleanup Function**
  • Implement `clear_helper_data_dir(dir_path)` in `kir_scraper.py`
  • Remove all files from directory (not subdirectories)
  • Log count of files removed
  • Verification: Unit test with temp directory

• **Step 2.5: Implement Main Download Function**
  • Implement `download_latest_kir_data(config)` in `kir_scraper.py`
  • Orchestrate: clear directory, get URL, download file
  • Return path to downloaded file
  • Verification: Integration test (may use real URL or mock)

• **Step 2.6: Create Step 03 Script**
  • Create `03_download_helper_data.py` in project root
  • Setup logging, load config
  • Call `download_latest_kir_data()`
  • Handle errors with clear messages
  • Verification: Run script manually (downloads real KIR file)

• **Step 2.7: Rename Existing Step 03**
  • Rename `03_merger_and_excel.py` to `04_merger_and_excel.py`
  • Update any references in documentation
  • Verification: Script runs with new name

---

## Phase 3: City Checker Simplification

**Goal:** Simplify city_checker.py to handle only city-to-city mapping.

• **Step 3.1: Simplify City Mapping File Format**
  • Update `config/city_mapping.csv` to three-column format: `original_city;corrected_city;comment`
  • Remove any composite key entries (school_name column)
  • Keep only city-level corrections
  • Verification: File has correct format, loads in Excel

• **Step 3.2: Simplify City Checker Functions**
  • Update `_parse_mapping_csv()` to read three-column format
  • Update `load_city_mapping()` to return simple dict
  • Update `apply_city_mapping()` to use simple dict
  • Remove `check_city_variations()` function
  • Remove `_detect_variations()` function
  • Verification: Unit tests pass with new format

• **Step 3.3: Update City Checker Tests**
  • Update `tests/test_city_checker.py` to match simplified module
  • Remove tests for variation detection
  • Add tests for new three-column format
  • Verification: All city checker tests pass

---

## Phase 4: School Matcher Module

**Goal:** Implement core school name matching functionality.

• **Step 4.1: Create School Matcher Module Structure**
  • Create `src/tanulmanyi_versenyek/validation/school_matcher.py`
  • Add module-level logger
  • Add imports: rapidfuzz, pandas, pathlib
  • Verification: Module imports successfully

• **Step 4.2: Implement KIR Database Loader**
  • Implement `load_kir_database(config)` function
  • Load Excel file from config path
  • Validate required columns present
  • Raise clear errors if file missing or schema invalid
  • Verification: Unit test with fixture Excel file

• **Step 4.3: Implement School Mapping Loader**
  • Implement `load_school_mapping(config)` function
  • Load CSV with format: `school_name;city;corrected_school_name;comment`
  • Return dict keyed by (school_name, city) tuple
  • Return empty dict if file doesn't exist (graceful)
  • Verification: Unit test with sample mapping file

• **Step 4.4: Implement City Normalization Functions**
  • Implement `normalize_city(city)` - lowercase, strip, remove " kerület"
  • Implement `cities_match(our_city, kir_city)` - exact match + Budapest special case
  • Verification: Unit tests for various city formats

• **Step 4.5: Implement Single School Matcher**
  • Implement `match_school(our_name, our_city, kir_df, manual_mapping, config)` function
  • Check manual mapping first (return immediately if found)
  • Filter KIR candidates by city using `cities_match()`
  • Calculate token_set_ratio for each candidate
  • Return best match if score >= medium threshold
  • Return None if no match or score too low
  • Verification: Unit tests with various scenarios

• **Step 4.6: Implement Batch School Matcher**
  • Implement `match_all_schools(our_df, kir_df, manual_mapping, config)` function
  • Get unique (school_name, city) combinations
  • Call `match_school()` for each
  • Categorize by confidence: MANUAL, AUTO_HIGH, AUTO_MEDIUM, DROPPED
  • Return DataFrame with match results
  • Log statistics
  • Verification: Unit test with sample data

• **Step 4.7: Implement Match Application Function**
  • Implement `apply_matches(our_df, match_results)` function
  • Update iskola_nev with matched names
  • Update varos with normalized KIR cities
  • Add vármegye and régió columns
  • Remove rows with DROPPED status
  • Return new DataFrame
  • Verification: Unit test verifies schema changes

• **Step 4.8: Implement Audit File Generator**
  • Implement `generate_audit_file(match_results, output_path)` function
  • Add comment column based on match_method
  • Sort by match_method, then school_name
  • Save to CSV with semicolon delimiter
  • Verification: Unit test checks file format

• **Step 4.9: Create Test Fixtures**
  • Create `tests/fixtures/kir_sample.xlsx` with ~100 schools
  • Include schools from competition data for realistic testing
  • Create sample `school_mapping.csv` for tests
  • Verification: Fixtures load successfully in tests

• **Step 4.10: Write School Matcher Unit Tests**
  • Create `tests/test_school_matcher.py`
  • Test city normalization functions
  • Test KIR database loading (valid, missing, invalid schema)
  • Test school mapping loading
  • Test matching logic (manual, high-conf, medium-conf, dropped)
  • Test match application and audit generation
  • Verification: All school matcher tests pass

---

## Phase 5: Pipeline Integration

**Goal:** Integrate school matching into step 04 and update data schema.

• **Step 5.1: Add KIR File Validation to Step 04**
  • Add `validate_kir_file_exists(config)` function to `04_merger_and_excel.py`
  • Check if KIR file exists before proceeding
  • Raise FileNotFoundError with clear message if missing
  • Verification: Script fails gracefully when KIR file absent

• **Step 5.2: Update Validation Report Function**
  • Enhance `generate_validation_report()` in `04_merger_and_excel.py`
  • Accept optional `match_results` parameter
  • Add `school_matching` section to JSON output
  • Include statistics: total, manual, auto_high, auto_medium, dropped
  • Verification: JSON output has new section

• **Step 5.3: Integrate School Matching Workflow**
  • Update `main()` in `04_merger_and_excel.py`
  • After merge: apply city corrections
  • Load KIR database and school mappings
  • Call `match_all_schools()`
  • Call `apply_matches()` to update DataFrame
  • Generate audit file
  • Update validation report with match stats
  • Save master CSV with new schema
  • Verification: Manual run produces audit file and updated CSV

• **Step 5.4: Update Master CSV Schema**
  • Verify master CSV has columns: ev, targy, iskola_nev, varos, vármegye, régió, helyezes, evfolyam
  • Note: vármegye created directly (not renamed from megye)
  • Verify city names normalized (no " kerület" suffix)
  • Verification: Inspect master CSV structure

• **Step 5.5: Create Integration Tests**
  • Update `tests/test_integration.py`
  • Test full pipeline with KIR file present
  • Test pipeline fails if KIR file missing
  • Test manual mappings override automatic matches
  • Test dropped schools removed from final output
  • Use config overrides for test thresholds
  • Verification: Integration tests pass

---

## Phase 6: Notebook Enhancements

**Goal:** Add county/region rankings and filters to analysis notebook.

• **Step 6.1: Add Filter Helper Function**
  • Add `apply_filters()` function inline in notebook
  • Support year, grade, city, county, region filters
  • Handle "all", single value, and list of values
  • Verification: Test function with sample data in notebook

• **Step 6.2: Add County Rankings (Count-based)**
  • Add new notebook section after City Rankings
  • Bilingual title: "County Rankings (Count-based)" / "Vármegyék rangsora (darabszám alapján)"
  • Parameters: DISPLAY_TOP_N, YEAR_FILTER, GRADE_FILTER, REGION_FILTER
  • Group by vármegye, count teams
  • Sort by count desc, then name (Hungarian sort)
  • Verification: Run cell, verify output

• **Step 6.3: Add County Rankings (Weighted)**
  • Add new notebook section
  • Bilingual title: "County Rankings (Weighted)" / "Vármegyék rangsora (súlyozott pontszám alapján)"
  • Same parameters as count-based
  • Calculate weighted score: sum of (max_helyezes - helyezes + 1)
  • Sort by score desc, then name
  • Verification: Run cell, verify output

• **Step 6.4: Add Region Rankings (Count-based)**
  • Add new notebook section
  • Bilingual title: "Region Rankings (Count-based)" / "Régiók rangsora (darabszám alapján)"
  • Parameters: DISPLAY_TOP_N, YEAR_FILTER, GRADE_FILTER (no REGION_FILTER)
  • Group by régió, count teams
  • Sort by count desc, then name
  • Verification: Run cell, verify output

• **Step 6.5: Add Region Rankings (Weighted)**
  • Add new notebook section
  • Bilingual title: "Region Rankings (Weighted)" / "Régiók rangsora (súlyozott pontszám alapján)"
  • Same parameters as count-based
  • Calculate weighted score
  • Sort by score desc, then name
  • Verification: Run cell, verify output

• **Step 6.6: Update Existing Rankings with New Filters**
  • Update School Rankings sections to add COUNTY_FILTER and REGION_FILTER parameters
  • Update City Rankings sections to add COUNTY_FILTER and REGION_FILTER parameters
  • Update filter application calls
  • Verification: Run all ranking cells, verify filters work

• **Step 6.7: Update Pandas Display Settings**
  • Wrap all ranking displays with pandas max_rows setting
  • Save original setting, set to DISPLAY_TOP_N, display, restore
  • Apply to all ranking sections
  • Verification: Rankings display correct number of rows

• **Step 6.8: Create Notebook Helper Tests**
  • Update `tests/test_notebook_helpers.py`
  • Add tests for county filter (string, list)
  • Add tests for region filter (string, list)
  • Add tests for combined filters
  • Verification: All notebook helper tests pass

---

## Phase 7: Documentation and Testing

**Goal:** Update documentation and ensure comprehensive test coverage.

• **Step 7.1: Update Main README**
  • Update version to 0.4.0
  • Add step 03 to "Futtatás" section
  • Update step numbers (03 → 04)
  • Mention new vármegye and régió columns
  • Update statistics (schools, cities after cleaning)
  • Mention audit file in "Eredmények" section
  • Verification: README accurate and complete

• **Step 7.2: Update Kaggle README (English)**
  • Update `templates/kaggle/README.en.md`
  • Add vármegye and régió to column descriptions
  • Update example row
  • Describe school matching in "Data Quality" section
  • Update version to 0.4.0, date to 2025-12-28
  • Add "New in 0.4.0" section
  • Verification: README accurate and complete

• **Step 7.3: Update Kaggle README (Hungarian)**
  • Update `templates/kaggle/README.hu.md`
  • Mirror changes from English version
  • Ensure consistent translation
  • Verification: Both language versions aligned

• **Step 7.4: Run Full Test Suite**
  • Run `pytest tests/ -v`
  • Verify all unit tests pass
  • Verify all integration tests pass
  • Check test coverage for new modules
  • Verification: All tests green

• **Step 7.5: Manual End-to-End Test**
  • Clear `data/helper_data/`, `data/kaggle/`, `data/analysis_templates/`
  • Run: `poetry run python 03_download_helper_data.py`
  • Verify KIR file downloaded
  • Run: `poetry run python 04_merger_and_excel.py`
  • Verify audit file generated
  • Verify master CSV has new columns
  • Verify validation report has school_matching section
  • Inspect audit file for reasonable matches
  • Verification: Pipeline runs end-to-end successfully

• **Step 7.6: Test Notebook on Kaggle**
  • Upload updated notebook to Kaggle
  • Attach updated dataset
  • Run all cells
  • Verify county and region rankings display
  • Verify filters work correctly
  • Verification: Notebook runs successfully on Kaggle

• **Step 7.7: Create Release Notes**
  • Document new features in v0.4.0
  • List breaking changes (script renumbering, schema changes)
  • Provide migration guide for users
  • Verification: Release notes clear and complete

---

## Process Notes

• Each step should be completed and verified before moving to the next
• Integration tests use real data where possible (not fabricated)
• Test fixtures committed to git for deterministic testing
• Module-level loggers used throughout (no logger parameters)
• Configuration accessed via `get_config()` function
• All new code follows project coding rules (README-ai-rules.md)
• Fail fast on critical errors (KIR file missing, schema invalid)
• Graceful degradation on optional features (mapping files)
