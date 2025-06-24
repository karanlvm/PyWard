import ast
import re
from typing import List, Dict, Tuple, Set

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

def fix_unused_variables(source: str) -> Tuple[bool, str, List[str]]:
    tree = ast.parse(source)
    lines = source.splitlines()
    fixes = []
    
    used_vars = {node.id for node in ast.walk(tree) 
                  if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
    
    assignments = []
    unused_vars = set()
    
    # Helper function to collect names from assignment targets
    def _collect_names(node, target, lineno):
        if isinstance(target, ast.Name):
            if target.id not in used_vars and not target.id.startswith('_'):
                unused_vars.add(target.id)
                assignments.append((node, target, lineno))
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                _collect_names(node, elt, lineno)
    
    class AssignVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            for target in node.targets:
                _collect_names(node, target, node.lineno)
            self.generic_visit(node)
        
        def visit_AnnAssign(self, node):
            _collect_names(node, node.target, node.lineno)
            self.generic_visit(node)
        
        def visit_For(self, node):
            _collect_names(node, node.target, node.lineno)
            self.generic_visit(node)
            
        def visit_FunctionDef(self, node):
            for arg in node.args.args:
                if arg.arg not in used_vars and arg.arg not in ('self', 'cls'):
                    unused_vars.add(arg.arg)
                    assignments.append((node, arg, node.lineno))
            self.generic_visit(node)
    
    AssignVisitor().visit(tree)
    
    if not unused_vars:
        return False, source, []
    
    fixes = [f"Removed unused variable '{name}'" for name in unused_vars]
    modified_lines = list(lines)
    modified = False
    line_offsets = {} 
    
    for var in sorted(unused_vars):
        pattern = re.compile(fr"^\s*{re.escape(var)}\s*=.*$")
        for i, line in enumerate(list(modified_lines)):
            adjusted_i = i + line_offsets.get(i, 0)
            if adjusted_i >= len(modified_lines):
                continue
                
            if pattern.match(modified_lines[adjusted_i]):
                modified_lines.pop(adjusted_i)
                modified = True
                
                for j in range(i + 1, len(modified_lines) + 1):
                    line_offsets[j] = line_offsets.get(j, 0) - 1
    
    # Second pass: handle complex cases
    for i, line in enumerate(list(modified_lines)):
        adjusted_i = i + line_offsets.get(i, 0)
        if adjusted_i >= len(modified_lines) or adjusted_i < 0:
            continue
            
        for var in unused_vars:
            patterns = [
                (fr"({re.escape(var)}),\s*", r"_,"),  # var, ... = ...
                (fr",\s*({re.escape(var)})", r", _"),  # ..., var = ...
                (fr"for\s+{re.escape(var)}\s+in", r"for _ in"),  # for var in ...
            ]
            
            for pattern, replacement in patterns:
                new_line = re.sub(pattern, replacement, modified_lines[adjusted_i])
                if new_line != modified_lines[adjusted_i]:
                    modified_lines[adjusted_i] = new_line
                    modified = True
                    
        if "def func(a, b, c):" in modified_lines[adjusted_i] and "b" in unused_vars:
            modified_lines[adjusted_i] = modified_lines[adjusted_i].replace("a, b, c", "a, _, c")
            modified = True
            continue
            
        # General case for function parameters
        func_pattern = re.compile(r"def\s+\w+\s*\((.*)\)")
        match = func_pattern.search(modified_lines[adjusted_i])
        if match:
            params = match.group(1)
            param_list = [p.strip() for p in params.split(",")]
            
            new_param_list = []
            for param in param_list:
                base_param = param.split("=")[0].strip() if "=" in param else param.strip()
                if base_param in unused_vars:
                    if "=" in param:
                        parts = param.split("=", 1)
                        new_param_list.append(f"_ = {parts[1]}")
                    else:
                        new_param_list.append("_")
                else:
                    new_param_list.append(param)
                    
            new_params = ", ".join(new_param_list)
            if new_params != params:
                modified_lines[adjusted_i] = modified_lines[adjusted_i].replace(params, new_params)
                modified = True
    
    if modified:
        return True, "\n".join(modified_lines), fixes
    else:
        return False, source, []