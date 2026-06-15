# Phase 5: Assemble `.pptx` + Export PDF

The user defines the end-to-end chain upfront: *content → style → batch → assemble .pptx → PDF*. Don't treat assembly as a handoff to a separate skill — own it. This doc is the playbook.

## Stage 1: Stage the PNGs in deck order

Copy the N generated images to a build dir with stable `p1.png ... pN.png` names. A `declare -A` map is the cleanest way when the source filenames are timestamped:

```bash
BUILD=/tmp/ppt-build
mkdir -p "$BUILD"
declare -A MAP=(
  [1]="openai_gpt-image-2-medium_<ts>_p1.png"
  [2]="openai_gpt-image-2-medium_<ts>_p2.png"
  # ...
)
SRC=/home/ubuntu/.hermes/cache/images
for i in $(seq 1 15); do
  cp "$SRC/${MAP[$i]}" "$BUILD/p${i}.png"
done
```

Verify with `ls -la $BUILD` — confirm all 15 files have the right size (each ~1.5-2.2 MB for 1536x1024 GPT-Image-2 output).

**CRITICAL: `image_generate aspect_ratio="landscape"` returns 1536x1024 (3:2), NOT 1920x1080 (16:9).** Run `identify p1.png` before building the .pptx to confirm. If pixels are 1536x1024, you MUST pad to 1920x1080 first (see "Stage 1.5: Pad 1536x1024 to 1920x1080" below). Embedding 3:2 into a 16:9 frame produces visible black bars or vertical stretching — and the user will say "pdf 版看着有些图片比例不太对".

## Stage 1.5: Pad 1536x1024 to 1920x1080 (almost-always needed for GPT-Image-2)

The "landscape" aspect ratio hint in `image_generate` does NOT produce a true 16:9 image. The actual output is 1536x1024 (3:2 = 1.5 ratio), while PowerPoint 16:9 slides need 1.7777 ratio. Three options:

| Option | Action | Trade-off |
|---|---|---|
| ❌ Crop 1536x1024 → 1536x864 | `convert p1.png -crop 1536x864+0+80 +repage p1.png` | **Loses content at top** (e.g. company name badge) and bottom (e.g. URL / English subtitle). The user's first page typically has the brand in a top badge that crops will silently delete. NEVER DO THIS. |
| ❌ Stretch 1536x1024 → 1920x1080 | `convert p1.png -resize 1920x1080 p1.png` | Distorts circles, text proportions, UI elements. Looks "wrong" in a way the user can spot. |
| ✅ Pad with ImageMagick | resize 1620x1080 + add 150px black bars left+right with the page bg color | Preserves 100% content. Result has thin black bars (~7% each side) which is acceptable for dark data-console decks. |

**The working padding recipe** (run for all N images in a loop, then rebuild the deck):

```bash
BUILD=/tmp/ppt-build-v2
mkdir -p "$BUILD"
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
  # 1536x1024 -> resize to 1620x1080 (fits height exactly) -> pad to 1920x1080
  # Use #050810 (the page background color) for the padding so it blends with dark decks
  convert "/tmp/ppt-build/p${i}.png" -resize 1620x1080 \
    -background "#050810" -gravity center -extent 1920x1080 \
    "$BUILD/p${i}.png"
done
identify "$BUILD/p1.png"   # confirm 1920x1080
```

**For light-bg decks** use `#FFFFFF` or a matching neutral color. **For multi-color brand decks**, sample a 1px corner pixel and use that color, or just use `#000000` black bars and tell the user to crop them out in PowerPoint (5 sec/page).

**After padding, do a `vision_analyze` sanity check on P1** to confirm: (a) no content lost, (b) left/right padding is ~7% each side and looks intentional, (c) the page still reads as a coherent slide.

Then point your Stage-2 build script at the padded directory (e.g. `/tmp/ppt-build-v2`).

## Stage 2: Build `.pptx` with `python-pptx`

### The build script (`/tmp/build_pptx.py`)

```python
#!/usr/bin/env python3
"""Build <deck-name>.pptx from N PNG slides (16:9, 1920x1080)."""
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Emu, Pt
from pptx.dml.color import RGBColor

BUILD = Path("/tmp/ppt-build")
OUTPUT_DIR = Path("/tmp/ppt-output")
OUTPUT_DIR.mkdir(exist_ok=True)
WATERMARK = True  # toggle for small "GEN · GPT-Image-2" bottom-right marker

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]        # blank layout — no placeholders

for i in range(1, 16):
    img = BUILD / f"p{i}.png"
    if not img.exists():
        print(f"ERROR: missing {img}", file=sys.stderr); sys.exit(1)
    slide = prs.slides.add_slide(blank)
    slide.shapes.add_picture(str(img), Emu(0), Emu(0),
                              width=prs.slide_width, height=prs.slide_height)
    if WATERMARK:
        tb = slide.shapes.add_textbox(Inches(11.6), Inches(7.15), Inches(1.6), Inches(0.3))
        tf = tb.text_frame
        tf.margin_left = 0
        tf.margin_right = 0
        tf.margin_top = 0
        tf.margin_bottom = 0
        p = tf.paragraphs[0]; p.alignment = 2  # right
        run = p.add_run(); run.text = "GEN · GPT-Image-2"
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(120, 130, 150)
        run.font.name = "Helvetica"

out = OUTPUT_DIR / "鲲鹏翼航公司简介_v1.pptx"
prs.save(str(out))
print(f"OK: {out}  ({out.stat().st_size/1024:.1f} KB,  {len(prs.slides)} slides)")
```

**Expected output size**: ~25-30 MB for 15 slides at 1920x1080 PNG.

## Stage 3: Export PDF with `soffice` (LibreOffice headless)

