import logging
import shutil
from pathlib import Path
from tanulmanyi_versenyek.common import config
from tanulmanyi_versenyek.common import logger
from tanulmanyi_versenyek.merger.data_merger import (
    merge_processed_data,
    generate_validation_report,
    generate_excel_report
)

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

        kaggle_template_dir = Path(cfg['paths']['kaggle_template_dir'])
        kaggle_output_dir = Path(cfg['paths']['kaggle_dir'])

        if kaggle_output_dir.exists():
            shutil.rmtree(kaggle_output_dir)
            logging.info(f"Cleaned up existing Kaggle directory: {kaggle_output_dir}")

        kaggle_output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created Kaggle directory: {kaggle_output_dir}")

        if kaggle_template_dir.exists():
            for item in kaggle_template_dir.iterdir():
                if item.is_file():
                    shutil.copy(item, kaggle_output_dir / item.name)
                    logging.info(f"Copied {item.name} to Kaggle directory")
        else:
            logging.warning(f"Kaggle template directory not found: {kaggle_template_dir}")

        master_df, duplicates_removed = merge_processed_data(cfg)
        if master_df.empty:
            logging.error("Master DataFrame is empty, cannot proceed")
            return

        generate_validation_report(master_df, cfg, duplicates_removed)
        generate_excel_report(master_df, cfg)

        logging.info("Script completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
