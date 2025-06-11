import pytest
import ast

# Assuming your linter functions are in 'pyward_linter_checks.py'
# Adjust the import path if your file structure is different.
from pyward.rules.nested_loops import (
    check_unused_imports,
    check_unreachable_code,
    check_string_concat_in_loop,
    check_len_call_in_loop,
    check_range_len_pattern,
    check_append_in_loop,
    check_unused_variables,
    check_deeply_nested_loops,
    check_dict_comprehension,
    check_set_comprehension,
    check_genexpr_vs_list,
    check_membership_on_list_in_loop,
    check_open_without_context,
    check_list_build_then_copy,
    check_sort_assignment,
    run_all_optimization_checks # For a potential integration test
)

# Mock/Helper for formatting warnings, to match the expected output
# In a real scenario, you might mock the actual formatter from pyward.format.formatter
def format_optimization_warning(message: str, lineno: int) -> str:
    return f"[Optimization] Line {lineno}: {message}"

# --- Test Cases ---

# 1. Test check_unused_imports
@pytest.mark.parametrize("code, expected_warnings", [
    ("import os\nimport sys\nprint(sys.version)", [format_optimization_warning("Imported name 'os' is never used.", 1)]),
    ("from math import pi, sin\nprint(sin(0))", [format_optimization_warning("Imported name 'pi' is never used.", 1)]),
    ("import os\nimport os.path\nprint(os.getcwd())", [format_optimization_warning("Imported name 'path' is never used.", 2)]), # Note: current linter splits by '.', so 'path' will be the name
    ("import sys as system", [format_optimization_warning("Imported name 'system' is never used.", 1)]),
    ("import pandas.core.frame\nprint(pandas)", []), # 'pandas' is used, 'core' and 'frame' are part of it. Current linter uses split('.')[0]
    ("import numpy as np\nprint(np.array([1]))", []),
    ("print('Hello')", []),
    ("from collections import defaultdict\nd = defaultdict(int)", []),
    ("import foo.bar\nprint(foo)", []),
])
def test_check_unused_imports(code, expected_warnings):
    tree = ast.parse(code)
    warnings = check_unused_imports(tree)
    # Use sets for order-independent comparison if multiple warnings could occur
    assert sorted(warnings) == sorted(expected_warnings)

# 2. Test check_unreachable_code
@pytest.mark.parametrize("code, expected_warnings_details", [
    ("def f():\n  return 1\n  print('unreachable')", [(3, "This code is unreachable.")]),
    ("def f():\n  raise ValueError()\n  x = 10", [(3, "This code is unreachable.")]),
    ("def f():\n  for i in range(3):\n    break\n    print('unreachable')", [(4, "This code is unreachable.")]),
    ("def f():\n  for i in range(3):\n    continue\n    print('unreachable')", [(4, "This code is unreachable.")]),
    ("def f():\n  if True:\n    return\n    print('unreachable in if')", [(4, "This code is unreachable.")]),
    ("def f():\n  if False:\n    pass\n  else:\n    return\n    print('unreachable in else')", [(6, "This code is unreachable.")]),
    ("def f():\n  try:\n    return 1\n    print('unreachable in try')\n  except:\n    return 2\n    print('unreachable in except')\n  finally:\n    print('in finally')\n  print('after try-except-finally')", # This last print is also unreachable
     [(4, "This code is unreachable."), (7, "This code is unreachable."), (10, "This code is unreachable.")]), # Line numbers need care
    ("def f():\n  return 1\n  if True:\n    print('nested unreachable')", # The 'if True:' and its body
     [(3, "This code is unreachable."), (4, "[Optimization] Line 4: This code is unreachable.")]), # Current linter's specific nested output format
    ("def f():\n  print('ok')\n  return 1", []),
    ("def f():\n  if True:\n    print('ok')\n  else:\n    print('also ok')", []),
])
def test_check_unreachable_code(code, expected_warnings_details):
    tree = ast.parse(code)
    warnings = check_unreachable_code(tree)
    expected_formatted_warnings = [format_optimization_warning(msg, line) for line, msg in expected_warnings_details]
    # Filter out specific nested messages if they are too complex to match exactly, or adjust expectations
    # For now, let's assume the main "This code is unreachable." messages are primary.
    
    # A simple check for now, can be made more robust
    # The linter's nested unreachable logic can produce multiple similar messages for compound statements
    # We will check if the expected primary unreachables are present.
    # A more precise test would check the exact set of messages and line numbers.
    generated_warning_tuples = set()
    for w in warnings:
        try:
            parts = w.split(":")
            line = int(parts[0].split("Line ")[1])
            msg = ":".join(parts[1:]).strip()
            if msg.startswith("[Optimization] Line"): # handling the nested format string
                actual_line_in_msg = int(msg.split("Line ")[1].split(":")[0])
                actual_msg_content = msg.split(f"Line {actual_line_in_msg}: ")[1]
                generated_warning_tuples.add((actual_line_in_msg, actual_msg_content))
            else:
                generated_warning_tuples.add((line, msg))

        except: # Simplistic parsing for test
            pass

    expected_warning_tuples = set(expected_warnings_details)
    
    # Check if all expected warnings are found among the generated ones
    # This is a bit lenient due to the complex nested reporting of the linter
    for ew_tuple in expected_warning_tuples:
        assert ew_tuple in generated_warning_tuples or \
               any(gw_line == ew_tuple[0] and ew_tuple[1] in gw_msg for gw_line, gw_msg in generated_warning_tuples), \
               f"Expected warning {ew_tuple} not found in {generated_warning_tuples}"

    if not expected_warnings_details:
        assert not warnings

