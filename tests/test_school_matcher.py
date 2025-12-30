"""Tests for school_matcher module."""

import pandas as pd
import pytest
from pathlib import Path

from tanulmanyi_versenyek.common.config import get_config
from tanulmanyi_versenyek.validation.school_matcher import (
    load_kir_database,
    load_school_mapping,
    normalize_city,
    cities_match,
    match_school,
    match_all_schools,
    apply_matches,
    generate_audit_file
)


@pytest.fixture
def test_config(tmp_path):
    """Create test configuration."""
    config = get_config()
    config['kir']['locations_file'] = 'tests/fixtures/kir_sample.xlsx'
    config['validation']['school_mapping_file'] = str(tmp_path / 'school_mapping.csv')
    return config


@pytest.fixture
def kir_df():
    """Load KIR sample fixture."""
    return pd.read_excel('tests/fixtures/kir_sample.xlsx')


class TestCityNormalization:
    """Tests for city normalization functions."""

    def test_normalize_city_basic(self):
        assert normalize_city("Budapest") == "budapest"
        assert normalize_city("Debrecen") == "debrecen"

    def test_normalize_city_budapest_kerulet(self):
        assert normalize_city("Budapest III. kerület") == "budapest iii."
        assert normalize_city("Budapest XIV. ker.") == "budapest xiv."

    def test_normalize_city_none(self):
        assert normalize_city(None) == ""
        assert normalize_city(pd.NA) == ""

    def test_normalize_city_whitespace(self):
        assert normalize_city("  Budapest  ") == "budapest"

    def test_cities_match_exact(self):
        assert cities_match("Budapest", "Budapest")
        assert cities_match("Debrecen", "Debrecen")

    def test_cities_match_budapest_special_case(self):
        assert cities_match("Budapest", "Budapest III. kerület")
        assert cities_match("Budapest", "Budapest XIV.")

    def test_cities_match_different(self):
        assert not cities_match("Budapest", "Debrecen")
        assert not cities_match("Szeged", "Pécs")


class TestSchoolMapping:
    """Tests for school mapping loader."""

    def test_load_school_mapping_valid_file(self, tmp_path):
        mapping_file = tmp_path / 'school_mapping.csv'
        mapping_file.write_text(
            'school_name;city;corrected_school_name;comment\n'
            'Test School;Budapest;Official Test School;Manual mapping\n',
            encoding='utf-8'
        )

        config = get_config()
        config['validation']['school_mapping_file'] = str(mapping_file)

        mapping = load_school_mapping(config)

        assert len(mapping) == 1
        assert ('Test School', 'Budapest') in mapping
        assert mapping[('Test School', 'Budapest')]['corrected_school_name'] == 'Official Test School'

    def test_load_school_mapping_missing_file(self, test_config):
        mapping = load_school_mapping(test_config)
        assert mapping == {}

    def test_load_school_mapping_empty_corrected_name(self, tmp_path):
        mapping_file = tmp_path / 'school_mapping.csv'
        mapping_file.write_text(
            'school_name;city;corrected_school_name;comment\n'
            'Test School;Budapest;;Should be skipped\n',
            encoding='utf-8'
        )

        config = get_config()
        config['validation']['school_mapping_file'] = str(mapping_file)

        mapping = load_school_mapping(config)
        assert len(mapping) == 0


class TestKIRDatabase:
    """Tests for KIR database loader."""

    def test_load_kir_database_valid(self, test_config):
        kir_df = load_kir_database(test_config)
        assert len(kir_df) > 0
        assert 'Intézmény megnevezése' in kir_df.columns
        assert 'A feladatellátási hely települése' in kir_df.columns

    def test_load_kir_database_missing_file(self, test_config):
        test_config['kir']['locations_file'] = 'nonexistent.xlsx'
        with pytest.raises(FileNotFoundError):
            load_kir_database(test_config)


