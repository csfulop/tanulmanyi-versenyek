import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from tanulmanyi_versenyek.kir_downloader.kir_scraper import (
    get_latest_kir_url,
    download_kir_file,
    clear_helper_data_dir,
    download_latest_kir_data
)


class TestGetLatestKirUrl:
    @patch('tanulmanyi_versenyek.kir_downloader.kir_scraper.requests.get')
    def test_finds_single_matching_file(self, mock_get):
        html = '''
        <html>
            <a href="https://example.com/kir_mukodo_feladatellatasi_helyek_2024_12_15.xlsx">File</a>
            <a href="https://example.com/other_file.xlsx">Other</a>
        </html>
        '''
        mock_response = Mock()
        mock_response.content = html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        url = get_latest_kir_url(
            'https://kir.oktatas.hu/kirpub/index',
            'kir_mukodo_feladatellatasi_helyek_{date}.xlsx'
        )

        assert url == 'https://example.com/kir_mukodo_feladatellatasi_helyek_2024_12_15.xlsx'

    @patch('tanulmanyi_versenyek.kir_downloader.kir_scraper.requests.get')
    def test_no_matching_file_raises_error(self, mock_get):
        html = '<html><a href="/other_file.xlsx">Other</a></html>'
        mock_response = Mock()
        mock_response.content = html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="No KIR file matching pattern"):
            get_latest_kir_url(
                'https://kir.oktatas.hu/kirpub/index',
                'kir_mukodo_feladatellatasi_helyek_{date}.xlsx'
            )

    @patch('tanulmanyi_versenyek.kir_downloader.kir_scraper.requests.get')
    def test_multiple_matching_files_raises_error(self, mock_get):
        html = '''
        <html>
            <a href="https://example.com/kir_mukodo_feladatellatasi_helyek_2024_12_01.xlsx">Old</a>
            <a href="https://example.com/kir_mukodo_feladatellatasi_helyek_2024_12_15.xlsx">New</a>
        </html>
        '''
        mock_response = Mock()
        mock_response.content = html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Multiple KIR files found"):
            get_latest_kir_url(
                'https://kir.oktatas.hu/kirpub/index',
                'kir_mukodo_feladatellatasi_helyek_{date}.xlsx'
            )


class TestDownloadKirFile:
    @patch('tanulmanyi_versenyek.kir_downloader.kir_scraper.requests.get')
    def test_downloads_file(self, mock_get, tmp_path):
        mock_response = Mock()
        mock_response.iter_content = Mock(return_value=[b'test', b'data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        output_path = tmp_path / "test.xlsx"
        download_kir_file('https://example.com/file.xlsx', output_path)

        assert output_path.exists()
        assert output_path.read_bytes() == b'testdata'


class TestClearHelperDataDir:
    def test_removes_files(self, tmp_path):
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "file2.txt").write_text("test")
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        clear_helper_data_dir(tmp_path)

        assert not (tmp_path / "file1.txt").exists()
        assert not (tmp_path / "file2.txt").exists()
        assert subdir.exists()

    def test_handles_nonexistent_directory(self, tmp_path):
        nonexistent = tmp_path / "nonexistent"
        clear_helper_data_dir(nonexistent)


class TestDownloadLatestKirData:
    @patch('tanulmanyi_versenyek.kir_downloader.kir_scraper.requests.get')
    def test_downloads_kir_file_to_correct_location(self, mock_get, tmp_path):
        config = {
            'paths': {'helper_data_dir': str(tmp_path)},
            'kir': {
                'index_url': 'https://kir.oktatas.hu/kirpub/index',
                'locations_filename_pattern': 'kir_mukodo_feladatellatasi_helyek_{date}.xlsx',
                'locations_file': str(tmp_path / 'kir.xlsx')
            }
        }

        html = '<html><a href="https://example.com/kir_mukodo_feladatellatasi_helyek_2024_12_15.xlsx">File</a></html>'
        mock_index_response = Mock()
        mock_index_response.content = html.encode('utf-8')
        mock_index_response.raise_for_status = Mock()

        mock_file_response = Mock()
        mock_file_response.iter_content = Mock(return_value=[b'test', b'data'])
        mock_file_response.raise_for_status = Mock()

        mock_get.side_effect = [mock_index_response, mock_file_response]

        result = download_latest_kir_data(config)

        assert result == Path(tmp_path / 'kir.xlsx')
        assert result.exists()
        assert result.read_bytes() == b'testdata'
