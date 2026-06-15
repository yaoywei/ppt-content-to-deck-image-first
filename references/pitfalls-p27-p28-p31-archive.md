# Pitfalls P27, P28, P31 (Archived)

These three pitfalls were originally in SKILL.md but were moved to this reference file on 2026-06-13 to keep SKILL.md under the 100KB character cap. They remain **load-bearing** for any agent using this skill.

---

## Pitfall 27: 不要为"行业 + 风格"建专用 skill, 复用通用 skill 就行 — 否则客户会装错

- **Symptom (observed 2026-06-12/13)**: agent built a specialized skill `company-deck-c1-hud` (15-page HUD-style PPT for 无人机/低空经济) as a separate repo, pushed to GitHub, and the user shared the repo with a client. The client installed the HUD-specific skill, generated a deck, and got a HUD cyberpunk style — wrong for the use case (领导汇报 / 政企 / 严肃场合). The agent had to retroactively archive the specialized skill and re-direct everyone to the general-purpose `ppt-content-to-deck-image-first`. The user explicitly said "我搞太复杂了 单独把科技类的搞成了一个 skill 昨天都还给客户发错了".
- **Why this is a class-level pitfall, not a one-off**: any "specialized" PPT skill that locks a style (HUD / cyberpunk / 未来感 / 二次元 / 国潮 / 党政红 / 教育绿) is wrong for the **wrong audience** install. The class-level umbrella `ppt-content-to-deck-image-first` does NOT lock a style — for any audience, ALWAYS go through the umbrella.
- **The fix — never fork a single-style skill, 3 rules**:
  1. **If you find yourself building "X-style-PPT-skill" for a single company / single style / single industry, STOP**. Use the umbrella skill's 3-phase loop (Phase 1 cover-pick) to produce the style. The user can re-trigger the same workflow in the next session.
  2. **Specialized skills are OK only for truly different workflows** (e.g. `mck-ppt-design` builds McKinsey-style decks from python-pptx primitives with no AI image-gen — fundamentally different from cover-first image pipeline). Style-locked + same workflow = NOT a new skill.
  3. **If you must publish a specialized skill to GitHub for the user to share with clients, ALWAYS archive the previous one with a clear "已被通用版 X 取代" pointer in the description, AND make the README of the new general one start with "any audience / any style, pick the right one for you" so the client can't go wrong on install**.
- **Anti-patterns**:
  - "user mentioned a specific company / industry / style, so I'll build a skill just for that." — wrong. The same skill handles it via Phase 1 style pick. Specialized skills fragment the user's tooling and confuse clients on install.
- **Real session 2026-06-12/13** (鲲鹏翼航 v3 + v4): agent built `company-deck-c1-hud` for one company, pushed to GitHub, user shared with client who installed and got HUD-style output for what should have been a 领导汇报 deck. User said "我搞太复杂了". Archive + redirect pattern resolved it (commit `bde396b` archived old repo with redirect note, new general-purpose repo at `yaoywei/ppt-content-to-deck-image-first`).

---

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
- **Anti-patterns**:
  - "User said '用公司介绍PPT skill' so I'll send them the one I remember — the one I built last time for a different client." Skills are tools, not mandates. Match by scene.
- **Related**: P21 (don't use HUD for leadership) is the negative form of this. P28 is the class-level positive rule: pick by scene, name is just a hint.

---

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
- **Anti-patterns**:
  - "agent picks full-bleed because it's 'the easier thing to build' and adds a 'if you need editable...' caveat at delivery" — wrong; user wanted editable by default.
- **Real session 2026-06-13** (鲲鹏翼航 v4): 15-page deck shipped full-bleed. The agent's last delivery message had to add the "如果要文字可编辑，要重新出" caveat as an afterthought. The user didn't ask for editable in the session, but a professional who delivers 15-page decks to 领导 almost always wants editable. The Phase 0 question was skipped because the agent assumed "image-first" workflow = full-bleed. Wrong assumption.
