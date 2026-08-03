# Learning Voyage website redesign — signature visual edition

This package keeps the research-facing content architecture and AutoQA Foundation positioning while restoring the original Learning Voyage animated emblem, starfield, and exact Orion, Ursa Major, and Aquarius constellation maps. It is designed as an overlay for Owen’s existing GitHub Pages repository so the original logo asset remains intact.

## Strategic decision

The site leads with Owen's functional identity and inspectable work rather than the name recognition of Learning Voyage:

- AI data and evaluation program leadership
- research data operations
- human quality and calibration systems
- specialized-data sourcing and partnerships
- proprietary organizational data for AI
- agent environments and reinforcement-learning tasks
- public work on the capability and authority boundaries of LLM-based quality review

Learning Voyage remains the legal and administrative umbrella.

## Why AutoQA Foundation is first

Private client work establishes experience, but researchers cannot inspect it. AutoQA Foundation provides a public artifact with a defined thesis, source-level evidence, technical material, a pilot protocol, explicit limitations, and operational decision tools. It therefore appears immediately below the hero, before the client-experience strip.

The package also adds a dedicated case study at:

`/work/autoqa-foundation.html`

The case study attributes the work to Owen, explains the contribution without claiming peer review or certification, and links to the full public project.

## Client wording

The default build is **client-unnamed**. It uses this transparent line:

> Data and evaluation work supporting frontier AI and technology organizations through external AI data partners.

It deliberately does **not** say "Trusted by," use client logos, name end clients, claim employment, claim endorsement, or state that Learning Voyage held a direct contract.

Named-client copy exists in `COPY-ALTERNATIVES.md` and may be switched on only after Owen confirms that every governing agreement permits disclosure of each named organization (confidentiality, publicity, portfolio, client-identity, and trademark terms). Until then, keep the unnamed default. The test suite enforces coherence for both build modes.

## Files

- `index.html` — complete semantic homepage
- `work/autoqa-foundation.html` — complete AutoQA Foundation case study
- `styles.css` — responsive, accessible visual system shared by both pages
- `script.js` — navigation, deterministic starfield, logo fallback, and scroll-progress constellation animation; core content remains readable without JavaScript
- `assets/favicon.svg` — self-contained browser icon
- `assets/logo-fallback.svg` — ship-and-sea fallback used only when the repository’s original detailed emblem is unavailable
- `assets/og-image.png` — 1200 × 630 homepage social preview
- `assets/autoqa-og.png` — 1200 × 630 AutoQA case-study social preview
- `site.webmanifest` — basic install/identity metadata
- `robots.txt` — crawler policy
- `sitemap.xml` — homepage and case-study canonical listings
- `llms.txt` — machine-readable description of Owen, Learning Voyage, and AutoQA Foundation
- `404.html` — lightweight fallback page
- `CONTENT.md` — complete publication copy and LinkedIn integration copy
- `SITE-STRATEGY.md` — content, positioning, information architecture, and AutoQA recommendations
- `COPY-ALTERNATIVES.md` — named/unnamed client variants and AutoQA naming alternatives
- `QA-REPORT.md` — deterministic and browser-rendering results
- `tests/test_site.py` — content, metadata, link, attribution, and accessibility smoke tests

## Deploy to GitHub Pages

1. Back up the current repository or create a branch.
2. Preserve `docs/assets/images/LearningVoyageLogo.svg` from the existing repository. The homepage references that exact original asset.
3. Copy this package into the repository root as an overlay; do not delete the existing `docs/` asset tree.
4. Preserve the existing DNS configuration; this package includes `CNAME` with `learning.voyage`.
5. Commit and push to the Pages branch.
6. Confirm the homepage and `/work/autoqa-foundation.html` at desktop and mobile widths.
7. Run the test suite before publishing:

```bash
python -m unittest discover -s tests -v
```

## Local preview

```bash
python -m http.server 8000
```

Then open:

- `http://localhost:8000/`
- `http://localhost:8000/work/autoqa-foundation.html`

## Publication checks

- Confirm the figures 3,000+, seven prototypes, three months, 33%, 200+, and 100+ against your records.
- Confirm that the named end clients may be disclosed.
- Keep client logos off the site unless written permission expressly covers the intended use.
- Confirm that Owen is comfortable attributing AutoQA Foundation to Learning Voyage LLC.
- Add the same visible creator attribution to the AutoQA Foundation site itself.
- Replace the initials block with a professional portrait only when a current image is available and approved for publication.
- Keep the AutoQA limitation language: the project is an independent working framework, not a certification or an accuracy claim for a particular system.


## Restored signature visuals

- Original animated Learning Voyage emblem in the hero.
- Curved letter-by-letter Learning Voyage wordmark.
- Floating ship/emblem motion, glow pulse, and water shimmer.
- Deterministic ambient starfield.
- Exact Orion, Ursa Major, and Aquarius line/star maps from the original site.
- Scroll-progress line drawing, sequential star reveal, and late label reveal.
- Static completed render under `prefers-reduced-motion`.
- No GSAP or external animation dependency.

The visual elements are now structural transitions around the evidence-oriented content rather than a replacement for that content.
