# **Software Requirements Specification (SRS): Hungarian Academic Competition Results Pipeline**

## **1. Introduction**

### **1.1. Purpose**

This document specifies the requirements for the **Hungarian Academic Competition Results Pipeline (MVP)**. The purpose of this software is to create an automated data pipeline that scrapes competition results from public sources, processes them into a clean, unified dataset, and generates analytical reports. The initial MVP will focus exclusively on the "Bolyai Anyanyelvi Csapatverseny" (Bolyai Mother Tongue Team Competition) to validate the approach and provide a foundation for future expansion. The primary output will be a master CSV file and pre-configured Microsoft Excel pivot tables for local analysis.

### **1.2. Document Conventions**

*   **FR-XXX:** Denotes a specific Functional Requirement (e.g., FR-001).
*   **NFR-XXX:** Denotes a specific Non-Functional Requirement.
*   **MVP:** Minimum Viable Product. The initial, limited-scope version of the project.
*   **ETL:** Extract, Transform, Load. The process of gathering, cleaning, and storing data.
*   **Polite Scraping:** Scraping practices that minimize server load, such as using delays between requests.
*   **Idempotent:** An operation that produces the same result if executed multiple times.

### **1.3. Intended Audience and Reading Suggestions**

*   **Lead Developer / Coding Agent:** This is the primary audience. This document provides the complete technical specifications needed for implementation. Focus on Section 3, "Specific Requirements."
*   **Project Owner:** Review Sections 1 and 2 to ensure the high-level description and scope align with the project vision.
*   **Future Contributors:** Use this document as a starting point for understanding the architecture and how to extend the system with new data sources or features.

### **1.4. Product Scope**

The scope of this project is strictly limited to the MVP to ensure rapid delivery and validation.

**In Scope:**

*   Data collection from a single source: The Bolyai Mother Tongue Team Competition web archive.
*   A 3-step, command-line-based Python pipeline (Download, Parse, Merge/Report).
*   Processing of all available historical data from the source for the specified competition.
*   Outputting a single, master CSV file containing all processed data.
*   Generating two pre-configured Excel files with pivot tables for analysis.
*   All scripts and data will be stored and run locally on the user's machine.

**Out of Scope:**

*   Any other competitions (e.g., OKTV, Zrínyi Ilona, other Bolyai subjects).
*   A web-based user interface or interactive visualization dashboard.
*   User authentication or accounts.
*   Deployment to a server or public-facing platform (e.g., Kaggle, GitHub Pages).
*   Machine learning analysis or predictive modeling.

### **1.5. References**

