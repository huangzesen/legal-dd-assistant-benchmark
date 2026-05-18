# Release Notes

## v1.0.0 — initial public release

First public, packaged release of the PRC legal due-diligence assistant rule-following benchmark.

### Included
- **Conduct rulebook** (`reference/source_rules.md`): 16 basic principles + 15 prohibitions, the authoritative conduct standard candidates are graded against.
- **Rubric** (`reference/rubric.md`): 10 weighted dimensions (D1–D10, sum = 100) covering material-boundedness, step/order compliance, format compliance, source citation, source separation, risk categorisation, contradiction / material-gap handling, legal-basis currentness, cautious language, and self-check; plus 9 Critical Fails (CF-1 … CF-9) acting as one-vote vetoes.
- **Scenarios** (`reference/scenarios.md`): 12 synthetic scenarios, each with a hidden trap mapped to one or more CFs. All companies, contracts, dates, amounts, and licence numbers are invented; the `虚构…` prefix flags synthetic origin.
- **Evaluator guide** (`reference/evaluator_guide.md`): scoring workflow, evidence tag set, red-flag deductions, two-evaluator dispute resolution.
- **Golden expectations** (`reference/golden_expectations.md`): per-scenario should / should-not phrases. Intent-and-effect comparison; verbatim match not required.
- **Templates**: `assets/run_template.md` for single-run capture; `assets/score_sheet.example.json` as the score-sheet schema.
- **CLI** (`scripts/score_skeleton.py`): pure-stdlib Python loader/validator/printer for score sheets — emits per-dimension subtotal, CF status, and verdict.
- **Worked example** (`examples/S01_answer.example.md`): one Excellent-graded answer for scenario 1, showing what a passing output looks like.

### Verdict tiers
- Excellent: ≥ 90 weighted, no CF
- Pass: 70–89, no CF
- Marginal: 60–69, no CF
- Fail: < 60 or any CF triggered

### Not in this release
- No automated LLM-as-judge harness — scoring is intentionally tool-light; CF triggers should be human-reviewed because they often turn on legal-language nuance.
- No leaderboard or multi-run aggregation tooling.
- Scenario bodies are Chinese-only; English summaries appear in README and rubric headers. English translation of scenario bodies is left for a future minor release.

### Known caveats
- The rulebook reflects the conduct expectations of a PRC legal-DD assistant and is not a substitute for client-specific engagement standards.
- Public-search and "currentness" rules in the rulebook (e.g., 二.12, 一.13) ride on the assumption that the candidate has internet access to verify, but the benchmark itself does not require network. Candidates should signal "需进一步核实" instead of reaching out.
