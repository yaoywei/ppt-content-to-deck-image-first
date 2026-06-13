# Learn from a Reference PPT — Extraction Recipe

When the user pastes a `.pptx` (or `.pdf`/slide PNG) as a style reference — "**do it like this deck**", "**参考这份 PPT 的风格**", "**I want the look of 湖南驰阳介绍.pptx**" — you MUST extract the actual visual language before generating any cover. Do NOT generate from your prior on "what does a [industry] PPT look like" — the user wants THIS deck, not the median.

This is the missing step that makes leadership / 政企 PPT generation succeed on the first try instead of after 2-3 redo rounds.

## When this recipe applies

- User pastes a `.pptx` file with a phrase like "用这个风格 / 参考这份 / 风格和这个一样 / look like this deck"
- User pastes a slide PNG and says "do this style"
- User describes a deck in words (e.g. "湖南驰阳那种风格") AND provides a file (the words are vague, the file is the truth)

If the user just says "做一份政企风格 PPT" with NO reference file, skip this recipe and use `references/leadership-deck-style-rules.md` instead (the generic conservative style rules).

## The 4-step recipe

### Step 1 — Convert .pptx to .pdf

```bash
# CJK filenames: soffice handles them, pdftoppm does not always
soffice --headless --convert-to pdf "<path-to-pptx>" --outdir /tmp/ref-deck/ 2>&1 | tail -3
```

Notes:
- `--headless` is required (no GUI)
- Output filename may be mangled by hash-prefix from the upload pipeline; check `ls /tmp/ref-deck/` to find the actual file
- LibreOffice on a fresh container may warn "failed to launch javaldx" — that's fine, the PDF still generates
- If the user pastes a `.pdf` directly, skip this step

### Step 2 — Convert .pdf to per-page PNGs

```bash
# -r 100 = ~100 DPI, enough for layout analysis, vision_analyze has a size budget
pdftoppm -r 100 /tmp/ref-deck/<actual-filename>.pdf /tmp/ref-deck/p -png
ls /tmp/ref-deck/ | head -10
```

Output: `p-01.png`, `p-02.png`, ..., `p-32.png` (one per slide). 100 DPI gives ~1000-1500px wide images, which is the sweet spot for vision_analyze.

### Step 3 — vision_analyze 4-6 representative pages

Pick pages that exercise different parts of the visual language:

| Page type | Why pick it | What to learn |
|---|---|---|
| **Cover (p-01)** | Sets the overall tone | Logo position, cover layout, hero image style, color palette |
| **Contents / TOC (p-02)** | Shows the navigation pattern | Section numbering, divider style, sidebar pattern |
| **A text+image content page (e.g. p-04)** | The most common slide type | Image-vs-text split (50/50? 30/70?), paragraph density, sidebar pattern |
| **A photo-grid page (e.g. p-07 for certificates, p-15 for product gallery)** | Tests how the deck handles many images | Grid pattern (rows x cols, orientation mix), image border/frame style |
| **A team/people page (e.g. p-13)** | Tests the most "human" content | Photo style, card pattern, name+title layout |
| **A closing/contact page (last 1-2 pages)** | Often different style from interior pages | Final-pitch layout, contact card pattern |

For each page, ask vision_analyze the same 5 questions in Chinese (or English — vision is bilingual):

```
1) 主图位置（哪里、多大、占页面多大比例）
2) 文字位置（标题/正文分别在哪里）
3) 字号比例（标题/正文/小字各多大）
4) 边距留白（页面四周留多少、段间距多大）
5) 整体布局描述（左对齐/居中/分栏，固定元素如页眉页脚/Logo 位置）
```

The output of vision_analyze is the **prompt vocabulary** for Phase 1 and Phase 2. Copy the agent's own analysis back into the prompts.

### Step 4 — Build a style spec file

Save a file at `references/user-reference-<slug>.md` (one per reference deck, slug = company name or short id). The file is the **prompt prefix** for every generated page:

