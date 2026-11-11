#!/usr/bin/env python3
"""Run example main functions: cargo test alone only compiles them."""
from pathlib import Path
import argparse
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()
    examples = json.loads((ROOT / "scripts/examples.json").read_text())
    for example in examples:
        command = ["cargo", "run", "--quiet", "--locked", "--example", example["name"]]
        if args.release:
            command.append("--release")
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=90)
        if completed.returncode:
            print(completed.stdout, end="")
            print(completed.stderr, end="")
            raise SystemExit(f"FAILED: {example['name']}")
        print("OK", example["name"])
    print(f"Executed {len(examples)} programs with assertions.")


if __name__ == "__main__":
    main()
