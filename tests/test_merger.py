import pytest
import pandas as pd
from pathlib import Path
import tempfile
from tanulmanyi_versenyek.merger.data_merger import merge_processed_data

def test_merge_with_sample_data():
    """
    Integration test for merge_processed_data() using sample CSV files.
    Tests concatenation and deduplication logic.
    """
    test_data_dir = Path(__file__).parent / 'test_data' / 'sample_processed_csvs'
    assert test_data_dir.exists(), f"Test data directory not found: {test_data_dir}"

    csv_files = list(test_data_dir.glob('*.csv'))
    assert len(csv_files) == 3, f"Expected 3 CSV files, found {len(csv_files)}"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        master_csv_path = tmpdir_path / 'test_master.csv'

        test_config = {
            'paths': {
                'processed_csv_dir': str(test_data_dir),
                'master_csv': str(master_csv_path)
            }
        }

        result_df = merge_processed_data(test_config)

        assert not result_df.empty, "Result DataFrame should not be empty"
        assert len(result_df) == 7, f"Expected 7 unique rows after deduplication, got {len(result_df)}"

        expected_columns = ['ev', 'targy', 'iskola_nev', 'varos', 'megye', 'helyezes', 'evfolyam']
        assert list(result_df.columns) == expected_columns, f"Columns mismatch: {list(result_df.columns)}"

        unique_schools = result_df['iskola_nev'].nunique()
        assert unique_schools == 7, f"Expected 7 unique schools, got {unique_schools}"

        duplicate_check = result_df.duplicated(subset=['ev', 'evfolyam', 'iskola_nev', 'helyezes'])
        assert not duplicate_check.any(), "Found duplicates after deduplication"

        assert master_csv_path.exists(), "Master CSV file was not created"

        saved_df = pd.read_csv(master_csv_path, sep=';', encoding='utf-8')
        assert len(saved_df) == 7, "Saved CSV has incorrect number of rows"
