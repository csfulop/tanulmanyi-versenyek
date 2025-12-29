# Detailed Design Document: School Name Normalization - v0.4.0

## 1. Introduction

### 1.1. Purpose

This document provides a detailed technical design for implementing v0.4.0 of the Hungarian Academic Competition Results Pipeline. This release focuses on automated school name normalization using the official KIR database.

### 1.2. Scope

This design covers:
- KIR database download module architecture
- Simplified city mapping implementation
- School name matching algorithm and workflow
- Data schema changes and transformations
- Notebook enhancements for county/region analysis
- Testing strategy and test data management
- Documentation updates

### 1.3. Design Decisions Summary

Key architectural decisions made during design phase:

1. **KIR Downloader**: Use requests + BeautifulSoup (simpler than Playwright)
2. **Data Pipeline**: Functional approach with immutable DataFrames
3. **Audit Generation**: Separate function after matching (clear separation)
4. **Notebook Helpers**: Keep functions inline (Kaggle portability)
5. **Error Handling**: Fail fast with focused validation (only check used columns)
6. **City Checker**: Simplify in place (preserve git history)
7. **Test Data**: Committed fixture subset (fast, deterministic)
8. **Configuration**: Nested structure (better organization)
9. **Logging**: Module-level loggers (no logger parameters passed to functions)
10. **Column Creation**: Create vármegye directly (no rename from megye)
11. **Validation Report**: Enhance existing function (no separate update function)
12. **Integration Tests**: Use config overrides (no data fabrication)

### 1.4. References

- **Requirements**: `dev-history/v0.4/step1-requirements.md`
- **v0.3 Design**: `dev-history/v0.3/step2-design.md`
- **Analysis**: `!local-notes/school-name-cleaning/`

---

## 2. System Architecture

### 2.1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    v0.4.0 Architecture                       │
└─────────────────────────────────────────────────────────────┘

Step 01: Raw Downloader (unchanged)
    ↓
Step 02: HTML Parser (unchanged)
    ↓
Step 03: Download Helper Data (NEW)
    ├─→ KIR Downloader Module
    │   ├─ Scrape index page for latest URL
    │   ├─ Download Excel file
    │   └─ Save to data/helper_data/
    │
Step 04: Merger and Excel (renamed from 03, enhanced)
    ├─→ Load processed CSVs
    ├─→ Merge data
    ├─→ City Checker (simplified)
    │   └─ Apply city corrections
    ├─→ School Matcher (NEW)
    │   ├─ Load KIR database
    │   ├─ Load manual mappings
    │   ├─ Match schools (token_set_ratio)
    │   ├─ Apply matches to DataFrame
    │   └─ Generate audit file
    ├─→ Update validation report
    ├─→ Save master CSV (new schema)
    └─→ Generate Excel report (unchanged)
```

### 2.2. Module Structure

```
src/tanulmanyi_versenyek/
├── common/
│   ├── config.py           (unchanged)
│   └── logger.py           (unchanged)
├── scraper/
│   └── bolyai_downloader.py (unchanged)
├── parser/
│   └── html_parser.py      (unchanged)
├── merger/
│   └── data_merger.py      (unchanged)
├── validation/
│   ├── city_checker.py     (SIMPLIFIED)
│   └── school_matcher.py   (NEW)
└── kir_downloader/         (NEW MODULE)
    ├── __init__.py
    └── kir_scraper.py
```

### 2.3. Data Flow

```
Competition Data (CSV) ──┐
                         ├──→ Merge ──→ City Corrections ──┐
KIR Database (Excel) ────┤                                  │
                         │                                  ↓
City Mapping (CSV) ──────┤                         School Matching
                         │                                  │
School Mapping (CSV) ────┘                                  ↓
                                                    ┌───────┴────────┐
                                                    │                │
                                            Apply Matches    Generate Audit
                                                    │                │
                                                    ↓                ↓
                                            Master CSV       Audit CSV
                                         (new columns)
```

---

## 3. Configuration Design

### 3.1. Updated config.yaml Structure

```yaml
# Existing sections (unchanged)
data_source: { ... }
scraping: { ... }
logging: { ... }

# Updated paths section
paths:
  data_dir: "data"
  raw_html_dir: "data/raw_html"
  processed_csv_dir: "data/processed_csv"
  report_dir: "data/analysis_templates"
  kaggle_dir: "data/kaggle"
  helper_data_dir: "data/helper_data"                    # NEW
  master_csv: "data/kaggle/master_bolyai_anyanyelv.csv"
  validation_report: "data/validation_report.json"
  audit_file: "data/school_matching_audit.csv"           # NEW
  log_file: "data/pipeline.log"
  template_file: "templates/report_template.xlsx"
  kaggle_template_dir: "templates/kaggle"

