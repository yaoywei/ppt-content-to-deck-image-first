#!/usr/bin/env python3
"""
build-style-showcase-baoyu.py
生成 8 张 baoyu 风格展示大页
- 同样版式: 顶部页眉 + 主体缩略图 + 配色规范 + 元素清单
- 配色按各 baoyu 风格调整
"""
import os
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

LOGO_PATH = "/home/ubuntu/.hermes/image_cache/img_25564c002d96.jpg"
OUTPUT_DIR = os.path.expanduser("~/ppt-content-to-deck-image-first-build/examples")
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1920, 1080

# 8 个 baoyu 风格的配色 + 元数据
STYLES = [
    {
        "name": "cyberpunk-neon",
        "title_zh": "赛博朋克霓虹",
        "title_en": "Cyberpunk Neon",
        "ai_path": "/home/ubuntu/.hermes/cache/images/openai_gpt-image-2-medium_20260613_123215_a10ed495.png",
        "bg": (10, 14, 26),
        "accent": (0, 217, 255),
        "text": (220, 235, 255),
        "label": (140, 160, 190),
        "items": [
            ("深蓝黑 #0A0E1A", (10, 14, 26), "主背景"),
            ("电光蓝 #00D9FF", (0, 217, 255), "强调/线条"),
            ("紫红 #FF00C8", (255, 0, 200), "次要高光"),
            ("霓虹绿 #39FF14", (57, 255, 20), "数据/状态"),
            ("冷白 #DCEBFF", (220, 235, 255), "主文字"),
        ],
        "elements": [
            "✓ 深色底 + 高对比荧光",
            "✓ HUD 仪表盘 / 雷达扫描",
            "✓ 线框无人机 / 3D 渲染",
            "✓ 等宽数字字体",
            "✓ 数据流线 / 网格背景",
            "✓ 监控中心 / 指挥调度感",
            "✓ 适合: 科技/无人机/智能制造",
            "✗ 不用: 领导汇报/严肃场合",
        ],
        "tagline_zh": "赛博朋克霓虹 · 适合科技/无人机 · 深底荧光 · 年轻感",
    },
    {
        "name": "corporate-memphis",
        "title_zh": "商务扁平矢量",
        "title_en": "Corporate Memphis",
        "ai_path": "/home/ubuntu/.hermes/cache/images/openai_gpt-image-2-medium_20260613_123308_45c4763c.png",
        "bg": (255, 255, 255),
        "accent": (255, 107, 107),
        "text": (30, 40, 50),
        "label": (120, 130, 140),
        "items": [
            ("白底 #FFFFFF", (255, 255, 255), "主背景"),
            ("珊瑚红 #FF6B6B", (255, 107, 107), "强调/形状"),
            ("芥末黄 #FFD93D", (255, 217, 61), "次要形状"),
            ("深蓝 #2C3E50", (44, 62, 80), "标题/正文"),
            ("中灰 #7F8C8D", (127, 140, 141), "次要文字"),
        ],
        "elements": [
            "✓ 白底 + 丰富多彩有机形状",
            "✓ 扁平矢量插画",
            "✓ 多种肤色人物 (Slack 风)",
            "✓ 圆头粗体字",
            "✓ 简洁留白",
            "✓ 投资人友好",
            "✓ 适合: 商业/科技/路演",
            "✗ 不用: 严肃政企/领导汇报",
        ],
        "tagline_zh": "商务扁平矢量 · 适合路演/科技公司 · 简洁现代",
    },
    {
        "name": "chalkboard",
        "title_zh": "黑板粉笔",
        "title_en": "Chalkboard",
        "ai_path": "/home/ubuntu/.hermes/cache/images/openai_gpt-image-2-medium_20260613_123409_7115fb65.png",
        "bg": (35, 45, 40),
        "accent": (255, 240, 200),
        "text": (240, 240, 240),
        "label": (200, 200, 200),
        "items": [
            ("黑板绿 #232D28", (35, 45, 40), "主背景"),
            ("白色 #F0F0F0", (240, 240, 240), "主文字"),
            ("粉笔黄 #FFF0C8", (255, 240, 200), "强调"),
            ("粉笔蓝 #B8DCE6", (184, 220, 230), "次要"),
            ("粉笔粉 #F5B7B1", (245, 183, 177), "点缀"),
        ],
        "elements": [
            "✓ 黑板底 + 粉笔字",
            "✓ 手绘涂鸦风格",
            "✓ 公式/箭头/星号",
            "✓ 略微凌乱手绘温度",
            "✓ 教师/培训友好",
            "✓ 适合: 教育/培训/科普",
            "✗ 不用: 正式商务/金融",
        ],
        "tagline_zh": "黑板粉笔 · 适合教育/培训 · 手绘温度",
    },
    {
        "name": "aged-academia",
        "title_zh": "复古学术",
        "title_en": "Aged Academia",
        "ai_path": "/home/ubuntu/.hermes/cache/images/openai_gpt-image-2-medium_20260613_123510_8ad50714.png",
        "bg": (240, 225, 195),
        "accent": (90, 55, 30),
        "text": (60, 40, 20),
        "label": (110, 80, 50),
        "items": [
            ("羊皮纸 #F0E1C3", (240, 225, 195), "主背景"),
            ("深褐 #5A371E", (90, 55, 30), "标题/正文"),
            ("棕褐 #8B6F47", (139, 111, 71), "次要文字"),
            ("焦糖 #B8854A", (184, 133, 74), "装饰线"),
            ("墨黑 #1A0E08", (26, 14, 8), "重点强调"),
        ],
        "elements": [
            "✓ 羊皮纸/老纸背景",
            "✓ 棕褐色调 + 暗角",
            "✓ 衬线字体 (serif)",
            "✓ 维多利亚装饰边",
            "✓ 罗马数字 / 古典花纹",
            "✓ 学术/历史感",
            "✓ 适合: 历史/学术/咨询/品牌",
            "✗ 不用: 现代科技/儿童",
        ],
        "tagline_zh": "复古学术 · 适合历史/学术/咨询 · 维多利亚古典",
    },
    {
        "name": "craft-handmade",
        "title_zh": "纸艺手作",
        "title_en": "Craft Handmade",
        "ai_path": "/home/ubuntu/.hermes/cache/images/openai_gpt-image-2-medium_20260613_123652_1d17a59a.png",
        "bg": (250, 240, 220),
        "accent": (220, 100, 100),
        "text": (60, 50, 40),
        "label": (140, 110, 80),
        "items": [
            ("米色 #FAF0DC", (250, 240, 220), "主背景"),
            ("珊瑚粉 #DC6464", (220, 100, 100), "剪纸红"),
            ("芥末黄 #E0B040", (224, 176, 64), "剪纸黄"),
            ("鼠尾草绿 #8FA876", (143, 168, 118), "剪纸绿"),
            ("深褐 #3C2820", (60, 40, 32), "文字/手绘"),
        ],
        "elements": [
            "✓ 米色牛皮纸底",
            "✓ 剪纸字 (像剪贴出来)",
            "✓ 手绘铅笔感",
            "✓ 撕纸边 / 装饰胶带",
            "✓ 折纸小装饰",
            "✓ 温度感 / 老师风格",
            "✓ 适合: 教程/手作/文化",
            "✗ 不用: 正式/科技",
        ],
        "tagline_zh": "纸艺手作 · 适合教程/手作/文化 · 温度感",
    },
    {
        "name": "kawaii",
        "title_zh": "日系可爱",
        "title_en": "Kawaii Cute",
        "ai_path": "/home/ubuntu/.hermes/cache/images/openai_gpt-image-2-medium_20260613_123750_d4ce5f56.png",
        "bg": (255, 228, 236),
        "accent": (255, 150, 170),
        "text": (100, 80, 100),
        "label": (180, 130, 160),
        "items": [
            ("浅粉 #FFE4EC", (255, 228, 236), "主背景"),
            ("珊瑚粉 #FF96AA", (255, 150, 170), "主色/文字"),
            ("薄荷绿 #E0F5E5", (224, 245, 229), "点缀"),
            ("奶黄 #FFF5C8", (255, 245, 200), "点缀"),
            ("淡紫 #C8B6E2", (200, 182, 226), "次要文字"),
        ],
        "elements": [
            "✓ 粉彩马卡龙色调",
            "✓ Q版卡通 + 闪亮大眼",
            "✓ 圆头软体字",
            "✓ 漂浮云朵/星星/爱心",
            "✓ Sanrio / LINE 风",
            "✓ 适合: 母婴/女性/儿童",
            "✗ 不用: 严肃/科技/金融",
        ],
        "tagline_zh": "日系可爱 · 适合母婴/女性/儿童 · 粉彩马卡龙",
    },
    {
        "name": "technical-schematic",
        "title_zh": "工程蓝图",
        "title_en": "Technical Schematic",
        "ai_path": "/home/ubuntu/.hermes/cache/images/openai_gpt-image-2-medium_20260613_123928_8aa6a939.png",
        "bg": (14, 58, 92),
        "accent": (180, 220, 240),
        "text": (240, 250, 255),
        "label": (140, 180, 200),
        "items": [
            ("蓝图蓝 #0E3A5C", (14, 58, 92), "主背景"),
            ("白色 #F0FAFF", (240, 250, 255), "线条/文字"),
            ("青色 #B4DCF0", (180, 220, 240), "次要线条"),
            ("深蓝 #082340", (8, 35, 64), "重线条"),
            ("灰 #8090A0", (128, 144, 160), "标注/批注"),
        ],
        "elements": [
            "✓ 蓝图蓝底 + 白色技术线",
            "✓ 等宽字体 (monospace)",
            "✓ 尺寸标注 / 部件编号",
            "✓ 等距视图 / 剖面图",
            "✓ 工程批注 / 坐标系",
            "✓ 适合: 技术/制造/产品/航空",
            "✗ 不用: 商业/教育/儿童",
        ],
        "tagline_zh": "工程蓝图 · 适合技术/制造/航空 · 等宽字体",
    },
    {
        "name": "pixel-art",
        "title_zh": "像素复古",
        "title_en": "Pixel Art 8-bit",
        "ai_path": "/home/ubuntu/.hermes/cache/images/openai_gpt-image-2-medium_20260613_124033_5f683773.png",
        "bg": (26, 16, 51),
        "accent": (57, 255, 20),
        "text": (240, 240, 240),
        "label": (180, 180, 220),
        "items": [
            ("深紫 #1A1033", (26, 16, 51), "主背景"),
            ("霓虹绿 #39FF14", (57, 255, 20), "像素字/线条"),
            ("电光蓝 #00D9FF", (0, 217, 255), "次要像素"),
            ("品红 #FF00C8", (255, 0, 200), "高光像素"),
            ("纯白 #F0F0F0", (240, 240, 240), "主文字"),
        ],
        "elements": [
            "✓ 深紫底 + 像素字",
            "✓ 8 色调色板 (NES 风)",
            "✓ 块状粗体像素字",
            "✓ 16-bit 风格插画",
            "✓ 像素星星/特效",
            "✓ 适合: 游戏/怀旧/科技",
            "✗ 不用: 正式/商务",
        ],
        "tagline_zh": "像素复古 · 适合游戏/怀旧/科技 · 8-bit 情怀",
    },
]


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


