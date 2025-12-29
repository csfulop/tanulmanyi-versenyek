#!/usr/bin/env python3
"""Download helper data files (KIR database) for school matching."""

import logging

from tanulmanyi_versenyek.common.config import get_config
from tanulmanyi_versenyek.common.logger import setup_logging
from tanulmanyi_versenyek.kir_downloader.kir_scraper import download_latest_kir_data

log = logging.getLogger(__name__.split('.')[-1])


def main():
    setup_logging()
    log.info("Script starting: 03_download_helper_data.py")

    config = get_config()

    try:
        download_latest_kir_data(config)
        log.info("Script completed successfully")
    except Exception as e:
        log.error(f"Script failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
