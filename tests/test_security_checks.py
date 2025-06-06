# tests/test_security_checks.py

import ast
import pytest

from pyward.rules.security_rules import (
    check_exec_eval_usage,
    check_python_json_logger_import,
    check_subprocess_usage,
    check_pickle_usage,
    check_yaml_load_usage,
    check_hardcoded_secrets,
    check_weak_hashing_usage,
    run_all_checks,
)


def _parse_source(source: str) -> ast.AST:
    return ast.parse(source)


def test_exec_eval_usage_detects_both_exec_and_eval():
    source = """
eval("2 + 2")
exec("print('hello')")
"""
    tree = _parse_source(source)
    issues = check_exec_eval_usage(tree)

    # Expect two warnings: one for eval(), one for exec()
    assert len(issues) == 2
    assert any("eval()" in msg and "Line 2" in msg for msg in issues)
    assert any("exec()" in msg and "Line 3" in msg for msg in issues)


def test_python_json_logger_import_flags_import_and_importfrom():
    source = """
import python_json_logger
from python_json_logger import Foo
"""
    tree = _parse_source(source)
    issues = check_python_json_logger_import(tree)

    # Expect exactly two warnings: one for import, one for import-from
    assert len(issues) == 2
    assert all("CVE-2025-27607" in msg for msg in issues)
    # Check that line numbers match
    assert any("Line 2" in msg for msg in issues)
    assert any("Line 3" in msg for msg in issues)


def test_subprocess_usage_detects_shell_true_on_various_calls():
    source = """
import subprocess
subprocess.run("ls -la", shell=True)
subprocess.Popen(["echo", "hi"], shell=True)
subprocess.call("echo 'hi'", shell=True)
subprocess.check_output("ls", shell=True)
"""
    tree = _parse_source(source)
    issues = check_subprocess_usage(tree)

    # There should be four warnings, one per call with shell=True
    assert len(issues) == 4
    assert all("shell=True" in msg for msg in issues)
    # Check that subprocess.run appears in at least one message
    assert any("subprocess.run" in msg for msg in issues)
    assert any("subprocess.Popen" in msg for msg in issues)
    assert any("subprocess.call" in msg for msg in issues)
    assert any("subprocess.check_output" in msg for msg in issues)


def test_pickle_usage_detects_load_and_loads_calls():
    source = """
import pickle
pickle.load(open("data.pkl", "rb"))
pickle.loads(b"abc")
"""
    tree = _parse_source(source)
    issues = check_pickle_usage(tree)

    # Expect two warnings: one for load(), one for loads()
    assert len(issues) == 2
    assert any("pickle.load()" in msg and "Line 3" in msg for msg in issues)
    assert any("pickle.loads()" in msg and "Line 4" in msg for msg in issues)


def test_yaml_load_usage_flags_missing_safeloader():
    source = """
import yaml
yaml.load(open("config.yaml", "r"))
yaml.load("foo", Loader=yaml.SafeLoader)
"""
    tree = _parse_source(source)
    issues = check_yaml_load_usage(tree)

    # Only the first yaml.load (line 3) should be flagged; the second uses SafeLoader and should not
    assert len(issues) == 1
    assert "yaml.load() without SafeLoader" in issues[0]
    assert "Line 3" in issues[0]


def test_hardcoded_secrets_detects_all_keywords_including_not_prefix():
    source = """
my_secret = "supersecret123"
not_key = "okay_to_use"
password_token = "abc123"
some_var = 123
"""
    tree = _parse_source(source)
    issues = check_hardcoded_secrets(tree)

    # The module flags every assignment containing 'secret', 'key', 'password', or 'token',
    # including variables starting with 'not_'. So we expect three issues.
    assert len(issues) == 3
    assert any("my_secret" in msg and "Line 2" in msg for msg in issues)
    assert any("not_key" in msg and "Line 3" in msg for msg in issues)
    assert any("password_token" in msg and "Line 4" in msg for msg in issues)


def test_weak_hashing_usage_detects_md5_and_sha1():
    source = """
import hashlib
h1 = hashlib.md5(b"data")
h2 = hashlib.sha1(b"data")
h3 = hashlib.sha256(b"secure")
"""
    tree = _parse_source(source)
    issues = check_weak_hashing_usage(tree)

    # Should detect md5 (line 3) and sha1 (line 4), but not sha256
    assert len(issues) == 2
    assert any("hashlib.md5()" in msg and "Line 3" in msg for msg in issues)
    assert any("hashlib.sha1()" in msg and "Line 4" in msg for msg in issues)


def test_weak_hashing_usage_detect_md5_with_used_for_security_eq_true():
    source = """
import hashlib
h1 = hashlib.md5(b"data", usedforsecurity=True)
"""
    tree = _parse_source(source)
    issues = check_weak_hashing_usage(tree)

    # Should detect md5 (line 3) with usedforsecurity=True
    assert len(issues) == 1
    assert any("hashlib.md5()" in msg and "Line 3" in msg for msg in issues)


def test_weak_hashing_usage_ignore_md5_with_used_for_security_eq_false():
    source = """
import hashlib
h1 = hashlib.md5(b"data", usedforsecurity=False)
"""
    tree = _parse_source(source)
    issues = check_weak_hashing_usage(tree)
    assert len(issues) == 0


def test_run_all_checks_includes_pickle_usage_warning():
    source = """
import pickle
pickle.loads(b"abc")
"""
    tree = _parse_source(source)

    individual_issues = check_pickle_usage(tree)
    all_issues = run_all_checks(tree)

    # run_all_checks should include at least the warning about pickle.loads()
    assert any("pickle.loads()" in msg for msg in individual_issues)
    assert any("pickle.loads()" in msg for msg in all_issues)
    # Ensure run_all_checks returns at least as many issues as check_pickle_usage
    assert len(all_issues) >= len(individual_issues)
