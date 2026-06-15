# Post-process Recipe — Logo Overlay + 16:9 Padding (P11 + P24 fix)

The 30-line PIL script that **fixes two pitfalls in one pass**:
- **P11** — 1536×1024 (3:2) → 1920×1080 (16:9) padding, no letterbox, no stretch
- **P24** — composite the SAME real logo on every page, top-right corner

Use whenever you have:
- 10-16 generated PNGs from `image_generate` (all 1536×1024, 3:2 aspect)
- A real logo file (jpg/png/svg) provided by the user
- A target canvas of 1920×1080 (PPTX 16:9 standard) or 13.333"×7.5"

## Why this is a hard gate, not a nice-to-have

P29 documented that P11 and P24 get re-violated session after session even after being written. The fix is to **make the agent's choice mechanical**: there's no decision to make, just run this script.

## The script (drop-in, copy-paste, modify paths)

```python
#!/usr/bin/env python3
"""post-process.py — pad to 16:9 + overlay real logo on every page.

Run after image_generate produces 1536x1024 PNGs but before python-pptx
stitches the deck. Idempotent — running it twice produces the same output.

Args (modify in-place or wrap in argparse):
  LOGO_PATH: absolute path to the user's real logo file
  INPUT_DIR: where the raw 1536x1024 PNGs live
  OUTPUT_DIR: where the 1920x1080 PNGs should land
  FILE_MAPPING: {raw_filename.png: final_name.png} dict
"""
import os
import sys
from PIL import Image
from PIL.Image import Resampling  # Pillow >= 9.1

# --- Config (override per session) ---
LOGO_PATH = "/home/ubuntu/.hermes/image_cache/img_XXXXX.jpg"  # user's logo
INPUT_DIR = "/home/ubuntu/.hermes/cache/images"               # raw 1536x1024
OUTPUT_DIR = os.path.expanduser("~/deck-output/images-padded")  # 1920x1080

FILE_MAPPING = {
    # "raw_filename.png": "pNN-descriptive-name.png",
    # ...
}

# 16:9 standard for PPTX (13.333"x7.5" @ 144 DPI = 1920x1080)
TARGET_W = 1920
TARGET_H = 1080

# Logo target height = ~6.6% of canvas height (visually right, not dominating)
LOGO_H = 72   # 1080 * 0.066

# Logo margin from top-right corner
MARGIN_RIGHT = 40
MARGIN_TOP = 40


def process_image(input_path: str, output_path: str, logo: Image.Image):
    """Pad to 16:9 + paste logo top-right. Idempotent."""
    base = Image.open(input_path).convert("RGBA")
    if base.size != (TARGET_W, TARGET_H):
        # Step 1: create white 16:9 canvas, paste original centered
        canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (255, 255, 255, 255))
        x_off = (TARGET_W - base.size[0]) // 2
        y_off = (TARGET_H - base.size[1]) // 2
        canvas.paste(base, (x_off, y_off), base)
    else:
        canvas = base

    # Step 2: resize logo to LOGO_H height, preserve aspect
    logo_w = int(LOGO_H * (logo.size[0] / logo.size[1]))
    logo_resized = logo.resize((logo_w, LOGO_H), Resampling.LANCZOS)

    # Step 3: paste top-right with margin
    paste_x = TARGET_W - logo_w - MARGIN_RIGHT
    paste_y = MARGIN_TOP
    canvas.paste(logo_resized, (paste_x, paste_y), logo_resized)

    # Step 4: save (optimize=False! Pillow PNG optimize hangs at >5MB files)
    canvas.convert("RGB").save(output_path, "PNG", optimize=False)
    return canvas.size


def main():
    if not os.path.exists(LOGO_PATH):
        sys.exit(f"❌ Logo not found: {LOGO_PATH}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    logo = Image.open(LOGO_PATH).convert("RGBA")
    print(f"✅ Logo: {logo.size} → resize to {LOGO_H}px height")

    for input_name, output_name in FILE_MAPPING.items():
        input_path = os.path.join(INPUT_DIR, input_name)
        output_path = os.path.join(OUTPUT_DIR, output_name)
        if not os.path.exists(input_path):
            print(f"⚠️  Skip (not found): {input_name}")
            continue
        size = process_image(input_path, output_path, logo)
        print(f"✅ {output_name}: {size[0]}x{size[1]}, {os.path.getsize(output_path) // 1024}KB")


if __name__ == "__main__":
    main()
```

