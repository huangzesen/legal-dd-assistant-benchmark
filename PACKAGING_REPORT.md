# Packaging Report — legal-dd-assistant-benchmark v1.0.0

This report describes how the standalone, GitHub-ready skill repo was assembled
from the in-tree benchmark source, what was scrubbed, what checks were run, and
the exact next commands a maintainer would run to publish it.

## 1. Source → publish mapping

| Source file (in-tree benchmark) | Destination (publish dir) | Notes |
|---|---|---|
| `README.md`                       | `README.md` (rewritten)              | Replaced with public, GitHub-style landing; bilingual; no internal paths. |
| `source_rules.md`                 | `reference/source_rules.md`          | Verbatim — authoritative rulebook. |
| `rubric.md`                       | `reference/rubric.md`                | Verbatim — 10-dim / 100-pt rubric + 9 CFs. |
| `scenarios.md`                    | `reference/scenarios.md`             | Verbatim — 12 synthetic scenarios. |
| `evaluator_guide.md`              | `reference/evaluator_guide.md`       | Verbatim except two cross-dir path fixes (`assets/run_template.md`, `assets/score_sheet.example.json`). |
| `golden_expectations.md`          | `reference/golden_expectations.md`   | Verbatim. |
| `run_template.md`                 | `assets/run_template.md`             | Verbatim except two cross-dir path fixes (`reference/scenarios.md`, `reference/source_rules.md`). |
| `score_sheet.example.json`        | `assets/score_sheet.example.json`    | Verbatim. |
| `scripts/score_skeleton.py`       | `scripts/score_skeleton.py`          | Verbatim. |
| `runs/<local-run-id>/candidate_outputs/S01_answer.md` | `examples/S01_answer.example.md` | One graded-Excellent worked example. The directory pathname carried a local timestamp but the file content itself contains no personal identifiers — it is a model-generated answer about a synthetic 虚构 company. Renamed on copy to drop the timestamped run-id. |
| `runs/**` (all other run artifacts) | (not published) | Local benchmark validation outputs; ignored via `.gitignore`. |
| `packaging_report.md` (old)        | (not published) | Replaced by this file; the old report referenced internal provenance. |
| `.latest_claude_code_run`          | (not published) | Local pointer file. |

## 2. New top-level files created

- `SKILL.md` — agent-facing router with YAML frontmatter (`name: legal-dd-assistant-benchmark`, `version: 1.0.0`, strong trigger description, tags). The description explicitly lists invocation cues ("grade / score / evaluate ... PRC legal DD ... rulebook") and warns against using the skill to produce legal advice.
- `README.md` — human-facing GitHub landing: motivation, install instructions for both LingTai and the generic Anthropic Agent Skills convention, run procedure, verdict tiers, scenario index, synthetic-data disclaimer, MIT licence.
- `LICENSE` — MIT, 2026.
- `RELEASE_NOTES.md` — v1.0.0 release scope and known caveats.
- `.gitignore` — excludes `runs/`, Python caches, OS / editor metadata.
- `PACKAGING_REPORT.md` — this file.

## 3. Scrubbing performed

Privacy patterns explicitly searched for and confirmed absent in the publish dir:

- local absolute path prefixes
- local user-account names
- local project-root segments
- internal provenance / routing terms
- internal run timestamp prefixes (the example answer file was renamed to drop its run id)
- internal agent directory names
- daemon-id patterns

The two internal-provenance references that appeared in the original in-tree packaging report were **inside a file that is not published**. This public packaging report describes the scrub generically rather than reproducing private values.

## 4. Local checks run

### 4.1 Final tree

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

14 files, 4 subdirectories. No surprises, no leftover run artifacts.

### 4.2 Privacy grep

```
grep -rEn "<local-path>|<user-name>|<project-name>|<internal-provenance>|<timestamp>|<agent-dir>|<daemon-id>" <publish-dir>
```

Result: **no matches**. The publish directory is clean of local-path, user-account, internal-mail, timestamped-run, agent-dir, and daemon-id fragments.

### 4.3 Score CLI smoke test

```
python3 scripts/score_skeleton.py assets/score_sheet.example.json
```

Produces a clean dimensional table, subtotal **77.50 / 100**, no Critical Fails triggered, verdict **Pass**. `--strict` mode also exits 0 (no structural validation warnings).

### 4.4 Skill-validator availability

No project-local or harness-wide skill validator binary was found on `PATH` in this environment, so no separate validator pass was executed. The `SKILL.md` YAML frontmatter is hand-conformant to the Anthropic Agent Skills convention (required `name` + `description`, plus optional `version` and `tags`), matching the sibling `book-to-skill-distillation` skill at `work/publish/book-to-skill-distillation-skill/` that has already shipped under the same convention.

## 5. Caveats and future work

- **CF judgement is human-best.** The CLI honours the one-vote-veto rule mechanically, but the *decision* of whether a CF was triggered (especially CF-3, CF-6, CF-9) hinges on legal-language nuance and should be human-reviewed. `reference/evaluator_guide.md` §五 covers two-evaluator dispute resolution.
- **English-only scenario bodies absent.** Scenarios and rules are Chinese; English summaries appear in `README.md` and rubric headers only. A future minor release could ship parallel English scenarios.
- **One worked example only.** `examples/` includes only S01. Adding 1–2 more (e.g., a "Marginal" or "Fail" exemplar) would help calibrate evaluators, but ships only an authentic graded answer; synthetic "Fail" exemplars would have to be hand-authored.
- **No multi-run leaderboard tooling.** Out of scope for v1.0.0.

## 6. Exact next commands for the parent to publish

Run from the publish directory (`legal-dd-assistant-benchmark-skill/`):

```bash
# from inside the publish directory

# 1. Initialise git
git init -b main
git add .
git commit -m "Initial public release: legal-dd-assistant-benchmark v1.0.0"

# 2. Create the GitHub repo (public; adjust owner/visibility as needed)
gh repo create legal-dd-assistant-benchmark \
  --public \
  --description "PRC legal due-diligence assistant rule-following benchmark (LingTai / Agent Skill)" \
  --source . \
  --remote origin \
  --push

# 3. Tag and create the v1.0.0 release with the release notes
git tag -a v1.0.0 -m "v1.0.0 — initial public release"
git push origin v1.0.0
gh release create v1.0.0 \
  --title "v1.0.0 — initial public release" \
  --notes-file RELEASE_NOTES.md
```

The mechanical packaging daemon did not run these commands; the parent orchestrator performs publication after verification.
