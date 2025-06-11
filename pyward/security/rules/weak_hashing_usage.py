import ast
from typing import List
from pyward.format.formatter import format_security_warning

def check_weak_hashing_usage(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class HashVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "hashlib" and node.func.attr in ("md5","sha1"):
                # ignore usedforsecurity=False
                if not any(kw.arg == "usedforsecurity" and not kw.value.value for kw in node.keywords):
                    issues.append(
                        format_security_warning(
                            f"Use of hashlib.{node.func.attr}(). Consider sha256 or stronger.",
                            node.lineno
                        )
                    )
            self.generic_visit(node)

    HashVisitor().visit(tree)
    return issues
