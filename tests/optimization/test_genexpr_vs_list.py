import ast

from pyward.optimization.rules.genexpr_vs_list import check_genexpr_vs_list


def test_detect_genexpr_vs_list():
    src = "total = sum([x for x in [1,2]])\n"
    issues = check_genexpr_vs_list(ast.parse(src))
    assert len(issues) == 1
    # implementation emits "...sum() applied to list comprehension"
    assert "sum() applied to list comprehension" in issues[0]


def test_no_genexpr_vs_list():
    src = "total = sum(x for x in [1,2])\n"
    assert check_genexpr_vs_list(ast.parse(src)) == []
