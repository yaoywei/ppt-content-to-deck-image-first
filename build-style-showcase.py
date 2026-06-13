#!/usr/bin/env python3
"""
build-style-showcase.py
生成 "政府汇报风" 风格展示大页 (1920x1080)
一张图里展示该风格的所有关键元素:
- 配色 (白底+深蓝+红+淡世界地图)
- 固定页眉 (左上红蓝方块+章节编号+标题+红线)
- 右上角统一 logo
- 内容页版式 (左图右文 60/40)
- 资质页版式 (证书墙 2行3+5)
- 使命页版式 (3 段 block)
- 封面特征 (红色斜切色块)
- 英文/中文 tagline
"""
import os
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

# 路径
LOGO_PATH = "/home/ubuntu/.hermes/image_cache/img_25564c002d96.jpg"
P02_PATH = os.path.expanduser("~/ppt-content-to-deck-image-first-build/examples/p02-company-overview.png")
P03_PATH = os.path.expanduser("~/ppt-content-to-deck-image-first-build/examples/p03-mission-positioning.png")
P04_PATH = os.path.expanduser("~/ppt-content-to-deck-image-first-build/examples/p04-qualifications.png")
OUTPUT_PATH = os.path.expanduser("~/ppt-content-to-deck-image-first-build/examples/style-showcase-leadership.png")

# 画布
W, H = 1920, 1080

# 颜色
NAVY = (26, 58, 110)        # 深蓝
RED = (168, 30, 46)         # 政企红
WHITE = (255, 255, 255)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (60, 60, 60)
MID_GRAY = (130, 130, 130)
GOLD = (201, 169, 97)

# 创建画布
canvas = Image.new("RGB", (W, H), WHITE)
draw = ImageDraw.Draw(canvas)

# 字体 (尝试加载中文字体)
def load_font(size, bold=False):
    paths_bold = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    ]
    paths_normal = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for p in (paths_bold if bold else paths_normal):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_h1 = load_font(48, bold=True)
font_h2 = load_font(28, bold=True)
font_label = load_font(20, bold=True)
font_body = load_font(18)
font_small = load_font(16)
font_tagline_en = load_font(32, bold=True)
font_tagline_zh = load_font(22)


# === 1. 背景: 淡世界地图纹理 (浅灰点阵模拟) ===
# 用 1px 浅灰点阵作为装饰
for y in range(0, H, 16):
    for x in range(0, W, 16):
        draw.ellipse((x, y, x+1, y+1), fill=(220, 220, 225))


# === 2. 顶部页眉 (每页固定) ===
# 标题行
HEADER_Y = 50

# 左上: 红蓝方块 (叠放)
draw.rectangle((50, HEADER_Y-15, 50+24, HEADER_Y+9), fill=RED)            # 红方块上
draw.rectangle((80, HEADER_Y-15, 80+24, HEADER_Y+9), fill=NAVY)           # 蓝方块下偏右
# 章节编号 + 标题
draw.text((120, HEADER_Y-15), "01", fill=MID_GRAY, font=font_h2)
draw.text((170, HEADER_Y-15), "政府汇报风格 · 展示", fill=NAVY, font=font_h1)
# 红色细线
draw.rectangle((50, HEADER_Y+50, W-50, HEADER_Y+53), fill=RED)

# 右上角: logo (PIL 贴)
logo = Image.open(LOGO_PATH).convert("RGBA")
logo_h = 60
logo_aspect = logo.size[0] / logo.size[1]
logo_w = int(logo_h * logo_aspect)
logo_resized = logo.resize((logo_w, logo_h), Resampling.LANCZOS)
canvas.paste(logo_resized, (W - logo_w - 40, HEADER_Y-15), logo_resized)


# === 3. 主体内容区 (从 y=130 开始) ===
BODY_TOP = 130

# --- 左侧: 60% 区域 (1100 宽) ---

