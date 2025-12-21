# Detailed Design Document: Competition Analysis Notebook - v0.2.0

## 1. Introduction

### 1.1. Purpose

This document provides a detailed technical design for implementing the v0.2.0 release of the Hungarian Academic Competition Results Pipeline project. This release adds a Jupyter notebook for interactive data exploration and analysis, expanding the project horizontally into the visualization layer.

### 1.2. Scope

This design covers:
- Jupyter notebook structure and implementation
- Helper function specifications
- Data filtering and ranking algorithms
- Dual language (Hungarian/English) presentation
- Local execution infrastructure (Docker script)
- Documentation updates
- Testing strategy

### 1.3. Design Principles

Based on the requirements and architectural decisions:

1. **Self-Contained Notebook**: All code inline, no external module imports (Kaggle-native)
2. **Educational Focus**: Code should be readable and serve as a learning resource
3. **MVP Simplicity**: Focus on core features, defer advanced features to future versions
4. **Professional Presentation**: Fully formatted tables with styling
5. **Strict Validation**: Clear error messages for invalid inputs
6. **Minimal Infrastructure**: Simple Docker script, comprehensive README

### 1.4. References

- **Requirements**: `dev-history/v0.2/step1-requirements.md`
- **v0.1 Design**: `dev-history/v0.1/step2-design.md`
- **Master Dataset**: `data/kaggle/master_bolyai_anyanyelv.csv`

---

## 2. Architecture Overview

### 2.1. Component Structure

```
v0.2.0 Components:
├── notebooks/
│   └── competition_analysis.ipynb    # Self-contained analysis notebook
├── tests/
│   └── test_notebook_helpers.py      # Unit tests for helper functions
├── run_notebook_locally.sh           # Docker execution script
└── Documentation updates:
    ├── README.md                      # New "Notebooks" section
    └── templates/kaggle/README.*.md   # Brief notebook mention
```

### 2.2. Notebook Architecture

The notebook follows a linear, sectioned structure:

```
1. Introduction (HU + EN)
2. Imports & Configuration
3. Data Loading
4. Dataset Overview
5. Helper Functions Definition
6. School Rankings (Count-based)
7. School Rankings (Weighted)
8. City Rankings (Count-based)
9. City Rankings (Weighted)
10. School Search
```

Each analytical section (6-10) has:
- Hungarian explanation cell
- English explanation cell
- Configuration parameters (where applicable)
- Code execution cell(s)
- Formatted output display

### 2.3. Data Flow

```
CSV File (Kaggle path)
    ↓
Load with pandas
    ↓
Apply filters (grade, year)
    ↓
Calculate rankings (count or weighted)
    ↓
Format and display tables
```

---

## 3. Detailed Component Design

### 3.1. Notebook Structure

#### 3.1.1. Cell Organization

**Pattern for each section:**
```
[Markdown Cell - Hungarian]
🇭🇺 <span style="color: #477050;">**MAGYAR**</span>
[Hungarian explanation text]

[Markdown Cell - English]
🇬🇧 <span style="color: #477050;">**ENGLISH**</span>
[English explanation text]

[Code Cell]
# Python code
```

#### 3.1.2. Section Breakdown

**Section 1: Introduction**
- Purpose: Explain what the notebook does
- Content: Brief overview, link to dataset README
- Cells: 2 markdown (HU + EN)

**Section 2: Imports & Configuration**
- Purpose: Load libraries and set display options
- Content: Import pandas, configure pandas display settings
- Cells: 2 markdown (HU + EN) + 1 code

**Section 3: Data Loading**
- Purpose: Load CSV and handle errors
- Content: Load from `/kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv`
- Cells: 2 markdown (HU + EN) + 1 code

**Section 4: Dataset Overview**
- Purpose: Show basic statistics
- Content: 4 statistics (total records, year range, unique schools, unique cities)
- Cells: 2 markdown (HU + EN) + 1 code

**Section 5: Helper Functions**
- Purpose: Define all reusable functions
- Content: 5 helper functions (detailed in section 3.2)
- Cells: 2 markdown (HU + EN) + 1 code

**Section 6-9: Rankings**
- Purpose: Display school and city rankings
- Content: Parameters + ranking calculation + formatted table
- Cells per section: 2 markdown (HU + EN) + 2 code (params + execution)

**Section 10: School Search**
- Purpose: Search and display school results
- Content: Search parameter + search logic + results table
- Cells: 2 markdown (HU + EN) + 2 code (param + execution)

**Total cells: ~30 cells**

---

### 3.2. Helper Functions Specification

All helper functions will be defined in a single code cell in Section 5.

#### 3.2.1. Function: `filter_data()`

**Signature:**
```python
def filter_data(df: pd.DataFrame, 
                grade_filter: Union[str, int, List[int]], 
                year_filter: Union[str, List[str]]) -> pd.DataFrame
```

**Purpose:** Filter dataframe by grade and year with flexible input handling.

**Parameters:**
- `df`: Input dataframe
- `grade_filter`: "all", single grade (int or str), or list of grades
- `year_filter`: "all", single year (str), or list of years

**Logic:**
1. Handle grade_filter:
   - If "all": no filtering
   - If single value: convert to list
   - If list: use as-is
   - Validate all grades are in range 3-8
2. Handle year_filter:
   - If "all": no filtering
   - If single value: convert to list
   - If list: use as-is
   - Validate all years exist in dataset
3. Apply filters using pandas `.isin()`
4. Return filtered dataframe

**Error Handling:**
- Raise `ValueError` with clear message if invalid grade (not 3-8)
- Raise `ValueError` with clear message if invalid year (not in dataset)
- List valid options in error message

