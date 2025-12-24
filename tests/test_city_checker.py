"""Unit tests for city_checker module."""

import pandas as pd
import pytest

from tanulmanyi_versenyek.validation.city_checker import (
    _is_valid_entry,
    _parse_mapping_csv,
    load_city_mapping,
    apply_city_mapping,
    _detect_variations,
    _build_allowed_combinations,
    check_city_variations
)


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


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'iskola_nev': ['School A', 'School B', 'School C', 'School C', 'School D'],
        'varos': ['CITY1', 'City2-Suburb', 'City3', 'City4', 'City5'],
        'ev': ['2024-25', '2024-25', '2024-25', '2024-25', '2024-25']
    })


@pytest.fixture
def sample_mapping():
    """Create a sample mapping dictionary."""
    return {
        ('School A', 'CITY1'): {
            'corrected_city': 'City1',
            'comment': 'Normalize case',
            'is_valid': False
        },
        ('School B', 'City2-Suburb'): {
            'corrected_city': 'City2',
            'comment': 'Map suburb',
            'is_valid': False
        },
        ('School C', 'City3'): {
            'corrected_city': '',
            'comment': 'VALID - different schools',
            'is_valid': True
        },
        ('School C', 'City4'): {
            'corrected_city': '',
            'comment': 'VALID - different schools',
            'is_valid': True
        }
    }


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

    def test_parse_valid_csv(self, valid_csv_file):
        mapping = _parse_mapping_csv(valid_csv_file)

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

    def test_parse_missing_file(self, tmp_path):
        non_existent = tmp_path / "missing.csv"
        mapping = _parse_mapping_csv(non_existent)
        assert mapping == {}

    def test_parse_malformed_csv(self, malformed_csv_file):
        mapping = _parse_mapping_csv(malformed_csv_file)
        assert mapping == {}


class TestLoadCityMapping:
    """Tests for load_city_mapping function."""

    def test_load_with_valid_file(self, valid_csv_file):
        config = {
            'validation': {
                'city_mapping_file': str(valid_csv_file)
            }
        }
        mapping = load_city_mapping(config)

        assert len(mapping) == 3
        assert ('School A', 'CITY1') in mapping
        assert ('School B', 'City2-Suburb') in mapping
        assert ('School C', 'City3') in mapping

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
        corrected_df, count = apply_city_mapping(sample_dataframe, sample_mapping)

        assert count == 2
        assert corrected_df.loc[0, 'varos'] == 'City1'
        assert corrected_df.loc[1, 'varos'] == 'City2'
        assert corrected_df.loc[2, 'varos'] == 'City3'
        assert corrected_df.loc[3, 'varos'] == 'City4'

    def test_apply_with_empty_mapping(self, sample_dataframe):
        corrected_df, count = apply_city_mapping(sample_dataframe, {})

        assert count == 0
        pd.testing.assert_frame_equal(corrected_df, sample_dataframe)

    def test_apply_creates_copy(self, sample_dataframe, sample_mapping):
        original_city = sample_dataframe.loc[0, 'varos']
        corrected_df, count = apply_city_mapping(sample_dataframe, sample_mapping)

        assert sample_dataframe.loc[0, 'varos'] == original_city
        assert corrected_df.loc[0, 'varos'] != original_city

    def test_apply_composite_key(self):
        df = pd.DataFrame({
            'iskola_nev': ['School X', 'School X'],
            'varos': ['CityA', 'CityB']
        })
        mapping = {
            ('School X', 'CityA'): {'corrected_city': 'City A', 'comment': 'Fix', 'is_valid': False},
            ('School X', 'CityB'): {'corrected_city': 'City B', 'comment': 'Fix', 'is_valid': False}
        }

        corrected_df, count = apply_city_mapping(df, mapping)

        assert count == 2
        assert corrected_df.loc[0, 'varos'] == 'City A'
        assert corrected_df.loc[1, 'varos'] == 'City B'


