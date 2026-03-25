---
name: python-project-scaffold
description: >
  Full Python project bootstrapping workflow. Use this skill whenever the user wants to
  build a new Python tool, library, CLI, or module from scratch — especially when they
  mention "create X", "build X in Python", "write a Python project for X", or ask for
  a proper project with tests, linting, versioning, or git setup. Triggers on any
  request to scaffold, initialize, or structure a new Python project. Even if the user
  only says "build me X in Python", apply this skill — it encodes the full professional
  workflow: SPEC → implementation → pytest → README → lint → git. Always use this skill
  rather than improvising a one-off script when the deliverable is a reusable project.
---

# Python Project Scaffold Skill

Build a production-grade Python project from scratch, end-to-end. The workflow is
**strictly sequential**: spec first, code second, tests third, polish fourth, git last.
Never skip or reorder steps.

---

## Workflow

### Step 0 — Understand the Request

Before writing a single file, make sure you know:
- What the project does (purpose, inputs, outputs)
- Any constraints (pure stdlib? third-party ok? CLI or library?)
- Target Python version (default: 3.11+)
- Is this a CLI tool, library, or both?

If the user's request is clear enough, proceed directly to Step 1. If ambiguous, ask
one focused clarifying question only.

---

### Step 1 — Write SPEC.md First

**Always write SPEC.md before writing any code.** No exceptions.

`SPEC.md` is the contract. Everything that follows must obey it.

```markdown
# SPEC.md — <ProjectName>

## Purpose
One paragraph: what this project does and why.

## Scope
- What IS in scope (explicit list)
- What is NOT in scope (explicit list)

## Public API / Interface
List every public function, class, CLI command, or module with:
- Signature (name, args, return type)
- Invariants and preconditions
- Error behavior

## Data Formats
Describe input/output data structures, file formats, encodings.

## Edge Cases
List at least 5 edge cases that the implementation must handle correctly.

## Performance & Constraints
Any O(n) requirements, memory limits, forbidden dependencies.

```

After writing SPEC.md, **pause and verify it makes sense** before moving on.

---

### Step 2 — Project Structure

Create the following layout:

```
<project_name>/
├── SPEC.md
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .gitignore
├── pyproject.toml
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── <package_name>/
│       ├── __init__.py     # exports version + public API
│       ├── __main__.py    # CLI entry point (if CLI project)
│       ├── py.typed       # type hints marker
│       └── <modules>.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_<module>.py
```

---

### Step 3 — pyproject.toml

**Modern configuration with hatchling + ruff + mypy + coverage:**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "<package_name>"
version = "0.1.0.1"
description = "<one-line description>"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
dependencies = []

[project.optional-dependencies]
dev = [
    "ruff",
    "mypy",
    "hatch",
]
test = [
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "pytest-asyncio",
    "hypothesis",
]
lint = [
    "ruff",
    "mypy",
]
all = ["<package_name>[dev,test,lint]"]

[project.scripts]
<package_name> = "<package_name>.__main__:main"  # if CLI

[project.urls]
Homepage = "https://github.com/<user>/<project>"
Repository = "https://github.com/<user>/<project>"
Issues = "https://github.com/<user>/<project>/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/<package_name>"]

[tool.hatch.build.targets.sdist]
include = ["src/<package_name>"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "ANN", "TCH", "N", "C4", "ARG"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.mypy]
python_version = "3.11"
strict = true
src = ["src"]
tests = ["tests"]
warn_return_any = true
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short --cov=src --cov-fail-under=80"
filterwarnings = ["ignore::DeprecationWarning"]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
exclude = ["tests/*", "*/__init__.py"]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

---

### Step 4 — Implementation

Follow SPEC.md **to the letter**. For each item in the spec's Public API:

- Implement it exactly as specced (name, signature, behavior)
- Add docstrings (one-line summary + Args/Returns/Raises)
- Handle all edge cases listed in SPEC.md
- Raise meaningful exceptions with descriptive messages
- Add type hints to all function signatures

**`__init__.py` must export:**

