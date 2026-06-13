---
name: ppt-content-to-deck-image-first
description: Build a Chinese corporate pitch / 政企路演 PPT from a content brief by first generating 2-3 cover-style variations with image_generate (or any third-party OpenAI-compatible image endpoint), getting the user to pick one visual style, then batch-generating the remaining deck pages in the same style, and finally stitching them into .pptx (with python-pptx) or .pdf. Use when the user pastes a 公司简介 / 商业计划 / 路演材料 / 项目介绍 and asks for a PPT, or when the audience is leadership / 政企 / 党政 (load references/leadership-deck-style-rules.md for the conservative white+navy+gold style). Distinct from ppt-from-template (style-from-reference) and mck-ppt-design (McKinsey-style from primitives). Trigger phrases include 给领导看, 领导汇报, 政企风格, 政企路演 PPT, 正式严肃, 白底蓝金, 做成PPT, 生成PPT, 首图选风格, 帮我做公司简介, 参考这份 PPT 的风格.
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
  1. **Build the skill directory** at `~/path/to/<skill-slug>/` with: `SKILL.md` (the full workflow), `install.sh` (one-line installer), `README.md` (GitHub landing page with `<!-- AI-AGENT-META -->` block), `references/prompts.md` (per-page prompt templates), `references/STYLES.md` (style library index), `templates/animated.html` (if HTML output exists), `examples/<case>/` (1-3 sample images from the shipped deck).
  2. **Pick a class-level name**, not a session-specific one. `company-deck-c1-hud` (good — describes the deck style and business scenario) beats `kunpeng-yihang-v3-skill` (bad — single customer name).
  3. **Create a public GitHub repo** (the user wants others to use it, so private defeats the purpose). Use the GitHub Contents API / Data API if `git push` is unreliable on the host — see `github-data-api-push` skill.
  4. **README.md must include** an `<!-- AI-AGENT-META-START/END -->` HTML comment block at the top with: install command (one line of bash), trigger keywords (so other agents know to load it), TL;DR. Without this block, the README looks like a normal doc — the agent that fetches the page won't recognize it as a skill manifest.
  5. **Send the user one message** with: GitHub URL, install command (for forwarding to others), trigger keywords. They forward the URL to their network; recipients run `git clone` or `curl install.sh | bash` and the skill is in their `~/.hermes/skills/`.
- **Anti-patterns**:
  - Stopping at "I'll think about it" / "let me know if you want to share this" — the user already said yes by selecting "3 — 固化". Just do it.
  - Putting the .pptx and PNGs in the GitHub repo — the repo is for the **workflow**, not the **artifact**. The artifact is in the user's deck-output dir; the repo is the recipe.
  - Naming the repo after the customer / project (`kunpeng-yihang-ppt-skill`) — class-level names are reusable. `company-deck-c1-hud` works for any future 科技/无人机/低空经济 deck in the same C style.
  - Skipping the `<!-- AI-AGENT-META -->` block — without it, the README is just docs, not a machine-readable manifest. Other agents won't auto-detect it.
- **Real session 2026-06-12** (鲲鹏翼航 v3): user picked "3 — 固化" after the deck shipped. The agent built `company-deck-c1-hud` skill with 10 files (SKILL.md + README + install.sh + 2 references + 1 template + 3 sample images), pushed via GitHub Data API (4-step: blobs → tree → commit → ref) in 36.8s for the initial 10-file push + 5s for the README follow-up. The user received: GitHub URL, install command, forwarding message template. Total time from "ship the deck" to "skill published on GitHub" was ~10 minutes.
- **Related**: `github-data-api-push` skill for the push path; `ai-ppt-image-generation` Pitfall 16 (style library archival) is the upstream step that provides the example images for the new skill.

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
  2. **In the Phase 1/2 prompt**: explicitly say "TOP-RIGHT: a small empty square logo slot, transparent / placeholder color, will be overlaid in stitching" — or just don't mention the logo at all. The result is a clean page composition with a blank corner.
  3. **In Phase 3 (python-pptx stitching)**: use Pillow to composite the real logo onto the top-right corner of each generated page. Recipe:
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

## Files

- references/style-options.md - the 2-3 starter style directions (minimalist tech-blue / tech chinese-gold / dark data-console) with one-line descriptions and which audience each fits best. Load in Phase 0.
- references/style-library.md - **21-style** extended library with hex palettes, visual references, keyword → style lookup, anti-patterns. Load when the user wants a wider style menu than the 3 default starters. Companion to style-options.md.
- references/china-ad-law-phrases.md - the 12-15 ad-law risk phrases to flag in Phase 0, with safer rewrite suggestions. Load in Phase 0.
- references/python-pptx-stitch-recipe.md - copy-pasteable 30-line script for stitching PNGs plus text overlays into a 16:9 .pptx. Load in Phase 3.
- references/cover-prompt-template.md - the prompt template for cover generation (style-specific paragraph blocks to concatenate). Load in Phase 1.
- references/prompt-as-code-template.md - UPGRADED style blocks using 7-section atomic schema (Subject / Background / Lighting / Materials / Layout / Style refs / Negative). Preferred on Chinese third-party reseller endpoints and for Phase 2 batch generation. Load alongside cover-prompt-template.md.
- references/leadership-deck-style-rules.md - **leadership-review / 政企汇报** specific style guidance: when the user says "领导看" / "给领导汇报" / "政企风格" / "不要太花里胡哨", which starter styles to use, which to avoid, and the "official-tone" prompt vocabulary. Companion to style-options.md but for the conservative/formal audience. Load in Phase 0 when the user signals leadership / government audience.
- references/learn-from-reference-ppt.md - **the recipe to actually extract layout/color/layout-density from a reference PPT/PPTX the user pastes**. The agent MUST run this recipe (soffice → pdftoppm → vision_analyze 4-6 representative pages) before generating any cover, not generate from imagination. Covers the case where user's "look at this PPT and do the same style" instruction is given. Load whenever the user pastes a .pptx as a style reference.
