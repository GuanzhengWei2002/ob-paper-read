# Memory Schema

## Root Layout

Use a local workspace folder named `.ob-paper-read-memory/`.

Recommended structure:

```text
.ob-paper-read-memory/
|- user-profile.json
|- papers/
|- concepts/
|- questions/
|- sessions/
|- compare/
`- recommendations/
```

## user-profile.json

```json
{
  "user_id": "local-user",
  "domains_of_interest": [],
  "preferences": {
    "language": "zh-CN",
    "style": "intuition-first",
    "difficulty_default": "beginner",
    "depth_default": "standard"
  },
  "workspace": {
    "obsidian_vault_path": "",
    "raw_library_path": "",
    "guide_output_path": ""
  },
  "capabilities": {
    "pdf_upload_only": true
  },
  "recent_papers": [],
  "recent_sessions": []
}
```

Do not store API keys in this file.

## Paper Card

Store each paper as `papers/<paper_id>.json`.

```json
{
  "paper_id": "attention-is-all-you-need",
  "title": "Attention Is All You Need",
  "source": {
    "type": "pdf",
    "path": ""
  },
  "domain": "nlp",
  "topic": "transformer",
  "role": "landmark paper",
  "difficulty": "intermediate",
  "classification_reason": "",
  "classification_confidence": 0.0,
  "status": "reading_generated",
  "is_primary": true,
  "stage": "detailed_read",
  "reading_mode": "detailed",
  "reading_progress": {
    "overview": "done",
    "body": "in_progress",
    "reflection": "todo"
  },
  "summary_one_line": "",
  "why_it_matters": "",
  "core_problem": "",
  "core_method": "",
  "core_evidence": [],
  "prerequisites": [],
  "key_figures": [
    {
      "id": "transformer-architecture",
      "label": "Figure 1",
      "page": 3,
      "title": "",
      "caption": "",
      "teaching_point": "",
      "image_path": ""
    }
  ],
  "key_tables": [],
  "teaching_script": {
    "opening_hook": "",
    "author_context": "",
    "prerequisite_bridge": "",
    "title_walkthrough": "",
    "abstract_walkthrough": [],
    "conclusion_walkthrough": "",
    "introduction_walkthrough": "",
    "related_work_walkthrough": "",
    "method_overview": "",
    "method_walkthrough": "",
    "figure_walkthroughs": [],
    "experiment_walkthrough": [],
    "evidence_walkthrough": "",
    "limitation_walkthrough": "",
    "takeaways": [],
    "retell_script": "",
    "reflection_prompt": "",
    "mastery_questions": []
  },
  "teaching_adjustments": {
    "focus_more_on": [],
    "focus_less_on": [],
    "preferred_explanation_style": [],
    "figure_priority": [],
    "unresolved_concepts": [],
    "carry_into_next_generation": true,
    "notes": ""
  },
  "open_questions": [],
  "external_related_reads": [
    {
      "title": "",
      "relation": "",
      "why": "",
      "url": ""
    }
  ],
  "cited_papers": [],
  "question_refs": [],
  "session_refs": [],
  "local_related_papers": [],
  "reading_metrics": {
    "opened_count": 0,
    "active_reading_minutes": 0,
    "annotation_count": 0,
    "qa_count": 0,
    "summary_written": false,
    "last_read_at": ""
  },
  "mastery": {
    "problem": 0,
    "method": 0,
    "evidence": 0,
    "comparison": 0,
    "transfer": 0
  },
  "next_reads": {
    "predecessors": [],
    "successors": [],
    "parallel": []
  }
}
```

`teaching_script` is still the main lecture-note scaffold.

`teaching_adjustments` is a lighter user-memory layer that can bias later regeneration without replacing the core teaching pattern. Use it to record:

- which ideas need more space next time
- which background parts can be shortened
- whether the user prefers intuition-first, figure-first, or comparison-first explanation
- which unresolved concepts should be carried into the next `reading.md` generation

In other words:

- the general explanation pattern stays primary
- user memory only adjusts emphasis

## Question Memory

Store each reusable question as `questions/<question_id>.json`.

```json
{
  "question_id": "what-is-self-attention",
  "canonical_question": "What is self-attention?",
  "variants": [],
  "concept_tags": [],
  "papers": ["attention-is-all-you-need"],
  "sessions": [],
  "ask_count": 2,
  "status": "unresolved",
  "resolution_confidence": 0.2,
  "last_asked_at": "",
  "last_answer_note": "",
  "follow_up_prompt": "",
  "resolved_in_papers": [],
  "unresolved_in_papers": ["attention-is-all-you-need"]
}
```

Recommended `status` values:

- `open`
- `partially_resolved`
- `resolved`
- `reopened`

Use question memory to decide whether later `reading.md` regeneration should:

- reinforce the same concept
- add a simpler explanation path
- spend more space on a figure or comparison
- ask a follow-up question instead of repeating the same wording

## Session Summary

Store each reading session as `sessions/<timestamp>__<paper_id>.json`.

```json
{
  "session_id": "2026-04-07T20-30-00__attention-is-all-you-need",
  "paper_id": "attention-is-all-you-need",
  "started_at": "2026-04-07T20:30:00+08:00",
  "ended_at": "2026-04-07T21:02:00+08:00",
  "status": "open",
  "turns": [
    {
      "asked_at": "2026-04-07T20:31:00+08:00",
      "user": "Figure 1 该怎么读？",
      "assistant": "",
      "active_file": "papers/attention-is-all-you-need/reading.md",
      "selection": ""
    }
  ]
}
```

## Comparison Brief

Store generated comparison context in `compare/<base>__<target>.md`.

## Recommendation Cache

Store recommendation results as `recommendations/<paper_id>.json`.