## The 4-step workflow

1. **Generate** the 10-16 page PNGs with `image_generate`. **DO NOT mention the logo in the prompt** (P24 Pattern A: silent) or use a negative-instruction (P24 Pattern B: "no shapes, no icons, no logos, no squares"). Do **NOT** use P24 Pattern C's anti-pattern ("empty placeholder square" — AI will draw it).
2. **Verify** each PNG with `identify <file>` (ImageMagick) or `python3 -c "from PIL import Image; print(Image.open('<file>').size)"` — confirm 1536×1024 (or whatever the model actually returns). If 1920×1080 already, skip step 1 of the script.
3. **Run** this script. It does the padding + logo overlay in one pass per file. 10-16 files × ~0.5s = ~10 seconds total.
4. **Verify** the output: `python3 -c "from PIL import Image; print(Image.open('<output>').size)"` should print `1920×1080`. Optionally vision_analyze one file with the question "Is there a logo in the top-right corner? Is the canvas fully filled (no black bars)?"

## What this script does NOT do (and why)

- **Does not crop** — cropping loses content at the top/bottom edges (badges, subtitles, watermark). The user expects 16:9 delivery but the source is 3:2; padding with white (or transparent) canvas is the only lossless conversion.
- **Does not stretch** — stretching 1536×1024 to 1920×1080 = 1.25x horizontal × 1.05x vertical = noticeable UI distortion, especially in people / building / certificate photos.
- **Does not letterbox to black** — letterboxing on a white-background deck looks like "the image didn't load." Letterboxing to the page's own background color is acceptable, but the leadership palette is white so white padding is correct.
- **Does not handle transparency** — the AI-generated images are RGB with no alpha, so the paste doesn't need an alpha mask. If your AI endpoint returns RGBA, add `if base.mode == "RGBA": base = base.convert("RGB")` before step 1.

## Common gotchas

- **Pillow `optimize=True` hangs at >5MB files** (P11 + ai-ppt-image-generation Pitfall 1). This script uses `optimize=False` explicitly.
- **`Image.LANCZOS` raises AttributeError in Pillow >= 10.0** — use `Resampling.LANCZOS` (imported at top of script). Both are present in Pillow 9.x; 10.x removed the direct module-level constants.
- **The 1920×1080 final size is for PPTX 16:9 standard.** If the deck is PDF-only or non-16:9, change `TARGET_W` and `TARGET_H`. The padding logic is the same.
- **Logo position** is hard-coded to top-right with 40px margins. If the user's brand guideline says "logo top-left" or "logo bottom-right" or "no logo on cover, logo on interior pages only", modify the `paste_x` / `paste_y` calculation. The script does NOT auto-detect brand spec — that's a user input, not a heuristic.

## When to skip this script

- The user's `image_generate` endpoint already returns 1920×1080 (rare but happens with some DALL-E 3 endpoints — verify first, don't assume). Skip the padding step; still run the logo overlay.
- The user does NOT provide a logo file and does NOT want a logo. Skip the entire script; use the raw 1536×1024 PNGs as-is and let python-pptx handle the aspect (it will letterbox, which is acceptable for some styles).
- The user provides an SVG logo. Convert to PNG with `inkscape --export-type=png --export-filename=logo.png logo.svg` or `cairosvg logo.svg -o logo.png` before running the script (PIL doesn't read SVG natively).

## The relationship to `references/python-pptx-stitch-recipe.md`

This recipe handles **the per-PNG image assets** (P11 + P24 in one pass). The python-pptx stitch recipe handles **the slide-level composition** (slide size, text overlays, layout, export to .pptx). Run this recipe first, then run the python-pptx recipe. They are not redundant — different stages of the pipeline.

## Reference session

- **2026-06-13 鲲鹏翼航 v4**: user uploaded 湖南驰阳介绍.pptx as style reference. Agent extracted 5 pages via vision (P23). Generated 4 covers + 3 content pages with prompts that followed P24 Pattern C (anti-pattern — "empty placeholder square"). AI drew a visible box on each page. User caught it. Agent rewrote prompts to P24 Pattern B (negative instruction) + wrote this script. The 4 pages re-generated, script run, vision-verified 4/4 pages have the same logo (not 4 different AI-imitation logos). Total cost of skipping this script: 1 round-trip + 4 wasted image-gen calls. Cost of running it: ~10 seconds. Ratio: 1:60 in favor of running the script every time.