**Example:**
```python
# Valid calls
filter_data(df, "all", "all")
filter_data(df, 8, "2023-24")
filter_data(df, [7, 8], ["2023-24", "2024-25"])

# Invalid - raises ValueError
filter_data(df, 9, "all")  # Grade 9 doesn't exist
filter_data(df, 8, "2030-31")  # Year doesn't exist
```


#### 3.2.2. Function: `calculate_count_ranking()`

**Signature:**
```python
def calculate_count_ranking(df: pd.DataFrame, 
                           top_x: int, 
                           group_by: str) -> pd.DataFrame
```

**Purpose:** Count appearances in top X positions, grouped by school or city.

**Parameters:**
- `df`: Filtered dataframe
- `top_x`: Threshold for top positions (e.g., 3 for podium)
- `group_by`: Column to group by ("iskola_nev" or "varos")

**Logic:**
1. Filter dataframe to only rows where `helyezes <= top_x`
2. Group by specified column
3. Count occurrences
4. Sort by count (descending)
5. Reset index for clean display
6. Rename columns appropriately

**Return:**
- For schools: DataFrame with columns [School, City, Count]
- For cities: DataFrame with columns [City, Count]

**Example:**
```python
# School ranking
school_ranking = calculate_count_ranking(filtered_df, 3, "iskola_nev")
# Returns: [School Name, City, Count of Top 3]

# City ranking
city_ranking = calculate_count_ranking(filtered_df, 3, "varos")
# Returns: [City, Count of Top 3]
```

---

#### 3.2.3. Function: `calculate_weighted_ranking()`

**Signature:**
```python
def calculate_weighted_ranking(df: pd.DataFrame, 
                              top_x: int, 
                              group_by: str) -> pd.DataFrame
```

**Purpose:** Calculate weighted scores based on placement, grouped by school or city.

**Parameters:**
- `df`: Filtered dataframe
- `top_x`: Threshold for scoring (positions beyond this get 0 points)
- `group_by`: Column to group by ("iskola_nev" or "varos")

**Scoring Formula:**
```
points = max(0, top_x - helyezes + 1)

Examples for top_x = 3:
- 1st place: max(0, 3 - 1 + 1) = 3 points
- 2nd place: max(0, 3 - 2 + 1) = 2 points
- 3rd place: max(0, 3 - 3 + 1) = 1 point
- 4th+ place: max(0, 3 - 4 + 1) = 0 points
```

**Logic:**
1. Create new column `points` using formula: `top_x - helyezes + 1`
2. Set negative points to 0 (positions beyond top_x)
3. Group by specified column
4. Sum points
5. Sort by total points (descending)
6. Reset index for clean display
7. Rename columns appropriately

**Return:**
- For schools: DataFrame with columns [School, City, Weighted Score]
- For cities: DataFrame with columns [City, Weighted Score]

**Example:**
```python
# School weighted ranking
school_ranking = calculate_weighted_ranking(filtered_df, 10, "iskola_nev")
# Returns: [School Name, City, Weighted Score]

# City weighted ranking
city_ranking = calculate_weighted_ranking(filtered_df, 10, "varos")
# Returns: [City, Weighted Score]
```

---

#### 3.2.4. Function: `search_schools()`

**Signature:**
```python
def search_schools(df: pd.DataFrame, search_term: str) -> List[str]
```

**Purpose:** Find schools matching a partial name search.

**Parameters:**
- `df`: Full dataframe
- `search_term`: Partial school name (case-insensitive)

**Logic:**
1. Strip whitespace from search_term
2. Convert search_term to lowercase
3. Filter unique school names containing search_term (case-insensitive)
4. Return sorted list of matching school names

**Return:**
- List of matching school names (sorted alphabetically)
- Empty list if no matches

**Example:**
```python
matches = search_schools(df, "Kölcsey")
# Returns: ["Budapesti Kölcsey Ferenc Gimnázium", ...]

matches = search_schools(df, "xyz123")
# Returns: []
```

---

#### 3.2.5. Function: `get_school_results()`

**Signature:**
```python
def get_school_results(df: pd.DataFrame, school_name: str) -> pd.DataFrame
```

**Purpose:** Retrieve all competition results for a specific school.

**Parameters:**
- `df`: Full dataframe
- `school_name`: Exact school name

**Logic:**
1. Filter dataframe where `iskola_nev == school_name`
2. Select columns: `ev`, `evfolyam`, `targy`, `helyezes`
3. Sort by `ev` (descending), then `evfolyam` (ascending)
4. Reset index
5. Rename columns to display names

**Return:**
- DataFrame with columns [Year, Grade, Subject, Rank]
- Sorted by year (newest first), then grade (lowest first)

**Example:**
```python
results = get_school_results(df, "Budapesti Kölcsey Ferenc Gimnázium")
# Returns DataFrame:
#   Year      Grade  Subject    Rank
#   2024-25   7      Anyanyelv  1
#   2024-25   8      Anyanyelv  3
#   2023-24   7      Anyanyelv  2
#   ...
```

---

### 3.3. Table Formatting Specification

All ranking tables will use pandas Styler for professional formatting.

**Standard Table Style:**
```python
def format_ranking_table(df: pd.DataFrame, score_column: str) -> pd.io.formats.style.Styler:
    """
    Apply consistent formatting to ranking tables.
    
    Parameters:
    - df: DataFrame to format
    - score_column: Name of the score/count column for gradient
    
    Returns:
    - Styled DataFrame
    """
    return (df.style
        .background_gradient(subset=[score_column], cmap='YlGn')
        .set_properties(**{
            'text-align': 'left',
            'font-size': '11pt',
            'border': '1px solid #ddd'
        })
        .set_table_styles([
            {'selector': 'th', 'props': [
                ('background-color', '#477050'),
                ('color', 'white'),
                ('font-weight', 'bold'),
                ('text-align', 'left'),
                ('padding', '8px')
            ]},
            {'selector': 'td', 'props': [
                ('padding', '8px')
            ]},
            {'selector': 'tr:nth-of-type(even)', 'props': [
                ('background-color', '#f9f9f9')
            ]}
        ])
        .format({score_column: '{:,.0f}'})  # Thousands separator
        .hide(axis='index')  # Hide row numbers
    )
```

