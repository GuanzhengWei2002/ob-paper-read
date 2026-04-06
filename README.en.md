# ob-paper-read

[简体中文](./README.md) | English

`ob-paper-read` is a paper-reading workflow built for Codex, Claude Code, OpenClaw, and Obsidian.

It is not meant to be a “summarize this paper quickly” tool.  
It is meant to turn a PDF paper into a reading process that is easier to follow, interrupt, question, and retain.

## What It Tries To Solve

Many tools are good at finding papers, collecting papers, or summarizing papers.  
`ob-paper-read` focuses on a different problem: **how to actually read a paper well.**

The intended workspace is simple:

- left: the source PDF
- center: a lecture-style `reading.md`
- right: an AI chat panel inside Obsidian

## Core Capabilities

- start from PDF uploads and save papers into a local library
- create lightweight classification and reading context
- generate a detailed lecture-style `reading.md`
- extract key figures into local `assets/`
- record reading state, question history, and cross-session memory
- let user questions influence later emphasis without replacing the shared teaching pattern

## Outputs

For each paper, the core outputs are:

- `reading.md`
- `assets/`
- local memory records for paper state, questions, sessions, and teaching adjustments

The goal is not to create many files.  
The goal is for `reading.md` itself to feel like a guided lecture note that can be read, questioned, and revisited.

## Product Shape

- `PDF-first`: V1 starts from PDF upload
- `local-first`: files and memory stay local by default
- `single-paper focus`: when multiple PDFs are uploaded, the user chooses one primary paper
- `detailed reading by default`: explain deeply instead of skimming
- `Obsidian-native`: keep PDF, Markdown, and chat in one workspace

## Repository Structure

- `SKILL.md`: the main skill definition
- `scripts/`: helper scripts for memory bootstrap, paper cards, reading generation, figure extraction, and comparison context
- `references/`: setup docs, output rules, memory schema, plugin notes, and platform adapters
- `obsidian-plugin/`: the Obsidian right-sidebar chat plugin

## Obsidian Chat

This repository includes `OB Paper Read Chat`, a small Obsidian plugin that adds a right sidebar chat panel.

It supports two usage modes:

- `Bridge`: package the current Obsidian context and continue the conversation in Codex / Claude Code / OpenClaw
- `API`: chat directly inside Obsidian through an OpenAI-compatible endpoint

## Quick Start

1. Read [`references/setup.md`](./references/setup.md)
2. Run `scripts/bootstrap_memory.py`
3. Create or ingest a paper card
4. Generate `reading.md` with `scripts/create_reading_bundle.py`
5. Optionally extract figures with `scripts/extract_pdf_figures.py`
6. Open the PDF, `reading.md`, and the chat sidebar in Obsidian

## Current Scope

V1 includes:

- PDF uploads
- local storage
- a single primary paper flow
- lecture-style Markdown output
- optional figure extraction
- question-driven `teaching_adjustments`

V1 does not aim to be:

- a general search engine
- a web crawler
- a giant knowledge graph product

## Language Style

Default output style:

- Chinese-first
- keep standard English technical terms when they are the clearest form
- use mixed phrasing such as `self-attention（自注意力）` when helpful

## Notes

- keep machine-specific paths out of committed examples
- do not store API keys in repo files or local memory
- keep raw PDFs immutable
