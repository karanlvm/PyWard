import ast
from typing import List
from pyward.format.formatter import format_optimization_warning

def check_append_in_loop(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class AppendVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node):
            prev, self.in_loop = self.in_loop, True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_While(self, node):
            prev, self.in_loop = self.in_loop, True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_Call(self, node):
            if self.in_loop and isinstance(node.func, ast.Attribute) and node.func.attr == "append":
                issues.append(
                    format_optimization_warning(
                        "Using list.append() inside a loop. Consider using a list comprehension.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    AppendVisitor().visit(tree)
    return issues
