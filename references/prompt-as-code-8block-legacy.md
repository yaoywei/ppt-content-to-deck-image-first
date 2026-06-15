# Prompt-as-Code Template (GPT-Image-2)

Source: adapted from [freestylefly/awesome-gpt-image-2](https://github.com/freestylefly/awesome-gpt-image-2) "Atomic schema" pattern. The 470+ reverse-engineered cases in that repo consistently use this structure — it dramatically improves CJK text accuracy vs. prose prompts.

## Why this structure works

- `[Output]` + `[Layout]` set spatial constraints **before** the model thinks about content.
- `[Typography]` with "MUST render EXACTLY" + per-block size + color = forces per-region glyph generation.
- `white #FFFFFF` is the most reliable CJK glyph color on dark backgrounds.
- Specifying font style (`Noto Sans CJK SC` / `PingFang SC`) helps but is not 100% reliable — verification is still required.

## The 8 atomic blocks (always in this order)

```
[Output] ONE 16:9 landscape PPT <page-type> at 1920x1080
[Style] <palette + visual references, LOCKED after user picks a style>
[Subject] <main visual subject>
[Background] <bg color + texture/glow/pattern>
[Layout] <grid structure, card count, alignment>
[Typography - MUST render EXACTLY in Chinese, sans-serif white #FFFFFF]
  <block-1: section label, size, color>
  <block-2: main heading, size, color>
  <block-3+: bullets / cards / footer, each labeled by position and size>
[Quality] <resolution, polish level>
[Negative] NO WATERMARK, NO misspelled Chinese, ONLY the exact characters listed above
```

## Three proven style templates (lock one of these, then vary only [Subject] / [Layout] / [Typography])

### S1: 极简科技蓝 (Apple Keynote × McKinsey)

```
[Style] Minimalist tech-blue corporate, palette: deep navy #0A1F3A → #1A3A6B + silver white + gold accent #D4AF37
[Subject] Abstract geometric drone silhouette, wings-spread
[Background] Deep navy gradient, vertically smooth, no banding
[Layout] 16:9, top-right small compass icon, center-bottom 60% negative space for typography
[Quality] 1920x1080, ultra-clean, print-ready crispness
```

### S2: 科技国潮金 (Forbidden City cultural creative × SpaceX)

```
[Style] Tech + national-chic gold corporate, palette: midnight blue #0B1B3F + brushed gold #C8A456 + silk-thread gold accents
[Subject] Stylized metallic gold gradient drone, wing-spread silhouette, centered
[Background] Deep midnight blue with subtle gold guilloche silk-pattern texture overlay (low opacity 8%)
[Layout] 16:9, gold line connects 3 small landmark icons (pagoda, dune, modern skyscraper) symbolizing Silk Road global reach
[Quality] 1920x1080, premium, dignified, internationally credible
```

### S3: 未来数据大屏 (Iron Man HUD × DJI Enterprise dashboard)

```
[Style] Futuristic dark data-center command console, palette: near-black #050810 + cyan #00D4FF + electric-blue #1979FF
[Subject] Translucent wireframe drone with glowing thrusters, center stage
[Background] Near-black with layered cyan and electric-blue holographic data streams, volumetric glow, scan-line texture
[Layout] 16:9, behind subject: real-time holographic airspace radar display (flight paths, scanning grid, concentric rings, waypoint nodes)
[Quality] 1920x1080, cinematic, investor-grade, ultra-detailed
```

## Real example — a complete S3 cover page that passed vision QA

```
[Output] ONE 16:9 landscape PPT cover slide at 1920x1080
[Style] Futuristic dark data-center command console, palette: near-black #050810 + cyan #00D4FF + electric-blue #1979FF
[Subject] Translucent wireframe drone with glowing thrusters, center stage
[Background] Near-black #050810 with layered cyan and electric-blue holographic data streams, volumetric glow, scan-line texture
[Layout] Behind drone: real-time holographic airspace radar display with flight paths, scanning grid, concentric rings, waypoint nodes
[Bottom] Clean futuristic data visualization bar with abstract UI accents
[Style references] Iron Man HUD, DJI Enterprise dashboard, sci-fi command center
[Typography - MUST render EXACTLY in Chinese, sans-serif (Noto Sans CJK SC style), white #FFFFFF]
  Top-left small badge (32pt): "湖南鲲鹏翼航"
  Center-left main title (96pt bold): "鲲鹏翼航"
  Center-left subtitle (48pt): "科技 · 低空经济 · 全球服务"
  Bottom-center (24pt): "KUNPENG YIHANG · LOW-ALTITUDE INTELLIGENCE"
  Bottom-right small text (20pt): "湖南长沙 · 全球10+ 国"
[Quality] 1920x1080, cinematic, investor-grade, ultra-detailed, sharp contrast
[Negative] NO WATERMARK, NO English-only main text, NO random characters, NO misspelled Chinese, ONLY the exact characters listed above
```

**Result**: 0 错字 / 0 乱码 / 0 扭曲 across 15 pages using this template.

## Anti-patterns (don't do these)

- ❌ Prose prompts ("a futuristic cover with company name 鲲鹏翼航...") — CJK accuracy drops sharply.
- ❌ Mixing Chinese typography constraints inside English sentences — model skips the constraint.
- ❌ "Generate all 15 pages as a 2x4 grid" for first-pass style probes — grids confuse the model. Get individual cover probes first.
- ❌ Re-prompting on style after the user locked one — copy the [Style] block verbatim across all pages.
- ❌ Using Chinese typography in Phase 2 (style-probe) — save CJK rendering for Phase 3.
