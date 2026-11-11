#!/usr/bin/env python3
"""Install pinned official ebook tools without depending on Ubuntu mirrors."""
import argparse
import hashlib
import io
from pathlib import Path
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / ".tools"
BIN = TOOLS / "bin"


def download(url, expected):
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit("SHA-256 mismatch for " + url)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pandoc-only", action="store_true")
    args = parser.parse_args()
    BIN.mkdir(parents=True, exist_ok=True)
    pandoc = download(
        "https://github.com/jgm/pandoc/releases/download/3.13/pandoc-3.13-linux-amd64.tar.gz",
        "38aa33b325a2bc96a4c39409631212db55702f564250bcdbead180b3bf646389",
    )
    with tarfile.open(fileobj=io.BytesIO(pandoc), mode="r:gz") as archive:
        binary = BIN / "pandoc"
        binary.write_bytes(archive.extractfile("pandoc-3.13/bin/pandoc").read())
        binary.chmod(0o755)
    if args.pandoc_only:
        print("Installed verified Pandoc 3.13 in .tools/bin/.")
        return
    epubcheck = download(
        "https://github.com/w3c/epubcheck/releases/download/v5.4.0/epubcheck-5.4.0.zip",
        "33350c61038e71dfb3d45a76aed04bf5481e6d5500cb780f6e98db8bbd15a28c",
    )
    with zipfile.ZipFile(io.BytesIO(epubcheck)) as archive:
        for member in archive.infolist():
            if not (TOOLS / member.filename).resolve().is_relative_to(TOOLS.resolve()):
                raise SystemExit("Invalid EPUBCheck archive path")
        archive.extractall(TOOLS)
    wrapper = BIN / "epubcheck"
    wrapper.write_text(
        '#!/usr/bin/env bash\nset -euo pipefail\n'
        'exec java -jar "$(dirname "$0")/../epubcheck-5.4.0/epubcheck.jar" "$@"\n'
    )
    wrapper.chmod(0o755)
    print("Installed verified Pandoc 3.13 and EPUBCheck 5.4.0 in .tools/bin/ (Java required).")


if __name__ == "__main__":
    main()
