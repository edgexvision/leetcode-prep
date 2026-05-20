import json
from pathlib import Path
from typing import Any, Dict, List

CORE_PATTERNS = [
    "Hash Map",
    "Two Pointers",
    "Sliding Window",
    "Binary Search",
    "Stack",
    "Dynamic Programming 1D",
    "Dynamic Programming 2D",
    "Backtracking",
    "Graph DFS/BFS",
    "Intervals",
    "Heap",
    "Greedy / Kadane's",
]

_CONCEPTS_FILE = Path(__file__).resolve().parent.parent / "data" / "concepts.json"


def load_concepts() -> Dict[str, Any]:
    with open(_CONCEPTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_metrics(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not history:
        return {
            "readiness_score": 0,
            "pass_probability": 5,
            "pass_label": "Not ready",
            "pattern_coverage": {p: False for p in CORE_PATTERNS},
            "covered_count": 0,
            "total_patterns": len(CORE_PATTERNS),
            "difficulty_breakdown": {"Easy": 0, "Medium": 0, "Hard": 0},
            "total_submissions": 0,
            "avg_score": 0.0,
            "strengths": [],
            "weaknesses": [],
        }

    attempted_patterns = set(e.get("pattern", "") for e in history)
    pattern_coverage = {p: (p in attempted_patterns) for p in CORE_PATTERNS}
    covered_count = sum(1 for v in pattern_coverage.values() if v)

    # 40 pts: pattern coverage
    coverage_score = (covered_count / len(CORE_PATTERNS)) * 40

    # 30 pts: average code quality score
    avg_score = sum(e.get("score", 0) for e in history) / len(history)
    quality_score = (avg_score / 100) * 30

    # 20 pts: difficulty distribution (bonus for Medium and Hard)
    diff_count: Dict[str, int] = {"Easy": 0, "Medium": 0, "Hard": 0}
    for e in history:
        d = e.get("difficulty", "")
        if d in diff_count:
            diff_count[d] += 1
    total = len(history) or 1
    diff_score = min(20, (diff_count["Medium"] / total * 14) + (diff_count["Hard"] / total * 20))

    # 10 pts: volume (encourages consistent practice)
    volume_score = min(10, len(history) * 0.5)

    readiness_score = round(coverage_score + quality_score + diff_score + volume_score)
    readiness_score = min(100, readiness_score)

    if readiness_score >= 80:
        pass_prob, pass_label = 75, "Strong candidate"
    elif readiness_score >= 65:
        pass_prob, pass_label = 60, "Likely to pass"
    elif readiness_score >= 50:
        pass_prob, pass_label = 45, "Needs more practice"
    elif readiness_score >= 35:
        pass_prob, pass_label = 30, "High risk"
    else:
        pass_prob, pass_label = 10, "Not ready"

    # Strengths / weaknesses by pattern
    pattern_stats: Dict[str, Dict[str, Any]] = {}
    for e in history:
        p = e.get("pattern", "Unknown")
        stats = pattern_stats.setdefault(p, {"attempts": 0, "score_sum": 0, "fails": 0})
        stats["attempts"] += 1
        stats["score_sum"] += e.get("score", 0)
        if e.get("failed_cases", 0) > 0 or e.get("score", 100) < 80:
            stats["fails"] += 1

    for stats in pattern_stats.values():
        stats["avg_score"] = round(stats["score_sum"] / stats["attempts"], 1)
        stats["fail_rate"] = round(stats["fails"] / stats["attempts"], 2)

    strengths = [p for p, s in pattern_stats.items() if s["avg_score"] >= 85 and s["attempts"] >= 2]
    weaknesses = [p for p, s in sorted(pattern_stats.items(), key=lambda x: x[1]["fail_rate"], reverse=True) if s["fail_rate"] > 0]

    return {
        "readiness_score": readiness_score,
        "pass_probability": pass_prob,
        "pass_label": pass_label,
        "pattern_coverage": pattern_coverage,
        "covered_count": covered_count,
        "total_patterns": len(CORE_PATTERNS),
        "difficulty_breakdown": diff_count,
        "total_submissions": len(history),
        "avg_score": round(avg_score, 1),
        "strengths": strengths,
        "weaknesses": weaknesses[:5],
        "pattern_stats": pattern_stats,
    }
