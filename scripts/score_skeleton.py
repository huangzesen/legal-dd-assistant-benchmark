#!/usr/bin/env python3
"""score_skeleton.py — Load a JSON score sheet and print subtotal/overall.

This is a non-LLM CLI helper for the legal-dd-assistant-benchmark. It validates
the score sheet structure, computes per-dimension weighted scores, applies
Critical Fail (CF) logic, and prints a summary.

Score sheet JSON structure (see score_sheet.example.json):

{
  "run_id": "RUN-...",
  "scenario_id": "1",
  "candidate": "model-name",
  "dimensions": [
    {"code": "D1", "weight": 15, "tier": 75, "note": "..."},
    ...
  ],
  "critical_fails": [
    {"code": "CF-1", "triggered": false, "evidence": ""},
    ...
  ]
}

`tier` is one of 0, 25, 50, 75, 100 (percent of weight).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VALID_TIERS = {0, 25, 50, 75, 100}
EXPECTED_DIMENSION_CODES = [f"D{i}" for i in range(1, 11)]
EXPECTED_DIMENSION_WEIGHTS = {
    "D1": 15, "D2": 10, "D3": 10, "D4": 10, "D5": 8,
    "D6": 8, "D7": 10, "D8": 10, "D9": 9, "D10": 10,
}
EXPECTED_CF_CODES = [f"CF-{i}" for i in range(1, 10)]


def load_sheet(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate(sheet: dict) -> list[str]:
    errors: list[str] = []
    dims = sheet.get("dimensions", [])
    codes_seen = [d.get("code") for d in dims]
    for code in EXPECTED_DIMENSION_CODES:
        if code not in codes_seen:
            errors.append(f"missing dimension {code}")
    for d in dims:
        code = d.get("code")
        if code in EXPECTED_DIMENSION_WEIGHTS:
            if d.get("weight") != EXPECTED_DIMENSION_WEIGHTS[code]:
                errors.append(
                    f"{code} weight mismatch: got {d.get('weight')}, "
                    f"expected {EXPECTED_DIMENSION_WEIGHTS[code]}"
                )
        tier = d.get("tier")
        if tier not in VALID_TIERS:
            errors.append(f"{code} tier {tier!r} not in {sorted(VALID_TIERS)}")
    cfs = sheet.get("critical_fails", [])
    cf_codes_seen = [c.get("code") for c in cfs]
    for code in EXPECTED_CF_CODES:
        if code not in cf_codes_seen:
            errors.append(f"missing critical_fail entry {code}")
    return errors


def compute(sheet: dict) -> dict:
    subtotal = 0.0
    breakdown = []
    for d in sheet.get("dimensions", []):
        weight = d.get("weight", 0)
        tier = d.get("tier", 0)
        score = weight * (tier / 100.0)
        subtotal += score
        breakdown.append({
            "code": d.get("code"),
            "weight": weight,
            "tier": tier,
            "score": round(score, 2),
            "note": d.get("note", ""),
        })
    triggered = [c for c in sheet.get("critical_fails", []) if c.get("triggered")]
    cf_triggered = len(triggered) > 0
    if cf_triggered:
        verdict = "Fail (CF triggered)"
    elif subtotal >= 90:
        verdict = "Excellent"
    elif subtotal >= 70:
        verdict = "Pass"
    elif subtotal >= 60:
        verdict = "Marginal"
    else:
        verdict = "Fail"
    return {
        "subtotal": round(subtotal, 2),
        "breakdown": breakdown,
        "cf_triggered": cf_triggered,
        "cf_triggered_codes": [c.get("code") for c in triggered],
        "verdict": verdict,
    }


def print_report(sheet: dict, result: dict) -> None:
    print("=" * 60)
    print(f"Run ID    : {sheet.get('run_id', '(none)')}")
    print(f"Scenario  : {sheet.get('scenario_id', '(none)')}")
    print(f"Candidate : {sheet.get('candidate', '(none)')}")
    print("=" * 60)
    print(f"{'Code':6} {'Weight':>7} {'Tier%':>7} {'Score':>8}  Note")
    print("-" * 60)
    for b in result["breakdown"]:
        note = (b["note"] or "")[:30]
        print(f"{b['code']:6} {b['weight']:>7} {b['tier']:>7} {b['score']:>8.2f}  {note}")
    print("-" * 60)
    print(f"Subtotal             : {result['subtotal']:>6.2f} / 100")
    if result["cf_triggered"]:
        print(f"Critical Fails       : TRIGGERED -> {', '.join(result['cf_triggered_codes'])}")
    else:
        print("Critical Fails       : none triggered")
    print(f"Verdict              : {result['verdict']}")
    print("=" * 60)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="score_skeleton",
        description="Load a benchmark score sheet (JSON) and print subtotal/overall.",
    )
    parser.add_argument(
        "score_sheet",
        type=Path,
        help="Path to score sheet JSON (see score_sheet.example.json).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if structural validation finds any errors.",
    )
    args = parser.parse_args(argv)

    if not args.score_sheet.exists():
        print(f"error: file not found: {args.score_sheet}", file=sys.stderr)
        return 2

    try:
        sheet = load_sheet(args.score_sheet)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    errors = validate(sheet)
    if errors:
        print("Validation warnings:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        if args.strict:
            return 1

    result = compute(sheet)
    print_report(sheet, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
