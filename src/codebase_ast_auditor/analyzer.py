"""AST-based static analyzer: complexity, dependencies, classes, and architectural cohesion."""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class ModuleMetrics:
    """Metrics extracted from a single Python source file."""
    rel_path: str
    total_lines: int
    code_lines: int
    functions: int
    classes: int
    async_functions: int
    imports: List[str] = field(default_factory=list)
    syntax_error: bool = False
    error_message: str = ""


@dataclass
class ProjectAuditReport:
    """Consolidated architecture audit report for a project."""
    total_files: int
    total_code_lines: int
    total_classes: int
    total_functions: int
    test_files_count: int
    estimated_test_ratio: float
    modules: List[ModuleMetrics] = field(default_factory=list)
    top_imported_modules: List[Tuple[str, int]] = field(default_factory=list)


class CodebaseAnalyzer:
    """Pure-Python AST static analyzer that never executes foreign code."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def analyze_file(self, file_path: Path) -> ModuleMetrics:
        """Parse and extract AST metrics from a single file."""
        rel = str(file_path.relative_to(self.root))
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError as err:
            return ModuleMetrics(
                rel_path=rel,
                total_lines=0,
                code_lines=0,
                functions=0,
                classes=0,
                async_functions=0,
                syntax_error=True,
                error_message=str(err)
            )

        total_lines = len(content.splitlines())
        code_lines = len([l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")])

        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as syn_err:
            return ModuleMetrics(
                rel_path=rel,
                total_lines=total_lines,
                code_lines=code_lines,
                functions=0,
                classes=0,
                async_functions=0,
                syntax_error=True,
                error_message=f"SyntaxError at line {syn_err.lineno}: {syn_err.msg}"
            )

        functions = 0
        async_functions = 0
        classes = 0
        imports: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions += 1
            elif isinstance(node, ast.AsyncFunctionDef):
                async_functions += 1
                functions += 1
            elif isinstance(node, ast.ClassDef):
                classes += 1
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    imports.add(root_pkg)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_pkg = node.module.split(".")[0]
                    imports.add(root_pkg)

        return ModuleMetrics(
            rel_path=rel,
            total_lines=total_lines,
            code_lines=code_lines,
            functions=functions,
            classes=classes,
            async_functions=async_functions,
            imports=sorted(imports),
            syntax_error=False,
            error_message=""
        )

    def analyze_project(self, file_paths: List[Path]) -> ProjectAuditReport:
        """Run complete AST analysis across all candidate files."""
        modules: List[ModuleMetrics] = [self.analyze_file(p) for p in file_paths]

        total_code_lines = sum(m.code_lines for m in modules)
        total_classes = sum(m.classes for m in modules)
        total_functions = sum(m.functions for m in modules)

        test_files = [m for m in modules if "test" in Path(m.rel_path).name.lower() or "tests/" in m.rel_path]
        test_files_count = len(test_files)
        ratio = (test_files_count / len(modules)) if modules else 0.0

        import_counter: Dict[str, int] = {}
        for m in modules:
            for imp in m.imports:
                import_counter[imp] = import_counter.get(imp, 0) + 1

        sorted_imports = sorted(import_counter.items(), key=lambda kv: kv[1], reverse=True)[:10]

        return ProjectAuditReport(
            total_files=len(modules),
            total_code_lines=total_code_lines,
            total_classes=total_classes,
            total_functions=total_functions,
            test_files_count=test_files_count,
            estimated_test_ratio=round(ratio, 3),
            modules=modules,
            top_imported_modules=sorted_imports
        )
