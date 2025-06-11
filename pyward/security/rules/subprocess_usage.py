import ast
from typing import List
from pyward.format.formatter import format_security_warning

def check_subprocess_usage(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class SubprocessVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute):
                attr = node.func
                if isinstance(attr.value, ast.Name) and attr.value.id == "subprocess" and attr.attr in ("run","Popen","call","check_output"):
                    for kw in node.keywords:
                        if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value:
                            issues.append(
                                format_security_warning(
                                    f"Use of subprocess.{attr.attr}() with shell=True. Risk of shell injection.",
                                    node.lineno
                                )
                            )
            self.generic_visit(node)

    SubprocessVisitor().visit(tree)
    return issues
