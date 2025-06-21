import ast

from pyward.optimization.rules.string_concat_in_loop import \
    check_string_concat_in_loop


def test_detect_concat():
    src = "s = ''\nfor _ in [1]:\n    s = s + 'a'\n"
    issues = check_string_concat_in_loop(ast.parse(src))
    assert len(issues) == 1
    assert "String concatenation in loop for 's'" in issues[0]


def test_no_concat_outside_loop():
    src = "s = ''\ns = s + 'a'\n"
    assert check_string_concat_in_loop(ast.parse(src)) == []
