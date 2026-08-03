# Non-negotiable visual preservation

The animated Learning Voyage emblem and constellation sequences are part of the brand, not disposable decoration. Any implementation based on this package must preserve them unless Owen explicitly changes that decision.

## Preserve exactly from the current repository

- `docs/assets/images/LearningVoyageLogo.svg`, the detailed original production emblem.
- The curved `LEARNING VOYAGE` letter reveal around the emblem.
- Floating/bobbing motion, glow pulse, and water shimmer.
- The deterministic ambient starfield.
- The existing Orion, Ursa Major, and Aquarius star coordinates, line connections, labels, and Orion M42 marker.
- Scroll-progress drawing and sequential star reveal.
- A complete static version for `prefers-reduced-motion`.

## What may change

- Copy, section order, typography, spacing, and interaction polish may improve.
- The emblem may be resized responsively, but it must remain prominent in the first viewport.
- Constellations may be used as transitions around stronger content, but they must not be removed or reduced to generic dots.

## Design intent

The site should feel like a distinctive research-oriented professional portfolio with a celestial/nautical identity. It should not become a generic AI consultancy template, a sterile research-paper page, or a lead-generation funnel.

## Deployment rule

Overlay the redesign on the existing GitHub Pages repository. Do not delete the `docs/` asset tree. The included `assets/logo-fallback.svg` is only a resilient local fallback; production should render the original detailed emblem.
