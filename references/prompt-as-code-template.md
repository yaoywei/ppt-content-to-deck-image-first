# Prompt-as-Code Structured Prompts (Upgraded Style Blocks)

After 6/2026, the GPT-Image-2 prompt engineering community (e.g. `freestylefly/awesome-gpt-image-2` on GitHub — 400+ reverse-engineered cases, 20+ industrial templates) has converged on a 7-section atomic schema for image-gen prompts:

```
[Subject]    - the main object / figure / scene focal point
[Background] - color, gradient, texture, environment
[Lighting]   - color temperature, key/rim, intensity, mood
[Materials]  - surface finish, reflectivity, texture detail
[Layout]     - composition, positioning, negative space
[Style refs] - named design references (Apple keynote, McKinsey deck, etc.)
[Negative]   - explicit exclusions (NO TEXT, NO WATERMARK, etc.)
```

**Why this beats prose prompts:**

1. **Variance control** - AI image models interpret "minimalist tech-blue cover with abstract drone" 12 different ways. The structured `[Subject] / [Background] / [Lighting]` partitioning forces a more consistent interpretation across regenerations.
2. **Diff-friendly** - if the user says "background too dark, lighten it", you change only `[Background]` and re-roll, not rewrite the whole prompt.
3. **Chinese third-party reseller endpoints** (zhongzhuan, ciyuan, apimart, pptoken, etc.) have higher variance than first-party OpenAI. Structured prompts dampen that variance.
4. **Per-page variation** - in Phase 2, the `[Subject] / [Layout] / [Background]` blocks are locked to the chosen style; only the per-page content slot rotates. This is exactly the "shared style prefix" pattern from the SKILL.md, but expressed as 3-4 atomic slots instead of one prose paragraph.

**These templates are an UPGRADE of the prose style blocks in `cover-prompt-template.md`.** Both work; use Prompt-as-Code when:
- User is on a Chinese third-party reseller (most non-direct-OpenAI users)
- You've already re-rolled a cover 2+ times and need to tighten
- You want to A/B two background colors without re-prompting everything

---

## Style Block A: 极简科技蓝 (Prompt-as-Code)

```
[Subject] Abstract geometric drone silhouette, wings-spread, hovering at center-right of slide
[Background] Deep navy gradient #0A1F3A → #1A3A6B, vertically smooth, no banding
[Lighting] Single soft top-light, 4500K cool white, drone rim-lit gold accent (#D4AF37)
[Materials] Brushed titanium drone body, frosted glass subtle UI accents top-right (compass/aircraft icon)
[Layout] 16:9, top-right small compass icon, center-bottom 60% negative space for typography overlay later
[Style references] Apple keynote cover, McKinsey strategy deck cover
[Quality] 1920x1080, ultra-clean, print-ready crispness, no noise, no grain
[Negative] NO TEXT, NO LETTERS, NO WATERMARK, NO CAPTIONS, NO LOGOS anywhere
```

**Per-page variation (Phase 2):** swap `[Subject]` slot:
- Data dashboard page → `[Subject] Minimal 3-column data dashboard card, thin gold dividers, abstract number placeholders`
- Scenario grid page → `[Subject] 2x2 grid of abstract scenario cards, each with a small monochrome drone-icon glyph`
- Team portrait page → `[Subject] 5 head-and-shoulders silhouettes, evenly spaced, no facial detail, monochrome`
- Timeline page → `[Subject] Horizontal arrow traversing slide, 5 small milestone dots evenly distributed`

---

## Style Block B: 科技国潮金 (Prompt-as-Code)