**Usage in notebook:**
```python
# Display formatted table
styled_table = format_ranking_table(ranking_df, 'Count')
display(styled_table)
```

**Note:** This formatting function will be included in the helper functions section.

---

### 3.4. Parameter Configuration

#### 3.4.1. Global Parameters (Sections 6-9)

Defined at the top of ranking sections:

```python
# === CONFIGURATION PARAMETERS ===
# Adjust these values and re-run the cell to see updated results

TOP_X = 3  # Threshold for "top X" placements (e.g., 3 = podium finishes)

GRADE_FILTER = "all"  # Options: "all", single grade (e.g., 8), or list (e.g., [7, 8])

YEAR_FILTER = "all"  # Options: "all", single year (e.g., "2023-24"), or list (e.g., ["2023-24", "2024-25"])

DISPLAY_TOP_N = 50  # Number of top results to display in tables
```

#### 3.4.2. School Search Parameter (Section 10)

Defined at the top of school search section:

```python
# === SCHOOL SEARCH PARAMETER ===
# Enter a partial school name (case-insensitive)

SCHOOL_SEARCH = ""  # Example: "Kölcsey" or "Budapest"
```

---

### 3.5. Error Handling Strategy

#### 3.5.1. Data Loading Errors

```python
try:
    df = pd.read_csv('/kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv', 
                     sep=';', encoding='utf-8')
    print(f"✓ Successfully loaded {len(df)} records")
except FileNotFoundError:
    print("✗ Error: Dataset file not found!")
    print("  Make sure the dataset is attached to this notebook.")
    print("  Expected path: /kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv")
    raise
except Exception as e:
    print(f"✗ Error loading dataset: {e}")
    raise
```

#### 3.5.2. Filter Validation Errors

```python
# In filter_data() function
valid_grades = [3, 4, 5, 6, 7, 8]
valid_years = df['ev'].unique().tolist()

# Validate grades
if grade_filter != "all":
    grades_to_check = [grade_filter] if not isinstance(grade_filter, list) else grade_filter
    invalid_grades = [g for g in grades_to_check if g not in valid_grades]
    if invalid_grades:
        raise ValueError(
            f"Invalid grade(s): {invalid_grades}\n"
            f"Valid grades are: {valid_grades}"
        )

# Validate years
if year_filter != "all":
    years_to_check = [year_filter] if not isinstance(year_filter, list) else year_filter
    invalid_years = [y for y in years_to_check if y not in valid_years]
    if invalid_years:
        raise ValueError(
            f"Invalid year(s): {invalid_years}\n"
            f"Valid years are: {sorted(valid_years)}"
        )
```

#### 3.5.3. School Search Handling

```python
# In school search section
if SCHOOL_SEARCH == "":
    print("ℹ Please enter a school name to search.")
else:
    matches = search_schools(df, SCHOOL_SEARCH)
    
    if len(matches) == 0:
        print(f"✗ No schools found matching: '{SCHOOL_SEARCH}'")
        print("  Try a different search term or check spelling.")
    
    elif len(matches) > 1:
        print(f"ℹ Found {len(matches)} schools matching '{SCHOOL_SEARCH}':")
        print()
        for i, school in enumerate(matches, 1):
            print(f"  {i}. {school}")
        print()
        print("  Please refine your search to be more specific.")
    
    else:
        # Exactly one match - display results
        school_name = matches[0]
        print(f"✓ Found: {school_name}")
        print()
        results = get_school_results(df, school_name)
        display(results)
```

---


## 4. Infrastructure Components

### 4.1. Docker Execution Script

**File:** `run_notebook_locally.sh`

**Purpose:** Launch Jupyter notebook in Kaggle's Docker environment with proper volume mounts.

**Implementation:**

```bash
#!/bin/bash

# Run Jupyter notebook locally using Kaggle's Docker image
# This ensures the same environment as Kaggle's platform

echo "Starting Jupyter notebook in Kaggle Docker environment..."
echo ""
echo "Mounting:"
echo "  - data/kaggle/ → /kaggle/input/tanulmanyi-versenyek/"
echo "  - notebooks/ → /kaggle/working/"
echo ""
echo "Jupyter will be available at: http://localhost:8888"
echo ""

docker run -it --rm \
  -p 8888:8888 \
  -v "$(pwd)/data/kaggle":/kaggle/input/tanulmanyi-versenyek \
  -v "$(pwd)/notebooks":/kaggle/working \
  kaggle/python \
  jupyter notebook \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --NotebookApp.token='' \
    --NotebookApp.password=''
```

**Key Features:**
- Uses official `kaggle/python` Docker image
- Mounts local data directory to Kaggle's expected path
- Mounts notebooks directory for editing
- Disables authentication for local use
- Exposes Jupyter on port 8888

**Usage:**
```bash
chmod +x run_notebook_locally.sh
./run_notebook_locally.sh
```

---

### 4.2. Testing Infrastructure

**File:** `tests/test_notebook_helpers.py`

**Purpose:** Unit tests for helper functions to ensure correctness.

**Structure:**

