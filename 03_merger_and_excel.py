import logging
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
