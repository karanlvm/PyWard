import ast
from typing import List

from pyward.optimization.run import run_all_optimization_checks
from pyward.security.run import run_all_security_checks


def analyze_file(
    filepath: str,
    run_optimization: bool = True,
    run_security: bool = True,
    verbose: bool = False,
) -> List[str]:
    """
    Parse filepath into AST and source text, then run:
      - optimization checks on the source text
      - security checks on the AST
    Returns a list of formatted issue strings.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as se:
        return [f"SyntaxError while parsing {filepath}: {se}"]

    issues: List[str] = []

    if run_optimization:
        issues.extend(run_all_optimization_checks(source))

    if run_security:
        issues.extend(run_all_security_checks(tree))

    if verbose and not issues:
        issues.append("Verbose: no issues found, but checks were performed.")

    return issues
