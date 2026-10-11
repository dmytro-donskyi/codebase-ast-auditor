# 🛡️ Codebase AST Auditor

[![CI](https://github.com/dmitriy-donskoy/codebase-ast-auditor/actions/workflows/ci.yml/badge.svg)](https://github.com/dmitriy-donskoy/codebase-ast-auditor/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests: 100% Green](https://img.shields.io/badge/tests-100%25%20passed-brightgreen.svg)]()

> **Deterministic static AST code scanner, architectural dependency graph analyzer, and complexity auditor for Python projects.**  
> Zero third-party dependencies. Zero arbitrary code execution. Fail-closed by design.

---

## 🚀 Key Highlights

* **100% Safe Static Analysis:** Parses code purely via Python's native `ast` module. Never imports or executes target code.
* **Fail-Closed Perimeter Guard:** Automatically ignores virtual environments (`.venv`, `env`), build artifacts (`dist`, `build`, `__pycache__`), and sensitive configuration trees.
* **Architectural Dependency Mapping:** Extracts package imports, class hierarchies, and async function ratios.
* **Test Coverage Ratio Estimation:** Automatically discovers test files and computes test-to-source file ratios.
* **CI/CD Ready:** Generates both formatted human-readable terminal reports and machine-parsable JSON for automation pipelines.

---

## 📦 Installation

```bash
# Clone and install locally
git clone https://github.com/dmitriy-donskoy/codebase-ast-auditor.git
cd codebase-ast-auditor
pip install -e .
```

Or run directly without installation:
```bash
python3 -m codebase_ast_auditor.cli /path/to/target/project
```

---

## 🛠️ Usage

### 1. Human-Readable Architectural Audit
```bash
codebase-ast-auditor ./my-project
```

**Sample Output:**
```text
====================================================================
 🛡️  CODEBASE AST AUDITOR :: STATIC ARCHITECTURE REPORT
====================================================================
 Target Root:          /home/user/my-project
 Python Files Found:   48
 Total Code Lines:     12,450
 Declared Classes:     62
 Total Functions:      310
 Test Files Detected:  24 (50.0%)
--------------------------------------------------------------------
 Top Dependencies:
   • fastapi                  imported in 18 file(s)
   • sqlalchemy               imported in 14 file(s)
   • pydantic                 imported in 12 file(s)
   • pytest                   imported in 24 file(s)
====================================================================
 [OK] Static audit completed with Exit Code 0.
```

### 2. Machine-Readable JSON Export
```bash
codebase-ast-auditor ./my-project --json
```

---

## 🧪 Deterministic Testing

Every single feature is verified by strict unit and regression test suites:

```bash
pytest tests -v
```

---

## 📄 License

Distributed under the **MIT License**. Created by **Dmitriy Donskoy**.
