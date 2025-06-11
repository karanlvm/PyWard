# pyward/cli.py

import os
import sys
import re
import argparse

from pyward.analyzer import analyze_file
from pyward.fixer    import fix_file


SUPPRESS_TOKEN = "pyward: suppress"

# PYWARD banner
BANNER = r"""
______      _    _               _ 
| ___ \    | |  | |             | |
| |_/ /   _| |  | | __ _ _ __ __| |
|  __/ | | | |/\| |/ _` | '__/ _` |
| |  | |_| \  /\  / (_| | | | (_| |
\_|   \__, |\/  \/ \__,_|_|  \__,_|
       __/ |                       
      |___/                        
"""

def parse_warning_meta(warning: str):
    """
    Extract (rule_id, lineno) from a warning string.
    We still parse rule_id for display, but we only suppress generically.
    """
    # line number
    m_line = re.search(r"Line\s+(\d+)", warning, re.IGNORECASE)
    lineno = int(m_line.group(1)) if m_line else None

    # CVE-based ID?
    m_cve = re.search(r"(CVE-\d{4}-\d+)", warning)
    if m_cve:
        return m_cve.group(1), lineno

    # optimization tag after "[Optimization]"
    m_opt = re.search(r"\[Optimization\]\s+([\w-]+)", warning)
    if m_opt:
        return m_opt.group(1), lineno

    return None, lineno


def is_suppressed(lines, lineno):
    if lineno is None:
        return False

    for ln in (lineno, lineno - 1):
        if ln < 1 or ln > len(lines):
            continue
        parts = lines[ln - 1].split("#", 1)
        if len(parts) < 2:
            continue
        comment = parts[1].strip().lower()
        if comment.startswith(SUPPRESS_TOKEN):
            return True

    return False



def main():
    # 1) Show banner
    print(BANNER)

    # 2) Arg parsing
    parser = argparse.ArgumentParser(
        prog="pyward",
        description="PyWard: CLI linter for Python (optimization + security checks)"
    )

    parser.add_argument(
        "-f", "--fix",
        action="store_true",
        help="Auto-fix issues when possible (currently: unused-imports)."
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-o", "--optimize",
        action="store_true",
        help="Run only optimization checks."
    )
    group.add_argument(
        "-s", "--security",
        action="store_true",
        help="Run only security checks."
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed warnings even if none are found."
    )

    parser.add_argument(
        "filepath",
        nargs="?",
        help="Path to the Python file to analyze."
    )

    args = parser.parse_args()
    if not args.filepath:
        parser.print_help()
        sys.exit(1)

    path = args.filepath
    if not os.path.isfile(path):
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)

    run_opt = not args.security
    run_sec = not args.optimize

    try:
        # 3) Analyze
        issues = analyze_file(
            path,
            run_optimization=run_opt,
            run_security=run_sec,
            verbose=args.verbose
        )

        # 4) Fix-mode
        if args.fix:
            print("🔧 Applying fixes...")
            fix_file(path, write=True)
            issues = analyze_file(
                path,
                run_optimization=run_opt,
                run_security=run_sec,
                verbose=args.verbose
            )
            if not issues:
                print("✅ All fixable issues resolved.")
                sys.exit(0)
            else:
                print(f"⚠️  {len(issues)} issue(s) remain after fix:")
                for i, w in enumerate(issues, 1):
                    print(f"  {i}. {w}")
                sys.exit(1)

        # 5) Load source for suppression
        with open(path, "r") as f:
            source_lines = f.readlines()

        # 6) Filter: no --disable; only inline suppress
        filtered = []
        for w in issues:
            _, lineno = parse_warning_meta(w)
            if is_suppressed(source_lines, lineno):
                continue
            filtered.append(w)

        # 7) Report
        if not filtered:
            msg = "✅ No issues found"
            if args.verbose:
                msg += " (verbose)"
            print(f"{msg} in {path}")
            sys.exit(0)

        print(f"❌ Found {len(filtered)} issue(s) in {path}:")
        for i, w in enumerate(filtered, 1):
            print(f"  {i}. {w}")
        sys.exit(1)

    except Exception as e:
        print(f"Error analyzing '{path}': {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
