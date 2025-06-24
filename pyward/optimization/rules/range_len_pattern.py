import ast
from typing import List

from pyward.format.formatter import format_optimization_warning


def check_range_len_pattern(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
            fn, args = node.iter.func, node.iter.args
            if isinstance(fn, ast.Name) and fn.id == "range" and len(args) == 1:
                inner = args[0]
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Name)
                    and inner.func.id == "len"
                ):
                    issues.append(
                        format_optimization_warning(
                            "Loop over 'range(len(...))'. Consider using 'enumerate()' instead.",
                            node.lineno,
                        )
                    )
    return issues
