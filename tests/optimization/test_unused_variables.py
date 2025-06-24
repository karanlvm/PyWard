import ast

from colorama import Back, Fore, Style

from pyward.optimization.rules.unused_variables import check_unused_variables

OPT = f"{Fore.WHITE}{Back.YELLOW}[Optimization]{Style.RESET_ALL}"


def test_detect_unused_variable():
    src = "a = 1\nb = 2\nprint(a)\n"
    issues = check_unused_variables(ast.parse(src))
    assert len(issues) == 1
    msg = issues[0]
    assert msg.startswith(OPT)
    assert "Variable 'b' is assigned but never used" in msg


def test_ignore_underscore():
    src = "_x = 5\nprint(_x)\ny = 10\n"
    issues = check_unused_variables(ast.parse(src))
    assert len(issues) == 1
    assert "Variable 'y' is assigned but never used" in issues[0]
