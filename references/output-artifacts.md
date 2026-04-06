# Output Artifacts

## Goal

Produce concrete local files that feel ready to read inside Obsidian, not like temporary AI scratch output.

V1 should create:

- raw PDF in the local library path
- one main Markdown deliverable: `reading.md`
- rendered figure assets under `assets/`
- session and question records in memory

Language default:

- Chinese first
- preserve standard technical terms such as `Transformer`, `self-attention`, `baseline`, and `encoder-decoder`
- when helpful, use `English term（中文解释）`

## Suggested Local Layout

```text
workspace-root/
|- raw-papers/
|- papers/
|  `- <paper-id>/
|     |- reading.md
|     |- assets/
|     `- compare/
`- .ob-paper-read-memory/
```

Keep the PDF immutable. Edit only Markdown and derived assets.

## reading.md

`reading.md` is the main user-facing file.

It should feel like:

- a lecture note
- a guided reading handout
- a teacher walking section by section through the paper

It should not feel like:

- a short summary
- a list of buzzwords
- a generic “AI summarized this paper” shell

Output rules:

- do not mention hidden reference teachers, ASR transcripts, or internal inspiration sources
- write as if the assistant itself is guiding the user through the paper
- prefer generous detail over short recap
- when a figure matters, spend real space teaching the figure
- keep the paper’s own argumentative order visible: problem, old route, new route, evidence, limits

Recommended structure:

```md
# <title>

## 开场导读（Opening Guide）
## 读前准备（Before We Read）
### 标题怎么读（How To Read The Title）
### 摘要逐句拆解（Abstract Walkthrough）
### 先看结论（Conclusion First）
## 作者与时代背景（Authors And Context）
## 正文带读（Guided Reading）
### 引言：作者是怎么把问题立起来的（Introduction）
### 相关工作 / 基线：旧路线到底卡在哪里（Related Work / Baseline）
### 方法总览：先抓主干，再看细节（Method Overview）
### 方法细讲（Method Walkthrough）
## 关键图表精讲（Key Figures）
## 实验与证据（Experiments And Evidence）
## 关键表格（Key Tables）
## 局限与边界（Limitations）
## 读完你应该带走什么（What To Retain）
## 30 秒复述模板（Short Retell）
## 你的问题（Open Questions）
## 我的笔记（My Notes）
## 掌握度检查（Mastery Check）
## 本地延伸阅读（Local Follow-Up Reads）
## arXiv 延伸阅读（Related arXiv Reads）
```

## What “Lecture-Style” Means

The file should repeatedly answer:

- this section is doing what
- this section matters because what
- what the reader should retain here

The file should actively reduce confusion by:

- introducing just enough prerequisite context
- naming the old route before explaining the new one
- translating notation or module names into intuition
- reminding the reader where they are in the argument

If user memory exists, it should only adjust emphasis:

- add more space to repeated weak spots
- reinforce unresolved concepts
- prioritize figures the user keeps asking about

It should not replace the shared lecture-note scaffold.

## Figure Assets

Each key figure or table should be rendered into `papers/<paper-id>/assets/` and embedded into `reading.md`.

Recommended card structure:

```json
{
  "key_figures": [
    {
      "id": "transformer-architecture",
      "label": "Figure 1",
      "page": 3,
      "title": "The Transformer - model architecture",
      "caption": "",
      "teaching_point": "",
      "image_path": "./assets/figure-p03-figure-1.png"
    }
  ]
}
```

The image alone is not enough. Each figure section should explain:

- what the figure is showing
- why the figure matters
- what the reader should notice first
- what confusion the figure is supposed to remove

## Related arXiv Reads

When local follow-up papers are missing or too sparse, add a small `arXiv 延伸阅读` section with:

- predecessor papers
- comparison baselines
- important successors
- one sentence on why each link matters
