# Obsidian Plugin

## Goal

Give Obsidian the missing AI surface:

- a right-sidebar chat panel
- a context packet built from the active file and current paper memory
- local question memory writes
- local session memory writes

Plugin files live in:

- `obsidian-plugin/manifest.json`
- `obsidian-plugin/main.js`
- `obsidian-plugin/styles.css`

## What The Plugin Actually Does

Think of the plugin as “the right-side chat column” in Obsidian.

Typical reading layout:

- left pane: PDF
- center pane: `reading.md`
- right pane: `OB Paper Read Chat`

When the user asks a question in the plugin, it packages:

- current active file path
- current Markdown selection
- current paper card summary
- recent repeated questions for the same paper

It does not send the entire vault.

## Install Into A Vault

Copy the plugin folder to:

- `<vault>/.obsidian/plugins/ob-paper-read-chat/`

That folder should contain:

- `manifest.json`
- `main.js`
- `styles.css`

Then in Obsidian:

1. open `Settings`
2. go to `Community plugins`
3. enable community plugins if needed
4. enable `OB Paper Read Chat`

After that:

1. open the command palette
2. run `Open OB Paper Read Chat`
3. the chat panel will appear on the right side

## Two Modes

### Bridge mode

Use this when the user wants to keep using Codex / Claude Code / OpenClaw outside Obsidian.

Behavior:

- build a context packet
- copy it as JSON or a bridge prompt
- let the user paste it into the external agent

Bridge mode does not need a separate API key.

But the answer is still produced outside Obsidian:

- Codex quota in Codex
- Claude Code quota in Claude Code
- OpenClaw quota in OpenClaw

### API mode

Use this when the user wants to chat directly inside Obsidian.

Behavior:

- call an OpenAI-compatible `/chat/completions` endpoint
- include the context packet with the current paper context
- write question and session memory locally

API mode usually needs:

- an API base URL
- an API key
- a model name

If the user wants “direct chat in Obsidian but still magically consume Codex / Claude Code / OpenClaw app quotas”, that does not exist by default. It would require a dedicated local bridge or proxy layer.

## Recommended First Use

If the user only wants to get started quickly:

1. enable the plugin
2. open a PDF on the left
3. open `reading.md` in the center
4. open `OB Paper Read Chat` on the right
5. choose `API` mode if direct chat is the priority

Then ask questions like:

- `Figure 1 应该怎么读？`
- `这篇论文为什么敢去掉 RNN？`
- `这里的 baseline 到底是谁？`
- `把这一段翻成更好懂的话`

## What Gets Written To Memory

The plugin can persist:

- question memory under `questions/`
- session turns under `sessions/`
- lightweight paper metrics such as `qa_count` and `last_read_at`
