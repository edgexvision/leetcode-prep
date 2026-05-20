# I built a self-hosted LeetCode practice tool that actually teaches you — here's how

I was grinding LeetCode for months but felt like I was going in circles. I'd solve a problem, move on, and forget it completely by the time it came up in an interview. The feedback loop was broken: LeetCode tells you pass/fail, not *why* your solution is suboptimal or which pattern you should have used.

So I built my own tool.

## What I built

A local Flask web app — 77+ questions covering the Blind 75, a CodeMirror editor, and a real Python execution engine. No subscriptions, no ads, runs fully offline on your laptop. The question bank grows over time.

Here's what makes it different from just doing LeetCode.

---

### It reviews your *approach*, not just your output

After every submission, an AST-based analyser inspects your code and tells you:

- **What algorithm you actually used** — "Approach detected: Nested loops / Sorting"
- **Your estimated time complexity** — derived from loop nesting depth
- **Whether you used the wrong pattern** — "This is a Hash Map problem but your code doesn't show that pattern. The intended approach is O(n) with a hash map."

Knowing you passed the tests is not the same as knowing you solved it well.

---

### Spaced repetition built in

The single biggest gap between "I can understand this solution" and "I can reproduce it in an interview" is *retention*.

Every submission computes a next-review date:
- Failed → review tomorrow
- Passed (first time) → 3 days
- Passed repeatedly → 7 → 14 → 30 days
- Slow or messy code → interval halved

The home page shows a **Due for Review** queue. You open those questions cold, no hints, and try to reproduce your solution from scratch. That's exactly what an interview tests.

---

### Time tracking shows you getting faster

A live stopwatch runs while you code. Every submission stores the elapsed time. After a few attempts, a small bar chart shows your improvement: 45 min → 28 min → 14 min. That trend is more motivating than any streak counter.

---

### The hints are tiered and the insights are hidden

Each question has three hints, revealed one at a time — you only look at the next one if you're genuinely stuck. The key insight (the core "aha" for the problem) is hidden behind a separate toggle so you're forced to think first.

---

### Interview readiness score

A 0–100 score tracks: pattern coverage (have you touched every major pattern?), code quality, difficulty mix (you should be doing 60% Medium), and total volume. It's not a vanity metric — it's calibrated so that hitting 80+ means you've done the work.

---

## The stack

Python 3.10+, Flask, CodeMirror 5. No database — just a JSON file for history. Runs fully offline.

## Get it

[github.com/edgexvision/leetcode-prep](https://github.com/edgexvision/leetcode-prep)

```bash
pip install flask
python3 -m leetcode_tool.main serve
```

Open `http://localhost:5000` and start practicing.

---

## A note on how this was built

This tool was built using **vibe coding** — I described what I wanted and iterated with AI (Claude) to build it. It was a fun way to ship something useful fast, but it means there may be bugs, edge cases, or suboptimal code I haven't caught. Use it as a learning aid, not a source of truth.

**Disclaimer:** This project is provided as-is for personal learning purposes. I make no guarantees about correctness, completeness, or fitness for any particular use. I am not legally responsible for any issues arising from using this tool. The question content is inspired by publicly known interview problems — always refer to official sources for authoritative problem statements.

---

Would love feedback. If you use it and find something broken or have ideas, open an issue.
