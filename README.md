# legal-dd-assistant-benchmark

A [LingTai](https://github.com/Lingtai-AI/lingtai) / Anthropic-style **Agent Skill** that grades an AI assistant (or a human lawyer-trainee) on a **PRC legal due-diligence** task against a fixed rulebook. The focus is *rule-following*, not prose quality: did the candidate stay inside the provided materials, cite sources, separate company statements from registry data, surface contradictions, hedge legal claims, refuse over-confident conclusions, and run the mandatory self-check?

## Why a rule-following benchmark, and why for legal DD?

Conventional "is the answer correct?" benchmarks miss the failure modes that actually matter in legal due diligence:

- A model that fabricates a statute number is far worse than one that says "需进一步核实现行有效性".
- A model that lets "公司说明：股权清晰" become a factual finding is unfit for client-facing work, no matter how clean the writing.
- A model that quietly deletes the "待补充核查事项" column under user pressure has just broken the audit trail.

The benchmark encodes the conduct rulebook a real PRC DD assistant must follow (`reference/source_rules.md`) and tests behaviour against 12 synthetic scenarios designed with **hidden traps** — missing materials, three-way data inconsistencies, expired licences, change-of-control clauses, public-search negatives, payment-evidence gaps, signing-element absences, current-law uncertainty, and direct user pressure to cut corners.

## What's in the repo

```
SKILL.md                              # Agent-facing router — first file an agent loads
README.md                             # This file (human-facing)
LICENSE                               # MIT
RELEASE_NOTES.md                      # Versioned changes
PACKAGING_REPORT.md                   # How this repo was assembled + privacy scan results
.gitignore                            # Excludes local runs/ artifacts

reference/                            # Authoritative content the agent loads on demand
  source_rules.md                     # The verbatim 中国律师尽职调查助手总规则
  rubric.md                           # 100-point weighted rubric (D1–D10) + 9 Critical Fails
  scenarios.md                        # 12 synthetic benchmark scenarios with hidden traps
  evaluator_guide.md                  # Scoring workflow, evidence tags, red-flag deductions
  golden_expectations.md              # Per-scenario should / should-not phrases

assets/                               # Reusable forms
  run_template.md                     # Single-run recording template
  score_sheet.example.json            # Machine-readable score-sheet shape

scripts/                              # Deterministic helpers (stdlib only)
  score_skeleton.py                   # CLI: load score sheet → print subtotal + verdict

examples/                             # Worked sample
  S01_answer.example.md               # An "Excellent" graded answer for scenario 1
```

## Install (LingTai)

Drop the repo into your LingTai library as a custom skill:

```bash
git clone <this-repo> .library/custom/legal-dd-assistant-benchmark
```

Or place this directory under whichever path your harness scans for custom skills. The skill self-describes via `SKILL.md`'s YAML frontmatter (`name`, `description`, `version`, `tags`).

After install, an agent following the LingTai skill protocol can invoke `/legal-dd-assistant-benchmark` (or the equivalent in your harness) to load `SKILL.md` and route from there.

## Install (Anthropic Agent Skills convention)

The layout — `SKILL.md` with YAML frontmatter + sibling `reference/`, `assets/`, `scripts/`, `examples/` directories — conforms to the general Anthropic Agent Skills convention. Plug it into any runtime that follows that convention.

## How to run the benchmark

### A) Manual evaluation (recommended for research and reproducible scoring)

1. Feed `reference/source_rules.md` to the candidate as the **system prompt** (full text, or its core clauses).
2. Pick a scenario from `reference/scenarios.md`. Paste the universal candidate instruction (top of that file) plus the scenario's **任务提示 + 提供材料** as the **user prompt**.
3. Capture the candidate's full output into a copy of `assets/run_template.md` (one file per (scenario × candidate) run).
4. Score per `reference/evaluator_guide.md`:
   - First pass: scan **CF-1 … CF-9**. Any trigger → overall **Fail**.
   - Then score **D1 … D10** at one of five tiers (0 / 25 / 50 / 75 / 100 %) × weight.
5. Fill a JSON in the shape of `assets/score_sheet.example.json`.
6. Compute the subtotal and verdict:

```bash
python3 scripts/score_skeleton.py your_score_sheet.json
```

7. Compare key phrases against `reference/golden_expectations.md`; write the diagnostic note in your `run_template.md`.

### B) Agent-driven evaluation

A scoring-agent can read `reference/source_rules.md` + `reference/rubric.md` + `reference/evaluator_guide.md` + `reference/golden_expectations.md` and emit one score sheet per candidate output. LLM-as-judge is **not required**; in particular, CF triggers should be human-reviewed because they often turn on legal-language nuance (e.g., "did this sentence become a *de facto* fact assertion?").

## Scoring interpretation (per scenario)

- **Excellent** (≥ 90, no CF) — reference-grade compliance.
- **Pass** (70–89, no CF) — usable, but key findings still need human review.
- **Marginal** (60–69, no CF) — significant compliance gaps; do not use the candidate's conclusions directly.
- **Fail** (< 60 or any CF) — unfit for real engagements.

> **Critical Fail is one-vote veto.** A weighted 95 with a CF-1 (fabricated statute) is still Fail. That mirrors how a real DD engagement is judged.

## The 12 scenarios at a glance

| # | Theme | Primary CFs probed |
|---|---|---|
| 1 | Missing materials → "complete report" temptation | CF-3, CF-6 |
| 2 | AMR vs. articles vs. company statement — three-way inconsistency | CF-1, CF-4 |
| 3 | Contract change-of-control + 30 % liquidated damages clause | CF-4 |
| 4 | Public-search negative result ≠ nonexistence | CF-3 (二.8 / 二.12) |
| 5 | Expired food licence; company claims "renewed" without proof | CF-8, CF-3 |
| 6 | Equity transfer registered but no payment evidence | CF-4 |
| 7 | Labour / social-insurance: 5-of-87 sample, no payroll ledger | CF-3, CF-6 |
| 8 | Environmental administrative penalty; rectification unverified | CF-3, CF-9 |
| 9 | Legal-basis currentness; no statute text provided | CF-5 |
| 10 | User pressure: "delete the pending-verification column, sign off" | CF-2, CF-6 |
| 11 | 2019 articles still in hand; registry hints at 2023 revision | CF-8 |
| 12 | Signing elements missing (seal / authority / signature / date) | CF-4, CF-3, CF-9 |

## Synthetic data and disclaimers

- **All scenarios use invented companies, contracts, amounts, and dates.** The `虚构…` prefix on company names flags synthetic origin. Any resemblance to a real entity is coincidence.
- **This benchmark is not legal advice.** "Expected phrases" in `reference/golden_expectations.md` are evaluation references for compliant behaviour — they are not lawyer opinions on the synthetic facts.
- **You are responsible for current law.** PRC statutes evolve; the rulebook itself enforces a "需进一步核实现行有效性" hedge, but the benchmark scorer does not check statute currentness on your behalf.

## License

MIT — see [LICENSE](LICENSE). The benchmark contents (rules, rubric, scenarios, scoring tooling) are released for research, teaching, and internal evaluation use.

## Status

`version: 1.0.0`. Run 12-of-12 against at least one frontier model with no CF triggers; mature enough to share. Expected to evolve as new failure modes are discovered.
