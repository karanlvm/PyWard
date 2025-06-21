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

- `--version`
  Show the PyWard version and exit.

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


### Contributors

<table>
<tr>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/karanlvm>
            <img src=https://avatars.githubusercontent.com/u/69917470?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Karan Vasudevamurthy/>
            <br />
            <sub style="font-size:14px"><b>Karan Vasudevamurthy</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/cafewang>
            <img src=https://avatars.githubusercontent.com/u/18161562?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=cafewang/>
            <br />
            <sub style="font-size:14px"><b>cafewang</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/TheRGuy9201>
            <img src=https://avatars.githubusercontent.com/u/191140580?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Reeck Mondal/>
            <br />
            <sub style="font-size:14px"><b>Reeck Mondal</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/PriyanshusSGupta>
            <img src=https://avatars.githubusercontent.com/u/118932398?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Priyanshu Gupta/>
            <br />
            <sub style="font-size:14px"><b>Priyanshu Gupta</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/nature011235>
            <img src=https://avatars.githubusercontent.com/u/87652464?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=nature011235/>
            <br />
            <sub style="font-size:14px"><b>nature011235</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/DannyNavi>
            <img src=https://avatars.githubusercontent.com/u/129900868?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=DannyNavi/>
            <br />
            <sub style="font-size:14px"><b>DannyNavi</b></sub>
        </a>
    </td>
</tr>
<tr>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/nayanaaj9>
            <img src=https://avatars.githubusercontent.com/u/215096912?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Nayana Jagadeesh/>
            <br />
            <sub style="font-size:14px"><b>Nayana Jagadeesh</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/datasciritwik>
            <img src=https://avatars.githubusercontent.com/u/97968834?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Ritwik Singh/>
            <br />
            <sub style="font-size:14px"><b>Ritwik Singh</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/maxadov>
            <img src=https://avatars.githubusercontent.com/u/214614554?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Aydyn Maxadov/>
            <br />
            <sub style="font-size:14px"><b>Aydyn Maxadov</b></sub>
        </a>
    </td>
</tr>
</table>

