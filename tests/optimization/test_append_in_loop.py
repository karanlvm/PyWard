import ast
from pyward.optimization.rules.append_in_loop import check_append_in_loop

def test_detect_append():
    src = "lst=[]\nfor x in [1]:\n    lst.append(x)\n"
    issues = check_append_in_loop(ast.parse(src))
    assert len(issues) == 1
    assert "Using list.append() inside a loop" in issues[0]

def test_no_append_outside():
    src = "lst=[]\nlst.append(1)\n"
    assert check_append_in_loop(ast.parse(src)) == []
