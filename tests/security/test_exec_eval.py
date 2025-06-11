import ast
from colorama import Fore, Back, Style
from pyward.security.rules.exec_eval import check_exec_eval_usage

SEC = f"{Fore.WHITE}{Back.RED}[Security]{Style.RESET_ALL}"

def test_detect_eval_and_exec():
    src = "eval('2+2')\nexec('print(1)')\n"
    issues = check_exec_eval_usage(ast.parse(src))
    assert len(issues) == 2
    assert any("eval()" in m and "Line 1" in m for m in issues)
    assert any("exec()" in m and "Line 2" in m for m in issues)
    for m in issues:
        assert m.startswith(SEC)
