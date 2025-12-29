import logging
import re
from pathlib import Path
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger(__name__.split('.')[-1])


def get_latest_kir_url(index_url, pattern):
    log.info(f"Fetching KIR index page: {index_url}")
    response = requests.get(index_url, timeout=30, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    pattern_regex = pattern.replace('{date}', r'(\d{4}_\d{2}_\d{2})')
    matching_links = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        if re.search(pattern_regex, href):
            matching_links.append(href)

    if len(matching_links) == 0:
        raise ValueError(f"No KIR file matching pattern '{pattern}' found on index page")

    if len(matching_links) > 1:
        raise ValueError(f"Multiple KIR files found matching pattern '{pattern}': {matching_links}")

    log.info(f"Found KIR file: {matching_links[0]}")
    return matching_links[0]


def download_kir_file(url, output_path):
    log.info(f"Downloading KIR file from: {url}")
    response = requests.get(url, stream=True, timeout=60, verify=False)
    response.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    file_size = output_path.stat().st_size
    log.info(f"Downloaded {file_size:,} bytes to {output_path}")


def clear_helper_data_dir(dir_path):
    if not dir_path.exists():
        log.info(f"Directory does not exist: {dir_path}")
        return

    files = [f for f in dir_path.iterdir() if f.is_file()]
    for file in files:
        file.unlink()

    log.info(f"Removed {len(files)} file(s) from {dir_path}")


def download_latest_kir_data(config):
    helper_dir = Path(config['paths']['helper_data_dir'])
    clear_helper_data_dir(helper_dir)

    url = get_latest_kir_url(
        config['kir']['index_url'],
        config['kir']['locations_filename_pattern']
    )

    output_path = Path(config['kir']['locations_file'])
    download_kir_file(url, output_path)

    return output_path
