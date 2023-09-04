# DLSS-Downloader
Python script to download and swap DLSS versions in games.  
Works only on Windows.

## Dependencies
* tqdm (progress bar during download)
* pywin32 (DLL version checks)
* prettytable (pretty printing of available DLSS versions)

install:
```python
pip install tqdm pywin32 prettytable
```

## Usage
### List available DLSS versions:
```powershell
❯ python dlss_mng.py -lv
+----------+----------------------------------+
| Version  |             MD5 Hash             |
+----------+----------------------------------+
| 1.0.0.0  | 65D2E2A86352D77244A73BEDD5837F50 |
| 1.0.9.0  | 667B23ED632FD0B9A5F2992ACE8C6B51 |
| 1.0.11.0 | 41878C22B109427192788DD4FCE796C1 |
|          |                                  |
|    ..    |    ..      ..      ..      ..    |
|          |                                  |
| 3.1.11.0 | ADB36F4684E64ADA9C8D82AD365E6D19 |
| 3.1.13.0 | 22B2359CF7EC76F523FEEEC53FA81464 |
| 3.1.30.0 | 96F5CED18C119946E4A674C14D908692 |
| 3.5.0.0  | A6B5079411A58630799478EBB6BAA722 |
| 3.5.0.0  | BF68025B3603C382FCA65B148B979682 |
+----------+----------------------------------+
```

### Download specific version:
Downloads a `nvngx_dlss.dll` file. 
```
❯ python .\dlss_mng.py -d 3.1.30.0
Found 3.1.30.0 version
Downloading DLSS...
Version: 3.1.30.0
MD5 Hash: 96F5CED18C119946E4A674C14D908692
100%|███████████████████████████████████████████████████████████████████| 8854/8854 [00:26<00:00, 338.26it/s]
Unzipping... Writing DLSS 3.1.30.0 to D:\Projects\Python\DLSS-Downloader

❯ ls
╭───┬────────────────┬──────┬─────────┬────────────────╮
│ # │      name      │ type │  size   │    modified    │
├───┼────────────────┼──────┼─────────┼────────────────┤
│ 0 │ .gitignore     │ file │  1.9 KB │ 2 years ago    │
│ 1 │ .vscode        │ dir  │     0 B │ a year ago     │
│ 2 │ LICENSE        │ file │ 35.8 KB │ 2 years ago    │
│ 3 │ README.md      │ file │  2.5 KB │ 2 days ago     │
│ 4 │ __pycache__    │ dir  │  4.1 KB │ 9 hours ago    │
│ 5 │ dlss_mng.py    │ file │  7.5 KB │ 8 hours ago    │
│ 6 │ nvngx_dlss.dll │ file │ 51.7 MB │ 37 seconds ago │
│ 7 │ utils.py       │ file │  3.9 KB │ 9 hours ago    │
╰───┴────────────────┴──────┴─────────┴────────────────╯
```

You can pass the MD5 hash instead of version string too.
```
python .\dlss_mng.py -d 96F5CED18C119946E4A674C14D908692
```

### Show information about a game's DLSS version
```
python .\dlss_mng.py -g "S:\\SteamLibrary\\steamapps\\common\\Metro Exodus Enhanced Edition" -i
Metro Exodus Enhanced Edition has a backup DLSS 2.1.24.0
Metro Exodus Enhanced Edition uses DLSS 3.5.0.0
```

### Swap dlss within a game directory
Downloads the latest version and swaps the existing dll within a game directory
(The game must use DLSS to begin with).  
This backs up the existing dlss .dll file (saved as `nvngx_dlss.dll.backup`).  

```
❯ python .\dlss_mng.py -g "S:\\SteamLibrary\\steamapps\\common\\Metro Exodus Enhanced Edition" -s 96F5CED18C119946E4A674C14D908692
Found 3.1.30.0 version
Downloading DLSS...
Version: 3.1.30.0
MD5 Hash: 96F5CED18C119946E4A674C14D908692
100%|███████████████████████████████████████████████████████████████████| 8854/8854 [00:26<00:00, 332.29it/s]
Unzipping... done.
Metro Exodus Enhanced Edition has DLSS 2.1.24.0 backed up.
Metro Exodus Enhanced Edition was using DLSS 3.5.0.0
Metro Exodus Enhanced Edition now uses DLSS 3.1.30.0
```

### Restore original DLSS version from backed up version
Restore original DLSS from back up (`nvngx_dlss.dll.backup`).  
Only works if a backup was created by the script earlier.
```
❯ python .\dlss_mng.py -g "S:\\SteamLibrary\\steamapps\\common\\Metro Exodus Enhanced Edition" -r
Restoring... done.
Metro Exodus Enhanced Edition has DLSS 2.1.24.0 backed up.
Metro Exodus Enhanced Edition was using DLSS 3.1.30.0
Metro Exodus Enhanced Edition now uses DLSS 2.1.24.0
```
