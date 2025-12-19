import logging
import json
from pathlib import Path
import pandas as pd
from tanulmanyi_versenyek.common import config
from tanulmanyi_versenyek.common import logger

def merge_processed_data(cfg):
    """
    Merge all processed CSV files into a single master CSV.
    Performs deduplication based on (ev, evfolyam, iskola_nev, helyezes).

    Args:
        cfg: Configuration dictionary

    Returns:
        pd.DataFrame: The merged and deduplicated master DataFrame
    """
    processed_dir = Path(cfg['paths']['processed_csv_dir'])
    master_csv_path = Path(cfg['paths']['master_csv'])

    csv_files = list(processed_dir.glob('*.csv'))
    if not csv_files:
        logging.warning(f"No CSV files found in {processed_dir}")
        return pd.DataFrame()

    logging.info(f"Found {len(csv_files)} CSV files to merge")

    dataframes = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
            dataframes.append(df)
            logging.debug(f"Loaded {csv_file.name}: {len(df)} rows")
        except Exception as e:
            logging.error(f"Failed to load {csv_file.name}: {e}")

    if not dataframes:
        logging.error("No dataframes loaded successfully")
        return pd.DataFrame()

    master_df = pd.concat(dataframes, ignore_index=True)
    logging.info(f"Concatenated {len(dataframes)} files: {len(master_df)} total rows")

    initial_count = len(master_df)
    master_df = master_df.drop_duplicates(subset=['ev', 'evfolyam', 'iskola_nev', 'helyezes'], keep='first')
    final_count = len(master_df)
    duplicates_removed = initial_count - final_count

    logging.info(f"Deduplication complete: removed {duplicates_removed} duplicates, {final_count} rows remaining")

    master_df.to_csv(master_csv_path, sep=';', encoding='utf-8', index=False)
    logging.info(f"Master CSV saved to {master_csv_path}")

    return master_df

def generate_validation_report(df, cfg):
    """
    Generate a validation report with data quality metrics.

    Args:
        df: Master DataFrame
        cfg: Configuration dictionary
    """
    report_path = Path(cfg['paths']['validation_report'])

    total_rows = len(df)
    null_counts = df.isnull().sum().to_dict()
    null_percentages = {col: (count / total_rows * 100) if total_rows > 0 else 0
                       for col, count in null_counts.items()}
    unique_schools = df['iskola_nev'].nunique() if 'iskola_nev' in df.columns else 0

    report = {
        'total_rows': total_rows,
        'null_counts': null_counts,
        'null_percentages': null_percentages,
        'unique_schools': unique_schools
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logging.info(f"Validation report saved to {report_path}")
    logging.info(f"Total rows: {total_rows}, Unique schools: {unique_schools}")

def generate_excel_report(df, cfg):
    """
    Placeholder for Excel report generation.
    Will be implemented later.

    Args:
        df: Master DataFrame
        cfg: Configuration dictionary
    """
    logging.info("Excel generation skipped for now")

def main():
    """
    Main function for the merger and Excel report generation script.
    Sets up logging and loads configuration.
    """
    logger.setup_logging()
    logging.info("Script starting: 03_merger_and_excel.py")
    try:
        cfg = config.get_config()
        logging.info("Configuration loaded successfully.")

        master_df = merge_processed_data(cfg)
        if master_df.empty:
            logging.error("Master DataFrame is empty, cannot proceed")
            return

        generate_validation_report(master_df, cfg)
        generate_excel_report(master_df, cfg)

        logging.info("Script completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
