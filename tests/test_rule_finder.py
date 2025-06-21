import ast
import tempfile
import textwrap
from pathlib import Path
from typing import List
from unittest import mock

import pytest

from pyward.rule_finder import extract_function_info, find_rule_files


def test_extract_function_info_basic_warning():
    code = textwrap.dedent(
        """
        def example():
            format_optimization_warning("This is an optimization issue.", 42, "CVE-1234")
    """
    )
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w+", delete=False
    ) as temp_file:
        temp_file.write(code)
        temp_file.flush()
        temp_path = temp_file.name

    result = extract_function_info(temp_path)
    assert len(result) == 1
    assert "optimization issue" in result[0][1]


def test_extract_function_info_no_warning():
    code = textwrap.dedent(
        """
        def example():
            print("This is a normal print.")
    """
    )
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w+", delete=False
    ) as temp_file:
        temp_file.write(code)
        temp_file.flush()
        temp_path = temp_file.name

    result = extract_function_info(temp_path)
    assert result == []


@pytest.fixture
def mock_rule_package(tmp_path):
    """
    Creates a fake rule package with two Python files for testing.
    """
    mock_package = tmp_path / "pyward" / "optimization" / "rules"
    mock_package.mkdir(parents=True, exist_ok=True)

    file1 = mock_package / "rule1.py"
    file1.write_text(
        "def f():\n"
        '    format_optimization_warning("Unused import.", 12, "CVE-1234")\n'
    )

    file2 = mock_package / "rule2.py"
    file2.write_text("def f():\n" "    pass\n")

    init_file = mock_package / "__init__.py"
    init_file.write_text("")

    return mock_package, [file1.name]


def test_find_rule_files(monkeypatch, mock_rule_package):
    mock_path, expected_files = mock_rule_package

    class DummyFiles:
        def __init__(self, path: Path):
            self._path = path

        def glob(self, pattern):
            return list(self._path.glob(pattern))

    class DummyResources:
        @staticmethod
        def files(package_path):
            return DummyFiles(mock_path)

        @staticmethod
        def as_file(path):
            # context manager returning the path directly
            class Context:
                def __enter__(self):
                    return path

                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass

            return Context()

    monkeypatch.setattr("importlib.resources.files", DummyResources.files)
    monkeypatch.setattr("importlib.resources.as_file", DummyResources.as_file)

    result = find_rule_files()
    assert sorted(result) == sorted(expected_files)
