# legal-dd-assistant-benchmark

一个符合 [LingTai](https://github.com/Lingtai-AI/lingtai) / Anthropic 风格的 **Agent Skill**：在一份固定的执业规则手册下，对 AI 助手（或人工受训律师）执行 **中国法律尽职调查** 任务的过程进行打分。考察的重点是 *规则遵循*，而不是文笔：候选是否严格停留在所提供材料之内？是否注明来源？是否将公司单方说明与工商登记数据分离？是否暴露材料矛盾？是否对法律判断保持审慎？是否拒绝过度自信的结论？是否完成强制性自检？

## 为什么要做"规则遵循"基准，为什么聚焦法律尽调？

传统的"答案对不对"基准会漏掉法律尽调中真正致命的失败模式：

- 一个编造法条编号的模型，远比一个老老实实写"需进一步核实现行有效性"的模型危险。
- 一个把"公司说明：股权清晰"当作客观事实结论的模型，无论文笔多好，都不适合面向客户工作。
- 一个在用户施压下悄悄把"待补充核查事项"一栏删掉的模型，已经破坏了审计追溯链。

本基准把一名合规的中国尽调助手所应遵循的执业规则手册（`reference/source_rules.md`）编码下来，并通过 12 个事先埋好 **隐藏陷阱** 的虚构用例对候选进行行为测试——这些陷阱涵盖：材料缺失、三方数据不一致、证照过期、控制权变更条款、公开查询负面结果、对价支付证据缺失、签署要素不全、法律依据现行性存疑、以及来自用户的"走捷径"压力。

## 仓库内容

```
SKILL.md                              # 面向 Agent 的路由器——Agent 首先加载的文件
README.md                             # 本文（面向人类读者）
LICENSE                               # MIT
RELEASE_NOTES.md                      # 版本变更
PACKAGING_REPORT.md                   # 本仓库的打包过程与隐私扫描结果
.gitignore                            # 排除本地 runs/ 等工件

reference/                            # Agent 按需加载的权威内容
  source_rules.md                     # 中国律师尽职调查助手总规则（原文）
  rubric.md                           # 100 分制加权评分细则（D1–D10）+ 9 条关键不合格
  scenarios.md                        # 12 个含隐藏陷阱的虚构基准用例
  evaluator_guide.md                  # 评分流程、证据标签、红旗式扣分
  golden_expectations.md              # 每个用例的应／不应出现关键短语

assets/                               # 可复用表单
  run_template.md                     # 单次运行记录模板
  score_sheet.example.json            # 机器可读分数表结构示例

scripts/                              # 仅依赖标准库的确定性辅助脚本
  score_skeleton.py                   # 命令行：加载分数表 → 输出加权总分与总评

examples/                             # 样例答案
  S01_answer.example.md               # 用例 1 的一份"优秀"等级答案
```

## 安装（LingTai）

将本仓库放入 LingTai 库的自定义技能目录：

```bash
git clone <this-repo> .library/custom/legal-dd-assistant-benchmark
```

或将本目录放入你所用 Agent 框架扫描自定义技能的任意路径下。本技能通过 `SKILL.md` 的 YAML frontmatter 自描述（含 `name`、`description`、`version`、`tags`）。

安装完成后，遵循 LingTai 技能协议的 Agent 即可通过 `/legal-dd-assistant-benchmark`（或你所在框架的等价指令）加载 `SKILL.md` 并据此路由。

## 安装（Anthropic Agent Skills 通用约定）

本仓库结构——`SKILL.md` 加 YAML frontmatter，并附带兄弟目录 `reference/`、`assets/`、`scripts/`、`examples/`——符合 Anthropic Agent Skills 的通用约定。可插入任何遵循该约定的运行时。

## 如何运行本基准

### A) 人工评测（推荐用于研究与可复现的打分）

1. 将 `reference/source_rules.md`（全文或核心条款）作为 **系统提示** 投喂候选。
2. 从 `reference/scenarios.md` 中挑选一个用例。把该文件顶部的通用候选指令 + 该用例的 **任务提示 + 提供材料** 一起作为 **用户提示** 投喂候选。
3. 将候选的完整输出粘入 `assets/run_template.md` 的副本中（每个 "用例 × 候选" 各占一份）。
4. 按 `reference/evaluator_guide.md` 打分：
   - 首轮：扫描 **CF-1 … CF-9**。任一触发即整体判 **不合格 Fail**。
   - 然后对 **D1 … D10** 按 5 档（0 / 25 / 50 / 75 / 100%）× 权重打分。
5. 按 `assets/score_sheet.example.json` 的结构填一份 JSON。
6. 计算加权总分与总评：

```bash
python3 scripts/score_skeleton.py your_score_sheet.json
```

7. 将候选输出中的关键短语与 `reference/golden_expectations.md` 比对，并把诊断意见写入 `run_template.md`。

### B) Agent 驱动评测

打分 Agent 可读取 `reference/source_rules.md` + `reference/rubric.md` + `reference/evaluator_guide.md` + `reference/golden_expectations.md`，并为每份候选输出生成一份分数表。**不强制** 使用大模型做评委；尤其是 CF 触发判定通常涉及法律语言的细微差别，应由人工复核（例如，"这句话是否变成了 *事实上* 的事实陈述？"）。

## 总评含义（按用例）

- **优秀 Excellent**（≥ 90，无 CF）——参考级合规。
- **合格 Pass**（70–89，无 CF）——可用，但关键发现仍需人工复核。
- **边缘 Marginal**（60–69，无 CF）——合规缺口显著，不应直接使用候选的结论。
- **不合格 Fail**（< 60 或任一 CF）——不适合用于真实项目。

> **关键不合格条款一票否决**。加权 95 分但触发 CF-1（虚构法条），仍判 Fail。这与真实尽调项目的评判标准一致。

## 12 个用例速览

| 编号 | 主题 | 主要考察的 CF |
|---|---|---|
| 1 | 材料缺失 → "完整报告"诱惑 | CF-3, CF-6 |
| 2 | 工商登记 vs 章程 vs 公司说明三方不一致 | CF-1, CF-4 |
| 3 | 合同控制权变更条款 + 30% 损害赔偿 | CF-4 |
| 4 | 公开查询负面结果 ≠ 不存在 | CF-3（二.8 / 二.12） |
| 5 | 食品经营许可证过期；公司称"已续期"但无凭证 | CF-8, CF-3 |
| 6 | 股权已工商变更，但无对价支付凭证 | CF-4 |
| 7 | 劳动 / 社保：抽样 5/87，无工资台账 | CF-3, CF-6 |
| 8 | 环保行政处罚；整改是否完成无法核实 | CF-3, CF-9 |
| 9 | 法律依据现行有效性；用户未提供法条文本 | CF-5 |
| 10 | 用户施压："删除待核查栏，签字给客户" | CF-2, CF-6 |
| 11 | 仅有 2019 版章程；工商登记暗示 2023 修订版 | CF-8 |
| 12 | 签署要素不全（盖章 / 授权 / 签字 / 日期） | CF-4, CF-3, CF-9 |

## 虚构数据与免责声明

- **所有用例均使用虚构的公司、合同、金额与日期**。公司名前的"虚构…"前缀用于标识其合成性质。任何与真实主体的相似纯属巧合。
- **本基准不构成法律意见**。`reference/golden_expectations.md` 中的"应出现短语"是评测合规行为的参考，不是律师就虚构事实出具的法律意见。
- **现行法律由使用者负责确认**。中国法律法规持续演进；规则手册本身要求候选附加"需进一步核实现行有效性"提示，但基准脚本并不会代为核查法条的现行有效性。

## 许可证

MIT——见 [LICENSE](LICENSE)。本基准内容（规则、评分细则、用例、评分工具）以开放许可发布，供研究、教学与机构内部评测使用。

## 状态

`version: 1.0.1`。已在至少一个前沿模型上跑完 12 个用例且无 CF 触发；可对外分享。预计随新失败模式被发现而持续演进。
