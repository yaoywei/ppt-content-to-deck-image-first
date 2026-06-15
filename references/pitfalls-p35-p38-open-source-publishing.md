# Pitfalls P35–P38: Open-source Publishing Workflow

Companion to parent SKILL.md (which already has P1–P34 + 4-stall 演示流程).
This file captures the 4 pitfalls that emerged from the 2026-06-13 鲲鹏翼航 v4→v5 + 16-style gallery push: reconcile-before-push, baoyu-style成品示例, vision-verify replacement files, README+公众号 dual-audience design.

---

## Pitfall 35: Before pushing to GitHub, **reconcile README references vs files actually being uploaded** — every image path in the README must have a corresponding blob in the same commit

- **Symptom (observed 2026-06-13)**: agent rewrote README with 18 image references (`cover-red-diagonal.png` + `p02` + `p03` + 12 new `style-*-4xxx.jpg` + 1 leadership P4 + 1 anti-pattern). The commit only uploaded 12 new style images + the new README. **The earlier-generated high-density examples (cyberpunk/chinese-ink/watercolor-soft) were referenced in README but never blob-uploaded in this commit** — they had been uploaded in a previous commit (b9a99c288c) which actually never happened; the user saw broken-image icons in GitHub for those 3 cells.
- **Why this is a class-level pitfall, not a one-off**: any time the agent refactors README images (renames, additions, deletions) it must **enumerate which files are being touched** in the push plan, and verify each path resolves to a blob in the new commit. A "the images are already on the remote" assumption is fragile because (a) prior commits may have been force-pushed away, (b) the agent may have intended to upload something and forgotten, (c) file renames silently break old references.
- **The fix — reconcile before `git push` (or the GitHub API equivalent), 4 steps**:
  1. **Parse README** to extract every `examples/<file>` reference into a set. Run a 1-liner: `grep -oE 'examples/[A-Za-z0-9._-]+\.(jpg|png)' README.md | sort -u`.
  2. **Enumerate the files actually being uploaded** in the push plan (the new blob list, or `git status` before push). Build a set.
  3. **Diff the two sets**: any reference in README but NOT in upload set = broken image after push. Any file in upload set but NOT referenced = wasted bytes. Fix BEFORE pushing.
  4. **After push, verify remotely**: `curl -sS -m 20 "https://api.github.com/repos/<owner>/<repo>/contents/examples" | python3 -c "import json,sys; d=json.load(sys.stdin); print('\n'.join(x['name'] for x in d))"` returns the actual file list. Diff against README references again. **0 missing** is the bar.
- **Hard gate (per P29/P30)**: before issuing the commit, run the diff. If non-empty missing-list, refuse to push. This is a 10-second check that prevents 5-15 minutes of "user reports broken image → re-investigate → re-push" loop.
- **What NOT to do**:
  - "I already pushed them in a previous commit" — verified-by-curiosity, not by `curl`. Public repos don't need a token for the contents API; use it.
  - "The commit message says I uploaded 12 files" — message ≠ reality. The API says what's real.
  - "Let me just push and check" — pushes broken state to the public README. Customers see `![alt](https://...)` rendering as a broken icon, which is worse than 0 sample images.
- **Real session 2026-06-13** (16-style showcase gallery): 18 references in README, only 12 in upload set → user saw 3 broken-image icons on GitHub → 1 round-trip + 1 extra commit. Fix cost: a `grep + diff` that took 8 seconds. The lesson: **never push README image references without verifying the upload set matches**.

---

## Pitfall 36: For "成品示例图" / style-showcase / GitHub README sample images, the right shape is **one full content page per image** (baoyu-style) — NOT an abstract "style index card" with color swatches and label words

- **Symptom (observed 2026-06-13)**: agent first generated 3 "style index cards" (cyberpunk-neon / chinese-ink / watercolor-soft) where each image was: a thumbnail of one cover + 5 color swatches with hex codes + 6 style-element checklist items + bilingual tagline. The agent called these "成品示例图" and pushed them. **User feedback: "你参考baoyu他那些风格嘛"** and "除了领导汇报风格可以 其他的风格效果都不行". The agent had hallucinated a "style showcase" template from `style-showcase-page-recipe.md` (PIL-built) but the AI-generated versions looked "low" and didn't read as "real PPT samples".
- **Why the first attempt was wrong**: the 3 style-showcase PIL-built images (in `examples/style-showcase-*.png` shipped in earlier commit) ARE the right pattern for **a PIL-synthesized single page summarizing design tokens** — they have hex palettes, checklist, and tagline. But for **AI-generated GitHub README sample images** that need to convince customers "this skill can produce real PPT pages", the right shape is **a complete information page that could ship in an actual deck** — title + 2×2 cards with real content + footer tag. The agent confused "design system documentation page" with "product sample page".
- **The two distinct shapes**:
  | Shape | Use when | Example |
  |---|---|---|
  | **Style index card** (PIL-built, swatches + labels) | README "design system" section, design tokens overview | `examples/style-showcase-leadership.png` (the PIL one, kept) |
  | **成品示例图** (AI-generated, full content page with 4 cards) | README "what can this style produce" sample gallery, customer-facing | The 12 + 7 "4 大xxx" images shipped in 16-style gallery |
  The user **always** wants the second shape for AI-generated README samples. The first shape is a *meta* artifact that documents a style's tokens, not a *product* artifact that demonstrates what an actual deck page looks like.
