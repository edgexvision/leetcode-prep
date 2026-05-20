# LeetCodePrep

A self-hosted Python practice tool that runs entirely on your laptop. Built to actually help you crack the coding round — not just collect green checkmarks.

## What it does

- **77+ questions covering the Blind 75** with tiered hints, key insight reveals, and pattern explanations — question bank grows over time
- **Browser-based Python editor** (CodeMirror, Dracula theme) with autocomplete and real test execution
- **Smart code review** — detects your actual algorithm (hash map, two pointers, BFS, DP, etc.), estimates your time complexity, and flags pattern mismatches against the intended approach
- **Spaced repetition** — resurfaces questions on a 1 → 3 → 7 → 14 → 30 day schedule based on how well you solved them
- **Time tracking** — live stopwatch per question, progress chart showing improvement across attempts
- **Interview readiness score** — 0–100 score based on pattern coverage, code quality, difficulty mix, and volume
- **Company filter** — filter questions by company (Amazon, Google, Meta, etc.)
- **Solved / attempted / unsolved** tracking with status filters

## Setup

```bash
pip install -r requirements.txt
python3 -m leetcode_tool.main serve
```

Open `http://127.0.0.1:5000`

## Project structure

```
data/
  questions.json     # 77 Blind 75 questions with test cases, hints, patterns
  concepts.json      # Pattern explanations, templates, watch-outs
leetcode_tool/
  app.py             # Flask routes
  runner.py          # Sandboxed Python execution engine
  critic.py          # AST-based code analyser (approach detection, complexity)
  history.py         # Submission history + spaced repetition logic
  metrics.py         # Readiness score computation
  question_bank.py   # Question loading and recommendation
```

## Stack

Python 3.10+, Flask, CodeMirror 5 — no database, no external API, runs fully offline.

## Disclaimer

Built with vibe coding (AI-assisted). There may be bugs or mistakes as a result. Provided as-is for personal learning — no guarantees of correctness or completeness. The author is not legally responsible for any issues arising from use of this tool.
