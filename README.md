# ob-paper-read

[简体中文](./README.zh-CN.md) | English

`ob-paper-read` is an Obsidian-oriented paper-reading skill pack.

It is designed for a workflow where:

- the user uploads one or more PDF papers in Codex / Claude Code / OpenClaw
- the skill saves those PDFs into a local library
- the skill generates a lecture-style `reading.md`
- the user reads the PDF and `reading.md` side by side in Obsidian
- chat turns, reading state, and reusable questions are written into local memory

## What This Repo Contains

- `SKILL.md`: the main skill contract
- `scripts/`: local helpers for memory bootstrap, paper cards, reading note generation, comparison briefs, and figure extraction
- `references/`: setup, memory, output, compatibility, plugin, and adapter docs
- `obsidian-plugin/`: a minimal Obsidian sidebar chat plugin

## Current V1 Scope

- PDF uploads only
- local library only
- one primary paper at a time
- one main output file per paper: `reading.md`
- detailed lecture-style guidance instead of short summary
- optional figure extraction into `assets/`

Not in V1:

- URL ingestion as the default path
- web search as a required dependency
- a domain-specific knowledge map

## Core Product Shape

- host chat is responsible for file upload
- `ob-paper-read` is responsible for classification, memory, and output structure
- Obsidian is the reading workspace

## Output Style

The main deliverable is `reading.md`.

It should feel like:

- a lecture handout
- a guided reading note
- a teacher walking the user through title, abstract, conclusion, body, figures, evidence, and limits

It should not feel like:

- "here is a short summary"
- a flat bullet dump
- an unstructured note shell

Default language:

- Chinese first
- preserve standard English technical terms where accuracy matters
- use `English term (Chinese explanation)` when helpful

## Obsidian Chat

This repo includes `OB Paper Read Chat`, a minimal Obsidian plugin that gives the vault a right-sidebar chat panel.

Modes:

- `Bridge`: copy an Obsidian context packet into Codex / Claude Code / OpenClaw
- `API`: direct in-Obsidian chat against an OpenAI-compatible endpoint

## Quick Start

1. Read `references/setup.md`.
2. Run `scripts/bootstrap_memory.py`.
3. Create or ingest one paper card.
4. Generate `reading.md` with `scripts/create_reading_bundle.py`.
5. Optionally extract key figures with `scripts/extract_pdf_figures.py`.
6. Open the PDF, `reading.md`, and the chat plugin in Obsidian.

## Repository Notes

- keep machine-specific paths out of committed examples when possible
- keep API keys out of repo files and local memory
- keep raw PDFs immutable
