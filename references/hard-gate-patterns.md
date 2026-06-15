# Hard Gate Patterns — Converting Soft "MUST" Pitfalls into Executable Checks

The 4 patterns for taking a pitfall that's been re-violated in the same session and converting it from prose to a 1-line check the agent will actually run.

**The diagnosis is P29**: "When the same agent wrote the pitfalls in the same skill yesterday and re-violated them today, the pitfall is too soft." This file is P29's prescription.

## Why soft pitfalls fail (the data)

From session 2026-06-13 鲲鹏翼航 v4, the agent re-violated:
- **P23** ("must extract reference PPT via vision before generating") — read the pitfall, acknowledged in chat, then generated without extracting
- **P24** ("AI cannot reproduce a real logo, leave the slot empty") — read the pitfall, then wrote "empty placeholder square" in the prompt (which AI drew as a literal box)
- **P25** ("看一眼 style probe should be 1 cover + 2 sparse, not 4 full-density") — read the pitfall, then generated 4 full-density content pages
- **P26** ("skill name vs build directory") — read the pitfall, still conflated the two names in chat

**Pattern**: the agent scrolls past prose. The fix is to put a 1-line check at the top of the decision tree, not at the bottom of a paragraph.

## Pattern 1: Pre-condition `ls` gate (1-line shell check before action)

**Best for**: pitfalls that say "do X before Y." The gate is "have you done X?" — verifiable with a file system check.

**Template**:
```bash
# Pre-condition gate: <what must be true before proceeding>
ls <path/pattern> 2>/dev/null | wc -l   # must be >= N
# If 0: refuse to <action>, do <prerequisite> first.
```

**Examples**:

| Pitfall | Pre-condition gate |
|---|---|
| P23 (extract reference PPT) | `ls references/user-reference-*.md 2>/dev/null \| wc -l` must be ≥ 1 before calling `image_generate` |
| P11 (16:9 padding) | `ls images-padded/ 2>/dev/null \| wc -l` must be ≥ N (number of generated pages) before calling `python-pptx` build |
| P24 (logo overlay) | `ls user-inputs/logo.* 2>/dev/null \| wc -l` must be 0 (no logo provided → no overlay needed) OR the post-process script must have run (check `ls images-padded/*.png` exists) |
| P27 (README has examples) | `ls examples/*.png 2>/dev/null \| wc -l` must be ≥ 3 before pushing to GitHub |
| "Have I read the user's brief?" | the brief text should be in conversation history; if agent is about to call `image_generate` without the brief being read, refuse |

**Where to put it in the pitfall**: as the **FIRST 2 lines of the pitfall**, before the symptom/why. The agent reads top-down. The gate is at the top.

**Anti-pattern**: putting the gate at the bottom of a long paragraph ("after the agent understands the why, then it will check the gate"). The agent has already scrolled past by then.

## Pattern 2: Output `vision_analyze` gate (1-question check after action)

**Best for**: pitfalls that say "the output should look like X." The gate is "does the output look like X?" — verifiable with a vision call.

**Template**:
> "After every `<action>`, run `vision_analyze` with question: '<one specific question that maps to the pitfall's symptom>'. If the answer indicates the symptom, `<recovery action>`."

**Examples**:

| Pitfall | Output vision gate |
|---|---|
| P23 (extraction was right) | "After generating the cover, vision_analyze with: 'What is the dominant color of the page background, and is there a diagonal color block on the left? Does the title text say [user's company name]?' Compare to the reference PPT — if 3+ dimensions mismatch, the reference was not actually extracted, the agent hallucinated." |
| P24 (logo slot was left empty) | "After every image_generate, vision_analyze: 'Does the top-right corner contain (a) a placeholder box / drawn logo / any shape, or (b) clean white space? If (a), the prompt leaked the logo slot; regenerate with the negative-instruction pattern.' This is a mechanical check, not a 'I think it looks OK.'" |
| P25 (style probe density) | "After generating 2+ content pages, vision_analyze: 'What percentage of this page is white space (rough estimate)? Is there a 50%+ content block on a single page, or is the content distributed across the whole page with 40-50% white space?' If density is too high, regenerate with less content." |
| P17 (CJK typos in overlays) | "After every python-pptx overlay slide, run `pdftotext file.pdf - \| grep <expected text>` to verify the actual text is correct, NOT just vision. Vision is unreliable for CJK near-miss characters." |

**Where to put it in the pitfall**: at the **end of the pitfall, as a "verification" step**. The agent has finished the action; the gate fires before declaring done.

**Anti-pattern**: "I'll re-look at the image before shipping." That's not a check, that's a vibe. The gate is a 1-question vision call with a binary answer.

