import json
import re
import subprocess
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "home": ROOT / "index.html",
    "autoqa": ROOT / "work" / "autoqa-foundation.html",
}
SOUPS = {
    name: BeautifulSoup(path.read_text(encoding="utf-8"), "lxml")
    for name, path in PAGES.items()
}
RAW = {name: path.read_text(encoding="utf-8") for name, path in PAGES.items()}
CONFIG = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
CLIENT_MODE = CONFIG["clientNames"]


class SiteTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "index.html",
            "work/autoqa-foundation.html",
            "styles.css",
            "robots.txt",
            "sitemap.xml",
            "site.webmanifest",
            "404.html",
            "CNAME",
            "llms.txt",
            "site.config.json",
            "tools/apply_client_copy.py",
            "tests/fixtures/constellation_golden.json",
            "docs/assets/images/LearningVoyageLogo.svg",
            "docs/assets/images/favicon-32.png",
            "docs/assets/images/favicon-192.png",
            "docs/assets/images/apple-touch-icon.png",
        ]
        for item in required:
            self.assertTrue((ROOT / item).exists(), item)

    def test_single_h1_per_page(self):
        for name, soup in SOUPS.items():
            self.assertEqual(len(soup.find_all("h1")), 1, name)

    def test_landmarks(self):
        for name, soup in SOUPS.items():
            self.assertIsNotNone(soup.find("nav"), name)
            self.assertIsNotNone(soup.find("main"), name)
            self.assertIsNotNone(soup.find("footer"), name)

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
        expected_type = {"home": "ProfessionalService", "autoqa": "TechArticle"}
        for name, soup in SOUPS.items():
            scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
            self.assertEqual(len(scripts), 1, name)
            data = json.loads(scripts[0].string)
            self.assertEqual(data["@context"], "https://schema.org", name)
            self.assertEqual(data["@type"], expected_type[name], name)

    def test_no_former_vendor_names_anywhere(self):
        forbidden = ["Labelbox", "Alignerr", "Scale AI", "Outlier"]
        for name, raw in RAW.items():
            for term in forbidden:
                self.assertNotIn(term, raw, f"{name}: {term}")

    def test_no_trusted_by_language(self):
        for name, soup in SOUPS.items():
            self.assertNotRegex(soup.get_text(" ").lower(), r"trusted\s+by", name)

    def test_no_consulting_funnel_language(self):
        home_text = SOUPS["home"].get_text(" ")
        for term in ["AI Strategy", "Explore Services", "Book a consultation", "Assess", "Implement", "Train"]:
            self.assertNotIn(term, home_text, term)

    def test_client_copy_matches_config(self):
        result = subprocess.run(
            ["python3", "tools/apply_client_copy.py", "--check"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_client_language_guardrails(self):
        home_text = SOUPS["home"].get_text(" ")
        self.assertIn("external AI data partner", home_text)
        if CLIENT_MODE == "unnamed":
            for raw_name, raw in RAW.items():
                self.assertNotIn("Anthropic", raw, raw_name)
                self.assertNotIn("Amazon", raw, raw_name)
            self.assertIn("frontier AI and technology organizations", home_text)
            self.assertIn("a frontier AI lab", home_text)
            self.assertIn("deliberately generalized", home_text)
        else:
            self.assertIn("Anthropic", home_text)
            self.assertIn("Amazon", home_text)
            self.assertIn("do not imply employment, endorsement, or a direct commercial relationship", home_text)

    def test_no_vendor_logo_assets_or_references(self):
        for logo in ["LabelboxLogo.svg", "ScaleLogo.svg", "AlignerrLogo.svg"]:
            self.assertFalse((ROOT / "docs/assets/images" / logo).exists(), logo)
            for name, raw in RAW.items():
                self.assertNotIn(logo, raw, f"{name}: {logo}")

    def test_signature_visuals_preserved_from_live_site(self):
        home = SOUPS["home"]
        # Original emblem, loaded from the preserved repository asset
        logo = home.find("img", class_="hero-logo")
        self.assertIsNotNone(logo)
        self.assertEqual(logo.get("src"), "/docs/assets/images/LearningVoyageLogo.svg")
        # Original hero structure
        for cls in ["logo-with-text", "logo-glow", "logo-wrapper"]:
            self.assertIsNotNone(home.find(class_=cls), cls)
        # Curved wordmark on the original bottom-curve path
        text_path = home.find(lambda tag: tag.name and tag.name.lower() == "textpath")
        self.assertIsNotNone(text_path)
        self.assertEqual(text_path.get("href"), "#bottom-curve")
        letters = "".join(t.get_text() for t in text_path.find_all("tspan")).replace("\xa0", "")
        self.assertIn("LEARNING", letters)
        self.assertIn("VOYAGE", letters)
        # Ambient starfield
        self.assertIsNotNone(home.find("div", id="starfield"))
        # All three constellation transitions
        constellations = home.find_all(attrs={"data-constellation": True})
        self.assertEqual(
            {node.get("data-constellation") for node in constellations},
            {"orion", "ursa", "aquarius"},
        )

    def test_animation_system_preserved(self):
        raw = RAW["home"]
        self.assertIn("gsap@3/dist/gsap.min.js", raw)
        self.assertIn("gsap@3/dist/ScrollTrigger.min.js", raw)
        self.assertIn("GSAP CDN unavailable", raw)  # static fallback path retained
        self.assertIn("createStarfield()", raw)
        route = SOUPS["home"].find("svg", class_="route")
        self.assertIsNotNone(route)
        self.assertEqual(len(route.find_all("circle", class_="route-waypoint")), 3)

    def test_constellation_geometry_matches_original(self):
        golden = json.loads((ROOT / "tests/fixtures/constellation_golden.json").read_text(encoding="utf-8"))["groups"]
        html = RAW["home"]
        for gid, expected in golden.items():
            start = html.find('id="%s"' % gid)
            self.assertGreater(start, -1, gid)
            seg = html[start:start + 9000]
            lines = [list(m) for m in re.findall(r'<line[^>]*x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', seg)]
            stars = [list(m) for m in re.findall(r'<circle class="star"[^>]*cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" fill="([^"]+)"', seg)]
            nebulas = [list(m) for m in re.findall(r'<circle class="nebula"[^>]*cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"', seg)]
            labels = [list(m) for m in re.findall(r'<text class="star-label[^"]*" x="([\d.]+)" y="([\d.]+)" data-label="([^"]+)"', seg)]
            self.assertEqual(expected["lines"], lines, f"{gid} lines differ from original")
            self.assertEqual(expected["stars"], stars, f"{gid} stars differ from original")
            self.assertEqual(expected["nebulas"], nebulas, f"{gid} nebulas differ from original")
            self.assertEqual(expected["labels"], labels, f"{gid} labels differ from original")

    def test_reduced_motion_static_completion_css(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        block = css[css.find("@media (prefers-reduced-motion: reduce)"):]
        self.assertIn("scale(1) !important", block)
        self.assertIn("stroke-dashoffset: 0 !important", block)
        self.assertIn(".star-label tspan", block)

    def test_autoqa_is_prominent_and_attributed(self):
        home = SOUPS["home"]
        case_text = SOUPS["autoqa"].get_text(" ")
        self.assertIsNotNone(home.find(id="public-work"))
        self.assertGreaterEqual(home.get_text(" ").count("AutoQA Foundation"), 3)
        self.assertIn("Created by Owen Onderdonk", case_text)
        self.assertIn("not a certification body", case_text)

    def test_autoqa_external_link_present(self):
        for name, soup in SOUPS.items():
            links = {a.get("href") for a in soup.find_all("a", href=True)}
            self.assertIn("https://autoqa-foundation.vercel.app/", links, name)

    def test_established_direction_development_labels(self):
        home_text = SOUPS["home"].get_text(" ")
        self.assertIn("Established", home_text)
        self.assertIn("Current direction", home_text)
        self.assertIn("In development", home_text)

    def test_ops_files(self):
        self.assertEqual((ROOT / "CNAME").read_text(encoding="utf-8").strip(), "learning.voyage")
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("https://learning.voyage/sitemap.xml", robots)
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("https://learning.voyage/", sitemap)
        self.assertIn("https://learning.voyage/work/autoqa-foundation.html", sitemap)
        llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
        self.assertIn("Owen", llms)
        self.assertIn("AutoQA Foundation", llms)
        json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))

    def test_og_image_dimensions(self):
        from PIL import Image
        with Image.open(ROOT / "docs/assets/images/og-image.png") as handle:
            self.assertEqual(handle.size, (1200, 630))


if __name__ == "__main__":
    unittest.main()
