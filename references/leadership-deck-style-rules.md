# Leadership / 政企汇报 / 保守风 PPT — Style Rules

When the audience is leadership (领导 / 政企 / 党政 / 国企 / 央企 / 严肃场合), use this style guide INSTEAD of the default 3-style HUD 霓虹 starters. The whole point is to **avoid the "花里胡哨" look** that real leadership audiences reject.

## When to load this file

Load when the user says ANY of:
- "给领导看 / 领导汇报 / 领导检查 / 给 XX 局长看 / 给 XX 主任看"
- "政企 / 国企 / 党政 / 央企 / 央企汇报"
- "正式 / 严肃 / 不要花里胡哨 / 简单 / 干净 / 商务"
- "白底 / 蓝金 / 实拍"
- User provides a reference PPT with: white background, navy + gold, photo grids, official seals, certificate walls (e.g. 湖南驰阳介绍.pptx, 政府工作报告, 央国企简介)

**Do NOT load** for: 路演 / 创业 / 投资人 / 科技公司产品发布 / 二次元 / 消费品 / 营销

## Anti-patterns (do NOT do these for leadership)

| Anti-pattern | Why it's wrong |
|---|---|
| **HUD / 赛博朋克 / 电光蓝霓虹** | 领导看着"像游戏 / 像诈骗 / 像不正经" |
| **深色底 + 高对比荧光** | 投影效果差，领导戴老花镜看高对比度字会累 |
| **3D 渲染图 / 异形元素** | 显得不正式、不稳重 |
| **英文为主 / 中英混排** | 党政场合不专业，IT 服务 / 国企客户排斥 |
| **抽象艺术 / 概念图** | 领导要的是"看到信息"不是"看到艺术" |
| **渐变色背景** | 显得"互联网公司" / "轻浮" |
| **AI-art signature / 隐式水印** | 领导一眼看出是 AI 做的，扣印象分 |
| **emoji / 表情符号** | 任何政府 / 国企汇报材料都不能有 |
| **"全球领先" / "行业第一" / "国家级"** | 广告法红线，见 `china-ad-law-phrases.md` |

## The "leadership-safe" style palette (3 starters)

### Style L1: 白底 + 深蓝 + 金 — 政企经典
- **Background**: white (`#FFFFFF`)
- **Primary**: navy blue (`#1A3A6E`)
- **Accent**: gold (`#C9A961`)
- **Text**: dark gray (`#333333`)
- **Secondary text**: medium gray (`#666666`)
- **Lines / dividers**: thin navy blue 1px
- **Use when**: default for any 政企 / 国企 / 央企 / 政府汇报
- **Aesthetic reference**: 湖南驰阳介绍.pptx, 中信银行年报, 华为企业业务 PPT (NOT the consumer side), 中国移动汇报材料

### Style L2: 白底 + 红色 + 深灰 — 党政汇报
- **Background**: white (`#FFFFFF`)
- **Primary**: Chinese red (`#C8102E` or `#A4243B`)
- **Accent**: dark gray (`#333333`)
- **Secondary**: gold (`#C9A961`) — sparingly
- **Text**: black (`#000000`)
- **Use when**: explicit 党政 audience, 党建汇报, 政府工作汇报
- **Aesthetic reference**: 各级政府工作报告, 国资委汇报材料, 党建 100 周年 PPT
- **WARNING**: red is politically loaded. Don't use red for tech companies (looks "revolutionary"), don't use for foreign companies (culturally off). Default to L1 unless 党政 is explicit.

### Style L3: 白底 + 深绿 + 米色 — 教育 / 医疗 / 公共服务
- **Background**: white (`#FFFFFF`)
- **Primary**: deep green (`#1B5E20` or `#2E7D32`)
- **Accent**: warm beige (`#F5F0E1`)
- **Text**: dark gray (`#333333`)
- **Use when**: 学校 / 医院 / 公共服务 / 事业单位汇报
- **Aesthetic reference**: 大学校庆材料, 三甲医院汇报, 教育局工作汇报

## The 4 most common "page types" in 政企 decks

