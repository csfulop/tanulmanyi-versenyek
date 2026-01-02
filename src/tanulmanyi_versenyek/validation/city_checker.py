"""City name validation and mapping functionality."""

import logging
from pathlib import Path
from typing import Dict

import pandas as pd

log = logging.getLogger(__name__.split('.')[-1])


def _parse_mapping_csv(filepath: Path) -> Dict[str, str]:
    """Parse city mapping CSV file into dictionary.

    Args:
        filepath: Path to city_mapping.csv

    Returns:
        Dictionary: {original_city: corrected_city}
    """
    try:
        df = pd.read_csv(filepath, sep=';', encoding='utf-8')
    except Exception as e:
        log.error(f"Failed to read mapping CSV: {e}")
        return {}

    required_columns = ['original_city', 'corrected_city']
    if not all(col in df.columns for col in required_columns):
        log.error(f"Missing required columns. Expected: {required_columns}, Found: {list(df.columns)}")
        return {}

    mapping = {}
    for _, row in df.iterrows():
        if pd.notna(row['corrected_city']) and row['corrected_city']:
            mapping[row['original_city']] = row['corrected_city']
        else:
            log.warning(f"Skipping row with empty corrected_city: original_city=\"{row['original_city']}\"")

    return mapping


def load_city_mapping(config: dict) -> Dict[str, str]:
    """Load city mapping configuration from CSV file.

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary of city mappings, empty dict if file missing or error
    """
    mapping_file = config.get('validation', {}).get('city_mapping_file')
    if not mapping_file:
        log.info("No city mapping file configured")
        return {}

    filepath = Path(mapping_file)
    if not filepath.exists():
        log.info(f"No city mapping file found at {filepath}, skipping corrections")
        return {}

    mapping = _parse_mapping_csv(filepath)
    if mapping:
        log.info(f"Loaded {len(mapping)} city mappings from {filepath}")
    return mapping


def apply_city_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> tuple[pd.DataFrame, dict]:
    """Apply city name corrections to DataFrame.

    Args:
        df: DataFrame with 'varos' column
        mapping: City mapping dictionary from load_city_mapping()

    Returns:
        Tuple of (corrected DataFrame, dict with 'corrected' and 'dropped' counts)
    """
    corrected_df = df.copy()
    corrected_count = 0
    dropped_count = 0

    if mapping:
        rows_to_drop = []
        for idx, row in corrected_df.iterrows():
            if row['varos'] in mapping:
                original = row['varos']
                corrected = mapping[original]
                
                if corrected == 'DROP':
                    log.debug(f"Marked for drop: \"{original}\"")
                    rows_to_drop.append(idx)
                    dropped_count += 1
                else:
                    log.debug(f"Applied: \"{original}\" → \"{corrected}\"")
                    corrected_df.at[idx, 'varos'] = corrected
                    corrected_count += 1
        
        if rows_to_drop:
            corrected_df = corrected_df.drop(rows_to_drop)
        
        log.info(f"Applied {corrected_count} city corrections, dropped {dropped_count} schools from excluded cities")

    return corrected_df, {'corrected': corrected_count, 'dropped': dropped_count}
