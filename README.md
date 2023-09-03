# DLSS-Downloader
Python script to download and swap DLSS versions in games.

## Dependencies
* tqdm (progress bar during download)

install:
```python
pip install tqdm
```

## Usage
### List existing DLSS versions:
```powershell
❯ python dlss_mng.py -lv

Available DLSS versions:
        1.0.0.0 : 65D2E2A86352D77244A73BEDD5837F50 
        1.0.9.0 : 667B23ED632FD0B9A5F2992ACE8C6B51 
        1.0.11.0 : 41878C22B109427192788DD4FCE796C1
        1.0.13.0 : A8ED873E61FCB3A105D249824A0B0511
        
        ....

        2.3.1.0 : 0FC1727AD4A52C29E2897567008B3407
        2.3.2.0 : D62B6857F2F874E3892B30ABCE3DC603
        2.3.3.0 : 229DD563C5A7CFE67A927C06333249DA
        2.3.4.0 : 49B252E0F803A01C0CF6964ED4B16AD8
```

### Download specific version:
```powershell
❯ ls

❯ python dlss_mng.py -v 2.3.4.0
Found 2.3.4.0 version
Downloading 2.3.4.0 version...
100%|███████████████████████████████████████████████| 2403/2403 [00:03<00:00, 663.44it/s]
Unzipping... done.

❯ ls
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---          24/12/2021    22:45       14464712 nvngx_dlss_2.3.4.0.dll
```

### Swap dlss within a game directory
Downloads the latest version and swaps the existing dll within a game directory
(The game must use DLSS to begin with).  
This backs up the existing dlss .dll file (saved as `nvngx_dlss.dll.backup`).  
A DLSS version can be specified with the `-v` flag.

```powershell
❯ python dlss_mng.py -g "Path\to\game\directory"
Found 2.3.4.0 version
Downloading 2.3.4.0 version...
100%|███████████████████████████████████████████████| 2403/2403 [00:03<00:00, 663.44it/s]
Unzipping... done.

❯ python dlss_mng.py -g "Path\to\game\directory" -v 1.0.13.0
Found 1.0.13.0 version
Downloading 1.0.13.0 version...
100%|███████████████████████████████████████████████| 2403/2403 [00:03<00:00, 663.44it/s]
Unzipping... done.
```

### Restore original DLSS version from backed up version
Restore original DLSS from back up (`nvngx_dlss.dll.backup`).  
Only works if a backup was created by the script earlier.
```powershell
❯ python .\dlss_mng.py -g "Path\to\game\directory" -r 
Restoring... done.
```