```python
"""
Unit tests for notebook helper functions.

Note: These functions are duplicated from the notebook for testing purposes.
Any changes to the notebook helper functions must be reflected here.
"""

import pytest
import pandas as pd
import numpy as np


# === HELPER FUNCTIONS (DUPLICATED FROM NOTEBOOK) ===
# Keep in sync with notebooks/competition_analysis.ipynb

def filter_data(df, grade_filter, year_filter):
    """[Copy exact implementation from notebook]"""
    pass

def calculate_count_ranking(df, top_x, group_by):
    """[Copy exact implementation from notebook]"""
    pass

def calculate_weighted_ranking(df, top_x, group_by):
    """[Copy exact implementation from notebook]"""
    pass

def search_schools(df, search_term):
    """[Copy exact implementation from notebook]"""
    pass

def get_school_results(df, school_name):
    """[Copy exact implementation from notebook]"""
    pass


# === TEST FIXTURES ===

@pytest.fixture
def sample_df():
    """Create a small sample dataframe for testing."""
    return pd.DataFrame({
        'ev': ['2023-24', '2023-24', '2023-24', '2024-25', '2024-25'],
        'targy': ['Anyanyelv'] * 5,
        'iskola_nev': ['School A', 'School B', 'School A', 'School C', 'School A'],
        'varos': ['Budapest', 'Debrecen', 'Budapest', 'Szeged', 'Budapest'],
        'megye': [''] * 5,
        'helyezes': [1, 2, 5, 1, 3],
        'evfolyam': [8, 7, 8, 8, 7]
    })


# === TESTS FOR filter_data() ===

def test_filter_data_all(sample_df):
    """Test filtering with 'all' for both parameters."""
    result = filter_data(sample_df, "all", "all")
    assert len(result) == len(sample_df)

def test_filter_data_single_grade(sample_df):
    """Test filtering by single grade."""
    result = filter_data(sample_df, 8, "all")
    assert len(result) == 3
    assert all(result['evfolyam'] == 8)

def test_filter_data_multiple_grades(sample_df):
    """Test filtering by multiple grades."""
    result = filter_data(sample_df, [7, 8], "all")
    assert len(result) == 5

def test_filter_data_single_year(sample_df):
    """Test filtering by single year."""
    result = filter_data(sample_df, "all", "2023-24")
    assert len(result) == 3
    assert all(result['ev'] == '2023-24')

def test_filter_data_multiple_years(sample_df):
    """Test filtering by multiple years."""
    result = filter_data(sample_df, "all", ["2023-24", "2024-25"])
    assert len(result) == 5

def test_filter_data_combined(sample_df):
    """Test filtering by both grade and year."""
    result = filter_data(sample_df, 8, "2023-24")
    assert len(result) == 2

def test_filter_data_invalid_grade(sample_df):
    """Test that invalid grade raises ValueError."""
    with pytest.raises(ValueError, match="Invalid grade"):
        filter_data(sample_df, 9, "all")

def test_filter_data_invalid_year(sample_df):
    """Test that invalid year raises ValueError."""
    with pytest.raises(ValueError, match="Invalid year"):
        filter_data(sample_df, "all", "2030-31")


# === TESTS FOR calculate_count_ranking() ===

def test_count_ranking_schools(sample_df):
    """Test count ranking for schools."""
    result = calculate_count_ranking(sample_df, 3, "iskola_nev")
    assert len(result) == 3  # 3 unique schools
    assert result.iloc[0]['iskola_nev'] == 'School A'  # Most appearances
    assert result.iloc[0]['Count'] == 3

def test_count_ranking_cities(sample_df):
    """Test count ranking for cities."""
    result = calculate_count_ranking(sample_df, 3, "varos")
    assert len(result) == 3  # 3 unique cities
    assert result.iloc[0]['varos'] == 'Budapest'  # Most appearances

def test_count_ranking_top_threshold(sample_df):
    """Test that only top X positions are counted."""
    result = calculate_count_ranking(sample_df, 2, "iskola_nev")
    # Only positions 1 and 2 should be counted
    # School A: 2 appearances (1st, 1st)
    # School B: 1 appearance (2nd)
    # School C: 1 appearance (1st)
    assert result.iloc[0]['Count'] == 2


# === TESTS FOR calculate_weighted_ranking() ===

def test_weighted_ranking_schools(sample_df):
    """Test weighted ranking for schools."""
    result = calculate_weighted_ranking(sample_df, 3, "iskola_nev")
    # School A: 1st (3pts) + 1st (3pts) + 3rd (1pt) = 7pts
    # School B: 2nd (2pts) = 2pts
    # School C: 1st (3pts) = 3pts
    assert result.iloc[0]['iskola_nev'] == 'School A'
    assert result.iloc[0]['Weighted Score'] == 7

def test_weighted_ranking_formula(sample_df):
    """Test weighted scoring formula."""
    result = calculate_weighted_ranking(sample_df, 3, "iskola_nev")
    # Verify specific scores
    school_a_score = result[result['iskola_nev'] == 'School A']['Weighted Score'].iloc[0]
    assert school_a_score == 7  # 3 + 3 + 1

def test_weighted_ranking_zero_points(sample_df):
    """Test that positions beyond top_x get 0 points."""
    result = calculate_weighted_ranking(sample_df, 2, "iskola_nev")
    # School A's 3rd and 5th place should not count
    school_a_score = result[result['iskola_nev'] == 'School A']['Weighted Score'].iloc[0]
    assert school_a_score == 6  # Only 1st + 1st


# === TESTS FOR search_schools() ===

def test_search_schools_exact_match(sample_df):
    """Test search with exact match."""
    result = search_schools(sample_df, "School A")
    assert len(result) == 1
    assert result[0] == "School A"

def test_search_schools_partial_match(sample_df):
    """Test search with partial match."""
    result = search_schools(sample_df, "School")
    assert len(result) == 3  # All schools match

def test_search_schools_case_insensitive(sample_df):
    """Test that search is case-insensitive."""
    result = search_schools(sample_df, "school a")
    assert len(result) == 1
    assert result[0] == "School A"

def test_search_schools_no_match(sample_df):
    """Test search with no matches."""
    result = search_schools(sample_df, "XYZ123")
    assert len(result) == 0


# === TESTS FOR get_school_results() ===

def test_get_school_results(sample_df):
    """Test retrieving results for a specific school."""
    result = get_school_results(sample_df, "School A")
    assert len(result) == 3
    # Check sorting: year desc, grade asc
    assert result.iloc[0]['Year'] == '2024-25'
    assert result.iloc[1]['Year'] == '2023-24'
    assert result.iloc[2]['Year'] == '2023-24'

def test_get_school_results_columns(sample_df):
    """Test that result has correct columns."""
    result = get_school_results(sample_df, "School A")
    expected_columns = ['Year', 'Grade', 'Subject', 'Rank']
    assert list(result.columns) == expected_columns

def test_get_school_results_no_match(sample_df):
    """Test retrieving results for non-existent school."""
    result = get_school_results(sample_df, "Nonexistent School")
    assert len(result) == 0
```

