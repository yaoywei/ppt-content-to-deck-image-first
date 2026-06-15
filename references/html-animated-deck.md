# HTML Animated Deck — Single-File Build Reference

A standalone pattern for producing a **playable, animated PowerPoint-equivalent** as a single self-contained `.html` file. The user double-clicks it, it opens in any browser, and they get full motion + interaction.

This is the right answer when the user asks for "动画 / 特效 / 视觉炸裂" on top of the static `.pptx`/`.pdf` deliverables. The `.pptx` chain does not animate.

## When to use

- User says "加上动画" / "特效" / "动效" / "视觉冲击" / "炸裂"
- User wants to "本地浏览器打开" the deck
- User is pitching live and motion sells the brand
- User wants to share a deck that anyone can open (no PowerPoint required)

**Always produce BOTH .pptx AND .html** when the user asks for animation. The .pptx is for archival / sharing / printing, the .html is for "feel the brand".

## Architecture — 1300 lines of inline CSS + JS

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <style>/* ALL CSS INLINE — no external stylesheets */</style>
</head>
<body>
  <!-- 15 .slide divs, only one has .active at a time -->
  <div class="slide active" id="slide-1">...</div>
  <div class="slide" id="slide-2">...</div>
  ...
  <!-- Navigation chrome (always visible) -->
  <div class="nav">...</div>
  <div class="hint">...</div>
  <script>/* ALL JS INLINE */</script>
</body>
</html>
```

**Critical constraints**:
- Zero external dependencies (no `<link>`, no `<script src=...>`)
- All fonts via system stack: `'PingFang SC', 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif`
- Single file, ~43 KB total
- Works offline, works in any browser, no server required

## Animation building blocks (the proven palette)

### Top scanning line (every page)
```css
.scanline {
  position: absolute;
  left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, #00D4FF 50%, transparent 100%);
  box-shadow: 0 0 12px #00D4FF, 0 0 24px #00D4FF;
  animation: scan 4s linear infinite;
}
@keyframes scan {
  0% { top: -2px; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}
```

### Radar sweep (behind cover, P9 international, P15 contact)
```css
.radar-bg {
  position: absolute;
  top: 50%; left: 50%;
  width: 800px; height: 800px;
  transform: translate(-50%, -50%);
  background: conic-gradient(
    from 0deg,
    transparent 0deg,
    rgba(0, 212, 255, 0.12) 30deg,
    transparent 60deg,
    transparent 360deg
  );
  border-radius: 50%;
  animation: radar-rotate 6s linear infinite;
}
@keyframes radar-rotate {
  to { transform: translate(-50%, -50%) rotate(360deg); }
}
```

### Concentric ring stack (atmospheric background)
```css
.ring { position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  border: 1px solid rgba(0, 212, 255, 0.18);
  border-radius: 50%; }
.ring.r1 { width: 200px; height: 200px; }
.ring.r2 { width: 400px; height: 400px; }
.ring.r3 { width: 600px; height: 600px; }
.ring.r4 { width: 900px; height: 900px; }
```

### Grid background (subtle texture)
```css
.grid-bg {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(0, 212, 255, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 212, 255, 0.06) 1px, transparent 1px);
  background-size: 60px 60px;
}
```

### Particle field (per-slide, generated via JS)
```css
.particle {
  position: absolute;
  width: 2px; height: 2px;
  background: #00D4FF;
  border-radius: 50%;
  box-shadow: 0 0 4px #00D4FF;
  animation: float linear infinite;
}
@keyframes float {
  0% { transform: translateY(0) translateX(0); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(-100vh) translateX(50px); opacity: 0; }
}
```
```js
// Generate 15 particles per slide
function makeParticles() {
  document.querySelectorAll('.slide').forEach(slide => {
    for (let i = 0; i < 15; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      p.style.left = Math.random() * 100 + '%';
      p.style.top = (80 + Math.random() * 20) + '%';
      p.style.animationDuration = (8 + Math.random() * 8) + 's';
      p.style.animationDelay = (Math.random() * 5) + 's';
      slide.appendChild(p);
    }
  });
}
```

### Counter (P3 key numbers)
```js
function animateNumbers() {
  document.querySelectorAll('.stat-number').forEach(el => {
    const target = parseInt(el.dataset.target);
    const duration = 1500;
    const start = performance.now();
    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      el.textContent = Math.round(target * eased) + (target === 98 ? '%' : '+');
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  });
}
```
HTML: `<div class="stat-number" data-target="100">0</div>`

### Bar chart growth (P13 talent structure)
```css
.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #00D4FF 0%, #1979FF 100%);
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.5);
  width: 0;
  animation: barGrow 1.5s ease-out forwards;
  animation-delay: inherit;
}
@keyframes barGrow { to { width: var(--target-width); } }
```
HTML: `<div class="bar-fill" style="--target-width:30%"></div>`

### Timeline nodes (P14 history)
```css
.timeline::before {
  content: '';
  position: absolute;
  top: 50px; left: 60px; right: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00D4FF 20%, #1979FF 50%, #00D4FF 80%, transparent);
  box-shadow: 0 0 8px #00D4FF;
}
.timeline-year {
  width: 100px; height: 100px;
  border-radius: 50%;
  background: radial-gradient(circle, #00D4FF 0%, #1979FF 100%);
  box-shadow: 0 0 32px rgba(0, 212, 255, 0.7), inset 0 0 20px rgba(0,0,0,0.3);
}
```

### Card entrance with stagger
```css
.info-card {
  opacity: 0;
  transform: scale(0.9);
  animation: cardScaleIn 0.5s ease-out forwards;
}
.info-card:nth-child(1) { animation-delay: 0.5s; }
.info-card:nth-child(2) { animation-delay: 0.7s; }
/* ... */
@keyframes cardScaleIn {
  to { opacity: 1; transform: scale(1); }
}
```

### Title reveal (cover)
```css
@keyframes titleReveal {
  0% { opacity: 0; transform: translateY(40px); filter: blur(10px); }
  100% { opacity: 1; transform: translateY(0); filter: blur(0); }
}
```

## Page-switching logic (the engine)

```js
let currentSlide = 1;
const totalSlides = 15;

function showSlide(n) {
  if (n < 1 || n > totalSlides) return;
  document.querySelectorAll('.slide').forEach(s => s.classList.remove('active'));
  document.getElementById('slide-' + n).classList.add('active');
  currentSlide = n;
  document.getElementById('cur').textContent = n;

  // Restart animations on the new slide (reflow trick)
  const target = document.getElementById('slide-' + n);
  target.querySelectorAll('*').forEach(el => {
    const anim = el.style.animation;
    if (anim) {
      el.style.animation = 'none';
      el.offsetHeight; // force reflow
      el.style.animation = '';
    }
  });

  if (n === 3) setTimeout(animateNumbers, 600);
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
    e.preventDefault(); showSlide(currentSlide + 1);
  } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
    e.preventDefault(); showSlide(currentSlide - 1);
  } else if (e.key === 'f' || e.key === 'F') {
    document.documentElement.requestFullscreen();
  } else if (e.key === 'Escape') {
    document.body.classList.toggle('overview');
  }
});

