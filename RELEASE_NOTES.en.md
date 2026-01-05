# Release Notes

This document contains user-facing release notes for the Hungarian Academic Competition Results Pipeline project.

---

## Version 0.4.0 - School Name Normalization (January 5, 2026)

### Summary
Normalizes all school names against the official Hungarian school database (KIR), adds county and region data, and dramatically improves data quality. School names are now consistent across years, and geographic analysis by county and region is now possible.

### What's New
- **Automated school name normalization**: All school names are matched against the official KIR (Köznevelési Információs Rendszer) database using fuzzy matching. Schools that changed names over time now appear under their current official name, making rankings accurate and consistent.
- **County and region data**: Every school now has county (vármegye) and region (régió) information from the KIR database. You can now analyze competition results by geographic region and compare educational outcomes across Hungary.
- **County and region rankings**: The analysis notebook now includes county and region rankings (both count-based and weighted), allowing you to see which areas of Hungary perform best in the competition.
- **Comprehensive audit trail**: Every school matching decision is documented in an audit file showing confidence scores, match methods (automatic vs manual), and explanations. Full transparency into data quality improvements.
- **Manual override system**: Edge cases and low-confidence matches can be manually corrected via a simple CSV mapping file, giving you control over data quality.

### Improvements
- **Consistent school names**: 724 schools (93%) automatically matched with high confidence. School name variations like "AMI" vs "Alapfokú Művészeti Iskola" are now unified under official names.
- **Better city names**: City names are normalized from KIR (e.g., "Budapest III. kerület" → "Budapest III."), ensuring consistency with official administrative boundaries.
- **Enhanced filtering**: School and city rankings now support filtering by county and region in addition to existing filters (year, grade, city).
- **50x faster processing**: School matching optimized from 9 minutes to 10 seconds using city-indexed lookups and pre-filtering. Total pipeline time reduced from ~24 minutes to ~15 minutes.

### Data Quality
- **School name consolidation**: 779 unique school-city combinations matched to 613 official schools. Schools that appeared under multiple names are now unified, providing accurate performance tracking.
- **Geographic data complete**: 100% of schools now have county and region information (previously 0%). All data sourced from official government database.
- **High matching confidence**: 93% of schools matched automatically with ≥90% confidence. 7% matched via manual mapping file for edge cases. Zero schools with low confidence kept in dataset.
- **Closed schools excluded**: 1 school not found in KIR database (closed) was excluded from the dataset, ensuring only active schools are included.

### Breaking Changes
- **Schema change**: Column `megye` (empty) removed. New columns `varmegye` (county) and `regio` (region) added. If you have code that references the `megye` column, update it to use `varmegye`.
- **Script renumbering**: Step 03 is now KIR database download. Previous step 03 (merger) is now step 04. Update any automation scripts accordingly.
- **Statistics changed**: Dataset now has 3,231 records (down from 3,233), 613 schools (down from 766), 260 cities (down from 261). This is due to school name consolidation and exclusion of closed schools.

### Known Limitations
- **Historical name changes not tracked**: Schools appear with their current official name from KIR. If a school changed names in 2020, all historical results show the new name.
- **Closed schools excluded**: Schools not in the current KIR database are excluded. This may affect historical analysis if schools closed between competition years.
- **Manual mapping maintenance**: The manual school mapping file requires periodic review as schools change names or close.

### Upgrade Instructions
1. Pull latest code: `git pull`
2. Install dependencies: `poetry install` (adds rapidfuzz, beautifulsoup4)
3. Download KIR database: `poetry run python 03_download_helper_data.py`
4. Re-run pipeline: `poetry run python 04_merger_and_excel.py`

### Metrics
- Total records: 3,231 (down from 3,233)
- Unique schools: 613 (down from 766 after name consolidation)
- Cities: 260 (down from 261)
- Schools matched automatically (high confidence): 661 (85%)
- Schools matched automatically (medium confidence): 63 (8%)
- Schools matched manually: 54 (7%)
- Schools excluded: 1 (0.1%)
- Tests passing: 100/100

---

## Version 0.3.0 - Data Quality & Usability (December 26, 2025)

### Summary
Improves data quality through city name cleaning and enhances notebook usability with navigation and filtering features. City names are now consistent across the dataset, making rankings more accurate and reliable.

