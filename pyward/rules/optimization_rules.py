import ast
from typing import List, Set, Tuple, Dict
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

    used_names: Set[str] = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for name, lineno in import_nodes:
        if name not in used_names:
            issues.append(
                format_optimization_warning(
                    f"Imported name '{name}' is never used.",
                    lineno
                )
            )
    return issues

def check_unused_variables(tree: ast.AST) -> List[str]:
    issues: List[str] = []
    assigned_names: Dict[str, int] = {}

    def _collect_target(tgt: ast.AST, lineno: int):
        if isinstance(tgt, ast.Name):
            if tgt.id not in assigned_names:
                assigned_names[tgt.id] = lineno
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

    used_names: Set[str] = {
        n.id for n in ast.walk(tree)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
    }

    for name, lineno in assigned_names.items():
        if not name.startswith("_") and name not in used_names:
            issues.append(
                format_optimization_warning(
                    f"Variable '{name}' is assigned but never used.",
                    lineno
                )
            )
    return issues

def check_unreachable_code(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    def _check_body(body: List[ast.AST]):
        unreachable = False
        for node in body:
            if unreachable:
                issues.append(
                    format_optimization_warning(
                        "This code is unreachable.",
                        node.lineno
                    )
                )
                if hasattr(node, "body"):
                    _check_body(node.body)  # type: ignore
                continue

            if isinstance(node, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                unreachable = True

            # recurse into nested blocks
            for sect in getattr(node, "body", []) + getattr(node, "orelse", []) + getattr(node, "finalbody", []):
                _check_body([sect])  # type: ignore

    _check_body(tree.body)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _check_body(node.body)
    return issues

def check_string_concat_in_loop(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class ConcatVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_While(self, node: ast.While):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_Assign(self, node: ast.Assign):
            if self.in_loop and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                val = node.value
                if isinstance(val, ast.BinOp) and isinstance(val.op, ast.Add):
                    if isinstance(val.left, ast.Name) and val.left.id == name:
                        issues.append(
                            format_optimization_warning(
                                f"String concatenation in loop for '{name}'. Consider using ''.join() or appending to a list and joining outside the loop.",
                                node.lineno
                            )
                        )
            self.generic_visit(node)

        def visit_AugAssign(self, node: ast.AugAssign):
            if self.in_loop and isinstance(node.op, ast.Add) and isinstance(node.target, ast.Name):
                issues.append(
                    format_optimization_warning(
                        f"Augmented assignment '{node.target.id} += ...' in loop. Consider using ''.join() or appending to a list and joining outside the loop.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    ConcatVisitor().visit(tree)
    return issues

def check_len_call_in_loop(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class LenVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_While(self, node: ast.While):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_Call(self, node: ast.Call):
            if self.in_loop and isinstance(node.func, ast.Name) and node.func.id == "len":
                issues.append(
                    format_optimization_warning(
                        "Call to len() inside loop. Consider storing the length in a variable before the loop.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    LenVisitor().visit(tree)
    return issues

def check_range_len_pattern(tree: ast.AST) -> List[str]:
    issues: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
            fn = node.iter.func
            args = node.iter.args
            if isinstance(fn, ast.Name) and fn.id == "range" and len(args) == 1:
                inner = args[0]
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) and inner.func.id == "len":
                    issues.append(
                        format_optimization_warning(
                            "Loop over 'range(len(...))'. Consider using 'enumerate()' to iterate directly over the sequence.",
                            node.lineno
                        )
                    )
    return issues

def check_append_in_loop(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class AppendVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_While(self, node: ast.While):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_Call(self, node: ast.Call):
            if self.in_loop and isinstance(node.func, ast.Attribute) and node.func.attr == "append":
                issues.append(
                    format_optimization_warning(
                        "Using list.append() inside a loop. Consider using a list comprehension for better performance.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    AppendVisitor().visit(tree)
    return issues

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
                                f"List '{src}' is built via append and then copied with slice. Consider using a list comprehension: [transform(x) for x in iterable if cond(x)]",
                                node.lineno
                            )
                        )
            self.generic_visit(node)

    BuildVisitor().visit(tree)
    return issues

def check_sort_assignment(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class SortVisitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign):
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "sort"
            ):
                issues.append(
                    format_optimization_warning(
                        "Assignment of list.sort() which returns None. Use sorted(list) if you need the sorted result in a new variable.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    SortVisitor().visit(tree)
    return issues

def check_deeply_nested_loops(tree: ast.AST, max_depth: int = 2) -> List[str]:
    issues: List[str] = []

    class NestVisitor(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0

        def visit_FunctionDef(self, node: ast.FunctionDef):
            prev = self.depth; self.depth = 0
            self.generic_visit(node)
            self.depth = prev

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            prev = self.depth; self.depth = 0
            self.generic_visit(node)
            self.depth = prev

        def visit_For(self, node: ast.For):
            self.depth += 1
            if self.depth > max_depth:
                issues.append(
                    format_optimization_warning(
                        f"High complexity: loop nesting depth is {self.depth}.",
                        node.lineno
                    )
                )
            self.generic_visit(node)
            self.depth -= 1

        def visit_While(self, node: ast.While):
            self.depth += 1
            if self.depth > max_depth:
                issues.append(
                    format_optimization_warning(
                        f"High complexity: loop nesting depth is {self.depth}.",
                        node.lineno
                    )
                )
            self.generic_visit(node)
            self.depth -= 1

    NestVisitor().visit(tree)
    return issues

def check_dict_comprehension(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class DictVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_While(self, node: ast.While):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_Assign(self, node: ast.Assign):
            if self.in_loop and len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript):
                dname = node.targets[0].value.id  # type: ignore
                issues.append(
                    format_optimization_warning(
                        f"Building dict '{dname}' via loop assignment. Consider using a dict comprehension.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    DictVisitor().visit(tree)
    return issues

def check_set_comprehension(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class SetVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_While(self, node: ast.While):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_Call(self, node: ast.Call):
            if self.in_loop and isinstance(node.func, ast.Attribute) and node.func.attr == "add":
                sname = node.func.value.id  # type: ignore
                issues.append(
                    format_optimization_warning(
                        f"Building set '{sname}' via add() in a loop. Consider using a set comprehension.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    SetVisitor().visit(tree)
    return issues

def check_genexpr_vs_list(tree: ast.AST) -> List[str]:
    issues: List[str] = []
    GENFUNCS = {"sum", "any", "all", "max", "min"}

    class GenVisitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in GENFUNCS:
                arg = node.args[0] if node.args else None
                if isinstance(arg, ast.ListComp):
                    fname = node.func.id
                    issues.append(
                        format_optimization_warning(
                            f"{fname}() applied to a list comprehension. Consider using a generator expression (remove the brackets) for better memory efficiency.",
                            node.lineno
                        )
                    )
            self.generic_visit(node)

    GenVisitor().visit(tree)
    return issues

def check_membership_on_list_in_loop(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class MemVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_While(self, node: ast.While):
            prev = self.in_loop; self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_Compare(self, node: ast.Compare):
            if self.in_loop:
                for op, comp in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.In, ast.NotIn)) and isinstance(comp, ast.Name):
                        expr = ast.unparse(node)
                        issues.append(
                            format_optimization_warning(
                                f"Membership test '{expr}' inside a loop. If '{comp.id}' is a large list, consider converting it to a set for faster lookups.",
                                node.lineno
                            )
                        )
            self.generic_visit(node)

    MemVisitor().visit(tree)
    return issues

def check_open_without_context(tree: ast.AST) -> List[str]:
    issues: List[str] = []

    class OpenVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_with = False

        def visit_With(self, node: ast.With):
            prev = self.in_with; self.in_with = True
            self.generic_visit(node)
            self.in_with = prev

        def visit_AsyncWith(self, node: ast.AsyncWith):
            prev = self.in_with; self.in_with = True
            self.generic_visit(node)
            self.in_with = prev

        def visit_Call(self, node: ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open" and not self.in_with:
                issues.append(
                    format_optimization_warning(
                        "Use of open() outside of a 'with' context manager. Consider using 'with open(...) as f:' for better resource management.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    OpenVisitor().visit(tree)
    return issues

def run_all_optimization_checks(source_code: str) -> List[str]:
    tree = ast.parse(source_code)
    issues: List[str] = []

    issues.extend(check_unused_imports(tree))
    issues.extend(check_unused_variables(tree))
    issues.extend(check_unreachable_code(tree))
    issues.extend(check_string_concat_in_loop(tree))
    issues.extend(check_len_call_in_loop(tree))
    issues.extend(check_range_len_pattern(tree))
    issues.extend(check_append_in_loop(tree))
    issues.extend(check_list_build_then_copy(tree))
    issues.extend(check_sort_assignment(tree))
    issues.extend(check_deeply_nested_loops(tree))
    issues.extend(check_dict_comprehension(tree))
    issues.extend(check_set_comprehension(tree))
    issues.extend(check_genexpr_vs_list(tree))
    issues.extend(check_membership_on_list_in_loop(tree))
    issues.extend(check_open_without_context(tree))

    return sorted(set(issues))
