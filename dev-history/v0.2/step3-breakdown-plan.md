# **Step-by-Step Implementation Breakdown Plan - v0.2.0**

This document provides a detailed, step-by-step implementation plan based on the `step1-requirements.md` and `step2-design.md` documents for v0.2.0. The plan is broken down into five phases, with each phase further divided into granular, actionable steps designed for incremental progress, early testing, and a robust implementation.

## **Overview of Phases**

1. **Phase 1: Project Setup & Infrastructure.** Set up the notebook directory structure, Docker execution script, and test infrastructure.
2. **Phase 2: Helper Functions Implementation.** Build and test all helper functions (filtering, ranking, search) using a test-first approach.
3. **Phase 3: Notebook Implementation.** Create the Jupyter notebook with all analysis sections, using the tested helper functions.
4. **Phase 4: Documentation Updates.** Update README files and Kaggle dataset documentation to reflect the new notebook component.
5. **Phase 5: Validation & Testing.** Perform end-to-end testing both locally (Docker) and on Kaggle platform.

---

## **Phase 1: Project Setup & Infrastructure**

**Goal:** Establish the directory structure and execution infrastructure for the notebook component.

* **Step 1.1: Create Directory Structure.**
  * Create `notebooks/` directory in project root.
  * Create `notebooks/README.md` placeholder file.
  * Create `run_notebook_locally.sh` script in project root.
  * Make the script executable: `chmod +x run_notebook_locally.sh`
* **Step 1.2: Implement Docker Execution Script.**
  * Implement `run_notebook_locally.sh` to run Jupyter using Kaggle's Docker image.
  * Configure volume mounts: `data/kaggle/` → `/kaggle/input/tanulmanyi-versenyek/` and `notebooks/` → `/kaggle/working/`.
  * Configure Jupyter to run on port 8888 without authentication for local development.
* **Step 1.3: Create Test File Structure.**
  * Create `tests/test_notebook_helpers.py`.
  * Add imports: `pytest`, `pandas`, `numpy`.
  * Create a `sample_df` fixture with representative test data (5-10 rows covering different years, grades, schools, cities).
* **Step 1.4: Verify Infrastructure.**
  * Run `./run_notebook_locally.sh` to verify Docker script works (will pull image on first run).
  * Access Jupyter at `http://localhost:8888` and verify the `notebooks/` directory is visible.
  * Run `poetry run pytest tests/test_notebook_helpers.py` to verify test file is valid (should pass with no tests yet).

---

## **Phase 2: Helper Functions Implementation**

**Goal:** Implement and test all helper functions that will be used in the notebook, following a test-first approach.

* **Step 2.1: Implement `filter_data()` Function.**
  * Write unit tests in `tests/test_notebook_helpers.py` for `filter_data()` covering:
    * Filtering by single grade, multiple grades, and "all".
    * Filtering by single year, multiple years, and "all".
    * Combined grade and year filtering.
    * Invalid grade/year validation with appropriate error messages.
  * Implement `filter_data(df, grade_filter, year_filter)` function in the test file.
  * Run tests and verify all pass: `poetry run pytest tests/test_notebook_helpers.py::test_filter_data -v`
* **Step 2.2: Implement `calculate_count_ranking()` Function.**
  * Write unit tests for `calculate_count_ranking()` covering:
    * Grouping by school or city.
    * Correct counting of appearances.
    * Proper sorting (descending by count).
    * Top-N limiting functionality.
  * Implement `calculate_count_ranking(df, group_by, top_n)` function.
  * Run tests and verify all pass.
* **Step 2.3: Implement `calculate_weighted_ranking()` Function.**
  * Write unit tests for `calculate_weighted_ranking()` covering:
    * Correct weighted score calculation (1st place = 10 points, 2nd = 7, 3rd = 5, 4-6th = 3, 7-10th = 1).
    * Grouping by school or city.
    * Proper sorting (descending by weighted score).
    * Top-N limiting functionality.
  * Implement `calculate_weighted_ranking(df, group_by, top_n)` function.
  * Run tests and verify all pass.
