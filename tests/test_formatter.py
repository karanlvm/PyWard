import pytest
from colorama import Fore, Back, Style

from pyward.format.formatter import (
    format_security_warning,
    format_optimization_warning,
)

OPTIMIZATION_COLOR = f"{Fore.WHITE}{Back.YELLOW}"
SECURITY_COLOR = f"{Fore.WHITE}{Back.RED}"
CVE_COLOR = f"{Fore.RED}"
OPTIMIZATION_LABEL = f"{OPTIMIZATION_COLOR}[Optimization]{Style.RESET_ALL}"
SECURITY_LABEL = f"{SECURITY_COLOR}[Security]{Style.RESET_ALL}"


def test_format_security_warning_with_cve_id():
    msg = "Unsafe eval usage detected."
    lineno = 42
    cve_id = "CVE-2023-12345"
    warning = format_security_warning(
        msg,
        lineno,
        cve_id
    )
    assert warning == (
        f"{SECURITY_LABEL}{CVE_COLOR}[{cve_id}]{Style.RESET_ALL} Line {lineno}: {msg}"
    )


def test_format_security_warning_without_cve_id():
    msg = "Unsafe eval usage detected."
    lineno = 42
    warning = format_security_warning(
        msg,
        lineno
    )
    assert warning == (
        f"{SECURITY_LABEL} Line {lineno}: {msg}"
    )


def test_format_optimization_warning():
    msg = "Unused import detected."
    lineno = 10
    warning = format_optimization_warning(
        msg,
        lineno
    )
    assert warning == (
        f"{OPTIMIZATION_LABEL} Line {lineno}: {msg}"
    )


if __name__ == "__main__":
    pytest.main()
