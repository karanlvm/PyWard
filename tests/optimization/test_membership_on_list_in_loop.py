import ast
from pyward.optimization.rules.membership_on_list_in_loop import check_membership_on_list_in_loop

def test_detect_membership_in_loop():
    src = "lst=[1]\nfor x in [2]:\n    if x in lst: pass\n"
    issues = check_membership_on_list_in_loop(ast.parse(src))
    assert len(issues) == 1
    # implementation emits "...inside loop", not "inside a loop"
    assert "Membership test 'x in lst' inside loop" in issues[0]

def test_no_membership_in_loop():
    src = "if x in []: pass\n"
    assert check_membership_on_list_in_loop(ast.parse(src)) == []
