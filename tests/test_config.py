import pytest
from tanulmanyi_versenyek.common.config import get_config

def test_get_config_returns_dict_and_has_data_source():
    """
    Test that get_config() returns a dictionary and contains the 'data_source' key.
    """
    config = get_config()
    assert isinstance(config, dict)
    assert "data_source" in config

