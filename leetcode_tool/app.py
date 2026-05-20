import json
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, render_template, request, redirect, url_for

from leetcode_tool.question_bank import get_question_by_id, popular_questions, recommended_by_weakness
from leetcode_tool.runner import execute_submission, SubmissionError
from leetcode_tool.critic import analyze_code
from leetcode_tool.history import load_history, add_history_entry, summarize_history, recommended_next_questions, due_for_review, question_time_history
from leetcode_tool.metrics import compute_metrics, load_concepts


def create_app() -> Flask:
    template_path = str(Path(__file__).resolve().parent / "templates")
    static_path = str(Path(__file__).resolve().parent / "static")
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)
    app.secret_key = "leetcode-prep-secret"

    def _question_status(history: list) -> dict:
        solved, attempted = set(), set()
        for e in history:
            qid = e.get("question_id")
            if qid is None:
                continue
            if e.get("passed", 0) == e.get("total", -1) and e.get("total", 0) > 0:
                solved.add(qid)
            else:
                attempted.add(qid)
        # a question that was eventually solved should not appear as "attempted"
        attempted -= solved
        return {"solved": solved, "attempted": attempted}

    @app.route("/")
    def index() -> str:
        questions = popular_questions(limit=100)
        history = load_history()
        summary = summarize_history(history)
        metrics = compute_metrics(history)
        recommended = recommended_next_questions(history, limit=5)
        status = _question_status(history)
        from collections import Counter
        company_counts = Counter(c for q in questions for c in q.get("companies", []))
        companies = [c for c, _ in company_counts.most_common()]
        due_ids = set(due_for_review(history))
        due_questions = [q for q in questions if q["id"] in due_ids]
        return render_template("index.html", questions=questions, summary=summary, metrics=metrics, recommended=recommended, status=status, companies=companies, due_questions=due_questions)

    @app.route("/question/<int:question_id>")
    def question_view(question_id: int) -> str:
        question = get_question_by_id(question_id)
        history = load_history()
        summary = summarize_history(history)
        metrics = compute_metrics(history)
        recommended = recommended_next_questions(history, limit=5)
        concepts = load_concepts()
        pattern_info = concepts.get(question.get("pattern", ""), None)
        starter_code = f"{question['signature']}\n    pass\n"
        time_hist = question_time_history(history, question_id)
        return render_template(
            "question.html",
            question=question,
            starter_code=starter_code,
            result=None,
            feedback=None,
            summary=summary,
            metrics=metrics,
            recommended=recommended,
            pattern_info=pattern_info,
            time_hist=time_hist,
        )

    @app.route("/submit", methods=["POST"])
    def submit() -> str:
        question_id = int(request.form.get("question_id", "0"))
        code = request.form.get("code", "")
        time_seconds = request.form.get("time_seconds")
        time_seconds = int(time_seconds) if time_seconds and time_seconds.isdigit() else None
        question = get_question_by_id(question_id)
        try:
            result = execute_submission(code, question["function_name"], question["test_cases"])
        except SubmissionError as exc:
            result = None
            feedback = {"style": [], "efficiency": [], "readability": [], "risk": [], "score": 0, "error": str(exc)}
        else:
            feedback = analyze_code(code, question=question)
            add_history_entry({
                "question_id": question["id"],
                "title": question["title"],
                "passed": result.passed,
                "total": result.total,
                "score": feedback["score"],
                "tags": question["tags"],
                "pattern": question.get("pattern", ""),
                "difficulty": question.get("difficulty", ""),
                "failed_cases": len(result.failed_cases),
                "feedback": feedback,
                "time_seconds": time_seconds,
            })

        history = load_history()
        summary = summarize_history(history)
        metrics = compute_metrics(history)
        recommended = recommended_next_questions(history, limit=5)
        concepts = load_concepts()
        pattern_info = concepts.get(question.get("pattern", ""), None)
        time_hist = question_time_history(history, question_id)
        return render_template(
            "question.html",
            question=question,
            starter_code=code,
            result=result,
            feedback=feedback,
            summary=summary,
            metrics=metrics,
            recommended=recommended,
            pattern_info=pattern_info,
            time_hist=time_hist,
        )

    @app.route("/concepts")
    def concepts_page() -> str:
        concepts = load_concepts()
        history = load_history()
        metrics = compute_metrics(history)
        return render_template("concepts.html", concepts=concepts, metrics=metrics)

    @app.route("/concepts/<pattern_name>")
    def concept_detail(pattern_name: str) -> str:
        concepts = load_concepts()
        info = concepts.get(pattern_name)
        history = load_history()
        metrics = compute_metrics(history)
        return render_template("concept_detail.html", pattern_name=pattern_name, info=info, metrics=metrics)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)
