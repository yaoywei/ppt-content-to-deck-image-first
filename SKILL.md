---
name: ppt-content-to-deck-image-first
description: Build a Chinese corporate pitch / 政企路演 PPT from a content brief by first generating 2-3 cover-style variations with image_generate, getting the user to pick one visual style, then batch-generating the remaining deck pages in the same style, and finally stitching them into .pptx (with python-pptx) or .pdf. Use when the user pastes a 公司简介 / 商业计划 / 路演材料 / 项目介绍 and asks for a PPT, or when the audience is leadership / 政企 / 党政. Also use when the user wants to OPEN-SOURCE PUBLISH the skill repo (README sample images, 公众号 cover, multi-style gallery) — load references/style-showcase-page-recipe.md for the "成品示例图" pattern. Distinct from ppt-from-template and mck-ppt-design. Triggers include 给领导看, 领导汇报, 政企风格, 做成PPT, 生成PPT, 首图选风格, 帮我做公司简介, 参考这份 PPT 的风格, 风格代表图, 出 1 张代表图, 多风格样图, 开源推广, 公众号配图, 风格一览图.
license: MIT
metadata:
  hermes:
    tags: [ppt, image-generation, chinese, corporate, deck, pitch]
    related_skills: [hermes-image-generation-providers, powerpoint, mck-ppt-design, ppt-from-template, ppt-generator, dragon-ppt-maker, hermes-secrets, handling-secrets-in-chat]
---

# PPT from Content - Cover-First Image Pipeline

Build a Chinese corporate / 政企 PPT in a 3-phase lock-step loop:

1. **Analyze content** then suggest 2-3 visual styles, generate one cover per style, user picks one
2. **Batch generate** the remaining 10-16 slides in the chosen style
3. **Stitch** into .pptx (with python-pptx) or .pdf, with optional small-text overlays (company name / numbers / labels) on top of the AI-generated visuals

The reason this loop exists: image-gen output is subjective, and redoing 16 slides because the user dislikes the 16th is wasteful. Locking the visual style on the cover cuts rework from 16xN to about 1xN.

## When to use

- User pastes a long Chinese company brief / pitch material / project introduction (10+ sections, 4+ data tables, 5+ named people) and asks for a PPT
- User is willing to wait 10-30 minutes for the whole pipeline (3 covers x 60-90s + about 15 slides x 60-90s + 30s stitching)
- User is OK with AI-generated backgrounds plus small overlays of text and logos (because text on AI images is unreliable - see Pitfall 1)
- NOT for: editing an existing .pptx, copying the visual style of a reference deck (use ppt-from-template), or for pure text / structure PPTs with no visual design (use mck-ppt-design or powerpoint)

## Phase 0 - Up-front alignment (do this BEFORE generating any image)

Before any tool call, confirm 4 things with the user in one message. Do not split into 4 messages; consolidate:

1. **Style direction**: present 2-3 named styles (see references/style-options.md) as a short menu, with one-line descriptions. The user picks, possibly with a hybrid like "main color A plus header using B's gold."
2. **Output format**: .pptx (editable, text-overlay via python-pptx) vs .pdf (locked, every page is the raw image). Recommend .pptx for any future edit; .pdf for final delivery.
3. **Page count target**: based on content density, suggest a count and let the user adjust. Default 14-16 for a company brief, 20-25 for a business plan.
4. **Image model / API**: confirm the user has an image_gen key configured, or is OK using whatever's already there. If not configured, walk them through hermes-secrets add OPENAI_API_KEY (see hermes-secrets) and never echo the key in chat. If the key is a third-party reseller (zhongzhuan.chat, sharehub.club, etc.), see handling-secrets-in-chat section 5a for the rotation path warning.

5. **Reference PPT/PNG handling** — if the user pastes a reference slide image, do NOT ask them to describe it in words. Run `vision_analyze` on the image to extract the visual language (palette, font mood, edge style, density, icon style — NOT text content), then propose the closest matching style from the library as "based on your reference, the closest style is X — confirm or override". Save the extracted description to `references/user-reference-<slug>.md` so the style stays consistent across all generated pages.

6. **Resource gathering (skip-allowed)** — ask in one consolidated message about: (a) company logo (PNG/SVG, transparent bg preferred, can skip), (b) team headshots (can skip), (c) client logo wall (can skip), (d) project case photos (can skip), (e) company VI primary/secondary colors (default to the style's built-in palette if user doesn't provide). Each item is optional — never block waiting for assets. If user provides files, save them under `user-inputs/` and use Pillow to normalize (transparent bg / center crop / stroke). If user skips, use AI-generated placeholders or text-only fallbacks.

7. **Persist user config across sessions** — first-run inputs (logo path, VI colors, default style, API keys) get saved to `~/.hermes/skills/<skill>/user-config.yaml` (or via `hermes-secrets` for API keys). Subsequent runs read this file and skip the prompts. API keys go through `hermes-secrets` and are NEVER echoed to chat or written to skill output files.

8. **Vision-based Chinese verification is OFF by default** — opt-in via a `verify_chinese: bool` flag in user-config. Default false. Only enable when the user explicitly asks for high-fidelity text rendering or when the deck is going to a public/investor audience where错字 would be embarrassing.

9. **Editability mode (overlay text vs full-bleed)** — ASK in Phase 0 before any image_generate: "**文字可编辑性**：你这份 PPT 后续需要自己改文字吗？需要 → 用 overlay-text 模式（图片是背景，文字是 PPTX 文本框，可编辑）。不需要 → 用 full-bleed 模式（图片是整体，文字锁在图里）." Default to **overlay-text (editable)** if the user doesn't reply. **Do not** silently pick full-bleed. See Pitfall 31.

Also flag advertising-law risk phrases in the content (see references/china-ad-law-phrases.md) - "国家级高新技术企业", "全球领先", "行业第一" etc. - and propose a softer rewrite. The user is the legal owner of the text; the agent surfaces the risk, does not silently rewrite.

## Phase 1 - Generate 2-3 cover variations, user picks one

For each of the 2-3 chosen styles, call image_generate (or the direct provider - see hermes-image-generation-providers for the bypass pattern if the tool is in a stale gateway import cache).

**Each cover prompt must include:**

- Aspect ratio landscape (16:9)
- The company name in Chinese, in the prompt literally - otherwise the model will hallucinate a similar-sounding but wrong name
- English subtitle (optional)
- One tagline from the company's own content (do not invent)
- No reference to a logo - AI image models will fake a logo and the result will be unrecognizable garbage

Do not put a phone number, address, or URL on the cover - those go on the last contact-us slide where text overlay is reliable.

**Per-image latency budget:** 60-90s for gpt-image-2-medium via Chinese resellers. 3 covers serial = 3-5 min (well within tool timeout). If you try to parallelize, you will trip the rate limit (120s cool-down after 3 invalid-key attempts, then 429 with a Chinese error message - see hermes-image-generation-providers section "Generation latency budget").

**Self-verify each cover with vision_analyze** before showing the user (per the working pattern in this session):
- Is the Chinese company name rendered correctly character-by-character? Sometimes simplified / traditional gets confused; sometimes the AI inserts a hallucinated character.
- Is the visual style aligned with the intended direction?
- Any text glitches / AI-isms (gibberish English, fake Chinese, watermark-looking patterns)?

If a cover fails the self-check, regenerate it (do not ship a known-bad one as an option). If the user picks a flawed cover anyway, that is their call.

Show the user all 3 covers with MEDIA:absolute-path lines (one per cover). Wait for the explicit pick before moving to Phase 2. Do not auto-pick on their behalf even if one is clearly the best.

## Phase 2 - Batch-generate the remaining 10-16 slides

**Lock the visual language from the chosen cover** (color palette, layout density, typography mood) into a shared prompt prefix, then vary only the per-page content. Example pattern:

```
{shared_style_prefix} | {per_page_content} | 16:9, no text overlays, no logo, no watermark
```

Per-page content should describe the visual, not transcribe the data. A page about "3 key numbers: 100人 / 10省 / 10国" should not prompt "write '100人 / 10省 / 10国' on the page" - that produces mangled text. Instead, prompt a data-dashboard layout with three big number placeholders, and overlay the actual text in python-pptx during Phase 3.

**Slide-by-slide outline template (for a 14-page company brief deck):**

| # | Title | Visual content | Text overlay (added in Phase 3) |
|---|---|---|---|
| 1 | Cover | (Phase 1 output) | (none) |
| 2 | One-line positioning | Minimal hero card | the company tagline |
| 3 | Three key numbers | Big number row | headcount / provinces / countries |
| 4 | Business overview | Three-pillar infographic | 城市 / 工业 / 国际 |
| 5-6 | City scenario pages | 2x2 scenario grid + product shot | per-scenario metric |
| 7-8 | Industrial scenario pages | Equipment + radar visual | per-scenario metric |
| 9 | International business | Globe with route arcs | 东南亚 / 中东 / 非洲 |
| 10 | Training program | Classroom / lab visual | training track + certificate validity |
| 11 | Core team | 5-portrait grid layout | name + role |
| 12 | Talent structure | Donut + bar | 博士 2 / 硕士 3 / etc. |
| 13 | Timeline | Horizontal arrow + 5 milestones | 2018 / 2019-20 / ... / 2025 |
| 14 | Contact us | Map pin + clean contact card | address / phone / URL |

**Batch size = (script timeout cap) / (per-image latency) times safety margin.** For 300s cap and 60-90s per image, 3 images per execute_code call is the safe upper bound. 5 slides in one script = 5x90s = 450s, will time out. Split.

**Re-prompt strategy for failures:**

- If a slide's first output is "almost right" but the visual feels off, retry with the same prompt - image-gen has natural variance and 2nd-try often nails it
- If a slide fails 3x in a row, stop, report the blocker, and ask the user whether to skip that slide or change direction. Do not burn 10 minutes on one stubborn page.

## Phase 3 - Stitch into .pptx (or .pdf)

**For .pptx with text overlay (recommended for editable decks):**

Use the powerpoint skill's python-pptx pattern. Each slide = one full-bleed image (16:9, fills the whole 13.33" x 7.5" slide), then overlay text boxes for the small text that AI image-gen cannot reliably produce. Reference: references/python-pptx-stitch-recipe.md for the exact 30-line script.

Why overlay: AI-generated Chinese text is unreliable (hallucinated characters, wrong stroke count, simplified / traditional mix). Generating a clean background plus overlaying real text in a system font is faster and correct.

**For .pdf only (final delivery, no edits):**

Skip the text overlay - the AI image is the final. Concatenate the 14-16 PNGs into a single PDF with img2pdf or PIL. Faster to build, no editable text.

**Verification before declaring done:**

- Open the .pptx / .pdf and check page 1, page N, and 2 random middle pages - the visual style is consistent (same color palette, same density, same typography mood)
- All company names spelled correctly on overlay slides
- No AI-hallucinated Chinese characters leaked into overlays
- The file opens cleanly in PowerPoint / Keynote / LibreOffice (no corruption)

## Pitfalls

