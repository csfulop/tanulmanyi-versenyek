"""
Unit tests for notebook helper functions.

Note: These functions are duplicated from the notebook for testing purposes.
Any changes to the notebook helper functions must be reflected here.
"""

import pytest
import pandas as pd


# === HELPER FUNCTIONS ===

def hungarian_sort_key(text):
    """Convert Hungarian text to sortable form by normalizing accented characters."""
    if not isinstance(text, str):
        return text
    HUNGARIAN_SORT_MAP = str.maketrans(
        'aáeéiíoóöőuúüűAÁEÉIÍOÓÖŐUÚÜŰ',
        'aaeeiioooouuuuAAEEIIOOOOUUUU'
    )
    return text.translate(HUNGARIAN_SORT_MAP)


def filter_data(df, grade_filter, year_filter, city_filter="all"):
    """Filter dataframe by grade, year, and city."""
    filtered = df.copy()
    
    # Handle grade filter
    if grade_filter != "all":
        grades = [grade_filter] if not isinstance(grade_filter, list) else grade_filter
        invalid_grades = [g for g in grades if g not in [3, 4, 5, 6, 7, 8]]
        if invalid_grades:
            raise ValueError(f"Invalid grade(s): {invalid_grades}\nValid grades are: [3, 4, 5, 6, 7, 8]")
        filtered = filtered[filtered['evfolyam'].isin(grades)]
    
    # Handle year filter
    if year_filter != "all":
        years = [year_filter] if not isinstance(year_filter, list) else year_filter
        valid_years = df['ev'].unique().tolist()
        invalid_years = [y for y in years if y not in valid_years]
        if invalid_years:
            raise ValueError(f"Invalid year(s): {invalid_years}\nValid years are: {sorted(valid_years)}")
        filtered = filtered[filtered['ev'].isin(years)]
    
    # Handle city filter
    if city_filter != "all":
        if isinstance(city_filter, str):
            filtered = filtered[filtered['varos'] == city_filter]
        elif isinstance(city_filter, list):
            filtered = filtered[filtered['varos'].isin(city_filter)]
        else:
            print("⚠️ Invalid CITY_FILTER format. Using all cities.")
    
    return filtered


def calculate_count_ranking(df, top_x, group_by):
    """Count appearances in top X positions."""
    top_df = df[df['helyezes'] <= top_x].copy()

    if group_by == 'iskola_nev':
        # Count by school only
        result = top_df.groupby('iskola_nev').size().reset_index(name='Count')
        # Add most common city for each school
        city_map = top_df.groupby('iskola_nev')['varos'].agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0])
        result['varos'] = result['iskola_nev'].map(city_map)
        result = result[['iskola_nev', 'varos', 'Count']]
        result = result.sort_values(
            ['Count', 'iskola_nev'],
            ascending=[False, True],
            key=lambda col: col.map(hungarian_sort_key) if col.name == 'iskola_nev' else col
        ).reset_index(drop=True)
    else:  # group_by == 'varos'
        result = top_df.groupby('varos').size().reset_index(name='Count')
        result = result.sort_values(
            ['Count', 'varos'],
            ascending=[False, True],
            key=lambda col: col.map(hungarian_sort_key) if col.name == 'varos' else col
        ).reset_index(drop=True)

    return result


def calculate_weighted_ranking(df, top_x, group_by):
    """Calculate weighted scores based on placement."""
    scored_df = df.copy()
    scored_df['points'] = scored_df['helyezes'].apply(lambda x: max(0, top_x - x + 1))
    scored_df = scored_df[scored_df['points'] > 0]

    if group_by == 'iskola_nev':
        # Sum points by school only
        result = scored_df.groupby('iskola_nev')['points'].sum().reset_index(name='Weighted Score')
        # Add most common city for each school
        city_map = scored_df.groupby('iskola_nev')['varos'].agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0])
        result['varos'] = result['iskola_nev'].map(city_map)
        result = result[['iskola_nev', 'varos', 'Weighted Score']]
        result = result.sort_values(
            ['Weighted Score', 'iskola_nev'],
            ascending=[False, True],
            key=lambda col: col.map(hungarian_sort_key) if col.name == 'iskola_nev' else col
        ).reset_index(drop=True)
    else:  # group_by == 'varos'
        result = scored_df.groupby('varos')['points'].sum().reset_index(name='Weighted Score')
        result = result.sort_values(
            ['Weighted Score', 'varos'],
            ascending=[False, True],
            key=lambda col: col.map(hungarian_sort_key) if col.name == 'varos' else col
        ).reset_index(drop=True)

    return result


