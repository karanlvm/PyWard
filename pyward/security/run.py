import ast
import pkgutil
import importlib
from typing import List, Tuple

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


def run_all_security_fixes(source_code: str, skip: List[str] = None) -> Tuple[bool, str]:
    """fix code with fixable security rules, add rule into skip list, return fix flag and fixed code"""
    skip_set = set(skip or [])

    pkg = importlib.import_module(f"{__package__}.rules")
    prefix = pkg.__name__ + "."
    current_source = source_code
    file_ever_changed = False
    for _, mod_name, _ in pkgutil.iter_modules(pkg.__path__, prefix):
        mod = importlib.import_module(mod_name)
        for fn_name in dir(mod):
            fix_fn_name = "fix_" + mod_name
            check_fn_name = "check_" + mod_name
            if fn_name != fix_fn_name or check_fn_name in skip_set:
                continue
            fix_fn = getattr(mod, fix_fn_name)
            if callable(fix_fn_name):
                file_changed, current_source = fix_fn(source_code)
                file_ever_changed = file_changed or file_ever_changed
                skip.append(check_fn_name)

    return (file_ever_changed, current_source)
