import logging
import logging.handlers
import os
from tanulmanyi_versenyek.common.config import get_config

def setup_logging():
    """
    Sets up logging for the application, configuring console and file handlers.
    The log format, file path, and log level are retrieved from the application's configuration.
    """
    config = get_config()
    log_config = config['logging']
    log_file_path = config['paths']['log_file']
    log_level = getattr(logging, log_config['log_level'].upper(), logging.INFO)

    # Ensure log directory exists
    log_dir = os.path.dirname(log_file_path)
    os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define formatter
    formatter = logging.Formatter(log_config['log_format'])

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (RotatingFileHandler for log rotation)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=log_config['max_bytes'],
        backupCount=log_config['backup_count'],
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("Logging setup complete.")

if __name__ == "__main__":
    # Example usage and basic test
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