# A. 红色斜切色块 (封面特征展示) - 放在左上
block_x, block_y = 60, BODY_TOP
block_w, block_h = 480, 180
# 画斜切多边形 (左对齐, 右边斜切)
diagonal = 50  # 斜切偏移
polygon = [
    (block_x, block_y),
    (block_x + block_w - diagonal, block_y),
    (block_x + block_w, block_y + diagonal),
    (block_x + block_w, block_y + block_h),
    (block_x, block_y + block_h),
]
draw.polygon(polygon, fill=RED)
# 标题在斜切块上
draw.text((block_x + 20, block_y + 30), "湖南鲲鹏翼航科技", fill=WHITE, font=font_h2)
draw.text((block_x + 20, block_y + 75), "低空经济整体解决方案提供商", fill=WHITE, font=font_body)
draw.text((block_x + 20, block_y + 120), "国家级高新技术企业", fill=(255, 220, 200), font=font_small)

# 斜切色块右下方标注 "封面特征"
draw.text((block_x + block_w + 15, block_y + block_h - 25), "↑ 封面: 红色斜切色块", fill=MID_GRAY, font=font_small)

# B. 内容页示例 (左图右文 60/40) - 放在斜切块下方
content_x, content_y = 60, BODY_TOP + 220
content_w, content_h = 1080, 320

# 框线
draw.rectangle((content_x, content_y, content_x + content_w, content_y + content_h),
               outline=LIGHT_GRAY, width=2)

# 左 60% 缩略图
thumb_w = int(content_w * 0.6) - 20
thumb_h = content_h - 40
thumb_x = content_x + 10
thumb_y = content_y + 20
# 加载 p02 缩略图
try:
    p02 = Image.open(P02_PATH).convert("RGB")
    p02_resized = p02.resize((thumb_w, thumb_h), Resampling.LANCZOS)
    canvas.paste(p02_resized, (thumb_x, thumb_y))
