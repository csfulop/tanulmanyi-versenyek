# **Detailed Design Document: Hungarian Academic Competition Results Pipeline (MVP)**

## **1. Introduction**

### **1.1. Purpose**

This document provides a detailed technical design for the "Hungarian Academic Competition Results Pipeline" project. It translates the requirements specified in `step1-requirements.md` into an actionable blueprint for implementation. The design prioritizes simplicity, maintainability, and robustness for the Minimum Viable Product (MVP).

### **1.2. Scope**

This design covers the three main pipeline stages (Download, Parse, Merge/Report), shared components, data models, error handling, and testing strategy for the Bolyai Mother Tongue Competition MVP.

## **2. High-Level Architecture & Project Structure**

The project will be implemented as a series of three independent Python scripts, which share common logic through a `src/common` module. This approach was chosen for its simplicity and clear separation of concerns, fitting the MVP scope.

The final project structure will be as follows:

```
bolyai_pipeline/
├── 01_raw_downloader.py         # Main script for Stage 1
├── 02_html_parser.py            # Main script for Stage 2
├── 03_merger_and_excel.py       # Main script for Stage 3
├── config.yaml                  # All configuration
├── pyproject.toml               # Poetry dependencies
├── README.md
├── templates/
│   └── report_template.xlsx     # Single Excel template for all reports
├── src/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration loader
│   │   └── logger.py            # Logging setup
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── bolyai_downloader.py # WebsiteDownloader class
│   └── parser/
│       ├── __init__.py
│       └── html_parser.py       # HtmlTableParser class
└── data/                          # Generated output directory (ignored by git)
    ├── raw_html/
    ├── processed_csv/
    ├── analysis_templates/
    ├── master_bolyai_anyanyelv.csv
    ├── validation_report.json
    └── pipeline.log
```

## **3. Common Modules Design (`src/common/`)**

### **3.1. Configuration (`config.py` & `config.yaml`)**

*   **`config.yaml`**: A single YAML file will store all configuration to avoid hardcoded values. It will be structured into logical sections.
    ```yaml
    data_source:
      base_url: "https://magyar.bolyaiverseny.hu/verseny/archivum/eredmenyek.php"
      subject: "Anyanyelv"
      grades: [3, 4, 5, 6, 7, 8]
      rounds: ["írásbeli döntő"] # Final list to be confirmed

    scraping:
      delay_seconds: 5
      timeout_seconds: 30
      max_retries: 3
      headless: True
      user_agent: "Bolyai-Competition-Scraper/1.0"
      selectors:
        year_dropdown: "#verseny_eve"
        grade_dropdown: "#verseny_evfolyam"
        round_dropdown: "#verseny_fordulo"
        results_table: "#middle > table > tbody > tr > td > table" # Example

    paths:
      data_dir: "data"
      raw_html_dir: "data/raw_html"
      processed_csv_dir: "data/processed_csv"
      report_dir: "data/analysis_templates"
      master_csv: "data/master_bolyai_anyanyelv.csv"
      validation_report: "data/validation_report.json"
      log_file: "data/pipeline.log"
      template_file: "templates/report_template.xlsx"
    ```
*   **`src/common/config.py`**:
    *   Will contain a single function: `get_config()`.
    *   This function will use `functools.lru_cache(maxsize=1)` to ensure the YAML file is read from disk and parsed only once.
    *   It will use the `PyYAML` library to parse the file.
    *   It will perform a basic validation check to ensure the top-level keys (`data_source`, `scraping`, `paths`) are present.

### **3.2. Logging (`logger.py`)**

*   **`src/common/logger.py`**:
    *   Will contain a single function: `setup_logging()`.
    *   It will configure Python's built-in `logging` module.
    *   It will set up two handlers: a `StreamHandler` for console output and a `FileHandler` to write to the path specified in `config.paths.log_file`.
    *   Both handlers will use a standard formatter: `%(asctime)s - %(levelname)s - %(name)s - %(message)s`.
    *   The default logging level will be `INFO`.
    *   This function must be called at the beginning of each main script.

