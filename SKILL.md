---
name: ob-paper-read
description: Obsidian-oriented PDF paper reading with single-paper focus, detailed-reading guidance, local memory, and a single Markdown deliverable. Use when Codex needs to turn one or more uploaded PDF papers into an Obsidian-friendly reading workflow with classification, reading.md, reading status, question memory, and later comparison support.
---

# Ob Paper Read

## Overview

Run paper reading as a local workspace, not a one-shot summary.

V1 scope:

- PDF uploads only
- local library only
- Obsidian-oriented outputs
- no external search or URL ingestion
- Chinese-first output with English technical terms kept when appropriate

Normal user flow:

- user uploads PDF files directly in the host chat UI
- the host exposes those files to the agent
- the skill saves them into the configured local PDF library path
- the user reads the generated Markdown outputs in Obsidian

Treat the workspace as four layers:

- immutable raw PDF sources
- one lecture-style Markdown artifact, `reading.md`
- rendered figure assets inside `assets/`
- persistent memory across sessions

Load [references/session-flow.md](references/session-flow.md) for the reading workflow. Load [references/memory-schema.md](references/memory-schema.md) when writing persistent memory. Load [references/output-artifacts.md](references/output-artifacts.md) when creating Markdown deliverables. Load [references/setup.md](references/setup.md) when the user asks about prerequisites or quickstart. Load [references/compatibility.md](references/compatibility.md) when the user asks about Windows or macOS usage, path handling, or shell differences. Load [references/obsidian-workspace.md](references/obsidian-workspace.md) when the user asks about panes, context packets, or reading-state logic. Load [references/obsidian-plugin.md](references/obsidian-plugin.md) when the user asks where the AI chat lives inside Obsidian or how context returns from Obsidian into the model. Load [references/platform-adapters.md](references/platform-adapters.md) when the skill needs to run in Codex, Claude Code, or OpenClaw.

## Core Rules

1. Default to one primary paper.
2. Treat multiple uploaded PDFs as a candidate pool, not a simultaneous reading assignment.
3. Use a detailed-reading route by default.
4. Answer interruptions, then explicitly return to the last reading anchor.
5. Judge mastery by what the user can explain.
6. Recommend from the local library only in V1.
7. Do not mark a paper as read just because it was saved.
8. Produce concrete files, not just chat answers.
9. Default to Chinese explanations, with English technical terms preserved where they help accuracy.
10. In Markdown deliverables, prefer Chinese section titles with optional English in parentheses.
11. Treat "three-pass reading" as an internal method hint, not the default user-facing structure.
12. `reading.md` should read like a guided lecture note, not like a generic summary.
13. When a figure matters, extract it from the PDF and embed it into `reading.md`.
14. Reference materials may shape the prompt internally, but the final output should not mention those reference authors or sources unless the user explicitly asks for them.
15. Default to very detailed explanation, not terse summarization.
16. User memory may adjust emphasis, but the main lecture-note structure should still follow the general teaching pattern.
17. Use `teaching_adjustments` and resolved/unresolved question memory to strengthen weak spots, not to replace the paper’s main explanatory route.

## Workflow

### 1. Intake

Inspect uploaded PDFs or local PDF paths.

Prefer this interaction model:

- end user uploads PDFs directly in the chat dialog
- the skill copies or saves those uploaded files into the configured local PDF library path

Treat manual local file paths as a fallback for setup, testing, or migration.

For each PDF, produce:

- one-line role
- rough difficulty
- domain
- topic
- likely relationship to the others

If multiple PDFs are present, ask the user to choose one primary paper before teaching.

### 2. Classification

Classify each paper with lightweight labels:

- `domain`
- `topic`
- `role`
- `difficulty`

Prefer broad stable labels over fragile micro-taxonomies.

Create or update a paper card immediately.

When question memory already exists, write those signals into lightweight `teaching_adjustments` fields such as:

- `focus_more_on`
- `focus_less_on`
- `preferred_explanation_style`
- `figure_priority`
- `unresolved_concepts`

These should bias later regeneration, but they should not replace the shared lecture-note scaffold.

### 3. Detailed Reading
Start by quickly clarifying:

1. title
2. abstract
3. conclusion

Then continue into the body with a detailed route:

4. introduction
5. related work or baseline
6. method
7. key figure
8. key table or experiment
9. limitation or discussion

Explain:

- core problem
- core method
- claimed result
- why it matters
- what the user should retain

Fill only the prerequisites needed to keep the user moving.

For each major section, answer:

- What is this section doing?
- Why does it exist?
- What should the user retain?

### 4. Reflection And Deepening

If the user wants more depth, deepen the same reading file rather than switching to a separate pass-oriented artifact.

Focus on:

- revisit marked confusions
- resolve key details
- ask author-view reflection questions
- help the user restate the paper in their own words

If the user has repeated unresolved questions, update:

- the paper card’s `teaching_adjustments`
- the question record’s `status`
- the next generation pass for `reading.md`

### 5. Mastery And Status

Use reading status values such as:

- `saved`
- `classified`
- `reading_generated`
- `selected_as_primary`
- `reading_in_progress`
- `mastery_checked`
- `read_completed`
- `compared`

Promote a paper to `read_completed` only when there is evidence such as reading time, notes, annotations, mastery answers, or a written summary.

### 6. Recommendation

Recommend next steps from three buckets:

- predecessor papers
- successor papers
- parallel papers

Use only the local library in V1. If there is no good local next read, say what is missing.

### 7. Comparison Reading

Only compare after the first paper has been read and written to memory. Read the first paper card, concept cards, summary, and question memory before teaching the next paper.

Use [scripts/build_compare_context.py](scripts/build_compare_context.py) to generate a reusable comparison brief from two stored paper cards.

## Outputs

Persist:

- user profile
- paper card
- concept cards
- question memory
- session summary
- recommendation cache
- comparison brief

Generate:

- `reading.md`
- figure assets under `papers/<paper-id>/assets/`

Use:

- [scripts/bootstrap_memory.py](scripts/bootstrap_memory.py) to create the local memory workspace
- [scripts/create_paper_card.py](scripts/create_paper_card.py) to create a paper card
- [scripts/create_reading_bundle.py](scripts/create_reading_bundle.py) to create the Markdown reading bundle
- [scripts/extract_pdf_figures.py](scripts/extract_pdf_figures.py) to render key figure and table pages into image assets

## Resource Map

Read these files only when needed:

- [references/session-flow.md](references/session-flow.md)
- [references/memory-schema.md](references/memory-schema.md)
- [references/output-artifacts.md](references/output-artifacts.md)
- [references/setup.md](references/setup.md)
- [references/compatibility.md](references/compatibility.md)
- [references/obsidian-workspace.md](references/obsidian-workspace.md)
- [references/obsidian-plugin.md](references/obsidian-plugin.md)
- [references/platform-adapters.md](references/platform-adapters.md)
