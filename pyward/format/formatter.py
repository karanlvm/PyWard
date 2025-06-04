from colorama import Fore, Back, Style
from typing import Optional


def format_security_warning(message: str, lineno: int, cve_id: Optional[str] = None) -> str:
    return f"[Security]{'[' + cve_id + ']' if cve_id is not None else ''} Line {lineno}: {message}"

def format_optimization_warning(message: str, lineno: int) -> str:
    return f"[Optimization] Line {lineno}: {message}"
