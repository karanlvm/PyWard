# tests/test_ssl_verification_disabled.py

import ast

import pytest

from pyward.security.rules.ssl_verification import \
    check_ssl_verification_disabled


def _parse_source(src: str) -> ast.AST:
    return ast.parse(src)


def test_requests_methods_with_verify_false_are_flagged():
    source = """
import requests
requests.get("https://example.com", verify=False)
requests.post("https://example.com", data=data, verify=False)
requests.put("https://api.example.com/resource", json=data, verify=False)
"""
    tree = _parse_source(source)
    issues = check_ssl_verification_disabled(tree)

    # One issue per call
    assert len(issues) == 3
    assert any("requests.get()" in msg and "Line 3" in msg for msg in issues)
    assert any("requests.post()" in msg and "Line 4" in msg for msg in issues)
    assert any("requests.put()" in msg and "Line 5" in msg for msg in issues)


def test_requests_request_call_with_verify_false_is_flagged():
    source = """
import requests
response = requests.request('GET', "https://example.com", verify=False)
"""
    tree = _parse_source(source)
    issues = check_ssl_verification_disabled(tree)

    assert len(issues) == 1
    assert "requests.request()" in issues[0]
    assert "Line 3" in issues[0]


def test_session_method_with_verify_false_is_flagged():
    source = """
import requests
session = requests.Session()
response = session.get("https://example.com", verify=False)
"""
    tree = _parse_source(source)
    issues = check_ssl_verification_disabled(tree)

    assert len(issues) == 1
    # generic warning for non-requests.* call
    assert "verify=False" in issues[0]
    assert "man-in-the-middle attacks" in issues[0]
    assert "Line 4" in issues[0]


@pytest.mark.parametrize(
    "call",
    [
        'requests.get("https://example.com")',
        'requests.post("https://example.com", data=data, verify=True)',
        'session.get("https://example.com")',
    ],
)
def test_no_issues_when_verify_true_or_omitted(call):
    source = f"""
import requests
session = requests.Session()
_ = {call}
"""
    tree = _parse_source(source)
    issues = check_ssl_verification_disabled(tree)
    assert issues == []
