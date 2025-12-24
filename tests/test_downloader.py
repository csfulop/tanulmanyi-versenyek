import pytest
import logging
import os
from tanulmanyi_versenyek.common.config import get_config
from tanulmanyi_versenyek.common.logger import setup_logging
from tanulmanyi_versenyek.scraper.bolyai_downloader import WebsiteDownloader

# Setup logging for tests (optional, but good for debugging)
setup_logging()
test_logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def downloader_with_config():
    """
    Fixture to provide a WebsiteDownloader instance with loaded config for testing.
    Uses 'module' scope to ensure browser is launched/closed once per test module.
    """
    config = get_config()
    with WebsiteDownloader(config=config) as downloader:
        yield downloader

def test_get_available_years_from_local_html(downloader_with_config):
    """
    Test that get_available_years correctly extracts year strings from a local HTML file.
    """
    test_logger.info("Running test_get_available_years_from_local_html.")
    
    # Path to the local HTML fixture
    test_data_path = os.path.join(
        os.path.dirname(__file__), 
        "test_data", 
        "sample_archive_page.html"
    )

    assert os.path.exists(test_data_path), f"Test data file not found: {test_data_path}"

    with open(test_data_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    years = downloader_with_config.get_available_years(html_content=html_content)

    test_logger.debug(f"Extracted years: {years}")

    # Assertions based on the content of sample_archive_page.html
    # From the manual inspection, we know these years are present.
    expected_years = ["2015-16", "2016-17", "2017-18", "2018-19", "2019-20", 
                      "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
    
    assert isinstance(years, list)
    assert len(years) > 0
    assert years == expected_years
    test_logger.info("test_get_available_years_from_local_html passed.")