* **Step 2.4: Implement `search_school()` Function.**
  * Write unit tests for `search_school()` covering:
    * Case-insensitive partial matching.
    * Handling of no matches (return empty DataFrame).
    * Handling of multiple matches (return all).
    * Proper sorting of results (by year descending, then grade descending).
  * Implement `search_school(df, school_name_pattern)` function.
  * Run tests and verify all pass.
* **Step 2.5: Implement `format_table()` Function.**
  * Write unit tests for `format_table()` covering:
    * Column renaming based on language parameter.
    * Proper styling (header background, borders, alignment).
    * Handling of empty DataFrames.
  * Implement `format_table(df, column_map, title)` function.
  * Run tests and verify all pass.
* **Step 2.6: Run Full Test Suite.**
  * Run all tests: `poetry run pytest tests/test_notebook_helpers.py -v`
  * Verify 100% pass rate before proceeding to notebook implementation.

---

## **Phase 3: Notebook Implementation**

**Goal:** Create the Jupyter notebook with all analysis sections, using the tested helper functions.

* **Step 3.1: Create Notebook Skeleton.**
  * Create `notebooks/competition_analysis.ipynb`.
  * Add title cell: "Bolyai Anyanyelvi Csapatverseny - Eredményelemzés / Competition Results Analysis"
  * Add introduction cells in both Hungarian and English explaining the notebook's purpose.
* **Step 3.2: Implement Imports & Configuration Section.**
  * Add cell with imports: `pandas`, `numpy`, `IPython.display`.
  * Add cell defining Kaggle file path constant: `DATASET_PATH = "/kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv"`
  * Add cell with configuration constants (e.g., default top-N values, language settings).
* **Step 3.3: Implement Data Loading Section.**
  * Add cell to load CSV file using pandas with proper encoding and delimiter.
  * Add cell to display basic dataset info: shape, columns, data types.
  * Add cell to display first few rows as a preview.
* **Step 3.4: Implement Dataset Overview Section.**
  * Add cells (HU + EN) explaining the dataset structure and coverage.
  * Add cell displaying summary statistics: total records, year range, grade distribution, unique schools, unique cities.
* **Step 3.5: Implement Helper Functions Section.**
  * Copy all tested helper functions from `tests/test_notebook_helpers.py` into a single code cell.
  * Add markdown cells (HU + EN) explaining what each helper function does.
* **Step 3.6: Implement School Rankings (Count-based) Section.**
  * Add markdown cells (HU + EN) explaining count-based ranking methodology.
  * Add cell with configuration parameters: `grade_filter`, `year_filter`, `top_n`.
  * Add cell calling `filter_data()` and `calculate_count_ranking()`.
  * Add cell calling `format_table()` to display results in Hungarian.
  * Add cell calling `format_table()` to display results in English.
* **Step 3.7: Implement School Rankings (Weighted) Section.**
  * Add markdown cells (HU + EN) explaining weighted ranking methodology and scoring system.
  * Add cell with configuration parameters (same as count-based).
  * Add cell calling `filter_data()` and `calculate_weighted_ranking()`.
  * Add cell calling `format_table()` to display results in both languages.
* **Step 3.8: Implement City Rankings (Count-based) Section.**
  * Add markdown cells (HU + EN) explaining city-level count-based ranking.
  * Add cell with configuration parameters.
  * Add cell calling `filter_data()` and `calculate_count_ranking(group_by='varos')`.
  * Add cell calling `format_table()` to display results in both languages.
* **Step 3.9: Implement City Rankings (Weighted) Section.**
  * Add markdown cells (HU + EN) explaining city-level weighted ranking.
  * Add cell with configuration parameters.
  * Add cell calling `filter_data()` and `calculate_weighted_ranking(group_by='varos')`.
  * Add cell calling `format_table()` to display results in both languages.