def build_one(style):
    name = style["name"]
    print(f"\n=== Building {name} ===")

    # 判断背景是深色还是浅色 (决定文字颜色)
    bg = style["bg"]
    is_dark = sum(bg[:3]) < 384  # 中等阈值

    canvas = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(canvas)

    # 背景纹理 (按风格选)
    if name in ("cyberpunk-neon", "technical-schematic", "pixel-art"):
        # 网格
        for y in range(0, H, 30):
            line_color = (bg[0]+15, bg[1]+15, bg[2]+25) if name == "cyberpunk-neon" else (bg[0]+15, bg[1]+15, bg[2]+20)
            draw.line((0, y, W, y), fill=line_color, width=1)
        for x in range(0, W, 30):
            draw.line((x, 0, x, H), fill=line_color, width=1)
    elif name == "aged-academia":
        # 羊皮纸颗粒
        for y in range(0, H, 8):
            for x in range(0, W, 8):
                shade_var = ((x * 17 + y * 31) % 20) - 10
                dot_color = (
                    max(0, min(255, bg[0] + shade_var)),
                    max(0, min(255, bg[1] + shade_var)),
                    max(0, min(255, bg[2] + shade_var))
                )
                draw.ellipse((x, y, x+1, y+1), fill=dot_color)
    elif name == "craft-handmade":
        # 牛皮纸纹
        for y in range(0, H, 12):
            for x in range(0, W, 12):
                shade_var = ((x * 13 + y * 23) % 15) - 7
                dot_color = (
                    max(0, min(255, bg[0] + shade_var)),
                    max(0, min(255, bg[1] + shade_var - 3)),
                    max(0, min(255, bg[2] + shade_var - 5))
                )
                draw.ellipse((x, y, x+1, y+1), fill=dot_color)

    font_h1 = load_font(48, bold=True)
    font_h2 = load_font(28, bold=True)
    font_label = load_font(20, bold=True)
    font_body = load_font(18)
    font_small = load_font(16)
    font_tagline_en = load_font(32, bold=True)
    font_tagline_zh = load_font(22)

    # 顶部页眉
    HEADER_Y = 50
    # 风格化方块
    draw.rectangle((50, HEADER_Y-15, 50+24, HEADER_Y+9), fill=style["accent"])
    draw.rectangle((80, HEADER_Y-15, 80+24, HEADER_Y+9), fill=style["text"])
    draw.text((120, HEADER_Y-15), "BAOYU", fill=style["label"], font=font_h2)
    draw.text((220, HEADER_Y-15), f"{style['title_zh']} · {style['title_en']}", fill=style["text"], font=font_h1)
    # 细线
    draw.rectangle((50, HEADER_Y+50, W-50, HEADER_Y+53), fill=style["accent"])

    # 右上角: logo
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo_h = 60
    logo_aspect = logo.size[0] / logo.size[1]
    logo_w = int(logo_h * logo_aspect)
    logo_resized = logo.resize((logo_w, logo_h), Resampling.LANCZOS)
    canvas.paste(logo_resized, (W - logo_w - 40, HEADER_Y-15), logo_resized)

    # 主体内容
    BODY_TOP = 130

    # 左侧 60% - 缩略图
    block_x, block_y = 60, BODY_TOP
    block_w, block_h = 1100, 600
    try:
        ai_img = Image.open(style["ai_path"]).convert("RGB")
        aspect_in = ai_img.size[0] / ai_img.size[1]
        aspect_out = block_w / block_h
        if aspect_in > aspect_out:
            new_w = block_w
            new_h = int(block_w / aspect_in)
        else:
            new_h = block_h
            new_w = int(block_h * aspect_in)
        ai_resized = ai_img.resize((new_w, new_h), Resampling.LANCZOS)
        px = block_x + (block_w - new_w) // 2
        py = block_y + (block_h - new_h) // 2
        canvas.paste(ai_resized, (px, py))
        # 边框
        draw.rectangle((block_x, block_y, block_x + block_w, block_y + block_h),
                       outline=style["label"], width=2)
    except Exception as e:
        print(f"  ⚠️ failed: {e}")

    # 右侧 40% - 配色 + 元素
    feat_x, feat_y = 1180, BODY_TOP
    feat_w, feat_h = 680, 800
    draw.rectangle((feat_x, feat_y, feat_x + feat_w, feat_y + feat_h),
                   outline=style["label"], width=2)
    draw.text((feat_x + 20, feat_y + 15), "● 关键设计元素", fill=style["accent"], font=font_label)

    # 配色
    items = style["items"]
    for i, (name_c, color, desc) in enumerate(items):
        iy = feat_y + 60 + i * 50
        draw.rectangle((feat_x + 30, iy, feat_x + 70, iy + 30), fill=color, outline=style["text"], width=1)
        draw.text((feat_x + 90, iy + 5), name_c, fill=style["text"], font=font_label)
        draw.text((feat_x + 380, iy + 5), desc, fill=style["label"], font=font_body)

    # 元素清单
    elements = style["elements"]
    for i, elem in enumerate(elements):
        ey = feat_y + 60 + len(items) * 50 + i * 32
        if elem.startswith("✓"):
            color = style["accent"]
        else:  # ✗
            color = (200, 100, 100) if not is_dark else (255, 120, 120)
        draw.text((feat_x + 30, ey), elem, fill=color, font=font_small)

    # 底部 tagline
    tagline_y = H - 60
    draw.rectangle((0, tagline_y, W, tagline_y + 2), fill=style["accent"])
    draw.text((50, tagline_y + 12), style["title_en"], fill=style["text"], font=font_tagline_en)
    draw.text((50, tagline_y + 50), style["tagline_zh"], fill=style["label"], font=font_tagline_zh)

    output_path = os.path.join(OUTPUT_DIR, f"style-showcase-{name}.png")
    canvas.save(output_path, "PNG", optimize=False)
    print(f"  ✅ {output_path} ({os.path.getsize(output_path)//1024}KB)")


if __name__ == "__main__":
    for style in STYLES:
        build_one(style)
    print("\nAll done")