**Test Execution:**
```bash
poetry run pytest tests/test_notebook_helpers.py -v
```

**Expected Output:**
```
tests/test_notebook_helpers.py::test_filter_data_all PASSED
tests/test_notebook_helpers.py::test_filter_data_single_grade PASSED
tests/test_notebook_helpers.py::test_filter_data_multiple_grades PASSED
...
======================== 20 passed in 0.5s ========================
```

---


## 5. Documentation Updates

### 5.1. Main README.md Updates

**Location:** Project root `README.md`

**Changes:** Add new section after "Hogyan használd?" (How to use)

**New Section:**

```markdown
## Notebooks - Adatelemzés / Data Analysis

A projekt tartalmaz egy Jupyter notebookot az adatok interaktív elemzéséhez.

### Notebook használata Kaggle-ön

1. Töltsd fel a notebookot a Kaggle-re
2. Csatold hozzá a `tanulmanyi-versenyek` adathalmazt
3. Futtasd a cellákat sorban

### Notebook használata lokálisan

Docker segítségével futtathatod a notebookot ugyanabban a környezetben, mint a Kaggle:

```bash
# Indítsd el a Jupyter szervert Kaggle Docker környezetben
./run_notebook_locally.sh

# Nyisd meg a böngészőben: http://localhost:8888
```

**Előfeltételek:**
- Docker telepítve
- Az adatok a `data/kaggle/` mappában

**Részletek:** Lásd `notebooks/README.md`

---

The project includes a Jupyter notebook for interactive data exploration.

### Using the Notebook on Kaggle

1. Upload the notebook to Kaggle
2. Attach the `tanulmanyi-versenyek` dataset
3. Run the cells in order

### Using the Notebook Locally

You can run the notebook in the same environment as Kaggle using Docker:

```bash
# Start Jupyter server in Kaggle Docker environment
./run_notebook_locally.sh

# Open in browser: http://localhost:8888
```

**Prerequisites:**
- Docker installed
- Data in `data/kaggle/` directory

**Details:** See `notebooks/README.md`
```

---

### 5.2. Notebooks README

**New File:** `notebooks/README.md`

**Content:**

```markdown
# Competition Analysis Notebook

## Overview

This directory contains Jupyter notebooks for analyzing Hungarian academic competition results.

## Notebooks

### `competition_analysis.ipynb`

Interactive analysis notebook with the following features:

**Rankings:**
- School rankings (count-based and weighted scoring)
- City rankings (count-based and weighted scoring)
- Configurable filters (grade, year, top-X threshold)

**Search:**
- Search for specific schools by partial name
- View complete competition history

**Languages:**
- Dual language support (Hungarian 🇭🇺 and English 🇬🇧)
- Each section has explanations in both languages

## Running on Kaggle

1. Upload `competition_analysis.ipynb` to Kaggle
2. Add the `tanulmanyi-versenyek` dataset to your notebook
3. Run cells in order

The notebook expects data at: `/kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv`

## Running Locally

### Prerequisites

- Docker installed and running
- Dataset in `../data/kaggle/` directory

### Steps

1. From the project root, run:
   ```bash
   ./run_notebook_locally.sh
   ```

2. Open your browser to: `http://localhost:8888`

3. Navigate to `competition_analysis.ipynb`

### How It Works

The script launches Jupyter in Kaggle's official Docker image with:
- Data mounted to `/kaggle/input/tanulmanyi-versenyek/`
- Notebooks directory mounted to `/kaggle/working/`

This ensures the exact same environment as Kaggle's platform.

### Troubleshooting

**Port 8888 already in use:**
```bash
# Find and stop the process using port 8888
lsof -ti:8888 | xargs kill -9
```

**Docker image not found:**
```bash
# Pull the Kaggle image manually
docker pull kaggle/python
```

**Permission denied:**
```bash
# Make the script executable
chmod +x run_notebook_locally.sh
```

## Customization

### Parameters

The notebook has configurable parameters at the top of each analysis section:

- `TOP_X`: Threshold for "top X" placements (default: 3)
- `GRADE_FILTER`: Filter by grade(s) (default: "all")
- `YEAR_FILTER`: Filter by year(s) (default: "all")
- `DISPLAY_TOP_N`: Number of results to show (default: 50)
- `SCHOOL_SEARCH`: Partial school name for search

### Modifying Code

All helper functions are defined in the "Helper Functions" section. You can:
- Modify ranking algorithms
- Add new metrics
- Change table formatting
- Add new analysis sections

## Data Schema

The notebook expects a CSV file with these columns:

| Column | Type | Description |
|--------|------|-------------|
| ev | string | Academic year (e.g., "2023-24") |
| targy | string | Subject (always "Anyanyelv") |
| iskola_nev | string | School name |
| varos | string | City |
| megye | string | County (empty in current version) |
| helyezes | integer | Final rank/placement |
| evfolyam | integer | Grade level (3-8) |