// Touch swipe
let touchStartX = 0;
document.addEventListener('touchstart', e => touchStartX = e.touches[0].clientX);
document.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - touchStartX;
  if (Math.abs(dx) > 60) {
    if (dx < 0) showSlide(currentSlide + 1);
    else showSlide(currentSlide - 1);
  }
});
```

## Overview mode (Esc key)

Shows all 15 slides in a 4-column grid, scaled down:

```css
body.overview .slide {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9 */
  animation: none !important;
}
body.overview .slide-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding: 24px;
}
```

## Feishu delivery — known trap (2026-06-11)

**The Feishu attachment channel often fails silently for `.html` and `.zip` files.** `send_message` returns `success: true` but the user never sees the file. This is the same trap described in Pitfall 10 of the parent skill.

**Fallback chain** (always run in order):

1. Send `.html` via `MEDIA:` — works on some clients/versions
2. Send `.zip` (via Python `zipfile` since the `zip` CLI is often missing) via `MEDIA:`
3. **Confirm receipt** — always ask "你收到了吗?" after each send. Never trust the `success: true` API flag for attachments.
4. If both fail, fall back to **static Playwright screenshots** — render the HTML headlessly, capture each slide as PNG, send the PNGs via `MEDIA:`. The user loses interactivity but gets to see the visuals.

## Playwright rendering fallback (when .html delivery fails)

Playwright is pre-installed at `/tmp/pwvenv/` on this machine (verified 2026-06-11). Chromium binary at `/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome`.

```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    page.goto("file:///path/to/animated.html")
    page.wait_for_load_state("networkidle")
    time.sleep(2)  # let entrance animations settle

    for i in range(1, 16):
        page.evaluate(f"showSlide({i})")
        time.sleep(2.5)  # let in-slide animations finish
        page.screenshot(path=f"p{i:02d}.png")
```

Then `montage` the 15 PNGs into 2-3 grid images and `MEDIA:` send those.

## Visual verification (vision_analyze)

After the HTML is built, **always run vision_analyze on the Playwright-captured PNGs** of the most-text-dense pages (cover, key numbers, bar chart, timeline). This catches:
- CJK rendering failures (font fallback, garbled glyphs)
- Animation-glitched static frames (some `transform: translate` end-states look broken)
- Missing particles / rings / overlay elements

If vision reports issues, fix the corresponding CSS/HTML and rebuild the file.

## Color palette (locked, the proven one)

| Role | Hex |
|---|---|
| Background | `#050810` |
| Primary accent (cyan) | `#00D4FF` |
| Secondary accent (electric blue) | `#1979FF` |
| Text | `#FFFFFF` |
| Muted text | `rgba(255, 255, 255, 0.5-0.7)` |
| Card border | `rgba(0, 212, 255, 0.25-0.3)` |
| Card background | `rgba(0, 212, 255, 0.03-0.06)` |

These map directly to the S3 "未来数据大屏" style from Phase 1 of the parent skill. If the user picked a different style, swap the palette but keep the same CSS structure.

## Anti-patterns

- **Skipping .pptx** when adding .html. The user often still needs the .pptx.
- **Multi-file HTML deck** (separate .js / .css files). They break in transit / on offline viewers.
- **External font / script / image references**. They break offline.
- **Animating the nav chrome** (the prev/next buttons, page counter). They should stay static so the user can always see where they are.
- **Heavy video / WebGL / canvas effects**. They break on low-end machines and make the file huge. CSS + small JS is enough for "视觉冲击".
- **Wide character set fonts** (e.g. downloading the full Noto Sans CJK at 30MB+). Use the system font stack instead.