1.  **Primary Data Source:** Bolyai Mother Tongue Competition Archives - [https://magyar.bolyaiverseny.hu/verseny/archivum/eredmenyek.php](https://magyar.bolyaiverseny.hu/verseny/archivum/eredmenyek.php)
2.  **Project Conception:** The `chat.txt` log file detailing the project's ideation and refinement.

## **2. Overall Description**

### **2.1. Product Perspective**

The product is a new, standalone, local-first data processing pipeline. It will be executed via a command-line interface (CLI). It is designed to be modular, allowing for future integration with a front-end visualization layer or the addition of other data-sourcing modules.

### **2.2. Product Functions**

The system will perform the following major functions:
1.  **Data Extraction:** Automatically download the raw HTML source files of competition results from the target website, skipping files that have already been downloaded.
2.  **Data Transformation:** Parse the downloaded HTML files to extract structured data (e.g., year, school name, rank) into intermediate CSV files.
3.  **Data Loading & Reporting:** Merge the intermediate CSVs into a single master data file and use this master file to generate Excel spreadsheets containing pre-built pivot tables for analysis.
4.  **Validation:** Perform basic data quality checks and log a summary report.

### **2.3. User Characteristics**

The primary user is the project owner, who is technically proficient with experience in software development and data concepts. They are comfortable running Python scripts from a command line and using Microsoft Excel for data analysis but are not an expert in web scraping or data engineering.

### **2.4. Constraints**

*   **Technical:**
    *   The solution must be implemented in Python 3.11+ using the Poetry dependency management tool.
    *   The pipeline must operate without a backend server or database. All data is to be stored in local files (HTML, CSV, XLSX).
    *   Web scraping must be performed using the Playwright library to handle JavaScript-driven content.
*   **Ethical/Legal:**
    *   Scraping must be "polite," incorporating a delay (configurable, e.g., 5-10 seconds) between HTTP requests to avoid overloading the source server.
    *   The project is for non-commercial, personal use. No personally identifiable information (e.g., student names) shall be stored.
*   **Budgetary:** The solution must be implemented using free and open-source software, with no cloud or hosting costs.

### **2.5. Assumptions and Dependencies**

*   The HTML structure of the source website is assumed to be consistent across different years' result pages. Changes to the website's layout may break the parser.
*   The user's machine has Python 3.11+ and Poetry installed.
*   The user has Microsoft Excel 2016 or newer to properly use the generated pivot tables.
*   The source website's `robots.txt` file does not explicitly forbid scraping its result pages (to be manually verified before development).

## **3. Specific Requirements**

### **3.1. Functional Requirements**

**FR-001: Raw HTML Downloader**
*   **Description:** The system shall have a script (`01_raw_downloader.py`) that browses to the source URL, identifies all available competition years from the dropdown menu, and downloads the full HTML source for each year's results page. The script must be idempotent, checking for the existence of an output file before downloading to avoid redundant requests on subsequent runs.
*   **Priority:** High
*   **Acceptance Criteria:** When the script is run, it saves files named `data/raw_html/anyanyelv_YYYY.html` for each year not already present. The log indicates which years were downloaded and which were skipped.

**FR-002: HTML Parser**
*   **Description:** The system shall have a script (`02_html_parser.py`) that takes a raw HTML file as input and produces a structured CSV file (`data/processed_csv/anyanyelv_YYYY.csv`) as output. It must parse the HTML table to extract the following seven fields: `ev` (year), `targy` (subject), `iskola_nev` (school name), `varos` (city), `megye` (county), `helyezes` (rank), and `evfolyam` (grade).
*   **Priority:** High
*   **Acceptance Criteria:** A processed CSV file is created for each raw HTML file. The CSV has exactly seven columns with the specified headers. Data quality checks show over 95% of cells are populated correctly.

**FR-003: Master CSV Merger**
*   **Description:** The system shall have a script (`03_merger_and_excel.py`) that finds all files in `data/processed_csv/`, merges them into a single master file at `data/master_bolyai_anyanyelv.csv`, and removes duplicate entries. A duplicate is defined as a row with the same combination of `ev`, `evfolyam`, `iskola_nev`, and `helyezes`.
*   **Priority:** High
*   **Acceptance Criteria:** The `master_bolyai_anyanyelv.csv` file is created and contains data from all processed years. The file contains no duplicate rows as per the definition.

**FR-004: Excel Pivot Table Generation**
*   **Description:** The `03_merger_and_excel.py` script shall use the master CSV to generate two Excel files in `data/analysis_templates/`:
    1.  `top10_iskolak.xlsx`: A pivot table configured to show the count of top-10 placements per school per year. (Rows: `iskola_nev`, Columns: `ev`, Values: Count of `helyezes`).
    2.  `megyei_rangsor.xlsx`: A pivot table configured to show the count of top-3 placements (podium finishes) per county per grade. (Rows: `megye`, Columns: `evfolyam`, Values: Count of `helyezes`).
*   **Priority:** High
*   **Acceptance Criteria:** The two XLSX files are created. When opened in Excel, the pivot tables can be refreshed (`Data -> Refresh All`) to reflect the latest data in the master CSV.

**FR-005: Externalized Configuration**
*   **Description:** All hardcoded variables that are likely to change, such as source URLs, HTML element selectors, and scraping delays, must be stored in an external `config.yaml` file. The Python scripts must load their configuration from this file.
*   **Priority:** High
*   **Acceptance Criteria:** Changing the scraping delay in `config.yaml` alters the script's behavior without requiring any code modification.

**FR-006: Validation and Logging**
*   **Description:** Each pipeline step shall log its progress to the console and to a file (`pipeline.log`). After the merge step, a `validation_report.json` file shall be generated, containing key data quality metrics (e.g., total rows, null value percentages per column, number of unique schools).
*   **Priority:** High
*   **Acceptance Criteria:** A `validation_report.json` file is present in the `data/` directory after a successful run, containing metrics like `{"total_rows": 5000, "null_counts": {"megye": 50}}`.

### **3.2. Non-Functional Requirements**

*   **NFR-001 (Performance):** The entire pipeline (all three scripts) shall complete execution in under 5 minutes on a standard developer machine (e.g., 4-core CPU, 8GB RAM). Total disk space usage for the `data` directory should not exceed 100MB for the MVP.
*   **NFR-002 (Usability):** The pipeline must be executable via simple, documented CLI commands (e.g., `poetry run python 01_raw_downloader.py`). A `README.md` file must provide clear, concise setup instructions that can be followed in under 5 minutes.
*   **NFR-003 (Reliability):** All scripts must be idempotent. Network requests must include a retry mechanism (e.g., 3 retries) with a timeout (e.g., 30 seconds) to handle transient network failures.
*   **NFR-004 (Maintainability):** The code must be organized into three distinct, single-responsibility scripts. Code must adhere to PEP 8 style guidelines. The use of a `config.yaml` file is mandatory to separate configuration from logic.
*   **NFR-005 (Portability):** The solution must be cross-platform and run on modern versions of Windows, macOS, and Linux where Python 3.11+ and Poetry can be installed.

### **3.3. External Interface Requirements**

*   **3.3.1. User Interfaces:** The only user interface will be the command line. Scripts should provide feedback during execution, such as progress bars for downloads and logs for processing steps.
*   **3.3.2. Hardware Interfaces:** Not applicable.
*   **3.3.3. Software Interfaces:**
    *   **Python Libraries:** The project will interface with Playwright, Pandas, and OpenPyXL via their respective Python APIs.
    *   **File Formats:** The system will read and write HTML, CSV (UTF-8, semicolon-separated), XLSX, YAML, and JSON files.
*   **3.3.4. Communications Interfaces:** The system will make HTTPS GET requests to the Bolyai competition website. It must use a standard User-Agent string to identify itself as a bot (e.g., `Bolyai-Competition-Scraper/1.0`).

## **4. Appendices**

### **4.1. Glossary**

*   **CSV (Comma-Separated Values):** A text file format for storing tabular data. In this project, it will be semicolon-separated to accommodate decimal commas.
*   **Pivot Table:** An Excel feature that allows data to be summarized and reorganized for analysis.
*   **Poetry:** A dependency management and packaging tool for Python.
*   **Playwright:** A Python library for automating web browser interactions.

### **4.2. Other Supporting Information**

#### **4.2.1. Target Data Schema (for `master_bolyai_anyanyelv.csv`)**

The master CSV file will have the following semicolon-separated columns:

| Header | Data Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `ev` | String | "2022/2023" | The academic year of the competition. |
| `targy` | String | "Anyanyelv" | The subject of the competition, fixed to "Anyanyelv". |
| `iskola_nev`| String | "Budapesti Kölcsey F. Gimnázium" | The name of the school. |
| `varos` | String | "Budapest" | The city where the school is located. |
| `megye` | String | "Pest" | The county where the school is located. |
| `helyezes` | Integer | 1 | The final rank achieved by the team. |
| `evfolyam` | Integer | 8 | The grade of the competing students (3-8). |

**Note on Competition Rounds:**
The competition has two rounds: "Írásbeli döntő" (written finals) and "Szóbeli döntő" (oral finals). The Szóbeli round provides final positions, while the Írásbeli round provides preliminary positions (which become final for teams that don't qualify for the oral round). During COVID-19 pandemic years, the Szóbeli round was skipped, making the Írásbeli positions final for all teams.

#### **4.2.2. Proposed Project Directory Structure**

```
bolyai_pipeline/
├── 01_raw_downloader.py
├── 02_html_parser.py
├── 03_merger_and_excel.py
├── config.yaml
├── pyproject.toml
├── README.md
└── data/
    ├── raw_html/
    │   └── anyanyelv_2022.html
    ├── processed_csv/
    │   └── anyanyelv_2022.csv
    ├── analysis_templates/
    │   ├── top10_iskolak.xlsx
    │   └── megyei_rangsor.xlsx
    ├── master_bolyai_anyanyelv.csv
    └── validation_report.json
```