"""Fetch DLSS versions from the OG DLSS-Swapper site."""

import os
import sys
import json
import argparse
import urllib.request as url_request

parser = argparse.ArgumentParser(description="Download and swap DLSS dlls.")

parser.add_argument(
    "-s",
    "--swap",
    help="Download DLSS dll and swap dll in the given path.",
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
    help="Restore given dll to original (backed up) file.",
    type=str
)

DLSS_RECORDS_URL = r"https://raw.githubusercontent.com/beeradmoore/dlss-archive/main/dlss_records.json"


def parse_dlss_records():
    json_data = None
    with url_request.urlopen(DLSS_RECORDS_URL) as url:
        json_data = json.loads(url.read().decode())

    return json_data


def download_dlss_file(raw_url: str):
    data = None
    with url_request.urlopen(raw_url) as url:
        data = url.read()

    return data


def swap_dlss(swap_path: str = None,
              download_version: str = None,
              should_list_versions: bool = False,
              should_restore: bool = False):
    json_data = parse_dlss_records()
    if json_data is None:
        sys.exit("Failed to parse DLSS records url.")

    # use stable versions - for now
    versions = json_data['stable']

    if should_list_versions:
        out = f"Available DLSS versions:{os.linesep}"
        for dlss_version in versions:
            current_version = dlss_version["version"]
            current_md5 = dlss_version["md5_hash"]
            out += f"\t{current_version} : {current_md5}{os.linesep}"

        print(out)
        sys.exit()

    selected_version = ""
    if download_version:
        # if a specific DLSS version was specified, look for it
        for dlss_version in versions:
            if dlss_version["version"] == download_version:
                selected_version = dlss_version
                break

        if not selected_version:
            # if not found, quit
            sys.exit(f"Could not find given DLSS version: {download_version}. Use -lv to list versions.")

        selected_version_str = selected_version["version"]
        print(f"Found {selected_version_str} version")
    else:
        # otherwise, use the latest one
        selected_version = versions[-1]

    # set the dlss file path
    dlss_file_path = "nvngx_dlss.zip"
    if swap_path and os.path.isfile(swap_path):
        dlss_file_path = swap_path
        # TODO: check if swap_path.name is nvngx_dlss.dll

    selected_version_str = selected_version["version"]
    print(f"Downloading {selected_version_str} version... ", end='')

    dlss_file_contents = download_dlss_file(selected_version["download_url"])
    if dlss_file_contents is None:
        sys.exit("Failed to download DLSS file.")

    print("done")
    # TODO: unzip

    with open(dlss_file_path, 'wb') as f:
        f.write(dlss_file_contents)


if __name__ == '__main__':
    args = parser.parse_args()

    swap_dlss(
        args.swap,
        args.version,
        args.list_versions,
        args.restore
    )
