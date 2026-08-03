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

  // Disable transitions during resize to prevent stutter
  let resizeTimer;
  window.addEventListener('resize', () => {
    document.body.classList.add('resizing');
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => document.body.classList.remove('resizing'), 200);
  });

  // Twinkling stars: production look (60 stars, twinkle keyframes) with a
  // seeded generator so the layout is reproducible across visits.
  const makeStarfield = () => {
    const field = document.querySelector('[data-starfield]');
    if (!field) return;
    let seed = 74291;
    const random = () => {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      return seed / 4294967296;
    };
    const fragment = document.createDocumentFragment();
    for (let index = 0; index < 60; index += 1) {
      const star = document.createElement('span');
      star.className = 'twinkle-star';
      star.style.left = (random() * 100).toFixed(3) + '%';
      star.style.top = (random() * 100).toFixed(3) + '%';
      const size = (random() * 2 + 1).toFixed(2) + 'px';
      star.style.width = size;
      star.style.height = size;
      star.style.animationDelay = (random() * 5).toFixed(2) + 's';
      star.style.animationDuration = (random() * 3 + 2).toFixed(2) + 's';
      fragment.appendChild(star);
    }
    field.replaceChildren(fragment);
  };
  makeStarfield();

  // Scroll fade-ins (html.js gates the hidden state so no-JS stays readable)
  const fadeTargets = document.querySelectorAll('.capability-card, .work-item, .writing-card, .principle-grid article, .evidence-grid article, .connect-card');
  if ('IntersectionObserver' in window && fadeTargets.length) {
    const fadeObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    fadeTargets.forEach((el) => fadeObserver.observe(el));
  }

  // Constellation scan-line reveal. This is a dependency-free port of the
  // production ScrollTrigger implementation: a virtual scan line moves down
  // through each constellation with scroll; stars pop in when the line passes
  // them, connecting lines draw once both endpoint stars have settled, labels
  // fade in letter by letter, and scrolling back up un-draws the figure.
  const constellations = Array.from(document.querySelectorAll('.constellation-transition')).map((section) => {
    const svgElement = section.querySelector('.constellation-svg');
    if (!svgElement) return null;

    const stars = section.querySelectorAll('.star');
    const labels = section.querySelectorAll('.star-label:not(.nebula-label)');
    const lines = section.querySelectorAll('.constellation-line');
    const nebula = section.querySelector('.nebula');
    const nebulaLabel = section.querySelector('.nebula-label');
    if (nebulaLabel && nebulaLabel.dataset.label) nebulaLabel.textContent = nebulaLabel.dataset.label;

    let minStarY = Infinity;
    let maxStarY = -Infinity;
    stars.forEach((star) => {
      const cy = parseFloat(star.getAttribute('cy'));
      if (cy < minStarY) minStarY = cy;
      if (cy > maxStarY) maxStarY = cy;
    });

    const starData = [];
    const starByPos = {};
    const lineData = [];
    stars.forEach((s) => {
      const cx = parseFloat(s.getAttribute('cx'));
      const cy = parseFloat(s.getAttribute('cy'));
      const idx = starData.length;
      const data = { el: s, cx, cy, visible: false, settled: false };
      s.addEventListener('transitionend', (e) => {
        if (e.propertyName !== 'transform' || !data.visible) return;
        data.settled = true;
        for (let j = 0; j < lineData.length; j += 1) {
          const ln = lineData[j];
          if (ln.starA === undefined || ln.starB === undefined) continue;
          if (starData[ln.starA].settled && starData[ln.starB].settled) {
            ln.el.style.transition = 'stroke-dashoffset 0.3s ease-out';
            ln.el.style.strokeDashoffset = 0;
          }
        }
      });
      starData.push(data);
      starByPos[cx + ',' + cy] = idx;
    });

    lines.forEach((line) => {
      const x1 = parseFloat(line.getAttribute('x1'));
      const y1 = parseFloat(line.getAttribute('y1'));
      const x2 = parseFloat(line.getAttribute('x2'));
      const y2 = parseFloat(line.getAttribute('y2'));
      const len = Math.hypot(x2 - x1, y2 - y1);
      line.style.strokeDasharray = len;
      line.style.strokeDashoffset = len;
      lineData.push({ el: line, len, starA: starByPos[x1 + ',' + y1], starB: starByPos[x2 + ',' + y2] });
    });

    const labelData = [];
    labels.forEach((l) => {
      const text = l.getAttribute('data-label') || l.textContent;
      const y = parseFloat(l.getAttribute('y'));
      l.textContent = '';
      const chars = [];
      for (let c = 0; c < text.length; c += 1) {
        const tspan = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
        tspan.textContent = text[c];
        tspan.style.opacity = '0';
        tspan.style.transition = 'opacity 0.4s ease-out ' + (c * 0.04) + 's';
        l.appendChild(tspan);
        chars.push(tspan);
      }
      labelData.push({ el: l, y, chars, wasVisible: false });
    });

    const nebulaCy = nebula ? parseFloat(nebula.getAttribute('cy')) : null;

    return {
      section, starData, lineData, labelData, nebula, nebulaLabel, nebulaCy,
      minStarY, maxStarY, lastProgress: 0, lastTime: 0,
    };
  }).filter(Boolean);

  const finishConstellation = (c) => {
    c.lineData.forEach((ln) => { ln.el.style.strokeDashoffset = 0; });
    c.starData.forEach((s) => { s.visible = true; s.settled = true; s.el.classList.add('visible'); });
    c.labelData.forEach((lb) => {
      lb.el.classList.add('visible');
      lb.wasVisible = true;
      lb.chars.forEach((ch) => { ch.style.opacity = '1'; });
    });
    if (c.nebula) c.nebula.classList.add('visible');
    if (c.nebulaLabel) c.nebulaLabel.classList.add('visible');
  };

  const resetConstellation = (c) => {
    c.section.classList.remove('visible');
    c.lineData.forEach((ln) => { ln.el.style.strokeDashoffset = ln.len; });
    c.starData.forEach((s) => { s.visible = false; s.settled = false; s.el.classList.remove('visible'); });
    c.labelData.forEach((lb) => {
      lb.el.classList.remove('visible');
      lb.wasVisible = false;
      const last = lb.chars.length - 1;
      lb.chars.forEach((ch, i) => {
        ch.style.transition = 'opacity 0.3s ease-out ' + ((last - i) * 0.04) + 's';
        ch.style.opacity = '0';
      });
    });
    if (c.nebula) c.nebula.classList.remove('visible');
    if (c.nebulaLabel) c.nebulaLabel.classList.remove('visible');
  };

  const updateConstellation = (c, now) => {
    const rect = c.section.getBoundingClientRect();
    const vh = window.innerHeight;
    const travel = vh * 0.8 + rect.height;
    const p = clamp((vh * 0.9 - rect.top) / travel);

    if (p <= 0) {
      if (c.lastProgress > 0) resetConstellation(c);
      c.lastProgress = 0;
      c.lastTime = now;
      return;
    }

    c.section.classList.add('visible');

    if (p >= 1) {
      if (c.lastProgress < 1) finishConstellation(c);
      c.lastProgress = 1;
      c.lastTime = now;
      return;
    }

    const dt = Math.max((now - c.lastTime) / 1000, 1 / 240);
    const vel = Math.abs(p - c.lastProgress) * travel / dt;
    const direction = p >= c.lastProgress ? 1 : -1;

    // Fast scroll (~2000+px/s) = snappy (0.08s), slow scroll = smooth (0.6s)
    const duration = Math.max(0.08, Math.min(0.6, 0.6 - vel / 4000));
    const durStr = duration.toFixed(2) + 's';
    const fastThreshold = 0.15;
    const isFast = duration < fastThreshold;

    let adjusted;
    if (direction === 1) {
      // Drawing: finish by ~50% scroll
      adjusted = Math.min(p * 2.0, 1.0);
    } else {
      // Un-drawing: hold fully drawn until 35%, then un-draw from 35% to 0%
      if (p > 0.65) adjusted = 1.0;
      else if (p < 0.15) adjusted = 0;
      else adjusted = (p - 0.15) / 0.5;
    }
    const scanY = c.minStarY + adjusted * (c.maxStarY + 10 - c.minStarY);

    for (let i = 0; i < c.starData.length; i += 1) {
      const s = c.starData[i];
      const shouldBeVisible = scanY > s.cy;
      if (shouldBeVisible && !s.visible) {
        s.visible = true;
        if (isFast) {
          s.settled = true;
          s.el.style.transition = 'none';
          s.el.classList.add('visible');
        } else {
          s.settled = false;
          s.el.style.transition = 'transform ' + durStr + ' ease-out';
          s.el.classList.add('visible');
        }
      } else if (!shouldBeVisible && s.visible) {
        s.visible = false;
        s.settled = false;
        s.el.style.transition = 'transform ' + durStr + ' ease-out';
        s.el.classList.remove('visible');
      }
    }

    const lineDur = Math.max(0.05, duration * 0.5);
    const lineDurStr = lineDur.toFixed(2) + 's';
    for (let i = 0; i < c.lineData.length; i += 1) {
      const ln = c.lineData[i];
      if (ln.starA === undefined || ln.starB === undefined) continue;
      const bothSettled = c.starData[ln.starA].settled && c.starData[ln.starB].settled;
      const bothVisible = c.starData[ln.starA].visible && c.starData[ln.starB].visible;
      if (bothSettled) {
        ln.el.style.transition = isFast ? 'none' : 'stroke-dashoffset 0.3s ease-out';
        ln.el.style.strokeDashoffset = 0;
      } else if (!bothVisible) {
        ln.el.style.transition = 'stroke-dashoffset ' + lineDurStr + ' ease-out';
        ln.el.style.strokeDashoffset = ln.len;
      }
    }

    for (let i = 0; i < c.labelData.length; i += 1) {
      const lb = c.labelData[i];
      const isVisible = scanY > lb.y + 4;
      if (isVisible && !lb.wasVisible) {
        lb.el.classList.add('visible');
        for (let ch = 0; ch < lb.chars.length; ch += 1) {
          lb.chars[ch].style.transition = 'opacity 0.15s ease-out ' + (ch * 0.08) + 's';
          lb.chars[ch].style.opacity = '1';
        }
        lb.wasVisible = true;
      } else if (!isVisible && lb.wasVisible) {
        lb.el.classList.remove('visible');
        const last = lb.chars.length - 1;
        for (let ch = 0; ch < lb.chars.length; ch += 1) {
          lb.chars[ch].style.transition = 'opacity 0.15s ease-out ' + ((last - ch) * 0.08) + 's';
          lb.chars[ch].style.opacity = '0';
        }
        lb.wasVisible = false;
      }
    }

    if (c.nebula) {
      if (scanY > c.nebulaCy) {
        c.nebula.classList.add('visible');
        if (c.nebulaLabel) c.nebulaLabel.classList.add('visible');
      } else {
        c.nebula.classList.remove('visible');
        if (c.nebulaLabel) c.nebulaLabel.classList.remove('visible');
      }
    }

    c.lastProgress = p;
    c.lastTime = now;
  };

  // Course line drawn on scroll through the experience section
  const route = document.querySelector('.route');
  const routeParts = route ? {
    progressPath: route.querySelector('.route-path-progress'),
    waypoints: route.querySelectorAll('.route-waypoint'),
    routeStar: route.querySelector('.route-star'),
    wpFractions: [0.14, 0.5, 0.86],
  } : null;

  const updateRoute = () => {
    if (!routeParts) return;
    const rect = route.getBoundingClientRect();
    const vh = window.innerHeight;
    const p = clamp((vh * 0.92 - rect.top) / (vh * 0.52));
    routeParts.progressPath.style.strokeDashoffset = 1 - p;
    routeParts.waypoints.forEach((wp, i) => wp.classList.toggle('reached', p >= routeParts.wpFractions[i]));
    if (routeParts.routeStar) routeParts.routeStar.classList.toggle('reached', p >= 0.97);
  };

  const finishAllStatic = () => {
    constellations.forEach((c) => {
      c.section.classList.add('visible');
      finishConstellation(c);
    });
    if (routeParts) {
      routeParts.progressPath.style.strokeDashoffset = 0;
      routeParts.waypoints.forEach((wp) => wp.classList.add('reached'));
      if (routeParts.routeStar) routeParts.routeStar.classList.add('reached');
    }
  };

  let frameRequested = false;
  const requestRender = () => {
    syncHeader();
    if (reducedMotion.matches) return;
    if (frameRequested) return;
    frameRequested = true;
    requestAnimationFrame((now) => {
      constellations.forEach((c) => updateConstellation(c, now));
      updateRoute();
      frameRequested = false;
    });
  };

  if (reducedMotion.matches) {
    finishAllStatic();
  }
  reducedMotion.addEventListener?.('change', () => {
    if (reducedMotion.matches) finishAllStatic();
  });

  window.addEventListener('scroll', requestRender, { passive: true });
  window.addEventListener('resize', requestRender, { passive: true });
  requestRender();
})();
