import pytest
import tempfile
import os
from unittest.mock import patch
from pyward.analyzer import analyze_file

@pytest.fixture
def temp_python_file():
    """temporary Python file"""
    temp_dir = tempfile.mkdtemp()
    
    def _create_file(content: str, filename: str = "test.py") -> str:
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath
    
    yield _create_file

    for filename in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, filename))
    os.rmdir(temp_dir)

@pytest.fixture
def mock_rules():
    """mock optimization and security rule checkers function."""
    with patch('pyward.analyzer.run_all_optimization_checks') as mock_opt, \
         patch('pyward.analyzer.run_all_security_checks') as mock_sec:
        mock_opt.return_value = []
        mock_sec.return_value = []
        yield mock_opt, mock_sec

def test_analyze_file_valid_python_file(temp_python_file, mock_rules):
    """Test analyzing a valid Python file with no issues."""
    content = "print('test')"
    filepath = temp_python_file(content)
    mock_opt, mock_sec = mock_rules
    
    issues = analyze_file(filepath)
    
    assert issues == []
    mock_opt.assert_called_once()
    mock_sec.assert_called_once()

@pytest.mark.parametrize("run_optimization,run_security,expected_calls", [
    (True, True, (1, 1)),    # Both enabled
    (True, False, (1, 0)),   # Only optimization
    (False, True, (0, 1)),   # Only security
    (False, False, (0, 0)),  # Both disabled
])
def test_analyze_file_rule_combinations(temp_python_file, mock_rules, 
                                       run_optimization, run_security, expected_calls):
    """Test different combinations of optimization and security rule execution."""
    content = "print('test')"
    filepath = temp_python_file(content)
    mock_opt, mock_sec = mock_rules
    
    analyze_file(filepath, run_optimization=run_optimization, run_security=run_security)
    
    assert mock_opt.call_count == expected_calls[0]
    assert mock_sec.call_count == expected_calls[1]

@pytest.mark.parametrize("verbose,has_issues,expected_verbose_message", [
    (True, False, True),   # Verbose mode, no issues -> should show verbose message
    (True, True, False),   # Verbose mode, has issues -> should not show verbose message
    (False, False, False), # Not verbose, no issues -> should not show verbose message
    (False, True, False),  # Not verbose, has issues -> should not show verbose message
])
def test_analyze_file_verbose_mode(temp_python_file, verbose, has_issues, expected_verbose_message):
    """Test verbose mode behavior with different scenarios."""
    content = "print('test')"
    filepath = temp_python_file(content)
    
    issues_to_return = ["Line 1: Some issue"] if has_issues else []
    
    with patch('pyward.analyzer.run_all_optimization_checks', return_value=issues_to_return), \
         patch('pyward.analyzer.run_all_security_checks', return_value=[]):
        
        issues = analyze_file(filepath, verbose=verbose)
        
    if expected_verbose_message:
        assert len(issues) == 1
        assert "Verbose: no issues found" in issues[0]
    elif has_issues:
        assert len(issues) == 1
        assert "Some issue" in issues[0]
    else:
        assert len(issues) == 0


def test_analyze_file_syntax_error(temp_python_file):
    """Test analyzing a file with syntax errors."""
    content = '''
def invalid_syntax(
    print("missing closing parenthesis")
'''
    filepath = temp_python_file(content)
    
    issues = analyze_file(filepath)
    
    assert len(issues) == 1
    assert "SyntaxError" in issues[0]
    assert filepath in issues[0]


def test_analyze_file_nonexistent_file():
    """Test analyzing a non-existent file."""
    nonexistent_path = "/nonexistent/path/test.py"
    
    with pytest.raises(FileNotFoundError):
        analyze_file(nonexistent_path)

def test_analyze_file_encoding_error():
    """Test analyzing a file with encoding issues."""
    temp_dir = tempfile.mkdtemp()
    filepath = os.path.join(temp_dir, "test_encoding.py")
    
    try:
        # Create a file with invalid UTF-8 encoding
        with open(filepath, "wb") as f:
            f.write(b'\xff\xfe# This is not valid UTF-8\n')
        
        with pytest.raises(UnicodeDecodeError):
            analyze_file(filepath)
    finally:
        os.remove(filepath)
        os.rmdir(temp_dir)

@pytest.mark.parametrize("exception_source,error_message", [
    ("optimization", "Optimization error"),
    ("security", "Security error"),
])
def test_analyze_file_rule_checker_exceptions(temp_python_file, exception_source, error_message):
    """Test behavior when rule checkers raise exceptions."""
    content = "import os"
    filepath = temp_python_file(content)
    
    if exception_source == "optimization":
        with patch('pyward.analyzer.run_all_optimization_checks', 
                  side_effect=Exception(error_message)):
            with pytest.raises(Exception, match=error_message):
                analyze_file(filepath)
    else:
        with patch('pyward.analyzer.run_all_optimization_checks', return_value=[]), \
             patch('pyward.analyzer.run_all_security_checks', 
                  side_effect=Exception(error_message)):
            with pytest.raises(Exception, match=error_message):
                analyze_file(filepath)

def test_analyze_file_mixed_issues(temp_python_file):
    """Test analyzing a file with both optimization and security issues."""
    content = '''
import numpy
exec("dangerous_code")
'''
    filepath = temp_python_file(content)
    

    issues = analyze_file(filepath)
        
    assert len(issues) == 2
    assert any("numpy" in issue for issue in issues)
    assert any("exec()" in issue for issue in issues)


@pytest.mark.parametrize("file_extension", [".py", ".pyx", ".pyi"])
def test_analyze_file_different_extensions(temp_python_file, file_extension):
    """Test analyzing files with different Python-related extensions."""
    content = "print('test')"
    filepath = temp_python_file(content, f"test{file_extension}")
    
    issues = analyze_file(filepath)
    
    assert issues == []


def test_analyze_file_source_code_passed_to_optimization_rules(temp_python_file):
    """Test that source code (not AST) is passed to optimization rules."""
    content = "print('test')"
    filepath = temp_python_file(content)
    
    with patch('pyward.analyzer.run_all_optimization_checks') as mock_opt, \
         patch('pyward.analyzer.run_all_security_checks', return_value=[]):
        
        analyze_file(filepath)
        
        # Verify that run_all_optimization_checks was called with source code string
        mock_opt.assert_called_once()
        args = mock_opt.call_args[0]
        assert len(args) == 1
        assert isinstance(args[0], str)
        assert "print('test')" in args[0]

def test_analyze_file_ast_passed_to_security_rules(temp_python_file):
    """Test that AST (not source code) is passed to security rules."""
    content = "print('test')"
    filepath = temp_python_file(content)
    
    with patch('pyward.analyzer.run_all_optimization_checks', return_value=[]), \
         patch('pyward.analyzer.run_all_security_checks') as mock_sec:
        
        analyze_file(filepath)
        
        # Verify that run_all_security_checks was called with AST
        mock_sec.assert_called_once()
        args = mock_sec.call_args[0]
        assert len(args) == 1
        # AST objects have specific attributes
        assert hasattr(args[0], 'body')  # AST modules have a body attribute