# Compatibility

## Goal

Keep the skill usable on both Windows and macOS without changing the core workflow.

Supported intent:

- Windows with PowerShell and Obsidian
- macOS with zsh or bash and Obsidian

## Core Compatibility Rules

1. Use Python scripts for file operations whenever possible.
2. Treat paths as data, not shell snippets.
3. Avoid hardcoding drive letters or home-directory assumptions in prompts.
4. Store absolute source PDF paths in memory after the host has saved the uploaded file locally.
5. Prefer UTF-8 for all Markdown and JSON files.
6. Read JSON with UTF-8 BOM tolerance when files may be rewritten by Windows tools.
7. Normalize absolute PDF paths to forward-slash form when writing Obsidian frontmatter.

## Why The Scripts Are Portable

The included scripts use Python and `pathlib`, so path joining and directory creation are already cross-platform.

Portable scripts:

- `scripts/bootstrap_memory.py`
- `scripts/create_paper_card.py`
- `scripts/create_reading_bundle.py`
- `scripts/build_compare_context.py`

## Path Examples

Windows examples:

- workspace root: `D:\paper-read-workspace`
- raw PDF library: `D:\paper-read-workspace\raw-papers`
- Obsidian vault: `D:\paper-read-workspace\reading-vault`

macOS examples:

- workspace root: `/Users/<name>/paper-read-workspace`
- raw PDF library: `/Users/<name>/paper-read-workspace/raw-papers`
- Obsidian vault: `/Users/<name>/paper-read-workspace/reading-vault`

## Host Upload Behavior

Normal user flow should stay the same on both operating systems:

1. user uploads a PDF in the host chat UI
2. the host exposes the uploaded file to the agent
3. the skill saves or copies that file into the configured local PDF library path
4. the saved absolute local path is written into the paper card

Do not assume the temporary upload path itself is stable. Persist a copy into the user's library path.

## Shell Differences

On Windows:

- default examples use PowerShell
- line continuation uses backtick
- absolute paths often include drive letters

On macOS:

- default examples should use `bash` or `zsh`
- line continuation uses backslash
- absolute paths begin with `/Users/...`

When writing docs or examples, prefer providing both forms if the command is user-facing.

## Obsidian Notes

Obsidian itself is cross-platform, so the important compatibility points are:

- the vault path in `user-profile.json`
- the raw PDF library path in `user-profile.json`
- any plugin-specific local path settings
- frontmatter should avoid raw Windows backslashes in YAML string values

Keep those values user-configurable and never hardcode them in scripts.

## Validation Notes

If a user cannot run the bundled validator script, they should still be able to run:

- `python -m py_compile ...`
- the four included Python scripts directly

That gives a lightweight cross-platform smoke test.
