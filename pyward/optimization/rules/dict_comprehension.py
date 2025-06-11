import ast
from typing import List
from pyward.format.formatter import format_optimization_warning

def check_dict_comprehension(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class DictVisitor(ast.NodeVisitor):
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

        def visit_Assign(self, node):
            if self.in_loop and len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript):
                dname = node.targets[0].value.id  # type: ignore
                issues.append(
                    format_optimization_warning(
                        f"Building dict '{dname}' via loop assignment. Consider using dict comprehension.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    DictVisitor().visit(tree)
    return issues
