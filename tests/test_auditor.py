"""Unit and regression tests for codebase_ast_auditor (100% Deterministic)."""
from pathlib import Path
import pytest

from codebase_ast_auditor.scanner import FileScanner
from codebase_ast_auditor.analyzer import CodebaseAnalyzer, ModuleMetrics


def test_scanner_ignores_caches_and_envs(tmp_path: Path):
    (tmp_path / "valid.py").write_text("x = 1\n", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "module.py").write_text("def f(): pass\n", encoding="utf-8")

    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "ignored.py").write_text("bad = True\n", encoding="utf-8")

    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    (pycache / "compiled.py").write_text("bad2 = True\n", encoding="utf-8")

    scanner = FileScanner(tmp_path)
    files = scanner.scan_python_files()

    names = [f.name for f in files]
    assert "valid.py" in names
    assert "module.py" in names
    assert "ignored.py" not in names
    assert "compiled.py" not in names


def test_analyzer_counts_ast_elements(tmp_path: Path):
    code = """
import os
import sys
from pathlib import Path

class UserService:
    def __init__(self):
        pass

    def get_user(self):
        return None

async def fetch_remote():
    return 42
"""
    f = tmp_path / "service.py"
    f.write_text(code, encoding="utf-8")

    analyzer = CodebaseAnalyzer(tmp_path)
    metrics = analyzer.analyze_file(f)

    assert not metrics.syntax_error
    assert metrics.classes == 1
    assert metrics.functions == 3  # __init__, get_user, fetch_remote
    assert metrics.async_functions == 1
    assert "os" in metrics.imports
    assert "sys" in metrics.imports
    assert "pathlib" in metrics.imports


def test_analyzer_handles_syntax_errors_gracefully(tmp_path: Path):
    broken = tmp_path / "broken.py"
    broken.write_text("def unclosed_function(:\n", encoding="utf-8")

    analyzer = CodebaseAnalyzer(tmp_path)
    metrics = analyzer.analyze_file(broken)

    assert metrics.syntax_error
    assert "SyntaxError" in metrics.error_message


def test_project_audit_summary(tmp_path: Path):
    (tmp_path / "main.py").write_text("import json\ndef run(): pass\n", encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text("import json\ndef test_ok(): assert True\n", encoding="utf-8")

    scanner = FileScanner(tmp_path)
    files = scanner.scan_python_files()

    analyzer = CodebaseAnalyzer(tmp_path)
    report = analyzer.analyze_project(files)

    assert report.total_files == 2
    assert report.test_files_count == 1
    assert report.estimated_test_ratio == 0.5
    assert len(report.top_imported_modules) >= 1
    assert report.top_imported_modules[0][0] == "json"
