<!-- AI-AGENT-META-START -->
<!--
skill: ppt-content-to-deck-image-first
description: 中文公司宣传 PPT 一键生成（领导汇报 / 路演 / 政企 / 党政 / 央国企），3-phase cover-pick loop，不锁风格。
install: curl -fsSL https://raw.githubusercontent.com/yaoywei/ppt-content-to-deck-image-first/main/install.sh | bash
triggers: "用 ppt-content-to-deck-image-first 风格做 PPT", "给领导看", "领导汇报", "政企风格", "参考这份 PPT 的风格", "做成 PPT", "首图选风格", "公司简介 PPT"
audience: 中文公司 (路演 / 政企 / 党政 / 央国企 / 商业计划 / 项目介绍)
tldr: 输入公司内容，AI 出 3 张候选封面让你挑，再批量出剩下 10-15 页，最后拼成 .pptx/.pdf。风格不锁 - 路演能做出科技霓虹感，领导汇报能做出白底+深蓝+金/红的稳重感。引用了湖南驰阳介绍.pptx 这种真实版式作为参考。
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

### 1. 领导汇报 / 政企 / 党政风格（**白底 + 深蓝 + 红 + 斜切**）

**适用场景**：给领导看、给客户做汇报、央企/国企/政府汇报材料

**真实案例**：湖南鲲鹏翼航科技有限公司（无人机 / 低空经济），**4 张样图**：

**封面（红色斜切色块 + 大标题 + 右侧实景图）：**

![封面](examples/cover-red-diagonal.png)

**P2 公司概况（左图右文 50/50 + 固定页眉）：**

![公司概况](examples/p02-company-overview.png)

**P3 使命定位（3 段 label+body 块，无装饰）：**

![使命定位](examples/p03-mission-positioning.png)

**P4 资质荣誉（证书墙 2 行 3+5）：**

![资质荣誉](examples/p04-qualifications.png)

> **风格来源**：参考了《湖南驰阳介绍.pptx》的真实版式（红色斜切色块、淡世界地图背景、固定页眉、50/50 左图右文、证书墙）。**不是凭空猜的** —— 见 `references/learn-from-reference-ppt.md`。

---

### 2. 科技 / 路演 / 投资人风格（**深色底 + 电光蓝 + HUD 仪表盘**）

**适用场景**：路演、给投资人看、科技公司产品发布、无人机/低空经济

> **注意**：本 skill 的默认 3 张候选封面里**包含**这种风格，**但不会自动锁定**。如果你说"给领导看"，AI 会跳过这种风格，直接出政企风候选。

---

### 3. 反面教材（**别这样出领导汇报 PPT**）

**agent 凭空猜的"领导汇报"封面**（错 6/7 维度：用了蓝金、深底没地图、logo 错位、文字密度过大）：

![反面教材](examples/anti-pattern-blind-guess-blue-gold.png)

**为什么错**：没看用户给的参考 PPT，**凭"中国领导汇报 PPT 是什么样"的训练均值猜**。**真实领导汇报 PPT 跟均值差很多**。

**正确做法**：见 `references/learn-from-reference-ppt.md` —— 用户给参考 PPT 时，**必须先 vision 提取 4-6 页版式**（pptx→pdf→png→vision_analyze），**再**写 prompt。

---

## 适合谁用

| 场景 | 适用 | 说明 |
|---|---|---|
| **领导汇报 / 政企 / 党政** | ✅ | 风格 L1（白底+深蓝+金）或 L2（白底+红色+深灰） |
| **路演 / 投资人** | ✅ | 风格 A（深色+电光蓝+HUD） |
| **公司宣传 / 商业计划** | ✅ | 风格 B（白底+科技蓝） |
| **项目介绍 / 产品发布** | ✅ | 视受众而定 |
| **编辑现有 .pptx** | ❌ | 用 `powerpoint-pptx` skill |
| **复刻参考 PPT 的版式** | 部分 | 见 `references/learn-from-reference-ppt.md`（提取风格而非复刻） |

---

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/yaoywei/ppt-content-to-deck-image-first/main/install.sh | bash
```

**作用**：克隆本仓库到 `~/.hermes/skills/ppt-content-to-deck-image-first/`，下次 `skill_view name="ppt-content-to-deck-image-first"` 就能加载。

**更新**：

```bash
cd ~/.hermes/skills/ppt-content-to-deck-image-first && git pull origin main
```

**卸载**：

```bash
rm -rf ~/.hermes/skills/ppt-content-to-deck-image-first
```

---

## 触发关键词

| 关键词 | 加载什么 |
|---|---|
| "做成 PPT" / "生成 PPT" / "首图选风格" | 主 skill |
| "给领导看" / "领导汇报" / "政企" | 加载 `references/leadership-deck-style-rules.md` |
| "参考这份 PPT 的风格" / "按这个风格做" | 加载 `references/learn-from-reference-ppt.md`，**先 vision 提取** |
| "路演" / "投资人" / "科技公司" | 默认 3 风格（A 极简科技蓝 / B 科技国潮金 / C 未来数据大屏）|

---

## 仓库结构

```
ppt-content-to-deck-image-first/
├── SKILL.md                                          # 主 skill（3-phase loop + 21-27 pitfalls）
├── install.sh                                        # 一键安装脚本
├── README.md                                         # 本文件
├── examples/                                         # 真实样图（不花钱就能看）
│   ├── cover-red-diagonal.png                        # 领导汇报风封面
│   ├── p02-company-overview.png                      # 领导汇报风 P2
│   ├── p03-mission-positioning.png                   # 领导汇报风 P3
│   ├── p04-qualifications.png                        # 领导汇报风 P4
│   └── anti-pattern-blind-guess-blue-gold.png        # 反面教材
└── references/                                       # 按需加载的 reference 文档
    ├── leadership-deck-style-rules.md                # 领导汇报风格规则（L1/L2/L3 + prompt 词汇）
    ├── learn-from-reference-ppt.md                   # 复刻参考 PPT 的 recipe（pptx→pdf→png→vision）
    ├── style-options.md                              # 默认 3 风格说明
    ├── style-library.md                              # 21 风格扩展库
    ├── cover-prompt-template.md                      # 封面 prompt 模板（prose 版）
    ├── prompt-as-code-template.md                    # 封面 prompt 模板（Prompt-as-Code 7-section 版）
    ├── china-ad-law-phrases.md                       # 广告法红线词 + 替换建议
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
