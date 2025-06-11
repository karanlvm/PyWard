from pyward.optimization.run import run_all_optimization_checks

def test_combined_rules():
    src = "\n".join([
        "import sys",          
        "x = 1",               
        "def f(): return; y=2"
    ])
    issues = run_all_optimization_checks(src)
    assert any("Imported name 'sys' is never used" in m for m in issues)
    assert any("This code is unreachable" in m for m in issues)
    # may also include other rules—just ensure at least 2 issues found
    assert len(issues) >= 2
