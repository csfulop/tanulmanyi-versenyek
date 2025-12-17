# **Step-by-Step Implementation Breakdown Plan**

This document provides a detailed, step-by-step implementation plan based on the `step1-requirements.md` and `step2-design.md` documents. The plan is broken down into four phases, with each phase further divided into granular, actionable steps designed for incremental progress, early testing, and a robust implementation.

## **Overview of Phases**

1.  **Phase 1: Project Scaffolding & Core Services.** Set up the project environment, directory structure, and implement the shared `config` and `logging` modules. This is the foundational layer.
2.  **Phase 2: Implement the Downloader.** Build and test the first pipeline stage (`01_raw_downloader.py` and its helper class), resulting in raw HTML files.
3.  **Phase 3: Implement the Parser.** Build and test the second pipeline stage (`02_html_parser.py` and its helper class), which consumes the raw HTML and produces clean, intermediate CSV files.
4.  **Phase 4: Implement the Merger & Reporter.** Build and test the final stage (`03_merger_and_excel.py`), which consumes the intermediate CSVs and produces the final master dataset and Excel report.

---

## **Phase 1: Project Scaffolding & Core Services**

**Goal:** Establish a runnable project environment with functional, tested configuration and logging modules.

*   **Step 1.1: Initialize Project Environment.**
    *   Initialize the Poetry project: `poetry init`
    *   Add primary dependencies: `poetry add pyyaml playwright pandas openpyxl`
    *   Add development dependencies: `poetry add pytest --group dev`
*   **Step 1.2: Create Directory & File Structure.**
    *   Create directories: `src/common`, `src/scraper`, `src/parser`, `data/`, `templates/`, `tests/`.
    *   Create empty `__init__.py` files in `src/common`, `src/scraper`, `src/parser` to make them Python modules.
*   **Step 1.3: Implement Configuration Module.**
    *   Create `config.yaml` with the structure defined in `step2-design.md`, using placeholder values for selectors and paths.
    *   Implement `src/common/config.py` with the `get_config()` function, utilizing `@functools.lru_cache` for efficient loading.
*   **Step 1.4: Test Configuration Module.**
    *   Create `tests/test_config.py`.
    *   Write a unit test to call `src.common.config.get_config()` and assert that it returns a dictionary, and that a known key (e.g., `data_source`) exists.
*   **Step 1.5: Implement Logging Module.**
    *   Implement `src/common/logger.py` with the `setup_logging()` function, configuring console and file handlers with the specified format and default INFO level.
*   **Step 1.6: Create Main Script Skeletons.**
    *   Create `01_raw_downloader.py`, `02_html_parser.py`, and `03_merger_and_excel.py`.
    *   In each script, add the `if __name__ == "__main__":` block to call `src.common.config.get_config()` and `src.common.logger.setup_logging()`, and log a simple "Script starting..." message.
    *   **Verification:** Run each script (`poetry run python 01_raw_downloader.py`, etc.) to confirm correct setup of logging and config loading. Check console output and `data/pipeline.log`.

---

## **Phase 2: Implement the Downloader**

**Goal:** Create a functional, tested downloader that collects raw HTML files from the specified website.

*   **Step 2.1: Manual Data Gathering for Testing.**
    *   Manually save the HTML content of the Bolyai competition main archive page (the one with dropdowns) to `tests/test_data/sample_archive_page.html`. This will be used for local testing of dropdown parsing.
*   **Step 2.2: Implement `WebsiteDownloader` Skeleton.**
    *   Create `src/scraper/bolyai_downloader.py`.
    *   Implement the `WebsiteDownloader` class with `__init__`, `__enter__`, and `__exit__` methods for Playwright browser lifecycle management. It should accept `config` and `logger` objects.
*   **Step 2.3: Implement and Test `get_available_years`.**
    *   Implement the `get_available_years` method within `WebsiteDownloader`. It should be able to process either live URL content or a local HTML string (for testing).
    *   Create `tests/test_downloader.py`.
    *   Write an integration test that reads `tests/test_data/sample_archive_page.html`, passes its content (or path) to `get_available_years`, and asserts that the method correctly extracts a list of year strings.
*   **Step 2.4: Implement `get_html_for_combination`.**
    *   Implement the `get_html_for_combination(year, grade, round)` method within `WebsiteDownloader`. This method will handle live navigation, dropdown selections, page waiting, retries, and the polite delay as specified in `config.yaml`. Update `config.yaml` with the `scraping.selectors` for the dropdowns.
*   **Step 2.5: Integrate into `01_raw_downloader.py`.**
    *   Flesh out the `main()` function in `01_raw_downloader.py`.
    *   Add logic to ensure `config.paths.raw_html_dir` exists.
    *   Use `WebsiteDownloader` within a `with` statement.
    *   Implement the triple-nested loop (years, grades, rounds), checking for existing files before attempting to download and save the HTML using the descriptive file naming convention (`{subject}_{year}_{grade}_{round_slug}.html`).
*   **Step 2.6: Manual End-to-End Test.**
    *   Clear `data/raw_html/`.
    *   Run `poetry run python 01_raw_downloader.py`.
    *   **Verification:** Confirm that HTML files are downloaded, named correctly, and the script respects delays and logs progress.

---

## **Phase 3: Implement the Parser**

**Goal:** Convert raw HTML files into clean, structured intermediate CSV files.

*   **Step 3.1: Implement `HtmlTableParser` Skeleton.**
    *   Create `src/parser/html_parser.py`.
    *   Implement the `HtmlTableParser` class with an `__init__` method accepting the path to an HTML file, `config`, and `logger`.
