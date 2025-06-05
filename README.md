# PyWard

[![PyPI version](https://img.shields.io/pypi/v/pyward-cli?label=PyPI)](https://pypi.org/project/pyward-cli/)
![CI](https://github.com/karanlvm/PyWard/actions/workflows/ci.yml/badge.svg)

PyWard is a lightweight command-line linter for Python code. It helps developers catch optimization issues (like unused imports and unreachable code) and security vulnerabilities (such as unsafe `eval`/`exec` usage and known CVE patterns).

## Features

- **Optimization Checks**
  - Detects unused imports
  - Flags unreachable code blocks

- **Security Checks**
  - Flags usage of `eval()` and `exec()` (e.g., CVE-2025-3248)
  - Detects vulnerable imports like `python_json_logger` (e.g., CVE-2025-27607)

- **Flexible CLI**
  - Run all checks by default
  - Use `-o`/`--optimize` to run only optimization checks
  - Use `-s`/`--security` to run only security checks
  - Use `-v`/`--verbose` for detailed output, even if no issues are found

## Installation

Install from PyPI:

```bash
pip install pyward-cli
```

Ensure that you have Python 3.7 or newer.

## Usage

Basic usage (runs both optimization and security checks):

```bash
pyward <your_python_file.py>
```

### Options

- `-o, --optimize`  
  Run only optimization checks (unused imports, unreachable code).

- `-s, --security`  
  Run only security checks (unsafe calls, CVE-based rules).

- `-v, --verbose`  
  Show detailed warnings and suggestions, even if no issues are detected.

### Examples

Run all checks on `demo.py`:

```bash
pyward demo.py
```

Run only optimization checks:

```bash
pyward -o demo.py
```

Run only security checks:

```bash
pyward -s demo.py
```

Run with verbose mode:

```bash
pyward -v demo.py
```

## Contributing

Contributions are welcome! To add new rules or improve existing ones:

1. Fork the repository.
2. Create a new branch (e.g., `feature/new-rule`).
3. Implement your changes and add tests if applicable.
4. Open a pull request detailing your enhancements.

Please adhere to the project’s coding style and include meaningful commit messages.
For more details on the contributing process, see the [CONTRIBUTING](CONTRIBUTING.md)
## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

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
        <a href=https://github.com/DannyNavi>
            <img src=https://avatars.githubusercontent.com/u/129900868?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=DannyNavi/>
            <br />
            <sub style="font-size:14px"><b>DannyNavi</b></sub>
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
