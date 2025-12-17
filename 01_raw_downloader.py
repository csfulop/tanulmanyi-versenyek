import logging
from tanulmanyi_versenyek.common import config
from tanulmanyi_versenyek.common import logger

def main():
    """
    Main function for the raw downloader script.
    Sets up logging and loads configuration.
    """
    logger.setup_logging()
    logging.info("Script starting: 01_raw_downloader.py")
    try:
        cfg = config.get_config()
        logging.info("Configuration loaded successfully.")
        # TODO: Add downloader logic here
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        # Potentially re-raise or handle specific exceptions

if __name__ == "__main__":
    main()
