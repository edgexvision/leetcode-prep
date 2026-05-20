import json
from pathlib import Path
from typing import Dict, List, Any

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "questions.json"


def load_questions() -> List[Dict[str, Any]]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_question_by_id(question_id: int) -> Dict[str, Any]:
    questions = load_questions()
    for q in questions:
        if q["id"] == question_id:
            return q
    raise ValueError(f"Question id {question_id} not found")


def popular_questions(limit: int = 10) -> List[Dict[str, Any]]:
    questions = load_questions()
    questions.sort(key=lambda q: (-q["frequency"], q["difficulty"]))
    return questions[:limit]


def recommended_by_weakness(weakness_tags: List[str], limit: int = 5) -> List[Dict[str, Any]]:
    questions = load_questions()
    matched = [q for q in questions if any(tag in q["tags"] for tag in weakness_tags)]
    matched.sort(key=lambda q: (-q["frequency"], q["difficulty"]))
    return matched[:limit]
