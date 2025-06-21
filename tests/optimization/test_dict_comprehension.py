import ast

from pyward.optimization.rules.dict_comprehension import \
    check_dict_comprehension


def test_detect_dict_comprehension():
    src = "d={}\nfor k,v in [(1,2)]: d[k]=v\n"
    issues = check_dict_comprehension(ast.parse(src))
    assert len(issues) == 1
    assert "Building dict 'd' via loop assignment" in issues[0]


def test_no_dict_comprehension():
    src = "d={k:v for k,v in [(1,2)]}\n"
    assert check_dict_comprehension(ast.parse(src)) == []
