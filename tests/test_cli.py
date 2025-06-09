import pytest
import tempfile
import os
import sys
import subprocess
from unittest.mock import patch
from io import StringIO
from pyward.cli import main


@pytest.fixture
def temp_python_file():
    """Fixture to create a temporary Python file for CLI testing."""
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test.py")

    with open(temp_file, "w", encoding="utf-8") as f:
        f.write("print('Hello, World!')\n")

    yield temp_file

    # Cleanup
    os.remove(temp_file)
    os.rmdir(temp_dir)


@pytest.fixture
def mock_analyze_file():
    """Fixture to mock the analyze_file function."""
    with patch("pyward.cli.analyze_file") as mock:
        yield mock


class TestCLIMain:
    """Test cases for the main CLI function."""

    def test_main_no_issues_found(self, temp_python_file, mock_analyze_file):
        mock_analyze_file.return_value = []

        with patch("sys.argv", ["pyward", temp_python_file]), patch(
            "sys.stdout", new=StringIO()
        ) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()

        mock_analyze_file.assert_called_once_with(
            temp_python_file, run_optimization=True, run_security=True, verbose=False
        )

        output = fake_stdout.getvalue()
        assert "✅ No issues found" in output
        assert temp_python_file in output
        assert exc_info.value.code == 0

    def test_main_with_issues_found(self, temp_python_file, mock_analyze_file):
        mock_analyze_file.return_value = [
            "Line 1: Imported name 'os' is never used.",
            "Line 5: Use of exec() detected.",
        ]

        with patch("sys.argv", ["pyward", temp_python_file]), patch(
            "sys.stdout", new=StringIO()
        ) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()

        output = fake_stdout.getvalue()
        assert "❌ Found 2 issue(s)" in output
        assert temp_python_file in output
        assert "1. Line 1: Imported name 'os'" in output
        assert "2. Line 5: Use of exec()" in output
        assert exc_info.value.code == 1

    @pytest.mark.parametrize(
        "flag,expected_opt,expected_sec",
        [
            (["-o"], True, False),  # Optimization only
            (["--optimize"], True, False),  # Optimization only (long form)
            (["-s"], False, True),  # Security only
            (["--security"], False, True),  # Security only (long form)
            ([], True, True),  # Default behavior (both)
        ],
    )
    def test_main_flag_combinations(
        self, temp_python_file, mock_analyze_file, flag, expected_opt, expected_sec
    ):
        mock_analyze_file.return_value = []

        argv = ["pyward"] + flag + [temp_python_file]

        with patch("sys.argv", argv), patch("sys.stdout", new=StringIO()):
            with pytest.raises(SystemExit) as exc_info:
                main()

        mock_analyze_file.assert_called_once_with(
            temp_python_file,
            run_optimization=expected_opt,
            run_security=expected_sec,
            verbose=False,
        )
        assert exc_info.value.code == 0

    @pytest.mark.parametrize("verbose_flag", ["-v", "--verbose"])
    def test_main_verbose_flag(self, temp_python_file, mock_analyze_file, verbose_flag):
        mock_analyze_file.return_value = [
            "Verbose: no issues found, but checks were performed."
        ]

        with patch("sys.argv", ["pyward", verbose_flag, temp_python_file]), patch(
            "sys.stdout", new=StringIO()
        ) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()

        mock_analyze_file.assert_called_once_with(
            temp_python_file, run_optimization=True, run_security=True, verbose=True
        )

        output = fake_stdout.getvalue()
        assert "❌ Found 1 issue(s)" in output
        assert "Verbose: no issues found" in output
        assert exc_info.value.code == 1

    def test_main_combined_optimization_flags(
        self, temp_python_file, mock_analyze_file
    ):
        mock_analyze_file.return_value = []

        with patch("sys.argv", ["pyward", "-o", "-v", temp_python_file]), patch(
            "sys.stdout", new=StringIO()
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()

        mock_analyze_file.assert_called_once_with(
            temp_python_file, run_optimization=True, run_security=False, verbose=True
        )
        assert exc_info.value.code == 0

    def test_main_combined_security_flags(self, temp_python_file, mock_analyze_file):
        mock_analyze_file.return_value = []

        with patch("sys.argv", ["pyward", "-s", "-v", temp_python_file]), patch(
            "sys.stdout", new=StringIO()
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()

        mock_analyze_file.assert_called_once_with(
            temp_python_file, run_optimization=False, run_security=True, verbose=True
        )
        assert exc_info.value.code == 0

    def test_main_no_filepath_provided(self):
        with patch("sys.argv", ["pyward"]), patch(
            "sys.stdout", new=StringIO()
        ) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()

        output = fake_stdout.getvalue()
        assert exc_info.value.code == 1
        assert "usage:" in output

    def test_main_file_not_found_error(self, mock_analyze_file):
        nonexistent_file = "/nonexistent/path/test.py"
        mock_analyze_file.side_effect = FileNotFoundError()

        with patch("sys.argv", ["pyward", nonexistent_file]), patch(
            "sys.stdout", new=StringIO()
        ) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()

        output = fake_stdout.getvalue()
        assert "Error: File" in output
        assert "does not exist" in output
        assert exc_info.value.code == 1

    def test_main_general_exception(self, temp_python_file, mock_analyze_file):
        mock_analyze_file.side_effect = Exception("Something went wrong")

        with patch("sys.argv", ["pyward", temp_python_file]), patch(
            "sys.stdout", new=StringIO()
        ) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()

        output = fake_stdout.getvalue()
        assert "Error analyzing" in output
        assert temp_python_file in output
        assert "Something went wrong" in output
        assert exc_info.value.code == 1

    def test_main_help_flag(self):
        with patch("sys.argv", ["pyward", "-h"]), patch(
            "sys.stdout", new=StringIO()
        ) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()

        output = fake_stdout.getvalue()
        assert "PyWard: CLI linter for Python" in output
        assert "optimization + security checks" in output
        assert exc_info.value.code == 0

    def test_main_mutually_exclusive_flags_error(self, temp_python_file):
        with patch("sys.argv", ["pyward", "-o", "-s", temp_python_file]), patch(
            "sys.stderr", new=StringIO()
        ) as fake_stderr:
            with pytest.raises(SystemExit) as exc_info:
                main()

            # argparse should exit with error code 2 for invalid arguments
            assert exc_info.value.code == 2

        error_output = fake_stderr.getvalue()
        assert "not allowed" in error_output

    @pytest.mark.parametrize("issues_count", [1, 5, 25, 50, 100])
    def test_main_large_number_of_issues(
        self, temp_python_file, mock_analyze_file, issues_count
    ):
        """Test main function with varying numbers of issues."""
        issues = [
            f"Line {i}: Mock issue number {i}" for i in range(1, issues_count + 1)
        ]
        mock_analyze_file.return_value = issues

        with patch("sys.argv", ["pyward", temp_python_file]), patch(
            "sys.stdout", new=StringIO()
        ) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()

        output = fake_stdout.getvalue()
        assert f"❌ Found {issues_count} issue(s)" in output
        assert (
            f"{issues_count}. Line {issues_count}: Mock issue number {issues_count}"
            in output
        )

        assert exc_info.value.code == 1

    def test_main_empty_issues_list(self, temp_python_file, mock_analyze_file):
        mock_analyze_file.return_value = []

        with patch("sys.argv", ["pyward", temp_python_file]), patch(
            "sys.stdout", new=StringIO()
        ) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()

        output = fake_stdout.getvalue()
        assert "✅ No issues found" in output
        assert exc_info.value.code == 0

    def test_cli_integration(self):
        from pathlib import Path

        content = (
            "import os\n"
            "import sys\n"
            "x = 1\n"
            "y = 2\n"
            "def foo():\n"
            "    return 3\n"
            "    z = 4\n"
            "for i in range(len([1, 2])):\n"
            "    s = ''\n"
            "    s = s + 'a'\n"
            "    lst = []\n"
            "    lst.append(i)\n"
            "d = {}\n"
            "for k, v in [('a', 1)]:\n"
            "    d[k] = v\n"
            "s2 = set()\n"
            "for x in [1, 2]:\n"
            "    s2.add(x)\n"
            "total = sum([x for x in [1, 2, 3]])\n"
            "lst2 = [1, 2, 3]\n"
            "for x in [1, 4]:\n"
            "    if x in lst2:\n"
            "        pass\n"
            "f = open('file.txt')\n"
            "temp = []\n"
            "for x in range(5):\n"
            "    temp.append(x)\n"
            "copy = temp[:]\n"
        )
        content += (
            "import pickle\n"
            'pickle.loads(b"abc")\n'
            "import urllib.request\n"
            "url = input()\n"
            "urllib.request.urlopen(url)\n"
        )

        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, "integration_test.py")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)

            current_dir = Path(__file__).parent
            project_root = current_dir.parent
            cmd = [sys.executable, "-m", "pyward.cli", temp_file]
            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root)

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=project_root, env=env
            )
            output = result.stdout.lower()
            assert result.returncode == 1
            assert len(output) > 0
            assert "issue" in output
            count_optimization = len(
                [line for line in output.split("\n") if "optimization" in line]
            )
            count_security = len(
                [line for line in output.split("\n") if "security" in line]
            )
            assert count_optimization >= 18
            assert count_security >= 2

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)