class TestDetectVariations:
    """Tests for _detect_variations function."""

    def test_detect_with_variations(self):
        df = pd.DataFrame({
            'iskola_nev': ['School A', 'School A', 'School B'],
            'varos': ['City1', 'City2', 'City3']
        })

        variations = _detect_variations(df)

        assert len(variations) == 1
        assert 'School A' in variations
        assert variations['School A']['count'] == 2
        assert set(variations['School A']['cities']) == {'City1', 'City2'}

    def test_detect_no_variations(self):
        df = pd.DataFrame({
            'iskola_nev': ['School A', 'School B', 'School C'],
            'varos': ['City1', 'City2', 'City3']
        })

        variations = _detect_variations(df)

        assert len(variations) == 0

    def test_detect_multiple_schools_with_variations(self):
        df = pd.DataFrame({
            'iskola_nev': ['School A', 'School A', 'School B', 'School B', 'School C'],
            'varos': ['City1', 'City2', 'City3', 'City4', 'City5']
        })

        variations = _detect_variations(df)

        assert len(variations) == 2
        assert 'School A' in variations
        assert 'School B' in variations
        assert 'School C' not in variations


class TestBuildAllowedCombinations:
    """Tests for _build_allowed_combinations function."""

    def test_build_with_valid_and_corrections(self):
        mapping = {
            ('School A', 'CITY1'): {'corrected_city': 'City1', 'comment': 'Fix', 'is_valid': False},
            ('School B', 'City2'): {'corrected_city': '', 'comment': 'VALID', 'is_valid': True},
            ('School C', 'City3'): {'corrected_city': 'City3Fixed', 'comment': 'Fix', 'is_valid': False}
        }

        allowed = _build_allowed_combinations(mapping)

        assert len(allowed) == 3
        assert ('School A', 'City1') in allowed
        assert ('School B', 'City2') in allowed
        assert ('School C', 'City3Fixed') in allowed
        assert ('School A', 'CITY1') not in allowed

    def test_build_empty_mapping(self):
        allowed = _build_allowed_combinations({})
        assert len(allowed) == 0


class TestCheckCityVariations:
    """Tests for check_city_variations function."""

    def test_check_all_valid(self, sample_dataframe, sample_mapping):
        stats = check_city_variations(sample_dataframe, sample_mapping)

        assert stats['total_schools_with_variations'] == 1
        assert stats['valid_combinations'] == 2
        assert stats['unmapped_combinations'] == 0

    def test_check_partially_mapped(self):
        df = pd.DataFrame({
            'iskola_nev': ['School X', 'School X', 'School X'],
            'varos': ['City1', 'City2', 'City3']
        })
        mapping = {
            ('School X', 'OrigCity1'): {'corrected_city': 'City1', 'comment': 'Fix', 'is_valid': False},
            ('School X', 'City2'): {'corrected_city': '', 'comment': 'VALID', 'is_valid': True}
        }

        stats = check_city_variations(df, mapping)

        assert stats['total_schools_with_variations'] == 1
        assert stats['valid_combinations'] == 2
        assert stats['unmapped_combinations'] == 1

    def test_check_no_variations(self):
        df = pd.DataFrame({
            'iskola_nev': ['School A', 'School B'],
            'varos': ['City1', 'City2']
        })

        stats = check_city_variations(df, {})

        assert stats['total_schools_with_variations'] == 0
        assert stats['valid_combinations'] == 0
        assert stats['unmapped_combinations'] == 0

    def test_check_all_unmapped(self):
        df = pd.DataFrame({
            'iskola_nev': ['School Y', 'School Y'],
            'varos': ['CityA', 'CityB']
        })

        stats = check_city_variations(df, {})

        assert stats['total_schools_with_variations'] == 1
        assert stats['valid_combinations'] == 0
        assert stats['unmapped_combinations'] == 2

    def test_check_after_correction_no_false_warnings(self):
        """Test that corrected cities don't trigger warnings.

        Scenario: School has typo 'citB' corrected to 'CityB'.
        After correction, both entries show 'CityB'.
        Should not warn about 'CityB' since it's in allowed combinations.
        """
        df_after_correction = pd.DataFrame({
            'iskola_nev': ['School A', 'School A'],
            'varos': ['CityB', 'CityB']
        })
        mapping = {
            ('School A', 'citB'): {'corrected_city': 'CityB', 'comment': 'Fix typo', 'is_valid': False}
        }

        stats = check_city_variations(df_after_correction, mapping)

        assert stats['total_schools_with_variations'] == 0
        assert stats['valid_combinations'] == 0
        assert stats['unmapped_combinations'] == 0
