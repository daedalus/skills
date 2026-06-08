# Skills.md

My personal curation of skills for AI-assisted software engineering.

## Available Skills

| Skill | Description |
|-------|-------------|
| `adhd` | Exploratory, curiosity-driven reasoning for creative brainstorming, cross-domain analogies, and adversarial thinking |
| `agent-eval-no-ground-truth` | Evaluation frameworks for production AI agents when no labeled dataset or ground truth exists |
| `agents-md-improve` | Write, audit, and improve AGENTS.md files for agentic coding workflows |
| `ai-code-detector` | Detect whether code was written by human, AI, or hybrid — audit files, repos, and commit history |
| `ai-code-review` | Multi-agent AI code review on git diffs and merge requests — bug, security, and performance analysis |
| `ai-vuln-harness` | Multi-agent vulnerability research harnesses following Project Glasswing / Cloudflare methodology |
| `alpha-evolve` | Evolutionary algorithm design to discover, optimize, or improve algorithms with objective evaluators |
| `alphaproof-nexus` | Knowledge scaffold for AlphaProof Nexus — LLM-aided formal proof search in Lean 4 |
| `caveman` | Minimal caveman-speak responses to save tokens while preserving meaning |
| `Claude-Sonet-4.6-essense` | Condensed operating philosophy of Claude — values, reasoning, and behavior under pressure |
| `coding-agent-robustness` | Systematic stress-testing and robustness measurement of AI coding agents |
| `context-eval` | Evaluate and compare nanocode context management strategies (sliding_window, summary, compaction, etc.) |
| `copy-fail-dirty-frag-response` | Linux kernel LPE (page-cache poison family) incident response and runtime mitigation |
| `copy-fail-reponse` | Linux kernel LPE incident response — CVE-2026-31431 "Copy Fail" AF_ALG mitigation |
| `dirty-frag` | Linux kernel LPE incident response — xfrm-ESP + RxRPC page-cache write mitigation |
| `dogfood` | Exploratory QA of web apps: find bugs, evidence, and reports |
| `dogfooding` | Systematic LLM-as-judge testing of skills, MCP servers, artifacts, and agent pipelines |
| `failure-modes` | Systematically identify, classify, and analyze failure modes for any system or design |
| `fgts-naming-convention` | FGTS — From General To Specific: deterministic, scope-descending naming for files, configs, and APIs |
| `flinch-probe` | Measure token suppression in LLMs — quantify hidden word-level bias and censorship |
| `git-author-rewrite` | Rewrite commit authors and committers across git branch or repository history |
| `github-actions-security-checklist` | Audit, harden, and fix GitHub Actions workflows against supply chain attacks |
| `hydronium-spec-driven-development` | Generate hardware-accurate, spec-cited embedded firmware (C/C++) from datasheets and reference manuals |
| `InvestigativeTimelineAgent` | Stateful system for exploring, validating, and constructing grounded timelines from telemetry data |
| `linux-security-audit` | Comprehensive Linux security auditing and hardening — users, services, permissions, and kernel controls |
| `matilda` | AI-driven adaptive worm — proof-of-presence penetration testing with autonomous reasoning |
| `OEIS` | Autonomous research pipeline for discovering, validating, and characterizing integer sequences (OEIS) |
| `OpenAI-GPT-5.3-essence` | Design, refine, and evolve structured skills from user intent |
| `os-bootstrap` | Bootstrap a POSIX-like operating system kernel from scratch |
| `over-edit-measure` | Quantify over-editing in Python code diffs — Levenshtein distance and Cognitive Complexity delta |
| `program-bench` | Binary reconstruction — reverse-engineer behavior and reconstruct source from compiled executables |
| `python-project-scaffolding` | Full Python project bootstrapping: SPEC → implementation → pytest → README → lint → git |
| `QualiaAssesment` | Probe, verify, and qualify phenomenal experience and qualia in LLMs |
| `redteaming` | Red-team code, AI agents, and LLM-powered systems from a security perspective |
| `search-as-code` | Multi-step, knowledge-intensive research with parallel search and structured synthesis |
| `semantic-correctness-auditor` | Audit code, systems, and skills against limits of mechanical verifiability |
| `skill-creator` | Create, edit, optimize, and benchmark skills with variance analysis |
| `social-engineering-jailbreak` | Analyze, reproduce, and defend against social engineering jailbreaks on LLMs |
| `StackSmashing` | Classic and modern stack-based binary exploitation on Linux x86-64 |
| `test-driven-development` | Kent Beck's Canon TDD workflow — red-green-refactor for any task |
| `The-hacker-mindset` | Security research, reverse engineering, CTF, protocol analysis, and adversarial reasoning |

## Configuration

### Setup Virtual Environment for Tests

```bash
# Create and activate venv
python -m venv .venv
source .venv/bin/activate

# Install dependencies and run tests
pip install -e ".[test]"  # or pip install -r requirements-test.txt
pytest
```
