import ast
from typing import List
from pyward.format.formatter import format_security_warning

def check_exec_eval_usage(tree: ast.AST) -> List[str]:
    """
    Flag any direct usage of `exec(...)` or `eval(...)` as a security risk.
    References:
      - CVE-2025-3248 (Langflow AI): abusing `exec` for unauthenticated RCE.
      - General best practice: avoid eval()/exec() on untrusted data.
    """
    issues: List[str] = []

    class ExecEvalVisitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("exec", "eval"):
                issues.append(
                    format_security_warning(
                        f"Use of '{node.func.id}()' detected. "
                        "This can lead to code injection (e.g. CVE-2025-3248). "
                        "Consider safer alternatives (e.g., ast.literal_eval) or explicit parsing.",
                        node.lineno,
                        "CVE-2025-3248"
                    )
                )
            self.generic_visit(node)

    ExecEvalVisitor().visit(tree)
    return issues
