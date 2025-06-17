# triggers check_unused_imports
import os
import sys
from typing import (
    List,
    Set,
    Tuple,
)

def foo():
    print(os.getcwd())
    s: Set = set([])
