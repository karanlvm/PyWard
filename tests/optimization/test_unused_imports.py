import ast
from colorama import Fore, Back, Style
from pyward.optimization.rules.unused_imports import check_unused_imports

OPT = f"{Fore.WHITE}{Back.YELLOW}[Optimization]{Style.RESET_ALL}"

def test_single_unused():
    src = "import os\nimport sys\nprint(os.getcwd())\n"
    issues = check_unused_imports(ast.parse(src))
    assert len(issues) == 1
    msg = issues[0]
    assert msg.startswith(OPT)
    assert "Imported name 'sys' is never used" in msg

def test_no_unused():
    src = "import math\nx = math.pi\n"
    assert check_unused_imports(ast.parse(src)) == []
