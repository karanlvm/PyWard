import ast
from typing import List

from pyward.format.formatter import format_security_warning


def check_yaml_load_usage(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class YAMLVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "yaml"
                and node.func.attr == "load"
            ):
                safe = any(
                    kw.arg == "Loader" and getattr(kw.value, "attr", "") == "SafeLoader"
                    for kw in node.keywords
                )
                if not safe:
                    issues.append(
                        format_security_warning(
                            "Use of yaml.load() without SafeLoader. Risk of code execution.",
                            node.lineno,
                        )
                    )
            self.generic_visit(node)

    YAMLVisitor().visit(tree)
    return issues
