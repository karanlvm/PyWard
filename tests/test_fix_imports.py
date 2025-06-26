from textwrap import dedent

from pyward.fixer.fix_imports import ImportFixer


def test_remove_single_unused_import():
    source = dedent(
        """
        import os
        import sys
        
        print(sys.version)
    """
    ).lstrip()

    expected = dedent(
        """
        import sys
        
        print(sys.version)
    """
    ).lstrip()

    fixer = ImportFixer(source)
    changed, new_source, msgs = fixer.fix()

    assert changed
    assert new_source == expected
    assert msgs == ["import os deleted"]


def test_remove_unused_name_from_multi_import():
    source = dedent(
        """
        from typing import List, Dict, Union
        
        x: List[int] = []
        y: Dict[str, int] = {}
    """
    ).lstrip()

    expected = dedent(
        """
        from typing import List, Dict
        
        x: List[int] = []
        y: Dict[str, int] = {}
    """
    ).lstrip()


    fixer = ImportFixer(source)
    changed, new_source, msgs = fixer.fix()

    assert changed
    assert new_source == expected
    assert msgs == ["from typing import Union deleted"]


def test_remove_entire_from_import():
    source = dedent(
        """
        from pathlib import Path
        import sys
        
        print(sys.version)
    """
    ).lstrip()

    expected = dedent(
        """
        import sys
        
        print(sys.version)
    """
    ).lstrip()

    fixer = ImportFixer(source)
    changed, new_source, msgs = fixer.fix()

    assert changed
    assert new_source == expected
    assert msgs == ["from pathlib import Path deleted"]


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

    expected = dedent(
        """
        from typing import (
            List,
            Dict
        )
        
        x: List[int] = []
        y: Dict[str, int] = {}
    """
    ).lstrip()

    
    fixer = ImportFixer(source)
    changed, new_source, msgs = fixer.fix()

    assert changed
    assert new_source == expected
    assert msgs[0] == "from typing import Union deleted"
    assert msgs[1] == "from typing import Optional deleted"


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
    changed, new_source, msgs = fixer.fix()

    assert not changed
    assert new_source == source
    assert msgs == []


def test_handle_alias_imports():
    source = dedent(
        """
        from os import path as p, getenv as ge
        
        print(p.exists('/tmp'))
    """
    ).lstrip()

    expected = dedent(
        """
        from os import path as p
        
        print(p.exists('/tmp'))
    """
    ).lstrip()

    fixer = ImportFixer(source)
    changed, new_source, msgs = fixer.fix()

    assert changed
    assert new_source == expected
    assert msgs == ["from os import getenv as ge deleted"]


def test_middle_item_removed():
    source = """
import os, typing, sys

print(os.path.basename(__file__))
print(sys.argv)
"""
    
    expected = """
import os, sys

print(os.path.basename(__file__))
print(sys.argv)
"""
    
    fixer = ImportFixer(source)
    changed, new_source, msgs = fixer.fix()

    assert changed == True
    assert new_source == expected
    assert msgs == ["import typing deleted"]

def test_from_clause_middle_item_removed():
    source = """
from typing import List, Set, Tuple

l: List[int] = []
t: Tuple[int, int] = (1, 2)
"""
    
    expected = """
from typing import List, Tuple

l: List[int] = []
t: Tuple[int, int] = (1, 2)
"""
    
    fixer = ImportFixer(source)
    changed, new_source, msgs = fixer.fix()
    
    assert changed == True
    assert new_source == expected
    assert msgs == ["from typing import Set deleted"]

def test_multiline_from_clause_middle_item_removed():
    source = """
from typing import (
    List,
    Union, Set, Optional,
    Tuple,
)

l: List[int] = []
t: Tuple[int, int] = (1, 2)
u: Union[int, str] = "123"
o: Optional[str] = "abc"
"""
    
    expected = """
from typing import (
    List,
    Union,
    Optional,
    Tuple
)

l: List[int] = []
t: Tuple[int, int] = (1, 2)
u: Union[int, str] = "123"
o: Optional[str] = "abc"
"""
    
    fixer = ImportFixer(source)
    changed, new_source, msgs = fixer.fix()

    assert changed == True
    assert new_source == expected
    assert msgs == ["from typing import Set deleted"]