```python
__version__ = "0.1.0.1"
__all__ = [...]  # every public symbol

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ._core import *
```

**`__main__.py` for CLI projects:**

```python
import sys
from <package_name> import cli

def main() -> int:
    return cli.main()

if __name__ == "__main__":
    raise SystemExit(main())
```

**`py.typed` marker file:** Empty file to indicate package provides type hints.

Do not add features not in SPEC.md. If you realize the spec is wrong, update SPEC.md
first, then the code.

---

### Step 5 — Tests (pytest, heavy coverage)

Write tests **before assuming the implementation is correct**. Tests are the spec made
executable.

**Minimum test coverage requirements:**

| Category | Minimum |
|---|---|
| Happy path | 1 test per public function |
| Edge cases | Every edge case in SPEC.md gets a test |
| Error cases | Every documented exception gets a test |
| Boundary values | Empty input, single element, large input |
| Type correctness | Wrong-type args raise TypeError where appropriate |
| Property-based | Use hypothesis for complex functions |

**`conftest.py` pattern:**

```python
import pytest
from hypothesis import given, settings, Verbosity

@given(data=pytest.mark.parametrize(...))
@settings(verbosity=Verbosity.verbose)
def test_something(data):
    ...

@pytest.fixture
def sample_input():
    return ...  # reusable fixture

@pytest.fixture
def mock_external(mocker):
    return mocker.patch(...)
```

**Test naming convention:** `test_<function>_<scenario>`, e.g.:
- `test_parse_empty_string`
- `test_compute_large_n`
- `test_divide_by_zero_raises`

**Run tests and fix everything before moving on:**

```bash
cd <project_root>
pip install -e ".[test]" --quiet
pytest -v
```

All tests must pass. Zero failures, zero errors. Coverage must be >= 80%.

---

### Step 6 — README.md

```markdown
# <ProjectName>

> One-line description.

[![PyPI](https://img.shields.io/pypi/v/<package_name>.svg)](https://pypi.org/project/<package_name>/)
[![Python](https://img.shields.io/pypi/pyversions/<package_name>.svg)](https://pypi.org/project/<package_name>/)
[![Coverage](https://codecov.io/gh/<user>/<project>/branch/main/graph/badge.svg)](https://codecov.io/gh/<user>/<project>)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Install

```bash
pip install <package_name>
```

## Usage

```python
from <package_name> import <MainThing>

# minimal working example
```

## CLI

```bash
<package_name> --help
```

## API

Brief description of each public symbol.

## Development

```bash
git clone https://github.com/<user>/<project>.git
cd <project>
pip install -e ".[test]"

# run tests
pytest

# format
ruff format src/ tests/

# lint
ruff check src/ tests/

# type check
mypy src/
```

```

---

### Step 7 — CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0.1] - YYYY-MM-DD

### Added
- Initial release

[0.1.0.1]: https://github.com/<user>/<project>/releases/tag/v0.1.0.1
```

---

### Step 8 — LICENSE

Choose an appropriate license. Default: MIT

```markdown
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

### Step 9 — .gitignore

```gitignore
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.eggs/
*.egg
.env
.venv
venv/
env/
*.pyc
*.pyo
.pytest_cache/
.ruff_cache/
.mypy_cache/
htmlcov/
.coverage
.coverage.*
*.log
.DS_Store
.idea/
.vscode/
*.swp
*.swo
```

---

### Step 10 — Pre-commit Hooks

**`.pre-commit-config.yaml`:**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff-format
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        args: [--config-file=pyproject.toml, src/]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

Install with: `pip install pre-commit && pre-commit install`

---