- **The fix — when the user asks for "风格代表图" / "成品示例" / "样图" for the README**:
  1. **Use the AI-image prompt to generate a complete, shippable content page** — title + 2×2 cards (each card: numbered badge, Chinese heading, English subtitle, 2 bullet points) + footer tag with the style's use case.
  2. **4 cards is the sweet spot** — enough density to demonstrate information density, low enough that the AI doesn't hallucinate text. 6+ cards regularly produce label-only cards with no real content.
  3. **Real, concrete, non-hallucinated content** — pick a concrete theme per style: banking 4 products, industrial 4 processes, education 4 abilities, tea 4 seasons. **NOT** abstract topics like "4 key features of this style" (the AI draws nothing meaningful).
  4. **The 4 cards per page should have a numbered badge (01/02/03/04)** — without explicit "01" "02" "03" "04" in the prompt, the AI often stamps all 4 cards "01" (P17's near-miss class). Always specify "01 or 02 or 03 or 04" in the prompt.
- **Style-showcase PIL recipe is still valid** for `examples/style-showcase-<name>.png` (the design-system documentation page). The pitfall is applying the *abstract* shape to *concrete README sample* needs.
- **Anti-patterns**:
  - "Let me generate a 1-page overview that captures the design language with swatches" — wrong shape for customer-facing README samples.
  - "Let me show 4 abstract style words like 'Tech / Pitch / Investor / Future'" — too abstract; cards have no real content the customer can read and judge.
  - "Just describe the style in the prompt" — AI image models don't have a "this is a style" concept, they paint from visual examples. Concrete content cards are what they can paint.
- **Real session 2026-06-13** (鲲鹏翼航 v4 → v5 push): agent's first 3 images were index cards → user said "low" → agent looked at baoyu (single fresh.webp that was a "4-card wellness infographic") and re-did with the "4 cards = complete information page" shape → 12+7 images that the user accepted. The "low" → "good" pivot happened on the second attempt with this pitfall's fix applied.

---

## Pitfall 37: When "fixing" a previously-shipped image (e.g. user said the old one was bad, or file path was wrong), **vision-verify the LOCAL file BEFORE pushing as the replacement** — "file exists at the right path" is not enough, "file is the right VERSION" is the bar

- **Symptom (observed 2026-06-13)**: user reported 3 images in GitHub README were "low" / wrong. Agent found 3 corresponding local files in `work/fix3/` and pushed them. The 3 images pushed were the **earliest style-probe candidates** (cypher-air city / 云栖茶事 / 小步启蒙) — the very images the user had previously called "low" and asked to redo. **The agent's mistake**: the local directory name "fix3" suggested "the fixed versions" but actually contained the **old, rejected** versions, while the real high-density成品图 were elsewhere. Agent pushed without vision-verifying the file content matched the intended replacement.
- **Why this is a class-level pitfall**: any "fix old file" workflow has a name-vs-content trap. A directory named `fix3/`, `v2/`, `replacement/` *suggests* it contains the fix, but it might contain anything. Directory names are a weak signal compared to file content.
- **The fix — vision-verify before any replacement push, 4 steps**:
  1. **Open the candidate file with `vision_analyze`** and ask the specific question that defines "is this the right version": e.g. "Is this '4 大应用场景' (电力/油气/智慧城市/应急救援)? 逐字读出标题和卡片". Not "what is this" — that lets the agent confirm "yes it's a cyberpunk image" when actually it should be the high-density 4-card version.
  2. **Compare to the originally-shipped version's content**, not its filename. If the candidate's content matches what the user asked for, ship it. If the content matches the OLD rejected version, find the real replacement.
  3. **When in doubt, look at the local cache by hash or by file size** — the 1.4MB city-nightscape vs the 1.5MB 4-card-dashboard have different byte signatures. The agent had 4 candidate files for cyberpunk (initial, redo, fix-attempt, real-fix); only the real-fix was correct.
  4. **The directory `fix3/` was a self-fulfilling name trap**: agent wrote it to mean "the 3 fixed images" but actually the agent had previously written OTHER high-density images to a different path. The label "fix3" only reflects the agent's intent, not the file's content. **Always treat directory names as hints to verify, not facts**.
- **Hard gate (per P29/P30)**: before any "push replacement image" action, run `vision_analyze` on the candidate. The question must reference the content the user wanted, not the file's path. If the vision answer doesn't match, refuse to push.
- **Real session 2026-06-13** (16-style showcase): agent pushed 3 wrong images as "fix" → user reported GitHub still wrong → agent looked at the real high-density files (which had timestamp `172558/172656/172920`) and re-pushed → 1 extra commit and 1 round-trip. Fix cost: 1 vision_analyze call (5 seconds) that would have caught the wrong-version-on-the-second-look.
- **Related**: P5 (vision self-check before showing the user) — the P37 fix is P5 applied to "pushing as a fix" instead of "showing the user the first time". The same self-check applies, but the failure mode is "I thought I fixed it, but I just re-pushed the bad version".

---

## Pitfall 38: For README + 公众号 dual-audience packages, the README's image grid is the **conversion surface** — design for "scroll-stopping visual diversity" not "comprehensive coverage" of style-library entries

- **Symptom (observed 2026-06-13)**: user wanted two distinct goals: (a) README on GitHub that "lets people see this is useful, want to install it", (b) 公众号 article to promote it. The agent initially focused on **completeness** — push the full style-showcase PIL index (11 images) plus 16-style grid plus leadership 4 sample pages = 30+ images. User said "我现在就是你的 多种风格样图帮我做好" and "除了领导汇报风格可以 其他的风格效果都不行" — **the comprehensive approach was the wrong goal**. The right goal was **a smaller, sharper grid where each image is visually distinct enough that a scrolling reader's eye is captured**.
- **Why "comprehensive coverage" is the wrong default for promotion surfaces**: every additional style reduces the average visual quality (because making 21 good images is harder than making 7) and increases cognitive load on the reader (they have to *compare* 21 styles instead of *recognize* 7). For "I want to try this" conversion, **fewer sharper** beats **more comprehensive**.
- **The fix — design the README grid for visual diversity, 3 rules**:
  1. **Each image must be visually distinct** — same style vocabulary = 视觉同质化 = 客户认为是同一张. The 7 dashboard images (light/dark/cream + 4-color/dark/corporate) hit this. The 11 PIL-built style-showcase pages hit a worst case: all 1920×1080 PIL mockups with hex swatches + checklist = 看起来一样.
  2. **3×N grid where N is 2-3 rows**, not 5-7 rows. Above 4 rows, GitHub README scroll-depth drops sharply. The 3×6 (18 images) grid is the upper bound.
  3. **Reserve 1 cell for "anti-pattern" or "what NOT to do"** — not always, but useful when the user is positioning the skill for first-time users who don't know the difference between "good" and "bad" output. The鲲鹏 case had this (1 anti-pattern cell). The leadership-style case doesn't need it (audience already knows what good looks like).
- **公众号-vs-README trade-off** (an extension of P15's "don't generate 18 in one shot"):
  - **README is the sales page**: 6-18 images, visual diversity, all on disk (so client doesn't have to install + pay to see the style).
  - **公众号 article is the story**: 1 hero image + 3-5 inline illustrations + 1 README screenshot. The agent should ask "do you want 公众号底稿" as a separate deliverable, not assume the README doubles as a 公众号 image bank.
  - **The 公众号底稿 should be drafted AFTER the README ships**, because the README defines which images are "the 5 visual anchors" the article will reference.
- **Real session 2026-06-13** (鲲鹏 v4 push): user said "现在就是你的 多种风格样图帮我做好 然后在github上给我同步一下" — the verb is "做好" not "做全". Agent should have pushed 7-9 sharp diverse images, not 16+11=27. Result was 16-style gallery, user accepted, but the earlier intermediate state of "11 PIL showcases" in the README was noise.
- **Anti-patterns**:
  - "I'll just generate one of each style in the style library" — 21 styles = 21 medium-quality images. 7 styles done well > 21 styles done adequately.
  - "I'll include all the existing style-showcase PIL images" — those are design-system docs, not product samples. They live in a separate `design-system/` subdir or get cut.
  - "The README should be comprehensive" — for a public-facing README, **scannable** beats **comprehensive**. The agent should design for "30-second skim" not "30-minute study".
- **Related**: P15 (cost-aware style probes, 3 not 18) and P25 (style-probe density, "看一眼" means 1-2 images not 4 full pages) are upstream of P38. P38 is the "promote the product" version of the same idea.