* **Step 3.10: Implement School Search Section.**
  * Add markdown cells (HU + EN) explaining school search functionality.
  * Add cell with search parameter: `school_name_pattern`.
  * Add cell calling `search_school()`.
  * Add cell calling `format_table()` to display search results in both languages.
  * Add cell with example searches and expected results.
* **Step 3.11: Add Conclusion Section.**
  * Add markdown cells (HU + EN) summarizing the notebook's capabilities.
  * Add cell with links to dataset, GitHub repository, and future roadmap.

---

## **Phase 4: Documentation Updates**

**Goal:** Update all relevant documentation to reflect the new notebook component.

* **Step 4.1: Update Main README.md.**
  * Add new "Notebooks" section after "Hogyan használd?" section.
  * Explain the purpose of the analysis notebook.
  * Provide instructions for running the notebook locally using Docker: `./run_notebook_locally.sh`
  * Provide link to the notebook on Kaggle (placeholder for now, to be updated after upload).
* **Step 4.2: Update notebooks/README.md.**
  * Add comprehensive documentation for the notebook directory.
  * Explain the notebook's purpose, features, and usage.
  * Document the Docker execution script and its configuration.
  * Provide troubleshooting tips for common issues.
* **Step 4.3: Update Kaggle Dataset Documentation.**
  * Update `templates/kaggle/README.hu.md` to mention the analysis notebook.
  * Update `templates/kaggle/README.en.md` to mention the analysis notebook.
  * Add a brief description and link to the notebook (to be updated after Kaggle upload).
* **Step 4.4: Update Version Information.**
  * Update `pyproject.toml` version to `0.2.0`.
  * Update main README.md "Verzió" section to reflect v0.2.0 and its features.

---

## **Phase 5: Validation & Testing**

**Goal:** Perform comprehensive end-to-end testing to ensure the notebook works correctly in all environments.

* **Step 5.1: Local Docker Testing.**
  * Run `./run_notebook_locally.sh` to start Jupyter in Docker.
  * Open the notebook in the browser.
  * Execute all cells in sequence ("Run All").
  * Verify all outputs are correct and properly formatted.
  * Test with different parameter configurations (different grades, years, top-N values).
  * Verify error handling by intentionally providing invalid inputs.
* **Step 5.2: Kaggle Platform Testing.**
  * Upload the notebook to Kaggle as a new notebook.
  * Attach the `master_bolyai_anyanyelv.csv` dataset to the notebook.
  * Verify the file path (`/kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv`) is correct.
  * Execute all cells in sequence on Kaggle.
  * Verify all outputs match the local Docker execution.
  * Test with different parameter configurations on Kaggle.
* **Step 5.3: Cross-Reference Validation.**
  * Compare notebook outputs with the Excel report from v0.1 (`data/analysis_templates/Bolyai_Analysis_Report.xlsx`).
  * Verify that school rankings match between the notebook and Excel pivot tables.
  * Verify that city rankings match between the notebook and Excel pivot tables.
  * Document any discrepancies and investigate root causes.
* **Step 5.4: Documentation Review.**
  * Review all updated documentation for accuracy and completeness.
  * Verify all links work correctly.
  * Verify all code examples in documentation are correct.
  * Check for typos and formatting issues.
* **Step 5.5: Final Integration Test.**
  * Run the full v0.1 pipeline: `01_raw_downloader.py`, `02_html_parser.py`, `03_merger_and_excel.py`.
  * Copy the generated `data/kaggle/master_bolyai_anyanyelv.csv` to a test location.
  * Run the notebook using this freshly generated CSV.
  * Verify the notebook works correctly with the latest data.
  * **Verification:** Confirm that the notebook produces correct, formatted outputs for all analysis sections and handles edge cases gracefully.

This completes the detailed, step-by-step implementation plan for v0.2.0.
