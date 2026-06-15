# Leadership Deck Case Study — 鲲鹏翼航 v4 (2026-06-13)

**Audience**: 领导汇报 (the deck is for senior Chinese government / SOE leadership review)
**Reference PPT used**: 湖南驰阳介绍.pptx (32 pages, real cybersecurity company, not a designed sample)
**Output**: 鲲鹏翼航 v4 (4 sample pages at the time of writing this — full 15-page deck to follow)

## What went RIGHT

1. **Pitfall 21 caught the HUD mismatch early** — user initially said "用 company-deck-c1-hud skill", the agent (correctly) refused to use the HUD style for a leadership audience and pivoted to the generalist skill.
2. **Phase 0 alignment** — agent asked about style, density, and output format before generating. Saved 1 round-trip of "redo it, I don't like it."
3. **Pitfall 13-style autonomy worked** — when user said "出一张新的图, 能看出风格 看出效果的" (a one-shot style probe), agent correctly did 1 image, not 4.
4. **Final 4-page batch (P1-P4) matched the reference on 6/7 dimensions** — red+navy+white-gray palette, red diagonal cover, fixed page header, world map background, 50/50 left-image-right-text, certificate wall. User said "风格还行" and "刚刚的效果我很满意".

## What went WRONG (the 4 violations)

| Violation | Symptom | Cost |
|---|---|---|
| **Pitfall 23 (vision extraction)** | Agent generated 4 cover candidates with `navy + gold + plain white + right-aligned text` because that's the "generic leadership PPT" prior. Reference was actually `navy + red + world map + left-aligned`. User: "比例有些不对" + "我觉得你可能需要学习一下这里面ppt中图片与文字的排版". | 4 wasted image generations (~$5-10) + 1 round-trip + user trust erosion |
| **Pitfall 24 (logo)** | Agent described the user's blue geometric logo in the prompt and let the AI draw it. The result was "in the family" but not the same shape. | Could have shipped a deck with the wrong logo. Fixed by adding the "leave slot empty + overlay in PIL" pattern. |
| **Pitfall 25 (style probe density)** | User said "出 1 张首图 + 3 张内容图". Agent generated 3 content pages with FULL section content (full company description, full mission text, full qualifications list). User: "内容有些拥挤了". | 3 pages need re-generation to lower density. Fix: 1 cover + 2-3 SPARSE content references, not full content. |
| **Pitfall 26 (skill name vs build dir)** | Earlier in the session, agent said "the skill is called company-deck-skill-build" — the BUILD CONTAINER, not the skill. User had to ask "是这个吗" to disambiguate. | Lost ~3 turns of conversation to a name confusion. |

## The reference extraction (湖南驰阳介绍.pptx) — what was ACTUALLY there

Vision_analyze on 5 representative pages revealed:

| Page | Real layout |
|---|---|
| **P1 cover** | 红色斜切色块 (red diagonal block, NOT gold), 大标题 white text left-aligned, 右侧 1 张大图 (not a grid), 顶部红蓝装饰 |
| **P2 contents** | 红色方框"目录/CONTENTS" left + 章节列表 right, 淡世界地图背景 |
| **P4 company** | **左图右文 50/50** (not text-with-corner-image), 顶部 红色细线 + 右上 logo, 章节标题"1.公司简介" |
| **P7 qualifications** | **证书墙 2 行: 上 3 横 + 下 5 竖**, 全部是证书图, 几乎无文字 |
| **P13 team** | **5 列 1 行**, 每列: 照片 + 蓝条姓名职务 + 简介框, 红底人物照, 统一卡格式 |
| **Background** | 淡世界地图纹理 (NOT plain white) |
| **Color palette** | 深蓝 + 红色 + 白灰 (NOT 蓝+金) |
| **Page header (every page)** | 左上: 红蓝小方块 + 章节编号 + 章节标题 + 红色细线; 右上: 公司 Logo |

**The 6 dimensions where the agent's first guess was wrong**: color (gold → red), background (white → world map), cover layout (grid → single hero), content page layout (text+small-image → 50/50 left-image-right-text), photo page (text list → certificate wall), header (none → fixed page header on every page).

## The prompt vocabulary that worked (for Phase 1/2 prompts after extraction)

```
A Chinese company [COVER / CONTENT / QUALIFICATIONS / TEAM] page in 湖南驰阳介绍.pptx style.

[Page-specific instructions here]

Background: white with very subtle light gray world map texture.
Color palette: navy blue (#1a3a6e) + dark red (#a01f2a) + white-gray.
Page header: top-LEFT has a small red square + small navy blue square stacked diagonally,
             then a section number in light gray, then a section title in dark navy blue bold;
             under the title a thin horizontal RED line.
Top-right: a small abstract blue low-poly geometric logo icon (only if AI knows the shape).
NO neon, NO HUD, NO cyberpunk, NO AI-art signature, NO English text.
```

The trick was **naming the reference PPT in the prompt** ("in 湖南驰阳介绍.pptx style") — gpt-image-2 has seen enough Chinese 政企 PPT in its training data to recognize the name as a style signal.

## The 5 sample images that shipped to the GitHub repo

| File | What it shows |
|---|---|
| `examples/cover-red-diagonal.png` | The chosen cover: red diagonal block, large title, single hero photo |
| `examples/p02-company-overview.png` | 公司概况: left-image-right-text 50/50, fixed page header |
| `examples/p03-mission-positioning.png` | 使命定位: 3 stacked label+body blocks, no decoration |
| `examples/p04-qualifications.png` | 资质荣誉: certificate wall 2 rows (3+5) |
| `examples/anti-pattern-blind-guess-blue-gold.png` | The 4 wasted candidates the agent generated FIRST. Kept as a "don't do this" example. |

These are committed in `examples/` of the public GitHub repo so any future visitor to `https://github.com/yaoywei/ppt-content-to-deck-image-first` can see the style WITHOUT installing the skill or paying for image-gen.

## Lessons for next time

1. **Vision-extract before generating**, even if the reference "looks like" what you'd generate. The variance between companies in the same industry is huge.
2. **Density budget is part of style confirmation** — a style probe should be sparse, not stuffed with full content. User's "看一眼" ≠ "build the deck".
3. **Real assets to stitching, AI fills the layout** — the user's logo, headshots, certificates, products go to PIL compositing, not to AI prompts.
4. **Skill name vs build dir** — always read `name:` from SKILL.md frontmatter, never guess from directory.
5. **Ship the skill with sample images** — the repo IS the sales page. Show, don't tell.