### What's New
- **City name cleaning system**: Automatically corrects city name variations using a manual mapping file. Case inconsistencies (MISKOLC → Miskolc), suburbs (Debrecen-Józsa → Debrecen), and missing Budapest districts (Budapest → Budapest II.) are now normalized, ensuring schools from the same city appear together in rankings.
- **Standalone city checker**: Run `python -m tanulmanyi_versenyek.validation.city_checker` to detect unmapped city variations and verify data quality without running the full pipeline.
- **Notebook table of contents**: Navigate quickly to any analysis section with clickable links. A prominent warning ensures you execute setup sections (imports, data loading, helper functions) before jumping to analysis.
- **City filter for school rankings**: Filter school rankings by city to focus on specific regions. Supports single city ("Budapest II."), multiple cities (["Budapest II.", "Debrecen"]), or all cities (default).
- **Better table display**: Rankings now show the full number of rows you request (DISPLAY_TOP_N) instead of truncating to 5 top + 5 bottom. School search shows all results without truncation.

### Improvements
- **Consistent city names**: 30 corrections applied across the dataset. Schools from "MISKOLC" and "Miskolc" now appear together, providing more accurate city and school rankings.
- **Transparent data cleaning**: All city corrections are documented in a human-readable CSV file (`config/city_mapping.csv`) with explanations for each change. Valid variations (same school name in different cities) are preserved and marked as intentional.
- **Enhanced validation reporting**: Validation reports now include city mapping statistics (corrections applied, valid variations, unmapped variations), giving you full visibility into data quality improvements.

### Data Quality
- **City variations fully addressed**: 9 city name issues corrected (case normalization, suburb mapping, Budapest district additions). 13 valid variations documented and preserved (schools with same name in different cities). Zero unmapped variations remaining.
- **Improved ranking accuracy**: City rankings now show 261 cities (down from 264) because variations like "MISKOLC" and "Miskolc" are merged. School rankings are more accurate as schools no longer split across city name variations.
- **Auditable corrections**: Every city correction is documented with school name, original city, corrected city, and human explanation. You can review or modify the mapping file to suit your analysis needs.

### Known Limitations
- **School name variations not yet addressed**: Schools still appear under multiple names due to official name changes over time (e.g., "Baár-Madas Református Gimnázium és Általános Iskola" vs "Baár-Madas Református Gimnázium, Általános Iskola és Kollégium"). This is planned for a future release.
- **Manual mapping file maintenance**: City corrections require manual review and updates to the CSV file. Automated city name detection using external databases is not yet implemented.
- **No interactive widgets**: Notebook parameters must still be edited in code cells. Dropdown menus and sliders are planned for future releases.

### Metrics
- Total records: 3,233
- Unique schools: 766
- Cities: 261 (reduced from 264 after cleaning)
- City corrections applied: 30
- Valid city variations: 13
- Unmapped variations: 0
- Tests passing: 84/84

---

## Version 0.2.0 - Interactive Analysis (December 22, 2025)

### Summary
Adds a Jupyter notebook for interactive data exploration with school and city rankings, search functionality, and dual language support. The notebook runs on Kaggle or locally, making the dataset accessible to analysts and researchers.

### What's New
- **Jupyter notebook for interactive analysis**: Explore competition results with ready-to-use code cells. Modify parameters (grade level, year range, top-N) and re-run to see updated results instantly.
- **School rankings with two methods**: View top-performing schools by participation count (how many times they placed) or weighted score (configurable threshold, e.g., top-3: 1st place = 3 points, 2nd = 2 points, 3rd = 1 point). Filter by grade level and year range.
- **City rankings with two methods**: Discover which cities produce the most finalist teams, using the same count and weighted scoring approaches as school rankings.
- **School search functionality**: Find specific schools by partial name match and view their complete competition history across all years and grade levels.
- **Dual language support**: All explanations and results display in both Hungarian and English, making the dataset accessible to international researchers.
- **Multiple execution options**: Run on Kaggle platform (recommended), locally with Poetry (fast), or with Docker (exact Kaggle environment, 20GB download).

### Improvements
- **Correct school counting**: Schools now count as single entities even when city names vary across years (e.g., "Budapest" vs "Budapest II."). Previously, the same school could appear multiple times in rankings.
- **Hungarian alphabetical sorting**: School and city names now sort correctly according to Hungarian grammar rules (á treated as variant of 'a', not as separate character after 'z').
- **Deterministic tie-breaking**: When multiple schools or cities have the same count or score, they now appear in consistent alphabetical order across all runs.

