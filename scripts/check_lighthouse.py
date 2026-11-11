#!/usr/bin/env python3
"""Record Lighthouse evidence and enforce basic SEO/accessibility regressions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "dist/lighthouse-mobile.report.json").read_text())
if report.get("runtimeError"):
    raise SystemExit(report["runtimeError"])
scores = {key: round(value["score"] * 100) for key, value in report["categories"].items()}
result = {"lighthouse": report["lighthouseVersion"], "url": report["finalDisplayedUrl"], "scores": scores,
          "metrics": {k: report["audits"][k].get("displayValue") for k in ["first-contentful-paint", "largest-contentful-paint", "cumulative-layout-shift", "total-blocking-time"]}}
(ROOT / "dist/lighthouse-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False))
# Speed scores fluctuate with shared CI hosts; retain measurements, don't gate
# publication on noisy timing. Concrete resource failures are browser-tested.
if scores["seo"] < 90 or scores["accessibility"] < 90:
    raise SystemExit("Lighthouse SEO/accessibility below 90")
