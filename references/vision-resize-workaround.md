# vision_analyze Resize Workaround

## The trap

When you batch 15 GPT-Image-2 outputs through `vision_analyze` for CJK QA, you will hit a 6/12 failure rate on the fresh PNGs. The error is consistent and confusing:

```
Error code: 400 - {'error': {'message': "Failed to deserialize the JSON body into the target type:
messages[0]: unknown variant `image_url`, expected `text` at line 1 column 2553757",
'type': 'invalid_request_error'}}
```

The model rejects the image with what looks like a schema deserialization error — but the root cause is the **image size**, not the schema. GPT-Image-2 outputs are 1536x1024 PNG, which is 1-2MB. Some go over the vision model's payload limit, triggering this opaque error.

## The fix (one-liner)

```bash
mkdir -p /tmp/qa_resized
for f in openai_gpt-image-2-medium_*.png; do
  convert "$f" -resize 1280x -quality 85 "/tmp/qa_resized/${f%.png}_small.jpg"
done
```

Then call `vision_analyze` on the `_small.jpg` versions, not the original PNGs.

## Verified results

- 6 images that returned HTTP 400 on the original PNGs: all 6 passed on the 1280x JPEG versions.
- 6 images that worked on the original PNGs: also still worked on the JPEG versions (no regression).
- CJK text readability: unaffected by the resize — the model still picks up the same characters.

## When this workaround is NOT enough

- If the resized image is still rejected (rare): the image may be corrupted. Re-download or regenerate.
- If `vision_analyze` returns a balance error (HTTP 403 / "Insufficient account balance"): resize will not help. Fall back to user manual verification, and surface this explicitly to the user — do not silently skip QA.

## Pattern to embed in QA workflows

```python
import os
import subprocess
from pathlib import Path

CACHE = Path("/home/ubuntu/.hermes/cache/images")
OUT = Path("/tmp/qa_resized")
OUT.mkdir(exist_ok=True)

for png in CACHE.glob("openai_gpt-image-2-medium_*.png"):
    jpg = OUT / f"{png.stem}_small.jpg"
    if not jpg.exists():
        subprocess.run(["convert", str(png), "-resize", "1280x", "-quality", "85", str(jpg)], check=True)
    # then vision_analyze on the jpg path
```

## Original error transcript (from session 20260611_220400)

```json
{
  "success": false,
  "error": "Error analyzing image: Error code: 400 - {'error': {'message': 'Failed to deserialize the JSON body into the target type: messages[0]: unknown variant `image_url`, expected `text` at line 1 column 2553757', 'type': 'invalid_request_error'}}"
}
```

This appeared on 6 of 12 pages, all the larger ones (>1.5MB). The smaller pages (<1.2MB) went through. Resize is the deterministic fix.
