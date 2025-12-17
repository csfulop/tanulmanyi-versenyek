import logging
from tanulmanyi_versenyek.common import config
from tanulmanyi_versenyek.common import logger

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
        # TODO: Add merger and reporter logic here
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
