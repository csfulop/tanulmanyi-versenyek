import logging
from pathlib import Path
from tanulmanyi_versenyek.common import config
from tanulmanyi_versenyek.common import logger
from tanulmanyi_versenyek.scraper.bolyai_downloader import WebsiteDownloader

def slugify(text):
    """Convert text to a filename-safe slug."""
    return text.lower().replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ö", "o").replace("ő", "o").replace("ú", "u").replace("ü", "u").replace("ű", "u")

def main():
    """
    Main function for the raw downloader script.
    Downloads HTML files for all year/grade/round combinations.
    """
    logger.setup_logging()
    log = logging.getLogger(__name__)
    log.info("Script starting: 01_raw_downloader.py")

    try:
        cfg = config.get_config()
        log.info("Configuration loaded successfully.")

        raw_html_dir = Path(cfg['paths']['raw_html_dir'])
        raw_html_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Ensured raw HTML directory exists: {raw_html_dir}")

        subject = cfg['data_source']['subject']
        grades = cfg['data_source']['grades']
        rounds = cfg['data_source']['rounds']

        downloaded = 0
        skipped = 0
        unavailable = 0

        with WebsiteDownloader(cfg, log) as downloader:
            years = downloader.get_available_years()
            log.info(f"Found {len(years)} years to process: {years}")

            for year in years:
                for grade_value in grades:
                    for round_name in rounds:
                        round_slug = slugify(round_name)
                        grade_slug = slugify(grade_value)
                        filename = f"{slugify(subject)}_{year}_{grade_slug}_{round_slug}.html"
                        filepath = raw_html_dir / filename

                        if filepath.exists():
                            log.info(f"Skipping existing file: {filename}")
                            skipped += 1
                        else:
                            log.info(f"Downloading: {filename}")
                            html_content = downloader.get_html_for_combination(year, grade_value, round_name)
                            if html_content:
                                filepath.write_text(html_content, encoding='utf-8')
                                log.info(f"Saved: {filename}")
                                downloaded += 1
                            else:
                                log.warning(f"Combination not available: {filename}")
                                unavailable += 1

            log.info(f"Download complete. Downloaded: {downloaded}, Skipped: {skipped}, Unavailable: {unavailable}")

    except Exception as e:
        log.error(f"An error occurred: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
