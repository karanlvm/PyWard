import ast
from typing import List

from pyward.format.formatter import format_optimization_warning


def check_membership_on_list_in_loop(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class MemVisitor(ast.NodeVisitor):
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

        def visit_Compare(self, node):
            if self.in_loop:
                for op, comp in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.In, ast.NotIn)) and isinstance(
                        comp, ast.Name
                    ):
                        expr = ast.unparse(node)
                        issues.append(
                            format_optimization_warning(
                                f"Membership test '{expr}' inside loop. Consider converting '{comp.id}' to set for faster lookups.",
                                node.lineno,
                            )
                        )
            self.generic_visit(node)

    MemVisitor().visit(tree)
    return issues