# Updated validation section
validation:
  city_mapping_file: "config/city_mapping.csv"
  school_mapping_file: "config/school_mapping.csv"       # NEW

# NEW: KIR database configuration
kir:
  index_url: "https://kir.oktatas.hu/kirpub/index"
  locations_file: "data/helper_data/kir_feladatellatasi_helyek.xlsx"
  locations_filename_pattern: "kir_mukodo_feladatellatasi_helyek_{date}.xlsx"
  required_columns:
    - "Intézmény megnevezése"
    - "A feladatellátási hely települése"
    - "A feladatellátási hely vármegyéje"
    - "A feladatellátási hely régiója"

# NEW: Matching configuration
matching:
  high_confidence_threshold: 90
  medium_confidence_threshold: 80
  algorithm: "token_set_ratio"  # rapidfuzz algorithm to use
```

### 3.2. Configuration Access Pattern

All modules use existing `get_config()` function from `common/config.py`:

```python
from tanulmanyi_versenyek.common.config import get_config

config = get_config()
threshold = config['matching']['high_confidence_threshold']
kir_file = config['kir']['locations_file']
```

---

## 4. Module Designs

### 4.1. KIR Downloader Module

**File**: `src/tanulmanyi_versenyek/kir_downloader/kir_scraper.py`

**Purpose**: Download latest KIR facility locations Excel file.

**Dependencies**:
- requests (HTTP client)
- BeautifulSoup4 (HTML parsing)
- pathlib (file operations)

**Functions**:

```python
import logging
log = logging.getLogger(__name__.split('.')[-1])

def get_latest_kir_url(index_url: str, pattern: str) -> str:
    """
    Scrape KIR index page to find latest facility locations file URL.
    
    Args:
        index_url: URL of KIR index page
        pattern: Filename pattern to search for
    
    Returns:
        Full URL to latest Excel file
        
    Raises:
        ValueError: If file not found on index page
        requests.RequestException: If HTTP request fails
    """
    # Implementation:
    # 1. GET request to index_url
    # 2. Parse HTML with BeautifulSoup
    # 3. Find all <a> tags with href containing pattern
    # 4. Extract most recent (by date in filename)
    # 5. Construct full URL
    # 6. Return URL

def download_kir_file(url: str, output_path: Path) -> None:
    """
    Download KIR Excel file from URL.
    
    Args:
        url: Full URL to Excel file
        output_path: Where to save file
        
        
    Raises:
        requests.RequestException: If download fails
        IOError: If file write fails
    """
    # Implementation:
    # 1. GET request with stream=True
    # 2. Check response status
    # 3. Write to output_path in chunks
    # 4. Log progress (file size)

def clear_helper_data_dir(dir_path: Path) -> None:
    """
    Remove all files from helper data directory.
    
    Args:
        dir_path: Directory to clear
        
    """
    # Implementation:
    # 1. Check if directory exists
    # 2. Iterate files, delete each
    # 3. Log count of files removed

def download_latest_kir_data(config) -> Path:
    """
    Main function: Download latest KIR data.
    
    Args:
        config: Configuration dictionary
        
        
    Returns:
        Path to downloaded file
        
    Raises:
        Exception: If any step fails
    """
    # Implementation:
    # 1. Clear helper data directory
    # 2. Get latest URL from index page
    # 3. Download file
    # 4. Return path
```

**Error Handling**:
- Network errors: Log and raise (fail fast)
- File not found on index: Log and raise with clear message
- Write errors: Log and raise

**Logging**:
- INFO: Start download, file found, download complete, file size
- ERROR: Network failures, file not found, write failures

---

### 4.2. Simplified City Checker Module

**File**: `src/tanulmanyi_versenyek/validation/city_checker.py` (SIMPLIFIED)

**Purpose**: Apply simple city-to-city corrections before school matching.

**Changes from v0.3**:
- Remove composite key logic (school_name, city)
- Remove variation detection functions
- Simplify to city-only mapping

**Functions to Keep** (simplified):

```python
def _parse_mapping_csv(filepath: Path) -> Dict[str, str]:
    """
    Parse city mapping CSV into simple dictionary.
    
    Args:
        filepath: Path to city_mapping.csv
        
        
    Returns:
        Dictionary: {original_city: corrected_city}
        Empty dict on error
        
    Format:
        original_city;corrected_city;comment
        MISKOLC;Miskolc;Normalize case
        Debrecen-Józsa;Debrecen;Map suburb
    """
    # Implementation:
    # 1. Read CSV with pandas (sep=';', encoding='utf-8')
    # 2. Check for required columns: original_city, corrected_city
    # 3. Build dict: {row['original_city']: row['corrected_city']}
    # 4. Skip rows where corrected_city is empty
    # 5. Return dict

