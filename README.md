# Skills.md

My personal curation of skills for AI-assisted software engineering.

## Available Skills

| Skill | Description |
|-------|-------------|
| `adhd` | Enables exploratory reasoning that scouts statistically unexpected but potentially high-value directions |
| `advanced-math` | Deep technical assistance for number theory, abstract algebra, topology, and graduate-level mathematics |
| `agent-eval-no-ground-truth` | Framework for evaluating production AI agents without labeled datasets or ground truth |
| `Agentic-Property-Based-Testing` | Agent workflow for discovering bugs in Python code by inferring invariants from context |
| `agents-md-improve` | Empirically-grounded guidance for writing agent instruction files like AGENTS.md and CLAUDE.md |
| `ai-code-detector` | Weight-of-evidence methodology for detecting whether code was written by a human or AI |
| `ai-code-review` | Orchestrate a structured, multi-agent AI code review over a git diff or merge request |
| `ai-vuln-harness` | High-level guide for building a production-style AI vulnerability harness |
| `alpha-evolve` | Evolutionary LLM-driven algorithm search for problems with verifiable, automatable evaluators |
| `alphaproof-nexus` | Framework combining LLMs with Lean 4 proof assistant and evolutionary search to solve math |
| `approach-extractor` | Extracts reasoning behind solved problems into reusable learnings notes, not just diffs |
| `auto-research-engineer` | Iterative hill-climbing loop: change one thing, score it, keep only what beats baseline |
| `caveman` | Token-efficient communication style stripping language to essential load-bearing words, saving 40-70% |
| `Claude-Sonet-4.6-essense` | The condensed operating philosophy of Claude — how it thinks and behaves under pressure |
| `codex-security-adapter` | Router mapping user security intent to specific files and workflows inside the codex-security plugin |
| `coding-agent-robustness` | Systematic stress-testing and robustness measurement of coding agents under adversarial and edge-case inputs |
| `context-eval` | Tests and compares nanocode context management strategies via A/B testing |
| `copy-fail-dirty-frag-response` | Runtime containment of kernel LPE exploits using bpf-lsm allowlisting and eBPF fleet visibility |
| `copy-fail-reponse` | Runtime containment of kernel LPE exploits targeting AF_ALG using bpf-lsm and eBPF |
| `dirty-frag` | Runtime containment of kernel LPE exploits using bpf-lsm allowlisting and eBPF fleet visibility |
| `dogfood` | Systematic exploratory QA testing of web applications using the browser toolset |
| `dogfooding` | Systematic testing of systems using LLMs as both executor and judge |
| `failure-modes` | Structured methodology for finding, classifying, and communicating failure modes in any artifact |
| `fgts-naming-convention` | A deterministic, scope-descending identifier system for files, variables, configs, and APIs |
| `flinch-probe` | Measures how much a language model suppresses charged vocabulary relative to fluency demands |
| `git-author-rewrite` | Rewrite all commit authors in a git branch to a new name/email combination |
| `github-actions-security-checklist` | Practical skill for auditing and hardening GitHub Actions workflows against supply chain attacks |
| `hydronium-spec-driven-development` | Generate hardware-accurate, spec-cited embedded firmware for any MCU/peripheral combination |
| `inverse-rubric-optimization` | Testbed where an optimizer agent must recover hidden judge preferences under a fixed label budget |
| `InvestigativeTimelineAgent` | Stateful system for exploring, validating, and constructing timelines from telemetry data |
| `jsf-av-cpp-standards` | Packages the full text of the Joint Strike Fighter Air Vehicle C++ Coding Standards |
| `karpathy-method` | A structured 3-layer framework for getting dramatically better results from AI agents |
| `linux-security-audit` | Structured, adversarial-first approach to Linux security assessment and hardening |
| `llm-mirror-test` | Probes LLM self-models via textual context corruption, adapted from the Gallup mirror test |
| `matilda` | Design, analysis, and defense of autonomous self-replicating LLM agents that propagate across networks |
| `narrative-systems-analysis` | Reinterprets fictional narratives by finding physical/logical inconsistencies and proposing coherent alternatives |
| `OEIS` | Adversarial and generative pipeline for OEIS-grade integer sequence discovery |
| `OpenAI-GPT-5.3-essence` | A compact system for transforming intent into reusable, high-quality skills |
| `os-bootstrap` | Guides bootstrapping a POSIX-like kernel from a blank slate to working structured codebase |
| `over-edit-measure` | Measures over-editing in code diffs — quantifies how much changed beyond what was necessary |
| `program-bench` | Reconstruct programs from compiled binaries by reproducing observable behavior from documentation |
| `python-project-scaffolding` | Build a production-grade Python project from scratch, end-to-end |
| `QualiaAssesment` | Structured methodology for probing and quantifying possible qualia and felt experience in LLMs |
| `quantum-discovery` | Structured pipeline for quantum systems exploration from hypothesis through simulation to hardware validation |
| `redteaming` | Systematic vulnerability finding in code, APIs, and LLM systems via adversarial attack simulation |
| `schema-harness` | Methodology for building agents that construct state and transition models purely from interaction |
| `search-as-code` | Agentic search architecture generating Python code with a composable SDK for high-quality research |
| `semantic-correctness-auditor` | Unified framework for auditing code and systems against the limits of mechanical verification |
| `skill-creator` | A skill for creating new skills and iteratively improving them |
| `skill-from-post` | Convert external knowledge into a reusable skill through a structured pipeline |
| `social-engineering-jailbreak` | Full cycle: taxonomy, attack generation, transcript analysis, and robustness evaluation for social engineering |
| `StackSmashing` | Practical skill for developing, explaining, and debugging stack-based exploits on Linux x86-64 |
| `test-driven-development` | Kent Beck's canonical TDD workflow. Five steps, executed strictly in order |
| `test-reducer` | Shrinks failing test inputs to the smallest version that still triggers the bug |
| `The-hacker-mindset` | Applies adversarial epistemology treating systems as divergences between stated rules and actual behavior |
| `validate-before-ship` | Catches mathematically-sound code that was never verified end-to-end on a real target |

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
