"""Shared publication settings for all offline formats and their checks."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION = json.loads((ROOT / "config/publication.json").read_text())
NAME = PUBLICATION["artifact_basename"]
