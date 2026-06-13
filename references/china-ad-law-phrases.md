# China Advertising Law Risk Phrases - Phase 0 Flag List

When the user's content brief contains any of these phrases (or close variants), surface them in Phase 0 with a safer rewrite suggestion. **Do not silently rewrite** - the user is the legal owner of the text and may have a specific reason for the wording (regulatory application, official seal, etc.).

Source: 中华人民共和国广告法 (2015 修订) 第十七条 - 禁止使用 "国家级" "最高级" "最佳" 等用语. State Administration for Market Regulation (国家市场监督管理总局) enforcement 2020-2025 has extended this to corporate profiles and investor materials, not just paid ads.

## Hard no-go phrases (高风险 - usually 删掉 or 重写)

| Original phrase | Why it's risky | Safer rewrite |
|---|---|---|
| 国家级高新技术企业 | 广告法禁词. "国家级" 是绝对化用语 | 已通过国家高新技术企业认定 (或写证书编号) |
| 全球领先 / 世界领先 | 广告法第十七条 | 行业领先 / 在XX领域持续深耕 / 已服务全球10+国家 |
| 行业第一 / 第一品牌 | 广告法 | 头部企业 / 行业领先品牌 |
| 最佳 / 最优 / 最强 | 广告法第十七条 | (具体数据替代) / 已服务 50+ 头部客户 |
| 顶级 / 顶尖 | 广告法 | 资深 / 行业领先 |
| 唯一 | 广告法 | 之一 / (具体差异点) |
| 永久 / 永远 | 广告法 (绝对承诺) | 长期 / 持续 |
| 100% 满意 / 100% 有效 | 广告法 | (具体数据) / 主流客户反馈 |
| 零风险 / 万无一失 | 广告法 | (具体安全措施) |
| 销量冠军 / 销量第一 | 广告法 | (具体来源的市场数据) |

## Soft risk phrases (中风险 - depends on context)

| Phrase | Context that makes it OK | Context that makes it risky |
|---|---|---|
| 领军企业 / 龙头企业 | Government-issued certification (工信部 / 行业协会 颁发) | Self-claim without backing |
| 高新技术企业 | Has the official certificate (write 证书编号) | Self-claim |
| 知名企业 / 知名品牌 | Industry-recognized (有数据支持) | Self-claim |
| 高端 / 顶级 | Actual product spec (e.g. 军工级芯片) | Marketing puffery |
| 第一家 / 首个 | Factual first (with citation) | Marketing claim |
| 最大 / 最高 / 最广 | Verifiable metric with source | Self-claim |

## Phrases to check for factual backing

- "服务超过 X 家 500 强企业" - need a verifiable client list
- "覆盖 X 个国家" - the actual count, not inflated
- "X 年行业经验" - actual years, not rounded up
- "团队规模 X 人" - actual headcount, not aspirational
- "获得 X 项专利" - actual patent numbers, not "多项"

## Output to the user in Phase 0

When you detect these, format your warning like:

> ⚠️ 广告法风险提示 - 以下表述在正式路演 / 政企材料中可能踩到《广告法》第十七条（绝对化用语禁令）。建议在 PPT 中改写为：
>
> 1. "国家级高新技术企业" → "已通过国家高新技术企业认定（GR2024XXXX）"
> 2. "全球领先" → "已服务全球 10+ 国家"
> 3. "行业第一品牌" → "低空经济领域头部企业"
>
> 你确认哪些改写、哪些保留原意？这一轮定下来，后续 PPT 全部按这个版本出。

Keep it tight - one message, not a 12-section audit. The user can ask for a deeper scan if they want.

## When the user says "违禁词 自动帮我改掉" (auto-fix ad-law phrases)

Some users (notably THIS user's default) want the ad-law rewrites applied **silently** rather than surfaced for confirmation. For these users:

1. Skip the Phase 0 "warning + ask for confirmation" loop entirely.
2. Apply the safer rewrites from the table above directly in the Phase 1 / Phase 2 / Phase 3 output.
3. Drop a one-line audit trail in the **PPTX 备注页 (notes)** of each affected slide, e.g.:
   > 备注：本页"国家级高新技术企业"已自动改写为"已通过国家高新技术企业认定（GR2024XXXX）"。原表述见源文档第X段。
4. After the deck is delivered, send a one-message summary listing every auto-rewrite, so the user can spot-check and decide whether to also update the source brief.
5. Save this user preference in MEMORY.md (user profile) so future sessions start with the silent-rewrite default.

Other users (who don't explicitly ask for silent auto-rewrite) keep the default surface-and-confirm flow above.
