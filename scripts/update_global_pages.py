#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


PAGE_TYPES = ("concept",)


def load_card(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "item"


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


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return unique_keep_order([str(item).strip() for item in value if str(item).strip()])
    text = str(value).strip()
    return [text] if text else []


def split_terms(values: list[str]) -> list[str]:
    results: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        pieces = re.split(r"[;,/]|(?:\s+\|\s+)", text)
        cleaned = [piece.strip() for piece in pieces if piece.strip()]
        if len(cleaned) <= 1:
            results.append(text)
        else:
            results.extend(cleaned)
    return unique_keep_order(results)


def page_dir_name(page_type: str) -> str:
    return {"concept": "concepts"}[page_type]


def page_template(page_type: str, title: str, card: dict, page_path: str, paper_link: str) -> str:
    summary = str(card.get("summary_one_line", "")).strip()
    topic = str(card.get("topic", "")).strip()
    role = str(card.get("role", "")).strip()
    domain = str(card.get("domain", "")).strip()
    core_problem = str(card.get("core_problem", "")).strip()
    core_method = str(card.get("core_method", "")).strip()
    why_it_matters = str(card.get("why_it_matters", "")).strip()

    title_map = {"concept": "一句话定义"}
    importance_map = {"concept": "为什么重要"}
    related_map = {"concept": "相关方法或上下文"}

    headline = summary or why_it_matters or f"{title} 是当前阅读库里的一个高频{page_type}条目。"
    importance = why_it_matters or core_problem or core_method or "后续读到更多论文后，再补充这一页为什么重要。"
    related_line = core_method or topic or role or domain or "后续补充"

    return (
        "---\n"
        f"type: {page_type}\n"
        f"id: {slugify(title)}\n"
        f"title: {title}\n"
        f"source_pages:\n"
        f"  - {paper_link}\n"
        "---\n\n"
        f"# {title}\n\n"
        f"## {title_map[page_type]}\n\n"
        f"{headline}\n\n"
        f"## {importance_map[page_type]}\n\n"
        f"{importance}\n\n"
        "## 当前理解\n\n"
        "- 这页是从单篇精读中抽出来的轻量全局卡片。\n"
        "- 先记录稳定信息，再随着更多论文继续修订。\n\n"
        f"## {related_map[page_type]}\n\n"
        f"- {related_line}\n\n"
        "## 在本库出现于\n\n"
        f"- {paper_link}\n\n"
        "## 待补充\n\n"
        "- 常见误解\n"
        "- 与相邻概念/方法的区别\n"
        "- 更完整的代表论文列表\n"
    )


def ensure_page(page_type: str, title: str, vault_root: Path, card: dict, paper_link: str) -> str:
    directory = vault_root / page_dir_name(page_type)
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{slugify(title)}.md"
    path = directory / filename
    if not path.exists():
        path.write_text(page_template(page_type, title, card, str(path), paper_link), encoding="utf-8")
    return f"{page_dir_name(page_type)}/{filename}"


def append_source_link(path: Path, paper_link: str) -> None:
    text = path.read_text(encoding="utf-8")
    if paper_link in text:
        return
    marker = "## 在本库出现于"
    if marker in text:
        updated = text.replace(marker, f"{marker}\n\n- {paper_link}", 1)
    else:
        suffix = "\n\n## 在本库出现于\n\n" + f"- {paper_link}\n"
        updated = text.rstrip() + suffix
    path.write_text(updated if updated.endswith("\n") else updated + "\n", encoding="utf-8")


def update_existing_page(path: Path, paper_link: str) -> None:
    append_source_link(path, paper_link)


def collect_items(card: dict, args: argparse.Namespace) -> dict[str, list[str]]:
    concepts = split_terms(
        as_list(args.concept)
        + as_list(card.get("prerequisites"))
        + as_list(card.get("teaching_adjustments", {}).get("unresolved_concepts"))
    )
    return {"concept": concepts}


def load_or_create_index(index_path: Path) -> str:
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return (
        "# Index\n\n"
        "## Papers\n\n"
        "## Concepts\n"
    )


def upsert_index_section(text: str, heading: str, entries: list[str]) -> str:
    pattern = re.compile(rf"(^## {re.escape(heading)}\n)(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    body = "".join(f"- {entry}\n" for entry in unique_keep_order(entries))
    replacement = f"## {heading}\n\n{body}"
    if match:
        return text[: match.start()] + replacement + text[match.end() :]
    suffix = "\n" if text.endswith("\n") else "\n\n"
    return text + suffix + replacement + "\n"


def update_index(vault_root: Path, paper_link: str, page_refs: dict[str, list[str]], card: dict) -> Path:
    overviews = vault_root / "overviews"
    overviews.mkdir(parents=True, exist_ok=True)
    index_path = overviews / "index.md"
    text = load_or_create_index(index_path)

    paper_title = str(card.get("title", "")).strip() or str(card.get("paper_id", "")).strip()
    paper_summary = str(card.get("summary_one_line", "")).strip()
    paper_entry = f"[[{paper_link}|{paper_title}]]"
    if paper_summary:
        paper_entry += f" - {paper_summary}"

    sections = {
        "Papers": [paper_entry],
        "Concepts": [f"[[{ref}|{Path(ref).stem.replace('-', ' ')}]]" for ref in page_refs["concept"]],
    }

    for heading, new_entries in sections.items():
        existing: list[str] = []
        pattern = re.compile(rf"^## {re.escape(heading)}\n\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
        match = pattern.search(text)
        if match:
            existing = [line[2:].strip() for line in match.group(1).splitlines() if line.startswith("- ")]
        text = upsert_index_section(text, heading, existing + new_entries)

    index_path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    return index_path


def update_log(vault_root: Path, paper_link: str, card: dict, page_refs: dict[str, list[str]]) -> Path:
    overviews = vault_root / "overviews"
    overviews.mkdir(parents=True, exist_ok=True)
    log_path = overviews / "log.md"
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else "# Log\n\n"

    today = datetime.now(timezone.utc).astimezone().date().isoformat()
    title = str(card.get("title", "")).strip() or str(card.get("paper_id", "")).strip()
    lines = [
        f"## [{today}] concept-update | {title}",
        f"- paper: [[{paper_link}|{title}]]",
    ]
    refs = page_refs["concept"]
    if refs:
        lines.append("- updated concepts: " + ", ".join(f"[[{ref}]]" for ref in refs))
    entry = "\n".join(lines) + "\n\n"
    log_path.write_text(existing + entry, encoding="utf-8")
    return log_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Update lightweight concept pages and a simple index from one paper card.")
    parser.add_argument("paper_id", help="Paper id that already exists in memory.")
    parser.add_argument("--root", default=".", help="Workspace root.")
    parser.add_argument("--memory-dir", default=".ob-paper-read-memory", help="Memory directory name.")
    parser.add_argument("--vault-dir", default="reading-vault", help="Vault output directory.")
    parser.add_argument("--concept", action="append", default=[], help="Extra concept term to add. Repeatable.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    memory_root = root / args.memory_dir
    card_path = memory_root / "papers" / f"{args.paper_id}.json"
    if not card_path.exists():
        raise FileNotFoundError(f"Paper card not found: {card_path}")

    card = load_card(card_path)
    vault_root = root / args.vault_dir
    vault_root.mkdir(parents=True, exist_ok=True)

    paper_link = f"papers/{args.paper_id}/reading"
    items = collect_items(card, args)
    page_refs: dict[str, list[str]] = {"concept": []}

    for page_type, values in items.items():
        for value in values:
            ref = ensure_page(page_type, value, vault_root, card, paper_link)
            update_existing_page(vault_root / ref, paper_link)
            page_refs[page_type].append(ref)

    index_path = update_index(vault_root, paper_link, page_refs, card)
    log_path = update_log(vault_root, paper_link, page_refs, card)

    print(f"Updated index: {index_path}")
    print(f"Updated log: {log_path}")
    refs = unique_keep_order(page_refs["concept"])
    if refs:
        print("concepts:")
        for ref in refs:
            print(f"  - {vault_root / ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