def load_city_mapping(config) -> Dict[str, str]:
    """
    Load city mapping from config file.
    
    Args:
        config: Configuration dictionary
        
        
    Returns:
        Dictionary of city mappings, empty if file missing/invalid
    """
    # Implementation:
    # 1. Get filepath from config['validation']['city_mapping_file']
    # 2. Check if file exists
    # 3. If not: log INFO "No city mapping file", return {}
    # 4. Call _parse_mapping_csv()
    # 5. Log INFO "Loaded N city mappings"
    # 6. Return mapping dict

def apply_city_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Apply city corrections to DataFrame.
    
    Args:
        df: DataFrame with 'varos' column
        mapping: City mapping dictionary
        
        
    Returns:
        New DataFrame with corrected cities
    """
    # Implementation:
    # 1. Create copy of DataFrame
    # 2. For each row where varos in mapping:
    #    - Log DEBUG: "Applied: {original} → {corrected}"
    #    - Update varos column
    # 3. Count corrections applied
    # 4. Log INFO: "Applied N city corrections"
    # 5. Return new DataFrame
```

**Functions to Remove**:
- `check_city_variations()` - No longer needed
- `_detect_variations()` - No longer needed
- All composite key logic

**Error Handling**:
- Missing file: Log INFO, return empty dict (graceful)
- Malformed CSV: Log ERROR, return empty dict
- Missing columns: Log ERROR, return empty dict

---

### 4.3. School Matcher Module

**File**: `src/tanulmanyi_versenyek/validation/school_matcher.py` (NEW)

**Purpose**: Match competition school names to official KIR database.

**Dependencies**:
- rapidfuzz (fuzzy string matching)
- pandas (data manipulation)
- pathlib (file operations)

**Module-level logger**:
```python
import logging
log = logging.getLogger(__name__.split('.')[-1])
```

**Core Functions**:

```python
def load_kir_database(config) -> pd.DataFrame:
    """
    Load and validate KIR facility locations Excel file.
    
    Args:
        config: Configuration dictionary
        
        
    Returns:
        DataFrame with KIR data
        
    Raises:
        FileNotFoundError: If KIR file doesn't exist
        ValueError: If required columns missing
    """
    # Implementation:
    # 1. Get filepath from config['kir']['locations_file']
    # 2. Check file exists, raise FileNotFoundError if not
    # 3. Load Excel with pandas
    # 4. Get required columns from config['kir']['required_columns']
    # 5. Validate all required columns present
    # 6. If missing: raise ValueError with clear message
    # 7. Log INFO: "Loaded N schools from KIR database"
    # 8. Return DataFrame

def load_school_mapping(config) -> Dict[Tuple[str, str], dict]:
    """
    Load manual school mapping file.
    
    Args:
        config: Configuration dictionary
        
        
    Returns:
        Dictionary keyed by (school_name, city) with values:
        {
            "corrected_school_name": str,
            "matched_city": str,
            "matched_county": str,
            "matched_region": str,
            "comment": str
        }
        Empty dict if file doesn't exist
    """
    # Implementation:
    # 1. Get filepath from config['validation']['school_mapping_file']
    # 2. Check if file exists, return {} if not
    # 3. Read CSV (sep=';', encoding='utf-8')
    # 4. Validate columns: school_name, city, corrected_school_name, comment
    # 5. For each row:
    #    - Look up corrected_school_name in KIR to get city/county/region
    #    - Build dict entry
    # 6. Log INFO: "Loaded N manual school mappings"
    # 7. Return dict

def normalize_city(city: str) -> str:
    """
    Normalize city name for comparison.
    
    Args:
        city: City name
        
    Returns:
        Normalized city name (lowercase, no " kerület")
    """
    # Implementation:
    # 1. Handle NaN/None → return ""
    # 2. Strip whitespace
    # 3. Lowercase
    # 4. Remove " kerület" and " ker." suffixes
    # 5. Return normalized string

def cities_match(our_city: str, kir_city: str) -> bool:
    """
    Check if two cities match (with Budapest special case).
    
    Args:
        our_city: City from competition data
        kir_city: City from KIR database
        
    Returns:
        True if cities match
    """
    # Implementation:
    # 1. Normalize both cities
    # 2. If exact match: return True
    # 3. If our_city == "budapest" and kir_city starts with "budapest": return True
    # 4. Otherwise: return False

def match_school(
    our_name: str,
    our_city: str,
    kir_df: pd.DataFrame,
    manual_mapping: Dict,
    config,
    log
) -> Optional[dict]:
    """
    Find best match for a school in KIR database.
    
    Args:
        our_name: School name from competition data
        our_city: City from competition data (after city corrections)
        kir_df: KIR database DataFrame
        manual_mapping: Manual override mappings
        config: Configuration dictionary
        
        
    Returns:
        Match dict with keys:
        {
            "matched_school_name": str,
            "matched_city": str,
            "matched_county": str,
            "matched_region": str,
            "confidence_score": float,
            "match_method": str  # "MANUAL", "AUTO_HIGH", "AUTO_MEDIUM"
        }
        None if no match found or score too low
    """
    # Implementation:
    # 1. Check manual_mapping for (our_name, our_city)
    #    - If found: return with match_method="MANUAL", no score
    # 
    # 2. Filter KIR candidates by city:
    #    - For each row in kir_df:
    #      - If cities_match(our_city, kir_city): add to candidates
    # 
    # 3. If no candidates: return None
    # 
    # 4. Calculate token_set_ratio for each candidate:
    #    - Use rapidfuzz.fuzz.token_set_ratio(our_name, kir_name)
    #    - Store (kir_row, score) tuples
    # 
    # 5. Find best match (highest score)
    # 
    # 6. Get thresholds from config:
    #    - medium_threshold = config['matching']['medium_confidence_threshold']
    #    - high_threshold = config['matching']['high_confidence_threshold']
    # 
    # 7. If score < medium_threshold: return None
    # 
    # 8. Determine match_method:
    #    - If score >= high_threshold: "AUTO_HIGH"
    #    - Else: "AUTO_MEDIUM"
    # 
    # 9. Extract data from best match row:
    #    - matched_school_name = row["Intézmény megnevezése"]
    #    - matched_city = row["A feladatellátási hely települése"]
    #    - matched_county = row["A feladatellátási hely vármegyéje"]
    #    - matched_region = row["A feladatellátási hely régiója"]
    # 
    # 10. Return match dict

def match_all_schools(
    our_df: pd.DataFrame,
    kir_df: pd.DataFrame,
    manual_mapping: Dict,
    config,
    log
) -> pd.DataFrame:
    """
    Match all unique schools in competition data to KIR.
    
    Args:
        our_df: Competition data DataFrame
        kir_df: KIR database DataFrame
        manual_mapping: Manual override mappings
        config: Configuration dictionary
        
        
    Returns:
        DataFrame with columns:
        - our_school_name
        - our_city
        - matched_school_name (or None)
        - matched_city (or None)
        - matched_county (or None)
        - matched_region (or None)
        - confidence_score (or None)
        - match_method ("MANUAL", "AUTO_HIGH", "AUTO_MEDIUM", "DROPPED")
        - status ("APPLIED" or "NOT_APPLIED")
    """
    # Implementation:
    # 1. Get unique (iskola_nev, varos) combinations from our_df
    # 
    # 2. Initialize results list
    # 
    # 3. For each unique (school, city):
    #    - Call match_school()
    #    - If match found:
    #      - Add to results with status="APPLIED"
    #    - If no match:
    #      - Add to results with match_method="DROPPED", status="NOT_APPLIED"
    # 
    # 4. Convert results to DataFrame
    # 
    # 5. Count statistics:
    #    - manual_count = len(df[df.match_method == "MANUAL"])
    #    - auto_high_count = len(df[df.match_method == "AUTO_HIGH"])
    #    - auto_medium_count = len(df[df.match_method == "AUTO_MEDIUM"])
    #    - dropped_count = len(df[df.match_method == "DROPPED"])
    # 
    # 6. Log INFO: "Matched N schools: M manual, H high-conf, L medium-conf, D dropped"
    # 
    # 7. Return results DataFrame

def apply_matches(
    our_df: pd.DataFrame,
    match_results: pd.DataFrame,
    log
) -> pd.DataFrame:
    """
    Apply school matches to competition DataFrame.
    
    Args:
        our_df: Competition data DataFrame
        match_results: Results from match_all_schools()
        
        
    Returns:
        New DataFrame with:
        - Updated iskola_nev (matched school names)
        - Updated varos (normalized KIR cities)
        - New vármegye column
        - New régió column
        - Dropped schools removed
    """
    # Implementation:
    # 1. Create copy of our_df
    # 
    # 2. Add new columns: vármegye, régió (initialize as None)
    # 
    # 3. For each row in our_df:
    #    - Get (iskola_nev, varos) key
    #    - Look up in match_results
    #    
    #    - If status == "APPLIED":
    #      - Update iskola_nev = matched_school_name
    #      - Update varos = normalize_city(matched_city)  # Remove " kerület"
    #      - Set vármegye = matched_county
    #      - Set régió = matched_region
    #    
    #    - If status == "NOT_APPLIED":
    #      - Mark row for removal
    # 
    # 4. Remove marked rows (dropped schools)
    # 
    # 5. Count applied and dropped
    # 
    # 6. Log INFO: "Applied N matches, dropped M schools"
    # 
    # 7. Return new DataFrame

def generate_audit_file(
    match_results: pd.DataFrame,
    output_path: Path,
    log
) -> None:
    """
    Generate audit CSV file from match results.
    
    Args:
        match_results: Results from match_all_schools()
        output_path: Where to save audit file
        
    """
    # Implementation:
    # 1. Create copy of match_results
    # 
    # 2. Add 'comment' column:
    #    - For MANUAL: copy from manual_mapping
    #    - For AUTO_*: empty or "Auto-matched"
    #    - For DROPPED: "Low confidence - needs manual review"
    # 
    # 3. Sort by match_method, then our_school_name
    # 
    # 4. Save to CSV (sep=';', encoding='utf-8', index=False)
    # 
    # 5. Log INFO: "Generated audit file: N schools, M applied, K dropped"
```

**Error Handling**:
- KIR file missing: Raise FileNotFoundError with clear message
- KIR schema invalid: Raise ValueError listing missing columns
- Manual mapping file missing: Log INFO, continue without (graceful)
- Malformed manual mapping: Log ERROR, skip invalid rows

**Logging**:
- INFO: Summary statistics (total matched, manual/auto/dropped counts), file operations
- ERROR: File not found, schema validation failures
- WARNING: Unmapped schools, low confidence matches
- ERROR: File errors, schema validation failures

---

## 5. Script Designs

### 5.1. Script 03: Download Helper Data

**File**: `03_download_helper_data.py` (NEW)

**Purpose**: Download latest KIR database file.

**Structure**:

```python
#!/usr/bin/env python3
"""Download helper data files (KIR database) for school matching."""

import logging
from pathlib import Path

from tanulmanyi_versenyek.common.config import get_config
from tanulmanyi_versenyek.common.logger import setup_logging
from tanulmanyi_versenyek.kir_downloader.kir_scraper import download_latest_kir_data

log = logging.getLogger(__name__.split('.')[-1])


def main():
    """Main entry point for helper data download."""
    # 1. Setup logging
    setup_logging()
    log.info("=" * 80)
    log.info("STEP 03: Download Helper Data")
    log.info("=" * 80)
    
    # 2. Load configuration
    config = get_config()
    
    # 3. Create helper data directory if needed
    helper_dir = Path(config['paths']['helper_data_dir'])
    helper_dir.mkdir(parents=True, exist_ok=True)
    
    # 4. Download KIR data
    try:
        kir_file = download_latest_kir_data(config)
        log.info(f"Successfully downloaded KIR data to: {kir_file}")
    except Exception as e:
        log.error(f"Failed to download KIR data: {e}")
        return 1
    
    log.info("=" * 80)
    log.info("Helper data download complete")
    log.info("=" * 80)
    return 0


if __name__ == "__main__":
    exit(main())
```

**Error Handling**:
- Network errors: Log and exit with code 1
- File write errors: Log and exit with code 1
- All errors: Clear message about what failed

---

### 5.2. Script 04: Merger and Excel (UPDATED)

**File**: `04_merger_and_excel.py` (renamed from `03_merger_and_excel.py`)

**Purpose**: Merge CSVs, apply school matching, generate outputs.

**Changes from v0.3**:
1. Rename file (03 → 04)
2. Add KIR file validation
3. Add city mapping step
4. Add school matching workflow
5. Update schema (rename megye → vármegye, add régió)
6. Generate audit file

**Updated Workflow**:

```python
#!/usr/bin/env python3
"""Merge processed CSVs, match schools, generate master CSV and reports."""

import logging
from pathlib import Path

from tanulmanyi_versenyek.common.config import get_config
from tanulmanyi_versenyek.common.logger import setup_logging
from tanulmanyi_versenyek.merger.data_merger import merge_processed_data
from tanulmanyi_versenyek.validation.city_checker import (
    load_city_mapping,
    apply_city_mapping
)
from tanulmanyi_versenyek.validation.school_matcher import (
    load_kir_database,
    load_school_mapping,
    match_all_schools,
    apply_matches,
    generate_audit_file
)

log = logging.getLogger(__name__.split('.')[-1])


def validate_kir_file_exists(config) -> None:
    """Validate KIR file exists before proceeding."""
    kir_file = Path(config['kir']['locations_file'])
    if not kir_file.exists():
        raise FileNotFoundError(
            f"KIR database file not found: {kir_file}\n"
            f"Please run: poetry run python 03_download_helper_data.py"
        )


def generate_validation_report(config, master_df, match_results=None):
    """
    Generate validation report with optional school matching statistics.
    
    Args:
        config: Configuration dictionary
        master_df: Master DataFrame
        match_results: Optional DataFrame with matching results from match_all_schools()
    """
    # Implementation:
    # 1. Generate standard validation statistics (existing logic)
    # 2. If match_results provided:
    #    - Add school_matching section with statistics:
    #      - total_schools
    #      - manual_matches
    #      - auto_high_confidence
    #      - auto_medium_confidence
    #      - dropped_low_confidence
    #      - records_kept (len(master_df))
    #      - records_dropped (original_count - len(master_df))
    # 3. Save to validation_report.json


def main():
    """Main entry point for merger and analysis."""
    # 1. Setup logging
    setup_logging()
    log.info("=" * 80)
    log.info("STEP 04: Merge Data and Generate Reports")
    log.info("=" * 80)
    
    # 2. Load configuration
    config = get_config()
    
    # 3. Validate KIR file exists
    try:
        validate_kir_file_exists(config)
    except FileNotFoundError as e:
        log.error(str(e))
        return 1
    
    # 4. Merge processed CSVs
    log.info("Merging processed CSV files...")
    master_df, dup_count = merge_processed_data(config)
    log.info(f"Merged data: {len(master_df)} records, {dup_count} duplicates removed")
    original_count = len(master_df)
    
    # 5. Apply city corrections
    log.info("Applying city corrections...")
    city_mapping = load_city_mapping(config)
    master_df = apply_city_mapping(master_df, city_mapping)
    
    # 6. Load KIR database
    log.info("Loading KIR database...")
    try:
        kir_df = load_kir_database(config)
    except (FileNotFoundError, ValueError) as e:
        log.error(f"Failed to load KIR database: {e}")
        return 1
    
    # 7. Load manual school mappings
    log.info("Loading manual school mappings...")
    school_mapping = load_school_mapping(config)
    
    # 8. Match schools
    log.info("Matching schools to KIR database...")
    match_results = match_all_schools(master_df, kir_df, school_mapping, config)
    
    # 9. Apply matches to DataFrame (creates vármegye and régió columns)
    log.info("Applying school matches...")
    master_df = apply_matches(master_df, match_results)
    final_count = len(master_df)
    
    # 10. Generate audit file
    log.info("Generating audit file...")
    audit_path = Path(config['paths']['audit_file'])
    generate_audit_file(match_results, audit_path)
    
    # 11. Generate validation report (with school matching stats)
    log.info("Generating validation report...")
    generate_validation_report(config, master_df, match_results)
    
    # 12. Save master CSV
    log.info("Saving master CSV...")
    master_csv_path = Path(config['paths']['master_csv'])
    master_df.to_csv(master_csv_path, sep=';', encoding='utf-8', index=False)
    log.info(f"Saved master CSV: {len(master_df)} records")
    
    # 13. Generate Excel report (existing logic - unchanged)
    log.info("Generating Excel report...")
    # ... existing Excel generation code ...
    
    log.info("=" * 80)
    log.info("Pipeline complete")
    log.info("=" * 80)
    return 0


if __name__ == "__main__":
    exit(main())
```

**Error Handling**:
- KIR file missing: Clear error message, exit code 1
- KIR schema invalid: Clear error message, exit code 1
- Other errors: Log and continue where possible

---

## 6. Data Schema Design

### 6.1. Master CSV Schema Changes

**Current Schema (v0.3)**:
```csv
ev;targy;iskola_nev;varos;megye;helyezes;evfolyam
```

**New Schema (v0.4)**:
```csv
ev;targy;iskola_nev;varos;vármegye;régió;helyezes;evfolyam
```

**Changes**:
1. **Rename**: `megye` → `vármegye`
2. **Add**: `régió` column
3. **Update**: `iskola_nev` values (matched to KIR)
4. **Update**: `varos` values (normalized, no " kerület")

**Column Definitions**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| ev | String | Academic year | "2024-25" |
| targy | String | Subject | "Anyanyelv" |
| iskola_nev | String | School name (from KIR) | "Abádszalóki Kovács Mihály Általános Iskola" |
| varos | String | City (normalized) | "Budapest III." (not "Budapest III. kerület") |
| vármegye | String | County (from KIR) | "Jász-Nagykun-Szolnok" |
| régió | String | Region (from KIR) | "Észak-Alföld" |
| helyezes | Integer | Final placement | 1 |
| evfolyam | Integer | Grade level | 8 |

### 6.2. Audit File Schema

**File**: `data/school_matching_audit.csv`

**Schema**:
```csv
our_school_name;our_city;matched_school_name;matched_city;confidence_score;match_method;status;comment
```

**Column Definitions**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| our_school_name | String | Original name from competition | "Apáczai Csere János Gyakorló..." |
| our_city | String | City after city corrections | "Nyíregyháza" |
| matched_school_name | String | KIR school name (or empty) | "Nyíregyházi Apáczai Csere János..." |
| matched_city | String | KIR city (or empty) | "Nyíregyháza" |
| confidence_score | Float | Match score 0-100 (or empty) | 88.9 |
| match_method | String | MANUAL, AUTO_HIGH, AUTO_MEDIUM, DROPPED | "AUTO_MEDIUM" |
| status | String | APPLIED or NOT_APPLIED | "APPLIED" |
| comment | String | Explanation | "Auto-matched" or "Low confidence..." |

### 6.3. Validation Report Schema Update

**File**: `data/validation_report.json`

**New Section**:
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

---

## 7. Notebook Design

### 7.1. New Sections

**Location**: `notebooks/competition_analysis.ipynb`

**New Sections to Add** (after existing City Rankings):

1. **County Rankings (Count-based)**
   - Bilingual title: HU + EN
   - Parameters: DISPLAY_TOP_N, YEAR_FILTER, GRADE_FILTER, REGION_FILTER
   - Logic: Group by vármegye, count teams
   - Sort: Count desc, then name (Hungarian sort)

2. **County Rankings (Weighted)**
   - Same parameters
   - Logic: Sum of (max_helyezes - helyezes + 1) per year/grade
   - Sort: Score desc, then name

3. **Region Rankings (Count-based)**
   - Parameters: DISPLAY_TOP_N, YEAR_FILTER, GRADE_FILTER (no REGION_FILTER)
   - Logic: Group by régió, count teams
   - Sort: Count desc, then name

4. **Region Rankings (Weighted)**
   - Same parameters
   - Logic: Weighted score
   - Sort: Score desc, then name

### 7.2. Filter Updates

**Existing Sections to Update**:

1. **School Rankings (Count + Weighted)**
   - Add: COUNTY_FILTER parameter
   - Add: REGION_FILTER parameter
   - Keep: CITY_FILTER, YEAR_FILTER, GRADE_FILTER

2. **City Rankings (Count + Weighted)**
   - Add: COUNTY_FILTER parameter
   - Add: REGION_FILTER parameter
   - Keep: YEAR_FILTER, GRADE_FILTER
   - No CITY_FILTER (doesn't make sense)

### 7.3. Filter Implementation Pattern

**Inline Helper Function** (add to notebook):

```python
def apply_filters(df, year_filter="all", grade_filter="all", 
                  city_filter="all", county_filter="all", region_filter="all"):
    """
    Apply filters to DataFrame.
    
    Args:
        df: DataFrame to filter
        *_filter: "all" or string or list of values
        
    Returns:
        Filtered DataFrame
    """
    result = df.copy()
    
    # Year filter
    if year_filter != "all":
        if isinstance(year_filter, str):
            result = result[result['ev'] == year_filter]
        else:  # list
            result = result[result['ev'].isin(year_filter)]
    
    # Grade filter
    if grade_filter != "all":
        if isinstance(grade_filter, (int, str)):
            result = result[result['evfolyam'] == int(grade_filter)]
        else:  # list
            result = result[result['evfolyam'].isin([int(g) for g in grade_filter])]
    
    # City filter
    if city_filter != "all":
        if isinstance(city_filter, str):
            result = result[result['varos'] == city_filter]
        else:  # list
            result = result[result['varos'].isin(city_filter)]
    
    # County filter
    if county_filter != "all":
        if isinstance(county_filter, str):
            result = result[result['vármegye'] == county_filter]
        else:  # list
            result = result[result['vármegye'].isin(county_filter)]
    
    # Region filter
    if region_filter != "all":
        if isinstance(region_filter, str):
            result = result[result['régió'] == region_filter]
        else:  # list
            result = result[result['régió'].isin(region_filter)]
    
    return result
```

**Hungarian Sort Helper** (already exists, keep):

```python
def hungarian_sort_key(text):
    """Create sort key for Hungarian text (normalize accents)."""
    # ... existing implementation ...
```

### 7.4. Pandas Display Settings

For all ranking sections, wrap display with:

```python
# Save original setting
original_max_rows = pd.options.display.max_rows

# Set to DISPLAY_TOP_N
pd.options.display.max_rows = DISPLAY_TOP_N

# Display DataFrame
display(ranking_df)

# Restore original setting
pd.options.display.max_rows = original_max_rows
```

---

## 8. Testing Strategy

### 8.1. Test Data Management

**KIR Test Fixture**:
- **Location**: `tests/fixtures/kir_sample.xlsx`
- **Content**: Subset of real KIR data (~100 schools)
- **Selection criteria**: Include schools from our competition data for realistic testing
- **Committed to git**: Yes (deterministic tests)

**Competition Test Data**:
- **Location**: `tests/test_data/` (existing)
- **Use existing fixtures**: Sample CSVs from v0.3

### 8.2. Unit Tests

**File**: `tests/test_school_matcher.py` (NEW)

**Test Coverage**:

```python
class TestCityNormalization:
    def test_normalize_city_basic()
    def test_normalize_city_budapest_kerulet()
    def test_normalize_city_none()
    def test_cities_match_exact()
    def test_cities_match_budapest_special_case()
    def test_cities_match_different()

class TestSchoolMapping:
    def test_load_school_mapping_valid_file()
    def test_load_school_mapping_missing_file()
    def test_load_school_mapping_malformed()

class TestKIRDatabase:
    def test_load_kir_database_valid()
    def test_load_kir_database_missing_file()
    def test_load_kir_database_missing_columns()

class TestSchoolMatching:
    def test_match_school_manual_override()
    def test_match_school_high_confidence()
    def test_match_school_medium_confidence()
    def test_match_school_low_confidence_dropped()
    def test_match_school_no_candidates()
    def test_match_school_budapest_no_district()
    
class TestMatchApplication:
    def test_apply_matches_updates_columns()
    def test_apply_matches_drops_unmatched()
    def test_apply_matches_normalizes_city()

class TestAuditGeneration:
    def test_generate_audit_file_structure()
    def test_generate_audit_file_comments()
```

**Test Fixtures**:
- Use `tests/fixtures/kir_sample.xlsx`
- Create sample school_mapping.csv in tests
- Use existing competition data samples

---

**File**: `tests/test_city_checker.py` (UPDATE)

**Changes**:
- Remove composite key tests
- Remove variation detection tests
- Update to simple city-only mapping
- Test new simplified functions

---

**File**: `tests/test_notebook_helpers.py` (UPDATE)

**New Test Coverage**:

```python
class TestFilters:
    def test_apply_filters_year_string()
    def test_apply_filters_year_list()
    def test_apply_filters_grade_int()
    def test_apply_filters_grade_list()
    def test_apply_filters_city_string()
    def test_apply_filters_city_list()
    def test_apply_filters_county_string()      # NEW
    def test_apply_filters_county_list()        # NEW
    def test_apply_filters_region_string()      # NEW
    def test_apply_filters_region_list()        # NEW
    def test_apply_filters_combined()
    def test_apply_filters_all()
```

### 8.3. Integration Tests

**File**: `tests/test_integration.py` (UPDATE)

**New Test Scenarios**:

```python
def test_full_pipeline_with_kir():
    """Test complete pipeline from merge to final output."""
    # 1. Run merge with real data
    # 2. Apply city corrections
    # 3. Match schools with KIR fixture
    # 4. Verify audit file generated
    # 5. Verify master CSV has new columns
    # 6. Verify validation report updated

def test_pipeline_kir_file_missing():
    """Test that pipeline fails gracefully if KIR missing."""
    # 1. Remove KIR file
    # 2. Run step 04
    # 3. Verify exits with error code 1
    # 4. Verify error message is clear

def test_manual_mapping_override():
    """Test that manual mappings override automatic matches."""
    # Use one known result file (e.g., anyanyelv_2024-25_8.-osztaly_szobeli-donto.csv)
    # 1. Create school_mapping.csv with override for one known school
    # 2. Run matching
    # 3. Verify manual mapping used (not automatic)
    # 4. Verify audit file shows MANUAL method

def test_dropped_schools_removed():
    """Test that low-confidence schools are dropped with high thresholds."""
    # Use real data with artificially high thresholds in test config
    # 1. Override config with very high thresholds:
    #    matching:
    #      high_confidence_threshold: 99
    #      medium_confidence_threshold: 98
    # 2. Run matching with test config
    # 3. Verify some schools were dropped (final count < original count)
    # 4. Verify audit file shows DROPPED status for low-confidence matches
    # 5. Verify dropped schools not in final DataFrame
```

### 8.4. Test Execution

**Unit tests** (fast):
```bash
pytest tests/test_school_matcher.py -v
pytest tests/test_city_checker.py -v
pytest tests/test_notebook_helpers.py -v
```

**Integration tests** (slower):
```bash
pytest tests/test_integration.py -v
```

**All tests**:
```bash
pytest tests/ -v
```

---

## 9. Error Handling Strategy

### 9.1. Error Categories

**Critical Errors (Fail Fast)**:
- KIR file missing → Exit with code 1, clear message
- KIR schema invalid → Exit with code 1, list missing columns
- Config file malformed → Exit with code 1

**Recoverable Errors (Log and Continue)**:
- City mapping file missing → Log INFO, continue without corrections
- School mapping file missing → Log INFO, continue without manual overrides
- Malformed mapping file → Log ERROR, skip invalid rows

**Warnings (Log Only)**:
- Low confidence matches → Log WARNING, add to audit as DROPPED
- No candidates found → Log WARNING, add to audit as DROPPED

### 9.2. Error Messages

All error messages must be:
- **Clear**: Explain what went wrong
- **Actionable**: Tell user how to fix
- **Contextual**: Include relevant details (file path, missing columns, etc.)

**Examples**:

```python
# Good error message
raise FileNotFoundError(
    f"KIR database file not found: {kir_file}\n"
    f"Please run: poetry run python 03_download_helper_data.py"
)

# Good validation error
raise ValueError(
    f"KIR database missing required columns.\n"
    f"Expected: {required_columns}\n"
    f"Found: {list(kir_df.columns)}"
)
```

---

