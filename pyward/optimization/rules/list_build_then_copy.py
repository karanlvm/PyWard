import ast
from typing import List, Dict
from pyward.format.formatter import format_optimization_warning

def check_list_build_then_copy(tree: ast.AST) -> List[str]:
    issues: List[str] = []
    empties: Dict[str, int] = {}

    class BuildVisitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                if isinstance(node.value, ast.List) and not node.value.elts:
                    empties[name] = node.lineno
                if (
                    isinstance(node.value, ast.Subscript)
                    and isinstance(node.value.value, ast.Name)
                    and isinstance(node.value.slice, ast.Slice)
                    and node.value.slice.lower is None and node.value.slice.upper is None
                ):
                    src = node.value.value.id
                    if src in empties:
                        issues.append(
                            format_optimization_warning(
                                f"List '{src}' is built via append then copied with slice. Consider using a list comprehension.",
                                node.lineno
                            )
                        )
            self.generic_visit(node)

    BuildVisitor().visit(tree)
    return issues
