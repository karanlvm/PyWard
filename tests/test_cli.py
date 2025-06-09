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
    with patch('pyward.cli.analyze_file') as mock:
        yield mock


class TestCLIMain:
    """Test cases for the main CLI function."""

    def test_main_no_issues_found(self, temp_python_file, mock_analyze_file):
        """Test main function when no issues are found."""
        mock_analyze_file.return_value = []
        
        with patch('sys.argv', ['pyward', temp_python_file]), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        mock_analyze_file.assert_called_once_with(
            temp_python_file,
            run_optimization=True,
            run_security=True,
            verbose=False
        )
        
        output = fake_stdout.getvalue()
        assert "✅ No issues found" in output
        assert temp_python_file in output
        assert exc_info.value.code == 0

    def test_main_with_issues_found(self, temp_python_file, mock_analyze_file):
        """Test main function when issues are found."""
        mock_analyze_file.return_value = [
            "Line 1: Imported name 'os' is never used.",
            "Line 5: Use of exec() detected."
        ]
        
        with patch('sys.argv', ['pyward', temp_python_file]), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        output = fake_stdout.getvalue()
        assert "❌ Found 2 issue(s)" in output
        assert temp_python_file in output
        assert "1. Line 1: Imported name 'os'" in output
        assert "2. Line 5: Use of exec()" in output
        assert exc_info.value.code == 1

    @pytest.mark.parametrize("flag,expected_opt,expected_sec", [
        (['-o'], True, False),              # Optimization only
        (['--optimize'], True, False),      # Optimization only (long form)
        (['-s'], False, True),              # Security only
        (['--security'], False, True),      # Security only (long form)
        ([], True, True),                   # Default behavior (both)
    ])
    def test_main_flag_combinations(self, temp_python_file, mock_analyze_file,
                                   flag, expected_opt, expected_sec):
        """Test different flag combinations for optimization and security checks."""
        mock_analyze_file.return_value = []
        
        argv = ['pyward'] + flag + [temp_python_file]
        
        with patch('sys.argv', argv), \
             patch('sys.stdout', new=StringIO()):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        mock_analyze_file.assert_called_once_with(
            temp_python_file,
            run_optimization=expected_opt,
            run_security=expected_sec,
            verbose=False
        )
        assert exc_info.value.code == 0

    @pytest.mark.parametrize("verbose_flag", ['-v', '--verbose'])
    def test_main_verbose_flag(self, temp_python_file, mock_analyze_file, verbose_flag):
        """Test main function with verbose flags."""
        mock_analyze_file.return_value = ["Verbose: no issues found, but checks were performed."]
        
        with patch('sys.argv', ['pyward', verbose_flag, temp_python_file]), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        mock_analyze_file.assert_called_once_with(
            temp_python_file,
            run_optimization=True,
            run_security=True,
            verbose=True
        )
        
        output = fake_stdout.getvalue()
        assert "❌ Found 1 issue(s)" in output
        assert "Verbose: no issues found" in output
        assert exc_info.value.code == 1

    def test_main_combined_flags(self, temp_python_file, mock_analyze_file):
        """Test main function with combined flags."""
        mock_analyze_file.return_value = []
        
        with patch('sys.argv', ['pyward', '-o', '-v', temp_python_file]), \
             patch('sys.stdout', new=StringIO()):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        mock_analyze_file.assert_called_once_with(
            temp_python_file,
            run_optimization=True,
            run_security=False,
            verbose=True
        )
        assert exc_info.value.code == 0

    def test_main_no_filepath_provided(self):
        """Test main function when no filepath is provided."""
        with patch('sys.argv', ['pyward']), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        output = fake_stdout.getvalue()
        assert exc_info.value.code == 1
        assert "usage:" in output

    def test_main_file_not_found_error(self, mock_analyze_file):
        """Test main function when file doesn't exist."""
        nonexistent_file = "/nonexistent/path/test.py"
        mock_analyze_file.side_effect = FileNotFoundError()
        
        with patch('sys.argv', ['pyward', nonexistent_file]), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        output = fake_stdout.getvalue()
        assert "Error: File" in output
        assert "does not exist" in output
        assert exc_info.value.code == 1

    def test_main_general_exception(self, temp_python_file, mock_analyze_file):
        """Test main function when analyze_file raises a general exception."""
        mock_analyze_file.side_effect = Exception("Something went wrong")
        
        with patch('sys.argv', ['pyward', temp_python_file]), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        output = fake_stdout.getvalue()
        assert "Error analyzing" in output
        assert temp_python_file in output
        assert "Something went wrong" in output
        assert exc_info.value.code == 1

    def test_main_help_flag(self):
        """Test main function with -h/--help flag."""
        with patch('sys.argv', ['pyward', '-h']), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        output = fake_stdout.getvalue()
        assert "PyWard: CLI linter for Python" in output
        assert "optimization + security checks" in output
        assert exc_info.value.code == 0

    def test_main_mutually_exclusive_flags_error(self, temp_python_file):
        """Test main function with mutually exclusive flags."""
        with patch('sys.argv', ['pyward', '-o', '-s', temp_python_file]), \
             patch('sys.stderr', new=StringIO()) as fake_stderr:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # argparse should exit with error code 2 for invalid arguments
            assert exc_info.value.code == 2
            
        error_output = fake_stderr.getvalue()
        assert "not allowed" in error_output

    @pytest.mark.parametrize("issues_count", [1, 5, 25, 50, 100])
    def test_main_large_number_of_issues(self, temp_python_file, mock_analyze_file, 
                                        issues_count):
        """Test main function with varying numbers of issues."""
        issues = [f"Line {i}: Mock issue number {i}" for i in range(1, issues_count + 1)]
        mock_analyze_file.return_value = issues
        
        with patch('sys.argv', ['pyward', temp_python_file]), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        output = fake_stdout.getvalue()
        assert f"❌ Found {issues_count} issue(s)" in output
        assert f"{issues_count}. Line {issues_count}: Mock issue number {issues_count}" in output
        
        assert exc_info.value.code == 1

    def test_main_output_formatting(self, temp_python_file, mock_analyze_file):
        """Test that main function formats output correctly."""
        mock_analyze_file.return_value = [
            "Optimization issue here",
            "Security issue here"
        ]
        
        with patch('sys.argv', ['pyward', temp_python_file]), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        output = fake_stdout.getvalue()
        lines = output.strip().split('\n')
        
        # Check header line
        assert any("❌ Found 2 issue(s)" in line for line in lines)
        
        # Check issue formatting
        assert any("1. Optimization issue here" in line for line in lines)
        assert any("2. Security issue here" in line for line in lines)
        
        assert exc_info.value.code == 1

    def test_main_empty_issues_list(self, temp_python_file, mock_analyze_file):
        """Test main function with empty issues list."""
        mock_analyze_file.return_value = []
        
        with patch('sys.argv', ['pyward', temp_python_file]), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        output = fake_stdout.getvalue()
        assert "✅ No issues found" in output
        assert exc_info.value.code == 0

    def test_main_single_issue(self, temp_python_file, mock_analyze_file):
        """Test main function with exactly one issue."""
        mock_analyze_file.return_value = ["Line 5: Single issue found"]
        
        with patch('sys.argv', ['pyward', temp_python_file]), \
             patch('sys.stdout', new=StringIO()) as fake_stdout:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        output = fake_stdout.getvalue()
        assert "❌ Found 1 issue(s)" in output
        assert "1. Line 5: Single issue found" in output
        assert exc_info.value.code == 1

    def test_cli_module_execution(self):
        """Test CLI module execution - covers the if __name__ == '__main__' entry point"""
        
        result = subprocess.run(
            [sys.executable, '-m', 'pyward.cli', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert "PyWard: CLI linter for Python" in result.stdout

class TestCLIArgumentParsing:
    """Test cases for CLI argument parsing."""

    def test_argument_parser_configuration(self):
        """Test that argument parser is configured correctly."""
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
        args = parser.parse_args(['-o', 'test.py'])
        assert args.optimize is True
        assert args.security is False
        
        args = parser.parse_args(['-s', 'test.py'])
        assert args.optimize is False
        assert args.security is True
        
        args = parser.parse_args(['-v', 'test.py'])
        assert args.verbose is True

    @pytest.mark.parametrize("invalid_args", [
        ['-o', '-s', 'test.py'],           # Mutually exclusive flags
        ['--optimize', '--security', 'test.py'],  # Long form mutually exclusive
    ])
    def test_invalid_argument_combinations(self, invalid_args):
        """Test that invalid argument combinations are rejected."""
        with patch('sys.argv', ['pyward'] + invalid_args), \
             patch('sys.stderr', new=StringIO()):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_long_flag_names(self, temp_python_file, mock_analyze_file):
        """Test main function with long flag names."""
        mock_analyze_file.return_value = []
        
        with patch('sys.argv', ['pyward', '--optimize', '--verbose', temp_python_file]), \
             patch('sys.stdout', new=StringIO()):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        mock_analyze_file.assert_called_once_with(
            temp_python_file,
            run_optimization=True,
            run_security=False,
            verbose=True
        )
        assert exc_info.value.code == 0

    def test_default_behavior(self, temp_python_file, mock_analyze_file):
        """Test main function default behavior (both optimization and security enabled)."""
        mock_analyze_file.return_value = []
        
        with patch('sys.argv', ['pyward', temp_python_file]), \
             patch('sys.stdout', new=StringIO()):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
        # Default should be both optimization and security enabled
        mock_analyze_file.assert_called_once_with(
            temp_python_file,
            run_optimization=True,
            run_security=True,
            verbose=False
        )
        assert exc_info.value.code == 0


