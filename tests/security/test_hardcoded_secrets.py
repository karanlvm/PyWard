import ast
from pyward.security.rules.hardcoded_secrets import check_hardcoded_secrets

def test_detect_various_secrets():
    src = "\n".join([
        "my_secret='s'",
        "not_key='ok'",
        "password_token='p'",
        "x=1"
    ])
    issues = check_hardcoded_secrets(ast.parse(src))
    assert len(issues) == 3
    assert any("my_secret" in m and "Line 1" in m for m in issues)
    assert any("not_key" in m and "Line 2" in m for m in issues)
    assert any("password_token" in m and "Line 3" in m for m in issues)
