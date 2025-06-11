import ast
from typing import List
from pyward.format.formatter import format_security_warning

def check_url_open_usage(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class URLVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            # urllib.request.urlopen
            if isinstance(node.func, ast.Attribute):
                f = node.func
                if (isinstance(f.value, ast.Attribute)
                    and isinstance(f.value.value, ast.Name)
                    and f.value.value.id == "urllib"
                    and f.value.attr == "request"
                    and f.attr == "urlopen"):
                    if not node.args or not isinstance(node.args[0], ast.Constant):
                        issues.append(
                            format_security_warning(
                                "Dynamic URL to urllib.request.urlopen(). Validate/sanitize first.",
                                node.lineno
                            )
                        )
                # urllib3.PoolManager().request
                if f.attr == "request" and len(node.args) >= 2:
                    if not isinstance(node.args[1], ast.Constant):
                        issues.append(
                            format_security_warning(
                                "Dynamic URL to urllib3.PoolManager().request(). Validate/sanitize first.",
                                node.lineno
                            )
                        )
            self.generic_visit(node)

    URLVisitor().visit(tree)
    return issues
