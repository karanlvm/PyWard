import ast
from typing import List, Optional, Tuple, Set, Dict
import re
from dataclasses import dataclass

@dataclass
class ImportInfo:
    """Information about an import statement."""
    node: ast.AST
    names: List[str]
    aliases: Dict[str, str]
    lineno: int
    end_lineno: Optional[int]  # For multiline imports
    is_from: bool
    module: Optional[str] = None
    level: int = 0

class ImportFixer:
    """Fixes unused imports by removing them from the source code."""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.parsed_source = self._preprocess_source(source_code)
        self.tree = ast.parse(self.parsed_source)
        self.unused_names: Set[str] = set()  
        self.imports: Dict[int, ImportInfo] = {}  
        self.lines = self.source_code.splitlines()
        self._collect_imports()
        self._find_unused_imports()

    def _preprocess_source(self, source: str) -> str:
        """Convert trailing comma imports to valid syntax for parsing."""
        lines = source.splitlines()
        result = []
        for line in lines:
            if not line.strip().startswith('from') and not line.strip().startswith('import'):
                result.append(line)
                continue
                
            if '(' in line: 
                result.append(line)
                continue

            if line.rstrip().endswith(','):
                if line.strip().startswith('from'):
                    result.append(re.sub(r'import\s+(.+?),\s*$', r'import (\1)', line))
                else:
                    result.append(re.sub(r'import\s+(.+?),\s*$', r'import (\1)', line))
            else:
                result.append(line)
        return '\n'.join(result)

    def _find_multiline_import_end(self, start_line: int) -> Optional[int]:
        """Find the end line of a multiline import."""
        if '(' not in self.lines[start_line - 1]:
            return None
            
        level = 0
        for i, line in enumerate(self.lines[start_line - 1:], start=start_line):
            level += line.count('(') - line.count(')')
            if level == 0:
                return i
        return None

    def _collect_imports(self) -> None:
        """Collect all import statements and their information."""
        for node in ast.walk(self.tree):
            if not hasattr(node, 'lineno'):
                continue

            end_lineno = self._find_multiline_import_end(node.lineno)
            if isinstance(node, ast.Import):
                names = []
                aliases = {}
                for alias in node.names:
                    base_name = alias.name.split(".")[0]
                    names.append(base_name)
                    if alias.asname:
                        aliases[base_name] = alias.asname
                
                self.imports[node.lineno] = ImportInfo(
                    node=node,
                    names=names,
                    aliases=aliases,
                    lineno=node.lineno,
                    end_lineno=end_lineno,
                    is_from=False
                )

            elif isinstance(node, ast.ImportFrom):
                names = []
                aliases = {}
                for alias in node.names:
                    names.append(alias.name)
                    if alias.asname:
                        aliases[alias.name] = alias.asname
                
                self.imports[node.lineno] = ImportInfo(
                    node=node,
                    names=names,
                    aliases=aliases,
                    lineno=node.lineno,
                    end_lineno=end_lineno,
                    is_from=True,
                    module=node.module,
                    level=node.level
                )

    def _find_unused_imports(self) -> None:
        """Find which imported names are never used."""
        used_names = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        for info in self.imports.values():
            for name in info.names:
                alias = info.aliases.get(name, name)
                if alias not in used_names:
                    self.unused_names.add(name)

    def _fix_multiline_import(self, info: ImportInfo) -> List[str]:
        """Fix a multiline import statement while preserving formatting."""
        if not info.end_lineno:
            return []

        original_lines = self.lines[info.lineno - 1:info.end_lineno]
        result = []
        header = original_lines[0] 
        result.append(header)

        used_names = set(n for n in info.names if n not in self.unused_names)
        
        for line in original_lines[1:-1]:  
            stripped = line.strip()
            if not stripped:  
                result.append(line)
                continue
            
            if stripped.startswith('#'): 
                result.append(line)
                continue
        
            parts = line.rstrip().split('#', 1)
            code_part = parts[0].rstrip()
            comment_part = f"  # {parts[1].strip()}" if len(parts) > 1 else ""
            
            indentation = line[:len(line) - len(line.lstrip())]
            
            name = code_part.strip().rstrip(',').strip()
            
            if name in used_names:
                result.append(f"{indentation}{name}{',' if code_part.rstrip().endswith(',') else ''}{comment_part}")
        
        result.append(original_lines[-1]) 
        return result

    def _fix_simple_import(self, info: ImportInfo) -> Optional[str]:
        """Fix a single-line import statement."""
        used_names = [n for n in info.names if n not in self.unused_names]
        
        if not used_names:
            return None
            
        if info.is_from:
            names_str = ", ".join(
                f"{name} as {info.aliases[name]}" if name in info.aliases else name
                for name in used_names
            )
            return f"from {info.module} import {names_str}"
        else:
            names_str = ", ".join(
                f"{name} as {info.aliases[name]}" if name in info.aliases else name
                for name in used_names
            )
            return f"import {names_str}"

    def fix(self) -> str:
        """Apply fixes and return the modified source code."""
        if not self.unused_names:
            return self.source_code

        result_lines = self.lines.copy()
        
        for lineno in sorted(self.imports.keys(), reverse=True):
            info = self.imports[lineno]
            
            if all(name in self.unused_names for name in info.names):
                if info.end_lineno:
                    del result_lines[info.lineno - 1:info.end_lineno]
                else:
                    del result_lines[info.lineno - 1]
                continue

            if not any(name in self.unused_names for name in info.names):
                continue

            if info.end_lineno:
                fixed_lines = self._fix_multiline_import(info)
                result_lines[info.lineno - 1:info.end_lineno] = fixed_lines
            else:
                fixed = self._fix_simple_import(info)
                if fixed:
                    result_lines[info.lineno - 1] = fixed

        return "\n".join(result_lines) + "\n"


def fix_file(filepath: str, write: bool = False) -> Optional[str]:
    """
    Fix unused imports in the given file.
    If write=True, overwrites the original file, otherwise returns the fixed content.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    fixer = ImportFixer(source)
    fixed = fixer.fix()

    if write:
        if fixed != source:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fixed)
        return None
    return fixed