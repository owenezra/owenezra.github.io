"""Full-fidelity verification of the revamped site served from the repo root.

Captures desktop/mobile/reduced-motion screenshots with the ORIGINAL
LearningVoyageLogo.svg asset (not the fallback) and checks constellation
scroll-draw behavior over real HTTP.
"""
import json
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "previews"
OUT.mkdir(exist_ok=True)
PORT = 8619

server = subprocess.Popen(
    ["python", "-m", "http.server", str(PORT)],
    cwd=ROOT,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
time.sleep(1.2)
base = f"http://127.0.0.1:{PORT}"
results = {}

try:
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

        # --- Desktop full page ---
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(base + "/", wait_until="networkidle")
        page.wait_for_timeout(1800)  # let logo arrival + curved letters settle
        logo_state = page.locator("img.voyage-logo").evaluate(
            "e => ({src: e.getAttribute('src'), complete: e.complete, naturalWidth: e.naturalWidth, naturalHeight: e.naturalHeight})"
        )
        # hero close-up with original emblem
        page.locator(".signature-hero").screenshot(path=str(OUT / "hero-emblem-desktop.png"))
        page.screenshot(path=str(OUT / "home-desktop-full.png"), full_page=True)
        results["desktop"] = {
            "logo": logo_state,
            "console_errors": errors,
            "overflow": page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"),
        }

        # --- Constellation transitions: scroll each to mid-draw and capture ---
        for name in ["orion", "ursa", "aquarius"]:
            page.evaluate(
                """(name) => {
                    const el = document.querySelector(`[data-constellation="${name}"]`);
                    const r = el.getBoundingClientRect();
                    const target = window.scrollY + r.top - window.innerHeight * 0.35;
                    window.scrollTo({top: target, behavior: 'instant'});
                }""",
                name,
            )
            page.wait_for_timeout(700)
            page.locator(f'[data-constellation="{name}"]').screenshot(path=str(OUT / f"{name}-transition.png"))
            state = page.locator(f'[data-constellation="{name}"] .constellation-line').first.evaluate(
                "e => getComputedStyle(e).strokeDashoffset"
            )
            results[f"{name}_offset_at_capture"] = state

        # --- Mobile full page + menu ---
        mob = browser.new_page(viewport={"width": 390, "height": 844})
        merr = []
        mob.on("console", lambda m: merr.append(m.text) if m.type == "error" else None)
        mob.goto(base + "/", wait_until="networkidle")
        mob.wait_for_timeout(1800)
        mob.locator(".signature-hero").screenshot(path=str(OUT / "hero-emblem-mobile.png"))
        mob.screenshot(path=str(OUT / "home-mobile-full.png"), full_page=True)
        results["mobile"] = {
            "console_errors": merr,
            "overflow": mob.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"),
        }
        mob.close()

        # --- Reduced motion: complete static render ---
        rm = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
        rm.goto(base + "/", wait_until="networkidle")
        rm.locator('[data-constellation="orion"]').scroll_into_view_if_needed()
        rm.wait_for_timeout(300)
        rm.locator('[data-constellation="orion"]').screenshot(path=str(OUT / "orion-reduced-motion.png"))
        results["reduced_motion"] = {
            "line_offset": rm.locator('[data-constellation="orion"] .constellation-line').first.evaluate(
                "e => getComputedStyle(e).strokeDashoffset"
            ),
            "star_opacity": rm.locator('[data-constellation="orion"] .star').first.evaluate(
                "e => getComputedStyle(e).opacity"
            ),
        }
        rm.close()

        # --- AutoQA case study ---
        cs = browser.new_page(viewport={"width": 1440, "height": 1000})
        cs.goto(base + "/work/autoqa-foundation.html", wait_until="networkidle")
        cs.wait_for_timeout(600)
        cs.screenshot(path=str(OUT / "autoqa-case-desktop.png"), full_page=True)
        cs.close()
        csm = browser.new_page(viewport={"width": 390, "height": 844})
        csm.goto(base + "/work/autoqa-foundation.html", wait_until="networkidle")
        csm.wait_for_timeout(600)
        csm.screenshot(path=str(OUT / "autoqa-case-mobile.png"), full_page=True)
        csm.close()

        page.close()
        browser.close()
finally:
    server.terminate()
    server.wait()

print(json.dumps(results, indent=2))

failures = []
logo = results["desktop"]["logo"]
if not (logo["complete"] and logo["naturalWidth"] > 0):
    failures.append(f"original logo did not load: {logo}")
if logo["src"] != "/docs/assets/images/LearningVoyageLogo.svg":
    failures.append(f"unexpected logo src: {logo['src']}")
for k in ("desktop", "mobile"):
    if results[k]["console_errors"]:
        failures.append(f"{k}: console errors {results[k]['console_errors']}")
    if results[k]["overflow"] != 0:
        failures.append(f"{k}: horizontal overflow {results[k]['overflow']}")
if results["reduced_motion"]["line_offset"] not in ("0px", "0"):
    failures.append("reduced motion incomplete")
if float(results["reduced_motion"]["star_opacity"]) < 0.99:
    failures.append("reduced motion stars hidden")
if failures:
    raise SystemExit("FAILURES: " + "; ".join(failures))
print("ALL FULL-FIDELITY CHECKS PASSED")
