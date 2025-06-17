import ast
from typing import List, Set, Tuple
from pyward.format.formatter import format_optimization_warning
from pyward.fixer.fix_imports import ImportFixer

def check_unused_imports(tree: ast.AST) -> List[str]:
    issues: List[str] = []
    imported_names: Set[str] = set()
    import_nodes: List[Tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = (alias.asname or alias.name).split(".")[0]
                imported_names.add(name)
                import_nodes.append((name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                imported_names.add(name)
                import_nodes.append((name, node.lineno))

    if not imported_names:
        return issues

    used_names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for name, lineno in import_nodes:
        if name not in used_names:
            issues.append(
                format_optimization_warning(
                    f"Imported name '{name}' is never used.",
                    lineno
                )
            )
    return issues


def fix_unused_imports(source: str) -> Tuple[bool, str]:
    fixer = ImportFixer(source)
    if not fixer.unused_names_in_import:
        return (False, source)
    for name_and_import in fixer.unused_names_in_import:
        msg = f"from {name_and_import[1].module} import {name_and_import[0]} deleted" if name_and_import[1].is_from else f"import {name_and_import[0]} deleted"
        print(msg)
    return (True, fixer.fix())
