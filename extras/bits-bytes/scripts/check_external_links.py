#!/usr/bin/env python3
"""Check external documentation URLs separately from the deterministic CI."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def check(url):
    for attempt in range(2):
        try:
            request = urllib.request.Request(url, headers={"User-Agent":"rust-bits-bytes-ru link checker"})
            with urllib.request.urlopen(request, timeout=20) as response:
                response.read(1)
            return None
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt:
                return url, str(error)
            time.sleep(1)


def main():
    urls = set()
    for file in (ROOT / "docs").glob("[0-9][0-9]-*.md"):
        for url in re.findall(r"\]\((https?://[^\s)]+)\)", file.read_text()):
            # The repository itself is covered by local path checks.
            if "github.com/Waikizashi/" not in url:
                urls.add(urllib.parse.urldefrag(url)[0])
    errors = [result for result in ThreadPoolExecutor(6).map(check, sorted(urls)) if result]
    for url, error in errors:
        print(url, error)
    if errors:
        raise SystemExit(f"{len(errors)} external URLs failed; review transient failures before changing links.")
    print(f"Checked {len(urls)} external URLs (fragments are not validated).")


if __name__ == "__main__":
    main()