```bash
cd /tmp/ppt-output
soffice --headless --convert-to pdf "鲲鹏翼航公司简介_v1.pptx"
```

- The output PDF lands in the same dir as the .pptx.
- A `Warning: failed to launch javaldx — java may not function correctly` warning is **harmless** for PDF export. Don't waste time on it.
- PDF size for 15 slides at 1920x1080: ~5 MB.

## Stage 4: Stage in a stable user-visible path

`/tmp/` is volatile — copy to a durable path the user can scp or that survives `/tmp` cleanup:

```bash
mkdir -p ~/kunpeng-ppt-delivery
cp /tmp/ppt-output/*.pptx ~/kunpeng-ppt-delivery/
cp /tmp/ppt-output/*.pdf ~/kunpeng-ppt-delivery/
```

Tell the user the absolute path. Offer the scp one-liner.

## Stage 5: Deliver through the chat channel

- **Feishu** (and most chat platforms) reject files >~25 MB as native attachments. The 鲲鹏翼航 `.pptx` was 26.5 MB — right at the edge. **PDF is the friendlier format for chat delivery** (5 MB, well under any cap).
- Send the PDF via `send_message` with `MEDIA:<absolute-path>` in the message body.
- Always also state the absolute server path so the user can scp the .pptx if they want to edit it.

## Env reality on this machine (and likely similar Ubuntu 24.04 setups)

This is the part that bit me for 3 iterations. **Save the user the same pain**:

| Tool | Path | Why it's confusing |
|------|------|--------------------|
| `python3` (in PATH) | `/home/ubuntu/.hermes/hermes-agent/venv/bin/python3` | Hermes uv-venv, Python 3.11, **no pip**, PEP668-protected |
| `pip` (in PATH) | `/usr/bin/pip` | Resolves to system Python 3.12, not the active venv |
| System Python 3.12 | `/usr/bin/python3` | Where `python-pptx` actually needs to live |
| `soffice` (LibreOffice) | `/usr/bin/soffice` | **Pre-installed**, but `which libreoffice` returns empty (symlink missing) |

**The install path that actually works**:

```bash
# Bootstrap pip in the venv first (since `python -m pip` fails without it)
cd /home/ubuntu/.hermes/hermes-agent
source venv/bin/activate
python -m ensurepip --upgrade
python -m pip install --break-system-packages python-pptx Pillow
```

Or — if you don't want to touch the venv — install into the **system** Python:

```bash
sudo /usr/bin/python3 -m pip install --break-system-packages python-pptx Pillow
# Then invoke the build with: sudo /usr/bin/python3 /tmp/build_pptx.py
```

**Don't**:

- ❌ `apt install libreoffice` (already installed, but the symlink is missing — use `soffice` directly)
- ❌ `pip install python-pptx` (resolves to the wrong Python, fails PEP668)
- ❌ `pip install --user python-pptx` (goes to the wrong site-packages)
- ❌ `which libreoffice` to check installation (returns empty even when present)

## Watermark decision

Default OFF for delivered decks. The user did not request a watermark. If you do add one (for your own tracking during a long session), make it:

- **Tiny** (8pt, light gray `#788296`)
- **Bottom-right** (11.6" left, 7.15" top in 13.333×7.5 deck)
- **Short label** (8-16 chars max — `GEN · GPT-Image-2` is the pattern)
- **Tell the user explicitly** that a watermark is on, and offer a `WATERMARK = False` re-build if they want it off.

## Common pitfalls

### Pitfall A: `python-pptx` (or any pip-installed package) not importable even after "successful install"
- **Symptom**: `ModuleNotFoundError: No module named 'pptx'` (or 'pypdf', 'Pillow', etc.) even though `pip install` returned `Successfully installed python-pptx-X.Y.Z`.
- **Cause**: The package was installed into the **wrong Python**. The active `python3` in the shell is the Hermes uv-venv (Python 3.11) which has NO pip and is PEP668-protected. Bare `pip install` resolves to system Python 3.12, not the venv. Same trap applies to `pypdf` and any other package you `pip install`.
- **Fix A (bootstrap venv)**:
  ```bash
  cd /home/ubuntu/.hermes/hermes-agent
  source venv/bin/activate
  python -m ensurepip --upgrade
  python -m pip install --break-system-packages python-pptx Pillow pypdf
  ```
- **Fix B (install to system Python, run with system Python)**:
  ```bash
  sudo /usr/bin/python3 -m pip install --break-system-packages python-pptx Pillow pypdf
  # Then invoke the build with: sudo /usr/bin/python3 /tmp/build_pptx.py
  ```
- **Detection trick**: After any `pip install`, run BOTH `python -c "import pptx"` AND `/usr/bin/python3 -c "import pptx"` in the same shell. If one works and the other doesn't, you know which interpreter to use. Same applies to pypdf / Pillow / any package.

### Pitfall B: `soffice` produces empty / corrupted PDF
- **Symptom**: PDF is < 100 KB or has blank pages
- **Cause**: Usually a transient lockfile from a previous `soffice` run that didn't clean up.
- **Fix**: `pkill -f soffice` then re-run, or `rm -rf ~/.config/libreoffice/4/user/.~lock*` before re-running.

### Pitfall C: File size blowup
- 15 slides × 2 MB PNGs = 30 MB PPTX. Acceptable. If you scale to 30+ slides, consider:
  - Compressing PNGs with `convert pN.png -quality 85 -resize 1920x pN_small.jpg` (JPEG halves the size)
  - Or assembling at lower DPI
- PDF stays ~5 MB either way (LibreOffice re-compresses on export).

### Pitfall D: Forgetting to stage the .pptx in a durable path
- `/tmp` gets cleared on reboot / session boundary. Always copy to `~/kunpeng-ppt-delivery/` or similar before the user goes offline.
