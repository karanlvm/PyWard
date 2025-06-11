import ast
from pyward.optimization.rules.sort_assignment import check_sort_assignment

def test_detect_sort_assignment():
    src = "lst=[3]; x=lst.sort()\n"
    issues = check_sort_assignment(ast.parse(src))
    assert len(issues) == 1
    assert "Assignment of list.sort()" in issues[0]

def test_no_sort_assignment():
    src = "lst=[3]\nlst.sort()\nx=sorted(lst)\n"
    assert check_sort_assignment(ast.parse(src)) == []
