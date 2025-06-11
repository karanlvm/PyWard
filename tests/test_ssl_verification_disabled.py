import ast
import pytest

from pyward.rules.security_rules import check_ssl_verification_disabled


def _parse_source(source: str) -> ast.AST:
    return ast.parse(source)


def test_requests_method_with_verify_false():
    source = """
import requests
response = requests.get("https://example.com", verify=False)
response = requests.post("https://example.com", data=data, verify=False)
response = requests.put("https://api.example.com/resource", json=data, verify=False)
"""
    tree = _parse_source(source)
    issues = check_ssl_verification_disabled(tree)

    # We should have 3 issues, one for each requests method call
    assert len(issues) == 3
    assert any("requests.get()" in msg and "Line 3" in msg for msg in issues)
    assert any("requests.post()" in msg and "Line 4" in msg for msg in issues)
    assert any("requests.put()" in msg and "Line 5" in msg for msg in issues)


def test_requests_generic_method_with_verify_false():
    source = """
import requests
response = requests.request('GET', "https://example.com", verify=False)
"""
    tree = _parse_source(source)
    issues = check_ssl_verification_disabled(tree)

    # We should have 1 issue for the requests.request call
    assert len(issues) == 1
    assert "requests.request()" in issues[0]
    assert "Line 3" in issues[0]


def test_requests_session_method_with_verify_false():
    source = """
import requests
session = requests.Session()
response = session.get("https://example.com", verify=False)
"""
    tree = _parse_source(source)
    issues = check_ssl_verification_disabled(tree)

    assert len(issues) == 1
    assert "verify=False" in issues[0]
    assert "Line 4" in issues[0]


def test_requests_methods_with_verify_true_or_omitted():
    source = """
import requests
response = requests.get("https://example.com")  # Default is verify=True
response = requests.post("https://example.com", data=data, verify=True)
"""
    tree = _parse_source(source)
    issues = check_ssl_verification_disabled(tree)

    assert len(issues) == 0  # No issues should be reported for these cases