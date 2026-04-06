# Session Flow

## Goal

Run reading as a guided sequence:

1. intake
2. detailed reading
3. mastery-check and close
4. linking and comparison

## Intake

### Single paper

Produce:

- one-line paper position
- likely audience
- likely difficulty
- prerequisite concepts
- domain
- topic
- role

Create or update the paper card immediately.

### Multiple papers

Treat the upload as a candidate pool.

For each paper, produce:

- title
- one-line role
- rough difficulty
- relationship to the others

Then ask the user to choose one primary paper.

Do not start simultaneous reading unless the user explicitly insists. If the user insists, recommend reading one paper first and promise comparison support once memory exists.

### Storage Rules

- In normal use, the user uploads PDF files directly in the host chat dialog.
- The skill should save those uploaded files into the configured local library path.
- Save raw sources to the configured library path.
- Keep raw PDFs immutable.
- Record source path and source type in the paper card.
- V1 supports PDF uploads only.

## Detailed Reading

Start by quickly clarifying:

1. title
2. abstract
3. conclusion

Then continue into the body:

4. introduction
5. related work or baseline
6. method
7. key figure
8. key table or experiment
9. discussion or limitation if present

Produce a reading map with:

- paper position
- core problem
- core method
- claimed result
- why it matters
- prerequisite gap list
- what to watch during the body read

For each section, answer:

- What is this section doing?
- Why does the user need it?
- What is the one thing to retain?

During detailed reading:

- mark open questions instead of stalling on every confusion
- identify important cited papers
- identify strong local comparison candidates

Three-pass reading can still be used internally as a thinking aid, but it should not be the default user-facing output structure.

## Deepening And Reflection

Only deepen further when the user wants a fuller read or the paper is important enough to justify it.

Focus on:

- resolving marked confusions
- understanding key details
- reconstructing the paper from the author's point of view
- testing whether the user can restate the paper in their own words

## Interruption Policy

Classify interruptions into one of these groups:

- prerequisite
- terminology
- implementation
- intuition
- current-practice
- off-track compare

After answering, re-anchor the session with a sentence that names the exact return point.

Examples:

- "We were at the abstract's method sentence."
- "We were at Figure 1."
- "We were in the experiment section, comparing against the baseline."

Store reusable interruptions in question memory when they are likely to recur.

## Mastery Check

Use 3-5 questions.

Recommended set:

1. What problem does this paper solve?
2. What is the paper's main method?
3. What evidence supports the claim?
4. What does it improve over previous work?
5. Where would you use or question it?

Interpretation:

- Questions 1-3 answered well: core grasp
- Questions 1-5 answered well: strong working grasp

## Reading Status

Use status values such as:

- `saved`
- `classified`
- `reading_generated`
- `selected_as_primary`
- `reading_in_progress`
- `mastery_checked`
- `read_completed`
- `compared`

Update status from behavior, not file existence.

## Linking

Recommend:

- predecessor papers
- successor papers
- parallel papers

Use this recommendation order:

1. local unread papers
2. local previously read comparison anchors
3. no strong local match yet

If there is no good local follow-up, explicitly say what is missing from the current library.

## Comparison Reading

Only compare after the first paper is stored in memory.

Load:

- first paper card
- first paper summary
- concept cards touched by the first paper
- unresolved question memory that should carry into the second paper

Then compare the second paper on:

- problem framing
- method
- evidence
- strengths
- limitations
- recommended reading order

## Session Boundary

On session start, load:

- user profile
- current paper card
- recent session for the same paper if one exists
- related question memory

On session close, write:

- covered sections
- user questions
- mastery results
- time spent
- next action
- files updated
