"""Fetch DLSS versions from the OG DLSS-Swapper site."""

import os
import sys
import zipfile
import argparse
from pathlib import Path

from utils import DLSS_FILENAME, find_file_in_directory, DLSS_BACKUP_FILENAME
from utils import parse_dlss_records, download_dlss_file, unzip_dlss_file_contents
from utils import get_dlss_versions_list_str, get_specific_dlss_version


parser = argparse.ArgumentParser(description="Download and swap DLSS dlls.")

parser.add_argument(
    "-g",
    "--game_path",
    help="The path to the game's directory.",
    type=str
)
parser.add_argument(
    "-v",
    "--version",
    help="Specify DLSS version to download.",
    type=str
)
parser.add_argument(
    "-lv",
    "--list_versions",
    help="List available dlss verisons and quit",
    action='store_true'
)
parser.add_argument(
    "-r",
    "--restore",
    help="Restore a backed up dlss dll file in the given game path.",
    action="store_true"
)
parser.add_argument(
    "-s",
    "--swap",
    help="Download DLSS dll and swap dll in the given game path."
         "Downloads the latest version by default.",
    action="store_true"
)


def swap_dlss(game_dir_path: str = None,
              download_version: str = None,
              should_list_versions: bool = False,
              should_swap: bool = False,
              should_restore: bool = False):
    json_data = parse_dlss_records()
    if json_data is None:
        sys.exit("Failed to parse DLSS records url.")

    # use stable versions - for now
    versions = json_data['stable']

    if should_list_versions:
        print(get_dlss_versions_list_str(versions))
        sys.exit()

    if should_restore:
        dlss_file_path = find_file_in_directory(game_dir_path, DLSS_BACKUP_FILENAME)
        if dlss_file_path is None:
            sys.exit("Could not find dlss backup file.")

        print("Restoring...", end=' ')
        with open(dlss_file_path, 'rb') as dlss_backup:
            dlss_backup_contents = dlss_backup.read()
            with open(Path(dlss_file_path.parent, DLSS_FILENAME), 'wb') as f:
                f.write(dlss_backup_contents)

        print("done.")
        sys.exit()

    selected_version = None
    if download_version:
        selected_version = get_specific_dlss_version(versions, download_version)
        if selected_version is None:
            # if not found, quit
            sys.exit(
                f"Could not find given DLSS version: {download_version}."
                "Use -lv to list versions."
            )

        version_str = selected_version["version"]
        print(f"Found {version_str} version")
    else:
        # otherwise, use the latest one
        selected_version = versions[-1]

    # build string with dlss version number
    dlss_file_name = Path(
        Path(selected_version["download_url"]).name.replace(".zip", ".dll")
    )

    # set the dlss file path
    dlss_file_path = dlss_file_name

    selected_version_str = selected_version["version"]
    print(f"Downloading {selected_version_str} version...")

    # download the dlss zip file
    dlss_file_contents = download_dlss_file(
        selected_version["download_url"],
        use_progress_bar=True
    )
    if dlss_file_contents is None:
        sys.exit("Failed to download DLSS file.")

    # unzip
    print("Unzipping...", end=' ')
    dlss_dll_bytes = None

    # try to unzip
    try:
        dlss_dll_bytes = unzip_dlss_file_contents(dlss_file_contents)
    except KeyError:
        sys.exit("Could not find nvngx_dlss.dll in zip.")
    except zipfile.BadZipFile:
        sys.exit("Downloaded file was not a zip.")

    # quit if unzipping still somehow failed
    if dlss_dll_bytes is None:
        sys.exit("Failed to unzip dlss file.")

    if should_swap:
        # locate dlss file in game folder
        dlss_file_path = find_file_in_directory(game_dir_path, DLSS_FILENAME)
        if dlss_file_path is None:
            sys.exit("dlss .dll file was not found at given game directory.")

        # TODO: check DLSS version of game - warn if replacing with older version
        # TODO: add flag to disable warnings

        # backup old dlss file
        with open(dlss_file_path, 'rb') as old_f:
            old_dlss_contents = old_f.read()

            backup_file_path = Path(dlss_file_path.parent, DLSS_BACKUP_FILENAME)
            with open(backup_file_path, 'wb') as new_f:
                new_f.write(old_dlss_contents)

    # write dlss dll contents
    with open(dlss_file_path, 'wb') as f:
        f.write(dlss_dll_bytes)

    print("done.")


if __name__ == '__main__':
    args = parser.parse_args()

    swap_dlss(
        args.game_path,
        args.version,
        args.list_versions,
        args.swap,
        args.restore
    )
