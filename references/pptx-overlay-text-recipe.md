# PPTX Overlay-Text Mode — Editable Chinese text on top of AI-generated backgrounds

**When to use this**: the user is shipping the deck to 领导 / 客户 and may need to tweak wording (change company name, fix a phone number, edit a tagline) at the meeting WITHOUT re-rendering the images. This is the default mode for any "领导汇报" / "客户演示" workflow.

**When NOT to use this**: the user said "I just need a final deck, no edits" or "做一个 demo 看看" — then full-bleed mode (one image per slide, all text in the PNG) is fine because they won't edit it. See `post-process-logo-overlay-recipe.md` for the full-bleed case.

## The 2 modes side-by-side

| | Full-bleed (P31 alt) | Overlay-text (P31 default) |
|---|---|---|
| Image role | The whole slide | Background of the slide (full or 60% left) |
| Text role | Baked into the PNG | python-pptx text boxes (editable in PowerPoint) |
| Editability | Locked | Fully editable — click, retype, change font |
| Phase 3 work | `add_picture` only | `add_picture` + `add_textbox` per slide |
| Phase 0 must ask? | No (defaulting is fine) | YES — see the hard-gate line in SKILL.md |
| Cost to build | 1 line per slide | 10-15 lines per slide |
| When user says "改个字" | Re-render whole deck | Just open PowerPoint, retype |
| Best for | One-shot demo, archival, web preview | Live meetings, follow-up emails, follow-up edits |

## The Phase 0 question (HARD GATE per P29/P30)

The agent MUST include this literal line in the Phase 0 confirmation message:

> **文字可编辑模式 (overlay text) 还是 full-bleed 锁定模式？默认 overlay (可编辑)，请回复确认。**

If the user doesn't reply, **default to overlay-text (mode 2) and tell the user you did so**. Never silently default to full-bleed — the cost of re-rendering is too high if they wanted editable.

## Overlay-text mode — Phase 3 implementation

The 30-line script `build-pptx-overlay.py` template (adapt to your page content):

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from PIL import Image
import os

EXAMPLES_DIR = os.path.expanduser("~/path/to/examples")
OUTPUT = os.path.expanduser("~/path/to/deck.pptx")

# Page metadata: (filename, [list of text overlays])
# Each overlay: (left, top, width, height, text, font_size_pt, color_hex, bold)
PAGES = [
    ("cover-red-diagonal.png", []),  # cover has no overlay (image already has all text)
    ("p02-company-overview.png", [
        (0.5, 0.4, 4.5, 0.6, "公司概况", 28, "1A3A6E", True),       # title
        (0.5, 1.2, 4.5, 0.5, "湖南鲲鹏翼航科技有限公司", 18, "A01F2A", True),  # sub
        (0.5, 1.8, 4.5, 3.0, "湖南鲲鹏翼航科技有限公司总部位于湖南长沙...", 12, "333333", False),  # body
    ]),
    ("p03-mission-positioning.png", [
        (0.5, 0.4, 6.0, 0.6, "企业使命与定位", 28, "1A3A6E", True),
        (0.5, 1.5, 6.0, 0.5, "核心使命", 16, "A01F2A", True),
        (0.5, 2.0, 6.0, 0.4, "搭建全球低空产业生态桥梁，赋能...", 12, "333333", False),
        # ... 2 more overlays for 愿景目标 / 业务定位
    ]),
    # ... P4-P15
]

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

for filename, overlays in PAGES:
    slide = prs.slides.add_slide(blank)
    img_path = os.path.join(EXAMPLES_DIR, filename)
    # Step 1: full-bleed image as background
    slide.shapes.add_picture(img_path, 0, 0, width=prs.slide_width, height=prs.slide_height)
    # Step 2: add text boxes on top
    for left, top, width, height, text, size, color, bold in overlays:
        tb = slide.shapes.add_textbox(
            Inches(left), Inches(top), Inches(width), Inches(height)
        )
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor.from_string(color)
        run.font.bold = bold
        # For CJK text on Linux without Microsoft fonts, fall back to:
        # run.font.name = "Noto Sans CJK SC"  # Linux
        # run.font.name = "Microsoft YaHei"   # Windows
        # run.font.name = "PingFang SC"        # macOS

prs.save(OUTPUT)
print(f"Saved: {OUTPUT}, {len(prs.slides)} slides, {os.path.getsize(OUTPUT)/1024/1024:.1f} MB")
```

## Key design decisions

1. **Background image is STILL full-bleed** (1920×1080 covers the whole slide). The overlays sit on top in pre-defined (left, top, width, height) boxes. The image provides the visual chrome (red diagonal block, world map texture, page header); the text boxes provide the editable content.

2. **Coordinate system is Inches(13.333) wide × Inches(7.5) tall** (16:9). All overlay (left, top, width, height) values are in inches. For 1920×1080 background, the mapping is `inch = pixel / 96`. So a 100px-wide text box is `Inches(100/96)` ≈ `Inches(1.04)`.

3. **Font size in Pt**, color in hex RGB. The agent MUST pick a CJK font that exists on the user's system. See the `run.font.name` comment above — Windows 默认 Microsoft YaHei, macOS PingFang SC, Linux Noto Sans CJK SC. If none exist, PowerPoint will fall back to a substitute (often SimSun or a system default) and the look may differ from the AI-generated image.

4. **Text boxes can be empty if the user doesn't want overlay on that page**. The cover (P1) typically has no overlay because the cover image already contains the company name. The qualification page (P4) has overlays for the section title only; the certificate content is in the image.

## Verification before delivery (HARD GATE)

After building the overlay-text .pptx, verify the text is actually editable, not flattened:

```bash
# Unzip the .pptx (it's a zip), look at slide 2's XML
unzip -p deck.pptx ppt/slides/slide2.xml | grep -oE '<a:t>[^<]*</a:t>' | head -5
# Expected: actual text like <a:t>公司概况</a:t>, NOT empty or just image references
```

If the output is empty or shows only `<a:t></a:t>` placeholders, the overlay didn't work — the script silently fell through to full-bleed. Debug by re-checking the `add_textbox` calls.

## The trade-off the user needs to know

Overlay-text mode **mismatches the AI image's typography**. The AI-generated text in the PNG uses the image model's "fake" font, which is often bolder and more decorative than the system font in python-pptx. So:
- **Full-bleed mode**: typography is consistent (all text is the AI's font), but text is locked.
- **Overlay-text mode**: text is editable, but the overlaid text may look slightly different from the surrounding image text (different font, different kerning, different weight).

This is a real trade-off. The Phase 0 question is exactly: "do you want consistent-looking locked text, or editable slightly-mismatched text?" Most users pick editable. But the agent should disclose the trade-off, not hide it.

## When to use the "no-overlay, image as background only" pattern

Sometimes the user wants the image to fill only PART of the slide (e.g. 60% left) and have the right 40% be PURELY text overlays (no image). Use this when:

- The user has a 5-line body of text that needs to be VERY readable
- The image is decorative (a 1-color block, a subtle texture, an abstract shape)
- The user wants to add bullet points later in PowerPoint

Implementation: `add_picture` with `width=Inches(8.0), height=Inches(7.5)` (left 60%), then `add_textbox` for the right 40% with the body content. The right side is pure white background with text — this is essentially the **mck-ppt-design** pattern but with an AI-generated left-side image.
