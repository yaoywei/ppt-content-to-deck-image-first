# Style Showcase Page Recipe — 2x2 成品示例图 (FINISHED EXAMPLE, not abstract index)

> **STATUS (2026-06-13)**: This recipe was REVERSED. The old "5-element abstract style index card" pattern (style name + 5 color swatches + 6-item element checklist + bilingual tagline) **fails the "I can use this" test** — user said "这几张效果看起来很low啊". The new pattern is **2x2 finished example page** with REAL content (e.g. "银行服务 / 4 大产品线" with 4 real bank products listed). This file is rewritten to the new pattern. The old recipe is at the bottom of this file marked DEPRECATED for reference only.

## Why this matters at the class level

Any "show me the style" / "give me a sample" task has TWO audiences with different needs:
- **Designer audience**: wants the abstract index card (palette + element checklist) — they understand design systems
- **Business user audience** (the user): wants a FINISHED example with real content — they want to see "what my deck would look like"

Default to the **business user audience** unless explicitly told otherwise. Real user feedback (2026-06-13): "这几张效果看起来很low啊" + "我需要十几个不同的风格" — the user is not asking for a design system, they're asking "can this tool make my deck? show me 10 examples".

## The new pattern: 2x2 finished example page

Each image has exactly 4 elements:

### 1. Top title bar
- A **real-sounding topic** (e.g. "银行服务 / 4 大产品线", "低空经济 / 4 大应用场景", "茶道养生 / 4 时饮茶", "幼儿启蒙 / 4 大能力培养")
- NOT just the style name (e.g. NOT "Corporate Memphis" or "Cyberpunk Neon")
- The topic must look like a real company deck content, not a design system showcase

### 2. 2x2 card grid
4 cards arranged in 2x2, each with:
- **Numbered badge**: explicit "01" or "02" or "03" or "04" in the prompt. AI defaults to "01" for all 4 if you say "numbered"
- **Chinese heading**: 2-4 characters, e.g. "储蓄", "电力巡检", "春茶", "语言表达"
- **English subtitle**: short, e.g. "Savings", "Power Line", "Spring", "Language"
- **2 short Chinese bullets**: real content, not lorem ipsum. e.g. "活期 / 定期 / 大额存单" + "灵活存取 收益稳健"

### 3. Bottom bilingual tag
- Style **audience keywords** (NOT the style name): e.g. "国企 / 银行 / 央企 / 保险", "SaaS / AI / Web3", "茶饮 / 白酒 / 中医药 / 文旅国潮", "教育 / 母婴 / 心理 / 公益"
- The tag answers "which client would use this"

### 4. Bottom-right end cue
- A one-line English usage line: e.g. "Tech / Pitch / Investor Decks", "Banking / SOE", "Tea / Spirits / TCM"
- Anchors the international audience

## The prompt template (copy-paste)

```
Single 1920x1080 high-density information graphic in [STYLE NAME] style.
[STYLE BG DESCRIPTION e.g. clean white #FFFFFF with subtle navy #1E40AF and orange #F97316 accents].
Title at top "[TOPIC]" in [TYPOGRAPHY STYLE].
Four content cards in 2x2 grid with [BORDER STYLE].
Each card: small numbered badge "01" or "02" or "03" or "04", Chinese heading, English subtitle, 2 Chinese bullets.
Card 1 "[BADGE] [HEADING]" / "[ENGLISH]" / "[BULLET 1]" / "[BULLET 2]".
Card 2 "[BADGE] [HEADING]" / "[ENGLISH]" / "[BULLET 1]" / "[BULLET 2]".
Card 3 "[BADGE] [HEADING]" / "[ENGLISH]" / "[BULLET 1]" / "[BULLET 2]".
Card 4 "[BADGE] [HEADING]" / "[ENGLISH]" / "[BULLET 1]" / "[BULLET 2]".
Bottom bar "[AUDIENCE KEYWORDS]".
[Cue line] "[END CUE ENGLISH]".
No fake characters, no decorative micro-text.
```

**Critical**: replace `[BADGE]` with literal "01", "02", "03", "04" — NOT "01-04" or "numbered". AI will not auto-increment.

## Real example prompts (12 styles, 2026-06-13 batch)

See `references/open-source-publish-recipe.md` for the full 12-style table. The pattern:

| Style | BG description |
|---|---|
| corporate-memphis | clean white #FFFFFF with subtle geometric shapes in navy #1E40AF and orange #F97316 |
| blueprint | deep blueprint blue #0F2A5C background with thin white technical grid lines |
| elegant-serif | warm cream #FAF7F2 with subtle gold #B45309 lines and refined serif typography |
| morandi-journal | soft morandi #E8DDD4 background with muted pastel accents |
| kawaii | soft pink #FCE7F3 background with cute cloud and heart decorations |
| neon-glassmorphism | deep purple #312E81 with frosted glass cards and neon pink #831843 accents |
| dark-mode-dashboard | very dark #0A0E1A with neon green/red/yellow dashboard widgets |
| light-mode-clean | clean white with light gray cards and single navy #1F2937 accent |
| gradient-mesh | vibrant gradient blending purple #818CF8, pink #F472B6, yellow #FBBF24 |
| bold-graphic | bold yellow #FACC15 with thick black #000000 borders and red #EF4444 shapes |
| pop-laboratory | white #FFFFFF with bright primary color blocks (blue/green/orange/red) |
| hand-drawn-edu | warm FFFBEB with hand-drawn doodle elements in dark #292524 and accent blue #0284C7 |

## Mandatory vision-check gate (4 Chinese text bugs)

Observed 3 of 12 images in 2026-06-13 batch had to be regenerated. The 4 bugs:

| Bug | Example | Defense |
|---|---|---|
| Similar-looking char | "次日达" → "次良达" (日→良) | vision_analyze with "读出次X达这个具体的字" |
| Truncated compound | "防光老" instead of "防晒老" | Hard-code "must be exactly 防晒老 (not 防光老)" in prompt |
| AI-typical micro-text | "PA:++++" with extra colon | Add "No colon between label and value" in prompt |
| Radical shift | "复曝率" instead of "复购率" | vision_analyze with "读出复X率这个具体的字" |

For every image, vision_analyze with both (a) "逐字读出所有文字" and (b) one specific-character question per risky term. Re-prompt any image with bugs.

## The "abstraction" question (when to use the 5-element abstract card)

The abstract index card (the OLD recipe below) is still useful for ONE specific use case: when the user explicitly says "I want a design system overview" or "I want to understand the design tokens". In that case, use the 5-element pattern.

For all other cases (especially open-source publish, 公众号, README sample images), use the 2x2 finished-example pattern. The user is buying a tool, not studying design theory.

---

## DEPRECATED: the old 5-element abstract style index card (reference only)

The old pattern: 1920x1080 image with style name + 5 color palette swatches + 6-item element checklist + bilingual tagline. Used in earlier 鲲鹏翼航 v4 sessions (commit `c43637d`). User rejected this pattern on 2026-06-13. **Do NOT use this pattern in new work.**

The reasons it's deprecated:
1. Museum-cold (reads as designer's portfolio, not "I can use this")
2. No content proof (shows style elements, not what real content looks like)
3. Doesn't scale (12 styles × 3 minutes/prompt = 36 min, vs 30 min for the 2x2 batch)
4. User explicitly said it "看起来很low啊" and asked for 12 styles to be done as finished examples instead

If you find yourself wanting to use this pattern, ask "would the user look at this and immediately know what their bank deck would look like in this style?" — if the answer is "no, they'd have to imagine", use the 2x2 finished-example pattern instead.
