import ast
from fileinput import lineno
from os import name
from typing import List, Set, Tuple, Dict, Optional
from pyward.format.formatter import format_optimization_warning
from dataclasses import dataclass, field


@dataclass
class ImportInfo:
    """Information about an import statement."""
    node: ast.AST
    alias_name_pairs: List[Tuple[Optional[str], str]]
    lineno: int
    col_offset: int
    end_lineno: int
    end_col_offset: int
    is_from: bool = False
    module: Optional[str] = None
    names_in_use: List[Tuple[str, str]] = field(default_factory=list)
    names_unused: List[Tuple[str, str]] = field(default_factory=list)

    def __eq__(self, value: object) -> bool:
        """eq for the same object"""
        return value == self
    
    def __hash__(self) -> int:
        """same object with same hash value"""
        return hash((self.lineno, self.col_offset, self.end_lineno, self.end_col_offset))

def collect_imports(tree: ast.AST) -> List[ImportInfo]:
    imports: List[ImportInfo] = list()
    name_to_import: Dict[Tuple[str, str], ImportInfo] = dict()

    for node in ast.walk(tree):
        if (not isinstance(node, ast.Import)) and (not isinstance(node, ast.ImportFrom)):
            continue
        import_info = ImportInfo(
            node = node,
            alias_name_pairs = [(alias.asname, alias.name) for alias in node.names],
            lineno = node.lineno,
            col_offset = node.col_offset,
            end_lineno = node.end_lineno,
            end_col_offset = node.end_col_offset,
        )
        if (isinstance(node, ast.ImportFrom)):
            import_info.is_from = True
            import_info.module = node.module

        imports.append(import_info)
        for alias in node.names:
            name_to_import[(alias.asname, alias.name)] = import_info

    if not name_to_import:
        return imports

    used_names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for name, import_info in name_to_import.items():
        if (name[0] if name[0] else name[1]) in used_names:
            import_info.names_in_use.append(name)
        else:
            import_info.names_unused.append(name)

    return imports

def check_unused_imports(tree: ast.AST) -> List[str]:
    issues: List[str] = []
    imports: List[ImportInfo] = collect_imports(tree)

    for import_info in imports:
        for unused_name in import_info.names_unused:
            issues.append(
                format_optimization_warning(
                    f"Imported name '{unused_name[1] + ' as ' + unused_name[0] if unused_name[0] else unused_name[1]}' is never used.",
                    import_info.lineno
                )
            )
    return issues


def fix_unused_imports(source: str) -> Tuple[bool, str, List[str]]:
    imports: List[ImportInfo] = collect_imports(ast.parse(source))

    def get_msg(name: Tuple[str, str], item: ImportInfo) -> str:
        return f"from {item.module} import {name[1] + ' as ' + name[0] if name[0] else name[1]} deleted" \
            if item.is_from else f"import {name[1] + ' as ' + name[0] if name[0] else name[1]} deleted"

    fixes = [get_msg(name, item) for item in imports for name in item.names_unused]

    if not fixes:
        return (False, source, [])    

    return (True, __fix_unused_imports(source, imports), fixes)


def __fix_unused_imports(source: str, imports: List[ImportInfo]) -> str:
    line_to_import: Dict[int, List[ImportInfo]] = dict()
    for import_info in imports:
        if not import_info.names_unused:
            continue
        for line_no in range(import_info.lineno, import_info.end_lineno + 1):
            line_to_import.setdefault(line_no, list()).append(import_info)

    lines: List[str] = source.splitlines()
    new_lines: List[str] = []

    for line_no, line in enumerate(lines, start=1):
        imports_to_fix: List[ImportInfo] = line_to_import.get(line_no, [])
        if not imports_to_fix:
            new_lines.append(line)
            continue
        
        new_line: str = ""
        prev_import_range: Optional[Tuple[int, int]] = None
        for import_info in imports_to_fix:
            range_pair: Tuple[int, int] = get_range(import_info, line_no, line)
            if not prev_import_range:
                new_line += line[0: range_pair[0]]
            else:
                new_line += line[prev_import_range[1]: range_pair[0]]
            prev_import_range = range_pair
            new_line += generate_import_clause(line_no, import_info)

        if ((line == "") or (new_line != "")):
            new_lines.append(new_line)

    return "\n".join(new_lines) + "\n"

def get_range(import_info: ImportInfo, line_no: int, line: str) -> Tuple[int, int]:
    """Get the range of the import statement in current line."""
    start_lineno = import_info.lineno
    end_lineno = import_info.end_lineno
    if start_lineno == end_lineno:
        return (import_info.col_offset, import_info.end_col_offset)

    if start_lineno == line_no:
        return (import_info.col_offset, len(line))
    elif end_lineno == line_no:
        return (0, import_info.end_col_offset)
    else:
        return (0, len(line))

def generate_import_clause(line_no: int, import_info: ImportInfo) -> str:
    """Generate the import clause for the given import info."""
    if line_no != import_info.lineno:
        return ""
    if not import_info.names_in_use:
        return ""
    if import_info.is_from:
        if import_info.lineno == import_info.end_lineno:
            return f"from {import_info.module} import {', '.join([name[1] + ' as ' + name[0] if name[0] else name[1] for name in import_info.names_in_use])}"
        else:
            new_line = '\n'
            trailing = ',\n    '
            return f"from {import_info.module} import ({new_line}    {trailing.join([name[1] + ' as ' + name[0] if name[0] else name[1] for name in import_info.names_in_use])}{new_line})"
    else:
        return f"import {', '.join([name[1] + ' as ' + name[0] if name[0] else name[1] for name in import_info.names_in_use])}"
