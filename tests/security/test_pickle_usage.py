import ast
from pyward.security.rules.pickle_usage import check_pickle_usage

def test_detect_load_and_loads():
    src = "import pickle\npickle.load(f)\npickle.loads(b'')\n"
    issues = check_pickle_usage(ast.parse(src))
    assert len(issues) == 2
    assert any("pickle.load()" in m and "Line 2" in m for m in issues)
    assert any("pickle.loads()" in m and "Line 3" in m for m in issues)
