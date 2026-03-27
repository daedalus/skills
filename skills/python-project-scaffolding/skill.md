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

### Step — 0.5 Setup project internal variables to use later

```
<package_name> Is the package name.
<project_name> Is the project name.
<version> Is the project version (default :"0.1.0").
<project_description> Is the project description.
<is_mcp_server> Is this project about MCP server? (true/false)
<author_name> is the author name (ask).
<author_email> is the author email (ask).
<github_username> Is the github username (ask).
<target_python> Is the target Python version (default: "3.11").
<ruff_version> Is the ruff version (default: "v0.9.0").
<mypy_version> Is the mypy version (default: "v1.14.0").
<pre_commit_version> Is the pre-commit version (default: "v5.0.0").
<hatch_version> Is the hatch version (default: "latest").
<scm_version> Is the setuptools-scm version (default: "0.1.1").
```


### Step 1 — Write SPEC.md First

**Always write SPEC.md before writing any code.** No exceptions.

`SPEC.md` is the contract. Everything that follows must obey it.

```markdown
# SPEC.md — <project_name>

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
version = "<version>"
description = "<one-line description>"
readme = "README.md"
requires-python = ">=<target_python>"
license = {text = "MIT"}
authors = [
    {name = "<author_name>", email = "<author_email>"}
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
Homepage = "https://github.com/<github_username>/<project_name>"
Repository = "https://github.com/<github_username>/<project_name>"
Issues = "https://github.com/<github_username>/<project_name>/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/<package_name>"]

[tool.hatch.build.targets.sdist]
include = ["src/<package_name>"]

[tool.ruff]
line-length = 88
target-version = "py<target_python>"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "ANN", "TCH", "N", "C4", "ARG"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.mypy]
python_version = "<target_python>"
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
- Add verbose docstrings (comprehensive summary + detailed Args/Returns/Raises/Examples)
- Every function should have at minimum: summary line, extended description, Args section with types, Returns section with types, Raises section, and Examples section where helpful
- Handle all edge cases listed in SPEC.md
- Raise meaningful exceptions with descriptive messages
- Add type hints to all function signatures

**`__init__.py` must export:**

```python
__version__ = "<version>"
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

**Verify the package imports correctly:**
```bash
python -c "import <package_name>; print(<package_name>.__version__)"
```

---

### Step 6 — README.md

```markdown
# <ProjectName>

> One-line description.

[![PyPI](https://img.shields.io/pypi/v/<package_name>.svg)](https://pypi.org/project/<package_name>/)
[![Python](https://img.shields.io/pypi/pyversions/<package_name>.svg)](https://pypi.org/project/<package_name>/)
[![Coverage](https://codecov.io/gh/<author_name>/<project_name>/branch/main/graph/badge.svg)](https://codecov.io/gh/<author_name>/<project_name>)
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
git clone https://github.com/<github_username>/<project_name>.git
cd <project_name>
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

**Apply this step ONLY if `<is_mcp_server>` is `true`.**
```README.md
mcp-name: io.github.<github_username>/<package_name>
```


---

### Step 7 — CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Added
- Initial release

[<version>]: https://github.com/<github_username>/<project_name>/releases/tag/v<version>
```

---

### Step 8 — LICENSE

Choose an appropriate license. Default: MIT

```markdown
MIT License

Copyright (c) 2026 <author_name>

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
    rev: <ruff_version>
    hooks:
      - id: ruff-format
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: <mypy_version>
    hooks:
      - id: mypy
        args: [--config-file=pyproject.toml, src/]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: <pre_commit_version>
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

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv pip install --system -e ".[test]"

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

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv pip install --system -e ".[lint]"

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

### Step 11.5 — PyPI Publish (`.github/workflows/pypi-publish.yml`)

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Create virtual environment and install build tools
        run: uv venv && uv pip install build twine

      - name: Build package
        run: uv run python -m build

      - name: Check package
        run: uv run python -m twine check dist/*

      - name: Upload dist artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/libtor
    permissions:
      id-token: write
    steps:
      - name: Download dist artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          user: __token__
          password: ${{ secrets.PYPI_API_TOKEN }}
```

### Step 11.6 — MCP registry Publish
**Apply this step ONLY if `<is_mcp_server>` is `true`.**

**`server.json`:**
```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.<github_username>/<project_name>",
  "description": "<project_description>",
  "repository": {
    "url": "https://github.com/<github_username>/<project_name>",
    "source": "github"
  },
  "version": "<version>",
  "packages": [
    {
      "registryType": "pypi",
      "identifier": "<project_name>",
      "version": "<version>",
      "transport": {
        "type": "stdio"
      }
    }
  ]
}

```

**`mcp.json`:**
```json
{
  "mcpServers": {
    "<package_name>": {
      "command": "<package_name>",
      "env": {}
    }
  }
}

```

### Step 11.7 — Publish Python MCP Server (`.github/workflows/mcp-publish.yml`)

**Apply this step ONLY if `<is_mcp_server>` is `true`.**

```yaml
name: Publish Python MCP Server

on:
  workflow_run:
    workflows: ["Publish to PyPI"]
    types:
      - completed
  workflow_dispatch:

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Install MCP Publisher
        run: |
          curl -L "https://github.com/modelcontextprotocol/registry/releases/download/v1.5.0/mcp-publisher_linux_amd64.tar.gz" | tar xz mcp-publisher

      - name: Publish to MCP Registry
        run: |
          ./mcp-publisher login github-oidc
          ./mcp-publisher publish
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
git commit -m "feat: initial release v<version>

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
- [ ] `python -c "import <package_name>"` succeeds
- [ ] Coverage >= 80%
- [ ] `ruff format --check src/ tests/` exits cleanly
- [ ] `ruff check src/ tests/` exits cleanly
- [ ] `mypy src/` exits cleanly
- [ ] `__version__ == "<version>"` in `__init__.py`
- [ ] README.md present with install + usage example
- [ ] CHANGELOG.md present
- [ ] LICENSE present
- [ ] pyproject.toml has `readme = "README.md"`
- [ ] `.gitignore` present
- [ ] `.pre-commit-config.yaml` present
- [ ] `.github/workflows/ci.yml` present
- [ ] `.github/workflows/pypi-publish.yml` present
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
`setuptools-scm` for automatic version management instead of hardcoding `<scm_version>`.

**Language:** Make sure the code and the main documentation is always in english.
