import ast
from typing import List
from pyward.format.formatter import format_optimization_warning

def check_open_without_context(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class OpenVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_with = False

        def visit_With(self, node):
            prev, self.in_with = self.in_with, True
            self.generic_visit(node)
            self.in_with = prev

        def visit_AsyncWith(self, node):
            prev, self.in_with = self.in_with, True
            self.generic_visit(node)
            self.in_with = prev

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == "open" and not self.in_with:
                issues.append(
                    format_optimization_warning(
                        "Use of open() outside of a 'with' context manager. Consider using 'with open(...) as f:'.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    OpenVisitor().visit(tree)
    return issues
