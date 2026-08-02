# learning.voyage — owenezra.github.io

Personal site for Owen Onderdonk / Learning Voyage LLC, served with GitHub Pages
at the custom domain `learning.voyage` (see `CNAME`).

The site presents Owen's work in AI data, evaluation, and research operations,
led by the public AutoQA Foundation project, inside the original Learning Voyage
visual identity: the animated ship emblem, curved wordmark, ambient starfield,
and the Orion, Ursa Major, and Aquarius constellation transitions.

## Structure

- `index.html` — homepage (hero → Orion → AutoQA Foundation → experience →
  work → selected work → Ursa Major → research questions → principles →
  Aquarius → about → connect)
- `work/autoqa-foundation.html` — AutoQA Foundation case study
- `styles.css` — shared responsive, reduced-motion-aware styles (no frameworks)
- `script.js` — navigation, deterministic starfield, scroll-progress
  constellation animation (no external animation dependency)
- `docs/assets/images/LearningVoyageLogo.svg` — original emblem, preserved from
  the previous site generation. **Do not delete** (see
  `PRESERVE-ORIGINAL-ASSETS.md` and `VISUAL-PRESERVATION.md`)
- `assets/` — favicon, social images, emblem fallback (fallback only; production
  renders the original)
- `robots.txt`, `sitemap.xml`, `site.webmanifest`, `llms.txt`, `404.html`
- `tests/` — deterministic and browser test suites
- `tools/apply_client_copy.py` + `site.config.json` — client-name toggle

## Client-name toggle (important)

Public copy defaults to the **client-unnamed** variants. Named references to
end clients may only be published after Owen confirms disclosure permission
under the governing agreements (see `COPY-ALTERNATIVES.md`).

```bash
# 1. edit site.config.json:  "clientNames": "named"  or  "unnamed"
# 2. apply and verify
python3 tools/apply_client_copy.py
python3 tools/apply_client_copy.py --check
```

The tool rewrites the marked `CLIENT-COPY` regions in `index.html`; the served
HTML always matches the config, and the named text never sits hidden in source.
The test suite enforces consistency and blocks named-client language whenever
the config is `unnamed`.

## Tests

```bash
# deterministic suite (content, guardrails, metadata, links, accessibility
# smoke, exact constellation geometry vs the original site, ops files)
python3 -m unittest discover -s tests -v

# browser suite (serves this repo locally; uses system Chrome or Playwright
# Chromium; checks console errors, overflow at 390/768/1024/1440, mobile menu,
# scroll animation, reduced-motion completion, original emblem loading)
python3 tests/browser_smoke.py
```

Browser-test requirements: `pip install playwright beautifulsoup4 lxml pillow`
plus a system Chrome or `playwright install chromium`.

## Local preview

```bash
python3 -m http.server 8000
# http://localhost:8000/  and  /work/autoqa-foundation.html
```

## Deployment

GitHub Pages serves the `main` branch at the custom domain. Content changes
land via pull request; DNS and `CNAME` are unchanged. Rollback is `git revert`
of the merge commit (the previous design remains reachable in history).
