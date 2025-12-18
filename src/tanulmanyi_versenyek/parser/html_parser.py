import logging
from pathlib import Path


class HtmlTableParser:
    """
    Parses HTML files containing Bolyai competition results into structured DataFrames.
    """

    def __init__(self, html_file_path: Path, config: dict, logger: logging.Logger):
        """
        Initialize the parser with a path to an HTML file.

        Args:
            html_file_path: Path to the HTML file to parse
            config: Configuration dictionary
            logger: Logger instance for logging
        """
        self.html_file_path = html_file_path
        self.config = config
        self.logger = logger