class TestCLIArgumentParsing:
    """Test cases for CLI argument parsing."""

    def test_argument_parser_configuration(self):
        import argparse

        # Create a parser similar to the one in main()
        parser = argparse.ArgumentParser(
            prog="pyward",
            description="PyWard: CLI linter for Python (optimization + security checks)",
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument("-o", "--optimize", action="store_true")
        group.add_argument("-s", "--security", action="store_true")
        parser.add_argument("-v", "--verbose", action="store_true")
        parser.add_argument("filepath", nargs="?")

        # Test valid argument combinations
        args = parser.parse_args(["-o", "test.py"])
        assert args.optimize is True
        assert args.security is False

        args = parser.parse_args(["-s", "test.py"])
        assert args.optimize is False
        assert args.security is True

        args = parser.parse_args(["-v", "test.py"])
        assert args.verbose is True

    @pytest.mark.parametrize(
        "invalid_args",
        [
            ["-o", "-s", "test.py"],  # Mutually exclusive flags
            ["--optimize", "--security", "test.py"],  # Long form mutually exclusive
        ],
    )
    def test_invalid_argument_combinations(self, invalid_args):
        with patch("sys.argv", ["pyward"] + invalid_args), patch(
            "sys.stderr", new=StringIO()
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_long_flag_names(self, temp_python_file, mock_analyze_file):
        mock_analyze_file.return_value = []

        with patch(
            "sys.argv", ["pyward", "--optimize", "--verbose", temp_python_file]
        ), patch("sys.stdout", new=StringIO()):
            with pytest.raises(SystemExit) as exc_info:
                main()

        mock_analyze_file.assert_called_once_with(
            temp_python_file, run_optimization=True, run_security=False, verbose=True
        )
        assert exc_info.value.code == 0

    def test_default_behavior(self, temp_python_file, mock_analyze_file):
        mock_analyze_file.return_value = []

        with patch("sys.argv", ["pyward", temp_python_file]), patch(
            "sys.stdout", new=StringIO()
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # Default should be both optimization and security enabled
        mock_analyze_file.assert_called_once_with(
            temp_python_file, run_optimization=True, run_security=True, verbose=False
        )
        assert exc_info.value.code == 0
