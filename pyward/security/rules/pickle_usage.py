import ast
from typing import List
from pyward.format.formatter import format_security_warning

def check_pickle_usage(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class PickleVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle" and node.func.attr in ("load","loads"):
                issues.append(
                    format_security_warning(
                        "Use of pickle.%s() detected. Untrusted pickle can lead to RCE." % node.func.attr,
                        node.lineno
                    )
                )
            self.generic_visit(node)

    PickleVisitor().visit(tree)
    return issues
