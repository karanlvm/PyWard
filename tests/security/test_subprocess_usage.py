import ast

from pyward.security.rules.subprocess_usage import check_subprocess_usage


def test_detect_all_shell_true_calls():
    src = "\n".join(
        [
            "import subprocess",
            "subprocess.run('ls', shell=True)",
            "subprocess.Popen([], shell=True)",
            "subprocess.call('x', shell=True)",
            "subprocess.check_output('x', shell=True)",
        ]
    )
    issues = check_subprocess_usage(ast.parse(src))
    assert len(issues) == 4
    assert all("shell=True" in m for m in issues)
