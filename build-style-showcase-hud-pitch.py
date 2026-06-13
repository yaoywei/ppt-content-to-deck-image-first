#!/usr/bin/env python3
"""
build-style-showcase-hud-pitch.py
生成 HUD 未来数据大屏风 + 路演风 两张风格展示大页
- 同样版式: 顶部页眉 + 主体缩略图 + 配色规范 + 元素清单
- 区别: 配色/装饰/字体按各风格调整
"""
import os
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

LOGO_PATH = "/home/ubuntu/.hermes/image_cache/img_25564c002d96.jpg"
HUD_AI_PATH = "/home/ubuntu/.hermes/cache/images/openai_gpt-image-2-medium_20260613_120231_45f5dcbe.png"
PITCH_AI_PATH = "/home/ubuntu/.hermes/cache/images/openai_gpt-image-2-medium_20260613_120340_350f1ed0.png"

OUTPUT_DIR = os.path.expanduser("~/ppt-content-to-deck-image-first-build/examples")
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1920, 1080

def load_font(size, bold=False):
    paths_bold = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]
    paths_normal = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    ]
    for p in (paths_bold if bold else paths_normal):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


# === HUD 风格 ===
def build_hud():
    DARK_BG = (10, 14, 26)        # 深蓝黑
    CYAN = (0, 217, 255)          # 电光蓝
    PURPLE = (120, 80, 200)       # 紫色高光
    WHITE = (220, 235, 255)       # 偏冷的白色
    DARK_GRAY = (90, 110, 140)
    MID_GRAY = (140, 160, 190)
    LIGHT_LINE = (40, 60, 90)

    canvas = Image.new("RGB", (W, H), DARK_BG)
    draw = ImageDraw.Draw(canvas)

    # 1. 背景: 网格纹理 (cyberpunk grid)
    for y in range(0, H, 30):
        draw.line((0, y, W, y), fill=(25, 35, 55), width=1)
    for x in range(0, W, 30):
        draw.line((x, 0, x, H), fill=(25, 35, 55), width=1)
    # 几个辉光圆 (radar scan)
    for r, alpha_offset in [(200, 1.0), (300, 0.7), (400, 0.5), (500, 0.3)]:
        # 简化为同色同心圆
        draw.ellipse((W//2 - r, H//2 - r, W//2 + r, H//2 + r),
                    outline=(0, 80, 130), width=2)

    font_h1 = load_font(48, bold=True)
    font_h2 = load_font(28, bold=True)
    font_label = load_font(20, bold=True)
    font_body = load_font(18)
    font_small = load_font(16)
    font_tagline_en = load_font(32, bold=True)

    # 2. 顶部页眉
    HEADER_Y = 50
    # 左上: 紫色 + 青色方块 (替代政府风的红蓝)
    draw.rectangle((50, HEADER_Y-15, 50+24, HEADER_Y+9), fill=PURPLE)
    draw.rectangle((80, HEADER_Y-15, 80+24, HEADER_Y+9), fill=CYAN)
    draw.text((120, HEADER_Y-15), "02", fill=MID_GRAY, font=font_h2)
    draw.text((170, HEADER_Y-15), "未来数据大屏 · HUD 风格", fill=CYAN, font=font_h1)
    # 青色细线
    draw.rectangle((50, HEADER_Y+50, W-50, HEADER_Y+53), fill=CYAN)

    # 右上角: logo
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_h = 60
    logo_aspect = logo.size[0] / logo.size[1]
    logo_w = int(logo_h * logo_aspect)
    logo_resized = logo.resize((logo_w, logo_h), Resampling.LANCZOS)
    canvas.paste(logo_resized, (W - logo_w - 40, HEADER_Y-15), logo_resized)

    # 3. 主体内容
    BODY_TOP = 130

    # 左侧 60% - HUD 封面缩略图
    block_x, block_y = 60, BODY_TOP
    block_w, block_h = 1100, 600
    # 加载并 padding HUD AI 图
    try:
        hud_ai = Image.open(HUD_AI_PATH).convert("RGB")
        # 1920x1080 -> 1100x600 (3:2 -> 11:6, 接近)
        aspect_in = hud_ai.size[0] / hud_ai.size[1]
        aspect_out = block_w / block_h
        if aspect_in > aspect_out:
            new_w = block_w
            new_h = int(block_w / aspect_in)
        else:
            new_h = block_h
            new_w = int(block_h * aspect_in)
        hud_resized = hud_ai.resize((new_w, new_h), Resampling.LANCZOS)
        # 居中贴
        px = block_x + (block_w - new_w) // 2
        py = block_y + (block_h - new_h) // 2
        canvas.paste(hud_resized, (px, py))
        # 边框
        draw.rectangle((block_x, block_y, block_x + block_w, block_y + block_h),
                       outline=CYAN, width=2)
    except Exception as e:
        draw.rectangle((block_x, block_y, block_x + block_w, block_y + block_h),
                       outline=(80, 80, 80))
        draw.text((block_x + 30, block_y + 30), f"err: {e}", fill=WHITE, font=font_body)

    # 标注
    draw.text((block_x, block_y + block_h + 15), "↑ 封面: 深色 + 电光蓝霓虹 + HUD 仪表盘 + 线框无人机", fill=CYAN, font=font_label)

    # 4. 右侧 40% - 配色 + 元素清单
    feat_x, feat_y = 1180, BODY_TOP
    feat_w, feat_h = 680, 800
    draw.rectangle((feat_x, feat_y, feat_x + feat_w, feat_y + feat_h),
                   outline=(40, 80, 130), width=2)
    draw.text((feat_x + 20, feat_y + 15), "● 关键设计元素", fill=CYAN, font=font_label)

    items = [
        ("深蓝黑 #0A0E1A", DARK_BG, "主背景"),
        ("电光蓝 #00D9FF", CYAN, "强调/线条/字"),
        ("紫色 #7850C8", PURPLE, "次要高光"),
        ("冷白 #DCEBFF", WHITE, "主文字"),
        ("深灰", (60, 70, 90), "次要文字"),
    ]
    for i, (name, color, desc) in enumerate(items):
        iy = feat_y + 60 + i * 50
        draw.rectangle((feat_x + 30, iy, feat_x + 70, iy + 30), fill=color, outline=CYAN, width=1)
        draw.text((feat_x + 90, iy + 5), name, fill=WHITE, font=font_label)
        draw.text((feat_x + 380, iy + 5), desc, fill=MID_GRAY, font=font_body)

    elements = [
        "✓ 深色底 + 高对比荧光",
        "✓ HUD 仪表盘 / 雷达扫描 / 数字地图",
        "✓ 线框无人机 / 3D 渲染图",
        "✓ 等宽字体 (数字)",
        "✓ 数据流线 / 网格背景",
        "✓ 监控中心 / 指挥调度感",
        "✓ 适合: 无人机/低空/智能制造",
        "✗ 不用: 领导汇报/严肃场合",
    ]
    for i, elem in enumerate(elements):
        ey = feat_y + 60 + len(items) * 50 + i * 32
        color = CYAN if elem.startswith("✓") else (255, 100, 100)
        draw.text((feat_x + 30, ey), elem, fill=color, font=font_small)

    # 5. 底部 tagline
    tagline_y = H - 60
    draw.rectangle((0, tagline_y, W, tagline_y + 2), fill=CYAN)
    draw.text((50, tagline_y + 12), "Cyberpunk HUD Command Center Style", fill=CYAN, font=font_tagline_en)
    draw.text((50, tagline_y + 50), "未来数据大屏风格 · 适合无人机/低空/智能制造 · 深底霓虹 · 年轻感 · 不适合领导", fill=MID_GRAY, font=font_small)

    output_path = os.path.join(OUTPUT_DIR, "style-showcase-hud.png")
    canvas.save(output_path, "PNG", optimize=False)
    print(f"✅ HUD: {output_path} ({os.path.getsize(output_path)//1024}KB)")


# === 路演风格 ===
def build_pitch():
    WHITE = (255, 255, 255)
    NAVY = (10, 37, 64)           # 深蓝
    BRIGHT_BLUE = (33, 150, 243)  # 亮蓝
    LIGHT_BLUE_BG = (245, 250, 255)
    GRAY = (130, 140, 155)
    DARK_GRAY = (60, 70, 80)

    canvas = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(canvas)

    # 1. 背景: 极淡蓝色渐变 (用渐变圆角矩形模拟)
    for y in range(0, H, 4):
        shade = 252 - int(y * 0.005)
        shade = max(245, shade)
        draw.line((0, y, W, y), fill=(shade, shade + 2, 255), width=4)

    font_h1 = load_font(48, bold=True)
    font_h2 = load_font(28, bold=True)
    font_label = load_font(20, bold=True)
    font_body = load_font(18)
    font_small = load_font(16)
    font_tagline_en = load_font(32, bold=True)

    # 2. 顶部页眉
    HEADER_Y = 50
    # 左上: 深蓝 + 亮蓝方块
    draw.rectangle((50, HEADER_Y-15, 50+24, HEADER_Y+9), fill=NAVY)
    draw.rectangle((80, HEADER_Y-15, 80+24, HEADER_Y+9), fill=BRIGHT_BLUE)
    draw.text((120, HEADER_Y-15), "03", fill=GRAY, font=font_h2)
    draw.text((170, HEADER_Y-15), "现代极简科技蓝", fill=NAVY, font=font_h1)
    draw.rectangle((50, HEADER_Y+50, W-50, HEADER_Y+53), fill=BRIGHT_BLUE)

    # 右上角: logo
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_h = 60
    logo_aspect = logo.size[0] / logo.size[1]
    logo_w = int(logo_h * logo_aspect)
    logo_resized = logo.resize((logo_w, logo_h), Resampling.LANCZOS)
    canvas.paste(logo_resized, (W - logo_w - 40, HEADER_Y-15), logo_resized)

    # 3. 主体内容
    BODY_TOP = 130

    # 左侧 60% - 路演封面缩略图
    block_x, block_y = 60, BODY_TOP
    block_w, block_h = 1100, 600
    try:
        pitch_ai = Image.open(PITCH_AI_PATH).convert("RGB")
        aspect_in = pitch_ai.size[0] / pitch_ai.size[1]
        aspect_out = block_w / block_h
        if aspect_in > aspect_out:
            new_w = block_w
            new_h = int(block_w / aspect_in)
        else:
            new_h = block_h
            new_w = int(block_h * aspect_in)
        pitch_resized = pitch_ai.resize((new_w, new_h), Resampling.LANCZOS)
        px = block_x + (block_w - new_w) // 2
        py = block_y + (block_h - new_h) // 2
        canvas.paste(pitch_resized, (px, py))
        draw.rectangle((block_x, block_y, block_x + block_w, block_y + block_h),
                       outline=LIGHT_BLUE_BG, width=2)
    except Exception as e:
        draw.rectangle((block_x, block_y, block_x + block_w, block_y + block_h), outline=GRAY)
        draw.text((block_x + 30, block_y + 30), f"err: {e}", fill=DARK_GRAY, font=font_body)

    draw.text((block_x, block_y + block_h + 15), "↑ 封面: 白底 + 现代极简 + 等距无人机插画 + 数据大字", fill=NAVY, font=font_label)

    # 4. 右侧 40% - 配色 + 元素清单
    feat_x, feat_y = 1180, BODY_TOP
    feat_w, feat_h = 680, 800
    draw.rectangle((feat_x, feat_y, feat_x + feat_w, feat_y + feat_h),
                   outline=LIGHT_BLUE_BG, width=2)
    draw.text((feat_x + 20, feat_y + 15), "● 关键设计元素", fill=BRIGHT_BLUE, font=font_label)

    items = [
        ("白底 #FFFFFF", WHITE, "主背景"),
        ("深蓝 #0A2540", NAVY, "标题/正文"),
        ("亮蓝 #2196F3", BRIGHT_BLUE, "强调/线条"),
        ("淡蓝 #F5FAFF", LIGHT_BLUE_BG, "辅助背景"),
        ("中灰", GRAY, "次要文字"),
    ]
    for i, (name, color, desc) in enumerate(items):
        iy = feat_y + 60 + i * 50
        draw.rectangle((feat_x + 30, iy, feat_x + 70, iy + 30), fill=color, outline=GRAY, width=1)
        draw.text((feat_x + 90, iy + 5), name, fill=DARK_GRAY, font=font_label)
        draw.text((feat_x + 380, iy + 5), desc, fill=GRAY, font=font_body)

    elements = [
        "✓ 白底 + 现代无衬线字体",
        "✓ 等距插画 (isometric)",
        "✓ 大数据字 (98% accuracy)",
        "✓ 几何装饰 (圆/六边形)",
        "✓ 简洁留白",
        "✓ 投资人友好",
        "✓ 适合: 科技公司/创业/路演",
        "✗ 不用: 严肃政企/领导汇报",
    ]
    for i, elem in enumerate(elements):
        ey = feat_y + 60 + len(items) * 50 + i * 32
        color = BRIGHT_BLUE if elem.startswith("✓") else (200, 100, 100)
        draw.text((feat_x + 30, ey), elem, fill=color, font=font_small)

    # 5. 底部 tagline
    tagline_y = H - 60
    draw.rectangle((0, tagline_y, W, tagline_y + 2), fill=NAVY)
    draw.text((50, tagline_y + 12), "Modern Minimalist Tech-Blue Style", fill=NAVY, font=font_tagline_en)
    draw.text((50, tagline_y + 50), "现代极简科技蓝 · 适合路演/科技公司/创业 · 白底极简 · 投资人友好", fill=GRAY, font=font_small)

    output_path = os.path.join(OUTPUT_DIR, "style-showcase-pitch.png")
    canvas.save(output_path, "PNG", optimize=False)
    print(f"✅ Pitch: {output_path} ({os.path.getsize(output_path)//1024}KB)")


if __name__ == "__main__":
    build_hud()
    build_pitch()
    print("Done")
