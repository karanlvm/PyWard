import ast
import pkgutil
import importlib
from typing import List

def run_all_optimization_checks(source_code: str, skip: List[str] = None) -> List[str]:
    skip = set(skip or [])
    tree = ast.parse(source_code)
    issues: List[str] = []

    pkg = importlib.import_module(f"{__package__}.rules")
    prefix = pkg.__name__ + "."
    for _, mod_name, _ in pkgutil.iter_modules(pkg.__path__, prefix):
        mod = importlib.import_module(mod_name)
        for fn_name in dir(mod):
            if not fn_name.startswith("check_") or fn_name in skip:
                continue
            fn = getattr(mod, fn_name)
            issues.extend(fn(tree))

    return issues

