import ast
from pyward.security.rules.python_json_logger import check_python_json_logger_import

def test_detect_import_and_from():
    src = "import python_json_logger\nfrom python_json_logger import Foo\n"
    issues = check_python_json_logger_import(ast.parse(src))
    assert len(issues) == 2
    assert all("CVE-2025-27607" in m for m in issues)
    assert any("Line 1" in m for m in issues)
    assert any("Line 2" in m for m in issues)