## Future Enhancements

Planned features for future versions:
- Interactive widgets (ipywidgets) for parameter selection
- Chart visualizations (Plotly)
- Advanced statistical analysis
- Export functionality

## Support

For issues or questions:
- Check the main project README
- Review the dataset README on Kaggle
- Open an issue on GitHub
```

---

### 5.3. Kaggle Dataset README Updates

**Files:** 
- `templates/kaggle/README.hu.md`
- `templates/kaggle/README.en.md`

**Changes:** Add one sentence at the end of each file

**Hungarian version (README.hu.md):**

Add before the "Licenc" section:

```markdown
## Elemzési Notebook

Az adathalmaz mellett elérhető egy Jupyter notebook is, amely interaktív elemzési példákat tartalmaz.
```

**English version (README.en.md):**

Add before the "License" section:

```markdown
## Analysis Notebook

An analysis Jupyter notebook with interactive exploration examples is available alongside this dataset.
```

---


## 6. Implementation Plan

### 6.1. Development Phases

**Phase 1: Setup and Infrastructure (1-2 hours)**
- Create `notebooks/` directory
- Create `run_notebook_locally.sh` script
- Test Docker script execution
- Create `notebooks/README.md`

**Phase 2: Notebook Structure (2-3 hours)**
- Create `competition_analysis.ipynb`
- Add all section headers (markdown cells)
- Add dual language explanations (Hungarian + English)
- Set up imports and configuration

**Phase 3: Helper Functions (3-4 hours)**
- Implement `filter_data()`
- Implement `calculate_count_ranking()`
- Implement `calculate_weighted_ranking()`
- Implement `search_schools()`
- Implement `get_school_results()`
- Implement `format_ranking_table()`
- Add comprehensive docstrings

**Phase 4: Analysis Sections (3-4 hours)**
- Implement data loading with error handling
- Implement dataset overview statistics
- Implement school rankings (count + weighted)
- Implement city rankings (count + weighted)
- Implement school search
- Apply table formatting to all outputs

**Phase 5: Testing (2-3 hours)**
- Create `tests/test_notebook_helpers.py`
- Implement all unit tests (20+ tests)
- Run tests and fix issues
- Verify notebook executes end-to-end

**Phase 6: Documentation (1-2 hours)**
- Update main `README.md`
- Update Kaggle dataset READMEs
- Review all documentation for accuracy
- Add usage examples

**Phase 7: Validation (1-2 hours)**
- Test notebook on Kaggle platform
- Test Docker script on clean environment
- Verify all links and references
- Final review of dual language content

**Total Estimated Time: 13-20 hours**

---

### 6.2. Implementation Order

**Step-by-step implementation sequence:**

1. **Create directory structure**
   ```bash
   mkdir -p notebooks
   touch notebooks/README.md
   touch run_notebook_locally.sh
   chmod +x run_notebook_locally.sh
   ```

2. **Implement Docker script**
   - Write `run_notebook_locally.sh` per specification
   - Test locally to ensure it works

3. **Create notebook skeleton**
   - Create `notebooks/competition_analysis.ipynb`
   - Add all section headers (10 sections)
   - Add placeholder markdown cells for dual language

4. **Implement helper functions**
   - Start with `filter_data()` (most critical)
   - Then ranking functions
   - Then search functions
   - Add formatting function last

5. **Create test file**
   - Create `tests/test_notebook_helpers.py`
   - Copy helper functions to test file
   - Implement tests incrementally as functions are completed
   - Run tests after each function

6. **Implement notebook sections**
   - Section 1-2: Introduction and imports
   - Section 3-4: Data loading and overview
   - Section 5: Helper functions (copy from development)
   - Section 6-9: Rankings (use helper functions)
   - Section 10: School search

7. **Add dual language content**
   - Write Hungarian explanations
   - Write English explanations
   - Review for accuracy and clarity

8. **Apply formatting**
   - Add table styling to all outputs
   - Test formatting in Jupyter
   - Adjust colors and layout as needed

9. **Update documentation**
   - Main README
   - Notebooks README
   - Kaggle READMEs

10. **Final testing**
    - Run all tests: `pytest tests/test_notebook_helpers.py -v`
    - Execute notebook end-to-end locally
    - Upload to Kaggle and test there
    - Verify Docker script on clean machine

---

### 6.3. Code Quality Checklist

Before considering implementation complete, verify:

**Code Quality:**
- [ ] All functions have docstrings
- [ ] Variable names are descriptive
- [ ] No magic numbers (use named constants)
- [ ] Error messages are clear and actionable
- [ ] Code follows PEP 8 style guidelines

**Functionality:**
- [ ] All helper functions work correctly
- [ ] Filtering handles all input types (single, list, "all")
- [ ] Ranking calculations are accurate
- [ ] Search handles edge cases (no match, multiple matches)
- [ ] Table formatting displays correctly

**Testing:**
- [ ] All unit tests pass
- [ ] Edge cases are covered
- [ ] Error conditions are tested
- [ ] Test coverage is comprehensive

**Documentation:**
- [ ] All markdown cells have dual language
- [ ] Translations are accurate
- [ ] Code comments explain complex logic
- [ ] README files are complete and accurate

**User Experience:**
- [ ] Parameters are easy to find and modify
- [ ] Error messages guide users to solutions
- [ ] Tables are readable and professional
- [ ] Notebook flows logically

**Platform Compatibility:**
- [ ] Notebook runs on Kaggle without modifications
- [ ] Docker script works on Linux/macOS
- [ ] All file paths are correct
- [ ] No external dependencies beyond pandas

---


## 7. Technical Specifications

### 7.1. Dependencies

**Required Libraries (all available in Kaggle Docker):**
- `pandas >= 1.3.0` - Data manipulation
- `IPython` - Display utilities (included in Jupyter)

**No additional installations required** - notebook uses only standard Kaggle environment.

---

### 7.2. File Paths

**Kaggle Environment:**
```python
DATA_PATH = '/kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv'
```

**Local Environment (via Docker):**
- Same path as Kaggle (Docker mounts handle this)
- No path detection needed

---

### 7.3. Data Assumptions

The notebook assumes the input CSV has:
- Semicolon (`;`) delimiter
- UTF-8 encoding
- Column names: `ev`, `targy`, `iskola_nev`, `varos`, `megye`, `helyezes`, `evfolyam`
- Grade values: 3, 4, 5, 6, 7, 8
- Year format: "YYYY-YY" (e.g., "2023-24")
- No missing values in key columns (ev, iskola_nev, varos, helyezes, evfolyam)

**Validation:** The data loading section should verify these assumptions and provide clear error messages if violated.

---

### 7.4. Performance Considerations

**Dataset Size:**
- Current: 3,233 rows
- Expected growth: ~300 rows per year
- 10-year projection: ~6,000 rows

**Performance Targets:**
- Data loading: < 1 second
- Filtering: < 0.1 seconds
- Ranking calculation: < 0.5 seconds
- Table formatting: < 0.5 seconds
- Total notebook execution: < 5 seconds

**Optimization Strategies:**
- Use vectorized pandas operations (no loops)
- Filter data once, reuse filtered dataframe
- Avoid unnecessary data copies
- Use efficient pandas methods (`.isin()`, `.groupby()`, `.agg()`)

---

### 7.5. Styling Constants

**Color Scheme:**
```python
# Hungarian/English header color
HEADER_COLOR = '#477050'  # Dark green

