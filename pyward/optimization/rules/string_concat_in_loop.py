import ast
from typing import List
from pyward.format.formatter import format_optimization_warning

def check_string_concat_in_loop(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class ConcatVisitor(ast.NodeVisitor):
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
            if self.in_loop and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                val = node.value
                if isinstance(val, ast.BinOp) and isinstance(val.op, ast.Add):
                    if isinstance(val.left, ast.Name) and val.left.id == name:
                        issues.append(
                            format_optimization_warning(
                                f"String concatenation in loop for '{name}'. Consider using ''.join() or appending to a list.",
                                node.lineno
                            )
                        )
            self.generic_visit(node)

        def visit_AugAssign(self, node):
            if self.in_loop and isinstance(node.op, ast.Add) and isinstance(node.target, ast.Name):
                issues.append(
                    format_optimization_warning(
                        f"Augmented assignment '{node.target.id} += ...' in loop. Consider using ''.join() or appending to a list.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    ConcatVisitor().visit(tree)
    return issues
