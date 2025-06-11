import ast
from typing import List
from pyward.format.formatter import format_optimization_warning

def check_genexpr_vs_list(tree: ast.AST) -> List[str]:
    issues: List[str] = []
    GENFUNCS = {"sum", "any", "all", "max", "min"}

    class GenVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id in GENFUNCS:
                arg = node.args[0] if node.args else None
                if isinstance(arg, ast.ListComp):
                    issues.append(
                        format_optimization_warning(
                            f"{node.func.id}() applied to list comprehension. Consider using a generator expression.",
                            node.lineno
                        )
                    )
            self.generic_visit(node)

    GenVisitor().visit(tree)
    return issues
