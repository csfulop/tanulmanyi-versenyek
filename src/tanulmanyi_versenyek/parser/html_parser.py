import logging
import re
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

    def _parse_metadata_from_filename(self, filename: str) -> dict:
        """
        Extract metadata from the HTML filename.

        Filename format: {subject}_{year}_{grade_slug}_{round_slug}.html
        Example: anyanyelv_2022-23_8.-osztaly---altalanos-iskolai-kategoria_irasbeli-donto.html

        Args:
            filename: The filename to parse

        Returns:
            Dictionary with keys: year, grade, round
        """
        # Remove .html extension
        name_without_ext = filename.replace('.html', '')
        
        # Split by underscore
        parts = name_without_ext.split('_')
        
        if len(parts) < 4:
            raise ValueError(f"Invalid filename format: {filename}")
        
        # Extract year (second part)
        year = parts[1]
        
        # Extract grade slug (third part) and extract grade number
        grade_slug = parts[2]
        grade_match = re.match(r'(\d+)', grade_slug)
        if not grade_match:
            raise ValueError(f"Could not extract grade number from: {grade_slug}")
        grade = int(grade_match.group(1))
        
        # Extract round (fourth part onwards, joined back)
        round_slug = '_'.join(parts[3:])
        
        return {
            'year': year,
            'grade': grade,
            'round': round_slug
        }

