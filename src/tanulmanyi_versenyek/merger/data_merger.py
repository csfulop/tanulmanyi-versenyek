import logging
import json
from pathlib import Path
import pandas as pd

def merge_processed_data(cfg):
    """
    Merge all processed CSV files into a single master CSV.
    Performs deduplication based on (ev, evfolyam, iskola_nev, helyezes).
    Handles Írásbeli/Szóbeli merge: when both rounds exist for same year+grade,
    drops top N rows from Írásbeli (where N = Szóbeli row count).

    Args:
        cfg: Configuration dictionary

    Returns:
        tuple: (pd.DataFrame, int) - The merged DataFrame and number of duplicates removed
    """
    processed_dir = Path(cfg['paths']['processed_csv_dir'])
    master_csv_path = Path(cfg['paths']['master_csv'])

    csv_files = list(processed_dir.glob('*.csv'))
    if not csv_files:
        logging.warning(f"No CSV files found in {processed_dir}")
        return pd.DataFrame(), 0

    logging.info(f"Found {len(csv_files)} CSV files to merge")

    file_data = {}
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
            filename = csv_file.stem
            parts = filename.split('_')
            year = parts[1]
            grade = parts[2]
            round_type = parts[3]
            key = (year, grade)

            if key not in file_data:
                file_data[key] = {}
            file_data[key][round_type] = df

            logging.debug(f"Loaded {csv_file.name}: {len(df)} rows")
        except Exception as e:
            logging.error(f"Failed to load {csv_file.name}: {e}")

    if not file_data:
        logging.error("No dataframes loaded successfully")
        return pd.DataFrame(), 0

    dataframes = []
    for key, rounds in file_data.items():
        year, grade = key
        if 'szobeli-donto' in rounds and 'irasbeli-donto' in rounds:
            szobeli_df = rounds['szobeli-donto']
            irasbeli_df = rounds['irasbeli-donto']
            szobeli_count = len(szobeli_df)

            irasbeli_filtered = irasbeli_df.iloc[szobeli_count:]
            dataframes.append(szobeli_df)
            dataframes.append(irasbeli_filtered)
            logging.debug(f"{year} {grade}: Szóbeli={len(szobeli_df)} rows, Írásbeli={len(irasbeli_df)} rows, dropped top {szobeli_count} from Írásbeli")
        else:
            for round_type, df in rounds.items():
                dataframes.append(df)
                logging.debug(f"{year} {grade} {round_type}: {len(df)} rows (no merge needed)")

    master_df = pd.concat(dataframes, ignore_index=True)
    logging.info(f"Concatenated all files: {len(master_df)} total rows")

    initial_count = len(master_df)
    master_df = master_df.drop_duplicates(subset=['ev', 'evfolyam', 'iskola_nev', 'helyezes'], keep='first')
    final_count = len(master_df)
    duplicates_removed = initial_count - final_count

    logging.info(f"Deduplication complete: removed {duplicates_removed} duplicates, {final_count} rows remaining")

    master_df.to_csv(master_csv_path, sep=';', encoding='utf-8', index=False)
    logging.info(f"Master CSV saved to {master_csv_path}")

    return master_df, duplicates_removed

def generate_validation_report(df, cfg, duplicates_removed=0):
    """
    Generate a validation report with data quality metrics.

    Args:
        df: Master DataFrame
        cfg: Configuration dictionary
        duplicates_removed: Number of duplicate rows removed during merge
    """
    report_path = Path(cfg['paths']['validation_report'])

    total_rows = len(df)
    null_counts = df.isnull().sum().to_dict()
    null_percentages = {col: (count / total_rows * 100) if total_rows > 0 else 0
                       for col, count in null_counts.items()}
    unique_schools = df['iskola_nev'].nunique() if 'iskola_nev' in df.columns else 0

    report = {
        'total_rows': total_rows,
        'duplicates_removed': duplicates_removed,
        'null_counts': null_counts,
        'null_percentages': null_percentages,
        'unique_schools': unique_schools
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logging.info(f"Validation report saved to {report_path}")
    logging.info(f"Total rows: {total_rows}, Unique schools: {unique_schools}, Duplicates removed: {duplicates_removed}")

def generate_excel_report(df, cfg):
    """
    Placeholder for Excel report generation.
    Will be implemented later.

    Args:
        df: Master DataFrame
        cfg: Configuration dictionary
    """
    logging.info("Excel generation skipped for now")
