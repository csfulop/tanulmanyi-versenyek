import logging
from pathlib import Path
from tanulmanyi_versenyek.common import config
from tanulmanyi_versenyek.common import logger
from tanulmanyi_versenyek.parser.html_parser import HtmlTableParser

log = logging.getLogger('02_html_parser')


def main():
    """
    Main function for the HTML parser script.
    Parses all HTML files from raw_html directory and saves as CSV files.
    """
    logger.setup_logging()
    log.info("Script starting: 02_html_parser.py")

    try:
        cfg = config.get_config()
        log.info("Configuration loaded successfully.")

        raw_html_dir = Path(cfg['paths']['raw_html_dir'])
        processed_csv_dir = Path(cfg['paths']['processed_csv_dir'])
        
        # Ensure output directory exists
        processed_csv_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Ensured processed CSV directory exists: {processed_csv_dir}")

        # Find all HTML files
        html_files = sorted(raw_html_dir.glob("*.html"))
        
        if not html_files:
            log.warning(f"No HTML files found in {raw_html_dir}")
            return

        log.info(f"Found {len(html_files)} HTML files to process")

        processed = 0
        skipped = 0
        failed = 0

        for html_file in html_files:
            # Determine output CSV filename (same name, different extension)
            csv_filename = html_file.stem + ".csv"
            csv_filepath = processed_csv_dir / csv_filename

            # Check for idempotency
            if csv_filepath.exists():
                log.info(f"Skipping existing CSV: {csv_filename}")
                skipped += 1
                continue

            try:
                log.info(f"Parsing: {html_file.name}")
                
                # Parse HTML file
                parser = HtmlTableParser(html_file, cfg)
                df = parser.parse()

                # Save to CSV with semicolon delimiter and UTF-8 encoding
                df.to_csv(csv_filepath, sep=';', index=False, encoding='utf-8')
                
                log.info(f"Saved: {csv_filename} ({len(df)} rows)")
                processed += 1

            except Exception as e:
                log.error(f"Failed to parse {html_file.name}: {e}", exc_info=True)
                failed += 1

        log.info(f"Parsing complete. Processed: {processed}, Skipped: {skipped}, Failed: {failed}")

    except Exception as e:
        log.error(f"An error occurred: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