| Page | Layout | Key elements |
|---|---|---|
| **Cover** | Title left (40% width), photo grid right (55% width, 2x3 or 2x2), 5% margin | Company name BIG (e.g. 36-48pt), 1-line tagline below, 4 资质 tags at bottom (国家高新 / ISO 9001 / 18 分公司 / 服务 200+ 客户) |
| **公司简介** | Title top, 3-column 公司信息 (成立时间 / 总部 / 在职人数 / 资质), 1 hero image (office building) | 真实感办公楼照片 (or 写实渲染 if no real photo), 蓝条 accent 紧贴标题 |
| **资质 / 荣誉** | Title top, certificate wall as 3x3 or 4x3 grid of equal-sized rectangles | 每张图是"奖牌 / 证书 / 牌匾"——AI 渲染的"奖牌"风格要克制 (no 烫金) |
| **团队 / 客户** | Title top, 2x3 photo grid (headshots OR logos) | "team" 页 = 5 领导 portrait + name + title 下方; "客户" 页 = 6x6 logo wall |
| **合作模式 / 联系我们** | 左侧 联系方式, 右侧地图 / 总部大楼图 | 电话、邮箱、地址、官网 — 全是 overlay text, 不能让 AI 生成 |

## Prompt vocabulary (Chinese) for leadership style

When writing the cover-prompt, include these phrases verbatim in the prompt (the model responds to specific Chinese style cues):

- ✅ "official Chinese government-enterprise presentation"
- ✅ "white background" / "predominantly white"
- ✅ "navy blue and gold accents"
- ✅ "professional business style for high-level leadership review"
- ✅ "clean typography" / "clean professional typography"
- ✅ "subtle geometric decorative elements" (lines, dots, NOT shapes)
- ❌ "NO neon" / "NO HUD effects" / "NO cyberpunk" / "NO glowing"
- ❌ "NO AI-art signature" / "NO watermark" / "NO English text"
- ✅ "realistic photograph style" (when generating people / buildings / offices)
- ✅ "subtle navy blue and gold geometric decoration in corners" (NOT center decorations)

## The "5 photos in a grid" cover pattern (the most-tested 政企 layout)

```
+------------------------------------------------------------+
|                                                            |
|   [公司名称 — 36pt navy]            +----+----+            |
|   [副标题 — 16pt gray]              | 办公楼 | 办公区 |    |
|                                      +----+----+            |
|   ─── navy line ───                  | 会议 | 机房  |     |
|                                      +----+----+            |
|   国家高新 · 涉密资质 · 18分公司      | 团队 | 证书  |     |
|   服务数千家党政军机关                 +----+----+            |
|                                                            |
+------------------------------------------------------------+
```

**5 photos in 2x3 grid (right side)**: 办公楼外景 / 办公区 / 会议室 / 机房 / 团队合影 / 证书墙. The 6th slot is left as breathing room OR replaced with a "since 2012" / "98 staff" / "18 branches" stat.

**The "AI rendered vs real photo" problem**: AI-generated 政企 photos will look "uncanny" — people look slightly off, certificates have nonsense text on them, building proportions are wrong. **Mitigation**:
1. Make the prompt emphasize "realistic photograph style, NOT illustration"
2. Generate the cover FIRST, vision-verify, regenerate if any photo looks AI-obvious
3. If the user has real photos, use those instead (the user can drop them in `user-inputs/`)
4. If neither works, **fall back to text + geometric + data callouts** (no people, no buildings) — this is also a perfectly fine 政企 style, and avoids the "uncanny" problem entirely

## Pitfall: "5 photos" costs more than 1

- 1 cover = 1 image_generate call = ~30s
- 1 cover with 5 distinct photo elements = same call, but **higher variance** — the model may merge 2 photos into 1, repeat a face, or omit one entirely
- Budget: 2-3 regenerations to get one good "5 photos" cover. Don't be surprised.
- Alternative: generate the 5 photos SEPARATELY, then compose with Pillow. More control, but more work. Worth it for the "customers' logos" wall where each logo MUST be distinct.

## When the user wants a "more modern" look within leadership bounds

Sometimes "领导汇报" doesn't mean "looks like 2015". The user might want:
- Slightly larger titles
- A small accent color block (orange / teal) for a section, not the whole deck
- A modern sans-serif font (PingFang SC, Source Han Sans) instead of SimSun
- Cleaner data visualizations (single-color bars, NOT rainbow)

The rule: **all the conservative constraints stay, but the EXECUTION can be modern.** White background, navy primary, gold accent, real-data callouts, modern typography, subtle animation in HTML. This is the "Apple" of 政企 decks — modern execution, conservative palette.