### Data Quality
- **City name normalization awareness**: Documented that 15 schools have city name variations in source data (e.g., "Budapest" vs "Budapest VII."). Rankings now handle this correctly by grouping schools by name only.
- **School name variation documentation**: Identified 70+ school groups affected by official name changes over time. Added "Known Data Quality Limitations" section to dataset documentation with user recommendations.
- **Data authenticity preserved**: All data remains exactly as published on competition website. No subjective normalization applied, ensuring transparency and reproducibility.

### Bug Fixes
- Fixed ranking logic that incorrectly split schools with multiple city names into separate entries
- Fixed non-deterministic ordering when schools or cities had equal counts or scores
- Fixed incorrect Hungarian alphabetical order that placed accented characters after all ASCII letters

### Known Limitations
- **Data quality variations**: Some schools appear under multiple names due to official name changes over time (e.g., "Baár-Madas Református Gimnázium és Általános Iskola" vs "Baár-Madas Református Gimnázium, Általános Iskola és Kollégium"). Rankings count these as separate schools. See dataset documentation for details and recommendations.
- **No interactive widgets**: Parameters must be edited in code cells and re-run. Future versions may add dropdown menus and sliders for easier interaction.
- **No visualizations**: Results display as tables only. Charts and graphs are planned for future releases.
- **Manual parameter configuration**: Each analysis section requires editing configuration variables. No single control panel yet.

### Metrics
- Total records: 3,233
- Unique schools: 766
- Cities: 264
- Tests passing: 22/22
- Notebook cells: 31
- Languages supported: 2 (Hungarian, English)

---

## Version 0.1.0 - Initial MVP Release (December 20, 2025)

### Summary
Initial MVP release providing automated data collection and analysis for the Bolyai Mother Tongue Team Competition. This release covers 10 years of competition history (2015-16 through 2024-25) with a complete three-stage pipeline from web scraping to Excel reports.

### What's New
- **Automated data collection**: Downloads all available competition results from the official Bolyai website without manual intervention. The system respects server resources with 5-second delays between requests.
- **Intelligent result processing**: Automatically handles the two-round competition structure (written and oral finals), ensuring each school appears only once with their final placement. Special handling for COVID-19 years when oral finals were cancelled.
- **Excel analysis reports**: Generates ready-to-use Excel files with three worksheets: complete dataset, school rankings (by participation count), and city rankings (by number of finalist teams).
- **Data quality validation**: Produces detailed validation reports showing data completeness, duplicate handling, and quality metrics for transparency.
- **Complete historical coverage**: Processes all 6 grade levels (3rd through 8th grade) across 10 academic years, providing comprehensive historical perspective.

### Data Quality
- **Smart duplicate prevention**: The merge logic understands competition structure - preliminary positions from written finals are automatically replaced by final positions from oral finals for teams that advanced. This prevents the same school appearing twice with different placements.
- **Zero duplicates**: After intelligent merging, no duplicate records remain in the dataset. Each school-year-grade combination appears exactly once with the correct final placement.
- **Complete data coverage**: All core fields (year, subject, school name, city, placement, grade) are fully populated with no missing values. Only the county field is empty as this information is not available from the source website.

### Known Limitations
- **Single competition only**: This MVP covers only the Bolyai Mother Tongue Competition. Other subjects (math, English, etc.) and other competitions (OKTV, Zrínyi Ilona) are not yet supported.
- **No county information**: The dataset does not include county (megye) data because it's not available on the source website. A future release may add this through a city-to-county mapping database.
- **Static Excel tables**: The Excel report contains pre-calculated ranking tables rather than interactive pivot tables. Users can create their own pivot tables from the Data worksheet for custom analysis.
- **Command-line only**: The pipeline runs as three separate Python scripts. No graphical interface or web dashboard is available yet.

### Upgrade Instructions
This is the first release. To install:

```bash
# Clone the repository
git clone <repository-url>
cd tanulmanyi-versenyek

# Install dependencies
poetry install

# Install browser for web scraping (one-time setup)
poetry run playwright install chromium

# Run the pipeline
poetry run python 01_raw_downloader.py
poetry run python 02_html_parser.py
poetry run python 03_merger_and_excel.py
```

### Metrics
- Total records: 3,233
- Unique schools: 766
- Cities: 264
- Academic years covered: 10 (2015-16 through 2024-25)
- Grade levels: 6 (3rd through 8th grade)
- Tests passing: 16/16
