# Platform Adapters

## Portability Contract

Keep the skill portable by treating the folder as a prompt pack:

- `SKILL.md` holds the core behavior
- `references/` holds detailed contracts
- `scripts/` holds deterministic helpers

## Codex

Recommended prompt:

`Use $ob-paper-read to turn the PDF paper I uploaded into an Obsidian-friendly reading workflow with a single reading.md file and reading memory.`

## Claude Code

Load:

1. `SKILL.md`
2. `references/session-flow.md`
3. `references/memory-schema.md`
4. `references/obsidian-workspace.md`

Wrapper prompt:

```text
Use the workflow in ./ob-paper-read/SKILL.md.
If multiple PDFs are uploaded, ask me to choose one primary paper.
Guide me with a detailed reading route.
Answer interruptions, then return to the last reading anchor.
Persist memory using ./ob-paper-read/references/memory-schema.md.
```

## OpenClaw

Load:

1. `SKILL.md`
2. `references/session-flow.md`
3. `references/memory-schema.md`
4. `references/output-artifacts.md`
5. `references/obsidian-workspace.md`

Suggested smoke-test prompt:

```text
Use ./ob-paper-read as a prompt pack.
I uploaded 2 PDF papers.
First classify them, ask me to choose one primary paper, then create a single reading.md file for the chosen paper.
Default to a detailed reading structure and keep track of reading status and question memory.
Do not use any external APIs or URLs.
```

## Practical Note

The portable layer here is prompt and workflow compatibility, not a claim that all three platforms share the same native packaging model.