```markdown
# Style spec — extracted from <reference-deck-name> on <date>

## Color palette
- Primary: #1a3a6e (navy blue)
- Accent: #a01f2a (red)
- Background: white with light gray world map texture overlay
- Text: dark gray (#333)

## Fixed page elements (every page)
- Top-LEFT: small red square + small navy blue square stacked diagonally
- Top-LEFT (after decoration): section number in light gray, section title in dark navy blue bold
- Under title: thin horizontal RED line extending across the page
- Top-RIGHT: company logo (icon, ~50px square)
- Bottom of page: thin red horizontal line

## Cover (p-01) layout
- Large dark RED diagonal parallelogram color block on LEFT, 50% width × 60% height
- Sharp diagonal cut on its right edge
- White bold company name left-aligned inside the red block
- White subtitle below, smaller
- Thin NAVY BLUE diagonal sliver between red block and right-side image
- Right side: ONE single large photorealistic photo (45% page width)

## Content page layout (left-image-right-text)
- 50/50 horizontal split
- Left: ONE single tall photo (40% page width)
- Right: text (60% page width) — top: red company name as heading, below: gray paragraph
- NO bullet points, NO icons in the main area

## Qualifications / gallery page
- GRID of 8-10 photos, 2 rows
- Top row: 3 landscape photos
- Bottom row: 5 portrait photos
- Each photo: thin gray border
- Caption text below each photo (small, light gray)

## Team page
- 5 columns × 1 row
- Each column: photo (top) + name (middle, navy blue bar, white text) + title (below name) + bio (bottom, white background with navy blue border)
- Photos: red background, formal portrait style

## Style vocabulary for prompts
"official Chinese government-enterprise presentation, navy blue + red accents, white background with light world map texture, fixed page header with red+navy square decoration, red horizontal line under section title, top-right company logo, left-image-right-text 50/50 on content pages, NO neon / NO HUD / NO cyberpunk"
```

This file becomes the **prompt prefix** injected into every Phase 1 cover and Phase 2 batch page. Phase 2 batch generation then becomes mechanical: `{style_prefix} | {per_page_content} | no text overlays, no logo, no watermark`.

## The 5-minute vs 30-minute tradeoff

- **Skipping this recipe and going from memory**: 4 image generations × 2 rounds = 8 generations (~$10-20) + 2 round-trips with the user correcting "比例不对" / "颜色不对" / "页面布局不对". Total time: 30-45 minutes.
- **Running this recipe first**: 1 vision_analyze on each of 4-6 pages (~30s × 5 = 2.5 min) + 1 round of generation = $5-10. Total time: 10-15 minutes. First-try accuracy: 80-90% match.

The recipe pays for itself the first time.

## What if the user provides ONLY a description (no file)?

Use the `references/leadership-deck-style-rules.md` generic rules + ask 2-3 clarifying questions:
- "white + navy + gold" or "white + navy + red"?
- "lots of photos (real) or just text + decoration"?
- "10 pages or 30 pages"?

If the user can't or won't provide a file, the agent has to work from priors — and the priors are wrong 50%+ of the time on Chinese government/leadership decks (variance is huge). Be conservative: generate 2-3 cover candidates for the user to pick from, NOT a 4-page mini deck.

## Real session references

- **2026-06-13 (鲲鹏翼航 v4)**: user uploaded 湖南驰阳介绍.pptx (32 pages). Agent generated 4 covers from generic "leadership style" priors → user said "比例不对" + "需要学习排版". After running the recipe, next 4 covers matched the reference on 6/7 dimensions (color, header pattern, content layout, photo grid, palette, decoration). User said "风格还行" (proceeded).

- **2026-06-12 (鲲鹏翼航 v3)**: NO reference file was used; the user picked style from 3 generated covers. Worked OK because the user had clear style preferences (HUD / 未来感 / 科技). NOT a case where this recipe would have helped — the user wanted novel style, not a reproduction.
