# Setup And Quickstart

## Goal

Get a new user from “I have a PDF” to “I can open a lecture-style reading note in Obsidian” with the fewest moving parts.

V1 scope:

- PDF uploads only
- local library only
- local-memory workflow
- Obsidian recommended

## Prerequisites

Required:

- Python 3.11 or newer
- local filesystem access for storing PDFs and Markdown outputs

Recommended:

- Obsidian
- a dedicated vault or subfolder for reading outputs

Optional:

- `PDF++` for a stronger PDF reading experience
- `Templater` for later automation
- `Dataview` for later overviews
- `OB Paper Read Chat` from this repo if the user wants direct in-Obsidian chat

## Recommended Obsidian Plugins

Minimum useful setup:

- `PDF++`
- `OB Paper Read Chat`
- `Templater`

Nice to have:

- `Dataview`
- `QuickAdd`
- `Omnisearch`

Important mode choice:

- `Bridge` mode: no extra API key; the plugin packages context and hands it to Codex / Claude Code / OpenClaw outside Obsidian
- `API` mode: direct chat inside Obsidian; requires an OpenAI-compatible endpoint and usually an API key

## Python Dependencies

The included scripts only require the standard library, plus:

- `PyYAML` for skill validation
- `PyMuPDF` if you want figure extraction

Windows PowerShell:

```powershell
python -m pip install PyYAML PyMuPDF
```

macOS zsh/bash:

```bash
python3 -m pip install PyYAML PyMuPDF
```

## Validate The Skill

Windows PowerShell:

```powershell
$validator = Join-Path $env:USERPROFILE '.codex\skills\.system\skill-creator\scripts\quick_validate.py'
python $validator .\ob-paper-read
```

macOS zsh/bash:

```bash
validator="$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py"
python3 "$validator" ./ob-paper-read
```

## Suggested Workspace Layout

```text
workspace-root/
|- raw-papers/
|- reading-vault/
`- .ob-paper-read-memory/
```

Example placeholders:

- Windows workspace root: `D:\your-workspace`
- macOS workspace root: `/Users/<name>/your-workspace`

## First-Time Initialization

Create the memory workspace.

Windows PowerShell:

```powershell
python .\ob-paper-read\scripts\bootstrap_memory.py --root D:\your-workspace
```

macOS zsh/bash:

```bash
python3 ./ob-paper-read/scripts/bootstrap_memory.py --root /Users/<name>/your-workspace
```

Then edit:

- Windows: `D:\your-workspace\.ob-paper-read-memory\user-profile.json`
- macOS: `/Users/<name>/your-workspace/.ob-paper-read-memory/user-profile.json`

Fill:

- `workspace.obsidian_vault_path`
- `workspace.raw_library_path`
- `workspace.guide_output_path`

Do not store API keys in `user-profile.json`.

## Ingest One PDF Manually

Normal end-user flow is host upload in chat.

Manual commands below are mainly for:

- first-time setup
- local testing
- migration of existing PDFs

Windows PowerShell:

```powershell
python .\ob-paper-read\scripts\create_paper_card.py "Paper Title" `
  --root D:\your-workspace `
  --source-path "D:\path\to\paper.pdf" `
  --domain "your-domain" `
  --topic "your-topic" `
  --role "landmark paper" `
  --difficulty "intermediate" `
  --primary
```

macOS zsh/bash:

```bash
python3 ./ob-paper-read/scripts/create_paper_card.py "Paper Title" \
  --root /Users/<name>/your-workspace \
  --source-path "/Users/<name>/path/to/paper.pdf" \
  --domain "your-domain" \
  --topic "your-topic" \
  --role "landmark paper" \
  --difficulty "intermediate" \
  --primary
```

## Create The Reading Note

Windows PowerShell:

```powershell
python .\ob-paper-read\scripts\create_reading_bundle.py <paper-id> `
  --root D:\your-workspace `
  --vault-dir reading-vault `
  --suggest-concepts
```

macOS zsh/bash:

```bash
python3 ./ob-paper-read/scripts/create_reading_bundle.py <paper-id> \
  --root /Users/<name>/your-workspace \
  --vault-dir reading-vault \
  --suggest-concepts
```

This creates:

- `reading-vault/papers/<paper-id>/reading.md`

If concept suggestions are detected, the command also prints:

- a short concept candidate list
- why the suggestion is being shown now
- the next `update_global_pages.py` command to run if you want to accept it

## Update The Lightweight Concept Layer

After one paper has enough real reading context, you can update the optional concept layer.

Windows PowerShell:

```powershell
python .\ob-paper-read\scripts\update_global_pages.py <paper-id> `
  --root D:\your-workspace `
  --vault-dir reading-vault `
  --concept "self-attention"
```

macOS zsh/bash:

```bash
python3 ./ob-paper-read/scripts/update_global_pages.py <paper-id> \
  --root /Users/<name>/your-workspace \
  --vault-dir reading-vault \
  --concept "self-attention"
```

This updates:

- `reading-vault/concepts/`
- `reading-vault/overviews/index.md`

## Extract Key Figures

If the paper card already contains `key_figures` or `key_tables` with page numbers:

Windows PowerShell:

```powershell
python .\ob-paper-read\scripts\extract_pdf_figures.py <paper-id> `
  --root D:\your-workspace `
  --vault-dir reading-vault
```

macOS zsh/bash:

```bash
python3 ./ob-paper-read/scripts/extract_pdf_figures.py <paper-id> \
  --root /Users/<name>/your-workspace \
  --vault-dir reading-vault
```

This creates:

- `reading-vault/papers/<paper-id>/assets/`

Then regenerate `reading.md` so the figures are embedded.

## Normal User Flow

1. The user uploads one or more PDFs in Codex / Claude Code / OpenClaw.
2. The host exposes those uploaded files to the agent.
3. The skill saves them into `workspace.raw_library_path`.
4. The skill classifies them and asks the user to choose one primary paper.
5. The skill generates `reading.md`.
6. The skill optionally renders key figure assets.
7. The user opens the PDF and `reading.md` in Obsidian.

Meaning of `raw-papers/`:

- it is an internal storage destination
- it is not a folder the user needs to browse manually in normal use
- it is where uploaded PDFs are persisted after the host hands them to the agent

## Open In Obsidian

Recommended working layout:

- left pane: source PDF
- center pane: `reading.md`
- right sidebar: AI chat panel

For plugin installation and chat usage:

- see `references/obsidian-plugin.md`
