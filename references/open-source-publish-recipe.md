# Open-Source Publish Recipe (README sample images + 公众号 + 公众号配图)

When the user wants to open-source publish the skill repo or write a 公众号 post about it, follow this recipe. Captured from the 2026-06-13 鲲鹏翼航 v5 session (user: yaoywei).

## What this recipe covers

- The 12-style batch generation pattern (which 12 styles to pick, in what order)
- The 2x2 "成品示例图" pattern (the working alternative to the 5-element abstract index card)
- AI image-gen Chinese text bug audit (4 recurring bugs + the vision-check gate)
- Feishu send_message attachment batching (4 images per message cap)
- The README 3-column grid layout that scales from 6 to 16+ sample images

## The 12-style batch (when user says "我需要十几个不同的风格")

12 styles chosen to cover ~90% of business use cases from the 21-style library at `references/style-library.md`. **Order is by visual contrast** (so the 3-column grid in README doesn't have two visually-similar styles next to each other):

| # | Style | Industry | Title (4-card finished example) |
|---|---|---|---|
| 1 | corporate-memphis | 国企/银行/保险 | 银行服务 / 4 大产品线 |
| 2 | blueprint | 工业/制造/能源 | 工业制造 / 4 大流程 |
| 3 | elegant-serif | 高端/奢侈品 | 高定服务 / 4 大尊享 |
| 4 | morandi-journal | 文艺/家居/服饰 | 家居美学 / 4 大风格 |
| 5 | kawaii | 二次元/美妆 | 美妆护肤 / 4 大步骤 |
| 6 | neon-glassmorphism | SaaS/AI/Web3 | AI 助手 / 4 大能力 |
| 7 | dark-mode-dashboard | 数据大屏/运维 | 运维监控 / 4 大指标 |
| 8 | light-mode-clean | 商务/投行/咨询 | 投行业务 / 4 大板块 |
| 9 | gradient-mesh | 互联网/创业 | 创业成长 / 4 大阶段 |
| 10 | bold-graphic | 广告/消费品 | 营销策略 / 4 大引擎 |
| 11 | pop-laboratory | 行业报告/投资分析 | 行业研究 / 4 大维度 |
| 12 | hand-drawn-edu | 培训/SOP/教程 | 新人培训 / 4 大模块 |

When user wants MORE, add in this order (max 18 total — beyond 18 dilutes the gallery):
- retro-pop-grid (复古 70-80年代)
- aged-academia (学术/智库/高校)
- technical-schematic (硬件/技术发布会)
- comic-strip (讲故事/用户旅程)
- claymation (玩具/儿童/食品)

DO NOT add cyberpunk-neon / chinese-ink / watercolor-soft to this 12 — those are covered by the 3 "default" style showcases (one per foundational style family). Mixing the foundational 3 with the 12 doubles up on visual coverage.

## The 2x2 "成品示例图" pattern (the working alternative to the abstract index card)

**Pattern**: each finished example has 4 elements:
1. **Top title bar**: a real-sounding topic (e.g. "银行服务 / 4 大产品线") — NOT just the style name
2. **2x2 card grid**: 4 cards each with `编号 01/02/03/04` + Chinese heading + English subtitle + 2 short Chinese bullets
3. **Bottom bilingual tag**: style audience keywords (e.g. "国企 / 银行 / 央企 / 保险")
4. **Bottom-right end cue**: a one-line English usage line (e.g. "Tech / Pitch / Investor Decks")

**Why this beats the abstract index card**:
- Abstract card (the old 5-element pattern): "style name + palette swatches + element checklist + tagline" → reads as "designer's portfolio", user can't tell what they'd actually produce
- Finished example: "银行服务 / 4 大产品线" with 4 real bank products → user immediately sees "oh this style works for my bank deck"

**Why the abstract card failed in practice** (real session 2026-06-13): user said "这几张效果看起来很low啊" after seeing 3 abstract cards, then "这就好太多了" after seeing the 2x2 finished-example alternative. The 4-card pattern is the unlock.

## The 4 recurring Chinese-text bugs in AI image-gen (mandatory vision-check gate)

Observed in the 2026-06-13 12-image batch — 3 of 12 needed regeneration. The 4 bugs:

1. **Hallucinated similar-looking char**: "次日达" → AI rendered "次良达" (日→良, 1 stroke)
2. **Truncated/condensed compound**: "防光老 防色斑" → AI rendered "防光老 防色斑" when 防晒老 was the right parallel
3. **AI-typical micro-text pattern**: "PA:++++" → AI rendered "PA:++++" with extra colon (convention is "PA++++" no colon)
4. **Wrong-character radical shift**: "复购率" → AI rendered "复曝率" (购→曝, both have 手 radical)

**The fix**:
1. Hard-code every numeric/specific term with the EXACT character string in the prompt. Use the form `Card 4 second bullet must be exactly "复购率 38%" (not "复曝率")`. AI follows this kind of explicit "must be exactly X, not Y" instruction.
2. vision_analyze EVERY card with a "specific character" question for each risky term: "物流卡片的第二行 bullet 是什么？读出'次X达'这个具体的字". This forces vision to commit.
3. In the prompt, list forbidden characters explicitly: "No colon between label and value, no fake period, no extra space".
4. Numbered cards must be EXPLICITLY numbered: do NOT say "numbered badge" — say `"01" or "02" or "03" or "04"`. AI defaults all to "01" if you leave the exact digits ambiguous.

**Cost of skipping the gate**: 25% rework rate observed (3 of 12). Vision-check costs 1-2 seconds per image. ROI is massive.

## Feishu send_message attachment batching (4 images per message cap)

Feishu's per-message media attachment limit is ~4 images. Trying to send N>4 in one `send_message` returns `[2200] internal error` (generic, doesn't tell you why).

