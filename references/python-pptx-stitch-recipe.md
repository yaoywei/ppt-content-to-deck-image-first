# python-pptx Stitch Recipe - PNG Backgrounds + Text Overlays

The working pattern for combining AI-generated slide images with reliable text overlays. 30 lines, copy-paste, modify per-deck.

## Why this exists

AI image models (gpt-image-2, Flux Pro, etc.) cannot reliably render Chinese text. They hallucinate characters, mix simplified/traditional, and produce fake-looking "Chinese-looking" glyphs. The fix: AI generates the background visual, python-pptx overlays the real text using a system font (which always renders correctly).

## The script

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pathlib import Path

# --- 1. Configure ---
SLIDES_DIR = Path("/tmp/deck_slides")   # where the 14-16 PNGs live
OUTPUT_PPTX = Path("/tmp/output.pptx")
OVERLAYS = {
    # filename -> list of (left, top, width, height, text, font_size, bold)
    "02_positioning.png": [
        (0.5, 5.5, 12.0, 1.0, "搭建全球低空产业生态桥梁", 36, True),
    ],
    "03_numbers.png": [
        (1.0, 2.5, 3.5, 1.5, "100+", 80, True),
        (5.0, 2.5, 3.5, 1.5, "10", 80, True),
        (9.0, 2.5, 3.5, 1.5, "10+", 80, True),
        (1.0, 4.5, 3.5, 0.5, "人员规模", 18, False),
        (5.0, 4.5, 3.5, 0.5, "覆盖省份", 18, False),
        (9.0, 4.5, 3.5, 0.5, "服务国家", 18, False),
    ],
    # ... etc for each slide
}

# --- 2. Build deck ---
prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]  # truly blank layout

for png_path in sorted(SLIDES_DIR.glob("*.png")):
    slide = prs.slides.add_slide(blank_layout)

    # Full-bleed background
    slide.shapes.add_picture(
        str(png_path),
        0, 0,
        width=prs.slide_width,
        height=prs.slide_height,
    )

    # Text overlays
    if png_path.name in OVERLAYS:
        for left, top, width, height, text, size, bold in OVERLAYS[png_path.name]:
            tb = slide.shapes.add_textbox(
                Inches(left), Inches(top), Inches(width), Inches(height)
            )
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = text
            run.font.size = Pt(size)
            run.font.bold = bold
            # Use a Chinese-capable system font. Pick from:
            #   macOS:   "PingFang SC"  (preferred) or "STHeiti"
            #   Linux:   "Noto Sans CJK SC"  or "WenQuanYi Zen Hei"
            #   Windows: "Microsoft YaHei"   or "SimHei"
            run.font.name = "Noto Sans CJK SC"

prs.save(str(OUTPUT_PPTX))
print(f"Saved: {OUTPUT_PPTX}  ({OUTPUT_PPTX.stat().st_size // 1024} KB)")
```

## Font selection - per OS

| OS | Primary font | Fallback |
|---|---|---|
| macOS | `PingFang SC` | `STHeiti` |
| Linux (Debian/Ubuntu) | `Noto Sans CJK SC` | `WenQuanYi Zen Hei` |
| Windows | `Microsoft YaHei` | `SimHei` |

If you do not know the target OS (the file will be opened on someone else's machine), use **`Noto Sans CJK SC`** - it ships with LibreOffice and Google Docs, and Microsoft Office will substitute it cleanly. **Never** use the default `Calibri` - it has no CJK glyphs and PowerPoint will render tofu boxes.

If the target machine is a Chinese Windows without Noto, fall back to `Microsoft YaHei` and provide an alternative font in the slide layout for backwards compat.

## Coordinate convention

All numbers in the OVERLAYS dict are **inches from top-left** of the 16:9 slide (13.333" x 7.5"). This makes eyeballing the layout easy:

- Title usually: top 0.4-0.8", height 0.8-1.2", full width
- Big metric: top 2.0-3.0", height 1.5-2.0"
- Caption / sub-label: below the metric, top 4.0-5.0", height 0.4-0.6"
- Footer (page #, copyright): bottom 7.0", height 0.3"

## Per-slide overlay template (for the standard 14-page company brief)

```python
OVERLAYS = {
    "01_cover.png":           [],   # no overlays on cover
    "02_positioning.png":     [(0.5, 5.5, 12.3, 1.2, "<one-line positioning>", 36, True)],
    "03_numbers.png":         [(1.0, 2.5, 3.5, 1.5, "100+", 80, True),
                               (5.0, 2.5, 3.5, 1.5, "10", 80, True),
                               (9.0, 2.5, 3.5, 1.5, "10+", 80, True),
                               (1.0, 4.5, 3.5, 0.5, "人员", 18, False),
                               (5.0, 4.5, 3.5, 0.5, "省份", 18, False),
                               (9.0, 4.5, 3.5, 0.5, "国家", 18, False)],
    "04_business_overview.png": [
        (0.5, 2.0, 4.0, 4.0, "城市场景", 48, True),
        (4.7, 2.0, 4.0, 4.0, "工业场景", 48, True),
        (8.9, 2.0, 4.0, 4.0, "国际对接", 48, True),
    ],
    # ... fill in the rest
    "14_contact.png": [
        (1.0, 2.5, 11.3, 0.6, "湖南省长沙市芙蓉区车站北路瑞源大厦805", 24, False),
        (1.0, 3.5, 11.3, 0.6, "电话: 18073600813", 24, False),
        (1.0, 4.0, 11.3, 0.6, "官网: www.kunpengyihang.com", 24, False),
    ],
}
```

## Verification (must run before declaring done)

```python
from pptx import Presentation
prs = Presentation(str(OUTPUT_PPTX))
print(f"Slides: {len(prs.slides)}")
for i, s in enumerate(prs.slides, 1):
    n_pics = sum(1 for shp in s.shapes if shp.shape_type == 13)  # PICTURE
    n_text = sum(1 for shp in s.shapes if shp.has_text_frame)
    print(f"  Slide {i}: {n_pics} image(s), {n_text} text box(es)")
```

Expected: 14-16 slides, each with 1 picture and 0-8 text boxes.

## Common bugs

- **Slide is blank in PowerPoint but the script says it added the picture** - usually the picture is added at (0,0) with `width=None` and python-pptx is placing it off-slide. Always pass both `width=` and `height=` (or both `left=` and `top=`).
- **Text appears but in a different font than you set** - PowerPoint is substituting because the named font isn't installed. Embed the font (File > Save Options > Embed fonts) or use a guaranteed-installed fallback.
- **Chinese characters show as tofu boxes** - the font is not CJK-capable. Switch to one of the fonts in the table above.
- **Text wraps unexpectedly** - the textbox is too narrow for the longest line. Increase `width` or add a `tf.word_wrap = False` and use a smaller font size.
- **The PPTX is huge (> 50 MB)** - the source PNGs are too high-res. The image gen tools output 1500-2000px wide which is fine. If you see > 4000px images, downscale with PIL first: `Image.open(p).resize((1920, 1080), Image.LANCZOS).save(p)`.
