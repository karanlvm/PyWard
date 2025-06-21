import ast
from typing import List

from pyward.format.formatter import format_optimization_warning


def check_sort_assignment(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class SortVisitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign):
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "sort"
            ):
                issues.append(
                    format_optimization_warning(
                        "Assignment of list.sort() which returns None. Use sorted(list) instead.",
                        node.lineno,
                    )
                )
            self.generic_visit(node)

    SortVisitor().visit(tree)
    return issues