# Table header background
TABLE_HEADER_BG = '#477050'  # Dark green
TABLE_HEADER_TEXT = 'white'

# Gradient colormap for scores
GRADIENT_CMAP = 'YlGn'  # Yellow to Green

# Alternating row color
ALT_ROW_COLOR = '#f9f9f9'  # Light gray
```

**Typography:**
```python
FONT_SIZE = '11pt'
HEADER_FONT_WEIGHT = 'bold'
CELL_PADDING = '8px'
```

---

### 7.6. Markdown Templates

**Hungarian Section Header:**
```markdown
🇭🇺 <span style="color: #477050;">**MAGYAR**</span>

[Hungarian content here]
```

**English Section Header:**
```markdown
🇬🇧 <span style="color: #477050;">**ENGLISH**</span>

[English content here]
```

**Parameter Block:**
```python
# === CONFIGURATION PARAMETERS ===
# Adjust these values and re-run the cell to see updated results

PARAMETER_NAME = default_value  # Description
```

---

## 8. Risk Mitigation

### 8.1. Identified Risks

**Risk 1: Kaggle Environment Changes**
- **Impact:** Notebook may break if Kaggle updates Docker image
- **Mitigation:** Use only stable, core libraries (pandas)
- **Contingency:** Document Kaggle image version used

**Risk 2: Data Schema Changes**
- **Impact:** Notebook breaks if CSV schema changes
- **Mitigation:** Add schema validation in data loading
- **Contingency:** Clear error messages guide users to fix

**Risk 3: Duplication Drift**
- **Impact:** Tests and notebook functions get out of sync
- **Mitigation:** Add comment in both files noting duplication
- **Contingency:** Run tests before each release

**Risk 4: Translation Errors**
- **Impact:** Hungarian/English content may be inaccurate
- **Mitigation:** Have native speaker review translations
- **Contingency:** Users can reference English if Hungarian unclear

**Risk 5: Docker Compatibility**
- **Impact:** Script may not work on all platforms
- **Mitigation:** Test on Linux and macOS
- **Contingency:** Provide manual Docker command in README

---

### 8.2. Validation Strategy

**Pre-Release Validation:**

1. **Unit Tests**
   ```bash
   pytest tests/test_notebook_helpers.py -v
   # All tests must pass
   ```

2. **Notebook Execution**
   ```bash
   # Local execution
   ./run_notebook_locally.sh
   # Execute all cells, verify no errors
   ```

3. **Kaggle Upload**
   - Upload notebook to Kaggle
   - Attach dataset
   - Run all cells
   - Verify outputs match local execution

4. **Documentation Review**
   - Check all links work
   - Verify instructions are clear
   - Test Docker script on clean machine

5. **Code Review**
   - Check against quality checklist (section 6.3)
   - Verify dual language completeness
   - Review error messages for clarity

---

## 9. Success Criteria

### 9.1. Functional Requirements Met

- [ ] FR-001: Notebook structure with dual language ✓
- [ ] FR-002: Data loading and overview ✓
- [ ] FR-003: Configurable parameters ✓
- [ ] FR-004: Helper functions implemented ✓
- [ ] FR-005: School rankings (count-based) ✓
- [ ] FR-006: School rankings (weighted) ✓
- [ ] FR-007: City rankings (count-based) ✓
- [ ] FR-008: City rankings (weighted) ✓
- [ ] FR-009: School search with partial matching ✓
- [ ] FR-010: Dual language support ✓
- [ ] FR-011: Local execution support ✓

### 9.2. Non-Functional Requirements Met

- [ ] NFR-001: Performance (< 30 seconds total) ✓
- [ ] NFR-002: Usability (easy to modify parameters) ✓
- [ ] NFR-003: Maintainability (clean, modular code) ✓
- [ ] NFR-004: Portability (works on Kaggle and locally) ✓
- [ ] NFR-005: Educational value (readable, well-documented) ✓

### 9.3. Deliverables Complete

- [ ] `notebooks/competition_analysis.ipynb` created ✓
- [ ] `run_notebook_locally.sh` created and tested ✓
- [ ] `notebooks/README.md` created ✓
- [ ] `tests/test_notebook_helpers.py` created ✓
- [ ] Main `README.md` updated ✓
- [ ] Kaggle READMEs updated ✓
- [ ] All tests passing ✓
- [ ] Notebook runs on Kaggle ✓
- [ ] Docker script works locally ✓

---

## 10. Appendices

### 10.1. Example Notebook Cell Sequence

**Complete cell sequence for reference:**

```
Cell 1:  [Markdown] Introduction - Hungarian
Cell 2:  [Markdown] Introduction - English
Cell 3:  [Markdown] Imports - Hungarian
Cell 4:  [Markdown] Imports - English
Cell 5:  [Code] Import pandas, configure display
Cell 6:  [Markdown] Data Loading - Hungarian
Cell 7:  [Markdown] Data Loading - English
Cell 8:  [Code] Load CSV with error handling
Cell 9:  [Markdown] Dataset Overview - Hungarian
Cell 10: [Markdown] Dataset Overview - English
Cell 11: [Code] Display 4 statistics
Cell 12: [Markdown] Helper Functions - Hungarian
Cell 13: [Markdown] Helper Functions - English
Cell 14: [Code] Define all 6 helper functions
Cell 15: [Markdown] School Rankings Count - Hungarian
Cell 16: [Markdown] School Rankings Count - English
Cell 17: [Code] Parameters (TOP_X, GRADE_FILTER, YEAR_FILTER, DISPLAY_TOP_N)
Cell 18: [Code] Calculate and display count ranking
Cell 19: [Markdown] School Rankings Weighted - Hungarian
Cell 20: [Markdown] School Rankings Weighted - English
Cell 21: [Code] Calculate and display weighted ranking
Cell 22: [Markdown] City Rankings Count - Hungarian
Cell 23: [Markdown] City Rankings Count - English
Cell 24: [Code] Calculate and display count ranking
Cell 25: [Markdown] City Rankings Weighted - Hungarian
Cell 26: [Markdown] City Rankings Weighted - English
Cell 27: [Code] Calculate and display weighted ranking
Cell 28: [Markdown] School Search - Hungarian
Cell 29: [Markdown] School Search - English
Cell 30: [Code] SCHOOL_SEARCH parameter
Cell 31: [Code] Search and display results
```

**Total: 31 cells**

---

### 10.2. Sample Hungarian/English Text Pairs

**Introduction Section:**

**Hungarian:**
```markdown
# Bolyai Anyanyelvi Csapatverseny - Adatelemzés

