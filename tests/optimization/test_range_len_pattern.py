import ast

from pyward.optimization.rules.range_len_pattern import check_range_len_pattern


def test_detect_range_len():
    src = "a=[1,2]\nfor i in range(len(a)):\n    pass\n"
    issues = check_range_len_pattern(ast.parse(src))
    assert len(issues) == 1
    assert "Loop over 'range(len(...))'" in issues[0]


def test_no_range_len():
    src = "a=[1,2]\nfor i,val in enumerate(a):\n    pass\n"
    assert check_range_len_pattern(ast.parse(src)) == []
