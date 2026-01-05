# Bolyai Hungarian Mother Tongue Team Competition Results (2015-2025)

## Dataset Description

This dataset contains 10 years of historical results from the **Bolyai Hungarian Mother Tongue Team Competition** (Bolyai Anyanyelvi Csapatverseny), one of Hungary's most prestigious elementary and high school academic competitions.

**What's Inside:**
- 3,231 competition results from 2015-16 to 2024-25
- 613 different schools from 260 cities across Hungary
- Team rankings for grades 3-8
- Both written finals (Írásbeli döntő) and oral finals (Szóbeli döntő)
- School names normalized against official Hungarian school database (KIR)
- County (vármegye) and region (régió) data for all schools
- Interactive Jupyter notebook for data exploration
- Bilingual documentation (Hungarian and English)

**Context:**
The Bolyai Competition tests Hungarian language skills through team-based challenges, organized annually for students in grades 3-8. This dataset represents a decade of competitive academic achievement in Hungary's education system.

**Use Cases:**
- Analyze school performance trends over time
- Compare regional educational outcomes
- Identify top-performing schools, cities, counties and regions
- Study competition participation patterns
- Educational data visualization projects

## Files in This Dataset

### `master_bolyai_anyanyelv.csv`
Complete dataset of Bolyai Mother Tongue Competition results (2015-2025). Contains 3,231 records with school names normalized against the official Hungarian school database (KIR), cities, counties, regions, rankings, grades, and academic years. Semicolon-separated format, UTF-8 encoding. Main data file for analysis.

### `README.hu.md`
Hungarian language documentation. Includes dataset description, data collection methodology, column definitions, usage examples, known data quality limitations, and license information. Complete reference guide in Hungarian.

### `README.en.md`
English language documentation. Includes dataset description, data collection methodology, column definitions, usage examples, known data quality limitations, and license information. Complete reference guide in English.

### `LICENSE`
Creative Commons Attribution 4.0 International (CC BY 4.0) license. Specifies terms of use, attribution requirements, and permissions for the dataset. Free to use with proper attribution.

## Data Provenance

### Sources

**Competition Results:** Official Bolyai Competition website - https://magyar.bolyaiverseny.hu/verseny/archivum/eredmenyek.php

**School Data:** KIR (Köznevelési Információs Rendszer) official database - https://kir.oktatas.hu/kirpub/index

Data represents official competition results and school information published by the organizers for public access.

### Collection Methodology

Automated web scraping using Python with Playwright library for browser automation and BeautifulSoup for HTML parsing.

**Process:**
1. Automated navigation through competition result pages for all academic years (2015-16 to 2024-25) and grade levels (3-8)
2. Respectful data collection with 5-second delays between requests to avoid server overload
3. HTML table extraction and parsing into structured format
4. School name normalization using official Hungarian school database (KIR - Köznevelési Információs Rendszer)
5. Fuzzy matching algorithm (token_set_ratio) to match competition school names to official KIR names
6. Four-stage pipeline: (a) raw HTML download, (b) data extraction, (c) KIR database download, (d) school matching and merging
7. Quality validation: automated checks for completeness and consistency

**Deduplication logic:** Oral finals results (final placements) take precedence over written finals results (preliminary placements) when both exist for the same team.

**Output:** Semicolon-separated CSV file with UTF-8 encoding.

**Collection date:** January 2026

## Dataset Structure

### File: `master_bolyai_anyanyelv.csv`

A semicolon-separated CSV file containing all competition results.

**Columns:**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `ev` | String | Academic year of the competition (format: "YYYY-YY") | "2024-25" |
| `targy` | String | Subject (always "Anyanyelv" = Mother Tongue) | "Anyanyelv" |
| `iskola_nev` | String | Official name of the school (from KIR database) | "Abádszalóki Kovács Mihály Általános Iskola" |
| `varos` | String | City where the school is located, includes district number for Budapest (normalized from KIR) | "Budapest III." or "Debrecen" |
| `varmegye` | String | County where the school is located (from KIR database) | "Jász-Nagykun-Szolnok" |
| `regio` | String | Region where the school is located (from KIR database) | "Észak-Alföld" |
| `helyezes` | Integer | Final rank/placement achieved | 1 |
| `evfolyam` | Integer | Grade level (3-8) | 8 |

