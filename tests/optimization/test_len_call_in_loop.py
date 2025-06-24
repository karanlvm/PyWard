import ast

from pyward.optimization.rules.len_call_in_loop import check_len_call_in_loop


def test_detect_len_in_loop():
    src = "lst=[1]\nfor x in lst:\n    n = len(lst)\n"
    issues = check_len_call_in_loop(ast.parse(src))
    assert len(issues) == 1
    assert "Call to len() inside loop" in issues[0]


def test_no_len_outside_loop():
    src = "lst=[1]\nn = len(lst)\n"
    assert check_len_call_in_loop(ast.parse(src)) == []