Ez a notebook interaktív elemzési eszközöket biztosít a Bolyai Anyanyelvi Csapatverseny 
történelmi eredményeinek feltárásához. Az adathalmaz 10 év versenyeredményét tartalmazza 
(2015-16-tól 2024-25-ig).

**Mit találsz ebben a notebookban:**
- Iskolák rangsora (darabszám és súlyozott pontszám alapján)
- Városok rangsora (darabszám és súlyozott pontszám alapján)
- Iskola keresés (részleges név alapján)

**Használat:**
Minden elemzési szakaszban találsz konfigurálható paramétereket. Módosítsd az értékeket, 
majd futtasd újra a cellát az eredmények frissítéséhez.

További információ az adathalmazról: [Dataset README](link)
```

**English:**
```markdown
# Bolyai Mother Tongue Team Competition - Data Analysis

This notebook provides interactive analysis tools for exploring historical results of the 
Bolyai Mother Tongue Team Competition. The dataset contains 10 years of competition results 
(from 2015-16 to 2024-25).

**What you'll find in this notebook:**
- School rankings (by count and weighted score)
- City rankings (by count and weighted score)
- School search (by partial name)

**How to use:**
Each analysis section has configurable parameters. Modify the values and re-run the cell 
to see updated results.

For more information about the dataset: [Dataset README](link)
```

---

### 10.3. Git Commit Strategy

**Recommended commit sequence:**

```bash
# Commit 1: Infrastructure
git add run_notebook_locally.sh notebooks/README.md
git commit -m "feat(v0.2): Add Docker script and notebooks README"

# Commit 2: Notebook skeleton
git add notebooks/competition_analysis.ipynb
git commit -m "feat(v0.2): Create notebook structure with dual language"

# Commit 3: Helper functions
git add notebooks/competition_analysis.ipynb
git commit -m "feat(v0.2): Implement helper functions for filtering and ranking"

# Commit 4: Tests
git add tests/test_notebook_helpers.py
git commit -m "test(v0.2): Add unit tests for notebook helper functions"

# Commit 5: Analysis sections
git add notebooks/competition_analysis.ipynb
git commit -m "feat(v0.2): Implement ranking and search sections"

# Commit 6: Documentation
git add README.md templates/kaggle/README.*.md
git commit -m "docs(v0.2): Update documentation for notebook feature"

# Commit 7: Final polish
git add notebooks/competition_analysis.ipynb
git commit -m "style(v0.2): Apply table formatting and final polish"
```

---

## 11. Conclusion

This design document provides a complete blueprint for implementing v0.2.0 of the Hungarian Academic Competition Results Pipeline. The design prioritizes:

- **Simplicity**: Self-contained notebook, minimal infrastructure
- **Usability**: Clear parameters, formatted tables, dual language
- **Quality**: Comprehensive tests, error handling, documentation
- **Maintainability**: Clean code, modular functions, clear structure

The implementation can proceed directly from this document with all technical decisions made and specifications provided.

**Next Steps:**
1. Review and approve this design document
2. Begin implementation following Phase 1 (Setup and Infrastructure)
3. Proceed through phases sequentially
4. Validate against success criteria before release

---

**Document Version:** 1.0  
**Date:** 2025-12-21  
**Status:** Final  
**Approved By:** [Pending]  
**Implementation Start:** [TBD]
