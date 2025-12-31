import logging
import re
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup

log = logging.getLogger(__name__.split('.')[-1])


class HtmlTableParser:
    """
    Parses HTML files containing Bolyai competition results into structured DataFrames.
    """

    def __init__(self, html_file_path: Path, config: dict):
        """
        Initialize the parser with a path to an HTML file.

        Args:
            html_file_path: Path to the HTML file to parse
            config: Configuration dictionary
        """
        self.html_file_path = html_file_path
        self.config = config

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

    def parse(self) -> pd.DataFrame:
        """
        Parse the HTML file and return a clean DataFrame.

        Returns:
            DataFrame with parsed competition results
        """
        log.info(f"Parsing HTML file: {self.html_file_path.name}")
        
        # Extract metadata from filename
        metadata = self._parse_metadata_from_filename(self.html_file_path.name)
        
        # Read HTML with BeautifulSoup to preserve br tags
        with open(self.html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Find the results table
        table = soup.find('tbody', id='teams')
        if not table:
            raise ValueError(f"No results table found in {self.html_file_path}")
        
        # Parse table rows
        rows = []
        for tr in table.find_all('tr'):
            cells = tr.find_all('td')
            if len(cells) >= 4:
                # Extract helyezes (rank)
                helyezes_cell = cells[0]
                helyezes_text = helyezes_cell.get_text(strip=True)
                
                # Extract csapatnev (team name)
                csapatnev = cells[1].get_text(strip=True)
                
                # Extract iskola with br handling
                iskola_cell = cells[2]
                # Replace br with newline
                for br in iskola_cell.find_all('br'):
                    br.replace_with('\n')
                iskola_text = iskola_cell.get_text()
                
                # Extract pontszam (score)
                pontszam = cells[3].get_text(strip=True)
                
                rows.append({
                    'Helyezés': helyezes_text,
                    'Csapatnév': csapatnev,
                    'Iskola': iskola_text,
                    'Pontszám': pontszam
                })
        
        df = pd.DataFrame(rows)
        
        log.info(f"Extracted table with shape: {df.shape}")
        
        # Clean and transform data
        df = self._clean_data(df, metadata)
        
        return df

    def _clean_data(self, df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Clean and transform the raw DataFrame.

        Args:
            df: Raw DataFrame from HTML
            metadata: Metadata extracted from filename

        Returns:
            Cleaned DataFrame with target schema
        """
        # Normalize helyezes column - extract first number
        df['helyezes'] = df['Helyezés'].apply(self._normalize_helyezes)
        
        # Split Iskola column into school name and city
        df[['iskola_nev', 'varos']] = df['Iskola'].apply(self._split_school_and_city)
        
        # Add metadata columns
        df['ev'] = metadata['year']
        df['evfolyam'] = metadata['grade']
        df['targy'] = self.config['data_source']['subject']
        
        # Add geographic columns (will be populated by school matching)
        df['varmegye'] = ''
        df['regio'] = ''
        
        # Select and order columns according to target schema
        result_df = df[['ev', 'targy', 'iskola_nev', 'varos', 'varmegye', 'regio', 'helyezes', 'evfolyam']].copy()
        
        # Clean string columns
        result_df['iskola_nev'] = result_df['iskola_nev'].str.strip()
        result_df['varos'] = result_df['varos'].str.strip()
        
        log.info(f"Cleaned data: {len(result_df)} rows")
        
        return result_df

    def _normalize_helyezes(self, helyezes_str: str) -> int:
        """
        Normalize helyezes (rank) string to integer.
        Examples: "1. döntős" -> 1, "7." -> 7, "15." -> 15

        Args:
            helyezes_str: Raw helyezes string

        Returns:
            Normalized rank as integer
        """
        # Extract first number from string
        match = re.match(r'(\d+)', str(helyezes_str))
        if match:
            return int(match.group(1))
        raise ValueError(f"Could not extract rank from: {helyezes_str}")

    def _split_school_and_city(self, iskola_str: str) -> pd.Series:
        """
        Split school string into school name and city.
        Format: "School Name\nCity" where they are separated by newline (from <br> tag).

        Args:
            iskola_str: Combined school and city string with newline separator

        Returns:
            Series with school name and city

        Raises:
            ValueError: If no newline separator is found
        """
        # Split by newline (which replaced <br> tags)
        parts = str(iskola_str).split('\n', 1)
        
        if len(parts) == 2:
            school_name = parts[0]
            city = parts[1]
        else:
            raise ValueError(f"No newline separator found in school/city string: {iskola_str}")
        
        return pd.Series([school_name, city])

