# Software Requirements Specification (SRS): Bolyai Competition Analysis Notebook - v0.2.0

## 1. Introduction

### 1.1. Purpose

This document specifies the requirements for **version 0.2.0** of the Hungarian Academic Competition Results Pipeline project. This release expands the project horizontally into the visualization layer by adding a **Jupyter notebook for interactive data exploration**. The notebook will serve as an intermediate step between the raw data pipeline (v0.1) and a future web-based visualization dashboard, providing a technical playground for data exploration while being shareable on the Kaggle platform.

### 1.2. Document Conventions

- **FR-XXX:** Denotes a specific Functional Requirement
- **NFR-XXX:** Denotes a specific Non-Functional Requirement
- **MVP:** Minimum Viable Product - keeping features simple and focused for initial release
- **Kaggle-native:** Designed primarily for execution on the Kaggle platform

### 1.3. Intended Audience

- **Lead Developer / Coding Agent:** Primary audience for implementation
- **Project Owner:** For validation of requirements
- **Technical Users:** Data analysts and researchers who will use the notebook on Kaggle or locally
- **Future Contributors:** Understanding the analysis layer architecture

### 1.4. Product Scope

**In Scope for v0.2.0:**

- Single Jupyter notebook for data exploration and analysis
- Three core analytical features: school rankings, city rankings, and school search
- Dual language support (Hungarian and English)
- Kaggle-native implementation with dual local execution support (Poetry and Docker)
- Manual parameter configuration (no interactive widgets in MVP)
- Table-based output (no charts in MVP)

**Out of Scope for v0.2.0:**

- Interactive widgets (ipywidgets) - future enhancement
- Chart visualizations (Plotly/Matplotlib) - future enhancement
- Web-based dashboard - future version
- Additional competitions beyond Bolyai Anyanyelv
- Automated integration with the data pipeline
- Advanced statistical analysis or machine learning

### 1.5. References

1. **v0.1.0 Documentation:** `dev-history/v0.1/` - Previous version's requirements and design
2. **Dataset:** `data/kaggle/master_bolyai_anyanyelv.csv` - 3,233 competition results
3. **Kaggle Platform:** https://www.kaggle.com/
4. **Kaggle Docker Image:** https://github.com/kaggle/docker-python (optional, 20GB)

## 2. Overall Description

### 2.1. Product Perspective

The Jupyter notebook is a new component that sits on top of the existing data pipeline (v0.1). It consumes the master CSV file produced by the pipeline and provides an interactive exploration environment. The notebook is designed to be:

- **Kaggle-native:** Primary execution environment is Kaggle's notebook platform
- **Locally executable:** Can be run using Poetry (recommended) or Kaggle's Docker image (optional)
- **Standalone:** Independent from the data pipeline scripts, manually uploaded to Kaggle
- **Educational:** Serves as both an analysis tool and a template for users to learn from

### 2.2. Product Functions

The notebook will provide three core analytical functions:

1. **School Rankings**
   - Display top-performing schools based on competition results
   - Two ranking methods: count-based and weighted score
   - Filterable by grade level, year range, and top-X threshold

2. **City Rankings**
   - Display top-performing cities based on their schools' results
   - Two ranking methods: count-based and weighted score
   - Same filtering capabilities as school rankings

3. **School Search**
   - Search for specific schools using partial name matching
   - Display complete competition history for matched school(s)
   - Handle multiple matches gracefully

### 2.3. User Characteristics

**Primary Users:**
- Data analysts and researchers interested in Hungarian education
- Kaggle community members exploring the dataset
- Project owner and contributors for data validation and exploration

**Technical Level:**
- Comfortable with Jupyter notebooks
- Basic Python and Pandas knowledge
- Can edit variables and re-run cells
- May or may not speak Hungarian (hence dual language support)

### 2.4. Constraints

**Technical Constraints:**
- Must work in Kaggle's Python environment
- Must use libraries available in Kaggle's standard image (and in project's Poetry dependencies)
- File paths must be Kaggle-compatible (`/kaggle/input/...`) with fallback for local paths
- No external API calls or internet dependencies during execution

**Design Constraints:**
- Dual language (Hungarian/English) for all explanatory text
- Keep code simple and readable for educational purposes
- Manual parameter editing (no interactive widgets in MVP)
- Table-based output only (no charts in MVP)

