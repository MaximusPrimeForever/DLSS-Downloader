"""Stuff."""

import os
import io
import sys
import json
import zipfile
from pathlib import Path
from typing import Union
import urllib.request as url_request

from prettytable import PrettyTable

from win32api import GetFileVersionInfo, LOWORD, HIWORD  # type: ignore


DLSS_RECORDS_URL = r"https://raw.githubusercontent.com/beeradmoore/dlss-archive/main/dlss_records.json"
DLSS_FILENAME = "nvngx_dlss.dll"
DLSS_BACKUP_FILENAME = DLSS_FILENAME + ".backup"


def get_dll_version_number(filename: Union[Path, str]) -> str:
    info = GetFileVersionInfo(str(filename), "\\")
    ms = info['FileVersionMS']
    ls = info['FileVersionLS']
    return f"{HIWORD(ms)}.{LOWORD(ms)}.{HIWORD(ls)}.{LOWORD(ls)}"


def find_file_in_directory(dir_path: Union[str, Path], file_name: str) -> Union[Path, None]:
    file_path = None

    for root, _, files in os.walk(dir_path):
        for file in files:
            if file == file_name:
                file_path = Path(root, file)

    return file_path


def parse_dlss_records():
    json_data = None
    with url_request.urlopen(DLSS_RECORDS_URL) as url:
        json_data = json.loads(url.read().decode())

    return json_data


def download_dlss_file(raw_url: str, use_progress_bar=False):
    data = None
    with url_request.urlopen(raw_url) as url:
        file_size = 1000000  # default
        chunk_size = 4096
        data = bytes()

        # find the file size
        for key, value in url.getheaders():
            if key == "Content-Length":
                file_size = int(value)
                break

        download_iterator = range(int(file_size / chunk_size))
        if use_progress_bar:
            from tqdm import tqdm
            download_iterator = tqdm(download_iterator)

        # download and display progress bar
        for _ in download_iterator:
            data += url.read(chunk_size)

        # finish remaining data
        data += url.read()

    return data


def extract_dlss_dll_from_zip(zip_bytes: bytes) -> Union[bytes, None]:
    """Receives bytes object of dlss zip file, and returns bytes of dll file.

    None if failed.
    """
    dlss_dll_bytes = None
    zip_filelike = io.BytesIO(zip_bytes)

    # try to unzip
    with zipfile.ZipFile(zip_filelike).open(DLSS_FILENAME) as dlss_zip:
        dlss_dll_bytes = dlss_zip.read()

    # quit if unzipping still somehow failed
    return dlss_dll_bytes


def get_dlss_versions_list_str(dlss_records: dict):
    table = PrettyTable(["Version", "MD5 Hash"])

    for dlss_version in dlss_records:
        current_version = dlss_version["version"]
        current_md5 = dlss_version["md5_hash"]
        table.add_row([current_version, current_md5])

    return str(table)


def get_specific_dlss_version(dlss_records: dict, version_or_hash: str):
    for dlss_version in dlss_records:
        if dlss_version["version"] == version_or_hash:
            return dlss_version
    
    for dlss_version in dlss_records:
        if dlss_version["md5_hash"] == version_or_hash:
            return dlss_version

    return None

def get_game_info(game_path: Path):
    """Return formatted string which describes the game and its DLSS version."""
    dlss_file_path = find_file_in_directory(
        game_path,
        DLSS_FILENAME
    )
    if dlss_file_path is None:
        sys.exit(f"DLSS .dll file was not found at {game_path}.")
    
    dlss_backup_file_path = find_file_in_directory(
        game_path,
        DLSS_BACKUP_FILENAME
    )
    backup_version_number = None
    if dlss_backup_file_path is not None:
        backup_version_number = get_dll_version_number(dlss_backup_file_path)

    version_number = get_dll_version_number(dlss_file_path)
    return game_path.name, version_number, backup_version_number
