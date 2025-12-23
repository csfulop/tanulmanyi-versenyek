# Step-by-Step Implementation Breakdown Plan - v0.3.0

## Overview of Phases

This implementation is organized into 5 phases:

1. **Phase 1: City Validation Module Foundation** - Create the validation module structure and core loading logic
2. **Phase 2: City Mapping & Variation Detection** - Implement correction application and variation checking
3. **Phase 3: Pipeline Integration** - Integrate city validation into the merger script
4. **Phase 4: Notebook Enhancements** - Add TOC, city filter, and display settings
5. **Phase 5: Documentation & Final Testing** - Update documentation and perform comprehensive testing

---

## Phase 1: City Validation Module Foundation

**Goal**: Create the validation module structure with city mapping file loading capability.

### Step 1.1: Create Module Structure
- Create `src/tanulmanyi_versenyek/validation/` directory
- Create `__init__.py` (empty or with module docstring)
- Create `city_checker.py` with module-level imports and docstring
- **Verify**: Module can be imported: `from tanulmanyi_versenyek.validation import city_checker`

### Step 1.2: Implement Configuration Update
- Add `validation:` section to `config.yaml` with `city_mapping_file` path
- **Verify**: Config loads without errors, new section accessible

### Step 1.3: Implement Helper Functions
- Implement `_is_valid_entry(comment)` - checks if comment contains "VALID"
- Implement `_parse_mapping_csv(filepath, log)` - reads CSV, returns dictionary keyed by (school_name, original_city)
- Handle UTF-8 encoding, semicolon delimiter
- **Verify**: Unit test with sample CSV file, verify dictionary structure

### Step 1.4: Implement load_city_mapping()
- Implement `load_city_mapping(config, log)` function
- Get file path from config, check existence
- Call `_parse_mapping_csv()` if file exists
- Log INFO with count of loaded mappings, or INFO if file missing
- Return empty dict on any error (with ERROR log)
- **Verify**: Unit tests for success, missing file, malformed CSV cases

### Step 1.5: Create Initial Unit Tests
- Create `tests/test_city_checker.py`
- Write tests for `_is_valid_entry()`, `_parse_mapping_csv()`, `load_city_mapping()`
- Use pytest fixtures for sample CSV data
- **Verify**: All Phase 1 tests pass (`pytest tests/test_city_checker.py -v`)

---

## Phase 2: City Mapping & Variation Detection

**Goal**: Implement city correction application and unmapped variation detection.

### Step 2.1: Implement apply_city_mapping()
- Implement `apply_city_mapping(df, mapping, log)` function
- Iterate DataFrame rows, check (school_name, city) against mapping
- Skip if is_valid=True, apply corrected_city otherwise
- Log DEBUG for each correction, INFO for total count
- Return tuple: (corrected_df, corrections_count)
- **Verify**: Unit test with sample DataFrame, verify corrections applied and count accurate

### Step 2.2: Implement _detect_variations()
- Implement `_detect_variations(df)` private function
- Group by school_name, count unique cities
- Return dict of schools with 2+ cities and their city lists
- **Verify**: Unit test with sample data containing variations

### Step 2.3: Implement check_city_variations()
- Implement `check_city_variations(df, mapping, log)` function
- Call `_detect_variations()` to find schools with multiple cities
- For each variation, check if (school, city) in mapping or if city matches corrected_city
- Log WARNING for unmapped combinations (format: `Unmapped combination: school="...", city="..."`)
- Log INFO with summary statistics, DEBUG with details
- Return statistics dict (corrections_applied, valid_variations, unmapped_variations)
- **Verify**: Unit tests for all-mapped, partially-mapped, all-valid scenarios

### Step 2.4: Expand Unit Test Coverage
- Add tests for composite key handling (same school, different cities)
- Add tests for VALID entries (should not change)
- Add edge cases (empty DataFrame, no variations, etc.)
- **Verify**: All Phase 2 tests pass, coverage includes all branches

---

## Phase 3: Pipeline Integration

**Goal**: Integrate city validation into the merger script and update validation report.

### Step 3.1: Implement Standalone Execution
- Implement `main()` function in `city_checker.py`
- Setup logging, load config, load master CSV
- Call `load_city_mapping()` and `check_city_variations()`
- Add `if __name__ == "__main__":` block
- **Verify**: Run `python -m tanulmanyi_versenyek.validation.city_checker`, check logs

### Step 3.2: Update Merger Script
- Import city validation functions in `03_merger_and_excel.py`
- After merge, before validation report: call `load_city_mapping()`, `apply_city_mapping()`, `check_city_variations()`
- Pass city_stats to `generate_validation_report()`
- **Verify**: Run merger script, check logs for city mapping messages

