#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_card(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_card(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def yaml_scalar(value: object) -> str:
    text = str(value or "")
    text = text.replace("\\", "/")
    text = text.replace("'", "''")
    return f"'{text}'"


def write_text(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def remove_legacy_files(paper_dir: Path) -> None:
    for legacy_name in ("guide.md", "paper-card.md", "notes.md"):
        legacy_path = paper_dir / legacy_name
        if legacy_path.exists():
            legacy_path.unlink()


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def bullets(values: list[str], fallback: str) -> list[str]:
    items = [value for value in values if value]
    if not items:
        return [f"- {fallback}"]
    return [f"- {value}" for value in items]


def block(title: str, lines: list[str] | None = None) -> str:
    body = "\n".join(lines or [])
    return f"## {title}\n\n{body}\n\n"


def sub_block(title: str, lines: list[str] | None = None) -> str:
    body = "\n".join(lines or [])
    return f"### {title}\n\n{body}\n\n"


def frontmatter(card: dict) -> str:
    source = card.get("source", {})
    source_path = source.get("path", "") if isinstance(source, dict) else ""
    return (
        "---\n"
        f"title: {yaml_scalar(card.get('title', ''))}\n"
        f"paper_id: {yaml_scalar(card.get('paper_id', ''))}\n"
        f"status: {yaml_scalar(card.get('status', ''))}\n"
        f"domain: {yaml_scalar(card.get('domain', ''))}\n"
        f"topic: {yaml_scalar(card.get('topic', ''))}\n"
        f"role: {yaml_scalar(card.get('role', ''))}\n"
        f"difficulty: {yaml_scalar(card.get('difficulty', ''))}\n"
        f"source_pdf: {yaml_scalar(source_path)}\n"
        "---\n\n"
    )


def join_paragraphs(*parts: object) -> list[str]:
    lines: list[str] = []
    for part in parts:
        if part is None:
            continue
        if isinstance(part, list):
            for item in part:
                text = str(item).strip()
                if text:
                    lines.append(text)
        else:
            text = str(part).strip()
            if text:
                lines.append(text)
    return lines


def adjustment_lines(card: dict) -> list[str]:
    adjustments = card.get("teaching_adjustments", {}) or {}
    lines: list[str] = []
    focus_more_on = as_list(adjustments.get("focus_more_on"))
    focus_less_on = as_list(adjustments.get("focus_less_on"))
    preferred_style = as_list(adjustments.get("preferred_explanation_style"))
    figure_priority = as_list(adjustments.get("figure_priority"))
    unresolved_concepts = as_list(adjustments.get("unresolved_concepts"))
    notes = str(adjustments.get("notes", "")).strip()

    if focus_more_on:
        lines.append("- 这次会额外加重这些部分: " + " / ".join(focus_more_on))
    if focus_less_on:
        lines.append("- 这次会适度压缩这些背景: " + " / ".join(focus_less_on))
    if preferred_style:
        lines.append("- 这次优先采用这些讲法: " + " / ".join(preferred_style))
    if figure_priority:
        lines.append("- 这次会优先强化这些图表: " + " / ".join(figure_priority))
    if unresolved_concepts:
        lines.append("- 这些概念仍被视为未完全讲透: " + " / ".join(unresolved_concepts))
    if notes:
        lines.append(f"- 讲解备注: {notes}")
    return lines


def figure_walkthrough(entry: dict, extra_note: str = "") -> list[str]:
    label = entry.get("label") or entry.get("id") or "Key Figure"
    title = entry.get("title", "")
    caption = entry.get("caption", "")
    teaching_point = entry.get("teaching_point", "")
    image_path = entry.get("image_path", "")
    page = entry.get("page")

    lines = [f"#### {label}" + (f" | {title}" if title else "")]
    if page:
        lines.append(f"- 页码（Page）: {page}")
    if caption:
        lines.append(f"- 这张图在画什么: {caption}")
    if teaching_point:
        lines.append(f"- 读图重点: {teaching_point}")
    if extra_note:
        lines.append(f"- 记忆加重项: {extra_note}")
    if image_path:
        lines.append("")
        lines.append(f"![{label}]({image_path})")
        lines.append("")

    lines.extend(
        [
            "先沿着数据流看，不要一开始就试图记住每个方框的名字。",
            "如果这是结构总览图，先抓主干，再抓模块，再抓模块之间的关系。",
            "如果你开始被缩写或层数绕晕，就回到一个问题：这张图到底在说明作者换掉了旧方法里的什么。",
        ]
    )
    return lines


def figure_section(card: dict) -> str:
    entries = card.get("key_figures", []) or []
    adjustments = card.get("teaching_adjustments", {}) or {}
    figure_priority = set(as_list(adjustments.get("figure_priority")))

    if not entries:
        return block("关键图表精讲（Key Figures）", ["- 当前还没有配置需要抽取的关键图页码。"])

    lines: list[str] = [
        "这一节不是把图贴上来就结束，而是把图真正讲清楚。",
        "",
    ]
    for entry in entries:
        label = str(entry.get("label") or entry.get("id") or "").strip()
        title = str(entry.get("title") or "").strip()
        extra_note = ""
        if label in figure_priority or title in figure_priority:
            extra_note = "用户在历史提问里对这张图有较高关注，本次会讲得更细。"
        lines.extend(figure_walkthrough(entry, extra_note))
        lines.append("")
    return block("关键图表精讲（Key Figures）", lines)


def table_section(entries: list[dict]) -> str:
    if not entries:
        return block("关键表格（Key Tables）", ["- 当前还没有配置需要重点讲解的表格。"])

    lines: list[str] = []
    for entry in entries:
        label = entry.get("label") or entry.get("id") or "Key Table"
        title = entry.get("title", "")
        caption = entry.get("caption", "")
        teaching_point = entry.get("teaching_point", "")
        page = entry.get("page")
        lines.append(f"#### {label}" + (f" | {title}" if title else ""))
        if page:
            lines.append(f"- 页码（Page）: {page}")
        if caption:
            lines.append(f"- 表格在比较什么: {caption}")
        if teaching_point:
            lines.append(f"- 你最该先盯住的列/行: {teaching_point}")
        lines.extend(
            [
                "- 先看比较对象，再看指标，最后看作者有没有在关键指标上真正赢得有说服力。",
                "- 如果表格很大，不要试图一次扫完全部数字，先找作者最希望你注意的对比。",
                "",
            ]
        )
    return block("关键表格（Key Tables）", lines)


def related_reads_section(entries: list[dict]) -> str:
    if not entries:
        return block("arXiv 延伸阅读（Related arXiv Reads）", ["- 当前还没有补充外部延伸阅读。"])

    lines: list[str] = [
        "如果本地库里还没有足够合适的延伸阅读，可以先从下面这些 arXiv 论文接上。",
        "",
    ]
    for entry in entries:
        title = entry.get("title", "")
        relation = entry.get("relation", "")
        why = entry.get("why", "")
        url = entry.get("url", "")
        lines.append(f"### {title}")
        if relation:
            lines.append(f"- 关系（Relation）: {relation}")
        if why:
            lines.append(f"- 为什么值得读: {why}")
        if url:
            lines.append(f"- arXiv: {url}")
        lines.append("")
    return block("arXiv 延伸阅读（Related arXiv Reads）", lines)


def reading_markdown(card: dict) -> str:
    source = card.get("source", {})
    source_path = source.get("path", "") if isinstance(source, dict) else ""
    script = card.get("teaching_script", {})
    adjustments = card.get("teaching_adjustments", {}) or {}

    abstract_walkthrough = as_list(script.get("abstract_walkthrough"))
    experiment_walkthrough = as_list(script.get("experiment_walkthrough"))
    takeaways = as_list(script.get("takeaways"))
    unresolved_concepts = as_list(adjustments.get("unresolved_concepts"))
    personal_focus = adjustment_lines(card)

    mastery_questions = as_list(script.get("mastery_questions")) or [
        "这篇论文到底要解决什么问题？",
        "作者换掉了什么旧做法，为什么敢这么换？",
        "关键图或关键实验到底证明了什么？",
        "如果你给别人讲这篇论文，你会怎么用三到五句话讲清楚？",
    ]

    method_overview = str(script.get("method_overview", "")).strip() or (
        "读方法部分时，不要一上来陷进公式。先抓整体骨架，再抓关键模块各自解决什么问题。"
    )
    method_walkthrough = str(script.get("method_walkthrough", "")).strip() or (
        "方法部分应该像讲课一样拆开：整体架构、关键模块、每个模块解决什么问题、这些模块为什么要一起工作。"
    )
    evidence_walkthrough = str(script.get("evidence_walkthrough", "")).strip() or (
        "实验部分最重要的不是把结果数字念一遍，而是判断这些证据能不能真正支撑作者的核心主张。"
    )
    retell_script = str(script.get("retell_script", "")).strip() or (
        "可以试着用一个短复述来检验自己：旧路线哪里不够，作者换成了什么，新路线为什么更值得继续追。"
    )

    if unresolved_concepts:
        method_overview += "\n\n- 结合历史提问，这次会特别补清楚: " + " / ".join(unresolved_concepts)

    parts = [
        frontmatter(card),
        f"# {card.get('title', '')}\n\n",
        block(
            "开场导读（Opening Guide）",
            join_paragraphs(
                f"- 一句话总结（One-line Summary）: {card.get('summary_one_line', '')}",
                f"- 为什么值得读（Why It Matters）: {card.get('why_it_matters', '')}",
                f"- 原始 PDF（Source PDF）: {source_path}",
                "",
                script.get("opening_hook") or "这里先回答一个问题：这篇论文为什么值得认真读，而不是只看一眼摘要就结束。",
            ),
        ),
        block(
            "本次讲解重点（Memory-Guided Focus）",
            personal_focus or ["- 当前没有额外的个性化加重项，将按通用讲义范式展开。"],
        ),
        block(
            "读前准备（Before We Read）",
            [
                f"- 领域（Domain）: {card.get('domain', '')}",
                f"- 主题（Topic）: {card.get('topic', '')}",
                f"- 角色（Role）: {card.get('role', '')}",
                f"- 难度（Difficulty）: {card.get('difficulty', '')}",
                "",
                f"- 核心问题（Core Problem）: {card.get('core_problem', '')}",
                f"- 核心方法（Core Method）: {card.get('core_method', '')}",
                "",
            ]
            + join_paragraphs(
                script.get("prerequisite_bridge")
                or "这里只补真正需要的前置知识，补到能继续读下去为止，而不是把背景课开成另一门课。"
            )
            + bullets(card.get("prerequisites", []), "当前还没有补充前置知识。"),
        ),
        sub_block(
            "标题怎么读（How To Read The Title）",
            join_paragraphs(
                script.get("title_walkthrough")
                or "标题通常已经暴露了作者的立场：要挑战什么旧路线，要强调什么新主干。"
            ),
        ),
        sub_block(
            "摘要逐句拆解（Abstract Walkthrough）",
            bullets(
                abstract_walkthrough,
                "当前还没有补充摘要拆解。可以先按“旧问题 -> 新方法 -> 结果 -> 意义”的顺序讲。",
            ),
        ),
        sub_block(
            "先看结论（Conclusion First）",
            join_paragraphs(
                script.get("conclusion_walkthrough")
                or "先看结论的目的不是偷懒，而是先抓住作者最终想让你记住的判断。"
            ),
        ),
        block(
            "作者与时代背景（Authors And Context）",
            join_paragraphs(
                script.get("author_context")
                or "这里应该交代作者背景、论文所处阶段，以及它为什么在当时显得重要。"
            ),
        ),
        block(
            "正文带读（Guided Reading）",
            ["下面这一部分按论文自己的推进顺序来讲：立问题、讲旧路线、提新结构、拿实验说服读者。"],
        ),
        sub_block(
            "引言：作者是怎么把问题立起来的（Introduction）",
            join_paragraphs(
                script.get("introduction_walkthrough")
                or "读引言时，重点看作者如何界定旧路线的瓶颈，以及为什么这些瓶颈值得被重新设计。"
            ),
        ),
        sub_block(
            "相关工作 / 基线：旧路线到底卡在哪里（Related Work / Baseline）",
            join_paragraphs(
                script.get("related_work_walkthrough")
                or "相关工作部分最重要的不是记名字，而是弄清楚作者到底在和哪几类方法对话。"
            ),
        ),
        sub_block(
            "方法总览：先抓主干，再看细节（Method Overview）",
            join_paragraphs(method_overview),
        ),
        sub_block(
            "方法细讲（Method Walkthrough）",
            join_paragraphs(method_walkthrough),
        ),
        figure_section(card),
        sub_block(
            "实验与证据：作者到底证明了什么（Experiments And Evidence）",
            join_paragraphs(evidence_walkthrough)
            + bullets(
                experiment_walkthrough,
                "当前还没有补充实验拆解。建议先回答：比了谁、怎么比、为什么这个结果真的支持作者的结论。",
            )
            + bullets(card.get("core_evidence", []), "当前还没有提炼核心证据。"),
        ),
        table_section(card.get("key_tables", [])),
        sub_block(
            "局限与边界（Limitations）",
            join_paragraphs(
                script.get("limitation_walkthrough")
                or "真正读懂一篇论文，不只是知道它做成了什么，还要知道它还没解决什么。"
            ),
        ),
        block(
            "读完你应该带走什么（What To Retain）",
            bullets(
                takeaways,
                "当前还没有整理最终 takeaways。建议至少提炼出问题、方法、证据、位置这四件事。",
            ),
        ),
        block("30 秒复述模板（Short Retell）", join_paragraphs(retell_script)),
        block(
            "你的问题（Open Questions）",
            bullets(card.get("open_questions", []), "当前还没有记录新的疑问。")
            + bullets(unresolved_concepts, "当前还没有标记未解决概念。"),
        ),
        block(
            "我的笔记（My Notes）",
            [
                "### 划线与重点（Highlights）",
                "",
                "### 我自己的解释（My Explanation）",
                "",
                "### 我还没完全想通的地方（Still Confusing）",
                "",
                "### 反思（Reflection）",
                "",
            ]
            + join_paragraphs(
                script.get("reflection_prompt")
                or "试着不看原文，用自己的话把这篇论文讲给一个刚入门的人听。讲不顺的地方，通常就是还没真正吃透的地方。"
            ),
        ),
        block("掌握度检查（Mastery Check）", bullets(mastery_questions, "当前还没有补充掌握度问题。")),
        block(
            "本地延伸阅读（Local Follow-Up Reads）",
            ["### 前置论文（Predecessor）"]
            + bullets(card.get("next_reads", {}).get("predecessors", []), "当前还没有合适的本地前置论文。")
            + ["", "### 后续论文（Successor）"]
            + bullets(card.get("next_reads", {}).get("successors", []), "当前还没有合适的本地后续论文。")
            + ["", "### 平行阅读（Parallel）"]
            + bullets(card.get("next_reads", {}).get("parallel", []), "当前还没有合适的本地平行阅读。"),
        ),
        related_reads_section(card.get("external_related_reads", [])),
    ]
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a single reading.md file from a paper card.")
    parser.add_argument("paper_id", help="Paper id that already exists in memory.")
    parser.add_argument("--root", default=".", help="Workspace root.")
    parser.add_argument("--memory-dir", default=".ob-paper-read-memory", help="Memory directory name.")
    parser.add_argument("--vault-dir", default="reading-vault", help="Vault output directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing markdown files.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    card_path = root / args.memory_dir / "papers" / f"{args.paper_id}.json"
    if not card_path.exists():
        raise FileNotFoundError(f"Paper card not found: {card_path}")

    card = load_card(card_path)
    if card.get("status") in {"saved", "classified", "selected_as_primary", "guide_generated"}:
        card["status"] = "reading_generated"
        save_card(card_path, card)

    paper_dir = root / args.vault_dir / "papers" / args.paper_id
    if args.force:
        remove_legacy_files(paper_dir)

    write_text(paper_dir / "reading.md", reading_markdown(card), args.force)

    print(f"Created bundle in: {paper_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