```
[Subject] Stylized metallic gold gradient drone, wing-spread silhouette, centered
[Background] Deep midnight blue #0B1B3F with subtle gold guilloche silk-pattern texture overlay (low opacity 8%)
[Lighting] Warm gold rim-light from above, soft volumetric glow
[Materials] Brushed gold metallic body, silk-thread gold horizontal line traversing slide left to right
[Layout] 16:9, gold line connects 3 small landmark icons (pagoda, dune, modern skyscraper) symbolizing Silk Road global reach
[Background details] Subtle constellation-style dotted globe, low opacity
[Style references] Luxury Chinese tech brand (Forbidden City cultural creative), SpaceX annual report, Belt and Road publication cover
[Quality] 1920x1080, premium, dignified, internationally credible
[Negative] NO TEXT, NO LETTERS, NO WATERMARK, NO CAPTIONS, NO CHINESE CHARACTERS, NO LOGOS
```

**Per-page variation:**
- City scenario page → fade the gold line to a single landmark (skyscraper), keep gold + blue
- International page → keep the 3-landmark silk-road row, swap drone icon to a globe
- Timeline page → replace horizontal line with a vertical timeline of 5 gold milestone rings

---

## Style Block C: 未来数据大屏 (Prompt-as-Code)

```
[Subject] Translucent wireframe drone, glowing thrusters, center stage
[Background] Near-black #050810, cyan and electric-blue holographic data streams (#00D4FF, #1979FF), volumetric glow
[Lighting] Cyan key light from drone, electric-blue rim, dark moody atmosphere
[Materials] Holographic UI elements, glass-like data streams, scan-line texture
[Layout] 16:9, behind drone: real-time holographic airspace radar display (flight paths, scanning grid, concentric rings, waypoint nodes)
[Bottom] Clean data visualization bar with futuristic UI accents (no specific text, just clean abstract bars)
[Style references] Iron Man HUD, DJI Enterprise dashboard, sci-fi command center
[Quality] 1920x1080, cinematic, investor-grade, ultra-detailed
[Negative] NO TEXT, NO LETTERS, NO WATERMARK, NO CAPTIONS, NO CHINESE CHARACTERS, NO LOGOS
```

**Per-page variation:**
- Ops / data page → swap drone for a circular radar with scanning sweep
- Metrics page → replace drone with a holographic data chart (donut or bar) in wireframe
- International page → swap radar for a network map of glowing route arcs

---

## Concatenation pattern (how to use in code)

In a script / prompt-builder:

```python
def build_cover_prompt(style: str, page: str) -> str:
    base = STYLE_BLOCKS[style]  # one of A/B/C
    variation = PAGE_VARIATIONS[style][page]  # swap [Subject] slot
    return base.replace("[Subject] " + original_subject, "[Subject] " + variation)
```

Or simpler: keep the 7 sections as a dict, do `"\n".join(f"[{k}] {v}" for k, v in sections.items())`.

---

## What the awesome-gpt-image-2 repo is good for (and what it isn't)

**Good for:**
- A/B testing `[Lighting]` color temperatures on the same scene
- Finding which `[Negative]` keywords actually suppress fake-text on a given model
- A library of named `[Style references]` (Apple, McKinsey, SpaceX, Iron Man, DJI) for `[Style refs]` slots

**Not good for:**
- Chinese text rendering tricks (the repo is 90% English cases — the [Negative] `NO CHINESE CHARACTERS` is the practical lever)
- Layout / composition recipes specific to a 16:9 PPT cover (the repo covers general image-gen, not slide-gen)
- Font selection (the repo confirms: "AI does not pick fonts, it just generates something font-like")

---

## When to use Prompt-as-Code vs prose

| Scenario | Use Prompt-as-Code | Use prose (cover-prompt-template.md) |
|---|---|---|
| Direct OpenAI / first-party endpoint | OK, but prose is also fine | OK |
| Chinese third-party reseller (ciyuan / apimart / pptoken / zhongzhuan) | **Strongly preferred** | Higher variance, more re-rolls |
| User already approved a cover and you need 14 more pages in the same style | **Required** — the shared-prefix pattern lives here | Hard to keep consistent |
| Quick prototype to show user a rough idea | Optional | Faster to write |
| Phase 1 covers (first 3 attempts) | Optional | Faster to iterate |
| Phase 2 batch (14 pages, locked style) | **Required** | Will drift across pages |
