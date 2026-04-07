# Global Reading Layer

## Goal

Add a lightweight global layer on top of single-paper reading without replacing it.

Keep this distinction clear:

- `papers/<paper-id>/reading.md` is still the main reading artifact
- global pages are optional compact cross-paper notes

The global layer should stay very small, cheap to maintain, and useful after just a few papers.

## Minimal Scope

For now, keep only:

- `concepts/`
- `overviews/index.md`

`log.md` can still exist, but treat it as an implementation detail rather than part of the daily workflow.

Do not actively maintain methods, people, or topics unless the project clearly outgrows this simpler shape.

## Concepts

Use `concepts/` for stable concepts that recur across papers.

Each concept page should explain:

- what it is
- why it matters
- common confusion points
- which local papers use it

## Overviews

Use `overviews/` for navigation.

Create:

- `overviews/index.md`

`index.md` is a compact directory that lists:

- papers
- concepts

## Update Strategy

Default order:

1. finish or meaningfully advance one paper reading
2. optionally update a small number of concept pages
3. refresh `index.md`

Do not try to convert every noun into a global page.

Prefer creating a page only when the item is:

- stable
- reusable
- likely to appear again

## Script

Use `scripts/update_global_pages.py` to maintain the lightweight global layer.

It can:

- create missing concept pages
- update `overviews/index.md`

Automatic defaults:

- concepts from `prerequisites` and unresolved concept memory

Manual additions:

- `--concept`

## Practical Rule

Single-paper reading always has priority.

If the global layer starts slowing down the actual reading workflow, shrink it again.
