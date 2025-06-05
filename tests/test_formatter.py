import pytest
from colorama import Fore

from pyward.format.formatter import (
    format_security_warning,
    format_optimization_warning,
)

OPTIMIZATION_COLOR = Fore.YELLOW
SECURITY_COLOR = Fore.RED
OPTIMIZATION_LABEL = f"{OPTIMIZATION_COLOR}[Optimization]{Fore.RESET}"
SECURITY_LABEL = f"{SECURITY_COLOR}[Security]{Fore.RESET}"


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
        f"{SECURITY_LABEL}[{cve_id}] Line {lineno}: {msg}"
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