**Operational Constraints:**
- Notebook is manually uploaded to Kaggle (not automated)
- Local execution requires either Poetry environment or Docker installation (user's choice)
- Dataset must be pre-attached in Kaggle environment

### 2.5. Assumptions and Dependencies

**Assumptions:**
- The master CSV file (`master_bolyai_anyanyelv.csv`) exists and follows the v0.1 schema
- Users have basic familiarity with Jupyter notebooks
- Kaggle platform maintains backward compatibility with current Docker image
- Dataset is already uploaded to Kaggle and attached to the notebook

**Dependencies:**
- Python 3.11+ with Poetry (for local development)
- Kaggle Python Docker image (kaggle/python) - optional, 20GB
- Python libraries: pandas, jupyter, IPython (already in Poetry dependencies)
- Master CSV file from v0.1 pipeline

## 3. Specific Requirements

### 3.1. Functional Requirements

#### FR-001: Notebook Structure and Organization

**Description:** The notebook shall be organized into clearly defined sections with dual language support.

**Structure:**
1. **Introduction Section**
   - Hungarian explanation cell
   - English explanation cell
   - Link to dataset README on Kaggle
   - Code cell: imports and configuration

2. **Data Loading Section**
   - Hungarian explanation cell
   - English explanation cell
   - Code cell: load CSV from `/kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv`
   - Code cell: display dataset overview statistics

3. **Helper Functions Section**
   - Hungarian explanation cell
   - English explanation cell
   - Code cell: define all helper functions

4. **School Rankings Section**
   - Hungarian explanation cell
   - English explanation cell
   - Code cell: count-based ranking table
   - Code cell: weighted score ranking table

5. **City Rankings Section**
   - Hungarian explanation cell
   - English explanation cell
   - Code cell: count-based ranking table
   - Code cell: weighted score ranking table

6. **School Search Section**
   - Hungarian explanation cell
   - English explanation cell
   - Code cell: define SCHOOL_SEARCH parameter
   - Code cell: search and display results

**Acceptance Criteria:**
- Each section has separate Hungarian and English markdown cells
- Code cells are clearly separated from explanation cells
- Sections flow logically from data loading to analysis
- All text is properly formatted in markdown

**Priority:** High

---

#### FR-002: Data Loading and Overview

**Description:** The notebook shall load the master CSV file and display key dataset statistics.

**Data Loading:**
- Load from hardcoded path: `/kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv`
- Use pandas `read_csv()` with appropriate encoding (UTF-8) and delimiter (semicolon)
- Handle file not found error with clear message

**Dataset Overview Statistics:**
Display the following four statistics:
1. Total number of records
2. Year range covered (earliest to latest)
3. Number of unique schools
4. Number of unique cities

**Acceptance Criteria:**
- CSV loads successfully in Kaggle environment
- All four statistics are calculated and displayed
- Statistics are formatted clearly (not raw Python output)
- Error handling for missing or corrupted file

**Priority:** High

---

#### FR-003: Configurable Parameters

**Description:** The notebook shall provide configurable parameters at the top of relevant sections for user customization.

**Parameters:**

1. **TOP_X** (integer, default: 3)
   - Defines the threshold for "top X" placements
   - Used in both count and weighted calculations
   - Example: TOP_X = 3 means top 3 (podium) finishes

2. **GRADE_FILTER** (string, integer, or list, default: "all")
   - Filter results by grade level(s)
   - Options: 
     - `"all"` - include all grades
     - Single grade: `8` or `"8"` - only 8th grade
     - Multiple grades: `[5, 6, 7, 8]` - grades 5 through 8
   - Example: GRADE_FILTER = 8 shows only 8th grade results
   - Example: GRADE_FILTER = [7, 8] shows 7th and 8th grade results
   - Example: GRADE_FILTER = "all" includes all grades

3. **YEAR_FILTER** (string or list, default: "all")
   - Filter results by year(s)
   - Options:
     - `"all"` - include all years
     - Single year: `"2023-24"` - only that year
     - Multiple years: `["2022-23", "2023-24", "2024-25"]` - specific years
   - Example: YEAR_FILTER = "2023-24" shows only 2023-24 results
   - Example: YEAR_FILTER = ["2023-24", "2024-25"] shows only recent two years
   - Example: YEAR_FILTER = "all" includes all years

4. **DISPLAY_TOP_N** (integer, default: 50)
   - Number of top results to display in ranking tables
   - Example: DISPLAY_TOP_N = 50 shows top 50 schools/cities

**Note:** SCHOOL_SEARCH parameter is defined in the School Search section, not here.

**Acceptance Criteria:**
- All parameters are defined as simple Python variables
- Parameters are clearly commented with examples
- Changing parameters and re-running cells produces correct filtered results
- Invalid parameter values are handled gracefully

**Priority:** High

---

#### FR-004: Helper Functions

**Description:** The notebook shall define reusable helper functions at the top for data filtering and scoring calculations.

**Required Functions:**

1. **`filter_data(df, grade_filter, year_filter)`**
   - Filters dataframe based on grade and year parameters
   - Handles "all" option for both filters
   - Handles single value (e.g., 8 or "2023-24")
   - Handles list of values (e.g., [5, 6, 7, 8] or ["2022-23", "2023-24"])
   - Returns filtered dataframe

2. **`calculate_count_ranking(df, top_x, group_by)`**
   - Counts appearances in top X positions
   - Groups by specified column (school or city)
   - Returns sorted dataframe with counts

3. **`calculate_weighted_ranking(df, top_x, group_by)`**
   - Calculates weighted score: 1st place = X points, 2nd = X-1, ..., Xth = 1 point
   - Positions below X get 0 points
   - Groups by specified column (school or city)
   - Returns sorted dataframe with weighted scores

4. **`search_schools(df, search_term)`**
   - Performs case-insensitive partial matching on school names
   - Returns list of matching school names
   - Returns empty list if no matches

5. **`get_school_results(df, school_name)`**
   - Retrieves all competition results for a specific school
   - Sorts by year (descending) then grade (ascending)
   - Returns dataframe with columns: year, grade, subject, rank

**Acceptance Criteria:**
- All functions are defined in a single code cell
- Functions have clear docstrings
- Functions handle edge cases (empty dataframes, invalid inputs)
- Functions are used consistently throughout the notebook

**Priority:** High

---

#### FR-005: School Rankings - Count-Based

**Description:** The notebook shall display a ranking of schools based on the count of top X appearances.

**Calculation Logic:**
- Filter data based on GRADE_FILTER and YEAR_FILTER
- Count how many times each school appears in positions 1 through TOP_X
- Each position counts equally (no weighting)
- Group by school name

**Output Table Columns:**
1. School Name (iskola_nev)
2. City (varos)
3. Count (number of top X appearances)

**Display:**
- Show top DISPLAY_TOP_N schools
- Sort by count (descending)
- Display as formatted Pandas DataFrame

**Acceptance Criteria:**
- Table displays correct counts based on TOP_X parameter
- Filtering by grade and year works correctly
- Table is limited to DISPLAY_TOP_N rows
- Ties in count are handled consistently (alphabetical by school name)

**Priority:** High

---

#### FR-006: School Rankings - Weighted Score

**Description:** The notebook shall display a ranking of schools based on weighted scoring of placements.

**Calculation Logic:**
- Filter data based on GRADE_FILTER and YEAR_FILTER
- For each school, calculate weighted score:
  - 1st place = TOP_X points
  - 2nd place = TOP_X - 1 points
  - 3rd place = TOP_X - 2 points
  - ...
  - TOP_X place = 1 point
  - Below TOP_X = 0 points
- Sum all points for each school

**Output Table Columns:**
1. School Name (iskola_nev)
2. City (varos)
3. Weighted Score (total points)

**Display:**
- Show top DISPLAY_TOP_N schools
- Sort by weighted score (descending)
- Display as formatted Pandas DataFrame

**Acceptance Criteria:**
- Weighted scoring formula is correctly implemented
- Filtering by grade and year works correctly
- Table is limited to DISPLAY_TOP_N rows
- Ties in score are handled consistently (alphabetical by school name)

**Priority:** High

---

#### FR-007: City Rankings - Count-Based

**Description:** The notebook shall display a ranking of cities based on the count of top X appearances by schools from that city.

**Calculation Logic:**
- Filter data based on GRADE_FILTER and YEAR_FILTER
- Count how many times schools from each city appear in positions 1 through TOP_X
- Aggregate all schools from the same city

**Output Table Columns:**
1. City (varos)
2. Count (number of top X appearances)

**Display:**
- Show top DISPLAY_TOP_N cities
- Sort by count (descending)
- Display as formatted Pandas DataFrame

**Acceptance Criteria:**
- Table displays correct counts based on TOP_X parameter
- All schools from the same city are aggregated correctly
- Filtering by grade and year works correctly
- Table is limited to DISPLAY_TOP_N rows

**Priority:** High

---

#### FR-008: City Rankings - Weighted Score

**Description:** The notebook shall display a ranking of cities based on weighted scoring of placements by schools from that city.

**Calculation Logic:**
- Filter data based on GRADE_FILTER and YEAR_FILTER
- For each city, calculate weighted score using same formula as school rankings
- Aggregate scores from all schools in the same city

**Output Table Columns:**
1. City (varos)
2. Weighted Score (total points)

**Display:**
- Show top DISPLAY_TOP_N cities
- Sort by weighted score (descending)
- Display as formatted Pandas DataFrame

**Acceptance Criteria:**
- Weighted scoring formula is correctly implemented
- All schools from the same city are aggregated correctly
- Filtering by grade and year works correctly
- Table is limited to DISPLAY_TOP_N rows

**Priority:** High

---

#### FR-009: School Search with Partial Matching

**Description:** The notebook shall allow users to search for schools using partial name matching and display results appropriately.

**Parameter Definition:**
- **SCHOOL_SEARCH** (string, default: "")
  - Partial school name for search feature
  - Case-insensitive substring matching
  - Defined in the School Search section (not at the top with other parameters)
  - Example: SCHOOL_SEARCH = "Kölcsey"

**Search Logic:**
- Use SCHOOL_SEARCH parameter for search term
- Perform case-insensitive substring matching
- Find all schools containing the search term

**Behavior:**

1. **If SCHOOL_SEARCH is empty:**
   - Display message: "Please enter a school name to search"

2. **If no matches found:**
   - Display message: "No schools found matching: [search_term]"

3. **If multiple matches found:**
   - Display list of all matching school names
   - Display message: "Multiple schools found. Please refine your search to be more specific."
   - Do not show results table

4. **If exactly one match found:**
   - Display the school name
   - Display complete results table for that school

**Results Table (for single match):**
- Columns: Year (ev), Grade (evfolyam), Subject (targy), Rank (helyezes)
- Sorted by: Year descending, then Grade ascending
- Show all results (no limit)

**Acceptance Criteria:**
- Partial matching works correctly (case-insensitive)
- All four behaviors work as specified
- Results table displays correct data for matched school
- Sorting is correct (year desc, grade asc)

**Priority:** High

---

#### FR-010: Dual Language Support

**Description:** All explanatory text in the notebook shall be provided in both Hungarian and English.

**Implementation:**
- Each explanation has two separate markdown cells
- First cell: Hungarian text with 🇭🇺 flag emoji
- Second cell: English text with 🇬🇧 flag emoji
- Code cells remain language-neutral (comments in English)

**Content to Translate:**
- Section introductions
- Parameter explanations
- Usage instructions
- Output interpretations
- Error messages (where applicable)

**Acceptance Criteria:**
- Every markdown explanation has both Hungarian and English versions
- Translations are accurate and natural (not machine-translated)
- Flag emojis are used consistently
- Code comments are in English only

**Priority:** High

---

#### FR-011: Local Execution Support

**Description:** The project shall provide dual methods for running the notebook locally: Poetry (recommended, fast) and Docker (optional, exact Kaggle environment).

**Deliverables:**

1. **Bash Script: `run_notebook_with_poetry.sh`**
   - Launches Jupyter notebook server using Poetry environment
   - Simple wrapper around `poetry run jupyter notebook`
   - Fast startup, no download required
   - Uses relative paths in notebook

2. **Bash Script: `run_notebook_in_docker.sh`**
   - Launches Jupyter notebook server in Kaggle Docker container (20GB image)
   - Mounts local data directory to `/kaggle/input/tanulmanyi-versenyek/`
   - Mounts notebooks directory for editing
   - Provides exact Kaggle environment
   - Exposes Jupyter on localhost:8888

3. **Path Detection in Notebook**
   - Automatically detects if running on Kaggle or locally
   - Uses `/kaggle/input/...` on Kaggle
   - Uses `../data/kaggle/...` locally
   - Transparent to user

4. **README Section: "Running Locally"**
   - Explains both methods (Poetry recommended, Docker optional)
   - Shows prerequisites for each method
   - Explains trade-offs (speed vs exact environment)
   - Troubleshooting common issues

**Script Requirements (Poetry):**
```bash
#!/bin/bash
# Activate Poetry environment and run Jupyter
poetry run jupyter notebook
```

**Script Requirements (Docker):**
```bash
#!/bin/bash
# Pull Kaggle Docker image (20GB)
# Mount data/kaggle/ to /kaggle/input/tanulmanyi-versenyek/
# Mount notebooks/ to /kaggle/working/
# Run Jupyter notebook server
# Expose port 8888
```

**Acceptance Criteria:**
- Poetry script launches Jupyter quickly using existing environment
- Docker script successfully launches Jupyter in Kaggle Docker
- Path detection works transparently in both environments
- Data is accessible in both methods
- Notebook can be edited and saved locally
- README provides clear comparison and instructions for both methods
- Scripts work on Linux and macOS (Windows via WSL)

**Priority:** Medium

---

### 3.2. Non-Functional Requirements

#### NFR-001: Performance

**Description:** The notebook shall execute efficiently within Kaggle's resource constraints.

**Requirements:**
- All cells execute in under 5 seconds on Kaggle's standard kernel
- Memory usage stays within Kaggle's limits (16GB RAM)
- No unnecessary data copies or redundant calculations
- Efficient pandas operations (vectorized, no loops where possible)

**Acceptance Criteria:**
- Full notebook execution (all cells) completes in under 30 seconds
- No memory errors or kernel crashes
- Ranking calculations are optimized for the dataset size

**Priority:** Medium

---

#### NFR-002: Usability

**Description:** The notebook shall be easy to use for technical users with basic Python knowledge.

**Requirements:**
- Clear section headers and navigation
- Parameters are easy to find and modify
- Output tables are readable and well-formatted
- Error messages are helpful and actionable
- Code is clean and well-commented

**Acceptance Criteria:**
- A new user can modify parameters and get results without reading documentation
- All outputs are properly formatted (not raw Python objects)
- Code follows PEP 8 style guidelines
- Variable names are descriptive and consistent

**Priority:** High

---

#### NFR-003: Maintainability

**Description:** The notebook shall be easy to maintain and extend in future versions.

**Requirements:**
- Helper functions are modular and reusable
- Code is DRY (Don't Repeat Yourself)
- Clear separation between configuration, logic, and display
- Consistent naming conventions
- Minimal dependencies (only pandas required beyond standard library)

**Acceptance Criteria:**
- Adding a new ranking metric requires changes in only one place
- Helper functions can be reused for future features
- Code is self-documenting with clear variable names
- No hardcoded values in logic (use parameters)

**Priority:** Medium

---

#### NFR-004: Portability

**Description:** The notebook shall work consistently across different execution environments.

**Requirements:**
- Works in Kaggle's notebook environment (primary)
- Works locally using Poetry (recommended) or Kaggle Docker image (optional)
- Path detection handles both Kaggle and local environments
- Uses only libraries available in Kaggle's standard image and Poetry dependencies

**Acceptance Criteria:**
- Same notebook file works on Kaggle and locally without modifications
- No dependency installation required
- Results are identical in both environments

**Priority:** High

---

#### NFR-005: Educational Value

**Description:** The notebook shall serve as a learning resource for data analysis techniques.

**Requirements:**
- Code is readable and well-structured
- Comments explain "why" not just "what"
- Examples demonstrate best practices
- Dual language support makes it accessible to Hungarian and international users

**Acceptance Criteria:**
- A data analyst can understand the code without external documentation
- Code demonstrates good pandas practices
- Explanations are clear and concise in both languages

**Priority:** Medium

---

### 3.3. File and Directory Structure

**New Files:**
```
notebooks/
```
notebooks/
└── competition_analysis.ipynb     # Main analysis notebook (general name for future expansion)

run_notebook_with_poetry.sh       # Poetry execution script (project root) - RECOMMENDED
run_notebook_in_docker.sh          # Docker execution script (project root) - OPTIONAL
```

**Updated Files:**
```
README.md                          # Add section on notebook usage
```

**No Changes to Existing Pipeline:**
- The notebook is independent of the v0.1 pipeline scripts
- No modifications to `01_raw_downloader.py`, `02_html_parser.py`, or `03_merger_and_excel.py`
- Notebook is not automatically copied to `data/kaggle/` directory

---

### 3.4. Data Schema Reference

The notebook will consume the master CSV file with the following schema:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| ev | string | Academic year | "2023-24" |
| targy | string | Subject (always "Anyanyelv") | "Anyanyelv" |
| iskola_nev | string | School name | "Budapesti Kölcsey F. Gimnázium" |
| varos | string | City | "Budapest" |
| megye | string | County (always empty in v0.1) | "" |
| helyezes | integer | Final rank/placement | 1 |
| evfolyam | integer | Grade level | 8 |

**Data Characteristics:**
- 3,233 total records
- 10 academic years (2015-16 through 2024-25)
- 766 unique schools
- 264 unique cities
- Grades 3-8 (with subcategories for grades 7-8)

---

## 4. Future Enhancements (Post-v0.2.0)

The following features are identified for future versions but are out of scope for v0.2.0:

### 4.1. Interactive Widgets

**Description:** Add ipywidgets for interactive parameter selection without cell re-execution.

**Features:**
- Dropdown menus for grade and year filters
- Slider for TOP_X and DISPLAY_TOP_N
- Text input for school search
- Real-time chart updates

**Benefits:**
- Better user experience
- No need to edit code
- More accessible to non-technical users

---

### 4.2. Chart Visualizations

**Description:** Add Plotly charts alongside tables for visual analysis.

**Planned Charts:**
- Horizontal bar charts for rankings
- Time series line charts for trends
- Geographic maps for city distribution
- Heatmaps for grade/year performance

**Benefits:**
- Visual pattern recognition
- Better for presentations
- Prepares code for web dashboard

---

### 4.3. Advanced Analytics

**Description:** Add statistical analysis and trend detection.

**Features:**
- Year-over-year growth rates
- Performance consistency metrics
- Emerging schools identification
- Correlation analysis between cities and performance

---

### 4.4. Export Functionality

**Description:** Allow users to export filtered results and rankings.

**Features:**
- Export tables to CSV
- Generate PDF reports
- Save custom filtered datasets

---

## 5. Appendices

### 5.1. Glossary

- **Kaggle:** Online platform for data science competitions and dataset sharing
- **Jupyter Notebook:** Interactive computational environment for data analysis
- **Pandas:** Python library for data manipulation and analysis
- **Docker:** Containerization platform for consistent environments
- **ipywidgets:** Interactive HTML widgets for Jupyter notebooks
- **Plotly:** Interactive graphing library for Python

### 5.2. Example Parameter Configurations

**Example 1: Podium Finishes (Top 3)**
```python
TOP_X = 3
GRADE_FILTER = "all"
YEAR_FILTER = "all"
DISPLAY_TOP_N = 50
```

**Example 2: Top 10 in 8th Grade Only, Recent Years**
```python
TOP_X = 10
GRADE_FILTER = 8  # Single grade
YEAR_FILTER = ["2022-23", "2023-24", "2024-25"]  # Multiple years
DISPLAY_TOP_N = 30
```

**Example 3: Top 5 in Upper Grades, Single Recent Year**
```python
TOP_X = 5
GRADE_FILTER = [7, 8]  # Multiple grades
YEAR_FILTER = "2024-25"  # Single year
DISPLAY_TOP_N = 20
```

**Example 4: All Placements, Middle Grades**
```python
TOP_X = 100  # Effectively all placements
GRADE_FILTER = [5, 6]  # Multiple grades
YEAR_FILTER = "all"
DISPLAY_TOP_N = 100
```

### 5.3. Weighted Scoring Formula

For TOP_X = 3:
- 1st place: 3 points
- 2nd place: 2 points
- 3rd place: 1 point
- 4th+ place: 0 points

For TOP_X = 10:
- 1st place: 10 points
- 2nd place: 9 points
- ...
- 10th place: 1 point
- 11th+ place: 0 points

General formula: `points = max(0, TOP_X - rank + 1)`

### 5.4. Success Criteria for v0.2.0

The release will be considered successful when:

1. ✅ Notebook executes without errors on Kaggle
2. ✅ All three core features (school rankings, city rankings, school search) work correctly
3. ✅ Dual language support is complete and accurate
4. ✅ Local execution via both Poetry and Docker works
5. ✅ Documentation is clear and comprehensive
6. ✅ Code is clean, readable, and well-commented
7. ✅ Notebook is uploaded to Kaggle and publicly accessible

---

**Document Version:** 1.0  
**Date:** 2025-12-21  
**Status:** Final  
**Next Step:** Create detailed design document (step2-design.md)
