import ast
import pytest
import tempfile, os
from pyward.analyzer import analyze_file

# A small fixture to write a temp file
@pytest.fixture
def temp_file():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "f.py")
    yield path, d
    os.remove(path)
    os.rmdir(d)

def test_analyze_empty_file(temp_file):
    path, d = temp_file
    open(path, "w").close()
    issues = analyze_file(path)
    assert issues == []

def test_analyze_syntax_error(temp_file):
    path, d = temp_file
    with open(path, "w") as f:
        f.write("def bad(\n")
    issues = analyze_file(path)
    assert len(issues) == 1
    assert "SyntaxError while parsing" in issues[0]

def test_analyze_optimization_and_security(temp_file):
    path, d = temp_file
    content = "import os\nexec('x')\n"
    with open(path, "w") as f:
        f.write(content)
    issues = analyze_file(path)
    # should flag unused-import + exec
    assert any("Imported name 'os' is never used" in m for m in issues)
    assert any("Use of 'exec()' detected"   in m for m in issues)
    assert len(issues) == 2

def test_verbose_mode(temp_file):
    path, d = temp_file
    with open(path, "w") as f:
        f.write("print(1)\n")
    issues = analyze_file(path, verbose=True, run_optimization=False, run_security=False)
    assert issues == ["Verbose: no issues found, but checks were performed."]

def test_disable_each_runner(temp_file):
    path, d = temp_file
    with open(path, "w") as f:
        f.write("import os\nexec('x')\n")
    # only optimization
    issues = analyze_file(path, run_optimization=True, run_security=False)
    assert any("Imported name 'os'" in m for m in issues)
    assert not any("exec()" in m for m in issues)
    # only security
    issues = analyze_file(path, run_optimization=False, run_security=True)
    assert any("exec()" in m for m in issues)
    assert not any("os" in m for m in issues)
