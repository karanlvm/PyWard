import os
import ast
import pandas as pd
from typing import List, Tuple
import importlib.resources
from pathlib import Path
import sys

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

def extract_function_info_from_content(content: str, file_name: str) -> List[Tuple[str, str]]:
    """Extract function info from file content string."""
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"Syntax error in {file_name}: {e}")
        return []
    
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            for inner_node in ast.walk(node):
                if isinstance(inner_node, ast.Call) and isinstance(inner_node.func, ast.Name) and inner_node.func.id in ("format_optimization_warning", "format_security_warning"):
                    if inner_node.args:
                        first_arg = inner_node.args[0]
                        warning = extract_string_from_node(first_arg)
                        if warning:
                            results.append((function_name, warning))
    return results

def extract_function_info(file_path: str) -> List[Tuple[str, str]]:
    """Extract function info from file path (legacy function for development)."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return extract_function_info_from_content(content, file_path)

def scan_package_rules(package_name: str) -> List[str]:
    """Scan rules from installed package using importlib.resources."""
    rule_files = []
    
    try:
        # Try to access the main package rules
        if importlib.resources.is_resource(package_name, '__init__.py'):
            package_files = importlib.resources.contents(package_name)
            for file_name in package_files:
                if file_name.endswith('.py') and file_name != '__init__.py':
                    try:
                        content = importlib.resources.read_text(package_name, file_name)
                        if extract_function_info_from_content(content, file_name):
                            rule_files.append(file_name)
                    except Exception as e:
                        print(f"Could not read {file_name}: {e}")
        
        # Try to access rules subdirectory
        rules_package = f"{package_name}.rules"
        try:
            rules_files = importlib.resources.contents(rules_package)
            for file_name in rules_files:
                if file_name.endswith('.py') and file_name != '__init__.py':
                    try:
                        content = importlib.resources.read_text(rules_package, file_name)
                        if extract_function_info_from_content(content, file_name):
                            rule_files.append(file_name)
                    except Exception as e:
                        print(f"Could not read {file_name} from rules: {e}")
        except (ImportError, FileNotFoundError):
            # Rules subdirectory doesn't exist
            pass
            
    except (ImportError, FileNotFoundError):
        print(f"Package {package_name} not found")
        
    return rule_files

def process_directory(directory_path: str) -> pd.DataFrame:
    """Process directory for development/local usage."""
    data = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if extract_function_info(file_path):
                    data.append({'File': file})
    return pd.DataFrame(data, columns=['File'])

def find_rule_files(package_name: str = None) -> List[str]:
    """
    Scans for Python rule files and returns a list of unique file names.
    
    Args:
        package_name: Name of the package to scan. If None, tries to detect
                     or falls back to local directory scanning.
    """
    # If package_name is provided, use it
    if package_name:
        return scan_package_rules(package_name)
    
    # Try to detect if we're running from an installed package
    # Check if we're in site-packages or similar
    current_file = Path(__file__).resolve()
    if 'site-packages' in str(current_file) or 'dist-packages' in str(current_file):
        # Try to infer package name from the path
        parts = current_file.parts
        try:
            site_packages_idx = next(i for i, part in enumerate(parts) if 'packages' in part)
            if site_packages_idx + 1 < len(parts):
                inferred_package = parts[site_packages_idx + 1]
                print(f"Detected installed package: {inferred_package}")
                return scan_package_rules(inferred_package)
        except (StopIteration, IndexError):
            pass
    
    # Fall back to local directory scanning (development mode)
    print("Using local directory scanning (development mode)")
    base_dir = os.getcwd()
    
    # Check if we can find a setup.py or pyproject.toml to infer package structure
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    dirs_to_process = []
    
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        dirs_to_process.append(subdir_path)
        rules_path = os.path.join(subdir_path, 'rules')
        if os.path.exists(rules_path) and os.path.isdir(rules_path):
            dirs_to_process.append(rules_path)
    
    all_data = []
    for directory_path in dirs_to_process:
        df = process_directory(directory_path)
        if not df.empty:
            all_data.append(df)
    
    if not all_data:
        print("No rule files found to process.")
        return []
    
    # Combine DataFrames to find unique files
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.drop_duplicates(subset='File', keep='first').sort_values(by='File')
    
    return final_df['File'].tolist()

# For your CLI integration
def get_available_rules(package_name: str = 'pyward') -> List[str]:
    """
    Public API function to get available rules.
    
    Args:
        package_name: The name of your package (default: 'pyward')
    """
    return find_rule_files(package_name)

# This block is for testing `rule_finder.py` directly.
if __name__ == "__main__":
    print("Running rule finder script directly...")
    
    # You can test with explicit package name
    rule_files = find_rule_files('optimization')  # Replace with your actual package name
    
    # Or let it auto-detect
    # rule_files = find_rule_files()
    
    if rule_files:
        print(f"\nDiscovered {len(rule_files)} Rule Files:")
        for i, rule_file in enumerate(rule_files, 1):
            print(f"{i:2d}. {rule_file}")
    else:
        print("No rule files found.")