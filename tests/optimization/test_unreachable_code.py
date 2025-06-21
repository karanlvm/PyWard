import ast

from colorama import Back, Fore, Style

from pyward.optimization.rules.unreachable_code import check_unreachable_code

OPT = f"{Fore.WHITE}{Back.YELLOW}[Optimization]{Style.RESET_ALL}"


def test_function_level_unreachable():
    src = "def f():\n  return\n  x = 1\n"
    issues = check_unreachable_code(ast.parse(src))
    assert len(issues) == 1
    assert "This code is unreachable." in issues[0]


def test_module_level_unreachable():
    src = "x = 1\nraise Exception()\ny = 2\n"
    issues = check_unreachable_code(ast.parse(src))
    assert len(issues) == 1
    assert "This code is unreachable." in issues[0]