1. **AI-generated Chinese text is unreliable** - characters get mangled, simplified / traditional mixed, fake characters inserted. Do not put the company name, key numbers, or any factual data on the AI-generated image directly. Put them as python-pptx text overlays in Phase 3. See hermes-image-generation-providers for the general image-gen reliability profile.
2. **image_generate tool uses gateway import cache** - if you patched the plugin source, the change will not take effect until the gateway restarts. Use the execute_code + importlib.reload + OpenAIImageGenProvider().generate() bypass pattern from hermes-image-generation-providers section "Gateway subprocess import cache" to prove the patch works without bouncing the gateway.
3. **Chinese ad-law phrases** are legal risk in a deck that will be shown to government, investors, or the public. Surface "国家级高新技术企业", "全球领先", "行业第一" and similar to the user in Phase 0, propose softer rewrites (e.g. "已通过国家高新技术企业认定" or "在低空经济领域持续深耕"). Do not silently rewrite.
4. **Rate limits on third-party endpoints** are aggressive (about 1 concurrent, 120s cool-down after 3 consecutive invalid-key attempts). Do not parallelize. Plan batch size = cap / latency times 0.7. See hermes-image-generation-providers section "Generation latency budget".
5. **Vision self-check before showing the user** - never ship a cover that the user has to reject. Spend 1 extra vision_analyze per cover to catch mangled Chinese. It is faster than the user discovering it and redoing Phase 1.
6. **Do not promise specific fonts / exact pixel-perfect layouts** - the AI image side has natural variance. Promise "visual style consistent across all slides"; promise "all Chinese text on overlays will be correct"; do NOT promise "all numbers land in the same pixel position on every page."
7. **If the user asks for a one-shot full deck without the cover-pick loop** - refuse gently and explain why. The 30-min full-deck on a wrong-style retry is much worse than the 5-min cover-pick loop. The user's time is the constraint.
8. **Send image batches ONE AT A TIME PER IMAGE (parallel `send_message` calls in the same tool block), never as a montage / triptych / collage** - the user is reviewing visual style, and a multi-image grid (montage, side-by-side, triptych) makes it hard to focus on any single one, and on chat platforms (Feishu / 飞书) inline image rendering of montage PNGs is unreliable. Workflow: (a) generate N images in one tool round (parallel `image_generate` calls), (b) for each output call `send_message(action="send", target=chat, message="MEDIA:/abs/path")` separately, **all within the same tool block** (parallel, not serial), (c) do not wait for "看到了A" before sending B. The user explicitly flagged *"别拼在一起 你三张分开给我看"* — and the parallel-send-in-one-block pattern is what satisfies both that preference AND the "no one-image-per-round stall" rule from the complementary `ai-ppt-image-generation` skill. This applies to ALL "show me N visual variants" tasks, not just covers. The two skills are NOT in conflict: one says "parallel in one tool block" (correct), the other says "not one at a time with waits between" (also correct, and they are the same thing).
9. **For users who explicitly say "违禁词 自动帮我改掉" / "auto-fix the ad-law phrases"** - do not surface the warning in Phase 0 and wait for confirmation. Apply the safer rewrites from references/china-ad-law-phrases.md **silently in the slide content** AND drop a one-line audit trail in the **PPTX 备注页 (notes)** like "本页已自动改写：'国家级高新技术企业' → '已通过国家高新技术企业认定'". This is a user-preference default for THIS user, not a general rule - other users still get the Phase 0 surface-and-confirm flow.
10. **Use Prompt-as-Code structured prompts, not prose** - after 6/2026 the GPT-Image-2 prompt engineering community has converged on a 7-section atomic structure (Subject / Background / Lighting / Materials / Layout / Style references / Negative) that is more stable across regenerations than the prose prompts in references/cover-prompt-template.md. See references/prompt-as-code-template.md for the upgraded templates for each of the 3 styles. The prose templates still work, but Prompt-as-Code is preferred when the user is on a Chinese third-party reseller endpoint where variance is high.
11. **`image_generate aspect_ratio="landscape"` returns 1536x1024 (3:2), NOT 1920x1080 (16:9).** When stitched into the python-pptx 16:9 (13.333"x7.5") deck, the image gets either letterboxed (top/bottom black bars) or vertically stretched. The user will report *"pdf 版看着有些图片比例不太对"*. Always (a) `identify p1.png` after staging to confirm pixel dimensions, (b) if 1536x1024, pad with `convert p1.png -resize 1620x1080 -background "#050810" -gravity center -extent 1920x1080 p1_padded.png` for all N images before building the .pptx. Do NOT crop (loses top brand badge / bottom English subtitle) and do NOT stretch (distorts UI). For the padding recipe and full diagnostic, see `ai-ppt-image-generation` skill's `references/pptx-pdf-assembly.md` "Stage 1.5".
12. **If the user signals "卡住了？" / "能接着继续吗" mid-pipeline** - the user thinks you are stalled. This usually means: (a) you sent an image and are waiting for confirmation, when you should be sending the next, (b) you said "等你确认" when actually you had more work to do in parallel, (c) you batched pages but only sent 1-2 before pausing. When you see this signal, immediately (1) stop waiting, (2) send the rest of the batch in one tool block (parallel `send_message`), (3) tell the user explicitly that more images are on the way and which pages. Don't apologize for the slowdown — just resume.
13. **If the user says "我睡了 明早验收" / "我明早来看" / "I'm sleeping" mid-pipeline** - this is a **full-autonomy signal**, not a pause. The user has explicitly delegated the rest of the run. Do NOT stop and wait, do NOT ask clarifying questions, do NOT summarize what you would do "in the morning". Instead:
    1. **Do the entire remaining pipeline end-to-end** (all 14+ content pages, padding, .pptx, .pdf, optional .html). Make every decision the user would have made (style pick, page count, content placement) using the rules in this skill.
    2. **Save EVERY intermediate artifact visibly** under a stable path the user can browse in the morning. The 3 style-comparison images are NOT optional — the user said *"中间的几种风格图片生成也不要省略 我明早也能看到"*. Even though they sleep through the choice, the comparison still must exist on disk so they can audit the style decision in the morning.
    3. **Tell the user up front, before they sign off**: "I will make decisions X, Y, Z on your behalf because you're sleeping. If any are wrong, tell me in the morning and I'll fix them." This is the user's escape hatch — they don't have to wake up to course-correct, but they CAN if they want to.
    4. **At the end, send ONE final delivery report** with the absolute paths of all artifacts: style-comparisons/, images/, images-padded/, pptx/, pdf/, html/. The user wakes up, opens their phone, sees the paths, and can browse them via scp / file manager.
    5. **Anti-patterns to avoid**: (a) doing 1 step then writing a long "I'm pausing here, you can confirm in the morning" — the user wants the WORK done, not a status update; (b) skipping the style-comparison step because "the user can't pick anyway" — wrong, the user wants the comparison visible for audit; (c) batching the rest of the pages but only sending the cover/intro page — the user can't see your work without all pages delivered to disk.
14. **The 3 style-comparison covers in Phase 1 are deliverables, not throwaway previews** — even after the user picks one (or the agent picks one in autonomous mode), the 3 covers MUST be saved under a stable path (`style-comparisons/A-<name>.png`, `B-<name>.png`, `C-<name>.png`) and a 1x3 or 2x2 montage (`style-comparisons/三风格对比.png`) so the user can later review the design decision. This is the user's "audit trail" for "why did the agent pick this style?". Pattern observed in real session 2026-06-12: user explicitly said *"你站在ppt制作者和验收者等角度看看是否还有需要补充的内容"* and *"中间的几种风格图片生成也不要省略"* — the comparison images are the answer to the auditability concern.
15. **The 3-cover probe can be expanded to a wider style sweep, BUT ask first, and keep the count reasonable** — if the user (or the workflow) wants a broader view of style options beyond the 3 starters, generate up to 18 candidates in 2-3 rounds (3 + 5 + 10), but **stop and ask the user to pick from the first 3 before generating more**. User signal observed 2026-06-12 morning: *"不要出那么多吧 浪费钱啊"* — the agent generated 18 style probe images in one shot (~25-30 元 spent on a Chinese third-party image endpoint), and the user's complaint was specifically "you're burning money generating all 18 when 3-5 would have given me the same decision power". Anti-pattern: the agent interpreted the user's earlier "中间的几种风格图片生成也不要省略" (don't skip the style images) as "generate the entire 21-style library" — wrong. The right reading is "don't skip the COMPARISON step (3 probes), but don't generate the whole library either". The cost-aware defaults are: (a) 3 probes in the first round, (b) if user wants more, offer 3-5 additional candidates grouped by their stated preference (e.g. "you liked the dark/data style — want 3 more dark variants?"), (c) never generate the full 18+ in one shot without asking.
16. **After a deck ships, the style probe images are a reusable asset, not throwaway** — if the agent generated extra style candidates beyond the chosen one, copy them to a separate `style-library/` directory at the **session root** (not inside the dated deck dir), so future decks can reuse them as reference. Pattern: at end of a session, the user said *"3 — 把这个skill 固化 然后以后别人用"*, signaling that the style-probe images should be saved as a permanent asset for future PPT generation. The right shape is `~/kunpeng-ppt-delivery/style-library/<letter>-<stylename>.png` (not under `deck-2026-06-12/style-comparisons/`, which is one-off). Each style image gets a 1-line index card in `style-library/README.md` linking it to its use case.
17. **Vision can garble CJK near-miss characters in its reply** — when the agent asks vision_analyze to verify a Chinese phrase, the model's reply can substitute a similar-looking but DIFFERENT character (e.g. vision returns "厘米" for an image that actually says "厘米" — two characters that share many strokes; the rendered text in the model reply may have displayed a near-miss). **Never report a "typo" to the user based on a single vision read** — always (a) re-ask vision the same image with a more specific question ("逐字读出 X-Y 这 6 个字, 是 A 还是 B?"), (b) check the underlying PPTX/PDF text directly with `pdftotext` or `unzip -p file.pptx ppt/slides/slideN.xml | grep`, (c) only flag a real typo when BOTH vision and the raw text confirm it. This user explicitly called out a false-positive typo flag ("P8 错字: 厘米级" → it was actually correct as "厘米级"). The cost of a false positive is user trust erosion + a needless "fix" cycle.
18. **The "user picked C" signal can be ambiguous between "C is good, ship it" and "C is good, I want to see more dark/data variants like C"** — when the user picks one cover out of 3, do NOT default to "now batch-generate the deck". Confirm: (a) "lock and batch" vs (b) "show me more variants in this style before locking". Same conversation 2026-06-12, user picked C as a single image, agent correctly went to (a) but the false-positive typo flag from vision (Pitfall 17) and the agent's habit of expanding the style probe (Pitfall 15) both created unnecessary churn. The simplest question is *"锁这个风格出 15 页" vs "再出 3 个类似 C 的我挑一下"* — ask in one round, not after generating.

## Pitfall 19: After a successful run, package the workflow as a shareable skill
- **Symptom**: A complex deck (15+ pages, multi-step pipeline) just shipped successfully. The user says *"3 — 把这个skill 固化"*, *"以后别人用"*, or *"写成一个 skill 让人能直接用"*. The wrong move is to just hand the .pptx to the user and consider the job done — that ships a one-off artifact, not a reusable capability.
- **Why this is the highest-leverage step**:
  1. **The user just paid 30-60 minutes of your time + $20-30 in image-gen cost** to validate the workflow end-to-end. That investment is **fully recoverable** if the workflow is reusable.
  2. **The same user, OR people they refer, will want the same thing next time** — without a packaged skill, they pay the same discovery cost again.
  3. **"Share via GitHub link" is the distribution channel** — the user's phrasing *"发给别人 让别人用"* means they want a one-line install / clone command, not a zip file in chat.
  4. **Class-level skills get picked up by other Hermes agents automatically** — the `<!-- AI-AGENT-META -->` HTML comment block in the README signals to any agent that fetches the page "this is a skill, here is how to install it".
- **Fix — package + push in 5 steps**:
  1. **Build the skill directory** at `~/path/to/<skill-slug>/` with: `SKILL.md` (the full workflow), `install.sh` (one-line installer), `README.md` (GitHub landing page with `<!-- AI-AGENT-META -->` block), `references/prompt-as-code-template.md` (per-page prompt templates), `references/style-library.md` (style library index), `templates/animated.html` (if HTML output exists), `examples/<case>/` (1-3 sample images from the shipped deck).
  2. **Pick a class-level name**, not a session-specific one. `company-deck-c1-hud` (good — describes the deck style and business scenario) beats `kunpeng-yihang-v3-skill` (bad — single customer name).
  3. **Create a public GitHub repo** (the user wants others to use it, so private defeats the purpose). Use the GitHub Contents API / Data API if `git push` is unreliable on the host — see `github-data-api-push` skill.
  4. **README.md must include** an `<!-- AI-AGENT-META-START/END -->` HTML comment block at the top with: install command (one line of bash), trigger keywords (so other agents know to load it), TL;DR. Without this block, the README looks like a normal doc — the agent that fetches the page won't recognize it as a skill manifest.
  5. **Send the user one message** with: GitHub URL, install command (for forwarding to others), trigger keywords. They forward the URL to their network; recipients run `git clone` or `curl install.sh | bash` and the skill is in their `~/.hermes/skills/`.
- **Anti-patterns**:
  - Stopping at "I'll think about it" / "let me know if you want to share this" — the user already said yes by selecting "3 — 固化". Just do it.
  - Putting the .pptx and PNGs in the GitHub repo — the repo is for the **workflow**, not the **artifact**. The artifact is in the user's deck-output dir; the repo is the recipe.
  - Naming the repo after the customer / project (`kunpeng-yihang-ppt-skill`) — class-level names are reusable. `company-deck-c1-hud` works for any future 科技/无人机/低空经济 deck in the same C style.
  - Skipping the `<!-- AI-AGENT-META -->` block — without it, the README is just docs, not a machine-readable manifest. Other agents won't auto-detect it.
- **Real session 2026-06-12** (鲲鹏翼航 v3): user picked "3 — 固化" after the deck shipped. The agent built `company-deck-c1-hud` skill, pushed via GitHub Data API in ~37s. User received: GitHub URL, install command, forwarding template. Total "deck shipped → skill published" was ~10 minutes.
- **Related**: `github-data-api-push` skill for the push path.

## Pitfall 20: Distinguish "skill name" from "build directory name" — `company-deck-c1-hud` ≠ `company-deck-skill-build`

- **Symptom (observed 2026-06-12)**: user has a directory `~/company-deck-skill-build/` that CONTAINS a skill called `company-deck-c1-hud/`. The agent confuses the two and reports "the skill is called company-deck-skill-build" — wrong. The build directory is a *container* (it can hold many skills over time); the skill name is what's inside.
- **Why this matters**: the user's instruction was "use the company-deck-c1-hud skill" but `skill_view(name='company-deck-c1-hud')` returned "Skill not found" because the skill is **not installed in `~/.hermes/skills/`** — it's only source-cloned in the build dir, awaiting `install.sh`. If the agent had said "yes loaded it" (without checking), it would have hallucinated the workflow.
- **The right diagnostic when a skill name returns "not found"**:
  1. `ls ~/.hermes/skills/ | grep <slug>` — is it installed? If yes, you have a different bug. If no, go to step 2.
  2. `find ~/ -maxdepth 4 -name "SKILL.md" -path "*<slug>*" 2>/dev/null` — is the source somewhere on disk? If yes, the skill exists but is **uninstalled**. Read it from the build dir to extract the workflow, but tell the user "the skill is in the build dir, not installed — I'm reading the source for reference, but you should run `install.sh` before next session."
  3. Never `skill_view` something you're not sure exists — `Skill not found` is the truth, treat it as such.
- **Naming convention for the user**: when telling the user "the skill that does X is called Y", verify by `head -1 <path>/SKILL.md` and reading the `name:` frontmatter field. Don't infer from the directory name.
- **Related**: this is the same class of error as Pitfall 8's "send 18 images when user wanted 3" — both are "agent assumed a thing existed/worked without checking." The cost is wasted cycles or hallucinated workflow.

## Pitfall 21: For 领导汇报 / 政企白底 / 政企风格 decks, the C 风格 HUD 霓虹 is the WRONG default — force Phase 1 cover-pick

