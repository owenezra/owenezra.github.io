import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PRESERVED_REPOSITORY_ASSETS = {"/docs/assets/images/LearningVoyageLogo.svg"}
PAGES = {
    "home": ROOT / "index.html",
    "autoqa": ROOT / "work" / "autoqa-foundation.html",
}
SOUPS = {
    name: BeautifulSoup(path.read_text(encoding="utf-8"), "lxml")
    for name, path in PAGES.items()
}


class SiteTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "index.html",
            "work/autoqa-foundation.html",
            "styles.css",
            "script.js",
            "robots.txt",
            "sitemap.xml",
            "site.webmanifest",
            "404.html",
            "assets/favicon.svg",
            "assets/og-image.png",
            "assets/autoqa-og.png",
        ]
        for item in required:
            self.assertTrue((ROOT / item).exists(), item)

    def test_single_h1_per_page(self):
        for name, soup in SOUPS.items():
            self.assertEqual(len(soup.find_all("h1")), 1, name)

    def test_landmarks(self):
        for name, soup in SOUPS.items():
            self.assertIsNotNone(soup.find("header"), name)
            self.assertIsNotNone(soup.find("main"), name)
            self.assertIsNotNone(soup.find("footer"), name)
            self.assertIsNotNone(soup.find("nav"), name)

    def test_unique_ids(self):
        for name, soup in SOUPS.items():
            ids = [tag.get("id") for tag in soup.find_all(attrs={"id": True})]
            self.assertEqual(len(ids), len(set(ids)), name)

    def test_internal_anchor_targets_exist(self):
        for name, soup in SOUPS.items():
            ids = {tag.get("id") for tag in soup.find_all(attrs={"id": True})}
            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]
                if href.startswith("#") and len(href) > 1:
                    self.assertIn(href[1:], ids, f"{name}: {href}")

    def test_images_have_alt(self):
        for name, soup in SOUPS.items():
            for image in soup.find_all("img"):
                self.assertTrue(image.has_attr("alt"), name)

    def test_external_blank_links_are_safe(self):
        for name, soup in SOUPS.items():
            for anchor in soup.find_all("a", target="_blank"):
                rel = set(anchor.get("rel", []))
                self.assertIn("noopener", rel, f"{name}: {anchor.get('href')}")
                self.assertIn("noreferrer", rel, f"{name}: {anchor.get('href')}")

    def test_metadata(self):
        expected_canonical = {
            "home": "https://learning.voyage/",
            "autoqa": "https://learning.voyage/work/autoqa-foundation.html",
        }
        for name, soup in SOUPS.items():
            self.assertTrue(soup.title and soup.title.string, name)
            description = soup.find("meta", attrs={"name": "description"})
            canonical = soup.find("link", attrs={"rel": "canonical"})
            viewport = soup.find("meta", attrs={"name": "viewport"})
            self.assertIsNotNone(description, name)
            self.assertLessEqual(len(description.get("content", "")), 165, name)
            self.assertEqual(canonical.get("href"), expected_canonical[name])
            self.assertIsNotNone(viewport, name)

    def test_json_ld_is_valid_json(self):
        for name, soup in SOUPS.items():
            scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
            self.assertEqual(len(scripts), 1, name)
            data = json.loads(scripts[0].string)
            self.assertEqual(data["@context"], "https://schema.org", name)

    def test_no_former_vendor_names(self):
        forbidden = ["Labelbox", "Alignerr", "Scale AI"]
        for name, soup in SOUPS.items():
            visible_text = soup.get_text(" ")
            for term in forbidden:
                self.assertNotIn(term, visible_text, f"{name}: {term}")

    def test_no_trusted_by_claim(self):
        for name, soup in SOUPS.items():
            self.assertNotRegex(soup.get_text(" ").lower(), r"trusted\s+by", name)

    def test_client_relationship_context_present(self):
        text = SOUPS["home"].get_text(" ")
        self.assertIn("external AI data partners", text)
        named = ("Anthropic" in text) or ("Amazon" in text)
        if named:
            # Named build: client names are only permitted together with an
            # explicit external-partner relationship disclaimer.
            self.assertIn(
                "do not imply employment, endorsement, or a direct commercial relationship",
                text,
            )
        else:
            # Client-unnamed build (default): generalized descriptions must be
            # identified as deliberately generalized.
            self.assertIn(
                "deliberately generalized to protect confidential client and partner information",
                text,
            )

    def test_autoqa_is_prominent_and_attributed(self):
        home = SOUPS["home"]
        case = SOUPS["autoqa"]
        self.assertIsNotNone(home.find(id="public-work"))
        self.assertGreaterEqual(home.get_text(" ").count("AutoQA Foundation"), 4)
        self.assertIn("Created by Owen Onderdonk", case.get_text(" "))
        self.assertIn("not a certification body", case.get_text(" "))

    def test_autoqa_external_link_present(self):
        for name, soup in SOUPS.items():
            links = {a.get("href") for a in soup.find_all("a", href=True)}
            self.assertIn("https://autoqa-foundation.vercel.app/", links, name)

    def test_local_assets_resolve(self):
        for name, soup in SOUPS.items():
            for tag, attr in [("link", "href"), ("script", "src")]:
                for node in soup.find_all(tag):
                    value = node.get(attr)
                    if not value or not value.startswith("/"):
                        continue
                    parsed = urlparse(value)
                    if parsed.path == "/":
                        continue
                    if parsed.path in PRESERVED_REPOSITORY_ASSETS:
                        continue
                    target = ROOT / parsed.path.lstrip("/")
                    self.assertTrue(target.exists(), f"{name}: {value}")

    def test_signature_visuals_present(self):
        home = SOUPS["home"]
        logo = home.find("img", class_="voyage-logo")
        self.assertIsNotNone(logo)
        self.assertEqual(logo.get("src"), "/docs/assets/images/LearningVoyageLogo.svg")
        constellations = home.find_all(attrs={"data-constellation": True})
        self.assertEqual(
            {node.get("data-constellation") for node in constellations},
            {"orion", "ursa", "aquarius"},
        )
        for node in constellations:
            self.assertGreater(len(node.select(".constellation-line")), 10)
            self.assertGreater(len(node.select(".star")), 10)

    def test_original_asset_preservation_is_documented(self):
        note = (ROOT / "PRESERVE-ORIGINAL-ASSETS.md").read_text(encoding="utf-8")
        contract = (ROOT / "VISUAL-PRESERVATION.md").read_text(encoding="utf-8")
        self.assertIn("LearningVoyageLogo.svg", note)
        self.assertIn("Do not delete", note)
        self.assertIn("Non-negotiable", contract)
        self.assertIn("Orion, Ursa Major, and Aquarius", contract)

    def test_sitemap_includes_case_study(self):
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("https://learning.voyage/", sitemap)
        self.assertIn("https://learning.voyage/work/autoqa-foundation.html", sitemap)


if __name__ == "__main__":
    unittest.main()