### Step 3.3: Update Validation Report
- Modify `generate_validation_report()` signature in `data_merger.py` to accept `city_stats` parameter
- Add `city_mapping` section to report JSON if city_stats provided
- Include corrections_applied, valid_variations, unmapped_variations
- **Verify**: Run full pipeline, check `validation_report.json` contains city_mapping section

### Step 3.4: Create Example Mapping File
- Create `config/city_mapping.csv` with example entries from requirements
- Include all 22 entries (9 corrections + 13 VALID)
- **Verify**: Run pipeline with mapping file, verify corrections in master CSV

### Step 3.5: Integration Testing
- Test full pipeline with mapping file (verify corrections applied)
- Test full pipeline without mapping file (verify graceful handling)
- Test with malformed mapping file (verify error handling)
- **Verify**: All integration scenarios work, no breaking changes

---

## Phase 4: Notebook Enhancements

**Goal**: Add Table of Contents, city filter, and pandas display settings to the notebook.

### Step 4.1: Add Table of Contents
- Insert warning cell (markdown) before TOC with setup instructions (bilingual)
- Insert TOC cell (markdown) with grouped structure (Setup / Analysis)
- Use dual links format: `[English](#link) / [Magyar](#link)`
- **Verify**: Open notebook, click all links, verify navigation works

### Step 4.2: Add City Filter to School Rankings
- Add `CITY_FILTER = "all"` parameter to School Rankings (Count-based) section
- Add filter logic before ranking calculation (handle "all", string, list)
- Add bilingual documentation explaining the parameter
- Repeat for School Rankings (Weighted) section
- **Verify**: Test with "all", single city, list of cities; verify filtering works

### Step 4.3: Add Pandas Display Settings
- Wrap display calls in School Rankings (Count-based) with save/set/restore pattern
- Set `pd.options.display.max_rows = DISPLAY_TOP_N`
- Repeat for School Rankings (Weighted), City Rankings (Count-based), City Rankings (Weighted)
- For School Search: set to `None` (unlimited)
- **Verify**: Set DISPLAY_TOP_N=20, verify full 20 rows display (not 10)

### Step 4.4: Test Notebook Locally
- Run notebook with Poetry: `./run_notebook_with_poetry.sh`
- Execute all cells in order
- Test different parameter combinations (filters, DISPLAY_TOP_N values)
- **Verify**: No errors, all outputs correct, TOC links work

### Step 4.5: Test Notebook on Kaggle
- Upload updated notebook to Kaggle
- Attach dataset, run all cells
- Verify TOC, filters, display settings work identically
- **Verify**: Notebook runs successfully on Kaggle platform

---

## Phase 5: Documentation & Final Testing

**Goal**: Update documentation and perform comprehensive testing.

### Step 5.1: Update Kaggle Dataset READMEs
- Add "Data Cleaning Process" section to `templates/kaggle/README.en.md` (before limitations)
- Add "Adatminőség-javítási folyamat" section to `templates/kaggle/README.hu.md`
- Update "Known Data Quality Limitations" sections in both files
- **Verify**: Review both READMEs for clarity and completeness

### Step 5.2: Run Full Pipeline
- Execute 01, 02, 03 scripts in sequence with mapping file
- Verify city corrections in `data/kaggle/master_bolyai_anyanyelv.csv`
- Verify corrections in Excel report
- Verify validation report statistics
- **Verify**: All outputs reflect cleaned city names

### Step 5.3: Comprehensive Testing
- Run all unit tests: `pytest tests/ -v`
- Run standalone city checker: `python -m tanulmanyi_versenyek.validation.city_checker`
- Test notebook locally and on Kaggle
- Verify no breaking changes to existing functionality
- **Verify**: All tests pass, no regressions

### Step 5.4: Manual Validation Checklist
- Review acceptance criteria from requirements (sections 7.1, 7.2, 7.3)
- Check each item systematically
- Document any deviations or issues
- **Verify**: All acceptance criteria met

### Step 5.5: Final Review
- Review all code changes for clean code principles
- Check logging levels (DEBUG, INFO, WARNING, ERROR) are appropriate
- Verify error handling is graceful
- Ensure documentation is complete and accurate
- **Verify**: Code ready for production use

---

## Notes

- **Testing Philosophy**: Test after each phase, not just at the end
- **Incremental Progress**: Each step builds on previous work, no orphaned code
- **Error Handling**: All functions handle errors gracefully, log appropriately
- **Backward Compatibility**: System works without mapping file (optional feature)
- **Code Style**: Follow project conventions in `README-ai-rules.md`

---

**Document Version:** 1.0  
**Date:** 2025-12-23  
**Status:** Final  
**Ready for Implementation**
