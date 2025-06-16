import os
import ast
from typing import List, Tuple
import importlib.resources


def extract_string_from_node(node) -> str:
    """Extract string from Constant, JoinedStr, or BinOp nodes."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    elif isinstance(node, ast.JoinedStr):
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                parts.append("{...}")
        return "".join(parts)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        left_str = extract_string_from_node(node.left)
        if left_str:
            return left_str.replace('%s', '{...}').replace('%d', '{...}')
    return ""

def extract_function_info(file_path: str) -> List[Tuple[str, str]]:
    """
    Parses a Python file and extracts warnings from specific function calls.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return []

    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for inner_node in ast.walk(node):
                if isinstance(inner_node, ast.Call) and \
                   isinstance(inner_node.func, ast.Name) and \
                   inner_node.func.id in ("format_optimization_warning", "format_security_warning"):
                    if inner_node.args:
                        first_arg = inner_node.args[0]
                        warning = extract_string_from_node(first_arg)
                        if warning:
                            
                            results.append(('', warning))
    return results


def find_rule_files() -> List[str]:
    """
    Scans the package's internal rule directories for Python rule files
    and returns a list of the unique, sorted file names found.

    This version uses importlib.resources to be compatible with installed
    packages and is not dependent on the current working directory.
    """
    found_files = set()
    
    # Define the target packages based on your project structure.
    # These are the Python import paths to your rule directories.
    RULES_PACKAGES = [
        "pyward.optimization.rules",
        "pyward.security.rules"
    ]

    for package_path in RULES_PACKAGES:
        try:
            # Get a reference to the package resource
            package_files = importlib.resources.files(package_path)
        except ModuleNotFoundError:
            print(f"Warning: Could not find the rules package '{package_path}'. Skipping.")
            continue

        # Find all .py files within the package.
        # Use glob('*.py') since your rules are not in further subdirectories.
        for rule_file_resource in package_files.glob('*.py'):
            # Skip the __init__.py files as they are not rules.
            if rule_file_resource.name == '__init__.py':
                continue

            if not rule_file_resource.is_file():
                continue

            # Use 'as_file' to get a temporary, concrete file path on disk
            # that our existing extract_function_info function can read.
            with importlib.resources.as_file(rule_file_resource) as file_path:
                # Check if the file contains the warning functions we care about.
                if extract_function_info(str(file_path)):
                    found_files.add(rule_file_resource.name)

    if not found_files:
        print("No rule files found to process.")
        return []

    # Return a sorted list of unique file names
    return sorted(list(found_files))


# This block is for testing this file directly.
if __name__ == "__main__":
    print("Running rule finder script directly...")
    # To test this, run `python -m pyward.rule_finder` (or wherever this file is)
    # from the root of your project `karanlvm-pyward/`.
    rule_files = find_rule_files()
    if rule_files:
        print("\nDiscovered Rule Files:")
        for rule_file in rule_files:
            print(f"- {rule_file}")