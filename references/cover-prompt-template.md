# Cover Prompt Template - The 3 Style Blocks

The shared prompt prefix for each of the 3 starter styles. Concatenate the style block + per-page content + global suffix. Keep style block stable across the whole deck (the 14-16 pages in Phase 2 should all share the same style prefix so the visual language is consistent).

## Global suffix (always append)

```
, 16:9, 1920x1080, print-ready, no watermarks, no logos, no fake text, no Chinese characters that aren't verified.
```

The "no fake text" part is critical - AI image models love to insert gibberish Chinese, fake brand names, and hallucinated characters. The negative prompt doesn't fully suppress it, but it helps.

## Style block A: 极简科技蓝 (Minimalist Tech-Blue)

```
Minimalist tech-blue corporate cover slide for a Chinese low-altitude-economy company.
Deep navy blue gradient background (#0A1F3A → #1A3A6B).
Centered abstract geometric drone silhouette in negative space, clean and modern.
A single thin gold line traces a flight path across the slide suggesting global reach.
Lots of negative space, no clutter. Style: Apple keynote meets McKinsey consulting deck.
```

**Per-page variation pattern:** swap "cover slide" for "data dashboard page" / "scenario grid page" / "team portrait page" / "timeline page", keep all the visual descriptors.

## Style block B: 科技国潮金 (Tech Chinese-Gold)

```
Tech meets Chinese national-chic gold corporate cover slide for a low-altitude-economy company.
Deep midnight blue background (#0B1B3F) with subtle gold silk-pattern guilloche texture overlay.
Center: stylized drone icon in metallic gold gradient with wing-spread silhouette.
Below: a horizontal silk-road-inspired gold line traversing the slide from left to right,
connecting small minimalist landmark icons (Chinese pagoda, desert dune, modern skyscraper)
symbolizing global low-altitude reach. Subtle constellation pattern in background
suggesting global flight network. Style: luxury Chinese tech brand, Silk Road meets SpaceX.
Premium, dignified, internationally credible.
```

**Per-page variation pattern:** keep the gold + blue + silk-road motif. For product / data pages, fade the silk-road icon row to a single landmark (e.g. skyscraper for the "城市" page, pagoda for "国际").

## Style block C: 未来数据大屏 (Dark Command-Console)

```
Futuristic dark data-center command console cover slide for a Chinese low-altitude-economy tech company.
Near-black background (#050810) with cyan and electric-blue holographic data streams.
Center: large translucent drone rendered in wireframe with glowing thrusters.
Behind it: a real-time holographic low-altitude airspace radar display showing flight paths,
scanning grid, and data points. Style: Iron Man HUD meets DJI Enterprise dashboard.
High-tech, cool, investor-grade.
```

**Per-page variation pattern:** swap the central element per page - radar for ops pages, data chart for metrics pages, network map for international pages. Keep the wireframe + holographic + cyan/blue visual language.

## Per-page content snippets

For Phase 2 batch generation, here's the per-page content block to append after the style prefix. Adjust the actual content to your brief.

### Page 1: Cover
```
Large bold sans-serif Chinese text "[公司全称]" in white.
English subtitle below: "[公司英文名] · [行业]".
Small tagline at bottom: "[来自内容的slogan]".
```

### Page 2: One-line positioning
```
Centered minimal hero card on the dark/blue background.
Large white text "[公司slogan]" with a thin gold underline.
Below, 3 short bullet words in muted color: "[关键词1] · [关键词2] · [关键词3]".
```

### Page 3: Three key numbers
```
Big number row across the slide. Three columns.
Each column has a huge number (80pt+) in white, with a thin label below.
Left: "[数字1]" (人员)
Middle: "[数字2]" (省份)
Right: "[数字3]" (国家)
```

### Page 4: Business overview (3-pillar)
```
Three-pillar infographic across the slide.
Each pillar is a tall vertical card in the style's accent color.
Pillar 1: "[场景类别1]" with a small icon at the top.
Pillar 2: "[场景类别2]"
Pillar 3: "[场景类别3]"
```

### Page 5-8: Scenario pages (城市/工业)
```
2x2 grid of small scenario cards.
Each card shows a stylized icon (drone + scene) in the style's color.
Top-left card: "[场景1] ([核心指标])".
Top-right card: "[场景2] ([核心指标])".
Bottom-left: "[场景3] ([核心指标])".
Bottom-right: "[场景4] ([核心指标])".
```

### Page 9: International business
```
Globe with thin gold route arcs emanating from China to 3 small landmark icons:
[东南亚 landmark] / [中东 landmark] / [非洲 landmark].
Below the globe, a single line: "深耕中国 联通世界".
```

### Page 10: Training program
```
Classroom or lab visual with subtle drone/tech elements in the background.
Two columns: "无人机驾驶员" (left) and "无人机装调检修工" (right).
Each column has a small icon and a one-line description.
```

### Page 11: Core team
```
5-portrait grid layout. 5 stylized head-and-shoulders silhouettes (no real faces).
Below each silhouette, a small label area for the name and role.
```

### Page 12: Talent structure
```
Donut chart on the left (5 slices), bar chart on the right.
Donut shows headcount breakdown. Bar shows education level.
```

### Page 13: Timeline
```
Horizontal arrow traversing the slide left to right.
5 milestone markers along the arrow, each with a year above and a 2-word description below:
2018 / 2019-20 / 2021-22 / 2023-24 / 2025
```

### Page 14: Contact us
```
Map pin (长沙, China) centered on a clean world map background.
3 small lines at the bottom: address / phone / website.
Style: clean, minimal, professional.
```

## Things to add to the global suffix

If the user said the deck will be printed (not just projected), append: `, optimized for print, no large gradients that consume ink`.

If the user said the deck will be viewed on a small screen (phone preview), append: `, composition readable at 50% scale, no fine detail that disappears when shrunk`.

If the user said the audience is colorblind (rare but possible for accessibility-focused clients), append: `, high contrast, no red-green color pairs, distinguishable in grayscale`.

## Anti-patterns to avoid in the prompts

- "Use Helvetica / PingFang / Microsoft YaHei" - AI doesn't pick fonts, it just generates something font-like
- "Make the company name very large" - the AI will still mangle the characters
- "Use the brand color #FF6B35" - AI does not respect hex codes reliably; describe the color by name
- "Logo in the top-left corner" - AI will hallucinate a fake logo, do NOT ask for one
- "Photo of a real person" - AI will produce an uncanny-valley face. Use silhouettes or iconography instead.
- "Hand-drawn / watercolor / pencil sketch" - some styles are still flaky in 2026 image models; test first
