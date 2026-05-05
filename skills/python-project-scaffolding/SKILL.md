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

**Note:** If `rtk` is available in the environment, prefer using `rtk git <command>` instead of `git <command>` for better workflow integration and consistency.

### Step 0 — Understand the Request

The default branch is master.

Before writing a single file, make sure you know:
- What the project does (purpose, inputs, outputs)
- Any constraints (pure stdlib? third-party ok? CLI or library?)
- Target Python version (default: 3.11+)
- Is this a CLI tool, library, or both?

If the user's request is clear enough, proceed directly to Step 1. If ambiguous, ask
one focused clarifying question only.

---

### Step 1 — Setup project internal variables to use later

```
<package_name> Is the package name it must follow pypi conventions like hypenated between words.
<project_name> Is the project name.
<version> Is the project version (default :"0.1.0").
<project_description> Is the project description.
<is_mcp_server> Is this project about MCP server? (true/false)
<github_username> Is the github username (git config user.githubusername).
<author_name> Is the author name (git config user.name).
<author_email> Is the author email (git config.email).
<target_python> Is the target Python version (default: "3.11").
<ruff_version> Is the ruff version (default: "v0.9.0").
<prospector_version> Is the prospector version (default: "v1.18.0").
<semgrep_version> Is the semgrep version (default: "v1.161.0").
<pre_commit_version> Is the pre-commit version (default: "v5.0.0").
<hatch_version> Is the hatch version (default: "latest").
```


### Step 2 — Write docs/SPEC.md First

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

After writing docs/SPEC.md, **pause and verify it makes sense** before moving on.

---

### Step 3 — Project Structure

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

### Step 4 — Internal Subsystem Organization

When a package grows beyond a few modules, separate concerns into distinct subsystems
within `src/<package_name>/`. Each subsystem should be a self-contained package with a
clear responsibility. The following is a non-exhaustive list of common subsystem types
— use only those that apply to your project.

**Layout pattern (examples):**

```
src/<package_name>/
├── __init__.py
├── __main__.py
├── py.typed
├── core/              # Core domain logic, no external dependencies
│   ├── __init__.py
│   └── models.py
├── adapters/          # External integrations (API clients, DB, filesystem)
│   ├── __init__.py
│   ├── http.py
│   └── storage.py
├── services/          # Business logic orchestrating core + adapters
│   ├── __init__.py
│   └── pipeline.py
├── cli/               # CLI layer (if CLI project)
│   ├── __init__.py
│   └── commands.py
└── api/               # HTTP/API layer (if applicable)
    ├── __init__.py
    └── routes.py
```

**Rules:**

- `core/` has zero imports from `adapters/`, `services/`, `cli/`, or `api/`
- `adapters/` may import from `core/` but not from `services/`, `cli/`, or `api/`
- `services/` may import from `core/` and `adapters/`, but not from `cli/` or `api/`
- `cli/` and `api/` may import from any subsystem
- Never create catch-all modules like `utils.py` at the package root; place utility
  code near where it's used

**Dependency direction (inward):**

```
cli/api → services → adapters → core
```

This ensures `core` remains testable without external dependencies and can be reused
independently.

---

### Step 5 — pyproject.toml

**Modern configuration with hatchling + ruff + mypy (via prospector) + coverage:**

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
# Apply ONLY if <is_mcp_server> is true:
# dependencies = ["fastmcp"]

