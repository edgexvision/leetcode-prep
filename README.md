# LeetCodePrep

A self-hosted Python practice tool that runs entirely on your laptop. Built to actually help you crack the coding round — not just collect green checkmarks.

> **Built with vibe coding (AI-assisted).** There may be bugs or inaccuracies. See the [Disclaimer](#disclaimer) section.

---

## Features

- **77+ questions covering the Blind 75** — question bank grows over time
- **Browser-based Python editor** with syntax highlighting, autocomplete, and real test execution
- **Smart code review** — detects your algorithm, estimates complexity, flags pattern mismatches
- **Spaced repetition** — resurfaces questions on a schedule based on how well you solved them
- **Time tracking** — live stopwatch per session, progress chart across attempts
- **Interview readiness score** — 0–100 score explained below
- **Company filter** — filter by Amazon, Google, Meta, etc.
- **Solved / attempted / unsolved** tracking with status filters

---

## How each feature works

### Frequency score

Each question has a `frequency` field (range 75–98) in `data/questions.json`. These are **manually assigned estimates** inspired by community-reported interview frequency data from sources like Blind, Glassdoor, and NeetCode's public commentary. They are not scraped from LeetCode or any proprietary source — treat them as a rough relative signal (higher = more commonly reported), not a precise statistic.

### Interview readiness score (0–100)

Computed in `leetcode_tool/metrics.py` from your submission history across four dimensions:

| Component | Weight | How it's calculated |
|---|---|---|
| Pattern coverage | 40 pts | How many of the 12 core patterns you've attempted at least once |
| Code quality | 30 pts | Average critic score across all submissions |
| Difficulty mix | 20 pts | Weighted by Medium (×14%) and Hard (×20%) submissions |
| Volume | 10 pts | 0.5 pts per submission, capped at 10 |

**Pass probability** is a tiered label derived from the readiness score:

| Score | Label | Estimated pass probability |
|---|---|---|
| 80–100 | Strong candidate | ~75% |
| 65–79 | Likely to pass | ~60% |
| 50–64 | Needs more practice | ~45% |
| 35–49 | High risk | ~30% |
| 0–34 | Not ready | ~10% |

These probabilities are illustrative estimates, not statistically validated.

### Code review / critic score

After every submission, `leetcode_tool/critic.py` analyses your code using Python's AST (abstract syntax tree) — no AI, no external calls. It checks:

- **Approach detection** — scans for data structures and patterns (dict/Counter → Hash Map, deque+popleft → BFS, mid+lo+hi variables → Binary Search, etc.)
- **Complexity estimation** — counts maximum loop nesting depth to estimate O(n), O(n²), O(n log n), etc.
- **Pattern mismatch** — if you solved a "Hash Map" problem with nested loops, it flags it and tells you the intended approach
- **Complexity mismatch** — if your estimated complexity is worse than the known optimal, it calls it out with a specific hint
- **Style checks** — single-letter variable names (except i/j/k/x/y/z/n/m), mutable default arguments, deeply nested conditionals

The critic score starts at 100 and deducts points per finding: 5 per efficiency issue, 4 per risk, 3 per style issue, 2 per readability issue, 10 for a pattern mismatch.

### Spaced repetition

Intervals are stored in `leetcode_tool/history.py` and computed per submission:

| Outcome | Next review |
|---|---|
| Failed | 1 day |
| Passed (1st time) | 3 days |
| Passed (2nd time) | 7 days |
| Passed (3rd time) | 14 days |
| Passed (4th+ time) | 30 days |
| Passed but slow (>25 min) or low score (<70) | interval halved |

Progress is stored locally at `~/.leetcodeprep/history.json` — isolated per OS user, never pushed to the repo.

### Company tags

Company names are assigned manually to each question based on widely shared community interview reports (Blind, Glassdoor, etc.). They are descriptive signals only — not sourced from LeetCode or any company directly.

---

## Setup

```bash
pip install -r requirements.txt
python3 -m leetcode_tool.main serve
```

Open `http://127.0.0.1:5000`

---

## Project structure

```
data/
  questions.json     # Question bank: descriptions, test cases, hints, patterns, frequency
  concepts.json      # Pattern explanations, code templates, common pitfalls
leetcode_tool/
  app.py             # Flask routes
  runner.py          # Sandboxed Python execution engine (ListNode/TreeNode support)
  critic.py          # AST-based code analyser: approach detection, complexity estimation
  history.py         # Submission history + spaced repetition scheduling
  metrics.py         # Readiness score computation
  question_bank.py   # Question loading, filtering, recommendations
```

---

## Stack

Python 3.10+, Flask, CodeMirror 5 — no database, no external API, runs fully offline.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Disclaimer

**Not affiliated with LeetCode, NeetCode, Blind, or any company mentioned in the question data.** Company names are referenced descriptively based on publicly available community reports only.

Question descriptions are original summaries of well-known algorithmic problems — not reproduced from any proprietary source.

Built with vibe coding (AI-assisted) — there may be bugs or inaccuracies. Provided as-is for personal learning with no guarantees of correctness or completeness. The author accepts no legal responsibility for any outcomes arising from use of this tool. See [NOTICE](NOTICE) for full details.
