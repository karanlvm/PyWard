import ast
from typing import List

from pyward.format.formatter import format_security_warning


def check_hardcoded_secrets(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class SecretsVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            if (
                len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                var = node.targets[0].id.lower()
                if any(
                    k in var for k in ("key", "secret", "password", "token", "passwd")
                ):
                    issues.append(
                        format_security_warning(
                            f"Hard-coded secret in '{node.targets[0].id}'. Use env vars or vault.",
                            node.lineno,
                        )
                    )
            self.generic_visit(node)

    SecretsVisitor().visit(tree)
    return issues
