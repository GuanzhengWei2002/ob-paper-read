# ob-paper-read

[简体中文](./README.zh-CN.md) | English

`ob-paper-read` is an Obsidian-first paper reading workflow for Codex, Claude Code, and OpenClaw.

Instead of generating a shallow paper summary, it helps turn uploaded PDFs into a structured reading experience:

- save the paper into a local library
- classify it into a lightweight reading context
- generate a lecture-style `reading.md`
- extract key figures into local assets
- preserve reading state, question memory, and cross-session context

The intended workspace is simple:

- left: the source PDF
- center: `reading.md`
- right: an AI chat panel inside Obsidian

## Why This Exists

Most paper tools are optimized for retrieval or summarization.

`ob-paper-read` is optimized for reading:

- staying close to the original paper
- explaining section by section
- turning figures into teaching moments
- helping the reader build memory instead of collecting fragments

## What It Produces

For each paper, the core output is:

- `reading.md`: the main lecture-style reading note
- `assets/`: extracted key figures or tables
- local memory records for paper state, questions, and sessions

The goal is for `reading.md` to feel closer to a guided handout than a summary shell.

## Core Design

- PDF-first: V1 starts from uploaded PDF files
- local-first: files and memory stay in the user’s workspace
- single-paper focus: when multiple PDFs are uploaded, the user chooses one primary paper
- detailed reading by default: the output should explain, not skim
- Obsidian-native workflow: PDF, Markdown, and chat live in one workspace

## Repository Structure

- `SKILL.md`: the main skill definition
- `scripts/`: helper scripts for memory bootstrap, paper cards, reading bundle generation, figure extraction, and comparison context
- `references/`: setup docs, output rules, memory schema, plugin notes, and platform adapters
- `obsidian-plugin/`: a minimal sidebar chat plugin for Obsidian

## Obsidian Chat

This repository includes `OB Paper Read Chat`, a small Obsidian plugin that adds a right sidebar chat panel.

It supports two usage modes:

- `Bridge`: package the current Obsidian context and continue the conversation in Codex / Claude Code / OpenClaw
- `API`: chat directly inside Obsidian through an OpenAI-compatible endpoint

## Quick Start

1. Read [`references/setup.md`](./references/setup.md).
2. Run `scripts/bootstrap_memory.py`.
3. Create or ingest a paper card.
4. Generate `reading.md` with `scripts/create_reading_bundle.py`.
5. Optionally extract figures with `scripts/extract_pdf_figures.py`.
6. Open the PDF, `reading.md`, and the chat sidebar in Obsidian.

## Current Scope

V1 includes:

- PDF uploads
- local storage
- a single primary paper flow
- lecture-style Markdown output
- optional figure extraction

V1 does not aim to be:

- a general search engine
- a web crawler
- a giant knowledge graph product

## Language Style

The default output style is:

- Chinese-first
- English technical terms preserved when they are the clearest form
- optional bilingual phrasing such as `self-attention（自注意力）`

## Notes

- keep machine-specific paths out of committed examples
- do not store API keys in repo files or local memory
- keep raw PDFs immutable
