<!-- AI-AGENT-META-START -->
<!--
skill: ppt-content-to-deck-image-first
description: 中文公司宣传 PPT 一键生成（领导汇报 / 路演 / 政企 / 党政 / 央国企 / 茶酒文旅 / 教育母婴），3-phase cover-pick loop，不锁风格。
install: curl -fsSL https://raw.githubusercontent.com/yaoywei/ppt-content-to-deck-image-first/main/install.sh | bash
triggers: "用 ppt-content-to-deck-image-first 风格做 PPT", "给领导看", "领导汇报", "政企风格", "参考这份 PPT 的风格", "做成 PPT", "首图选风格", "公司简介 PPT"
audience: 中文公司 (路演 / 政企 / 党政 / 央国企 / 商业计划 / 项目介绍 / 茶酒文旅 / 教育母婴)
tldr: 输入公司内容，AI 出 3 张候选封面让你挑，再批量出剩下 10-15 页，最后拼成 .pptx/.pdf。风格不锁 - 路演能做出科技霓虹感，领导汇报能做出白底+深蓝+金/红的稳重感，茶酒文旅做出水墨留白，教育母婴做出柔和水彩。
-->
<!-- AI-AGENT-META-END -->

# ppt-content-to-deck-image-first

**中文公司宣传 PPT 一键生成 · 3-phase cover-pick loop · 风格不锁**

---

## 这是什么

把一段**中文公司介绍文本**（500-2000 字），一键生成**10-15 页**专业 PPT，**输出 .pptx + .pdf**。

**3 阶段工作流**：
1. **Phase 0**：分析内容 + 跟用户对齐风格
2. **Phase 1**：出 2-3 张**候选封面**（不同视觉风格），用户挑 1 个
3. **Phase 2**：用挑中的风格**批量出 10-15 张内容页**
4. **Phase 3**：拼成 .pptx（python-pptx）+ .pdf

**为什么这样做**：image-gen 主观性强。**先出 1 张封面让用户挑** = 把"返工 16 张"降到"返工 1 张"。

---

## 风格样图（**直接看，不用花钱生成**）

**一句话**：覆盖 6 大常见业务场景，6 种风格各 1 张代表图 + 领导汇报 4 张真实样张，共 10 张图。

| | | |
|:---:|:---:|:---:|
| ![领导汇报](examples/cover-red-diagonal.png) | ![Cyberpunk Neon](examples/style-cyberpunk-neon.jpg) | ![Chinese Ink](examples/style-chinese-ink.jpg) |
| **领导汇报 / 政企** | **科技 / 路演** | **茶酒 / 文旅 / 国潮** |
| 白底+深蓝+红+斜切 | 深色+电光蓝+HUD | 留白+水墨+篆刻 |
| ![公司概况](examples/p02-company-overview.png) | ![Watercolor Soft](examples/style-watercolor-soft.jpg) | ![使命定位](examples/p03-mission-positioning.png) |
| **公司概况**（50/50 布局） | **教育 / 母婴 / 心理** | **使命定位**（label+body） |
| 领导汇报风 P2 | 暖色+水彩+童趣 | 领导汇报风 P3 |
| ![资质荣誉](examples/p04-qualifications.png) | ![反面教材](examples/anti-pattern-blind-guess-blue-gold.png) | |
| **资质荣誉**（证书墙） | ⚠️ **反面教材** | |
| 领导汇报风 P4 | 别这样出领导汇报 | |

> **风格来源说明**：本仓库的"领导汇报"风格参考了**一份真实政企 PPT 的版式**（已脱敏）。提取方式见 `references/learn-from-reference-ppt.md` —— 用户给参考 PPT 时，**必须先 vision 提取 4-6 页版式**（pptx→pdf→png→vision\_analyze），**再**写 prompt。
>
> **⚠️ 反面教材**：右下图是 agent 凭"中国领导汇报 PPT 是什么样"的训练均值猜的封面（错 6/7 维度），**别这样出领导汇报 PPT**。要看"对"长什么样，看上面 3 张领导汇报样张。

---

## 适合谁用

| 场景 | 适用 | 风格索引 |
|---|---|---|
| **领导汇报 / 政企 / 党政** | ✅ | 白底+深蓝+金 / 白底+红色+斜切（看上面 3 张领导汇报样张） |
| **路演 / 投资人 / 科技产品发布** | ✅ | Cyberpunk Neon（深色+电光蓝+HUD） |
| **茶饮 / 白酒 / 中医药 / 文旅国潮** | ✅ | Chinese Ink（留白+水墨+篆刻） |
| **教育 / 母婴 / 心理 / 公益** | ✅ | Watercolor Soft（暖色+水彩+童趣） |
| **公司宣传 / 商业计划 / 项目介绍** | ✅ | 视受众选风格（10+ 种可选） |
| **编辑现有 .pptx** | ❌ | 用 `powerpoint-pptx` skill |
| **复刻参考 PPT 的版式** | 部分 | 见 `references/learn-from-reference-ppt.md`（提取风格而非复刻） |

