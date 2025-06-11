import ast
from typing import List
from pyward.format.formatter import format_optimization_warning

def check_set_comprehension(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class SetVisitor(ast.NodeVisitor):
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
            if self.in_loop and isinstance(node.func, ast.Attribute) and node.func.attr == "add":
                sname = node.func.value.id  # type: ignore
                issues.append(
                    format_optimization_warning(
                        f"Building set '{sname}' via add() in loop. Consider using set comprehension.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    SetVisitor().visit(tree)
    return issues
