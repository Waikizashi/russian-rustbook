#!/usr/bin/env bash
set -euo pipefail

# Fetch the official versioned binary and verify its pinned release SHA-256.
version=0.5.4
python3 - "$version" <<'PY'
import hashlib
import io
from pathlib import Path
import tarfile
import urllib.request
import sys

version = sys.argv[1]
url = f"https://github.com/rust-lang/mdBook/releases/download/v{version}/mdbook-v{version}-x86_64-unknown-linux-gnu.tar.gz"
with urllib.request.urlopen(url, timeout=60) as response:
    data = response.read()
expected = "3f28de05dafca9d0f2eab99c662116b0e37b89b1d96a08f8f430b9eeae958cd7"
if expected != hashlib.sha256(data).hexdigest():
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
