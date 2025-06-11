import ast
from typing import List
from pyward.format.formatter import format_optimization_warning

def check_len_call_in_loop(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class LenVisitor(ast.NodeVisitor):
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
            if self.in_loop and isinstance(node.func, ast.Name) and node.func.id == "len":
                issues.append(
                    format_optimization_warning(
                        "Call to len() inside loop. Consider storing the length in a variable before the loop.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    LenVisitor().visit(tree)
    return issues
