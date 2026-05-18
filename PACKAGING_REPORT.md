# 打包报告 — legal-dd-assistant-benchmark v1.0.0（中文化于 v1.0.1）

本报告说明面向公开发布的独立技能仓库是如何从内部基准源材料中组装而成的、做了哪些清洗、跑了哪些检查，以及维护者发布所需执行的下一步命令。

> 注：v1.0.1 仅将面向人/Agent 的英文叙述统一为简体中文，基准语义未变。本打包报告的源版本为 v1.0.0。

## 1. 源 → 发布映射

| 源文件（内部基准） | 目标（发布目录） | 备注 |
|---|---|---|
| `README.md`                       | `README.md`（重写）                   | 重写为面向 GitHub 公开发布的中文落地页，移除任何内部路径。 |
| `source_rules.md`                 | `reference/source_rules.md`          | 原样保留——权威规则手册。 |
| `rubric.md`                       | `reference/rubric.md`                | 原样保留——10 维 / 100 分制评分细则 + 9 条 CF。 |
| `scenarios.md`                    | `reference/scenarios.md`             | 原样保留——12 个虚构用例。 |
| `evaluator_guide.md`              | `reference/evaluator_guide.md`       | 原样保留，仅修正两处跨目录路径（`assets/run_template.md`、`assets/score_sheet.example.json`）。 |
| `golden_expectations.md`          | `reference/golden_expectations.md`   | 原样保留。 |
| `run_template.md`                 | `assets/run_template.md`             | 原样保留，仅修正两处跨目录路径（`reference/scenarios.md`、`reference/source_rules.md`）。 |
| `score_sheet.example.json`        | `assets/score_sheet.example.json`    | 原样保留。 |
| `scripts/score_skeleton.py`       | `scripts/score_skeleton.py`          | 原样保留。 |
| `runs/<本地运行 ID>/candidate_outputs/S01_answer.md` | `examples/S01_answer.example.md` | 一份"优秀"等级的样例答案。原目录路径含本地时间戳，但文件内容本身不含任何个人身份信息——内容是针对虚构公司的模型生成答案。复制时已重命名以去除带时间戳的运行 ID。 |
| `runs/**`（其余运行工件）           | （不发布）                            | 本地基准验证产物，已通过 `.gitignore` 排除。 |
| `packaging_report.md`（旧版）       | （不发布）                            | 由本报告替代；旧报告含内部出处信息。 |
| `.latest_claude_code_run`          | （不发布）                            | 本地指针文件。 |

## 2. 新建的顶级文件

- `SKILL.md` — 面向 Agent 的路由文件，含 YAML frontmatter（`name: legal-dd-assistant-benchmark`、`version: 1.0.0`、强触发词描述、tags）。描述中明确列出调用线索（"评分／打分／评估……中国法律尽调……规则手册"）并警告不得用于输出法律意见。
- `README.md` — 面向人类读者的 GitHub 落地页：动机说明、LingTai 与 Anthropic Agent Skills 通用约定的两种安装方式、运行流程、总评等级、用例索引、虚构数据免责声明、MIT 许可证。
- `LICENSE` — MIT，2026 年。
- `RELEASE_NOTES.md` — v1.0.0 发布范围与已知局限。
- `.gitignore` — 排除 `runs/`、Python 缓存、操作系统 / 编辑器元数据。
- `PACKAGING_REPORT.md` — 本文件。

## 3. 隐私清洗

清洗时显式搜索并确认发布目录中不存在的隐私模式：

- 本地绝对路径前缀
- 本地用户账户名
- 本地项目根段
- 内部出处 / 路由用术语
- 内部运行时间戳前缀（样例答案文件已重命名以去除其运行 ID）
- 内部 Agent 目录名
- daemon-id 模式

原内部打包报告中曾出现的两处内部出处引用，位于 **未发布** 的文件中。本公开打包报告以泛化措辞描述清洗过程，而不复刻具体的本地值。

## 4. 本地检查

### 4.1 最终目录树

```
.gitignore
LICENSE
PACKAGING_REPORT.md
README.md
RELEASE_NOTES.md
SKILL.md
assets/
  run_template.md
  score_sheet.example.json
examples/
  S01_answer.example.md
reference/
  evaluator_guide.md
  golden_expectations.md
  rubric.md
  scenarios.md
  source_rules.md
scripts/
  score_skeleton.py
```

共 14 个文件、4 个子目录。无残留运行工件，无意外文件。

### 4.2 隐私 grep

```
grep -rEn "<本地路径>|<用户名>|<项目名>|<内部出处>|<时间戳>|<Agent 目录>|<daemon-id>" <发布目录>
```

结果：**无匹配**。发布目录中不含本地路径、用户账户、内部邮件、带时间戳的运行、Agent 目录与 daemon-id 等碎片。

### 4.3 评分 CLI 冒烟测试

```
python3 scripts/score_skeleton.py assets/score_sheet.example.json
```

得到一份干净的维度表，加权总分 **77.50 / 100**，无 CF 触发，总评 **合格 Pass**。`--strict` 模式同样以退出码 0 通过（无结构校验告警）。

### 4.4 Skill 校验器

在本环境的 `PATH` 中未发现项目级或框架级的 skill 校验器可执行文件，因此未单独执行一次校验器扫描。`SKILL.md` 的 YAML frontmatter 已按 Anthropic Agent Skills 约定手工对齐（必填 `name` + `description`，可选 `version` 与 `tags`），与同一约定下已发布的姊妹技能 `work/publish/book-to-skill-distillation-skill/` 保持一致。

## 5. 局限与未来工作

- **CF 判定以人工为准**。CLI 机械地按"一票否决"汇总，但 *是否触发某条 CF*（尤其 CF-3、CF-6、CF-9）的 *判断* 涉及法律语言细微差别，应由人工复核。`reference/evaluator_guide.md` §五 介绍了双评分员争议处理。
- **暂无英文版用例正文**。用例与规则均为中文；早期 README 与评分细则曾以英文摘要呈现，自 v1.0.1 起已统一为中文。未来次版本可考虑配套发布英文用例。
- **仅有一份样例答案**。`examples/` 目前仅包含 S01。再增加 1–2 份（例如"边缘"或"不合格"档样例）有助于校准评分员；但出于真实性考虑，目前仅发布一份真实评分过的"优秀"样例；合成"不合格"样例需人工编写。
- **未提供多次运行排行榜工具**。不在 v1.0.0 范围内。

## 6. 维护者发布所需的下一步命令

请在发布目录（`legal-dd-assistant-benchmark-skill/`）中执行：

```bash
# 进入发布目录后执行

# 1. 初始化 git
git init -b main
git add .
git commit -m "Initial public release: legal-dd-assistant-benchmark v1.0.0"

# 2. 创建 GitHub 仓库（按需调整 owner 与可见性）
gh repo create legal-dd-assistant-benchmark \
  --public \
  --description "PRC legal due-diligence assistant rule-following benchmark (LingTai / Agent Skill)" \
  --source . \
  --remote origin \
  --push

# 3. 打 v1.0.0 tag 并以发布说明为内容创建 Release
git tag -a v1.0.0 -m "v1.0.0 — initial public release"
git push origin v1.0.0
gh release create v1.0.0 \
  --title "v1.0.0 — initial public release" \
  --notes-file RELEASE_NOTES.md
```

机械打包脚本本身不会执行上述命令；正式发布动作由父级编排者在审核通过后执行。
