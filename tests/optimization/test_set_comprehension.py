import ast

from pyward.optimization.rules.set_comprehension import check_set_comprehension


def test_detect_set_comprehension():
    src = "s=set()\nfor x in [1]: s.add(x)\n"
    issues = check_set_comprehension(ast.parse(src))
    assert len(issues) == 1
    assert "Building set 's' via add()" in issues[0]


def test_no_set_comprehension():
    src = "s={x for x in [1]}\n"
    assert check_set_comprehension(ast.parse(src)) == []
