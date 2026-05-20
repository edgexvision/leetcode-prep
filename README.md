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

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

**Not affiliated with LeetCode, NeetCode, Blind, or any company mentioned in the question data.** Company names are referenced descriptively based on publicly available community reports only.

Question descriptions are original summaries of well-known algorithmic problems — not reproduced from any proprietary source.

Built with vibe coding (AI-assisted) — there may be bugs or inaccuracies. Provided as-is for personal learning with no guarantees of correctness or completeness. The author accepts no legal responsibility for any outcomes arising from use of this tool. See [NOTICE](NOTICE) for full details.
