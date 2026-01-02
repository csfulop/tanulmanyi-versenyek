"""School name matching against KIR database."""

import logging
import re
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
from rapidfuzz import fuzz

log = logging.getLogger(__name__.split('.')[-1])


def _normalize_case_if_uppercase(text: str) -> str:
    """Convert FULL UPPERCASE to normal case with exceptions."""
    if pd.isna(text):
        return text
    
    # Only transform if ENTIRE string is uppercase
    if text != text.upper():
        return text
    
    # Hardcoded lowercase words (common Hungarian conjunctions/articles)
    lowercase_words = {'és', 'a', 'az', 'de', 'vagy'}
    
    words = text.split()
    normalized = []
    
    for i, word in enumerate(words):
        # Check for Roman numeral with dot (e.g., "XII.")
        if re.match(r'^[IVX]+\.$', word):
            # Keep uppercase: "XII."
            normalized.append(word)
        # Check if word is lowercase exception
        elif word.lower() in lowercase_words:
            normalized.append(word.lower())
        else:
            normalized.append(word.title())
    
    return ' '.join(normalized)


def load_kir_database(config) -> pd.DataFrame:
    """Load and validate KIR facility locations Excel file."""
    filepath = Path(config['kir']['locations_file'])

    if not filepath.exists():
        raise FileNotFoundError(f"KIR database file not found: {filepath}")

    kir_df = pd.read_excel(filepath)

    required_columns = config['kir']['required_columns']
    missing_columns = [col for col in required_columns if col not in kir_df.columns]

    if missing_columns:
        raise ValueError(
            f"KIR database missing required columns.\n"
            f"Expected: {required_columns}\n"
            f"Missing: {missing_columns}\n"
            f"Found: {list(kir_df.columns)}"
        )

    # Normalize FULL UPPERCASE names
    kir_df['Intézmény megnevezése'] = kir_df['Intézmény megnevezése'].apply(_normalize_case_if_uppercase)
    if 'A feladatellátási hely megnevezése' in kir_df.columns:
        kir_df['A feladatellátási hely megnevezése'] = kir_df['A feladatellátási hely megnevezése'].apply(_normalize_case_if_uppercase)

    log.info(f"Loaded {len(kir_df)} schools from KIR database")
    return kir_df


def load_school_mapping(config) -> Dict[Tuple[str, str], dict]:
    """Load manual school mapping file."""
    filepath = Path(config['validation']['school_mapping_file'])

    if not filepath.exists():
        log.info(f"No school mapping file found at {filepath}")
        return {}

    try:
        mapping_df = pd.read_csv(filepath, sep=';', encoding='utf-8')
    except Exception as e:
        log.error(f"Failed to read school mapping file: {e}")
        return {}

    required_columns = ['school_name', 'city', 'corrected_school_name', 'comment']
    missing_columns = [col for col in required_columns if col not in mapping_df.columns]

    if missing_columns:
        log.error(f"School mapping file missing columns: {missing_columns}")
        return {}

    mapping = {}
    for _, row in mapping_df.iterrows():
        school_name = row['school_name']
        city = row['city']
        corrected_name = row['corrected_school_name']
        comment = row['comment']

        if pd.isna(corrected_name) or str(corrected_name).strip() == '':
            log.warning(f"Skipping mapping with empty corrected_school_name: {school_name}, {city}")
            continue

        key = (school_name, city)
        mapping[key] = {
            'corrected_school_name': corrected_name,
            'comment': comment
        }

    log.info(f"Loaded {len(mapping)} manual school mappings")
    return mapping


def normalize_city(city: str) -> str:
    """Normalize city name for comparison."""
    if pd.isna(city):
        return ""

    normalized = str(city).strip().lower()
    normalized = normalized.replace(" kerület", "").replace(" ker.", "")
    return normalized


