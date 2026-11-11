#!/usr/bin/env bash
set -euo pipefail

# Fetch an official versioned binary and verify GitHub's published SHA-256.
version=0.5.4
python3 - "$version" <<'PY'
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request
import sys

version = sys.argv[1]
base = "https://api.github.com/repos/rust-lang/mdBook/releases/tags/v" + version
with urllib.request.urlopen(base, timeout=30) as response:
    release = json.load(response)
asset = next(a for a in release["assets"] if a["name"].endswith("x86_64-unknown-linux-gnu.tar.gz"))
with urllib.request.urlopen(asset["browser_download_url"], timeout=60) as response:
    data = response.read()
expected = asset.get("digest")
if not expected or expected != "sha256:" + hashlib.sha256(data).hexdigest():
    raise SystemExit("Missing or mismatched SHA-256 for the official mdBook asset")
destination = Path(".tools")
destination.mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
    member = archive.getmember("mdbook")
    if not member.isfile():
        raise SystemExit("Expected the official mdbook executable")
    binary = destination / "mdbook"
    binary.write_bytes(archive.extractfile(member).read())
    binary.chmod(0o755)
print("Installed mdBook", version, "in .tools/")
PY
