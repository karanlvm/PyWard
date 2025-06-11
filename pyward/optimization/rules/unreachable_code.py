import ast
from typing import List
from pyward.format.formatter import format_optimization_warning

def check_unreachable_code(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    def _check_body(body):
        unreachable = False
        for node in body:
            if unreachable:
                issues.append(
                    format_optimization_warning(
                        "This code is unreachable.",
                        node.lineno
                    )
                )
                if hasattr(node, "body"):
                    _check_body(node.body)
                continue
            if isinstance(node, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                unreachable = True
            for sect in getattr(node, "body", []) + getattr(node, "orelse", []) + getattr(node, "finalbody", []):
                _check_body([sect])

    _check_body(tree.body)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _check_body(node.body)
    return issues