**The fix**: K = ceil(N/4) sequential send_message calls, each with ≤4 `MEDIA:/abs/path` lines + caption text. Do not parallelize the K calls. Wait for each `success: true` before sending the next.

For 12 images: 3 sequential send_message × 4 images each. Each call takes 1-2s + image processing time. ~30 seconds end-to-end.

## README 3-column grid layout (the baoyu-inspired pattern)

When the README has 6+ sample images, use a 3-column grid:

```
| | | |
|:---:|:---:|:---:|
| ![img1](examples/img1.png) | ![img2](examples/img2.png) | ![img3](examples/img3.png) |
| **Style 1** | **Style 2** | **Style 3** |
| short-desc | short-desc | short-desc |
```

This pattern:
- Scales from 6 images (2 rows × 3 cols) to 16+ images (6 rows × 3 cols)
- Keeps the README scannable: each cell has 1 image + 3 lines of text
- Matches the baoyu-skills README pattern (which is the reference, not a copy)

**Common mistake**: putting 1 big image + 200 words of description. This is what the OLD 鲲鹏 v4 README did, and it failed the "I can use this" test. Use the grid.

## The PII 脱敏 (de-identification) gate (already in P33, restated for this context)

Before pushing the README + sample images to a public repo, do a full-repo PII grep:
- 真实客户公司名 (real client names from past sessions)
- 真实人物名 (real person names)
- 真实地址/电话 (real addresses/phones)

For the 2026-06-13 push, the audit found:
- README.md: 6 hits (鲲鹏 1, 驰阳 2, 湖南 3)
- SKILL.md: 13 hits (鲲鹏 3, 驰阳 5, 湖南 5)
- examples/real-logo.png: 1 visual PII (鲲鹏真 logo)

Fix: replace with generic labels ("某无人机公司（已脱敏）", "一份真实政企介绍.pptx（已脱敏）", "某地区"), and **delete** the real-logo.png (anonymization is harder for visual PII; deletion is cleaner).

## Quick checklist (use this when the user says "push to GitHub for open-source")

1. ✅ Pick 12 styles from the table above (or N styles user requested)
2. ✅ For each style, generate 1 finished example (2x2 cards) with explicit numbered badges (01/02/03/04)
3. ✅ vision_analyze every card with the "specific character" question for risky terms
4. ✅ Re-generate any image with text bugs (typical: 3 of 12)
5. ✅ Compress to 1280×720 JPEG q=85 (target <300KB per image)
6. ✅ Full-repo PII grep (鲲鹏/驰阳/真 logo). Replace text. Delete visual.
7. ✅ Update README: 3-column grid of all sample images + condensed install/usage
8. ✅ Push to GitHub via Blob API (<5MB files) or Release API (>5MB files)
9. ✅ Verify remote with `curl https://api.github.com/repos/.../contents/<file>` → no PII in rendered output
10. ✅ Send 4 images per `send_message` call, K = ceil(N/4) sequential calls
