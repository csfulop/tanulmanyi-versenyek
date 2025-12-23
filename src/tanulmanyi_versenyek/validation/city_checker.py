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


def apply_city_mapping(df: pd.DataFrame, mapping: Dict[Tuple[str, str], dict], log: logging.Logger) -> Tuple[pd.DataFrame, int]:
    """Apply city name corrections to DataFrame.

    Args:
        df: DataFrame with 'iskola_nev' and 'varos' columns
        mapping: City mapping dictionary from load_city_mapping()
        log: Logger instance

    Returns:
        Tuple of (corrected DataFrame, number of corrections applied)
    """
    if not mapping:
        return df, 0

    corrected_df = df.copy()
    corrections_count = 0

    for idx, row in corrected_df.iterrows():
        key = (row['iskola_nev'], row['varos'])
        if key in mapping:
            entry = mapping[key]
            if not entry['is_valid'] and entry['corrected_city']:
                log.debug(f"Applied mapping: school=\"{row['iskola_nev']}\", \"{row['varos']}\" → \"{entry['corrected_city']}\"")
                corrected_df.at[idx, 'varos'] = entry['corrected_city']
                corrections_count += 1

    log.info(f"Applied {corrections_count} city corrections")
    return corrected_df, corrections_count


def _detect_variations(df: pd.DataFrame) -> Dict[str, dict]:
    """Detect schools with multiple city variations.

    Args:
        df: DataFrame with 'iskola_nev' and 'varos' columns

    Returns:
        Dictionary of schools with variations:
        {
            "School Name": {
                "cities": ["City1", "City2"],
                "count": 2
            }
        }
    """
    school_cities = df.groupby('iskola_nev')['varos'].apply(lambda x: sorted(x.unique())).to_dict()
    variations = {school: {'cities': cities, 'count': len(cities)}
                  for school, cities in school_cities.items()
                  if len(cities) > 1}
    return variations


def _build_allowed_combinations(mapping: Dict[Tuple[str, str], dict]) -> set:
    """Build set of allowed (school, city) combinations from mapping.

    Includes:
    - (school_name, original_city) marked as VALID
    - (school_name, corrected_city) from corrections

    Args:
        mapping: City mapping dictionary

    Returns:
        Set of allowed (school_name, city) tuples
    """
    allowed = set()
    for (school, original_city), entry in mapping.items():
        if entry['is_valid']:
            allowed.add((school, original_city))
        elif entry['corrected_city']:
            allowed.add((school, entry['corrected_city']))
    return allowed


def check_city_variations(df: pd.DataFrame, mapping: Dict[Tuple[str, str], dict], log: logging.Logger) -> dict:
    """Check for unmapped city variations and log warnings.

    Args:
        df: DataFrame with 'iskola_nev' and 'varos' columns (after corrections applied)
        mapping: City mapping dictionary from load_city_mapping()
        log: Logger instance

    Returns:
        Statistics dictionary with:
        {
            "total_schools_with_variations": int,
            "valid_combinations": int,
            "unmapped_combinations": int
        }
    """
    variations = _detect_variations(df)
    allowed_combinations = _build_allowed_combinations(mapping)

    valid_count = 0
    unmapped_count = 0

    for school, info in variations.items():
        log.debug(f"School \"{school}\" has {info['count']} city variations: {info['cities']}")

        for city in info['cities']:
            key = (school, city)
            if key in allowed_combinations:
                valid_count += 1
            else:
                log.warning(f"Unmapped combination: school=\"{school}\", city=\"{city}\"")
                unmapped_count += 1

    log.info(f"City variation check: {len(variations)} schools with variations, "
             f"{valid_count} valid, {unmapped_count} unmapped")

    return {
        'total_schools_with_variations': len(variations),
        'valid_combinations': valid_count,
        'unmapped_combinations': unmapped_count
    }
