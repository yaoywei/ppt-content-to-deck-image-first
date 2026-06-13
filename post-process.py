#!/usr/bin/env python3
"""
post-process.py — PIL 脚本: padding + 贴真 logo
输入: AI 生成的 1536x1024 PNG (右上角留空)
输出: 1920x1080 PNG (右上角贴真 logo)

为什么这两步都要做:
- padding 修比例: 1536x1024 是 3:2 不是 16:9, 直接拼 PPTX 会黑边或拉伸 (Pitfall 11)
- 贴真 logo: AI 每次画的 logo 都不一样 (Pitfall 24), 必须用 PIL 贴真图保证 15 张一致
"""
import os
import sys
from PIL import Image
from PIL.Image import Resampling

# 配置
LOGO_PATH = "/home/ubuntu/.hermes/image_cache/img_25564c002d96.jpg"
INPUT_DIR = "/home/ubuntu/.hermes/cache/images"
OUTPUT_DIR = os.path.expanduser("~/ppt-content-to-deck-image-first-build/examples")

# 输出文件名映射 (新生成的图 → examples 里的命名)
FILE_MAPPING = {
    "openai_gpt-image-2-medium_20260613_103339_0e3f64f8.png": "cover-red-diagonal.png",
    "openai_gpt-image-2-medium_20260613_103436_7380dbf6.png": "p02-company-overview.png",
    "openai_gpt-image-2-medium_20260613_103544_e3d9b786.png": "p03-mission-positioning.png",
    "openai_gpt-image-2-medium_20260613_103730_6c77473a.png": "p04-qualifications.png",
}

# 目标画布 16:9 (Pitfall 11 推荐)
TARGET_W = 1920
TARGET_H = 1080

# logo 大小 (占画布高度的 ~6%)
LOGO_H = 72  # 1080 * 0.066 ≈ 72
# logo 边距 (右上角)
MARGIN_RIGHT = 40
MARGIN_TOP = 40


def process_image(input_path: str, output_path: str, logo: Image.Image):
    """padding 1536x1024 -> 1920x1080 (白底扩展) + 贴真 logo 右上角"""
    base = Image.open(input_path).convert("RGBA")
    if base.size != (TARGET_W, TARGET_H):
        # 1. 创建白底 16:9 画布
        canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (255, 255, 255, 255))
        # 2. 把原图居中贴上去
        x_offset = (TARGET_W - base.size[0]) // 2
        y_offset = (TARGET_H - base.size[1]) // 2
        canvas.paste(base, (x_offset, y_offset), base)
    else:
        canvas = base

    # 3. resize logo (按高度等比)
    logo_aspect = logo.size[0] / logo.size[1]
    logo_w = int(LOGO_H * logo_aspect)
    logo_resized = logo.resize((logo_w, LOGO_H), Resampling.LANCZOS)

    # 4. 贴到右上角
    paste_x = TARGET_W - logo_w - MARGIN_RIGHT
    paste_y = MARGIN_TOP
    canvas.paste(logo_resized, (paste_x, paste_y), logo_resized)

    # 5. 保存为 PNG
    canvas.convert("RGB").save(output_path, "PNG", optimize=False)  # Pitfall: optimize=True 会卡
    return canvas.size


def main():
    if not os.path.exists(LOGO_PATH):
        print(f"❌ Logo not found: {LOGO_PATH}")
        sys.exit(1)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    logo = Image.open(LOGO_PATH).convert("RGBA")
    print(f"✅ Logo: {logo.size}, will resize to height={LOGO_H}px")

    for input_name, output_name in FILE_MAPPING.items():
        input_path = os.path.join(INPUT_DIR, input_name)
        output_path = os.path.join(OUTPUT_DIR, output_name)
        if not os.path.exists(input_path):
            print(f"⚠️ Skip (not found): {input_name}")
            continue
        size = process_image(input_path, output_path, logo)
        print(f"✅ {output_name}: {size[0]}x{size[1]}, {os.path.getsize(output_path) // 1024}KB")


if __name__ == "__main__":
    main()
