"""Codebase AST Auditor — deterministic AST static analysis & architecture dependency auditor."""

from .analyzer import CodebaseAnalyzer, ModuleMetrics, ProjectAuditReport
from .scanner import FileScanner

__version__ = "0.1.0"
__all__ = ["CodebaseAnalyzer", "ModuleMetrics", "ProjectAuditReport", "FileScanner"]
