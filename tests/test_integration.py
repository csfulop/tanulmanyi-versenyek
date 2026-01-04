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
    assert df.shape[1] == 8, f"DataFrame should have 8 columns, got {df.shape[1]}"
    
    # Verify columns
    expected_columns = ['ev', 'targy', 'iskola_nev', 'varos', 'varmegye', 'regio', 'helyezes', 'evfolyam']
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


@pytest.fixture(scope="module")
def downloaded_kir_file(live_data_dir, config):
    """
    Download real KIR file for integration testing.
    Downloads once per test session and reuses.
    Note: Must run after downloaded_html to avoid clearing the HTML file.
    """
    import pandas as pd
    from tanulmanyi_versenyek.kir_downloader.kir_scraper import get_latest_kir_url, download_kir_file
    
    kir_path = live_data_dir / 'kir_feladatellatasi_helyek.xlsx'
    
    # Download KIR file (without clearing directory)
    index_url = config['kir']['index_url']
    pattern = 'kir_mukodo_feladatellatasi_helyek'
    
    url = get_latest_kir_url(index_url, pattern)
    download_kir_file(url, kir_path)
    
    assert kir_path.exists(), "KIR file should be downloaded"
    
    return kir_path


@pytest.mark.integration
def test_full_pipeline_with_kir(downloaded_html, downloaded_kir_file, config, tmp_path):
    """Test complete pipeline from parse to final output with school matching."""
    import pandas as pd
    from tanulmanyi_versenyek.parser.html_parser import HtmlTableParser
    from tanulmanyi_versenyek.validation.city_checker import load_city_mapping, apply_city_mapping
    from tanulmanyi_versenyek.validation.school_matcher import (
        load_kir_database,
        load_school_mapping,
        match_all_schools,
        apply_matches,
        generate_audit_file
    )

    # Parse the downloaded HTML to get test data
    parser = HtmlTableParser(downloaded_html, config)
    test_df = parser.parse()
    assert len(test_df) > 0, "Test DataFrame should not be empty"
    original_count = len(test_df)

    # Load full KIR database
    temp_config = config.copy()
    temp_config['kir'] = config['kir'].copy()
    temp_config['kir']['locations_file'] = str(downloaded_kir_file)
    
    kir_dict = load_kir_database(temp_config)
    assert len(kir_dict) > 0, "KIR dict should not be empty"

    # Apply city corrections
    city_mapping = load_city_mapping(temp_config)
    test_df, corrections_applied = apply_city_mapping(test_df, city_mapping)

    # Match schools (filtering by city happens inside match_all_schools)
    school_mapping = load_school_mapping(temp_config)
    match_results = match_all_schools(test_df, kir_dict, school_mapping, temp_config)

    # Verify match results structure
    assert 'our_school_name' in match_results.columns
    assert 'match_method' in match_results.columns
    assert 'status' in match_results.columns
    assert len(match_results) > 0

    # Apply matches
    test_df = apply_matches(test_df, match_results)

    # Verify new columns exist
    assert 'varmegye' in test_df.columns, "varmegye column should be added"
    assert 'regio' in test_df.columns, "regio column should be added"

    # Verify some schools matched (not all dropped)
    final_count = len(test_df)
    assert final_count > 0, "Should have some matched schools"
    assert final_count <= original_count, "Final count should be <= original count"

    # Verify audit file generation
    audit_path = tmp_path / 'audit.csv'
    generate_audit_file(match_results, audit_path)
    assert audit_path.exists(), "Audit file should be created"

    audit_df = pd.read_csv(audit_path, sep=';', encoding='utf-8')
    assert len(audit_df) == len(match_results), "Audit file should have all match results"
    
    # Verify at least some schools were matched (not all dropped)
    applied_count = len(match_results[match_results['status'] == 'APPLIED'])
    assert applied_count > 0, "Should have at least some matched schools"
