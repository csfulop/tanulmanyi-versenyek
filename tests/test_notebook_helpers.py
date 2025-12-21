"""
Unit tests for notebook helper functions.

Note: These functions are duplicated from the notebook for testing purposes.
Any changes to the notebook helper functions must be reflected here.
"""

import pytest
import pandas as pd


@pytest.fixture
def sample_df():
    """Create a sample dataframe with realistic test data."""
    return pd.DataFrame({
        'ev': [
            '2023-24', '2023-24', '2023-24', '2023-24', '2023-24',
            '2024-25', '2024-25', '2024-25', '2024-25', '2024-25'
        ],
        'targy': ['Anyanyelv'] * 10,
        'iskola_nev': [
            'Mustármag Keresztény Óvoda, Általános Iskola és Gimnázium',
            'Hajdúböszörményi Bocskai István Általános Iskola',
            'Veszprémi Deák Ferenc Általános Iskola',
            'Mustármag Keresztény Óvoda, Általános Iskola és Gimnázium',
            'Németh Imre Általános Iskola',
            'Mustármag Keresztény Óvoda, Általános Iskola és Gimnázium',
            'Petőfi Utcai Általános Iskola',
            'Hajdúböszörményi Bocskai István Általános Iskola',
            'Hétvezér Általános Iskola',
            'Veszprémi Deák Ferenc Általános Iskola'
        ],
        'varos': [
            'Budapest III.', 'Hajdúböszörmény', 'Veszprém', 'Budapest III.', 'Budapest XIV.',
            'Budapest III.', 'Békéscsaba', 'Hajdúböszörmény', 'Székesfehérvár', 'Veszprém'
        ],
        'megye': [''] * 10,
        'helyezes': [1, 2, 3, 5, 8, 1, 2, 3, 7, 10],
        'evfolyam': [3, 3, 4, 7, 8, 4, 5, 7, 8, 8]
    })


def test_fixture_structure(sample_df):
    """Verify the test fixture has correct structure."""
    assert len(sample_df) == 10
    assert list(sample_df.columns) == ['ev', 'targy', 'iskola_nev', 'varos', 'megye', 'helyezes', 'evfolyam']
    assert sample_df['targy'].unique().tolist() == ['Anyanyelv']