class TestSchoolMatching:
    """Tests for school matching logic."""

    def test_match_school_manual_override(self, kir_df, test_config):
        # Get a real school from KIR
        real_school = kir_df.iloc[0]
        school_name = real_school['Intézmény megnevezése']
        city = real_school['A feladatellátási hely települése']

        manual_mapping = {
            ('Test School', 'Budapest'): {
                'corrected_school_name': school_name,
                'comment': 'Manual test'
            }
        }

        result = match_school('Test School', 'Budapest', kir_df, manual_mapping, test_config)

        assert result is not None
        assert result['match_method'] == 'MANUAL'
        assert result['matched_school_name'] == school_name
        assert result['confidence_score'] is None
        assert result['comment'] == 'Manual test'

    def test_match_school_high_confidence(self, kir_df, test_config):
        # Use exact school name from KIR
        real_school = kir_df.iloc[0]
        school_name = real_school['Intézmény megnevezése']
        city = real_school['A feladatellátási hely települése']

        result = match_school(school_name, city, kir_df, {}, test_config)

        assert result is not None
        assert result['match_method'] == 'AUTO_HIGH'
        assert result['confidence_score'] >= test_config['matching']['high_confidence_threshold']
        assert result['comment'] == ''

    def test_match_school_no_candidates(self, kir_df, test_config):
        result = match_school('Nonexistent School', 'Nonexistent City', kir_df, {}, test_config)
        assert result is None

    def test_match_school_budapest_no_district(self, kir_df, test_config):
        # Find a Budapest school in KIR
        budapest_schools = kir_df[kir_df['A feladatellátási hely települése'].str.contains('Budapest', na=False)]
        assert len(budapest_schools) > 0, "Test fixture must contain Budapest schools"

        real_school = budapest_schools.iloc[0]
        school_name = real_school['Intézmény megnevezése']

        # Search with just "Budapest" (no district)
        result = match_school(school_name, 'Budapest', kir_df, {}, test_config)

        assert result is not None, "Budapest special case should match schools in any Budapest district"
        assert 'Budapest' in result['matched_city']


class TestMatchApplication:
    """Tests for match application to DataFrame."""

    def test_apply_matches_updates_columns(self, kir_df):
        # Create sample competition data
        real_school = kir_df.iloc[0]
        our_df = pd.DataFrame({
            'ev': ['2024-25'],
            'targy': ['Anyanyelv'],
            'iskola_nev': ['Test School'],
            'varos': ['Budapest'],
            'helyezes': [1],
            'evfolyam': [8]
        })

        # Create match results
        match_results = pd.DataFrame({
            'our_school_name': ['Test School'],
            'our_city': ['Budapest'],
            'matched_school_name': [real_school['Intézmény megnevezése']],
            'matched_city': [real_school['A feladatellátási hely települése']],
            'matched_county': [real_school['A feladatellátási hely vármegyéje']],
            'matched_region': [real_school['A feladatellátási hely régiója']],
            'confidence_score': [95.0],
            'match_method': ['AUTO_HIGH'],
            'status': ['APPLIED'],
            'comment': ['']
        })

        result_df = apply_matches(our_df, match_results)

        assert len(result_df) == 1
        assert 'vármegye' in result_df.columns
        assert 'régió' in result_df.columns
        assert result_df.iloc[0]['iskola_nev'] == real_school['Intézmény megnevezése']
        assert pd.notna(result_df.iloc[0]['vármegye'])

    def test_apply_matches_drops_unmatched(self):
        our_df = pd.DataFrame({
            'ev': ['2024-25'],
            'targy': ['Anyanyelv'],
            'iskola_nev': ['Test School'],
            'varos': ['Budapest'],
            'helyezes': [1],
            'evfolyam': [8]
        })

        match_results = pd.DataFrame({
            'our_school_name': ['Test School'],
            'our_city': ['Budapest'],
            'matched_school_name': [None],
            'matched_city': [None],
            'matched_county': [None],
            'matched_region': [None],
            'confidence_score': [None],
            'match_method': ['DROPPED'],
            'status': ['NOT_APPLIED'],
            'comment': ['Low confidence - needs manual review']
        })

        result_df = apply_matches(our_df, match_results)

        assert len(result_df) == 0

    def test_apply_matches_normalizes_city(self, kir_df):
        # Use a Budapest school with "kerület" in city name
        budapest_schools = kir_df[kir_df['A feladatellátási hely települése'].str.contains('kerület', na=False)]
        assert len(budapest_schools) > 0, "Test fixture must contain Budapest schools with 'kerület' suffix"

        real_school = budapest_schools.iloc[0]

        our_df = pd.DataFrame({
            'ev': ['2024-25'],
            'targy': ['Anyanyelv'],
            'iskola_nev': ['Test School'],
            'varos': ['Budapest'],
            'helyezes': [1],
            'evfolyam': [8]
        })

        match_results = pd.DataFrame({
            'our_school_name': ['Test School'],
            'our_city': ['Budapest'],
            'matched_school_name': [real_school['Intézmény megnevezése']],
            'matched_city': [real_school['A feladatellátási hely települése']],
            'matched_county': [real_school['A feladatellátási hely vármegyéje']],
            'matched_region': [real_school['A feladatellátási hely régiója']],
            'confidence_score': [95.0],
            'match_method': ['AUTO_HIGH'],
            'status': ['APPLIED'],
            'comment': ['']
        })

        result_df = apply_matches(our_df, match_results)

        # City should not contain " kerület"
        assert ' kerület' not in result_df.iloc[0]['varos'], "City should have 'kerület' suffix removed"


