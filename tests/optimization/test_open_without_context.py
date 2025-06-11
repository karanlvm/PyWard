import ast
from pyward.optimization.rules.open_without_context import check_open_without_context

def test_detect_open_without_context():
    src = "f=open('f')\n"
    issues = check_open_without_context(ast.parse(src))
    assert len(issues) == 1
    assert "Use of open() outside of a 'with' context manager" in issues[0]

def test_no_open_without_context():
    src = "with open('f') as f: data=f.read()\n"
    assert check_open_without_context(ast.parse(src)) == []
