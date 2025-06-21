import ast

from pyward.optimization.rules.list_build_then_copy import \
    check_list_build_then_copy


def test_detect_build_then_copy():
    src = "res=[]\nfor x in [1]: res.append(x)\ncopy=res[:]\n"
    issues = check_list_build_then_copy(ast.parse(src))
    assert len(issues) == 1
    assert "List 'res' is built via append" in issues[0]


def test_no_build_then_copy():
    src = "copy=[x for x in [1]]\n"
    assert check_list_build_then_copy(ast.parse(src)) == []
