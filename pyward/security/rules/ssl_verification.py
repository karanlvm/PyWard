import ast
from typing import List
from pyward.format.formatter import format_security_warning

def check_ssl_verification_disabled(tree: ast.AST) -> List[str]:
    """
    Flag any use of the requests library or its Session() with verify=False,
    which disables SSL certificate verification and exposes you to MITM attacks.
    Recommendation: Enable SSL verification or provide a custom CA bundle.
    """
    issues: List[str] = []

    class SSLVerificationVisitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            # Did someone explicitly pass verify=False?
            verify_false = any(
                kw.arg == "verify"
                and isinstance(kw.value, ast.Constant)
                and kw.value.value is False
                for kw in node.keywords
            )
            if not verify_false:
                return self.generic_visit(node)

            func = node.func
            # Only flag HTTP methods and generic .request calls
            if isinstance(func, ast.Attribute) and func.attr in (
                "get", "post", "put", "delete", "head", "options", "patch", "request"
            ):
                # Build a message prefix that mentions the exact call
                call_name = (
                    f"{func.value.id}.{func.attr}()"
                    if isinstance(func.value, ast.Name)
                    else f"{func.attr}()"
                )
                issues.append(
                    format_security_warning(
                        f"Use of {call_name} with verify=False detected. "
                        "Disabling certificate verification exposes users to "
                        "man-in-the-middle attacks. "
                        "Recommendation: Enable SSL verification or provide a "
                        "custom CA bundle instead.",
                        node.lineno
                    )
                )

            # continue walking
            self.generic_visit(node)

    SSLVerificationVisitor().visit(tree)
    return issues