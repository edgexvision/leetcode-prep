import ast
from typing import Dict, List, Any, Optional


# ── Approach detection helpers ────────────────────────────────────────────────

def _detect_approach(tree: ast.AST, code: str) -> List[str]:
    """Return a list of algorithmic approaches detected in the code."""
    approaches = []
    code_lower = code.lower()

    imports = set()
    used_names = set()
    attr_calls = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split('.')[0])
        if isinstance(node, ast.Name):
            used_names.add(node.id)
        if isinstance(node, ast.Attribute):
            attr_calls.add(node.attr)

    # Hash map
    if any(n in used_names for n in ('Counter', 'defaultdict', 'OrderedDict')) or \
       'collections' in imports or \
       any(isinstance(n, ast.Dict) for n in ast.walk(tree)):
        approaches.append("Hash Map / Counting")

    # Stack
    if 'stack' in code_lower or \
       ('append' in attr_calls and 'pop' in attr_calls and 'stack' in code_lower):
        approaches.append("Stack")

    # Heap / priority queue
    if 'heapq' in imports or 'heapq' in used_names or \
       any(a in attr_calls for a in ('heappush', 'heappop', 'heapify')):
        approaches.append("Heap / Priority Queue")

    # BFS (deque + while loop with popleft)
    if ('deque' in used_names or 'deque' in imports or 'collections' in imports) and \
       'popleft' in attr_calls:
        approaches.append("BFS (Queue)")

    # Two pointers
    ptr_names = {'left', 'right', 'lo', 'hi', 'l', 'r', 'start', 'end', 'low', 'high'}
    func_args = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                func_args.add(arg.arg)
    local_vars = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            local_vars.add(node.id)
    if len(ptr_names & (local_vars - func_args)) >= 2:
        approaches.append("Two Pointers")

    # Sliding window
    if ('window' in code_lower or 'sliding' in code_lower) or \
       (len(ptr_names & local_vars) >= 2 and _has_window_pattern(tree)):
        approaches.append("Sliding Window")

    # Binary search
    if 'bisect' in imports or 'bisect' in used_names or \
       ('mid' in local_vars and ('left' in local_vars or 'lo' in local_vars) and
        ('right' in local_vars or 'hi' in local_vars)):
        approaches.append("Binary Search")

    # DP — 1D
    if _has_dp_array(tree, dims=1):
        approaches.append("Dynamic Programming (1D)")

    # DP — 2D
    if _has_dp_array(tree, dims=2):
        approaches.append("Dynamic Programming (2D)")

    # Backtracking
    func_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    is_recursive = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in func_names
        for n in ast.walk(tree)
    )
    if is_recursive:
        if any(w in code_lower for w in ('backtrack', 'path', 'result', 'res')):
            approaches.append("Backtracking (Recursion)")
        else:
            approaches.append("Recursion / DFS")

    # Union-Find
    if any(n in code_lower for n in ('parent', 'union', 'find', 'rank')):
        approaches.append("Union-Find")

    # Sorting
    if 'sorted' in used_names or 'sort' in attr_calls:
        approaches.append("Sorting")

    return list(dict.fromkeys(approaches))  # preserve order, deduplicate