except Exception as e:
    draw.rectangle((thumb_x, thumb_y, thumb_x + thumb_w, thumb_y + thumb_h), fill=(230, 230, 235))
    draw.text((thumb_x + 20, thumb_y + thumb_h//2), f"p02 缩略图加载失败: {e}", fill=MID_GRAY, font=font_body)

# 右 40% 文字
text_x = thumb_x + thumb_w + 20
text_w = content_w - thumb_w - 50
# 标签: 红色加粗
draw.text((text_x, content_y + 30), "● 内容页: 左图右文 60/40", fill=RED, font=font_label)
draw.text((text_x, content_y + 80), "图片占 60% (无人机/办公/场景)", fill=DARK_GRAY, font=font_body)
draw.text((text_x, content_y + 115), "文字占 40% (3 段 block)", fill=DARK_GRAY, font=font_body)
draw.text((text_x, content_y + 150), "• 红色 label + 灰色正文", fill=DARK_GRAY, font=font_body)
draw.text((text_x, content_y + 180), "• 70px 边距, 5% 留白", fill=DARK_GRAY, font=font_body)

# C. 3 段 block 使命页 - 放在下方
mission_x, mission_y = 60, BODY_TOP + 570
mission_w, mission_h = 1080, 280
draw.rectangle((mission_x, mission_y, mission_x + mission_w, mission_y + mission_h),
               outline=LIGHT_GRAY, width=2)

# 标签
draw.text((mission_x + 20, mission_y + 20), "● 使命定位页: 3 段 block", fill=RED, font=font_label)

# 3 行 block
block_starts = [
    ("核心使命", "搭建全球低空产业生态桥梁，赋能低空经济全球化、智能化、场景化发展"),
    ("愿景目标", "成为全球低空经济领域技术领先、服务卓越、生态完整的核心服务商"),
    ("业务定位", "构建技术研发、场景应用、国际对接三位一体的业务体系"),
]
for i, (label, body) in enumerate(block_starts):
    by = mission_y + 70 + i * 60
    draw.text((mission_x + 30, by), label, fill=RED, font=font_label)
    # 测量 body 宽度
    draw.text((mission_x + 30 + 130, by), body, fill=DARK_GRAY, font=font_body)

# --- 右侧: 40% 区域 (从 x=1180 开始, 宽 680) ---

# D. 证书墙 (P4 缩略图) - 右上
cert_x, cert_y = 1180, BODY_TOP
cert_w, cert_h = 680, 450
draw.rectangle((cert_x, cert_y, cert_x + cert_w, cert_y + cert_h), outline=LIGHT_GRAY, width=2)
# 标签
draw.text((cert_x + 20, cert_y + 15), "● 资质页: 证书墙 (2 行 3+5)", fill=RED, font=font_label)

# 加载 p04 缩略图
try:
    p04 = Image.open(P04_PATH).convert("RGB")
    # 缩放以适应右侧区域
    inner_w = cert_w - 20
    inner_h = cert_h - 60
    p04_resized = p04.resize((inner_w, inner_h), Resampling.LANCZOS)
    canvas.paste(p04_resized, (cert_x + 10, cert_y + 50))
except Exception as e:
    draw.rectangle((cert_x + 10, cert_y + 50, cert_x + cert_w - 10, cert_y + cert_h - 10), fill=(230, 230, 235))
    draw.text((cert_x + 30, cert_y + cert_h//2), f"p04 缩略图加载失败: {e}", fill=MID_GRAY, font=font_body)

# E. 配色 + 字体 + 装饰 列表 (右下)
feat_x, feat_y = 1180, BODY_TOP + 470
feat_w, feat_h = 680, 380
draw.rectangle((feat_x, feat_y, feat_x + feat_w, feat_y + feat_h), outline=LIGHT_GRAY, width=2)
draw.text((feat_x + 20, feat_y + 15), "● 关键设计元素", fill=RED, font=font_label)

# 列出所有元素 + 颜色色块
items = [
    ("白底", WHITE, "主背景"),
    ("深蓝 #1A3A6E", NAVY, "标题/正文/页眉"),
    ("红色 #A81E2E", RED, "斜切块/标签/强调"),
    ("浅灰", LIGHT_GRAY, "分割线/留白"),
    ("金色 #C9A961", GOLD, "点缀 (可选)"),
]
for i, (name, color, desc) in enumerate(items):
    iy = feat_y + 60 + i * 45
    # 色块
    draw.rectangle((feat_x + 30, iy, feat_x + 70, iy + 30), fill=color, outline=DARK_GRAY, width=1)
    draw.text((feat_x + 90, iy + 5), name, fill=DARK_GRAY, font=font_label)
    draw.text((feat_x + 350, iy + 5), desc, fill=MID_GRAY, font=font_body)

# 元素清单
elements = [
    "✓ 固定页眉 (左上章节+标题+红线, 右上 logo)",
    "✓ 60/40 左图右文 (内容页)",
    "✓ 证书墙 2 行 3+5 (资质页)",
    "✓ 3 段 block (使命页)",
    "✓ 红色斜切色块 (封面)",
    "✓ 淡世界地图纹理 (国际化背景)",
    "✓ 真实照片 (不画 AI 风插图)",
    "✓ 15 张图 PIL 贴真 logo (100% 一致)",
]
for i, elem in enumerate(elements):
    ey = feat_y + 60 + len(items) * 45 + i * 28
    draw.text((feat_x + 30, ey), elem, fill=DARK_GRAY, font=font_small)


# === 4. 底部 tagline ===
tagline_y = H - 60
draw.rectangle((0, tagline_y, W, tagline_y + 2), fill=NAVY)
draw.text((50, tagline_y + 12), "Government Enterprise Leadership Style", fill=NAVY, font=font_tagline_en)
draw.text((50, tagline_y + 50), "政企汇报风格 · 适合给领导看 · 白底深蓝红 · 实拍图 · 严肃稳重", fill=MID_GRAY, font=font_tagline_zh)


# === 保存 ===
canvas.save(OUTPUT_PATH, "PNG", optimize=False)
print(f"✅ Saved: {OUTPUT_PATH}")
print(f"   Size: {os.path.getsize(OUTPUT_PATH) // 1024} KB")
print(f"   Dims: {W}x{H}")
