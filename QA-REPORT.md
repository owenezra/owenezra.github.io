# QA report — research-facing revamp (client-unnamed build)

Verification performed on branch `revamp/research-facing-site`, 2026-08-02.

## Deterministic suite

Command:

```bash
python -m unittest discover -s tests -v
```

Result: **18 tests passed, 0 failures, 0 errors.**

The suite covers required files, single H1 per page, semantic landmarks, unique
IDs, anchor targets, image alt text, safe external links, metadata and canonical
URLs, JSON-LD validity, absence of former workforce-platform names, no "Trusted
By" language, client-language coherence (named vs unnamed build), AutoQA
prominence and attribution, original emblem path, exact constellation families,
asset-preservation documentation, and sitemap coverage.

## Browser smoke test (isolated, fallback emblem)

Command:

```bash
python tests/browser_smoke.py
```

Result: desktop (1440px) and mobile (390px) — one H1, three constellations,
no console errors, no horizontal overflow, mobile menu ARIA state correct,
constellation lines draw progressively on scroll (stroke-dashoffset 24.19px →
0px). Reduced motion: lines complete (`0px`), stars fully visible (opacity 1).

## Full-fidelity served-site verification (original emblem)

Command:

```bash
python tests/verify_served_site.py
```

Serves the repository root over local HTTP and verifies the production render,
including the original `docs/assets/images/LearningVoyageLogo.svg`.

Result:

- original emblem loads over HTTP (`complete`, natural size 150 × 150) at the
  preserved repository path — the fallback is **not** used;
- curved letter-by-letter `LEARNING VOYAGE` wordmark renders under the emblem;
- no console errors and no horizontal overflow at 1440px or 390px;
- Orion, Ursa Major, and Aquarius transitions all render with original
  geometry, glow colors, and (Orion) M42 nebula treatment;
- reduced-motion render is complete and static.

Screenshots are in `previews/`:

- `hero-emblem-desktop.png`, `hero-emblem-mobile.png`
- `home-desktop-full.png`, `home-mobile-full.png`
- `orion-transition.png`, `ursa-transition.png`, `aquarius-transition.png`
- `orion-reduced-motion.png`
- `autoqa-case-desktop.png`, `autoqa-case-mobile.png`

## Geometry verification

An exact coordinate-level comparison between the previous production
`index.html` and this branch confirmed identical constellation geometry:

- Orion: 22 lines, 22 stars, M42 nebula, labels (M42, Betelgeuse, Bellatrix,
  Rigel, Saiph, Alnitak)
- Ursa Major: 17 lines, 17 stars, 9 labels
- Aquarius: 13 lines, 14 stars, 5 labels

All line coordinates, star positions/radii/colors, and label placements match
the original site exactly.

## Client-language state

This branch ships the **client-unnamed** build:

- "Data and evaluation work supporting frontier AI and technology
  organizations through external AI data partners."
- "Selected projects have included managing data and evaluation work
  supporting a frontier AI lab through an external AI data partner."
- Footer: "Project descriptions are deliberately generalized to protect
  confidential client and partner information."

Named-client variants and the exact toggle locations are documented in
`COPY-ALTERNATIVES.md`. Switch only after Owen confirms disclosure permission
for each organization.

## Manual checks still required before publication

1. Confirm the quantified claims (3,000+, seven prototypes, three months, 33%,
   200+, 100+, robotics-award wording) against records.
2. Confirm the public email inbox (`ahoythere@learning.voyage`) is active.
3. Decide on the portrait placeholder vs an approved professional photo.
4. Decide the AutoQA attribution line (Owen personally vs through Learning
   Voyage LLC) and whether AutoQA gets a `learning.voyage` subdomain.
5. Open the deployed pages on physical iOS and Android devices after merge.
