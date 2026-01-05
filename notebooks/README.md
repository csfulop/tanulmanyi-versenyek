# Competition Analysis Notebook

## Overview

This directory contains Jupyter notebooks for analyzing Hungarian academic competition results.

## Notebooks

### `competition_analysis.ipynb`

Interactive analysis notebook with the following features:

**Rankings:**
- School rankings (count-based and weighted scoring)
- City rankings (count-based and weighted scoring)
- County rankings (count-based and weighted scoring)
- Region rankings (count-based and weighted scoring)
- Configurable filters (grade, year, city, county, region, top-X threshold)

**Search:**
- Search for specific schools by partial name
- View complete competition history

**Languages:**
- Dual language support (Hungarian 🇭🇺 and English 🇬🇧)
- Each section has explanations in both languages
- Data tables use Hungarian column names

## Running on Kaggle

The notebook is already available on Kaggle, or you can upload your own version:

- **Notebook on Kaggle:** https://www.kaggle.com/code/csfulop/tanulmanyi-versenyek-eredmenyelemzes
- **Dataset on Kaggle:** https://www.kaggle.com/datasets/csfulop/tanulmanyi-versenyek

**To upload your own version:**
1. Upload `competition_analysis.ipynb` to Kaggle
2. Add the `tanulmanyi-versenyek` dataset to your notebook
3. Run cells in order

The notebook expects data at: `/kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv`

## Running Locally

### Method 1: Poetry (Recommended - Fast)

**Prerequisites:**
- Poetry installed
- Project dependencies installed (`poetry install`)

**Steps:**
```bash
# From project root
./run_notebook_with_poetry.sh
```

Then open your browser to: `http://localhost:8888`

**Advantages:**
- ✅ Fast startup (~2 seconds)
- ✅ Uses existing Poetry environment
- ✅ No download required
- ✅ Lightweight

**Disadvantages:**
- ❌ Not exact Kaggle environment (but uses same libraries)

### Method 2: Docker (Optional - Exact Kaggle Environment)

**Prerequisites:**
- Docker installed and running

**Steps:**
```bash
# From project root
./run_notebook_in_docker.sh
```

Then open your browser to: `http://localhost:8888`

**Note:** First run will download 20GB Docker image (may take 20-60 minutes).

**Advantages:**
- ✅ Exact Kaggle environment
- ✅ Guaranteed compatibility

**Disadvantages:**
- ❌ 20GB download on first run
- ❌ Slower startup (~10-30 seconds)

### How It Works

Both methods make the notebook work seamlessly:

**Poetry method:**
- Notebook detects local environment
- Uses relative path: `../data/kaggle/master_bolyai_anyanyelv.csv`

**Docker method:**
- Mounts `data/kaggle/` → `/kaggle/input/tanulmanyi-versenyek/`
- Mounts `notebooks/` → `/kaggle/working/`
- Notebook detects Kaggle-like environment
- Uses Kaggle path: `/kaggle/input/tanulmanyi-versenyek/master_bolyai_anyanyelv.csv`

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
chmod +x run_notebook_with_poetry.sh
chmod +x run_notebook_in_docker.sh
```

**Jupyter not found (Poetry method):**
```bash
# Reinstall dependencies
poetry install
```

## Customization

### Parameters

The notebook has configurable parameters at the top of each analysis section:

- `TOP_X`: Threshold for "top X" placements (default: 3 for count, 10 for weighted)
- `GRADE_FILTER`: Filter by grade(s) (default: "all")
  - Options: "all", single grade (e.g., 8), or list (e.g., [7, 8])
- `YEAR_FILTER`: Filter by year(s) (default: "all")
  - Options: "all", single year (e.g., "2023-24"), or list (e.g., ["2023-24", "2024-25"])
- `CITY_FILTER`: Filter by city/cities (default: "all")
  - Options: "all", single city (e.g., "Budapest III."), or list
- `COUNTY_FILTER`: Filter by county/counties (default: "all")
  - Options: "all", single county (e.g., "Pest"), or list
- `REGION_FILTER`: Filter by region(s) (default: "all")
  - Options: "all", single region (e.g., "Közép-Magyarország"), or list
- `DISPLAY_TOP_N`: Number of results to show (default: 50 for schools/cities, 20 for counties, 10 for regions)
- `SCHOOL_SEARCH`: Partial school name for search (default: "")

### Example Configurations

**Podium finishes only (top 3):**
```python
TOP_X = 3
GRADE_FILTER = "all"
YEAR_FILTER = "all"
```

**8th grade only, recent years:**
```python
TOP_X = 10
GRADE_FILTER = 8
YEAR_FILTER = ["2023-24", "2024-25"]
```

**Upper grades, single year:**
```python
TOP_X = 5
GRADE_FILTER = [7, 8]
YEAR_FILTER = "2024-25"
```

**Budapest schools only:**
```python
TOP_X = 10
CITY_FILTER = ["Budapest II.", "Budapest III.", "Budapest V."]
YEAR_FILTER = "all"
```

**Specific county analysis:**
```python
TOP_X = 10
COUNTY_FILTER = "Pest"
YEAR_FILTER = "all"
```

### Modifying Code

All helper functions are defined in the "Helper Functions" section. You can:
- Modify ranking algorithms
- Add new metrics
- Change display formatting
- Add new analysis sections

## Data Schema

The notebook expects a CSV file with these columns:

| Column | Type | Description |
|--------|------|-------------|
| ev | string | Academic year (e.g., "2023-24") |
| targy | string | Subject (always "Anyanyelv") |
| iskola_nev | string | School name (normalized from KIR database) |
| varos | string | City (normalized from KIR database) |
| varmegye | string | County (from KIR database) |
| regio | string | Region (from KIR database) |
| helyezes | integer | Final rank/placement |
| evfolyam | integer | Grade level (3-8) |

## Future Enhancements

Planned features for future versions:
- Interactive widgets (ipywidgets) for parameter selection
- Chart visualizations (Plotly)
- Advanced statistical analysis

## Support

For issues or questions:
- **GitHub Repository:** https://github.com/csfulop/tanulmanyi-versenyek
- **Kaggle Dataset:** https://www.kaggle.com/datasets/csfulop/tanulmanyi-versenyek
- **Kaggle Notebook:** https://www.kaggle.com/code/csfulop/tanulmanyi-versenyek-eredmenyelemzes
