import pytest
import logging
from pathlib import Path
from tanulmanyi_versenyek.parser.html_parser import HtmlTableParser
from tanulmanyi_versenyek.scraper.bolyai_downloader import WebsiteDownloader
from tanulmanyi_versenyek.common.config import get_config
from tanulmanyi_versenyek.common.logger import setup_logging

setup_logging()


@pytest.fixture(scope="module")
def config():
    """Provide config for integration tests."""
    return get_config()


@pytest.fixture(scope="module")
def live_data_dir():
    """Create and return live data directory for integration tests."""
    data_dir = Path("tests/test_data/live_data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture(scope="module")
def downloader_with_config(config):
    """Provide WebsiteDownloader instance for live tests."""
    with WebsiteDownloader(config=config) as downloader:
        yield downloader


@pytest.fixture(scope="module")
def downloaded_html(downloader_with_config, live_data_dir):
    """
    Download real HTML file from website for integration testing.
    This fixture performs the download and validates the result.
    """
    year = "2024-25"
    grade = "8. osztály - általános iskolai kategória"
    round_name = "Írásbeli döntő"
    
    html_content = downloader_with_config.get_html_for_combination(year, grade, round_name)
    
    # Validate download in fixture
    assert html_content is not None, "Download failed - returned None"
    assert len(html_content) > 1000, f"Downloaded content too small: {len(html_content)} bytes"
    assert "Bolyai" in html_content, "Downloaded content doesn't contain expected text"
    
    # Save with proper filename for parser metadata extraction
    filename = "anyanyelv_2024-25_8.-osztaly---altalanos-iskolai-kategoria_irasbeli-donto.html"
    file_path = live_data_dir / filename
    file_path.write_text(html_content, encoding='utf-8')
    
    return file_path


@pytest.mark.integration
def test_end_to_end_download_and_parse(downloaded_html, config):
    """
    End-to-end integration test: download real data from website and parse it.
    
    This test validates the complete pipeline:
    1. Download real HTML from website (done by fixture)
    2. Parse the downloaded HTML
    3. Verify output structure and data quality
    """

    # Verify file was downloaded
    assert downloaded_html.exists(), f"Downloaded file not found: {downloaded_html}"
    assert downloaded_html.stat().st_size > 1000, "Downloaded file too small"
    
    # Parse the downloaded file
    parser = HtmlTableParser(downloaded_html, config)
    df = parser.parse()
    
    # Verify structure
    assert df.shape[0] > 0, "DataFrame should have rows"
    assert df.shape[1] == 7, f"DataFrame should have 7 columns, got {df.shape[1]}"
    
    # Verify columns
    expected_columns = ['ev', 'targy', 'iskola_nev', 'varos', 'megye', 'helyezes', 'evfolyam']
    assert list(df.columns) == expected_columns, f"Unexpected columns: {list(df.columns)}"
    
    # Verify data types
    assert df['helyezes'].dtype == 'int64', f"helyezes should be int64, got {df['helyezes'].dtype}"
    assert df['evfolyam'].dtype == 'int64', f"evfolyam should be int64, got {df['evfolyam'].dtype}"
    
    # Verify no nulls
    null_counts = df.isnull().sum()
    assert null_counts.sum() == 0, f"Found null values: {null_counts[null_counts > 0]}"
    
    # Verify metadata
    assert all(df['ev'] == '2024-25'), "Year should be 2024-25"
    assert all(df['targy'] == 'Anyanyelv'), "Subject should be Anyanyelv"
    assert all(df['evfolyam'] == 8), "Grade should be 8"
    
    # Verify helyezes is numeric and positive
    assert all(df['helyezes'] > 0), "All ranks should be positive"
    assert df['helyezes'].min() == 1, "First rank should be 1"
    
    # Verify school names and cities are properly separated
    assert all(df['iskola_nev'].str.len() > 0), "All school names should be non-empty"
    assert all(df['varos'].str.len() > 0), "All cities should be non-empty"
    
    # Verify no school names contain city information (proper splitting)
    # Budapest schools should not have district in school name
    budapest_schools = df[df['varos'].str.contains('Budapest')]
    if len(budapest_schools) > 0:
        # School names should not end with district markers
        assert not any(budapest_schools['iskola_nev'].str.contains(r'Budapest [IVX]+\.$')), \
            "School names should not contain Budapest district"
    
    # Verify specific data quality
    first_row = df.iloc[0]
    assert first_row['helyezes'] == 1, "First row should have rank 1"
    assert 'Általános Iskola' in first_row['iskola_nev'] or 'Gimnázium' in first_row['iskola_nev'], \
        "School name should contain school type"
