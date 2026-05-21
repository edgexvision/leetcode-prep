import collections
import copy
import heapq
import bisect
import math
import functools
import itertools
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from typing import Any, Dict, List, Tuple

_TEST_TIMEOUT_SECONDS = 2


# ---------------------------------------------------------------------------
# Preamble injected into every submission's exec namespace
# ---------------------------------------------------------------------------
_PREAMBLE = """\
from typing import List, Dict, Set, Tuple, Optional, Any, Union, Deque
from collections import deque


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
    def __repr__(self):
        return f"ListNode({self.val})"


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    def __repr__(self):
        return f"TreeNode({self.val})"


def list_to_linked(arr):
    \"\"\"Convert a Python list to a ListNode chain. Returns None for empty list.\"\"\"
    if not arr:
        return None
    head = ListNode(arr[0])
    cur = head
    for val in arr[1:]:
        cur.next = ListNode(val)
        cur = cur.next
    return head


def linked_to_list(node):
    \"\"\"Convert a ListNode chain to a Python list of values.\"\"\"
    result = []
    while node is not None:
        result.append(node.val)
        node = node.next
    return result


def cyclic_list_to_linked(spec):
    \"\"\"Build a linked list from spec=[arr, pos].
    The tail's next points to nodes[pos]. pos=-1 means no cycle.
    \"\"\"
    arr, pos = spec[0], spec[1]
    if not arr:
        return None
    nodes = [ListNode(v) for v in arr]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    if pos != -1:
        nodes[-1].next = nodes[pos]
    return nodes[0]


def lists_to_linked_array(arrays):
    \"\"\"Map list_to_linked over a list of lists.
    Returns None for empty inner lists.
    \"\"\"
    return [list_to_linked(a) for a in arrays]


def list_to_tree(arr):
    \"\"\"Level-order BFS construction from list (None = missing node).
    Returns None for empty list.
    \"\"\"
    if not arr:
        return None
    root = TreeNode(arr[0])
    queue = deque([root])
    i = 1
    while queue and i < len(arr):
        node = queue.popleft()
        if i < len(arr) and arr[i] is not None:
            node.left = TreeNode(arr[i])
            queue.append(node.left)
        i += 1
        if i < len(arr) and arr[i] is not None:
            node.right = TreeNode(arr[i])
            queue.append(node.right)
        i += 1
    return root


def tree_to_list(root):
    \"\"\"Level-order BFS serialization, trims trailing Nones.
    Returns [] for None root.
    \"\"\"
    if root is None:
        return []
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            result.append(None)
        else:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    # Trim trailing Nones
    while result and result[-1] is None:
        result.pop()
    return result
"""


class SubmissionResult:
    def __init__(self, passed: int, total: int, failed_cases: List[Dict[str, Any]], runtime_ms: float):
        self.passed = passed
        self.total = total
        self.failed_cases = failed_cases
        self.runtime_ms = runtime_ms


class SubmissionError(Exception):
    pass


def _compare(result: Any, expected: Any, comparison: str) -> bool:
    if comparison == "any_order":
        try:
            return sorted(result) == sorted(expected)
        except TypeError:
            return sorted(str(x) for x in result) == sorted(str(x) for x in expected)
    if comparison == "sorted_groups":
        try:
            return sorted([sorted(g) for g in result]) == sorted([sorted(g) for g in expected])
        except Exception:
            return False
    if comparison == "set_of_tuples":
        try:
            return {tuple(x) for x in result} == {tuple(x) for x in expected}
        except Exception:
            return False
    if comparison == "set_of_sorted_tuples":
        try:
            return {tuple(sorted(x)) for x in result} == {tuple(sorted(x)) for x in expected}
        except Exception:
            return False
    return result == expected


def execute_submission(code: str, function_name: str, test_cases: List[Dict[str, Any]]) -> SubmissionResult:
    namespace = {
        "__name__": "__submission__",
        "__builtins__": {
            # constants
            "True": True, "False": False, "None": None,
            # types
            "list": list, "dict": dict, "set": set, "tuple": tuple,
            "int": int, "str": str, "float": float, "bool": bool,
            "bytes": bytes,
            # builtins used constantly in interview solutions
            "range": range, "len": len, "print": print,
            "min": min, "max": max, "sum": sum, "abs": abs,
            "sorted": sorted, "reversed": reversed,
            "enumerate": enumerate, "zip": zip,
            "map": map, "filter": filter,
            "any": any, "all": all,
            "isinstance": isinstance, "type": type,
            "round": round, "divmod": divmod, "pow": pow,
            "hash": hash, "id": id,
            "repr": repr, "chr": chr, "ord": ord, "hex": hex, "bin": bin,
            "open": open,
            # needed so `import X` statements inside solution code work
            "__import__": __import__,
            # needed for class definitions (ListNode, TreeNode in preamble)
            "__build_class__": __build_class__,
            # standard library modules needed for interview patterns
            "collections": collections,
            "heapq": heapq,
            "bisect": bisect,
            "math": math,
            "functools": functools,
            "itertools": itertools,
        }
    }

    try:
        exec(_PREAMBLE + code, namespace)
    except Exception as exc:
        raise SubmissionError(f"Failed to compile submission: {exc}") from exc

    if function_name not in namespace:
        raise SubmissionError(f"Submission must define a function named '{function_name}'")

    func = namespace[function_name]
    passed = 0
    failed_cases = []
    start = time.time()

    for idx, case in enumerate(test_cases, start=1):
        inputs = copy.deepcopy(case["input"])
        expected = case["expected"]
        comparison = case.get("comparison", "exact")

        # Apply input converters (name → function looked up from namespace)
        input_converters = case.get("input_converters", {})
        for param, converter_name in input_converters.items():
            converter = namespace.get(converter_name)
            if converter is not None and param in inputs:
                inputs[param] = converter(inputs[param])

        try:
            def _run():
                out = func(**inputs)
                output_converter_name = case.get("output_converter")
                if output_converter_name:
                    conv = namespace.get(output_converter_name)
                    if conv is not None:
                        out = conv(out)
                return out

            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(_run)
            try:
                result = future.result(timeout=_TEST_TIMEOUT_SECONDS)
            except FuturesTimeout:
                executor.shutdown(wait=False)  # don't block waiting for the stuck thread
                failed_cases.append({
                    "case": idx, "input": case["input"], "expected": expected,
                    "error": f"Time Limit Exceeded (>{_TEST_TIMEOUT_SECONDS}s) — infinite loop? Check your loop termination condition."
                })
                continue
            finally:
                executor.shutdown(wait=False)

            if _compare(result, expected, comparison):
                passed += 1
            else:
                failed_cases.append({"case": idx, "input": case["input"], "expected": expected, "output": result})
        except Exception as exc:
            failed_cases.append({"case": idx, "input": case["input"], "expected": expected, "error": str(exc)})

    runtime_ms = (time.time() - start) * 1000
    return SubmissionResult(passed=passed, total=len(test_cases), failed_cases=failed_cases, runtime_ms=runtime_ms)
