# pyward/analyzer.py

import ast
from typing import List

from pyward.rules.optimization_rules import (
    check_unused_imports,
    check_unreachable_code,
)
from pyward.rules.security_rules import (
    check_exec_eval_usage,
    check_python_json_logger_import,
    check_weak_hashing_usage,
)


def analyze_file(
    filepath: str,
    run_optimization: bool = True,
    run_security: bool = True,
    verbose: bool = False,
) -> List[str]:
    """
    Parse the given Python file into an AST and run:
      - Optimization checks if run_optimization is True
      - Security checks if run_security is True

    Returns a list of human-readable issue strings.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as se:
        return [f"SyntaxError while parsing {filepath}: {se}"]

    issues: List[str] = []

    # === Optimization rules ===
    if run_optimization:
        unused_imports = check_unused_imports(tree)
        issues.extend(unused_imports)

        unreachable = check_unreachable_code(tree)
        issues.extend(unreachable)

    # === Security rules ===
    if run_security:
        exec_eval_issues = check_exec_eval_usage(tree)
        issues.extend(exec_eval_issues)

        json_logger_issues = check_python_json_logger_import(tree)
        issues.extend(json_logger_issues)

        weak_hashing_issues = check_weak_hashing_usage(tree)
        issues.extend(weak_hashing_issues)

    # If verbose is requested but no issues found, add a placeholder message
    if verbose and not issues:
        issues.append("Verbose: no issues found, but checks were performed.")

    return issues
