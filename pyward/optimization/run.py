import ast
import pkgutil
import importlib
from typing import List, Tuple
from os import path

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
            if callable(fn):
                issues.extend(fn(tree))

    return issues


def run_all_optimization_fixes(source_code: str, skip: List[str] = None) -> Tuple[bool, str]:
    """fix code with fixable optimization rules, add rule into skip list, return fix flag and fixed code"""
    skip_set = set(skip or [])

    pkg = importlib.import_module(f"{__package__}.rules")
    prefix = pkg.__name__ + "."
    current_source = source_code
    file_ever_changed = False
    for _, mod_name, _ in pkgutil.iter_modules(pkg.__path__, prefix):
        mod = importlib.import_module(mod_name)
        rule_name = path.basename(str(mod.__file__))[0:-3]
        for fn_name in dir(mod):
            fix_fn_name = "fix_" + rule_name
            check_fn_name = "check_" + rule_name
            if fn_name != fix_fn_name or check_fn_name in skip_set:
                continue
            fix_fn = getattr(mod, fix_fn_name)
            if callable(fix_fn):
                file_changed, current_source = fix_fn(source_code)
                file_ever_changed = file_changed or file_ever_changed
                skip.append(check_fn_name)

    return (file_ever_changed, current_source)

