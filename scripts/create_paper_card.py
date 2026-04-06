#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "paper"


def default_card(
    paper_id: str,
    title: str,
    source_path: str,
    domain: str,
    topic: str,
    role: str,
    difficulty: str,
    is_primary: bool,
) -> dict:
    return {
        "paper_id": paper_id,
        "title": title,
        "source": {
            "type": "pdf",
            "path": source_path,
        },
        "domain": domain,
        "topic": topic,
        "role": role,
        "difficulty": difficulty,
        "classification_reason": "",
        "classification_confidence": 0.0,
        "status": "saved",
        "is_primary": is_primary,
        "stage": "intake",
        "reading_mode": "detailed",
        "reading_progress": {
            "overview": "todo",
            "body": "todo",
            "reflection": "todo",
        },
        "summary_one_line": "",
        "why_it_matters": "",
        "core_problem": "",
        "core_method": "",
        "core_evidence": [],
        "prerequisites": [],
        "key_figures": [],
        "key_tables": [],
        "teaching_script": {
            "opening_hook": "",
            "author_context": "",
            "prerequisite_bridge": "",
            "title_walkthrough": "",
            "abstract_walkthrough": [],
            "conclusion_walkthrough": "",
            "introduction_walkthrough": "",
            "related_work_walkthrough": "",
            "method_overview": "",
            "method_walkthrough": "",
            "figure_walkthroughs": [],
            "experiment_walkthrough": [],
            "evidence_walkthrough": "",
            "limitation_walkthrough": "",
            "takeaways": [],
            "retell_script": "",
            "reflection_prompt": "",
            "mastery_questions": [],
        },
        "open_questions": [],
        "external_related_reads": [],
        "cited_papers": [],
        "question_refs": [],
        "session_refs": [],
        "local_related_papers": [],
        "reading_metrics": {
            "opened_count": 0,
            "active_reading_minutes": 0,
            "annotation_count": 0,
            "qa_count": 0,
            "summary_written": False,
            "last_read_at": "",
        },
        "mastery": {
            "problem": 0,
            "method": 0,
            "evidence": 0,
            "comparison": 0,
            "transfer": 0,
        },
        "next_reads": {
            "predecessors": [],
            "successors": [],
            "parallel": [],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a paper card JSON stub.")
    parser.add_argument("title", help="Paper title.")
    parser.add_argument("--root", default=".", help="Workspace root.")
    parser.add_argument("--memory-dir", default=".ob-paper-read-memory", help="Memory directory name.")
    parser.add_argument("--paper-id", help="Explicit paper id. Default: slugified title.")
    parser.add_argument("--source-path", default="", help="Optional local PDF path.")
    parser.add_argument("--domain", default="", help="Optional domain label.")
    parser.add_argument("--topic", default="", help="Optional topic label.")
    parser.add_argument("--role", default="", help="Optional role such as landmark, survey, or application.")
    parser.add_argument("--difficulty", default="", help="Optional difficulty label.")
    parser.add_argument("--primary", action="store_true", help="Mark this paper as the current primary paper.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    memory_root = root / args.memory_dir
    papers_dir = memory_root / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)

    paper_id = args.paper_id or slugify(args.title)
    card = default_card(
        paper_id,
        args.title,
        args.source_path,
        args.domain,
        args.topic,
        args.role,
        args.difficulty,
        args.primary,
    )
    target = papers_dir / f"{paper_id}.json"
    target.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Created: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
