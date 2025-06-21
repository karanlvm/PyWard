import ast
from typing import Dict, List

from pyward.format.formatter import format_optimization_warning


def check_unused_variables(tree: ast.AST) -> List[str]:
    issues: List[str] = []
    assigned_names: Dict[str, int] = {}

    def _collect_target(tgt: ast.AST, lineno: int):
        if isinstance(tgt, ast.Name):
            assigned_names.setdefault(tgt.id, lineno)
        elif isinstance(tgt, (ast.Tuple, ast.List)):
            for elt in tgt.elts:
                _collect_target(elt, lineno)

    class AssignVisitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign):
            for t in node.targets:
                _collect_target(t, node.lineno)
            self.generic_visit(node)

        def visit_AnnAssign(self, node: ast.AnnAssign):
            _collect_target(node.target, node.lineno)
            self.generic_visit(node)

        def visit_AugAssign(self, node: ast.AugAssign):
            _collect_target(node.target, node.lineno)
            self.generic_visit(node)

        def visit_For(self, node: ast.For):
            _collect_target(node.target, node.lineno)
            self.generic_visit(node)

        def visit_With(self, node: ast.With):
            for item in node.items:
                if item.optional_vars:
                    _collect_target(item.optional_vars, node.lineno)
            self.generic_visit(node)

        def visit_AsyncWith(self, node: ast.AsyncWith):
            for item in node.items:
                if item.optional_vars:
                    _collect_target(item.optional_vars, node.lineno)
            self.generic_visit(node)

    AssignVisitor().visit(tree)

    used_names = {
        n.id
        for n in ast.walk(tree)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
    }
    for name, lineno in assigned_names.items():
        if not name.startswith("_") and name not in used_names:
            issues.append(
                format_optimization_warning(
                    f"Variable '{name}' is assigned but never used.", lineno
                )
            )
    return issues
