from pyward.security.run import run_all_security_checks


def test_combined_security_checks():
    src = "\n".join(
        [
            "import python_json_logger",
            "exec('x')",
            "import pickle\npickle.loads(b'')",
        ]
    )
    issues = run_all_security_checks(src)
    assert any("python_json_logger" in m for m in issues)
    assert any("exec()" in m for m in issues)
    assert any("pickle.loads()" in m for m in issues)
    assert len(issues) >= 3
