import ast

from pyward.optimization.rules.deeply_nested_loops import \
    check_deeply_nested_loops


def test_detect_nested_loops():
    src = "for _ in [1]:\n  for _ in [1]:\n    for _ in [1]: pass\n"
    issues = check_deeply_nested_loops(ast.parse(src), max_depth=2)
    assert len(issues) == 1
    assert "High complexity: loop nesting depth is 3" in issues[0]


def test_no_nested_loops_within_limit():
    src = "for _ in [1]:\n  for _ in [1]: pass\n"
    assert check_deeply_nested_loops(ast.parse(src), max_depth=2) == []
