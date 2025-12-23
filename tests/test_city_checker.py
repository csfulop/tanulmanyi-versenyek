"""Unit tests for city_checker module."""

import logging

import pytest

from tanulmanyi_versenyek.validation.city_checker import (
    _is_valid_entry,
    _parse_mapping_csv,
    load_city_mapping
)


@pytest.fixture
def logger():
    """Create a logger for testing."""
    return logging.getLogger('test')


@pytest.fixture
def valid_csv_file(tmp_path):
    """Create a valid mapping CSV file."""
    csv_content = """school_name;original_city;corrected_city;comment
School A;CITY1;City1;Normalize case
School B;City2-Suburb;City2;Map suburb to parent
School C;City3;;VALID - different schools"""
    csv_file = tmp_path / "mapping.csv"
    csv_file.write_text(csv_content, encoding='utf-8')
    return csv_file


@pytest.fixture
def malformed_csv_file(tmp_path):
    """Create a malformed CSV file."""
    csv_content = """invalid;csv;structure
data;without;proper;columns"""
    csv_file = tmp_path / "malformed.csv"
    csv_file.write_text(csv_content, encoding='utf-8')
    return csv_file


class TestIsValidEntry:
    """Tests for _is_valid_entry helper function."""

    def test_valid_uppercase(self):
        assert _is_valid_entry("VALID - different schools")

    def test_valid_lowercase(self):
        assert _is_valid_entry("valid - different schools")

    def test_valid_mixed_case(self):
        assert _is_valid_entry("Valid - different schools")

    def test_not_valid(self):
        assert not _is_valid_entry("Normalize case")

    def test_empty_string(self):
        assert not _is_valid_entry("")


class TestParseMappingCsv:
    """Tests for _parse_mapping_csv function."""

    def test_parse_valid_csv(self, valid_csv_file, logger):
        mapping = _parse_mapping_csv(valid_csv_file, logger)

        assert len(mapping) == 3
        assert ('School A', 'CITY1') in mapping
        assert mapping[('School A', 'CITY1')]['corrected_city'] == 'City1'
        assert mapping[('School A', 'CITY1')]['comment'] == 'Normalize case'
        assert not mapping[('School A', 'CITY1')]['is_valid']

        assert ('School B', 'City2-Suburb') in mapping
        assert mapping[('School B', 'City2-Suburb')]['corrected_city'] == 'City2'

        assert ('School C', 'City3') in mapping
        assert mapping[('School C', 'City3')]['corrected_city'] == ''
        assert mapping[('School C', 'City3')]['is_valid']

    def test_parse_missing_file(self, tmp_path, logger):
        non_existent = tmp_path / "missing.csv"
        mapping = _parse_mapping_csv(non_existent, logger)
        assert mapping == {}

    def test_parse_malformed_csv(self, malformed_csv_file, logger):
        mapping = _parse_mapping_csv(malformed_csv_file, logger)
        assert mapping == {}


class TestLoadCityMapping:
    """Tests for load_city_mapping function."""

    def test_load_with_valid_file(self, valid_csv_file, logger):
        config = {
            'validation': {
                'city_mapping_file': str(valid_csv_file)
            }
        }
        mapping = load_city_mapping(config, logger)

        assert len(mapping) == 3
        assert ('School A', 'CITY1') in mapping
        assert ('School B', 'City2-Suburb') in mapping
        assert ('School C', 'City3') in mapping

    def test_load_missing_file(self, tmp_path, logger):
        config = {
            'validation': {
                'city_mapping_file': str(tmp_path / "nonexistent.csv")
            }
        }
        mapping = load_city_mapping(config, logger)
        assert mapping == {}

    def test_load_no_config(self, logger):
        config = {}
        mapping = load_city_mapping(config, logger)
        assert mapping == {}

    def test_load_no_validation_section(self, logger):
        config = {'other': 'data'}
        mapping = load_city_mapping(config, logger)
        assert mapping == {}

    def test_load_malformed_csv(self, malformed_csv_file, logger):
        config = {
            'validation': {
                'city_mapping_file': str(malformed_csv_file)
            }
        }
        mapping = load_city_mapping(config, logger)
        assert mapping == {}
