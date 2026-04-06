# Obsidian Workspace

## Goal

Use Obsidian as the main reading surface:

- left pane: source PDF
- center pane: `reading.md`
- right sidebar: AI chat

Without a plugin, the right-side AI chat surface is missing. That means the user can still read the files, but cannot naturally ask questions inside Obsidian or send Obsidian context back into the model.

## Recommended Plugins

Required for the intended product feel:

- `OB Paper Read Chat`: right-sidebar chat, context packet, question memory, session writes

Recommended:

- `PDF++`: better PDF reading, highlighting, and note linking

Helpful but optional:

- `Dataview`: overview tables and reading dashboards
- `Templater`: custom note templates
- `QuickAdd`: repeated reading commands
- `Omnisearch`: stronger search

## Suggested Vault Layout

```text
vault-root/
|- raw-papers/
|- papers/
|  `- <paper-id>/
|     |- reading.md
|     |- assets/
|     `- compare/
|- overviews/
`- .ob-paper-read-memory/
```

## Context Packet

The plugin should not send the entire vault. It should send a compact context packet.

Recommended shape:

```json
{
  "generated_at": "",
  "active_file": {
    "path": "",
    "name": "",
    "extension": ""
  },
  "active_markdown": {
    "path": "",
    "selection": "",
    "headings": [],
    "frontmatter": {}
  },
  "paper": {
    "paper_id": "",
    "title": "",
    "status": "",
    "domain": "",
    "topic": "",
    "role": "",
    "source_pdf": "",
    "open_questions": [],
    "reading_progress": {}
  },
  "related_questions": []
}
```

Prioritize:

1. current `reading.md`
2. current selection
3. current paper card JSON
4. recent repeated questions
5. session turns for the same paper

## Reading Status

Do not treat `saved` as `read`.

Useful evidence:

- active reading minutes
- question count
- note edits
- highlights or annotations
- written reflection
- mastery answers

Useful thresholds:

- `reading_in_progress`: at least one real interaction
- `mastery_checked`: the user answered at least one mastery question after meaningful reading
- `read_completed`: the user can restate the paper and has written reflection or summary

## Question And Session Memory

Questions asked in the plugin should be written back to:

- `.ob-paper-read-memory/questions/`
- `.ob-paper-read-memory/sessions/`

That lets later sessions pull in:

- repeated confusions
- previous answers
- paper-specific conversation history

This is the core mechanism that turns the system from one-shot summary into cumulative reading support.
