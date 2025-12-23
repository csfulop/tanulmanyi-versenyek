"""City name validation and mapping functionality."""

import logging
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


def _is_valid_entry(comment: str) -> bool:
    """Check if mapping entry is marked as VALID (no correction needed)."""
    return "VALID" in comment.upper()


def _parse_mapping_csv(filepath: Path, log: logging.Logger) -> Dict[Tuple[str, str], dict]:
    """Parse city mapping CSV file into dictionary.

    Args:
        filepath: Path to city_mapping.csv
        log: Logger instance

    Returns:
        Dictionary keyed by (school_name, original_city) with values:
        {
            "corrected_city": str or "",
            "comment": str,
            "is_valid": bool
        }
    """
    try:
        df = pd.read_csv(filepath, sep=';', encoding='utf-8')
    except Exception as e:
        log.error(f"Failed to read mapping CSV: {e}")
        return {}

    required_columns = ['school_name', 'original_city', 'corrected_city', 'comment']
    if not all(col in df.columns for col in required_columns):
        log.error(f"Missing required columns. Expected: {required_columns}, Found: {list(df.columns)}")
        return {}

    mapping = {}
    for _, row in df.iterrows():
        key = (row['school_name'], row['original_city'])
        mapping[key] = {
            'corrected_city': row['corrected_city'] if pd.notna(row['corrected_city']) else '',
            'comment': row['comment'] if pd.notna(row['comment']) else '',
            'is_valid': _is_valid_entry(row['comment'] if pd.notna(row['comment']) else '')
        }

    return mapping


def load_city_mapping(config: dict, log: logging.Logger) -> Dict[Tuple[str, str], dict]:
    """Load city mapping configuration from CSV file.

    Args:
        config: Configuration dictionary
        log: Logger instance

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

    mapping = _parse_mapping_csv(filepath, log)
    if mapping:
        log.info(f"Loaded {len(mapping)} city mappings from {filepath}")
    return mapping
