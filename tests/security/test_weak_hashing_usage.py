import ast
from pyward.security.rules.weak_hashing_usage import check_weak_hashing_usage

def test_detect_md5_sha1_only():
    src = "\n".join([
        "import hashlib",
        "hashlib.md5(b'')",
        "hashlib.sha1(b'')",
        "hashlib.sha256(b'')"
    ])
    issues = check_weak_hashing_usage(ast.parse(src))
    assert len(issues) == 2
    assert any("hashlib.md5()" in m and "Line 2" in m for m in issues)
    assert any("hashlib.sha1()" in m and "Line 3" in m for m in issues)

def test_ignore_usedforsecurity_false():
    src = "import hashlib\nhashlib.md5(b'', usedforsecurity=False)\n"
    assert check_weak_hashing_usage(ast.parse(src)) == []
