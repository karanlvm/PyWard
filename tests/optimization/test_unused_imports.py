import ast
from colorama import Fore, Back, Style
from pyward.optimization.rules.unused_imports import check_unused_imports, fix_unused_imports

OPT = f"{Fore.WHITE}{Back.YELLOW}[Optimization]{Style.RESET_ALL}"

def test_single_unused():
    src = "import os\nimport sys\nprint(os.getcwd())\n"
    issues = check_unused_imports(ast.parse(src))
    assert len(issues) == 1
    msg = issues[0]
    assert msg.startswith(OPT)
    assert "Imported name 'sys' is never used" in msg

def test_no_unused():
    src = "import math\nx = math.pi\n"
    assert check_unused_imports(ast.parse(src)) == []

def test_remove_single_unused_import():
    source = """
import os
import sys

print(sys.version)
"""
    
    expected = """
import sys

print(sys.version)
"""
    fixed = fix_unused_imports(source)
    assert fixed[0] == True
    assert fixed[1] == expected
    assert fixed[2] == ["import os deleted"]


def test_remove_unused_name_from_multi_import():
    source = """
from typing import List, Dict, Union

x: List[int] = []
y: Dict[str, int] = {}
"""
    
    expected = """
from typing import List, Dict

x: List[int] = []
y: Dict[str, int] = {}
"""
    
    fixed = fix_unused_imports(source)
    assert fixed[0] == True
    assert fixed[1] == expected
    assert fixed[2] == ["from typing import Union deleted"]

def test_remove_entire_from_import():
    source = """
from pathlib import Path
import sys

print(sys.version)
"""
    
    expected = """
import sys

print(sys.version)
"""
    
    fixed = fix_unused_imports(source)
    assert fixed[0] == True
    assert fixed[1] == expected
    assert fixed[2] == ["from pathlib import Path deleted"]

def test_preserve_multiline_import():
    source = """
from typing import (
    List,
    Dict,  # we need this
    Union,
    Optional,
)

x: List[int] = []
y: Dict[str, int] = {}
"""

    expected = """
from typing import (
    List,
    Dict
)

x: List[int] = []
y: Dict[str, int] = {}
"""
    
    fixed = fix_unused_imports(source)
    assert fixed[0] == True
    assert fixed[1] == expected
    assert fixed[2][0] == "from typing import Union deleted"
    assert fixed[2][1] == "from typing import Optional deleted"

def test_no_changes_if_all_imports_used():
    source = """
import sys
from os import path

print(sys.version)
print(path.exists('/tmp'))
"""
    fixed = fix_unused_imports(source)
    assert fixed[0] == False
    assert fixed[1] == source
    assert fixed[2] == []

def test_handle_alias_imports():
    source = """
from os import path as p, getenv as ge

print(p.exists('/tmp'))
"""
    
    expected = """
from os import path as p

print(p.exists('/tmp'))
"""
    
    fixed = fix_unused_imports(source)
    assert fixed[0] == True
    assert fixed[1] == expected
    assert fixed[2] == ["from os import getenv as ge deleted"]

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
    
    fixed = fix_unused_imports(source)
    assert fixed[0] == True
    assert fixed[1] == expected
    assert fixed[2] == ["import typing deleted"]

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
    
    fixed = fix_unused_imports(source)
    assert fixed[0] == True
    assert fixed[1] == expected
    assert fixed[2] == ["from typing import Set deleted"]

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
    
    fixed = fix_unused_imports(source)
    assert fixed[0] == True
    assert fixed[1] == expected
    assert fixed[2] == ["from typing import Set deleted"]