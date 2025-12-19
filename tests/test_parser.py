import pytest
from pathlib import Path
from tanulmanyi_versenyek.parser.html_parser import HtmlTableParser
from tanulmanyi_versenyek.common.config import get_config
from tanulmanyi_versenyek.common.logger import setup_logging
import logging

setup_logging()
test_logger = logging.getLogger(__name__)


@pytest.fixture
def parser():
    """Fixture to provide a parser instance for testing."""
    config = get_config()
    dummy_path = Path("dummy.html")
    return HtmlTableParser(dummy_path, config, test_logger)


@pytest.fixture
def config():
    """Fixture to provide config for tests."""
    return get_config()


# Filename parsing tests
def test_parse_metadata_from_filename_simple_grade(parser):
    """Test parsing filename with simple grade (3-6)."""
    filename = "anyanyelv_2022-23_5.-osztaly_irasbeli-donto.html"
    metadata = parser._parse_metadata_from_filename(filename)
    
    assert metadata['year'] == '2022-23'
    assert metadata['grade'] == 5
    assert metadata['round'] == 'irasbeli-donto'


def test_parse_metadata_from_filename_grade_with_category(parser):
    """Test parsing filename with grade category (7-8)."""
    filename = "anyanyelv_2024-25_8.-osztaly---altalanos-iskolai-kategoria_irasbeli-donto.html"
    metadata = parser._parse_metadata_from_filename(filename)
    
    assert metadata['year'] == '2024-25'
    assert metadata['grade'] == 8
    assert metadata['round'] == 'irasbeli-donto'


def test_parse_metadata_from_filename_szobeli_round(parser):
    """Test parsing filename with szobeli round."""
    filename = "anyanyelv_2023-24_7.-osztaly---gimnaziumi-kategoria_szobeli-donto.html"
    metadata = parser._parse_metadata_from_filename(filename)
    
    assert metadata['year'] == '2023-24'
    assert metadata['grade'] == 7
    assert metadata['round'] == 'szobeli-donto'


def test_parse_metadata_from_filename_invalid_format(parser):
    """Test that invalid filename raises ValueError."""
    filename = "invalid_format.html"
    
    with pytest.raises(ValueError, match="Invalid filename format"):
        parser._parse_metadata_from_filename(filename)


def test_parse_metadata_from_filename_no_grade_number(parser):
    """Test that filename without grade number raises ValueError."""
    filename = "anyanyelv_2022-23_invalid_irasbeli-donto.html"
    
    with pytest.raises(ValueError, match="Could not extract grade number"):
        parser._parse_metadata_from_filename(filename)


# Helyezes normalization tests
def test_normalize_helyezes_dontos(parser):
    """Test normalizing 'döntős' format ranks."""
    assert parser._normalize_helyezes("1. döntős") == 1
    assert parser._normalize_helyezes("5. döntős") == 5


def test_normalize_helyezes_simple(parser):
    """Test normalizing simple rank format."""
    assert parser._normalize_helyezes("7.") == 7
    assert parser._normalize_helyezes("15.") == 15
    assert parser._normalize_helyezes("100.") == 100


def test_normalize_helyezes_invalid(parser):
    """Test that invalid helyezes raises ValueError."""
    with pytest.raises(ValueError, match="Could not extract rank"):
        parser._normalize_helyezes("invalid")


# School/city splitting tests
def test_split_school_and_city_simple(parser):
    """Test splitting simple school and city."""
    result = parser._split_school_and_city("Veszprémi Deák Ferenc Általános Iskola\nVeszprém")
    assert result[0] == "Veszprémi Deák Ferenc Általános Iskola"
    assert result[1] == "Veszprém"


def test_split_school_and_city_budapest_district(parser):
    """Test splitting Budapest school with district."""
    result = parser._split_school_and_city("Újpesti Homoktövis Általános Iskola\nBudapest IV.")
    assert result[0] == "Újpesti Homoktövis Általános Iskola"
    assert result[1] == "Budapest IV."


def test_split_school_and_city_no_newline(parser):
    """Test that missing newline raises ValueError."""
    with pytest.raises(ValueError, match="No newline separator found"):
        parser._split_school_and_city("School Name Without Separator")


# Integration test with committed fixture
def test_parse_with_committed_fixture(config):
    """Test parsing with small committed test fixture."""
    test_logger_int = logging.getLogger(__name__)
    
    # Use committed test fixture
    html_file = Path("tests/test_data/sample_result.html")
    assert html_file.exists(), f"Test fixture missing: {html_file}"
    
    # Rename fixture temporarily to have proper filename for metadata extraction
    temp_file = html_file.parent / "anyanyelv_2023-24_8.-osztaly---altalanos-iskolai-kategoria_irasbeli-donto.html"
    import shutil
    shutil.copy(html_file, temp_file)
    
    try:
        parser = HtmlTableParser(temp_file, config, test_logger_int)
        df = parser.parse()
        
        # Verify structure
        assert df.shape[0] == 3, "Should have 3 rows from fixture"
        assert df.shape[1] == 7, "Should have 7 columns"
        
        # Verify columns
        expected_columns = ['ev', 'targy', 'iskola_nev', 'varos', 'megye', 'helyezes', 'evfolyam']
        assert list(df.columns) == expected_columns
        
        # Verify data types
        assert df['helyezes'].dtype == 'int64'
        assert df['evfolyam'].dtype == 'int64'
        
        # Verify no nulls
        assert df.isnull().sum().sum() == 0
        
        # Verify metadata from filename
        assert all(df['ev'] == '2023-24')
        assert all(df['evfolyam'] == 8)
        
        # Verify specific values from fixture
        assert df.iloc[0]['helyezes'] == 1
        assert df.iloc[0]['iskola_nev'] == "Budapesti Teszt Általános Iskola"
        assert df.iloc[0]['varos'] == "Budapest IV."
        
        assert df.iloc[1]['helyezes'] == 2
        assert df.iloc[1]['iskola_nev'] == "Veszprémi Teszt Általános Iskola"
        assert df.iloc[1]['varos'] == "Veszprém"
        
        assert df.iloc[2]['helyezes'] == 3
        assert df.iloc[2]['varos'] == "Debrecen"
    finally:
        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()
