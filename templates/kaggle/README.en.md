# Bolyai Hungarian Mother Tongue Team Competition Results (2015-2025)

## Dataset Description

This dataset contains 10 years of historical results from the **Bolyai Hungarian Mother Tongue Team Competition** (Bolyai Anyanyelvi Csapatverseny), one of Hungary's most prestigious academic competitions for elementary and middle school students.

The competition is organized annually for students in grades 3-8, testing their Hungarian language skills through team-based challenges. This dataset includes results from both written finals (Írásbeli döntő) and oral finals (Szóbeli döntő) from the 2015-16 through 2024-25 academic years.

**Total Records**: 3,233 unique competition results  
**Schools Represented**: 766 different schools  
**Cities Covered**: 264 cities across Hungary  
**Time Period**: 10 academic years (2015-16 to 2024-25)

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
Retrieved from [Kaggle URL]
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

For questions, corrections, or suggestions regarding this dataset, please open an issue on the GitHub repository or contact via Kaggle.

## License

This dataset is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

You are free to share and adapt this dataset for any purpose, including commercial use, as long as you provide appropriate attribution.

### Data Source and Legal Notice

The competition results in this dataset are publicly available on the Bolyai Competition website (https://www.bolyaiverseny.hu). According to the competition's data policy, participant data (grade, school, placement) is public, and participants consent to this publication when registering.

This dataset contains only publicly available information. No private or registration data is included. The CC BY 4.0 license applies to the compilation, processing, documentation, and derived works, not to the underlying competition results which remain the property of the Bolyai Competition organizers.

For citation information, see the **Citation** section above.

---

**Keywords**: Hungary, education, academic competition, mother tongue, Hungarian language, elementary school, middle school, team competition, educational data, school rankings