def search_schools(df, search_term):
    """Find schools matching a partial name search."""
    search_term = search_term.strip().lower()
    schools = df['iskola_nev'].unique()
    matches = [s for s in schools if search_term in s.lower()]
    return sorted(matches)


def get_school_results(df, school_name):
    """Retrieve all competition results for a specific school."""
    results = df[df['iskola_nev'] == school_name].copy()
    results = results[['ev', 'evfolyam', 'targy', 'helyezes']]
    results = results.sort_values(['ev', 'evfolyam'], ascending=[False, True]).reset_index(drop=True)
    results.columns = ['Year', 'Grade', 'Subject', 'Rank']
    return results


# === TEST FIXTURES ===

@pytest.fixture
def sample_df():
    """Create a sample dataframe with realistic test data."""
    return pd.DataFrame({
        'ev': [
            '2023-24', '2023-24', '2023-24', '2023-24', '2023-24',
            '2024-25', '2024-25', '2024-25', '2024-25', '2024-25'
        ],
        'targy': ['Anyanyelv'] * 10,
        'iskola_nev': [
            'Mustármag Keresztény Óvoda, Általános Iskola és Gimnázium',
            'Hajdúböszörményi Bocskai István Általános Iskola',
            'Veszprémi Deák Ferenc Általános Iskola',
            'Mustármag Keresztény Óvoda, Általános Iskola és Gimnázium',
            'Németh Imre Általános Iskola',
            'Mustármag Keresztény Óvoda, Általános Iskola és Gimnázium',
            'Petőfi Utcai Általános Iskola',
            'Hajdúböszörményi Bocskai István Általános Iskola',
            'Hétvezér Általános Iskola',
            'Veszprémi Deák Ferenc Általános Iskola'
        ],
        'varos': [
            'Budapest III.', 'Hajdúböszörmény', 'Veszprém', 'Budapest III.', 'Budapest XIV.',
            'Budapest III.', 'Békéscsaba', 'Hajdúböszörmény', 'Székesfehérvár', 'Veszprém'
        ],
        'megye': [''] * 10,
        'helyezes': [1, 2, 3, 5, 8, 1, 2, 3, 7, 10],
        'evfolyam': [3, 3, 4, 7, 8, 4, 5, 7, 8, 8]
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
    assert len(result) == 5
    assert all(result['ev'] == '2023-24')


def test_filter_data_multiple_years(sample_df):
    """Test filtering by multiple years."""
    result = filter_data(sample_df, "all", ["2023-24", "2024-25"])
    assert len(result) == 10


def test_filter_data_combined(sample_df):
    """Test filtering by both grade and year."""
    result = filter_data(sample_df, 8, "2023-24")
    assert len(result) == 1


def test_filter_data_invalid_grade(sample_df):
    """Test that invalid grade raises ValueError."""
    with pytest.raises(ValueError, match="Invalid grade"):
        filter_data(sample_df, 9, "all")


def test_filter_data_invalid_year(sample_df):
    """Test that invalid year raises ValueError."""
    with pytest.raises(ValueError, match="Invalid year"):
        filter_data(sample_df, "all", "2030-31")


def test_filter_data_single_city(sample_df):
    """Test filtering by single city."""
    result = filter_data(sample_df, "all", "all", "Budapest III.")
    assert len(result) == 3
    assert all(result['varos'] == "Budapest III.")


def test_filter_data_multiple_cities(sample_df):
    """Test filtering by multiple cities."""
    result = filter_data(sample_df, "all", "all", ["Budapest III.", "Veszprém"])
    assert len(result) == 5
    assert set(result['varos'].unique()) == {"Budapest III.", "Veszprém"}


def test_filter_data_city_default_all(sample_df):
    """Test that city filter defaults to 'all'."""
    result = filter_data(sample_df, "all", "all")
    assert len(result) == len(sample_df)


def test_filter_data_combined_with_city(sample_df):
    """Test filtering by grade, year, and city together."""
    result = filter_data(sample_df, 8, "2023-24", "Budapest XIV.")
    assert len(result) == 1
    assert result.iloc[0]['evfolyam'] == 8
    assert result.iloc[0]['ev'] == "2023-24"
    assert result.iloc[0]['varos'] == "Budapest XIV."


def test_filter_data_city_no_match(sample_df):
    """Test filtering by city with no matches."""
    result = filter_data(sample_df, "all", "all", "NonExistentCity")
    assert len(result) == 0


# === TESTS FOR calculate_count_ranking() ===

def test_count_ranking_schools(sample_df):
    """Test count ranking for schools."""
    result = calculate_count_ranking(sample_df, 3, "iskola_nev")
    assert len(result) == 4  # 4 schools have top-3 placements
    assert result.iloc[0]['iskola_nev'] in ['Mustármag Keresztény Óvoda, Általános Iskola és Gimnázium', 
                                              'Hajdúböszörményi Bocskai István Általános Iskola']
    assert result.iloc[0]['Count'] == 2  # Top schools have 2 appearances each


def test_count_ranking_cities(sample_df):
    """Test count ranking for cities."""
    result = calculate_count_ranking(sample_df, 3, "varos")
    assert len(result) == 4
    assert result.iloc[0]['varos'] == 'Budapest III.'


def test_count_ranking_top_threshold(sample_df):
    """Test that only top X positions are counted."""
    result = calculate_count_ranking(sample_df, 2, "iskola_nev")
    mustarmag_count = result[result['iskola_nev'].str.contains('Mustármag')]['Count'].iloc[0]
    assert mustarmag_count == 2


# === TESTS FOR calculate_weighted_ranking() ===

def test_weighted_ranking_formula(sample_df):
    """Test weighted scoring formula with specific calculation."""
    result = calculate_weighted_ranking(sample_df, 3, "iskola_nev")
    mustarmag = result[result['iskola_nev'].str.contains('Mustármag')].iloc[0]
    # Mustármag: 1st place (3pts) + 1st place (3pts) = 6pts (5th place doesn't count)
    assert mustarmag['Weighted Score'] == 6


def test_weighted_ranking_sorting(sample_df):
    """Test that results are sorted by weighted score descending."""
    result = calculate_weighted_ranking(sample_df, 3, "iskola_nev")
    # Verify top school has highest score
    assert result.iloc[0]['iskola_nev'] in ['Mustármag Keresztény Óvoda, Általános Iskola és Gimnázium',
                                              'Hajdúböszörményi Bocskai István Általános Iskola']


def test_weighted_ranking_excludes_beyond_threshold(sample_df):
    """Test that positions beyond top_x are excluded from scoring."""
    result = calculate_weighted_ranking(sample_df, 2, "iskola_nev")
    mustarmag_score = result[result['iskola_nev'].str.contains('Mustármag')]['Weighted Score'].iloc[0]
    # With top_x=2: only 1st and 2nd place count
    # Mustármag has two 1st places: 2pts + 2pts = 4pts (3rd place excluded)
    assert mustarmag_score == 4


# === TESTS FOR search_schools() ===

def test_search_schools_exact_match(sample_df):
    """Test search with exact match."""
    result = search_schools(sample_df, "Mustármag")
    assert len(result) == 1


def test_search_schools_partial_match(sample_df):
    """Test search with partial match."""
    result = search_schools(sample_df, "Általános")
    assert len(result) >= 3


def test_search_schools_case_insensitive(sample_df):
    """Test that search is case-insensitive."""
    result = search_schools(sample_df, "mustármag")
    assert len(result) == 1


def test_search_schools_no_match(sample_df):
    """Test search with no matches."""
    result = search_schools(sample_df, "XYZ123")
    assert len(result) == 0


# === TESTS FOR get_school_results() ===

def test_get_school_results(sample_df):
    """Test retrieving results for a specific school."""
    result = get_school_results(sample_df, 'Mustármag Keresztény Óvoda, Általános Iskola és Gimnázium')
    assert len(result) == 3
    assert result.iloc[0]['Year'] == '2024-25'


def test_get_school_results_columns(sample_df):
    """Test that result has correct columns."""
    result = get_school_results(sample_df, 'Mustármag Keresztény Óvoda, Általános Iskola és Gimnázium')
    assert list(result.columns) == ['Year', 'Grade', 'Subject', 'Rank']


def test_get_school_results_no_match(sample_df):
    """Test retrieving results for non-existent school."""
    result = get_school_results(sample_df, "Nonexistent School")
    assert len(result) == 0


def test_fixture_structure(sample_df):
    """Verify the test fixture has correct structure."""
    assert len(sample_df) == 10
    assert list(sample_df.columns) == ['ev', 'targy', 'iskola_nev', 'varos', 'megye', 'helyezes', 'evfolyam']
    assert sample_df['targy'].unique().tolist() == ['Anyanyelv']


# === TESTS FOR hungarian_sort_key() ===

def test_hungarian_sort_key_basic():
    """Test that Hungarian accented characters are normalized."""
    assert hungarian_sort_key('Város') == 'Varos'
    assert hungarian_sort_key('Pécs') == 'Pecs'
    assert hungarian_sort_key('Győr') == 'Gyor'


def test_hungarian_sort_key_all_accents():
    """Test all Hungarian accented characters."""
    assert hungarian_sort_key('aáeéiíoóöőuúüű') == 'aaeeiioooouuuu'
    assert hungarian_sort_key('AÁEÉIÍOÓÖŐUÚÜŰ') == 'AAEEIIOOOOUUUU'


def test_hungarian_sort_key_non_string():
    """Test that non-string values are returned as-is."""
    assert hungarian_sort_key(123) == 123
    assert hungarian_sort_key(None) is None


def test_hungarian_sort_key_mixed_text():
    """Test text with mixed accented and non-accented characters."""
    assert hungarian_sort_key('Veszprém') == 'Veszprem'
    assert hungarian_sort_key('Debrecen') == 'Debrecen'


# === TESTS FOR city grouping fix ===

def test_count_ranking_school_with_multiple_cities():
    """Test that schools with multiple city names are counted together."""
    df = pd.DataFrame({
        'ev': ['2023-24'] * 6,
        'targy': ['Anyanyelv'] * 6,
        'iskola_nev': ['School A'] * 6,
        'varos': ['Budapest', 'Budapest II.', 'Budapest', 'Budapest II.', 'Budapest', 'Budapest II.'],
        'megye': [''] * 6,
        'helyezes': [1, 2, 3, 4, 5, 6],
        'evfolyam': [8] * 6
    })

    result = calculate_count_ranking(df, 6, 'iskola_nev')

    assert len(result) == 1
    assert result.iloc[0]['iskola_nev'] == 'School A'
    assert result.iloc[0]['Count'] == 6
    assert result.iloc[0]['varos'] in ['Budapest', 'Budapest II.']


def test_count_ranking_school_most_common_city():
    """Test that the most common city is selected for display."""
    df = pd.DataFrame({
        'ev': ['2023-24'] * 6,
        'targy': ['Anyanyelv'] * 6,
        'iskola_nev': ['School A'] * 6,
        'varos': ['Budapest II.', 'Budapest II.', 'Budapest II.', 'Budapest II.', 'Budapest', 'Budapest'],
        'megye': [''] * 6,
        'helyezes': [1, 2, 3, 4, 5, 6],
        'evfolyam': [8] * 6
    })

    result = calculate_count_ranking(df, 6, 'iskola_nev')

    assert result.iloc[0]['varos'] == 'Budapest II.'


def test_weighted_ranking_school_with_multiple_cities():
    """Test that weighted ranking counts schools with multiple cities together."""
    df = pd.DataFrame({
        'ev': ['2023-24'] * 6,
        'targy': ['Anyanyelv'] * 6,
        'iskola_nev': ['School A'] * 6,
        'varos': ['Budapest', 'Budapest II.', 'Budapest', 'Budapest II.', 'Budapest', 'Budapest II.'],
        'megye': [''] * 6,
        'helyezes': [1, 2, 3, 4, 5, 6],
        'evfolyam': [8] * 6
    })

    result = calculate_weighted_ranking(df, 6, 'iskola_nev')

    assert len(result) == 1
    assert result.iloc[0]['iskola_nev'] == 'School A'
    expected_score = 6 + 5 + 4 + 3 + 2 + 1
    assert result.iloc[0]['Weighted Score'] == expected_score


# === TESTS FOR tie-breaking with secondary sort ===

def test_count_ranking_schools_tie_alphabetical():
    """Test that schools with same count are sorted alphabetically."""
    df = pd.DataFrame({
        'ev': ['2023-24'] * 6,
        'targy': ['Anyanyelv'] * 6,
        'iskola_nev': ['Zebra School', 'Alpha School', 'Zebra School', 'Alpha School', 'Beta School', 'Beta School'],
        'varos': ['Budapest'] * 6,
        'megye': [''] * 6,
        'helyezes': [1, 1, 2, 2, 1, 2],
        'evfolyam': [8] * 6
    })

    result = calculate_count_ranking(df, 3, 'iskola_nev')

    assert len(result) == 3
    assert result.iloc[0]['iskola_nev'] == 'Alpha School'
    assert result.iloc[1]['iskola_nev'] == 'Beta School'
    assert result.iloc[2]['iskola_nev'] == 'Zebra School'


def test_count_ranking_cities_tie_alphabetical():
    """Test that cities with same count are sorted alphabetically."""
    df = pd.DataFrame({
        'ev': ['2023-24'] * 6,
        'targy': ['Anyanyelv'] * 6,
        'iskola_nev': ['School A', 'School B', 'School C', 'School D', 'School E', 'School F'],
        'varos': ['Zalaegerszeg', 'Debrecen', 'Zalaegerszeg', 'Debrecen', 'Szeged', 'Szeged'],
        'megye': [''] * 6,
        'helyezes': [1, 1, 2, 2, 1, 2],
        'evfolyam': [8] * 6
    })

    result = calculate_count_ranking(df, 3, 'varos')

    assert len(result) == 3
    assert result.iloc[0]['varos'] == 'Debrecen'
    assert result.iloc[1]['varos'] == 'Szeged'
    assert result.iloc[2]['varos'] == 'Zalaegerszeg'


def test_weighted_ranking_schools_tie_alphabetical():
    """Test that schools with same weighted score are sorted alphabetically."""
    df = pd.DataFrame({
        'ev': ['2023-24'] * 4,
        'targy': ['Anyanyelv'] * 4,
        'iskola_nev': ['Zebra School', 'Alpha School', 'Zebra School', 'Alpha School'],
        'varos': ['Budapest'] * 4,
        'megye': [''] * 4,
        'helyezes': [1, 2, 2, 1],
        'evfolyam': [8] * 4
    })

    result = calculate_weighted_ranking(df, 3, 'iskola_nev')

    assert len(result) == 2
    assert result.iloc[0]['iskola_nev'] == 'Alpha School'
    assert result.iloc[1]['iskola_nev'] == 'Zebra School'


# === TESTS FOR Hungarian alphabetical sorting ===

def test_count_ranking_hungarian_alphabetical_order():
    """Test that Hungarian accented characters are sorted correctly."""
    df = pd.DataFrame({
        'ev': ['2023-24'] * 4,
        'targy': ['Anyanyelv'] * 4,
        'iskola_nev': ['School A', 'School B', 'School C', 'School D'],
        'varos': ['Veszprém', 'Valahol', 'Vác', 'Veresegyház'],
        'megye': [''] * 4,
        'helyezes': [1, 1, 1, 1],
        'evfolyam': [8] * 4
    })

    result = calculate_count_ranking(df, 3, 'varos')

    assert len(result) == 4
    assert result.iloc[0]['varos'] == 'Vác'
    assert result.iloc[1]['varos'] == 'Valahol'
    assert result.iloc[2]['varos'] == 'Veresegyház'
    assert result.iloc[3]['varos'] == 'Veszprém'


def test_weighted_ranking_hungarian_alphabetical_order():
    """Test Hungarian sorting in weighted rankings."""
    df = pd.DataFrame({
        'ev': ['2023-24'] * 4,
        'targy': ['Anyanyelv'] * 4,
        'iskola_nev': ['Pécs Gimnázium', 'Paks Gimnázium', 'Pápa Gimnázium', 'Pécel Gimnázium'],
        'varos': ['Pécs', 'Paks', 'Pápa', 'Pécel'],
        'megye': [''] * 4,
        'helyezes': [1, 1, 1, 1],
        'evfolyam': [8] * 4
    })

    result = calculate_weighted_ranking(df, 3, 'iskola_nev')

    assert len(result) == 4
    assert result.iloc[0]['iskola_nev'] == 'Paks Gimnázium'
    assert result.iloc[1]['iskola_nev'] == 'Pápa Gimnázium'
    assert result.iloc[2]['iskola_nev'] == 'Pécel Gimnázium'
    assert result.iloc[3]['iskola_nev'] == 'Pécs Gimnázium'
