import ast
from typing import List, Set, Tuple
from pyward.format.formatter import format_optimization_warning

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