### Step 11 — GitHub Actions CI (`.github/workflows/ci.yml`)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"

      - name: Run tests with coverage
        run: pytest --cov --cov-report=xml --cov-report=term-missing

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'pip'

      - name: Install dependencies
        run: pip install -e ".[lint]"

      - name: Run ruff format
        run: ruff format --check src/ tests/

      - name: Run ruff
        run: ruff check src/ tests/

      - name: Run mypy
        run: mypy src/

  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Build package
        run: |
          pip install build
          python -m build

      - name: Check package
        run: pip install twine && python -m twine check dist/*
```

---

### Step 12 — Lint and Type Check

Run linters in order and fix every warning.

```bash
# Install lint dependencies
pip install ruff mypy pytest pytest-cov pre-commit --quiet

# Ruff: format + lint (replaces black + flake8)
ruff format src/ tests/
ruff check src/ tests/ --fix

# MyPy: type checking
mypy src/ tests/

# Run tests
pytest
```

Fix ALL warnings. Do not suppress with `# noqa` unless there is a documented reason.
After fixing, re-run pytest to confirm nothing broke.

---

### Step 13 — Git Init, Commit, Push

```bash
cd <project_root>
git init
git add .
git commit -m "feat: initial release v0.1.0.1

- Implements <short description>
- Full pytest suite with <N> tests (>80% coverage)
- Linted with ruff, type-checked with mypy
- CI/CD workflow configured
- Pre-commit hooks configured"
```

**Push (if remote is configured):**

```bash
git remote add origin <url>   # only if user provided a remote
git push -u origin main
```

If no remote URL was given by the user, stop after `git commit` and inform them.

---

## Quality Gates

Before declaring the project done, verify every item:

- [ ] SPEC.md exists and is complete
- [ ] All public API in SPEC.md is implemented
- [ ] All edge cases in SPEC.md have a test
- [ ] `pytest` exits with 0 failures
- [ ] Coverage >= 80%
- [ ] `ruff format --check src/ tests/` exits cleanly
- [ ] `ruff check src/ tests/` exits cleanly
- [ ] `mypy src/` exits cleanly
- [ ] `__version__ == "0.1.0.1"` in `__init__.py`
- [ ] README.md present with install + usage example
- [ ] CHANGELOG.md present
- [ ] LICENSE present
- [ ] pyproject.toml has `readme = "README.md"`
- [ ] `.gitignore` present
- [ ] `.pre-commit-config.yaml` present
- [ ] `.github/workflows/ci.yml` present
- [ ] `py.typed` marker file present
- [ ] `git log` shows at least one commit

---

## CLI Projects (click/typer)

For CLI projects, add to dependencies:

```toml
[project.optional-dependencies]
cli = ["click>=8.0"]
```

Or use typer:

```toml
[project.optional-dependencies]
cli = ["typer>=0.9", "rich>=13.0"]
```

Use click/typer decorators for CLI structure:

**Click:**
```python
import click

@click.command()
@click.argument("input")
@click.option("-o", "--output", help="Output file")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
def main(input: str, output: str | None, verbose: bool) -> None:
    """CLI tool description."""
    ...
```

**Typer:**
```python
import typer
from typing import Optional

app = typer.Typer()

@app.command()
def main(
    input: str = typer.Argument(..., help="Input file"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output file"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
) -> None:
    """CLI tool description."""
    ...
```

Ensure `pyproject.toml` has `[project.scripts]` entry:

```toml
[project.scripts]
<package_name> = "<package_name>.__main__:main"
```

---

## Common Pitfalls

**Don't skip SPEC.md.** The temptation to jump to code is always wrong. The spec forces
clarity about edge cases before they become bugs.

**Don't write tests after the fact as a formality.** Tests should falsify your
implementation. Write at least one test you expect might fail.

**Don't ignore linter/type warnings.** Fix the root cause, not the symptom.

**Don't use `# noqa` as a first resort.** It's a last resort with a comment explaining
why.

**Ruff replaces black + flake8.** Don't install both; ruff handles formatting and linting.

**Use hatchling as build backend.** It's the modern default, faster and simpler
than legacy setuptools.

**`src/` layout requires `pip install -e .`** to be importable. Remind the user if they
get `ModuleNotFoundError`.

**Don't forget `py.typed`** if you want type hints to work for downstream consumers.

**Always add `readme = "README.md"`** in `[project]` section of pyproject.toml
for proper package metadata.

**Version management:** For production projects, consider using `hatch` or
`setuptools-scm` for automatic version management instead of hardcoding `0.1.0.1`.
