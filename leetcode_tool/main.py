import argparse
from pathlib import Path
from typing import Any, Dict, List

from leetcode_tool.app import create_app
from leetcode_tool.question_bank import popular_questions, get_question_by_id, recommended_by_weakness
from leetcode_tool.runner import execute_submission, SubmissionError
from leetcode_tool.critic import analyze_code
from leetcode_tool.history import add_history_entry, load_history, summarize_history, recommended_next_questions


def print_question(q: Dict[str, Any]) -> None:
    print(f"[{q['id']}] {q['title']} ({q['difficulty']}) - frequency {q['frequency']}")
    print(q["description"])
    print("Function signature:", q["signature"])
    print("Tags:", ", ".join(q["tags"]))
    print("Examples:")
    for example in q["examples"]:
        print("  input=", example["input"], "expected=", example["output"])


def list_questions(args: argparse.Namespace) -> None:
    questions = popular_questions(limit=args.limit)
    for q in questions:
        print_question(q)
        print("-")


def view_question(args: argparse.Namespace) -> None:
    q = get_question_by_id(args.id)
    print_question(q)


def submit_solution(args: argparse.Namespace) -> None:
    q = get_question_by_id(args.id)
    if not Path(args.file).exists():
        print(f"Solution file not found: {args.file}")
        return

    code = Path(args.file).read_text(encoding="utf-8")
    try:
        result = execute_submission(code, q["function_name"], q["test_cases"])
    except SubmissionError as exc:
        print("Submission error:", exc)
        return

    print(f"Passed {result.passed}/{result.total} test cases in {result.runtime_ms:.2f} ms")
    if result.failed_cases:
        print("Failed cases:")
        for case in result.failed_cases:
            print(case)
    feedback = analyze_code(code)
    print("\nCritique:")
    print(f"Score: {feedback['score']}")
    if feedback["style"]:
        print("Style:")
        for item in feedback["style"]:
            print("  -", item)
    if feedback["efficiency"]:
        print("Efficiency:")
        for item in feedback["efficiency"]:
            print("  -", item)
    if feedback["readability"]:
        print("Readability:")
        for item in feedback["readability"]:
            print("  -", item)

    add_history_entry({
        "question_id": q["id"],
        "title": q["title"],
        "passed": result.passed,
        "total": result.total,
        "score": feedback["score"],
        "tags": q["tags"],
        "pattern": q.get("pattern", ""),
        "difficulty": q.get("difficulty", ""),
        "failed_cases": len(result.failed_cases),
        "feedback": feedback,
    })


def show_weaknesses(_: argparse.Namespace) -> None:
    history = load_history()
    if not history:
        print("No submission history found. Submit at least one solution first.")
        return

    tag_failures = {}
    for entry in history:
        if entry["failed_cases"] > 0 or entry["score"] < 90:
            for tag in entry["tags"]:
                tag_failures[tag] = tag_failures.get(tag, 0) + 1

    if not tag_failures:
        print("Your recent submissions look strong. Keep practicing the same categories.")
        return

    sorted_tags = sorted(tag_failures.items(), key=lambda pair: -pair[1])
    print("Weakness areas based on history:")
    for tag, count in sorted_tags:
        print(f"  - {tag}: {count} flagged submissions")

    recommended = recommended_by_weakness([tag for tag, _ in sorted_tags])
    if recommended:
        print("\nRecommended next questions:")
        for q in recommended:
            print(f"  - [{q['id']}] {q['title']} ({q['difficulty']})")


def main() -> None:
    parser = argparse.ArgumentParser(description="LeetCodePrep practice tool")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List popular questions")
    list_parser.add_argument("--limit", type=int, default=10)
    list_parser.set_defaults(func=list_questions)

    view_parser = subparsers.add_parser("view", help="View a question prompt")
    view_parser.add_argument("--id", type=int, required=True)
    view_parser.set_defaults(func=view_question)

    submit_parser = subparsers.add_parser("submit", help="Submit a Python solution file")
    submit_parser.add_argument("--id", type=int, required=True)
    submit_parser.add_argument("--file", type=str, required=True)
    submit_parser.set_defaults(func=submit_solution)

    weakness_parser = subparsers.add_parser("weakness", help="Show weakness recommendation")
    weakness_parser.set_defaults(func=show_weaknesses)

    serve_parser = subparsers.add_parser("serve", help="Run the web UI")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=5000)
    serve_parser.set_defaults(func=lambda args: create_app().run(host=args.host, port=args.port, debug=True))

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