def _has_window_pattern(tree: ast.AST) -> bool:
    """Check for a window-like sliding pattern (two indexes + shrink step)."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.While, ast.For)):
            body_src = ast.dump(node)
            if ('left' in body_src or 'start' in body_src) and \
               ('right' in body_src or 'end' in body_src):
                return True
    return False


def _has_dp_array(tree: ast.AST, dims: int) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('dp', 'memo', 'cache'):
                    if dims == 2 and isinstance(node.value, ast.ListComp):
                        return True
                    if dims == 1 and isinstance(node.value, (ast.List, ast.BinOp)):
                        return True
    return False


# ── Complexity estimation ─────────────────────────────────────────────────────

def _estimate_complexity(tree: ast.AST) -> str:
    """Estimate time complexity from loop nesting and recursion patterns."""
    max_depth = _max_loop_depth(tree, 0)
    func_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    is_recursive = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in func_names
        for n in ast.walk(tree)
    )
    has_sort = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ('sort', 'sorted')
        or isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'sorted'
        for n in ast.walk(tree)
    )
    has_binary_search = any(
        isinstance(n, ast.Name) and n.id in ('bisect', 'bisect_left', 'bisect_right')
        for n in ast.walk(tree)
    )

    if is_recursive:
        if max_depth >= 1:
            return "O(n · recursion depth) — verify your recurrence"
        return "O(recursion depth) — verify your recurrence"

    if max_depth == 0:
        if has_sort:
            return "O(n log n)"
        if has_binary_search:
            return "O(log n)"
        return "O(n) or O(1)"
    if max_depth == 1:
        if has_sort:
            return "O(n log n)"
        return "O(n)"
    if max_depth == 2:
        return "O(n²)"
    return f"O(n^{max_depth})"


def _max_loop_depth(node: ast.AST, depth: int) -> int:
    max_d = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.For, ast.While)):
            d = _max_loop_depth(child, depth + 1)
        else:
            d = _max_loop_depth(child, depth)
        max_d = max(max_d, d)
    return max_d


# ── Approach vs expected pattern ─────────────────────────────────────────────

_PATTERN_SIGNALS = {
    "Hash Map": ["Hash Map / Counting"],
    "Two Pointers": ["Two Pointers"],
    "Sliding Window": ["Sliding Window", "Two Pointers"],
    "Binary Search": ["Binary Search"],
    "Stack": ["Stack"],
    "Dynamic Programming 1D": ["Dynamic Programming (1D)"],
    "Dynamic Programming 2D": ["Dynamic Programming (2D)"],
    "Backtracking": ["Backtracking (Recursion)"],
    "Graph DFS/BFS": ["BFS (Queue)", "Recursion / DFS"],
    "Intervals": ["Sorting"],
    "Heap": ["Heap / Priority Queue"],
    "Linked List": [],
    "Tree DFS": ["Recursion / DFS"],
    "Tree BFS": ["BFS (Queue)"],
    "Bit Manipulation": [],
    "Trie": [],
    "Greedy / Kadane's": [],
    "Matrix": [],
    "Expand Around Center": [],
    "Heap / Quickselect": ["Heap / Priority Queue", "Sorting"],
}


def _pattern_feedback(detected: List[str], expected_pattern: str) -> Optional[str]:
    expected_signals = _PATTERN_SIGNALS.get(expected_pattern, [])
    if not expected_signals:
        return None
    if any(s in detected for s in expected_signals):
        return None  # using the right approach
    return (
        f"This is a '{expected_pattern}' problem but your code doesn't show that pattern. "
        f"The intended approach uses: {', '.join(expected_signals)}."
    )


# ── Classic AST checks ────────────────────────────────────────────────────────

def _check_variable_names(tree: ast.AST) -> List[str]:
    findings = []
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in seen:
                continue
            seen.add(node.id)
            if len(node.id) == 1 and node.id not in {"i", "j", "k", "x", "y", "z", "n", "m"}:
                findings.append(f"Variable '{node.id}' is a single letter — use a descriptive name.")
            if node.id.isupper() and len(node.id) > 1:
                findings.append(f"Avoid all-caps variable '{node.id}' — use snake_case.")
    return findings


def _check_mutable_defaults(tree: ast.AST) -> List[str]:
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.defaults:
                if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                    findings.append(
                        f"'{node.name}' uses a mutable default argument — use None and assign inside."
                    )
    return findings


def _check_early_return(tree: ast.AST) -> List[str]:
    """Detect if code could benefit from early returns instead of deeply nested ifs."""
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            max_if_depth = _max_if_depth(node, 0)
            if max_if_depth >= 3:
                findings.append(
                    "Deeply nested conditionals — consider early returns or guard clauses to flatten the logic."
                )
    return findings


def _max_if_depth(node: ast.AST, depth: int) -> int:
    max_d = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.If):
            d = _max_if_depth(child, depth + 1)
        else:
            d = _max_if_depth(child, depth)
        max_d = max(max_d, d)
    return max_d


def _check_unnecessary_list_conversion(tree: ast.AST) -> List[str]:
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == 'list' and node.args:
                inner = node.args[0]
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name):
                    if inner.func.id in ('range', 'map', 'filter', 'zip', 'enumerate'):
                        findings.append(
                            f"Wrapping {inner.func.id}() in list() is often unnecessary — "
                            "you can iterate directly in a for-loop."
                        )
                        break
    return findings


# ── Main entry point ──────────────────────────────────────────────────────────

def analyze_code(code: str, question: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    report = {
        "readability": [],
        "efficiency": [],
        "style": [],
        "risk": [],
        "approach": [],
        "estimated_complexity": "",
        "pattern_warning": None,
        "score": 100,
    }

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {**report, "style": [f"Syntax error: {exc}"], "score": 0, "error": str(exc)}

    detected = _detect_approach(tree, code)
    report["approach"] = detected
    report["estimated_complexity"] = _estimate_complexity(tree)

    if question:
        warn = _pattern_feedback(detected, question.get("pattern", ""))
        if warn:
            report["pattern_warning"] = warn

    report["style"].extend(_check_variable_names(tree))
    report["style"].extend(_check_mutable_defaults(tree))
    report["readability"].extend(_check_early_return(tree))
    report["efficiency"].extend(_check_unnecessary_list_conversion(tree))

    # Complexity mismatch
    expected_tc = question.get("time_complexity", "") if question else ""
    estimated = report["estimated_complexity"]
    if expected_tc and estimated:
        if "n²" in estimated and "O(n)" == expected_tc.strip():
            report["efficiency"].append(
                f"Your solution appears O(n²) but this problem has an O(n) solution. "
                f"Hint: can you avoid the nested loop with a hash map or two pointers?"
            )
        elif "n²" in estimated and "O(n log n)" in expected_tc:
            report["efficiency"].append(
                f"Your solution appears O(n²) but O(n log n) is achievable. Consider sorting first."
            )

    deductions = (
        len(report["style"]) * 3 +
        len(report["efficiency"]) * 5 +
        len(report["readability"]) * 2 +
        len(report["risk"]) * 4 +
        (10 if report["pattern_warning"] else 0)
    )
    report["score"] = max(0, 100 - deductions)
    return report
