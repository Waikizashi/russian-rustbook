#!/usr/bin/env python3
"""Build both books, add SEO, and fail before publishing on any check error."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(*args, cwd=ROOT):
    subprocess.run(args, cwd=cwd, check=True)


def main():
    mdbook = ROOT / ".tools/mdbook"
    if not mdbook.is_file():
        mdbook = shutil.which("mdbook")
    if not mdbook:
        raise SystemExit("Install mdBook: bash scripts/install_mdbook.sh")
    if subprocess.check_output([str(mdbook), "--version"], text=True).strip() != "mdbook v0.5.4":
        raise SystemExit("Expected mdBook 0.5.4")
    run(str(mdbook), "build")
    extra = ROOT / "extras/bits-bytes"
    run(sys.executable, "scripts/prepare_book.py", cwd=extra)
    run(str(mdbook), "build", "--dest-dir", str(ROOT / "book/extras/bits-bytes"), cwd=extra)
    run("node", str(ROOT / "scripts/search_index.cjs"))
    for script in ["site_seo.py", "check_site.py", "check_seo.py"]:
        run(sys.executable, str(ROOT / "scripts" / script))


if __name__ == "__main__":
    main()
