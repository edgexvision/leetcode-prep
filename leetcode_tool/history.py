import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from leetcode_tool.question_bank import recommended_by_weakness

HISTORY_FILE = Path.home() / ".leetcodeprep" / "history.json"
HISTORY_FILE.parent.mkdir(exist_ok=True)

# Spaced repetition intervals (days) indexed by consecutive successful solves
_SR_INTERVALS = [1, 3, 7, 14, 30]


def load_history() -> List[Dict[str, Any]]:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history: List[Dict[str, Any]]) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def _compute_next_review(passed: int, total: int, score: int, time_seconds: Optional[int],
                         consecutive_successes: int) -> str:
    """Return ISO date string for when this question should next be reviewed."""
    solved = passed == total and total > 0
    if not solved:
        days = 1
    else:
        # Bump interval based on consecutive successes, capped by score/time quality
        idx = min(consecutive_successes, len(_SR_INTERVALS) - 1)
        days = _SR_INTERVALS[idx]
        # Penalise if solution was slow (> 25 min) or low quality
        if time_seconds and time_seconds > 1500:
            days = max(1, days // 2)
        if score < 70:
            days = max(1, days // 2)
    return (date.today() + timedelta(days=days)).isoformat()


def add_history_entry(entry: Dict[str, Any]) -> None:
    history = load_history()

    # Count consecutive successes for this question to compute SR interval
    qid = entry.get("question_id")
    consecutive = 0
    for e in reversed(history):
        if e.get("question_id") != qid:
            continue
        if e.get("passed", 0) == e.get("total", -1) and e.get("total", 0) > 0:
            consecutive += 1
        else:
            break

    entry["next_review"] = _compute_next_review(
        passed=entry.get("passed", 0),
        total=entry.get("total", 0),
        score=entry.get("score", 0),
        time_seconds=entry.get("time_seconds"),
        consecutive_successes=consecutive,
    )
    entry["submitted_on"] = date.today().isoformat()
    history.append(entry)
    save_history(history)


def due_for_review(history: List[Dict[str, Any]]) -> List[int]:
    """Return question IDs whose next_review date is today or in the past."""
    today = date.today().isoformat()
    latest: Dict[int, Dict[str, Any]] = {}
    for e in history:
        qid = e.get("question_id")
        if qid is not None:
            latest[qid] = e  # last entry wins
    return [
        qid for qid, e in latest.items()
        if e.get("next_review", "9999-12-31") <= today
    ]


def question_time_history(history: List[Dict[str, Any]], question_id: int) -> List[Dict[str, Any]]:
    """Return all timed submissions for a question, oldest first."""
    return [
        {"time_seconds": e["time_seconds"], "passed": e.get("passed", 0),
         "total": e.get("total", 0), "submitted_on": e.get("submitted_on", "")}
        for e in history
        if e.get("question_id") == question_id and e.get("time_seconds") is not None
    ]


def summarize_history(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not history:
        return {"total_submissions": 0, "average_score": 0.0, "top_tags": [], "tag_stats": {}}

    total_score = 0
    tag_stats: Dict[str, Dict[str, Any]] = {}
    for entry in history:
        total_score += entry.get("score", 0)
        for tag in entry.get("tags", []):
            stats = tag_stats.setdefault(tag, {"attempts": 0, "flags": 0, "score_sum": 0})
            stats["attempts"] += 1
            stats["score_sum"] += entry.get("score", 0)
            if entry.get("failed_cases", 0) > 0 or entry.get("score", 100) < 90:
                stats["flags"] += 1

    for stats in tag_stats.values():
        stats["average_score"] = round(stats["score_sum"] / stats["attempts"], 1)
        stats["severity"] = round(stats["flags"] / stats["attempts"], 2)

    sorted_tags = sorted(tag_stats.items(), key=lambda item: (-item[1]["severity"], -item[1]["attempts"]))
    return {
        "total_submissions": len(history),
        "average_score": round(total_score / len(history), 1),
        "top_tags": [tag for tag, _ in sorted_tags],
        "tag_stats": {tag: stats for tag, stats in sorted_tags},
    }


def recommended_next_questions(history: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    tags = [tag for tag, stats in summarize_history(history)["tag_stats"].items() if stats["severity"] > 0]
    if not tags:
        return []
    return recommended_by_weakness(tags, limit=limit)
