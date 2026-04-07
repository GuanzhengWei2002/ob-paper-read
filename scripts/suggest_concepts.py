#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


REVIEW_KEY = "global_concept_review"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def split_terms(values: list[str]) -> list[str]:
    results: list[str] = []
    for value in values:
        pieces = re.split(r"[;,/]|(?:\s+\|\s+)", str(value).strip())
        cleaned = [piece.strip() for piece in pieces if piece.strip()]
        results.extend(cleaned or [str(value).strip()])
    return results


def unique_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(text)
    return result


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "item"


def paper_link(paper_id: str) -> str:
    return f"papers/{paper_id}/reading"


def load_question_payloads(memory_root: Path, paper_id: str) -> list[dict]:
    questions_dir = memory_root / "questions"
    if not questions_dir.exists():
        return []
    payloads: list[dict] = []
    for path in sorted(questions_dir.glob("*.json")):
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        if paper_id in as_list(payload.get("papers")):
            payloads.append(payload)
    return payloads


def collect_candidates(card: dict, question_payloads: list[dict]) -> tuple[list[str], dict[str, str]]:
    reasons: dict[str, str] = {}

    def add(term: str, reason: str) -> None:
        text = str(term).strip()
        if not text:
            return
        key = text.casefold()
        if key not in reasons:
            reasons[key] = reason

    for item in split_terms(as_list(card.get("prerequisites"))):
        add(item, "来自 prerequisites")
    for item in split_terms(as_list(card.get("teaching_adjustments", {}).get("unresolved_concepts"))):
        add(item, "来自 unresolved_concepts")

    tag_counts: dict[str, int] = {}
    for payload in question_payloads:
        ask_count = int(payload.get("ask_count", 0) or 0)
        for item in split_terms(as_list(payload.get("concept_tags"))):
            key = item.casefold()
            tag_counts[key] = tag_counts.get(key, 0) + max(ask_count, 1)
            if tag_counts[key] >= 2:
                add(item, f"问题记忆里重复出现 {tag_counts[key]} 次")

    ordered = unique_keep_order(list(reasons.keys()))
    display_map = {item.casefold(): item for item in split_terms(as_list(card.get("prerequisites")) + as_list(card.get("teaching_adjustments", {}).get("unresolved_concepts")))}
    for payload in question_payloads:
        for item in split_terms(as_list(payload.get("concept_tags"))):
            display_map.setdefault(item.casefold(), item)

    concepts = [display_map[key] for key in ordered if key in display_map]
    return concepts, reasons


def should_suggest(card: dict, concepts: list[str], question_payloads: list[dict]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not concepts:
        return False, reasons

    if as_list(card.get("prerequisites")):
        reasons.append("paper card 里已有 prerequisites")
    if as_list(card.get("teaching_adjustments", {}).get("unresolved_concepts")):
        reasons.append("存在 unresolved_concepts")
    if any(int(payload.get("ask_count", 0) or 0) >= 2 for payload in question_payloads):
        reasons.append("至少一个相关问题被重复提到 2 次以上")
    status_order = {
        "saved": 0,
        "classified": 1,
        "reading_generated": 2,
        "selected_as_primary": 2,
        "reading_in_progress": 3,
        "mastery_checked": 4,
        "read_completed": 5,
        "compared": 6,
    }
    status = str(card.get("status", "")).strip()
    if status_order.get(status, 0) >= status_order["reading_in_progress"]:
        reasons.append(f"阅读状态已到 {status}")
    metrics = card.get("reading_metrics", {}) or {}
    if int(metrics.get("qa_count", 0) or 0) > 0:
        reasons.append("已经产生过阅读问答")

    return bool(reasons), reasons


def build_update_command(script_dir: Path, paper_id: str, root: Path, vault_dir: str, concepts: list[str]) -> str:
    script_path = script_dir / "update_global_pages.py"
    pieces = [
        f'python "{script_path}"',
        paper_id,
        f'--root "{root}"',
        f'--vault-dir "{vault_dir}"',
    ]
    for concept in concepts:
        pieces.append(f'--concept "{concept}"')
    return " ".join(pieces)


def update_review_state(card_path: Path, card: dict, concepts: list[str], suggestion_reasons: list[str]) -> None:
    review = card.get(REVIEW_KEY, {}) or {}
    review["last_suggested_at"] = datetime.now(timezone.utc).astimezone().isoformat()
    review["suggested_concepts"] = concepts
    review["suggestion_reasons"] = suggestion_reasons
    card[REVIEW_KEY] = review
    save_json(card_path, card)


def analyze(card_path: Path, root: Path, memory_dir: str, vault_dir: str) -> dict:
    card = load_json(card_path)
    paper_id = str(card.get("paper_id", "")).strip() or card_path.stem
    memory_root = root / memory_dir
    question_payloads = load_question_payloads(memory_root, paper_id)
    concepts, concept_reasons = collect_candidates(card, question_payloads)
    should_prompt, suggestion_reasons = should_suggest(card, concepts, question_payloads)
    command = build_update_command(Path(__file__).resolve().parent, paper_id, root, vault_dir, concepts) if concepts else ""
    return {
        "card": card,
        "paper_id": paper_id,
        "concepts": concepts,
        "concept_reasons": concept_reasons,
        "should_prompt": should_prompt,
        "suggestion_reasons": suggestion_reasons,
        "command": command,
        "question_payloads": question_payloads,
    }


def print_report(result: dict) -> None:
    concepts = result["concepts"]
    if not result["should_prompt"]:
        print("No concept suggestion right now.")
        if not concepts:
            print("Reason: no stable concept candidates found.")
        return

    print(f"Suggested concepts for {result['paper_id']}:")
    for concept in concepts:
        reason = result["concept_reasons"].get(concept.casefold(), "值得沉淀")
        print(f"- {concept} ({reason})")
    print("")
    print("Why suggest now:")
    for reason in result["suggestion_reasons"]:
        print(f"- {reason}")
    print("")
    print("Next step:")
    print(result["command"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Suggest concept pages worth updating after a paper reading step.")
    parser.add_argument("paper_id", help="Paper id that already exists in memory.")
    parser.add_argument("--root", default=".", help="Workspace root.")
    parser.add_argument("--memory-dir", default=".ob-paper-read-memory", help="Memory directory name.")
    parser.add_argument("--vault-dir", default="reading-vault", help="Vault output directory.")
    parser.add_argument("--write-review-state", action="store_true", help="Write the latest suggestion info back into the paper card.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    card_path = root / args.memory_dir / "papers" / f"{args.paper_id}.json"
    if not card_path.exists():
        raise FileNotFoundError(f"Paper card not found: {card_path}")

    result = analyze(card_path, root, args.memory_dir, args.vault_dir)
    print_report(result)

    if args.write_review_state and result["should_prompt"]:
        update_review_state(card_path, result["card"], result["concepts"], result["suggestion_reasons"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
