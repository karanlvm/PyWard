# PyWard

[![PyPI version](https://img.shields.io/pypi/v/pyward-cli?label=PyPI)](https://pypi.org/project/pyward-cli/)  
![CI](https://github.com/karanlvm/PyWard/actions/workflows/ci.yml/badge.svg)

PyWard is a lightweight command-line linter for Python code. It helps developers catch optimization issues and security vulnerabilities.

## Installation

Install from PyPI:

```bash
pip install pyward-cli
```

Ensure that you have Python 3.7 or newer.

## Usage

Basic usage (runs all checks):

```bash
pyward <file_or_directory>
```

### Flags

- `-r, --recursive`  
  Scan directories recursively.

- `-o, --optimize`  
  Run only optimization checks.

- `-s, --security`  
  Run only security checks.

- `-k, --skip <check>`  
  Skip a specific check by its name (e.g. `--skip unused_imports`).

- `-v, --verbose`  
  Show detailed warnings even if no issues are found.

### Available Checks

#### Optimization Checks
- `append_in_loop`  
- `deeply_nested_loops`  
- `dict_comprehension`  
- `genexpr_vs_list`  
- `len_call_in_loop`  
- `list_build_then_copy`  
- `membership_on_list_in_loop`  
- `open_without_context`  
- `range_len_pattern`  
- `set_comprehension`  
- `sort_assignment`  
- `string_concat_in_loop`  
- `unreachable_code`  
- `unused_imports`  
- `unused_variables`  

#### Security Checks
- `exec_eval`  
- `hardcoded_secrets`  
- `pickle_usage`  
- `python_json_logger`  
- `ssl_verification`  
- `subprocess_usage`  
- `url_open_usage`  
- `weak_hashing_usage`  
- `yaml_load`  

## Examples

Scan recursively and skip unused_imports:

```bash
pyward -r --skip unused_imports demo
```

Run only security checks:

```bash
pyward -s my_script.py
```

Verbose output:

```bash
pyward -v my_script.py
```

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md) for details.

## License

MIT License — see [LICENSE](LICENSE).
