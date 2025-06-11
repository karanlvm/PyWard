import ast
import pkgutil
import importlib
from typing import List

def run_all_security_checks(
    source_code: str,
    skip: List[str] = None
) -> List[str]:
    """
    Dynamically imports every module in pyward.security.rules
    and runs all functions prefixed with `check_`, unless in skip.
    """
    skip = set(skip or [])
    tree = ast.parse(source_code)
    issues: List[str] = []

    pkg = importlib.import_module(f"{__package__}.rules")
    prefix = pkg.__name__ + "."
    for _, mod_name, _ in pkgutil.iter_modules(pkg.__path__, prefix):
        mod = importlib.import_module(mod_name)
        for attr in dir(mod):
            if not attr.startswith("check_") or attr in skip:
                continue
            fn = getattr(mod, attr)
            if callable(fn):
                issues.extend(fn(tree))

    return issues
