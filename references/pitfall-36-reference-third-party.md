# Pitfall 36: When user says "参考 X 的风格 / 参考 X 的 readme", they mean BORROW THE LAYOUT PATTERN, not COPY THE BRAND — the boundary is technical, not aesthetic

- **Symptom (observed 2026-06-13)**: user said "但是这几张效果看起来很low啊 你参考一下baoyu的readme 看一下" (these look low, look at baoyu's README) in response to plain AI covers. Agent read baoyu's README, saw the 3×N grid of high-density style index cards, and reproduced **the visual pattern** (left thumbnail + right swatches + checklist + tagline) but with **its own** colors / brand / wording / palette choices (cyberpunk-neon / chinese-ink / watercolor-soft, NOT baoyu's 21 style names). User then said **"只参考风格"** (only reference the style, not copy) — a hard boundary the agent did NOT violate (since the agent already used its own brand tokens), but the user felt the need to draw the line explicitly.
- **The 2 things "参考 X" can mean, and how to know which**:
  1. **Technical / structural pattern** (the layout grid, the 5-element card, the PIL pre-build step) — these are **publicly reusable** patterns, no IP issue, freely borrowed. baoyu's 3×N grid + per-cell index card is in this category.
  2. **Aesthetic / brand identity** (specific color tokens like baoyu's `#FFD98A` mustard yellow, specific style names like "morandi-journal" / "aged-academia", specific decorative motifs like baoyu's signature hand-drawn dots) — these are **baoyu's brand IP**, do not copy, do not re-use verbatim.
  - **The user's "只参考风格" sentence is a CLASS-LEVEL signal that the user wants (1), not (2)**. They were looking at the *category* of pattern (high-density info card), not the *specific instance* (baoyu's 21 styles). The agent's job is to use the pattern template with **its own** brand / palette / style names / wording.
- **Why this is a class-level pitfall, not a one-off**: any "look at X for inspiration" task has this ambiguity. If the agent just *clones* X (e.g., copy the 21 baoyu style names + their exact hex codes), the result is a knock-off that damages both the agent's reputation and X's brand. If the agent over-corrects and avoids all inspiration from X, the result misses the user's intent ("I want something LIKE this, not THIS"). The middle path is: use the **pattern**, not the **content**.
- **The 4-step decision tree when user says "参考 X"**:
  1. **Categorize X into (1) structural vs (2) aesthetic**: Is what I see a layout / format / step sequence (reusable) or a brand token / name / decoration (IP-protected)? The grid, the per-image checklist, the prompt template structure = (1). The specific palette, the specific style names, the specific decorations = (2).
  2. **Borrow (1) verbatim if useful**: take the 3-column grid layout, take the 5-element card structure, take the "swatches + checklist" idea. These are all templates, not content.
  3. **Generate (2) fresh**: pick your own color palette (or the user's brand colors), your own style names, your own decorative elements. The agent already has `references/style-options.md` and `references/style-library.md` for this — use those, do not borrow X's tokens.
  4. **Tell the user explicitly which (1) you borrowed and which (2) you replaced**: "I borrowed the 3-column grid + 5-element card pattern from baoyu README, but used your brand palette (cyberpunk-neon) and our own 6 checklist items. No baoyu content was copied." This is the audit-trail pattern that prevents "did you copy X?" follow-up.
- **Hard gate (per P29/P30)**: before declaring "I learned from X", run a self-quote grep on the **output** (the README / skill files / generated artifacts) for X's signature strings:
  ```bash
  # Pre-condition: does my output contain any of X's brand tokens?
  grep -niE "<X-style-name>|<X-hex-code>|<X-signature-decoration>" <my_output>
  # If non-empty: I copied X's content, not just X's pattern. Refactor before shipping.
  # If empty: I borrowed the pattern, replaced the content. Ship.
  ```
  The grep is the audit trail. The "只参考风格" user signal means: at the grep level, your output should not contain X's fingerprints.
- **Anti-patterns**:
  - "I read baoyu's README so my output should LOOK like baoyu" — wrong. Read it for the pattern, not for the look. The look is baoyu's brand.
  - "I'll reuse the 21 baoyu style names but change the descriptions" — wrong. The names are the brand. Make your own.
  - "I'll just paste baoyu's hex codes into my swatches" — wrong. Pick a palette that matches the user's brand, not the inspiration source.
  - "User said '参考 X', so I should reproduce X as closely as possible" — wrong. User said "参考", not "复制". 参考 = inspiration from the pattern, 复制 = exact reproduction.
- **Real session 2026-06-13** (鲲鹏翼航 v4 → open-source release prep): user said "参考一下baoyu的readme" → agent read baoyu → produced 3 high-density index cards **using 3 own style names** (cyberpunk-neon / chinese-ink / watercolor-soft) with **own palettes** (baoyu has different colors per style) and **own checklist items** (not baoyu's). User then said "只参考风格" — confirming the boundary was already implicitly respected, but stating it explicitly. The user's correction here is **prophylactic** (preventing future drift), not reactive (the agent had not yet crossed the line). Both kinds of user signals should be encoded as pitfalls.
- **Related**: P29 / P30 (hard gate patterns — the grep is the gate); P19 (package the workflow — when packaging for open source, the package's README is also subject to this pitfall, do not include X's brand in the package).
