#!/usr/bin/env python3
"""Repository-local browser smoke test.

Serves the actual repository over a local HTTP server so the production asset
paths resolve exactly as they will on GitHub Pages — including the original
emblem at /docs/assets/images/LearningVoyageLogo.svg — then checks rendering,
animation, navigation, reduced-motion, and responsive behavior in Chromium.

Usage:
    python3 tests/browser_smoke.py
"""

import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    raise SystemExit("Install Playwright first: pip install playwright (uses system Chrome or bundled Chromium)") from exc

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "tests" / "results"
VIEWPORTS = [
    ("desktop-1440", {"width": 1440, "height": 1000}),
    ("laptop-1024", {"width": 1024, "height": 800}),
    ("tablet-768", {"width": 768, "height": 900}),
    ("mobile-390", {"width": 390, "height": 844}),
]
SYSTEM_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *args):
        pass


def serve():
    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, server.server_address[1]


def launch(browser_type):
    try:
        return browser_type.launch(channel="chrome", headless=True)
    except Exception:
        if Path(SYSTEM_CHROME).exists():
            return browser_type.launch(executable_path=SYSTEM_CHROME, headless=True, args=["--no-sandbox"])
        return browser_type.launch(headless=True)


def main():
    server, port = serve()
    base = f"http://127.0.0.1:{port}"
    results = {}
    try:
        with sync_playwright() as p:
            browser = launch(p.chromium)
            for label, viewport in VIEWPORTS:
                page = browser.new_page(viewport=viewport)
                console_errors, bad_responses = [], []
                page.on("console", lambda msg, e=console_errors: e.append(msg.text) if msg.type == "error" else None)
                page.on("response", lambda res, b=bad_responses: b.append(f"{res.status} {res.url}") if res.status >= 400 else None)
                page.goto(base + "/", wait_until="networkidle")
                page.wait_for_timeout(300)

                constellation_checks = {}
                for name in ("orion", "ursa", "aquarius"):
                    sel = f'[data-constellation="{name}"] .constellation-line'
                    before = page.locator(sel).first.evaluate("e => getComputedStyle(e).strokeDashoffset")
                    page.locator(f'[data-constellation="{name}"]').scroll_into_view_if_needed()
                    page.wait_for_timeout(350)
                    after = page.locator(sel).first.evaluate("e => getComputedStyle(e).strokeDashoffset")
                    constellation_checks[name] = {"before": before, "after": after, "animated": before != after}

                page.locator(".hero").scroll_into_view_if_needed()
                page.wait_for_timeout(200)
                logo = page.locator(".voyage-logo")
                menu_ok = True
                if viewport["width"] <= 760:
                    button = page.locator("[data-menu-button]")
                    button.click()
                    menu_ok = button.get_attribute("aria-expanded") == "true"
                    page.keyboard.press("Escape")
                    menu_ok = menu_ok and button.get_attribute("aria-expanded") == "false"

                results[label] = {
                    "title": page.title(),
                    "h1_count": page.locator("h1").count(),
                    "constellations": page.locator("[data-constellation]").count(),
                    "horizontal_overflow": page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"),
                    "menu_ok": menu_ok,
                    "console_errors": console_errors,
                    "bad_responses": bad_responses,
                    "constellation_animation": constellation_checks,
                    "original_logo": {
                        "src": logo.get_attribute("src"),
                        "loaded": logo.evaluate("e => e.complete && e.naturalWidth > 100"),
                        "is_fallback": logo.evaluate("e => e.classList.contains('is-fallback')"),
                    },
                }
                page.close()

            # Case study page render check
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            case_errors = []
            page.on("console", lambda msg, e=case_errors: e.append(msg.text) if msg.type == "error" else None)
            page.goto(base + "/work/autoqa-foundation.html", wait_until="networkidle")
            results["case-study"] = {
                "title": page.title(),
                "h1_count": page.locator("h1").count(),
                "horizontal_overflow": page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"),
                "console_errors": case_errors,
            }
            page.close()

            # Reduced motion: constellations must resolve to a complete static state
            page = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
            page.goto(base + "/", wait_until="networkidle")
            page.locator('[data-constellation="orion"]').scroll_into_view_if_needed()
            page.wait_for_timeout(150)
            results["reduced-motion"] = {
                "line_offset": page.locator('[data-constellation="orion"] .constellation-line').first.evaluate("e => getComputedStyle(e).strokeDashoffset"),
                "star_opacity": page.locator('[data-constellation="orion"] .star').first.evaluate("e => getComputedStyle(e).opacity"),
                "label_opacity": page.locator('[data-constellation="orion"] .star-label').first.evaluate("e => getComputedStyle(e).opacity"),
            }
            page.close()
            browser.close()
    finally:
        server.shutdown()

    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "browser-results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))

    failures = []
    for label, _ in VIEWPORTS:
        row = results[label]
        if row["h1_count"] != 1:
            failures.append(f"{label}: expected one h1")
        if row["constellations"] != 3:
            failures.append(f"{label}: expected three constellations")
        if row["horizontal_overflow"] != 0:
            failures.append(f"{label}: horizontal overflow")
        if row["console_errors"]:
            failures.append(f"{label}: console errors: {row['console_errors'][:2]}")
        if row["bad_responses"]:
            failures.append(f"{label}: broken assets: {row['bad_responses'][:3]}")
        if not row["menu_ok"]:
            failures.append(f"{label}: menu behavior")
        for cname, check in row["constellation_animation"].items():
            if not check["animated"]:
                failures.append(f"{label}: {cname} did not animate on scroll")
        logo = row["original_logo"]
        if logo["src"] != "/docs/assets/images/LearningVoyageLogo.svg" or not logo["loaded"] or logo["is_fallback"]:
            failures.append(f"{label}: original emblem did not load from /docs/assets/images/LearningVoyageLogo.svg")
    case = results["case-study"]
    if case["h1_count"] != 1 or case["horizontal_overflow"] != 0 or case["console_errors"]:
        failures.append("case-study: render check failed")
    if results["reduced-motion"]["line_offset"] not in ("0px", "0"):
        failures.append("reduced-motion: constellation line not complete")
    if float(results["reduced-motion"]["star_opacity"]) < 0.99:
        failures.append("reduced-motion: star not visible")
    if float(results["reduced-motion"]["label_opacity"]) < 0.5:
        failures.append("reduced-motion: star labels not revealed")
    if failures:
        raise SystemExit("Browser smoke failures: " + "; ".join(failures))
    print("Browser smoke: all checks passed.")


if __name__ == "__main__":
    main()
