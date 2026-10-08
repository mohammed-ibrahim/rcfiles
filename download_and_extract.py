import os
import shutil
import zipfile
from datetime import datetime
from urllib.parse import urlparse, unquote
from urllib.request import urlopen, Request
import ssl


def download_and_extract(url, temp_dir):
    """
    Download a .zip from `url` into a timestamped sub-directory of `temp_dir`
    (named like 08-OCT-2026-11-35), extract the zip, then extract every .jar
    found inside it.

    Returns the path of the created sub-directory.
    """
    # 1. Create sub-directory named DD-MMM-YYYY-HH-MM (e.g. 08-OCT-2026-11-35)
    sub_dir_name = datetime.now().strftime("%d-%b-%Y-%H-%M").upper()
    sub_dir = os.path.join(temp_dir, sub_dir_name)
    os.makedirs(sub_dir, exist_ok=True)

    # 2. Download the zip file
    file_name = os.path.basename(unquote(urlparse(url).path)) or "download.zip"
    if not file_name.lower().endswith(".zip"):
        file_name += ".zip"
    zip_path = os.path.join(sub_dir, file_name)

    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ssl_ctx = ssl._create_unverified_context()
    with urlopen(request, context=ssl_ctx) as response, open(zip_path, "wb") as out_file:
        shutil.copyfileobj(response, out_file)
    print(f"Downloaded: {zip_path}")

    # 3. Extract the zip into the sub-directory
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(sub_dir)
    print(f"Extracted zip to: {sub_dir}")

    # 4. Find every .jar (including in nested folders) and unzip each one
    #    into a folder named after the jar (without extension)
    for root, _, files in os.walk(sub_dir):
        for name in files:
            if name.lower().endswith(".jar"):
                jar_path = os.path.join(root, name)
                jar_out_dir = os.path.join(root, os.path.splitext(name)[0])
                os.makedirs(jar_out_dir, exist_ok=True)
                with zipfile.ZipFile(jar_path, "r") as jf:
                    jf.extractall(jar_out_dir)
                print(f"Extracted jar: {jar_path} -> {jar_out_dir}")

    return sub_dir


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python3 download_and_extract.py <url> <temp_dir>")
        sys.exit(1)

    download_and_extract(sys.argv[1], sys.argv[2])