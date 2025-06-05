import ast
from typing import List, Set, Tuple, Dict
from pyward.format.formatter import format_optimization_warning


def check_unused_imports(tree: ast.AST) -> List[str]:
    """
    Find all imported names (both 'import X' and 'from Y import Z') and then
    see if any of those names are never used elsewhere in the AST.

    Returns a list of warning messages for each unused import.
    """
    issues: List[str] = []

    # 1) Collect all imported names and the linenos where they appear
    imported_names: Set[str] = set()
    import_nodes: List[Tuple[str, int]] = []  # (name, lineno)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                imported_names.add(name.split(".")[0])
                import_nodes.append((name.split(".")[0], node.lineno))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                imported_names.add(name)
                import_nodes.append((name, node.lineno))

    if not imported_names:
        return issues

    # 2) Walk tree again to see which names are actually used
    used_names: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)

    # 3) Anything in imported_names but not in used_names is unused
    unused = imported_names - used_names
    for name, lineno in import_nodes:
        if name in unused:
            issues.append(
                format_optimization_warning(f"Imported name '{name}' is never used.", lineno)
            )

    return issues


def check_unreachable_code(tree: ast.AST) -> List[str]:
    """
    Detect unreachable code: i.e., statements immediately following a 'return',
    'raise', 'break', or 'continue' within the same block. We scan FunctionDef
    and Module-level bodies looking for these patterns.

    Returns a list of warning messages for each unreachable code block.
    """
    issues: List[str] = []

    def _check_body(body: list):
        """
        Given a list of AST nodes (statements), if we see a Return/Raise/Break/Continue,
        any subsequent statement in the same body is unreachable.
        """
        unreachable = False
        for node in body:
            if unreachable:
                issues.append(
                    format_optimization_warning("This code is unreachable.", node.lineno)
                )
                # Continue scanning to catch nested unreachable statements
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.AsyncWith)):
                    _nested: List[ast.AST] = []
                    if isinstance(node, ast.If):
                        _nested.extend(node.body + node.orelse)
                    elif isinstance(node, (ast.For, ast.While)):
                        _nested.extend(node.body + node.orelse)
                    elif isinstance(node, ast.Try):
                        _nested.extend(node.body)
                        for handler in node.handlers:
                            _nested.extend(handler.body)
                        _nested.extend(node.orelse + node.finalbody)
                    elif isinstance(node, (ast.With, ast.AsyncWith)):
                        _nested.extend(node.body)
                    for n in _nested:
                        issues.append(
                            f"[Optimization] Line {n.lineno}: This code is unreachable."
                        )
                continue

            if isinstance(node, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                unreachable = True

            # Dive into compound statements for nested unreachable checks
            if isinstance(node, ast.If):
                _check_body(node.body)
                _check_body(node.orelse)
            elif isinstance(node, (ast.For, ast.While)):
                _check_body(node.body)
                _check_body(node.orelse)
            elif isinstance(node, ast.Try):
                _check_body(node.body)
                for handler in node.handlers:
                    _check_body(handler.body)
                _check_body(node.orelse)
                _check_body(node.finalbody)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Don’t drill into nested function definitions here; they have their own scope.
                pass
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                _check_body(node.body)

    # Check module-level code
    _check_body(tree.body)

    # Also check inside each function definition
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _check_body(node.body)

    return issues


def check_string_concat_in_loop(tree: ast.AST) -> List[str]:
    """
    Detect string concatenation within loops: patterns like 's = s + ...' or 's += ...'.
    Suggest using ''.join() or other efficient methods instead of repeated concatenation.
    """
    issues: List[str] = []

    class ConcatVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev_in_loop = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev_in_loop

        def visit_While(self, node: ast.While):
            prev_in_loop = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev_in_loop

        def visit_Assign(self, node: ast.Assign):
            if self.in_loop and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                target = node.targets[0].id
                value = node.value
                if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add):
                    left = value.left
                    if isinstance(left, ast.Name) and left.id == target:
                        issues.append(
                            format_optimization_warning(
                                f"String concatenation in loop for '{target}'. "
                                "Consider using ''.join() or appending to a list and joining outside the loop.",
                                node.lineno
                            )
                        )
            self.generic_visit(node)

        def visit_AugAssign(self, node: ast.AugAssign):
            if self.in_loop and isinstance(node.op, ast.Add) and isinstance(node.target, ast.Name):
                issues.append(
                    format_optimization_warning(
                        f"Augmented assignment '{node.target.id} += ...' in loop. "
                        "Consider using ''.join() or appending to a list and joining outside the loop.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    ConcatVisitor().visit(tree)
    return issues


def check_len_call_in_loop(tree: ast.AST) -> List[str]:
    """
    Detect calls to len() inside loops, which may result in repeated length computations.
    Suggest storing the length in a variable before the loop.
    """
    issues: List[str] = []

    class LenVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev_in_loop = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev_in_loop

        def visit_While(self, node: ast.While):
            prev_in_loop = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev_in_loop

        def visit_Call(self, node: ast.Call):
            if self.in_loop and isinstance(node.func, ast.Name) and node.func.id == "len":
                issues.append(
                    format_optimization_warning(
                        "Call to len() inside loop. "
                        "Consider storing the length in a variable before the loop.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    LenVisitor().visit(tree)
    return issues


def check_range_len_pattern(tree: ast.AST) -> List[str]:
    """
    Detect loops of the form 'for i in range(len(seq))' and suggest using 'for i, value in enumerate(seq)'.
    """
    issues: List[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            iter_node = node.iter
            if (
                isinstance(iter_node, ast.Call)
                and isinstance(iter_node.func, ast.Name)
                and iter_node.func.id == "range"
            ):
                args = iter_node.args
                if len(args) == 1 and isinstance(args[0], ast.Call):
                    inner = args[0]
                    if isinstance(inner.func, ast.Name) and inner.func.id == "len":
                        issues.append(
                            format_optimization_warning(
                                "Loop over 'range(len(...))'. "
                                "Consider using 'enumerate()' to iterate directly over the sequence.",
                                node.lineno
                            )
                        )
    return issues


def check_append_in_loop(tree: ast.AST) -> List[str]:
    """
    Detect using list.append() inside loops and suggest using list comprehensions for building lists.
    """
    issues: List[str] = []

    class AppendVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev_in_loop = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev_in_loop

        def visit_While(self, node: ast.While):
            prev_in_loop = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev_in_loop

        def visit_Call(self, node: ast.Call):
            if (
                self.in_loop
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "append"
            ):
                issues.append(
                    format_optimization_warning(
                        "Using list.append() inside a loop. "
                        "Consider using a list comprehension for better performance.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    AppendVisitor().visit(tree)
    return issues


def check_unused_variables(tree: ast.AST) -> List[str]:
    """
    Find all variable names assigned to (including in Assign, AnnAssign, For-loop targets,
    With as-targets, etc.) and then check if any of those variables are never used elsewhere
    (in a Load context). Returns a list of warning messages for each unused variable.
    """
    issues: List[str] = []
    assigned_names: Dict[str, int] = {}

    # 1) Collect all assigned names and their first lineno
    class AssignVisitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign):
            for target in node.targets:
                _collect_target(target, node.lineno)
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

    def _collect_target(target_node: ast.AST, lineno: int):
        """
        Helper to collect names from assignment targets, including tuples/lists.
        """
        if isinstance(target_node, ast.Name):
            name = target_node.id
            if name not in assigned_names:
                assigned_names[name] = lineno
        elif isinstance(target_node, (ast.Tuple, ast.List)):
            for elt in target_node.elts:
                _collect_target(elt, lineno)
        # Ignore other target types (attributes, subscripts, etc.)

    AssignVisitor().visit(tree)

    # 2) Walk tree to see which names are actually used (Load contexts)
    used_names: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_names.add(node.id)

    # 3) Variables assigned but never used
    for name, lineno in assigned_names.items():
        if name not in used_names and not name.startswith("_"):
            issues.append(
                format_optimization_warning(
                    f"Variable '{name}' is assigned but never used.",
                    lineno
                )
            )

    return issues


# --------------------------------------------
# Additional High-Impact Checks
# --------------------------------------------

def check_dict_comprehension(tree: ast.AST) -> List[str]:
    """
    Detect patterns where a dict is built via a loop with repeated assignments like:
        d = {}
        for k, v in iterable:
            d[k] = transform(v)
    and suggest using a dict comprehension instead.
    We simply flag any assignment to d[...] inside a loop, because that is often convertible.
    """
    issues: List[str] = []

    class DictCompVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_While(self, node: ast.While):
            prev = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_Assign(self, node: ast.Assign):
            if self.in_loop and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                    dict_name = target.value.id
                    issues.append(
                        format_optimization_warning(
                            f"Building dict '{dict_name}' via loop assignment. "
                            "Consider using a dict comprehension.",
                            node.lineno
                        )
                    )
            self.generic_visit(node)

    DictCompVisitor().visit(tree)
    return issues


def check_set_comprehension(tree: ast.AST) -> List[str]:
    """
    Detect patterns where a set is built via a loop with repeated add() calls:
        s = set()
        for x in iterable:
            if cond(x):
                s.add(transform(x))
    and suggest using a set comprehension instead.
    """
    issues: List[str] = []

    class SetCompVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_While(self, node: ast.While):
            prev = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_Call(self, node: ast.Call):
            if (
                self.in_loop
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add"
                and isinstance(node.func.value, ast.Name)
            ):
                set_name = node.func.value.id
                issues.append(
                    format_optimization_warning(
                        f"Building set '{set_name}' via add() in a loop. "
                        "Consider using a set comprehension.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    SetCompVisitor().visit(tree)
    return issues


def check_genexpr_vs_list(tree: ast.AST) -> List[str]:
    """
    Detect uses of sum(), any(), all(), max(), min() where the argument is a list comprehension,
    e.g., sum([f(x) for x in data]) and suggest using a generator expression instead.
    """
    issues: List[str] = []

    GENFUNCS = {"sum", "any", "all", "max", "min"}

    class GenExprVisitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            # Check if function is one of GENFUNCS
            if isinstance(node.func, ast.Name) and node.func.id in GENFUNCS:
                if node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.ListComp):
                        func_name = node.func.id
                        issues.append(
                            format_optimization_warning(
                                f"{func_name}() applied to a list comprehension. "
                                "Consider using a generator expression (remove the brackets) for better memory efficiency.",
                                node.lineno
                            )
                        )
            self.generic_visit(node)

    GenExprVisitor().visit(tree)
    return issues


def check_membership_on_list_in_loop(tree: ast.AST) -> List[str]:
    """
    Detect 'x in y' checks inside loops where y is a list name, and suggest converting y to a set
    if membership tests are frequent.
    We flag any Compare with 'In' or 'NotIn' inside loops where the comparator is a Name.
    """
    issues: List[str] = []

    class MembershipVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_loop = False

        def visit_For(self, node: ast.For):
            prev = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_While(self, node: ast.While):
            prev = self.in_loop
            self.in_loop = True
            self.generic_visit(node)
            self.in_loop = prev

        def visit_Compare(self, node: ast.Compare):
            if self.in_loop:
                # If 'in' or 'not in' is used
                for op in node.ops:
                    if isinstance(op, (ast.In, ast.NotIn)):
                        for comp in node.comparators:
                            if isinstance(comp, ast.Name):
                                list_name = comp.id
                                issues.append(
                                    format_optimization_warning(
                                        f"Membership test '{ast.unparse(node)}' inside a loop. "
                                        f"If '{list_name}' is a large list, consider converting it to a set for faster lookups.",
                                        node.lineno
                                    )
                                )
            self.generic_visit(node)

    MembershipVisitor().visit(tree)
    return issues


def check_open_without_context(tree: ast.AST) -> List[str]:
    """
    Detect calls to open() that are not within a 'with' context manager. Suggest using
    'with open(...) as f' to ensure proper resource cleanup and potentially better performance.
    """
    issues: List[str] = []

    class OpenVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_with = False

        def visit_With(self, node: ast.With):
            prev = self.in_with
            self.in_with = True
            self.generic_visit(node)
            self.in_with = prev

        def visit_AsyncWith(self, node: ast.AsyncWith):
            prev = self.in_with
            self.in_with = True
            self.generic_visit(node)
            self.in_with = prev

        def visit_Call(self, node: ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open" and not self.in_with:
                issues.append(
                    format_optimization_warning(
                        "Use of open() outside of a 'with' context manager. "
                        "Consider using 'with open(...) as f:' for better resource management.",
                        node.lineno
                    )
                )
            self.generic_visit(node)

    OpenVisitor().visit(tree)
    return issues


# --------------------------------------------
# Combined Runner
# --------------------------------------------

def run_all_optimization_checks(source_code: str) -> List[str]:
    """
    Parse the source code into an AST and run all optimization checks, including:
      - Unused imports
      - Unreachable code
      - String concatenation in loops
      - len() calls in loops
      - range(len(...)) patterns
      - append() in loops
      - Unused variables
      - Dict construction via loops
      - Set construction via loops
      - sum/any/all/max/min on list comprehensions
      - Membership tests on lists inside loops
      - open() without context managers

    Returns a combined list of all warning messages (deduplicated and sorted).
    """
    tree = ast.parse(source_code)
    issues: List[str] = []

    # Core checks
    issues.extend(check_unused_imports(tree))
    issues.extend(check_unreachable_code(tree))
    issues.extend(check_string_concat_in_loop(tree))
    issues.extend(check_len_call_in_loop(tree))
    issues.extend(check_range_len_pattern(tree))
    issues.extend(check_append_in_loop(tree))
    issues.extend(check_unused_variables(tree))

    # Additional high-impact checks
    issues.extend(check_dict_comprehension(tree))
    issues.extend(check_set_comprehension(tree))
    issues.extend(check_genexpr_vs_list(tree))
    issues.extend(check_membership_on_list_in_loop(tree))
    issues.extend(check_open_without_context(tree))

    # Deduplicate and sort for consistent output
    return sorted(set(issues))
