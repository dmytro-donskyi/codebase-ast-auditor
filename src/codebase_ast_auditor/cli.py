"""CLI interface for running codebase-ast-auditor."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analyzer import CodebaseAnalyzer
from .scanner import FileScanner


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="codebase-ast-auditor",
        description="Deterministic AST static analyzer and architecture audit engine."
    )
    parser.add_argument("path", nargs="?", default=".", help="Target repository or folder path")
    parser.add_argument("--json", action="store_true", help="Output results in machine-readable JSON")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Error: Path does not exist: {root}", file=sys.stderr)
        sys.exit(1)

    scanner = FileScanner(root)
    files = scanner.scan_python_files()
    analyzer = CodebaseAnalyzer(root)
    report = analyzer.analyze_project(files)

    if args.json:
        out = {
            "root": str(root),
            "total_files": report.total_files,
            "total_code_lines": report.total_code_lines,
            "total_classes": report.total_classes,
            "total_functions": report.total_functions,
            "test_files_count": report.test_files_count,
            "estimated_test_ratio": report.estimated_test_ratio,
            "top_imports": report.top_imported_modules,
        }
        print(json.dumps(out, indent=2))
        sys.exit(0)

    print("=" * 68)
    print(" 🛡️  CODEBASE AST AUDITOR :: STATIC ARCHITECTURE REPORT")
    print("=" * 68)
    print(f" Target Root:          {root}")
    print(f" Python Files Found:   {report.total_files}")
    print(f" Total Code Lines:     {report.total_code_lines}")
    print(f" Declared Classes:     {report.total_classes}")
    print(f" Total Functions:      {report.total_functions}")
    print(f" Test Files Detected:  {report.test_files_count} ({report.estimated_test_ratio * 100:.1f}%)")
    print("-" * 68)
    print(" Top Dependencies:")
    for mod, count in report.top_imported_modules:
        print(f"   • {mod:<24} imported in {count} file(s)")
    print("=" * 68)
    print(" [OK] Static audit completed with Exit Code 0.")


if __name__ == "__main__":
    main()
