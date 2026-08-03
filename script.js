(() => {
  // Publication configuration. The client-experience sentence is gated by
  // governing agreements. To enable a named-client sentence after disclosure
  // permission is confirmed, paste the approved wording from the private claim
  // ledger into CLIENT_REFERENCE_NAMED and set the flag to true. The named
  // wording is deliberately not stored in this public file while disabled.
  const ENABLE_NAMED_CLIENT_REFERENCE = false;
  const CLIENT_REFERENCE_UNNAMED = 'Selected work has included managing data and evaluation projects supporting a frontier AI lab through an external AI data partner.';
  const CLIENT_REFERENCE_NAMED = '';

  const header = document.querySelector('[data-header]');
  const button = document.querySelector('[data-menu-button]');
  const menu = document.querySelector('[data-menu]');
  const year = document.querySelector('[data-year]');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  const clientReference = (ENABLE_NAMED_CLIENT_REFERENCE && CLIENT_REFERENCE_NAMED)
    ? CLIENT_REFERENCE_NAMED
    : CLIENT_REFERENCE_UNNAMED;
  document.querySelectorAll('[data-client-reference]').forEach((node) => {
    node.textContent = clientReference;
  });

  const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
  const ease = (value) => 1 - Math.pow(1 - clamp(value), 3);

  const syncHeader = () => {
    if (!header) return;
    header.classList.toggle('is-scrolled', window.scrollY > 8);
  };

  const closeMenu = () => {
    if (!button || !menu) return;
    button.setAttribute('aria-expanded', 'false');
    menu.classList.remove('is-open');
  };

  if (year) year.textContent = String(new Date().getFullYear());

  if (button && menu) {
    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') === 'true';
      button.setAttribute('aria-expanded', String(!open));
      menu.classList.toggle('is-open', !open);
    });

    menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeMenu();
    });
  }

  const logo = document.querySelector('.voyage-logo');
  if (logo) {
    logo.addEventListener('error', () => {
      if (logo.classList.contains('is-fallback')) return;
      const fallback = logo.dataset.logoFallback;
      if (!fallback) return;
      logo.classList.add('is-fallback');
      logo.alt = 'Learning Voyage compass mark';
      logo.src = fallback;
    });
  }

  const makeStarfield = () => {
    const field = document.querySelector('[data-starfield]');
    if (!field) return;
    const count = window.innerWidth < 760 ? 54 : 108;
    let seed = 74291;
    const random = () => {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      return seed / 4294967296;
    };
    const fragment = document.createDocumentFragment();
    for (let index = 0; index < count; index += 1) {
      const star = document.createElement('span');
      star.className = 'starfield-star';
      star.style.setProperty('--x', `${(random() * 100).toFixed(3)}%`);
      star.style.setProperty('--y', `${(random() * 100).toFixed(3)}%`);
      star.style.setProperty('--size', `${(0.65 + random() * 1.55).toFixed(2)}px`);
      star.style.setProperty('--opacity', `${(0.28 + random() * 0.58).toFixed(2)}`);
      star.style.setProperty('--duration', `${(2.7 + random() * 5.8).toFixed(2)}s`);
      star.style.setProperty('--delay', `${(-random() * 6).toFixed(2)}s`);
      fragment.appendChild(star);
    }
    field.replaceChildren(fragment);
  };

  const constellations = Array.from(document.querySelectorAll('[data-constellation]')).map((section) => {
    const lines = Array.from(section.querySelectorAll('.constellation-line'));
    const stars = Array.from(section.querySelectorAll('.star, .nebula'));
    const labels = Array.from(section.querySelectorAll('.star-label'));

    lines.forEach((line) => {
      const length = Math.max(0.01, line.getTotalLength());
      line.dataset.length = String(length);
      line.style.strokeDasharray = `${length}`;
      line.style.strokeDashoffset = `${length}`;
    });

    labels.forEach((label) => {
      label.textContent = label.dataset.label || '';
    });

    return { section, lines, stars, labels };
  });

  const renderConstellations = () => {
    const viewport = window.innerHeight;
    const noMotion = reducedMotion.matches;

    constellations.forEach(({ section, lines, stars, labels }) => {
      const rect = section.getBoundingClientRect();
      const travel = viewport + rect.height * 0.46;
      const progress = noMotion ? 1 : clamp((viewport * 0.9 - rect.top) / travel);

      lines.forEach((line, index) => {
        const start = (index / Math.max(1, lines.length)) * 0.66;
        const local = ease(clamp((progress - start) / 0.22));
        const length = Number(line.dataset.length || 1);
        line.style.strokeDashoffset = String(length * (1 - local));
        line.style.opacity = String(0.2 + local * 0.8);
      });

      stars.forEach((star, index) => {
        const start = 0.17 + (index / Math.max(1, stars.length)) * 0.68;
        const local = ease(clamp((progress - start) / 0.13));
        star.style.opacity = String(local);
        star.style.transform = `scale(${0.18 + local * 0.82})`;
      });

      labels.forEach((label, index) => {
        const start = 0.68 + (index / Math.max(1, labels.length)) * 0.22;
        const local = ease(clamp((progress - start) / 0.12));
        label.style.opacity = String(local * 0.78);
      });
    });
  };

  let frameRequested = false;
  const requestRender = () => {
    syncHeader();
    if (frameRequested) return;
    frameRequested = true;
    requestAnimationFrame(() => {
      renderConstellations();
      frameRequested = false;
    });
  };

  makeStarfield();
  window.addEventListener('scroll', requestRender, { passive: true });
  window.addEventListener('resize', requestRender, { passive: true });
  reducedMotion.addEventListener?.('change', requestRender);
  requestRender();
})();
