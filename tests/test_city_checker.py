"""Unit tests for city_checker module."""

import pandas as pd
import pytest

from tanulmanyi_versenyek.validation.city_checker import (
    _parse_mapping_csv,
    load_city_mapping,
    apply_city_mapping
)


@pytest.fixture
def valid_csv_file(tmp_path):
    """Create a valid mapping CSV file."""
    csv_content = """original_city;corrected_city;comment
CITY1;City1;Normalize case
City2-Suburb;City2;Map suburb to parent"""
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


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'iskola_nev': ['School A', 'School B', 'School C', 'School D'],
        'varos': ['CITY1', 'City2-Suburb', 'City3', 'City5'],
        'ev': ['2024-25', '2024-25', '2024-25', '2024-25']
    })


@pytest.fixture
def sample_mapping():
    """Create a sample mapping dictionary."""
    return {
        'CITY1': 'City1',
        'City2-Suburb': 'City2'
    }


class TestParseMappingCsv:
    """Tests for _parse_mapping_csv function."""

    def test_parse_valid_csv(self, valid_csv_file):
        mapping = _parse_mapping_csv(valid_csv_file)

        assert len(mapping) == 2
        assert mapping['CITY1'] == 'City1'
        assert mapping['City2-Suburb'] == 'City2'

    def test_parse_missing_file(self, tmp_path):
        non_existent = tmp_path / "missing.csv"
        mapping = _parse_mapping_csv(non_existent)
        assert mapping == {}

    def test_parse_malformed_csv(self, malformed_csv_file):
        mapping = _parse_mapping_csv(malformed_csv_file)
        assert mapping == {}

    def test_parse_empty_corrected_city(self, tmp_path):
        csv_content = """original_city;corrected_city;comment
City1;;Empty correction
City2;City2Fixed;Valid correction"""
        csv_file = tmp_path / "mapping.csv"
        csv_file.write_text(csv_content, encoding='utf-8')

        mapping = _parse_mapping_csv(csv_file)

        assert len(mapping) == 1
        assert 'City2' in mapping
        assert 'City1' not in mapping


class TestLoadCityMapping:
    """Tests for load_city_mapping function."""

    def test_load_with_valid_file(self, valid_csv_file):
        config = {
            'validation': {
                'city_mapping_file': str(valid_csv_file)
            }
        }
        mapping = load_city_mapping(config)

        assert len(mapping) == 2
        assert mapping['CITY1'] == 'City1'
        assert mapping['City2-Suburb'] == 'City2'

    def test_load_missing_file(self, tmp_path):
        config = {
            'validation': {
                'city_mapping_file': str(tmp_path / "nonexistent.csv")
            }
        }
        mapping = load_city_mapping(config)
        assert mapping == {}

    def test_load_no_config(self):
        config = {}
        mapping = load_city_mapping(config)
        assert mapping == {}

    def test_load_no_validation_section(self):
        config = {'other': 'data'}
        mapping = load_city_mapping(config)
        assert mapping == {}

    def test_load_malformed_csv(self, malformed_csv_file):
        config = {
            'validation': {
                'city_mapping_file': str(malformed_csv_file)
            }
        }
        mapping = load_city_mapping(config)
        assert mapping == {}


class TestApplyCityMapping:
    """Tests for apply_city_mapping function."""

    def test_apply_corrections(self, sample_dataframe, sample_mapping):
        corrected_df, stats = apply_city_mapping(sample_dataframe, sample_mapping)

        assert stats['corrected'] == 2
        assert stats['dropped'] == 0
        assert corrected_df.loc[0, 'varos'] == 'City1'
        assert corrected_df.loc[1, 'varos'] == 'City2'
        assert corrected_df.loc[2, 'varos'] == 'City3'
        assert corrected_df.loc[3, 'varos'] == 'City5'

    def test_apply_with_empty_mapping(self, sample_dataframe):
        corrected_df, stats = apply_city_mapping(sample_dataframe, {})

        assert stats['corrected'] == 0
        assert stats['dropped'] == 0
        pd.testing.assert_frame_equal(corrected_df, sample_dataframe)

    def test_apply_creates_copy(self, sample_dataframe, sample_mapping):
        original_city = sample_dataframe.loc[0, 'varos']
        corrected_df, stats = apply_city_mapping(sample_dataframe, sample_mapping)

        assert stats['corrected'] == 2
        assert sample_dataframe.loc[0, 'varos'] == original_city
        assert corrected_df.loc[0, 'varos'] != original_city

    def test_apply_multiple_same_city(self):
        df = pd.DataFrame({
            'iskola_nev': ['School A', 'School B', 'School C'],
            'varos': ['CITY1', 'CITY1', 'City2']
        })
        mapping = {'CITY1': 'City1'}

        corrected_df, stats = apply_city_mapping(df, mapping)

        assert stats['corrected'] == 2
        assert stats['dropped'] == 0
        assert corrected_df.loc[0, 'varos'] == 'City1'
        assert corrected_df.loc[1, 'varos'] == 'City1'
        assert corrected_df.loc[2, 'varos'] == 'City2'

    def test_apply_drop_city(self):
        df = pd.DataFrame({
            'iskola_nev': ['School A', 'School B', 'School C'],
            'varos': ['City1', 'City2', 'City3']
        })
        mapping = {'City2': 'DROP'}

        corrected_df, stats = apply_city_mapping(df, mapping)

        assert stats['corrected'] == 0
        assert stats['dropped'] == 1
        assert len(corrected_df) == 2
        assert 'School B' not in corrected_df['iskola_nev'].values
        assert corrected_df.loc[0, 'iskola_nev'] == 'School A'
        assert corrected_df.loc[2, 'iskola_nev'] == 'School C'

    def test_apply_drop_and_correct(self):
        df = pd.DataFrame({
            'iskola_nev': ['School A', 'School B', 'School C', 'School D'],
            'varos': ['CITY1', 'City2', 'CITY1', 'City3']
        })
        mapping = {'CITY1': 'City1', 'City2': 'DROP'}

        corrected_df, stats = apply_city_mapping(df, mapping)

        assert stats['corrected'] == 2
        assert stats['dropped'] == 1
        assert len(corrected_df) == 3
        assert 'School B' not in corrected_df['iskola_nev'].values
