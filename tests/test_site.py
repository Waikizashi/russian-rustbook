"""Regression tests for the risks specific to project Pages and generated SEO."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_site import resolve_url
from check_seo import SEO, validate
from site_seo import normalize_headings

BASE = "https://waikizashi.github.io/russian-rustbook/"


class PagesTests(unittest.TestCase):
    def test_same_origin_absolute_assets_and_base_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            page = root / "extras/bits-bytes/01-bits.html"
            for url in ["../../css/main.css", "/russian-rustbook/css/main.css", BASE + "css/main.css"]:
                self.assertEqual(resolve_url(page, url, root, BASE), (root / "css/main.css", ""))
            with self.assertRaises(ValueError):
                resolve_url(page, "/css/main.css", root, BASE)
            with self.assertRaises(ValueError):
                resolve_url(page, "/russian-rustbook/%2e%2e/secret", root, BASE)

    def test_section_headings_preserve_anchors_and_code(self):
        html = '<h1 class="menu-title">Book</h1><main><h2 id="borrow">Borrowing</h2><h4 id="rules">Rules</h4><pre>&lt;h1&gt;example&lt;/h1&gt;</pre><h2 id="summary">Summary</h2></main>'
        result = normalize_headings(html)
        self.assertEqual(SEO(result).headings, [1, 2, 2])
        self.assertIn('id="borrow"', result)
        self.assertIn('&lt;h1&gt;example&lt;/h1&gt;', result)
        self.assertNotIn('<h1 class="menu-title">', result)

    def test_wrong_canonical_and_sitemap_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text('''<html lang="ru"><head>
<title>Rust на русском</title><meta name="description" content="Практическое руководство по языку Rust с примерами программ.">
<link rel="canonical" href="https://example.com/wrong.html">
</head><body><main><h1>Rust</h1></main></body></html>''')
            (root / "sitemap.xml").write_text('''<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/wrong.html</loc></url></urlset>''')
            (root / "robots.txt").write_text("Sitemap: " + BASE + "sitemap.xml\n")
            report = validate(root, {"base_url": BASE})
            self.assertTrue(any("canonical outside" in e for e in report["errors"]))
            self.assertTrue(any("sitemap" in e for e in report["errors"]))


if __name__ == "__main__":
    unittest.main()
