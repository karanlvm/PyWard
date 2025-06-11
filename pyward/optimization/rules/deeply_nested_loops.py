import ast
from typing import List
from pyward.format.formatter import format_optimization_warning

def check_deeply_nested_loops(tree: ast.AST, max_depth: int = 2) -> List[str]:
    issues: List[str] = []

    class NestVisitor(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0

        def visit_FunctionDef(self, node):
            prev, self.depth = self.depth, 0
            self.generic_visit(node)
            self.depth = prev

        def visit_AsyncFunctionDef(self, node):
            prev, self.depth = self.depth, 0
            self.generic_visit(node)
            self.depth = prev

        def visit_For(self, node):
            self.depth += 1
            if self.depth > max_depth:
                issues.append(
                    format_optimization_warning(
                        f"High complexity: loop nesting depth is {self.depth}.",
                        node.lineno
                    )
                )
            self.generic_visit(node)
            self.depth -= 1

        def visit_While(self, node):
            self.depth += 1
            if self.depth > max_depth:
                issues.append(
                    format_optimization_warning(
                        f"High complexity: loop nesting depth is {self.depth}.",
                        node.lineno
                    )
                )
            self.generic_visit(node)
            self.depth -= 1

    NestVisitor().visit(tree)
    return issues
