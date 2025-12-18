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
