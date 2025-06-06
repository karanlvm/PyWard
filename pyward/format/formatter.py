from colorama import Fore, Back, Style


def format_security_warning(message: str, lineno: int, cve_id: str = '') -> str:
    cve_format = f"{Fore.RED}[{cve_id}]{Style.RESET_ALL}" if cve_id != '' else ''
    return (
        f"{Fore.WHITE}{Back.RED}[Security]{Style.RESET_ALL}"
        f"{cve_format}"
        f" Line {lineno}: {message}"
    )


def format_optimization_warning(message: str, lineno: int) -> str:
    return (
        f"{Fore.WHITE}{Back.YELLOW}[Optimization]{Style.RESET_ALL} "
        f"Line {lineno}: {message}"
    )
