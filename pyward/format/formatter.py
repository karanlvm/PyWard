from colorama import Fore


def format_security_warning(message: str, lineno: int, cve_id: str = '') -> str:
    return (
        f"{Fore.RED}[Security]{Fore.RESET}"
        f"{'[' + cve_id + ']' if cve_id != '' else ''} Line {lineno}: {message}"
    )


def format_optimization_warning(message: str, lineno: int) -> str:
    return (
        f"{Fore.YELLOW}[Optimization]{Fore.RESET} "
        f"Line {lineno}: {message}"
    )
