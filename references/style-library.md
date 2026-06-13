# Style Library — 21 visual styles for image-first PPT generation

Companion to the parent skill's `style-options.md` (which covers 3 starter styles in depth). This file extends the library to 21 styles, each with hex palette + visual references + which-deck-types-it-fits + which-it-doesn't, derived from the baoyu 21-style infographic library + Kunpeng Yihang production experience (2026-06-11).

## How to use this file

In Phase 0 of the parent workflow, when the user says "选个风格" or you need to propose 2-3 candidates:

1. Scan the user's content for keywords → map to a style (see "Keyword → Style" table below)
2. Show 2-3 candidate styles by **name + 1-line description + hex preview**, not the full reference
3. Generate one cover per candidate via `image_generate` and let them pick
4. After they pick, **lock the entire `[Style]` atomic block** (see parent skill's Prompt-as-Code template) — every subsequent page reuses the same palette

## The 21 styles

### 1. cyberpunk-neon
- **Palette**: bg `#050810`, accent `#00D4FF`, accent2 `#1979FF`, text `#FFFFFF`
- **Visual refs**: Iron Man HUD, Blade Runner 2049 UI, 蔚来 ET9 dashboard
- **Fits**: 科技 / 互联网 / AI / 数据 / 无人机 / 智能硬件公司
- **Not for**: 政企汇报（视觉过暗） / 教育（视觉过强）
- **Prompt fragment**: "near-black background #050810, electric cyan #00D4FF accent, secondary electric blue #1979FF, white text, radar scan, concentric rings, scanning line, particle field, HUD-style layout, dark data console aesthetic, glow lines"

### 2. corporate-memphis
- **Palette**: bg `#FFFFFF`, primary `#1E40AF` (商务蓝), accent `#F97316` (强调橙), text `#1F2937`
- **Visual refs**: Microsoft Fluent UI, Slack brand refresh, Stripe blog
- **Fits**: 国企 / 央企 / 政企汇报 / 银行 / 保险 / 律所
- **Not for**: 科技创业公司（视觉过保守） / 游戏（视觉过平）
- **Prompt fragment**: "clean white background #FFFFFF, business blue #1E40AF, accent orange #F97316, dark slate text, flat geometric shapes (circles/triangles/squares), generous whitespace, clear hierarchy, modern sans-serif"

### 3. blueprint
- **Palette**: bg `#0F2A5C` (深蓝), line `#3B82F6` (浅蓝), text `#FFFFFF`, warning `#FCD34D`
- **Visual refs**: 工程制图, NASA technical diagrams, Tesla patent illustrations
- **Fits**: 工业 / 制造 / 工程 / 能源 / 航空航天 / 国防
- **Not for**: 互联网 / 消费品（视觉过硬）
- **Prompt fragment**: "blueprint paper texture background #0F2A5C, light blue #3B82F6 technical lines, white annotations, isometric/orthographic views, grid background, dimensional labels, mechanical / engineering aesthetic, sans-serif technical font"

### 4. technical-schematic
- **Palette**: bg `#FFFFFF`, line `#1F2937`, accent `#DC2626`
- **Visual refs**: Apple technical drawings, Dyson product schematics
- **Fits**: 硬件公司 / 制造业 / 技术发布会
- **Prompt fragment**: "clean white background, dark gray #1F2937 line work, red #DC2626 highlight, exploded views, callout labels, technical schematics"

### 5. minimalist-flat
- **Palette**: bg `#FAFAFA`, text `#111827`, accent `#0EA5E9`
- **Visual refs**: Apple Keynote, Linear, Vercel, Notion
- **Fits**: SaaS / 咨询 / 简洁商务 / 投资人路演
- **Prompt fragment**: "near-white background #FAFAFA, dark text #111827, single accent color #0EA5E9, ultra-clean, generous whitespace, subtle dividers, modern minimal sans-serif"

### 6. elegant-serif
- **Palette**: bg `#FAF7F2` (米白), text `#1C1917` (墨黑), accent `#B45309` (古铜金)
- **Visual refs**: 苹果发布会 (高端版), 万宝龙, 蒂芙尼 catalog
- **Fits**: 高端品牌 / 奢侈品 / 珠宝 / 私人银行 / 艺术品
- **Not for**: 互联网（视觉过暖） / 快消
- **Prompt fragment**: "warm off-white #FAF7F2 background, deep ink #1C1917 text, bronze-gold #B45309 accent, elegant serif typography, generous whitespace, editorial layout, refined and sophisticated"

### 7. bold-graphic
- **Palette**: bg `#FACC15` (黄), text `#000000` (黑), accent `#EF4444` (红)
- **Visual refs**: 麦当劳 (改版后), Spotify Wrapped, Apple Music ads
- **Fits**: 创意 / 广告 / 市场 / 消费品 / 娱乐
- **Prompt fragment**: "bright yellow #FACC15 background, pure black text, red #EF4444 accent, oversized bold typography, graphic poster aesthetic, high contrast, playful"

### 8. watercolor-soft
- **Palette**: bg `#FEF3C7` 渐变到 `#DBEAFE`, text `#374151`, accent `#F472B6`
- **Visual refs**: Airbnb 旧品牌, Headspace, Calm app
- **Fits**: 教育 / 文化 / 公益 / 心理 / 医疗 / 母婴
- **Prompt fragment**: "soft watercolor gradient background #FEF3C7 to #DBEAFE, muted gray #374151 text, soft pink #F472B6 accent, organic shapes, hand-painted feel, gentle typography"

### 9. chinese-ink
- **Palette**: bg `#F5F1E8` (宣纸), ink `#1A1A1A` (墨), accent `#C9302C` (朱砂) / `#D4A574` (金)
- **Visual refs**: 故宫博物院文创, 观复博物馆, 中国国家地理
- **Fits**: 传统文化 / 国潮 / 茶 / 酒 / 中医药 / 文旅
- **Prompt fragment**: "rice-paper texture #F5F1E8 background, deep ink #1A1A1A, vermillion #C9302C accent or aged gold #D4A574, traditional Chinese ink-wash brushstrokes, seal-style accent, calligraphic typography"

### 10. pop-laboratory
- **Palette**: bg `#FFFFFF`, data accent `#3B82F6` / `#10B981` / `#F59E0B` / `#EF4444` (4色)
- **Visual refs**: The Economist, FT, McKinsey reports
- **Fits**: 数据可视化 / 行业报告 / 投资分析 / 学术报告
- **Prompt fragment**: "white background, 4-color data palette #3B82F6 #10B981 #F59E0B #EF4444, clean bar charts / line charts / pie charts, sans-serif, minimal chartjunk, reference to Economist style"

### 11. morandi-journal
- **Palette**: bg `#E8DDD4` (灰粉), text `#4A4A4A`, accent `#A0937D` (灰金)
- **Visual refs**: 无印良品, 江南布衣, IKEA 旧版
- **Fits**: 文艺 / 设计 / 生活美学 / 家居 / 服饰
- **Prompt fragment**: "muted Morandi color palette, dusty pink #E8DDD4 background, soft gray #4A4A4A text, gray-gold #A0937D accent, soft fabric / paper texture, zen layout, Japanese minimalism"

### 12. retro-pop-grid
- **Palette**: bg `#FDE68A` (奶油黄) / `#FCA5A5` (粉), text `#1F2937`, accent `#3730A3` (深紫)
- **Visual refs**: Stranger Things 标题, 70年代瑞士海报
- **Fits**: 复古 / 怀旧 / 70-80年代品牌
- **Prompt fragment**: "retro 70s pop aesthetic, cream yellow #FDE68A and dusty pink #FCA5A5 background, dark slate text, deep purple #3730A3 accent, grid layouts, geometric Bauhaus shapes, vintage typography"

### 13. claymation
- **Palette**: bg `#FEF3C7` (暖), accents 多种饱和色, soft shadows
- **Visual refs**: Aardman (小羊肖恩), 乐高, 黏土动画
- **Fits**: 消费品 / 玩具 / 儿童 / 食品
- **Prompt fragment**: "claymation / clay sculpture aesthetic, warm cream #FEF3C7 background, soft 3D shapes, playful saturated colors, soft shadows, child-friendly"

### 14. kawaii
- **Palette**: bg `#FCE7F3` (粉), text `#831843` (深粉), accent `#FBBF24` (黄)
- **Visual refs**: 三丽鸥 (Hello Kitty), 泡泡玛特
- **Fits**: 二次元 / 女性向 / 美妆 / 萌系 IP
- **Prompt fragment**: "kawaii cute aesthetic, soft pink #FCE7F3 background, deep pink #831843 text, sunshine yellow #FBBF24 accent, rounded shapes, simple cute character mascots, pastel palette"

### 15. aged-academia
- **Palette**: bg `#F5F1E8` (羊皮纸), text `#3F3F3F`, accent `#7C2D12` (深褐)
- **Visual refs**: 牛津大学, 普林斯顿, Harvard Business Review
- **Fits**: 学术 / 研究所 / 智库 / 高校 / 出版
- **Prompt fragment**: "aged parchment / academic paper #F5F1E8 background, deep brown #7C2D12 accent, classic serif typography, scholarly layout, formal reference style"

### 16. neon-glassmorphism
- **Palette**: bg 渐变 `#312E81` (深紫) → `#831843` (深粉), glass cards 半透明白
- **Visual refs**: Stripe Sessions 2023, Linear 2024 rebrand
- **Fits**: SaaS / AI产品 / 现代互联网 / 加密 / Web3
- **Prompt fragment**: "neon glassmorphism aesthetic, dark gradient #312E81 to #831843 background, frosted glass cards with white border, soft glow, vibrant neon highlights, modern SaaS dashboard"

### 17. dark-mode-dashboard
- **Palette**: bg `#0A0E1A`, multi-color data accent (青/紫/粉/黄)
- **Visual refs**: Datadog, Grafana, Vercel Analytics
- **Fits**: 数据大屏 / 监控 / 运维 / 实时数据
- **Prompt fragment**: "near-black #0A0E1A background, multi-color neon data accents (cyan/purple/pink/yellow), real-time data visualization aesthetic, dashboard / monitoring center feel, dense information, monospace font for numbers"

### 18. light-mode-clean
- **Palette**: bg `#FFFFFF`, text `#1F2937`, divider `#E5E7EB`, accent `#3B82F6`
- **Visual refs**: McKinsey decks, BCG reports, Bain consulting
- **Fits**: 经典商务 / 报告 / 季度汇报 / 投行 / 咨询
- **Prompt fragment**: "clean white background, dark slate #1F2937 text, light gray #E5E7EB dividers, single blue #3B82F6 accent, classic business / consulting aesthetic, restrained typography, clear hierarchy"

### 19. gradient-mesh
- **Palette**: 渐变 `#818CF8` (紫) → `#F472B6` (粉) → `#FBBF24` (黄)
- **Visual refs**: Stripe homepage, Linear marketing site
- **Fits**: 现代互联网 / 创业公司 / 产品发布
- **Prompt fragment**: "vibrant gradient mesh background, purple #818CF8 to pink #F472B6 to yellow #FBBF24, soft mesh-like color transitions, modern internet startup aesthetic, clean white cards on top"

### 20. comic-strip
- **Palette**: bg `#FFFFFF` + 多个面板, text `#000000`, accent 黄/红
- **Visual refs**: Marvel 漫画, 新周刊 插图
- **Fits**: 讲故事 / 用户旅程 / 内容创作 / 教育
- **Prompt fragment**: "comic strip aesthetic, multiple panel grid layout, white background, black ink lines, primary color fills, speech bubble style labels, narrative / story-driven layout"

### 21. hand-drawn-edu
- **Palette**: bg `#FFFBEB` (暖白), text `#292524`, accent `#0284C7` (蓝)
- **Visual refs**: Khan Academy, Notion templates, 一周进步
- **Fits**: 培训材料 / SOP / 内部知识库 / 教程
- **Prompt fragment**: "hand-drawn illustration aesthetic, warm off-white #FFFBEB background, dark warm text, sky blue #0284C7 accent, sketchy line work, friendly approachable feel, training material / SOP style"

## Keyword → Style quick lookup

| Content keywords | Recommended style |
|---|---|
| 科技 / 互联网 / AI / 数据 / 无人机 / 智能 | cyberpunk-neon |
| 国企 / 政府 / 央企 / 银行 / 保险 | corporate-memphis |
| 工业 / 制造 / 工程 / 能源 / 航空 | blueprint |
| 高端 / 奢侈品 / 珠宝 / 私人银行 | elegant-serif |
| 茶 / 酒 / 中医药 / 国潮 / 文旅 | chinese-ink |
| 教育 / 文化 / 公益 / 母婴 / 心理 | watercolor-soft |
| 文艺 / 家居 / 服饰 / 美学 | morandi-journal |
| 二次元 / 美妆 / 女性向 | kawaii |
| SaaS / AI产品 / 加密 / Web3 | neon-glassmorphism |
| 数据大屏 / 监控 / 运维 | dark-mode-dashboard |
| 商务 / 咨询 / 投行 / 季度汇报 | light-mode-clean |
| 互联网 / 创业 / 产品发布 | gradient-mesh |
| 玩具 / 儿童 / 食品 | claymation |
| 广告 / 市场 / 消费品 | bold-graphic |
| 学术 / 智库 / 高校 | aged-academia |
| 培训 / SOP / 教程 | hand-drawn-edu |
| 讲故事 / 用户旅程 | comic-strip |
| 行业报告 / 投资分析 | pop-laboratory |
| 复古 / 70-80年代 | retro-pop-grid |
| 硬件 / 技术发布会 | technical-schematic |
| (default fallback) | minimalist-flat |

## How to apply a chosen style

Once the user picks a style:

1. **Lock the hex palette** in your working memory / scratchpad
2. **Lock the prompt fragment** — copy it verbatim into every subsequent page's prompt
3. **Reuse verbatim** for ALL 14-16 pages. Paraphrasing the prompt fragment = style drift.
4. **Vision-verify the first cover** before batching (Phase 3 of the parent workflow). If the style drifted, fix the prompt fragment and re-probe — do not proceed with 15 off-style pages.

## Anti-patterns

- **Mixing two styles' palettes in one deck.** Pick one, stick to it. The user will say "颜色怎么每页不一样" if you drift.
- **Using "minimalist-flat" as a fallback for everything.** It's the least distinctive — for a real "wow" the user needs `cyberpunk-neon` or `gradient-mesh`. Only use minimalist-flat when the user explicitly says "低调点" / "商务一点" / "保守一点".
- **Forcing `chinese-ink` on a tech company.** Style has to match content mood. Tech ≠ ink.
- **Skipping the style probe.** Generating 15 pages in a default style and hoping the user likes it is the #1 rework generator. Always do the 3-cover probe + user pick loop.
