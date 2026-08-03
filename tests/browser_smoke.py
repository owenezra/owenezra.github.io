from pathlib import Path
import base64
import json

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    raise SystemExit("Install Playwright first: pip install playwright && playwright install chromium") from exc

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text(encoding="utf-8")
css = (ROOT / "styles.css").read_text(encoding="utf-8")
js = (ROOT / "script.js").read_text(encoding="utf-8")
fallback = (ROOT / "assets" / "favicon.svg").read_bytes()
fallback_uri = "data:image/svg+xml;base64," + base64.b64encode(fallback).decode("ascii")

# The production homepage intentionally references the original emblem in the
# current repository. This isolated smoke test substitutes the local fallback so
# it can test layout and interaction without overwriting or duplicating that asset.
html = html.replace('<link rel="stylesheet" href="/styles.css">', f"<style>{css}</style>")
html = html.replace('<script src="/script.js" defer></script>', f"<script>{js}</script>")
html = html.replace('/docs/assets/images/LearningVoyageLogo.svg', fallback_uri)
html = html.replace('/assets/favicon.svg', fallback_uri)

results = {}
with sync_playwright() as p:
    launch_kwargs = {"headless": True, "args": ["--no-sandbox"]}
    for candidate in (
        "/usr/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ):
        if Path(candidate).exists():
            launch_kwargs["executable_path"] = candidate
            break
    browser = p.chromium.launch(**launch_kwargs)
    for label, viewport in [("desktop", {"width": 1440, "height": 1000}), ("mobile", {"width": 390, "height": 844})]:
        page = browser.new_page(viewport=viewport)
        errors = []
        page.on("console", lambda msg, errors=errors: errors.append(msg.text) if msg.type == "error" else None)
        page.set_content(html, wait_until="load")
        page.wait_for_timeout(350)

        before = page.locator('[data-constellation="orion"] .constellation-line').first.evaluate(
            "e => getComputedStyle(e).strokeDashoffset"
        )
        page.locator('[data-constellation="orion"]').scroll_into_view_if_needed()
        page.wait_for_timeout(350)
        after = page.locator('[data-constellation="orion"] .constellation-line').first.evaluate(
            "e => getComputedStyle(e).strokeDashoffset"
        )

        menu_ok = True
        if label == "mobile":
            button = page.locator("[data-menu-button]")
            button.click()
            menu_ok = button.get_attribute("aria-expanded") == "true"
            page.keyboard.press("Escape")
            menu_ok = menu_ok and button.get_attribute("aria-expanded") == "false"

        results[label] = {
            "title": page.title(),
            "h1_count": page.locator("h1").count(),
            "constellations": page.locator("[data-constellation]").count(),
            "line_before": before,
            "line_after": after,
            "horizontal_overflow": page.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth"
            ),
            "menu_ok": menu_ok,
            "console_errors": errors,
        }
        page.close()

    page = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
    page.set_content(html, wait_until="load")
    page.locator('[data-constellation="orion"]').scroll_into_view_if_needed()
    page.wait_for_timeout(100)
    results["reduced_motion"] = {
        "line_offset": page.locator('[data-constellation="orion"] .constellation-line').first.evaluate(
            "e => getComputedStyle(e).strokeDashoffset"
        ),
        "star_opacity": page.locator('[data-constellation="orion"] .star').first.evaluate(
            "e => getComputedStyle(e).opacity"
        ),
    }
    page.close()
    browser.close()

print(json.dumps(results, indent=2))

failures = []
for key in ("desktop", "mobile"):
    row = results[key]
    if row["h1_count"] != 1:
        failures.append(f"{key}: expected one h1")
    if row["constellations"] != 3:
        failures.append(f"{key}: expected three constellations")
    if row["horizontal_overflow"] != 0:
        failures.append(f"{key}: horizontal overflow")
    if row["console_errors"]:
        failures.append(f"{key}: console errors")
    if not row["menu_ok"]:
        failures.append(f"{key}: menu behavior")
    if row["line_before"] == row["line_after"]:
        failures.append(f"{key}: constellation did not animate")
if results["reduced_motion"]["line_offset"] not in ("0px", "0"):
    failures.append("reduced motion: line not complete")
if float(results["reduced_motion"]["star_opacity"]) < 0.99:
    failures.append("reduced motion: star not visible")
if failures:
    raise SystemExit("Browser smoke failures: " + "; ".join(failures))