**Note on school names**: All school names have been normalized against the official Hungarian school database (KIR - Köznevelési Információs Rendszer) using fuzzy matching. This ensures consistency across years even when schools change names or have minor variations in competition records.

**Note on geographic data**: County (vármegye) and region (régió) data comes from the KIR database and represents the official administrative location of each school.

## Data Collection Methodology

### Source
Data was collected from the official Bolyai Competition website: https://magyar.bolyaiverseny.hu/verseny/archivum/eredmenyek.php

### Collection Process
- **Automated web scraping** using Playwright (Python)
- **Polite scraping practices**: 5-second delays between requests
- **Data extraction**: HTML table parsing with BeautifulSoup
- **Data validation**: Automated quality checks and deduplication

### Competition Structure

The Bolyai Competition has two rounds:

1. **Írásbeli döntő (Written Finals)**: All qualifying teams compete. Results show preliminary rankings.
2. **Szóbeli döntő (Oral Finals)**: Top 6 teams from each grade category advance. Results show final rankings.

**Important**: Teams that advance to the oral finals appear only once in this dataset with their **final placement** from the oral round. Teams that did not advance appear with their placement from the written finals.

**COVID-19 Exception**: In academic years 2020-21 and 2021-22, oral finals were cancelled. For these years, written final placements are considered final.

## Data Quality

### Completeness
- ✅ **100% complete** for: `ev`, `targy`, `iskola_nev`, `varos`, `varmegye`, `regio`, `helyezes`, `evfolyam`

### Accuracy
- School names normalized against official KIR database (Köznevelési Információs Rendszer)
- Fuzzy matching algorithm with 80%+ confidence threshold
- Manual override system for edge cases
- Automated validation checks performed
- Comprehensive audit trail of all matching decisions

### School Name Normalization
- **Automated matching**: 724 schools (93%) matched automatically with high confidence (≥90%)
- **Manual overrides**: 54 schools (7%) matched via manual mapping file
- **Dropped schools**: 1 school dropped (not found in KIR database, closed)
- **Audit file**: Complete record of all matching decisions available in source repository

### Deduplication
- Teams appearing in both written and oral finals are deduplicated
- Only final placements are retained
- 0 duplicate records in the final dataset

## Use Cases

This dataset can be used for:

- **Educational research**: Analyzing geographic distribution of academic excellence
- **School performance analysis**: Tracking schools' competition participation and success
- **Trend analysis**: Identifying patterns in competition results over time
- **Geographic analysis**: Understanding regional differences in academic achievement
- **Data visualization**: Creating maps, charts, and dashboards
- **Machine learning**: Predicting competition outcomes, clustering schools by performance

## Limitations

1. **No student names**: For privacy reasons, individual student names are not included
2. **Single subject only**: This dataset covers only the Mother Tongue category. Other subjects (Math, English, etc.) are not included
3. **Incomplete historical data**: Only results from 2015-16 onwards are available
4. **Grade subcategories**: Grades 7-8 have subcategories (elementary vs. gymnasium) which are normalized to base grade numbers
5. **School name variations**: Historical name changes are not tracked - schools appear with their current official name from KIR database
6. **Closed schools**: Schools not found in the current KIR database are excluded from the dataset

## Privacy & Ethics

- **No personal data**: Student names and other personally identifiable information are not included
- **Public data only**: All data was collected from publicly available competition results
- **Ethical scraping**: Automated collection followed polite scraping practices with appropriate delays
- **Non-commercial use**: This dataset is intended for educational and research purposes

