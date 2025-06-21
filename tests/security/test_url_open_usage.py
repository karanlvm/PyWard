import ast

from pyward.security.rules.url_open_usage import check_url_open_usage


def test_flag_dynamic_urlopen():
    src = "import urllib.request\nurl=input()\nurllib.request.urlopen(url)\n"
    issues = check_url_open_usage(ast.parse(src))
    assert len(issues) == 1
    assert "urlopen" in issues[0] and "Line 3" in issues[0]


def test_no_flag_constant_url():
    src = "import urllib.request\nurllib.request.urlopen('http://x')\n"
    assert check_url_open_usage(ast.parse(src)) == []