## Pattern 3: Literal refusal pattern (convert "don't" into "user's next message will be X, refuse X")

**Best for**: pitfalls that say "don't do X." The gate is "if you do X, the user's next message will be Y, refuse to set up Y."

**Template**:
> "When <trigger phrase>, **do** <minimal correct response>. Anti-pattern: if you do <wrong thing>, the user's next message WILL be '<'specific complaint>' — refuse that outcome by doing the right thing."

**Examples**:

| Pitfall | Literal refusal |
|---|---|
| P25 (style probe density) | "When user says '看一眼' / '出 1 张' / '感觉一下' — generate exactly 1 cover + 2 sparse content pages. **Anti-pattern refusal**: if you generate 4 full-density content pages, the user's next message WILL be '内容太挤了 / 感觉差点 / 风格差点意思'. Refuse to do that. The cost of 'extra pages I can show the user' is a re-pick cycle. 3 images is the cost-aware default." |
| P28 (scene → skill) | "When user says '推荐一个做 PPT 的 skill' / '发个做公司简介的工具', **do not** recommend `company-deck-c1-hud` without asking 'who's the audience?'. The next message will be '客户说跑出来是科技风, 不是我想要的'. Refuse to recommend a specialized skill without an audience check first." |
| P7 (one-shot full deck) | "When user says '直接出 15 页, 不需要选' — **refuse gently and explain why**. The next message will be '这风格我不要' after 15 minutes of waiting. The 5-min cover-pick loop is the cost-aware default." |
| P8 (send 18 images) | "When user says '多出几个风格看看' — generate **3** more, not 18. The next message will be '不要出那么多吧 浪费钱啊'. 3 probes is the cost-aware default." |

**Where to put it in the pitfall**: as a **callout box at the top** of the pitfall, with the user's likely complaint in quotes. The pattern is: "USER WILL SAY 'X' — REFUSE TO TRIGGER X."

**Anti-pattern**: "be careful not to over-generate." That's not a refusal, that's a hedge. The literal refusal names the exact user complaint as a prediction.

## Pattern 4: Self-quote grep (audit before submission)

**Best for**: post-action audit. The agent's previous turns contain the keywords from the pitfall; if those keywords are absent, the pitfall was skipped.

**Template**:
> "Before submitting any <output>, grep your OWN message history for the pitfall's required keywords. If they're absent, the pitfall was skipped — go back."

**Examples**:

| Pitfall | Self-quote keywords to grep |
|---|---|
| P23 (extract reference) | `vision_analyze`, `extracted`, `references/user-reference-` |
| P24 (logo overlay) | `user-inputs/logo`, `PIL`, `paste`, `Resampling.LANCZOS` |
| P11 (16:9 padding) | `1920x1080`, `padding`, `extent`, `target_w`, `target_h` |
| P28 (scene → skill) | `audience`, `who will see`, `scene` |
| P27 (README has examples) | `examples/`, `real sample images`, `inline rendering` |

**Implementation**: the agent scans its own conversation history. If a `vision_analyze` call for the reference PPT is missing, the pitfall was skipped. If a `paste` / `Resampling.LANCZOS` is missing from the PIL script, P24 was skipped.

**Where to put it in the pitfall**: as the **last line** of the pitfall, as a self-audit. The agent should do this audit right before declaring done.

**Anti-pattern**: "I'll think about whether I did the right thing." Thinking is not greping. The audit is `grep "vision_analyze" <history>` — a literal text search.

## The 3 patterns can stack

A pitfall can have all three patterns at once:
1. **Pre-condition `ls`** at the top (have I done X?)
2. **Output `vision_analyze`** in the middle (does the output match X?)
3. **Literal refusal** at the end (the user's next message will be Y if I get this wrong)

**Redundancy is the point.** One of them will fire even if the agent skims past the others.

## The 4th pattern (self-quote grep) is the audit

After the action is done, before declaring complete, the agent greps its own message history. If the keywords from the pitfall are absent, the pitfall was skipped. This is the meta-check.

## Reference session

- **2026-06-13 鲲鹏翼航 v4** — agent re-violated P23/P24/P25/P26 in the same session where the pitfalls existed. After the user re-pointed out the problems, the agent rewrote P24 step 2 to add Pattern A/B/C (silent / negative / anti-pattern), wrote `references/post-process-logo-overlay-recipe.md` (the mechanical 2-step fix), and added P30 (this file's parent pitfall) as the meta-rule for next time. The next time the same pitfalls get re-violated, the gate patterns from this file should fire BEFORE the user has to push back.