*   **Step 3.2: Implement and Unit Test Filename Parsing.**
    *   Add a private method, `_parse_metadata_from_filename(filename_str)`, to `HtmlTableParser` to extract `year`, `grade`, `round` from the descriptive HTML filenames.
    *   In `tests/test_parser.py`, write a unit test for this method to ensure accurate metadata extraction from various filename formats.
*   **Step 3.3: Implement Core HTML Table Parsing.**
    *   Implement the `parse()` method within `HtmlTableParser`.
    *   Inside `parse()`, read the HTML file content.
    *   Use `pandas.read_html()` with the table selector from `config.yaml` to extract the main data table into a DataFrame.
*   **Step 3.4: Implement Data Cleaning and Transformation.**
    *   Within the `parse()` method, add steps to:
        *   Rename columns based on `config.yaml` mappings to match the target schema.
        *   Normalize the `helyezes` column (e.g., convert "1-3. hely" to `1`).
        *   Add metadata columns (`ev`, `evfolyam`, `fordulo`, `targy`) derived from filename parsing and config.
        *   Clean string columns (e.g., strip whitespace).
*   **Step 3.5: Write Main Parser Integration Test.**
    *   In `tests/test_parser.py`, write an integration test.
    *   It should instantiate `HtmlTableParser` with `tests/test_data/sample_archive_page.html`.
    *   Call `parse()` and assert the returned DataFrame's structure (column names, data types), that metadata is present, and that `helyezes` is numeric.
*   **Step 3.6: Integrate into `02_html_parser.py`.**
    *   Flesh out the `main()` function in `02_html_parser.py`.
    *   Implement logic to scan `data/raw_html/`, check for existing CSVs in `data/processed_csv/` for idempotency.
    *   For each new HTML file, instantiate `HtmlTableParser`, call `parse()`, and save the resulting DataFrame to a new CSV file (e.g., `anyanyelv_2022-2023_8_irasbeli-donto.csv`) in `data/processed_csv/`, using semicolon delimiters and UTF-8 encoding.
*   **Step 3.7: Manual End-to-End Test.**
    *   Run `poetry run python 02_html_parser.py` (ensure `data/raw_html` is populated from Phase 2).
    *   **Verification:** Confirm that CSV files are created in `data/processed_csv/` and manually inspect their content and structure.

---

## **Phase 4: Implement the Merger & Reporter**

**Goal:** Aggregate processed data, generate a validation report, and create the final, templated Excel report.

*   **Step 4.1: Manual Excel Template Creation.**
    *   Manually create `templates/report_template.xlsx`.
    *   It must contain three sheets: `Data`, `Top 10 Schools`, and `County Rankings`.
    *   Pre-configure the pivot tables on the "Top 10 Schools" and "County Rankings" sheets to source data from the `Data` sheet.
*   **Step 4.2: Implement CSV Merging and Deduplication.**
    *   In `03_merger_and_excel.py`, implement a function (e.g., `merge_processed_data()`) to:
        *   Scan `data/processed_csv/` for all CSV files.
        *   Load them into a list of pandas DataFrames and concatenate them.
        *   Perform deduplication based on (`ev`, `evfolyam`, `iskola_nev`, `helyezes`).
        *   Save the final master DataFrame to `data/master_bolyai_anyanyelv.csv`.
*   **Step 4.3: Implement Validation Report Generation.**
    *   Implement a function (e.g., `generate_validation_report(df)`) that takes the master DataFrame, calculates metrics (total rows, null percentages per column, unique school count), and saves them to `data/validation_report.json` as a JSON object.
*   **Step 4.4: Write Integration Test for Merging.**
    *   Create `tests/test_merger.py` (if not already existing from Phase 3).
    *   Create a few small, sample CSV files in `tests/test_data/sample_processed_csvs/` (including one with a duplicate row).
    *   Write an integration test that calls `merge_processed_data()` on these samples and asserts that the resulting master DataFrame has the correct number of rows and unique entries after deduplication.
*   **Step 4.5: Implement Excel Report Generation.**
    *   Implement a function (e.g., `generate_excel_report(df)`) that:
        *   Copies `templates/report_template.xlsx` to `data/analysis_templates/Bolyai_Analysis_Report.xlsx`.
        *   Uses `pandas.ExcelWriter` (or `openpyxl`) to write the master DataFrame to the `Data` sheet of the copied Excel file.
*   **Step 4.6: Integrate into `03_merger_and_excel.py`.**
    *   Flesh out the `main()` function in `03_merger_and_excel.py` to call `merge_processed_data()`, `generate_validation_report()`, and `generate_excel_report()` in sequence.
*   **Step 4.7: Full Pipeline End-to-End Manual Test.**
    *   Run all scripts in sequence: `poetry run python 01_raw_downloader.py`, `poetry run python 02_html_parser.py`, `poetry run python 03_merger_and_excel.py`.
    *   **Verification:**
        *   Confirm `data/master_bolyai_anyanyelv.csv` is created.
        *   Confirm `data/validation_report.json` is created and contains reasonable metrics.
        *   Confirm `data/analysis_templates/Bolyai_Analysis_Report.xlsx` is created.
        *   Open the Excel report, go to the `Data` tab, click "Refresh All", and verify that both pivot tables (`Top 10 Schools`, `County Rankings`) update correctly with the full dataset.

This completes the detailed, step-by-step implementation plan for the project.