class TestAuditGeneration:
    """Tests for audit file generation."""

    def test_generate_audit_file_structure(self, tmp_path):
        match_results = pd.DataFrame({
            'our_school_name': ['School A', 'School B'],
            'our_city': ['Budapest', 'Debrecen'],
            'matched_school_name': ['Official School A', None],
            'matched_city': ['Budapest', None],
            'matched_county': ['Budapest', None],
            'matched_region': ['Közép-Magyarország', None],
            'confidence_score': [95.0, None],
            'match_method': ['AUTO_HIGH', 'DROPPED'],
            'status': ['APPLIED', 'NOT_APPLIED'],
            'comment': ['', 'Low confidence - needs manual review']
        })

        output_path = tmp_path / 'audit.csv'
        generate_audit_file(match_results, output_path)

        assert output_path.exists()

        audit_df = pd.read_csv(output_path, sep=';', encoding='utf-8')
        assert 'comment' in audit_df.columns
        assert len(audit_df) == 2

    def test_generate_audit_file_comments(self, tmp_path):
        match_results = pd.DataFrame({
            'our_school_name': ['School A', 'School B', 'School C'],
            'our_city': ['Budapest', 'Debrecen', 'Szeged'],
            'matched_school_name': ['Official A', 'Official B', None],
            'matched_city': ['Budapest', 'Debrecen', None],
            'matched_county': ['Budapest', 'Hajdú-Bihar', None],
            'matched_region': ['Közép-Magyarország', 'Észak-Alföld', None],
            'confidence_score': [None, 85.0, None],
            'match_method': ['MANUAL', 'AUTO_MEDIUM', 'DROPPED'],
            'status': ['APPLIED', 'APPLIED', 'NOT_APPLIED'],
            'comment': ['Manual test mapping', '', 'Low confidence - needs manual review']
        })

        output_path = tmp_path / 'audit.csv'
        generate_audit_file(match_results, output_path)

        audit_df = pd.read_csv(output_path, sep=';', encoding='utf-8')

        # Check comments
        manual_row = audit_df[audit_df['match_method'] == 'MANUAL'].iloc[0]
        assert manual_row['comment'] == 'Manual test mapping'

        auto_row = audit_df[audit_df['match_method'] == 'AUTO_MEDIUM'].iloc[0]
        assert pd.isna(auto_row['comment']) or auto_row['comment'] == ''

        dropped_row = audit_df[audit_df['match_method'] == 'DROPPED'].iloc[0]
        assert 'Low confidence' in dropped_row['comment']


class TestBatchMatching:
    """Tests for batch school matching."""

    def test_match_all_schools(self, kir_df, test_config):
        # Create sample data with one real school and one fake
        real_school = kir_df.iloc[0]
        our_df = pd.DataFrame({
            'iskola_nev': [real_school['Intézmény megnevezése'], 'Nonexistent School'],
            'varos': [real_school['A feladatellátási hely települése'], 'Nonexistent City']
        })

        results = match_all_schools(our_df, kir_df, {}, test_config)

        assert len(results) == 2
        assert results.iloc[0]['status'] == 'APPLIED'
        assert results.iloc[1]['status'] == 'NOT_APPLIED'
