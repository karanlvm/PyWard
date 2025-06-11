import ast
from typing import List
from pyward.format.formatter import format_security_warning

def check_python_json_logger_import(tree: ast.AST) -> List[str]:
    """
    Flag any import of 'python_json_logger' (vulnerable to CVE-2025-27607).
    """
    issues: List[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("python_json_logger"):
                    issues.append(
                        format_security_warning(
                            "'python_json_logger' import detected. "
                            "This package was vulnerable to RCE (CVE-2025-27607). "
                            "Update to a patched version or remove this dependency.",
                            node.lineno,
                            "CVE-2025-27607"
                        )
                    )
        elif isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("python_json_logger"):
            issues.append(
                format_security_warning(
                    "'from python_json_logger import ...' detected. "
                    "This package was vulnerable to RCE (CVE-2025-27607). "
                    "Update to a patched version or remove this dependency.",
                    node.lineno,
                    "CVE-2025-27607"
                )
            )

    return issues