def cities_match(our_city: str, kir_city: str) -> bool:
    """Check if two cities match (with Budapest special case)."""
    our_normalized = normalize_city(our_city)
    kir_normalized = normalize_city(kir_city)

    if our_normalized == kir_normalized:
        return True

    if our_normalized == "budapest" and kir_normalized.startswith("budapest"):
        return True

    return False


def _calculate_best_match_score(our_name: str, candidate: pd.Series) -> float:
    """Calculate best fuzzy match score across both name columns."""
    scores = []
    for column in ['Intézmény megnevezése', 'A feladatellátási hely megnevezése']:
        if pd.notna(candidate.get(column)):
            kir_name = candidate[column]
            score = fuzz.token_set_ratio(our_name, kir_name)
            scores.append(score)
    return max(scores) if scores else 0


def match_school(
    our_name: str,
    our_city: str,
    kir_df: pd.DataFrame,
    manual_mapping: Dict,
    config
) -> dict:
    """Find best match for a school in KIR database."""
    key = (our_name, our_city)
    if key in manual_mapping:
        manual_entry = manual_mapping[key]
        corrected_name = manual_entry['corrected_school_name']

        if corrected_name == 'DROP':
            return {
                'matched_school_name': None,
                'matched_city': None,
                'matched_county': None,
                'matched_region': None,
                'confidence_score': None,
                'match_method': 'MANUAL_DROP',
                'comment': manual_entry['comment']
            }

        kir_match = kir_df[kir_df['Intézmény megnevezése'] == corrected_name]
        if len(kir_match) == 0:
            log.warning(f"Manual mapping references non-existent KIR school: {corrected_name}")
            return {
                'matched_school_name': None,
                'matched_city': None,
                'matched_county': None,
                'matched_region': None,
                'confidence_score': None,
                'match_method': 'NO_MATCH',
                'comment': 'Manual mapping references non-existent KIR school'
            }

        kir_row = kir_match.iloc[0]
        return {
            'matched_school_name': kir_row['Intézmény megnevezése'],
            'matched_city': kir_row['A feladatellátási hely települése'],
            'matched_county': kir_row['A feladatellátási hely vármegyéje'],
            'matched_region': kir_row['A feladatellátási hely régiója'],
            'confidence_score': None,
            'match_method': 'MANUAL',
            'comment': manual_entry['comment']
        }

    candidates = []
    for _, kir_row in kir_df.iterrows():
        kir_city = kir_row['A feladatellátási hely települése']
        if cities_match(our_city, kir_city):
            candidates.append(kir_row)

    if not candidates:
        return {
            'matched_school_name': None,
            'matched_city': None,
            'matched_county': None,
            'matched_region': None,
            'confidence_score': None,
            'match_method': 'NO_MATCH',
            'comment': 'No schools found in this city in KIR database'
        }

    best_match = None
    best_score = 0

    for candidate in candidates:
        score = _calculate_best_match_score(our_name, candidate)
        if score > best_score:
            best_score = score
            best_match = candidate

    medium_threshold = config['matching']['medium_confidence_threshold']
    high_threshold = config['matching']['high_confidence_threshold']

    if best_score < medium_threshold:
        return {
            'matched_school_name': best_match['Intézmény megnevezése'],
            'matched_city': best_match['A feladatellátási hely települése'],
            'matched_county': best_match['A feladatellátási hely vármegyéje'],
            'matched_region': best_match['A feladatellátási hely régiója'],
            'confidence_score': best_score,
            'match_method': 'DROPPED',
            'comment': f'Low confidence (score < {medium_threshold}) - needs manual review'
        }

    match_method = 'AUTO_HIGH' if best_score >= high_threshold else 'AUTO_MEDIUM'

    return {
        'matched_school_name': best_match['Intézmény megnevezése'],
        'matched_city': best_match['A feladatellátási hely települése'],
        'matched_county': best_match['A feladatellátási hely vármegyéje'],
        'matched_region': best_match['A feladatellátási hely régiója'],
        'confidence_score': best_score,
        'match_method': match_method,
        'comment': ''
    }


