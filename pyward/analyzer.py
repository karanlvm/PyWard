import ast
from typing import List

from pyward.rules.optimization_rules import run_all_optimization_checks
from pyward.rules.security_rules import run_all_checks as run_all_security_checks


def analyze_file(
    filepath: str,
    run_optimization: bool = True,
    run_security: bool = True,
    verbose: bool = False,
) -> List[str]:
    """
    Parse the given Python file into an AST (and source text) and run:
      - All optimization checks if run_optimization is True
      - All security checks if run_security is True

    Returns a list of human-readable issue strings.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as se:
        return [f"SyntaxError while parsing {filepath}: {se}"]

    issues: List[str] = []

    if run_optimization:
        # optimization_rules.run_all_optimization_checks expects the source text
        issues.extend(run_all_optimization_checks(source))

    if run_security:
        # security_rules.run_all_checks expects the AST
        issues.extend(run_all_security_checks(tree))

    if verbose and not issues:
        issues.append("Verbose: no issues found, but checks were performed.")

    return issues
