# Skills.md

My personal curation of skills.md

## Available Skills

| Skill | Description |
|-------|-------------|
| `python-project-scaffolding` | Full Python project bootstrapping workflow - SPEC → implementation → pytest → README → lint → git |
| `Claude-Sonet-4.6-essense` | Condensed operating philosophy of Claude - values, reasoning, and behavior |
| `OpenAI-GPT-5.3-essence` | GPT model essence and behavior patterns |
| `OEIS` | OEIS (Online Encyclopedia of Integer Sequences) integration |
| `redteaming` | Red teaming methodologies and practices |
| `QualiaAssesment` | Qualia assessment techniques |
| `StackSmashing` | Stack smashing / buffer overflow exploitation |
| `InvestigativeTimelineAgent` | Investigative timeline agent for tracking events |

## Configuration

### Version Bumping

Configure how version bumping is handled in your projects:

| Tool | Configuration |
|------|---------------|
| **commitizen** | `.czrc` or `pyproject.toml` with `[tool.commitizen]` |
| **bump2version** | `.bumpversion.cfg` or `pyproject.toml` with `[tool.bumpversion]` |
| **standard-version** | `.versionrc` or `package.json` |

Example for Python projects using commitizen:

```toml
# pyproject.toml
[tool.commitizen]
version = "0.1.0"
tag_format = "v$version"
```

### Setup Virtual Environment for Tests

```bash
# Create and activate venv
python -m venv .venv
source .venv/bin/activate

# Install dependencies and run tests
pip install -e ".[test]"  # or pip install -r requirements-test.txt
pytest
```