## **4. Pipeline Stage Design**

### **4.1. Stage 1: Downloader (`01_raw_downloader.py`)**

*   **Main Script**: Orchestrates the download process. It initializes config and logging, creates the output directory, and runs a triple-nested loop for `year`, `grade`, and `round`. It checks for file existence to ensure idempotency.
*   **`src/scraper/bolyai_downloader.py`**:
    *   Defines a `WebsiteDownloader` class to encapsulate all Playwright logic.
    *   Implements the context manager protocol (`__enter__`/`__exit__`) to guarantee browser shutdown.
    *   **`get_available_years()`**: Returns a list of all years from the website's dropdown.
    *   **`get_html_for_combination(year, grade, round)`**: Selects the three options on the page, waits for content to load, and returns the page's HTML. This method will handle retries, timeouts, and the polite scraping delay.
*   **File Naming**: Output files will be named descriptively: `{subject}_{year}_{grade}_{round_slug}.html`. Example: `anyanyelv_2022-2023_8_irasbeli-donto.html`.

### **4.2. Stage 2: Parser (`02_html_parser.py`)**

*   **Main Script**: Scans the raw HTML directory, checks for corresponding processed CSVs to ensure idempotency, and uses the `HtmlTableParser` for processing.
*   **`src/parser/html_parser.py`**:
    *   Defines an `HtmlTableParser` class.
    *   The core parsing will be done using `pandas.read_html()` for simplicity and efficiency.
    *   **`parse()` method**:
        1.  Parses the filename to extract metadata (`year`, `grade`, `round`).
        2.  Calls `pd.read_html()` using the table selector from the config.
        3.  Performs data cleaning: renames columns, normalizes the `helyezes` column (e.g., "1-3. hely" -> 1), and adds metadata columns.
        4.  Returns a clean pandas DataFrame.
*   **Output**: The script saves the DataFrame to a CSV file (e.g., `anyanyelv_2022-2023_8_irasbeli-donto.csv`) in the processed directory, using UTF-8 encoding and a semicolon delimiter.

### **4.3. Stage 3: Merger & Reporter (`03_merger_and_excel.py`)**

This script will be executed as a single file with three distinct functional steps.

1.  **Merge CSVs**: It will find and concatenate all files from `data/processed_csv/` into a master DataFrame, perform deduplication, and save the result to `data/master_bolyai_anyanyelv.csv`.
2.  **Generate Validation Report**: It will calculate metrics (row count, null percentages) from the master DataFrame and save them to `data/validation_report.json`.
3.  **Generate Excel Report**: It will use the **template-based approach**:
    *   It will copy the single template file `templates/report_template.xlsx` to the final output directory (e.g., as `Bolyai_Analysis_Report.xlsx`).
    *   The template will contain three pre-configured sheets: `Data`, `Top 10 Schools` (Pivot), and `County Rankings` (Pivot).
    *   The script will write the master DataFrame to the `Data` sheet of the newly copied file.

## **5. Testing Strategy**

The testing strategy for the MVP will prioritize integration tests for the most critical and complex components.

*   **Test Data**: A small collection of representative HTML files (e.g., one for a normal year, one for a year with a slightly different format, one for a case with no results) will be saved in a `tests/test_data` directory.
*   **Parser Testing**: An integration test will run the `HtmlTableParser` against these saved HTML files and assert that the output DataFrame has the expected shape, columns, and data types. This is the highest priority test.
*   **Unit Tests**: Simple unit tests will be written for any pure, reusable data cleaning functions (e.g., the function that normalizes the `helyezes` string).
*   **E2E/Downloader Testing**: E2E tests and tests for the live downloader are out of scope for the MVP due to their complexity and potential flakiness. The downloader's robustness will be ensured through extensive logging and manual verification during development.

This design provides a complete and actionable plan for building the MVP pipeline.