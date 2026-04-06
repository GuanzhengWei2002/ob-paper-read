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


def figure_walkthrough(entry: dict) -> list[str]:
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
    if image_path:
        lines.append("")
        lines.append(f"![{label}]({image_path})")
        lines.append("")

    lines.extend(
        [
            "先不要急着把图里的每个方框都看成一个术语清单，更好的读法是先沿着数据流看：输入是怎么进来，表示是怎么被变换，最后输出是怎么生成的。",
            "如果这是结构总览图，你最应该先抓住的是主干，而不是角落里的细节。先看大的模块分工，再看每个模块内部各自承担什么职责。",
            "如果你发现自己开始被层数、箭头、缩写绕晕了，停一下，回到一个最简单的问题：这张图到底想证明作者的方法和旧方法相比，换掉了什么。",
        ]
    )
    return lines


def figure_section(entries: list[dict]) -> str:
    if not entries:
        return block("关键图表精讲（Key Figures）", ["- 当前还没有配置需要抽取的关键图页码。"])

    lines: list[str] = [
        "这一节不是把图贴上来就结束，而是把图真正讲明白。读图时先抓主干，再抓模块，再抓作者想让你相信的设计选择。",
        "",
    ]
    for entry in entries:
        lines.extend(figure_walkthrough(entry))
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
                "- 先看比较对象是谁，再看评价指标是什么，最后看作者有没有在关键指标上真正赢得有说服力。",
                "- 如果表格很大，不要试图一次扫完所有数字。先找作者最想你看到的那一组对比。",
                "",
            ]
        )
    return block("关键表格（Key Tables）", lines)


def related_reads_section(entries: list[dict]) -> str:
    if not entries:
        return block("arXiv 延伸阅读（Related arXiv Reads）", ["- 当前还没有补充外部延伸阅读。"])

    lines: list[str] = [
        "本地库里如果还没有足够合适的延伸阅读，可以先从下面这些 arXiv 论文接上。",
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

    abstract_walkthrough = as_list(script.get("abstract_walkthrough"))
    experiment_walkthrough = as_list(script.get("experiment_walkthrough"))
    takeaways = as_list(script.get("takeaways"))
    mastery_questions = as_list(script.get("mastery_questions")) or [
        "这篇论文到底要解决什么问题？",
        "作者换掉了什么旧做法，为什么敢这么换？",
        "Figure 1 或关键实验到底证明了什么？",
        "如果你给别人讲这篇论文，你会怎么用三到五句话讲清楚？",
    ]

    method_overview = str(script.get("method_overview", "")).strip()
    if not method_overview:
        method_overview = (
            "读方法部分时，不要一上来陷进公式。先抓整体骨架，再抓几个关键模块各自解决什么问题。"
            "如果主干想清楚了，细节会容易挂上去。"
        )

    evidence_walkthrough = str(script.get("evidence_walkthrough", "")).strip()
    if not evidence_walkthrough:
        evidence_walkthrough = (
            "实验部分最重要的不是把结果数字念一遍，而是判断这些证据能不能真正支撑作者的核心主张。"
        )

    retell_script = str(script.get("retell_script", "")).strip()
    if not retell_script:
        retell_script = (
            "可以试着用一个短复述来检验自己：旧路线哪里不够，作者换成了什么，新路线为什么更值得继续追。"
        )

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
                script.get("opening_hook") or "这一节应该先告诉读者：这篇论文为什么值得认真读，而不是只看一个摘要就结束。",
            ),
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
                or "这一节只补真正需要的前置知识，补到能继续读下去为止，而不是把背景课开成另一门课。"
            )
            + bullets(card.get("prerequisites", []), "当前还没有补充前置知识。"),
        ),
        sub_block(
            "标题怎么读（How To Read The Title）",
            join_paragraphs(
                script.get("title_walkthrough")
                or "标题不是装饰，它通常已经暴露了作者的立场：要挑战什么旧路线，要强调什么新主干。"
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
                or "先看结论的目的不是偷懒，而是先抓住作者最终想让你记住的判断，再回头读正文会更有方向。"
            ),
        ),
        block(
            "作者与时代背景（Authors And Context）",
            join_paragraphs(
                script.get("author_context")
                or "这里应该交代作者来自什么背景、论文处于什么技术阶段、为什么这篇工作在当时显得重要。"
            ),
        ),
        block(
            "正文带读（Guided Reading）",
            [
                "下面这一部分不是泛泛复述，而是按照论文自己的推进顺序来讲：作者先立问题，再交代旧路线，再提出新结构，最后拿实验去证明。",
            ],
        ),
        sub_block(
            "引言：作者是怎么把问题立起来的（Introduction）",
            join_paragraphs(
                script.get("introduction_walkthrough")
                or "读引言时，要盯住作者如何界定旧路线的瓶颈，以及为什么这些瓶颈值得被重新设计。"
            ),
        ),
        sub_block(
            "相关工作 / 基线：旧路线到底卡在哪里（Related Work / Baseline）",
            join_paragraphs(
                script.get("related_work_walkthrough")
                or "相关工作部分最重要的不是记名字，而是搞清楚作者到底在和哪几类方法对话。"
            ),
        ),
        sub_block(
            "方法总览：先抓主干，再看细节（Method Overview）",
            join_paragraphs(method_overview),
        ),
        sub_block(
            "方法细讲（Method Walkthrough）",
            join_paragraphs(
                script.get("method_walkthrough")
                or "方法部分应该像讲课一样拆开：整体架构、关键模块、每个模块解决什么问题、这些模块为什么要一起工作。"
            ),
        ),
        figure_section(card.get("key_figures", [])),
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
        block(
            "30 秒复述模板（Short Retell）",
            join_paragraphs(retell_script),
        ),
        block(
            "你的问题（Open Questions）",
            bullets(card.get("open_questions", []), "当前还没有记录新的疑问。"),
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
        block(
            "掌握度检查（Mastery Check）",
            bullets(mastery_questions, "当前还没有补充掌握度问题。"),
        ),
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
