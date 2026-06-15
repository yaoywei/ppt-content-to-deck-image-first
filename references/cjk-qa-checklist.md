# CJK QA Checklist (per page, post-generation)

After batch-generating N PPT images with GPT-Image-2, run this checklist on each page. It assumes `vision_analyze` is available and you have applied the `vision-resize-workaround.md` first.

## 1. The single-question vision prompt (copy-paste)

```
逐字读出图中所有中文文字。告诉我是否有错字/乱码/扭曲。
```

If the page has known specific text (e.g. names, numbers, addresses), append:

```
特别核对：<list the high-risk tokens>
```

The model returns a JSON with `analysis` containing:
1. A literal transcription of every visible Chinese character
2. A judgment on whether anything is misspelled/garbled/distorted
3. Style notes that are NOT errors (e.g. "X is a known synonym")

## 2. The verification table (output to user)

| Page | Title | Text status | Notes |
|------|-------|-------------|-------|
| P1  | 封面 | ✅ | — |
| P2  | 公司定位 | ✅ | — |
| P3  | 关键数字 | ✅ | "含博士2 / 硕士3" could be "含博士2人 / 硕士3人" (style) |
| P4  | 业务全景 | ❌ | "城市环境与墨霾巡检" → should be "雾霾" |
| ...  | ...   | ... | ... |

Surface the table in the assistant response so the user can re-verify.

## 3. "Should I re-render this page?" decision tree

```
Is the text materially wrong (real错字 like 墨霾 vs 雾霾, or乱码)?
├─ YES → Re-render that one page ONLY with a refined prompt
│         Do NOT re-batch the whole set.
│         Refine: add the correct characters in the [Typography] block more
│         explicitly (e.g. "城市环境与雾霾巡检 (NOT 墨霾)").
└─ NO (style nitpick like missing顿号 / spacing)
         → Surface to user as a "polish suggestion"
         → Do NOT re-render automatically. Let the user decide.
```

## 4. Common CJK rendering issues seen in this domain

| Issue | Example | Fix |
|-------|---------|-----|
| 同音字错位 | 雾霾 → 墨霾 | Use 雾 character explicitly + add "NOT 墨" in negative |
| 罕见字变常见字 | 沐函麦 → 沐函来 | Pin exact name in typography block |
| 数字变文字 | 98% → 九八% | Specify "98% (Arabic numerals)" |
| 标点丢失 | 顿号 → 空格 | Specify "、" character explicitly |
| 排版粘连 | 国家级 → 国家级高 | Add "(single line, no wrap)" constraint |
| 符号乱 | × → x | Specify "×" (U+00D7) not "x" |

## 5. When vision is unavailable

Fallback hierarchy:

1. **Try the resize workaround** (`vision-resize-workaround.md`).
2. **If vision is truly down** (balance / network / model outage): tell the user explicitly, do not silently skip. Provide direct image paths so the user can `MEDIA:` preview them in Feishu.
3. **Do not "pass" pages on hope** — the user has explicitly delegated CJK QA to vision, and the cost of a re-render is small relative to a visible错字 in a delivered deck.

## 6. Final pre-delivery checklist

Before telling the user "done":

- [ ] All N pages have a ✅ or a flagged issue in the verification table
- [ ] Any ❌ pages have been re-rendered and re-verified
- [ ] User has been shown the table (or a summary of it)
- [ ] User knows the next step (assemble `.pptx` via `powerpoint` skill, or convert to PDF, or just take the raw images)
- [ ] File paths are listed absolutely so the user / pipeline can pick them up