---

## 安装

**一行命令**（推荐）：

```bash
curl -fsSL https://raw.githubusercontent.com/yaoywei/ppt-content-to-deck-image-first/main/install.sh | bash
```

**作用**：克隆本仓库到 `~/.hermes/skills/ppt-content-to-deck-image-first/`，下次 `skill_view name="ppt-content-to-deck-image-first"` 就能加载。

**直接告诉 agent**（最快）：

> 请帮我安装 github.com/yaoywei/ppt-content-to-deck-image-first

**更新**：

```bash
cd ~/.hermes/skills/ppt-content-to-deck-image-first && git pull origin main
```

**卸载**：

```bash
rm -rf ~/.hermes/skills/ppt-content-to-deck-image-first
```

---

## 用法（10 秒上手）

1. **告诉 agent 你的公司内容**（一段 500-2000 字的中文介绍）
2. **说"用 ppt-content-to-deck-image-first 风格做成 PPT"**
3. **agent 会问你 3-4 个对齐问题**（受众、风格偏好、页数、是否需要文字可编辑）
4. **出 2-3 张候选封面 → 你挑 1**
5. **批量出剩下 10-15 页**
6. **拼成 .pptx + .pdf，交付**

**示例 prompt**（直接发给你的 agent）：

> 我公司是做工业无人机智能巡检的，主要客户是电网和油气管线。最近要做一份 12 页的 PPT 给南方电网的领导汇报。
>
> 请用 ppt-content-to-deck-image-first 风格做，**给领导看**所以要稳重（白底+深蓝+红+斜切那种），文字要可编辑（领导会改几个字）。

---

## 触发关键词

| 关键词 | 加载什么 |
|---|---|
| "做成 PPT" / "生成 PPT" / "首图选风格" | 主 skill |
| "给领导看" / "领导汇报" / "政企" / "党政" | 加载 `references/leadership-deck-style-rules.md` |
| "参考这份 PPT 的风格" / "按这个风格做" | 加载 `references/learn-from-reference-ppt.md`，**先 vision 提取** |
| "路演" / "投资人" / "科技公司" / "低空经济" | 默认 Cyberpunk Neon 风格 |
| "茶" / "酒" / "国潮" / "文旅" / "中医药" | 默认 Chinese Ink 风格 |
| "教育" / "母婴" / "心理" / "公益" | 默认 Watercolor Soft 风格 |

---

## 仓库结构

```
ppt-content-to-deck-image-first/
├── SKILL.md                                          # 主 skill（3-phase loop + 30+ pitfalls）
├── install.sh                                        # 一键安装脚本
├── README.md                                         # 本文件
├── build-pptx.py                                     # 拼 .pptx 的入口脚本
├── post-process.py                                   # 后处理（padding + logo overlay）
├── build-style-showcase*.py                          # 风格索引页生成脚本
├── examples/                                         # 真实样图（不花钱就能看）
│   ├── cover-red-diagonal.png                        # 领导汇报风封面
│   ├── p02-company-overview.png                      # 领导汇报风 P2
│   ├── p03-mission-positioning.png                   # 领导汇报风 P3
│   ├── p04-qualifications.png                        # 领导汇报风 P4
│   ├── anti-pattern-blind-guess-blue-gold.png        # 反面教材
│   ├── style-cyberpunk-neon.jpg                      # Cyberpunk Neon 风格索引
│   ├── style-chinese-ink.jpg                         # Chinese Ink 风格索引
│   └── style-watercolor-soft.jpg                     # Watercolor Soft 风格索引
└── references/                                       # 按需加载的 reference 文档
    ├── leadership-deck-style-rules.md                # 领导汇报风格规则
    ├── learn-from-reference-ppt.md                   # 复刻参考 PPT 的 recipe
    ├── style-options.md                              # 默认 3 风格说明
    ├── style-library.md                              # 21 风格扩展库
    ├── cover-prompt-template.md                      # 封面 prompt 模板
    ├── prompt-as-code-template.md                    # Prompt-as-Code 7-section 版
    ├── china-ad-law-phrases.md                       # 广告法红线词
    └── python-pptx-stitch-recipe.md                  # python-pptx 拼图脚本
```

---

## 与其他 skill 的关系

| Skill | 关系 |
|---|---|
| `ppt-from-template` | 复刻参考 PPT 的版式（视觉/排版细节复刻）—— 本 skill 偏向"按风格自由生成" |
| `mck-ppt-design` | 麦肯锡咨询风，**纯 python-pptx 不用 AI 生图** —— 本 skill 偏向 AI 生图 + overlay |
| `dragon-ppt-maker` | 另一种 PPT 生成路径 |
| `ppt` | 单 HTML 文件的乔布斯风演示稿 —— 本 skill 是 .pptx/.pdf |
| `powerpoint-pptx` | 编辑/读取 .pptx 文件结构 —— 本 skill 用其作为底层 |

---

## License

MIT

## 作者

[yaoywei](https://github.com/yaoywei)