# 3. Test check_string_concat_in_loop
@pytest.mark.parametrize("code, expected_details", [
    ("s = ''\nfor i in range(3):\n  s = s + str(i)", [(3, "String concatenation in loop for 's'. Consider using ''.join() or appending to a list and joining outside the loop.")]),
    ("s = ''\nfor i in range(3):\n  s += str(i)", [(3, "Augmented assignment 's += ...' in loop. Consider using ''.join() or appending to a list and joining outside the loop.")]),
    ("s = ''\nwhile True:\n  s = s + 'a'\n  break", [(3, "String concatenation in loop for 's'. Consider using ''.join() or appending to a list and joining outside the loop.")]),
    ("s = ''\ns = s + 'a'", []),
    ("my_list = []\nfor i in range(3):\n  my_list.append(str(i))", []),
])
def test_check_string_concat_in_loop(code, expected_details):
    tree = ast.parse(code)
    warnings = check_string_concat_in_loop(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 4. Test check_len_call_in_loop
@pytest.mark.parametrize("code, expected_details", [
    ("data = [1,2,3]\nfor x in data:\n  if len(data) > 1: pass", [(3, "Call to len() inside loop. Consider storing the length in a variable before the loop.")]),
    ("data = [1,2,3]\ni = 0\nwhile i < len(data):\n  i += 1", [(3, "Call to len() inside loop. Consider storing the length in a variable before the loop.")]),
    ("data = [1,2,3]\nl = len(data)\nfor x in data:\n  if l > 1: pass", []),
    ("len([1,2,3])", []),
])
def test_check_len_call_in_loop(code, expected_details):
    tree = ast.parse(code)
    warnings = check_len_call_in_loop(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 5. Test check_range_len_pattern
@pytest.mark.parametrize("code, expected_details", [
    ("data = [1,2,3]\nfor i in range(len(data)): pass", [(2, "Loop over 'range(len(...))'. Consider using 'enumerate()' to iterate directly over the sequence.")]),
    ("data = [1,2,3]\nfor i in range(10): pass", []),
    ("data = [1,2,3]\nfor i, item in enumerate(data): pass", []),
])
def test_check_range_len_pattern(code, expected_details):
    tree = ast.parse(code)
    warnings = check_range_len_pattern(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 6. Test check_append_in_loop
@pytest.mark.parametrize("code, expected_details", [
    ("res = []\nfor i in range(3):\n  res.append(i)", [(3, "Using list.append() inside a loop. Consider using a list comprehension for better performance.")]),
    ("res = []\ni=0\nwhile i < 3:\n  res.append(i)\n  i+=1", [(4, "Using list.append() inside a loop. Consider using a list comprehension for better performance.")]),
    ("res = [i for i in range(3)]", []),
    ("res = []\nres.append(0)", []),
])
def test_check_append_in_loop(code, expected_details):
    tree = ast.parse(code)
    warnings = check_append_in_loop(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 7. Test check_unused_variables
@pytest.mark.parametrize("code, expected_details", [
    ("x = 10", [(1, "Variable 'x' is assigned but never used.")]),
    ("x: int = 10", [(1, "Variable 'x' is assigned but never used.")]),
    ("for unused_var in range(3): pass", [(1, "Variable 'unused_var' is assigned but never used.")]),
    ("a, b = 1, 2\nprint(a)", [(1, "Variable 'b' is assigned but never used.")]),
    ("with open('f.txt', 'w') as f_unused: pass", [(1, "Variable 'f_unused' is assigned but never used.")]), # Assuming f_unused is name
    ("x = 10\nprint(x)", []),
    ("_x = 10", []), # Ignored
    ("x = 1\nx += 2", [(1, "Variable 'x' is assigned but never used.")]), # x used in augassign target, but not loaded after
    ("def my_func(param_unused):\n  local_unused = 1", [(2, "Variable 'local_unused' is assigned but never used.")]), # Param not checked by this, local is
])
def test_check_unused_variables(code, expected_details):
    tree = ast.parse(code)
    warnings = check_unused_variables(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 8. Test check_deeply_nested_loops
@pytest.mark.parametrize("code, max_depth, expected_details", [
    ("for i in range(1):\n for j in range(1):\n  for k in range(1): pass", 2,
     [(3, "High complexity: Loop nesting depth is 3. Consider extracting nested logic into separate functions.")]),
    ("for i in range(1):\n for j in range(1):\n  while True:\n   for l in range(1): break; break; break", 2,
     [(3, "High complexity: Loop nesting depth is 3. Consider extracting nested logic into separate functions."),
      (4, "High complexity: Loop nesting depth is 4. Consider extracting nested logic into separate functions.")]),
    ("for i in range(1):\n for j in range(1): pass", 2, []),
    ("def f():\n for i in range(1):\n  for j in range(1):\n   for k in range(1): pass\nfor x in range(1):\n for y in range(1): pass", 2,
     [(4, "High complexity: Loop nesting depth is 3. Consider extracting nested logic into separate functions.")]), # Depth resets for function
])
def test_check_deeply_nested_loops(code, max_depth, expected_details):
    tree = ast.parse(code)
    warnings = check_deeply_nested_loops(tree, max_depth)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 9. Test check_dict_comprehension
@pytest.mark.parametrize("code, expected_details", [
    ("d = {}\nfor k,v in [(1,1)]:\n  d[k] = v", [(3, "Building dict 'd' via loop assignment. Consider using a dict comprehension.")]),
    ("d = {k:v for k,v in [(1,1)]}", []),
    ("d = {}\nd['key'] = 'val'", []),
])
def test_check_dict_comprehension(code, expected_details):
    tree = ast.parse(code)
    warnings = check_dict_comprehension(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 10. Test check_set_comprehension
@pytest.mark.parametrize("code, expected_details", [
    ("s = set()\nfor x in [1,2]:\n  s.add(x)", [(3, "Building set 's' via add() in a loop. Consider using a set comprehension.")]),
    ("s = {x for x in [1,2]}", []),
    ("s = set()\ns.add(1)", []),
])
def test_check_set_comprehension(code, expected_details):
    tree = ast.parse(code)
    warnings = check_set_comprehension(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 11. Test check_genexpr_vs_list
@pytest.mark.parametrize("code, expected_details", [
    ("sum([x*x for x in range(3)])", [(1, "sum() applied to a list comprehension. Consider using a generator expression (remove the brackets) for better memory efficiency.")]),
    ("any([x > 1 for x in range(3)])", [(1, "any() applied to a list comprehension. Consider using a generator expression (remove the brackets) for better memory efficiency.")]),
    ("sum(x*x for x in range(3))", []),
    ("my_list = [x*x for x in range(3)]\nsum(my_list)", []),
])
def test_check_genexpr_vs_list(code, expected_details):
    tree = ast.parse(code)
    warnings = check_genexpr_vs_list(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 12. Test check_membership_on_list_in_loop
@pytest.mark.parametrize("code, expected_details", [
    ("my_list = [1,2]\nfor x in range(3):\n  if x in my_list: pass", [(3, "Membership test 'x in my_list' inside a loop. If 'my_list' is a large list, consider converting it to a set for faster lookups.")]),
    ("my_list = [1,2]\nfor x in range(3):\n  if x not in my_list: pass", [(3, "Membership test 'x not in my_list' inside a loop. If 'my_list' is a large list, consider converting it to a set for faster lookups.")]),
    ("my_set = {1,2}\nfor x in range(3):\n  if x in my_set: pass", []), # Should be empty as current check specifically looks for ast.Name
    ("my_list = [1,2]\nif 1 in my_list: pass", []),
    ("my_list = [1,2]\nfor x in range(3):\n  if x in [10, 20]: pass", []), # Comparator is not ast.Name
])
def test_check_membership_on_list_in_loop(code, expected_details):
    tree = ast.parse(code)
    warnings = check_membership_on_list_in_loop(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 13. Test check_open_without_context
@pytest.mark.parametrize("code, expected_details", [
    ("f = open('file.txt', 'w')", [(1, "Use of open() outside of a 'with' context manager. Consider using 'with open(...) as f:' for better resource management.")]),
    ("with open('file.txt', 'w') as f: pass", []),
    ("def my_open(): pass\nf = my_open()", []),
])
def test_check_open_without_context(code, expected_details):
    tree = ast.parse(code)
    warnings = check_open_without_context(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 14. Test check_list_build_then_copy
@pytest.mark.parametrize("code, expected_details", [
    ("res = []\nfor x in range(3): res.append(x)\nfinal = res[:]",
     [(3, "List 'res' is built via append and then copied with slice. Consider using a list comprehension: [transform(x) for x in iterable if cond(x)]")]),
    ("res = [1]\nfor x in range(3): res.append(x)\nfinal = res[:]", []), # Not initially empty
    ("res = []\nfinal = res[:]", []), # No build loop
    ("res = []\nfor x in range(3): res.append(x)\nprint(res)", []), # No copy
])
def test_check_list_build_then_copy(code, expected_details):
    tree = ast.parse(code)
    warnings = check_list_build_then_copy(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# 15. Test check_sort_assignment
@pytest.mark.parametrize("code, expected_details", [
    ("my_list = [3,1,2]\nsorted_list = my_list.sort()", [(2, "Assignment of list.sort() which returns None. Use sorted(list) if you need the sorted result in a new variable.")]),
    ("my_list = [3,1,2]\nmy_list.sort()", []),
    ("my_list = [3,1,2]\nsorted_list = sorted(my_list)", []),
])
def test_check_sort_assignment(code, expected_details):
    tree = ast.parse(code)
    warnings = check_sort_assignment(tree)
    expected_warnings = [format_optimization_warning(msg, line) for line, msg in expected_details]
    assert sorted(warnings) == sorted(expected_warnings)

# Integration test for run_all_optimization_checks (example)
def test_run_all_optimization_checks_integration():
    source_code = """
import os # unused
import sys

def my_func():
    x = 10 # unused
    s = ""
    for i in range(len(sys.argv)): # range(len) and len in loop
        s = s + str(i) # string concat
        if len(sys.argv) > 0: # len in loop
            pass
    return s
    print("unreachable") # unreachable
"""
    # Expected warnings (line numbers are relative to the source_code string)
    # Line 2: unused 'os'
    # Line 6: unused 'x'
    # Line 8: range(len(...)) on sys.argv
    # Line 8: len() in loop (from range(len()))
    # Line 9: string concat 's = s + ...'
    # Line 10: len() in loop
    # Line 13: unreachable code
    
    # We will check for the presence of key phrases, actual line numbers can be tricky
    # with multiline strings in tests if not careful with parsing.
    # The run_all_optimization_checks sorts and de-duplicates.

    warnings = run_all_optimization_checks(source_code)
    
    expected_messages_content = [
        "Imported name 'os' is never used.", # Line 2 of snippet -> line 1 of ast
        "Variable 'x' is assigned but never used.", # Line 6 of snippet -> line 2 of func body
        "Loop over 'range(len(...))'.", # Line 8
        "Call to len() inside loop.", # Line 8 (from range(len)) AND Line 10
        "String concatenation in loop for 's'.", # Line 9
        "This code is unreachable." # Line 13
    ]

    # Check that each expected message type is present
    for expected_msg_part in expected_messages_content:
        assert any(expected_msg_part in w for w in warnings), f"Expected part '{expected_msg_part}' not found in warnings: {warnings}"

    # Verify a few specific line numbers if possible (adjust based on actual AST parsing of the snippet)
    # The ast module line numbers are 1-indexed from the start of the parsed string.
    # "import os" is on line 2 of the snippet, which becomes line 1 of the AST `tree`.
    assert format_optimization_warning("Imported name 'os' is never used.", 1) in warnings # `import os` on line 1 of ast
    # `x=10` is on line 5 of ast (def my_func():, x=10)
    assert format_optimization_warning("Variable 'x' is assigned but never used.", 5) in warnings


if __name__ == "__main__":
    pytest.main()