## Citation

If you use this dataset in your research or project, please cite:

```
Csaba Fülöp (2025). Bolyai Hungarian Mother Tongue Team Competition Results Dataset (2015-2025). 
Retrieved from https://www.kaggle.com/datasets/csfulop/tanulmanyi-versenyek
License: CC BY 4.0
```

**Original data source:** Bolyai Competition Official Website (https://magyar.bolyaiverseny.hu)

## Updates & Maintenance

- **Current version**: 0.4.0
- **Last updated**: January 5, 2026
- **Update frequency**: Planned annual updates after each competition year
- **Future enhancements**: 
  - Additional subjects (Math, English, etc.)
  - Other Hungarian academic competitions (OKTV, Zrínyi Ilona)

## Contact & Feedback

For questions, corrections, or suggestions:

- **GitHub Repository:** https://github.com/csfulop/tanulmanyi-versenyek
- **Kaggle Dataset:** https://www.kaggle.com/datasets/csfulop/tanulmanyi-versenyek
- **Kaggle Notebook:** https://www.kaggle.com/code/csfulop/tanulmanyi-versenyek-eredmenyelemzes

## Analysis Notebook

An analysis Jupyter notebook with interactive exploration examples is available alongside this dataset. The notebook includes school and city rankings, as well as school search functionality.

## Data Cleaning Process

### School Name Normalization

All school names in this dataset have been normalized against the official Hungarian school database (KIR - Köznevelési Információs Rendszer):

- **Automated matching**: Fuzzy string matching algorithm (token_set_ratio) matches competition school names to official KIR names
- **Confidence thresholds**: 
  - High confidence (≥90%): Automatically applied (661 schools, 85%)
  - Medium confidence (≥80%): Automatically applied (63 schools, 8%)
  - Low confidence (<80%): Dropped from dataset (0 schools)
- **Manual overrides**: 54 schools (7%) matched via manual mapping file for edge cases
- **Manual drops**: 1 school (0.1%) manually excluded (not in KIR, closed)
- **Geographic data**: County and region information extracted from KIR database

The normalization process ensures consistency across years even when schools change names or have minor variations in competition records.

### City Name Normalization

City names are normalized as part of the school matching process:

- **Source**: Official city names from KIR database
- **Budapest districts**: Preserved from KIR (e.g., "Budapest III.")
- **Preprocessing**: Simple corrections applied before matching (e.g., "Debrecen-Józsa" → "Debrecen")

For details on the cleaning methodology and audit trail, see the project repository.

## Known Data Quality Limitations

### School Name Variations

**Status**: ✅ **Addressed in v0.4.0**

All school names have been normalized against the official KIR database using fuzzy matching:
- 93% of schools matched automatically with high confidence
- 7% matched via manual mapping file
- Schools not found in KIR database (likely closed) are excluded

**Historical name changes**: Schools appear with their current official name from the KIR database. Historical name variations are not tracked in this version.

### City Name Variations

**Status**: ✅ **Addressed in v0.4.0**

All city names have been normalized through the KIR database matching process. City names are consistent and reliable.

## License

This dataset is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

You are free to share and adapt this dataset for any purpose, including commercial use, as long as you provide appropriate attribution.

### Data Source and Legal Notice

The competition results in this dataset are publicly available on the Bolyai Competition website (https://www.bolyaiverseny.hu). According to the competition's data policy (https://www.bolyaiverseny.hu/adatkezeles.php), participant data (grade, school, placement) is public, and participants consent to this publication when registering.

This dataset contains only publicly available information. No private or registration data is included. The CC BY 4.0 license applies to the compilation, processing, documentation, and derived works, not to the underlying competition results which remain the property of the Bolyai Competition organizers.

For citation information, see the **Citation** section above.

---

**Keywords**: Hungary, education, academic competition, mother tongue, Hungarian language, elementary school, middle school, team competition, educational data, school rankings