- **Symptom (observed 2026-06-12)**: user says "这份 PPT 是给领导看的 / 领导不喜欢花里胡哨的 / 政企风格" and then asks to use a previously-built skill (e.g. `company-deck-c1-hud` for 无人机 HUD). Agent defaults to the skill's locked C 风格 (深蓝黑底 + 电光蓝霓虹 + HUD 仪表盘) and starts generating without asking — wrong audience, wrong tone. Leadership decks need **白底 / 深蓝+金 / 实拍风格 / 简洁几何** which is the OPPOSITE of the HUD 霓虹 style.
- **Why this is a class-level pitfall (not just for this one skill)**: any "specialized" PPT skill that locks a style (HUD / cyberpunk / 未来感 / 二次元 / 国潮) is wrong for the **政企 / leadership / conservative** audience. The class-level umbrella `ppt-content-to-deck-image-first` does NOT lock a style (it's a 3-phase loop with style choice) — for leadership decks, ALWAYS go through the umbrella, not the specialized skill.
- **Signal phrases that flip the audience to "leadership"** (load `references/leadership-deck-style-rules.md`):
  - "给领导看 / 领导汇报 / 领导检查 / 给 XX 看" — explicit leadership audience
  - "政企 / 国企 / 党政 / 央企" — government / SOE context
  - "正式 / 严肃 / 不要花里胡哨 / 简单 / 干净 / 商务" — conservative style preference
  - "白底 / 蓝金 / 实拍" — explicit conservative palette
  - User provides a reference PPT (e.g. 湖南驰阳介绍.pptx) with white background, navy + gold, photo grids — that's a leadership-style reference, NOT a HUD reference
- **The fix**: when any of the above signals appear, **do NOT use the specialized skill's locked style**. Instead:
  1. Tell the user: "the C 风格 HUD is wrong for leadership decks — too neon, too 'tech-bro'. The right tone is white background, navy + gold, photo-grid layout, clean typography. I'll generate 3 conservative-style cover candidates for you to pick from."
  2. Generate 3 Phase 1 covers in leadership style (white, navy, gold, simple geometric) — see `references/leadership-deck-style-rules.md` for the prompt vocabulary
  3. Get explicit user pick before Phase 2 batch
  4. Real session 2026-06-12: user said "领导的 ppt / 领导不喜欢花里胡哨的 / 想要湖南驰阳那种风格" after initially asking to use `company-deck-c1-hud`. Agent correctly (a) noticed the contradiction, (b) refused to use the HUD skill, (c) generated 1 cover in the conservative style for the user to evaluate. User confirmed direction only after seeing the cover.
- **Anti-pattern**: "user said to use skill X, so I use skill X regardless of the audience mismatch." Skills are tools, not mandates. The audience determines the style; the style determines the skill.
- **The leadership style vocabulary (for prompts)**: "official Chinese government-enterprise presentation, white background, navy blue + gold accents, clean professional typography, photo grid layout, subtle geometric decoration, NO neon / NO HUD / NO cyberpunk / NO AI-art signature". See `references/leadership-deck-style-rules.md` for the full prompt template.

## Pitfall 23: When the user pastes a reference PPT (".pptx as 风格参考"), you MUST vision-analyze 4-6 pages of it BEFORE generating — not generate from your imagination of the style
- **Symptom (observed 2026-06-13)**: user said "是的 这个就是 参考风格的ppt" + uploaded `湖南驰阳介绍.pptx`. Agent generated 4 cover-style images with `navy blue + gold + white background` palette because that's what the *generic* "leadership PPT" stereotype suggests — and the user immediately flagged: **"比例有些不对"** and **"我觉得你可能需要学习一下这里面ppt中图片与文字的排版"**. The agent had not actually looked at the reference; it had hallucinated the style. The reference was actually `navy blue + red + white-gray`, with red diagonal block on cover, light world map texture, fixed page header (red+navy square + section number + title + red line + top-right logo), left-image-right-text 50/50 on content pages, certificate wall on qualifications page, and 5-column team card layout. The agent's "leadership style" guess was wrong on 6 out of 7 dimensions.
- **Why this is a class-level pitfall, not a one-off**: any "do it like this PPT" instruction is an instruction to **extract**, not to **hallucinate**. The agent's prior on "what does a Chinese leadership PPT look like" is the median of all such decks the training data has seen, which is a generic consultant style — not the specific company's actual style. The user is asking for THIS company's style, not the average.
- **The fix — extract, don't guess, 4 steps**:
  0. **HARD GATE (per P29/P30) — pre-condition `ls` check before any image_generate when a reference PPT is in play**:
     ```bash
     # Pre-condition: did we extract the reference PPT yet?
     ls references/user-reference-*.md 2>/dev/null | wc -l   # must be >= 1
     # If 0, refuse to call image_generate, run steps 1-4 first.
     ```
     This is a 1-line shell check. The agent runs it BEFORE Phase 1. If the file doesn't exist, the agent does the extraction (steps 1-4 below) BEFORE generating any cover. This is the P23 hard gate.
  1. **Convert .pptx → .pdf** with `soffice --headless --convert-to pdf <pptx> --outdir <dir>`. The .pptx may have CJK filenames that confuse `pdftoppm`; pass the converted PDF's actual filename.
  2. **Convert .pdf → per-page PNGs** with `pdftoppm -r 100 <pdf> <prefix> -png`. -r 100 is enough for layout extraction; vision_analyze has a size budget and high-res is wasted.
  3. **vision_analyze 4-6 representative pages** — pick: cover (p1), contents page (p2), a content page with text+image (early middle), a photo-grid page (qualifications or gallery), a team/people page, a closing page. The first 3 are mandatory; the others are style-specific. For each page ask: "1) 主图位置 2) 文字位置 3) 字号比例 4) 边距留白 5) 整体布局描述" (or the equivalent in English). The output of vision_analyze is the **prompt vocabulary** for Phase 1/2 — copy the agent's own analysis back into the prompt.
  4. **Build a `references/user-reference-<slug>.md`** summarizing: exact color palette (with hex if vision can name it), fixed elements that appear on every page (page header, footer, logo position), cover layout pattern, content page pattern (left-image-right-text / top-text-bottom-image / etc.), photo-grid pattern (rows x columns, orientation mix), typography mood (serif/sans, weight, density). This file becomes the **prompt prefix** for every generated page in Phase 2.
- **The recipe lives at `references/learn-from-reference-ppt.md`** with copy-pasteable commands. Run it whenever the user pastes a .pptx as a style reference, before generating any cover.
- **Don't skip the extraction even if**:
  - the reference "looks familiar" (it's probably not the same deck you've seen before)
  - the user only pastes 1 page (extract what's there, ask for more if needed)
  - you think you know the industry (e.g. "Chinese cybersecurity PPT always looks like X" — they don't, the variance is huge)
- **Anti-pattern**: "user said the style is 湖南驰阳, I'll just describe a generic government-enterprise deck in my prompt" — the result is the generic version, not the user's specific version. User will say "比例不对" or "感觉差点意思" and you redo.
- **Real session 2026-06-13** (鲲鹏翼航 v4): user uploaded 湖南驰阳介绍.pptx (32 pages, real layout: red diagonal cover, fixed page header, world map background, 50/50 left-image-right-text, certificate wall, 5-column team). Agent generated 4 covers with `navy + gold + plain white + right-aligned text` — wrong on 6/7 dimensions. User said "我觉得你可能需要学习一下这里面ppt中图片与文字的排版". After running the extraction recipe, the next 4 covers matched the reference on 6/7 dimensions and the user said "风格还行" (proceeded). Cost of skipping extraction: 4 wasted image generations (~$5-10) + 1 round-trip. Cost of running extraction: 60-90 seconds.

## Pitfall 24: AI image-gen cannot reproduce a real logo — leave the slot empty in the prompt, overlay the real logo in python-pptx stitching
- **Symptom (observed 2026-06-13)**: user uploaded a real logo (a blue low-poly geometric icon) and asked the agent to "use this logo" in the cover. The agent described the logo in the prompt ("abstract blue low-poly geometric logo icon, light blue, dark navy, teal gradients, faceted polygon, lightning-bolt-like shape") and let the AI draw it. The result was **a similar-looking but visibly different shape** — the proportions, the facet count, the angle of the cut were all off. The user could not have shipped this; the logo would have been "the wrong logo" in the deck.
- **Why AI cannot reproduce a real logo**: (a) image models don't have a "logo fidelity" objective — they optimize for "looks like a logo" not "is THIS logo", (b) the model's description of the logo is a lossy compression of the actual pixel data, (c) the variance of image generation means even a perfect description produces 5+ visually-distinct shapes per prompt.
- **The fix — leave the slot empty, overlay in stitching, 4 steps**:
  1. **When the user pastes a logo file (jpg/png/svg)**: save it under `user-inputs/logo.<ext>`. Do NOT describe it to the AI in detail. Do NOT include it as a reference (most image-gen endpoints don't support reference images anyway).
  2. **In the Phase 1/2 prompt**: **NEVER say "empty placeholder square" or "logo slot" or any phrase that names a shape** — the AI will draw the shape. Use one of these two patterns:
     - **Pattern A (silent)**: do not mention the logo at all in the prompt. The top-right corner will be whatever the surrounding page composition leaves there (white space in the leadership palette, or scene-bleed in the dark style).
     - **Pattern B (negative)**: explicitly forbid: `"TOP-RIGHT CORNER: completely EMPTY white space, no shapes, no icons, no logos, no squares, no decorations, no marks — just clean white background"`. This is the most reliable — the AI follows the negative instruction better than the positive "empty placeholder" instruction.
     - **Anti-pattern (what NOT to write)**: `"TOP-RIGHT: a small empty white placeholder square (50x50px) — logo will be overlaid in post-processing"`. The AI reads "empty white placeholder square" as a literal shape and draws a 50x50 white box with a faint border, exactly as described. The user will see two elements: the AI's box AND the overlaid logo, and the box looks like a broken image placeholder.
  3. **In Phase 3 (python-pptx stitching)**: use Pillow to composite the real logo onto the top-right corner of each generated page. **The composite must be the same logo file on every page** — that's how you guarantee visual consistency across 15 slides. Recipe:
     ```python
     from PIL import Image
     base = Image.open("p1.png").convert("RGBA")
     logo = Image.open("user-inputs/logo.png").convert("RGBA")
     # Resize logo to target size (e.g. 60x60px for 16:9 1920x1080 base)
     logo = logo.resize((60, 60), Image.LANCZOS)
     # Paste at top-right with 5% margin
     margin = int(base.width * 0.03)
     base.paste(logo, (base.width - 60 - margin, margin), logo)
     base.save("p1_with_logo.png")
     ```
  4. **Tell the user explicitly in the chat**: "AI 画的 logo 跟你发的原图不会 100% 一致, 我会在 PPTX 拼图时用你原图覆盖, 这样最准."
- **The same principle applies to**:
  - **Team headshots**: if user provides 5 real photos, use the photos in the team page (not AI portraits of "5 Chinese professionals")
  - **Client logos** (the 客户案例 page): if user pastes a client logo wall, use it. If not, AI-generated fake logos are clearly fake — prefer a list of names instead.
  - **Product photos**: if user has drone photos, use them. If not, AI drones are recognizable as fake.
  - **Certification photos**: if user has the actual certificate images, use them. If not, AI certificates are obviously fake.
- **Class of rule**: **real assets go to stitching, AI fills the layout/background/decoration**. The split is: AI does the things the user couldn't get a real photo of (background scene, abstract decoration, mood imagery); user-provided assets are used as-is for the things they could provide (logos, people, certificates, products).
- **Anti-pattern**: "the user gave me a logo, I'll describe it in the prompt and let AI draw it" — the user will see the discrepancy and lose trust. "Real assets" includes logos.
- **Real session 2026-06-13**: agent produced 4 covers with AI-imitated logos. The shapes were "in the family" of the original (blue geometric polygons) but not the same shape. The fix: leave the logo slot empty in prompts, overlay real logo in PIL compositing during Phase 3. Total overhead: 5 lines of code in the stitching script.

## Pitfall 25: For "看一眼风格合不合适" / "出 1-2 张看看" requests, the user wants VISUAL style confirmation, not a final product — generate ONE clean reference, not 4 busy ones
- **Symptom (observed 2026-06-13)**: user said "按照这个风格做一下首图 和前三张内容图" (one cover + three content pages) in response to the agent generating 4 cover-style candidates. The agent then generated 4 detailed pages with section numbers, page headers, full content, and full photo grids — but the user just wanted to validate the style. User's next message was "风格还行 内容有些拥挤了" — the style was right but the density was too high, because the user wasn't asking for "the deck" yet, just a style probe.
- **The right pattern for "看一眼风格" requests**:
  1. **One cover (P1)** — show the full visual language: color palette, decorative elements, page header, layout density. This is the most information per square pixel.
  2. **Two contrasting content pages** — pick (a) a text-heavy page (e.g. 公司概况 with one paragraph) and (b) a photo-heavy page (e.g. 资质 with a photo grid). The contrast shows the agent can handle both, not just one mode.
  3. **Less is more on each page**: use only the page-header decoration + the section content, not "everything" (no full photo wall AND no full text block AND no full sidebar — pick ONE per page).
  4. **Density budget for a style probe**: 40-50% white space, 1 photo (or no photo), 1 text block, 1 decorative element (page header). If the probe is at 70% density, the user will read it as "this is busy" and the real deck will inherit that.
- **The 4-image generation was a wrong scale** for a "看一眼" request. The right scale is 2-3 images, each a clean reference, with the user picking the style from the cover. After pick → batch the rest. This is the same pattern as Pitfall 15 ("3 covers, not 18") applied to the "show me your style" round, not just the first style-probe round.
- **Signal phrases that indicate "style probe" not "production"**: "看看风格 / 看下效果 / 出一张看看 / 感觉一下 / 是不是这个意思" — these are all low-commitment validation asks, not "build the deck."
- **Anti-pattern**: agent takes "做一下首图和前三张" as a 4-page mini deck and fills each page with section content. User reads it as "the final density is too high" and the style probe failed its job (which is to validate density, not just visual language).
- **Real session 2026-06-13** (鲲鹏翼航 v4): user said "出一张新的图, 能看出风格 看出效果的" (one image, show style + effect). Agent correctly did 1. Then user said "出 1 张首图 + 3 张内容图" — but the 3 content pages were over-stuffed with the full section content (full company description, full mission text, full qualifications list). User feedback: "内容有些拥挤了". The right move would have been: 1 cover (full) + 2-3 content pages (sparse, just the section title + 1 short sentence + 1 photo, to validate the layout works at low density). Density tuning is part of style confirmation.

## Pitfall 26: Skill names with a build directory container (e.g. `company-deck-skill-build/`) and a nested skill (`company-deck-c1-hud/`) are a navigation trap — always read the `name:` frontmatter
- **Symptom (observed 2026-06-13)**: user said "做ppt的skill到底叫什么 是叫company-deck-skill-build 这个吗". Agent had said "yes" earlier in the session, conflating the **build container directory** (`~/company-deck-skill-build/`) with the **skill name** (`company-deck-c1-hud/`). The user had to ask explicitly because the agent's earlier statement was wrong on the literal name.
- **Why the agent got it wrong**: the directory `~/company-deck-skill-build/` is more visually salient than the nested `company-deck-c1-hud/SKILL.md` (which is 2 levels deep). When the agent scans the filesystem, the outer directory wins the heuristic. The actual skill name is in the `name:` frontmatter of `SKILL.md`, NOT the directory name.
- **The fix — read frontmatter, not directory name, 3 steps**:
  1. **When a user mentions a skill by any name** (whether they say "the company-deck-skill-build skill" or "the company-deck-c1-hud skill" or "那个做PPT的skill"), do NOT guess. Run `head -10 <path>/SKILL.md` and read the `name:` field.
  2. **If the user gave a fuzzy reference** ("the PPT skill we built last time"), locate candidates via `find ~/.hermes/skills ~/company-deck-skill-build -name SKILL.md 2>/dev/null`, then for each candidate check the `name:` and `description:` to see if it matches what the user means.
  3. **When reporting "the skill is X" to the user**, quote the frontmatter value literally: "The skill is `company-deck-c1-hud` (per the `name:` field in SKILL.md), located at `<path>`. The directory `company-deck-skill-build` is the build container, not the skill."
- **This is a generalization of Pitfall 20** ("`company-deck-c1-hud` ≠ `company-deck-skill-build`") which only covered one specific case. Pitfall 26 is the class-level rule.
- **Related**: this is the same class of error as the user's "你**没**主动加载 skill 或读文件" feedback pattern from earlier sessions — agent states a thing about a file without reading the file.

## Pitfall 22: When the user says "I already did X", still verify — but NARRATE that you're verifying, don't verify silently

- **Symptom (observed 2026-06-12)**: user says "你已经推送完成了吗 完成了" in response to "did the push go through?" The agent took the user's word, wrote "✅ 推送成功" and skipped verification. A few turns later, the server's `/opt/resume-optimizer` was found to still have the OLD code — the push had actually failed (`Permission denied (publickey)`), the user's "是的 完成了" was about a DIFFERENT action (probably a different repo or context).
- **The right pattern**: when the user asserts completion of a critical step, do NOT silently trust. **Verify, and narrate the verification.** Something like:
  > "你说推送完成了 — 让我用 `git log --oneline origin/main..HEAD` 实测确认下，避免我假装已推。"
  
  This (a) is the truth-telling pattern the user has explicitly asked for (the user's MEMORY is full of "别装" / "验真" / "实测"), (b) catches the case where the user is misremembering or the action failed silently, (c) costs 1 second.
- **What NOT to do**: skip verification because "the user said so" and report success without checking. The 2026-06-12 case cost ~20 minutes of "deploy is broken, why isn't the fix working?" debugging on the server side that would have been caught instantly by `git log --oneline -1` on the dev box.
- **The class of actions that ALWAYS need verification, even if the user said they did it**: file push / pull, deployment, build, config change, credential rotation, database migration, anything that has a "did it actually land" question. **Reads are OK to trust** (the user is unlikely to be wrong about something they just saw).
- **Related**: this is the opposite of Pitfall 20 (agent falsely claimed a skill was loaded). Both are "agent stated a thing without checking." The fix is the same: always verify, narrate the verification, never silently trust.
- **User pattern reinforcement**: the user has a high "don't fake it" / "验真别装" preference. The right framing when verifying is **"let me double-check this is actually done"**, NOT "I don't believe you, let me check." The first is diligent; the second is confrontational.

## Pitfall 27: After a successful deck, the user may want to ship the skill to clients — repo README must already contain the actual style sample images, not a "generate to see" workflow

- **Symptom (observed 2026-06-13)**: user said "推荐给客户看的页面最好是仓库有了 这样用户就不用再花钱又生成一次 才能看到你推荐的页面效果". Translation: the GitHub repo's README / landing page is what the client sees FIRST — it must show the style options visually WITHOUT requiring them to install the skill and pay for image-gen calls. If the repo is "install.sh → then run the skill → then pay $5-30 to see what you get", the client bounces.
- **Why this matters at the class level**: any "ship a skill publicly" workflow has the same problem. The repo is the sales page. Images cost money. The user is asking: "make the sales page show the product without a paywall."
- **The fix — README must include real sample images, 4 steps**:
  1. **At the end of the deck run, BEFORE pushing the repo, copy 3-5 of the generated PNGs to `examples/`** in the build directory. Pick: (a) the cover (the chosen one, the "this is what your cover looks like" hero), (b) 2-3 contrasting content pages (a text-heavy one + a photo-heavy one), (c) optionally an anti-pattern / "what NOT to do" if you made one.
  2. **Write the README to embed those images inline** with `![description](examples/<filename>.png)` — NOT a "see `examples/` folder" link. Inline rendering is what makes the GitHub page visually convincing. The user clicked on a repo expecting to see something, not to navigate to a subfolder.
  3. **At the top of the README, include the `<!-- AI-AGENT-META -->` block** with: install command, trigger keywords, one-paragraph TL;DR. See `references/leadership-deck-style-rules.md` for the meta-block template pattern.
  4. **Size-check before pushing**: 3-5 sample images at 1-2 MB each = 5-10 MB total. This is fine for a public GitHub repo. If a single image is > 5 MB, downscale to 1280px JPEG (q=85) before commit. PNGs > 2 MB should be re-encoded with `pngquant --quality=80-90`.
- **The 5-image budget covers**: 1 cover (hero shot) + 1 contents page (so client sees the style is consistent across pages) + 2 contrasting content pages (text-heavy + photo-heavy) + 1 anti-pattern. That's enough for a client to decide "yes this style works for my use case" in 30 seconds of scrolling.
- **Anti-pattern**: "I'll let the client install the skill and run a 5-minute test generation to see the style" — the client will not. They'll close the tab. The repo is the demo. Show, don't tell.
- **Related**: this is the upstream half of Pitfall 19 ("package the workflow as a shareable skill") — 19 covers the WHY of packaging, 27 covers the HOW of making the repo a sales page. Both must be true for the skill to be useful to non-author users.

## Pitfall 28: When recommending / pushing a skill to a client, match the skill to the SCENE, not the SKILL NAME — a 政企 leadership deck should NEVER get a HUD-style skill, even if the user asked for "a PPT skill"

- **Symptom (observed 2026-06-13)**: user pushed `company-deck-c1-hud` (a HUD-霓虹风格 specialized skill) to a client who had a 领导汇报 use case. The client ran the skill and got deep-blue-black + 电光蓝霓虹 + HUD 仪表盘 — entirely wrong tone for a 党政/央企 audience. User's response: "我昨天都还给客户发错了 他说他一用生成的就是这个科技类的 误会了 我都误会了." The user themself got confused, then shipped the wrong skill to the client.
- **Why this is a class-level pitfall (not a one-off)**: there are now at LEAST TWO skills that could be "the PPT skill" — the specialized `company-deck-c1-hud` (HUD style) and the generalist `ppt-content-to-deck-image-first` (3-phase loop, no locked style). They are NOT interchangeable. Picking the wrong one ships a deck in the wrong tone, and the user discovers it AFTER the client already ran it.
- **The fix — scene-first, not skill-first, 4 steps**:
  1. **Before recommending a skill to ANY external user, ask the user 2 questions**: (a) "谁会看这份 PPT?" (audience: 领导 / 客户 / 投资人 / 公众 / 同事), (b) "你想要什么调性?" (tone: 正式 / 创新 / 科技 / 国潮 / 简洁). The answers determine the style, which determines the skill.
  2. **Map scene → skill** (this is the lookup table you should embed in your reasoning):
     - 领导汇报 / 政企 / 党政 / 央企 / 国企 / 严肃场合 / 不要花里胡哨 → **`ppt-content-to-deck-image-first`** (generalist) + load `references/leadership-deck-style-rules.md` in Phase 0. This is the DEFAULT for any business use case unless the user explicitly says "科技感" / "未来感" / "创新风".
     - 路演 / 投资人 / 科技公司产品发布 / 无人机 / 低空经济 / 智能制造 / 数字孪生 → **`company-deck-c1-hud`** if you want a locked HUD style for consistency, OR `ppt-content-to-deck-image-first` if you want the user to pick from 3 styles.
     - 内部培训 / 团队对齐 / 工作汇报 → **`mck-ppt-design`** (McKinsey-style, no AI imagery, pure python-pptx).
     - 政府工作报告 / 国资委汇报 → `ppt-content-to-deck-image-first` + L2 palette (白底+红色+深灰).
  3. **When in doubt, ALWAYS pick the generalist** (`ppt-content-to-deck-image-first`). The generalist can produce any of the specialized skill's outputs via the 3-phase style pick. The reverse is not true.
  4. **Audit your recommendation** before sending: "I am about to recommend `X` to user `Y` for use case `Z`. Does the user need locked style, or do they need style choice?" If they need style choice, the generalist is always right. If they need locked style (e.g. 5 decks a month in the same corporate style), the specialized skill is fine.
- **Cost of the wrong pick**: client redoes 15 slides (~$15-30 in image-gen + 20-30 min of waiting), user loses face ("why did you send me the wrong tool?"), and the agent has to do a re-pick mid-stream.
- **Real session 2026-06-13**: user wanted to recommend a PPT skill to a client. User picked `company-deck-c1-hud` (HUD style, which they themselves originally built for 鲲鹏翼航 无人机路演). The client had a 领导汇报 use case. The output was wrong. Lesson: **the skill name is a clue, not a verdict. Read the skill's `description:` field to confirm the audience before recommending.**
- **Anti-pattern**: "user said '用公司介绍PPT skill' so I'll send them the one I remember — the one I built last time for a different client." Skills are tools, not mandates. Match by scene.
- **Related**: Pitfall 21 (don't use HUD for leadership) is the negative form of this. Pitfall 28 is the class-level positive rule: pick by scene, name is just a hint.

## Pitfall 29: When the same agent wrote the pitfalls in the same skill yesterday and re-violated them today, the pitfall is too soft — the next iteration must be a HARD GATE (e.g. "MUST X before Y, or refuse to proceed")

- **Symptom (observed 2026-06-13)**: the agent loaded `ppt-content-to-deck-image-first/SKILL.md` at session start. The skill already contained Pitfall 23 ("MUST vision-analyze 4-6 pages of the reference PPT before generating — not generate from your imagination"). The agent **read** the pitfall, **acknowledged** it in the chat ("I should extract first, not guess"), then **skipped** the extraction and generated from imagination anyway. Same for Pitfall 24 (logo — agent AI-imitated it instead of leaving the slot empty), Pitfall 25 (style probe — agent over-stuffed 3 content pages with full section content), Pitfall 26 (skill name vs build dir — agent had said "yes loaded" earlier without checking).
- **Why soft pitfalls fail**: a pitfall written as a "should" / "MUST" in prose is, in practice, just one more paragraph the agent scrolls past. The agent's actual decision tree at tool-call time is: "do I have everything I need? if yes, call the tool." The pitfall is decoration, not a gate.
- **The fix — make pitfalls into executable checks, 4 patterns**:
  1. **Pre-condition gate**: a pitfall that says "MUST X before Y" must include a code block the agent can verify with a 1-line check. Example:
     > "Pitfall 23 pre-condition gate: before calling `image_generate`, verify `ls references/user-reference-*.md 2>/dev/null | wc -l >= 1`. If 0, the reference PPT has not been extracted — refuse to generate, do the extraction first."
  2. **Output validation gate**: after the generation, run a vision check on the result. Example:
     > "Pitfall 24 output check: after generating cover, vision_analyze with question 'Does the top-right corner contain a recognizable version of the user's logo, or a placeholder/empty slot?' If the AI drew a fake logo, regenerate with an empty slot."
  3. **Anti-pattern as a literal refusal**: convert the soft "don't" into a "if you do this, the user's next message will be X — refuse X before it happens." Example:
     > "Pitfall 25 refusal: when user says '出 1 张看看' or '看一眼风格', do NOT generate full 4-page decks. The user's next message will be '内容太挤了' or '感觉差点'. Generate ONE cover + at most 2 sparse content references."
  4. **Self-quote check**: before submitting any Phase 1/2 batch, the agent should grep its OWN message history for keywords from the relevant pitfall ("vision_analyze", "extracted", "user-reference-*.md"). If they're absent, the pitfall was skipped — go back and do it.
- **Pattern across the 4 violations on 2026-06-13**: the pitfalls existed (21, 23, 24, 25, 26) and the agent had read them. The agent then proceeded as if they didn't apply. The fix is to make the pitfall's "MUST" enforceable in code or in the agent's decision tree, not just in prose. Any future pitfall in this skill should ship with its gate pattern.
- **Anti-pattern**: "I read the pitfalls at the top of the skill, I'll be careful" — being careful is not a check. The agent is at the limit of its short-term memory and tool sequence budget by the time it's about to call image_generate. The check must be a 1-line `ls` or a 1-question `vision_analyze`, not a memory test.
- **Real session 2026-06-13** (鲲鹏翼航 v4): all 4 violations (Pitfall 23/24/25/26) happened in the same session where the skill with those pitfalls was loaded. The fix is to embed executable pre-conditions into the next revision of the pitfalls, not to write more pitfalls.
## Files

- references/style-options.md - the 2-3 starter style directions (minimalist tech-blue / tech chinese-gold / dark data-console) with one-line descriptions and which audience each fits best. Load in Phase 0.
- references/style-library.md - **21-style** extended library with hex palettes, visual references, keyword → style lookup, anti-patterns. Load when the user wants a wider style menu than the 3 default starters. Companion to style-options.md.
- references/china-ad-law-phrases.md - the 12-15 ad-law risk phrases to flag in Phase 0, with safer rewrite suggestions. Load in Phase 0.
- references/python-pptx-stitch-recipe.md - copy-pasteable 30-line script for stitching PNGs plus text overlays into a 16:9 .pptx. Load in Phase 3.
- references/cover-prompt-template.md - the prompt template for cover generation (style-specific paragraph blocks to concatenate). Load in Phase 1.
- references/prompt-as-code-template.md - UPGRADED style blocks using 7-section atomic schema (Subject / Background / Lighting / Materials / Layout / Style refs / Negative). Preferred on Chinese third-party reseller endpoints and for Phase 2 batch generation. Load alongside cover-prompt-template.md.
- **references/pitfalls-p35-p38-open-source-publishing.md** - P35–P38 (read first if doing README + 公众号 dual-audience work): P35 reconcile references vs upload set, P36 成品示例图 vs index-card, P37 vision-verify replacement files, P38 README conversion-surface design.

- **references/pitfalls-p27-p28-p31-archive.md** - P27/P28/P31 archived (SKILL.md 已 100KB 拆出去): P27 不要为"行业+风格"建专用 skill; P28 scene-first 选 skill; P31 Phase 0 必问文字可编辑 vs full-bleed.
- **Why this is a class-level pitfall, not a one-off**: any "specialized" PPT skill that locks a style (HUD / cyberpunk / 未来感 / 二次元 / 国潮 / 党政红 / 教育绿) is wrong for the **wrong audience** install. The class-level umbrella `ppt-content-to-deck-image-first` does NOT lock a style — for any audience, ALWAYS go through the umbrella.
- **The fix — never fork a single-style skill, 3 rules**:
  1. **If you find yourself building "X-style-PPT-skill" for a single company / single style / single industry, STOP**. Use the umbrella skill's 3-phase loop (Phase 1 cover-pick) to produce the style. The user can re-trigger the same workflow in the next session.
  2. **Specialized skills are OK only for truly different workflows** (e.g. `mck-ppt-design` builds McKinsey-style decks from python-pptx primitives with no AI image-gen — fundamentally different from cover-first image pipeline). Style-locked + same workflow = NOT a new skill.
  3. **If you must publish a specialized skill to GitHub for the user to share with clients, ALWAYS archive the previous one with a clear "已被通用版 X 取代" pointer in the description, AND make the README of the new general one start with "any audience / any style, pick the right one for you" so the client can't go wrong on install**.
- **Anti-pattern**: "user mentioned a specific company / industry / style, so I'll build a skill just for that." — wrong. The same skill handles it via Phase 1 style pick. Specialized skills fragment the user's tooling and confuse clients on install.
- **Real session 2026-06-12/13** (鲲鹏翼航 v3 + v4): agent built `company-deck-c1-hud` for one company, pushed to GitHub, user shared with client who installed and got HUD-style output for what should have been a 领导汇报 deck. User said "我搞太复杂了". Archive + redirect pattern resolved it (commit `bde396b` archived old repo with redirect note, new general-purpose repo at `yaoywei/ppt-content-to-deck-image-first`).

## Pitfall 28: For "给客户/开源用" packages, add a "style showcase page" — 1 image that shows the entire style at a glance

- **Symptom (observed 2026-06-13)**: after producing 15 real PPT pages and pushing to GitHub, the user said "把不同风格的内容 搞一个大页 都给我来上一张 这个大页 就是能够最大程度的展示这个风格 内容 能做到吗 生成图片后发给我 然后上传到github". The user wanted a **single 1920x1080 image** that captures the entire visual language of a style — so a potential client browsing the GitHub repo sees the style at a glance, without clicking through 15 example pages.
- **Why this is a class-level pitfall**: GitHub repos for "design system" / "style kit" / "template package" live or die by their README preview. If the README is text-only, the user clicks away. If the README has 1 image showing "this is what you get", the user clicks "use this template". For a PPT-skill repo, that image IS the deck's visual identity.
- **The fix — produce a "style showcase page" before declaring the skill done, 5 elements**:
  1. **Top header (fixed per page in the actual deck)**: small accent square + section number + style name + thin horizontal line. Mirrors what every real page of the deck shows.
  2. **Main thumbnail (60% of page width)**: a representative page from the actual deck (e.g. a content page with photo + text, or a cover). Loaded with PIL and pasted in. NOT a new AI generation — must be a real example.
  3. **Color palette swatches (5 items)**: main background, primary, accent, secondary, text color. Each as a colored rectangle + hex/name + role description.
  4. **Element checklist (8 items)**: ✓ what this style uses (e.g. "✓ fixed page header, ✓ 60/40 image-text, ✓ certificate wall, ✓ world map texture") and ✗ what it does NOT use (e.g. "✗ no neon, ✗ no HUD, ✗ no 3D"). Color-coded (green ✓ / red ✗).
  5. **Bottom bilingual tagline**: English style name (large) + Chinese one-liner describing who it's for.
- **Implementation (PIL, ~300 lines)**: a single Python script `build-style-showcase.py` with a `STYLES` array (one entry per style with name/title_en/title_zh/ai_path/bg/accent/text/label/items/elements/tagline_zh) and a `build_one(style)` function. Output: `examples/style-showcase-{name}.png` at 1920x1080. Add the script to the repo so users can regenerate after style changes.
- **How many showcase pages to produce**: at minimum the 3 main styles the skill supports (e.g. leadership / HUD / pitch). For "open-source release" packages targeting baoyu's 21 styles, 8-11 showcase pages covers 80%+ of common use cases. More than 11 starts diluting; users want a curated gallery, not a wall of 21.
- **Why this beats the alternative (15 separate example pages)**: a single 1920x1080 image can show ALL the style's design tokens in one glance. 15 separate images require the viewer to click into each one, infer the pattern, and synthesize. The showcase page is the synthesis done FOR them.
- **Anti-pattern**: "I'll just put the 15 example images in a 5x3 grid in the README" — the user has to do the synthesis work. Bad. Build a dedicated single-image that does the synthesis.
- **Real session 2026-06-13** (鲲鹏翼航 v4): 8 baoyu style showcases + 3 in-house showcases (leadership / HUD / pitch) = 11 total. GitHub README updated to feature all 11 in a gallery grid. Each showcase is 1920x1080, ~600-1100KB. Generation: ~3 minutes per style (1 AI cover + 1 PIL script run).
- **references/leadership-deck-style-rules.md** - **leadership-review / 政企汇报** specific style guidance: when the user says "领导看" / "给领导汇报" / "政企风格" / "不要太花里胡哨", which starter styles to use, which to avoid, and the "official-tone" prompt vocabulary. Companion to style-options.md but for the conservative/formal audience. Load in Phase 0 when the user signals leadership / government audience.
- **references/pitfall-36-reference-third-party.md** - **Pitfall 36** (参考第三方风格的边界): when user says "参考 X 的风格" / "参考 X 的 readme", they mean BORROW THE LAYOUT PATTERN, not COPY THE BRAND. Distinguish (1) structural pattern (3×N grid, 5-element card) which is freely borrowed from (2) brand identity (specific palette hex, style names, decoration motifs) which is IP-protected. Includes a grep-based hard gate to audit the output. User signal: "只参考风格" is a prophylactic boundary, encode it even before the agent crosses the line.
- references/learn-from-reference-ppt.md - **the recipe to actually extract layout/color/layout-density from a reference PPT/PPTX the user pastes**. The agent MUST run this recipe (soffice → pdftoppm → vision_analyze 4-6 representative pages) before generating any cover, not generate from imagination. Covers the case where user's "look at this PPT and do the same style" instruction is given. Load whenever the user pastes a .pptx as a style reference.
- references/leadership-deck-case-study-2026-06-13.md - **the 鲲鹏翼航 v4 case study** — what went right, the 4 specific pitfall violations (23/24/25/26) and their costs, the real 湖南驰阳 reference layout, and the 5 sample images that shipped in `examples/`. Load when (a) you're about to generate a 领导汇报 deck and want a worked example to mirror, (b) you're auditing whether the current session has re-violated any pitfalls the agent already wrote, (c) you're about to push a new deck's images to a public repo and want to know which to include in the README.
- references/post-process-logo-overlay-recipe.md - **the 30-line PIL script + 2-step post-process recipe** for the case where the user provides a real logo and the agent has 15 generated 1536x1024 PNGs: (1) pad 1536x1024 → 1920x1080 with white canvas (Pitfall 11, fixes PPTX letterbox/stretch), (2) composite the same logo file at top-right of every page. The two-step pattern is a HARD GATE that enforces P24 (logo consistency) and P11 (16:9 padding) in code rather than prose. Load whenever a real logo needs to be overlaid on AI-generated slides.
- references/hard-gate-patterns.md - **the 4 patterns for converting soft "MUST" pitfalls into executable checks** (P29's fix). Includes: pre-condition `ls` gates, output vision_analyze gates, anti-pattern-as-literal-refusal framing, and self-quote grep. Load when you are about to write a new pitfall in this skill, or when you are auditing whether the current session has re-violated P23/P24/P25/P26 and need a concrete check to enforce them.
- references/pptx-overlay-text-recipe.md - **the 2-mode decision + python-pptx overlay-text code** for P31. Mode 1: full-bleed (one image per slide, text locked). Mode 2: overlay-text (image as background, real text boxes for editable Chinese). Includes a 30-line `build-pptx-overlay.py` template that adds 1-3 text boxes per slide on top of the image. **Default to mode 2** unless user explicitly says "I just need a final deck, no edits." Load whenever the user is about to ship a deck to领导/客户 and may need to tweak wording at the meeting.
- **references/github-release-large-assets-recipe.md** - **the 4-step pattern for pushing > 5 MB files (PPTX/PDF/ZIP) to GitHub via the Releases API instead of the Blob API**. Includes the size threshold check (`du -h`), the `POST /releases` payload, the upload_url template stripping, and the `Content-Type: application/octet-stream` upload. Empirically: Blob API times out at ~6 MB, Release upload handles up to 2 GB per asset. Load whenever you're pushing a generated deck artifact (.pptx/.pdf) to a skill repo.
- **references/git-push-large-repo-strategies.md** - **the 4 git-push strategies for existing 40 MB+ repos where full `git clone` times out at the 600s foreground limit**. Strategy 1: GitHub Data API 4-step (best when PAT available). Strategy 2: `git fetch --filter=blob:none` + per-file checkout (no PAT needed, works for SSH-key-only agents). Strategy 3: API-only file download (for when even fetch fails). Strategy 4: user creates empty repo, agent pushes first commit. Includes a decision tree, hard gate `curl size` check, and the 30-second recipe that succeeded on the 40.6 MB `ppt-content-to-deck-image-first` repo. Load whenever the agent needs to push 1-5 small files to a large existing repo, or whenever `git clone` times out.

## Pitfall 30: When a pitfall gets re-violated in the same skill load, convert the pitfall from prose "MUST" into one of 3 hard gate patterns — a 1-line `ls`, a 1-question `vision_analyze`, or a literal refusal

- **Symptom (observed 2026-06-13)**: P29 is the meta-pitfall: "the same agent wrote the pitfalls in the same skill yesterday and re-violated them today, the pitfall is too soft." This P30 is the **fix recipe** for P29. After re-violation, the answer is not "write more prose" — the answer is "convert to an executable check."
- **Why soft "MUST" pitfalls fail (recap from P29)**: at tool-call time, the agent's decision tree is "do I have everything I need? if yes, call the tool." A prose paragraph is not in that decision tree — it's decoration the agent scrolls past while optimizing for the next tool call.
- **The 3 hard-gate patterns (use whichever fits the pitfall)**:
  1. **Pre-condition `ls` gate** — the agent runs a 1-line shell check before the next action. Example for P23 (must extract reference PPT before generating):
     ```bash
     # Pre-condition gate: did we extract the reference PPT?
     ls references/user-reference-*.md 2>/dev/null | wc -l   # must be >= 1
     # If 0: refuse to call image_generate, do the extraction first.
     ```
     Embed this as the FIRST 2 lines of the pitfall, not at the bottom. The agent reads top-down, the gate is at the top.
  2. **Output vision_analyze gate** — the agent runs a 1-question vision check after the action. Example for P24 (logo consistency):
     > "After every image_generate, run `vision_analyze` with question: 'Does the top-right corner contain (a) a placeholder box / drawn logo / any shape, or (b) clean white space? If (a), the prompt leaked the logo slot; regenerate with the negative-instruction pattern from P24 step 2 Pattern B.'"
     This is a **mechanical check**, not a "I think it looks OK."
  3. **Literal refusal pattern** — convert the soft "don't" into "if you do this, the user's next message will be X, refuse X." Example for P25 (style probe density):
     > "When user says '看一眼' / '出 1 张' / '感觉一下' — generate exactly 1 cover + 2 sparse content pages. **Anti-pattern refusal**: if you generate 4 full-density content pages, the user's next message WILL be '内容太挤了 / 感觉差点 / 风格差点意思'. Refuse to do that. The cost of 'extra pages I can show the user' is a re-pick cycle. 3 images is the cost-aware default."
- **Audit pattern for existing pitfalls**: any time you observe the same agent re-violating a pitfall in the same skill load, the next maintenance pass should (a) add a 1-line `ls` gate at the TOP of the pitfall, (b) add a 1-question `vision_analyze` AFTER the relevant action, (c) embed the user's "I told you so" message as a literal refusal at the start. Prose is not enough.
- **The 3 patterns can stack** — a pitfall can have all three: pre-condition `ls` + output vision check + literal refusal. The redundancy is the point; one of them will fire.
- **Anti-pattern**: "I'll be more careful next time" — being careful is not a check. The agent is at the limit of its context budget by the time it's about to call image_generate. The check must be a 1-line shell command, a 1-question vision call, or a 1-line refusal — not a memory test.
- **Real session 2026-06-13** (鲲鹏翼航 v4 — second attempt after the user pushed back): agent re-violated P23 (extracted AFTER generating, not before), re-violated P24 (prompt said "empty placeholder square" → AI drew a visible box), re-violated P25 (over-stuffed 3 content pages with full section content). After the user re-pointed out the problems, the agent converted to: (a) prompt 彻底不提 logo + (b) PIL overlay 真图 in 2-step recipe. That fix is captured in `references/post-process-logo-overlay-recipe.md` and in P24 step 2 Pattern A/B/C. The next time this happens, the gate patterns from this pitfall should fire FIRST, not after the user pushes back.
- **Related**: this is the implementation of P29's "convert paragraphs to gates" thesis. P29 is the diagnosis, P30 is the prescription.

## Pitfall 31: Default to "full-bleed image per slide" locks the text — ASK the user in Phase 0 whether they want editable text (overlay) or locked visuals (full-bleed)

- **Symptom (observed 2026-06-13)**: 鲲鹏翼航 v4 15-page deck shipped with `slide.shapes.add_picture(img, 0, 0, width=prs.slide_width, height=prs.slide_height)` — one full-bleed image per slide, no python-pptx text overlay. The result: **every Chinese character is baked into the PNG**. The user can't edit "公司概况" → "公司概览" in PowerPoint, can't change a phone number, can't fix a typo without re-rendering. The agent's delivery message even had to add: **"这版每页是 full-bleed 图片，文字在图里，不是在 PPTX 文本框里。如果你要文字可编辑，要重新出"** — that "if you want editable" caveat should have been a Phase 0 question, not a delivery footnote.
- **Why this matters at the class level**: the user is a 鲲鹏翼航-style professional who delivers PPTs to领导/客户. **The default expectation is editable text** (领导 wants to tweak wording at the meeting). Shipping a locked full-bleed deck as the default is like delivering a PDF when they asked for a .pptx.
- **The 2 modes the agent must distinguish in Phase 0**:
  1. **Full-bleed mode** (default in the current skill flow): one image fills the whole 16:9 slide. Fast, beautiful, but text is locked. Use when: (a) the deck is a one-shot deliverable, (b) the user said "I just need a final deck", (c) the user provides the final text in advance and won't edit.
  2. **Overlay-text mode** (the alternative): the AI image is the **background** (left 40-60% of the slide), python-pptx text boxes overlay on the right 40-60% with REAL, EDITABLE Chinese text. Use when: (a) the user said "I'll need to edit later", (b) the user said "领导汇报" / "客户要改" / "后续还要调", (c) the deck is going to a workflow where multiple people touch the file.
- **The fix — ASK in Phase 0, before any image_generate, 3-step**:
  1. **Add to the Phase 0 alignment list (line 38 area of SKILL.md)**: a 5th question: "**文字可编辑性**：你这份 PPT 后续需要自己改文字吗？比如改公司名、改电话、改正文。需要 → 用 overlay-text 模式（图片是背景，文字是 PPTX 文本框）。不需要 → 用 full-bleed 模式（图片是整体，文字是图片里的）。" Most users will say "可编辑" — that should be the default if they don't specify.
  2. **Implement overlay-text mode in Phase 3**: instead of `add_picture` with full slide dimensions, the image is the background (added as a picture with width=slide_width, height=slide_height OR a 60% width left-side image), then `slide.shapes.add_textbox(...)` for the title, body text, and bullets. The text uses real fonts (SimSun / 思源黑体 / whatever the system has), with font sizes in points, so PowerPoint treats them as editable text.
  3. **Verify the result before delivery**: open the .pptx, click on a text box, confirm the text is editable (not a flattened image). `unzip -p file.pptx ppt/slides/slide2.xml | grep -o '<a:t>[^<]*</a:t>' | head -5` should show raw text nodes, not just image references.
- **The cost of skipping this question**: re-render the whole deck if the user later says "I need to edit". That's 15 image generations (~$10-20) + 30-60 minutes. Asking 1 question in Phase 0 costs 30 seconds.
- **Hard gate pattern (per P29/P30)**: at the END of the Phase 0 confirmation message, the agent MUST include the literal line: **"文字可编辑模式 (overlay text) 还是 full-bleed 锁定模式？默认 overlay (可编辑)，请回复确认。"** If the user doesn't reply, the agent should default to overlay mode (most common need) and tell the user it did so. Never default to full-bleed silently.
- **Anti-pattern**: agent picks full-bleed because it's "the easier thing to build" and adds a "if you need editable..." caveat at delivery. The user wanted editable by default; the agent should have asked.
- **Real session 2026-06-13** (鲲鹏翼航 v4): 15-page deck shipped full-bleed. The agent's last delivery message had to add the "如果要文字可编辑，要重新出" caveat as an afterthought. The user didn't ask for editable in the session, but a professional who delivers 15-page decks to 领导 almost always wants editable. The Phase 0 question was skipped because the agent assumed "image-first" workflow = full-bleed. Wrong assumption.

## Pitfall 32: When pushing a deck repo to GitHub, files > 5 MB go through Release upload_url — the Blob API will time out

- **Symptom (observed 2026-06-13)**: 鲲鹏翼航 v4 PPTX is 24 MB. Agent tried to push it through the GitHub Data API (`POST /git/blobs` with base64 content). At blob #6 (cover-red-diagonal.png, ~1.4 MB), got `urllib.error.URLError: TimeoutError: The write operation timed out` after 190 seconds. The first 5 blobs (small files) had pushed fine; the upload URL timeouts scale poorly with file size, even when the per-file size is well under GitHub's 100 MB blob limit.
- **Why the Blob API times out on large files**: (a) base64 encoding inflates the file by ~33% (24 MB → 32 MB POST body), (b) `urllib.request.urlopen` defaults to 60s timeout per write, (c) GitHub's blob endpoint has no streaming — it expects the full body in one write. A 32 MB single write over a slow network hits the timeout. The `github-data-api-push` skill notes the 100 MB blob limit but doesn't flag the **practical timeout** on uploads over ~5 MB.
- **The fix — use GitHub Releases for > 5 MB files, 4 steps**:
  1. **Identify the size split in your push plan**: `find . -size +5M -type f` — anything bigger is a Release asset, anything smaller is a Blob.
  2. **Push the small files via the Blob API** as the `github-data-api-push` skill instructs (blobs → tree → commit → ref).
  3. **Create a Release** (or find an existing one): `POST /repos/{owner}/{repo}/releases` with `tag_name`, `name`, `body` (markdown description of the deck), `draft: false`, `prerelease: false`. The response includes an `upload_url` template like `https://uploads.github.com/repos/.../releases/{id}/assets{?name,label}`.
  4. **Upload each large file** to the Release's `upload_url` (strip the `{?name,label}` template first, then append `?name=<filename>`): `POST https://uploads.github.com/repos/.../releases/{id}/assets?name=deck.pptx` with `Content-Type: application/octet-stream` and the raw binary as the body. This endpoint is **designed for large files** and supports up to 2 GB per asset. No base64 inflation.
- **The size threshold is 5 MB, not 100 MB**: 100 MB is the GitHub limit, but the practical timeout is much lower. Empirically: 1.4 MB blobs push fine, 6 MB blobs sometimes time out, 24 MB blobs always time out. The 5 MB cutoff is conservative.
- **Hard gate (P29/P30 pattern)**: before any `POST /git/blobs` call, run `du -h <file>` and check against the 5 MB threshold. If over, route to Release.
- **The user-facing message**: after pushing the small files + creating the release + uploading large files, send the user TWO links: the repo `commit/<sha>` URL (for the workflow files) and the `releases/tag/<tag>` URL (for the binary download). The release page has direct download links for the .pptx and .pdf that the user can hand to clients.
- **Anti-pattern**: pushing a 24 MB PPTX through the Blob API, hitting timeout, retrying 3 times, all timing out. Each retry costs 3+ minutes. The right move is to detect the size once and route correctly.
- **Real session 2026-06-13** (鲲鹏翼航 v4): first attempt pushed 18 small files (~23 MB total) successfully via Blob API, then timed out on the PPTX. The recovery was to create a Release `v1.0.0-kunpeng-v4` and upload the PPTX (24 MB) and PDF (4 MB) to `https://uploads.github.com/.../releases/{id}/assets?name=...`. Both uploads completed in <60s each. Total time: 207s for the full code + release push.
- **Related**: `github-data-api-push` skill (this pitfall updates its implicit size assumption); Pitfall 19 (package the workflow — Release is part of the packaging, especially for binary deliverables).

## Pitfall 33: README and public docs MUST be scrubbed for client-specific PII before any push — when the user says "this is someone else's privacy", they mean ALL files, not just the one they named

- **Symptom (observed 2026-06-13)**: user shipped a PPT skill repo to GitHub. README.md and 2 reference files in `references/` (leadership-deck-style-rules.md, learn-from-reference-ppt.md) all referenced real client names ("湖南驰阳介绍.pptx" as a style sample, "湖南鲲鹏翼航科技有限公司" as a real case study) — that information was in `examples/` as the real client's logo too. The user later said "README 里不能出现驰阳相关的内容 这是别人隐私了". The agent read the message as "fix README only" and proposed a minimal-change edit. The **correct interpretation** is "the WHOLE repo is leaking PII, the user is calling out the first place they noticed". A 1-grep audit revealed 5+ files with the same leak.
- **Why this is a class-level pitfall, not a one-off**: the user named ONE privacy violation, but the violation is **structural** (client-specific PII was used as illustrative content during the original skill build, leaked into 5+ files). Fixing only the named file leaves the same leak in 4 others. The user will discover this in the next PR review or when sharing the repo with a new audience.
- **The fix — PII audit before push, 5 steps**:
  1. **Build a known-PII list BEFORE pushing anything**, not after. Sources of PII to check: (a) company names mentioned in the conversation, (b) real customer's logo or photos in `examples/`, (c) reference PPT filenames the user pasted (e.g. "湖南驰阳介绍.pptx" — that's a filename, but it implies the company), (d) named individuals (team pages), (e) addresses / phone numbers / tax IDs.
  2. **Run 1 grep per PII category across the WHOLE repo, not just the file the user mentioned**:
     ```bash
     # Replace <PII> with the actual name; check README, references/, examples/, SKILL.md
     grep -rni "<PII>" . --exclude-dir=.git
     ```
     If the grep returns N>1 files, the leak is structural — fix ALL N, not just the first.
  3. **For each match, decide one of 3 actions**: (a) **delete** (the reference adds nothing once anonymized, e.g. "湖南驰阳介绍.pptx" → "参考的真实版式"), (b) **anonymize** (replace with neutral placeholder, e.g. "湖南鲲鹏翼航科技有限公司" → "真实项目（已脱敏）" or just remove the line), (c) **move to a private branch** (only if the PII is essential context, e.g. a case study that needs the company name to be useful — but this is rare for public repos).
  4. **For example images (logos, photos)**: anonymization is harder. Options: (a) **delete the example** from `examples/`, (b) **crop or blur the PII region** with PIL before pushing, (c) **replace with a generic placeholder** (a public-domain logo or a simple geometric icon). For the 鲲鹏翼航 case, the `real-logo.png` was kept but a generic "geometric icon" prompt was used in all AI-generated pages so the synthetic version is not a knockoff of the real logo.
  5. **Tell the user the audit result, not just the fix you applied**. Something like: "I found 5 files mentioning the client name (README + 2 references + 1 example). I anonymized all 5. The `real-logo.png` in examples/ is the actual logo — I can either delete it, replace with a generic placeholder, or move it to a private branch. Which do you prefer?" The audit + report pattern is what the user trusts; the silent fix is what loses trust.
- **Hard gate (per P29/P30)**: before `git push` (or any API write) to a public repo, run a PII grep:
  ```bash
  # PII audit hard gate — block push if any match
  grep -rni "<company-name>\|<project-name>\|<real-person-name>" \
    . --exclude-dir=.git --exclude-dir=node_modules 2>/dev/null
  # If non-empty: refuse to push, surface the matches to the user
  ```
  This is a 1-line check the agent should run before any push that involves code, README, or examples. The push is the moment the PII goes public — that's the gate.
- **The user's framing matters**: "这是别人隐私了" is a high-trust signal. The user is telling the agent "you leaked something I didn't notice, this is a real problem, fix it properly". The agent's job is to (a) take the signal seriously, (b) audit broadly, (c) report broadly, (d) don't argue or minimize. If the user says "just fix README", the agent should fix README AND mention "I also found X in references/ and Y in examples/ — should I fix those too?". The user often doesn't know the leak is structural; the agent does.
- **Anti-patterns**:
  - "User said README, so I only fix README" — wrong, the user is reporting a class, not a single file.
  - "I'll add a `<!-- anonymized -->` HTML comment" — the comment is not the fix; the actual PII text needs to be replaced.
  - "The example logo is essential to the demo, I'll keep it" — the demo's value is not worth the privacy violation. Replace with a generic placeholder.
  - "I'll just rename the company to '某科技公司'" — Chinese readers will still recognize it from context (industry, city, the actual logo next to it). The fix is structural, not cosmetic.
- **Real session 2026-06-13** (鲲鹏翼航 v4 → v5 push): user said "README 里不能出现驰阳相关的内容 这是别人隐私了". Agent ran the audit and found 5+ files with the leak (README 3 mentions, SKILL.md 4 mentions, 2 references files 2+4 mentions, `examples/real-logo.png` is the actual logo). Agent proposed: (a) README脱敏 3 处, (b) SKILL.md 4 处同样脱敏, (c) 2 个 references 文件 6 处脱敏, (d) `real-logo.png` 改用通用几何图标替代. User confirmed "yes fix all". Result: public repo with no client-specific PII.
- **Related**: P29/P30 (hard gate patterns — the PII grep is a pre-condition gate); P19 (package the workflow — the public repo is the package, privacy is part of the package quality).

## Pitfall 35: "出 1 张代表图" for README 开源 = STYLE INDEX CARD, not plain cover — the "low" trap

- **Symptom (observed 2026-06-13)**: user said "你不用出完 你每个风格出个具有代表性的一张图就行 最主要是风格要区分开 让别人觉得 什么都能做" — explicit goal is **README 推广 + 视觉差异 + 风格齐全**. Agent called `image_generate` with 3 plain "cover-style" prompts (one per style: cyberpunk city, chinese-ink mountain, watercolor sun). User replied **"但是这几张效果看起来很low啊 你参考一下baoyu的readme 看一下"**. The agent's plain covers LOOKED fine in isolation, but **the user judges them as a 3-row README gallery** — and 3 plain covers side by side is uniform-low-density, not designed.
- **Why this is a class-level pitfall, not a one-off**: agent's mental model was "user said '1 image per style' = 1 prompt per style = 3 plain covers". User's mental model was "this is going in a README gallery, so each image must be a **baoyu-style high-density style index card**" (thumbnail + swatches + checklist + tagline). The agent confused "1 image per style" (count) with "high-density per cell" (density). Different metrics. Same prompt count, very different result.
- **The right read of "出 1 张代表图"**:
  - **Count**: 1 image per style ✓
  - **Density per image**: each image must include **5 elements** (header + thumbnail + 5 swatches + element checklist + bilingual tagline) — see `references/style-showcase-page-recipe.md` "5 elements" section
  - **Layout density benchmark**: each image should look like a baoyu `screenshots/xhs-images-styles/cute.webp` cell, not a baoyu `examples/` cover
  - **Cross-image coherence**: when the 3 images are placed in a 3-column README grid, they should look like a **gallery of designed cards**, not a **gallery of pretty covers**
- **The fix — 4 steps before any "代表图" image_generate**:
  1. **Identify intent**: is the user building a README / 公众号 / 开源 / 推广 / sample gallery? If yes → style index card. If the user is deciding a real deck cover → plain cover (Phase 1 candidate, no card needed).
  2. **Look at baoyu first**: open `https://github.com/JimLiu/baoyu-skills/blob/main/README.zh.md` and find the `screenshots/xhs-images-styles/` table grid. The per-cell density is the target.
  3. **Use the index card prompt pattern** (5 elements: header + thumbnail + 5 swatches + checklist + tagline). See `references/style-showcase-page-recipe.md` for the prompt template + PIL build script. The image goes from "low-density cover" to "high-density design system card" by adding: 5 hex-code swatches, 6 ✓/✗ checklist items, "01 / [style-name]" header, "Education / Parenting / Wellness | 教育 / 母婴 / 心理 / 公益" bilingual tagline.
  4. **Verify cross-image coherence before delivering**: lay the 3 images side by side (PIL montage or just open them in a tab). If they look "low" as a row, increase density. If they look "designed" as a row, ship.
- **The prompt template that worked** (proven 2026-06-13 with 3 zero-typo images):
  ```
  Single 1920x1080 infographic style index card. Layout: left 60% contains a smaller embedded thumbnail of a [style-description] with [key visual elements]. Right 40% contains vertical color palette swatches (5 stacked rectangles: [hex1], [hex2], [hex3], [hex4], [hex5]) with hex codes beneath each. Below the swatches: a clean checklist of 6 style elements with green checkmarks. Top: small accent square + section number "0X" + style name "[Name]" + thin horizontal line. Bottom bilingual tagline: "[English use cases]" in English, "[中文使用场景]" in Chinese. Clean, museum-quality infographic design, professional.
  ```
  The 6 checklist items: 3 ✓ ("uses X", "uses Y", "uses Z") + 3 ✗ ("no A", "no B", "no C"). Concrete, not generic.
- **Why the agent missed this on first try**: the skill already had `references/style-showcase-page-recipe.md` (and a 5-elements template inside it). The agent loaded the skill, but did not consult the recipe — it generated from the simpler "cover prompt" pattern in the main SKILL.md. P29's "soft pitfall fails" pattern: the recipe was documentation, not a hard gate. The fix here is to make the hard gate EXPLICIT and place it at the top of the recipe file, not buried in the middle of the skill body.
- **Anti-patterns**:
  - "User said '1 image per style', so 1 prompt per style with no density layering" — wrong. The user judges the row, not each cell.
  - "I generated 3 pretty covers, they look fine in `image_generate` output" — fine in isolation, low in a gallery.
  - "I should match baoyu's 3×3 grid in PIL post-processing" — wrong, baoyu's density is **per image**, not from grid aggregation. The grid is just the display layout. Each cell must be self-sufficient.
  - "Skip the swatches/checklist, those are 'design system' details" — wrong, they are exactly what makes the cell "designed" vs "pretty".
- **Real session 2026-06-13** (鲲鹏翼航 v4 → open-source release prep): user asked "每个风格出一个具有代表性的一张图就行". Agent first tried 3 plain covers (city / mountain / watercolor). User said "low". Agent then read baoyu README and produced 3 high-density style index cards. 0 typos on all 3. User did not push back. Cost of skipping the recipe: 1 round-trip + 3 wasted image generations. Cost of using the recipe from the start: 0.

## Pitfall 34: Before "rebuilding" missing files, ALWAYS check the remote first — local file loss ≠ remote file loss, and redoing work that already shipped is a 30-60 min trap

- **Symptom (observed 2026-06-13)**: agent thought "session cleanup" had deleted all 15 locally-built style showcase pages. Agent regenerated 12 of them via PIL + AI, took 30 minutes and ~$10 in image-gen cost, only to discover (via `git fetch` + GitHub API `git log` and `/contents/`) that **all 15 files were already on the remote, shipped in commits `eee61212` and earlier**. The "rebuild" was a complete waste. Worse: the regenerated versions were **lower quality** than the original (smaller files, less detail — the original used a more elaborate PIL script that wasn't reloaded from the session memory).
- **Why this is a class-level pitfall, not a one-off**: any time the agent's local filesystem shows "missing" files, the first reaction is often "I need to rebuild" — but local file loss is not the same as remote file loss. The remote (GitHub / S3 / whatever the source of truth is) is the canonical store for shipped work. Local copies are convenience caches that can be wiped without losing the artifact.
- **The fix — verify-before-rebuild, 4 steps**:
  1. **Before any "let me rebuild X" intent, ask one question**: "is X supposed to be in a remote?" If yes, check the remote. If no, rebuild locally.
  2. **Check the remote with the cheapest possible API call**:
     - **GitHub**: `curl -sS -m 20 "https://api.github.com/repos/<owner>/<repo>/contents/<path>"` — returns the file listing + last commit SHA. 1-second call, no auth needed for public repos.
     - **GitHub commits**: `curl -sS -m 20 "https://api.github.com/repos/<owner>/<repo>/commits?per_page=10"` — 1-second, no auth, returns the last 10 commit messages and SHAs. Often the commit message tells you exactly what was shipped.
     - **GitHub specific file**: `curl -sS -m 20 "https://api.github.com/repos/<owner>/<repo>/contents/<file>"` — returns the file's base64 content. 1-second for files up to ~1 MB.
     - **Git tags / releases**: `git ls-remote <remote>` or `curl -sS "https://api.github.com/repos/<owner>/<repo>/git/refs/heads/<branch>"` — returns the current SHA of main. If this succeeds, the remote is alive and the agent can compare its local commit history.
  3. **If the remote has the file**: **STOP the rebuild**, fetch the remote file (with `curl` + base64 decode, or `git fetch` + `git checkout origin/main -- <path>`), and continue with the original. Do NOT regenerate.
  4. **If the remote does NOT have the file**: rebuild locally, but save the result to the remote FIRST this time (so a future "session cleanup" doesn't lose it again). The fix for the cleanup problem is "always push immediately, never accumulate local-only state".
- **Hard gate (per P29/P30)**: before any "rebuild", "regenerate", "redo" intent, run a 1-line remote check:
  ```bash
  # Pre-condition: does the remote actually lack the file?
  curl -sS -m 10 -o /dev/null -w "%{http_code}\n" \
    "https://api.github.com/repos/<owner>/<repo>/contents/<path>"
  # 404 → remote lacks the file, rebuild is justified
  # 200 → remote has the file, abort the rebuild, fetch it
  ```
  This is a 1-line `curl` that costs <1 second. The rebuild it prevents costs 30-60 minutes and $5-20 in image-gen costs.
- **The cost asymmetry**: a 1-second `curl` check vs a 30-60 minute rebuild. The 1-second check is **always** worth it, even when the agent is 99% sure the rebuild is needed. The 1% case is "the file is already on the remote, you don't need to rebuild" — that's 30-60 minutes saved.
- **Anti-patterns**:
  - "I lost the local files, let me rebuild them" — check the remote first.
  - "I don't have a token, I can't fetch the remote" — public GitHub repos don't need a token for read. `curl` works.
  - "I'll rebuild and just push when done" — the original version may have been better than what you'd rebuild (more elaborate PIL script, more visual detail). The remote is the canonical version, not your reconstruction.
  - "The user said 'redo it', so I redo it" — the user's "redo" intent is based on their (incorrect) belief that the work is lost. The right move is "let me check the remote first" — and if the work is there, show the user "it's already on the remote, here's the link".
- **Real session 2026-06-13** (baoyu-styles-export push): agent thought the 15 style showcase pages were "lost in session cleanup". Spent 30 minutes regenerating 12 + 3. Then ran `git log --oneline` against the remote via API and discovered commits `eee61212` and earlier had all 15 already shipped. The regenerated versions were smaller (78KB vs 651KB for `leadership`) — the original used a more elaborate PIL script that wasn't in the agent's working memory. Lesson: the **local memory of the session is not the canonical store**; the **remote repo is**. Always check the remote before rebuilding.
- **Related**: P22 (user says "I did X" → still verify) is the same class — "the truth is in the system state, not in the user's (or agent's) memory". This pitfall generalizes P22 to the local-vs-remote filesystem case.

## Pitfall 35: For open-source publish (README samples + 公众号), the 5-element "abstract index card" is the WRONG pattern — use the 2x2 "成品示例图" recipe, vision-check for Chinese text bugs, batch Feishu sends 4-per-message

- **Symptom (observed 2026-06-13)**: agent generated 3 abstract style index cards (Cyberpunk Neon / Chinese Ink / Watercolor Soft) following the existing `references/style-showcase-page-recipe.md` pattern. User's response: **"这几张效果看起来很low啊 你参考一下baoyu他那些风格嘛"** + later **"这就好太多了 然后我需要十几个不同的风格"**. The "好太多了" came from the 2x2 finished-example pattern, NOT from the abstract cards.
- **The fix (full recipe)**: see `references/open-source-publish-recipe.md` — covers (a) the 12-style batch table, (b) the 2x2 finished-example prompt template, (c) the 4 recurring Chinese-text bugs in AI image-gen with the vision-check gate, (d) the Feishu 4-images-per-message batching rule, (e) the README 3-column grid layout, (f) the full-repo PII 脱敏 gate.
- **The 3 sub-lessons at a glance**:
  1. **Abstract card fails, finished example wins** — 4-card with real content (e.g. "银行服务 / 4 大产品线" with 4 real bank products) > style-name + 5-swatch + 6-item checklist
  2. **AI 4 text-bug cluster** — 日/良, 晒/光, 购/曝, PA colon. vision-check EVERY card with a "specific character" question. Re-prompt with "must be exactly X (not Y)" form for any risky term
  3. **Feishu batch sends** — `send_message` caps at ~4 media per call. K = ceil(N/4) sequential calls, not parallel

---

## Technical Pitfalls (consolidated from `ai-ppt-image-generation`)

These are the image-generation-engineering pitfalls that came from a sibling skill that was archived into this one. The class is the same — the focus shifts to **how `image_generate` and `vision_analyze` actually behave under load** rather than workflow / publishing decisions.

### Technical Pitfall 1: `image_generate aspect_ratio="landscape"` returns 1536x1024 (3:2), NOT 1920x1080

**Symptom**: The assembled `.pptx` (or PDF export) has visible top/bottom **black bands** OR the image is visibly stretched vertically. The user reports "pdf 版看着有些图片比例不太对" (PDF version, some images look wrong aspect ratio).

**Cause**: `image_generate` with `aspect_ratio="landscape"` returns a **1536x1024** image (3:2 ratio, not 16:9). The "landscape" string is a hint, not a strict size contract. PowerPoint slide is 13.333"×7.5" = 16:9 (1.7777).

**Detection**: After staging PNGs, run `identify p1.png` to confirm pixel dimensions before building the .pptx. 1536x1024 = 3:2. Anything other than 1920x1080 (or 3840x2160 etc. with the same 16:9 ratio) needs padding.

**Fix — PIL padding (preferred, preserves all content)**: Resize 1536x1024 → 1620x1080, then pad left+right with 150px each side of the page background color (`#050810` for dark data-console decks) to reach 1920x1080.

```bash
convert p1.png -resize 1620x1080 -background "#050810" -gravity center -extent 1920x1080 p1_padded.png
```

- **DO NOT crop** (e.g. crop 1536x1024 to 1536x864 by removing 80px from top + bottom) — this **loses content at the top of the page**, including brand names / URLs / English subtitles.
- **DO NOT stretch** (e.g. resize 1536x1024 to 1920x1080 directly) — this distorts everything, especially circular UI elements and text proportions.
- **Always verify by vision** after padding: `vision_analyze` the padded image and confirm (a) no content lost, (b) left/right padding is ~7% each side and acceptable.

Use the `scripts/pad_to_169.py` helper (supports `--only N` for single-page re-padding).

### Technical Pitfall 2: Pillow `optimize=True` HANGS on batch PNG padding

**Symptom**: The padding script that worked for 1-3 pages hangs for 15+ minutes (or runs out of memory) when padding a full 15-page batch.

**Cause**: Pillow's PNG optimizer is single-threaded. `img.save(out, "PNG", optimize=True)` on a 1920x1080 full-resolution PNG can take 30-60+ seconds per page. On 15 pages, that's 7-15 minutes — long enough for the agent to look "stuck" to the user.

**Fix**: Pass `optimize=False` (or omit it — it defaults to False):

```python
img.save(out, "PNG")  # NOT optimize=True
# Or, if you must optimize for size, do it in parallel with multiprocessing.Pool
```

### Technical Pitfall 3: Pillow >= 9.1 moved `LANCZOS` to `Image.Resampling.LANCZOS`

**Symptom**: Code uses `Image.LANCZOS` (old API) — runs fine on Pillow 9.0 and earlier, but Pyright reports `"LANCZOS" is not a known attribute of module "PIL.Image"`. The code is actually correct.

**Cause**: Pillow 9.1+ moved resampling enums to `Image.Resampling.LANCZOS` and emits `DeprecationWarning` for the old path. The old path still works in 9.1-9.2 but is removed in Pillow 10.

**Fix — try/except dual-path pattern**:

```python
try:
    LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # Pillow < 9.1
    LANCZOS = Image.LANCZOS
```

Then use `LANCZOS` everywhere in the script. Works on every Pillow version and silences Pyright.

### Technical Pitfall 4: `vision_analyze` rejects images > ~2MB with "image_url unknown variant" HTTP 400

**Symptom**: After Phase 4, you call `vision_analyze` on the full-size padded PNG (1920x1080, ~1.5-2MB) and get back an HTTP 400 error with body `"image_url unknown variant"`.

**Cause**: Some vision backends have a payload size cap (commonly 2MB) on the image_url attachment. The 1920x1080 PNG from the padded batch is at or over that cap, especially with CJK content (which compresses worse than English text).

**Fix — ImageMagick resize before vision**:

```bash
# Downsample to 1024x768 first (well under 2MB) for vision QA:
convert p1.png -resize 1024x768 p1_vision.png
vision_analyze p1_vision.png "..."
# Use the original 1920x1080 only for the final .pptx stitch.
```

**Why not always run at 1024x768?** The user wants the final 1920x1080 in the deck. The 1024x768 is only for the vision QA loop where pixel-perfect rendering doesn't matter — the QA question is "is the CJK correct? does the layout work?" which survives the downscale.

### Technical Pitfall 5: "One image per round" conversation stall

**Symptom**: Mid-pipeline, the user sends "卡住了？" or "能接着继续吗" — meaning they think the agent has stalled.

**Cause**: The agent sent one image via `send_message`, waited for "看到了吗", sent the next, etc. From the user's perspective, this looks like a hung process.

**Fix**:
- **For style-probe phase** (3 cover candidates): generate all 3 in one round AND send all 3 in one assistant turn (3 separate `send_message` calls in one tool block, all in parallel). User sees them all arrive together.
- **For batch page delivery** (P5-P15 after style lock): send **all the page images in one tool block** (multiple `send_message` calls in parallel), not one at a time.
- **One image at a time is only OK** for the very first cover (P1) when the user is asked to verify CJK rendering on that single page before committing the rest.

### Technical Pitfall 6: Feishu `send_message` returns `success: true` but attachment silently fails

**Symptom**: Agent calls `send_message(action="send", message="...MEDIA:/path/to/file.html...")`, gets back `{"success": true, "message_id": "om_xxx"}` — but user reports "没拿到" (didn't get it).

**Cause**: Feishu's `send_message` API reports success at the API layer but the actual attachment upload/delivery can silently fail for `.html`, `.zip`, and sometimes large `.pptx` files. The user sees nothing in the chat.

**Detection**: User explicitly says "没收到" / "没收到" / "I didn't get it" / "I don't see the file" / "couldn't download". This is the only signal — the API itself never reports failure.

**Fix — never trust the API success flag for attachments**:
1. After sending any file via `MEDIA:`, **always follow up with a text message asking "你收到了吗?"** in the same assistant turn (or next turn if the same channel).
2. If the user says "没收到", switch to a different delivery path:
   - **Different file type**: `.html` → try `.zip` (via Python `zipfile` since `zip` CLI is often missing)
   - **Different content type**: HTML source code → base64 in chat text (ugly but works for small files)
   - **Screenshot fallback**: when HTML is the desired content but delivery fails, render the HTML with Playwright and send static PNGs instead
   - **Server path with scp instructions**: `scp ubuntu@server:/path/to/file ./` — works if the user has SSH access
3. **Never retry the same `MEDIA:` send with the same file path** — same failure mode.

**Verification trick**: send a tiny test file (1 KB text file) first to confirm the attachment channel works for this session, before sending the real 43 KB HTML.

### Technical Pitfall 7: Vision can garble CJK near-miss characters in its reply

**Symptom**: The agent calls `vision_analyze` on a Chinese-heavy image, gets a response that includes a phrase like "厘米级" when the image actually says "厘米级" — two characters that share many strokes. The agent then incorrectly reports "P8 错字: 厘米级" to the user.

**Cause**: The vision model's reply is generated text — when transcribing a CJK phrase, the model can substitute a near-miss character that the human reader (or the agent parsing the reply) reads as a "typo" that isn't actually in the image.

**Fix — verify before reporting a CJK typo**:
1. **Re-ask vision with a more specific question**: instead of "is there a typo?", ask "逐字读出 <phrase> 这 N 个字, 第一个字是 A 还是 B? 第二个字是 C 还是 D?" — multiple choice, with a forced per-character answer.
2. **Cross-check the raw asset**: `pdftotext -layout file.pdf | grep <phrase>`, or `unzip -p file.pptx ppt/slides/slideN.xml | grep <phrase>`. If the raw text shows the "correct" version, the image is fine and vision just garbled its reply.
3. **If vision is consistently garbling CJK transcription, run vision on a JPEG-downsized version (Pitfall 4 resize trick)** — the smaller payload may give a cleaner reply.

**Rule**: **Never report a "typo" to the user based on a single vision read.** Always have a second source. The cost of a false positive (user trust erosion + needless "fix" cycle) is much higher than the cost of one extra verification step.

### Technical Pitfall 8: `/tmp/` and session-scoped scratch directories get cleaned mid-session

**Symptom**: Agent builds a deck or asset batch under `/tmp/<slug>/` or `/home/ubuntu/<tmp-dir>/`. After a `git push` failure or session-event handler runs, the entire directory is gone. The agent then says "⚠️ directory not found" and has to redo all the work.

**Confirmed 2026-06-13 on a 12-page baoyu styling batch**: 11 generated `*-styling-page.png` + 8 AI `*-preview.png` + PIL script vanished between turns. The session rolled over a cleanup boundary. Only the `~/.hermes/cache/images/` (gpt-image-2 source output) survived.

**Fix — put long-lived work under `/home/ubuntu/projects/`, not `/tmp/`**:
1. Default to `/home/ubuntu/projects/<skill-or-project-slug>/` as the working tree.
2. `/tmp/` is only for truly ephemeral scratch (downloads, build artifacts you'll never want to keep). Never use `/tmp/` for outputs the user will see, push, or want back.
3. For git projects: `cd /home/ubuntu/projects/<slug>` → `git init` → add files → commit. Git history survives session cleanup even if the working tree doesn't, so the next session can re-create the working tree from the remote.
4. After every successful batch, **commit immediately** (local commit is fine if push is uncertain). The .git/ directory lives in the same dir as the work — if the dir is cleaned, the .git is too, but at least the commit step is one command away from being saved.

**For AI-generated source PNGs**: `image_generate` puts outputs in `~/.hermes/cache/images/` (the Hermes-managed cache). This survives sessions. For PIL composition that combines these PNGs, save the composed output to `/home/ubuntu/projects/`, not `/tmp/`.

### Technical Pitfall 9: User wants to change just one page of an already-shipped deck

**Symptom**: After the deck is built and delivered, the user says "第 7 页改一下" or "I want to swap the cover" or "use the other cover style on P3".

**Cause**: The default workflow is whole-batch. If the user wants to change one page, the obvious wrong move is to re-run the whole 15-page pipeline, which wastes 5-10 minutes and risks the user seeing drift on the pages they liked.

**Fix — single-page regenerate with `scripts/check_state.py --only-page N`**:
1. Locate the deck: `cd ~/path/to/deck-output/<slug>-<ts>/`
2. Run `python scripts/check_state.py --only-page 7` — it tells you exactly which file to edit (`prompts/07-xxx.md`) and the 5 commands to run in order.
3. Edit only the relevant prompt. Re-run image_generate. Save the output as `images/p7.png` (overwrite).
4. Re-pad just that page: `pad_to_169.py images images-padded --only 7`
5. Re-build the .pptx pointing at the padded dir (it picks up the new p7.png + all the unchanged p1-p15.png).
6. Re-export PDF with `soffice --headless --convert-to pdf`.

Total wall time: 60-90s for one page (vs 5-10 min for the whole batch). The other 14 pages are byte-identical to before.

### Technical Pitfall 10: The 18 style probes are a sunk cost — archive, don't delete

**Symptom**: After generating 18 style candidates (the over-generation pitfall), the user complains "不要出那么多吧 浪费钱啊" (don't make so many, waste of money). The obvious wrong move is to delete the 18 images.

**Why archive instead of delete**:
1. The 18 images are a one-time sunk cost — the user has already paid for them.
2. Next deck / next company will need style probing again — without a library, the user pays the full 18-image cost again.
3. The 18 probes ARE the style library — they already span the design space (minimalist / gold / dark-data / blueprint / glass / watercolor / morandi / etc.). Curating them is essentially free.
4. Re-running them with the same prompts gives visually consistent results — the library is reusable.

**Fix — archive as `style-library/` asset**:
1. After the user picks one style and the deck ships, ask one question: *"要把这 18 张对比图归档为风格库吗? (一次性投入, 以后做别的 PPT 直接复用, 不再花 18 张的钱)"*
2. If yes: `mkdir -p ~/path/to/style-library/` + `cp -r <deck-output>/style-comparisons/* <library>/` + write `README.md` index card with letter / name / palette / best-for tags.
3. Update skill's `references/style-options.md` to point to the local library path (so the next session can `ls` it before deciding to generate new probes).
4. **Cost savings**: 18 images × ~$1.5 = $27 saved per future deck. Pays back after 1 future deck.

### Linked scripts and references from the merged skill

- `scripts/pad_to_169.py` — Pad 1536x1024 → 1920x1080 (150px-each-side black bar). Use `--only N` for single-page.
- `scripts/build_pptx.py` — Assemble padded PNGs into a 16:9 .pptx (one full-bleed image per slide, blank layout).
- `scripts/check_state.py` — Multi-state checkpoint tool: `--check`, `--status`, `--resume`, `--only-page N`, `--find-decks`. For "where am I?" during long sessions.
- `scripts/batch_styling_page.py` — Batch the styling-page generation.
- `scripts/reveal.py` — Reveal script for previews.
- `references/pptx-pdf-assembly.md` — Full .pptx assembly + PDF export playbook.
- `references/vision-resize-workaround.md` — The ImageMagick one-liner + error transcript.
- `references/cjk-qa-checklist.md` — Per-page verification checklist + the "should I re-render?" decision tree.
- `references/styling-page-pil-template.md` — PIL template for styling-page composition.
- `references/html-animated-deck.md` — The 1300-line single-HTML animated deck pattern.
- `references/prompt-as-code-8block-legacy.md` — Older 8-block Prompt-as-Code template (S1/S2/S3 styles). Use the upgraded 7-section `references/prompt-as-code-template.md` for new work.
