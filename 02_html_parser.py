import logging
from tanulmanyi_versenyek.common import config
from tanulmanyi_versenyek.common import logger

def main():
    """
    Main function for the HTML parser script.
    Sets up logging and loads configuration.
    """
    logger.setup_logging()
    logging.info("Script starting: 02_html_parser.py")
    try:
        cfg = config.get_config()
        logging.info("Configuration loaded successfully.")
        # TODO: Add parser logic here
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
