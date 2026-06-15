# Styling-Page PIL Composition Template

A reusable PIL recipe for composing a **styling-page preview** (1600×1000) from:
- One AI-generated thumbnail (1536×1024 baoyu style preview, or any landscape)
- Metadata: style ID, display name, palette (3 hex), elements, tagline

The output is a self-contained preview page suitable for:
- GitHub README hero images
- GitHub Pages gallery thumbnails
- Internal style-library documentation

## When to use

- You've generated N style thumbnails via `image_generate` and want a uniform preview page for each
- You're building a "style library" repo (e.g. for a design system or PPT template kit)
- The user wants to compare styles side-by-side with consistent chrome

## Proven layout (1600×1000)

```
┌────────────────────────────────────────────────────────────┐
│  HEADER (dark slate, h=90)                                │
│  🎨 {style_id}                                            │
│  baoyu-style · 1536×1024 preview                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   PREVIEW FRAME (1200×600, centered, with shadow border)  │
│   [the AI-generated thumbnail]                             │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  {Display name in Chinese, big bold)                       │
│                                                            │
│  PALETTE    [swatch] [swatch] [swatch]                    │
│                                                            │
│  ELEMENTS   {keyword chips}                                │
│                                                            │
│  BEST FOR   {tagline, recommended scenarios}              │
│                                                            │
│                                  [style-id: {id} badge]   │
└────────────────────────────────────────────────────────────┘
```

## Working PIL script (drop-in, 12 styles at once)

The full script lives at `scripts/batch_styling_page.py` in this skill's sibling directory — copy it, then edit the `STYLES` list to match your batch.

Key design decisions:
- **CANVAS_W=1600, CANVAS_H=1000** (16:10 ratio, not 16:9 — slightly taller to fit the metadata block comfortably)
- **PREVIEW_W=1200, PREVIEW_H=600** — the AI thumbnail is downscaled with `Image.LANCZOS` and centered in the frame
- **HEADER_H=90** — dark slate (#1e293b) for visual separation
- **Palette swatches**: 70×70 rounded rectangles, 12px radius, drawn with `ImageDraw.rounded_rectangle`
- **Style-id badge**: bottom-right, dark background + white text, 8px rounded corners
- **Font fallback chain**: WQY MicroHei → WQY ZenHei → Noto Sans CJK Bold → DejaVu Sans Bold → PIL default. Always include CJK fonts first for Chinese rendering.

## Pillow compatibility shim (REQUIRED)

```python
try:
    LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # Pillow < 9.1
    LANCZOS = Image.LANCZOS
```

Pillow 9.1+ moved `LANCZOS` to `Image.Resampling.LANCZOS`. The old `Image.LANCZOS` path still works in 9.1-9.2 but is removed in Pillow 10. See Pitfall 19.

## Output size budget

| Component | Size |
|---|---|
| One 1536×1024 baoyu thumbnail | 1-3 MB |
| One 1600×1000 styling page | 400 KB - 1 MB |
| 12-style batch total | ~10 MB |

12 thumbnails + 12 styling pages = ~24 MB before README. With README + index.html ≈ 25 MB. Fits GitHub single-push comfortably.

## File-system placement (survives session cleanup)

- **NEVER** put long-lived work under `/tmp/<slug>/` or `/home/ubuntu/<scratch-dir>/` — these get cleaned mid-session (see Pitfall 18)
- **Default to** `/home/ubuntu/projects/<project-slug>/` for any output the user will see, push, or want back
- **Source AI thumbnails** stay in `~/.hermes/cache/images/` (Hermes-managed, survives sessions)
- **Composed output** (PIL pages) goes under `/home/ubuntu/projects/<project-slug>/docs/`
- **Git** initialized at the project root, commit immediately after each successful batch (local commit is fine even if push is uncertain)

## Common gotchas

1. **Missing CJK font** → styling page renders boxes (`□□□`) for the Chinese display name. Verify the font fallback chain hits a CJK font on the system: `fc-list :lang=zh | head -3`. If empty, install `wqy-microhei` or `fonts-noto-cjk`.
2. **Image is too small to fill the frame** → the AI thumbnail comes back at 1536×1024 (3:2) but the preview frame is 1200×600 (2:1). The `thumbnail()` call downsizes preserving aspect ratio; if the source is much narrower, the frame has visible side margins. The `frame shadow` + `center` logic handles this — output looks intentional, not buggy.
3. **Hex color parsing fails** → palette strings sometimes have typos (`#FF6B6B / #4ECDC4` with extra spaces). The `hex_to_rgb()` helper strips `#`, `/`, whitespace — but if a "color" doesn't start with `#`, it's silently dropped. Add a guard if your palette strings are unreliable.

## What to do after generating

1. Vision-verify at least 1-2 of the 12 pages (use `vision_analyze` per the parent's QA workflow)
2. Write `README.md` with a table of all styles (id / display / best for)
3. Write `docs/index.html` as a GitHub-Pages gallery (responsive CSS grid, `auto-fill minmax(360px, 1fr)`)
4. `git init` + `git commit` + `git push` (if remote exists, otherwise instruct user to create empty repo and push)

## Proven output (real session, 2026-06-13)

12 baoyu styles → 12 AI thumbnails + 12 PIL styling pages + README + index.html = ~35 MB
Single git push: 60 seconds
GitHub Pages preview: works at `https://<user>.github.io/baoyu-styles-export/`

Styles shipped: cyberpunk-neon, corporate-memphis, chalkboard, aged-academia, craft-handmade, kawaii, technical-schematic, pixel-art, morandi-journal, retro-pop-grid, hand-drawn-edu, ui-wireframe.
