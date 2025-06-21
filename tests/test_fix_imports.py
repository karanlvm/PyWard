from textwrap import dedent

import pytest

from pyward.fixer.fix_imports import ImportFixer


def test_remove_single_unused_import():
    source = dedent(
        """
        import os
        import sys
        
        print(sys.version)
    """
    ).lstrip()

    fixer = ImportFixer(source)
    result = fixer.fix()

    expected = dedent(
        """
        import sys
        
        print(sys.version)
    """
    ).lstrip()

    assert result == expected


def test_remove_unused_name_from_multi_import():
    source = dedent(
        """
        from typing import List, Dict, Union
        
        x: List[int] = []
        y: Dict[str, int] = {}
    """
    ).lstrip()

    fixer = ImportFixer(source)
    result = fixer.fix()

    expected = dedent(
        """
        from typing import List, Dict
        
        x: List[int] = []
        y: Dict[str, int] = {}
    """
    ).lstrip()

    assert result == expected


def test_handle_trailing_comma():
    source = dedent(
        """
        from os import path, getenv,
        
        print(path.exists('/tmp'))
    """
    ).lstrip()

    fixer = ImportFixer(source)
    result = fixer.fix()

    expected = dedent(
        """
        from os import path
        
        print(path.exists('/tmp'))
    """
    ).lstrip()

    assert result == expected


def test_remove_entire_from_import():
    source = dedent(
        """
        from pathlib import Path
        import sys
        
        print(sys.version)
    """
    ).lstrip()

    fixer = ImportFixer(source)
    result = fixer.fix()

    expected = dedent(
        """
        import sys
        
        print(sys.version)
    """
    ).lstrip()

    assert result == expected


def test_preserve_multiline_import():
    source = dedent(
        """
        from typing import (
            List,
            Dict,  # we need this
            Union,
            Optional,
        )
        
        x: List[int] = []
        y: Dict[str, int] = {}
    """
    ).lstrip()

    fixer = ImportFixer(source)
    result = fixer.fix()

    expected = dedent(
        """
        from typing import (
            List,
            Dict,  # we need this
        )
        
        x: List[int] = []
        y: Dict[str, int] = {}
    """
    ).lstrip()

    assert result == expected


def test_no_changes_if_all_imports_used():
    source = dedent(
        """
        import sys
        from os import path
        
        print(sys.version)
        print(path.exists('/tmp'))
    """
    ).lstrip()

    fixer = ImportFixer(source)
    result = fixer.fix()

    assert result == source


def test_handle_alias_imports():
    source = dedent(
        """
        from os import path as p, getenv as ge
        
        print(p.exists('/tmp'))
    """
    ).lstrip()

    fixer = ImportFixer(source)
    result = fixer.fix()

    expected = dedent(
        """
        from os import path as p
        
        print(p.exists('/tmp'))
    """
    ).lstrip()

    assert result == expected