[project.optional-dependencies]
dev = [
    "ruff",
    "mypy",
    "hatch",
    "pip-api",
]
test = [
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "pytest-asyncio",
    "hypothesis",
]
lint = [
    "prospector[with_ruff,with_mypy]",
    "semgrep",
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

# Note: mypy options are configured inside prospector (see below)
# prospector --with-tool ruff --with-tool mypy will use [tool.mypy] if present
[tool.mypy]
python_version = "<target_python>"
strict = true
warn_return_any = true
warn_unused_ignores = true

[tool.prospector]
output-format = "text"
strictness = "medium"
test-warnings = false

[tool.prospector.tools]
ruff = true
mypy = true
pylint = true
pyflakes = false  # redundant with ruff's F rules
pycodestyle = false  # redundant with ruff's E/W rules
mccabe = true

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

### Step 6 — Implementation

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

### Step 7 — Tests (pytest, heavy coverage)

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

### Step 8 — README.md

```markdown
**<package_name>** — One-line description.

[![PyPI](https://img.shields.io/pypi/v/<package_name>.svg)](https://pypi.org/project/<package_name>/)
[![Python](https://img.shields.io/pypi/pyversions/<package_name>.svg)](https://pypi.org/project/<package_name>/)
[![Coverage](https://codecov.io/gh/<author_name>/<project_name>/branch/master/graph/badge.svg)](https://codecov.io/gh/<author_name>/<project_name>)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/master/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/<github_username>/<package_nane>)

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

# lint + type check (prospector runs ruff check + mypy together)
prospector --with-tool ruff --with-tool mypy src/
semgrep --config=auto --severity=ERROR src/
```

```

<!-- Apply this step ONLY if `<is_mcp_server>` is `true`. -->

```markdown
mcp-name: io.github.<github_username>/<package_name>
```

---

### Step 9 — CHANGELOG.md

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

### Step 10 — LICENSE

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

### Step 11 — .gitignore

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
.hypothesis/
```

---

### Step 12 — Pre-commit Hooks

**`.pre-commit-config.yaml`:**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: <ruff_version>
    hooks:
      - id: ruff-format

  - repo: https://github.com/landscapeio/prospector-pre-commit
    rev: <prospector_version>
    hooks:
      - id: prospector
        additional_dependencies:
          - ".[with_ruff,with_mypy]"
        args: [--with-tool=ruff, --with-tool=mypy, --with-tool=pylint, --path=src/]

  - repo: https://github.com/semgrep/semgrep
    rev: <semgrep_version>
    hooks:
      - id: semgrep
        args: [--config=auto, --severity=ERROR, src/]

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

### Step 13 — GitHub Actions CI

**Write `.github/workflows/ci.yml` with the content below:**

```yaml
name: CI

on:
  push:
      branches: [master]
  pull_request:
      branches: [master]

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
          fail_ci_if_error: false

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

      - name: Run prospector (ruff check + mypy + pylint with blending)
        run: prospector --with-tool ruff --with-tool mypy --with-tool pylint src/

      - name: Run semgrep
        run: semgrep --config=auto --severity=ERROR src/

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

### Step 14 — PyPI Publish

**Write `.github/workflows/pypi-publish.yml` with the content below:**

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
      url: https://pypi.org/p/<project_name>
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

### Step 15 — Create a Companion SKILL.md and install-skill.py

**Apply this step ONLY if `<is_mcp_server>` is `true`.**
**Write `scripts/install-skill.py` with the content below:**

```python
#!/usr/bin/env python3
"""Install skill to agent directories."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

AGENT_DIRECTORIES = {
    "claude": Path.home() / ".claude" / "skills",
    "opencode": Path.home() / ".opencode" / "skills",
}

PROJECT_NAME = "<project_name>"
SOURCE_DIR = Path(__file__).parent.parent / "skills" / PROJECT_NAME


def find_agent_dirs() -> dict[str, Path]:
    """Find available agent skill directories."""
    found = {}
    for agent, base_dir in AGENT_DIRECTORIES.items():
        if base_dir.exists():
            found[agent] = base_dir
    return found


def install_skill(agent: str, target_dir: Path) -> bool:
    """Install the skill to the target directory."""
    target_path = target_dir / PROJECT_NAME

    if target_path.exists():
        if target_path.is_symlink():
            target_path.unlink()
        elif target_path.is_dir():
            shutil.rmtree(target_path)

    try:
        os.symlink(SOURCE_DIR.resolve(), target_path)
        print(f"Installed {PROJECT_NAME} to {agent} at {target_path}")
        return True
    except OSError:
        shutil.copytree(SOURCE_DIR.resolve(), target_path)
        print(f"Copied {PROJECT_NAME} to {agent} at {target_path}")
        return True


def main() -> int:
    if not SOURCE_DIR.exists():
        print(f"Error: Skill source not found at {SOURCE_DIR}", file=sys.stderr)
        return 1

    agents = find_agent_dirs()
    if not agents:
        print("No agent skill directories found", file=sys.stderr)
        return 1

    print(f"Found agents: {', '.join(agents.keys())}")

    for agent, target_dir in agents.items():
        install_skill(agent, target_dir)

    print("\nInstallation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Apply this step ONLY if `<is_mcp_server>` is `true`.**
**Write `skills/<project_name>/SKILL.md` with the content below:**

```markdown
name: {PROJECT_NAME}
description: >
  {PROJECT_DESCRIPTION}
  Triggers on specific keywords or phrases related to this project.
---

# {PROJECT_NAME} Skill

[Description of the skill's purpose and usage]

## Usage

[How to use this skill]

## Examples

- [Example 1]
- [Example 2]

```

### Step 16 — MCP Registry Publish

**Apply this step ONLY if `<is_mcp_server>` is `true`.**
**Update `pyproject.toml` with MCP server configuration:**

```toml
[project.optional-dependencies]
mcp = ["fastmcp"]
```

Then proceed with Step 17.

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

### Step 17 — Publish Python MCP Server

**Apply this step ONLY if `<is_mcp_server>` is `true`.**
**Write `.github/workflows/mcp-publish.yml` with the content below:**
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

### Step 18 — Bumpversion Configuration

**`.bumpversion.cfg`:**

```ini
[bumpversion]
current_version = <version>

[bumpversion:file:pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file:src/<project_name>/__init__.py]
search = __version__ = "{current_version}"
replace = __version__ = "{new_version}"
```

**Apply this step ONLY if `<is_mcp_server>` is `true`.**
```ini
[bumpversion:file:server.json]
search = "version": "{current_version}"
replace = "version": "{new_version}"
```

---

### Step 19 — Lint and Type Check

Run linters in order and fix every warning.

```bash
# Install lint dependencies
pip install prospector[with_ruff,with_mypy] ruff pytest pytest-cov pre-commit --quiet

# Ruff: format (not included in prospector)
ruff format src/ tests/

# Prospector: runs ruff check + mypy + pylint together with blending (deduplication)
prospector --with-tool ruff --with-tool mypy --with-tool pylint src/

# Semgrep: security and pattern scanning (not included in prospector)
semgrep --config=auto --severity=ERROR src/

# Run tests
pytest
```

Fix ALL warnings. Do not suppress with `# noqa` unless there is a documented reason.
After fixing, re-run pytest to confirm nothing broke.

---

### Step 20 — Git Init, Commit, Push

```bash
cd <project_root>

# If rtk is available, prefer using "rtk git <command>" instead of "git <command>" for better workflow integration

# Create GitHub repository (requires GitHub CLI)
gh repo create <project_name> --public --source=. --push=false

# Initialize git (if not already done)
git init

# Commit all files
git add .
git commit -m "feat: initial release v<version>
- Implements <short description>
- Full pytest suite with <N> tests (>80% coverage)
- Linted with ruff format, prospector (ruff check + mypy), and semgrep
- CI/CD workflow configured
- Pre-commit hooks configured"

# Add remote (SSH)
git remote add origin git@github.com:<github_username>/<project_name>.git

# Add remote (HTTPS) - optional alternative
git remote add origin-https https://github.com/<github_username>/<project_name>.git

# Push to master branch
git push -u origin master
```

If no remote URL was given by the user, stop after `git commit` and inform them.

---

### Step 21 — Verify Dependencies on PyPI

Before finalizing, verify all dependencies in `pyproject.toml` exist on PyPI:

```bash
# Extract all dependencies from pyproject.toml and check each one
pip install --quiet pip-api 2>/dev/null || pip install pip-api

python3 << 'EOF'
import tomllib
import pip_api

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

deps = data.get("project", {}).get("dependencies", [])
for extra, extra_deps in data.get("project", {}).get("optional-dependencies", {}).items():
    deps.extend(extra_deps)

# Extract package names (remove version specifiers)
import re
for dep in deps:
    pkg_name = re.split(r"[<>=!~]", dep)[0].strip()
    try:
        pip_api.pypi_project(pkg_name)
        print(f"✓ {pkg_name}")
    except Exception as e:
        print(f"✗ {pkg_name}: NOT FOUND - {e}")
        exit(1)

print("\nAll dependencies verified on PyPI!")
EOF
```

This gate prevents hallucinated package names from being committed. If any package fails, fix `pyproject.toml` before proceeding.

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

## MCP Server Projects (fastmcp)

**Apply this step ONLY if `<is_mcp_server>` is `true`.**

For MCP server projects, use fastmcp:

```toml
[project.optional-dependencies]
mcp = ["fastmcp"]
```

Implement the MCP server using fastmcp:

```python
import fastmcp

mcp = fastmcp.FastMCP("<package_name>")

@mcp.tool()
def your_tool(arg: str) -> str:
    """Tool description."""
    ...

@mcp.resource("resource://name")
def your_resource() -> str:
    ...
```

**Every function of every tool must have proper documentation with at least one example.**

```python
@mcp.tool()
def your_tool(arg: str) -> str:
    """Short description of what the tool does.

    Args:
        arg: Description of the argument.

    Returns:
        Description of the return value.

    Example:
        >>> your_tool("example_input")
        "expected_output"
    """
    ...
```

For stdio transport, ensure `__main__.py` runs the server:

```python
import sys
from <package_name> import mcp

if __name__ == "__main__":
    mcp.run()
```

---

### Step 22 - Quality Gates


Before declaring the project done, verify every item:

- [ ] SPEC.md exists and is complete
- [ ] All public API in SPEC.md is implemented
- [ ] All edge cases in SPEC.md have a test
- [ ] `pytest` exits with 0 failures
- [ ] `python -c "import <package_name>"` succeeds
- [ ] Coverage >= 80%
- [ ] `ruff format --check src/ tests/` exits cleanly
- [ ] `prospector --with-tool ruff --with-tool mypy src/` exits cleanly
- [ ] `semgrep --config=auto --severity=ERROR src/` exits cleanly
- [ ] `__version__ == "<version>"` in `__init__.py`
- [ ] README.md present with install + usage example
- [ ] `mcp-name` present in README.md (if `<is_mcp_server>` is true)
- [ ] CHANGELOG.md present
- [ ] LICENSE present
- [ ] pyproject.toml has `readme = "README.md"`
- [ ] `.gitignore` present
- [ ] `.github/workflows` directory present
- [ ] `.pre-commit-config.yaml` present
- [ ] `.github/workflows/ci.yml` present
- [ ] `.github/workflows/pypi-publish.yml` present
- [ ] `.github/workflows/mcp-publish.yml` present
- [ ] `scripts/install-skill.py` present (if `<is_mcp_server>` is true)
- [ ] `skills/<project_name>/SKILL.md` present (if `<is_mcp_server>` is true)
- [ ] `server.json` present (if `<is_mcp_server>` is true)
- [ ] `mcp.json` present (if `<is_mcp_server>` is true)
- [ ] `.bumpversion.cfg` present
- [ ] `AGENTS.md` present
- [ ] `py.typed` marker file present
- [ ] `git log` shows at least one commit
- [ ] All dependencies verified on PyPI (Step 21)
- [ ] Step 20 complete: gh repo created, git initialized, at least one commit exists, remote configured (SSH + HTTPS) and pushed


---

### Step 23 — AGENTS.md

Create `AGENTS.md` at the project root to document agent behaviors, commands, and workflows:

```markdown
# AGENTS.md — <project_name>

## Overview

<one-paragraph description of what this project does and who it's for>

## Commands

| Command | Description |
|---------|------------|
| `pytest` | Run test suite |
| `ruff format` | Format code |
| `prospector --with-tool ruff --with-tool mypy src/` | Lint + type check (with blending) |
| `semgrep --config=auto src/` | Security and pattern scanning |

## Development

```bash
# Setup
pip install -e ".[test]"

# Test
pytest

# Format
ruff format src/ tests/

# Lint + type check (prospector runs ruff check + mypy together)
prospector --with-tool ruff --with-tool mypy src/
semgrep --config=auto --severity=ERROR src/
```

## Testing

<brief description of testing approach>

## Code Style

- Format: ruff format
- Lint + Type check: prospector (runs ruff check + mypy with blending)
- Docstrings: Google style

## Release

```bash
# Bump version
bumpversion patch  # or minor/major
git tag v<version>
git push && git push --tags
```

## MCP Server (if `<is_mcp_server>` is true)

```bash
# Install and use
pip install <package_name>
```

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "<package_name>": {
      "command": "<package_name>"
    }
  }
}
```
```

---

## Code Quality

Review for:
- No duplicated code (DRY principle)
- Consistent error handling
- Full type coverage
- Clear tool/module/class/function descriptions.
- What assumptions does this code make that aren't in the spec? What inputs would produce surprising behavior?

---

## Common Pitfalls

**Don't make conditional imports** All the imports should be in the header of the module.

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
`setuptools-scm` for automatic version management.

**Language:** Make sure the code and the main documentation is always in english.

**README.md** Make sure it's not vague.

---


