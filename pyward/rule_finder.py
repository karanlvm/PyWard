import os
import ast
import pandas as pd
from typing import List, Tuple

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
            function_name = node.name
            for inner_node in ast.walk(node):
                if isinstance(inner_node, ast.Call) and isinstance(inner_node.func, ast.Name) and inner_node.func.id in ("format_optimization_warning", "format_security_warning"):
                    if inner_node.args:
                        first_arg = inner_node.args[0]
                        warning = extract_string_from_node(first_arg)
                        if warning:
                            results.append((function_name, warning))
    return results

def process_directory(directory_path: str) -> pd.DataFrame:
    data = []
    rules_path = os.path.join(directory_path)
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if extract_function_info(file_path):
                     data.append({'File': file})
    df = pd.DataFrame(data, columns=['File'])
    return df


# MODIFIED FUNCTION: This no longer saves a CSV.
def find_rule_files() -> List[str]:
    """
    Scans directories for Python rule files and returns a list of the
    unique file names found.
    """
    base_dir = os.getcwd()
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

    # Combine DataFrames in memory to find unique files
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.drop_duplicates(subset='File', keep='first').sort_values(by='File')
    
    # Return the list of file names directly
    return final_df['File'].tolist()


# This block is for testing `rule_finder.py` directly.
if __name__ == "__main__":
    print("Running rule finder script directly...")
    rule_files = find_rule_files()
    if rule_files:
        print("\nDiscovered Rule Files:")
        print(rule_files)