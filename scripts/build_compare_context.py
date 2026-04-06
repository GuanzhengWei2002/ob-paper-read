#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_card(path: Path) -> dict:
    # Accept both plain UTF-8 and UTF-8 with BOM because some editors and
    # PowerShell write JSON with a BOM by default on Windows.
    return json.loads(path.read_text(encoding="utf-8-sig"))


def compare_brief(base: dict, target: dict) -> str:
    def bullet_list(values: list[str]) -> str:
        if not values:
            return "- (fill this during reading)"
        return "\n".join(f"- {item}" for item in values)

    def source_path(card: dict) -> str:
        source = card.get("source", {})
        if isinstance(source, dict):
            return source.get("path", "")
        return ""

    return f"""# Comparison Brief

## Base Paper

- Title: {base.get("title", "")}
- Why it matters: {base.get("why_it_matters", "")}
- Problem: {base.get("core_problem", "")}
- Method: {base.get("core_method", "")}
- PDF Path: {source_path(base)}

## Target Paper

- Title: {target.get("title", "")}
- Why it matters: {target.get("why_it_matters", "")}
- Problem: {target.get("core_problem", "")}
- Method: {target.get("core_method", "")}
- PDF Path: {source_path(target)}

## Compare

### Shared Topic

- Base topic: {base.get("topic", "")}
- Target topic: {target.get("topic", "")}

### Problem Framing

- Base: {base.get("core_problem", "")}
- Target: {target.get("core_problem", "")}

### Method Change

- Base: {base.get("core_method", "")}
- Target: {target.get("core_method", "")}

### Evidence

Base evidence:
{bullet_list(base.get("core_evidence", []))}

Target evidence:
{bullet_list(target.get("core_evidence", []))}

### Prerequisite Transfer

Carry these concepts into the target reading:
{bullet_list(base.get("prerequisites", []))}

### Open Questions Worth Carrying Forward

{bullet_list(base.get("open_questions", []))}

### Questions To Resolve While Reading The Target Paper

- What does the target paper keep from the base paper?
- What does the target paper change?
- What new evidence does it add?
- What old limitation does it address?
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a comparison brief from two paper cards.")
    parser.add_argument("base_paper", help="Path to the base paper card JSON.")
    parser.add_argument("target_paper", help="Path to the target paper card JSON.")
    parser.add_argument("--out", help="Optional output markdown path.")
    args = parser.parse_args()

    base = load_card(Path(args.base_paper).resolve())
    target = load_card(Path(args.target_paper).resolve())
    text = compare_brief(base, target)

    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"Created: {out_path}")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
