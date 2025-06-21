#!/usr/bin/env python3
import os
import argparse
import sys
from pathlib import Path
from typing import Tuple

from pyward.optimization.run import (
    run_all_optimization_checks,
    run_all_optimization_fixes,
)
from pyward.security.run import (
    run_all_security_checks,
    run_all_security_fixes,
)
from pyward.rule_finder import find_rule_files

from pyward import __version__ as VERSION

def fix_file(
    source: str,
    run_opt: bool,
    run_sec: bool,
    skip_list: list[str],
) -> Tuple[bool, str, list[str]]:
    """
    Fix file according to fixable optimization and security rules.
    Returns (file_ever_changed, fixed_source, fix_messages).
    """
    current_source = source
    file_ever_changed = False
    all_fixes: list[str] = []

    if run_opt:
        changed, current_source, fixes = run_all_optimization_fixes(
            current_source, skip_list
        )
        file_ever_changed = file_ever_changed or changed
        all_fixes.extend(fixes)

    if run_sec:
        changed, current_source, fixes = run_all_security_fixes(
            current_source, skip_list
        )
        file_ever_changed = file_ever_changed or changed
        all_fixes.extend(fixes)

    return file_ever_changed, current_source, all_fixes


def analyze_file(
    source: str,
    run_optimization: bool,
    run_security: bool,
    skip_list: list[str],
) -> list[str]:
    """
    Run optimization and/or security checks on the given source string.
    Returns a list of issue messages.
    """
    issues: list[str] = []

    if run_optimization:
        issues.extend(
            run_all_optimization_checks(source, skip=skip_list)
        )

    if run_security:
        issues.extend(
            run_all_security_checks(source, skip=skip_list)
        )

    return issues


class ArgumentParser1(argparse.ArgumentParser):
    def error(self, message):
        # 🐛 FIX: now catches missing required args and prints to stdout
        if "the following arguments are required" in message:
            output_stream = sys.stdout
            print(self.format_usage().strip(), file=output_stream)
            print(f"{self.prog}: error: {message}", file=output_stream)
            sys.exit(1)
        super().error(message)


def list_checks():
    """
    Finds and prints a list of all available check names.
    """
    available = find_rule_files()
    if not available:
        print("No checks found.")
        return

    print("\nAvailable Checks:")
    for f in available:
        print(f"- {os.path.splitext(f)[0]}")


def main():
    if "--list" in sys.argv or "-l" in sys.argv:
        list_checks()
        sys.exit(0)

    # Only show ASCII logo when running in a real terminal
    if sys.stdout.isatty():
        print(r"""
 ____      __        __            _ 
|  _ \ _   \ \      / /_ _ _ __ __| |
| |_) | | | \ \ /\ / / _` | '__/ _` |
|  __/| |_| |\ V  V / (_| | | | (_| |
|_|    \__, | \_/\_/ \__,_|_|  \__,_|
        |___/                         
        PyWard: fast, zero-config Python linting
""")

    parser = ArgumentParser1(
        prog="pyward",
        description="PyWard: CLI linter for Python (optimization + security checks)",
    )
    parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Auto-fix optimization and security issues (writes file in place).",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all available checks",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively lint all .py files under a directory.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-o",
        "--optimize",
        action="store_true",
        help="Only run optimization checks.",
    )
    group.add_argument(
        "-s",
        "--security",
        action="store_true",
        help="Only run security checks.",
    )
    parser.add_argument(
        "-k",
        "--skip-checks",
        help="Comma-separated list of rule names (without 'check_' prefix) to skip.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output, even if no issues.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show PyWard version and exit.",
    )
    parser.add_argument(
        "filepath",
        type=Path,
        nargs="?",
        help="Path to the Python file or directory to analyze.",
    )

    args = parser.parse_args()

    if args.version:
        print(f"PyWard Version {VERSION}")
        sys.exit(0)

    if args.filepath is None:
        parser.error("the following arguments are required: filepath")

    # Build list of files
    paths: list[Path] = []
    if args.filepath.is_dir():
        if not args.recursive:
            print(
                f"Error: {args.filepath} is a directory (use -r to recurse)",
                file=sys.stderr,
            )
            sys.exit(1)
        paths = list(args.filepath.rglob("*.py"))
    else:
        paths = [args.filepath]

    if not paths:
        print(f"No Python files found in {args.filepath}", file=sys.stderr)
        sys.exit(1)

    # Prepare skip list
    skip_list: list[str] = []
    if args.skip_checks:
        for name in args.skip_checks.split(","):
            nm = name.strip()
            if not nm.startswith("check_"):
                nm = f"check_{nm}"
            skip_list.append(nm)

    run_opt = not args.security
    run_sec = not args.optimize
    any_issues = False

    for path in paths:
        file_str = str(path)

        try:
            source = Path(file_str).read_text(encoding="utf-8")

            # apply fixes first, if requested
            if args.fix:
                changed, new_src, fixes = fix_file(
                    source, run_opt, run_sec, skip_list
                )
                if changed:
                    print(f"\n🔧 Applied {len(fixes)} fix(es) to {file_str}")
                    for idx, msg in enumerate(fixes, 1):
                        print(f"{idx}. {msg}")
                    with open(file_str, "w", encoding="utf-8") as f:
                        f.write(new_src)
                    source = new_src

            issues = analyze_file(
                source,
                run_optimization=run_opt,
                run_security=run_sec,
                skip_list=skip_list,
            )

        except FileNotFoundError:
            print(f"Error: File '{file_str}' not found", file=sys.stderr)
            any_issues = True
            continue
        except Exception as e:
            print(f"Error analyzing {file_str}: {e}", file=sys.stderr)
            any_issues = True
            continue

        # report
        if not issues:
            if args.verbose:
                print(f"✅ No issues found in {file_str} (verbose)")
            else:
                print(f"✅ No issues found in {file_str}")
        else:
            any_issues = True
            print(f"\n❌ Found {len(issues)} issue(s) in {file_str}")
            for idx, msg in enumerate(issues, 1):
                print(f"{idx}. {msg}")

    sys.exit(1 if any_issues else 0)


if __name__ == "__main__":
    main()
