import ast

from pyward.security.rules.yaml_load import check_yaml_load_usage


def test_flag_missing_safeloader():
    src = "import yaml\nyaml.load(data)\nyaml.load(data, Loader=yaml.SafeLoader)\n"
    issues = check_yaml_load_usage(ast.parse(src))
    assert len(issues) == 1
    assert "yaml.load() without SafeLoader" in issues[0]
    assert "Line 2" in issues[0]
