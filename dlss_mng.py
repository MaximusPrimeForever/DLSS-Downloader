"""Fetch DLSS versions from the OG DLSS-Swapper site."""
import os
import sys
import zipfile
import argparse
from pathlib import Path

from utils import DLSS_FILENAME, find_file_in_directory, DLSS_BACKUP_FILENAME
from utils import parse_dlss_records, download_dlss_file, extract_dlss_dll_from_zip
from utils import get_dlss_versions_list_str, get_specific_dlss_version, get_game_info

DLSS_VERSION_LATEST="latest"


parser = argparse.ArgumentParser(description="Download and swap DLSS dlls.")
parser.add_argument(
    "-lv",
    "--list_versions",
    help="List available dlss verisons and quit",
    action='store_true'
)
parser.add_argument(
    "-g",
    "--game_path",
    help="The path to the game's directory.",
    type=str,
    default=""
)
parser.add_argument(
    "-d",
    "--download",
    help="Download a specific DLSS version to the working directory.",
    type=str,
)
parser.add_argument(
    "-s",
    "--swap",
    help="Download DLSS dll and swap dll in the given game path. "
         "A specific version can be downloaded. If not provided, the latest is downloaded.",
    type=str,
)
parser.add_argument(
    "-r",
    "--restore",
    help="Restore a backed up dlss dll file in the given game path.",
    action="store_true"
)
parser.add_argument(
    "-i",
    "--info",
    help="Print DLSS version of the game, and quit.",
    action="store_true"
)


def download_dlss(dlss_records, version_to_download=DLSS_VERSION_LATEST) -> tuple[dict, bytes]:
    """Download a DLSS version.

    Return tuple of metadata, and raw bytes of dll after unzipping.
    """
    selected_version = None
    if version_to_download == DLSS_VERSION_LATEST:
        selected_version = dlss_records[-1]
    else:
        selected_version = get_specific_dlss_version(dlss_records, version_to_download)
        if selected_version is None:
            # if not found, quit
            sys.exit(
                f"Could not find given DLSS version: {version_to_download}. "
                "Use -lv to list versions."
            )

        version_str = selected_version["version"]
        print(f"Found {version_str} version")

    selected_version_str = selected_version["version"]
    selected_version_additional_label = selected_version["additional_label"]
    selected_version_hash = selected_version["md5_hash"]
    print("Downloading DLSS...")
    print(f"Version: {selected_version_str} {selected_version_additional_label}")
    print(f"MD5 Hash: {selected_version_hash}")

    # download the dlss zip file
    dlss_zip_raw = download_dlss_file(
        selected_version["download_url"],
        use_progress_bar=True
    )
    if dlss_zip_raw is None:
        sys.exit("Failed to download DLSS file.")

    # unzip
    print("Unzipping...", end=' ')
    dlss_dll_bytes = None

    # try to unzip
    try:
        dlss_dll_bytes = extract_dlss_dll_from_zip(dlss_zip_raw)
    except KeyError:
        sys.exit("Could not find nvngx_dlss.dll in zip.")
    except zipfile.BadZipFile:
        sys.exit("Downloaded file was not a zip.")

    # quit if unzipping still somehow failed
    if dlss_dll_bytes is None:
        sys.exit("Failed to unzip dlss file.")

    return selected_version, dlss_dll_bytes


def print_summary(game_path: Path, previous_dlss_version: str):
    game_name, new_dlss_version, backup_dlss_version = get_game_info(game_path)
    print(f"{game_name} has DLSS {backup_dlss_version} backed up.")
    print(f"{game_name} was using DLSS {previous_dlss_version}")
    print(f"{game_name} now uses DLSS {new_dlss_version}")


def swap_dlss(should_list_versions: bool,
              game_dir_path: Path,
              download_version: str,
              swap_version: str,
              should_print_game_info: bool = False,
              should_restore: bool = False):
    """Main function to handle DLSS IO operations."""
    json_data = parse_dlss_records()
    if json_data is None:
        sys.exit("Failed to parse DLSS records url.")

    # use stable versions - for now
    dlss_records = json_data['stable']

    # list versions and exit
    if should_list_versions:
        print(get_dlss_versions_list_str(dlss_records))
        sys.exit()

    # determine which version to download
    should_download = False
    should_swap = False
    version_to_download = DLSS_VERSION_LATEST
    if download_version:
        version_to_download = download_version
        should_download = True
    if swap_version:
        version_to_download = swap_version
        should_swap = True

    if should_download:
        metadata, raw_data = download_dlss(dlss_records, version_to_download)
        cwd = os.getcwd()
        version = metadata["version"]

        print(f"Writing DLSS {version} to {cwd}")
        with open(Path(cwd, DLSS_FILENAME), 'wb') as f:
            f.write(raw_data)

        sys.exit(0)

    if not game_dir_path:
        print("Game path must be provided!")
        sys.exit()

    # get game's info
    game_dir_path = Path(game_dir_path)
    game_name, current_dlss_version, backup_dlss_version = get_game_info(game_dir_path)

    # print game's DLSS info and quit
    if should_print_game_info:
        if backup_dlss_version is not None:
            print(f"{game_name} has a backup DLSS {backup_dlss_version}")

        print(f"{game_name} uses DLSS {current_dlss_version}")
        sys.exit()

    # restore the game's original DLSS.dll
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
        print_summary(game_dir_path, current_dlss_version)
        sys.exit()

    if should_swap:
        metadata, raw_data = download_dlss(dlss_records, version_to_download)
        # locate dlss file in game folder
        dlss_file_path = find_file_in_directory(game_dir_path, DLSS_FILENAME)
        if dlss_file_path is None:
            sys.exit("dlss .dll file was not found at given game directory.")

        # backup old dlss file if there is no backup
        backup_file_path = Path(dlss_file_path.parent, DLSS_BACKUP_FILENAME)
        if not backup_file_path.exists():
            with open(dlss_file_path, 'rb') as old_f:
                old_dlss_contents = old_f.read()

                with open(backup_file_path, 'wb') as new_f:
                    new_f.write(old_dlss_contents)

        # write dlss dll contents
        with open(dlss_file_path, 'wb') as f:
            f.write(raw_data)

    print("done.")
    print_summary(game_dir_path, current_dlss_version)


if __name__ == '__main__':
    args = parser.parse_args()

    if args.list_versions and args.download == DLSS_VERSION_LATEST and args.swap == DLSS_VERSION_LATEST:
        print("Only one option should be used - either download or swap. Not both.")
        sys.exit(1)

    # manage game's dlss
    swap_dlss(
        should_list_versions=args.list_versions,
        game_dir_path=args.game_path,
        should_print_game_info=args.info,
        download_version=args.download,
        swap_version=args.swap,
        should_restore=args.restore
    )