def match_all_schools(
    our_df: pd.DataFrame,
    kir_df: pd.DataFrame,
    manual_mapping: Dict,
    config
) -> pd.DataFrame:
    """Match all unique schools in competition data to KIR."""
    unique_schools = our_df[['iskola_nev', 'varos']].drop_duplicates()

    results = []
    for _, row in unique_schools.iterrows():
        school_name = row['iskola_nev']
        city = row['varos']

        match_result = match_school(school_name, city, kir_df, manual_mapping, config)

        status = 'APPLIED' if match_result['match_method'] in ['MANUAL', 'AUTO_HIGH', 'AUTO_MEDIUM'] else 'NOT_APPLIED'

        results.append({
            'our_school_name': school_name,
            'our_city': city,
            'matched_school_name': match_result['matched_school_name'],
            'matched_city': match_result['matched_city'],
            'matched_county': match_result['matched_county'],
            'matched_region': match_result['matched_region'],
            'confidence_score': match_result['confidence_score'],
            'match_method': match_result['match_method'],
            'status': status,
            'comment': match_result['comment']
        })

    results_df = pd.DataFrame(results)

    manual_count = len(results_df[results_df['match_method'] == 'MANUAL'])
    manual_drop_count = len(results_df[results_df['match_method'] == 'MANUAL_DROP'])
    auto_high_count = len(results_df[results_df['match_method'] == 'AUTO_HIGH'])
    auto_medium_count = len(results_df[results_df['match_method'] == 'AUTO_MEDIUM'])
    dropped_count = len(results_df[results_df['match_method'] == 'DROPPED'])
    no_match_count = len(results_df[results_df['match_method'] == 'NO_MATCH'])

    log.info(
        f"Matched {len(results_df)} schools: "
        f"{manual_count} manual, {auto_high_count} high-conf, "
        f"{auto_medium_count} medium-conf, {dropped_count} dropped, "
        f"{no_match_count} no-match, {manual_drop_count} manual-drop"
    )

    return results_df


def apply_matches(our_df: pd.DataFrame, match_results: pd.DataFrame) -> pd.DataFrame:
    """Apply school matches to competition DataFrame."""
    result_df = our_df.copy()

    result_df['varmegye'] = None
    result_df['regio'] = None

    match_lookup = {}
    for _, row in match_results.iterrows():
        key = (row['our_school_name'], row['our_city'])
        match_lookup[key] = row

    rows_to_keep = []
    for idx, row in result_df.iterrows():
        key = (row['iskola_nev'], row['varos'])
        match = match_lookup.get(key)

        if match is None:
            log.error(f"School not found in match results: {key}")
            continue

        if match['status'] == 'APPLIED':
            result_df.at[idx, 'iskola_nev'] = match['matched_school_name']
            city = match['matched_city']
            city = city.replace(" kerület", "").replace(" ker.", "")
            result_df.at[idx, 'varos'] = city
            result_df.at[idx, 'varmegye'] = match['matched_county']
            result_df.at[idx, 'regio'] = match['matched_region']
            rows_to_keep.append(idx)

    result_df = result_df.loc[rows_to_keep]

    applied_count = len(match_results[match_results['status'] == 'APPLIED'])
    dropped_count = len(match_results[match_results['status'] == 'NOT_APPLIED'])

    log.info(f"Applied {applied_count} matches, dropped {dropped_count} schools")

    return result_df


def generate_audit_file(match_results: pd.DataFrame, output_path: Path) -> None:
    """Generate audit CSV file from match results."""
    audit_df = match_results.copy()
    audit_df = audit_df.sort_values(by=['match_method', 'our_school_name'])
    audit_df.to_csv(output_path, sep=';', encoding='utf-8', index=False)

    applied_count = len(audit_df[audit_df['status'] == 'APPLIED'])
    dropped_count = len(audit_df[audit_df['status'] == 'NOT_APPLIED'])

    log.info(f"Generated audit file: {len(audit_df)} schools, {applied_count} applied, {dropped_count} dropped")
