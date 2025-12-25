# Bolyai Hungarian Mother Tongue Team Competition Results (2015-2025)

## Dataset Description

This dataset contains 10 years of historical results from the **Bolyai Hungarian Mother Tongue Team Competition** (Bolyai Anyanyelvi Csapatverseny), one of Hungary's most prestigious elementary and high school academic competitions.

**What's Inside:**
- 3,233 competition results from 2015-16 to 2024-25
- 766 different schools from 264 cities across Hungary
- Team rankings for grades 3-8
- Both written finals (Írásbeli döntő) and oral finals (Szóbeli döntő)
- Interactive Jupyter notebook for data exploration
- Bilingual documentation (Hungarian and English)

**Context:**
The Bolyai Competition tests Hungarian language skills through team-based challenges, organized annually for students in grades 3-8. This dataset represents a decade of competitive academic achievement in Hungary's education system.

**Use Cases:**
- Analyze school performance trends over time
- Compare regional educational outcomes
- Identify top-performing schools and cities
- Study competition participation patterns
- Educational data visualization projects

## Files in This Dataset

### `master_bolyai_anyanyelv.csv`
Complete dataset of Bolyai Mother Tongue Competition results (2015-2025). Contains 3,233 records with school names, cities, rankings, grades, and academic years. Semicolon-separated format, UTF-8 encoding. Main data file for analysis.

### `README.hu.md`
Hungarian language documentation. Includes dataset description, data collection methodology, column definitions, usage examples, known data quality limitations, and license information. Complete reference guide in Hungarian.

### `README.en.md`
English language documentation. Includes dataset description, data collection methodology, column definitions, usage examples, known data quality limitations, and license information. Complete reference guide in English.

### `LICENSE`
Creative Commons Attribution 4.0 International (CC BY 4.0) license. Specifies terms of use, attribution requirements, and permissions for the dataset. Free to use with proper attribution.

## Data Provenance

### Sources

Official Bolyai Competition website: https://magyar.bolyaiverseny.hu/verseny/archivum/eredmenyek.php

Data represents official competition results published by the organizers for public access.

### Collection Methodology

Automated web scraping using Python with Playwright library for browser automation and BeautifulSoup for HTML parsing.

**Process:**
1. Automated navigation through competition result pages for all academic years (2015-16 to 2024-25) and grade levels (3-8)
2. Respectful data collection with 5-second delays between requests to avoid server overload
3. HTML table extraction and parsing into structured format
4. Three-stage pipeline: (a) raw HTML download, (b) data extraction and normalization, (c) merging and deduplication
5. Quality validation: automated checks for completeness and consistency

**Deduplication logic:** Oral finals results (final placements) take precedence over written finals results (preliminary placements) when both exist for the same team.

**Output:** Semicolon-separated CSV file with UTF-8 encoding.

**Collection date:** December 2025

## Dataset Structure

### File: `master_bolyai_anyanyelv.csv`

A semicolon-separated CSV file containing all competition results.

**Columns:**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `ev` | String | Academic year of the competition | "2024-25" |
| `targy` | String | Subject (always "Anyanyelv" = Mother Tongue) | "Anyanyelv" |
| `iskola_nev` | String | Name of the school | "Budapesti Kölcsey F. Gimnázium" |
| `varos` | String | City where the school is located (includes district number for Budapest) | "Budapest III." or "Debrecen" |
| `megye` | String | County (currently empty - not available in source) | "" |
| `helyezes` | Integer | Final rank/placement achieved by the team | 1 |
| `evfolyam` | Integer | Grade level (3-8) | 8 |

**Note on `megye` column**: This column is currently empty as county information is not provided in the source data. Future versions may include this through city-to-county mapping.

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
- ✅ **100% complete** for: `ev`, `targy`, `iskola_nev`, `varos`, `helyezes`, `evfolyam`
- ⚠️ **0% complete** for: `megye` (not available in source data)

### Accuracy
- Data extracted directly from official competition results
- Automated validation checks performed
- Manual spot-checking of sample records

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

1. **County data unavailable**: The `megye` column is empty as this information is not provided in the source data
2. **No student names**: For privacy reasons, individual student names are not included
3. **Single subject only**: This dataset covers only the Mother Tongue category. Other subjects (Math, English, etc.) are not included
4. **Incomplete historical data**: Only results from 2015-16 onwards are available
5. **Grade subcategories**: Grades 7-8 have subcategories (elementary vs. gymnasium) which are normalized to base grade numbers

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

- **Current version**: 0.1.0 (MVP)
- **Last updated**: December 20, 2025
- **Update frequency**: Planned annual updates after each competition year
- **Future enhancements**: 
  - County data enrichment
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

### City Name Normalization

The dataset includes manual city name cleaning to address variations in the source data:

- **Case normalization**: "MISKOLC" → "Miskolc"
- **Suburb mapping**: "Debrecen-Józsa" → "Debrecen"
- **Budapest districts**: Missing districts added where identifiable (e.g., "Budapest" → "Budapest II." for specific schools)

The cleaning process uses a manually maintained mapping file that preserves data authenticity while improving consistency. Valid variations (e.g., schools with the same name in different cities) are documented but not modified.

For details on the cleaning methodology, see the project repository.

## Known Data Quality Limitations

### School and City Name Inconsistencies

This dataset contains school and city names with the following characteristics:

**1. City Name Variations (Fully Addressed):**
- All city name variations have been normalized through manual mapping
- Examples of corrections: "MISKOLC" → "Miskolc", "Debrecen-Józsa" → "Debrecen", "Budapest" → "Budapest II."
- Valid variations (different schools with same name in different cities) are preserved
- **Affected schools**: 15 (9 corrected, 6 valid variations documented)

**2. School Name Changes (Not Yet Addressed):**
- Schools' official names may change over time (reorganization, renaming)
- Minor variations in spelling or abbreviations
- Example: "Baár-Madas Református Gimnázium és Általános Iskola" vs "Baár-Madas Református Gimnázium, Általános Iskola és Kollégium"
- **Affected school groups**: 70+
- **Status**: Planned for future release

**Impact on Rankings:**
- City name variations have been fully addressed through cleaning
- School name variations still cause the same school to appear multiple times in rankings
- Rankings thus provide a **lower bound estimate** of schools' performance
- Actual rankings may be higher if all school name variations were consolidated

**Why School Names Aren't Fixed Yet:**
- More complex than city names (70+ variations vs 15)
- Requires careful research of official school names
- Planned for future release after city cleaning is stable

**Recommendations for Users:**
- City names are now fully consistent and reliable
- Use partial name search to find schools (school names still have variations)
- Be aware that school rankings are conservative estimates
- Check all name variations of a school for complete results

## License

This dataset is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

You are free to share and adapt this dataset for any purpose, including commercial use, as long as you provide appropriate attribution.

### Data Source and Legal Notice

The competition results in this dataset are publicly available on the Bolyai Competition website (https://www.bolyaiverseny.hu). According to the competition's data policy (https://www.bolyaiverseny.hu/adatkezeles.php), participant data (grade, school, placement) is public, and participants consent to this publication when registering.

This dataset contains only publicly available information. No private or registration data is included. The CC BY 4.0 license applies to the compilation, processing, documentation, and derived works, not to the underlying competition results which remain the property of the Bolyai Competition organizers.

For citation information, see the **Citation** section above.

---

**Keywords**: Hungary, education, academic competition, mother tongue, Hungarian language, elementary school, middle school, team competition, educational data, school rankings
