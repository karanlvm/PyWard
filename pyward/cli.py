import argparse
import sys
from pyward.analyzer import analyze_file
from pyward.fixer import fix_file


def main():
    parser = argparse.ArgumentParser(
        prog="pyward",
        description="PyWard: CLI linter for Python (optimization + security checks)",
    )

    # Mutually exclusive flags: -o (optimization only) vs. -s (security only)
    group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Automatically fix issues when possible (currently supports: unused imports).",
    )
    group.add_argument(
        "-o",
        "--optimize",
        action="store_true",
        help="Run only optimization checks (unused imports, unreachable code).",
    )
    group.add_argument(
        "-s",
        "--security",
        action="store_true",
        help="Run only security checks (unsafe calls, CVE-based rules).",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed warnings and suggestions even if no issues are found.",
    )

    parser.add_argument(
        "filepath",
        nargs="?",
        help="Path to the Python file you want to analyze (e.g., myscript.py).",
    )

    args = parser.parse_args()

    # If no filepath is provided, show help and exit
    if not args.filepath:
        parser.print_help()
        sys.exit(1)    # Determine which checks to run
    run_opt = True
    run_sec = True
    if args.optimize:
        run_opt = True
        run_sec = False
    elif args.security:
        run_opt = False
        run_sec = True

    try:
        issues = analyze_file(
            args.filepath,
            run_optimization=run_opt,
            run_security=run_sec,
            verbose=args.verbose,
        )

        if not issues:
            print(f"✅ No issues found in {args.filepath}")
            sys.exit(0)
        else:
            print(f"❌ Found {len(issues)} issue(s) in {args.filepath}:")
            for i, issue in enumerate(issues, start=1):
                print(f"  {i}. {issue}")
            
            if args.fix:
                print("\nApplying fixes...")
                fix_file(args.filepath, write=True)
                print("✅ Fixes applied successfully")
                # Re-run analysis to verify fixes
                remaining_issues = analyze_file(
                    args.filepath,
                    run_optimization=run_opt,
                    run_security=run_sec,
                    verbose=args.verbose,
                )
                if remaining_issues:
                    print(f"\n⚠️ {len(remaining_issues)} issue(s) remain unfixed:")
                    for i, issue in enumerate(remaining_issues, start=1):
                        print(f"  {i}. {issue}")
                    sys.exit(1)
                else:
                    print("✅ All fixable issues were resolved")
                    sys.exit(0)
            else:
                sys.exit(1)

    except FileNotFoundError:
        print(f"Error: File '{args.filepath}' does not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing '{args.filepath}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
